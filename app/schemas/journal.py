from datetime import datetime

from pydantic import BaseModel, Field


class JournalEntryCreate(BaseModel):
    title: str | None = Field(default=None, max_length=150)
    body: str = Field(min_length=1, max_length=5000)
    tags: list[str] = Field(default_factory=list)


class JournalEntryRead(BaseModel):
    id: str
    title: str | None
    body: str
    tags: list[str]
    created_at: datetime

    model_config = {'from_attributes': True}
