"""Language detection utilities."""

from langdetect import LangDetectException, detect


def detect_language(text: str) -> str:
    """Detect whether text is in Brazilian Portuguese or English.

    Uses ``langdetect`` for detection.  Falls back to ``"en"`` if detection
    fails or the language is not PT or EN.

    Args:
        text: The text to analyse.

    Returns:
        str: ``"pt"`` for Portuguese, ``"en"`` for English (or unknown).
    """
    if not text or not text.strip():
        return "en"
    try:
        lang = detect(text)
        return "pt" if lang.startswith("pt") else "en"
    except LangDetectException:
        return "en"
