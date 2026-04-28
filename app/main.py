from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
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
        'steps': 'Inhala 4 segundos; sostén 4 segundos; exhala 4 segundos; repite 5 veces.',
    },
    {
        'slug': 'anclaje-5-sentidos',
        'title': 'Anclaje de 5 sentidos',
        'category': 'ansiedad',
        'duration_minutes': 5,
        'description': 'Técnica breve para volver al presente cuando sientes ansiedad.',
        'steps': 'Nombra 5 cosas que ves, 4 que sientes, 3 que escuchas, 2 que hueles y 1 que saboreas.',
    },
    {
        'slug': 'reestructuracion-pensamientos',
        'title': 'Reestructuración de pensamientos',
        'category': 'tcc',
        'duration_minutes': 5,
        'description': 'Identifica un pensamiento negativo y contrástalo con una alternativa más equilibrada.',
        'steps': 'Escribe el pensamiento, busca evidencia a favor/en contra y formula uno más realista.',
    },
    {
        'slug': 'pausa-breve-estudio',
        'title': 'Pausa breve de estudio',
        'category': 'estudio',
        'duration_minutes': 3,
        'description': 'Micro-pausa para despejar la mente durante una jornada de estudio.',
        'steps': 'Levántate, estira cuello y hombros, toma agua y respira profundo tres veces.',
    },
    {
        'slug': 'respiracion-4-7-8',
        'title': 'Respiración 4-7-8',
        'category': 'respiracion',
        'duration_minutes': 4,
        'description': 'Ejercicio de respiración lenta para reducir activación emocional.',
        'steps': 'Inhala 4 segundos; sostén 7 segundos; exhala lentamente 8 segundos; repite 4 veces.',
    },
    {
        'slug': 'frase-motivacional-breve',
        'title': 'Frase motivacional breve',
        'category': 'motivacion',
        'duration_minutes': 1,
        'description': 'Mensaje breve para recuperar confianza durante momentos de ansiedad académica.',
        'steps': 'Lee la frase con calma; respira profundo; identifica una acción pequeña que puedas hacer ahora.',
    },
    {
        'slug': 'guia-tcc-breve',
        'title': 'Guía TCC breve',
        'category': 'tcc',
        'duration_minutes': 5,
        'description': 'Guía corta para identificar pensamiento automático y construir una alternativa más equilibrada.',
        'steps': 'Describe la situación; identifica el pensamiento; reconoce la emoción; busca evidencia; escribe un pensamiento alternativo.',
    },
]


async def seed_exercises() -> None:
    async with AsyncSessionLocal() as db:
        await _seed_exercises(db)


async def _seed_exercises(db: AsyncSession) -> None:
    result = await db.execute(select(func.count()).select_from(Exercise))
    count = result.scalar_one()
    if count > 0:
        return

    for item in SEED_EXERCISES:
        db.add(Exercise(**item))
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


@app.get('/health', tags=['health'])
async def health():
    return {'status': 'ok', 'app': settings.APP_NAME}
