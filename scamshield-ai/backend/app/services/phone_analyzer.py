import re

from app.models import ScoreFactor

PHONE_PATTERN = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
SCAM_CONTEXT = re.compile(r"(?:otp|pin|bank|payment|prize|winner|refund|urgent|verify|account)", re.IGNORECASE)


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if digits.startswith("00"):
        digits = digits[2:]
    return f"+{digits}" if digits else ""


def analyze_phone(value: str) -> list[ScoreFactor]:
    normalized = normalize_phone(value)
    valid_shape = bool(normalized and 8 <= len(normalized.lstrip("+")) <= 15)
    factors = [
        ScoreFactor(
            name="Phone Number Format",
            weight=0.10,
            status="good" if valid_shape else "warning",
            detail="Phone number has a plausible international format" if valid_shape else "Could not confirm a valid international phone number",
        )
    ]
    if SCAM_CONTEXT.search(value):
        factors.append(ScoreFactor(
            name="Scam Context",
            weight=0.20,
            status="bad",
            detail="The surrounding text contains payment, verification, urgency, or prize language",
        ))
    else:
        factors.append(ScoreFactor(
            name="Scam Context",
            weight=0.20,
            status="good",
            detail="No common scam context was found around this number",
        ))
    return factors
