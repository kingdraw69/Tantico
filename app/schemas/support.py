from typing import Literal

from pydantic import BaseModel, Field


class SupportRecommendationRequest(BaseModel):
    emotion: Literal[
        'ansiedad',
        'estres_academico',
        'tristeza',
        'confusion',
        'calma',
        'crisis'
    ]
    intensity: int = Field(default=3, ge=1, le=5)
    minutes_available: int = Field(default=3, ge=1, le=15)


class SupportToolResponse(BaseModel):
    slug: str
    title: str
    category: str
    duration_minutes: int
    description: str
    steps: str


class SupportRecommendationResponse(BaseModel):
    emotion: str
    recommended_tool: SupportToolResponse
    motivational_phrase: str
    tcc_prompt: str | None = None