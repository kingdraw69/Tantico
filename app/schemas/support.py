from pydantic import BaseModel, Field


class MotivationRequest(BaseModel):
    emotion: str = Field(..., examples=["ansiedad", "estres_academico", "tristeza"])
    context: str | None = Field(default=None, examples=["parcial", "entrega", "exposicion"])


class MotivationResponse(BaseModel):
    emotion: str
    message: str


class CBTGuideRequest(BaseModel):
    situation: str
    automatic_thought: str
    emotion: str
    intensity: int = Field(..., ge=1, le=5)


class CBTGuideResponse(BaseModel):
    situation: str
    automatic_thought: str
    emotion: str
    intensity: int
    balanced_thought: str
    suggested_action: str


class SupportRecommendationRequest(BaseModel):
    emotion: str
    stress_level: int = Field(..., ge=1, le=5)
    minutes_available: int = Field(default=3, ge=1, le=10)


class SupportRecommendationResponse(BaseModel):
    emotion: str
    recommended_exercise_slug: str
    reason: str