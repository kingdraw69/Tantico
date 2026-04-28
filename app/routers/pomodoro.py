from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import PomodoroSession, User
from app.schemas.pomodoro import PomodoroSessionCreate, PomodoroSessionRead

router = APIRouter(prefix='/pomodoro', tags=['pomodoro'])


@router.post('', response_model=PomodoroSessionRead)
async def create_pomodoro_session(
    payload: PomodoroSessionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = PomodoroSession(
        user_id=user.id,
        focus_minutes=payload.focus_minutes,
        break_minutes=payload.break_minutes,
        cycles_completed=payload.cycles_completed,
        note=payload.note,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return PomodoroSessionRead.model_validate(session)


@router.get('', response_model=list[PomodoroSessionRead])
async def list_pomodoro_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PomodoroSession)
        .where(PomodoroSession.user_id == user.id)
        .order_by(desc(PomodoroSession.created_at))
    )
    return [PomodoroSessionRead.model_validate(item) for item in result.scalars().all()]
