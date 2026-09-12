#!/usr/bin/env python3
"""
audit_relation_consistency.py — 关系一致性审计
==============================================
检查: broken target / invalid relation_type / missing inverse / weak / isolated / over-connected
"""
import re, json, sys, yaml
from pathlib import Path
from collections import defaultdict

try:
    from scripts._relation_schema import INVERSE_MAP, LEGACY_GENERIC_RELATION_TYPES, VALID_RELATION_TYPES
    from scripts._accepted_knowledge import select_paths
except ModuleNotFoundError:
    from _relation_schema import INVERSE_MAP, LEGACY_GENERIC_RELATION_TYPES, VALID_RELATION_TYPES
    from _accepted_knowledge import select_paths

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
IDX = BASE / "04-knowledge" / "quality" / "relation-index.yml"
GENERIC_EXPLICIT_BASELINE = BASE / "06-runtime" / "governance" / "relation-generic-explicit-baseline.jsonl"
DRY = "--dry-run" in sys.argv

if not IDX.exists():
    print("relation-index.yml 不存在，请先运行 build_relation_index.py")
    sys.exit(1)

data = yaml.safe_load(IDX.read_text(encoding="utf-8"))
relations = [r for r in data if isinstance(r, dict)]

VALID_TYPES = VALID_RELATION_TYPES
GENERIC_RELATION_TYPES = LEGACY_GENERIC_RELATION_TYPES

BLOCKING_ISSUE_KEYS = (
    "broken_target",
    "invalid_relation_type",
    "missing_inverse",
    "weak_evidence",
    "unbaselined_generic_evidence_backed",
)


def relation_identity(relation):
    return (
        relation.get("source", ""),
        relation.get("target", ""),
        relation.get("relation_type", ""),
    )


def find_unbaselined_generic_evidence_backed(relations, baseline_relations):
    baseline_keys = {relation_identity(relation) for relation in baseline_relations}
    return [
        relation
        for relation in relations
        if relation.get("relation_type") in GENERIC_RELATION_TYPES
        and relation.get("relation_source") == "explicit"
        and relation.get("review_status") == "evidence_backed_relation"
        and relation_identity(relation) not in baseline_keys
    ]


def blocking_issue_count(issues):
    """Return relation-integrity findings that must fail the closeout gate."""
    return sum(len(issues.get(key, [])) for key in BLOCKING_ISSUE_KEYS)


def requires_inverse(relation):
    return (
        relation.get("relation_type") in INVERSE_MAP
        and relation.get("review_status") not in {"weak_association", "defer_source_review"}
        and relation.get("bidirectional_required") is not False
    )


def has_direct_relation_evidence(relation):
    """The relation contract accepts evidence text, evidence_ref, or claim_id."""
    return bool(
        relation.get("evidence")
        or relation.get("evidence_ref")
        or relation.get("claim_id")
    )


def load_jsonl(path):
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

unit_files = []
for dname in ["persons","families","institutions","places","works","archives","terms","procedures","events"]:
    d = UNITS / dname
    if d.exists():
        unit_files.extend(d.rglob("*.md"))
all_units = {
    str(f.relative_to(UNITS)).replace("\\", "/")
    for f in select_paths(BASE, "units", sorted(unit_files))
}

def normalize_unit_ref(ref, source=""):
    """Resolve KU-relative targets such as ../works/foo.md to units-root paths."""
    if not ref:
        return ref
    if ref in all_units or ref.startswith("claim/") or "structure/" in ref:
        return ref
    if ref.startswith("../") and not source:
        stripped = ref
        while stripped.startswith("../"):
            stripped = stripped[3:]
        if stripped in all_units:
            return stripped
    if ref.startswith("../") and source:
        base = UNITS / source
        try:
            resolved = (base.parent / ref).resolve()
            rel = resolved.relative_to(UNITS.resolve())
            return str(rel).replace("\\", "/")
        except ValueError:
            return ref
    if "/" not in ref and ref.endswith(".md") and source:
        base = UNITS / source
        try:
            resolved = (base.parent / ref).resolve()
            rel = resolved.relative_to(UNITS.resolve())
            return str(rel).replace("\\", "/")
        except ValueError:
            return ref
    return ref

normalized_relations = []
for rel in relations:
    source = normalize_unit_ref(rel.get("source", ""))
    target = normalize_unit_ref(rel.get("target", ""), rel.get("source", ""))
    normalized_relations.append((source, target, rel))
relation_keys = {
    (source, target, rel.get("relation_type", ""))
    for source, target, rel in normalized_relations
}

issues = {
    "broken_target": [],
    "invalid_relation_type": [],
    "missing_inverse": [],
    "weak_evidence": [],
    "unbaselined_generic_evidence_backed": find_unbaselined_generic_evidence_backed(
        relations,
        load_jsonl(GENERIC_EXPLICIT_BASELINE),
    ),
}
unit_degrees = defaultdict(int)

for source, target, rel in normalized_relations:
    rtype = rel.get("relation_type","")
    unit_degrees[source] += 1
    unit_degrees[target] += 1

    if target not in all_units and not target.startswith("claim/") and not "structure/" in target:
        issues["broken_target"].append({
            "source": source,
            "target": rel.get("target",""),
            "normalized_target": target,
            "relation_type": rtype,
        })

    if rtype not in VALID_TYPES:
        issues["invalid_relation_type"].append({"source":source,"relation_type":rtype})

    if rel.get("confidence") in ("low","medium") and not has_direct_relation_evidence(rel):
        if rtype not in ("related_to","involves_person","relates_to_term","relates_to_work"):
            issues["weak_evidence"].append({"source":source,"target":target,"relation_type":rtype})

    inv = INVERSE_MAP.get(rtype)
    if requires_inverse(rel):
        has_inv = (target, source, inv) in relation_keys
        if not has_inv:
            issues["missing_inverse"].append({"source":source,"target":target,"relation_type":rtype,"expected_inverse":inv})

def collect_isolated_units(units, degrees):
    return [unit for unit in units if degrees.get(unit, 0) == 0]


isolated_all = collect_isolated_units(all_units, unit_degrees)
isolated_preview = isolated_all[:100]
over_connected = sorted([(u,d) for u,d in unit_degrees.items() if d > 50], key=lambda x:-x[1])[:10]

print(f"audit_relation_consistency.py")
print(f"  broken target: {len(issues['broken_target'])}")
print(f"  invalid relation_type: {len(issues['invalid_relation_type'])}")
print(f"  missing inverse: {len(issues['missing_inverse'])}")
print(f"  weak evidence: {len(issues['weak_evidence'])}")
print(f"  unbaselined generic evidence-backed: {len(issues['unbaselined_generic_evidence_backed'])}")
print(f"  isolated units (0 relations): {len(isolated_all)}")
print(f"  isolated preview rows: {len(isolated_preview)}")
print(f"  over-connected (>50): {len(over_connected)}")

if __name__ == "__main__" and blocking_issue_count(issues):
    sys.exit(1)
