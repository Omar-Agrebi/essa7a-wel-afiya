from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.constants import NotificationStatus
from app.api.schemas.opportunity_schema import OpportunityRead

class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    notification_id: UUID
    message: str
    status: NotificationStatus
    timestamp: datetime
    opportunity: OpportunityRead

class NotificationStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    status: NotificationStatus
