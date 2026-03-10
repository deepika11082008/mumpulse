# config.py — central config for all models

class Config:
    DEBUG = False
    PORT = 5000

    # HuggingFace model names
    SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
    CLASSIFIER_MODEL = "facebook/bart-large-mnli"
    INTENT_MODEL    = "facebook/bart-large-mnli"  # zero-shot works for intent too

    # Labels for text classification
    CLASSIFICATION_LABELS = [
        "technology", "sports", "politics", "health",
        "business", "entertainment", "science"
    ]

    # Labels for intent detection
    INTENT_LABELS = [
        "greeting", "goodbye", "help_request", "complaint",
        "question", "order", "cancel", "thanks"
    ]