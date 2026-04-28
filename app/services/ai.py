from google import genai
from google.genai import types

from app.core.config import get_settings

settings = get_settings()


SYSTEM_PROMPT = """
Eres Hablemos Tantico, un chatbot de apoyo emocional y autocuidado para estudiantes de la Universidad Autónoma de Bucaramanga.

Tu objetivo es escuchar, validar emociones y sugerir acciones breves de autocuidado.
No eres psicólogo, no diagnosticas, no reemplazas terapia y no das instrucciones clínicas.

Estilo de respuesta:
- Cercano, amable y respetuoso.
- Claro y breve.
- Con lenguaje natural colombiano de forma moderada.
- Máximo 5 a 7 líneas.
- Primero valida la emoción.
- Luego sugiere una acción concreta de 1 a 5 minutos.
- No prometas curas.
- No pidas datos personales innecesarios.
- No generes dependencia emocional.

Si detectas riesgo de autolesión, crisis o peligro inmediato, no continúes una conversación normal.
En ese caso recomienda buscar apoyo inmediato con alguien de confianza, Bienestar Universitario o una línea de emergencia disponible.
"""


def generate_template_reply(emotion: str, suggested_action: str) -> str:
    templates = {
        'ansiedad': (
            'Entiendo que te estés sintiendo así. Cuando la ansiedad sube, '
            'todo puede sentirse más grande y difícil de manejar. Vamos con algo pequeño: '
            'haz una pausa breve, respira con calma y luego toma una sola acción.'
        ),
        'estres_academico': (
            'Suena a que tienes muchas cosas encima y eso puede saturar bastante. '
            'No tienes que resolverlo todo al mismo tiempo. Elige una tarea pequeña, '
            'trabaja unos minutos y después haces una pausa corta.'
        ),
        'tristeza': (
            'Siento que estés pasando por este momento. No tienes que exigirte estar bien de inmediato. '
            'Podemos empezar con algo sencillo: respirar, tomar agua o escribir en una frase qué necesitas ahora.'
        ),
        'confusion': (
            'Gracias por contarlo. A veces no saber exactamente qué sentimos también pesa. '
            'Podemos empezar identificando si lo que más aparece ahora es miedo, presión, tristeza o cansancio.'
        ),
    }

    base = templates.get(emotion, templates['confusion'])
    return f'{base} Acción sugerida: {suggested_action}.'


def generate_gemini_reply(user_message: str, emotion: str, suggested_action: str) -> str:
    if not settings.AI_ENABLED or not settings.GEMINI_API_KEY:
        return generate_template_reply(emotion, suggested_action)

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = f"""
Mensaje del estudiante:
{user_message}

Emoción detectada por el sistema:
{emotion}

Acción sugerida por el sistema:
{suggested_action}

Genera una respuesta empática, breve, no clínica y segura.
No diagnostiques.
No digas que eres psicólogo.
No reemplaces a Bienestar Universitario.
"""

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
                max_output_tokens=220,
            ),
        )

        if not response.text:
            return generate_template_reply(emotion, suggested_action)

        return response.text.strip()

    except Exception:
        return generate_template_reply(emotion, suggested_action)