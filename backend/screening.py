# models/screening_ai.py
# Interactive postpartum AI companion — Day 1 to Day 5
# Free conversation: AI listens, responds empathetically, keeps talking until mother stops

from transformers import pipeline
from config import Config

_sentiment_pipeline = None

def load_model():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        print("[ScreeningAI] Loading sentiment model...")
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=Config.SENTIMENT_MODEL
        )
        print("[ScreeningAI] Ready.")


# ── DAY CONTEXT ───────────────────────────────────────────────────────────────
# Each postpartum day has its own opener + topics the AI gently watches for

DAY_PROFILES = {
    1: {
        "greeting": (
            "Hi mama, welcome. Day 1 with your little one — how are you feeling right now? "
            "There's no right or wrong answer, just take your time and talk to me."
        ),
        "topics": ["pain", "birth", "shock", "overwhelmed", "baby", "feeding", "tired"],
        "context": "first day postpartum, physically recovering from birth"
    },
    2: {
        "greeting": (
            "Good to see you again. You're on day 2 now — how did last night go? "
            "How are you feeling in your body and your heart today?"
        ),
        "topics": ["sleep", "feeding", "crying", "milk", "support", "lonely", "scared"],
        "context": "second day postpartum, milk may be coming in, sleep deprived"
    },
    3: {
        "greeting": (
            "Hey, you made it to day 3. This day can feel really emotional for a lot of mums — "
            "the baby blues often peak around now. How are you holding up today?"
        ),
        "topics": ["crying", "emotional", "hormones", "blues", "love", "bonding", "regret"],
        "context": "day 3, baby blues peak, hormonal drop, emotional"
    },
    4: {
        "greeting": (
            "Day 4 — you're doing it. How are things feeling today compared to yesterday? "
            "Talk to me about anything on your mind."
        ),
        "topics": ["routine", "exhausted", "partner", "help", "alone", "feeding", "worried"],
        "context": "day 4, settling into newborn life, exhaustion building"
    },
    5: {
        "greeting": (
            "Day 5 already. How are you feeling today? "
            "I want to hear how this first week has really been for you — the good and the hard parts."
        ),
        "topics": ["week", "reflection", "struggling", "coping", "support", "future", "hope"],
        "context": "day 5, end of first week, reflecting on the journey"
    }
}


# ── EMPATHETIC RESPONSE LIBRARY ───────────────────────────────────────────────

# When mother sounds distressed
DISTRESS_RESPONSES = [
    "That sounds really hard, and I want you to know you're not alone in feeling this way. Can you tell me more?",
    "Thank you for trusting me with that. What you're going through is real and it matters. What's been the hardest part?",
    "I hear you. It's okay to not be okay right now. Is there anything specific that's been weighing on you most?",
    "You're carrying a lot right now. That takes strength, even when it doesn't feel like it. How long have you been feeling this way?",
    "That makes complete sense given everything you're going through. You don't have to pretend to be fine here. What would help you most right now?",
    "I'm really glad you're talking to me. You matter, and so does how you feel. What happened that brought this feeling on?",
    "It's brave to say that out loud. A lot of mums feel exactly this but never say it. How are you coping day to day?",
]

# When mother sounds okay/positive
POSITIVE_RESPONSES = [
    "That's really lovely to hear. Even small moments of joy matter so much. What's been going well?",
    "I'm so glad. It sounds like you're finding your footing. What's been helping you the most?",
    "That's wonderful. How does it feel compared to what you expected?",
    "It's great that you're feeling that way — you deserve those good moments. Anything you're still finding tricky?",
    "Really good to hear that. How are you taking care of yourself alongside caring for baby?",
]

# When mother seems neutral/uncertain
NEUTRAL_RESPONSES = [
    "Tell me more about that — I want to understand how you're really feeling.",
    "I hear you. Can you walk me through what a typical moment in your day looks like right now?",
    "That's okay. Sometimes feelings are hard to put into words. What comes to mind when you think about how this week has been?",
    "I'm listening. Is there something specific on your mind, or just a general heaviness?",
    "You can say anything here — there's no judgment. What would you want someone to know about how you're feeling?",
]

# Crisis-aware responses (when distress words like self-harm detected)
CRISIS_RESPONSES = [
    (
        "I'm really glad you told me that, and I want you to know it takes real courage to say it. "
        "What you're feeling is serious and you deserve real support right now. "
        "Please reach out to your doctor, midwife, or a crisis line today — you don't have to face this alone. "
        "Can you tell me if there's someone with you right now?"
    )
]

