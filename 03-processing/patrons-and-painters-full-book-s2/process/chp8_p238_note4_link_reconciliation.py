"""Link p.238 note 4 to the body statements in its marked sentence.

The note's phrase "These pictures" remains ambiguous as to whether it refers
to the two genre scenes alone or also the preceding satirical picture. The
source marker applies to the sentence containing both body statements, so this
migration records the note-to-sentence links without resolving that referent.
Default mode is dry-run; use --apply after reviewing the displayed change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"

EXPECTED_TABLE_SHA256 = "b7b2f5e920b29fd16c743d4e7ecfcbf982966cd3b10e7b87ae703d87b421fc7a"
EXPECTED_SOURCE_SHA256 = "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6"
EXPECTED_PDF_SHA256 = "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3"
BODY_SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l327-336"
NOTE_SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l372-461"
EXPECTED_BODY_SEGMENT_SHA256 = "4851272f69e09219355eb926cb06e76ed40d459db5efebd44dc83df1e9ebfacb"
EXPECTED_NOTE_SEGMENT_SHA256 = "62a4611253d2bf05494ef55b0511b53861b0947a05aee1c7a9fdbab976ecbc3f"
NOTE_ID = "st-chp8-p238-note4-pictures-at-pisa-cabinet"
BODY_IDS = [
    "st-chp8-p238-silva-satirical-picture",
    "st-chp8-p238-genre-scenes-and-subject-popularity",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed link after preconditions pass")
    args = parser.parse_args()

    for path, expected in (
        (TABLE, EXPECTED_TABLE_SHA256),
        (SOURCE, EXPECTED_SOURCE_SHA256),
        (PDF, EXPECTED_PDF_SHA256),
    ):
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.name} sha256={actual}")

    segments = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines())
    }
    if segments[BODY_SEGMENT_ID].get("sha256") != EXPECTED_BODY_SEGMENT_SHA256:
        raise SystemExit("precondition failed: body segment hash changed")
    if segments[NOTE_SEGMENT_ID].get("sha256") != EXPECTED_NOTE_SEGMENT_SHA256:
        raise SystemExit("precondition failed: note segment hash changed")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if not source_lines[331].rstrip().endswith("century.4"):
        raise SystemExit("precondition failed: printed footnote marker 4 moved from body line 332")
    note_text = source_lines[445]
    if not note_text.startswith("4 These pictures are") or "Gabinetto del R. Intendente di Finanza di Pisa" not in note_text:
        raise SystemExit("precondition failed: footnote 4 text changed")

    raw_lines = TABLE.read_bytes().splitlines(keepends=True)
    rows = [json.loads(line) for line in raw_lines]
    if len(rows) != 12251:
        raise SystemExit(f"precondition failed: statement count={len(rows)}")
    by_id = {row["statement_id"]: (index, row) for index, row in enumerate(rows)}
    if len(by_id) != len(rows):
        raise SystemExit("precondition failed: duplicate statement_id")
    if NOTE_ID not in by_id or any(body_id not in by_id for body_id in BODY_IDS):
        raise SystemExit("precondition failed: expected statement is missing")

    note_index, note = by_id[NOTE_ID]
    note_q = note.get("qualifiers", {})
    if note.get("segment_id") != NOTE_SEGMENT_ID or note_q.get("source_line_start") != 446 or note_q.get("source_line_end") != 446:
        raise SystemExit("precondition failed: note statement anchor changed")
    if note_q.get("footnote_marker") != 4 or note_q.get("linked_body_statement_ids"):
        raise SystemExit("precondition failed: note marker or existing links changed")

    for body_id in BODY_IDS:
        _, body = by_id[body_id]
        q = body.get("qualifiers", {})
        if body.get("segment_id") != BODY_SEGMENT_ID or q.get("source_line_start") != 332 or q.get("source_line_end") != 332:
            raise SystemExit(f"precondition failed: body anchor changed for {body_id}")
        if not q.get("relation_candidate"):
            raise SystemExit(f"precondition failed: relation-candidate marker missing for {body_id}")

    updated = json.loads(json.dumps(note))
    updated["qualifiers"]["linked_body_statement_ids"] = BODY_IDS
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "statement_id": NOTE_ID,
        "linked_body_statement_ids": BODY_IDS,
        "qualification_unchanged": updated["qualifiers"].get("qualification") == note_q.get("qualification"),
        "relationship_endpoints_unchanged": [updated.get("subject_candidate_id"), updated.get("object_candidate_id")] == [note.get("subject_candidate_id"), note.get("object_candidate_id")],
    }, ensure_ascii=True, indent=2))
    if not args.apply:
        return 0

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp8-p238-note4-link-"))
    backup = backup_dir / "book-statements.jsonl"
    shutil.copy2(TABLE, backup)
    old_line = raw_lines[note_index]
    newline = b"\r\n" if old_line.endswith(b"\r\n") else b"\n"
    raw_lines[note_index] = json.dumps(updated, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline
    TABLE.write_bytes(b"".join(raw_lines))

    written = [json.loads(line) for line in TABLE.read_bytes().splitlines()]
    changed = [
        (before["statement_id"], before, after)
        for before, after in zip(rows, written)
        if before != after
    ]
    if len(changed) != 1 or changed[0][0] != NOTE_ID:
        shutil.copy2(backup, TABLE)
        raise SystemExit("postcondition failed; restored backup")
    after_q = changed[0][2]["qualifiers"]
    if after_q.get("linked_body_statement_ids") != BODY_IDS or after_q.get("qualification") != note_q.get("qualification"):
        shutil.copy2(backup, TABLE)
        raise SystemExit("postcondition failed; restored backup")

    print(f"backup={backup}")
    print(f"table_sha256={sha256(TABLE)}")
    print("rows_changed=1; changed_path=qualifiers.linked_body_statement_ids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
