"""Clear stale footnote-pending prose for p.279-280 after note migration.

The body records already point to the completed note segment and exact note
line. Citation-only notes have no note statement ID by design; p.280 notes 3,
5, and 7 also link to their extracted note statements. This migration changes
only qualification wording and preserves all caveats about unconsulted works.
Default mode is dry-run; use --apply after reviewing the listed changes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"
NOTES_SEGMENT = "chp-10:10_CHP-10_intro:l491-634"

EXPECTED_TABLE_SHA256 = "73c9093112dc29d5433cff3592f43ea4fdefd7a9e7ec5cc236ca2650de5f8964"
EXPECTED_SOURCE_SHA256 = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_PDF_SHA256 = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENTS = {
    "chp-10:10_CHP-10_intro:l43-49": "f311fdf054bf8adc8fe5bcab01d4a0458950b7f837b4da9af644e1ced09e283b",
    "chp-10:10_CHP-10_intro:l51-61": "877f9ed4cdae9e0e1bc219c8e90b31521e82843d62c83877f5d7a6c2420722c6",
    NOTES_SEGMENT: "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76",
}

REPLACEMENTS = {
    "st-chp10-p279-marco-ricci-manchester-decorate-mansions": (
        "Footnote 1 is pending the later notes segment. ", "",
    ),
    "st-chp10-p279-narford-seat-fountaine": (
        "Footnote 2 is pending the later notes segment. ", "",
    ),
    "st-chp10-p279-pellegrini-manchester-decorate-mansions": (
        "Footnote 1 is pending the later notes segment. ", "",
    ),
    "st-chp10-p279-pellegrini-draws-motteux": (
        "Note 3 is pending the later notes segment; ", "",
    ),
    "st-chp10-p280-bentinck-orange-loyalty-reward": (
        "Footnote 2 remains pending the later notes segment. ",
        "Footnote 2 is transcribed at source L510; the cited Turberville passage was not independently consulted. ",
    ),
    "st-chp10-p280-burlington-grand-tour-and-mansion": (
        "Footnote 6 remains pending. ",
        "Footnote 6 is transcribed at L514; the cited item was not independently consulted. ",
    ),
    "st-chp10-p280-portland-commissioned-pellegrini": (
        "Footnote 1 remains pending the later consolidated notes segment. ",
        "Footnote 1 is transcribed at L510; the cited Vertue passage was not independently consulted. ",
    ),
    "st-chp10-p280-vertue-praises-portland-paintings": (
        "Footnote 4 is pending the notes segment.",
        "P.280 note 4 at L512 cites Vertue, vol. IV, p.48; the cited passage was not independently consulted.",
    ),
    "st-chp10-p280-ricci-early-burlington-employment": (
        "; footnote 5 remains pending the consolidated notes segment.", ".",
    ),
    "st-chp10-p280-ricci-paintings-burlington-house-chiswick": (
        "Footnote 7 later qualifies the transfer as probable; the note is pending and the transfer is not independently verified.",
        "Footnote 7 at L515 reports Haskell's probability that the works at the villa were transferred from the Earl's town house.",
    ),
    "st-chp10-p280-sheffield-title-house-politics": (
        "The source's note 8 remains pending; it is a source trail, not independent corroboration. Complete Peerage and H. Clifford Smith p.26 are citation pointers, not independent verification.",
        "P.280 note 8 at L516 is transcribed as citations to Complete Peerage and H. Clifford Smith, p.26; neither work was independently consulted.",
    ),
}

EXPECTED_LINKS = {
    "st-chp10-p279-marco-ricci-manchester-decorate-mansions": (507, []),
    "st-chp10-p279-narford-seat-fountaine": (508, []),
    "st-chp10-p279-pellegrini-manchester-decorate-mansions": (507, []),
    "st-chp10-p279-pellegrini-draws-motteux": (509, []),
    "st-chp10-p280-bentinck-orange-loyalty-reward": (510, []),
    "st-chp10-p280-burlington-grand-tour-and-mansion": (514, []),
    "st-chp10-p280-portland-commissioned-pellegrini": (510, []),
    "st-chp10-p280-vertue-praises-portland-paintings": (512, []),
    "st-chp10-p280-ricci-early-burlington-employment": (513, [
        "st-chp10-notes-p280n5-presentation-dated-1713",
        "st-chp10-notes-p280n5-susanna-dated-1713",
        "st-chp10-notes-p280n5-presentation-chatsworth",
        "st-chp10-notes-p280n5-susanna-chatsworth",
        "st-chp10-notes-p280n5-devonshire-inherited-burlington-estate",
    ]),
    "st-chp10-p280-ricci-paintings-burlington-house-chiswick": (515, [
        "st-chp10-notes-p280n7-chiswick-villa-began-1725",
        "st-chp10-notes-p280n7-probable-transfer-to-chiswick",
    ]),
    "st-chp10-p280-sheffield-title-house-politics": (516, []),
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write reviewed qualification updates")
    args = parser.parse_args()

    for path, expected in ((TABLE, EXPECTED_TABLE_SHA256), (SOURCE, EXPECTED_SOURCE_SHA256), (PDF, EXPECTED_PDF_SHA256)):
        actual = file_hash(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.name} sha256={actual}")

    segment_rows = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines())
    }
    for segment_id, expected in EXPECTED_SEGMENTS.items():
        if segment_rows.get(segment_id, {}).get("sha256") != expected:
            raise SystemExit(f"precondition failed: segment hash changed: {segment_id}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    expected_note_lines = {
        507: "1 See above all for this whole section Watson",
        508: "2 Vertue, HI, p. 94.",
        509: "3 Mostra di Pellegrini, 1959, p. 56.",
        510: "1 Verme, I, p. 38. 4 Turberville, H, p. 14.",
        511: "3 A sketch for the Last Supper is in the National Gallery of Art",
        512: "4 Vertue, IV, p. 48.",
        513: "5 Ricci dated two pictures for Lord Burlington in 1713.",
        514: "8 Wittkower, 1948.",
        515: "7 Charlton.",
        516: "8 See the Complete Peerage, and H. Clifford Smith, p. 26.",
    }
    for line_number, prefix in expected_note_lines.items():
        if not source_lines[line_number - 1].startswith(prefix):
            raise SystemExit(f"precondition failed: source L{line_number} changed")

    raw_lines = TABLE.read_bytes().splitlines(keepends=True)
    rows = [json.loads(line) for line in raw_lines]
    if len(rows) != 12251:
        raise SystemExit(f"precondition failed: statement count={len(rows)}")
    by_id = {row["statement_id"]: (i, row) for i, row in enumerate(rows)}
    if len(by_id) != len(rows) or not set(REPLACEMENTS) <= set(by_id):
        raise SystemExit("precondition failed: duplicate or missing statement IDs")

    source_markers = {
        "st-chp10-p279-marco-ricci-manchester-decorate-mansions": 1,
        "st-chp10-p279-narford-seat-fountaine": 2,
        "st-chp10-p279-pellegrini-manchester-decorate-mansions": 1,
        "st-chp10-p279-pellegrini-draws-motteux": 3,
        "st-chp10-p280-bentinck-orange-loyalty-reward": 2,
        "st-chp10-p280-burlington-grand-tour-and-mansion": 6,
        "st-chp10-p280-portland-commissioned-pellegrini": 1,
        "st-chp10-p280-vertue-praises-portland-paintings": 4,
        "st-chp10-p280-ricci-early-burlington-employment": 5,
        "st-chp10-p280-ricci-paintings-burlington-house-chiswick": 7,
        "st-chp10-p280-sheffield-title-house-politics": 8,
    }
    plans = {}
    for statement_id, (old, new) in REPLACEMENTS.items():
        _, row = by_id[statement_id]
        q = row.get("qualifiers", {})
        expected_line, expected_note_ids = EXPECTED_LINKS[statement_id]
        expected_segment = "chp-10:10_CHP-10_intro:l43-49" if "p279" in statement_id else "chp-10:10_CHP-10_intro:l51-61"
        if row.get("segment_id") != expected_segment or q.get("footnote_marker") != source_markers[statement_id]:
            raise SystemExit(f"precondition failed: body anchor/marker changed: {statement_id}")
        if q.get("footnote_text_pending") is not False or q.get("footnote_link_status") != "resolved_source_migration":
            raise SystemExit(f"precondition failed: note processing state changed: {statement_id}")
        if q.get("footnote_segment") != NOTES_SEGMENT or q.get("footnote_source_line") != expected_line:
            raise SystemExit(f"precondition failed: note segment/source line changed: {statement_id}")
        if q.get("footnote_note_statement_ids", []) != expected_note_ids:
            raise SystemExit(f"precondition failed: note statement links changed: {statement_id}")
        qualification = q.get("qualification", "")
        if qualification.count(old) != 1:
            raise SystemExit(f"precondition failed: expected stale wording not found once: {statement_id}")
        updated = json.loads(json.dumps(row))
        updated["qualifiers"]["qualification"] = qualification.replace(old, new, 1)
        if re.search(r"\b(?:pending|queued|unreviewed)\b", updated["qualifiers"]["qualification"], re.I):
            raise SystemExit(f"precondition failed: unrelated unresolved status remains in qualification: {statement_id}")
        plans[statement_id] = updated

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "rows": [{
            "statement_id": sid,
            "qualification_before": by_id[sid][1]["qualifiers"]["qualification"],
            "qualification_after": plans[sid]["qualifiers"]["qualification"],
            "note_segment": NOTES_SEGMENT,
            "note_source_line": EXPECTED_LINKS[sid][0],
        } for sid in REPLACEMENTS],
    }, ensure_ascii=True, indent=2))
    if not args.apply:
        return 0

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp10-p279-280-note-status-"))
    backup = backup_dir / "book-statements.jsonl"
    shutil.copy2(TABLE, backup)
    for statement_id, updated in plans.items():
        index, _ = by_id[statement_id]
        line = raw_lines[index]
        newline = b"\r\n" if line.endswith(b"\r\n") else b"\n"
        raw_lines[index] = json.dumps(updated, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline
    TABLE.write_bytes(b"".join(raw_lines))

    written = [json.loads(line) for line in TABLE.read_bytes().splitlines()]
    differences = []
    for before, after in zip(rows, written):
        if before == after:
            continue
        expected_after = plans.get(before["statement_id"])
        if expected_after != after or {k: v for k, v in before.items() if k != "qualifiers"} != {k: v for k, v in after.items() if k != "qualifiers"}:
            shutil.copy2(backup, TABLE)
            raise SystemExit("postcondition failed; restored backup")
        if {k: v for k, v in before["qualifiers"].items() if k != "qualification"} != {k: v for k, v in after["qualifiers"].items() if k != "qualification"}:
            shutil.copy2(backup, TABLE)
            raise SystemExit("postcondition failed; restored backup")
        differences.append(before["statement_id"])
    if set(differences) != set(REPLACEMENTS):
        shutil.copy2(backup, TABLE)
        raise SystemExit("postcondition failed: changed row set differs; restored backup")

    print(f"backup={backup}")
    print(f"table_sha256={file_hash(TABLE)}")
    print(f"rows_changed={len(differences)}; changed_path=qualifiers.qualification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
