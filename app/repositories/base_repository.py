"""Generic base repository for async database operations."""
from typing import TypeVar, Generic, Type, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database.base import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    """
    Generic repository class providing standard CRUD operations.
    """
    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Initializes the repository with the database session and SQLAlchemy model.
        
        Args:
            session (AsyncSession): The asynchronous database session.
            model (Type[T]): The SQLAlchemy model class.
        """
        self.session = session
        self.model = model

    async def get_by_id(self, id: str) -> T | None:
        """
        Retrieves a single record by its primary key.
        
        Args:
            id (UUID): The primary key ID to search for.
            
        Returns:
            T | None: The found record or None.
        """
        try:
            result = await self.session.get(self.model, id)
            return result
        except Exception as e:
            raise e

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """
        Retrieves multiple records, ordered by created_at descending if available.
        
        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            
        Returns:
            list[T]: A list of records.
        """
        try:
            stmt = select(self.model)
            if hasattr(self.model, 'created_at'):
                stmt = stmt.order_by(self.model.created_at.desc())
            stmt = stmt.offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def create(self, obj_in: dict[str, Any]) -> T:
        """
        Creates a new record in the database.
        
        Args:
            obj_in (dict): A dictionary containing the fields to save.
            
        Returns:
            T: The created record.
        """
        try:
            db_obj = self.model(**obj_in)
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            return db_obj
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update(self, id: str, obj_in: dict[str, Any]) -> T | None:
        """
        Updates an existing record.
        
        Args:
            id (UUID): The primary key ID of the record to update.
            obj_in (dict): A dictionary of fields to update.
            
        Returns:
            T | None: The updated record, or None if not found.
        """
        try:
            db_obj = await self.session.get(self.model, id)
            if not db_obj:
                return None
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            await self.session.commit()
            await self.session.refresh(db_obj)
            return db_obj
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete(self, id: str) -> bool:
        """
        Deletes a record from the database.
        
        Args:
            id (UUID): The primary key ID of the record to delete.
            
        Returns:
            bool: True if the record was successfully deleted, False otherwise.
        """
        try:
            db_obj = await self.session.get(self.model, id)
            if not db_obj:
                return False
            await self.session.delete(db_obj)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise e

    async def count(self) -> int:
        """
        Counts the total number of records for the model.
        
        Returns:
            int: The total count of records.
        """
        try:
            stmt = select(func.count()).select_from(self.model)
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            raise e
