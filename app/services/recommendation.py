from typing import Sequence

from app.models.entities import Exercise, MoodCheckIn


def recommend_exercise_slugs(checkin: MoodCheckIn, exercises: Sequence[Exercise]) -> list[str]:
    recommendations: list[str] = []

    if checkin.stress_score >= 4:
        recommendations.extend(['respiracion-4-4-4', 'anclaje-5-sentidos'])
    if checkin.mood_score <= 2:
        recommendations.append('reestructuracion-pensamientos')
    if not recommendations:
        recommendations.append('pausa-breve-estudio')

    available = {exercise.slug for exercise in exercises}
    return [slug for slug in recommendations if slug in available][:3]
