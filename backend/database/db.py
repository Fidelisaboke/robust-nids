"""
Database module.
Contains the database class, which has the database configuration and methods
for database session management.
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings


class Database:
    def __init__(self) -> None:
        self.engine = create_engine(
            str(settings.DATABASE_URL),
            pool_size=5,
            max_overflow=10,
            echo=settings.DEBUG,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db = Database()
