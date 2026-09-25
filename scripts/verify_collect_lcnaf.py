#!/usr/bin/env python3
"""Collect LC/NACO name-authority evidence for person and institution KUs.

The collector is read-only with respect to knowledge units. It emits evidence
JSONL for later Agent review and ``verify_apply_evidence.py`` processing.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

try:
    from scripts import _collect_common as common
except ModuleNotFoundError:
    import _collect_common as common


SUGGEST_API = "https://id.loc.gov/authorities/names/suggest2/"
MAX_CANDIDATES = 10
QUALITY_RANK = {"none": 0, "weak": 1, "medium": 2, "strong": 3}
TYPE_ALIASES = {"persons": "person", "institutions": "institution"}
EXPECTED_RDF_TYPES = {"person": "PersonalName", "institution": "CorporateName"}


def normalize_text(value: str) -> str:
    """LCNAF 名称匹配需忽略年份（如 Smith, John 1960-2020）。"""
    decomposed = unicodedata.normalize("NFKD", value or "")
    asciiish = "".join(char for char in decomposed if not unicodedata.combining(char))
    asciiish = re.sub(r"\b(?:1[0-9]{3}|20[0-9]{2})\b", " ", asciiish.lower())
    asciiish = re.sub(r"[^a-z0-9]+", " ", asciiish)
    return re.sub(r"\s+", " ", asciiish).strip()


def tokens(value: str, ku_type: str) -> set[str]:
    result = set(normalize_text(value).split())
    if ku_type == "institution":
        result -= {"the", "and", "co", "company", "inc", "incorporated", "ltd", "limited"}
    return result


def name_score(query: str, candidate: str, ku_type: str) -> float:
    query_tokens = tokens(query, ku_type)
    candidate_tokens = tokens(candidate, ku_type)
    if not query_tokens or not candidate_tokens:
        return 0.0
    if query_tokens == candidate_tokens:
        return 1.0
    return round(len(query_tokens & candidate_tokens) / max(len(query_tokens), len(candidate_tokens)), 3)


def candidate_labels(hit: dict) -> list[str]:
    label = str(hit.get("suggestLabel") or hit.get("aLabel") or "")
    labels = [label]
    if " (USE " in label:
        labels.append(label.split(" (USE ", 1)[0])
        labels.append(label.split(" (USE ", 1)[1].rstrip(")"))
    more = hit.get("more") if isinstance(hit.get("more"), dict) else {}
    for key in ("variantLabels", "authorizedNNs"):
        value = more.get(key) or []
        if isinstance(value, list):
            labels.extend(str(item) for item in value if item)
    return list(dict.fromkeys(item for item in labels if item))


def is_type_compatible(hit: dict, ku_type: str) -> bool:
    expected = EXPECTED_RDF_TYPES.get(ku_type)
    more = hit.get("more") if isinstance(hit.get("more"), dict) else {}
    rdf_types = set(more.get("rdftypes") or [])
    return bool(expected and expected in rdf_types)


def verified_fields(hit: dict, ku_type: str) -> list[str]:
    more = hit.get("more") if isinstance(hit.get("more"), dict) else {}
    fields = ["authority_heading", "entity_type"]
    mapping = {
        "variantLabels": "variant_name",
        "birthdates": "birth_date",
        "deathdates": "death_date",
        "occupations": "occupation",
        "activityfields": "activity_field",
        "locales": "associated_place",
        "sources": "authority_source_note",
    }
    for key, field in mapping.items():
        if more.get(key):
            fields.append(field)
    if ku_type == "institution" and "CorporateName" in set(more.get("rdftypes") or []):
        fields.append("corporate_identity")
    return fields


def quality_for_score(score: float) -> str:
    if score >= 0.82:
        return "strong"
    if score >= 0.6:
        return "medium"
    if score > 0:
        return "weak"
    return "none"


def evaluate_candidates(query: str, ku_type: str, hits: list[dict]) -> tuple[dict | None, list[dict], str | None]:
    evaluated: list[dict] = []
    for rank, hit in enumerate(hits, start=1):
        compatible = is_type_compatible(hit, ku_type)
        labels = candidate_labels(hit)
        score = max((name_score(query, label, ku_type) for label in labels), default=0.0)
        quality = quality_for_score(score) if compatible else "none"
        evaluated.append(
            {
                "candidate_rank": rank,
                "label": str(hit.get("suggestLabel") or ""),
                "uri": str(hit.get("uri") or "").replace("http://", "https://", 1),
                "type_compatible": compatible,
                "match_quality": quality,
                "match_score": score,
                "verified_fields": verified_fields(hit, ku_type) if compatible else [],
                "authority_metadata": hit.get("more") if isinstance(hit.get("more"), dict) else {},
            }
        )
    ranked = sorted(
        evaluated,
        key=lambda row: (-QUALITY_RANK[row["match_quality"]], -row["match_score"], row["candidate_rank"]),
    )
    if not hits:
        return None, evaluated, "no_search_results"
    compatible = [row for row in ranked if row["type_compatible"]]
    if not compatible:
        return None, evaluated, "no_type_compatible_candidate"
    best = compatible[0]
    if best["match_quality"] in {"none", "weak"}:
        return best, evaluated, "weak_name_match"
    tied = [
        row
        for row in compatible[1:]
        if row["match_quality"] == "strong"
        and best["match_quality"] == "strong"
        and abs(row["match_score"] - best["match_score"]) < 0.04
        and row["uri"] != best["uri"]
    ]
    if tied:
        return best, evaluated, "ambiguous_authority_heading"
    return best, evaluated, None


def basic_fact_scope(ku_type: str, fields: list[str], quality: str) -> bool:
    if ku_type != "person" or quality != "strong":
        return False
    groups = [
        {"birth_date", "death_date"},
        {"occupation", "activity_field"},
        {"associated_place"},
    ]
    return sum(bool(set(fields) & group) for group in groups) >= 2


class LcnafAdapter(common.Adapter):
    name = "LCNAF"
    description = "通过 LC/NACO 名称规范档收集 person/institution 的身份证据。"
    type_aliases = TYPE_ALIASES

    def accepts(self, ku_type: str) -> bool:
        return ku_type in EXPECTED_RDF_TYPES

    def search(self, label: str, ku_type: str, fm: str, path: Path) -> tuple[dict | None, dict | None]:
        params = {"q": label, "count": MAX_CANDIDATES}
        if ku_type == "person":
            params["searchtype"] = "keyword"
        return common.request_json(SUGGEST_API, params, stage="search")

    def evaluate(self, label: str, ku_type: str, fm: str, path: Path, payload: dict | None) -> tuple[dict | None, list[dict], str | None]:
        hits = payload.get("hits") if isinstance(payload, dict) and isinstance(payload.get("hits"), list) else []
        return evaluate_candidates(label, ku_type, hits)

    def build_evidence(self, path, ku_type, label, fm, best, candidates, blocking_reason, payload, collection_error):
        fields = best.get("verified_fields", []) if best else []
        quality = best.get("match_quality", "none") if best else "none"
        scope = "basic_fact" if basic_fact_scope(ku_type, fields, quality) else "entity_identity_only"
        recommended: dict = {}
        if not blocking_reason and quality in {"strong", "medium"}:
            recommended = {
                "evidence_status": "externally_verified" if scope == "basic_fact" else "partially_verified",
                "verification_level": "L6",
                "confidence": "medium",
                "consensus": "tentative",
            }
        return {
            "ku_path": path.relative_to(common.BASE).as_posix(),
            "platform": "Library of Congress Name Authority File",
            "source_type": "library_authority_api",
            "source_authority": "national_library_authority",
            "source_independence_group": "lc_naf",
            "url": best.get("uri", "") if best else "",
            "claim_scope": scope,
            "claim_target": "identity_and_type_fields" if scope == "basic_fact" else "name_en",
            "match_quality": quality,
            "match_score": best.get("match_score", 0.0) if best else 0.0,
            "verified_fields": fields,
            "conflicting_fields": [],
            "candidate_rank": best.get("candidate_rank", 0) if best else 0,
            "candidate_count": payload.get("count", len(candidates)) if isinstance(payload, dict) else 0,
            "returned_candidate_count": len(candidates),
            "authority_label": best.get("label", "") if best else "",
            "candidates": candidates,
            "collection_error": collection_error,
            "blocking_reason": blocking_reason,
            "recommended_changes": recommended,
            "notes": (
                "LC/NACO authority evidence is limited to identity and recorded authority metadata; "
                "it does not validate contribution, authorship, or domain-relevance claims."
            ),
        }


def main() -> int:
    return common.run(LcnafAdapter())


if __name__ == "__main__":
    raise SystemExit(main())
