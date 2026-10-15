"""Restore the p.268 S2 mention rows and close its open classifications."""
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
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BODY_BACKUP = TABLES / "mentions.csv.bak-s2-chp9-notes-p268-p275-20261002"
LEGACY_NOTE_SPEC = PROCESS / "chp9_p268_p275_notes_migration.py"
BODY_SEGMENT = "chp-9:09_CHP-9_sec_ii:l6-16"
NOTES_SEGMENT = "chp-9:09_CHP-9_sec_ii:l85-127"

EXPECTED_HASHES = {
    MENTIONS: "f126fcd14999e5f5f2c6944e5dc37fc1742ba460596f23264d61c3503fcbe552",
    STATEMENTS: "da21244669fc14a25b98b9cd18cec118960090dfa78ff2acc6abf4c528cb4355",
    COVERAGE: "d9573522d08a67975f946c7c91878c7b3e2198c1108eefcc11b40ab1f9eaf414",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    BODY_BACKUP: "d9a81391d871228faba35176e19eab145ab85733f88b556881365864e059c32e",
    LEGACY_NOTE_SPEC: "8c02184e04b490be86791aca891241bd1d77e1d466374ea34b6bff4a477ab3b3",
}
SEGMENT_HASHES = {
    BODY_SEGMENT: "011ed62e984b1e67c23bc2e36b88e9957fae9c3f97458a06918a4b75254853f8",
    NOTES_SEGMENT: "d00ced6fff3f96f5cf574f47f45eea80ef1b6867c581d7d017f217ee2a8a5a99",
}
BACKUP_SUFFIX = ".bak-s2-chp9-p268-reconciliation-20261014"

# Recovered from the p.268 rows in the hash-pinned legacy note migration spec.
NOTE_MENTIONS = [
    ("m-chp9-notes-silhouette156", "cand-8773", 86, "Etienne de Silhouette", "P.268 note 1 citation locator."),
    ("m-chp9-notes-tabacco123", "cand-8774", 87, "Tabacco, p. 123", "P.268 note 2 citation locator."),
    ("m-chp9-notes-burney140", "cand-8775", 88, "Burney, I, p. 140", "P.268 note 4 citation locator."),
    ("m-chp9-notes-coggiola304", "cand-8776", 89, "Coggiola-Pittoni, 193 5, p. 304", "P.268 note 5 citation locator; preserve the S0 OCR reading."),
    ("m-chp9-notes-ferrari1882", "cand-8777", 89, "L. Ferrari, 1882, p. 22", "P.268 note 5 citation locator."),
    ("m-chp9-notes-benigna_memoir", "cand-8778", 89, "Biblioteca Marciana, MS. Itai. Cl. VII, 1620", "Manuscript locator cited by Haskell; not independently consulted."),
    ("m-chp9-notes-benigna_person", "cand-8779", 89, "Antonio Benigna", "Compiler named in the cited manuscript; identity alignment remains for S3."),
    ("m-chp9-notes-manini_brothers", "cand-8780", 89, "Fratelli Co:Co:Manini", "Preserve the source's abbreviated family name; identity alignment remains for S3."),
    ("m-chp9-notes-zanetti_may1743", "cand-8781", 90, "22 Maggio 1743", "Date locator for the cited Zanetti report; publication not independently consulted."),
    ("m-chp9-note-extra-001", "cand-8778", 89, "Libri di Memorie", "Title of the quoted Benigna manuscript; not independently consulted."),
    ("m-chp9-note-extra-002", "cand-8827", 89, "[of the Jesuit Chuch]", "Haskell's bracketed building identification; preserve the S0 OCR reading and editorial status."),
]

