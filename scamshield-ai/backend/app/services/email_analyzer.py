import re
from app.models import ScoreFactor

RED_FLAG_CATEGORIES = {
    "Urgency / Threat Language": {
        "weight": 0.20,
        "patterns": [
            r"account\s+(will\s+be\s+|has\s+been\s+)?(suspend|lock|clos|terminat|disabl)",
            r"immediate\s+action\s+required",
            r"verify\s+your\s+account\s+(now|immediately)",
            r"unusual\s+(activity|login|sign-in)",
            r"your\s+(account|payment)\s+(has\s+been\s+)?(compromised|flagged)",
            r"failure\s+to\s+(respond|comply|verify).{0,30}(result|lead)",
        ],
    },
    "Credential / Payment Request": {
        "weight": 0.25,
        "patterns": [
            r"(confirm|verify|update)\s+your\s+(password|account\s+details|payment\s+information)",
            r"enter\s+your\s+(password|pin|otp|card\s+number)",
            r"click\s+(here|below)\s+to\s+(verify|login|sign\s+in)",
            r"provide\s+your\s+(bank|card|social\s+security)",
        ],
    },
    "Generic Greeting": {
        "weight": 0.10,
        "patterns": [
            r"^dear\s+(customer|user|valued\s+customer|sir\s*/\s*madam)",
            r"dear\s+account\s+holder",
        ],
    },
    "Suspicious Link Language": {
        "weight": 0.20,
        "patterns": [
            r"click\s+(here|this\s+link|below)",
            r"bit\.ly|tinyurl|t\.co\/",
            r"http[s]?:\/\/(?!.*\b(google|microsoft|apple|amazon)\.com)[^\s]{0,10}\.(xyz|top|tk|ru|info|click)",
        ],
    },
    "Sender Impersonation Language": {
        "weight": 0.15,
        "patterns": [
            r"this\s+is\s+(an?\s+)?(official|automated)\s+(notice|message|email)\s+from",
            r"on\s+behalf\s+of\s+(paypal|amazon|microsoft|apple|bank|irs|government)",
            r"security\s+team\s+at",
        ],
    },
    "Unexpected Attachment/Prize": {
        "weight": 0.10,
        "patterns": [
            r"you\s+(have\s+)?won",
            r"claim\s+your\s+(prize|reward|refund)",
            r"open\s+the\s+attach(ed|ment)",
            r"invoice\s+attached",
        ],
    },
}


def analyze_email_text(text: str) -> list[ScoreFactor]:
    text_lower = text.lower()
    factors = []

    for category, config in RED_FLAG_CATEGORIES.items():
        matched = any(re.search(pattern, text_lower, re.MULTILINE) for pattern in config["patterns"])

        if matched:
            factors.append(ScoreFactor(
                name=category,
                weight=config["weight"],
                status="bad",
                detail=f"Text contains language typical of '{category.lower()}' phishing",
            ))
        else:
            factors.append(ScoreFactor(
                name=category,
                weight=config["weight"],
                status="good",
                detail="No red-flag language detected in this category",
            ))

    return factors