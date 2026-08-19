import whois
from datetime import datetime, timezone
from app.models import ScoreFactor

def get_domain_age_days(domain: str) -> int | None:
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date is None:
            return None
        if creation_date.tzinfo is None:
            creation_date = creation_date.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - creation_date).days
        return age
    except Exception:
        return None

def analyze_whois(domain: str) -> ScoreFactor:
    age_days = get_domain_age_days(domain)

    if age_days is None:
        return ScoreFactor(
            name="Domain Age",
            weight=0.2,
            status="warning",
            detail="Could not retrieve WHOIS data",
        )

    if age_days < 90:
        return ScoreFactor(
            name="Domain Age",
            weight=0.2,
            status="bad",
            detail=f"Domain registered only {age_days} days ago — high risk",
        )
    elif age_days < 365:
        return ScoreFactor(
            name="Domain Age",
            weight=0.2,
            status="warning",
            detail=f"Domain is {age_days} days old — relatively new",
        )
    else:
        years = age_days // 365
        return ScoreFactor(
            name="Domain Age",
            weight=0.2,
            status="good",
            detail=f"Domain has existed for {years}+ years",
        )
def get_raw_domain_age_days(domain: str) -> int | None:
    """Returns raw age in days, or None if unavailable — used for ML features."""
    return get_domain_age_days(domain)  # reuses your existing helper function