"""Recover p.259 mentions and finish its S2 relation-candidate decisions.

Defaults to a read-only preflight. The printed page and its notes were reviewed
against CHP-9.pdf physical page 21; mention spans are checked against S0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BACKUP_SOURCE = TABLES / "mentions.csv.bak-s2-chp9-p260-20261001"
P259 = "chp-9:09_CHP-9_intro:l188-200"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SOURCE_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
P259_SEGMENT_HASH = "717631e0c86fc16769da90d83e6363ce28a3576fbe24c8be41eb46d2d6958d2b"
NOTES_SEGMENT_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_HASHES = {
    MENTIONS: "9ee4780ca2567f60d8844ee2139b158e7ca4fab9f90ff3a4e807c2324bfa3205",
    STATEMENTS: "0325066b73165487da3ffa2f71d4428eefc4f48573833d9da681efd7ef4b245f",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    BACKUP_SOURCE: "9f4aa94529742a35f2dacc85f968a21a03497dd610f22b2b2d8f96a2663d0bd7",
    SOURCE: SOURCE_HASH,
}
BACKUP_SUFFIX = ".bak-s2-chp9-p259-recovery-20261014"

# True means a source-grounded relation candidate for later S6 review. False
# retains the S2 assertion without proposing a formal relation.
CLASSIFICATIONS = {
    "st-chp9-p259-batoni-classicism-and-venetian-taste": False,
    "st-chp9-p259-contemporaries-saw-old-virtues": False,
    "st-chp9-p259-foscarini-doge-accession-suspected": False,
    "st-chp9-p259-foscarini-proud-cultivated-and-scholarly": False,
    "st-chp9-p259-leading-artists-exception": False,
    "st-chp9-p259-marco-library-versus-pictures": True,
    "st-chp9-p259-note1-querini-cross-reference": False,
    "st-chp9-p259-note2-fontana-citation": False,
    "st-chp9-p259-note3-visconti-letter-citation": True,
    "st-chp9-p259-note4-pietro-picture-inventory-location": True,
    "st-chp9-p259-note4-pietro-will-inventory-location": True,
    "st-chp9-p259-note6-clark-citation": False,
    "st-chp9-p259-triumph-as-encouragement-from-past": True,
    "st-chp9-p259-triumph-depicts-arts-republic-history-fame": True,
    "st-chp9-p259-triumph-depicts-sages-and-warrior": True,
    "st-chp9-p259-triumph-exalted-state-over-family": True,
    "st-chp9-p259-triumph-programme-venetian-recovery": True,
}

REASONS = {
    "st-chp9-p259-batoni-classicism-and-venetian-taste": "S2: this is Haskell's authorial style judgment about the painting and its relation to Venetian taste; retain the qualified evaluation without turning it into a broader artist or audience relation.",
    "st-chp9-p259-contemporaries-saw-old-virtues": "S2: this is an attributed characterization of Foscarini by unnamed contemporaries, paralleling the page's character judgments; it is not an independently measured relation or consensus.",
    "st-chp9-p259-foscarini-doge-accession-suspected": "S2: the sentence records suspicion about the methods of Foscarini's accession but supplies no method, agent, or positive relation to assert.",
    "st-chp9-p259-foscarini-proud-cultivated-and-scholarly": "S2: this is an authorial character and taste assessment; the source does not identify a separate endpoint for a historical relation.",
    "st-chp9-p259-leading-artists-exception": "S2: Haskell gives a qualified negative generalization ('unlikely', 'with one exception') about unidentified artists; retain it as content and leave any specific employment to separately supported statements.",
    "st-chp9-p259-marco-library-versus-pictures": "S2: the possessive and the reported attention explicitly link Foscarini to his source-described library and its Venetian-history contents; do not promote this candidate to a formal ownership edge without later review.",
    "st-chp9-p259-note1-querini-cross-reference": "S2: this is an editorial cross-reference to another chapter, not an additional historical relation or independent evidence.",
    "st-chp9-p259-note2-fontana-citation": "S2: bibliographic locator only; the cited page was not independently consulted and the surname/work remain unresolved.",
    "st-chp9-p259-note3-visconti-letter-citation": "S2: the note names a specific letter, its sender and addressee, and its publication locator; retain the archive-to-participant relation candidate while recording that the letter and publication were not independently consulted.",
    "st-chp9-p259-note4-pietro-picture-inventory-location": "S2: the note explicitly locates a named archival inventory at Biblioteca Correr under the cited shelfmark; retain as a source-reported archive-location candidate, not an independently checked custody fact.",
    "st-chp9-p259-note4-pietro-will-inventory-location": "S2: the note explicitly locates Pietro Foscarini's will at Biblioteca Correr under the cited shelfmark; retain as a source-reported archive-location candidate, not an independently checked custody fact.",
    "st-chp9-p259-note6-clark-citation": "S2: this is a bibliographic pointer to Clark's discussion, not a historical relation; the named picture's repository claim is preserved separately.",
    "st-chp9-p259-triumph-as-encouragement-from-past": "S2: Haskell explicitly interprets the painting's subject as relating Foscarini's political outlook to Venice's past; preserve this as the author's reading, not a direct statement of Foscarini's intention.",
    "st-chp9-p259-triumph-depicts-arts-republic-history-fame": "S2: this explicitly describes iconographic subjects and their arrangement in the painting; retain work-to-subject candidates without treating the allegorical composition as a political event or inferring extra edges among figures.",
    "st-chp9-p259-triumph-depicts-sages-and-warrior": "S2: this explicitly describes figures and represented content in the painting; retain work-to-subject candidates while leaving generic sages and warrior unidentified and treating the scene as iconography.",
    "st-chp9-p259-triumph-exalted-state-over-family": "S2: Haskell explicitly interprets the painting as exalting the Venetian State rather than the patron's family; preserve the attributed work-to-subject/theme relation and the comparative qualification.",
    "st-chp9-p259-triumph-programme-venetian-recovery": "S2: the quoted programme links the painting to a represented account of Venice's recovery, peace, arts, and Doge Loredano; keep it as an attributed programme/subject candidate, not an independently verified historical account.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(f.name)
    temp_path.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(f.name)
    temp_path.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"fingerprint changed; inspect before continuing: {path.relative_to(ROOT)}")

segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
for sid, expected in ((P259, P259_SEGMENT_HASH), (NOTES, NOTES_SEGMENT_HASH)):
    meta = segments.get(sid)
    if not meta or meta["sha256"] != expected or meta["asset_sha256"] != SOURCE_HASH:
        raise SystemExit(f"unexpected source-segment metadata: {sid}")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()

_, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
_, backup_mentions = read_csv(BACKUP_SOURCE)
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
if len(statement_by_id) != len(statement_rows):
    raise SystemExit("statement IDs are not unique")

recovered = [row for row in backup_mentions if row["mention_id"].startswith("m-chp9-p259-")]
if len(recovered) != 67 or len({row["mention_id"] for row in recovered}) != 67:
    raise SystemExit(f"expected 67 unique p.259 backup mentions, found {len(recovered)}")
if Counter(row["segment_id"] for row in recovered) != Counter({P259: 47, NOTES: 20}):
    raise SystemExit("unexpected p.259 mention distribution across body and consolidated notes")

current_ids = {row["mention_id"] for row in current_mentions}
current_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in current_mentions}
for row in recovered:
    sid = row["segment_id"]
    meta = segments.get(sid)
    if not meta or row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"missing source segment or candidate for {row['mention_id']}")
    segment_text = "\n".join(source_lines[meta["line_start"] - 1 : meta["line_end"]])
    start, end = int(row["start_char"]), int(row["end_char"])
    if start < 0 or end <= start or segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"source-span mismatch for {row['mention_id']}")
    if row["mention_id"] in current_ids or (sid, row["start_char"], row["end_char"]) in current_spans:
        raise SystemExit(f"mention ID or source span already exists: {row['mention_id']}")

page_rows = [row for row in statement_rows if row.get("segment_id") == P259]
page_and_note_rows = [row for row in statement_rows if row.get("statement_id", "").startswith("st-chp9-p259-")]
unset_ids = {row["statement_id"] for row in page_and_note_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
if len(page_rows) != 20 or len(page_and_note_rows) != 29 or unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.259 statement state: body={len(page_rows)}, all={len(page_and_note_rows)}, unset={sorted(unset_ids)}")

for statement_id, value in CLASSIFICATIONS.items():
    row = statement_by_id[statement_id]
    qualifiers = row["qualifiers"]
    qualifiers["relation_candidate"] = value
    reason = REASONS[statement_id]
    qualification = qualifiers.get("qualification", "").strip()
    if reason not in qualification:
        qualifiers["qualification"] = (qualification + " " + reason).strip()

before = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in read_jsonl(STATEMENTS))
after = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in statement_rows)
if before.get(None, 0) - after.get(None, 0) != 17:
    raise SystemExit(f"unexpected global classification delta: before={before}, after={after}")
if after[True] != before[True] + 9 or after[False] != before[False] + 8:
    raise SystemExit(f"unexpected global classification counts: {after}")

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "page": 259,
    "recovered_mentions": len(recovered),
    "mention_distribution": dict(Counter(row["segment_id"] for row in recovered)),
    "p259_body_statements": len(page_rows),
    "p259_statement_classifications_after": {
        "true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in page_and_note_rows),
        "false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in page_and_note_rows),
        "unset": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in page_and_note_rows),
    },
    "global_statement_count": len(statement_rows),
    "global_classifications_after": {"true": after[True], "false": after[False], "unset": after.get(None, 0)},
}, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write recovered mentions and reviewed classifications")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, STATEMENTS]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("a p.259 recovery backup already exists; inspect before applying")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    try:
        write_csv(MENTIONS, mention_fields, current_mentions + recovered)
        write_jsonl(STATEMENTS, statement_rows)
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; recovery backups: " + ", ".join(str(path.relative_to(ROOT)) for path in backups))
