"""Shared automation boundary for evidence classification and application."""
from __future__ import annotations

from collections.abc import Callable, Mapping


SAFE_SCOPES = {
    "entity_identity_only",
    "bibliographic_hint",
    "term_existence",
    "event_identity_only",
}

LIMITED_SCOPES = SAFE_SCOPES

L3_CHANGE_VALUES = {
    "evidence_status": {"externally_verified"},
    "consensus": {"confirmed"},
    "confidence": {"high"},
}

REQUIRED_EVIDENCE_FIELDS = (
    "ku_path",
    "platform",
    "source_type",
    "source_authority",
    "source_independence_group",
    "claim_scope",
    "claim_target",
    "match_quality",
    "match_score",
    "recommended_changes",
)


def recommended_changes(entry: Mapping[str, object]) -> dict:
    changes = entry.get("recommended_changes") or {}
    return dict(changes) if isinstance(changes, Mapping) else {}


def validate_evidence_schema(entry: Mapping[str, object]) -> list[str]:
    issues: list[str] = []
    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in entry or entry[field] is None or entry[field] == "":
            issues.append(f"missing required evidence field: {field}")
    if entry.get("blocking_reason"):
        issues.append(f"BLOCKED: evidence has blocking_reason: {entry['blocking_reason']}")
    match_quality = entry.get("match_quality")
    if match_quality and match_quality not in {"strong", "medium", "weak", "none"}:
        issues.append(f"invalid match_quality: {match_quality}")
    return issues


def validate_recommended_changes(changes: Mapping[str, object], entry: Mapping[str, object]) -> list[str]:
    warnings: list[str] = []
    claim_scope = str(entry.get("claim_scope") or "entity_identity_only")
    if changes.get("confidence") == "high":
        warnings.append("BLOCKED: single evidence source cannot set confidence=high")
    if changes.get("evidence_status") == "externally_verified":
        if claim_scope in LIMITED_SCOPES and not entry.get("second_source_confirmed"):
            warnings.append(
                f"BLOCKED: {claim_scope} single-source evidence cannot set evidence_status=externally_verified"
            )
    if changes.get("consensus") == "confirmed":
        if claim_scope in LIMITED_SCOPES:
            warnings.append(f"BLOCKED: {claim_scope} evidence cannot set consensus=confirmed")
        if entry.get("match_quality") != "strong":
            warnings.append("BLOCKED: consensus=confirmed requires strong evidence")
    if "source_count" in changes:
        warnings.append("BLOCKED: source_count auto-increment not allowed")
    return warnings


def l3_reasons(entry: Mapping[str, object]) -> list[str]:
    reasons: list[str] = []
    if entry.get("blocking_reason"):
        reasons.append(f"blocking_reason: {entry['blocking_reason']}")
    proposed = str(entry.get("proposed_ku_path") or "")
    if proposed and not entry.get("ku_path"):
        reasons.append("proposed_new_event_ku" if "events/" in proposed else "proposed_new_ku")
    changes = recommended_changes(entry)
    for field, unsafe_values in L3_CHANGE_VALUES.items():
        if changes.get(field) in unsafe_values:
            reasons.append(f"unsafe_recommended_change:{field}={changes[field]}")
    if "source_count" in changes:
        reasons.append("source_count_auto_change_forbidden")
    action = str(entry.get("recommended_action") or "").lower()
    if "event" in action and ("create" in action or "apply" in action) and proposed:
        reasons.append("event_boundary_requires_agent_decision")
    if str(entry.get("event_ku_decision") or "").startswith("defer"):
        reasons.append("event_ku_decision_deferred")
    return reasons


def classify_evidence(
    entry: Mapping[str, object],
    ku_exists: Callable[[str], bool],
) -> tuple[str, str, list[str]]:
    """Return risk, action and reasons without making a semantic decision."""
    reasons = l3_reasons(entry)
    if reasons:
        return "L3", "defer", reasons

    changes = recommended_changes(entry)
    scope = str(entry.get("claim_scope") or entry.get("claim_affordance") or "")
    match_quality = str(entry.get("match_quality") or "")
    ku_path = str(entry.get("ku_path") or "")

    if ku_path and ku_exists(ku_path):
        if (
            scope in SAFE_SCOPES
            and match_quality in {"strong", "medium"}
            and changes.get("evidence_status") in {None, "source_backed", "partially_verified"}
            and changes.get("confidence") in {None, "low", "medium"}
            and changes.get("consensus") in {None, "tentative"}
        ):
            return "L1", "apply_low_risk_existing_ku", [
                "existing_ku",
                f"safe_scope:{scope}",
                f"match_quality:{match_quality}",
            ]
        return "L2", "dry_run_then_agent_review", [
            "existing_ku_but_not_l1",
            f"scope:{scope or 'missing'}",
            f"match_quality:{match_quality or 'missing'}",
        ]

    if entry.get("candidate_type") or entry.get("claim_affordance"):
        return "L2", "plan_only_agent_review", ["candidate_or_collected_evidence"]
    return "L3", "defer", ["unrecognized_or_missing_ku_path"]
