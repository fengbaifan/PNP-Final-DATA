#!/usr/bin/env python3
"""关系表读取：relations.csv 是关系唯一源，本模块提供 relation-index.yml 兼容读取。

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
    "rejected": "conflict",
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
        return []
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    edges: list[dict] = []
    for r in rows:
        subj = r.get("subject_ku_id", "")
        obj = r.get("object_ku_id", "")
        pred = r.get("predicate", "")
        status = r.get("status", "formal")
        edges.append({
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
            "relation_source": "explicit" if r.get("origin") != "inferred" else "inferred_by_rule",
            "evidence_ref": {
                "doc_id": r.get("evidence_doc_id", "") or "",
                "source_file": r.get("evidence_source_file", "") or "",
                "source_span": r.get("evidence_span", "") or "",
            },
            "note": "",
            "evidence": "",
            "claim_id": None,
            "confidence": "medium",
            "bidirectional_required": False,
        })
    return edges
