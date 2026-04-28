from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import CrisisEvent, User
from app.schemas.crisis import CrisisEvaluateRequest, CrisisEvaluateResponse
from app.services.crisis import evaluate_crisis_text

router = APIRouter(prefix='/crisis', tags=['crisis'])
settings = get_settings()


@router.post('/evaluate', response_model=CrisisEvaluateResponse)
async def evaluate_crisis(
    payload: CrisisEvaluateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    is_crisis, detected = evaluate_crisis_text(payload.text)

    if is_crisis:
        event = CrisisEvent(user_id=user.id, trigger_text=payload.text, severity='high')
        db.add(event)
        await db.commit()

    message = (
        'Detectamos señales de crisis. Busca apoyo inmediato y usa el recurso institucional configurado.'
        if is_crisis
        else 'No se detectaron palabras críticas, pero puedes usar ejercicios breves o pedir ayuda.'
    )

    return CrisisEvaluateResponse(
        is_crisis=is_crisis,
        severity='high' if is_crisis else 'low',
        detected_keywords=detected,
        help_resource_name=settings.HELP_RESOURCE_NAME,
        help_resource_url=settings.HELP_RESOURCE_URL,
        message=message,
    )
