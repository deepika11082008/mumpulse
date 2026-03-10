# models/sentiment.py — Sentiment Analysis using HuggingFace

from transformers import pipeline
from config import Config

# Load once at startup (not on every request)
_sentiment_pipeline = None

def load_model():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        print("[Sentiment] Loading model...")
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=Config.SENTIMENT_MODEL
        )
        print("[Sentiment] Model ready.")


def analyze(text: str) -> dict:
    """
    Analyze sentiment of given text.
    Returns: { label: 'POSITIVE'|'NEGATIVE', score: float, text: str }
    """
    load_model()

    if not text or not text.strip():
        return {"error": "Text cannot be empty"}

    result = _sentiment_pipeline(text[:512])[0]  # limit to 512 tokens

    return {
        "text": text,
        "sentiment": result["label"],       # POSITIVE or NEGATIVE
        "confidence": round(result["score"], 4)
    }