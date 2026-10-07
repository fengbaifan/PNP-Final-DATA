"""Repair the stale body-statement target on the Chapter 4 Salerno note."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
INTRO = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_intro.md"
BODY_SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-4.pdf"

NOTE_ID = "st-chp4-intro-notes-02-salerno-citation"
OLD_BODY_ID = "st-chp4-sec-i-l3-4-collection"
BODY_ID = "st-chp4-sec-i-l3-4-collection-ranking"

EXPECTED_HASHES = {
    STATEMENTS: "682a71330f1d21894e68b40294c8dbbbcb7016123a20a66ad74a71ab7b67c1c2",
    INTRO: "6703a3c57834a1ec42d3c292d3883571c9f17c67831b38570125b588d225b40b",
    BODY_SOURCE: "3961adefb7ea2e1f2e44e02173a494c509964e7273b6b3867619643bbd9ecb64",
    PDF: "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows() -> list[dict]:
    return [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def by_id(rows: list[dict]) -> dict[str, dict]:
    result = {row["statement_id"]: row for row in rows}
    if len(result) != len(rows):
        raise SystemExit("duplicate statement_id in book-statements.jsonl")
    return result


def write_rows(rows: list[dict]) -> None:
    with STATEMENTS.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed citation-body link repair")
args = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"hash lock failed for {path.relative_to(ROOT)}: {actual}")

intro_lines = INTRO.read_text(encoding="utf-8").splitlines()
body_lines = BODY_SOURCE.read_text(encoding="utf-8").splitlines()
if "2 Salerno" not in intro_lines[11]:
    raise SystemExit("unexpected p.94 note 2 source text")
if "Marchese Giustiniani (Plate 17b).2" not in body_lines[2]:
    raise SystemExit("unexpected p.94 body anchor at S0 L3")

rows = read_rows()
indexed = by_id(rows)
if NOTE_ID not in indexed or BODY_ID not in indexed:
    raise SystemExit("Salerno note or current Giustiniani body statement is missing")
if OLD_BODY_ID in indexed:
    raise SystemExit("old body target unexpectedly exists; review before relinking")

note = indexed[NOTE_ID]
nq = note.get("qualifiers", {})
body = indexed[BODY_ID]
bq = body.get("qualifiers", {})
if nq.get("citation_body_statement_id") != OLD_BODY_ID:
    raise SystemExit("unexpected current Salerno citation target")
if (body.get("segment_id"), bq.get("source_line_start"), bq.get("printed_page_locator"), bq.get("pdf_physical_page"), bq.get("footnote_marker")) != (
    "chp-4:04_CHP-4_sec_i:l3-4", 3, "p.94 inferred from index; no printed folio on physical page 1", 1, 2
):
    raise SystemExit("current Giustiniani statement no longer matches the p.94 note anchor")

updated = copy.deepcopy(rows)
by_id(updated)[NOTE_ID]["qualifiers"]["citation_body_statement_id"] = BODY_ID

print("verified p.94 note 2 and its Giustiniani collection body anchor against S0 and CHP-4.pdf")
print("planned repair: replace one obsolete citation_body_statement_id with the current statement ID")
print("expected table effect: update 1 existing statement qualifier; no rows or counts change")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp4-salerno-citation-link-"))
shutil.copy2(STATEMENTS, backup_dir / STATEMENTS.name)
write_rows(updated)
written = by_id(read_rows())
if written[NOTE_ID]["qualifiers"].get("citation_body_statement_id") != BODY_ID:
    raise SystemExit(f"post-write citation target verification failed; backup: {backup_dir}")
if len(written) != len(rows):
    raise SystemExit(f"post-write statement count changed; backup: {backup_dir}")
print(f"applied Salerno citation-body link repair; recovery copy: {backup_dir}")
