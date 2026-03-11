# routes/screening_routes.py
# Voice in → AI responds → ElevenLabs speaks it back as MP3

import io
from flask import Blueprint, request, jsonify, send_file
from models.voice_analyzer  import transcribe_audio, measure_voice_stress
from models.screening_ai    import get_day_greeting, get_ai_response, clear_conversation
from models.risk_calculator import count_sad_words, calculate_risk
from utils.firebase         import (
    create_session, save_response,
    save_risk_result, get_session, get_user_sessions
)
from utils.tts import text_to_speech

screening_bp = Blueprint("screening", __name__, url_prefix="/api/screening")


# ── 1. START DAY — returns AI greeting as MP3 ─────────────────────────────────
@screening_bp.route("/start", methods=["POST"])
def start_day():
    """
    POST /api/screening/start
    Body: { "user_id": "abc", "baby_age_weeks": 6, "day": 1 }

    Returns:
      - session_id, day, ai_message (text)
      - ai_audio_url: call /api/screening/speak/<session_id>/0 to get MP3
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    user_id        = data.get("user_id")
    baby_age_weeks = data.get("baby_age_weeks")
    day            = int(data.get("day", 1))

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    if baby_age_weeks is None:
        return jsonify({"error": "baby_age_weeks is required"}), 400
    if day not in [1, 2, 3, 4, 5]:
        return jsonify({"error": "day must be 1–5"}), 400

    session_id = create_session(user_id, int(baby_age_weeks))
    greeting   = get_day_greeting(day)

    # Convert greeting to speech
    audio_bytes, tts_error = text_to_speech(greeting)

    response_data = {
        "session_id": session_id,
        "day":        day,
        "ai_message": greeting,
        "has_audio":  audio_bytes is not None
    }

    if tts_error:
        response_data["tts_warning"] = tts_error

    # If audio generated, return it directly as MP3
    if audio_bytes:
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype    = "audio/mpeg",
            as_attachment = False,
            download_name = "greeting.mp3",
            # Pass session info in headers so frontend still has it
        ), 200, {
            "X-Session-Id": session_id,
            "X-Day":        str(day),
            "X-AI-Message": greeting[:200]   # truncated for header safety
        }

    # Fallback: no audio, return JSON
    return jsonify(response_data), 201


# ── 2. MOTHER SPEAKS — AI RESPONDS WITH AUDIO ────────────────────────────────
@screening_bp.route("/talk", methods=["POST"])
def talk():
    """
    POST /api/screening/talk
    Form-data:
      - session_id  (string)
      - day         (int 1–5)
      - audio       (WAV/MP3 file)

    Returns: MP3 audio of AI response
    Headers carry: transcription, sentiment, risk data
    """
    session_id = request.form.get("session_id")
    day        = request.form.get("day")
    audio_file = request.files.get("audio")

    # --- Validate ---
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    if not day:
        return jsonify({"error": "day is required"}), 400
    if not audio_file:
        return jsonify({"error": "audio file is required"}), 400

    day = int(day)

    # --- Get session ---
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    baby_age_weeks = session.get("baby_age_weeks", 0)
    audio_bytes    = audio_file.read()

    # --- Step 1: Transcribe mother's voice ---
    try:
        transcribed_text = transcribe_audio(audio_bytes)
    except Exception as e:
        transcribed_text = ""

    # Fallback if transcription empty
    if not transcribed_text or not transcribed_text.strip():
        fallback_msg = "I didn't quite catch that. Could you speak a little closer to the mic and try again?"
        audio_bytes_out, _ = text_to_speech(fallback_msg)
        if audio_bytes_out:
            return send_file(
                io.BytesIO(audio_bytes_out),
                mimetype="audio/mpeg",
                download_name="response.mp3"
            ), 200, {"X-AI-Message": fallback_msg, "X-Fallback": "true"}
        return jsonify({"ai_message": fallback_msg}), 200

    # --- Step 2: Voice stress ---
    try:
        voice_stress = measure_voice_stress(audio_bytes)
    except Exception:
        voice_stress = 0.0   # fallback to 0 if stress detection fails

    # --- Step 3: Sad word count ---
    sad_word_count = count_sad_words(transcribed_text)

    # --- Step 4: AI generates empathetic response ---
    try:
        ai_result = get_ai_response(
            session_id  = session_id,
            mother_text = transcribed_text,
            day         = day
        )
        ai_message = ai_result["ai_message"]
        sentiment  = ai_result["sentiment"]
        is_crisis  = ai_result["is_crisis"]
        turn_number = ai_result["turn_number"]
    except Exception as e:
        ai_message  = "I'm here with you. Take your time and tell me how you're feeling."
        sentiment   = "NEUTRAL"
        is_crisis   = False
        turn_number = 0

    # --- Step 5: Convert AI response to speech ---
    audio_out, tts_error = text_to_speech(ai_message)

    # --- Step 6: Save to Firebase ---
    try:
        save_response(
            session_id       = session_id,
            question_id      = turn_number,
            transcribed_text = transcribed_text,
            sentiment        = sentiment,
            voice_stress     = voice_stress,
            sad_word_count   = sad_word_count
        )
    except Exception:
        pass  # Don't crash if Firebase save fails

    # --- Step 7: Return MP3 audio to frontend ---
    headers = {
        "X-Session-Id":       session_id,
        "X-Turn-Number":      str(turn_number),
        "X-Transcribed-Text": transcribed_text[:200],
        "X-Sentiment":        sentiment,
        "X-Voice-Stress":     str(voice_stress),
        "X-Sad-Word-Count":   str(sad_word_count),
        "X-Is-Crisis":        str(is_crisis).lower(),
        "X-AI-Message":       ai_message[:200]
    }

    if audio_out:
        return send_file(
            io.BytesIO(audio_out),
            mimetype      = "audio/mpeg",
            download_name = "response.mp3"
        ), 200, headers

    # Fallback: no audio, return JSON with text
    if tts_error:
        headers["X-TTS-Error"] = tts_error
    return jsonify({"ai_message": ai_message, "tts_error": tts_error}), 200, headers


# ── 3. END SESSION — risk score + farewell audio ──────────────────────────────
@screening_bp.route("/end", methods=["POST"])
def end_session():
    """
    POST /api/screening/end
    Body: { "session_id": "abc123" }

    Calculates risk, saves to Firebase, returns farewell MP3.
    """
    data       = request.get_json(silent=True)
    session_id = data.get("session_id") if data else None

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    responses      = session.get("responses", [])
    baby_age_weeks = session.get("baby_age_weeks", 0)

    if not responses:
        return jsonify({"error": "No responses recorded yet"}), 400

    # Aggregate
    total_sad_words  = sum(r.get("sad_word_count", 0) for r in responses)
    avg_voice_stress = sum(r.get("voice_stress",   0) for r in responses) / len(responses)

    # Calculate risk
    risk_result = calculate_risk(total_sad_words, baby_age_weeks, avg_voice_stress)

    # Save to Firebase
    try:
        save_risk_result(session_id, risk_result)
    except Exception:
        pass

    # Clear memory
    clear_conversation(session_id)

    farewell = (
        "Thank you so much for talking with me today. "
        "You did something really important just by showing up and being honest. "
        "Take care of yourself — you matter just as much as your baby does."
    )

    audio_out, _ = text_to_speech(farewell)

    headers = {
        "X-Risk-Score": str(risk_result["risk_score"]),
        "X-Risk-Level": risk_result["risk_level"],
        "X-AI-Message": farewell
    }

    if audio_out:
        return send_file(
            io.BytesIO(audio_out),
            mimetype      = "audio/mpeg",
            download_name = "farewell.mp3"
        ), 200, headers

    return jsonify({"ai_message": farewell, "risk_result": risk_result}), 200


# ── 4. GET RESULT ─────────────────────────────────────────────────────────────
@screening_bp.route("/result/<session_id>", methods=["GET"])
def get_result(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session), 200


# ── 5. USER HISTORY ───────────────────────────────────────────────────────────
@screening_bp.route("/history/<user_id>", methods=["GET"])
def get_history(user_id):
    sessions = get_user_sessions(user_id)
    return jsonify({"user_id": user_id, "sessions": sessions}), 200