#!/usr/bin/env python3
"""Collect LC/NACO name-authority evidence for person and institution KUs.

The collector is read-only with respect to knowledge units. It emits evidence
JSONL for later Agent review and ``verify_apply_evidence.py`` processing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

try:
    from scripts._verification_targets import load_result_targets, resolve, resolve_single_target, write_jsonl
except ModuleNotFoundError:
    from _verification_targets import load_result_targets, resolve, resolve_single_target, write_jsonl


BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
SUGGEST_API = "https://id.loc.gov/authorities/names/suggest2/"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Infographic-Knowledge-Distillation/5.3",
}
HTTP_TIMEOUT = 20
MAX_API_RETRIES = 2
REQUEST_DELAY = 0.15
MAX_CANDIDATES = 10
QUALITY_RANK = {"none": 0, "weak": 1, "medium": 2, "strong": 3}
TYPE_ALIASES = {"persons": "person", "institutions": "institution"}
EXPECTED_RDF_TYPES = {"person": "PersonalName", "institution": "CorporateName"}


def extract_frontmatter(text: str) -> str:
    match = re.search(r"^\ufeff?---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    return match.group(1).strip("\n") if match else ""


def scalar_fm(fm: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    return match.group(1).strip().strip('"').strip("'") if match else ""


def normalize_text(value: str) -> str:
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


def request_suggestions(query: str, ku_type: str) -> tuple[dict | None, dict | None]:
    if not requests:
        return None, {
            "stage": "search",
            "error_type": "missing_dependency",
            "attempts": 0,
            "retryable": False,
        }
    params = {"q": query, "count": MAX_CANDIDATES}
    if ku_type == "person":
        params["searchtype"] = "keyword"
    last_error: dict | None = None
    for attempt in range(1, MAX_API_RETRIES + 2):
        try:
            response = requests.get(SUGGEST_API, params=params, headers=HEADERS, timeout=HTTP_TIMEOUT)
            if response.status_code == 200:
                return response.json(), None
            retryable = response.status_code == 429 or response.status_code >= 500
            last_error = {
                "stage": "search",
                "error_type": "http_error",
                "http_status": response.status_code,
                "attempts": attempt,
                "retryable": retryable,
            }
            if not retryable or attempt > MAX_API_RETRIES:
                break
        except Exception as exc:
            last_error = {
                "stage": "search",
                "error_type": type(exc).__name__,
                "message": str(exc)[:300],
                "attempts": attempt,
                "retryable": True,
            }
            if attempt > MAX_API_RETRIES:
                break
        time.sleep(min(2 ** (attempt - 1), 4))
    return None, last_error


def collect_one(ku_path: Path, verbose: bool = False) -> dict | None:
    fm = extract_frontmatter(ku_path.read_text(encoding="utf-8"))
    if not fm:
        return None
    ku_type = scalar_fm(fm, "type").lower() or TYPE_ALIASES.get(ku_path.parent.name, "")
    if ku_type not in EXPECTED_RDF_TYPES:
        raise ValueError(f"LCNAF collector 只接受 person/institution：{ku_path}")
    query = scalar_fm(fm, "name_en") or scalar_fm(fm, "name_original") or scalar_fm(fm, "title")
    rel = ku_path.relative_to(BASE).as_posix()
    payload, collection_error = request_suggestions(query, ku_type)
    hits = payload.get("hits") if isinstance(payload, dict) and isinstance(payload.get("hits"), list) else []
    best, candidates, blocking_reason = evaluate_candidates(query, ku_type, hits)
    if collection_error:
        blocking_reason = "api_error"
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
    evidence = {
        "ku_path": rel,
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
        "candidate_count": payload.get("count", len(hits)) if isinstance(payload, dict) else 0,
        "returned_candidate_count": len(hits),
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
    if verbose:
        print(
            f"[{ku_type}] {query}: {quality} {blocking_reason or 'candidate'} "
            f"{evidence['authority_label']}",
            file=sys.stderr,
        )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--ku", help="指定知识元文件名或 slug")
    scope.add_argument("--input-result", type=Path, help="读取包含 targets 的批次规划 JSON")
    parser.add_argument("--checkpoint", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.checkpoint and not args.input_result:
        parser.error("--checkpoint 只能与 --input-result 一起使用")
    if args.ku:
        target = resolve_single_target(args.ku, UNITS)
        if not target:
            parser.error(f"未找到 KU：{args.ku}")
        files = [target]
    else:
        files = load_result_targets(resolve(args.input_result, BASE), BASE, UNITS, args.checkpoint)
    invalid = [path for path in files if path.parent.name not in TYPE_ALIASES]
    if invalid:
        parser.error(f"LCNAF collector 收到非人物/机构目标：{invalid[0]}")
    if args.dry_run:
        print(f"targets={len(files)} checkpoint={args.checkpoint or 'all'} output={args.output}")
        return 0
    rows: list[dict] = []
    for path in files:
        evidence = collect_one(path, verbose=args.verbose)
        if evidence:
            rows.append(evidence)
        time.sleep(REQUEST_DELAY)
    output = resolve(args.output, BASE)
    write_jsonl(rows, output)
    print(f"evidence={output.relative_to(BASE) if output.is_relative_to(BASE) else output}")
    print(f"rows={len(rows)}")
    print(f"blocked={sum(bool(row.get('blocking_reason')) for row in rows)}")
    print(f"basic_fact={sum(row.get('claim_scope') == 'basic_fact' for row in rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
