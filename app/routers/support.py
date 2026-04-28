from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import User
from app.schemas.support import (
    MotivationRequest,
    MotivationResponse,
    CBTGuideRequest,
    CBTGuideResponse,
    SupportRecommendationRequest,
    SupportRecommendationResponse,
)
from app.services.support import (
    get_motivational_message,
    recommend_support_action,
    generate_cbt_guide,
)

router = APIRouter(prefix="/support", tags=["support"])


@router.post("/motivation", response_model=MotivationResponse)
async def motivation(
    payload: MotivationRequest,
    user: User = Depends(get_current_user),
):
    message = get_motivational_message(payload.emotion, payload.context)

    return MotivationResponse(
        emotion=payload.emotion,
        message=message,
    )


@router.post("/recommendation", response_model=SupportRecommendationResponse)
async def support_recommendation(
    payload: SupportRecommendationRequest,
    user: User = Depends(get_current_user),
):
    slug, reason = recommend_support_action(
        emotion=payload.emotion,
        stress_level=payload.stress_level,
        minutes_available=payload.minutes_available,
    )

    return SupportRecommendationResponse(
        emotion=payload.emotion,
        recommended_exercise_slug=slug,
        reason=reason,
    )


@router.post("/cbt-guide", response_model=CBTGuideResponse)
async def cbt_guide(
    payload: CBTGuideRequest,
    user: User = Depends(get_current_user),
):
    result = generate_cbt_guide(
        situation=payload.situation,
        automatic_thought=payload.automatic_thought,
        emotion=payload.emotion,
        intensity=payload.intensity,
    )

    return CBTGuideResponse(**result)