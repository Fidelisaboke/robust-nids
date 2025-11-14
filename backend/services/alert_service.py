from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends
from sqlalchemy import func

from core.dependencies import get_alert_repository, get_user_repository
from database.models import Alert, User
from database.repositories.alert import AlertRepository
from database.repositories.user import UserRepository
from schemas.nids import AlertCreate, AlertsSummaryResponse, AlertUpdate
from services.email_service import EmailService, get_email_service
from services.exceptions.alert import AlertNotFoundError
from services.exceptions.user import UserNotFoundError
from utils.enums import AlertSeverity, AlertStatus


class AlertService:
    """Service for managing alert operations."""

    def __init__(
        self,
        alert_repo: AlertRepository,
        user_repo: UserRepository,
        email_service: EmailService,
    ):
        self.alert_repo = alert_repo
        self.user_repo = user_repo
        self.email_service = email_service

    def get_alert(self, alert_id: int) -> Alert:
        """
        Fetch a single alert by its ID.

        :param alert_id: The ID of the alert to fetch.
        :raises AlertNotFoundError: If the alert does not exist.
        :return: The Alert object.
        """
        alert = self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise AlertNotFoundError()
        return alert

    def list_alerts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[AlertSeverity] = None,
        status: Optional[AlertStatus] = None,
        sort_by: str = "flow_timestamp",
        sort_direction: str = "desc",
    ):
        """
        Get a paginatable query for alerts with optional filters.

        :return: A SQLAlchemy Select statement.
        """
        return self.alert_repo.list_all(
            start_date=start_date,
            end_date=end_date,
            severity=severity,
            status=status,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    def create_alert(self, alert_data: AlertCreate) -> Alert:
        """
        Create a new alert.

        :param alert_data: Data for the new alert.
        :return: The newly created Alert object.
        """
        alert_dict = alert_data.model_dump()
        new_alert = self.alert_repo.create(alert_dict)
        self.alert_repo.session.flush()
        self.alert_repo.session.refresh(new_alert)
        return new_alert

    def update_alert(self, alert_id: int, update_data: AlertUpdate) -> Alert:
        """
        Perform a generic update on an alert.

        :param alert_id: The ID of the alert to update.
        :param update_data: The fields to update.
        :return: The updated Alert object.
        """
        alert = self.get_alert(alert_id)
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_alert = self.alert_repo.update(alert, update_dict)
        self.alert_repo.session.flush()
        self.alert_repo.session.refresh(updated_alert)
        return updated_alert

    def delete_alert(self, alert_id: int) -> None:
        """
        Delete an alert by its ID.

        :param alert_id: The ID of the alert to delete.
        """
        alert = self.get_alert(alert_id)
        self.alert_repo.delete(alert)
        self.alert_repo.session.flush()

    def assign_alert(self, alert_id: int, user_id: int) -> Alert:
        """
        Assign an alert to a user (analyst).

        :param alert_id: The ID of the alert.
        :param user_id: The ID of the user to assign.
        :raises UserNotFoundError: If the user does not exist.
        :return: The updated Alert object.
        """
        alert = self.get_alert(alert_id)
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        update_data = {"assigned_to_id": user.id, "status": AlertStatus.INVESTIGATING}
        updated_alert = self.alert_repo.update(alert, update_data)
        self.alert_repo.session.flush()
        self.alert_repo.session.refresh(updated_alert)
        return updated_alert

    def acknowledge_alert(self, alert_id: int, user: User) -> Alert:
        """
        Acknowledge an alert, assigning it to the current user if unassigned.

        :param alert_id: The ID of the alert.
        :param user: The currently authenticated user.
        :return: The updated Alert object.
        """
        alert = self.get_alert(alert_id)
        update_data = {"status": AlertStatus.ACKNOWLEDGED}
        if not alert.assigned_to_id:
            update_data["assigned_to_id"] = user.id

        updated_alert = self.alert_repo.update(alert, update_data)
        self.alert_repo.session.flush()
        self.alert_repo.session.refresh(updated_alert)
        return updated_alert

    def resolve_alert(self, alert_id: int, user: User, notes: Optional[str]) -> Alert:
        """
        Resolve an alert, adding optional notes to the description.

        :param alert_id: The ID of the alert.
        :param user: The currently authenticated user.
        :param notes: Analyst's resolution notes.
        :return: The updated Alert object.
        """
        alert = self.get_alert(alert_id)

        # Prevent alert from being resolved multiple times
        if alert.status == AlertStatus.RESOLVED:
            return alert

        new_description = alert.description or ""
        if notes:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            new_description += f"\n\n--- RESOLVED by {user.username} at {timestamp} ---\n{notes}"

        update_data = {
            "status": AlertStatus.RESOLVED,
            "description": new_description,
            "assigned_to_id": alert.assigned_to_id or user.id,  # Keep assignment
        }

        updated_alert = self.alert_repo.update(alert, update_data)
        self.alert_repo.session.flush()
        self.alert_repo.session.refresh(updated_alert)
        return updated_alert

    def get_alert_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by_time: str = "day",  # 'day' or 'hour'
    ) -> AlertsSummaryResponse:
        """
        Generates aggregated statistics for alerts.

        :param start_date: Optional filter for start of time range.
        :param end_date: Optional filter for end of time range.
        :param group_by_time: Granularity for time_series ('day' or 'hour').
        :return: AlertsSummaryResponse
        """
        session = self.alert_repo.session

        # Base query with time filters
        base_query = session.query(Alert)
        if start_date:
            base_query = base_query.filter(Alert.flow_timestamp >= start_date)
        if end_date:
            base_query = base_query.filter(Alert.flow_timestamp <= end_date)

        # 1. Total Alerts
        total_alerts = base_query.count()

        # 2. Counts by Status
        status_counts_query = (
            base_query.with_entities(Alert.status, func.count(Alert.id)).group_by(Alert.status).all()
        )
        by_status = {status: count for status, count in status_counts_query}

        # 3. Counts by Severity
        severity_counts_query = (
            base_query.with_entities(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
        )
        by_severity = {severity: count for severity, count in severity_counts_query}

        # 4. Top 10 by Category
        category_counts_query = (
            base_query.with_entities(Alert.category, func.count(Alert.id).label("count"))
            .group_by(Alert.category)
            .order_by(func.count(Alert.id).desc())
            .limit(10)
            .all()
        )
        by_category = [{"category": category, "count": count} for category, count in category_counts_query]

        # 5. Time Series (Histogram)
        # Use date_trunc for efficient grouping by hour or day
        if group_by_time not in ["day", "hour"]:
            group_by_time = "day"

        time_series_query = (
            base_query.with_entities(
                func.date_trunc(group_by_time, Alert.flow_timestamp).label("timestamp"),
                func.count(Alert.id).label("count"),
            )
            .group_by("timestamp")
            .order_by("timestamp")
            .all()
        )
        time_series = [{"timestamp": ts, "count": count} for ts, count in time_series_query]

        return AlertsSummaryResponse(
            total_alerts=total_alerts,
            by_status=by_status,
            by_severity=by_severity,
            by_category=by_category,
            time_series=time_series,
        )


# Dependency injection
def get_alert_service(
    alert_repo: AlertRepository = Depends(get_alert_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
) -> AlertService:
    return AlertService(alert_repo, user_repo, email_service)
