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

def exercise_to_response(item: Exercise) -> SupportToolResponse:
    return SupportToolResponse(
        slug=item.slug,
        title=item.title,
        category=item.category,
        duration_minutes=item.duration_minutes,
        description=item.description,
        steps=item.steps,
    )

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
        exercise_to_response(item)
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

    return exercise_to_response(exercise)


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
        recommended_tool=exercise_to_response(selected_tool),
        motivational_phrase=get_motivational_phrase(payload.emotion),
        tcc_prompt=get_tcc_prompt(payload.emotion),
    )
@router.post('/panic')
async def activate_panic_button(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    panic_slugs = [
        'conexion-tierra-54321-contactos',
        'respiracion-4-4-4',
        'frase-motivacional',
        'reestructuracion-pensamientos',
    ]

    result = await db.execute(
        select(Exercise).where(
            Exercise.slug.in_(panic_slugs),
            Exercise.is_active.is_(True),
        )
    )

    exercises = list(result.scalars().all())

    ordered_exercises = sorted(
        exercises,
        key=lambda item: panic_slugs.index(item.slug) if item.slug in panic_slugs else 999,
    )

    return {
        'panic_mode': True,
        'message': (
            'Estoy contigo. Vamos a hacer una pausa segura primero. '
            'Sigue estos ejercicios despacio. Si estás en peligro inmediato, '
            'busca ayuda humana ahora mismo o llama al 123 en Colombia.'
        ),
        'exercises': [
            exercise_to_response(item).model_dump()
            for item in ordered_exercises
        ],
        'motivational_phrase': (
            'No tienes que resolver todo en este momento. Primero respira, '
            'vuelve al presente y busca apoyo si lo necesitas.'
        ),
        'tcc_prompt': (
            'Pregunta guía: ¿lo que estoy pensando ahora es un hecho confirmado '
            'o una interpretación nacida del miedo o la angustia?'
        ),
        'help_resource': {
            'name': 'Bienestar Universitario UNAB',
            'emergency': '123 Colombia',
        },
    }