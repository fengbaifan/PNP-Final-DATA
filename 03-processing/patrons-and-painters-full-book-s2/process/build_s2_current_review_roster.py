#!/usr/bin/env python3
"""Build a source-ordered, version-bound S2 current-statement review roster."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
REVIEW_REPORT = (
    "03-processing/patrons-and-painters-full-book-s2/process/"
    "s2-independent-review-chp1-2-4-20261020.md"
)
REVIEW_SNAPSHOT = "2273e274"
BATCHES = {
    "S2-B001-CH2-SEC-II-L118-145": {
        "chp-2:02_CHP-2_sec_ii:l118-125",
        "chp-2:02_CHP-2_sec_ii:l127-139",
        "chp-2:02_CHP-2_sec_ii:l141-145",
    },
    "S2-B002-CH2-SEC-II-L147-193": {"chp-2:02_CHP-2_sec_ii:l147-193"},
    "S2-B003-CH2-VISUAL-AND-SEC-IV-L3-17": {
        "chp-2:02_CHP-2_sec_ii_visual-transcription:l1-3",
        "chp-2:02_CHP-2_sec_ii_visual-transcription:l8-9",
        "chp-2:02_CHP-2_sec_iv:l3-4",
        "chp-2:02_CHP-2_sec_iv:l6-17",
    },
    "S2-B004-CH2-SEC-IV-L19-43": {
        "chp-2:02_CHP-2_sec_iv:l19-29",
        "chp-2:02_CHP-2_sec_iv:l31-43",
    },
}
SEGMENT_BATCH = {
    segment_id: batch_id
    for batch_id, segment_ids in BATCHES.items()
    for segment_id in segment_ids
}
BATCH_STATEMENT_OVERRIDES = {
    statement_id: "S2-B004-CH2-SEC-IV-L19-43"
    for statement_id in (
        [f"st-chp2-seciv-l190-245-citation-{number:02d}" for number in range(5, 19)]
        + [
            "st-chp2-seciv-l190-245-poussin-lost-and-current-locations",
            "st-chp2-seciv-l190-245-valentin-picture-location",
            "st-chp2-seciv-l190-245-valentin-inventory-1631",
            "st-chp2-seciv-l190-245-valentin-published-thuillier-1958",
            "st-chp2-seciv-l190-245-valentin-exhibition-1961",
            "st-chp2-seciv-l190-245-vouet-election",
            "st-chp2-seciv-l190-245-poussin-germanicus-current-location",
            "st-chp2-seciv-l190-245-second-capture-current-location",
        ]
    )
}

FIELDS = [
    "current_order",
    "snapshot_commit",
    "statement_id",
    "chapter",
    "section",
    "source_id",
    "source_file",
    "segment_id",
    "source_line_start",
    "source_line_end",
    "segment_sha256",
    "source_asset_sha256",
    "snapshot_statement_sha256",
    "current_statement_sha256",
    "snapshot_segment_mention_count",
    "snapshot_segment_mentions_sha256",
    "current_segment_mention_count",
    "current_segment_mentions_sha256",
    "history_9622_membership",
    "prior_review_match",
    "prior_review_ref",
    "current_review_status",
    "review_batch_id",
    "review_outcome",
    "review_evidence_ref",
    "follow_up_note",
]


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def canonical_hash(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_git_jsonl(revision: str, relative_path: str) -> list[dict]:
    raw = subprocess.check_output(
        ["git", "show", f"{revision}:{relative_path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8-sig",
    )
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="s2-current-review-roster.csv")
    args = parser.parse_args()

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / "03-processing/patrons-and-painters-full-book-s2/process" / output
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing roster: {output}")

    statements_path = "04-knowledge/tables/book-statements.jsonl"
    segments_path = "04-knowledge/tables/segments.jsonl"
    statements = read_jsonl(ROOT / statements_path)
    segments = read_jsonl(ROOT / segments_path)
    with (TABLES / "mentions.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as stream:
        mentions = list(csv.DictReader(stream))

    statement_ids = [row["statement_id"] for row in statements]
    if len(statement_ids) != len(set(statement_ids)):
        raise SystemExit("Duplicate statement_id in current table")

    current_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    old_statements = read_git_jsonl(REVIEW_SNAPSHOT, statements_path)
    old_segments = read_git_jsonl(REVIEW_SNAPSHOT, segments_path)
    old_statement_hashes = {
        row["statement_id"]: canonical_hash(row) for row in old_statements
    }
    old_segment_hashes = {
        row["segment_id"]: row["sha256"] for row in old_segments
    }

    segment_by_id = {row["segment_id"]: row for row in segments}
    segment_order = {row["segment_id"]: index for index, row in enumerate(segments)}
    if len(segment_by_id) != len(segments):
        raise SystemExit("Duplicate segment_id in current table")

    mentions_by_segment: dict[str, list[dict]] = defaultdict(list)
    for mention in mentions:
        mentions_by_segment[mention["segment_id"]].append(mention)
    mention_hashes = {
        segment_id: canonical_hash(sorted(rows, key=lambda row: row["mention_id"]))
        for segment_id, rows in mentions_by_segment.items()
    }

    ordered_statements = sorted(
        statements,
        key=lambda row: (
            segment_order.get(row["segment_id"], len(segments)),
            int(row.get("qualifiers", {}).get("source_line_start") or 0),
            int(row.get("qualifiers", {}).get("source_line_end") or 0),
            row["statement_id"],
        ),
    )
    if any(row["segment_id"] not in segment_by_id for row in statements):
        raise SystemExit("A statement references a missing S0 segment")

    rows_by_batch = {
        batch_id: [
            row
            for row in ordered_statements
            if row["segment_id"] in segment_ids
            or BATCH_STATEMENT_OVERRIDES.get(row["statement_id"]) == batch_id
        ]
        for batch_id, segment_ids in BATCHES.items()
    }
    expected_batch_counts = {
        "S2-B001-CH2-SEC-II-L118-145": 100,
        "S2-B002-CH2-SEC-II-L147-193": 85,
        "S2-B003-CH2-VISUAL-AND-SEC-IV-L3-17": 53,
        "S2-B004-CH2-SEC-IV-L19-43": 75,
    }
    for batch_id, expected in expected_batch_counts.items():
        found = len(rows_by_batch[batch_id])
        if found != expected:
            raise SystemExit(f"Expected {expected} statements in {batch_id}; found {found}")
    batch_ids = {
        batch_id: {row["statement_id"] for row in rows}
        for batch_id, rows in rows_by_batch.items()
    }

    output_rows: list[dict[str, str]] = []
    counts = defaultdict(int)
    for order, statement in enumerate(ordered_statements, start=1):
        segment = segment_by_id[statement["segment_id"]]
        chapter = segment["chapter"]
        statement_hash = canonical_hash(statement)
        exact_old_object = old_statement_hashes.get(statement["statement_id"]) == statement_hash
        exact_old_segment = old_segment_hashes.get(segment["segment_id"]) == segment["sha256"]

        assigned_batch = BATCH_STATEMENT_OVERRIDES.get(
            statement["statement_id"], SEGMENT_BATCH.get(statement["segment_id"], "")
        )
        if chapter in {"chp-1", "chp-2"} and exact_old_object and exact_old_segment:
            prior_match = "exact_object_and_source_segment"
            prior_ref = f"{REVIEW_REPORT}; scope={chapter}"
            current_status = "prior_review_mapped_open"
            follow_up = (
                "Prior report covers this exact ID and source segment; Chapter 2 remains unaccepted, "
                "and chapter-level follow-up subsets still need ID-level mapping."
                if chapter == "chp-2"
                else "Prior report states all 521 chapter statements were read; Chapter 1 remains unaccepted."
            )
        elif assigned_batch:
            prior_match = "current_object_differs_or_scope_unmapped"
            prior_ref = REVIEW_REPORT
            current_status = "in_batch"
            follow_up = "Current continuous-text batch; awaiting independent review result."
        else:
            prior_match = (
                "current_object_differs"
                if statement["statement_id"] in old_statement_hashes
                else "no_exact_review_mapping"
            )
            prior_ref = ""
            current_status = "needs_crosswalk"
            follow_up = "Map explicit prior review evidence to this exact current ID/version or review it."

        counts[current_status] += 1
        output_rows.append(
            {
                "current_order": str(order),
                "snapshot_commit": current_commit,
                "statement_id": statement["statement_id"],
                "chapter": chapter,
                "section": segment["section"],
                "source_id": segment["source_id"],
                "source_file": segment["source_file"],
                "segment_id": segment["segment_id"],
                "source_line_start": str(statement.get("qualifiers", {}).get("source_line_start", "")),
                "source_line_end": str(statement.get("qualifiers", {}).get("source_line_end", "")),
                "segment_sha256": segment["sha256"],
                "source_asset_sha256": segment.get("asset_sha256", ""),
                "snapshot_statement_sha256": statement_hash,
                "current_statement_sha256": statement_hash,
                "snapshot_segment_mention_count": str(len(mentions_by_segment.get(segment["segment_id"], []))),
                "snapshot_segment_mentions_sha256": mention_hashes.get(segment["segment_id"], canonical_hash([])),
                "current_segment_mention_count": str(len(mentions_by_segment.get(segment["segment_id"], []))),
                "current_segment_mentions_sha256": mention_hashes.get(segment["segment_id"], canonical_hash([])),
                "history_9622_membership": "unknown",
                "prior_review_match": prior_match,
                "prior_review_ref": prior_ref,
                "current_review_status": current_status,
                "review_batch_id": assigned_batch,
                "review_outcome": "",
                "review_evidence_ref": "",
                "follow_up_note": follow_up,
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"roster={output.relative_to(ROOT).as_posix()}")
    print(f"snapshot_commit={current_commit}")
    print(f"current_statement_ids={len(output_rows)}")
    print(f"previous_review_exact_mapped={counts['prior_review_mapped_open']}")
    print(f"needs_crosswalk_or_review={counts['needs_crosswalk']}")
    print(f"batch_01_rows={len(rows_by_batch['S2-B001-CH2-SEC-II-L118-145'])}")
    print(f"batch_02_rows={len(rows_by_batch['S2-B002-CH2-SEC-II-L147-193'])}")
    print(f"batch_03_rows={len(rows_by_batch['S2-B003-CH2-VISUAL-AND-SEC-IV-L3-17'])}")
    print(f"batch_04_rows={len(rows_by_batch['S2-B004-CH2-SEC-IV-L19-43'])}")
    print("historical_9622_membership=unknown for all rows")


if __name__ == "__main__":
    main()
