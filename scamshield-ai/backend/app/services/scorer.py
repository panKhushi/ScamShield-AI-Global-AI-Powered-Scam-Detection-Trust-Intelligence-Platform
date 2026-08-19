from app.models import ScoreFactor

STATUS_POINTS = {"good": 100, "warning": 50, "bad": 0}

def compute_rule_based_score(factors: list[ScoreFactor]) -> int:
    total_weight = sum(f.weight for f in factors)
    weighted_sum = sum(STATUS_POINTS[f.status] * f.weight for f in factors)
    return round(weighted_sum / total_weight) if total_weight else 0


def compute_final_score(rule_score: int, ml_scam_probability: float) -> tuple[int, str]:
    ml_trust_score = 100 - ml_scam_probability
    final_score = round((rule_score * 0.6) + (ml_trust_score * 0.4))

    if final_score >= 70:
        verdict = "safe"
    elif final_score >= 40:
        verdict = "suspicious"
    else:
        verdict = "dangerous"

    return final_score, verdict