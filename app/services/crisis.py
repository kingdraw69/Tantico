from app.core.config import get_settings

settings = get_settings()


def evaluate_crisis_text(text: str) -> tuple[bool, list[str]]:
    normalized = text.lower().strip()
    detected = [keyword for keyword in settings.CRISIS_KEYWORDS if keyword in normalized]
    return (len(detected) > 0, detected)
