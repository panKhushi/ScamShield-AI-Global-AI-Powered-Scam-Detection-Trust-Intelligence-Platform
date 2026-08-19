import httpx
import os
import base64
from app.models import ScoreFactor

VT_BASE = "https://www.virustotal.com/api/v3"

async def analyze_virustotal(url: str) -> ScoreFactor:
    api_key = os.getenv("VIRUSTOTAL_API_KEY")
    if not api_key:
        return ScoreFactor(
            name="VirusTotal", weight=0.25, status="warning",
            detail="API key not configured"
        )

    headers = {"x-apikey": api_key}
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(f"{VT_BASE}/urls/{url_id}", headers=headers)

            if res.status_code == 404:
                # Not seen before — submit it for scanning
                submit = await client.post(f"{VT_BASE}/urls", headers=headers, data={"url": url})
                return ScoreFactor(
                    name="VirusTotal", weight=0.25, status="warning",
                    detail="URL submitted for first-time scan — check back shortly"
                )

            data = res.json()
            stats = data["data"]["attributes"]["last_analysis_stats"]
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)

            if malicious > 0:
                return ScoreFactor(
                    name="VirusTotal", weight=0.25, status="bad",
                    detail=f"{malicious} security vendors flagged this as malicious"
                )
            elif suspicious > 0:
                return ScoreFactor(
                    name="VirusTotal", weight=0.25, status="warning",
                    detail=f"{suspicious} vendors marked this as suspicious"
                )
            else:
                return ScoreFactor(
                    name="VirusTotal", weight=0.25, status="good",
                    detail="No security vendors flagged this URL"
                )
    except Exception:
        return ScoreFactor(
            name="VirusTotal", weight=0.25, status="warning",
            detail="Could not reach VirusTotal API"
        )