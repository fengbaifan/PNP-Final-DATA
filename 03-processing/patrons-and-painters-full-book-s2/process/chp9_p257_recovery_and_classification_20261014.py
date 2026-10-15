"""Recover p.257 S2 mentions and classify its remaining statements.

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
BACKUP_SOURCE = TABLES / "mentions.csv.bak-s2-chp9-p258-20261001"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
P257 = "chp-9:09_CHP-9_intro:l167-177"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SOURCE_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
P257_SEGMENT_HASH = "57910b1c32121abe9cf27530e7548251827005fa067d300c430d902496245e2c"
NOTES_SEGMENT_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_HASHES = {
    MENTIONS: "40aa0bfa9d0e4a83da013432d7dfb0b4e8f6eecd13b21477d0dbda5b1789594c",
    STATEMENTS: "6200d8a1917b774f517c313ffb14e9ed7770ee94fef4bc8f81a73330e57d2243",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    BACKUP_SOURCE: "c3336c17dee2e82d8dc3de3d9abbbdcdb465b4168981378fc93ed9b967a89ce5",
    SOURCE: SOURCE_HASH,
}
BACKUP_SUFFIX = ".bak-s2-chp9-p257-recovery-20261014"

CLASSIFICATIONS = {
    "st-chp9-p257-cochin-also-admired-tiepolo": True,
    "st-chp9-p257-fragonard-connoisseurs-may-share-distinction": True,
    "st-chp9-p257-french-history-painters-admired-tiepolo": True,
    "st-chp9-p257-french-middle-class-history-painting-revival": True,
    "st-chp9-p257-history-painting-kept-alive-in-venice": True,
    "st-chp9-p257-labia-extravagance-reputation": False,
    "st-chp9-p257-longo-banquet-competitions": True,
    "st-chp9-p257-maria-labia-identifies-with-cleopatra": True,
    "st-chp9-p257-no-venetian-equivalent-to-boucher-fragonard": False,
    "st-chp9-p257-nobility-awareness-and-portraiture-dignity": True,
    "st-chp9-p257-present-day-taste-prefers-bozzetti": False,
    "st-chp9-p257-renier-free-republic-quote": False,
    "st-chp9-p257-tiepolo-delicate-compliment-to-maria": True,
    "st-chp9-p257-tiepolo-moral-commitment-compared-to-rubens": False,
    "st-chp9-p257-vandieres-french-history-painting-purpose": True,
    "st-chp9-p257-venetian-aristocracy-and-tiepolo-as-champion": True,
    "st-chp9-p257-venetian-erotic-painting-comparison": True,
    "st-chp9-p257-note1-longo-memoirs-citation": False,
    "st-chp9-p257-note2-tassini-citation": False,
    "st-chp9-p257-note3-de-brosses-citation": False,
    "st-chp9-p257-note4-marcellino-citation": False,
    "st-chp9-p257-note5-byam-shaw-citation": False,
    "st-chp9-p257-note6-villot-citation": False,
    "st-chp9-p257-note7-levey-citation": False,
}

CLASSIFICATION_REASONS = {
    "st-chp9-p257-cochin-also-admired-tiepolo": "Haskell reports a specific opinion relation between Cochin and Tiepolo; the cited Villot publication was not independently consulted.",
    "st-chp9-p257-fragonard-connoisseurs-may-share-distinction": "Haskell proposes a qualified relation between Fragonard/connoisseurs and their distinction between bozzetti and completed decoration; 'may' is retained and the unnamed group remains open.",
    "st-chp9-p257-french-history-painters-admired-tiepolo": "The source identifies an unnamed group of French history-painting revival advocates as admirers of Tiepolo.",
    "st-chp9-p257-french-middle-class-history-painting-revival": "Haskell links the moral fervour of the French middle classes to the revival of history painting and David's rhetoric; this remains an attributed group-to-genre claim.",
    "st-chp9-p257-history-painting-kept-alive-in-venice": "Haskell links Venetian nobles' political power and dreams to the continuation of history painting in Venice; preserve the author's causal interpretation.",
    "st-chp9-p257-labia-extravagance-reputation": "This is a reputational attribute assigned to the Labia family, not a relation between distinct entities.",
    "st-chp9-p257-longo-banquet-competitions": "Haskell reports a group patronage practice from Antonio Longo's Memoirs; the cited pages were not independently consulted.",
    "st-chp9-p257-maria-labia-identifies-with-cleopatra": "Haskell links Maria Labia to Cleopatra and the pearl-wager story as the allegory's intended identification; retain this as an attributed interpretation.",
    "st-chp9-p257-no-venetian-equivalent-to-boucher-fragonard": "This is a broad comparative absence claim about artists, not a positive entity relationship.",
    "st-chp9-p257-nobility-awareness-and-portraiture-dignity": "Haskell proposes a qualified causal link between Venetian nobles' awareness and the dignity of their portraiture; 'probably' remains explicit.",
    "st-chp9-p257-present-day-taste-prefers-bozzetti": "This is Haskell's present-day taste judgment about bozzetti and full-scale decoration, not a historical entity relationship.",
    "st-chp9-p257-renier-free-republic-quote": "This is a political quotation contrasting forms of civic participation, not a relationship among the project's identified historical entities.",
    "st-chp9-p257-tiepolo-delicate-compliment-to-maria": "Haskell explicitly identifies a relation of intended artistic compliment from Tiepolo to Maria Labia.",
    "st-chp9-p257-tiepolo-moral-commitment-compared-to-rubens": "This is an authorial moral evaluation and analogy; the cause is unspecified and no direct Tiepolo–Rubens relationship is claimed.",
    "st-chp9-p257-vandieres-french-history-painting-purpose": "Haskell quotes Vandières assigning the copied Tiepolo frescoes a purpose for French history painting; this is an attributed person-to-work-purpose relation.",
    "st-chp9-p257-venetian-aristocracy-and-tiepolo-as-champion": "Haskell explicitly relates the Venetian aristocracy's moral fervour to Tiepolo as its champion, while preserving the stated difference in artistic results.",
    "st-chp9-p257-venetian-erotic-painting-comparison": "Haskell proposes a qualified causal relation between Venetian nobles' awareness and the amount of erotic painting; 'probably' and the comparison with French rococo are retained.",
    "st-chp9-p257-note1-longo-memoirs-citation": "This is a bibliographic locator for the banquet-competition report; the cited pages were not independently consulted.",
    "st-chp9-p257-note2-tassini-citation": "This is a bibliographic locator only; Tassini's cited page was not independently consulted.",
    "st-chp9-p257-note3-de-brosses-citation": "This is a bibliographic locator only; De Brosses's cited page was not independently consulted.",
    "st-chp9-p257-note4-marcellino-citation": "This is a bibliographic locator for the quoted description; the cited note was not independently consulted.",
    "st-chp9-p257-note5-byam-shaw-citation": "This is a bibliographic locator for the Vandières quotation; the cited page was not independently consulted.",
    "st-chp9-p257-note6-villot-citation": "This is a bibliographic locator for the Cochin reference; the cited pages were not independently consulted.",
    "st-chp9-p257-note7-levey-citation": "This is a bibliographic locator only; the cited chapter was not independently consulted.",
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
for sid, expected in ((P257, P257_SEGMENT_HASH), (NOTES, NOTES_SEGMENT_HASH)):
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

recovered = [r for r in backup_mentions if r["mention_id"].startswith("m-chp9-p257-")]
if len(recovered) != 65 or len({r["mention_id"] for r in recovered}) != 65:
    raise SystemExit(f"expected 65 unique p.257 mentions in recovery source, found {len(recovered)}")
if Counter(r["segment_id"] for r in recovered) != Counter({P257: 51, NOTES: 14}):
    raise SystemExit("unexpected p.257 mention distribution between body and consolidated notes")

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

body_rows = [r for r in statement_rows if r.get("segment_id") == P257]
note_rows = [r for r in statement_rows if r.get("segment_id") == NOTES and r.get("statement_id", "").startswith("st-chp9-p257-")]
unset_ids = {
    r["statement_id"] for r in body_rows + note_rows
    if r.get("qualifiers", {}).get("relation_candidate") is None
}
if len(body_rows) != 22 or len(note_rows) != 7 or unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.257 statement state: body={len(body_rows)}, notes={len(note_rows)}, unset={sorted(unset_ids)}")

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
if len(statement_rows) != 14829 or status_counts_after.get(None, 0) != status_counts_before.get(None, 0) - 24:
    raise SystemExit(f"unexpected global statement totals: {len(statement_rows)} {status_counts_after}")
if status_counts_after[True] != status_counts_before[True] + 12 or status_counts_after[False] != status_counts_before[False] + 12:
    raise SystemExit(f"unexpected classification totals: {status_counts_after}")

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "recovered_mentions": len(recovered),
    "mention_distribution": dict(Counter(r["segment_id"] for r in recovered)),
    "p257_body_statements": len(body_rows),
    "p257_footnote_statements_in_notes_segment": len(note_rows),
    "p257_classifications_after": {"true": 17, "false": 12, "unset": 0},
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
