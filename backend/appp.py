# app.py — Main Flask application entry point

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.nlp_routes import nlp_bp

app = Flask(__name__)
app.config.from_object(Config)

# Allow requests from any frontend (React, mobile, etc.)
CORS(app)

# Register NLP blueprint
app.register_blueprint(nlp_bp)


# ─── HEALTH CHECK ─────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "NLP Backend is running"}), 200


# ─── 404 HANDLER ──────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404


# ─── 500 HANDLER ──────────────────────────────────────────────
@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("Starting NLP Backend...")
    print("Available routes:")
    print("  GET  /health")
    print("  POST /api/nlp/sentiment")
    print("  POST /api/nlp/classify")
    print("  POST /api/nlp/intent")
    print("  POST /api/nlp/analyze  (all-in-one)")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)