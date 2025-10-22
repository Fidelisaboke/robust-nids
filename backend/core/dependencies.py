"""Core FastAPI dependencies for FastAPI routes."""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from database.db import db
from database.repositories.permission import PermissionRepository
from database.repositories.role import RoleRepository
from database.repositories.user import UserRepository


def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that manages the request's database transaction.
    """
    with db.get_session() as session:
        try:
            yield session
            session.commit()
        except Exception:
            raise


def get_user_repository(session: Session = Depends(get_db_session)) -> UserRepository:
    """Dependency to provide a UserRepository instance."""
    return UserRepository(session)


def get_role_repository(session: Session = Depends(get_db_session)) -> RoleRepository:
    """Dependency to provide a RoleRepository instance."""
    return RoleRepository(session)


def get_permission_repository(session: Session = Depends(get_db_session)) -> PermissionRepository:
    """Dependency to provide a PermissionRepository instance."""
    return PermissionRepository(session)
