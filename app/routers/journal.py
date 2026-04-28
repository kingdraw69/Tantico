from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import JournalEntry, User
from app.schemas.journal import JournalEntryCreate, JournalEntryRead

router = APIRouter(prefix='/journal', tags=['journal'])


@router.post('', response_model=JournalEntryRead)
async def create_journal_entry(
    payload: JournalEntryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = JournalEntry(
        user_id=user.id,
        title=payload.title,
        body=payload.body,
        tags=','.join(payload.tags) if payload.tags else None,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    return JournalEntryRead(
        id=entry.id,
        title=entry.title,
        body=entry.body,
        tags=payload.tags,
        created_at=entry.created_at,
    )


@router.get('', response_model=list[JournalEntryRead])
async def list_journal_entries(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == user.id)
        .order_by(desc(JournalEntry.created_at))
    )
    entries = result.scalars().all()
    return [
        JournalEntryRead(
            id=entry.id,
            title=entry.title,
            body=entry.body,
            tags=entry.tags.split(',') if entry.tags else [],
            created_at=entry.created_at,
        )
        for entry in entries
    ]


@router.delete('/{entry_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JournalEntry).where(JournalEntry.id == entry_id, JournalEntry.user_id == user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail='Entrada no encontrada')
    await db.delete(entry)
    await db.commit()
