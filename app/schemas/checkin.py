from datetime import datetime

from pydantic import BaseModel, Field


class MoodCheckInCreate(BaseModel):
    mood_score: int = Field(ge=1, le=5)
    stress_score: int = Field(ge=1, le=5)
    note: str | None = Field(default=None, max_length=1000)


class MoodCheckInRead(BaseModel):
    id: str
    mood_score: int
    stress_score: int
    note: str | None
    created_at: datetime

    model_config = {'from_attributes': True}
