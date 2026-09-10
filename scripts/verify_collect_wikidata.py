#!/usr/bin/env python3
"""
verify_collect_wikidata.py — Wikidata 证据收集器（阶段1）
=========================================================
通过 Wikidata API 收集结构化证据，生成 evidence JSONL。
不直接修改知识元。证据需经 verify_apply_evidence.py 审核后写回。

验证策略：
1. 读取知识元 frontmatter 中的 name_en、type、title
2. 调用 wbsearchentities 搜索，输出 top 5 candidates
3. 对每个 candidate 获取 QID entity data
4. 检查 instance_of / occupation / birth/death / aliases
5. 计算 match_quality: strong / medium / weak
6. 只输出 evidence JSONL，不修改知识元

用法：
  python scripts/verify_collect_wikidata.py --ku jo-mora          # 验证单个
  python scripts/verify_collect_wikidata.py --ku jo-mora --verbose # 详细输出
  python scripts/verify_collect_wikidata.py --limit 5             # 批量前5个
  python scripts/verify_collect_wikidata.py --dry-run             # 仅预览
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

try:
    from scripts._verification_targets import (
        load_evidence_targets,
        load_result_targets,
        resolve,
        resolve_single_target,
        write_jsonl,
    )
except ModuleNotFoundError:
    from _verification_targets import (
        load_evidence_targets,
        load_result_targets,
        resolve,
        resolve_single_target,
        write_jsonl,
    )

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_ENTITY = "https://www.wikidata.org/wiki/Special:EntityData"
REQUEST_DELAY = 0.5
REQUEST_TIMEOUT = 10
MAX_API_RETRIES = 2
MIN_REQUEST_INTERVAL = 1.0
BASE_RETRY_DELAY = 5.0
MAX_RETRY_DELAY = 15.0
RETRYABLE_HTTP_STATUS = {429, 500, 502, 503, 504}
HEADERS = {"User-Agent": "Knowledge-Distillation/1.0"}
_last_request_started = 0.0
TYPE_QID_MAP = {
    "person": "Q5",
    "work": "Q386724",
    "place": "Q618123",
}

LIMITED_SCOPES = {
    "entity_identity_only",
    "term_existence",
    "event_identity_only",
    "bibliographic_hint",
}


def _extract_field_names(matched_fields: list) -> list[str]:
    result = []
    for m in matched_fields:
        if isinstance(m, dict):
            result.append(m.get("field", ""))
        else:
            result.append(str(m))
    return result


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_frontmatter(text: str) -> str:
    match = re.search(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    return match.group(1).strip("\n") if match else ""


def scalar_fm(fm: str, field: str) -> str:
    m = re.search(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def _error_kind(exc: Exception) -> tuple[str, bool]:
    name = type(exc).__name__.lower()
    if "timeout" in name:
        return "timeout", True
    if "connection" in name:
        return "connection_error", True
    return "request_error", False


def _retry_delay(response, attempt: int) -> float:
    headers = getattr(response, "headers", {}) or {}
    raw = headers.get("Retry-After")
    try:
        return min(MAX_RETRY_DELAY, max(0.0, float(raw)))
    except (TypeError, ValueError):
        return min(MAX_RETRY_DELAY, BASE_RETRY_DELAY * (2 ** (attempt - 1)))


def _throttle_requests() -> None:
    """Keep request starts below the observed Wikidata burst limit."""
    global _last_request_started
    now = time.monotonic()
    remaining = MIN_REQUEST_INTERVAL - (now - _last_request_started)
    if remaining > 0:
        time.sleep(remaining)
    _last_request_started = time.monotonic()


def request_json(url: str, *, stage: str, params: dict | None = None) -> tuple[dict | None, dict | None]:
    """Fetch one JSON object with bounded retry and non-sensitive errors."""
    if not requests:
        return None, {
            "stage": stage,
            "kind": "requests_unavailable",
            "http_status": None,
            "attempts": 0,
            "retryable": False,
        }

    total_attempts = MAX_API_RETRIES + 1
    for attempt in range(1, total_attempts + 1):
        response = None
        try:
            _throttle_requests()
            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            status = int(getattr(response, "status_code", 200))
            if status in RETRYABLE_HTTP_STATUS:
                if attempt < total_attempts:
                    time.sleep(_retry_delay(response, attempt))
                    continue
                return None, {
                    "stage": stage,
                    "kind": "rate_limited" if status == 429 else "http_retry_exhausted",
                    "http_status": status,
                    "attempts": attempt,
                    "retryable": True,
                }
            if status >= 400:
                return None, {
                    "stage": stage,
                    "kind": "http_error",
                    "http_status": status,
                    "attempts": attempt,
                    "retryable": False,
                }
            data = response.json()
            if not isinstance(data, dict):
                return None, {
                    "stage": stage,
                    "kind": "invalid_payload",
                    "http_status": status,
                    "attempts": attempt,
                    "retryable": False,
                }
            return data, None
        except Exception as exc:
            kind, retryable = _error_kind(exc)
            if retryable and attempt < total_attempts:
                time.sleep(min(MAX_RETRY_DELAY, BASE_RETRY_DELAY * (2 ** (attempt - 1))))
                continue
            status = getattr(getattr(exc, "response", None), "status_code", None)
            return None, {
                "stage": stage,
                "kind": kind,
                "http_status": status,
                "attempts": attempt,
                "retryable": retryable,
            }

    raise AssertionError("unreachable")


def search_wikidata(query: str, lang: str = "en") -> list[dict]:
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": lang,
        "format": "json",
        "limit": 5,
    }
    data, error = request_json(WIKIDATA_API, stage="search", params=params)
    if error:
        return [{"error": error}]
    search = data.get("search", []) if data else []
    return search if isinstance(search, list) else [{"error": {
        "stage": "search",
        "kind": "invalid_payload",
        "http_status": None,
        "attempts": 1,
        "retryable": False,
    }}]


def get_entities(qids: list[str], lang: str = "en") -> dict:
    unique_qids = list(dict.fromkeys(qid for qid in qids if qid))
    if not unique_qids:
        return {}
    params = {
        "action": "wbgetentities",
        "ids": "|".join(unique_qids),
        "props": "labels|aliases|claims|descriptions",
        "languages": lang,
        "languagefallback": 1,
        "format": "json",
    }
    data, error = request_json(WIKIDATA_API, stage="entity_batch", params=params)
    if error:
        return {"__error__": error}
    entities = data.get("entities", {}) if data else {}
    if not isinstance(entities, dict):
        return {"__error__": {
            "stage": "entity_batch",
            "kind": "invalid_payload",
            "http_status": None,
            "attempts": 1,
            "retryable": False,
        }}
    return entities


def get_entity(qid: str) -> dict:
    """Compatibility helper; batch collection uses get_entities()."""
    entities = get_entities([qid])
    if "__error__" in entities:
        return {"error": entities["__error__"]}
    return entities.get(qid, {})


def get_label(entity: dict, lang: str = "en") -> str:
    return entity.get("labels", {}).get(lang, {}).get("value", "")


def get_aliases(entity: dict, lang: str = "en") -> list[str]:
    return [a["value"] for a in entity.get("aliases", {}).get(lang, [])]


def get_claims(entity: dict, pid: str) -> list[dict]:
    return entity.get("claims", {}).get(pid, [])


def extract_year(s: str) -> int | None:
    m = re.search(r"(\d{4})", s)
    return int(m.group(1)) if m else None


def match_person(entity: dict, ku_name_en: str) -> tuple[int, int, list[dict]]:
    score, max_score, matched = 0, 0, []
    # P0-3: field-level pass/fail — only fail if ALL claims fail for a field
    max_score += 1
    p31_claims = get_claims(entity, "P31")
    if any(c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "") == "Q5" for c in p31_claims):
        score += 1
        matched.append({"field": "instance_of", "expected": "person (Q5)", "actual": "human (Q5)", "result": "pass"})
    else:
        non_human = [c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "") for c in p31_claims]
        matched.append({"field": "instance_of", "expected": "person (Q5)", "actual": str(non_human) if non_human else "none", "result": "fail" if p31_claims else "none"})
    max_score += 1
    occupation_claims = get_claims(entity, "P106")
    artist_qids = {
        "Q483501": "artist", "Q3391743": "painter", "Q1028181": "cartoonist",
        "Q644687": "illustrator", "Q1281618": "sculptor", "Q215627": "writer",
        "Q36180": "photographer", "Q49757": "historian", "Q205375": "designer", "Q486748": "architect",
    }
    found_occ = None
    for c in occupation_claims:
        qid = c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
        if qid in artist_qids:
            found_occ = artist_qids[qid]
            break
    if found_occ:
        score += 1
        matched.append({"field": "occupation", "expected": "creative", "actual": found_occ, "result": "pass"})
    else:
        matched.append({"field": "occupation", "expected": "creative", "actual": "not found" if not occupation_claims else "no artist QID", "result": "fail" if occupation_claims else "none"})
    max_score += 2
    for pid, label in [("P569", "birth_date"), ("P570", "death_date")]:
        claims = get_claims(entity, pid)
        if any(c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "") for c in claims):
            score += 1
            matched.append({"field": label, "expected": "date", "actual": "found", "result": "pass"})
        else:
            matched.append({"field": label, "expected": "date", "actual": "not found", "result": "none"})
    return score, max_score, matched


def match_place(entity: dict, ku_name_en: str) -> tuple[int, int, list[dict]]:
    score, max_score, matched = 0, 0, []
    place_qids = {"Q618123", "Q515", "Q486972", "Q3957", "Q16521"}
    max_score += 1
    p31_claims = get_claims(entity, "P31")
    if any(c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "") in place_qids for c in p31_claims):
        score += 1
        matched.append({"field": "instance_of", "expected": "place", "actual": "found", "result": "pass"})
    else:
        matched.append({"field": "instance_of", "expected": "place", "actual": "not found", "result": "fail" if p31_claims else "none"})
    max_score += 1
    if get_claims(entity, "P17"):
        score += 1
        matched.append({"field": "country", "expected": "present", "actual": "found", "result": "pass"})
    else:
        matched.append({"field": "country", "expected": "present", "actual": "not found", "result": "none"})
    return score, max_score, matched


def match_archive(entity: dict, ku_name_en: str) -> tuple[int, int, list[dict]]:
    # Published bibliography is one subset of archive; an unknown P31 is not a type conflict.
    score, max_score, matched = 0, 0, []
    pub_qids = {"Q571": "book", "Q191067": "article", "Q1002697": "journal", "Q7318358": "review",
                "Q49848": "periodical", "Q7377": "newspaper", "Q5292": "encyclopedia",
                "Q3331189": "edition", "Q11032": "serial"}
    max_score += 1
    p31_claims = get_claims(entity, "P31")
    found_pub = None
    for c in p31_claims:
        qid = c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
        if qid in pub_qids:
            found_pub = pub_qids[qid]
            break
    if found_pub:
        score += 1
        matched.append({"field": "instance_of", "expected": "archive", "actual": found_pub, "result": "pass"})
    else:
        matched.append({"field": "instance_of", "expected": "archive", "actual": "unclassified_document", "result": "none"})
    max_score += 1
    if get_claims(entity, "P50") or get_claims(entity, "P577") or get_claims(entity, "P123"):
        score += 1
        matched.append({"field": "author_or_date_or_publisher", "expected": "present", "actual": "found", "result": "pass"})
    else:
        matched.append({"field": "author_or_date_or_publisher", "expected": "present", "actual": "not found", "result": "none"})
    return score, max_score, matched


def match_work(entity: dict, ku_name_en: str) -> tuple[int, int, list[dict]]:
    score, max_score, matched = 0, 0, []
    work_qids = {"Q386724": "work", "Q838948": "artwork", "Q4502142": "map", "Q17489659": "visual artwork",
                 "Q51790": "book"}
    max_score += 1
    p31_claims = get_claims(entity, "P31")
    found_work = None
    for c in p31_claims:
        qid = c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
        if qid in work_qids:
            found_work = work_qids[qid]
            break
    if found_work:
        score += 1
        matched.append({"field": "instance_of", "expected": "work", "actual": found_work, "result": "pass"})
    else:
        matched.append({"field": "instance_of", "expected": "work", "actual": "not found", "result": "fail" if p31_claims else "none"})
    max_score += 1
    if get_claims(entity, "P170") or get_claims(entity, "P571") or get_claims(entity, "P195"):
        score += 1
        matched.append({"field": "creator_or_date_or_collection", "expected": "present", "actual": "found", "result": "pass"})
    else:
        matched.append({"field": "creator_or_date_or_collection", "expected": "present", "actual": "not found", "result": "none"})
    return score, max_score, matched


def match_generic_entity(entity: dict, ku_name_en: str) -> tuple[int, int, list[dict]]:
    score, max_score, matched = 0, 0, []
    max_score += 1
    has_parent = bool(get_claims(entity, "P279"))
    has_instance = bool(get_claims(entity, "P31"))
    has_desc_source = bool(get_claims(entity, "P1343"))
    if has_parent:
        score += 1
        matched.append({"field": "subclass_of (P279)", "expected": "present", "actual": "found", "result": "pass"})
    elif has_instance:
        score += 1
        matched.append({"field": "instance_of (P31)", "expected": "present", "actual": "found", "result": "pass"})
    else:
        matched.append({"field": "subclass_of or instance_of", "expected": "present", "actual": "not found", "result": "none"})
    max_score += 1
    if has_desc_source:
        score += 1
        matched.append({"field": "described_by_source (P1343)", "expected": "present", "actual": "found", "result": "pass"})
    else:
        matched.append({"field": "described_by_source (P1343)", "expected": "present", "actual": "not found", "result": "none"})
    return score, max_score, matched


def match_concept_entity(entity: dict, ku_name_en: str) -> tuple[int, int, list[dict]]:
    """Score term/procedure candidates without treating any P31 as a concept.

    Creative works, software, surnames and episodes often share exact labels
    with concepts.  A bare ``instance of`` claim is therefore not positive
    term identity evidence; P279 or a described-by-source claim is required.
    """
    score, max_score, matched = 0, 0, []
    max_score += 1
    has_parent = bool(get_claims(entity, "P279"))
    has_instance = bool(get_claims(entity, "P31"))
    if has_parent:
        score += 1
        matched.append({"field": "subclass_of (P279)", "expected": "concept hierarchy", "actual": "found", "result": "pass"})
    elif has_instance:
        matched.append({
            "field": "instance_of_only (P31)",
            "expected": "concept hierarchy or independent description",
            "actual": "instance claim only",
            "result": "none",
        })
    else:
        matched.append({
            "field": "concept_model",
            "expected": "subclass or instance claim",
            "actual": "not found",
            "result": "none",
        })

    max_score += 1
    if get_claims(entity, "P1343"):
        score += 1
        matched.append({"field": "described_by_source (P1343)", "expected": "present", "actual": "found", "result": "pass"})
    else:
        matched.append({"field": "described_by_source (P1343)", "expected": "present", "actual": "not found", "result": "none"})
    return score, max_score, matched


def match_family(entity: dict, ku_name_en: str) -> tuple[int, int, list[dict]]:
    """Collect a candidate without certifying kinship from a label or generic P31."""
    return 0, 1, [{
        "field": "family_identity",
        "expected": "source-backed family or branch, not surname, person or household",
        "actual": "requires semantic comparison of candidate and source context",
        "result": "none",
    }]


TYPE_MATCHER = {
    "person": match_person,
    "family": match_family,
    "institution": match_generic_entity,
    "place": match_place,
    "archive": match_archive,
    "work": match_work,
    "term": match_concept_entity,
    "procedure": match_concept_entity,
    "event": match_generic_entity,
}


def infer_claim_scope(ku_type: str, quality: str) -> str:
    if ku_type in {"term", "procedure"}:
        return "term_existence"
    if ku_type == "event":
        return "event_identity_only"
    if ku_type == "archive" and quality == "strong":
        return "bibliographic_fact"
    if ku_type in {"person", "institution", "place", "work"} and quality == "strong":
        return "basic_fact"
    if ku_type == "archive":
        return "bibliographic_hint"
    return "entity_identity_only"


def infer_claim_target(ku_type: str, claim_scope: str) -> str:
    if claim_scope == "basic_fact":
        return "identity_and_type_fields"
    if claim_scope == "bibliographic_fact":
        return "bibliographic_metadata"
    if ku_type in {"term", "procedure"}:
        return "term"
    if ku_type == "event":
        return "event_name"
    return "name_en"


def conflicting_fields(matched_fields: list[dict]) -> list[dict]:
    return [m for m in matched_fields if isinstance(m, dict) and m.get("result") == "fail"]


def match_has_api_error(best_match: dict | None) -> bool:
    if not best_match:
        return False
    fields = best_match.get("matched_fields") or []
    return any(field == "api_error" or (isinstance(field, dict) and field.get("field") == "api_error") for field in fields)


def match_score(candidate: dict, entity: dict, ku_name_en: str, ku_type: str) -> tuple[str, float, list[str]]:
    if "error" in candidate or "error" in entity:
        return "weak", 0.0, ["api_error"]

    match_text = get_label(entity).lower()
    aliases = [a.lower() for a in get_aliases(entity)]
    query_lower = ku_name_en.lower().strip()

    # ── P0-2: label/alias match is a mandatory threshold ──
    label_or_alias_match = False
    if query_lower == match_text:
        label_or_alias_match = True
    elif any(query_lower == a for a in aliases):
        label_or_alias_match = True
    # Additional fuzzy match: normalized title (remove parenthetical, strip)
    elif re.sub(r"\s*\([^)]*\)", "", query_lower).strip() == re.sub(r"\s*\([^)]*\)", "", match_text).strip():
        label_or_alias_match = True
    # High symmetric token overlap.  Query-only coverage allowed a generic term
    # such as "Anatomical Visualization" to match a much longer article title.
    elif query_lower and match_text:
        query_tokens = set(query_lower.split())
        label_tokens = set(match_text.split())
        union = query_tokens | label_tokens
        if union and len(query_tokens & label_tokens) / len(union) >= 0.8:
            label_or_alias_match = True

    matcher = TYPE_MATCHER.get(ku_type)
    if matcher:
        type_score, type_max, type_matched = matcher(entity, ku_name_en)
    else:
        type_score, type_max, type_matched = 0, 0, []

    matched = type_matched[:]
    if label_or_alias_match:
        matched.append({"field": "label_match", "expected": ku_name_en, "actual": match_text, "result": "pass"})
    else:
        matched.append({"field": "label_match", "expected": ku_name_en, "actual": match_text, "result": "fail"})

    # P0-2: if no label/alias match, quality is always weak regardless of type score
    if not label_or_alias_match:
        return "weak", 0.0, matched

    label_score = 1
    total_score = label_score + type_score
    total_max = 1 + type_max

    numeric_score = round(total_score / total_max, 2) if total_max else 0.0

    if total_max < 2:
        return "weak", numeric_score, matched
    if total_score >= total_max * 0.75:
        return "strong", numeric_score, matched
    elif total_score >= total_max * 0.5:
        return "medium", numeric_score, matched
    else:
        return "weak", numeric_score, matched


def is_better_match(quality: str, score: float, best_quality: str, best_score: float) -> bool:
    """Prefer semantic quality, then score; preserve the API's earlier rank on ties."""
    quality_rank = {"none": 0, "weak": 1, "medium": 2, "strong": 3}
    return (quality_rank.get(quality, 0), score) > (
        quality_rank.get(best_quality, 0),
        best_score,
    )


