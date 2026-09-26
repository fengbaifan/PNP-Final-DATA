#!/usr/bin/env python3
"""
Codex-only repository audit — v2.0
===================================
Features:
- Frontmatter-only field checking (YAML frontmatter isolation)
- Verification semantic checks (L7, confidence, consensus rules)
- Rule authority conflict detection
- Sub-scored health report
- Evidence chain traceability checks

Read-only. Never modifies knowledge units.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import yaml
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path

try:
    from scripts._relation_schema import RELATION_TYPES
    from scripts._accepted_knowledge import select_paths, select_claims, load_catalog
except ModuleNotFoundError:
    from _relation_schema import RELATION_TYPES
    from _accepted_knowledge import select_paths, select_claims, load_catalog

RELATION_TYPE_TOTAL = len(RELATION_TYPES)


BASE_UNIT_TYPES = [
    "persons",
    "families",
    "institutions",
    "places",
    "works",
    "archives",
    "terms",
    "procedures",
    "events",
]

# Deprecated directories (for backward-compatibility detection only)
DEPRECATED_DIRS = ["concepts", "techniques", "cases", "ideas"]

TYPE_DIR_MAP = {
    "persons": "person",
    "families": "family",
    "institutions": "institution",
    "places": "place",
    "works": "work",
    "archives": "archive",
    "terms": "term",
    "procedures": "procedure",
    "events": "event",
    # deprecated (for detection only)
    "concepts": "[DEPRECATED] concept",
    "techniques": "[DEPRECATED] technique",
    "cases": "[DEPRECATED] case",
    "ideas": "[DEPRECATED] idea",
}

STRUCTURE_DIRS = ["domains", "dimensions", "themes", "topics"]

REQUIRED_FIELDS = [
    "title",
    "type",
    "sources",
    "created",
    "updated",
]

RECOMMENDED_FIELDS = ["sub_type", "tags", "evidence_status"]

VALID_CONSENSUS = ["confirmed", "disputed", "tentative"]
VALID_CONFIDENCE = ["low", "medium", "high"]

FRONTMATTER_RE = re.compile(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


@lru_cache(maxsize=None)
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def split_frontmatter_body(text: str) -> tuple[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return "", text
    return match.group(1), text[match.end():]


@lru_cache(maxsize=None)
def extract_frontmatter(text: str) -> str:
    fm, _ = split_frontmatter_body(text)
    return fm.strip("\n")


@lru_cache(maxsize=None)
def has_frontmatter_field(text: str, field: str) -> bool:
    fm = extract_frontmatter(text)
    if not fm:
        return False
    return re.search(rf"^{re.escape(field)}\s*:", fm, re.MULTILINE) is not None


@lru_cache(maxsize=None)
def scalar_frontmatter_field(text: str, field: str) -> str:
    fm = extract_frontmatter(text)
    if not fm:
        return ""
    match = re.search(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip().strip('"').strip("'")


@lru_cache(maxsize=None)
def list_frontmatter_field(text: str, field: str) -> tuple[str, ...]:
    fm = extract_frontmatter(text)
    if not fm:
        return ()
    match = re.search(rf"^{re.escape(field)}\s*:\s*\[(.*?)\]", fm, re.MULTILINE)
    if not match:
        return ()
    raw = match.group(1)
    items = re.findall(r'"([^"]*)"', raw)
    if not items:
        items = re.findall(r"'([^']*)'", raw)
    return tuple(items)


@dataclass(frozen=True)
class UnitSnapshot:
    path: Path
    relative_path: str
    type_name: str
    text: str
    frontmatter: str
    body: str


def load_unit_snapshots(base: Path) -> list[UnitSnapshot]:
    snapshots: list[UnitSnapshot] = []
    for path in iter_unit_files(base):
        text = read_text(path)
        frontmatter, body = split_frontmatter_body(text)
        snapshots.append(UnitSnapshot(
            path=path,
            relative_path=path.relative_to(base).as_posix(),
            type_name=path.parent.name,
            text=text,
            frontmatter=frontmatter,
            body=body,
        ))
    return snapshots


def body_only_required_fields_check(text: str) -> list[str]:
    fm, body = split_frontmatter_body(text)
    result = []
    for field in REQUIRED_FIELDS:
        in_fm = has_frontmatter_field(text, field)
        in_body = re.search(rf"^{re.escape(field)}\s*:", body, re.MULTILINE)
        if not in_fm and in_body:
            result.append(field)
    return result


def discover_unit_types(base: Path) -> list[str]:
    units = base / "04-knowledge" / "units"
    discovered = sorted(path.name for path in units.iterdir() if path.is_dir()) if units.exists() else []
    ordered = [type_name for type_name in BASE_UNIT_TYPES if type_name in discovered]
    ordered.extend(type_name for type_name in discovered if type_name not in BASE_UNIT_TYPES)
    return ordered


def iter_unit_files(base: Path) -> list[Path]:
    units = base / "04-knowledge" / "units"
    files: list[Path] = []
    for type_name in discover_unit_types(base):
        files.extend(sorted((units / type_name).glob("*.md")))
    return select_paths(base, "units", files)


def count_by_type(base: Path) -> dict[str, int]:
    units = base / "04-knowledge" / "units"
    return {type_name: len(select_paths(base, "units", list((units / type_name).glob("*.md")))) for type_name in discover_unit_types(base)}


def count_structure_nodes(base: Path) -> dict[str, int]:
    structure = base / "04-knowledge" / "structure"
    result: dict[str, int] = {}
    for dname in STRUCTURE_DIRS:
        d = structure / dname
        if d.exists():
            result[dname] = len(select_paths(base, "structure", [f for f in d.rglob("*.md") if f.is_file() and f.name.lower() != "readme.md"]))
        else:
            result[dname] = 0
    return result


def structure_node_type_issues(base: Path) -> list[dict]:
    structure = base / "04-knowledge" / "structure"
    issues: list[dict] = []
    for directory in STRUCTURE_DIRS:
        expected = directory[:-1] if directory.endswith("s") else directory
        for path in sorted((structure / directory).rglob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            actual = scalar_frontmatter_field(read_text(path), "node_type")
            if actual != expected:
                issues.append({
                    "file": path.relative_to(base).as_posix(),
                    "expected": expected,
                    "actual": actual or "missing",
                })
    return issues


def hierarchy_assignment_check(snapshots: list[UnitSnapshot]) -> dict:
    scalar_fields = ("primary_domain", "primary_dimension", "primary_theme")
    present = {
        field: sum(bool(scalar_frontmatter_field(snapshot.text, field)) for snapshot in snapshots)
        for field in scalar_fields
    }
    valid_topic_memberships = 0
    complete = 0
    for snapshot in snapshots:
        try:
            data = yaml.safe_load(snapshot.frontmatter) or {}
        except yaml.YAMLError:
            data = {}
        memberships = data.get("topic_memberships") or [] if isinstance(data, dict) else []
        has_valid_membership = isinstance(memberships, list) and any(
            isinstance(item, dict) and str(item.get("topic") or "").strip() and str(item.get("role") or "").strip()
            for item in memberships
        )
        valid_topic_memberships += int(has_valid_membership)
        complete += int(
            all(scalar_frontmatter_field(snapshot.text, field) for field in scalar_fields)
            and has_valid_membership
        )
    total = len(snapshots)
    present["topic_memberships"] = valid_topic_memberships
    return {
        "total_units": total,
        "complete_assignments": complete,
        "units_missing_any_assignment": total - complete,
        "field_coverage": {
            field: f"{present[field]}/{total}"
            for field in (*scalar_fields, "topic_memberships")
        },
    }


def hierarchy_structure_issues(base: Path) -> list[dict]:
    """Validate the five-level spine without treating Cluster candidates as nodes."""
    structure = base / "04-knowledge" / "structure"
    theme_files = sorted((structure / "themes").glob("*.md"))
    topic_files = sorted((structure / "topics").glob("*.md"))
    theme_codes: dict[str, dict] = {}
    issues: list[dict] = []

    for path in theme_files:
        if path.name.lower() == "readme.md":
            continue
        try:
            data = yaml.safe_load(extract_frontmatter(read_text(path))) or {}
        except yaml.YAMLError as exc:
            issues.append({"file": path.relative_to(base).as_posix(), "issue": "invalid_theme_frontmatter", "detail": str(exc)})
            continue
        code = str(data.get("theme_code") or "").strip()
        dimension = str(data.get("primary_dimension") or "").strip()
        if not code:
            issues.append({"file": path.relative_to(base).as_posix(), "issue": "missing_theme_code"})
            continue
        if code in theme_codes:
            issues.append({"file": path.relative_to(base).as_posix(), "issue": "duplicate_theme_code", "theme_code": code})
        theme_codes[code] = {"path": path, "dimension": dimension}
        if not dimension or not code.startswith(f"{dimension}."):
            issues.append({"file": path.relative_to(base).as_posix(), "issue": "theme_dimension_mismatch", "theme_code": code, "primary_dimension": dimension})

    for path in topic_files:
        if path.name.lower() == "readme.md":
            continue
        try:
            data = yaml.safe_load(extract_frontmatter(read_text(path))) or {}
        except yaml.YAMLError as exc:
            issues.append({"file": path.relative_to(base).as_posix(), "issue": "invalid_topic_frontmatter", "detail": str(exc)})
            continue
        parent = str(data.get("parent_theme") or "").strip()
        dimension = str(data.get("primary_dimension") or "").strip()
        if parent not in theme_codes:
            issues.append({"file": path.relative_to(base).as_posix(), "issue": "unknown_parent_theme", "parent_theme": parent or "missing"})
        elif dimension != theme_codes[parent]["dimension"]:
            issues.append({"file": path.relative_to(base).as_posix(), "issue": "topic_dimension_mismatch", "parent_theme": parent, "primary_dimension": dimension})
    return issues


def missing_fields(files: list[Path], base: Path, fields: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for field in fields:
        result[field] = [
            path.relative_to(base).as_posix()
            for path in files
            if not has_frontmatter_field(read_text(path), field)
        ]
    return result


def missing_fields_by_type(files: list[Path], fields: list[str]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for path in files:
        type_name = path.parent.name
        result.setdefault(type_name, {field: 0 for field in fields})
        text = read_text(path)
        for field in fields:
            if not has_frontmatter_field(text, field):
                result[type_name][field] += 1
    return result


def frontmatter_issues(files: list[Path], base: Path) -> dict[str, list[str]]:
    missing_fm: list[str] = []
    malformed_fm: list[str] = []
    for path in files:
        text = read_text(path)
        fm, _ = split_frontmatter_body(text)
        if not fm:
            if text.startswith("---"):
                malformed_fm.append(path.relative_to(base).as_posix())
            else:
                missing_fm.append(path.relative_to(base).as_posix())
    return {"frontmatter_missing": missing_fm, "frontmatter_malformed": malformed_fm}


def body_only_field_issues(files: list[Path], base: Path) -> list[dict]:
    issues: list[dict] = []
    for path in files:
        text = read_text(path)
        body_fields = body_only_required_fields_check(text)
        if body_fields:
            issues.append({
                "file": path.relative_to(base).as_posix(),
                "body_only_fields": body_fields,
            })
    return issues


def type_mismatch_issues(files: list[Path], base: Path) -> list[dict]:
    issues: list[dict] = []
    for path in files:
        parent_dir = path.parent.name
        expected = TYPE_DIR_MAP.get(parent_dir)
        if not expected:
            continue
        text = read_text(path)
        actual = scalar_frontmatter_field(text, "type")
        if actual and actual != expected:
            issues.append({
                "file": path.relative_to(base).as_posix(),
                "expected_type": expected,
                "actual_type": actual,
            })
    return issues


def invalid_enum_issues(files: list[Path], base: Path) -> dict[str, list[str]]:
    bad_confidence: list[str] = []
    bad_consensus: list[str] = []
    for path in files:
        text = read_text(path)
        conf = scalar_frontmatter_field(text, "confidence")
        cons = scalar_frontmatter_field(text, "consensus")
        if conf and conf not in VALID_CONFIDENCE:
            bad_confidence.append(path.relative_to(base).as_posix())
        if cons and cons not in VALID_CONSENSUS:
            bad_consensus.append(path.relative_to(base).as_posix())
    return {"invalid_confidence": bad_confidence, "invalid_consensus": bad_consensus}


def verification_semantic_issues(files: list[Path], base: Path) -> dict:
    l7_high_confidence: list[str] = []
    source_count_1_high_confidence: list[str] = []
    confirmed_without_external: list[str] = []
    body_status_frontmatter_conflict: list[str] = []
    identity_only_external_overreach: list[str] = []

    for path in files:
        text = read_text(path)
        confidence = scalar_frontmatter_field(text, "confidence")
        consensus = scalar_frontmatter_field(text, "consensus")
        source_count_str = scalar_frontmatter_field(text, "source_count")
        source_count = int(source_count_str) if source_count_str.isdigit() else 0
        verification_methods = list_frontmatter_field(text, "verification_methods")
        evidence_status = scalar_frontmatter_field(text, "evidence_status")
        verification_level = scalar_frontmatter_field(text, "verification_level")

        has_l7 = any("L7" in m for m in verification_methods)
        only_l7 = has_l7 and all(("L7" in m or m == "L7" or "failed" in m.lower()) for m in verification_methods)

        if confidence == "high" and has_l7 and source_count <= 1:
            l7_high_confidence.append(path.relative_to(base).as_posix())

        if confidence == "high" and source_count == 1:
            source_count_1_high_confidence.append(path.relative_to(base).as_posix())

        if consensus == "confirmed" and source_count <= 1:
            if not evidence_status or evidence_status == "source_backed":
                confirmed_without_external.append(path.relative_to(base).as_posix())

        fm_status = scalar_frontmatter_field(text, "verification_status")
        if fm_status and "[UNVERIFIED" in text:
            body_status_frontmatter_conflict.append(path.relative_to(base).as_posix())

        limited_scope_in_body = any(
            token in text
            for token in (
                "证据范围**: entity_identity_only",
                "证据范围**: term_existence",
                "证据范围**: event_identity_only",
                "证据范围**: bibliographic_hint",
            )
        )
        legacy_identity_note = "identity/existence verification only" in text
        if evidence_status == "externally_verified":
            if (
                (limited_scope_in_body and source_count <= 1)
                or (verification_level in {"L1", "L2"} and source_count <= 1 and legacy_identity_note)
            ):
                identity_only_external_overreach.append(path.relative_to(base).as_posix())

    return {
        "l7_high_confidence": l7_high_confidence,
        "source_count_1_high_confidence": source_count_1_high_confidence,
        "confirmed_without_external_or_multisource": confirmed_without_external,
        "body_status_frontmatter_conflict": body_status_frontmatter_conflict,
        "identity_only_external_overreach": identity_only_external_overreach,
    }


def verification_conflicts(files: list[Path], base: Path) -> list[str]:
    conflicts: list[str] = []
    for path in files:
        text = read_text(path)
        fm_consensus = scalar_frontmatter_field(text, "consensus")
        if fm_consensus == "confirmed" and "[UNVERIFIED" in text:
            conflicts.append(path.relative_to(base).as_posix())
    return conflicts


def verification_schema_check(files: list[Path], base: Path) -> dict:
    missing_es: list[str] = []
    missing_vl: list[str] = []
    for path in files:
        text = read_text(path)
        evidence_status = scalar_frontmatter_field(text, "evidence_status")
        verification_level = scalar_frontmatter_field(text, "verification_level")
        consensus = scalar_frontmatter_field(text, "consensus")

        if not evidence_status:
            missing_es.append(path.relative_to(base).as_posix())
        if not verification_level and consensus != "tentative":
            missing_vl.append(path.relative_to(base).as_posix())

    return {
        "missing_evidence_status": {"count": len(missing_es), "files": missing_es},
        "missing_verification_level_when_not_tentative": {"count": len(missing_vl), "files": missing_vl},
    }


def rule_drift_check(base: Path) -> dict:
    """检测 AGENTS/skills/hooks/README 与磁盘事实的漂移。"""
    try:
        base_str = str(base)
        if base_str not in sys.path:
            sys.path.insert(0, base_str)
        from scripts.audit_rule_drift import collect_findings
        findings = collect_findings(base)
        return {
            "findings": len(findings),
            "details": findings,
        }
    except ImportError as exc:
        return {"findings": -1, "error": f"audit_rule_drift import failed: {exc}"}


def unverified_by_type(files: list[Path], base: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for path in files:
        if "[UNVERIFIED" in read_text(path):
            result.setdefault(path.parent.name, []).append(path.relative_to(base).as_posix())
    return result


def migration_todo_sources(files: list[Path], base: Path) -> list[str]:
    return [path.relative_to(base).as_posix() for path in files if "MIGRATION_TODO" in read_text(path)]


def obsidian_syntax(files: list[Path], base: Path) -> list[str]:
    return [path.relative_to(base).as_posix() for path in files if "[[" in read_text(path)]


def local_file_issues(files: list[Path], base: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for path in files:
        for match in re.finditer(r"local_file:\s*['\"]?([^'\"\n]+)", read_text(path)):
            raw = match.group(1).strip()
            target = (base / raw).resolve()
            try:
                target.relative_to(base.resolve())
            except ValueError:
                issues.append({"file": path.relative_to(base).as_posix(), "local_file": raw, "issue": "outside_workspace"})
                continue
            if not target.exists():
                issues.append({"file": path.relative_to(base).as_posix(), "local_file": raw, "issue": "missing"})
    return issues


def evidence_ref_check(files: list[Path], base: Path) -> dict:
    with_ref: int = 0
    without_ref: int = 0
    refs_resolvable: int = 0
    refs_broken: int = 0
    units_with_traceable_source: int = 0
    for path in files:
        try:
            data = yaml.safe_load(extract_frontmatter(read_text(path))) or {}
        except Exception:
            data = {}
        sources = data.get("sources", []) if isinstance(data, dict) else []
        if isinstance(sources, dict):
            sources = [sources]
        refs = [
            source.get("evidence_ref")
            for source in sources
            if isinstance(source, dict) and isinstance(source.get("evidence_ref"), dict)
        ]
        if refs:
            with_ref += 1
        else:
            without_ref += 1
        unit_has_resolvable_ref = False
        for ref in refs:
            source_file = str(ref.get("source_file", "")).strip()
            doc_id = str(ref.get("doc_id", "")).strip()
            resolvable = (
                source_file.startswith(("https://", "http://"))
                or bool(source_file and (base / source_file).exists())
                or bool(doc_id and (base / "02-sources" / doc_id).exists())
            )
            if resolvable:
                refs_resolvable += 1
                unit_has_resolvable_ref = True
            else:
                refs_broken += 1
        source_metadata_traceable = any(
            isinstance(source, dict)
            and bool(str(source.get("citation", "")).strip())
            and bool(str(source.get("location", "")).strip())
            for source in sources
        )
        if unit_has_resolvable_ref or source_metadata_traceable:
            units_with_traceable_source += 1
    return {
        "sources_with_evidence_ref": with_ref,
        "sources_without_evidence_ref": without_ref,
        "evidence_ref_resolvable": refs_resolvable,
        "evidence_ref_broken": refs_broken,
        "evidence_refs_total": refs_resolvable + refs_broken,
        "units_with_traceable_source": units_with_traceable_source,
    }


def claim_traceability_check(base: Path) -> dict:
    claim_path = base / "04-knowledge" / "quality" / "claim-registry.yml"
    if not claim_path.exists():
        return {"claim_registry_exists": False}
    try:
        import yaml
        claims = yaml.safe_load(read_text(claim_path)) or []
    except Exception as e:
        return {"claim_registry_exists": True, "parse_error": str(e)}

    if isinstance(claims, dict):
        entries = [v for v in claims.values() if isinstance(v, dict)]
    elif isinstance(claims, list):
        entries = [v for v in claims if isinstance(v, dict)]
    else:
        entries = []

    entries = select_claims(base, entries)
    total = len(entries)
    with_source = 0
    with_source_span = 0
    with_supports = 0
    with_supported_by = 0
    with_statement_en = 0
    for claim in entries:
        source = claim.get("source") if isinstance(claim.get("source"), dict) else {}
        if source.get("doc_id"):
            with_source += 1
        if source.get("source_span"):
            with_source_span += 1
        if claim.get("supports"):
            with_supports += 1
        if claim.get("supported_by"):
            with_supported_by += 1
        if claim.get("statement_en"):
            with_statement_en += 1
    return {
        "claim_registry_exists": True,
        "total_claims": total,
        "claims_with_source": with_source,
        "claims_with_source_span": with_source_span,
        "claims_with_supports": with_supports,
        "claims_with_supported_by": with_supported_by,
        "claims_with_statement_en": with_statement_en,
    }


def relation_traceability_check(base: Path) -> dict:
    try:
        from scripts._relation_tables import load_relations
    except ModuleNotFoundError:
        from _relation_tables import load_relations
    relations = load_relations(base / "04-knowledge" / "tables" / "relations.csv")

    explicit = [r for r in relations if isinstance(r, dict) and r.get("relation_source") == "explicit"]
    with_evidence = [
        r for r in explicit
        if r.get("evidence_ref") or r.get("evidence") or r.get("claim_id") or str(r.get("target", "")).startswith("claim/")
    ]
    return {
        "relation_index_exists": True,
        "explicit_relations": len(explicit),
        "explicit_relations_with_evidence": len(with_evidence),
    }


def _registry_claim_slugs(base: Path) -> set[str]:
    claim_path = base / "04-knowledge" / "quality" / "claim-registry.yml"
    if not claim_path.exists():
        return set()
    try:
        import yaml

        claims = yaml.safe_load(read_text(claim_path)) or []
    except Exception:
        return set()

    if isinstance(claims, dict):
        entries = [v for v in claims.values() if isinstance(v, dict)]
    elif isinstance(claims, list):
        entries = [v for v in claims if isinstance(v, dict)]
    else:
        entries = []

    slugs: set[str] = set()
    for claim in entries:
        claim_id = claim.get("claim_id", "")
        if isinstance(claim_id, str):
            claim_match = re.fullmatch(r"claim[-_](.+)", claim_id)
            if claim_match:
                slugs.add(claim_match.group(1))

        migrated_from = claim.get("migrated_from", "")
        if isinstance(migrated_from, str):
            match = re.search(r"(?:ideas|concepts)/([a-z0-9\-]+)\.md$", migrated_from)
            if match:
                slugs.add(match.group(1))

    return slugs


def markdown_link_issues(base: Path) -> list[dict[str, str]]:
    roots = [
        base / "04-knowledge",
        base / "05-outputs" / "records" / "index",
    ]
    issues: list[dict[str, str]] = []
    code_fence = re.compile(r"```.*?```", re.DOTALL)
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    claim_slugs = _registry_claim_slugs(base)
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            text = code_fence.sub("", read_text(path))
            for match in link_pattern.finditer(text):
                link = match.group(1).strip()
                if not link or re.match(r"^(https?:|mailto:|#)", link):
                    continue
                target_part = link.split("#", 1)[0]
                if not target_part:
                    continue
                claim_match = re.fullmatch(r"\.\./claim/([a-z0-9\-]+)\.md", target_part)
                if claim_match and claim_match.group(1) in claim_slugs:
                    continue
                target = (path.parent / target_part).resolve()
                try:
                    target.relative_to(base.resolve())
                except ValueError:
                    issues.append({"file": path.relative_to(base).as_posix(), "link": link, "issue": "outside_workspace"})
                    continue
                if not target.exists():
                    issues.append({"file": path.relative_to(base).as_posix(), "link": link, "issue": "missing"})
    return issues


COMPACT_PROCESSING_PROFILE = "compact-v4"
COMPACT_PROCESSING_FILES = (
    "source-map.jsonl",
    "semantic-units.jsonl",
    "candidate-ledger.jsonl",
    "manifest.json",
    "summary.md",
)


def compact_processing_profile(doc_dir: Path) -> bool:
    manifest = doc_dir / "manifest.json"
    if not manifest.exists():
        return False
    try:
        return json.loads(manifest.read_text(encoding="utf-8"))\
            .get("processing_profile") == COMPACT_PROCESSING_PROFILE
    except json.JSONDecodeError:
        return False


def compact_processing_packages(processing: Path) -> list[Path]:
    """Return every compact-v4 package, including supplemental nested packages."""
    packages: set[Path] = set()
    if not processing.exists():
        return []
    for manifest in processing.rglob("manifest.json"):
        package = manifest.parent
        if compact_processing_profile(package):
            packages.add(package)
    return sorted(packages)


def compact_processing_issues(doc_dir: Path, root: Path) -> list[str]:
    missing = [name for name in COMPACT_PROCESSING_FILES if not (doc_dir / name).is_file()]
    if missing:
        return missing
    try:
        from scripts.validate_processing_package import compact_package_issues
    except ModuleNotFoundError:
        from validate_processing_package import compact_package_issues
    return compact_package_issues(doc_dir, root=root)


def dataflow_issues(base: Path) -> list[str]:
    intake = base / "02-sources"
    processing = base / "03-processing"
    issues: list[str] = []
    for doc in sorted(path for path in intake.iterdir() if path.is_dir() and not path.name.startswith("_")):
        proc_doc = processing / doc.name
        if not proc_doc.exists():
            issues.append(f"{doc.name}: missing processing directory")
            continue
        if compact_processing_profile(proc_doc):
            for missing in compact_processing_issues(proc_doc, root=base):
                issues.append(f"{doc.name}: compact-v4 missing {missing}")
            continue
        reports = list(proc_doc.rglob("validation_report.txt"))
        cleaned = list(proc_doc.rglob("cleaned.md"))
        semantic_maps = list(proc_doc.rglob("semantic-map.md"))
        chunks = list(proc_doc.rglob("chunk_*.txt")) + list(proc_doc.rglob("chunk_*.md"))
        manifests = list(proc_doc.rglob("manifest.json"))
        legacy_processing = bool(reports and chunks)
        semantic_processing = bool(cleaned and semantic_maps and chunks)
        if not legacy_processing and not semantic_processing:
            issues.append(f"{doc.name}: missing processing report/cleaned semantic chunks")
        if not manifests:
            issues.append(f"{doc.name}: missing manifest.json")
    return issues


def chunk_meta_check(base: Path) -> dict[str, int]:
    processing = base / "03-processing"
    total_chunks = 0
    missing_meta = 0
    chunk_paths = list(processing.rglob("chunk_*.txt")) + list(processing.rglob("chunk_*.md"))
    for chunk_path in chunk_paths:
        total_chunks += 1
        meta_path = chunk_path.with_suffix(".meta.json")
        if not meta_path.exists():
            missing_meta += 1
    return {"total_chunks": total_chunks, "chunk_meta_missing": missing_meta}


def duplicate_basenames(files: list[Path], base: Path) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for path in files:
        normalized = re.sub(r"-\d{3,4}$", "", path.stem)
        groups.setdefault(normalized, []).append(path.relative_to(base / "04-knowledge" / "units").as_posix())
    return {name: paths for name, paths in groups.items() if len(paths) > 1}


def disambiguation_check(files: list[Path], duplicates: dict[str, list[str]], base: Path) -> dict:
    with_disambig = 0
    without_disambig = 0
    for group_name, paths in duplicates.items():
        for rel_path in paths:
            full_path = base / "04-knowledge" / "units" / rel_path
            text = read_text(full_path)
            fm = extract_frontmatter(text)
            if "disambiguation:" in fm:
                with_disambig += 1
            else:
                without_disambig += 1
    return {
        "duplicate_basenames": len(duplicates),
        "duplicates_with_disambiguation": with_disambig,
        "duplicates_without_disambiguation": without_disambig,
    }


def rule_authority_check(base: Path) -> dict:
    try:
        from scripts.audit_rule_drift import check_codex_core_layout
    except ModuleNotFoundError:
        from audit_rule_drift import check_codex_core_layout
    return {
        "agents_dir_exists": (base / ".agents/skills").is_dir(),
        "agents_entry_exists": (base / "AGENTS.md").is_file(),
        "pipeline_exists": (base / ".agents/pipeline.md").is_file(),
        "client": "codex",
        "hook_status": "not_configured",
        "adapter_issues": check_codex_core_layout(base),
        "legacy_references": 0,
    }


def hierarchy_version(base: Path) -> str:
    path = base / "04-knowledge" / "structure" / "hierarchy" / "index.md"
    if not path.exists():
        return "missing"
    match = re.search(r"version:\s*([0-9.]+)", read_text(path))
    return f"v{match.group(1)}" if match else "unknown"


def count_candidate_rows(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    in_table = False
    header_seen = False
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            header_seen = False
            continue
        if "---" in stripped:
            in_table = True
            continue
        if not in_table:
            header_seen = True
            continue
        if not header_seen:
            header_seen = True
            continue
        count += 1
    return count


def growth_candidate_signals(base: Path, duplicate_groups: dict[str, list[str]]) -> dict:
    unit_types = discover_unit_types(base)
    unknown_type_dirs = [type_name for type_name in unit_types if type_name not in BASE_UNIT_TYPES]
    return {
        "unknown_type_dirs": unknown_type_dirs,
        "duplicate_basename_groups": len(duplicate_groups),
        "type_candidate_rows": count_candidate_rows(base / "04-knowledge" / "structure" / "taxonomy" / "type-candidates.md"),
        "dimension_candidate_rows": count_candidate_rows(base / "04-knowledge" / "structure" / "dimension-candidates.md"),
    }


def snapshot_disclaimer_check(base: Path) -> list[str]:
    drafts_readme = base / "05-outputs" / "drafts" / "README.md"
    if not drafts_readme.parent.exists():
        return []
    if not drafts_readme.exists():
        return ["drafts/README.md missing"]
    text = read_text(drafts_readme)
    if "历史快照" not in text and "snapshot" not in text.lower():
        return ["drafts/README.md missing snapshot disclaimer"]
    return []


def current_health_exists(base: Path) -> bool:
    return (base / "06-runtime" / "state" / "current-health.json").exists()


def governance_backlog_exists(base: Path) -> bool:
    return (base / "06-runtime" / "governance" / "governance-backlog.md").exists()


def source_hash_check(base: Path) -> dict:
    intake = base / "02-sources"
    processing = base / "03-processing"
    declared_paths: set[str] = set()
    mismatched: list[str] = []
    missing_paths: list[str] = []
    metadata_files = sorted(processing.glob("*/source-metadata.json"))
    try:
        from scripts._source_fingerprint import source_sha256
    except ModuleNotFoundError:
        from _source_fingerprint import source_sha256

    for metadata_path in metadata_files:
        try:
            metadata = json.loads(read_text(metadata_path))
        except json.JSONDecodeError:
            missing_paths.append(f"{metadata_path.relative_to(base).as_posix()}:invalid_metadata")
            continue
        for asset in metadata.get("source_assets") or []:
            if not isinstance(asset, dict) or not asset.get("path"):
                missing_paths.append(f"{metadata_path.relative_to(base).as_posix()}:invalid_asset")
                continue
            rel = str(asset["path"])
            declared_paths.add(rel)
            path = base / rel
            expected = str(asset.get("sha256") or "")
            if not path.is_file() or not expected.startswith("sha256:"):
                missing_paths.append(rel)
            elif source_sha256(path) != expected:
                mismatched.append(rel)

    legacy_total = 0
    missing_hash = 0
    for doc_dir in intake.iterdir():
        if not doc_dir.is_dir() or doc_dir.name.startswith("_"):
            continue
        for orig_file in doc_dir.rglob("original.*"):
            if orig_file.suffix in (".bak", ".tmp", ".swp"):
                continue
            rel_original = orig_file.relative_to(base).as_posix()
            if rel_original in declared_paths:
                continue
            legacy_total += 1
            nearest_meta = None
            for p in [orig_file.parent, doc_dir]:
                candidate = p / "intake-metadata.json"
                if candidate.exists():
                    nearest_meta = candidate
                    break
            if not nearest_meta:
                missing_hash += 1
                continue
            try:
                meta = json.loads(read_text(nearest_meta))
                if "source_sha256" not in meta and "original_hash" not in meta:
                    missing_hash += 1
            except (json.JSONDecodeError, KeyError):
                missing_hash += 1
    reopened_packages = []
    for package in compact_processing_packages(processing):
        try:
            from scripts.validate_processing_package import package_source_state
        except (ModuleNotFoundError, ImportError):
            from validate_processing_package import package_source_state
        state = package_source_state(package, root=base)
        if state["effective_status"] == "reopened_source_drift":
            reopened_packages.append(package.relative_to(base).as_posix())
    return {
        "total_sources": len(declared_paths) + legacy_total,
        "source_hash_missing": len(missing_paths) + missing_hash,
        "source_hash_drift": len(mismatched),
        "declared_source_assets": len(declared_paths),
        "metadata_files": len(metadata_files),
        "reopened_packages": reopened_packages,
        "missing_sample": sorted(missing_paths)[:25],
        "drift_sample": sorted(mismatched)[:25],
    }


def build_structural_health_score(results: dict) -> dict:
    total = 0

    rule_authority = results.get("rule_authority", {})
    ra_score = 20
    if not rule_authority.get("agents_dir_exists", False):
        ra_score -= 5
    if not rule_authority.get("agents_entry_exists", False):
        ra_score -= 10
    if not rule_authority.get("pipeline_exists", False):
        ra_score -= 5
    if rule_authority.get("adapter_issues"):
        ra_score -= min(len(rule_authority["adapter_issues"]), 5)
    ra_score = max(0, ra_score)
    total += ra_score

    frontmatter_issues_count = (
        len(results.get("frontmatter_missing", [])) +
        len(results.get("frontmatter_malformed", [])) +
        sum(len(v) for v in results.get("required_field_missing", {}).values()) +
        len(results.get("body_only_field_issues", []))
    )
    fm_score = max(0, 20 - min(frontmatter_issues_count * 1, 20))
    total += fm_score

    vs = results.get("verification_semantic_issues", {})
    ver_issues = (
        len(vs.get("l7_high_confidence", [])) * 3 +
        len(vs.get("source_count_1_high_confidence", [])) * 2 +
        len(vs.get("confirmed_without_external_or_multisource", [])) * 3 +
        len(vs.get("body_status_frontmatter_conflict", [])) * 2 +
        len(vs.get("identity_only_external_overreach", [])) * 3
    )
    ver_score = max(0, 20 - min(ver_issues, 20))
    total += ver_score

    er = results.get("evidence_ref", {})
    total_er = er.get("sources_with_evidence_ref", 0) + er.get("sources_without_evidence_ref", 1)
    evidence_ref_ratio = er.get("units_with_traceable_source", er.get("sources_with_evidence_ref", 0)) / max(total_er, 1)
    resolvable_ratio = er.get("evidence_ref_resolvable", 0) / max(
        er.get("evidence_refs_total", er.get("sources_with_evidence_ref", 0)), 1
    )
    rt = results.get("relation_traceability", {})
    relation_evidence_ratio = rt.get("explicit_relations_with_evidence", 0) / max(rt.get("explicit_relations", 0), 1)
    link_penalty = min(len(results.get("markdown_link_issues", [])) // 200, 1)
    local_penalty = min(len(results.get("local_file_issues", [])), 2)
    trace_score = round(
        evidence_ref_ratio * 5 +
        resolvable_ratio * 4 +
        relation_evidence_ratio * 6 -
        link_penalty -
        local_penalty
    )
    trace_score = max(0, min(trace_score, 15))
    total += trace_score

    accepted_catalog = results.get("execution_scope", {}).get("knowledge_inputs") == "accepted_catalog"
    inventory_is_progress = results.get("execution_scope", {}).get("processing_inventory_is_research_progress", True)
    df_issues = 0 if accepted_catalog else len(results.get("dataflow_issues", []))
    df_score = max(0, 10 - min(df_issues * 2, 10))
    total += df_score

    missing_disclaimer = len(results.get("snapshot_disclaimer_missing", []))
    has_current = results.get("current_health_exists", False)
    vs2 = results.get("verification_schema", {})
    vs2_issues = vs2.get("missing_evidence_status", {}).get("count", 0) // 10
    report_score = 10
    if missing_disclaimer > 0:
        report_score -= min(missing_disclaimer * 2, 6)
    if not has_current:
        report_score -= 4
    report_score -= min(vs2_issues, 4)
    report_score = max(0, report_score)
    total += report_score

    adapter_issues = len(results.get("rule_authority", {}).get("adapter_issues", []))
    eng_score = max(0, 5 - min(adapter_issues, 5))
    rule_drift_count = results.get("rule_drift", {}).get("findings", 0)
    if rule_drift_count > 0:
        eng_score = max(0, eng_score - min(rule_drift_count // 5, 3))
    retention = results.get("runtime_artifact_retention", {})
    if retention.get("review_required", 0):
        eng_score = max(0, eng_score - 1)
    if retention.get("ephemeral_residue", 0):
        eng_score = max(0, eng_score - min(retention["ephemeral_residue"], 2))
    total += eng_score

    rq = results.get("recall_quality", {})
    rq_issues = (
        len(rq.get("chapters_without_candidate", [])) * 2 +
        len(rq.get("chapters_without_decision", [])) * 2 +
        len(rq.get("chapters_without_recall", [])) * 2 +
        len(rq.get("semantic_maps_with_unresolved", [])) * 1 +
        rq.get("manifests_scaffolded", 0) * 2
    )
    recall_score = 15 if not inventory_is_progress else max(0, 15 - min(rq_issues, 15))
    total += recall_score

    srq = results.get("semantic_artifact_integrity", {})
    srq_issues = (
        len(srq.get("chapters_without_reading_ledger", [])) * 2 +
        len(srq.get("chapters_without_continuity_map", [])) * 2 +
        len(srq.get("chapters_without_semantic_stitch_log", [])) * 2 +
        len(srq.get("chapters_without_source_structure_map", [])) * 1 +
        len(srq.get("chapters_without_extraction_coverage_matrix", [])) * 2
    )
    reading_score = 15 if not inventory_is_progress else max(0, 15 - min(srq_issues, 15))
    total += reading_score

    return {
        "score_kind": "structural_contract_health",
        "max_score": 130,
        "total": total,
        "rule_authority": ra_score,
        "frontmatter": fm_score,
        "verification_semantics": ver_score,
        "traceability": trace_score,
        "dataflow": df_score,
        "report_freshness": report_score,
        "engineering_safety": eng_score,
        "recall_quality": recall_score,
        "semantic_artifact_integrity": reading_score,
    }


def build_knowledge_structure_quality_score(results: dict) -> dict:
    da = results.get("disambiguation", {})
    without = da.get("duplicates_without_disambiguation", 0)
    dup_score = max(0, 15 - without * 2)
    type_m = (
        len(results.get("type_mismatches", []))
        + len(results.get("structure_node_type_issues", []))
        + len(results.get("hierarchy_structure_issues", []))
    )
    type_score = max(0, 10 - type_m * 2)
    invalid_conf = len(results.get("invalid_enums", {}).get("invalid_confidence", [])) + len(results.get("invalid_enums", {}).get("invalid_consensus", []))
    enum_score = max(0, 10 - invalid_conf * 5)
    unverified = sum(len(v) for v in results.get("unverified_by_type", {}).values())
    ver_score_kq = max(0, 10 - unverified // 10)
    recommended_missing_total = sum(len(v) for v in results.get("recommended_field_missing", {}).values())
    rec_score = max(0, 10 - recommended_missing_total // 20)
    hierarchy = results.get("hierarchy_assignment", {})
    hierarchy_total = hierarchy.get("total_units", 0)
    hierarchy_score = 10 if hierarchy_total == 0 else int(
        10 * hierarchy.get("complete_assignments", 0) / hierarchy_total
    )
    total = dup_score + type_score + enum_score + ver_score_kq + rec_score + hierarchy_score
    return {
        "score_kind": "knowledge_schema_and_state_integrity",
        "max_score": 65,
        "total": total,
        "disambiguation": dup_score,
        "type_correctness": type_score,
        "enum_validity": enum_score,
        "verification_coverage": ver_score_kq,
        "recommended_fields": rec_score,
        "hierarchy_assignment": hierarchy_score,
    }


def build_evidence_quality_score(results: dict) -> dict:
    er = results.get("evidence_ref", {})
    total_er = er.get("sources_with_evidence_ref", 0) + er.get("sources_without_evidence_ref", 0)
    coverage = er.get("units_with_traceable_source", er.get("sources_with_evidence_ref", 0)) / max(total_er, 1)
    er_score = int(coverage * 20)
    cm = results.get("chunk_meta", {})
    chunk_total = cm.get("total_chunks", 0)
    chunk_missing = cm.get("chunk_meta_missing", 0)
    chunk_score = 15 if chunk_total == 0 else max(0, 15 - int((chunk_missing / max(chunk_total, 1)) * 15))
    sh = results.get("source_hash", {})
    hash_total = sh.get("total_sources", 0)
    hash_missing = sh.get("source_hash_missing", 0) + sh.get("source_hash_drift", 0)
    hash_score = 10 if hash_total == 0 else max(0, 10 - int((hash_missing / max(hash_total, 1)) * 10))
    vs2 = results.get("verification_schema", {})
    es_count = vs2.get("missing_evidence_status", {}).get("count", 0)
    total_units = max(results.get("summary", {}).get("total_units", 1), 1)
    schema_coverage = max(0, 10 - int((es_count / total_units) * 50))
    total = er_score + chunk_score + hash_score + schema_coverage
    return {
        "score_kind": "evidence_chain_integrity",
        "max_score": 55,
        "total": total,
        "evidence_ref_coverage": er_score,
        "chunk_meta_completeness": chunk_score,
        "source_hash_completeness": hash_score,
        "verification_schema_coverage": schema_coverage,
    }


def knowledge_maturity_check(base: Path, snapshots: list[UnitSnapshot]) -> dict:
    """Expose semantic maturity distributions without collapsing them into a score."""
    from collections import Counter

    source_counts: Counter[str] = Counter()
    confidence: Counter[str] = Counter()
    consensus: Counter[str] = Counter()
    evidence_status: Counter[str] = Counter()
    unit_refs = {snapshot.relative_path.removeprefix("04-knowledge/units/") for snapshot in snapshots}

    for snapshot in snapshots:
        raw_source_count = scalar_frontmatter_field(snapshot.text, "source_count")
        if raw_source_count.isdigit():
            value = int(raw_source_count)
        else:
            try:
                frontmatter_data = yaml.safe_load(snapshot.frontmatter) or {}
            except yaml.YAMLError:
                frontmatter_data = {}
            raw_sources = frontmatter_data.get("sources") or [] if isinstance(frontmatter_data, dict) else []
            value = len(raw_sources) if isinstance(raw_sources, list) else 0
        source_counts["multi_source" if value >= 2 else "single_source" if value == 1 else "zero"] += 1
        confidence[scalar_frontmatter_field(snapshot.text, "confidence") or "missing"] += 1
        consensus[scalar_frontmatter_field(snapshot.text, "consensus") or "missing"] += 1
        evidence_status[scalar_frontmatter_field(snapshot.text, "evidence_status") or "missing"] += 1

    connected: set[str] = set()
    try:
        from scripts._relation_tables import load_relations
    except ModuleNotFoundError:
        from _relation_tables import load_relations
    relation_table = base / "04-knowledge" / "tables" / "relations.csv"
    for relation in (load_relations(relation_table) if relation_table.is_file() else []):
        for field in ("source", "target"):
            ref = str(relation.get(field) or "").removeprefix("04-knowledge/units/")
            if ref in unit_refs:
                connected.add(ref)
    isolated = sorted(unit_refs - connected)

    candidate_inventory = {"total": 0, "by_state": {}, "by_candidate_type": {}}
    candidate_counts = {"total": 0, "by_state": {}, "by_candidate_type": {}}
    discovery_manifest = base / "06-runtime" / "state" / "discovery-manifest.json"
    if discovery_manifest.is_file():
        try:
            discovery = json.loads(discovery_manifest.read_text(encoding="utf-8-sig"))
            candidate_inventory = discovery.get("candidate_counts", candidate_inventory)
            candidate_counts = discovery.get("actionable_candidate_counts", candidate_counts)
        except json.JSONDecodeError:
            pass

    hierarchy = hierarchy_assignment_check(snapshots)
    catalog = load_catalog(base)
    discovery_started = (
        bool(catalog["structure"])
        if catalog is not None
        else any(count_structure_nodes(base).values())
    )
    return {
        "metric_kind": "unscored_semantic_maturity",
        "total_units": len(snapshots),
        "source_count_distribution": dict(sorted(source_counts.items())),
        "confidence_distribution": dict(sorted(confidence.items())),
        "consensus_distribution": dict(sorted(consensus.items())),
        "evidence_status_distribution": dict(sorted(evidence_status.items())),
        "isolated_units": {"count": len(isolated), "sample": isolated[:25]},
        "candidate_debt": candidate_counts,
        "candidate_inventory": candidate_inventory,
        "research_debt": {
            "single_source_units": source_counts.get("single_source", 0),
            "tentative_units": consensus.get("tentative", 0),
            "low_confidence_units": confidence.get("low", 0),
            "candidates_needing_evidence": candidate_counts.get("by_state", {}).get("needs_evidence", 0),
            "units_missing_hierarchy_assignment": (
                hierarchy["units_missing_any_assignment"] if discovery_started else 0
            ),
        },
        "hierarchy_assignment_status": "active" if discovery_started else "not_started",
    }


def recall_quality_check(base: Path) -> dict:
    """Scan processing dirs for missing recall audit artifacts.

    Checks whether each processing chapter has the v3.1 mandatory recall
    products and tracks unresolved candidates in semantic-map files.
    """
    processing = base / "03-processing"
    manifests_scaffolded = 0
    chapters_without_candidate = []
    chapters_without_decision = []
    chapters_without_recall = []
    semantic_maps_with_unresolved = []
    total_chapters = 0

    for doc_dir in sorted(p for p in processing.iterdir() if p.is_dir() and not p.name.startswith("_")):
        if compact_processing_profile(doc_dir):
            total_chapters += 1
            missing = set(compact_processing_issues(doc_dir, root=base))
            relative = doc_dir.relative_to(base).as_posix()
            if "candidate-ledger.jsonl" in missing:
                chapters_without_candidate.append(relative)
                chapters_without_decision.append(relative)
            if "summary.md" in missing:
                chapters_without_recall.append(relative)
            continue
        for ch_dir in sorted(p for p in doc_dir.iterdir() if p.is_dir()):
            if compact_processing_profile(ch_dir):
                total_chapters += 1
                missing = set(compact_processing_issues(ch_dir, root=base))
                relative = ch_dir.relative_to(base).as_posix()
                if any(item.startswith("candidate-ledger.jsonl") for item in missing):
                    chapters_without_candidate.append(relative)
                    chapters_without_decision.append(relative)
                if any(item.startswith("summary.md") for item in missing):
                    chapters_without_recall.append(relative)
                continue
            total_chapters += 1
            if not (ch_dir / "candidate-units.md").exists():
                chapters_without_candidate.append(ch_dir.relative_to(base).as_posix())
            if not (ch_dir / "extraction-decision-matrix.md").exists():
                chapters_without_decision.append(ch_dir.relative_to(base).as_posix())
            if not (ch_dir / "recall-audit.md").exists():
                chapters_without_recall.append(ch_dir.relative_to(base).as_posix())
            # Check semantic-map for unresolved candidates
            sm = ch_dir / "semantic-map.md"
            if sm.exists():
                content = read_text(sm)
                if "❌" in content or "scaffolded" in content.lower() or "pending" in content.lower():
                    semantic_maps_with_unresolved.append(ch_dir.relative_to(base).as_posix())

        # Check manifest status
        mf = doc_dir / "manifest.json"
        if mf.exists():
            try:
                import json
                mf_data = json.loads(mf.read_text(encoding="utf-8"))
                if "scaffolded" in str(mf_data.get("status", "")):
                    manifests_scaffolded += 1
                if mf_data.get("semantic_review_status", "") == "pending":
                    manifests_scaffolded += 1
            except Exception:
                pass

    return {
        "total_chapters": total_chapters,
        "chapters_without_candidate": chapters_without_candidate,
        "chapters_without_decision": chapters_without_decision,
        "chapters_without_recall": chapters_without_recall,
        "semantic_maps_with_unresolved": semantic_maps_with_unresolved,
        "manifests_scaffolded": manifests_scaffolded,
    }


def semantic_artifact_integrity_check(base: Path) -> dict:
    """Scan processing dirs for missing mechanical semantic artifacts."""
    processing = base / "03-processing"
    chapters_without_ledger = []
    chapters_without_continuity = []
    chapters_without_stitch = []
    chapters_without_structure = []
    chapters_without_coverage_matrix = []
    total_chapters = 0

    for doc_dir in sorted(p for p in processing.iterdir() if p.is_dir() and not p.name.startswith("_")):
        if compact_processing_profile(doc_dir):
            total_chapters += 1
            missing = set(compact_processing_issues(doc_dir, root=base))
            relative = doc_dir.relative_to(base).as_posix()
            if "source-map.jsonl" in missing:
                chapters_without_ledger.append(relative)
                chapters_without_structure.append(relative)
                chapters_without_coverage_matrix.append(relative)
            if "semantic-units.jsonl" in missing:
                chapters_without_continuity.append(relative)
                chapters_without_stitch.append(relative)
            continue
        for ch_dir in sorted(p for p in doc_dir.iterdir() if p.is_dir()):
            if compact_processing_profile(ch_dir):
                total_chapters += 1
                missing = set(compact_processing_issues(ch_dir, root=base))
                relative = ch_dir.relative_to(base).as_posix()
                if any(item.startswith("source-map.jsonl") for item in missing):
                    chapters_without_ledger.append(relative)
                    chapters_without_structure.append(relative)
                    chapters_without_coverage_matrix.append(relative)
                if any(item.startswith("semantic-units.jsonl") for item in missing):
                    chapters_without_continuity.append(relative)
                    chapters_without_stitch.append(relative)
                continue
            total_chapters += 1
            if not (ch_dir / "reading-ledger.md").exists():
                chapters_without_ledger.append(ch_dir.relative_to(base).as_posix())
            if not (ch_dir / "continuity-map.md").exists():
                chapters_without_continuity.append(ch_dir.relative_to(base).as_posix())
            if not (ch_dir / "semantic-stitch-log.md").exists():
                chapters_without_stitch.append(ch_dir.relative_to(base).as_posix())
            if not (ch_dir / "source-structure-map.md").exists():
                chapters_without_structure.append(ch_dir.relative_to(base).as_posix())
            if not (ch_dir / "extraction-coverage-matrix.md").exists():
                chapters_without_coverage_matrix.append(ch_dir.relative_to(base).as_posix())

    return {
        "metric_label": "语义工件完整性",
        "metric_boundary": "只检查覆盖工件与引用闭合，不代表语义验收",
        "total_chapters": total_chapters,
        "chapters_without_reading_ledger": chapters_without_ledger,
        "chapters_without_continuity_map": chapters_without_continuity,
        "chapters_without_semantic_stitch_log": chapters_without_stitch,
        "chapters_without_source_structure_map": chapters_without_structure,
        "chapters_without_extraction_coverage_matrix": chapters_without_coverage_matrix,
    }

TRANSLATION_FIELD_GROUPS = {
    "persons": ["name_original", "language_original", "name_zh", "translation_status"],
    "families": ["name_original", "name_original_language", "name_zh", "translation_status"],
    "institutions": ["name_original", "name_original_language", "name_zh", "translation_status"],
    "places": [],
    "works": ["title_original", "title_original_language", "title_zh"],
    "archives": ["title_original", "title_original_language", "title_zh"],
    "terms": ["term_original", "term_zh", "academic_translation_status"],
    "procedures": [],
    "events": [],
}

TRANSLATION_INDEX_TYPES = ["persons", "terms", "archives", "works", "families", "institutions"]


def translation_coverage_gap_count(translation_health: dict) -> int:
    gaps = 0
    for type_data in translation_health.values():
        for value in type_data.get("coverage", {}).values():
            if not isinstance(value, str) or "/" not in value:
                gaps += 1
                continue
            numerator, denominator = value.split("/", 1)
            if not numerator.isdigit() or not denominator.isdigit():
                gaps += 1
                continue
            gaps += max(0, int(denominator) - int(numerator))
    return gaps


def translation_health_check(base: Path) -> dict:
    units = base / "04-knowledge" / "units"
    result = {}
    for type_name, fields in TRANSLATION_FIELD_GROUPS.items():
        if not fields:
            continue
        d = units / type_name
        if not d.exists():
            continue
        fcount = len(list(d.glob("*.md")))
        field_coverage = {}
        for fld in fields:
            cnt = 0
            for f in d.glob("*.md"):
                frontmatter = extract_frontmatter(f.read_text(encoding="utf-8"))
                if re.search(rf"^{fld}:", frontmatter, re.MULTILINE):
                    cnt += 1
            field_coverage[fld] = f"{cnt}/{fcount}"
        result[type_name] = {"total": fcount, "coverage": field_coverage}
    return result


def translation_index_integrity_check(base: Path) -> dict:
    import yaml

    units = base / "04-knowledge" / "units"
    expected = sorted(
        f"{type_name}/{path.stem}"
        for type_name in TRANSLATION_INDEX_TYPES
        for path in (units / type_name).rglob("*.md")
        if (units / type_name).exists()
    )
    index_path = base / "04-knowledge" / "quality" / "translation-index.yml"
    if not index_path.exists():
        return {
            "index_exists": False,
            "expected": len(expected),
            "indexed": 0,
            "declared_total": 0,
            "missing": expected,
            "stale": [],
            "duplicate": [],
            "declared_total_mismatch": bool(expected),
        }
    data = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    rows = [row for row in data.get("index", []) if isinstance(row, dict)]
    slugs = [row.get("slug") for row in rows if row.get("slug")]
    duplicate = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    return {
        "index_exists": True,
        "expected": len(expected),
        "indexed": len(slugs),
        "declared_total": data.get("total", 0),
        "missing": sorted(set(expected) - set(slugs)),
        "stale": sorted(set(slugs) - set(expected)),
        "duplicate": duplicate,
        "declared_total_mismatch": data.get("total", 0) != len(slugs),
    }


def architecture_drift_check(base: Path, counts: dict) -> dict:
    deprecated_with_files = {t: counts.get(t, 0) for t in DEPRECATED_DIRS if counts.get(t, 0) > 0}
    hierarchy_path = base / "04-knowledge" / "structure" / "hierarchy" / "index.md"
    hv = hierarchy_version(base)
    hierarchy_has_old_types = False
    if hierarchy_path.exists():
        htext = hierarchy_path.read_text(encoding="utf-8")
        hierarchy_has_old_types = any(t in htext for t in ["concept/", "technique/", "ideas/", "cases/"])
    hier_stat_old = False
    if hierarchy_path.exists():
        htext = hierarchy_path.read_text(encoding="utf-8")
        in_table = False
        for line in htext.splitlines():
            if "统计概览" in line or ("合计" in line and "议题" in line):
                in_table = True
            if in_table and "758" in line and "个知识元" in line:
                hier_stat_old = True
                break
            if in_table and "---" in line:
                in_table = False
    return {
        "deprecated_type_drift": len(deprecated_with_files),
        "deprecated_details": deprecated_with_files,
        "hierarchy_version": hv,
        "hierarchy_has_old_type_refs": hierarchy_has_old_types,
        "hierarchy_has_old_statistics": hier_stat_old,
    }


def relation_health_check(base: Path) -> dict:
    try:
        from scripts._relation_tables import load_relations
    except ModuleNotFoundError:
        from _relation_tables import load_relations
    relations = load_relations(base / "04-knowledge" / "tables" / "relations.csv")
    if load_catalog(base) is not None:
        try:
            from scripts.build_knowledge_graph_data import endpoint_node_id
        except ModuleNotFoundError:
            from build_knowledge_graph_data import endpoint_node_id
        units_root = base / "04-knowledge" / "units"
        admitted = {endpoint_node_id(path.relative_to(units_root).as_posix()) for path in iter_unit_files(base)}
        relations = [r for r in relations if endpoint_node_id(str(r.get("source", ""))) in admitted
                     and endpoint_node_id(str(r.get("target", ""))) in admitted]
    sources = {}
    types = {}
    for r in relations:
        sources[r.get("relation_source", "unknown")] = sources.get(r.get("relation_source", "unknown"), 0) + 1
        types[r.get("relation_type", "unknown")] = types.get(r.get("relation_type", "unknown"), 0) + 1
    weak = sum(1 for r in relations if r.get("review_status") in ("weak_inference",))
    needs_ev = sum(1 for r in relations if r.get("review_status") == "needs_evidence")
    broad_weak_types = {"related_to", "involves_person", "relates_to_term", "relates_to_work"}
    weak_evidence = sum(
        1
        for r in relations
        if r.get("confidence") in ("low", "medium")
        and not (r.get("evidence") or r.get("evidence_ref") or r.get("claim_id"))
        and r.get("relation_type") not in broad_weak_types
    )
    return {
        "relation_index_exists": True,
        "relation_index_total": len(relations),
        "explicit_relation_count": sources.get("explicit", 0),
        "inferred_relation_count": sources.get("inferred_by_rule", 0) + sources.get("inferred_by_model", 0),
        "migrated_from_related_count": sources.get("migrated_from_related", 0),
        "weak_inference_count": weak,
        "weak_evidence_count": weak_evidence,
        "needs_evidence_count": needs_ev,
        "relation_type_coverage": f"{len(types)}/{RELATION_TYPE_TOTAL}",
    }


def semantic_acceptance_check(base: Path) -> dict:
    """Report Agent reread acceptance separately from artifact integrity."""
    processing = base / "03-processing"
    packages = []
    legacy_without_acceptance = []
    counts = {
        "accepted": 0,
        "accepted_with_findings": 0,
        "pending_or_invalid": 0,
        "reopened_source_drift": 0,
    }
    try:
        from scripts.validate_processing_package import package_source_state
    except ModuleNotFoundError:
        from validate_processing_package import package_source_state
    for package in compact_processing_packages(processing):
        manifest_path = package / "manifest.json"
        try:
            manifest = json.loads(read_text(manifest_path))
        except json.JSONDecodeError:
            counts["pending_or_invalid"] += 1
            packages.append({"package": package.relative_to(base).as_posix(), "reread_status": "invalid_manifest"})
            continue
        source_state = package_source_state(package, root=base)
        acceptance = manifest.get("semantic_acceptance") or {}
        reread_status = acceptance.get("reread_status", "pending")
        if source_state["effective_status"] == "reopened_source_drift":
            effective = "stale_source_drift"
            counts["reopened_source_drift"] += 1
        elif reread_status in {"accepted", "accepted_with_findings"}:
            effective = reread_status
            counts[reread_status] += 1
        else:
            effective = "pending_or_invalid"
            counts["pending_or_invalid"] += 1
        packages.append({
            "package": package.relative_to(base).as_posix(),
            "reread_status": reread_status,
            "effective_status": effective,
            "source_version": acceptance.get("source_version"),
            "omission_count": acceptance.get("omission_count"),
            "acceptance_boundary": acceptance.get("acceptance_boundary"),
        })
    compact_set = set(compact_processing_packages(processing))
    for doc_dir in sorted(path for path in processing.iterdir() if path.is_dir() and not path.name.startswith("_")):
        if doc_dir in compact_set:
            continue
        for scope in sorted(path for path in doc_dir.iterdir() if path.is_dir()):
            if scope in compact_set:
                continue
            if (scope / "manifest.json").is_file():
                legacy_without_acceptance.append(scope.relative_to(base).as_posix())
    return {
        "metric_kind": "unscored_agent_semantic_acceptance",
        "total_packages": len(packages),
        "legacy_packages_without_acceptance": len(legacy_without_acceptance),
        "legacy_sample": legacy_without_acceptance[:25],
        **counts,
        "packages": packages,
    }


def runtime_artifact_retention_check(base: Path) -> dict:
    """Expose compact retention signals in health without copying the full report."""
    try:
        from scripts.build_runtime_index import build_retention_inventory
    except (ModuleNotFoundError, ImportError):
        from build_runtime_index import build_retention_inventory
    inventory = build_retention_inventory(base)
    tiers = inventory.get("retention_tiers", {})
    provenance = inventory.get("r2_provenance", {})
    return {
        "files": inventory.get("files", 0),
        "r1_provenance": tiers.get("R1", {}).get("files", 0),
        "r2_validated": tiers.get("R2", {}).get("files", 0),
        "review_required": provenance.get("review_required", 0),
        "ephemeral_residue": len(inventory.get("ephemeral_residue", [])),
        "duplicate_capacity_signal": inventory.get("potential_duplicate_bytes", 0),
        "metric_boundary": "容量和重复仅是信号；review_required 与 R3 残留是治理问题，不自动授权删除。",
    }


def build_results(base: Path) -> dict:
    snapshots = load_unit_snapshots(base)
    files = [snapshot.path for snapshot in snapshots]
    counts = {
        type_name: sum(snapshot.type_name == type_name for snapshot in snapshots)
        for type_name in discover_unit_types(base)
    }
    required_missing = missing_fields(files, base, REQUIRED_FIELDS)
    recommended_missing = missing_fields(files, base, RECOMMENDED_FIELDS)
    link_issues = markdown_link_issues(base)
    state_conflicts = verification_conflicts(files, base)
    dataflow = dataflow_issues(base)
    duplicate_groups = duplicate_basenames(files, base)
    fm_issues = frontmatter_issues(files, base)
    body_field_issues = body_only_field_issues(files, base)
    type_mismatches = type_mismatch_issues(files, base)
    invalid_enums = invalid_enum_issues(files, base)
    ver_semantic = verification_semantic_issues(files, base)
    rule_auth = rule_authority_check(base)
    disambig = disambiguation_check(files, duplicate_groups, base)
    snapshot_missing = snapshot_disclaimer_check(base)
    chunk_meta = chunk_meta_check(base)
    evidence_ref = evidence_ref_check(files, base)
    source_hash = source_hash_check(base)
    claim_traceability = claim_traceability_check(base)
    relation_traceability = relation_traceability_check(base)
    ver_schema = verification_schema_check(files, base)
    rule_drift = rule_drift_check(base)
    translation_health = translation_health_check(base)
    translation_index_integrity = translation_index_integrity_check(base)
    arch_drift = architecture_drift_check(base, counts)
    relation_health = relation_health_check(base)
    from scripts.build_output_gallery import file_back_health
    output_file_back = file_back_health(base)
    runtime_retention = runtime_artifact_retention_check(base)

    base_type_coverage = sum(1 for type_name in BASE_UNIT_TYPES if counts.get(type_name, 0) > 0)
    active_type_count = base_type_coverage
    total_type_count = len(BASE_UNIT_TYPES)
    deprecated_type_drift = sum(1 for type_name in DEPRECATED_DIRS if counts.get(type_name, 0) > 0)
    structure_node_counts = count_structure_nodes(base)
    structure_node_count = sum(1 for c in structure_node_counts.values() if c > 0)
    hierarchy_assignment = hierarchy_assignment_check(snapshots)

    raw_results = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "rule_authority": rule_auth,
        "summary": {
            "total_units": sum(counts.values()),
            "type_coverage": f"{active_type_count}/{total_type_count}",
            "base_type_coverage": f"{base_type_coverage}/{len(BASE_UNIT_TYPES)}",
            "structure_node_coverage": f"{structure_node_count}/{len(STRUCTURE_DIRS)}",
            "deprecated_type_drift": deprecated_type_drift,
            "hierarchy_version": hierarchy_version(base),
        },
        "structure_node_counts": structure_node_counts,
        "structure_node_type_issues": structure_node_type_issues(base),
        "hierarchy_structure_issues": hierarchy_structure_issues(base),
        "hierarchy_assignment": hierarchy_assignment,
        "counts_by_type": counts,
        "required_field_missing": required_missing,
        "recommended_field_missing": recommended_missing,
        "recommended_field_missing_by_type": missing_fields_by_type(files, RECOMMENDED_FIELDS),
        "frontmatter_missing": fm_issues["frontmatter_missing"],
        "frontmatter_malformed": fm_issues["frontmatter_malformed"],
        "body_only_field_issues": body_field_issues,
        "type_mismatches": type_mismatches,
        "invalid_enums": invalid_enums,
        "verification_semantic_issues": ver_semantic,
        "verification_state_conflicts": state_conflicts,
        "unverified_by_type": unverified_by_type(files, base),
        "migration_todo_sources": migration_todo_sources(files, base),
        "obsidian_syntax": obsidian_syntax(files, base),
        "local_file_issues": local_file_issues(files, base),
        "markdown_link_issues": link_issues,
        "duplicate_basenames": duplicate_groups,
        "disambiguation": disambig,
        "growth_candidate_signals": growth_candidate_signals(base, duplicate_groups),
        "dataflow_issues": dataflow,
        "snapshot_disclaimer_missing": snapshot_missing,
        "current_health_exists": current_health_exists(base),
        "governance_backlog_exists": governance_backlog_exists(base),
        "chunk_meta": chunk_meta,
        "evidence_ref": evidence_ref,
        "claim_traceability": claim_traceability,
        "relation_traceability": relation_traceability,
        "source_hash": source_hash,
        "verification_schema": ver_schema,
        "recall_quality": recall_quality_check(base),
        "semantic_artifact_integrity": semantic_artifact_integrity_check(base),
        "semantic_acceptance": semantic_acceptance_check(base),
        "rule_drift": rule_drift,
        "architecture_drift": arch_drift,
        "translation_health": translation_health,
        "translation_index_integrity": translation_index_integrity,
        "relation_health": relation_health,
        "output_file_back": output_file_back,
        "runtime_artifact_retention": runtime_retention,
    }
    agents_entry = base / "AGENTS.md"
    first_part = agents_entry.is_file() and any(value in read_text(agents_entry) for value in ("当前执行第一部分", "研究尚未执行"))
    accepted_catalog = load_catalog(base) is not None
    raw_results["execution_scope"] = {
        "part": "knowledge" if first_part else "unspecified",
        "hierarchy_assignment": "not_in_current_scope" if first_part else "review_required",
        "knowledge_inputs": "accepted_catalog" if accepted_catalog else "legacy_inventory",
        "processing_inventory_is_research_progress": not accepted_catalog,
    }
    raw_results["structural_health"] = build_structural_health_score(raw_results)
    raw_results["knowledge_structure_quality"] = build_knowledge_structure_quality_score(raw_results)
    raw_results["evidence_quality"] = build_evidence_quality_score(raw_results)
    raw_results["knowledge_maturity"] = knowledge_maturity_check(base, snapshots)
    return raw_results


def print_report(results: dict) -> None:
    summary = results["summary"]
    hs = results["structural_health"]
    kq = results.get("knowledge_structure_quality", {})
    eq = results.get("evidence_quality", {})
    print(f"知识库健康报告 - {results['timestamp']}")
    print(f"结构门禁健康: {hs['total']}/{hs['max_score']} | 知识结构完整性: {kq.get('total', '?')}/{kq.get('max_score', '?')} | 证据链完整性: {eq.get('total', '?')}/{eq.get('max_score', '?')}")
    print(f"  规则权威: {hs['rule_authority']}/20 | Frontmatter: {hs['frontmatter']}/20")
    print(f"  验证语义: {hs['verification_semantics']}/20 | 可追溯性: {hs['traceability']}/15")
    print(f"  数据流: {hs['dataflow']}/10 | 报告时效: {hs['report_freshness']}/10")
    print(f"  工程安全: {hs['engineering_safety']}/5")
    print(f"知识元总数: {summary['total_units']} | 类型覆盖: {summary['type_coverage']} | 基础类型覆盖: {summary['base_type_coverage']} | 层级: {summary['hierarchy_version']}")
    print(f"  结构节点: {summary.get('structure_node_coverage', 'N/A')} | 废弃类型残留: {summary.get('deprecated_type_drift', 'N/A')}")
    hierarchy = results.get("hierarchy_assignment", {})
    print(f"  层级完整挂载: {hierarchy.get('complete_assignments', '?')}/{hierarchy.get('total_units', '?')}")
    ad = results.get('architecture_drift', {})
    if ad.get('hierarchy_has_old_type_refs'):
        print(f"  ⚠️ hierarchy 仍引用旧类型路径")
    if ad.get('hierarchy_has_old_statistics'):
        print(f"  ⚠️ hierarchy 仍包含旧统计数字(758)")
    th = results.get('translation_health', {})
    if th:
        total_persons = th.get('persons', {}).get('total', 0)
        if total_persons:
            no_cov = th['persons']['coverage'].get('name_original', '0/0')
            print(f"  翻译字段: persons name_original={no_cov}")
    print("")

    ra = results["rule_authority"]
    print("规则权威:")
    print(f"  Codex AGENTS 入口: {ra['agents_entry_exists']} | Skill 根: {ra['agents_dir_exists']} | 阶段契约: {ra['pipeline_exists']}")
    print("  Hook: 未配置；权限由实际 Codex 环境控制")
    print(f"  客户端适配问题: {len(ra['adapter_issues'])} ({'✗ 需修复' if ra['adapter_issues'] else '✓ 干净'})")
    for issue in ra["adapter_issues"][:10]:
        print(f"    - {issue}")
    print("")

    print("类型计数:")
    for key, value in results["counts_by_type"].items():
        print(f"  - {key}: {value}")
    print("")

    fm_missing = len(results["frontmatter_missing"])
    fm_malformed = len(results["frontmatter_malformed"])
    print(f"Frontmatter 缺失: {fm_missing} | Frontmatter 格式错误: {fm_malformed}")
    print(f"Frontmatter 必需字段缺失: {sum(len(v) for v in results['required_field_missing'].values())}")
    print(f"正文冒充字段: {len(results['body_only_field_issues'])} ({'✗ 有冒充' if results['body_only_field_issues'] else '✓ 无冒充'})")

    for issue in results.get("body_only_field_issues", []):
        print(f"    {issue['file']}: {', '.join(issue['body_only_fields'])}")
    print("")

    print(f"类型值不匹配: {len(results['type_mismatches'])}")
    for m in results.get("type_mismatches", []):
        print(f"    {m['file']}: dir={m['expected_type']}, frontmatter type={m['actual_type']}")
    print("")

    ie = results["invalid_enums"]
    print(f"非法 confidence 值: {len(ie['invalid_confidence'])} | 非法 consensus 值: {len(ie['invalid_consensus'])}")
    print("")

    vs = results["verification_semantic_issues"]
    print("验证语义问题:")
    print(f"  L7 + high confidence（单源）: {len(vs['l7_high_confidence'])}")
    print(f"  source_count=1 + high confidence: {len(vs['source_count_1_high_confidence'])}")
    print(f"  confirmed 无外部多源: {len(vs['confirmed_without_external_or_multisource'])}")
    print(f"  正文/元数据验证状态矛盾: {len(vs['body_status_frontmatter_conflict'])}")
    print(f"  identity/term 单源越权 externally_verified: {len(vs['identity_only_external_overreach'])}")
    print("")

    print(f"推荐字段缺失: {sum(len(v) for v in results['recommended_field_missing'].values())}")
    print(f"Markdown 断链: {len(results['markdown_link_issues'])}")
    print(f"local_file 问题: {len(results['local_file_issues'])}")
    print(f"同名跨类型组: {len(results['duplicate_basenames'])}")
    da = results["disambiguation"]
    print(f"  有消歧说明: {da['duplicates_with_disambiguation']} | 无消歧说明: {da['duplicates_without_disambiguation']}")
    print(f"UNVERIFIED: {sum(len(v) for v in results['unverified_by_type'].values())}")
    print(f"MIGRATION_TODO: {len(results['migration_todo_sources'])}")
    print(f"数据流问题: {len(results['dataflow_issues'])}")

    cm = results["chunk_meta"]
    print(f"Chunk 元数据: 总计 {cm['total_chunks']}, 缺 meta.json {cm['chunk_meta_missing']}")
    er = results["evidence_ref"]
    total_er = er["sources_with_evidence_ref"] + er["sources_without_evidence_ref"]
    print(f"证据引用: {er['sources_with_evidence_ref']}/{total_er} (可解析: {er['evidence_ref_resolvable']})")
    sh = results["source_hash"]
    print(f"来源哈希: 总计 {sh['total_sources']}, 缺 hash {sh['source_hash_missing']}")
    print(f"快照声明缺失: {len(results['snapshot_disclaimer_missing'])} | current-health: {'✓' if results['current_health_exists'] else '✗'} | governance-backlog: {'✓' if results['governance_backlog_exists'] else '✗'}")
    print(f"验证状态矛盾: {len(results['verification_state_conflicts'])}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Codex-only 知识库健康检查 v2.0")
    parser.add_argument("--base-path", default=".", help="项目根目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--summary", action="store_true", help="仅输出摘要 JSON")
    args = parser.parse_args()
    base = Path(args.base_path).resolve()
    results = build_results(base)
    if args.summary:
        summary_out = {
            "structural_health": results["structural_health"],
            "knowledge_maturity": results["knowledge_maturity"],
            "summary": results["summary"],
            "rule_authority": results["rule_authority"],
            "verification_semantic_issues": results["verification_semantic_issues"],
        }
        print(json.dumps(summary_out, ensure_ascii=False, indent=2))
    elif args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_report(results)


if __name__ == "__main__":
    main()
