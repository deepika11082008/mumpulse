utils/helpers.py — Shared utility functions

def validate_text(text):
    """Returns error string if invalid, None if OK."""
    if not text:
        return "Text is required"
    if not isinstance(text, str):
        return "Text must be a string"
    if len(text.strip()) == 0:
        return "Text cannot be blank"
    if len(text) > 5000:
        return "Text too long (max 5000 characters)"
    return None