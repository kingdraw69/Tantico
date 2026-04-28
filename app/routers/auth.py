from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.entities import User
from app.schemas.auth import GuestLoginResponse, OAuthVerifyRequest, OAuthVerifyResponse

router = APIRouter(prefix='/auth', tags=['auth'])
settings = get_settings()


@router.post('/guest', response_model=GuestLoginResponse)
async def login_as_guest(db: AsyncSession = Depends(get_db)) -> GuestLoginResponse:
    user = User(is_guest=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({'sub': user.id, 'is_guest': True})
    return GuestLoginResponse(access_token=token, user_id=user.id)


@router.post('/oauth/verify', response_model=OAuthVerifyResponse)
async def verify_oauth_token(
    payload: OAuthVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> OAuthVerifyResponse:
    if not settings.ALLOW_DEV_AUTH:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail='La verificación real OAuth/OIDC aún no está configurada en este entorno.',
        )

    if payload.provider != 'dev':
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail='Por ahora solo existe el proveedor dev para pruebas locales.',
        )

    if not payload.email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Para el proveedor dev debes enviar un correo en el campo email.',
        )

    stmt = select(User).where(User.email == payload.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            is_guest=False,
            email=payload.email,
            display_name=payload.display_name,
            provider=payload.provider,
            provider_sub=f'dev::{payload.email}',
            allow_sync=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        changed = False
        if not user.display_name and payload.display_name:
            user.display_name = payload.display_name
            changed = True
        if not user.provider:
            user.provider = payload.provider
            changed = True
        if not user.provider_sub:
            user.provider_sub = f'dev::{payload.email}'
            changed = True
        if changed:
            await db.commit()
            await db.refresh(user)

    token = create_access_token({'sub': user.id, 'is_guest': False})
    return OAuthVerifyResponse(
        access_token=token,
        user_id=user.id,
        is_guest=False,
        provider=payload.provider,
    )
