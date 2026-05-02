from contextlib import asynccontextmanager

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal, init_db
from app.models.entities import Exercise
from app.routers import auth, checkins, content, crisis, journal, pomodoro, privacy, chat, support

settings = get_settings()

SEED_EXERCISES = [
    {
        'slug': 'respiracion-4-4-4',
        'title': 'Respiración 4-4-4',
        'category': 'respiracion',
        'duration_minutes': 3,
        'description': 'Ejercicio breve para regular el estrés en momentos de carga académica.',
        'steps': '1. Siéntate cómodo. 2. Inhala durante 4 segundos. 3. Sostén el aire 4 segundos. 4. Exhala durante 4 segundos. 5. Repite el ciclo 5 veces.',
    },
    {
        'slug': 'respiracion-4-7-8',
        'title': 'Respiración 4-7-8',
        'category': 'respiracion',
        'duration_minutes': 4,
        'description': 'Técnica de respiración para disminuir activación fisiológica asociada a ansiedad.',
        'steps': '1. Inhala por la nariz durante 4 segundos. 2. Sostén la respiración durante 7 segundos. 3. Exhala lentamente durante 8 segundos. 4. Repite 4 ciclos sin forzar el aire.',
    },
    {
        'slug': 'anclaje-5-sentidos',
        'title': 'Anclaje de 5 sentidos',
        'category': 'ansiedad',
        'duration_minutes': 5,
        'description': 'Técnica de grounding para volver al presente cuando sientes ansiedad o bloqueo.',
        'steps': '1. Nombra 5 cosas que ves. 2. Nombra 4 cosas que puedes sentir. 3. Nombra 3 sonidos. 4. Nombra 2 olores. 5. Nombra 1 sabor o una respiración agradable.',
    },
    {
        'slug': 'reestructuracion-pensamientos',
        'title': 'Reestructuración de pensamientos',
        'category': 'tcc',
        'duration_minutes': 5,
        'description': 'Guía TCC breve para identificar un pensamiento negativo y formular una alternativa más equilibrada.',
        'steps': '1. Escribe el pensamiento que te preocupa. 2. Identifica qué emoción produce. 3. Busca evidencia a favor y en contra. 4. Formula un pensamiento más realista. 5. Define una acción pequeña.',
    },
    {
        'slug': 'pausa-breve-estudio',
        'title': 'Pausa breve de estudio',
        'category': 'estudio',
        'duration_minutes': 3,
        'description': 'Micro-pausa para despejar la mente durante una jornada de estudio o entregas.',
        'steps': '1. Levántate de la silla. 2. Estira cuello y hombros. 3. Toma agua. 4. Respira profundo tres veces. 5. Vuelve con una sola tarea prioritaria.',
    },
    {
        'slug': 'pausa-consciente',
        'title': 'Pausa consciente',
        'category': 'regulacion',
        'duration_minutes': 2,
        'description': 'Ejercicio corto para revisar cómo está tu cuerpo y prevenir sobrecarga emocional.',
        'steps': '1. Cierra los ojos si te sientes cómodo. 2. Nota tu respiración. 3. Relaja mandíbula y hombros. 4. Pregúntate: ¿qué necesito ahora mismo? 5. Elige una acción amable.',
    },
    {
        'slug': 'frase-motivacional-breve',
        'title': 'Frase motivacional breve',
        'category': 'motivacion',
        'duration_minutes': 1,
        'description': 'Mensaje corto de apoyo para recuperar claridad y continuar con una acción pequeña.',
        'steps': 'Lee esta frase lentamente: No tienes que poder con todo al mismo tiempo. Ahora basta con dar un paso pequeño y cuidarte en el proceso.',
    },
    {
        'slug': 'contacto-bienestar',
        'title': 'Contacto con Bienestar Universitario',
        'category': 'crisis',
        'duration_minutes': 1,
        'description': 'Ruta de apoyo cuando el estudiante necesita acompañamiento humano o presenta señales de crisis.',
        'steps': '1. Busca un lugar seguro. 2. Contacta a alguien de confianza. 3. Comunícate con Bienestar Universitario. 4. Si hay peligro inmediato, acude a una línea de emergencia o servicio de urgencias.',
    },
]


async def seed_exercises() -> None:
    async with AsyncSessionLocal() as db:
        await _seed_exercises(db)

async def _seed_exercises(db: AsyncSession) -> None:
    result = await db.execute(select(Exercise.slug))
    existing_slugs = set(result.scalars().all())

    seen_slugs = set()

    for item in SEED_EXERCISES:
        slug = item['slug']

        if slug in seen_slugs:
            continue

        seen_slugs.add(slug)

        if slug not in existing_slugs:
            db.add(Exercise(**item))
            existing_slugs.add(slug)

    await db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    await seed_exercises()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(checkins.router, prefix=settings.API_V1_PREFIX)
app.include_router(content.router, prefix=settings.API_V1_PREFIX)
app.include_router(crisis.router, prefix=settings.API_V1_PREFIX)
app.include_router(journal.router, prefix=settings.API_V1_PREFIX)
app.include_router(pomodoro.router, prefix=settings.API_V1_PREFIX)
app.include_router(privacy.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)  
app.include_router(support.router, prefix=settings.API_V1_PREFIX)

STATIC_DIR = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get('/health', tags=['health'])
async def health():
    return {'status': 'ok', 'app': settings.APP_NAME}


@app.get("/", tags=["ui"])
async def web_chat():
    return FileResponse(STATIC_DIR / "index.html")