# routes/nlp_routes.py — All NLP API endpoints

from flask import Blueprint, request, jsonify
from models import sentiment, classifier, intent

nlp_bp = Blueprint("nlp", __name__, url_prefix="/api/nlp")


def get_text_from_request():
    """Helper to safely extract 'text' from JSON body."""
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return None, jsonify({"error": "Missing 'text' field in request body"}), 400
    return data["text"], None, None


# ─── SENTIMENT ───────────────────────────────────────────────
@nlp_bp.route("/sentiment", methods=["POST"])
def sentiment_route():
    """
    POST /api/nlp/sentiment
    Body: { "text": "I love this product!" }
    """
    text, err_response, code = get_text_from_request()
    if err_response:
        return err_response, code

    result = sentiment.analyze(text)
    return jsonify(result), 200


# ─── TEXT CLASSIFICATION ─────────────────────────────────────
@nlp_bp.route("/classify", methods=["POST"])
def classify_route():
    """
    POST /api/nlp/classify
    Body: { "text": "...", "labels": ["optional", "custom", "labels"] }
    """
    text, err_response, code = get_text_from_request()
    if err_response:
        return err_response, code

    data = request.get_json()
    custom_labels = data.get("labels", None)  # optional custom labels

    result = classifier.classify(text, labels=custom_labels)
    return jsonify(result), 200


# ─── INTENT DETECTION ────────────────────────────────────────
@nlp_bp.route("/intent", methods=["POST"])
def intent_route():
    """
    POST /api/nlp/intent
    Body: { "text": "...", "intents": ["optional", "custom", "intents"] }
    """
    text, err_response, code = get_text_from_request()
    if err_response:
        return err_response, code

    data = request.get_json()
    custom_intents = data.get("intents", None)  # optional custom intent list

    result = intent.detect_intent(text, custom_intents=custom_intents)
    return jsonify(result), 200


# ─── COMBINED (all 3 at once) ─────────────────────────────────
@nlp_bp.route("/analyze", methods=["POST"])
def analyze_all_route():
    """
    POST /api/nlp/analyze
    Runs all 3 NLP models on the same text.
    Body: { "text": "..." }
    """
    text, err_response, code = get_text_from_request()
    if err_response:
        return err_response, code

    return jsonify({
        "text": text,
        "sentiment":     sentiment.analyze(text),
        "classification": classifier.classify(text),
        "intent":        intent.detect_intent(text)
    }), 200