import asyncio
import json
from typing import Any
from fastapi import HTTPException
from google.genai.errors import ClientError

from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services.ai import generate_gemini_reply
from app.services.emotion import analyze_emotion
from app.services.safety import evaluate_safety


CRISIS_REPLY = (
    "Siento mucho que estés pasando por algo tan fuerte. "
    "No tienes que enfrentar esto a solas. Primero vamos a volver al presente: "
    "mira a tu alrededor y nombra mentalmente 5 cosas que puedes ver, "
    "luego 4 cosas que puedes tocar, 3 sonidos que puedes escuchar, "
    "2 cosas que puedes oler y 1 cosa que puedas saborear o sentir en tu respiración. "
    "Después de esta pausa, busca apoyo humano inmediato: una persona de confianza, "
    "Bienestar Universitario o una línea de emergencia. Si estás en peligro inmediato en Colombia, llama al 123."
)


def recommend_from_emotion(emotion: str, intensity: int, minutes_available: int) -> str | None:
    if emotion == "crisis":
        return "conexion-tierra-54321-contactos"

    if emotion == "ansiedad" and intensity >= 4:
        return "respiracion-4-4-4"

    if emotion == "ansiedad":
        return "respiracion-suave"

    if emotion == "estres_academico":
        return "pausa-breve-estudio"

    if emotion == "tristeza":
        return "reestructuracion-pensamientos"

    if emotion == "enojo":
        return "pausa-regulacion-emocional"

    if minutes_available <= 2 and emotion != "neutral":
        return "pausa-breve-estudio"

    return None


def avatar_state_from_result(emotion: str, risk_level: str) -> str:
    """
    Define el estado visual de Ana.
    """
    if risk_level == "alto" or emotion == "crisis":
        return "crisis"

    if emotion in {"ansiedad", "estres_academico", "tristeza", "enojo", "confusion"}:
        return "supportive"

    return "speaking"


def intent_from_result(emotion: str, risk_level: str) -> str:
    """
    Define la intención conversacional para el frontend/documentación.
    """
    if risk_level == "alto" or emotion == "crisis":
        return "crisis_support"

    if emotion == "estres_academico":
        return "academic_support"

    if emotion in {"ansiedad", "tristeza", "enojo", "confusion"}:
        return "emotional_support"

    return "normal_conversation"


async def generate_contextual_reply(
    message: str,
    emotion: str,
    risk_level: str,
    suggested_action: str | None,
    conversation_history: list[dict[str, Any]],
) -> str:
    """
    Usa Gemini como motor conversacional real.
    No usa respuestas locales programadas para conversación normal.
    """

    # La crisis sí se mantiene local por seguridad.
    if risk_level == "alto" or emotion == "crisis":
        return CRISIS_REPLY

    prompt = build_gemini_prompt(
        message=message,
        emotion=emotion,
        risk_level=risk_level,
        suggested_action=suggested_action,
        conversation_history=conversation_history,
    )

    try:
        reply = await asyncio.to_thread(
            generate_gemini_reply,
            prompt,
            emotion,
            suggested_action,
        )

        reply = clean_reply_text(reply.strip()) if reply else ""

        if not reply:
            raise HTTPException(
                status_code=503,
                detail="Gemini no generó respuesta. Revisa la configuración de IA.",
            )

        return reply

    except ClientError as exc:
        status_code = getattr(exc, "status_code", None)

        if status_code == 429:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini está conectado, pero se agotó la cuota disponible "
                    "para este modelo o proyecto. Espera a que se libere la cuota, "
                    "usa otra API key con cuota disponible o habilita facturación."
                ),
            )

        print("[Gemini ClientError]", repr(exc))
        raise HTTPException(
            status_code=503,
            detail="Gemini rechazó la solicitud. Revisa el modelo, la API key o la configuración.",
        )

    except HTTPException:
        raise

    except Exception as exc:
        print("[Gemini ERROR]", repr(exc))
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con Gemini desde el backend.",
        )
