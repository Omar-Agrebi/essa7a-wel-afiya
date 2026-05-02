from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.core.constants import NotificationStatus
from app.api.schemas.opportunity_schema import OpportunityRead

class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    notification_id: str
    message: str
    status: str
    timestamp: datetime
    opportunity: Optional[OpportunityRead] = None

class NotificationStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str
