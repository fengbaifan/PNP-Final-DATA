#!/usr/bin/env python3
"""Read-only locator for typed candidate names missing from S2 mention spans.

This is a heuristic recall prompt, not an entity extractor or semantic gate.
It only detects existing typed candidate labels that appear literally in a
reviewed S2 segment without overlapping any recorded mention. It cannot find
unlisted entities, judge identity, or determine whether a candidate hit should
be a mention.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "04-knowledge" / "tables"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.translate(str.maketrans({"’": "'", "‘": "'", "`": "'", "–": "-", "—": "-", "−": "-"}))
    return value


def normalize_with_map(value: str) -> tuple[str, list[int], list[int]]:
    """Normalize a segment while mapping each normalized character to source offsets."""
    chars: list[str] = []
    starts: list[int] = []
    ends: list[int] = []
    for source_index, original in enumerate(value):
        for char in normalize(original):
            if char.isspace():
                if chars and chars[-1] == " ":
                    ends[-1] = source_index + 1
                elif chars:
                    chars.append(" ")
                    starts.append(source_index)
                    ends.append(source_index + 1)
            else:
                chars.append(char)
                starts.append(source_index)
                ends.append(source_index + 1)
    return "".join(chars), starts, ends


def build_patterns(
    candidates: Iterable[dict[str, str]], min_single_word_chars: int = 6
) -> list[tuple[re.Pattern[str], list[dict[str, str]]]]:
    """Compile distinct typed names; omit short single words to limit generic hits."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for candidate in candidates:
        if not candidate.get("suggested_type", "").strip():
            continue
        if candidate.get("exclude_reason", "").strip() or candidate.get("status") in {"excluded", "rejected"}:
            continue
        for label in (candidate.get("canonical_name", ""), candidate.get("sub_entry", "")):
            label = label.strip()
            normalized = normalize(label).strip()
            if not normalized or (" " not in normalized and len(normalized) < min_single_word_chars):
                continue
            values = grouped[normalized]
            record = {
                "candidate_id": candidate.get("candidate_id", ""),
                "label": label,
                "suggested_type": candidate.get("suggested_type", ""),
                "source_segment_id": candidate.get("candidate_source_ref", "").split("#", 1)[0],
                "source_local_only": (
                    candidate.get("candidate_origin") == "body-mention"
                    and "identified only by office" in candidate.get("detail", "").casefold()
                ),
            }
            if record not in values:
                values.append(record)

    patterns = []
    for label, records in grouped.items():
        body = r"\s+".join(re.escape(part) for part in label.split())
        patterns.append((re.compile(r"(?<!\w)" + body + r"(?!\w)"), records))
    return patterns


def find_uncovered_spans(
    text: str,
    patterns: Iterable[tuple[re.Pattern[str], list[dict[str, str]]]],
    existing_spans: Iterable[tuple[int, int]],
    segment_id: str | None = None,
) -> list[dict[str, object]]:
    normalized, starts, ends = normalize_with_map(text)
    existing = list(existing_spans)
    hits: dict[tuple[int, int], dict[str, object]] = {}
    for pattern, candidates in patterns:
        for match in pattern.finditer(normalized):
            start = starts[match.start()]
            end = ends[match.end() - 1]
            if any(start < existing_end and end > existing_start for existing_start, existing_end in existing):
                continue
            matching_candidates = [
                candidate
                for candidate in candidates
                if not candidate.get("source_local_only")
                or not segment_id
                or candidate.get("source_segment_id") == segment_id
            ]
            if not matching_candidates:
                continue
            key = (start, end)
            hit = hits.setdefault(
                key,
                {"start_char": start, "end_char": end, "surface_form": text[start:end], "candidate_matches": []},
            )
            matches = hit["candidate_matches"]
            for candidate in matching_candidates:
                if candidate not in matches:
                    matches.append(candidate)
    return [hits[key] for key in sorted(hits)]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def audit(chapter: str | None, min_single_word_chars: int) -> tuple[dict[str, object], list[dict[str, object]]]:
    coverage = {row["segment_id"]: row for row in read_csv(TABLES / "s2-coverage.csv")}
    mentions: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for row in read_csv(TABLES / "mentions.csv"):
        mentions[row["segment_id"]].append((int(row["start_char"]), int(row["end_char"])))
    patterns = build_patterns(read_csv(TABLES / "entity-candidates.csv"), min_single_word_chars)

    segment_rows = (json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line)
    source_cache: dict[Path, list[str]] = {}
    scanned = 0
    hits: list[dict[str, object]] = []
    for segment in segment_rows:
        segment_id = segment["segment_id"]
        state = coverage.get(segment_id)
        if chapter and segment.get("chapter") != chapter:
            continue
        if not state or state.get("disposition") != "reviewed" or state.get("migration_status") not in {"complete", "partial"}:
            continue
        source = (ROOT / segment["source_file"]).resolve()
        if not source.is_relative_to(ROOT):
            raise ValueError(f"segment source escapes repository: {segment['source_file']}")
        if source not in source_cache:
            source_cache[source] = source.read_text(encoding="utf-8-sig").splitlines()
        text = "\n".join(source_cache[source][segment["line_start"] - 1 : segment["line_end"]])
        spans = find_uncovered_spans(text, patterns, mentions.get(segment_id, []), segment_id=segment_id)
        scanned += 1
        for span in spans:
            hits.append({"segment_id": segment_id, **span})

    summary = {
        "chapter": chapter or "all",
        "reviewed_segments_scanned": scanned,
        "typed_candidate_name_patterns": len(patterns),
        "uncovered_candidate_surface_spans": len(hits),
        "interpretation": "heuristic prompts only; not recall, precision, or semantic acceptance",
    }
    hits.sort(key=lambda row: (str(row["segment_id"]), int(row["start_char"]), int(row["end_char"])))
    return summary, hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", help="limit to a chapter ID, for example chp-1")
    parser.add_argument(
        "--min-single-word-chars",
        type=int,
        default=6,
        help="ignore shorter single-word candidate labels to reduce generic hits (default: 6)",
    )
    args = parser.parse_args(argv)
    if args.min_single_word_chars < 1:
        parser.error("--min-single-word-chars must be positive")
    summary, hits = audit(args.chapter, args.min_single_word_chars)
    print(json.dumps({"kind": "summary", **summary}, ensure_ascii=False))
    for hit in hits:
        print(json.dumps({"kind": "candidate_surface_hit", **hit}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
