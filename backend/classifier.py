# models/classifier.py — Zero-shot Text Classification using HuggingFace

from transformers import pipeline
from config import Config

_classifier_pipeline = None

def load_model():
    global _classifier_pipeline
    if _classifier_pipeline is None:
        print("[Classifier] Loading model...")
        _classifier_pipeline = pipeline(
            "zero-shot-classification",
            model=Config.CLASSIFIER_MODEL
        )
        print("[Classifier] Model ready.")


def classify(text: str, labels: list = None) -> dict:
    """
    Classify text into one of the predefined categories.
    Returns: { text, top_label, scores: [{label, score}] }
    """
    load_model()

    if not text or not text.strip():
        return {"error": "Text cannot be empty"}

    candidate_labels = labels or Config.CLASSIFICATION_LABELS
    result = _classifier_pipeline(text[:512], candidate_labels)

    scores = [
        {"label": lbl, "score": round(sc, 4)}
        for lbl, sc in zip(result["labels"], result["scores"])
    ]

    return {
        "text": text,
        "top_label": result["labels"][0],
        "confidence": round(result["scores"][0], 4),
        "all_scores": scores
    }