CLASSIFICATIONS = {
    "st-chp9-p268-church-altarpiece-market": True,
    "st-chp9-p268-cignaroli-saints-claim": True,
    "st-chp9-p268-clergy-land-income-comparison": False,
    "st-chp9-p268-n01": False,
    "st-chp9-p268-n01-silhouette-piety-rhetoric": False,
    "st-chp9-p268-n02": False,
    "st-chp9-p268-n03": False,
    "st-chp9-p268-n04": False,
    "st-chp9-p268-n05": False,
    "st-chp9-p268-n06": False,
    "st-chp9-p268-observer-complaint-partial": False,
    "st-chp9-p268-property-transfer-ban-1767": True,
    "st-chp9-p268-traveller-younger-sons": True,
    "st-chp9-p268-venetian-piety-lavishness": False,
}
REASONS = {
    "st-chp9-p268-church-altarpiece-market": "S2: Haskell explicitly links Church demand for altarpieces to a market for modern painting; preserve the broad comparison without inferring individual commissions.",
    "st-chp9-p268-cignaroli-saints-claim": "S2: the attributed claim links Cignaroli's reported output to religious subjects; retain 'it was claimed' and 'must have' as qualifications.",
    "st-chp9-p268-clergy-land-income-comparison": "S2: this is an aggregate population and income comparison, not a formal relation between identified entities.",
    "st-chp9-p268-n01": "S2: bibliographic citation locator only; it does not itself assert a historical relation.",
    "st-chp9-p268-n01-silhouette-piety-rhetoric": "S2: this is a rhetorical interpretation of visible piety, not a concrete relation between identified entities.",
    "st-chp9-p268-n02": "S2: bibliographic citation locator only; the cited page was not independently consulted.",
    "st-chp9-p268-n03": "S2: bibliographic citation locator only; the cited page was not independently consulted.",
    "st-chp9-p268-n04": "S2: bibliographic citation locator only; the cited page was not independently consulted.",
    "st-chp9-p268-n05": "S2: this statement records a citation chain; the Benigna content is represented in separate source-level statements.",
    "st-chp9-p268-n06": "S2: this is a source locator and observer attribution, not the reported complaint's substantive content.",
    "st-chp9-p268-observer-complaint-partial": "S2: p.268 contains only the opening fragment of Zanetti's reported complaint; the substantive continuation is recorded at p.269.",
    "st-chp9-p268-property-transfer-ban-1767": "S2: Haskell reports an explicit 1767 policy forbidding secular property from passing into clerical ownership.",
    "st-chp9-p268-traveller-younger-sons": "S2: the attributed report connects noble younger sons with a lack of acceptable occupation; preserve the unnamed traveller and group-level generalization.",
    "st-chp9-p268-venetian-piety-lavishness": "S2: this is Haskell's broad interpretive distinction about piety and outward display, not a formal entity relation.",
}
EXPECTED_GLOBAL_BEFORE = {True: 9684, False: 4018, None: 1127}


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
for segment_id, expected in SEGMENT_HASHES.items():
    meta = segments.get(segment_id)
    if meta is None or meta["sha256"] != expected or meta["asset_sha256"] != EXPECTED_HASHES[SOURCE]:
        raise SystemExit(f"unexpected reviewed source segment: {segment_id}")

candidate_fields, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
current_mention_ids = {row["mention_id"] for row in current_mentions}
if len(current_mention_ids) != len(current_mentions):
    raise SystemExit("duplicate mention IDs already exist")

_, backup_rows = read_csv(BODY_BACKUP)
new_mentions = [row.copy() for row in backup_rows if row["segment_id"] == BODY_SEGMENT]
if len(new_mentions) != 39 or len({row["mention_id"] for row in new_mentions}) != 39:
    raise SystemExit(f"expected 39 unique p.268 body mentions, found {len(new_mentions)}")
if any(row["mention_id"] in current_mention_ids for row in new_mentions):
    raise SystemExit("one or more p.268 body mentions are already present")

def segment_text(segment_id):
    meta = segments[segment_id]
    return "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])


def segment_line_offset(segment_id, line_no):
    meta = segments[segment_id]
    if not meta["line_start"] <= line_no <= meta["line_end"]:
        raise SystemExit(f"line {line_no} is outside {segment_id}")
    return sum(len(source_lines[n - 1]) + 1 for n in range(meta["line_start"], line_no))


notes_text = segment_text(NOTES_SEGMENT)
for mention_id, candidate_id, line_no, surface, note in NOTE_MENTIONS:
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown note candidate: {mention_id} -> {candidate_id}")
    line = source_lines[line_no - 1]
    pos = line.find(surface)
    if pos < 0 or line.find(surface, pos + 1) >= 0:
        raise SystemExit(f"note surface missing or ambiguous on L{line_no}: {surface!r}")
    start = segment_line_offset(NOTES_SEGMENT, line_no) + pos
    end = start + len(surface)
    if notes_text[start:end] != surface:
        raise SystemExit(f"invalid p.268 note source span: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": NOTES_SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in current_mentions}