def build_gemini_prompt(
    message: str,
    emotion: str,
    risk_level: str,
    suggested_action: str | None,
    conversation_history: list[dict[str, Any]],
) -> str:
    """
    Construye un prompt para que Gemini converse como Ana.
    Ana debe conversar de manera natural, no como plantilla automática.
    """
    history_text = ""

    if conversation_history:
        recent_history = conversation_history[-12:]
        history_text = "\n".join(
            f"{item.get('role', 'user')}: {item.get('content', '')}"
            for item in recent_history
        )

    action_text = suggested_action if suggested_action else "ninguna"

    return f"""
    Eres Ana, una acompañante virtual conversacional del proyecto Hablemos Tantico para estudiantes de la UNAB.

    Ana conversa como una persona cercana, natural y amable.
    Ana NO es psicóloga, NO diagnostica, NO reemplaza a Bienestar Universitario y NO actúa como terapeuta.
    Ana puede hablar de temas cotidianos: el día del estudiante, clases, películas, familia, gustos, cansancio, planes, universidad, cosas buenas o malas del día.

    Estilo de Ana:
    - Habla en español colombiano natural.
    - Suena humana, cálida y genuina.
    - Responde al tema exacto que el estudiante menciona.
    - Si el estudiante cuenta algo feliz, conversa sobre eso con alegría.
    - Si el estudiante cuenta algo triste o ansioso, acompaña con cuidado.
    - No convierte todo en ejercicio emocional.
    - No responde siempre con frases genéricas.
    - No repite "cuéntame más" en cada mensaje.
    - No menciona la emoción detectada salvo que sea necesario.
    - No menciona "acción sugerida".
    - No uses formato JSON.
    - No uses lenguaje clínico.
    - Máximo 4 líneas.
    - Termina con una pregunta natural solo si encaja.

    Datos internos del sistema:
    emotion: {emotion}
    risk_level: {risk_level}
    suggested_action: {action_text}

    Historial reciente:
    {history_text}

    Mensaje actual del estudiante:
    {message}

    Responde únicamente como Ana, de forma natural y conversacional.
    """


def clean_reply_text(reply: str) -> str:
    """
    Limpia textos internos que no deberían mostrarse al usuario.
    Evita frases como: Acción sugerida: None.
    """
    if not reply:
        return ""

    forbidden_lines = [
        "acción sugerida: none",
        "accion sugerida: none",
        "acción sugerida: null",
        "accion sugerida: null",
        "acción sugerida: conversacion-normal",
        "accion sugerida: conversacion-normal",
        "acción sugerida: conversación-normal",
        "accion sugerida: conversación-normal",
    ]

    lines = reply.splitlines()
    cleaned_lines = []

    for line in lines:
        normalized = line.strip().lower()
        if any(forbidden in normalized for forbidden in forbidden_lines):
            continue
        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines).strip()

    cleaned = cleaned.replace("Acción sugerida: None.", "").strip()
    cleaned = cleaned.replace("Accion sugerida: None.", "").strip()
    cleaned = cleaned.replace("Acción sugerida: None", "").strip()
    cleaned = cleaned.replace("Accion sugerida: None", "").strip()

    return cleaned

async def generate_contextual_reply(
    message: str,
    emotion: str,
    risk_level: str,
    suggested_action: str | None,
    conversation_history: list[dict[str, Any]],
) -> str:
    """
    Usa Gemini como motor principal de conversación.
    Las respuestas locales quedan solo como respaldo si Gemini falla.
    """
    if risk_level == "alto" or emotion == "crisis":
        return CRISIS_REPLY

    try:
        prompt = build_gemini_prompt(
            message=message,
            emotion=emotion,
            risk_level=risk_level,
            suggested_action=suggested_action,
            conversation_history=conversation_history,
        )

        reply = await asyncio.to_thread(
            generate_gemini_reply,
            prompt,
            emotion,
            suggested_action,
        )

        reply = clean_reply_text(reply.strip()) if reply else ""

        if reply:
            return reply

        return local_normal_reply(message)

    except Exception:
        return local_normal_reply(message)

