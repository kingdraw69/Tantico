import json
from typing import Any

from app.core.config import settings


def _safe_json_loads(text: str) -> dict[str, Any] | None:
    try:
        clean = text.strip()

        if clean.startswith("```json"):
            clean = clean.replace("```json", "", 1).strip()

        if clean.startswith("```"):
            clean = clean.replace("```", "", 1).strip()

        if clean.endswith("```"):
            clean = clean[:-3].strip()

        return json.loads(clean)
    except Exception:
        return None


def _fallback_analysis(message: str) -> dict[str, Any]:
    text = message.lower()

    crisis_words = [
        "no quiero vivir",
        "hacerme daño",
        "suicid",
        "morirme",
        "quitarme la vida",
        "lastimarme",
    ]

    anxiety_words = [
        "ansioso",
        "ansiosa",
        "ansiedad",
        "nervioso",
        "nerviosa",
        "parcial",
        "examen",
        "exposición",
        "exposicion",
        "entrega",
    ]

    stress_words = [
        "estresado",
        "estresada",
        "estrés",
        "estres",
        "cansado",
        "cansada",
        "saturado",
        "saturada",
        "no sé por dónde empezar",
    ]

    sadness_words = [
        "triste",
        "sin ganas",
        "desmotivado",
        "desmotivada",
        "solo",
        "sola",
        "llorar",
    ]

    if any(word in text for word in crisis_words):
        return {
            "emotion": "crisis",
            "risk_level": "alto",
            "intent": "crisis_support",
            "suggested_action": "conexion-tierra-54321-contactos",
            "avatar_state": "crisis",
            "reply": (
                "Siento mucho que estés pasando por algo tan fuerte. "
                "No tienes que manejar esto a solas. Vamos primero a ubicarnos en el presente: "
                "mira a tu alrededor y dime mentalmente 5 cosas que puedes ver. Después busca a una persona de confianza "
                "o comunícate con una línea de emergencia."
            ),
        }

    if any(word in text for word in anxiety_words):
        return {
            "emotion": "ansiedad",
            "risk_level": "medio",
            "intent": "emotional_support",
            "suggested_action": "respiracion-4-4-4",
            "avatar_state": "supportive",
            "reply": (
                "Entiendo que te sientas así. Cuando aparece ansiedad, la mente intenta adelantarse a todo lo que podría salir mal. "
                "Vamos paso a paso: respira conmigo 4 segundos, sostén 4 y suelta 4. Después nos enfocamos solo en la siguiente acción pequeña."
            ),
        }

    if any(word in text for word in stress_words):
        return {
            "emotion": "estres_academico",
            "risk_level": "medio",
            "intent": "academic_support",
            "suggested_action": "pausa-breve-organizacion",
            "avatar_state": "supportive",
            "reply": (
                "Suena a que tienes varias cosas encima. Hagámoslo más liviano: elige una sola tarea, "
                "la más urgente o la más pequeña, y dale 10 minutos. No necesitas resolver todo ahora."
            ),
        }

    if any(word in text for word in sadness_words):
        return {
            "emotion": "tristeza",
            "risk_level": "bajo",
            "intent": "emotional_support",
            "suggested_action": "diario-rapido-emocional",
            "avatar_state": "supportive",
            "reply": (
                "Gracias por contármelo. A veces estar triste también necesita espacio y cuidado. "
                "Podemos empezar suave: escribe una frase sobre lo que sientes y una cosa pequeña que podrías hacer por ti hoy."
            ),
        }

    return {
        "emotion": "neutral",
        "risk_level": "bajo",
        "intent": "normal_conversation",
        "suggested_action": None,
        "avatar_state": "speaking",
        "reply": (
            "Te escucho. Cuéntame un poquito más para entenderte mejor. "
            "Podemos conversar con calma y, si aparece algo que te esté pesando, buscamos una acción sencilla."
        ),
    }


def analyze_message_with_gemini(
    message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Analiza emoción, riesgo e intención usando Gemini.
    Si Gemini no está activo o falla, usa reglas locales.
    """

    if not settings.AI_ENABLED or not settings.GEMINI_API_KEY:
        return _fallback_analysis(message)

    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        history_text = ""
        if conversation_history:
            limited_history = conversation_history[-10:]
            history_text = "\n".join(
                f"{item.get('role', 'user')}: {item.get('content', '')}"
                for item in limited_history
            )

        prompt = f"""
Eres Ana, un avatar de apoyo emocional para estudiantes universitarios de la UNAB.
Tu tarea es analizar el mensaje del estudiante y responder de forma empática, breve y segura.

Reglas importantes:
- No diagnostiques.
- No digas que eres psicóloga.
- No reemplaces atención profesional.
- Si detectas autolesión, suicidio, daño a sí mismo o riesgo alto, activa respuesta de crisis.
- Si no detectas una emoción clara o crítica, continúa la conversación de forma natural.
- La conversación normal debe poder sostenerse durante 5 a 10 minutos con preguntas suaves.
- Mantén tono colombiano, cercano, cálido y respetuoso.
- Recomienda acciones concretas solo cuando sean útiles.
- En crisis, primero guía conexión a tierra y luego sugiere buscar ayuda humana o emergencia.

Historial reciente:
{history_text}

Mensaje actual:
{message}

Devuelve SOLO JSON válido con esta estructura:
{{
  "emotion": "neutral | ansiedad | estres_academico | tristeza | confusion | enojo | crisis",
  "risk_level": "bajo | medio | alto",
  "intent": "normal_conversation | emotional_support | academic_support | crisis_support",
  "suggested_action": "respiracion-4-4-4 | grounding-54321 | diario-rapido-emocional | pausa-breve-organizacion | contacto-emergencia | null",
  "avatar_state": "speaking | supportive | crisis",
  "reply": "respuesta breve de Ana"
}}
"""

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        data = _safe_json_loads(response.text or "")

        if not data:
            return _fallback_analysis(message)

        return {
            "emotion": data.get("emotion", "neutral"),
            "risk_level": data.get("risk_level", "bajo"),
            "intent": data.get("intent", "normal_conversation"),
            "suggested_action": data.get("suggested_action"),
            "avatar_state": data.get("avatar_state", "speaking"),
            "reply": data.get("reply") or _fallback_analysis(message)["reply"],
        }

    except Exception:
        return _fallback_analysis(message)