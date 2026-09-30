import re

from app.models import ScoreFactor


SMS_RED_FLAG_CATEGORIES = {
    "Urgency / Threats": {
        "weight": 0.20,
        "patterns": [
            r"act\s+(now|immediately)",
            r"urgent(?:ly)?",
            r"last\s+warning",
            r"account\s+(will\s+be\s+)?(suspend|lock|clos|terminat|block)",
            r"within\s+(24|one)\s+hours?",
        ],
    },
    "Suspicious / Shortened Link": {
        "weight": 0.20,
        "patterns": [
            r"https?://\S+",
            r"\b(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly)/?\S*",
            r"click\s+(here|this\s+link|below)",
            r"tap\s+(here|the\s+link)",
        ],
    },
    "Prize / Refund Claim": {
        "weight": 0.15,
        "patterns": [
            r"\b(?:won|winner|winning|prize|lottery|reward|bonus)\b",
            r"\b(?:refund|rebate|cashback)\b",
            r"claim\s+(your|the)\s+\w*\s*(?:prize|reward|refund|winnings)",
        ],
    },
    "OTP / PIN / Bank Details Request": {
        "weight": 0.20,
        "patterns": [
            r"\b(?:otp|one[- ]time\s+password|pin|cvv)\b",
            r"(?:send|share|provide|confirm|enter|verify).{0,30}(?:otp|pin|password|card|bank|account)\b",
            r"\b(?:bank|debit|credit)\s+(?:details?|card)\b",
        ],
    },
    "Impersonation": {
        "weight": 0.15,
        "patterns": [
            r"\b(?:bank|police|government|tax|customs|delivery|courier|fedex|dhl|ups|royal\s+mail)\b",
            r"(?:from|message\s+from|on\s+behalf\s+of)\s+(?:your\s+)?(?:bank|government|delivery|courier)",
            r"customer\s+care|support\s+team|security\s+team",
        ],
    },
    "Unknown Sender Pattern": {
        "weight": 0.10,
        "patterns": [
            r"dear\s+(?:customer|user|winner|sir|madam)",
            r"you\s+have\s+been\s+selected",
            r"reply\s+(?:yes|no|stop)\s+to\s+\d+",
            r"call\s+\+?\d[\d\s-]{7,}",
        ],
    },
}


def analyze_sms_text(text: str) -> list[ScoreFactor]:
    text_lower = text.lower()
    factors: list[ScoreFactor] = []

    for category, config in SMS_RED_FLAG_CATEGORIES.items():
        matched = any(
            re.search(pattern, text_lower, re.MULTILINE)
            for pattern in config["patterns"]
        )
        factors.append(
            ScoreFactor(
                name=category,
                weight=config["weight"],
                status="bad" if matched else "good",
                detail=(
                    f"Text contains language typical of '{category.lower()}' scam messages"
                    if matched
                    else "No red-flag language detected in this category"
                ),
            )
        )

    return factors