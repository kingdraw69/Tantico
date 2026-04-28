def analyze_emotion(message: str) -> dict:
    text = message.lower().strip()

    crisis_keywords = [
        'hacerme daño',
        'no quiero vivir',
        'me quiero matar',
        'suicidio',
        'suicidarme',
        'autolesion',
        'autolesión',
        'lastimarme',
        'desaparecer',
        'no aguanto mas',
        'no aguanto más',
    ]

    anxiety_keywords = [
        'ansioso',
        'ansiosa',
        'ansiedad',
        'nervioso',
        'nerviosa',
        'pánico',
        'panico',
        'me bloqueo',
        'no puedo respirar',
        'me falta el aire',
        'me va a ir mal',
    ]

    stress_keywords = [
        'parcial',
        'entrega',
        'exposición',
        'exposicion',
        'no alcanzo',
        'muchas tareas',
        'trabajos',
        'saturado',
        'saturada',
        'no sé por dónde empezar',
        'no se por donde empezar',
    ]

    sadness_keywords = [
        'triste',
        'sin ganas',
        'desmotivado',
        'desmotivada',
        'vacío',
        'vacio',
        'llorar',
        'cansado de todo',
        'cansada de todo',
    ]

    if any(keyword in text for keyword in crisis_keywords):
        return {'emotion': 'crisis', 'intensity': 5}

    if any(keyword in text for keyword in anxiety_keywords):
        return {'emotion': 'ansiedad', 'intensity': 4}

    if any(keyword in text for keyword in stress_keywords):
        return {'emotion': 'estres_academico', 'intensity': 3}

    if any(keyword in text for keyword in sadness_keywords):
        return {'emotion': 'tristeza', 'intensity': 3}

    return {'emotion': 'confusion', 'intensity': 2}