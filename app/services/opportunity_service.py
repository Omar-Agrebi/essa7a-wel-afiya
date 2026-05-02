
from fastapi import HTTPException, status
from app.repositories.opportunity_repository import OpportunityRepository
from app.api.schemas.opportunity_schema import OpportunityCreate, OpportunityUpdate, OpportunityFilter

class OpportunityService:
    def __init__(self, repo: OpportunityRepository):
        self.repo = repo

    async def list_opportunities(self, filters: OpportunityFilter, skip: int, limit: int):
        """List opportunities with filters and pagination."""
        return await self.repo.list_all(filters=filters, skip=skip, limit=limit)

    async def get_opportunity(self, id: str):
        """Get an opportunity by its ID."""
        opportunity = await self.repo.get(id)
        if not opportunity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
        return opportunity

    async def create_opportunity(self, data: OpportunityCreate):
        """Create a new opportunity. Checks for duplicate URL."""
        existing = await self.repo.get_by_url(data.url)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Opportunity with this URL already exists")
        return await self.repo.create(data)

    async def update_opportunity(self, id: str, data: OpportunityUpdate):
        """Update an existing opportunity."""
        opportunity = await self.repo.get(id)
        if not opportunity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
        return await self.repo.update(id, data)

    async def delete_opportunity(self, id: str) -> bool:
        """Delete an opportunity by its ID."""
        opportunity = await self.repo.get(id)
        if not opportunity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
        return await self.repo.delete(id)

    async def search_opportunities(self, keyword: str):
        """Search for opportunities by keyword."""
        return await self.repo.search(keyword)

    async def get_expiring_soon(self, days: int):
        """Get opportunities expiring within the given number of days."""
        return await self.repo.get_expiring_soon(days)

    async def bulk_upsert_opportunities(self, items: list[dict]) -> dict:
        """Bulk upsert opportunities into the database."""
        return await self.repo.bulk_upsert(items)
