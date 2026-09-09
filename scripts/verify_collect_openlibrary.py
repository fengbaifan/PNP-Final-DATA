#!/usr/bin/env python3
"""Collect Open Library bibliographic evidence for work/publication KUs."""

from __future__ import annotations

import argparse
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
SEARCH_API = "https://openlibrary.org/search.json"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Infographic-Knowledge-Distillation/5.3 (+https://github.com/fengbaifan/Infographic-Knowledge-Distillation)",
}
HTTP_TIMEOUT = 25
MAX_API_RETRIES = 2
REQUEST_DELAY = 1.05
MAX_CANDIDATES = 10
TYPE_ALIASES = {"works": "work", "publications": "publication"}
QUALITY_RANK = {"none": 0, "weak": 1, "medium": 2, "strong": 3}


def extract_frontmatter(text: str) -> str:
    match = re.search(r"^\ufeff?---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    return match.group(1).strip("\n") if match else ""


def scalar_fm(fm: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    return match.group(1).strip().strip('"').strip("'") if match else ""


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value or "")
    asciiish = "".join(char for char in decomposed if not unicodedata.combining(char))
    asciiish = re.sub(r"\b(?:ca\.?|circa|approximately)\b", " ", asciiish.lower())
    asciiish = re.sub(r"\b(?:1[0-9]{3}|20[0-9]{2})\b", " ", asciiish)
    asciiish = re.sub(r"[^a-z0-9]+", " ", asciiish)
    return re.sub(r"\s+", " ", asciiish).strip()


def title_score(expected: str, actual: str) -> float:
    left = set(normalize_text(expected).split())
    right = set(normalize_text(actual).split())
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    return round(len(left & right) / max(len(left), len(right)), 3)


def expected_year(fm: str, *values: str) -> int | None:
    for field in ("publication_year", "year", "date"):
        raw = scalar_fm(fm, field)
        match = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", raw)
        if match:
            return int(match.group(1))
    terminal = re.compile(r"(?:,|\()\s*(?:ca\.?\s*)?(1[0-9]{3}|20[0-9]{2})\)?\s*$", re.IGNORECASE)
    for value in values:
        match = terminal.search(value or "")
        if match:
            return int(match.group(1))
    for value in values[:-1]:
        without_ranges = re.sub(r"\b(?:1[0-9]{3}|20[0-9]{2})\s*[-–]\s*(?:1[0-9]{3}|20[0-9]{2})\b", "", value or "")
        years = re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", without_ranges)
        if len(years) == 1:
            return int(years[0])
    if values:
        slug_match = re.search(r"(?:^|-)(1[0-9]{3}|20[0-9]{2})$", values[-1] or "")
        if slug_match:
            return int(slug_match.group(1))
    return None


def search_title(title: str) -> str:
    cleaned = re.sub(r"\s*\((?:ca\.?\s*)?\d{4}\)\s*$", "", title, flags=re.IGNORECASE)
    cleaned = re.sub(r",\s*(?:ca\.?\s*)?\d{4}\s*$", "", cleaned, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()


def quality_for_score(score: float) -> str:
    if score >= 0.86:
        return "strong"
    if score >= 0.65:
        return "medium"
    if score > 0:
        return "weak"
    return "none"


def author_lists_overlap(left: list[str], right: list[str]) -> bool:
    for left_name in left:
        left_tokens = normalize_text(left_name).split()
        if not left_tokens:
            continue
        for right_name in right:
            right_tokens = normalize_text(right_name).split()
            if not right_tokens:
                continue
            if left_tokens[-1] == right_tokens[-1] and len(left_tokens[-1]) > 2:
                return True
    return False


def request_search(query: str) -> tuple[dict | None, dict | None]:
    if not requests:
        return None, {"stage": "search", "error_type": "missing_dependency", "attempts": 0, "retryable": False}
    params = {
        "title": query,
        "limit": MAX_CANDIDATES,
        "fields": "key,title,author_name,first_publish_year,publisher,isbn,edition_count,language",
    }
    last_error: dict | None = None
    for attempt in range(1, MAX_API_RETRIES + 2):
        try:
            response = requests.get(SEARCH_API, params=params, headers=HEADERS, timeout=HTTP_TIMEOUT)
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


def evaluate_candidates(expected_title: str, year: int | None, docs: list[dict]) -> tuple[dict | None, list[dict], str | None]:
    rows: list[dict] = []
    for rank, doc in enumerate(docs, start=1):
        score = title_score(expected_title, str(doc.get("title") or ""))
        quality = quality_for_score(score)
        candidate_year = doc.get("first_publish_year")
        year_delta = abs(candidate_year - year) if year and isinstance(candidate_year, int) else None
        year_conflict = year_delta is not None and year_delta > 5
        fields = ["title"]
        for key, field in (
            ("author_name", "author"),
            ("first_publish_year", "first_publish_year"),
            ("publisher", "publisher"),
            ("isbn", "isbn"),
            ("edition_count", "edition_count"),
        ):
            if doc.get(key):
                fields.append(field)
        rows.append(
            {
                "candidate_rank": rank,
                "key": str(doc.get("key") or ""),
                "title": str(doc.get("title") or ""),
                "authors": doc.get("author_name") or [],
                "first_publish_year": candidate_year,
                "publishers": doc.get("publisher") or [],
                "isbns": doc.get("isbn") or [],
                "edition_count": doc.get("edition_count"),
                "match_quality": quality,
                "match_score": score,
                "year_delta": year_delta,
                "year_conflict": year_conflict,
                "verified_fields": fields,
            }
        )
    ranked = sorted(
        rows,
        key=lambda row: (
            row["year_conflict"],
            -QUALITY_RANK[row["match_quality"]],
            row["year_delta"] if row["year_delta"] is not None else 9999,
            -len(row["verified_fields"]),
            row["candidate_rank"],
        ),
    )
    if not ranked:
        return None, rows, "no_search_results"
    best = ranked[0]
    if best["match_quality"] in {"none", "weak"}:
        return best, rows, "weak_title_match"
    if best["year_conflict"]:
        return best, rows, "publication_year_conflict"
    equally_named = [
        row
        for row in ranked[1:]
        if row["match_quality"] == "strong"
        and best["match_quality"] == "strong"
        and abs(row["match_score"] - best["match_score"]) < 0.03
        and row["authors"]
        and best["authors"]
        and not author_lists_overlap(row["authors"], best["authors"])
        and (year is None or row["year_delta"] == best["year_delta"])
    ]
    if equally_named:
        return best, rows, "ambiguous_bibliographic_identity"
    return best, rows, None


def bibliographic_fact(best: dict | None, expected: int | None) -> bool:
    if not best or best.get("match_quality") != "strong":
        return False
    if expected is not None and best.get("year_delta") not in {0, 1, 2}:
        return False
    metadata = {"author", "first_publish_year", "publisher", "isbn"} & set(best.get("verified_fields") or [])
    return len(metadata) >= 2


def collect_one(path: Path, verbose: bool = False) -> dict | None:
    fm = extract_frontmatter(path.read_text(encoding="utf-8"))
    if not fm:
        return None
    ku_type = scalar_fm(fm, "type").lower() or TYPE_ALIASES.get(path.parent.name, "")
    if ku_type not in {"work", "publication"}:
        raise ValueError(f"Open Library collector 只接受 work/publication：{path}")
    display_title = scalar_fm(fm, "title")
    original_title = scalar_fm(fm, "title_original")
    title = scalar_fm(fm, "name_en") or original_title or display_title
    year = expected_year(fm, title, display_title, original_title, path.stem)
    query = search_title(title)
    payload, collection_error = request_search(query)
    docs = payload.get("docs") if isinstance(payload, dict) and isinstance(payload.get("docs"), list) else []
    best, candidates, blocking_reason = evaluate_candidates(title, year, docs)
    if collection_error:
        blocking_reason = "api_error"
    scope = "bibliographic_fact" if bibliographic_fact(best, year) and not blocking_reason else "bibliographic_hint"
    quality = best.get("match_quality", "none") if best else "none"
    recommended: dict = {}
    if not blocking_reason and quality in {"strong", "medium"}:
        recommended = {
            "evidence_status": "externally_verified" if scope == "bibliographic_fact" else "partially_verified",
            "verification_level": "L6",
            "confidence": "medium",
            "consensus": "tentative",
        }
    key = best.get("key", "") if best else ""
    url = f"https://openlibrary.org{key}" if key.startswith("/") else ""
    evidence = {
        "ku_path": path.relative_to(BASE).as_posix(),
        "platform": "Open Library",
        "source_type": "library_catalog_api",
        "source_authority": "aggregated_library_metadata",
        "source_independence_group": "openlibrary_internet_archive",
        "url": url,
        "claim_scope": scope,
        "claim_target": "bibliographic_identity_and_fields" if scope == "bibliographic_fact" else "title_or_bibliographic_identity",
        "match_quality": quality,
        "match_score": best.get("match_score", 0.0) if best else 0.0,
        "verified_fields": best.get("verified_fields", []) if best else [],
        "conflicting_fields": ["publication_year"] if best and best.get("year_conflict") else [],
        "expected_year": year,
        "matched_title": best.get("title", "") if best else "",
        "matched_authors": best.get("authors", []) if best else [],
        "matched_first_publish_year": best.get("first_publish_year") if best else None,
        "matched_publishers": best.get("publishers", []) if best else [],
        "matched_isbns": best.get("isbns", []) if best else [],
        "candidate_rank": best.get("candidate_rank", 0) if best else 0,
        "candidate_count": payload.get("numFound", len(docs)) if isinstance(payload, dict) else 0,
        "returned_candidate_count": len(docs),
        "candidates": candidates,
        "collection_error": collection_error,
        "blocking_reason": blocking_reason,
        "recommended_changes": recommended,
        "notes": (
            "Open Library metadata supports only bibliographic identity and recorded fields; "
            "it does not validate visual interpretation, authorship beyond the catalog record, or domain relevance."
        ),
    }
    if verbose:
        print(
            f"[{ku_type}] {title}: {quality} {blocking_reason or scope} "
            f"{evidence['matched_title']}",
            file=sys.stderr,
        )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--ku")
    scope.add_argument("--input-result", type=Path)
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
        parser.error(f"Open Library collector 收到非 work/publication 目标：{invalid[0]}")
    if args.dry_run:
        print(f"targets={len(files)} checkpoint={args.checkpoint or 'all'} output={args.output}")
        return 0
    rows = []
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
    print(f"bibliographic_fact={sum(row.get('claim_scope') == 'bibliographic_fact' for row in rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
