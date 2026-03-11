# models/risk_calculator.py
# Formula: (sad_words * baby_age_weeks) + voice_stress

# Postpartum-specific sad/distress word list
SAD_WORDS = {
    # Emotional distress
    "sad", "cry", "crying", "tears", "hopeless", "helpless", "worthless",
    "empty", "numb", "lost", "broken", "tired", "exhausted", "drained",
    "overwhelmed", "scared", "anxious", "worried", "panic", "fear",
    # Postpartum specific
    "failing", "bad mother", "bad mom", "hate", "regret", "mistake",
    "alone", "lonely", "isolated", "disconnected", "detached",
    "can't cope", "cannot cope", "giving up", "no energy", "no hope",
    "not bonding", "don't love", "don't feel", "numb", "zombie",
    "hurt myself", "hurt myself", "end it", "disappear", "die",
    # Softer distress
    "struggling", "difficult", "hard", "hard time", "falling apart",
    "not okay", "not fine", "not well", "depressed", "depression",
    "anxiety", "stressed", "stress", "dark", "darkness"
}

def count_sad_words(text: str) -> int:
    """Count how many distress/sad words appear in the transcribed text."""
    if not text:
        return 0
    text_lower = text.lower()
    count = 0
    for word in SAD_WORDS:
        if word in text_lower:
            count += 1
    return count

def calculate_risk(sad_word_count: int, baby_age_weeks: int, voice_stress: float) -> dict:
    """
    Risk Formula: (sad_words * baby_age_weeks) + voice_stress

    Args:
        sad_word_count  : number of distress words found in speech
        baby_age_weeks  : age of baby in weeks (0–52+)
        voice_stress    : float 0.0–1.0 from voice analysis

    Returns dict with score + risk level
    """
    raw_score = (sad_word_count * baby_age_weeks) + voice_stress

    # Determine risk level
    if raw_score <= 2:
        level = "LOW"
        message = "No significant signs of distress detected."
    elif raw_score <= 8:
        level = "MODERATE"
        message = "Some signs of emotional difficulty. Consider follow-up support."
    elif raw_score <= 20:
        level = "HIGH"
        message = "Significant distress indicators. Professional support is recommended."
    else:
        level = "CRITICAL"
        message = "Severe distress detected. Immediate professional help is strongly advised."

    return {
        "risk_score":       round(raw_score, 4),
        "risk_level":       level,
        "message":          message,
        "breakdown": {
            "sad_word_count":   sad_word_count,
            "baby_age_weeks":   baby_age_weeks,
            "voice_stress":     voice_stress,
            "formula":          f"({sad_word_count} × {baby_age_weeks}) + {voice_stress} = {round(raw_score, 4)}"
        }
    }