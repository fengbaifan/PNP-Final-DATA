#!/usr/bin/env python3
"""
build_relation_index.py v2.1 — 语义关系全量索引
================================================
v2.0 变更:
- 读取 relations 字段（主要来源），related（legacy fallback）
- 读取 hierarchy.role_in_theme 与 topic_memberships
- 读取 claim-registry.yml
- 全量输出（不再截断 500 条）
- 双向关系自动补全
- 标注 relation_source / review_status / confidence
"""
import re, json, sys, yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    from scripts._relation_schema import INVERSE_MAP, RELATION_TYPES
except ModuleNotFoundError:
    from _relation_schema import INVERSE_MAP, RELATION_TYPES

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
STRUCTURE = BASE / "04-knowledge" / "structure"
QUALITY = BASE / "04-knowledge" / "quality"
OUTPUT = QUALITY / "relation-index.yml"
CLAIM_YML = QUALITY / "claim-registry.yml"
TODAY = datetime.now().strftime("%Y-%m-%d")
DRY = "--dry-run" in sys.argv
VERBOSE = "--verbose" in sys.argv

def get_fm(text):
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""

def get_field(fm, field):
    m = re.search(rf"^{re.escape(field)}:\s*(.+)", fm, re.MULTILINE)
    return m.group(1).strip() if m else ""

_CLAIM_IDS = None

def _claim_ids():
    global _CLAIM_IDS
    if _CLAIM_IDS is not None:
        return _CLAIM_IDS
    ids = set()
    if CLAIM_YML.exists():
        data = yaml.safe_load(CLAIM_YML.read_text(encoding="utf-8")) or []
        if isinstance(data, dict):
            items = data.items()
        elif isinstance(data, list):
            items = ((item.get("claim_id"), item) for item in data if isinstance(item, dict))
        else:
            items = []
        for claim_id, claim_data in items:
            if claim_id:
                ids.add(str(claim_id))
            if isinstance(claim_data, dict) and claim_data.get("claim_id"):
                ids.add(str(claim_data["claim_id"]))
    _CLAIM_IDS = ids
    return _CLAIM_IDS

def _normalize_claim_target(target):
    if not target.startswith("claim/"):
        return target
    slug = target.split("claim/", 1)[1]
    if slug.endswith(".md"):
        slug = slug[:-3]
    candidates = [slug]
    if not slug.startswith("claim_"):
        candidates.append(f"claim_{slug}")
    for claim_id in candidates:
        if claim_id in _claim_ids():
            return f"claim/{claim_id}"
    return target

def _normalize_target_path(target, source=None):
    if not target:
        return ""
    normalized = target.replace("\\", "/").strip()
    if normalized.startswith("04-knowledge/units/"):
        normalized = normalized.split("04-knowledge/units/", 1)[1]
    elif normalized.startswith("units/"):
        normalized = normalized.split("units/", 1)[1]
    while normalized.startswith("../"):
        normalized = normalized[3:]
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if source and "/" not in normalized and normalized.endswith(".md") and "/" in source:
        normalized = f"{source.rsplit('/', 1)[0]}/{normalized}"
    normalized = _normalize_claim_target(normalized)
    return normalized

def iter_all_units():
    for dname in ["persons","institutions","places","works","publications","terms","procedures","events"]:
        d = UNITS / dname
        if d.exists():
            for f in sorted(d.glob("*.md")):
                yield f, dname

relations = []
path_to_type = {}
all_paths = set()

def _target_type_from_path(target):
    target = _normalize_target_path(target)
    for d in ["persons","institutions","places","works","publications","terms","procedures","events","topics","themes","domains","dimensions","claim"]:
        if f"/{d}/" in target or target.startswith(f"{d}/"):
            return d.rstrip("s")
    return "unknown"

def _infer_type(target):
    target = _normalize_target_path(target)
    for d in ["persons","institutions","places","works","publications","terms","procedures","events"]:
        if f"/{d}/" in target or target.startswith(f"{d}/"):
            return {
                "persons": "involves_person","institutions": "associated_institution",
                "places": "located_at","works": "relates_to_work",
                "publications": "cited_by","terms": "relates_to_term",
                "procedures": "uses_procedure","events": "relates_to_event",
            }.get(d, "related_to")
    return "related_to"

