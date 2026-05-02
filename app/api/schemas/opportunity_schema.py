from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.core.constants import OpportunityType, OpportunityCategory

class OpportunityCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    type: OpportunityType
    category: OpportunityCategory
    description: str | None = None
    skills_required: list[str] = []
    location: str | None = None
    eligibility: str | None = None
    deadline: date | None = None
    source: str
    url: str

class OpportunityUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str | None = None
    type: OpportunityType | None = None
    category: OpportunityCategory | None = None
    description: str | None = None
    skills_required: list[str] | None = None
    location: str | None = None
    eligibility: str | None = None
    deadline: date | None = None
    source: str | None = None
    url: str | None = None
    cluster_id: int | None = None
    cluster_label: str | None = None

class OpportunityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    type: str
    category: str
    description: str | None
    skills_required: list[str]
    location: str | None
    eligibility: str | None
    deadline: str | None
    source: str
    url: str
    cluster_id: int | None
    cluster_label: str | None
    created_at: datetime
    updated_at: datetime

class OpportunityFilter(BaseModel):
    type: str | None = None
    category: str | None = None
    keyword: str | None = None
    cluster_id: int | None = None
    expiring_in_days: int | None = None
