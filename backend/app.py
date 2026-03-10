import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from models import db
from auth import auth_bp
from voice import voice_bp
from questionnaire import q_bp
from dashboard import dashboard_bp

load_dotenv()


def create_app():
    app = Flask(__name__)

    # ── CONFIG ──────────────────────────────────────
    app.config['SECRET_KEY']                = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['JWT_SECRET_KEY']            = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    app.config['SQLALCHEMY_DATABASE_URI']   = os.getenv('DATABASE_URL', 'sqlite:///momcare.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER']             = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH']        = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB

    # ── EXTENSIONS ──────────────────────────────────
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    db.init_app(app)
    JWTManager(app)

    # ── BLUEPRINTS ──────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(voice_bp)
    app.register_blueprint(q_bp)
    app.register_blueprint(dashboard_bp)

    # ── CREATE TABLES + UPLOAD FOLDER ───────────────
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── HEALTH CHECK ────────────────────────────────
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'app': 'MomCare API'}), 200

    # ── ERROR HANDLERS ──────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request'}), 400

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)