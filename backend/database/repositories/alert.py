from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from database.models import Alert
from database.repositories.base import BaseRepository
from utils.enums import AlertSeverity, AlertStatus


class AlertRepository(BaseRepository):
    """Repository for alert-specific database access."""

    def get_by_id(self, entity_id: int) -> Alert | None:
        """
        Fetch an alert by its ID, pre-loading the assigned user.

        :param entity_id: The ID of the alert to fetch.
        :return: The Alert object, or None if not found.
        """
        return (
            self.session.query(Alert)
            .options(joinedload(Alert.assigned_user))
            .filter(Alert.id == entity_id)
            .first()
        )

    def create(self, data: dict) -> Alert:
        """
        Create a new alert record.

        :param data: A dictionary containing the alert data.
        :return: The newly created Alert object.
        """
        alert = Alert(**data)
        self.session.add(alert)
        return alert

    def update(self, entity: Alert, data: dict) -> Alert:
        """
        Update an existing alert record.

        :param entity: The Alert object to update.
        :param data: A dictionary with the fields to update.
        :return: The updated Alert object.
        """
        for key, value in data.items():
            setattr(entity, key, value)
        return entity

    def delete(self, entity: Alert) -> None:
        """
        Delete an alert record.

        :param entity: The Alert object to delete.
        """
        self.session.delete(entity)

    def list_all(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[AlertSeverity] = None,
        status: Optional[AlertStatus] = None,
        sort_by: str = "flow_timestamp",
        sort_direction: str = "desc",
    ):
        """
        Return a paginatable SQLAlchemy Select statement for alerts,
        with optional filters and sorting.

        :param start_date: Filter for alerts on or after this time.
        :param end_date: Filter for alerts on or before this time.
        :param severity: Filter by alert severity.
        :param status: Filter by alert status.
        :param sort_by: Column to sort by (default: 'flow_timestamp').
        :param sort_direction: 'asc' or 'desc' (default: 'desc').
        :return: A SQLAlchemy Select statement.
        """
        stmt = select(Alert).options(joinedload(Alert.assigned_user))

        # Apply filters
        if start_date:
            stmt = stmt.where(Alert.flow_timestamp >= start_date)
        if end_date:
            stmt = stmt.where(Alert.flow_timestamp <= end_date)
        if severity:
            stmt = stmt.where(Alert.severity == severity)
        if status:
            stmt = stmt.where(Alert.status == status)

        # Apply sorting
        sort_column = getattr(Alert, sort_by, Alert.flow_timestamp)
        if sort_direction == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return stmt

    def get_by_user_id(self, user_id: int):
        """
        Return a paginatable Select statement for alerts
        assigned to a specific user.

        :param user_id: The ID of the user.
        :return: A SQLAlchemy Select statement.
        """
        stmt = (
            self.list_all(sort_by="status", sort_direction="asc")
            .where(Alert.assigned_to_id == user_id)
            .where(Alert.status.in_([AlertStatus.ACTIVE, AlertStatus.INVESTIGATING]))
        )
        return stmt
