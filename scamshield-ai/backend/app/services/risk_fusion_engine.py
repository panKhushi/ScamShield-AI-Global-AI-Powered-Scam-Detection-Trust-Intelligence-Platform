from app.models import ScoreFactor


# Configurable weights — can be changed here without redeploying the whole app (FR-34).
# Weights should sum to 1.0 across whichever components are active for a given scan type.
RISK_WEIGHTS = {
    "domain": 0.15,
    "threat_intelligence": 0.15,
    "nlp_ml": 0.20,
    "community": 0.10,
    "anomaly": 0.10,
    "website": 0.20,
    "historical": 0.10,
}

STATUS_POINTS = {"good": 100, "warning": 50, "bad": 0}


def _factor_to_score(factor: ScoreFactor) -> float:
    """Converts a single ScoreFactor's status into a 0-100 sub-score."""
    return STATUS_POINTS.get(factor.status, 50)


def compute_component_score(factors: list[ScoreFactor], names: list[str]) -> float | None:
    """
    Averages the scores of factors whose name matches one of `names`.
    Returns None if no matching factor is present in this scan (component not applicable).
    """
    matched = [f for f in factors if f.name in names]
    if not matched:
        return None
    return sum(_factor_to_score(f) for f in matched) / len(matched)


def build_anomaly_factor(anomaly_result: dict) -> ScoreFactor:
    """Turns the Isolation Forest's raw output into a ScoreFactor for the pipeline."""
    if anomaly_result["is_anomaly"]:
        return ScoreFactor(
            name="Anomaly Detection",
            weight=0.10,
            status="warning",
            detail=f"This scan's pattern is statistically unusual compared to prior scans (score: {anomaly_result['anomaly_score']})",
        )
    else:
        return ScoreFactor(
            name="Anomaly Detection",
            weight=0.10,
            status="good",
            detail="Scan pattern is consistent with previously observed data",
        )


def fuse_risk(factors: list[ScoreFactor], ml_scam_probability: float) -> tuple[int, str, dict]:
    """
    Combines all available risk components into a single Trust/Risk Score (0-100)
    using the weighted Risk Fusion architecture. Components not present in this
    scan (e.g. no factors of that type) are excluded and remaining weights are
    re-normalized so they still sum to 1.0.

    Returns: (final_score, verdict, component_breakdown)
    """
    domain_score = compute_component_score(factors, ["Domain Age"])
    threat_intel_score = compute_component_score(factors, ["Google Safe Browsing", "VirusTotal"])
    community_score = compute_component_score(factors, ["Community Reports"])
    historical_score = compute_component_score(factors, ["Historical Intelligence"])
    anomaly_score = compute_component_score(factors, ["Anomaly Detection"])
    website_score = compute_component_score(
        factors, ["Login Form Detected", "OTP Request Detected", "Payment Form Detected", "Business Legitimacy Signals"]
    )
    nlp_ml_score = 100 - ml_scam_probability  # invert: probability of scam -> trust score

    components = {
        "domain": domain_score,
        "threat_intelligence": threat_intel_score,
        "community": community_score,
        "historical": historical_score,
        "nlp_ml": nlp_ml_score,
        "anomaly": anomaly_score,
        "website": website_score,
    }

    # Only include components actually present for this scan; re-normalize weights.
    active = {k: v for k, v in components.items() if v is not None}
    total_weight = sum(RISK_WEIGHTS[k] for k in active)

    if total_weight == 0:
        # Fallback: shouldn't happen in practice, but avoids a divide-by-zero.
        final_score = round(nlp_ml_score)
    else:
        weighted_sum = sum(active[k] * (RISK_WEIGHTS[k] / total_weight) for k in active)
        final_score = round(weighted_sum)

    if final_score >= 70:
        verdict = "safe"
    elif final_score >= 40:
        verdict = "suspicious"
    else:
        verdict = "dangerous"

    breakdown = {k: round(v, 1) for k, v in active.items()}

    return final_score, verdict, breakdown