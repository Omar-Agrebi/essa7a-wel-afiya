from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.constants import NotificationStatus

class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    notification_id: str
    message: str
    status: str
    timestamp: datetime

class NotificationStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str
