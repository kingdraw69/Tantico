def evaluate_safety(emotion_result: dict) -> dict:
    if emotion_result['emotion'] == 'crisis':
        return {
            'risk_level': 'alto',
            'activate_crisis': True,
        }

    if emotion_result['intensity'] >= 4:
        return {
            'risk_level': 'medio',
            'activate_crisis': False,
        }

    return {
        'risk_level': 'bajo',
        'activate_crisis': False,
    }