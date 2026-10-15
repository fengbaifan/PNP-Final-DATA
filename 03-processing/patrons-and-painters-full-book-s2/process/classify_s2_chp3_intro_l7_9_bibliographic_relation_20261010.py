from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
SEGMENT_ID = "chp-3:03_CHP-3_intro:l7-9"
STATEMENT_ID = "st-chp3-intro-l7-9-galassi-coverage-assessment"
SUBJECT_ID = "cand-4974"
OLD_OBJECT_ID = "cand-0646"
OBJECT_ID = "cand-11570"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp3-intro-l7-9-bibliographic-relation-20261010"
EXPECTED_HASHES = {
    "table": "ddb1ec47851810348cb9a346e74bd39ea025601a9cdc9758538df19c4f428d45",
    "candidates": "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    "mentions": "a2b3f66e5387732c6cdc66a7c9f3d36ac6737db6c76b40a7c3a5a7864477e800",
    "coverage": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "source": "0537ac39d933f5a377f4a1f153ab9cbbf724a448ef76b7f19190d1f95c3e1fda",
    "pdf": "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}
RELATION_NOTE = (
    "Negative bibliographic relation explicitly reported by Haskell: the cited "
    "Galassi Paluzzi study is said not to refer to Horae Subsecivae, the work "
    "identified in the following note. Keep the negation and Haskell's "
    "attribution; this does not verify the cited study's coverage and creates "
    "no formal S6 edge."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def read_jsonl(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    decoded = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in decoded else "\n"
    rows = [json.loads(line) for line in decoded.splitlines() if line.strip()]
    return rows, bom, newline


def serialize_jsonl(rows, bom: bool, newline: str) -> bytes:
    text = newline.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows
    ) + newline
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def relation_counts(rows):
    bilateral = [
        row
        for row in rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
    ]
    true_bilateral = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        for row in bilateral
    )
    false_bilateral = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is False
        for row in bilateral
    )
    pending_bilateral = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is None
        for row in bilateral
    )
    true_total = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        for row in rows
    )
    true_open = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
        for row in rows
    )
    return {
        "bilateral": len(bilateral),
        "classified_relation": true_bilateral,
        "classified_nonrelation": false_bilateral,
        "pending": pending_bilateral,
        "relation_candidates_total": true_total,
        "relation_candidates_open": true_open,
    }