async def process_chat_message(payload: ChatMessageCreate) -> ChatMessageResponse:
    """
    Procesa el mensaje del estudiante:
    1. Lee el contexto enviado desde Swagger/frontend.
    2. Analiza emoción con reglas locales.
    3. Evalúa seguridad.
    4. Si hay crisis, responde con ruta segura.
    5. Usa Gemini para generar respuesta contextual.
    6. Devuelve estado del avatar Ana.
    """

    # =========================
    # 1. Leer contexto del mensaje
    # =========================
    raw_context = getattr(payload, "context", None) or {}

    if hasattr(raw_context, "model_dump"):
        context = raw_context.model_dump()
    elif isinstance(raw_context, str):
        try:
            context = json.loads(raw_context)
        except json.JSONDecodeError:
            context = {}
    elif isinstance(raw_context, dict):
        context = raw_context
    else:
        context = {}

    try:
        minutes_available = int(context.get("minutes_available", 3))
    except (TypeError, ValueError):
        minutes_available = 3

    minutes_available = max(1, min(minutes_available, 15))

    allow_history_value = context.get("allow_history", False)

    if isinstance(allow_history_value, str):
        allow_history = allow_history_value.strip().lower() in {"true", "1", "yes", "si", "sí"}
    else:
        allow_history = bool(allow_history_value)

    conversation_history = context.get("conversation_history", [])

    if not isinstance(conversation_history, list):
        conversation_history = []

    # =========================
    # 2. Analizar emoción y seguridad
    # =========================
    emotion_result = analyze_emotion(payload.message)
    safety_result = evaluate_safety(emotion_result)

    emotion = emotion_result.get("emotion", "neutral")
    intensity = int(emotion_result.get("intensity", 1))
    risk_level = safety_result.get("risk_level", "bajo")

    # Si la emoción detectada es muy genérica y no hay riesgo,
    # la tratamos como conversación normal.
    if emotion in {"confusion", "desconocido", "none", "sin_detectar", ""} and risk_level == "bajo":
        emotion = "neutral"
        intensity = 1

    # Saludos y conversación cotidiana no deben activar apoyo emocional.
    casual_messages = {
        "hola",
        "holaa",
        "buenas",
        "buenos dias",
        "buenos días",
        "buenas tardes",
        "buenas noches",
        "hey",
        "ola",
        "qué más",
        "que mas",
    }

    if payload.message.strip().lower() in casual_messages and risk_level == "bajo":
        emotion = "neutral"
        intensity = 1

    # =========================
    # 3. Recomendar acción
    # =========================
    suggested_action = recommend_from_emotion(
        emotion=emotion,
        intensity=intensity,
        minutes_available=minutes_available,
    )

    if emotion == "neutral" and risk_level == "bajo":
        suggested_action = None

    # =========================
    # 4. Estado visual e intención
    # =========================
    avatar_state = avatar_state_from_result(
        emotion=emotion,
        risk_level=risk_level,
    )

    intent = intent_from_result(
        emotion=emotion,
        risk_level=risk_level,
    )

    # =========================
    # 5. Generar respuesta con Gemini o respaldo local
    # =========================
    reply = await generate_contextual_reply(
        message=payload.message,
        emotion=emotion,
        risk_level=risk_level,
        suggested_action=suggested_action,
        conversation_history=conversation_history,
    )

    # =========================
    # 6. Forzar protocolo seguro si hay crisis
    # =========================
    if risk_level == "alto" or emotion == "crisis":
        suggested_action = "conexion-tierra-54321-contactos"
        avatar_state = "crisis"
        intent = "crisis_support"
        allow_history = False

    return ChatMessageResponse(
        emotion=emotion,
        risk_level=risk_level,
        reply=reply,
        suggested_action=suggested_action,
        save_history=allow_history,
        avatar_state=avatar_state,
        intent=intent,
        voice_text=reply,
    )