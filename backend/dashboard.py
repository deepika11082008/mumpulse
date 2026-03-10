from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, Mother, VoiceEntry, Questionnaire

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


# ─────────────────────────────────────────────
#  GET /api/dashboard
#  Full summary for the logged-in mother
# ─────────────────────────────────────────────
@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def get_dashboard():
    mother_id = int(get_jwt_identity())
    mother    = Mother.query.get_or_404(mother_id)

    # voice entries
    entries = VoiceEntry.query.filter_by(mother_id=mother_id).order_by(
        VoiceEntry.day_number).all()
    completed_days = [e.day_number for e in entries]

    # questionnaire
    q = Questionnaire.query.filter_by(mother_id=mother_id).order_by(
        Questionnaire.submitted_at.desc()).first()

    return jsonify({
        'mother':          mother.to_dict(),
        'completed_days':  completed_days,
        'voice_entries':   [e.to_dict() for e in entries],
        'questionnaire':   q.to_dict() if q else None,
        'streak':          len(completed_days),
    }), 200


# ─────────────────────────────────────────────
#  GET /api/dashboard/profile
#  Update mother profile info
# ─────────────────────────────────────────────
@dashboard_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    mother_id = int(get_jwt_identity())
    mother    = Mother.query.get_or_404(mother_id)
    return jsonify(mother.to_dict()), 200


@dashboard_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    mother_id = int(get_jwt_identity())
    mother    = Mother.query.get_or_404(mother_id)
    data      = request.get_json()

    if 'name' in data and data['name'].strip():
        mother.name = data['name'].strip()
    if 'weeks_postpartum' in data:
        w = int(data['weeks_postpartum'])
        if 1 <= w <= 52:
            mother.weeks_postpartum = w

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'mother': mother.to_dict()}), 200