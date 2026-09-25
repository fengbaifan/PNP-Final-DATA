#!/usr/bin/env python3
"""Collect scholarly semantic candidates from OpenAlex for term/procedure KUs."""

from __future__ import annotations

import re
from pathlib import Path

try:
    from scripts import _collect_common as common
except ModuleNotFoundError:
    import _collect_common as common


SEARCH_API = "https://api.openalex.org/works"
MAX_CANDIDATES = 5
TYPE_ALIASES = {"terms": "term", "procedures": "procedure"}
SEMANTIC_CUE = re.compile(
    r"\b(?:defined as|refers to|means|is a|is an|present|introduce|propose|develop|describe)\b|"
    r"\b(?:method|technique|approach|procedure|process|framework|model)\s+(?:for|to|that|which|of)\b",
    re.IGNORECASE,
)


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
    expected = set(common.normalize_text(term).split())
    observed = set(common.normalize_text(text).split())
    if not expected or not observed:
        return 0.0
    return round(len(expected & observed) / len(expected), 3)


def semantic_context(term: str, abstract: str) -> tuple[bool, str]:
    if not abstract:
        return False, ""
    norm_term = common.normalize_text(term)
    norm_abstract = common.normalize_text(abstract)
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


class OpenAlexAdapter(common.Adapter):
    name = "OpenAlex"
    description = "通过 OpenAlex 收集 term/procedure 的学术语义候选证据。"
    type_aliases = TYPE_ALIASES

    def accepts(self, ku_type: str) -> bool:
        return ku_type in {"term", "procedure"}

    def search(self, label: str, ku_type: str, fm: str, path: Path) -> tuple[dict | None, dict | None]:
        params = {
            "search": f'"{label}"',
            "per-page": MAX_CANDIDATES,
            "select": "id,display_name,publication_year,doi,type,cited_by_count,authorships,primary_location,abstract_inverted_index,relevance_score,is_retracted",
        }
        return common.request_json(SEARCH_API, params, stage="search")

    def evaluate(self, label: str, ku_type: str, fm: str, path: Path, payload: dict | None) -> tuple[dict | None, list[dict], str | None]:
        docs = payload.get("results") if isinstance(payload, dict) and isinstance(payload.get("results"), list) else []
        return evaluate_candidates(label, docs)

    def build_evidence(self, path, ku_type, label, fm, best, candidates, blocking_reason, payload, collection_error):
        recommended = {}
        if best and not blocking_reason:
            recommended = {
                "evidence_status": "partially_verified",
                "verification_level": "L5",
                "confidence": "medium",
                "consensus": "tentative",
            }
        url = best.get("openalex_id", "") if best else ""
        return {
            "ku_path": path.relative_to(common.BASE).as_posix(),
            "platform": self.name,
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
            "candidate_count": payload.get("meta", {}).get("count", len(candidates)) if isinstance(payload, dict) else 0,
            "returned_candidate_count": len(candidates),
            "candidates": candidates,
            "collection_error": collection_error,
            "blocking_reason": blocking_reason,
            "recommended_changes": recommended,
            "notes": (
                "OpenAlex search covers scholarly titles, abstracts, and available full text. The reconstructed abstract is a candidate semantic source only; "
                "Agent review must confirm that it defines or substantively describes this exact term/procedure, and must reject mere mentions."
            ),
        }


def main() -> int:
    return common.run(OpenAlexAdapter())


if __name__ == "__main__":
    raise SystemExit(main())