def has_exact_label_match(matched_fields: list[dict] | list[str]) -> bool:
    return any(
        isinstance(field, dict)
        and field.get("field") == "label_match"
        and field.get("result") == "pass"
        for field in matched_fields
    )


def semantic_type_rank(matched_fields: list[dict] | list[str]) -> int:
    positive_type_fields = {
        "instance_of",
        "instance_of (P31)",
        "subclass_of (P279)",
    }
    return max(
        (
            1
            for field in matched_fields
            if isinstance(field, dict)
            and field.get("field") in positive_type_fields
            and field.get("result") == "pass"
        ),
        default=0,
    )


def should_replace_best_match(
    quality: str,
    score: float,
    matched_fields: list[dict] | list[str],
    best_quality: str,
    best_score: float,
    best_matched_fields: list[dict] | list[str],
) -> bool:
    """Keep Wikidata search rank when multiple candidates share an exact label.

    Field completeness is not identity evidence.  Without KU-specific dates or
    affiliations, a more completely described namesake must not displace the
    API's earlier exact-label candidate.
    """
    if has_exact_label_match(matched_fields) and has_exact_label_match(best_matched_fields):
        candidate_type_rank = semantic_type_rank(matched_fields)
        current_type_rank = semantic_type_rank(best_matched_fields)
        if candidate_type_rank != current_type_rank:
            return candidate_type_rank > current_type_rank
        return False
    return is_better_match(quality, score, best_quality, best_score)


