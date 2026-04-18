from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.api.schemas.recommendation_schema import RecommendationRead
from app.services.recommendation_service import RecommendationService
from app.repositories.recommendation_repository import RecommendationRepository
from database.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.api.schemas.opportunity_schema import OpportunityFilter
from app.services.opportunity_service import OpportunityService
from app.repositories.opportunity_repository import OpportunityRepository

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

def get_recommendation_service(db: AsyncSession = Depends(get_db)) -> RecommendationService:
    """Service factory for RecommendationService."""
    return RecommendationService(RecommendationRepository(db))

def get_opportunity_service(db: AsyncSession = Depends(get_db)) -> OpportunityService:
    """Service factory for OpportunityService."""
    return OpportunityService(OpportunityRepository(db))

@router.get("/", response_model=List[RecommendationRead])
async def get_my_recommendations(
    top_n: int = Query(10),
    current_user: User = Depends(get_current_user),
    service: RecommendationService = Depends(get_recommendation_service)
):
    """Get the top recommended opportunities for the active user."""
    return await service.get_recommendations(current_user.user_id, top_n)

@router.post("/refresh")
async def refresh_my_recommendations(
    current_user: User = Depends(get_current_user),
    rec_service: RecommendationService = Depends(get_recommendation_service),
    opp_service: OpportunityService = Depends(get_opportunity_service)
):
    """Trigger a freshness sweep re-calculating recommendations."""
    # Retrieve opportunities internally since service limits/filters are needed.
    # We fetch enough active opportunities (e.g., all of them)
    # in practice there may be a specific repo method here. We'll simply use limit=1000 for logic illustration.
    try:
        from ml.inference.recommender import OpportunityRecommender
    except ImportError:
        # Mocking for Phase 3 when ML modules are not yet created.
        return {"message": "refresh triggered", "count": 0}

    opportunities = await opp_service.list_opportunities(filters=OpportunityFilter(), skip=0, limit=1000)
    user_dict = {
        "user_id": str(current_user.user_id),
        "skills": current_user.skills,
        "interests": current_user.interests,
        "level": current_user.level
    }
    
    opportunities_dict = [
        {
            "id": str(opp.id),
            "title": opp.title,
            "type": opp.type,
            "category": opp.category,
            "description": opp.description,
            "skills_required": opp.skills_required,
            "level": getattr(opp, "level", "unknown"),  # Extracted level if applicable
            "deadline": str(opp.deadline) if opp.deadline else None,
            "cluster_label": opp.cluster_label
        } for opp in opportunities
    ]
    
    recommender = OpportunityRecommender()
    scored_opps = recommender.recommend(user=user_dict, opportunities=opportunities_dict, top_n=10)
    
    count = await rec_service.refresh_recommendations(current_user.user_id, scored_opps)
    
    return {"message": "refresh triggered", "count": count}
