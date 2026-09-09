#!/usr/bin/env python3
"""Derive a categorized governance backlog from the current health snapshot."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEALTH = ROOT / "06-runtime" / "state" / "current-health.json"
BACKLOG = ROOT / "06-runtime" / "governance" / "governance-backlog.md"


def load_health() -> dict:
    if not HEALTH.is_file():
        raise SystemExit("current-health.json is missing; run scripts/write_current_health.py")
    return json.loads(HEALTH.read_text(encoding="utf-8"))


def item(identifier: str, issue: str, scope: str, status: str = "open") -> dict:
    return {"id": identifier, "issue": issue, "scope": scope, "status": status}


def coverage_gap(value: object) -> int:
    if not isinstance(value, str) or "/" not in value:
        return 1
    left, right = value.split("/", 1)
    return max(0, int(right) - int(left)) if left.isdigit() and right.isdigit() else 1


def gen_p0(health: dict) -> list[dict]:
    items: list[dict] = []
    for field, files in health.get("required_field_missing", {}).items():
        if files:
            items.append(item(f"P0-FM-{field}", f"required frontmatter field missing: {field}", f"{len(files)} files"))
    for key, files in health.get("verification_semantic_issues", {}).items():
        if files:
            items.append(item(f"P0-VERIFY-{key}", f"verification semantic conflict: {key}", f"{len(files)} files"))
    conflicts = health.get("verification_state_conflicts", [])
    if conflicts:
        items.append(item("P0-VERIFY-STATE", "verification state conflicts", f"{len(conflicts)} files"))
    drift = health.get("rule_drift", {}).get("findings", 0)
    if drift < 0:
        detail = health.get("rule_drift", {}).get("error", "rule-drift audit unavailable")
        items.append(item("P0-RULE-AUDIT", "rule-drift audit could not run", str(detail)))
    elif drift > 0:
        items.append(item("P0-RULE-DRIFT", "active rules differ from repository facts", f"{drift} findings"))
    architecture = health.get("architecture_drift", {})
    if architecture.get("deprecated_type_drift", 0):
        items.append(item("P0-ARCH-TYPE", "deprecated type directories contain files", str(architecture["deprecated_type_drift"])))
    if architecture.get("hierarchy_has_old_type_refs") or architecture.get("hierarchy_has_old_statistics"):
        items.append(item("P0-ARCH-HIERARCHY", "hierarchy contains retired paths or statistics", "hierarchy/index.md"))
    node_type_issues = health.get("structure_node_type_issues", [])
    if node_type_issues:
        items.append(item("P0-ARCH-NODE-TYPE", "structure node directory and node_type differ", f"{len(node_type_issues)} files"))
    hierarchy_issues = health.get("hierarchy_structure_issues", [])
    if hierarchy_issues:
        items.append(item("P0-ARCH-HIERARCHY-CONTRACT", "five-level hierarchy structure contract differs from materialized nodes", f"{len(hierarchy_issues)} findings"))
    return items


def gen_p1(health: dict) -> list[dict]:
    items: list[dict] = []
    for type_name, type_data in health.get("translation_health", {}).items():
        for field, coverage in type_data.get("coverage", {}).items():
            gap = coverage_gap(coverage)
            if gap:
                items.append(item(
                    f"P1-TRANSLATION-{type_name.upper()}-{field.upper()}",
                    f"translation field coverage incomplete: {type_name}.{field}",
                    f"{gap} missing",
                ))
    translation = health.get("translation_index_integrity", {})
    if (
        not translation.get("index_exists", False)
        or translation.get("missing")
        or translation.get("stale")
        or translation.get("duplicate")
        or translation.get("declared_total_mismatch", False)
    ):
        items.append(item(
            "P1-TRANSLATION-INDEX-DRIFT",
            "translation index differs from eligible knowledge units",
            f"expected={translation.get('expected', 0)}, indexed={translation.get('indexed', 0)}",
        ))
    verification = health.get("verification_schema", {})
    missing_status = verification.get("missing_evidence_status", {}).get("count", 0)
    missing_level = verification.get("missing_verification_level_when_not_tentative", {}).get("count", 0)
    if missing_status:
        items.append(item("P1-EVIDENCE-STATUS", "evidence_status missing", f"{missing_status} files"))
    if missing_level:
        items.append(item("P1-VERIFY-LEVEL", "verification_level missing", f"{missing_level} files"))
    dataflow = health.get("dataflow_issues", [])
    if dataflow:
        items.append(item("P1-DATAFLOW", "source-to-processing dataflow is incomplete", f"{len(dataflow)} findings"))
    evidence_ref = health.get("evidence_ref", {})
    if evidence_ref.get("evidence_ref_broken", 0):
        items.append(item("P1-EVIDENCE-REF", "evidence references are broken", str(evidence_ref["evidence_ref_broken"])))
    source_hash = health.get("source_hash", {})
    if source_hash.get("source_hash_drift", 0) or source_hash.get("reopened_packages"):
        items.append(item(
            "P0-SOURCE-DRIFT",
            "source fingerprint drift reopened ingest state",
            f"drift={source_hash.get('source_hash_drift', 0)}, reopened={len(source_hash.get('reopened_packages', []))}",
        ))
    if source_hash.get("source_hash_missing", 0):
        items.append(item("P1-SOURCE-HASH", "source hash missing", str(source_hash["source_hash_missing"])))
    return items


def gen_p1_content(health: dict) -> list[dict]:
    content = health.get("content_quality", {})
    mapping = {
        "missing_sections": ("P1-CONTENT-SECTIONS", "required content sections missing"),
        "body_verify_vs_fm": ("P1-CONTENT-VERIFY", "body and frontmatter verification state differ"),
        "fm_body_verify_conflict": ("P1-CONTENT-CONFLICT", "frontmatter and body verification conflict"),
        "local_file_broken": ("P1-CONTENT-LINK", "local file reference broken"),
    }
    return [item(identifier, issue, f"{content.get(field, 0)} files") for field, (identifier, issue) in mapping.items() if content.get(field, 0)]


def gen_p1_ingest_coverage(health: dict) -> list[dict]:
    items: list[dict] = []
    semantic = health.get("semantic_artifact_integrity", {})
    for field in (
        "chapters_without_reading_ledger",
        "chapters_without_continuity_map",
        "chapters_without_semantic_stitch_log",
        "chapters_without_source_structure_map",
        "chapters_without_extraction_coverage_matrix",
    ):
        if semantic.get(field):
            items.append(item(f"P1-INGEST-{field.upper()}", field.replace("_", " "), f"{len(semantic[field])} packages"))
    recall = health.get("recall_quality", {})
    for field in ("chapters_without_candidate", "chapters_without_decision", "chapters_without_recall", "semantic_maps_with_unresolved"):
        if recall.get(field):
            items.append(item(f"P1-RECALL-{field.upper()}", field.replace("_", " "), f"{len(recall[field])} packages"))
    if recall.get("manifests_scaffolded", 0):
        items.append(item("P1-INGEST-SCAFFOLDED", "processing manifests remain scaffolded", str(recall["manifests_scaffolded"])))
    return items


def gen_p2_content(health: dict) -> list[dict]:
    content = health.get("content_quality", {})
    mapping = {
        "placeholder_content": ("P2-CONTENT-PLACEHOLDER", "placeholder content remains"),
        "title_format_issues": ("P2-CONTENT-TITLE", "title format issue"),
        "duplicate_titles": ("P2-CONTENT-DUP", "duplicate title"),
        "cross_type_same_name": ("P2-CONTENT-CROSS", "cross-type same-name object needs disambiguation"),
        "text_corruption": ("P2-CONTENT-CORRUPT", "suspected text corruption"),
    }
    return [item(identifier, issue, f"{content.get(field, 0)} findings") for field, (identifier, issue) in mapping.items() if content.get(field, 0)]


def gen_p2_runtime(health: dict) -> list[dict]:
    retention = health.get("runtime_artifact_retention", {})
    items: list[dict] = []
    review_required = retention.get("review_required", 0)
    if review_required:
        items.append(item(
            "P2-RUNTIME-R2-PROVENANCE",
            "possible R2 projections lack valid provenance manifests",
            f"{review_required} files retained as R1",
        ))
    ephemeral = retention.get("ephemeral_residue", 0)
    if ephemeral:
        items.append(item(
            "P2-RUNTIME-EPHEMERAL",
            "ephemeral runtime residue remains",
            f"{ephemeral} files",
        ))
    return items


def gen_research_debt(health: dict) -> list[dict]:
    debt = health.get("knowledge_maturity", {}).get("research_debt", {})
    labels = {
        "single_source_units": "knowledge units supported by one source",
        "tentative_units": "knowledge units with tentative consensus",
        "low_confidence_units": "knowledge units with low confidence",
        "candidates_needing_evidence": "candidates needing evidence",
        "units_missing_hierarchy_assignment": "knowledge units missing complete hierarchy assignment",
    }
    return [item(f"RD-{key.upper()}", labels[key], str(value), "research_debt") for key, value in debt.items() if value]


def gen_candidate_opportunities(health: dict) -> list[dict]:
    maturity = health.get("knowledge_maturity", {})
    items: list[dict] = []
    isolated = maturity.get("isolated_units", {}).get("count", 0)
    if isolated:
        items.append(item("OPP-ISOLATED", "isolated units may warrant relation review", str(isolated), "candidate_opportunity"))
    candidate_debt = maturity.get("candidate_debt", {})
    if candidate_debt.get("total", 0):
        items.append(item("OPP-CANDIDATES", "active discovery candidates", str(candidate_debt["total"]), "candidate_opportunity"))
    return items


def snapshot_datetime(health: dict) -> datetime:
    try:
        return datetime.fromisoformat(str(health["timestamp"]))
    except (KeyError, TypeError, ValueError):
        return datetime.now()


def gen_completed(health: dict, *, as_of: datetime | None = None) -> list[dict]:
    completed_on = (as_of or snapshot_datetime(health)).strftime("%Y-%m-%d")
    items: list[dict] = []
    if not any(health.get("required_field_missing", {}).values()):
        items.append({"id": "C-FM", "issue": "required frontmatter coverage complete", "date": completed_on})
    if not health.get("verification_state_conflicts", []):
        items.append({"id": "C-VERIFY", "issue": "verification state conflicts absent", "date": completed_on})
    if health.get("summary", {}).get("deprecated_type_drift", 0) == 0:
        items.append({"id": "C-SCHEMA", "issue": "deprecated type drift absent", "date": completed_on})
    if health.get("content_quality", {}).get("total_findings", 0) == 0:
        items.append({"id": "C-CONTENT", "issue": "mechanical content findings absent", "date": completed_on})
    return items


def render_section(title: str, items: list[dict]) -> list[str]:
    lines = [f"## {title}", ""]
    if not items:
        return [*lines, "No active items.", ""]
    lines.extend(["| ID | Issue | Scope | Status |", "|---|---|---|---|"])
    for entry in items:
        lines.append(f"| {entry['id']} | {entry['issue']} | {entry.get('scope', '-')} | {entry.get('status', 'open')} |")
    lines.append("")
    return lines


def generate_md(health: dict) -> str:
    generated_at = snapshot_datetime(health)
    structural = health.get("structural_health", {})
    maturity = health.get("knowledge_maturity", {})
    lines = [
        "# Governance Backlog",
        "",
        "> Derived status signal; it is not a semantic decision or proof of publication readiness.",
        f"> Snapshot: {generated_at.strftime('%Y-%m-%d %H:%M')}",
        f"> Structural health: {structural.get('total', '?')}/{structural.get('max_score', 130)}",
        f"> Knowledge units: {health.get('summary', {}).get('total_units', '?')}",
        f"> Maturity metrics: {maturity.get('metric_kind', 'missing')}",
        "",
    ]
    lines.extend(render_section("System defects - P0", gen_p0(health)))
    lines.extend(render_section("System defects - P1", gen_p1(health) + gen_p1_content(health) + gen_p1_ingest_coverage(health)))
    lines.extend(render_section("System defects - P2", gen_p2_content(health) + gen_p2_runtime(health)))
    lines.extend(render_section("Research debt (not a system defect)", gen_research_debt(health)))
    lines.extend(render_section("Candidate opportunities (not accepted knowledge)", gen_candidate_opportunities(health)))
    completed = [item(entry["id"], entry["issue"], entry["date"], "completed") for entry in gen_completed(health, as_of=generated_at)]
    lines.extend(render_section("Completed mechanical signals", completed))
    return "\n".join(lines)


def main() -> None:
    health = load_health()
    BACKLOG.parent.mkdir(parents=True, exist_ok=True)
    BACKLOG.write_text(generate_md(health), encoding="utf-8")
    print(f"wrote={BACKLOG}")
    print(f"system_p0={len(gen_p0(health))}")
    print(f"system_p1={len(gen_p1(health) + gen_p1_content(health) + gen_p1_ingest_coverage(health))}")
    print(f"system_p2={len(gen_p2_content(health) + gen_p2_runtime(health))}")
    print(f"research_debt={len(gen_research_debt(health))}")
    print(f"candidate_opportunities={len(gen_candidate_opportunities(health))}")


if __name__ == "__main__":
    main()
