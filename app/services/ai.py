from google import genai

from app.core.config import settings


def generate_gemini_reply(
    prompt: str,
    emotion: str | None = None,
    suggested_action: str | None = None,
) -> str:
    """
    Genera una respuesta usando Gemini.
    No devuelve respuestas programadas.
    """

    if not settings.AI_ENABLED:
        raise RuntimeError("AI_ENABLED está en false. Actívalo en el archivo .env")

    if not settings.GEMINI_API_KEY:
        raise RuntimeError("No hay GEMINI_API_KEY configurada en el archivo .env")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini respondió vacío.")

    return response.text.strip()