def _has_relation(source, target, existing):
    return any(r["source"] == source and r["target"] == target for r in existing)

def _weak_association_targets(frontmatter, source):
    """Return normalized targets that must not re-enter the formal relation graph."""
    return {
        _normalize_target_path(item["target"], source)
        for item in (frontmatter.get("weak_associations") or [])
        if isinstance(item, dict) and item.get("target")
    }

def _materialized_structure_target(value):
    """Return a real structure-node target from an explicit materialized path."""
    normalized = value.replace("\\", "/").strip().strip('"').strip("'")
    if normalized.startswith("structure/"):
        normalized = normalized.split("structure/", 1)[1]
    allowed = ("topics/", "themes/", "domains/", "dimensions/")
    if not normalized.startswith(allowed) or not normalized.endswith(".md"):
        return ""
    return normalized if (STRUCTURE / normalized).is_file() else ""


def _materialized_theme_target(theme_code):
    """Resolve a Theme code through frontmatter; never fabricate a filename."""
    code = str(theme_code or "").strip().strip('"').strip("'")
    if not code:
        return ""
    for path in sorted((STRUCTURE / "themes").glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        try:
            data = yaml.safe_load(get_fm(path.read_text(encoding="utf-8"))) or {}
        except yaml.YAMLError:
            continue
        if str(data.get("theme_code") or "").strip() == code:
            return f"themes/{path.name}"
    return ""

def _finalize(source, stype, rel, src):
    target = _normalize_target_path(rel.get("target", ""), source)
    has_evidence = bool(rel.get("evidence") or rel.get("evidence_ref") or rel.get("claim_id"))
    bidirectional_required = rel.get("bidirectional_required")
    if bidirectional_required is None:
        bidirectional_required = rel.get("relation_type") in INVERSE_MAP
    return {
        "source": source, "source_type": stype,
        "target": target,
        "target_type": _target_type_from_path(target),
        "relation_type": rel.get("relation_type", "related_to"),
        "inverse_relation_type": rel.get("inverse_relation_type"),
        "note": rel.get("note", ""),
        "evidence": rel.get("evidence", ""),
        "evidence_ref": rel.get("evidence_ref"),
        "claim_id": rel.get("claim_id"),
        "confidence": rel.get("confidence", "medium"),
        "relation_source": rel.get("relation_source", src),
        "bidirectional_required": bidirectional_required,
        "review_status": rel.get("review_status") or ("auto_validated" if has_evidence else "needs_evidence"),
    }

def _inverse_review_status(rel):
    status = rel.get("review_status")
    has_evidence = bool(rel.get("evidence") or rel.get("evidence_ref") or rel.get("claim_id"))
    if status == "conflict":
        return "conflict"
    if status in {"auto_validated", "evidence_backed_relation"} and has_evidence:
        return "auto_validated"
    if status == "needs_evidence":
        return "needs_evidence"
    return "weak_inference"

def _build_inverse_relation(rel):
    return {
        "source": rel["target"], "source_type": rel.get("target_type", "unknown"),
        "target": rel["source"], "target_type": rel["source_type"],
        "relation_type": INVERSE_MAP[rel["relation_type"]],
        "inverse_relation_type": rel["relation_type"],
        "note": f"auto-inverse of {rel['relation_type']}",
        "evidence": rel.get("evidence", ""),
        "evidence_ref": rel.get("evidence_ref"),
        "claim_id": rel.get("claim_id"),
        "confidence": rel.get("confidence", "medium"),
        "relation_source": "inferred_by_rule",
        "bidirectional_required": True,
        "review_status": _inverse_review_status(rel),
    }

def _should_build_inverse(rel):
    if rel.get("review_status") in {"weak_association", "defer_source_review"}:
        return False
    return rel.get("bidirectional_required") is not False and rel.get("relation_type") in INVERSE_MAP

# ── Scan all units ──
for f, dname in iter_all_units():
    rel = str(f.relative_to(UNITS)).replace("\\", "/")
    path_to_type[rel] = dname.rstrip("s")
    all_paths.add(rel)

for f, dname in iter_all_units():
    c = f.read_text(encoding="utf-8")
    fm = get_fm(c)
    parts = c.split("---", 2)
    if not fm:
        continue
    source_rel = str(f.relative_to(UNITS)).replace("\\", "/")
    source_type = dname.rstrip("s")

    # ── Source 1: relations field ──
    try:
        fm_data = yaml.safe_load(fm) or {}
    except Exception:
        fm_data = {}
    weak_targets = _weak_association_targets(fm_data, source_rel)
    for rel_item in fm_data.get("relations", []) or []:
        if isinstance(rel_item, dict) and rel_item.get("target"):
            relations.append(_finalize(source_rel, source_type, rel_item, "explicit"))

    # ── Source 2: five-level hierarchy memberships ──
    allowed_hierarchy_roles = {
        "term_anchor", "representative_work", "key_person", "key_institution",
        "geographical_context", "source_publication", "procedure", "evidence_event",
        "historical_context", "counterexample", "boundary_case", "supporting_source",
        "contested_claim",
    }
    role = str(fm_data.get("role_in_theme") or "").strip()
    theme_target = _materialized_theme_target(fm_data.get("primary_theme"))
    if theme_target and role in allowed_hierarchy_roles:
        relations.append({
            "source": source_rel, "source_type": source_type,
            "target": f"structure/{theme_target}", "target_type": "theme",
            "relation_type": "member_of",
            "note": f"hierarchy Theme role: {role}",
            "evidence": f"hierarchy.role_in_theme: {role}",
            "confidence": "high",
            "relation_source": "inferred_by_rule",
            "bidirectional_required": False,
            "review_status": "auto_validated",
        })

    for membership in fm_data.get("topic_memberships", []) or []:
        if not isinstance(membership, dict):
            continue
        topic_target = _materialized_structure_target(str(membership.get("topic") or ""))
        topic_role = str(membership.get("role") or "").strip()
        if topic_target and topic_target.startswith("topics/") and topic_role in allowed_hierarchy_roles:
            relations.append({
                "source": source_rel, "source_type": source_type,
                "target": f"structure/{topic_target}", "target_type": "topic",
                "relation_type": "member_of",
                "note": f"hierarchy Topic role: {topic_role}",
                "evidence": f"hierarchy.topic_memberships.role: {topic_role}",
                "confidence": "high",
                "relation_source": "inferred_by_rule",
                "bidirectional_required": False,
                "review_status": "auto_validated",
            })

    # ── Source 3: legacy related ──
    in_rel = False
    for line in fm.split("\n"):
        if re.match(r"^related:", line):
            in_rel = True
            continue
        if in_rel:
            m = re.match(r"^\s*-\s+(.*)", line)
            if m:
                target = _normalize_target_path(m.group(1).strip(), source_rel)
                rel_type = _infer_type(target)
                if target not in weak_targets and not _has_relation(source_rel, target, relations):
                    relations.append({
                        "source": source_rel, "source_type": source_type,
                        "target": target, "target_type": _target_type_from_path(target),
                        "relation_type": rel_type,
                        "note": "legacy related",
                        "confidence": "low",
                        "relation_source": "migrated_from_related",
                        "bidirectional_required": False,
                        "review_status": "needs_evidence",
                    })
            elif line.strip() and not line.strip().startswith("-"):
                break

    # ── Source 4: body markdown links (strong signal) ──
    body = parts[2] if len(c.split("---", 2)) >= 3 else ""
    body_links = re.findall(r"\[([^\]]*)\]\(\.\./([^)]+)\)", body)
    for link_text, link_path in body_links:
        link_norm = link_path.replace("\\", "/").split("/", 2)
        if len(link_norm) >= 3:
            link_norm = _normalize_target_path("/".join(link_norm[-2:]))
            if (
                link_norm in all_paths
                and link_norm not in weak_targets
                and not _has_relation(source_rel, link_norm, relations)
            ):
                rel_type = _infer_type(link_norm)
                relations.append({
                    "source": source_rel, "source_type": source_type,
                    "target": link_norm, "target_type": _target_type_from_path(link_norm),
                    "relation_type": rel_type,
                    "note": f"body link: {link_text}",
                    "confidence": "medium",
                    "relation_source": "inferred_by_rule",
                    "bidirectional_required": False,
                    "review_status": "weak_inference",
                })

# ── Source 5: claim-registry cross-references ──
if CLAIM_YML.exists():
    claims = yaml.safe_load(CLAIM_YML.read_text(encoding="utf-8")) or {}
    if isinstance(claims, dict):
        claim_iter = claims.items()
    elif isinstance(claims, list):
        claim_iter = ((c.get("claim_id"), c) for c in claims if isinstance(c, dict))
    else:
        claim_iter = []
    for claim_id, claim_data in claim_iter:
        if isinstance(claim_data, dict) and claim_id:
            for ku_path in claim_data.get("supported_by", []):
                rel_ku = ku_path.replace("\\", "/")
                if "units/" in rel_ku:
                    rel_ku = rel_ku.split("units/", 1)[1]
                if rel_ku in all_paths:
                    claim_target = f"claim/{claim_id}"
                    evidence = f"claim-registry.supported_by: {claim_id} -> {rel_ku}"
                    relations.append({
                        "source": rel_ku, "source_type": _target_type_from_path(rel_ku),
                        "target": claim_target,
                        "target_type": "claim",
                        "relation_type": "supports_claim",
                        "note": "from claim-registry",
                        "evidence": evidence,
                        "evidence_ref": claim_data.get("source"),
                        "confidence": "high",
                        "relation_source": "explicit",
                        "bidirectional_required": False,
                        "review_status": "auto_validated",
                    })
                    relations.append({
                        "source": claim_target, "source_type": "claim",
                        "target": rel_ku,
                        "target_type": _target_type_from_path(rel_ku),
                        "relation_type": "supported_by",
                        "note": "from claim-registry.supported_by",
                        "evidence": evidence,
                        "evidence_ref": claim_data.get("source"),
                        "confidence": "high",
                        "relation_source": "explicit",
                        "bidirectional_required": False,
                        "review_status": "auto_validated",
                    })

# ── Bidirectional completion ──
bidir_add = []
for rel in relations:
    if _should_build_inverse(rel):
        inv = INVERSE_MAP.get(rel["relation_type"])
        existing_inv = any(
            r["source"] == rel["target"] and r["target"] == rel["source"] and r["relation_type"] == inv
            for r in relations
        )
        if not existing_inv:
            bidir_add.append(_build_inverse_relation(rel))

relations.extend(bidir_add)

# ── Output ──
total = len(relations)
sources = defaultdict(int)
for rel in relations:
    sources[rel.get("relation_source", "unknown")] += 1

types = defaultdict(int)
for rel in relations:
    types[rel.get("relation_type", "unknown")] += 1

print(f"build_relation_index.py v2.1")
print(f"  关系总数: {total}")
print(f"  来源: explicit={sources.get('explicit',0)} inferred_by_rule={sources.get('inferred_by_rule',0)} migrated_from_related={sources.get('migrated_from_related',0)}")
print(f"  双向补全: {len(bidir_add)}")
print(f"  类型覆盖: {len(types)}/{len(RELATION_TYPES)}")


def render_relation_index(generated: str) -> str:
    header = f"# Relation Index v2.1\n# generated: {generated}\n# total: {total}\n# sources: {dict(sources)}\n\n"
    return header + yaml.dump(relations, allow_unicode=True, sort_keys=False, width=300)


def stable_generated_date(candidate: str, output: Path = OUTPUT) -> str:
    """Preserve the prior date when only the generated header date differs."""
    if not output.exists():
        return TODAY
    existing = output.read_text(encoding="utf-8")
    match = re.search(r"^# generated: (\d{4}-\d{2}-\d{2})$", existing, re.MULTILINE)
    if not match:
        return TODAY
    normalized_existing = re.sub(
        r"^# generated: \d{4}-\d{2}-\d{2}$",
        "# generated: <stable>",
        existing,
        count=1,
        flags=re.MULTILINE,
    )
    normalized_candidate = re.sub(
        r"^# generated: \d{4}-\d{2}-\d{2}$",
        "# generated: <stable>",
        candidate,
        count=1,
        flags=re.MULTILINE,
    )
    return match.group(1) if normalized_existing == normalized_candidate else TODAY


if not DRY:
    candidate = render_relation_index(TODAY)
    yaml_text = render_relation_index(stable_generated_date(candidate))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(yaml_text, encoding="utf-8")
    print(f"  written: {OUTPUT}")
else:
    print(f"  [DRY RUN]")
