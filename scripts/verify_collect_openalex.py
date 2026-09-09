#!/usr/bin/env python3
"""Collect scholarly semantic candidates from OpenAlex for term/procedure KUs."""

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
SEARCH_API = "https://api.openalex.org/works"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "PNP-Knowledge-Distillation/5.3 (+https://github.com/fengbaifan/PNP-Final-DATA)",
}
HTTP_TIMEOUT = 25
MAX_API_RETRIES = 2
REQUEST_DELAY = 0.15
MAX_CANDIDATES = 5
TYPE_ALIASES = {"terms": "term", "procedures": "procedure"}
SEMANTIC_CUE = re.compile(
    r"\b(?:defined as|refers to|means|is a|is an|present|introduce|propose|develop|describe)\b|"
    r"\b(?:method|technique|approach|procedure|process|framework|model)\s+(?:for|to|that|which|of)\b",
    re.IGNORECASE,
)


def extract_frontmatter(text: str) -> str:
    match = re.search(r"^\ufeff?---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    return match.group(1).strip("\n") if match else ""


def scalar_fm(fm: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    return match.group(1).strip().strip('"').strip("'") if match else ""


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value or "")
    asciiish = "".join(char for char in decomposed if not unicodedata.combining(char))
    asciiish = re.sub(r"[^a-z0-9]+", " ", asciiish.lower())
    return re.sub(r"\s+", " ", asciiish).strip()


def reconstruct_abstract(index: dict | None) -> str:
    if not isinstance(index, dict) or not index:
        return ""
    positioned: list[tuple[int, str]] = []
    for word, positions in index.items():
        if not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int) and 0 <= position < 10000:
                positioned.append((position, str(word)))
    positioned.sort(key=lambda item: item[0])
    return " ".join(word for _, word in positioned)


def term_coverage(term: str, text: str) -> float:
    expected = set(normalize_text(term).split())
    observed = set(normalize_text(text).split())
    if not expected or not observed:
        return 0.0
    return round(len(expected & observed) / len(expected), 3)


def semantic_context(term: str, abstract: str) -> tuple[bool, str]:
    if not abstract:
        return False, ""
    norm_term = normalize_text(term)
    norm_abstract = normalize_text(abstract)
    exact = bool(norm_term and norm_term in norm_abstract)
    cue = SEMANTIC_CUE.search(abstract)
    if not exact or not cue:
        return False, ""
    term_tokens = norm_term.split()
    first_token = term_tokens[0] if term_tokens else ""
    lower = abstract.lower()
    start = lower.find(first_token.lower()) if first_token else -1
    if start < 0:
        start = max(cue.start() - 180, 0)
    left = max(start - 220, 0)
    right = min(start + 580, len(abstract))
    return True, abstract[left:right].strip()


