import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from models import db, Mother, VoiceEntry

voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')

ALLOWED_EXTENSIONS = {'webm', 'mp3', 'wav', 'ogg', 'm4a'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─────────────────────────────────────────────
#  POST /api/voice/upload
#  Upload audio file for a specific day
# ─────────────────────────────────────────────
@voice_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_voice():
    mother_id = int(get_jwt_identity())
    mother    = Mother.query.get_or_404(mother_id)

    day_number = request.form.get('day_number')
    duration   = request.form.get('duration', '00:00')

    if not day_number:
        return jsonify({'error': 'day_number is required'}), 400

    day_number = int(day_number)
    if day_number < 1 or day_number > 5:
        return jsonify({'error': 'day_number must be between 1 and 5'}), 400

    # save or update existing entry for this day
    entry = VoiceEntry.query.filter_by(mother_id=mother_id, day_number=day_number).first()

    audio_path = None
    if 'audio' in request.files:
        file = request.files['audio']
        if file and allowed_file(file.filename):
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(mother_id))
            os.makedirs(upload_dir, exist_ok=True)
            filename   = secure_filename(f'day{day_number}_{file.filename}')
            full_path  = os.path.join(upload_dir, filename)
            file.save(full_path)
            audio_path = full_path

    if entry:
        # update existing
        if audio_path:
            entry.audio_path = audio_path
        entry.duration = duration
    else:
        entry = VoiceEntry(
            mother_id  = mother_id,
            day_number = day_number,
            duration   = duration,
            audio_path = audio_path,
        )
        db.session.add(entry)

    db.session.commit()
    return jsonify({'message': f'Day {day_number} recorded', 'entry': entry.to_dict()}), 200


# ─────────────────────────────────────────────
#  POST /api/voice/complete
#  Mark a day complete (no audio file — simulation mode)
# ─────────────────────────────────────────────
@voice_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_day():
    mother_id  = int(get_jwt_identity())
    data       = request.get_json()
    day_number = data.get('day_number')
    duration   = data.get('duration', '00:00')

    if not day_number or int(day_number) < 1 or int(day_number) > 5:
        return jsonify({'error': 'day_number must be 1–5'}), 400

    day_number = int(day_number)
    entry = VoiceEntry.query.filter_by(mother_id=mother_id, day_number=day_number).first()

    if not entry:
        entry = VoiceEntry(mother_id=mother_id, day_number=day_number, duration=duration)
        db.session.add(entry)
    else:
        entry.duration = duration

    db.session.commit()
    return jsonify({'message': f'Day {day_number} marked complete', 'entry': entry.to_dict()}), 200


# ─────────────────────────────────────────────
#  GET /api/voice/progress
#  Returns list of completed day numbers
# ─────────────────────────────────────────────
@voice_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    mother_id = int(get_jwt_identity())
    entries   = VoiceEntry.query.filter_by(mother_id=mother_id).all()
    return jsonify({
        'completed_days': [e.day_number for e in entries],
        'entries':        [e.to_dict() for e in entries],
    }), 200


# ─────────────────────────────────────────────
#  GET /api/voice/audio/<day>
#  Stream saved audio file for a day
# ─────────────────────────────────────────────
@voice_bp.route('/audio/<int:day_number>', methods=['GET'])
@jwt_required()
def get_audio(day_number):
    mother_id = int(get_jwt_identity())
    entry     = VoiceEntry.query.filter_by(mother_id=mother_id, day_number=day_number).first()

    if not entry or not entry.audio_path or not os.path.exists(entry.audio_path):
        return jsonify({'error': 'Audio not found'}), 404

    directory = os.path.dirname(entry.audio_path)
    filename  = os.path.basename(entry.audio_path)
    return send_from_directory(directory, filename)