def collect_one(ku_path: Path, verbose: bool = False) -> dict | None:
    text = read_text(ku_path)
    fm = extract_frontmatter(text)
    if not fm:
        return None

    name_en = scalar_fm(fm, "name_en") or scalar_fm(fm, "title")
    ku_type = scalar_fm(fm, "type")

    rel = ku_path.relative_to(BASE).as_posix()

    if verbose:
        print(f"\n  [{ku_type}] {name_en}", file=sys.stderr)

    candidates = search_wikidata(name_en)
    if candidates and isinstance(candidates[0], dict) and candidates[0].get("error"):
        collection_error = candidates[0]["error"]
        return {
            "ku_path": rel,
            "platform": "Wikidata",
            "source_type": "structured_database_api",
            "source_authority": "structured_reference",
            "source_independence_group": "wikimedia",
            "url": "",
            "claim_scope": infer_claim_scope(ku_type, "none"),
            "claim_target": infer_claim_target(ku_type, infer_claim_scope(ku_type, "none")),
            "match_quality": "none",
            "match_score": 0.0,
            "verified_fields": [],
            "conflicting_fields": [],
            "candidate_rank": 0,
            "candidate_count": 0,
            "match_detail": [],
            "candidates": [],
            "recommended_changes": {},
            "blocking_reason": "api_error",
            "collection_error": collection_error,
            "notes": "Wikidata API failed; this is a collection failure, not evidence that the object is absent.",
        }
    if not candidates:
        return {
            "ku_path": rel,
            "platform": "Wikidata",
            "source_type": "structured_database_api",
            "source_authority": "structured_reference",
            "source_independence_group": "wikimedia",
            "claim_scope": "entity_identity_only",
            "claim_target": "name_en",
            "match_quality": "none",
            "match_score": 0.0,
            "verified_fields": [],
            "conflicting_fields": [],
            "candidate_rank": 0,
            "candidate_count": 0,
            "recommended_changes": {},
            "blocking_reason": "no_search_results",
            "notes": "No Wikidata search results.",
        }

    top_candidates = []
    best_match = None
    best_quality = "none"

    best_score = 0.0
    best_rank = 0
    entities = get_entities([c.get("id", "") for c in candidates[:5]])
    entity_error = entities.get("__error__")

    for rank_index, c in enumerate(candidates[:5], start=1):
        qid = c.get("id", "")
        entity = {"error": entity_error} if entity_error else entities.get(qid, {})
        quality, score_value, matched = match_score(c, entity, name_en, ku_type)
        label = c.get("label", "?")
        desc = c.get("description", "")

        top_candidates.append({
            "qid": qid,
            "label": label,
            "description": desc,
            "match_quality": quality,
            "match_score": score_value,
            "matched_fields": matched,
            "candidate_rank": rank_index,
            "conflicting_fields": conflicting_fields(matched),
        })

        if best_match is None or should_replace_best_match(
            quality,
            score_value,
            matched,
            best_quality,
            best_score,
            best_match.get("matched_fields", []),
        ):
            best_match = top_candidates[-1]
            best_quality = quality
            best_score = score_value
            best_rank = rank_index

    claim_scope = infer_claim_scope(ku_type, best_quality)
    blocking_reason = None
    if match_has_api_error(best_match):
        blocking_reason = "api_error"
    elif best_match and best_match.get("conflicting_fields"):
        blocking_reason = "conflicting_fields"
    elif best_quality == "weak":
        blocking_reason = "weak_match"
    elif best_quality == "none":
        blocking_reason = "no_suitable_entity"

    if best_quality in ("strong", "medium"):
        evidence_status = "externally_verified" if best_quality == "strong" else "partially_verified"
        if claim_scope in LIMITED_SCOPES:
            evidence_status = "partially_verified"
        recommended = {
            "evidence_status": evidence_status,
            "verification_level": "L2",
            "confidence": "medium",
            "consensus": "tentative",
        }
        if blocking_reason:
            recommended = {}
    else:
        recommended = {}

    evidence = {
        "ku_path": rel,
        "platform": "Wikidata",
        "source_type": "structured_database_api",
        "source_authority": "structured_reference",
        "source_independence_group": "wikimedia",
        "url": f"https://www.wikidata.org/wiki/{best_match['qid']}" if best_match else "",
        "claim_scope": claim_scope,
        "claim_target": infer_claim_target(ku_type, claim_scope),
        "match_quality": best_quality,
        "match_score": best_score,
        "verified_fields": _extract_field_names(best_match.get("matched_fields", [])) if best_match else [],
        "conflicting_fields": best_match.get("conflicting_fields", []) if best_match else [],
        "candidate_rank": best_rank,
        "candidate_count": len(top_candidates),
        "match_detail": best_match.get("matched_fields", []) if best_match else [],
        "candidates": top_candidates,
        "recommended_changes": recommended,
        "blocking_reason": blocking_reason,
        "collection_error": entity_error if blocking_reason == "api_error" else None,
        "notes": (
            "Wikidata API failed; this is a collection failure, not evidence that the object is absent."
            if blocking_reason == "api_error"
            else "Wikidata entity identity verification. Contribution claims still rely on source literature."
        ),
    }

    if verbose:
        print(f"    quality={best_quality} matched={evidence['verified_fields']}", file=sys.stderr)

    return evidence


