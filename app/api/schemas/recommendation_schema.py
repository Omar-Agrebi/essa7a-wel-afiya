from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.api.schemas.opportunity_schema import OpportunityRead

class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    recommendation_id: UUID
    score: float
    match_reasons: list[str]
    opportunity: OpportunityRead
    created_at: datetime

class RecommendationRequest(BaseModel):
    top_n: int = 10
