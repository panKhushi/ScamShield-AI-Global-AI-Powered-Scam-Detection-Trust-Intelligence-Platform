import httpx
import os
from app.models import ScoreFactor

SAFE_BROWSING_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

async def analyze_safe_browsing(url: str) -> ScoreFactor:
    api_key = os.getenv("GOOGLE_SAFE_BROWSING_KEY")
    if not api_key:
        return ScoreFactor(
            name="Google Safe Browsing", weight=0.3, status="warning",
            detail="API key not configured"
        )

    payload = {
        "client": {"clientId": "scamshield-ai", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(f"{SAFE_BROWSING_URL}?key={api_key}", json=payload)
            data = res.json()

        if data.get("matches"):
            threat_type = data["matches"][0].get("threatType", "UNKNOWN")
            return ScoreFactor(
                name="Google Safe Browsing", weight=0.3, status="bad",
                detail=f"Flagged for: {threat_type}"
            )
        else:
            return ScoreFactor(
                name="Google Safe Browsing", weight=0.3, status="good",
                detail="No known threats found"
            )
    except Exception:
        return ScoreFactor(
            name="Google Safe Browsing", weight=0.3, status="warning",
            detail="Could not reach Safe Browsing API"
        )