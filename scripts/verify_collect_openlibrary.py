#!/usr/bin/env python3
"""Collect Open Library bibliographic evidence for work/archive KUs."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

try:
    from scripts import _collect_common as common
except ModuleNotFoundError:
    import _collect_common as common


SEARCH_API = "https://openlibrary.org/search.json"
MAX_CANDIDATES = 10
TYPE_ALIASES = {"works": "work", "archives": "archive"}
QUALITY_RANK = {"none": 0, "weak": 1, "medium": 2, "strong": 3}


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
        raw = common.scalar_fm(fm, field)
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


class OpenLibraryAdapter(common.Adapter):
    name = "Open Library"
    description = "通过 Open Library 收集 work/archive 的书目证据。"
    type_aliases = TYPE_ALIASES

    def accepts(self, ku_type: str) -> bool:
        return ku_type in {"work", "archive"}

    def _year(self, fm: str, label: str, path: Path) -> int | None:
        display_title = common.scalar_fm(fm, "title")
        original_title = common.scalar_fm(fm, "title_original")
        return expected_year(fm, label, display_title, original_title, path.stem)

    def search(self, label: str, ku_type: str, fm: str, path: Path) -> tuple[dict | None, dict | None]:
        query = search_title(label)
        params = {
            "title": query,
            "limit": MAX_CANDIDATES,
            "fields": "key,title,author_name,first_publish_year,publisher,isbn,edition_count,language",
        }
        return common.request_json(SEARCH_API, params, stage="search")

    def evaluate(self, label: str, ku_type: str, fm: str, path: Path, payload: dict | None) -> tuple[dict | None, list[dict], str | None]:
        year = self._year(fm, label, path)
        docs = payload.get("docs") if isinstance(payload, dict) and isinstance(payload.get("docs"), list) else []
        return evaluate_candidates(label, year, docs)

    def build_evidence(self, path, ku_type, label, fm, best, candidates, blocking_reason, payload, collection_error):
        year = self._year(fm, label, path)
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
        return {
            "ku_path": path.relative_to(common.BASE).as_posix(),
            "platform": self.name,
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
            "candidate_count": payload.get("numFound", len(candidates)) if isinstance(payload, dict) else 0,
            "returned_candidate_count": len(candidates),
            "candidates": candidates,
            "collection_error": collection_error,
            "blocking_reason": blocking_reason,
            "recommended_changes": recommended,
            "notes": (
                "Open Library metadata supports only bibliographic identity and recorded fields; "
                "it does not validate visual interpretation, authorship beyond the catalog record, or domain relevance."
            ),
        }


def main() -> int:
    return common.run(OpenLibraryAdapter())


if __name__ == "__main__":
    raise SystemExit(main())
