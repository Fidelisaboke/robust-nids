import csv
import logging
import os
import uuid
from datetime import datetime

from fastapi import Depends

from core.dependencies import get_report_repository
from database.db import db
from database.models import Report
from database.repositories.alert import AlertRepository
from database.repositories.report import ReportRepository
from schemas.reports import ReportCreate
from services.alert_service import AlertService, get_alert_service
from utils.enums import ReportStatus

app_logger = logging.getLogger("uvicorn.error")

# Where reports are saved. Ensure this directory exists.
REPORTS_DIR = "media/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


class ReportService:
    """Service for managing report generation."""

    def __init__(self, report_repo: ReportRepository, alert_service: AlertService):
        self.report_repo = report_repo
        self.alert_service = alert_service

    def get_report(self, report_id: int) -> Report:
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise Exception("Report not found")
        return report

    def list_reports(
        self, search: str | None, status: ReportStatus | None, sort_by: str | None, sort_order: str | None
    ):
        """Returns the query for paginated reports."""
        return self.report_repo.list_all(search, status, sort_by, sort_order)

    def list_reports_for_user(
        self,
        user_id: int,
        search: str | None,
        status: ReportStatus | None,
        sort_by: str | None,
        sort_order: str | None,
    ):
        """Returns the query for paginated user reports."""
        return self.report_repo.list_all_by_user(user_id, search, status, sort_by, sort_order)

    async def generate_report_file(self, report_data: ReportCreate, owner_id: int):
        """
        The actual worker task. Runs in the background.
        Creates the 'PENDING' record, generates the file, and updates status.
        """

        # Must create a new session inside the background task
        with db.get_session() as session:
            report_repo = ReportRepository(session)
            report = None
            try:
                # Create pending report entry
                report_dict = report_data.model_dump(mode="json")
                report = report_repo.create(
                    {
                        "title": report_data.title,
                        "status": ReportStatus.PENDING,
                        "owner_id": owner_id,
                        "parameters": report_dict,
                    }
                )
                session.commit()
                session.refresh(report)
                report_id = report.id
                app_logger.info(f"Report job {report_id} created and PENDING.")

                # Mark as RUNNING
                report_repo.update(report, {"status": ReportStatus.RUNNING})
                session.commit()

                # Fetch data
                alert_service = AlertService(AlertRepository(session), None, None)
                params = report.parameters
                start_date = (
                    datetime.fromisoformat(params.get("start_date")) if params.get("start_date") else None
                )
                end_date = datetime.fromisoformat(params.get("end_date")) if params.get("end_date") else None

                alert_query = alert_service.list_alerts(
                    start_date=start_date,
                    end_date=end_date,
                    severity=params.get("severity"),
                    status=params.get("status"),
                    search=params.get("search"),
                )
                alerts = session.execute(alert_query).scalars().all()

                # Generate the file
                file_name = f"report_{uuid.uuid4()}.csv"
                file_path = os.path.join(REPORTS_DIR, file_name)

                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    # Write Header
                    writer.writerow(
                        [
                            "ID",
                            "Title",
                            "Severity",
                            "Status",
                            "Category",
                            "Flow Timestamp",
                            "Source IP",
                            "Dest IP",
                            "Dest Port",
                            "Assigned To",
                        ]
                    )
                    # Write Data
                    for alert in alerts:
                        assigned_to_user = alert.assigned_user.email if alert.assigned_user else "N/A"
                        writer.writerow(
                            [
                                alert.id,
                                alert.title,
                                alert.severity.value,
                                alert.status.value,
                                alert.category,
                                alert.flow_timestamp.isoformat(),
                                alert.src_ip,
                                alert.dst_ip,
                                alert.dst_port,
                                assigned_to_user,
                            ]
                        )

                app_logger.info(f"Report {report_id} generated with {len(alerts)} rows.")

                # Mark as READY and save file path
                report_repo.update(report, {"status": ReportStatus.READY, "file_path": file_path})
                session.commit()

            except Exception as e:
                app_logger.error(f"Report generation failed for {report_id}: {e}")
                # Mark as FAILED
                if report:
                    report_repo.update(report, {"status": ReportStatus.FAILED})
                    session.commit()


    def delete_report(self, report_id: int) -> None:
        report = self.get_report(report_id)
        # Optionally delete the file from disk
        if report.file_path and os.path.exists(report.file_path):
            os.remove(report.file_path)
        self.report_repo.delete(report)
        self.report_repo.session.commit()
        return None


# Dependency Injection for the service
def get_report_service(
    report_repo: ReportRepository = Depends(get_report_repository),
    alert_service: AlertService = Depends(get_alert_service),
) -> ReportService:
    return ReportService(report_repo, alert_service)
