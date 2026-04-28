from datetime import datetime

from pydantic import BaseModel, Field


class PomodoroSessionCreate(BaseModel):
    focus_minutes: int = Field(ge=1, le=180)
    break_minutes: int = Field(ge=1, le=60)
    cycles_completed: int = Field(ge=1, le=12)
    note: str | None = Field(default=None, max_length=1000)


class PomodoroSessionRead(BaseModel):
    id: str
    focus_minutes: int
    break_minutes: int
    cycles_completed: int
    note: str | None
    created_at: datetime

    model_config = {'from_attributes': True}
