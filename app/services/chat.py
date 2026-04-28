import asyncio

from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services.ai import generate_gemini_reply
from app.services.emotion import analyze_emotion
from app.services.safety import evaluate_safety


def recommend_from_emotion(emotion: str, intensity: int, minutes_available: int) -> str:
    if emotion == 'ansiedad' and intensity >= 4:
        return 'respiracion-4-4-4'

    if emotion == 'estres_academico':
        return 'pausa-breve-estudio'

    if emotion == 'tristeza':
        return 'reestructuracion-pensamientos'

    if minutes_available <= 2:
        return 'pausa-breve-estudio'

    return 'anclaje-5-sentidos'


async def process_chat_message(payload: ChatMessageCreate) -> ChatMessageResponse:
    emotion_result = analyze_emotion(payload.message)
    safety_result = evaluate_safety(emotion_result)

    if safety_result['risk_level'] == 'alto':
        return ChatMessageResponse(
            emotion=emotion_result['emotion'],
            risk_level='alto',
            reply=(
                'Siento mucho que estés pasando por algo tan fuerte. '
                'En este momento es importante que no lo enfrentes a solas. '
                'Busca apoyo inmediato con alguien de confianza, Bienestar Universitario '
                'o una línea de emergencia disponible en tu ciudad. Tu seguridad es lo primero.'
            ),
            suggested_action='activar_ruta_crisis',
            save_history=False,
        )

    suggested_action = recommend_from_emotion(
        emotion=emotion_result['emotion'],
        intensity=emotion_result['intensity'],
        minutes_available=payload.context.minutes_available,
    )

    reply = await asyncio.to_thread(
        generate_gemini_reply,
        payload.message,
        emotion_result['emotion'],
        suggested_action,
    )

    return ChatMessageResponse(
        emotion=emotion_result['emotion'],
        risk_level=safety_result['risk_level'],
        reply=reply,
        suggested_action=suggested_action,
        save_history=payload.context.allow_history,
    )