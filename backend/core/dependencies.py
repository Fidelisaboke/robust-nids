
from sqlalchemy.orm import Session

from backend.database.db import db


def get_db_session() -> Session:
    """
    FastAPI dependency that manages the request's database transaction.
    """
    with db.get_session() as session:
        try:
            yield session
            session.commit()
        except Exception:
            raise