# Crisis trigger words
CRISIS_WORDS = {
    "hurt myself", "harm myself", "end it", "disappear", "don't want to be here",
    "want to die", "kill myself", "suicide", "not worth it", "better off without me",
    "better off dead", "can't go on", "give up"
}


# ── CONVERSATION MEMORY (in-memory per session) ───────────────────────────────
# Stores conversation history per session_id
_conversation_memory = {}

def get_conversation(session_id: str) -> list:
    return _conversation_memory.get(session_id, [])

def add_to_conversation(session_id: str, role: str, message: str):
    if session_id not in _conversation_memory:
        _conversation_memory[session_id] = []
    _conversation_memory[session_id].append({
        "role":    role,   # "mother" or "ai"
        "message": message
    })

def clear_conversation(session_id: str):
    if session_id in _conversation_memory:
        del _conversation_memory[session_id]


# ── MAIN FUNCTIONS ────────────────────────────────────────────────────────────

def get_day_greeting(day: int) -> str:
    """
    Return the AI opening message for a given postpartum day (1–5).
    Call this at the START of each day's session.
    """
    day = max(1, min(day, 5))  # clamp to 1–5
    return DAY_PROFILES[day]["greeting"]


def analyze_sentiment(text: str) -> str:
    """Returns POSITIVE, NEGATIVE, or NEUTRAL."""
    load_model()
    if not text or not text.strip():
        return "NEUTRAL"
    result = _sentiment_pipeline(text[:512])[0]
    score = result["score"]
    label = result["label"]
    # Only call it POSITIVE/NEGATIVE if confidence is high enough
    if score < 0.65:
        return "NEUTRAL"
    return label  # "POSITIVE" or "NEGATIVE"


def detect_crisis(text: str) -> bool:
    """Check if the mother's message contains crisis-level language."""
    text_lower = text.lower()
    for phrase in CRISIS_WORDS:
        if phrase in text_lower:
            return True
    return False


def get_ai_response(session_id: str, mother_text: str, day: int) -> dict:
    """
    Core function — generates AI response to whatever the mother says.

    Args:
        session_id   : unique session identifier (for conversation memory)
        mother_text  : what the mother just said (transcribed from voice)
        day          : postpartum day (1–5)

    Returns dict:
        {
            "ai_message"   : string — what the AI says back,
            "sentiment"    : POSITIVE | NEGATIVE | NEUTRAL,
            "is_crisis"    : bool,
            "turn_number"  : int — how many exchanges so far,
            "conversation" : full history list
        }
    """
    # Save mother's message to memory
    add_to_conversation(session_id, "mother", mother_text)

    conversation = get_conversation(session_id)
    turn_number  = len([c for c in conversation if c["role"] == "mother"])

    # --- Check for crisis first (highest priority) ---
    if detect_crisis(mother_text):
        ai_message = CRISIS_RESPONSES[0]
        add_to_conversation(session_id, "ai", ai_message)
        return {
            "ai_message":   ai_message,
            "sentiment":    "NEGATIVE",
            "is_crisis":    True,
            "turn_number":  turn_number,
            "conversation": conversation
        }

    # --- Analyze sentiment ---
    sentiment = analyze_sentiment(mother_text)

    # --- Pick response pool based on sentiment ---
    import hashlib
    seed = hashlib.md5(f"{session_id}{turn_number}{mother_text[:20]}".encode()).hexdigest()
    idx  = int(seed, 16)

    if sentiment == "NEGATIVE":
        pool = DISTRESS_RESPONSES
    elif sentiment == "POSITIVE":
        pool = POSITIVE_RESPONSES
    else:
        pool = NEUTRAL_RESPONSES

    base_response = pool[idx % len(pool)]

    # --- Add day-specific context on first turn ---
    if turn_number == 1:
        day_context = _get_day_context_note(day)
        ai_message  = f"{base_response} {day_context}".strip()
    else:
        ai_message = base_response

    # Save AI response to memory
    add_to_conversation(session_id, "ai", ai_message)

    return {
        "ai_message":   ai_message,
        "sentiment":    sentiment,
        "is_crisis":    False,
        "turn_number":  turn_number,
        "conversation": get_conversation(session_id)
    }


def _get_day_context_note(day: int) -> str:
    """Add a soft day-aware note to enrich the AI's first response."""
    notes = {
        1: "Your body has just been through something incredible — be gentle with yourself today.",
        2: "Day 2 can feel like a whirlwind. You're still in the thick of it and that's okay.",
        3: "Day 3 is often the most emotional — if you feel like crying, that's completely normal.",
        4: "By day 4 the exhaustion really sets in. It's okay to ask for help.",
        5: "You've made it through your first week. That's no small thing."
    }
    return notes.get(day, "")