from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.opportunity_schema import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityRead,
    OpportunityFilter
)
from app.services.opportunity_service import OpportunityService
from app.repositories.opportunity_repository import OpportunityRepository
from database.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/opportunities", tags=["opportunities"])

def get_opportunity_service(db: AsyncSession = Depends(get_db)) -> OpportunityService:
    """Service factory for OpportunityService."""
    return OpportunityService(OpportunityRepository(db))

@router.get("/", response_model=List[OpportunityRead])
async def list_opportunities(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    cluster_id: Optional[int] = Query(None),
    expiring_in_days: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    service: OpportunityService = Depends(get_opportunity_service)
):
    """List opportunities with filters and pagination."""
    filters = OpportunityFilter(
        type=type,
        category=category,
        keyword=keyword,
        cluster_id=cluster_id,
        expiring_in_days=expiring_in_days
    )
    return await service.list_opportunities(filters=filters, skip=skip, limit=limit)

@router.get("/search", response_model=List[OpportunityRead])
async def search_opportunities(
    keyword: str = Query(...),
    service: OpportunityService = Depends(get_opportunity_service)
):
    """Search for opportunities by keyword."""
    return await service.search_opportunities(keyword)

@router.get("/expiring", response_model=List[OpportunityRead])
async def expiring_opportunities(
    days: int = Query(7),
    service: OpportunityService = Depends(get_opportunity_service)
):
    """Get opportunities expiring within the given number of days."""
    return await service.get_expiring_soon(days)

@router.get("/{opportunity_id}", response_model=OpportunityRead)
async def get_opportunity(
    opportunity_id: UUID,
    service: OpportunityService = Depends(get_opportunity_service)
):
    """Get a specific opportunity by ID."""
    return await service.get_opportunity(opportunity_id)

@router.post("/", response_model=OpportunityRead, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    data: OpportunityCreate,
    current_user: User = Depends(get_current_user),
    service: OpportunityService = Depends(get_opportunity_service)
):
    """Create a new opportunity (Protected)."""
    return await service.create_opportunity(data)

@router.put("/{opportunity_id}", response_model=OpportunityRead)
async def update_opportunity(
    opportunity_id: UUID,
    data: OpportunityUpdate,
    current_user: User = Depends(get_current_user),
    service: OpportunityService = Depends(get_opportunity_service)
):
    """Update an existing opportunity (Protected)."""
    return await service.update_opportunity(opportunity_id, data)

@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: UUID,
    current_user: User = Depends(get_current_user),
    service: OpportunityService = Depends(get_opportunity_service)
):
    """Delete an opportunity (Protected)."""
    await service.delete_opportunity(opportunity_id)
