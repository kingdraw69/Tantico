from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import Exercise, User
from app.schemas.support import (
    SupportRecommendationRequest,
    SupportRecommendationResponse,
    SupportToolResponse,
)
from app.services.support import (
    get_motivational_phrase,
    get_tcc_prompt,
    select_support_tool,
)

router = APIRouter(prefix='/support', tags=['support'])


@router.get('/tools', response_model=list[SupportToolResponse])
async def list_support_tools(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Exercise)
        .where(Exercise.is_active.is_(True))
        .order_by(Exercise.category, Exercise.title)
    )

    exercises = result.scalars().all()

    return [
        SupportToolResponse(
            slug=item.slug,
            title=item.title,
            category=item.category,
            duration_minutes=item.duration_minutes,
            description=item.description,
            steps=item.steps,
        )
        for item in exercises
    ]


@router.get('/tools/{slug}', response_model=SupportToolResponse)
async def get_support_tool(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Exercise).where(
            Exercise.slug == slug,
            Exercise.is_active.is_(True),
        )
    )

    exercise = result.scalar_one_or_none()

    if not exercise:
        raise HTTPException(status_code=404, detail='Herramienta no encontrada')

    return SupportToolResponse(
        slug=exercise.slug,
        title=exercise.title,
        category=exercise.category,
        duration_minutes=exercise.duration_minutes,
        description=exercise.description,
        steps=exercise.steps,
    )


@router.post('/recommendation', response_model=SupportRecommendationResponse)
async def recommend_support_tool(
    payload: SupportRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Exercise).where(Exercise.is_active.is_(True))
    )

    exercises = list(result.scalars().all())

    selected_tool = select_support_tool(
        emotion=payload.emotion,
        intensity=payload.intensity,
        minutes_available=payload.minutes_available,
        exercises=exercises,
    )

    if not selected_tool:
        raise HTTPException(
            status_code=404,
            detail='No hay herramientas disponibles para esta emoción',
        )

    return SupportRecommendationResponse(
        emotion=payload.emotion,
        recommended_tool=SupportToolResponse(
            slug=selected_tool.slug,
            title=selected_tool.title,
            category=selected_tool.category,
            duration_minutes=selected_tool.duration_minutes,
            description=selected_tool.description,
            steps=selected_tool.steps,
        ),
        motivational_phrase=get_motivational_phrase(payload.emotion),
        tcc_prompt=get_tcc_prompt(payload.emotion),
    )