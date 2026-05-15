from typing import Any


GUIDED_EXERCISES: dict[str, dict[str, Any]] = {
    "respiracion-4-4-4": {
        "slug": "respiracion-4-4-4",
        "title": "Respiración 4-4-4",
        "category": "respiracion",
        "duration_minutes": 2,
        "description": "Ejercicio breve para bajar la activación física y volver al presente.",
        "steps": [
            "Si puedes, siéntate con la espalda apoyada.",
            "Inhala lentamente por la nariz contando hasta 4.",
            "Mantén el aire contando hasta 4.",
            "Exhala despacio por la boca contando hasta 4.",
            "Repite este ciclo durante 1 o 2 minutos.",
        ],
        "closing_message": "Muy bien. No tienes que resolver todo ahora; solo vuelve de a poquito al presente.",
    },
    "respiracion-suave": {
        "slug": "respiracion-suave",
        "title": "Respiración suave",
        "category": "respiracion",
        "duration_minutes": 1,
        "description": "Pausa corta para recuperar calma sin forzarte.",
        "steps": [
            "Suelta los hombros.",
            "Inhala suave por la nariz.",
            "Exhala más lento de lo que inhalaste.",
            "Repite tres veces.",
            "Nota si tu cuerpo baja aunque sea un poquito la tensión.",
        ],
        "closing_message": "Eso es suficiente por ahora. Un pasito pequeño también cuenta.",
    },
    "pausa-breve-estudio": {
        "slug": "pausa-breve-estudio",
        "title": "Pausa breve de estudio",
        "category": "organizacion",
        "duration_minutes": 3,
        "description": "Guía rápida para ordenar la mente cuando hay muchas tareas.",
        "steps": [
            "Escribe mentalmente o en una nota qué tienes pendiente.",
            "Elige solo una tarea pequeña para empezar.",
            "Define un tiempo corto: 10 o 15 minutos.",
            "Deja lo demás para después de esa primera acción.",
            "Empieza por lo más simple, no por lo perfecto.",
        ],
        "closing_message": "No necesitas hacerlo todo al mismo tiempo. Empieza por una cosa.",
    },
    "reestructuracion-pensamientos": {
        "slug": "reestructuracion-pensamientos",
        "title": "Guía TCC breve",
        "category": "tcc",
        "duration_minutes": 5,
        "description": "Ejercicio inspirado en TCC para revisar pensamientos difíciles.",
        "steps": [
            "Identifica el pensamiento que más pesa ahora.",
            "Pregúntate: ¿esto es un hecho o una interpretación?",
            "Busca una evidencia a favor y una evidencia en contra.",
            "Escribe una versión más equilibrada del pensamiento.",
            "Piensa en una acción pequeña que puedas hacer hoy.",
        ],
        "closing_message": "Un pensamiento no siempre es una verdad completa. Puedes mirarlo con más calma.",
    },
    "frase-motivacional": {
        "slug": "frase-motivacional",
        "title": "Frase de ánimo",
        "category": "motivacion",
        "duration_minutes": 1,
        "description": "Mensaje breve para acompañarte en un momento pesado.",
        "steps": [
            "Respira un momento.",
            "Repite con calma: estoy haciendo lo mejor que puedo con lo que tengo hoy.",
            "No tengo que poder con todo al mismo tiempo.",
            "Puedo dar un paso pequeño y eso también vale.",
        ],
        "closing_message": "Vas paso a paso. No estás fallando por sentirte cansado.",
    },
    "conexion-tierra-54321-contactos": {
        "slug": "conexion-tierra-54321-contactos",
        "title": "Botón de pánico: volver al presente",
        "category": "crisis",
        "duration_minutes": 3,
        "description": "Ejercicio inmediato para momentos de crisis, ansiedad intensa o desborde emocional.",
        "steps": [
            "Mira a tu alrededor y nombra 5 cosas que puedes ver.",
            "Ahora reconoce 4 cosas que puedes tocar.",
            "Escucha 3 sonidos a tu alrededor.",
            "Identifica 2 cosas que puedes oler.",
            "Nota 1 cosa que puedas saborear o siente tu respiración.",
            "Si estás en peligro inmediato, busca ayuda humana ahora: una persona de confianza, Bienestar Universitario o llama al 123 en Colombia.",
        ],
        "closing_message": "No tienes que pasar por esto a solas. Busca apoyo humano inmediato si sientes que puedes hacerte daño.",
    },
}


def get_guided_exercise(slug: str) -> dict[str, Any] | None:
    return GUIDED_EXERCISES.get(slug)


def get_panic_support() -> dict[str, Any]:
    return {
        "panic_mode": True,
        "message": (
            "Estoy contigo. Vamos a hacer una pausa segura primero. "
            "Sigue estos pasos despacio y, si estás en peligro inmediato, busca ayuda humana o llama al 123."
        ),
        "exercises": [
            GUIDED_EXERCISES["conexion-tierra-54321-contactos"],
            GUIDED_EXERCISES["respiracion-4-4-4"],
            GUIDED_EXERCISES["frase-motivacional"],
            GUIDED_EXERCISES["reestructuracion-pensamientos"],
        ],
        "help_resource": {
            "name": "Bienestar Universitario UNAB",
            "emergency": "123 Colombia",
        },
    }