def request_search(query: str) -> tuple[dict | None, dict | None]:
    if not requests:
        return None, {"stage": "search", "error_type": "missing_dependency", "attempts": 0, "retryable": False}
    params = {
        "search": f'"{query}"',
        "per-page": MAX_CANDIDATES,
        "select": "id,display_name,publication_year,doi,type,cited_by_count,authorships,primary_location,abstract_inverted_index,relevance_score,is_retracted",
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


def evaluate_candidates(term: str, docs: list[dict]) -> tuple[dict | None, list[dict], str | None]:
    rows: list[dict] = []
    for rank, doc in enumerate(docs, start=1):
        abstract = reconstruct_abstract(doc.get("abstract_inverted_index"))
        combined = f"{doc.get('display_name') or ''} {abstract}"
        coverage = term_coverage(term, combined)
        has_context, snippet = semantic_context(term, abstract)
        authors = []
        for authorship in doc.get("authorships") or []:
            author = authorship.get("author") if isinstance(authorship, dict) else None
            name = author.get("display_name") if isinstance(author, dict) else None
            if name:
                authors.append(str(name))
        location = doc.get("primary_location") if isinstance(doc.get("primary_location"), dict) else {}
        source = location.get("source") if isinstance(location.get("source"), dict) else {}
        rows.append({
            "candidate_rank": rank,
            "openalex_id": str(doc.get("id") or ""),
            "title": str(doc.get("display_name") or ""),
            "authors": authors,
            "publication_year": doc.get("publication_year"),
            "work_type": str(doc.get("type") or ""),
            "doi": str(doc.get("doi") or ""),
            "source": str(source.get("display_name") or ""),
            "cited_by_count": int(doc.get("cited_by_count") or 0),
            "relevance_score": doc.get("relevance_score"),
            "term_coverage": coverage,
            "abstract": abstract[:3500],
            "semantic_context": has_context,
            "semantic_snippet": snippet[:900],
            "is_retracted": bool(doc.get("is_retracted")),
        })
    ranked = sorted(rows, key=lambda row: (
        row["is_retracted"],
        not row["semantic_context"],
        -row["term_coverage"],
        -row["cited_by_count"],
        row["candidate_rank"],
    ))
    if not ranked:
        return None, rows, "no_search_results"
    best = ranked[0]
    if best["is_retracted"]:
        return best, rows, "retracted_candidate"
    if not any(row["abstract"] for row in ranked):
        return best, rows, "no_abstract_candidates"
    if best["term_coverage"] < 0.75:
        return best, rows, "weak_term_match"
    if not best["semantic_context"]:
        return best, rows, "no_semantic_context"
    return best, rows, None


def collect_one(path: Path, verbose: bool = False) -> dict | None:
    fm = extract_frontmatter(path.read_text(encoding="utf-8"))
    if not fm:
        return None
    ku_type = scalar_fm(fm, "type").lower() or TYPE_ALIASES.get(path.parent.name, "")
    if ku_type not in {"term", "procedure"}:
        raise ValueError(f"OpenAlex collector 只接受 term/procedure：{path}")
    label = scalar_fm(fm, "name_en") or scalar_fm(fm, "title_original") or scalar_fm(fm, "title")
    payload, collection_error = request_search(label)
    docs = payload.get("results") if isinstance(payload, dict) and isinstance(payload.get("results"), list) else []
    best, candidates, blocking_reason = evaluate_candidates(label, docs)
    if collection_error:
        blocking_reason = "api_error"
    recommended = {}
    if best and not blocking_reason:
        recommended = {
            "evidence_status": "partially_verified",
            "verification_level": "L5",
            "confidence": "medium",
            "consensus": "tentative",
        }
    url = best.get("openalex_id", "") if best else ""
    evidence = {
        "ku_path": path.relative_to(BASE).as_posix(),
        "platform": "OpenAlex",
        "source_type": "scholarly_index_api",
        "source_authority": "scholarly_metadata_and_abstract_index",
        "source_independence_group": "openalex_scholarly_graph",
        "url": url,
        "claim_scope": "scholarly_semantic_candidate",
        "claim_target": "definition_or_method_scope",
        "match_quality": "strong" if best and best["semantic_context"] else "weak" if best else "none",
        "match_score": best.get("term_coverage", 0.0) if best else 0.0,
        "verified_fields": ["scholarly_context", "abstract"] if best and best["semantic_context"] else [],
        "conflicting_fields": [],
        "query_term": label,
        "matched_title": best.get("title", "") if best else "",
        "matched_authors": best.get("authors", []) if best else [],
        "matched_publication_year": best.get("publication_year") if best else None,
        "matched_doi": best.get("doi", "") if best else "",
        "matched_source": best.get("source", "") if best else "",
        "semantic_snippet": best.get("semantic_snippet", "") if best else "",
        "candidate_count": payload.get("meta", {}).get("count", len(docs)) if isinstance(payload, dict) else 0,
        "returned_candidate_count": len(docs),
        "candidates": candidates,
        "collection_error": collection_error,
        "blocking_reason": blocking_reason,
        "recommended_changes": recommended,
        "notes": (
            "OpenAlex search covers scholarly titles, abstracts, and available full text. The reconstructed abstract is a candidate semantic source only; "
            "Agent review must confirm that it defines or substantively describes this exact term/procedure, and must reject mere mentions."
        ),
    }
    if verbose:
        print(f"[{ku_type}] {label}: {blocking_reason or 'semantic_candidate'} {evidence['matched_title']}", file=sys.stderr)
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
        parser.error(f"OpenAlex collector 收到非 term/procedure 目标：{invalid[0]}")
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
    print(f"semantic_candidates={sum(not row.get('blocking_reason') for row in rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
