from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l372-461"
SOURCE_STATEMENT_ID = "st-chp8-p222-n1-manuscript-source"
REPOSITORY_STATEMENT_ID = "st-chp8-p222-n1-manuscript-repository"
MENTION_ID = "m-chp8-p222-n1-ariostea"
SOURCE_FILE = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
OLD_CLAIM = "Haskell says his account of the Archbishop's palace is taken from Collezione Antonelli MS 610 in Biblioteca Ariostea, Ferrara."
NEW_CLAIM = "Haskell says his account of the Archbishop's palace is taken from the manuscript Collezione Antonelli MS 610."


def atomic_write(path: Path, content: str):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    temporary.replace(path)


rows = [
    json.loads(line)
    for line in STATEMENTS.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
if any(row["statement_id"] == REPOSITORY_STATEMENT_ID for row in rows):
    raise SystemExit(f"statement already exists: {REPOSITORY_STATEMENT_ID}")
source_row = next((row for row in rows if row["statement_id"] == SOURCE_STATEMENT_ID), None)
if source_row is None or source_row["subject_candidate_id"] != "cand-2962" or source_row["object_candidate_id"] != "cand-7711":
    raise SystemExit("source-use statement changed since review")
if source_row["qualifiers"].get("claim") != OLD_CLAIM:
    raise SystemExit("source-use claim changed since review")
if source_row["original_quote"] == "":
    raise SystemExit("source-use original quote is missing")

segments = [
    json.loads(line)
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
segment = next(row for row in segments if row["segment_id"] == SEGMENT_ID)
if segment["source_file"] != SOURCE_FILE or hashlib.sha256(SOURCE.read_bytes()).hexdigest() != segment["asset_sha256"]:
    raise SystemExit("source or segment metadata changed")
segment_text = "\n".join(SOURCE.read_text(encoding="utf-8-sig").splitlines()[int(segment["line_start"]) - 1:int(segment["line_end"])])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit("source segment hash mismatch")
quote = "It is a manuscript in the Biblioteca Ariostea, Ferrara—Collezione Antonelli MS. 610"
if quote not in segment_text:
    raise SystemExit("repository evidence span not found in the current source segment")

with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as stream:
    mentions = list(csv.DictReader(stream))
if not any(row["mention_id"] == MENTION_ID and row["candidate_id"] == "cand-7712" for row in mentions):
    raise SystemExit("restored repository mention is missing")

repository_row = {
    "statement_id": REPOSITORY_STATEMENT_ID,
    "segment_id": SEGMENT_ID,
    "subject_candidate_id": "cand-7711",
    "object_candidate_id": "cand-7712",
    "predicate": "manuscript_reported_at_library",
    "qualifiers": {
        "source_line_start": 382,
        "source_line_end": 382,
        "printed_page": 222,
        "pdf_physical_page": 24,
        "claim": "Haskell reports Collezione Antonelli MS. 610 as a manuscript in the Biblioteca Ariostea, Ferrara.",
        "speaker": "Haskell",
        "text_layer": "footnote report",
        "qualification": "This is Haskell's reported repository/location statement; no independent catalogue or current holding check was made.",
        "mentioned_candidate_ids": ["cand-7711", "cand-7712"],
        "footnote_marker": 1,
        "printed_page_locator": "p.222 n.1",
        "relation_candidate": True,
        "relation_candidate_note": "The note says the manuscript is in Biblioteca Ariostea, Ferrara. Preserve the manuscript and institution as distinct endpoints; S6 must resolve the repository/custody versus physical-location predicate boundary.",
    },
    "original_quote": quote,
    "origin": "book",
    "source_file": SOURCE_FILE,
}

preview = {
    "mode": "dry-run",
    "updated_current_statement": {
        "statement_id": SOURCE_STATEMENT_ID,
        "claim_before": OLD_CLAIM,
        "claim_after": NEW_CLAIM,
        "original_quote_preserved": True,
    },
    "added_relation_candidate": repository_row,
    "independent_review": "required for this current S2 version delta; unified reviewed-ledger count unchanged",
}

parser = argparse.ArgumentParser(description="Split the cited manuscript source and repository facts into S2 endpoint statements.")
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 row update")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

source_row["qualifiers"]["claim"] = NEW_CLAIM
source_index = rows.index(source_row)
rows.insert(source_index + 1, repository_row)
atomic_write(STATEMENTS, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
