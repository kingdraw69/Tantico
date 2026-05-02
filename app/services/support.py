from app.models.entities import Exercise


MOTIVATIONAL_PHRASES = {
    'ansiedad': [
        'Vamos paso a paso. No necesitas resolver todo ahora, solo regular un poco tu cuerpo.',
        'Lo que sientes es difícil, pero este momento puede bajar de intensidad con una pausa breve.',
        'Respira conmigo un momento. Primero calma el cuerpo, luego organizamos la mente.',
    ],
    'estres_academico': [
        'No tienes que hacerlo todo al mismo tiempo. Una tarea pequeña también cuenta como avance.',
        'Organizar el siguiente paso puede ser más útil que exigirte resolverlo todo hoy.',
        'Tu esfuerzo vale, incluso cuando el día se siente pesado.',
    ],
    'tristeza': [
        'No tienes que forzarte a estar bien de inmediato. Empezar con algo pequeño también es cuidarte.',
        'Está bien sentirte así. Hoy puedes darte un trato más amable.',
        'Un paso suave también es un paso. No estás fallando por necesitar una pausa.',
    ],
    'confusion': [
        'No saber exactamente qué sientes también es válido. Podemos empezar nombrando lo que aparece.',
        'Vamos con calma. A veces entender la emoción toma unos minutos.',
        'No necesitas tener todas las respuestas ahora; basta con observar qué está pasando dentro de ti.',
    ],
    'calma': [
        'Qué bueno que estés en un momento más tranquilo. Puedes aprovecharlo para cuidar tu energía.',
        'Mantener pequeñas pausas también ayuda a prevenir la sobrecarga.',
        'Este es un buen momento para reforzar hábitos que te ayuden después.',
    ],
    'crisis': [
        'Tu seguridad es lo primero. No tienes que atravesar esto a solas.',
    ],
}


TCC_PROMPTS = {
    'ansiedad': (
        'Guía TCC breve: escribe el pensamiento que te preocupa, por ejemplo: '
        '"me va a ir mal". Luego pregúntate: ¿qué evidencia tengo?, '
        '¿qué otra explicación más equilibrada podría existir?'
    ),
    'estres_academico': (
        'Guía TCC breve: identifica el pensamiento de presión, por ejemplo: '
        '"no voy a alcanzar". Luego conviértelo en una acción concreta: '
        '"durante 15 minutos haré solo el primer punto".'
    ),
    'tristeza': (
        'Guía TCC breve: escribe qué te estás diciendo a ti mismo en este momento. '
        'Después intenta responderte como le responderías a un amigo que quieres cuidar.'
    ),
    'confusion': (
        'Guía TCC breve: intenta completar esta frase: '
        '"ahora mismo siento ___ porque estoy pensando ___".'
    ),
    'calma': (
        'Guía TCC breve: identifica qué acción te ayudó a estar mejor y cómo podrías repetirla esta semana.'
    ),
}


def get_motivational_phrase(emotion: str) -> str:
    phrases = MOTIVATIONAL_PHRASES.get(emotion, MOTIVATIONAL_PHRASES['confusion'])
    return phrases[0]


def get_tcc_prompt(emotion: str) -> str | None:
    if emotion == 'crisis':
        return None

    return TCC_PROMPTS.get(emotion, TCC_PROMPTS['confusion'])


def select_support_tool(
    emotion: str,
    intensity: int,
    minutes_available: int,
    exercises: list[Exercise],
) -> Exercise | None:
    available_by_slug = {exercise.slug: exercise for exercise in exercises}

    if emotion == 'crisis':
        return available_by_slug.get('contacto-bienestar')

    if emotion == 'ansiedad' and intensity >= 4:
        if minutes_available <= 2:
            return available_by_slug.get('respiracion-4-4-4')
        return available_by_slug.get('respiracion-4-7-8') or available_by_slug.get('respiracion-4-4-4')

    if emotion == 'estres_academico':
        return available_by_slug.get('pausa-breve-estudio')

    if emotion == 'tristeza':
        return available_by_slug.get('reestructuracion-pensamientos')

    if emotion == 'confusion':
        return available_by_slug.get('anclaje-5-sentidos')

    if emotion == 'calma':
        return available_by_slug.get('pausa-consciente')

    return available_by_slug.get('anclaje-5-sentidos')