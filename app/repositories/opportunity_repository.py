"""Opportunity repository."""
from datetime import timedelta, timezone, datetime
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.repositories.base_repository import BaseRepository
from app.models.opportunity import Opportunity
from app.core.constants import OpportunityType, OpportunityCategory

class OpportunityRepository(BaseRepository[Opportunity]):
    """
    Repository for Opportunity specific database operations.
    """
    def __init__(self, session: AsyncSession):
        """Initializes the repository with the Opportunity model."""
        super().__init__(session, Opportunity)

    async def get_by_type(self, type: OpportunityType) -> list[Opportunity]:
        """
        Retrieves opportunities filtered by type.
        """
        try:
            stmt = select(Opportunity).where(Opportunity.type == type).order_by(Opportunity.created_at.desc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def get_by_category(self, category: OpportunityCategory) -> list[Opportunity]:
        """
        Retrieves opportunities filtered by category.
        """
        try:
            stmt = select(Opportunity).where(Opportunity.category == category).order_by(Opportunity.created_at.desc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def get_by_url(self, url: str) -> Opportunity | None:
        """
        Retrieves an opportunity by its exact URL (used for deduplication).
        """
        try:
            stmt = select(Opportunity).where(Opportunity.url == url)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise e

    async def search(self, keyword: str) -> list[Opportunity]:
        """
        Searches opportunities by a keyword matching title OR description (case-insensitive).
        Returns ordered by created_at descending.
        """
        try:
            search_pattern = f"%{keyword}%"
            stmt = select(Opportunity).where(
                or_(
                    Opportunity.title.ilike(search_pattern),
                    Opportunity.description.ilike(search_pattern)
                )
            ).order_by(Opportunity.created_at.desc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def get_expiring_soon(self, days: int) -> list[Opportunity]:
        """
        Retrieves opportunities expiring between today and today+days.
        Excludes already-expired opportunities.
        """
        try:
            today = datetime.now(timezone.utc).date()
            target_date = today + timedelta(days=days)
            stmt = select(Opportunity).where(
                Opportunity.deadline >= today,
                Opportunity.deadline <= target_date
            ).order_by(Opportunity.deadline.asc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def get_by_cluster(self, cluster_id: int) -> list[Opportunity]:
        """
        Retrieves opportunities filtered by cluster_id.
        """
        try:
            stmt = select(Opportunity).where(Opportunity.cluster_id == cluster_id).order_by(Opportunity.created_at.desc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise e

    async def upsert_by_url(self, obj_in: dict[str, Any]) -> tuple[Opportunity, bool]:
        """
        Upserts an opportunity based on its URL.
        If URL exists: updates all non-key fields, returns (opp, False).
        If URL new: inserts, returns (opp, True).
        """
        try:
            if "url" not in obj_in:
                raise ValueError("URL is required for upsert operation.")
            
            existing = await self.get_by_url(obj_in["url"])
            if existing:
                for key, value in obj_in.items():
                    if key != "url" and key != "id":
                        setattr(existing, key, value)
                await self.session.commit()
                await self.session.refresh(existing)
                return existing, False
            else:
                db_obj = Opportunity(**obj_in)
                self.session.add(db_obj)
                await self.session.commit()
                await self.session.refresh(db_obj)
                return db_obj, True
        except Exception as e:
            await self.session.rollback()
            raise e

    async def bulk_upsert(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Runs upsert_by_url for a list of items.
        Returns a dictionary with counts of inserted, updated, and logged errors.
        """
        report = {"inserted": 0, "updated": 0, "errors": []}
        for item in items:
            try:
                _, is_new = await self.upsert_by_url(item)
                if is_new:
                    report["inserted"] += 1
                else:
                    report["updated"] += 1
            except Exception as e:
                url = item.get("url", "UNKNOWN_URL")
                report["errors"].append(f"Error processing {url}: {str(e)}")
        return report
