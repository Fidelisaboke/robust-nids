"""
Database module.
Contains the database class, which has the database configuration and methods
for database session management.
"""

from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from core.config import AppConfig, DatabaseConfig

load_dotenv()


class Database:
    def __init__(self, config: DatabaseConfig = DatabaseConfig()) -> None:
        self.engine = create_engine(config.URL, pool_size=5, max_overflow=10, echo=AppConfig.DEBUG)
        self.SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

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
