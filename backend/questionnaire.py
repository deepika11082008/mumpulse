from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, Mother, Questionnaire

q_bp = Blueprint('questionnaire', __name__, url_prefix='/api/questionnaire')


def calculate_risk(total_score):
    """Score 0–15.  High risk = low score."""
    if total_score >= 11:
        return 'low'
    elif total_score >= 6:
        return 'moderate'
    else:
        return 'high'


# ─────────────────────────────────────────────
#  POST /api/questionnaire/submit
# ─────────────────────────────────────────────
@q_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit():
    mother_id = int(get_jwt_identity())
    data      = request.get_json()

    answers = data.get('answers')   # expects list of 5 ints (0–3)
    if not answers or len(answers) != 5:
        return jsonify({'error': '5 answers required (each 0–3)'}), 400

    for a in answers:
        if not isinstance(a, int) or a < 0 or a > 3:
            return jsonify({'error': 'Each answer must be an integer 0–3'}), 400

    # score: answer 0 → 3 pts, 1 → 2 pts, 2 → 1 pt, 3 → 0 pts
    total = sum(3 - a for a in answers)
    risk  = calculate_risk(total)

    # allow re-submission (overwrite latest)
    existing = Questionnaire.query.filter_by(mother_id=mother_id).order_by(
        Questionnaire.submitted_at.desc()).first()

    if existing:
        existing.q1_answer   = answers[0]
        existing.q2_answer   = answers[1]
        existing.q3_answer   = answers[2]
        existing.q4_answer   = answers[3]
        existing.q5_answer   = answers[4]
        existing.total_score = total
        existing.risk_level  = risk
        q = existing
    else:
        q = Questionnaire(
            mother_id   = mother_id,
            q1_answer   = answers[0],
            q2_answer   = answers[1],
            q3_answer   = answers[2],
            q4_answer   = answers[3],
            q5_answer   = answers[4],
            total_score = total,
            risk_level  = risk,
        )
        db.session.add(q)

    db.session.commit()
    return jsonify({
        'message':     'Questionnaire submitted',
        'total_score': total,
        'risk_level':  risk,
        'result':      q.to_dict(),
    }), 200


# ─────────────────────────────────────────────
#  GET /api/questionnaire/result
# ─────────────────────────────────────────────
@q_bp.route('/result', methods=['GET'])
@jwt_required()
def get_result():
    mother_id = int(get_jwt_identity())
    q = Questionnaire.query.filter_by(mother_id=mother_id).order_by(
        Questionnaire.submitted_at.desc()).first()

    if not q:
        return jsonify({'error': 'No questionnaire found'}), 404

    return jsonify(q.to_dict()), 200