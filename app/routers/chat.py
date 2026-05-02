from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.entities import User
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services.chat import process_chat_message

router = APIRouter(prefix='/chat', tags=['chat'])


@router.post('/message', response_model=ChatMessageResponse)
async def send_chat_message(
    payload: ChatMessageCreate,
    user: User = Depends(get_current_user),
):
    """
    Recibe un mensaje del estudiante, lo procesa con Ana y devuelve:
    emoción, riesgo, respuesta, acción sugerida y estado visual del avatar.
    """
    return await process_chat_message(payload)