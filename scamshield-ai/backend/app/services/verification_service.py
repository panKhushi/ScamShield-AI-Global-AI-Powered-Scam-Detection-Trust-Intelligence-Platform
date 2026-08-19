import re
from difflib import SequenceMatcher
from app.models import ScoreFactor


def _normalize(text: str) -> str:
    """Strips common suffixes/punctuation for fairer name-to-domain comparison."""
    text = text.lower().strip()
    text = re.sub(r"\b(inc|ltd|llc|pvt|private|limited|corp|corporation|co)\b", "", text)
    text = re.sub(r"[^a-z0-9]", "", text)
    return text


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def verify_company_domain_match(company_name: str, website_domain: str) -> ScoreFactor:
    """
    Checks whether the claimed company name plausibly matches its website domain.
    E.g. 'Acme Corp' vs 'acme.com' should match; 'Acme Corp' vs 'random-shop.xyz' should not.
    """
    normalized_name = _normalize(company_name)
    normalized_domain = _normalize(website_domain.split(".")[0])

    similarity = _similarity(normalized_name, normalized_domain)

    if similarity >= 0.7:
        return ScoreFactor(
            name="Company-Domain Consistency",
            weight=0.15,
            status="good",
            detail=f"Domain closely matches the claimed company name ({round(similarity * 100)}% similarity)",
        )
    elif similarity >= 0.4:
        return ScoreFactor(
            name="Company-Domain Consistency",
            weight=0.15,
            status="warning",
            detail=f"Domain only partially matches the claimed company name ({round(similarity * 100)}% similarity)",
        )
    else:
        return ScoreFactor(
            name="Company-Domain Consistency",
            weight=0.15,
            status="bad",
            detail=f"Domain does not resemble the claimed company name ({round(similarity * 100)}% similarity) — possible impersonation",
        )


def verify_recruiter_email_domain(recruiter_email: str, claimed_company: str) -> ScoreFactor:
    """
    Checks whether a recruiter's email domain is consistent with their claimed employer.
    Flags free/personal email providers as a red flag for a claimed corporate recruiter.
    """
    FREE_EMAIL_PROVIDERS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com"}

    if "@" not in recruiter_email:
        return ScoreFactor(
            name="Recruiter Email Consistency",
            weight=0.15,
            status="warning",
            detail="Invalid email format provided",
        )

    email_domain = recruiter_email.split("@")[-1].lower().strip()

    if email_domain in FREE_EMAIL_PROVIDERS:
        return ScoreFactor(
            name="Recruiter Email Consistency",
            weight=0.15,
            status="bad",
            detail=f"Recruiter is using a personal email provider ({email_domain}) rather than a company domain — common in fake recruiter scams",
        )

    normalized_company = _normalize(claimed_company)
    normalized_email_domain = _normalize(email_domain.split(".")[0])
    similarity = _similarity(normalized_company, normalized_email_domain)

    if similarity >= 0.6:
        return ScoreFactor(
            name="Recruiter Email Consistency",
            weight=0.15,
            status="good",
            detail=f"Recruiter's email domain is consistent with the claimed company",
        )
    else:
        return ScoreFactor(
            name="Recruiter Email Consistency",
            weight=0.15,
            status="warning",
            detail=f"Recruiter's email domain does not clearly match the claimed company — verify independently",
        )