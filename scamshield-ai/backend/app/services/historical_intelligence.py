import hashlib
import math
import os
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.orm import Session

from app.db_models import HistoricalEvent, HistoricalRecord
from app.models import HistoricalIntelligence, ScoreFactor

WINDOW_DAYS = int(os.getenv("HISTORY_WINDOW_DAYS", "90"))
VERY_RECENT_DAYS = int(os.getenv("HISTORY_VERY_RECENT_DAYS", "30"))
CRITICAL_RECENT_DAYS = int(os.getenv("HISTORY_CRITICAL_RECENT_DAYS", "7"))
TEXT_SIMILARITY_THRESHOLD = float(os.getenv("HISTORY_TEXT_SIMILARITY_THRESHOLD", "0.72"))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def normalize_url(value: str) -> str:
    candidate = value.strip()
    if not candidate.startswith(("http://", "https://")):
        candidate = f"https://{candidate}"

    parsed = urlsplit(candidate)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if hostname.startswith("www."):
        hostname = hostname[4:]

    try:
        port = parsed.port
    except ValueError:
        port = None
    netloc = hostname
    if port and not ((parsed.scheme == "http" and port == 80) or (parsed.scheme == "https" and port == 443)):
        netloc = f"{hostname}:{port}"

    path = parsed.path.rstrip("/") or "/"
    query_pairs = sorted(parse_qsl(parsed.query, keep_blank_values=True))
    query = urlencode(query_pairs, doseq=True)
    return urlunsplit(("", netloc, path, query, ""))[2:]


def _root_domain(hostname: str) -> str:
    host = hostname.lower().strip(".")
    labels = host.split(".")
    if len(labels) <= 2 or all(label.isdigit() for label in labels):
        return host
    return ".".join(labels[-2:])


def url_domains(value: str) -> tuple[str, str]:
    normalized = normalize_url(value)
    host = urlsplit(f"https://{normalized}").hostname or ""
    return host, _root_domain(host)


def normalize_text(value: str) -> str:
    text = value.casefold().replace("₹", " rs ")
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"[^\w\s@.+-]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def entity_fingerprint(entity_type: str, normalized_value: str) -> str:
    return fingerprint(f"{entity_type}:{normalized_value}")


def _text_similarity(left: str, right: str) -> float:
    left_tokens = Counter(left.split())
    right_tokens = Counter(right.split())
    vocabulary = set(left_tokens) | set(right_tokens)
    if not vocabulary:
        return 1.0
    dot = sum(left_tokens[token] * right_tokens[token] for token in vocabulary)
    left_norm = math.sqrt(sum(count * count for count in left_tokens.values()))
    right_norm = math.sqrt(sum(count * count for count in right_tokens.values()))
    cosine = dot / (left_norm * right_norm) if left_norm and right_norm else 0.0
    sequence = SequenceMatcher(None, left, right).ratio()
    return round((cosine * 0.7) + (sequence * 0.3), 4)


def _normalized_value(entity_type: str, value: str) -> str:
    return normalize_url(value) if entity_type == "url" else normalize_text(value)


def _match_records(entity_type: str, value: str, records: list[HistoricalRecord]) -> list[tuple[HistoricalRecord, str, float]]:
    normalized = _normalized_value(entity_type, value)
    value_hash = entity_fingerprint(entity_type, normalized)
    matches: list[tuple[HistoricalRecord, str, float]] = []

    if entity_type == "url":
        current_host, current_root = url_domains(value)
        for record in records:
            if record.entity_hash == value_hash:
                matches.append((record, "exact", 1.0))
                continue
            try:
                record_host, record_root = url_domains(record.normalized_value)
            except (ValueError, TypeError):
                continue
            if record_host == current_host:
                matches.append((record, "domain", 0.95))
            elif record_root == current_root:
                matches.append((record, "root_domain", 0.85))
        return matches

    for record in records:
        similarity = 1.0 if record.entity_hash == value_hash else _text_similarity(normalized, record.normalized_value)
        if similarity >= TEXT_SIMILARITY_THRESHOLD:
            matches.append((record, "exact" if similarity == 1.0 else "similar", similarity))
    return matches


def _recency_status(last_seen: datetime | None, now: datetime) -> str:
    if last_seen is None:
        return "NO_HISTORICAL_DATA"
    age = now - last_seen
    if age <= timedelta(days=CRITICAL_RECENT_DAYS):
        return "CRITICAL_RECENCY"
    if age <= timedelta(days=VERY_RECENT_DAYS):
        return "VERY_RECENT"
    if age <= timedelta(days=WINDOW_DAYS):
        return "RECENT_RECORD"
    return "OLD_RECORD"


def _risk_label(report_count: int, scan_count: int, recent_reports: int, classifications: list[str]) -> str:
    if report_count == 0 and scan_count == 0:
        return "UNKNOWN"
    if recent_reports > 0 or report_count >= 3 or any(value in {"dangerous", "scam"} for value in classifications):
        return "HIGH"
    if report_count > 0:
        return "MEDIUM"
    return "LOW"


def _trend(events: list[HistoricalEvent], now: datetime) -> str:
    recent_start = now - timedelta(days=30)
    previous_start = now - timedelta(days=60)
    recent = sum(1 for event in events if event.event_type == "report" and recent_start <= _as_aware(event.created_at) <= now)
    previous = sum(1 for event in events if event.event_type == "report" and previous_start <= _as_aware(event.created_at) < recent_start)
    if recent == previous == 0:
        return "INSUFFICIENT_DATA"
    if recent > previous:
        return "INCREASING"
    if recent < previous:
        return "DECREASING"
    return "STABLE"


