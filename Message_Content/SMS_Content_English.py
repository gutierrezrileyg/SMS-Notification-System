import re
from typing import Dict, Any

# GSM-7 character set
GSM7_CHARACTERS = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
    "@£$¥èéùìòÇ\nØøÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ"
    " !\"#$%&'()*+,-./:;<=>?¡ÄÖÑÜ§¿äöñüà^{}\\[~]`|€"
)

# Blacklisted words to reduce spam risk
BLACKLIST_TERMS = {
    "free",
    "gift",
    "winner",
    "cash",
    "buy now",
    "limited time"
}


def _sanitize_template(template: str, values: Dict[str, Any]) -> str:
    """
    Replace placeholders (e.g. {eta}) with actual values.
    """

    rendered = template

    for key, value in values.items():
        rendered = rendered.replace(f"{{{key}}}", str(value))

    # Check if any placeholders remain unreplaced
    remaining = re.findall(r"\{.*?\}", rendered)

    if remaining:
        raise ValueError(
            f"Missing values for placeholders: {', '.join(remaining)}"
        )

    return rendered


def _normalize_for_sms(text: str) -> str:
    """
    Replace unsupported characters with GSM-7 friendly equivalents.
    """

    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
        "ç": "c",
        "“": "\"",
        "”": "\"",
        "‘": "'",
        "’": "'",
        "—": "-",
        "–": "-",
        "…": "...",
    }

    normalized = text

    for source, target in replacements.items():
        normalized = normalized.replace(source, target)

    return normalized


def _contains_spam_risk(text: str) -> bool:
    """
    Detect spam-like content.
    """

    lowered = text.lower()

    # Reject links
    if re.search(r"https?://|www\.", lowered):
        return True

    # Allow official sender names like CENRO
    if re.search(r"\b[A-Z]{10,}\b", text):
        return True

    # Reject too many exclamation marks
    if text.count("!") > 2:
        return True

    # Reject blacklisted terms
    for term in BLACKLIST_TERMS:
        if term in lowered:
            return True

    return False


def build_sms_message(template: str, values: Dict[str, Any]) -> str:
    """
    Build and validate SMS message.
    """

    # Replace placeholders
    rendered = _sanitize_template(template, values)

    # Normalize characters
    normalized = _normalize_for_sms(rendered)

    # Spam validation
    if _contains_spam_risk(normalized):
        raise ValueError(
            "Message contains content that violates SMS compliance rules."
        )

    # Character limit
    if len(normalized) > 100:
        raise ValueError(
            f"Message exceeds the 100-character limit ({len(normalized)} chars)."
        )

    # GSM-7 validation
    invalid = [c for c in normalized if c not in GSM7_CHARACTERS]

    if invalid:
        raise ValueError(
            f"Unsupported GSM-7 characters: {set(invalid)}"
        )

    return normalized

# ==========================================
# TEST
# ==========================================

template = "CENRO: Waste collection arrives in {eta} min. Please prepare your segregated waste."

values = {
    "eta": 10
}

try:
    message = build_sms_message(template, values)
    print(message)

except ValueError as e:
    print(e)