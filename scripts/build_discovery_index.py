#!/usr/bin/env python3
"""Build one deterministic candidate index across active discovery origins."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from collections import Counter
from pathlib import Path

import yaml


BASE = Path(__file__).resolve().parents[1]
CANDIDATE_OUTPUT = "06-runtime/state/candidate-index.jsonl"
MANIFEST_OUTPUT = "06-runtime/state/discovery-manifest.json"
REQUIRED_FIELDS = {
    "candidate_id",
    "origin_type",
    "origin_ref",
    "candidate_type",
    "payload",
    "evidence_refs",
    "state",
    "decision",
    "created_at",
    "updated_at",
}
ORIGIN_TYPES = {"source", "knowledge", "relation_graph", "external", "output"}
CANDIDATE_TYPES = {"unit", "claim", "relation", "evidence", "theme", "topic", "cluster", "hierarchy_change"}
CLUSTER_TARGET_LEVELS = {"domain", "dimension", "theme", "topic", "ku", "claim", "relation"}
CLUSTER_PAYLOAD_FIELDS = {
    "target_level",
    "scope",
    "basis",
    "input_snapshot",
    "members",
    "boundary",
    "counterexamples",
    "stability_across_runs",
}
VALID_STATES = {
    "candidate",
    "needs_evidence",
    "ready_for_review",
    "approved",
    "applied",
    "no_delta",
    "deferred",
    "rejected",
    "blocked",
}
DECISION_STATUSES = {"pending", "approved", "deferred", "rejected", "blocked"}
DECISION_FIELDS = {"status", "reason", "decided_by", "decided_at"}
KNOWLEDGE_MATCH_STATUSES = {
    "novel",
    "existing_target",
    "potential_duplicate",
    "potential_conflict",
    "undetermined",
}
LIFECYCLE_CLASSES = {"active", "terminal", "historical_non_replay"}
RETIRED_RELATION_SIGNALS = {"s2_legacy_related", "s8_same_structure"}
TRANSITION_REQUIRED_FIELDS = {"candidate_id", "expected_state", "state", "decision", "updated_at"}
TRANSITION_OPTIONAL_FIELDS = {"target_ref", "payload_patch", "evidence_refs_add"}


def normalized_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(normalized_bytes(path)).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"{path}:{number}: candidate must be an object")
            records.append(item)
    return records


def candidate_sources(root: Path) -> list[Path]:
    paths: set[Path] = set()
    relation = root / "04-knowledge" / "quality" / "relation-candidates.yml"
    if relation.is_file():
        paths.add(relation)
    paths.update(path for path in (root / "03-processing").rglob("candidate-ledger.jsonl") if path.is_file())
    paths.update(path for path in (root / "06-runtime" / "automation").rglob("candidate-ledger.jsonl") if path.is_file())
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def candidate_decision_sources(root: Path) -> list[Path]:
    runtime = root / "06-runtime" / "automation"
    if not runtime.is_dir():
        return []
    return sorted(
        (path for path in runtime.rglob("candidate-decision-ledger.jsonl") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def load_source(path: Path) -> list[dict]:
    if path.suffix.lower() in {".yml", ".yaml"}:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or []
        if not isinstance(data, list):
            raise ValueError(f"{path}: candidate source must be a list")
        return [item for item in data if isinstance(item, dict)]
    return read_jsonl(path)


def validate_candidate(item: dict) -> list[str]:
    candidate_id = str(item.get("candidate_id") or "<missing>")
    issues = [f"{candidate_id}: missing {field}" for field in sorted(REQUIRED_FIELDS - set(item))]
    if item.get("origin_type") not in ORIGIN_TYPES:
        issues.append(f"{candidate_id}: invalid origin_type")
    if item.get("candidate_type") not in CANDIDATE_TYPES:
        issues.append(f"{candidate_id}: invalid candidate_type")
    if item.get("state") not in VALID_STATES:
        issues.append(f"{candidate_id}: invalid state")
    if not isinstance(item.get("evidence_refs"), list):
        issues.append(f"{candidate_id}: evidence_refs must be a list")
    decision = item.get("decision")
    if not isinstance(decision, dict):
        issues.append(f"{candidate_id}: decision must be an object")
    else:
        for field in sorted(DECISION_FIELDS - set(decision)):
            issues.append(f"{candidate_id}: decision missing {field}")
        if decision.get("status") not in DECISION_STATUSES:
            issues.append(f"{candidate_id}: invalid decision status")
        if item.get("state") in {"applied", "no_delta"} and decision.get("status") != "approved":
            issues.append(f"{candidate_id}: terminal write-back requires approved decision")
        if item.get("state") in {"rejected", "deferred", "blocked"} and decision.get("status") != item.get("state"):
            issues.append(f"{candidate_id}: decision/state mismatch")
    if item.get("lifecycle_class") not in LIFECYCLE_CLASSES:
        issues.append(f"{candidate_id}: invalid lifecycle_class")
    payload = item.get("payload")
    if (
        item.get("candidate_type") == "relation"
        and item.get("lifecycle_class") == "active"
        and isinstance(payload, dict)
        and payload.get("signal") in RETIRED_RELATION_SIGNALS
    ):
        issues.append(f"{candidate_id}: retired relation signal cannot remain active")
    knowledge_match = payload.get("knowledge_match") if isinstance(payload, dict) else None
    if isinstance(knowledge_match, dict):
        if knowledge_match.get("status") not in KNOWLEDGE_MATCH_STATUSES:
            issues.append(f"{candidate_id}: invalid knowledge_match status")
        if not isinstance(knowledge_match.get("target_refs"), list):
            issues.append(f"{candidate_id}: knowledge_match.target_refs must be a list")
    if item.get("candidate_type") == "cluster":
        if not isinstance(payload, dict):
            issues.append(f"{candidate_id}: cluster payload must be an object")
        else:
            missing = CLUSTER_PAYLOAD_FIELDS - set(payload)
            issues.extend(f"{candidate_id}: cluster payload missing {field}" for field in sorted(missing))
            if payload.get("target_level") not in CLUSTER_TARGET_LEVELS:
                issues.append(f"{candidate_id}: invalid cluster target_level")
            if not isinstance(payload.get("members"), list) or not payload.get("members"):
                issues.append(f"{candidate_id}: cluster members must be a non-empty list")
            if not isinstance(payload.get("counterexamples"), list):
                issues.append(f"{candidate_id}: cluster counterexamples must be a list")
    return issues


def canonical_candidate(item: dict) -> tuple[dict, list[str]]:
    """Normalize documented legacy spellings into the single current projection."""
    current = deepcopy({key: value for key, value in item.items() if not str(key).startswith("_")})
    normalizations: list[str] = []
    decision = current.get("decision")
    if isinstance(decision, dict):
        if decision.get("status") == "applied" and current.get("state") == "applied":
            decision["status"] = "approved"
            normalizations.append("decision_applied_to_approved")
        if decision.get("status") == "deferred" and current.get("state") == "needs_evidence":
            decision["status"] = "pending"
            normalizations.append("needs_evidence_decision_to_pending")
        for field in DECISION_FIELDS:
            if field not in decision:
                decision[field] = "legacy-record-unattributed" if field == "decided_by" else None
                normalizations.append(f"decision_missing_{field}")
    payload = current.get("payload")
    knowledge_match = payload.get("knowledge_match") if isinstance(payload, dict) else None
    if isinstance(knowledge_match, dict) and knowledge_match.get("status") == "existing":
        knowledge_match["status"] = "existing_target"
        normalizations.append("knowledge_match_existing_to_existing_target")
    if (
        isinstance(knowledge_match, dict)
        and knowledge_match.get("status") == "existing_target"
        and not isinstance(knowledge_match.get("target_refs"), list)
    ):
        target_refs: list[str] = []
        for value in (current.get("target_ref"), payload.get("unit") if isinstance(payload, dict) else None):
            if isinstance(value, str) and value and value not in target_refs:
                target_refs.append(value)
        for relation in payload.get("relation_candidates", []) if isinstance(payload, dict) else []:
            target = relation.get("target") if isinstance(relation, dict) else None
            if isinstance(target, str) and target:
                normalized_target = target if target.startswith("04-knowledge/units/") else f"04-knowledge/units/{target}"
                if normalized_target not in target_refs:
                    target_refs.append(normalized_target)
        knowledge_match["target_refs"] = target_refs
        normalizations.append("knowledge_match_target_refs_derived")

    if (
        isinstance(payload, dict)
        and payload.get("migration_mode") == "read_only_reference"
        and current.get("state") == "deferred"
    ):
        lifecycle = "historical_non_replay"
    elif current.get("state") in {"applied", "no_delta", "rejected"}:
        lifecycle = "terminal"
    else:
        lifecycle = "active"
    current["lifecycle_class"] = lifecycle
    return current, normalizations


def apply_candidate_transition(current: dict, transition: dict) -> tuple[dict | None, list[str], list[str]]:
    """Apply one append-only lifecycle transition without rewriting its source ledger."""
    candidate_id = str(transition.get("candidate_id") or "<missing>")
    issues = [
        f"{candidate_id}: transition missing {field}"
        for field in sorted(TRANSITION_REQUIRED_FIELDS - set(transition))
    ]
    unexpected = set(transition) - TRANSITION_REQUIRED_FIELDS - TRANSITION_OPTIONAL_FIELDS
    issues.extend(f"{candidate_id}: transition has unsupported field {field}" for field in sorted(unexpected))
    if issues:
        return None, issues, []
    if transition["expected_state"] != current.get("state"):
        return None, [
            f"{candidate_id}: transition expected state {transition['expected_state']} but found {current.get('state')}"
        ], []
    if not isinstance(transition.get("decision"), dict):
        return None, [f"{candidate_id}: transition decision must be an object"], []

    updated = deepcopy(current)
    updated["state"] = transition["state"]
    updated["decision"] = deepcopy(transition["decision"])
    updated["updated_at"] = transition["updated_at"]
    if "target_ref" in transition:
        updated["target_ref"] = transition["target_ref"]
    if "payload_patch" in transition:
        payload_patch = transition["payload_patch"]
        if not isinstance(payload_patch, dict):
            return None, [f"{candidate_id}: transition payload_patch must be an object"], []
        payload = updated.get("payload")
        if not isinstance(payload, dict):
            payload = {}
        payload.update(deepcopy(payload_patch))
        updated["payload"] = payload
    if "evidence_refs_add" in transition:
        additions = transition["evidence_refs_add"]
        if not isinstance(additions, list):
            return None, [f"{candidate_id}: transition evidence_refs_add must be a list"], []
        evidence_refs = updated.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            evidence_refs = []
        for ref in additions:
            if ref not in evidence_refs:
                evidence_refs.append(ref)
        updated["evidence_refs"] = evidence_refs

    normalized, normalizations = canonical_candidate(updated)
    validation_issues = validate_candidate(normalized)
    if validation_issues:
        return None, validation_issues, normalizations
    return normalized, [], normalizations


def build(root: Path = BASE) -> tuple[list[dict], dict]:
    sources = candidate_sources(root)
    transition_sources = candidate_decision_sources(root)
    indexed: dict[str, dict] = {}
    issues: list[str] = []
    normalization_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    for path in sources:
        relative = path.relative_to(root).as_posix()
        try:
            records = load_source(path)
        except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
            issues.append(f"{relative}: {exc}")
            continue
        source_counts[relative] = len(records)
        for raw in records:
            item, normalizations = canonical_candidate(raw)
            normalization_counts.update(normalizations)
            issues.extend(validate_candidate(item))
            candidate_id = str(item.get("candidate_id") or "")
            if not candidate_id:
                continue
            previous = indexed.get(candidate_id)
            if previous is not None and previous != item:
                issues.append(f"{candidate_id}: conflicting duplicate definitions")
                continue
            indexed[candidate_id] = item

    transition_source_counts: Counter[str] = Counter()
    applied_transition_counts: Counter[str] = Counter()
    for path in transition_sources:
        relative = path.relative_to(root).as_posix()
        try:
            transitions = read_jsonl(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            issues.append(f"{relative}: {exc}")
            continue
        transition_source_counts[relative] = len(transitions)
        for line_number, transition in enumerate(transitions, start=1):
            candidate_id = str(transition.get("candidate_id") or "")
            current = indexed.get(candidate_id)
            if current is None:
                issues.append(f"{relative}:{line_number}: unknown candidate {candidate_id or '<missing>'}")
                continue
            updated, transition_issues, normalizations = apply_candidate_transition(current, transition)
            if transition_issues:
                issues.extend(f"{relative}:{line_number}: {issue}" for issue in transition_issues)
                continue
            assert updated is not None
            indexed[candidate_id] = updated
            normalization_counts.update(normalizations)
            applied_transition_counts[f"{current.get('state')}->{updated.get('state')}"] += 1

    candidates = sorted(indexed.values(), key=lambda item: str(item["candidate_id"]))
    all_sources = sources + transition_sources
    input_state = {
        path.relative_to(root).as_posix(): f"sha256:{sha256(path)}"
        for path in all_sources
    }
    fingerprint = hashlib.sha256(
        json.dumps(input_state, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    output_text = "".join(
        json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for item in candidates
    )
    actionable = [item for item in candidates if item["lifecycle_class"] == "active"]
    manifest = {
        "schema_version": "1.1",
        "generator": "scripts/build_discovery_index.py",
        "parameters": [],
        "baseline_input_fingerprint": f"sha256:{fingerprint}",
        "input_state": input_state,
        "source_counts": dict(sorted(source_counts.items())),
        "candidate_transition_source_counts": dict(sorted(transition_source_counts.items())),
        "applied_candidate_transition_counts": dict(sorted(applied_transition_counts.items())),
        "candidate_counts": {
            "total": len(candidates),
            "by_origin_type": dict(
                sorted(Counter(str(item.get("origin_type") or "<missing>") for item in candidates).items())
            ),
            "by_candidate_type": dict(
                sorted(Counter(str(item.get("candidate_type") or "<missing>") for item in candidates).items())
            ),
            "by_state": dict(
                sorted(Counter(str(item.get("state") or "<missing>") for item in candidates).items())
            ),
            "by_lifecycle_class": dict(sorted(Counter(item["lifecycle_class"] for item in candidates).items())),
        },
        "actionable_candidate_counts": {
            "total": len(actionable),
            "by_origin_type": dict(
                sorted(Counter(str(item.get("origin_type") or "<missing>") for item in actionable).items())
            ),
            "by_candidate_type": dict(
                sorted(Counter(str(item.get("candidate_type") or "<missing>") for item in actionable).items())
            ),
            "by_state": dict(
                sorted(Counter(str(item.get("state") or "<missing>") for item in actionable).items())
            ),
        },
        "legacy_projection_normalizations": dict(sorted(normalization_counts.items())),
        "issues": sorted(set(issues)),
        "output_hashes": {
            CANDIDATE_OUTPUT: "sha256:" + hashlib.sha256(output_text.encode("utf-8")).hexdigest(),
        },
    }
    return candidates, manifest


def main(root: Path = BASE) -> int:
    candidates, manifest = build(root)
    candidate_path = root / CANDIDATE_OUTPUT
    manifest_path = root / MANIFEST_OUTPUT
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(
        "".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in candidates),
        encoding="utf-8",
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["candidate_counts"], ensure_ascii=False))
    return 1 if manifest["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