def check_history(db: Session, entity_type: str, value: str, now: datetime | None = None) -> HistoricalIntelligence:
    now = now or utc_now()
    records = db.query(HistoricalRecord).filter(HistoricalRecord.entity_type == entity_type).all()
    matches = _match_records(entity_type, value, records)
    if not matches:
        return HistoricalIntelligence(entity_type=entity_type, found=False)

    record_ids = [record.id for record, _, _ in matches]
    cutoff = now - timedelta(days=WINDOW_DAYS)
    events = db.query(HistoricalEvent).filter(
        HistoricalEvent.record_id.in_(record_ids),
        HistoricalEvent.created_at >= cutoff,
    ).order_by(HistoricalEvent.created_at.asc()).all()
    all_events = db.query(HistoricalEvent).filter(HistoricalEvent.record_id.in_(record_ids)).all()

    first_seen = min((_as_aware(record.first_seen) for record, _, _ in matches), default=None)
    last_seen = max((_as_aware(record.last_seen) for record, _, _ in matches), default=None)
    reports = [event for event in events if event.event_type == "report"]
    scans = [event for event in events if event.event_type == "scan"]
    recent_cutoff = now - timedelta(days=30)
    recent_reports = [event for event in reports if _as_aware(event.created_at) >= recent_cutoff]
    classifications = [event.classification for event in all_events if event.classification]

    timeline = [
        {
            "date": _as_aware(event.created_at).isoformat(),
            "event_type": event.event_type,
            "source": event.source,
            "classification": event.classification,
            "risk_score": event.risk_score,
        }
        for event in all_events
        if _as_aware(event.created_at) >= cutoff
    ]
    match_summaries = [
        {
            "match_type": match_type,
            "similarity_score": similarity,
            "classification": record.classification,
            "last_seen": _as_aware(record.last_seen).isoformat(),
            "source": record.source,
        }
        for record, match_type, similarity in sorted(matches, key=lambda item: item[2], reverse=True)
    ]

    return HistoricalIntelligence(
        entity_type=entity_type,
        found=True,
        first_seen=first_seen.isoformat() if first_seen else None,
        last_seen=last_seen.isoformat() if last_seen else None,
        reports_last_3_months=len(reports),
        scans_last_3_months=len(scans),
        recent_reports=len(recent_reports),
        recency_status=_recency_status(last_seen, now),
        historical_risk=_risk_label(len(reports), len(scans), len(recent_reports), classifications),
        trend=_trend(all_events, now),
        matches=match_summaries,
        timeline=timeline,
    )


def historical_factor(history: HistoricalIntelligence) -> ScoreFactor:
    if not history.found:
        return ScoreFactor(
            name="Historical Intelligence",
            weight=0.15,
            status="warning",
            detail="No historical record found; this is insufficient evidence to consider the entity safe",
        )
    status = {"HIGH": "bad", "MEDIUM": "warning", "LOW": "warning", "UNKNOWN": "warning"}[history.historical_risk]
    return ScoreFactor(
        name="Historical Intelligence",
        weight=0.15,
        status=status,
        detail=(
            f"{history.recency_status.replace('_', ' ').title()}: {history.reports_last_3_months} report(s) and "
            f"{history.scans_last_3_months} scan(s) in the last {WINDOW_DAYS} days"
        ),
    )


def _get_or_create(db: Session, entity_type: str, normalized: str, original: str, now: datetime) -> HistoricalRecord:
    entity_hash = entity_fingerprint(entity_type, normalized)
    record = db.query(HistoricalRecord).filter(HistoricalRecord.entity_hash == entity_hash).first()
    if record is None:
        record = HistoricalRecord(
            entity_type=entity_type,
            entity_hash=entity_hash,
            normalized_value=normalized,
            original_value=original[:500] if entity_type == "url" else None,
            first_seen=now,
            last_seen=now,
            scan_count=0,
            confirmed_report_count=0,
        )
        db.add(record)
        db.flush()
    return record


def _record_event(
    db: Session,
    entity_type: str,
    value: str,
    event_type: str,
    classification: str,
    risk_score: int,
    source: str,
    user_id: str | None = None,
) -> None:
    now = utc_now()
    normalized = _normalized_value(entity_type, value)
    record = _get_or_create(db, entity_type, normalized, value, now)
    record.last_seen = now
    if classification in {"dangerous", "scam"} or not record.classification:
        record.classification = classification
    record.risk_score = risk_score
    record.source = source
    if event_type == "scan":
        record.scan_count += 1
    else:
        record.confirmed_report_count += 1
    db.add(HistoricalEvent(
        record_id=record.id,
        event_type=event_type,
        source=source,
        classification=classification,
        risk_score=risk_score,
        user_id=user_id,
        created_at=now,
    ))
    db.commit()


def record_scan(db: Session, entity_type: str, value: str, classification: str, risk_score: int, user_id: str | None) -> None:
    _record_event(db, entity_type, value, "scan", classification, risk_score, "user_scan", user_id)


def record_report(db: Session, entity_type: str, value: str, classification: str = "scam", risk_score: int = 0, user_id: str | None = None) -> None:
    _record_event(db, entity_type, value, "report", classification, risk_score, "community_report", user_id)
