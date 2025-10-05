from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from backend.database.models import Base


class BaseRepository(ABC):
    """Abstract base repository defining common data access operations."""

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.
        :param session: Database session.
        """
        self.session = session

    @abstractmethod
    def get_by_id(self, entity_id: int):
        """Fetch entity by ID."""
        pass

    @abstractmethod
    def list_all(self):
        """Return all entities."""
        pass

    @abstractmethod
    def create(self, data: dict):
        """Create a new entity and persist."""
        pass

    @abstractmethod
    def update(self, entity: Base, data: dict):
        """Update an existing entity."""
        pass

    @abstractmethod
    def delete(self, entity: Base):
        """Delete an entity by ID."""
        pass
