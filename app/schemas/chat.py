from typing import Literal

from pydantic import BaseModel, Field


class ChatContext(BaseModel):
    source: str | None = None
    minutes_available: int = 5
    allow_history: bool = False
    conversation_history: list[dict] = []


class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1)
    context: ChatContext = ChatContext()


class ChatMessageResponse(BaseModel):
    emotion: str
    risk_level: str
    reply: str
    suggested_action: str | None = None
    save_history: bool = False
    avatar_state: str = "speaking"
    intent: str = "normal_conversation"
    voice_text: str | None = None