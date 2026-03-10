from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ─────────────────────────────────────────────
#  MOTHER (User)
# ─────────────────────────────────────────────
class Mother(db.Model):
    __tablename__ = 'mothers'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    weeks_postpartum = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    voice_entries   = db.relationship('VoiceEntry',   backref='mother', lazy=True, cascade='all, delete-orphan')
    questionnaires  = db.relationship('Questionnaire', backref='mother', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':               self.id,
            'name':             self.name,
            'date_of_birth':    self.date_of_birth.isoformat(),
            'weeks_postpartum': self.weeks_postpartum,
            'created_at':       self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────
#  VOICE ENTRY  (one per day, days 1–5)
# ─────────────────────────────────────────────
class VoiceEntry(db.Model):
    __tablename__ = 'voice_entries'

    id          = db.Column(db.Integer, primary_key=True)
    mother_id   = db.Column(db.Integer, db.ForeignKey('mothers.id'), nullable=False)
    day_number  = db.Column(db.Integer, nullable=False)          # 1–5
    audio_path  = db.Column(db.String(300), nullable=True)       # path to saved audio file
    duration    = db.Column(db.String(10), nullable=True)        # e.g. "02:34"
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':          self.id,
            'day_number':  self.day_number,
            'duration':    self.duration,
            'audio_path':  self.audio_path,
            'recorded_at': self.recorded_at.isoformat(),
        }


# ─────────────────────────────────────────────
#  QUESTIONNAIRE  (day 6 — 5 questions)
# ─────────────────────────────────────────────
class Questionnaire(db.Model):
    __tablename__ = 'questionnaires'

    id          = db.Column(db.Integer, primary_key=True)
    mother_id   = db.Column(db.Integer, db.ForeignKey('mothers.id'), nullable=False)

    # individual answer indices (0=best → 3=worst)
    q1_answer   = db.Column(db.Integer, nullable=False)   # calm / happy moment
    q2_answer   = db.Column(db.Integer, nullable=False)   # feeling supported
    q3_answer   = db.Column(db.Integer, nullable=False)   # comfortable sharing
    q4_answer   = db.Column(db.Integer, nullable=False)   # rest / self-care
    q5_answer   = db.Column(db.Integer, nullable=False)   # connected with baby

    total_score = db.Column(db.Integer, nullable=False)   # 0–15
    risk_level  = db.Column(db.String(10), nullable=False)  # low / moderate / high
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':           self.id,
            'answers':      [self.q1_answer, self.q2_answer, self.q3_answer,
                             self.q4_answer, self.q5_answer],
            'total_score':  self.total_score,
            'risk_level':   self.risk_level,
            'submitted_at': self.submitted_at.isoformat(),
        }