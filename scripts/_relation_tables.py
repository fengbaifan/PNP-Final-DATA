#!/usr/bin/env python3
"""关系表读取：relations.csv 是关系唯一源，本模块提供兼容读取。

脚本只改「读入」这一处：把 relations.csv 读成 relation-index.yml 兼容的边列表，
其余字段用默认值补齐，避免下游脚本逐处改字段名。
"""
from __future__ import annotations

import csv
from pathlib import Path

try:
    from scripts._relation_schema import INVERSE_MAP
except ModuleNotFoundError:
    from _relation_schema import INVERSE_MAP

BASE = Path(__file__).resolve().parents[1]
RELATIONS_CSV = BASE / "04-knowledge" / "tables" / "relations.csv"

TYPE_SINGULAR = {
    "persons": "person", "families": "family", "institutions": "institution",
    "places": "place", "works": "work", "archives": "archive",
    "terms": "term", "procedures": "procedure", "events": "event",
}
REVIEW_STATUS = {
    "formal": "evidence_backed_relation",
    "pending": "needs_evidence",
    "rejected": "rejected_relation",
}


def _idx_style(ku_id: str) -> str:
    """units/persons/xxx -> persons/xxx.md"""
    p = ku_id[len("units/"):] if ku_id.startswith("units/") else ku_id
    return p + ".md"


def _type_of(ku_id: str) -> str:
    parts = ku_id.split("/")
    return TYPE_SINGULAR.get(parts[1] if len(parts) >= 2 else "", "")


def load_relations(path: Path | None = None) -> list[dict]:
    path = path or RELATIONS_CSV
    if not path.exists():
        raise FileNotFoundError(f"authoritative relation table not found: {path}")
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"relation_id", "subject_ku_id", "object_ku_id", "predicate", "status", "origin",
                    "source_id", "source_file", "source_span"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"relations.csv missing required columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    edges: list[dict] = []
    for r in rows:
        subj = r.get("subject_ku_id", "")
        obj = r.get("object_ku_id", "")
        pred = r.get("predicate", "")
        status = r.get("status", "")
        if status not in REVIEW_STATUS:
            raise ValueError(f"{r.get('relation_id') or '<unknown>'}: unsupported relation status {status!r}")
        evidence_ref = {
            "doc_id": r.get("source_id", "") or "",
            "source_file": r.get("source_file", "") or "",
            "source_span": r.get("source_span", "") or "",
        }
        edges.append({
            "relation_id": r.get("relation_id", "") or "",
            "source": _idx_style(subj),
            "target": _idx_style(obj),
            "source_type": _type_of(subj),
            "target_type": _type_of(obj),
            "relation_type": pred,
            "inverse_relation_type": INVERSE_MAP.get(pred),
            "time": r.get("time", "") or "",
            "role": r.get("role", "") or "",
            "scope": r.get("scope", "") or "",
            "review_status": REVIEW_STATUS.get(status, "evidence_backed_relation"),
            "relation_source": "inferred_by_rule" if r.get("origin") == "inferred" else "explicit",
            "evidence_ref": evidence_ref if any(evidence_ref.values()) else None,
            "note": r.get("note", "") or "",
            "evidence": "",
            "claim_id": None,
            "confidence": "medium",
            "bidirectional_required": False,
        })
    return edges
