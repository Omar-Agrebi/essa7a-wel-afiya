"""Pydantic v2 schemas for the Opportunity domain."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.constants import OpportunityCategory, OpportunityType


class OpportunityCreate(BaseModel):
    """Schema for creating a new opportunity.

    All fields map 1-to-1 to the ``opportunities`` table columns that a
    caller is allowed to supply at creation time.
    """

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
    """Schema for partially updating an existing opportunity.

    Every field is optional so callers can perform partial (PATCH-style)
    updates.  Cluster information is writeable here because the
    AgentCluster post-processes records after initial creation.
    """

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
    """Schema returned to API clients for a single opportunity.

    Includes all stored columns that are safe to expose, plus cluster
    metadata assigned by the MAS pipeline.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    type: OpportunityType
    category: OpportunityCategory
    description: str | None
    skills_required: list[str]
    location: str | None
    eligibility: str | None
    deadline: date | None
    source: str
    url: str
    cluster_id: int | None
    cluster_label: str | None
    created_at: datetime
    updated_at: datetime


class OpportunityFilter(BaseModel):
    """Query parameters accepted by the list-opportunities endpoint.

    All fields default to ``None`` so each filter is applied only when
    an explicit value is provided by the caller.
    """

    model_config = ConfigDict(from_attributes=True)

    type: OpportunityType | None = None
    category: OpportunityCategory | None = None
    keyword: str | None = None
    cluster_id: int | None = None
    expiring_in_days: int | None = None
