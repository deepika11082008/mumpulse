from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import datetime
import bcrypt

from models import db, Mother

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ─────────────────────────────────────────────
#  POST /api/auth/register
# ─────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # validate required fields
    required = ['name', 'date_of_birth', 'weeks_postpartum', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'"{field}" is required'}), 400

    # check duplicate name + dob
    existing = Mother.query.filter_by(name=data['name'].strip()).first()
    if existing:
        return jsonify({'error': 'An account with this name already exists'}), 409

    # parse date
    try:
        dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'date_of_birth must be YYYY-MM-DD'}), 400

    # validate weeks
    weeks = int(data['weeks_postpartum'])
    if weeks < 1 or weeks > 52:
        return jsonify({'error': 'weeks_postpartum must be between 1 and 52'}), 400

    # hash password
    pw_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()

    mother = Mother(
        name             = data['name'].strip(),
        date_of_birth    = dob,
        weeks_postpartum = weeks,
        password_hash    = pw_hash,
    )
    db.session.add(mother)
    db.session.commit()

    token = create_access_token(identity=str(mother.id))
    return jsonify({
        'message': 'Account created successfully',
        'token':   token,
        'mother':  mother.to_dict(),
    }), 201


# ─────────────────────────────────────────────
#  POST /api/auth/login
# ─────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    name     = data.get('name', '').strip()
    password = data.get('password', '')

    if not name or not password:
        return jsonify({'error': 'name and password are required'}), 400

    mother = Mother.query.filter_by(name=name).first()
    if not mother:
        return jsonify({'error': 'No account found with that name'}), 404

    if not bcrypt.checkpw(password.encode(), mother.password_hash.encode()):
        return jsonify({'error': 'Incorrect password'}), 401

    token = create_access_token(identity=str(mother.id))
    return jsonify({
        'message': 'Login successful',
        'token':   token,
        'mother':  mother.to_dict(),
    }), 200