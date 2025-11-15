from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import joinedload

from database.models import Report, User
from database.repositories.base import BaseRepository
from utils.enums import ReportStatus


class ReportRepository(BaseRepository):
    """Repository for report-specific database access."""

    def get_by_id(self, entity_id: int) -> Report | None:
        return (
            self.session.query(Report)
            .options(joinedload(Report.owner))
            .filter(Report.id == entity_id)
            .first()
        )

    def list_all(
        self,
        search: str | None,
        status: ReportStatus | None,
        sort_by: str | None,
        sort_order: str | None,
    ):
        """
        Returns a SQLAlchemy select statement for all reports with their owners.
        Includes search, filtering, and sorting.
        """
        stmt = select(Report).options(joinedload(Report.owner))

        if status:
            stmt = stmt.filter(Report.status == status)

        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Report.title.ilike(search_term),
                    cast(Report.status, String).ilike(search_term),
                    Report.owner.has(User.email.ilike(search_term)),
                    Report.owner.has(User.first_name.ilike(search_term)),
                    Report.owner.has(User.last_name.ilike(search_term)),
                )
            )

        # Sorting
        sort_column = Report.created_at  # Default sort column
        if sort_by == "title":
            sort_column = Report.title
        elif sort_by == "status":
            sort_column = Report.status
        elif sort_by == "owner":
            sort_column = Report.owner_id

        if sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return stmt

    def list_all_by_user(
        self,
        user_id: int,
        search: str | None = None,
        status: ReportStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        """Get a paginatable query for all reports owned by a user."""
        stmt = self.list_all(search, status, sort_by, sort_order)
        stmt = stmt.filter(Report.owner_id == user_id)
        return stmt

    def create(self, data: dict) -> Report:
        report = Report(**data)
        self.session.add(report)
        return report

    def update(self, entity: Report, data: dict) -> Report:
        for key, value in data.items():
            setattr(entity, key, value)
        return entity

    def delete(self, entity: Report) -> None:
        self.session.delete(entity)
        return None
