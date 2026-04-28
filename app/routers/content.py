from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.entities import Exercise
from app.schemas.content import ExerciseRead

router = APIRouter(prefix='/content', tags=['content'])


@router.get('/exercises', response_model=list[ExerciseRead])
async def list_exercises(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exercise).where(Exercise.is_active.is_(True)).order_by(Exercise.title))
    return [ExerciseRead.model_validate(item) for item in result.scalars().all()]
