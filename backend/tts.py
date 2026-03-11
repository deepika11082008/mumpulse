# utils/tts.py
# Text-to-Speech using ElevenLabs API
# Converts AI text response → MP3 audio file → sent back to mother

import os
import requests
import tempfile

# ── CONFIG ────────────────────────────────────────────────────────────────────

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# ElevenLabs Voice ID — "Rachel" is warm, calm, empathetic (great for maternal health)
# You can change this to any voice from your ElevenLabs account
# Other good options:
#   "21m00Tcm4TlvDq8ikWAM" → Rachel (recommended)
#   "AZnzlk1XvdvUeBnXmlld" → Domi
#   "EXAVITQu4vr4xnSDxMaL" → Bella
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# Voice settings — tuned for calm, empathetic speech
VOICE_SETTINGS = {
    "stability":         0.75,   # 0–1: higher = more consistent, less expressive
    "similarity_boost":  0.75,   # 0–1: higher = closer to original voice
    "style":             0.30,   # 0–1: slight warmth/emotion
    "use_speaker_boost": True
}


# ── MAIN FUNCTION ─────────────────────────────────────────────────────────────

def text_to_speech(text: str) -> tuple:
    """
    Convert text to MP3 audio using ElevenLabs.

    Args:
        text : the AI message to speak

    Returns:
        (audio_bytes, error_message)
        - On success : (bytes, None)
        - On failure : (None, error_string)
    """
    if not ELEVENLABS_API_KEY:
        return None, "ELEVENLABS_API_KEY is not set in environment variables"

    if not text or not text.strip():
        return None, "Text is empty — nothing to speak"

    try:
        headers = {
            "xi-api-key":   ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept":       "audio/mpeg"
        }

        payload = {
            "text":           text,
            "model_id":       "eleven_monolingual_v1",
            "voice_settings": VOICE_SETTINGS
        }

        response = requests.post(
            ELEVENLABS_URL,
            json    = payload,
            headers = headers,
            timeout = 15
        )

        if response.status_code == 200:
            return response.content, None  # MP3 bytes ✅

        elif response.status_code == 401:
            return None, "Invalid ElevenLabs API key"

        elif response.status_code == 429:
            return None, "ElevenLabs rate limit reached — try again shortly"

        else:
            return None, f"ElevenLabs error {response.status_code}: {response.text}"

    except requests.exceptions.Timeout:
        return None, "ElevenLabs request timed out"

    except requests.exceptions.ConnectionError:
        return None, "Cannot reach ElevenLabs — check internet connection"

    except Exception as e:
        return None, f"Unexpected TTS error: {str(e)}"


def save_audio_temp(audio_bytes: bytes) -> str:
    """
    Save MP3 bytes to a temp file and return the file path.
    Useful for debugging or local playback.
    """
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.write(audio_bytes)
        tmp.close()
        return tmp.name
    except Exception as e:
        return None