def iter_units(limit: int = 0) -> list[Path]:
    files: list[Path] = []
    for type_dir in sorted(UNITS.iterdir()):
        if not type_dir.is_dir():
            continue
        for md in sorted(type_dir.glob("*.md")):
            if md.name.startswith("."):
                continue
            files.append(md)
            if limit and len(files) >= limit:
                return files
    return files


def main():
    parser = argparse.ArgumentParser(description="Wikidata 证据收集器（阶段1）")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--ku", help="指定知识元（文件名，不含路径）")
    scope.add_argument("--input-result", type=Path, help="读取包含 targets 的批次规划 JSON")
    scope.add_argument(
        "--retry-from",
        type=Path,
        action="append",
        help="从一个或多个历史 evidence JSONL 中只重跑 api_error 目标",
    )
    parser.add_argument("--checkpoint", type=int, default=0, help="只收集 input-result 中指定 checkpoint")
    parser.add_argument("--output", type=Path, help="原子写入 evidence JSONL；省略时输出到 stdout")
    parser.add_argument("--limit", type=int, default=0, help="批量限制")
    parser.add_argument("--verbose", action="store_true", help="详细输出到 stderr")
    parser.add_argument("--dry-run", action="store_true", help="仅预览")
    args = parser.parse_args()

    if not requests:
        print("[STUB] requests 库未安装。pip install requests", file=sys.stderr)
        return

    if args.dry_run:
        print("[DRY RUN] 将扫描知识元并通过 Wikidata API 收集证据")
        if args.ku:
            print(f"  target: {args.ku}")
        elif args.input_result:
            print(f"  input-result: {args.input_result} checkpoint={args.checkpoint or 'all'}")
        elif args.retry_from:
            print(f"  retry-from: {len(args.retry_from)} evidence file(s), blocking_reason=api_error")
        else:
            print(f"  scope: all UNITS (limit={args.limit})")
        print("  输出: evidence JSONL（每行一个 JSON 对象）")
        return

    if args.checkpoint and not args.input_result:
        parser.error("--checkpoint 只能与 --input-result 一起使用")
    if args.ku:
        target = resolve_single_target(args.ku, UNITS)
        if not target:
            print(f"未找到: {args.ku}", file=sys.stderr)
            sys.exit(1)
        files = [target]
    elif args.input_result:
        files = load_result_targets(resolve(args.input_result, BASE), BASE, UNITS, args.checkpoint)
    elif args.retry_from:
        retry_sources = [resolve(path, BASE) for path in args.retry_from]
        files = load_evidence_targets(retry_sources, BASE, UNITS, {"api_error"})
    else:
        files = iter_units(limit=args.limit)

    if args.verbose:
        print(f"待验证: {len(files)} 个知识元", file=sys.stderr)

    evidence_rows = []
    for path in files:
        evidence = collect_one(path, verbose=args.verbose)
        if evidence:
            if args.retry_from:
                evidence["retry_context"] = {
                    "mode": "api_error_only",
                    "prior_evidence_refs": [
                        source_path.relative_to(BASE).as_posix()
                        if source_path.is_relative_to(BASE)
                        else str(source_path)
                        for source_path in [resolve(source, BASE) for source in args.retry_from]
                    ],
                }
            evidence_rows.append(evidence)
        time.sleep(REQUEST_DELAY)

    if args.output:
        output = resolve(args.output, BASE)
        write_jsonl(evidence_rows, output)
        if args.verbose:
            print(f"evidence={output}", file=sys.stderr)
    else:
        for evidence in evidence_rows:
            print(json.dumps(evidence, ensure_ascii=False))

    if args.verbose:
        print(f"\n完成: {len(evidence_rows)} 条证据", file=sys.stderr)


if __name__ == "__main__":
    main()
