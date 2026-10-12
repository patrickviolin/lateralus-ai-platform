from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Index


# class SessionRegistry(BaseModel):
#     id: int = Field(...)
#     organization_id: str = Field(...)
#     session_id: str = Field(...)
#     platform: str = Field(...)
#
#
# class TranscriptEvent(BaseModel):
#     session_registry_id: int = Field(...)
#     session_position: int = Field(...)
#
# class MemoryObservations(BaseModel):
#     id: int = Field(...)
#     organization_id: str = Field(...)
#     source: str = Field(...)
#     external_id: str = Field(...)
#     occurred_at: str = Field(...)
#     references_url: str = Field(...)
#     metadata: str = Field(...)
#     payload: str = Field(...)


class MemorySummaries(SQLModel, table=True):
    __tablename__ = "memory_summaries"
    __table_args__ = (
        Index("uq_memory_summaries_coverage", "thread_id", "covers_through_message_id", unique=True),
    )
    thread_id: str = Field(primary_key=True)
    # organization_id: str = Field(...)
    revision: int = Field(primary_key=True)
    content: str = Field(...)
    covers_through_message_id: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    tombstoned_at: Optional[datetime] = Field(default=None)
    tombstone_reason: Optional[str] = Field(default=None)
    model: str = Field(...)
    prompt_version: str = Field(...)
    audience: str = Field(...)
    kind: str = Field(...)
    memory_agent: str = Field(...)
    memory_agent_version: str = Field(...)
