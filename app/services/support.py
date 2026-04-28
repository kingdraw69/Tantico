def get_motivational_message(emotion: str, context: str | None = None) -> str:
    emotion = emotion.lower()

    if emotion in {"ansiedad", "nervios"}:
        return (
            "Respira un momento. Sentirte nervioso no significa que no puedas hacerlo; "
            "significa que esto te importa. Vamos paso a paso."
        )

    if emotion in {"estres", "estres_academico"}:
        return (
            "Tienes muchas cosas encima, pero no tienes que resolver todo al mismo tiempo. "
            "Elige una sola tarea pequeña y empieza por ahí."
        )

    if emotion == "tristeza":
        return (
            "Lamento que te estés sintiendo así. No tienes que exigirte estar bien de inmediato. "
            "Haz algo pequeño por ti ahora: respirar, tomar agua o escribir lo que sientes."
        )

    if emotion == "confusion":
        return (
            "No tener claridad en este momento no significa que estés perdido. "
            "Puedes ordenar tus ideas empezando por una pregunta sencilla: ¿qué necesito primero?"
        )

    return (
        "Estoy contigo en este momento. Hagamos una pausa breve y busquemos una acción pequeña "
        "que puedas realizar ahora."
    )


def recommend_support_action(emotion: str, stress_level: int, minutes_available: int) -> tuple[str, str]:
    emotion = emotion.lower()

    if stress_level >= 4 or emotion in {"ansiedad", "nervios"}:
        return (
            "respiracion-4-4-4",
            "Se recomienda respiración guiada porque hay señales de ansiedad o activación emocional alta."
        )

    if emotion in {"estres", "estres_academico"}:
        return (
            "pausa-breve-estudio",
            "Se recomienda una pausa breve porque el malestar está asociado a carga académica."
        )

    if emotion == "tristeza":
        return (
            "reestructuracion-pensamientos",
            "Se recomienda una guía TCC breve para revisar pensamientos negativos."
        )

    if minutes_available <= 2:
        return (
            "respiracion-4-4-4",
            "Se recomienda un ejercicio corto porque el usuario tiene poco tiempo disponible."
        )

    return (
        "anclaje-5-sentidos",
        "Se recomienda grounding para volver al presente y reducir saturación mental."
    )


def generate_cbt_guide(
    situation: str,
    automatic_thought: str,
    emotion: str,
    intensity: int,
) -> dict:
    thought_lower = automatic_thought.lower()

    if "no puedo" in thought_lower or "voy a perder" in thought_lower:
        balanced = (
            "Estoy teniendo un pensamiento muy duro conmigo mismo. "
            "Aunque la situación sea difícil, puedo prepararme por partes y avanzar con una acción concreta."
        )
    elif "todo" in thought_lower or "nada" in thought_lower:
        balanced = (
            "Quizás estoy viendo la situación en extremos. "
            "Puedo buscar una forma más equilibrada de entender lo que está pasando."
        )
    else:
        balanced = (
            "Este pensamiento refleja cómo me siento ahora, pero no necesariamente define toda la realidad. "
            "Puedo observarlo con calma y elegir una respuesta más útil."
        )

    return {
        "situation": situation,
        "automatic_thought": automatic_thought,
        "emotion": emotion,
        "intensity": intensity,
        "balanced_thought": balanced,
        "suggested_action": "Elige una acción pequeña para los próximos 5 minutos: respirar, organizar una tarea o pedir apoyo.",
    }