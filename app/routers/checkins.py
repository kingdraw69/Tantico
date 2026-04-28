from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import Exercise, MoodCheckIn, User
from app.schemas.checkin import MoodCheckInCreate, MoodCheckInRead
from app.services.recommendation import recommend_exercise_slugs

router = APIRouter(prefix='/checkins', tags=['checkins'])


@router.post('', response_model=dict)
async def create_checkin(
    payload: MoodCheckInCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    checkin = MoodCheckIn(
        user_id=user.id,
        mood_score=payload.mood_score,
        stress_score=payload.stress_score,
        note=payload.note,
    )
    db.add(checkin)
    await db.commit()
    await db.refresh(checkin)

    exercises_result = await db.execute(select(Exercise).where(Exercise.is_active.is_(True)))
    exercises = exercises_result.scalars().all()
    recommended = recommend_exercise_slugs(checkin, exercises)

    return {
        'checkin': MoodCheckInRead.model_validate(checkin),
        'recommended_exercise_slugs': recommended,
    }


@router.get('', response_model=list[MoodCheckInRead])
async def list_checkins(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MoodCheckIn).where(MoodCheckIn.user_id == user.id).order_by(desc(MoodCheckIn.created_at))
    )
    return [MoodCheckInRead.model_validate(item) for item in result.scalars().all()]
