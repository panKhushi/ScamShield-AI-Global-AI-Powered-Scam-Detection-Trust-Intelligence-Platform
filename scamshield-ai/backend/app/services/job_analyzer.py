import re
from app.models import ScoreFactor

# Each category: (regex patterns, weight, label)
RED_FLAG_CATEGORIES = {
    "Upfront Payment Request": {
    "weight": 0.30,
    "patterns": [
        r"pay\s+.{0,20}(fee|deposit)",
        r"registration\s+fee",
        r"processing\s+fee",
        r"training\s+(fee|cost|charge)",
        r"send\s+(us\s+)?money",
        r"refundable\s+deposit",
        r"purchase\s+(equipment|a\s+starter\s+kit)",
        r"\$\d+\s+(fee|deposit|charge)",
    ],
},
    "Sensitive Info Requested Early": {
        "weight": 0.20,
        "patterns": [
            r"social\s+security\s+number",
            r"bank\s+(account|routing)\s+(number|details)",
            r"credit\s+card\s+(number|details)",
            r"send.{0,20}(id|passport|aadhar|pan\s+card)\s+(copy|scan|photo)",
        ],
    },
    "Urgency / Pressure Tactics": {
        "weight": 0.15,
        "patterns": [
            r"immediate(ly)?\s+(hire|start|joining)",
            r"urgent(ly)?\s+(hiring|required|need)",
            r"act\s+(now|fast|quickly)",
            r"limited\s+(time|slots|seats)",
            r"offer\s+expires",
            r"no\s+interview\s+(required|needed)",
        ],
    },
    "Unrealistic Compensation": {
        "weight": 0.15,
        "patterns": [
            r"earn\s+\$?\d{3,}\s*(per|/)\s*(day|hour)",
            r"unlimited\s+earning",
            r"guaranteed\s+income",
            r"no\s+experience.{0,20}high\s+pay",
            r"quick\s+money",
            r"work\s+from\s+home.{0,20}\$\d{3,}",
        ],
    },
    "Suspicious Communication Channel": {
        "weight": 0.10,
        "patterns": [
            r"contact\s+(us\s+)?(on|via)\s+telegram",
            r"whatsapp\s+(only|number)",
            r"personal\s+(gmail|yahoo|hotmail)",
            r"reply\s+to\s+this\s+(email|number)\s+only",
        ],
    },
    "Vague Job Details": {
        "weight": 0.10,
        "patterns": [
            r"flexible\s+hours.{0,30}no\s+experience",
            r"simple\s+tasks",
            r"data\s+entry.{0,20}no\s+skills",
            r"be\s+your\s+own\s+boss",
        ],
    },
}


def analyze_job_text(text: str) -> list[ScoreFactor]:
    text_lower = text.lower()
    factors = []

    for category, config in RED_FLAG_CATEGORIES.items():
        matched = any(re.search(pattern, text_lower) for pattern in config["patterns"])

        if matched:
            factors.append(ScoreFactor(
                name=category,
                weight=config["weight"],
                status="bad",
                detail=f"Text contains language typical of '{category.lower()}' scams",
            ))
        else:
            factors.append(ScoreFactor(
                name=category,
                weight=config["weight"],
                status="good",
                detail="No red-flag language detected in this category",
            ))

    return factors