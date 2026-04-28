from typing import Literal

from pydantic import BaseModel, Field


class ChatContext(BaseModel):
    source: str = 'chat'
    minutes_available: int = Field(default=3, ge=1, le=15)
    allow_history: bool = False


class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=2, max_length=1000)
    context: ChatContext = Field(default_factory=ChatContext)


class ChatMessageResponse(BaseModel):
    emotion: str
    risk_level: Literal['bajo', 'medio', 'alto']
    reply: str
    suggested_action: str | None = None
    save_history: bool = False