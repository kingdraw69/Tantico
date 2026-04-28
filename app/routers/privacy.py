from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import User
from app.schemas.privacy import PrivacyDeleteResponse

router = APIRouter(prefix='/privacy', tags=['privacy'])


@router.post('/delete', response_model=PrivacyDeleteResponse)
async def delete_my_data(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted_user_id = user.id
    await db.delete(user)
    await db.commit()
    return PrivacyDeleteResponse(
        message='Tus datos fueron eliminados correctamente.',
        deleted_user_id=deleted_user_id,
    )
