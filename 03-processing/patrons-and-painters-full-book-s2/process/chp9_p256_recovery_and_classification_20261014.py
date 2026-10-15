"""Recover p.256 S2 mentions and classify its remaining statements.

Defaults to a read-only preflight. Use --apply only after reviewing the summary.
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
BACKUP_SOURCE = TABLES / "mentions.csv.bak-s2-chp9-p257-20261001"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
P256 = "chp-9:09_CHP-9_intro:l157-165"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SOURCE_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
P256_SEGMENT_HASH = "2962dfdf9f25c1a0a8e2fa89b192fe3d26b5118a976e05a05f8812fa1bdf6c50"
NOTES_SEGMENT_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_HASHES = {
    MENTIONS: "e6657039c7c80ec22a26d5aa5a562c78ec204a956db8278c9b90a4073b3ec035",
    STATEMENTS: "062b4ac7a305a343bfc37f1b9c4e6066ac6a2685d0220fbd0c7a08421f5903c3",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    BACKUP_SOURCE: "646bfbb230570c4f08eec4ff1df7b487807c32910b7ae98d4c1e43d0ee93d09f",
    SOURCE: SOURCE_HASH,
}
BACKUP_SUFFIX = ".bak-s2-chp9-p256-recovery-20261014"

CLASSIFICATIONS = {
    "st-chp9-p256-antiquity-offered-exhilarating-scenes": False,
    "st-chp9-p256-banquet-as-aristocratic-extravagance-against-political-economy": True,
    "st-chp9-p256-banquet-glorifies-cleopatra-over-antony": True,
    "st-chp9-p256-classical-repertoire-codified-for-aristocratic-virtues": True,
    "st-chp9-p256-classical-scenes-may-have-precise-meanings": False,
    "st-chp9-p256-cordellina-described-as-leading-advocate": True,
    "st-chp9-p256-cordellina-lifestyle-and-wife": False,
    "st-chp9-p256-goldoni-lawyers-status": True,
    "st-chp9-p256-gozzi-literary-equivalent": True,
    "st-chp9-p256-patrician-families-claimed-roman-descent": True,
    "st-chp9-p256-sacrifice-theme-links-melodrama-and-power": True,
    "st-chp9-p256-sandi-ennobled-1685": False,
    "st-chp9-p256-sandi-fortunes-linked-to-law": True,
    "st-chp9-p256-state-officials-heard-roman-hero-comparisons": True,
    "st-chp9-p256-tiepolo-irritated-by-cordellina-entertainment": True,
    "st-chp9-p256-wall-paintings-allude-to-cordellina-magnanimity": True,
    "st-chp9-p256-note1-correr-manuscript-locator": False,
    "st-chp9-p256-note2-morassi-citation": False,
    "st-chp9-p256-note3-goldoni-memoirs-citation": False,
    "st-chp9-p256-note4-fontanella-citation": False,
    "st-chp9-p256-note5-tiepolo-letter-publication": True,
    "st-chp9-p256-note6-pietro-loredan-orazione": True,
    "st-chp9-p256-note7-antonio-loredan-orazione": True,
}

CLASSIFICATION_REASONS = {
    "st-chp9-p256-antiquity-offered-exhilarating-scenes": "This is Haskell's general characterization of classical subject matter, not a relation between identified entities.",
    "st-chp9-p256-banquet-as-aristocratic-extravagance-against-political-economy": "Haskell explicitly interprets the Banquet theme as an allusion to Venice's policy and aristocratic extravagance against contemporary political economy; this remains his attributed interpretation.",
    "st-chp9-p256-banquet-glorifies-cleopatra-over-antony": "The source connects the Banquet subject to Cleopatra and Antony and describes their roles in the represented narrative.",
    "st-chp9-p256-classical-repertoire-codified-for-aristocratic-virtues": "The source links the Greek and Roman story repertory to aristocratic virtues and to later artists' use of it; this remains a broad book-based relation candidate.",
    "st-chp9-p256-classical-scenes-may-have-precise-meanings": "This is a modal methodological interpretation about unspecified scenes and unknown meanings, not a relation among identifiable entities.",
    "st-chp9-p256-cordellina-described-as-leading-advocate": "The source assigns the named Cordellina a specific professional role.",
    "st-chp9-p256-cordellina-lifestyle-and-wife": "This is a biographical characterization of Cordellina's preferences and household behavior, not a separate formal relationship claim.",
    "st-chp9-p256-goldoni-lawyers-status": "Haskell reports a profession-to-status comparison attributed to Goldoni's Memoirs; the cited passage was not independently consulted.",
    "st-chp9-p256-gozzi-literary-equivalent": "Haskell explicitly links the reactionary manifesto's meaning to writings by Carlo Gozzi; this remains an attributed cross-media interpretation.",
    "st-chp9-p256-patrician-families-claimed-roman-descent": "The source states a group-level genealogy claim about patrician families; individual families and ancestry are not inferred.",
    "st-chp9-p256-sacrifice-theme-links-melodrama-and-power": "Haskell explicitly links the Sacrifice theme to contemporary melodrama and responsibilities of power; the general theme remains the stated endpoint.",
    "st-chp9-p256-sandi-ennobled-1685": "This is a date/status attribute for the Sandi, with no ennobling agent identified.",
    "st-chp9-p256-sandi-fortunes-linked-to-law": "The source explicitly links the Sandi family's fortunes to the legal profession.",
    "st-chp9-p256-state-officials-heard-roman-hero-comparisons": "The source describes a group-level rhetorical relation between state officials and comparisons to Roman heroes; the named cases remain separately represented.",
    "st-chp9-p256-tiepolo-irritated-by-cordellina-entertainment": "Haskell attributes a specific reaction by Tiepolo to the entertainment practices of Cordellina.",
    "st-chp9-p256-wall-paintings-allude-to-cordellina-magnanimity": "Haskell explicitly interprets the named wall paintings as allusions to their patron Cordellina's magnanimity; retain this as an attributed work-to-patron-meaning candidate.",
    "st-chp9-p256-note1-correr-manuscript-locator": "This is a manuscript citation locator only; the manuscript's content was not independently consulted.",
    "st-chp9-p256-note2-morassi-citation": "This is a bibliographic locator for Morassi; the note's four represented subjects are recorded separately and the cited pages were not consulted.",
    "st-chp9-p256-note3-goldoni-memoirs-citation": "This is a bibliographic locator only; Goldoni's cited passage was not independently consulted.",
    "st-chp9-p256-note4-fontanella-citation": "This is a bracketed source-name locator only; no independent bibliographic identity is inferred.",
    "st-chp9-p256-note5-tiepolo-letter-publication": "Haskell's note identifies a Tiepolo-to-Algarotti letter and its reported publication; retain this as a source-based correspondence/publication candidate, not independent verification.",
    "st-chp9-p256-note6-pietro-loredan-orazione": "The cited title identifies an oration for Pietro Loredan's departure to Legnano; retain this as a source-based work-to-person/event candidate, not independent verification.",
    "st-chp9-p256-note7-antonio-loredan-orazione": "The cited title identifies a Padua oration addressed to Antonio Loredan concerning his departure from office; retain this as a source-based work-to-person/event candidate, with no year inferred.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"fingerprint changed; inspect before continuing: {path.relative_to(ROOT)}")

segments = {r["segment_id"]: r for r in read_jsonl(SEGMENTS)}
for sid, expected in ((P256, P256_SEGMENT_HASH), (NOTES, NOTES_SEGMENT_HASH)):
    if sid not in segments or segments[sid]["sha256"] != expected or segments[sid]["asset_sha256"] != SOURCE_HASH:
        raise SystemExit(f"unexpected source segment metadata: {sid}")

candidate_fields, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {r["candidate_id"] for r in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
_, backup_mentions = read_csv(BACKUP_SOURCE)
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {r["statement_id"]: r for r in statement_rows}
if len(statement_by_id) != len(statement_rows):
    raise SystemExit("statement IDs are not unique")

recovered = [r for r in backup_mentions if r["mention_id"].startswith("m-chp9-p256-")]
if len(recovered) != 85 or len({r["mention_id"] for r in recovered}) != 85:
    raise SystemExit(f"expected 85 unique p.256 mentions in recovery source, found {len(recovered)}")
if Counter(r["segment_id"] for r in recovered) != Counter({P256: 54, NOTES: 31}):
    raise SystemExit("unexpected p.256 mention distribution between body and consolidated notes")

current_ids = {r["mention_id"] for r in current_mentions}
current_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in current_mentions}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for row in recovered:
    sid = row["segment_id"]
    meta = segments.get(sid)
    if meta is None or row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"missing segment or candidate for {row['mention_id']}")
    text = "\n".join(source_lines[meta["line_start"] - 1 : meta["line_end"]])
    start, end = int(row["start_char"]), int(row["end_char"])
    if start < 0 or end <= start or text[start:end] != row["surface_form"]:
        raise SystemExit(f"source span mismatch for {row['mention_id']}")
    if row["mention_id"] in current_ids or (sid, row["start_char"], row["end_char"]) in current_spans:
        raise SystemExit(f"mention ID or source span already exists: {row['mention_id']}")

body_rows = [r for r in statement_rows if r.get("segment_id") == P256]
note_rows = [r for r in statement_rows if r.get("segment_id") == NOTES and r.get("statement_id", "").startswith("st-chp9-p256-")]
unset_ids = {
    r["statement_id"] for r in body_rows + note_rows
    if r.get("qualifiers", {}).get("relation_candidate") is None
}
if len(body_rows) != 29 or len(note_rows) != 11 or unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.256 statement state: body={len(body_rows)}, notes={len(note_rows)}, unset={sorted(unset_ids)}")

for sid, value in CLASSIFICATIONS.items():
    row = statement_by_id[sid]
    qualifiers = row["qualifiers"]
    qualifiers["relation_candidate"] = value
    reason = CLASSIFICATION_REASONS[sid]
    existing = qualifiers.get("qualification", "").strip()
    if reason not in existing:
        qualifiers["qualification"] = (existing + " " + reason).strip()

status_counts_before = Counter(r.get("qualifiers", {}).get("relation_candidate") for r in read_jsonl(STATEMENTS))
status_counts_after = Counter(r.get("qualifiers", {}).get("relation_candidate") for r in statement_rows)
if len(statement_rows) != 14829 or status_counts_after.get(None, 0) != status_counts_before.get(None, 0) - 23:
    raise SystemExit(f"unexpected global statement totals: {len(statement_rows)} {status_counts_after}")
if status_counts_after[True] != status_counts_before[True] + 15 or status_counts_after[False] != status_counts_before[False] + 8:
    raise SystemExit(f"unexpected classification totals: {status_counts_after}")

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "recovered_mentions": len(recovered),
    "mention_distribution": dict(Counter(r["segment_id"] for r in recovered)),
    "p256_body_statements": len(body_rows),
    "p256_footnote_statements_in_notes_segment": len(note_rows),
    "p256_classifications_after": {"true": 32, "false": 8, "unset": 0},
    "global_statement_count_after": len(statement_rows),
    "global_classifications_after": {"true": status_counts_after[True], "false": status_counts_after[False], "unset": status_counts_after.get(None, 0)},
}, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write recovered mentions and reviewed classifications")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, STATEMENTS]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("a recovery backup already exists; inspect before applying")
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