new_ids, new_spans = set(), set()
for row in new_mentions:
    if row["mention_id"] in current_mention_ids or row["mention_id"] in new_ids:
        raise SystemExit(f"duplicate mention ID: {row['mention_id']}")
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"unknown candidate: {row['mention_id']} -> {row['candidate_id']}")
    span = (row["segment_id"], row["start_char"], row["end_char"])
    if span in existing_spans or span in new_spans:
        raise SystemExit(f"duplicate exact mention span: {row['mention_id']}")
    if segment_text(row["segment_id"])[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"source-span mismatch: {row['mention_id']}")
    new_ids.add(row["mention_id"])
    new_spans.add(span)

p268_unset = {
    row["statement_id"] for row in statement_rows
    if row["statement_id"].startswith("st-chp9-p268-")
    and row.get("qualifiers", {}).get("relation_candidate") is None
}
if p268_unset != set(CLASSIFICATIONS) or set(CLASSIFICATIONS) != set(REASONS):
    raise SystemExit(f"unexpected p.268 unset statements: {sorted(p268_unset)}")
for statement_id, value in CLASSIFICATIONS.items():
    qualifiers = statement_by_id[statement_id]["qualifiers"]
    if qualifiers.get("relation_candidate") is not None:
        raise SystemExit(f"statement is no longer unset: {statement_id}")
    qualifiers["relation_candidate"] = value
    qualification = qualifiers.get("qualification", "").strip()
    reason = REASONS[statement_id]
    if reason not in qualification:
        qualifiers["qualification"] = (qualification + " " + reason).strip()

before = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in read_jsonl(STATEMENTS))
after = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in statement_rows)
if dict(before) != EXPECTED_GLOBAL_BEFORE:
    raise SystemExit(f"unexpected global classification baseline: {dict(before)}")
if after[True] != before[True] + 4 or after[False] != before[False] + 10 or after[None] != before[None] - 14:
    raise SystemExit(f"unexpected classification delta: before={dict(before)}, after={dict(after)}")

body_coverage = coverage_by_id.get(BODY_SEGMENT)
notes_coverage = coverage_by_id.get(NOTES_SEGMENT)
if body_coverage is None or body_coverage["migration_status"] != "complete":
    raise SystemExit(f"unexpected p.268 body coverage: {body_coverage}")
if notes_coverage is None or notes_coverage["migration_status"] != "complete":
    raise SystemExit(f"unexpected p.268-275 note coverage before reconciliation: {notes_coverage}")
body_coverage["note"] += (
    " 2026-10-14 reconciliation restored 39 omitted p.268 body mentions from the hash-pinned migration backup; "
    "source spans and candidate IDs were checked. Classified 14 open p.268 statements: 4 relation candidates and 10 non-relational claims/source references."
)
notes_coverage["migration_status"] = "partial"
notes_coverage["note"] += (
    " 2026-10-14 reconciliation found that the consolidated p.268-275 note segment was marked complete although "
    "its mentions were absent. Restored the 11 p.268 note mentions and checked their source spans/candidate IDs; "
    "p.269-275 note mentions remain to be reconciled, so coverage is partial until that work is complete."
)

summary = {
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "printed_page": 268,
    "pdf_physical_page": 34,
    "recovered_mentions": len(new_mentions),
    "recovered_body_mentions": 39,
    "recovered_note_mentions": 11,
    "classified_statements": {"true": 4, "false": 10, "unset_closed": 14},
    "global_mentions_after": len(current_mentions) + len(new_mentions),
    "global_statements": len(statement_rows),
    "global_classifications_after": {"true": after[True], "false": after[False], "unset": after[None]},
    "notes_segment_status_after": notes_coverage["migration_status"],
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the verified p.268 S2 reconciliation")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, STATEMENTS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more p.268 reconciliation backups already exist")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    try:
        write_csv(MENTIONS, mention_fields, current_mentions + new_mentions)
        write_jsonl(STATEMENTS, statement_rows)
        write_csv(COVERAGE, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; recovery backups: " + ", ".join(path.name for path in backups))
