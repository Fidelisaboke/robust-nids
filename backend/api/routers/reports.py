import os
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from api.dependencies import get_current_active_user, require_permissions
from database.models import ReportStatus, User
from schemas.reports import ReportCreate, ReportOut
from services.report_service import ReportService, get_report_service
from utils.enums import SystemPermissions

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.post(
    "/",
    response_model=ReportOut,
    dependencies=[Depends(require_permissions(SystemPermissions.VIEW_ALERTS))],
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_new_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    report_service: ReportService = Depends(get_report_service),
):
    """
    Accepts a request to generate a new report.
    Creates the job and returns immediately.
    """
    # 1. Create the 'PENDING' job
    pending_report = ReportOut(
        id=-1,  # Placeholder ID
        title=report_data.title,
        status=ReportStatus.PENDING,
        parameters=report_data.model_dump(mode="json"),
        file_path=None,
        owner=current_user,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # 2. Add the heavy-lifting task to run in the background
    background_tasks.add_task(report_service.generate_report_file, report_data, current_user.id)

    # 3. Return the pending job object
    return pending_report


@router.get(
    "/",
    response_model=Page[ReportOut],
    dependencies=[Depends(require_permissions(SystemPermissions.VIEW_ALERTS))],
)
def list_reports(
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
    search: str | None = None,
    status: ReportStatus | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
):
    """
    Lists all reports generated.
    """
    # If admin, list all reports; else list only user's reports
    if current_user.is_admin:
        query = report_service.list_reports(search, status, sort_by, sort_order)
    else:
        query = report_service.list_reports_for_user(current_user.id, search, status, sort_by, sort_order)

    return paginate(report_service.report_repo.session, query)


@router.get(
    "/{report_id}/download", dependencies=[Depends(require_permissions(SystemPermissions.VIEW_ALERTS))]
)
def download_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    report_service: ReportService = Depends(get_report_service),
):
    """
    Downloads the generated report file if it's ready.
    1. Checks if the report belongs to the user.
    2. Checks if the report status is 'READY'.
    3. Streams the CSV file to the user.
    """
    report = report_service.get_report(report_id)

    # Security check: User can only download their own reports
    if report.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your report")

    if report.status != ReportStatus.READY:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report is not ready or has failed")

    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found")

    # Return a FileResponse to stream the CSV to the user
    return FileResponse(
        path=report.file_path,
        filename=f"{report.title.replace(' ', '_')}_{report.created_at.date()}.csv",
        media_type="text/csv",
    )


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permissions(SystemPermissions.VIEW_ALERTS))],
)
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    report_service: ReportService = Depends(get_report_service),
):
    """
    Deletes a report.
    """
    report = report_service.get_report(report_id)

    # Security check: User can only delete their own reports if they are not admin
    if not current_user.is_admin and report.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your report")

    report_service.delete_report(report_id)
    return None
