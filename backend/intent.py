# models/intent.py — Intent Detection using Zero-shot Classification

from transformers import pipeline
from config import Config

_intent_pipeline = None

def load_model():
    global _intent_pipeline
    if _intent_pipeline is None:
        print("[Intent] Loading model...")
        _intent_pipeline = pipeline(
            "zero-shot-classification",
            model=Config.INTENT_MODEL
        )
        print("[Intent] Model ready.")


def detect_intent(text: str, custom_intents: list = None) -> dict:
    """
    Detect user intent from text.
    Returns: { text, intent, confidence, all_intents: [{label, score}] }
    """
    load_model()

    if not text or not text.strip():
        return {"error": "Text cannot be empty"}

    intent_labels = custom_intents or Config.INTENT_LABELS
    result = _intent_pipeline(text[:512], intent_labels)

    all_intents = [
        {"intent": lbl, "score": round(sc, 4)}
        for lbl, sc in zip(result["labels"], result["scores"])
    ]

    return {
        "text": text,
        "intent": result["labels"][0],
        "confidence": round(result["scores"][0], 4),
        "all_intents": all_intents
    }