def preflight():
    paths = {
        "table": STATEMENTS,
        "candidates": CANDIDATES,
        "mentions": MENTIONS,
        "coverage": COVERAGE,
        "source": SOURCE,
        "pdf": PDF,
    }
    actual = {name: sha256(path) for name, path in paths.items()}
    if actual != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: expected={EXPECTED_HASHES}; actual={actual}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = [
            row for row in csv.DictReader(handle)
            if row.get("segment_id") == SEGMENT_ID
        ]
    if (
        len(coverage) != 1
        or coverage[0].get("disposition") != "reviewed"
        or coverage[0].get("migration_status") != "complete"
    ):
        raise SystemExit(f"coverage preflight failed: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidates = {row["candidate_id"]: row for row in csv.DictReader(handle)}
    source_candidate = candidates.get(SUBJECT_ID)
    old_object = candidates.get(OLD_OBJECT_ID)
    target_object = candidates.get(OBJECT_ID)
    if not source_candidate or source_candidate.get("suggested_type") != "archive":
        raise SystemExit("cited-study candidate is missing or has an unexpected type")
    if not old_object or old_object.get("canonical_name") != "Chandos, Grey Brydges, 5th Lord":
        raise SystemExit("existing person endpoint did not match the suspected mislink")
    if (
        not target_object
        or target_object.get("suggested_type") != "archive"
        or target_object.get("canonical_name")
        != "Horae Subsecivae (edition unspecified; pp. 386 ff. cited)"
    ):
        raise SystemExit("Horae archive candidate is missing or has an unexpected identity")

    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        mentions = {row["mention_id"]: row for row in csv.DictReader(handle)}
    subject_mention = mentions.get("m-chp3-intro-l7-9-0001")
    object_mention = mentions.get("m-chp3-intro-l7-9-0005")
    if (
        not subject_mention
        or subject_mention.get("candidate_id") != SUBJECT_ID
        or subject_mention.get("surface_form") != "Galassi Paluzzi, 1951"
        or not object_mention
        or object_mention.get("candidate_id") != OBJECT_ID
        or object_mention.get("surface_form") != "Horae Subsecivae"
    ):
        raise SystemExit("source mention-to-candidate mapping changed")

    rows, bom, newline = read_jsonl(STATEMENTS)
    selected = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
    if len(selected) != 1:
        raise SystemExit(f"expected one target statement, found {len(selected)}")
    row = selected[0]
    q = row.get("qualifiers") or {}
    if (
        row.get("segment_id") != SEGMENT_ID
        or row.get("predicate") != "bibliographic_coverage_assessment"
        or row.get("subject_candidate_id") != SUBJECT_ID
        or row.get("object_candidate_id") != OLD_OBJECT_ID
        or q.get("relation_candidate") is not None
        or q.get("negation") is not True
    ):
        raise SystemExit("target statement state changed or no longer matches review")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    start, end = q.get("source_line_start"), q.get("source_line_end")
    if (start, end) != (8, 8):
        raise SystemExit(f"unexpected source line anchor: {(start, end)}")
    anchor = normalize("\n".join(source_lines[start - 1:end]))
    if normalize(row.get("original_quote", "")) not in anchor:
        raise SystemExit("source quote does not match its anchored line")
    if "does not refer to the book mentioned in the next note" not in anchor:
        raise SystemExit("expected negative cross-reference wording is absent")
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    before_counts = relation_counts(rows)
    expected_before = {
        "bilateral": 8500,
        "classified_relation": 4486,
        "classified_nonrelation": 459,
        "pending": 3555,
        "relation_candidates_total": 4516,
        "relation_candidates_open": 30,
    }
    if before_counts != expected_before:
        raise SystemExit(f"unexpected relation counts before write: {before_counts}")

    for candidate_id in (SUBJECT_ID, OBJECT_ID):
        if candidate_id not in candidates:
            raise SystemExit(f"statement endpoint candidate is missing: {candidate_id}")

    preview_rows = []
    for current in rows:
        if current.get("statement_id") != STATEMENT_ID:
            preview_rows.append(current)
            continue
        updated = dict(current)
        updated["object_candidate_id"] = OBJECT_ID
        updated_qualifiers = dict(updated.get("qualifiers") or {})
        updated_qualifiers["mentioned_candidate_ids"] = [SUBJECT_ID, OBJECT_ID]
        updated_qualifiers["relation_candidate"] = True
        updated_qualifiers["relation_candidate_note"] = RELATION_NOTE
        updated["qualifiers"] = updated_qualifiers
        preview_rows.append(updated)

    after_counts = relation_counts(preview_rows)
    expected_after = {
        "bilateral": 8500,
        "classified_relation": 4487,
        "classified_nonrelation": 459,
        "pending": 3554,
        "relation_candidates_total": 4517,
        "relation_candidates_open": 30,
    }
    if after_counts != expected_after:
        raise SystemExit(f"unexpected projected relation counts: {after_counts}")
    return rows, preview_rows, bom, newline, actual, before_counts, after_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows, preview_rows, bom, newline, hashes, before_counts, after_counts = preflight()
    preview = {
        "statement_id": STATEMENT_ID,
        "before": {
            "subject_candidate_id": SUBJECT_ID,
            "object_candidate_id": OLD_OBJECT_ID,
            "relation_candidate": None,
        },
        "after": {
            "subject_candidate_id": SUBJECT_ID,
            "object_candidate_id": OBJECT_ID,
            "mentioned_candidate_ids": [SUBJECT_ID, OBJECT_ID],
            "relation_candidate": True,
            "relation_candidate_note": RELATION_NOTE,
        },
        "counts_before": before_counts,
        "counts_after": after_counts,
    }
    if args.dry_run:
        print(json.dumps({"preflight": "passed", "hashes": hashes, "change": preview}, ensure_ascii=False, indent=2))
        return

    shutil.copy2(STATEMENTS, BACKUP)
    STATEMENTS.write_bytes(serialize_jsonl(preview_rows, bom, newline))
    written_rows, _, _ = read_jsonl(STATEMENTS)
    target = [row for row in written_rows if row.get("statement_id") == STATEMENT_ID]
    if (
        len(target) != 1
        or target[0].get("object_candidate_id") != OBJECT_ID
        or (target[0].get("qualifiers") or {}).get("relation_candidate") is not True
    ):
        raise SystemExit("post-write target verification failed; recovery backup preserved")
    verified_counts = relation_counts(written_rows)
    if verified_counts != after_counts:
        raise SystemExit(f"post-write count verification failed: {verified_counts}")
    print(json.dumps({
        "applied": 1,
        "backup": str(BACKUP.relative_to(ROOT)),
        "before_sha256": hashes["table"],
        "after_sha256": sha256(STATEMENTS),
        "verified_counts": verified_counts,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
