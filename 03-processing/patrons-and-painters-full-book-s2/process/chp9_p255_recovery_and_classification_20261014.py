"""Recover p.255 S2 mentions and classify its remaining statements.

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
BACKUP_SOURCE = TABLES / "mentions.csv.bak-s2-chp9-p256-20261001"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
P255 = "chp-9:09_CHP-9_intro:l148-155"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SOURCE_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
P255_SEGMENT_HASH = "f88796ddd6e409c8850bf64361d76760ed61b8c36cc02b18a32bfe7b35010e3d"
NOTES_SEGMENT_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_HASHES = {
    MENTIONS: "230ce35743916ac9612d7c95f9f23a383961f7726bf1bff9e20efe5fc43f97c8",
    STATEMENTS: "b903771dba7b7b02ce7386c1d690fbc4fbab718605a83935dba1c90b1cafeea5",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    BACKUP_SOURCE: "fbfdec2b26cd72d43e46de9da8b1f7f63caebc43f54b85cfd085cdf1d8ae3928",
    SOURCE: SOURCE_HASH,
}
BACKUP_SUFFIX = ".bak-s2-chp9-p255-recovery-20261014"

CLASSIFICATIONS = {
    "st-chp9-p255-pisani-allegory-dated-1762": False,
    "st-chp9-p255-robespierre-aged-four": False,
    "st-chp9-p255-artist-initiative-in-subject-choice": True,
    "st-chp9-p255-wealthy-nobles-access-to-flattery": False,
    "st-chp9-p255-ancestral-glorification-older-aristocracy": False,
    "st-chp9-p255-time-as-suggestive-family-symbol": True,
    "st-chp9-p255-old-families-followed-historical-subjects": True,
    "st-chp9-p255-social-prestige-over-military-prowess": False,
    "st-chp9-p255-allusive-forms-of-patron-flattery": False,
    "st-chp9-p255-few-model-decoration-discrepancies": False,
    "st-chp9-p255-lorenzi-story-qualified-as-possibly-apocryphal": False,
    "st-chp9-p255-modelli-presented-for-inspection": True,
    "st-chp9-p255-novelli-chose-collalto-subject": True,
    "st-chp9-p255-painter-not-bound-too-rigidly": False,
    "st-chp9-p255-contracts-and-consultation-limits": False,
    "st-chp9-p255-note2-da-canal-citation": False,
    "st-chp9-p255-note4-contarini-work-location-label": True,
}

CLASSIFICATION_REASONS = {
    "st-chp9-p255-pisani-allegory-dated-1762": "This supplies a year for a work, a scalar date attribute rather than an entity-to-entity relationship.",
    "st-chp9-p255-robespierre-aged-four": "This is a biographical age statement, not a relationship candidate.",
    "st-chp9-p255-artist-initiative-in-subject-choice": "Haskell explicitly describes artist agency in choosing subjects in at least some cases and links the claim to examples in note 1; the claim is not assigned solely to Tiepolo.",
    "st-chp9-p255-wealthy-nobles-access-to-flattery": "This is a broad statement about access to patronal flattery, not a specific commission or identifiable entity pair.",
    "st-chp9-p255-ancestral-glorification-older-aristocracy": "This is a general social-historical characterization of a subject type, not a sufficiently specific entity relationship.",
    "st-chp9-p255-time-as-suggestive-family-symbol": "Haskell explicitly links the personified figure of Time to a family's age, wisdom, and virtue; no particular family or work is inferred.",
    "st-chp9-p255-old-families-followed-historical-subjects": "Haskell states that other old families followed the Corner's historical-subject commissions, while contrasting the means of Widmann and Grassi; no additional family or commission is inferred.",
    "st-chp9-p255-social-prestige-over-military-prowess": "This is Haskell's interpretive comparison of social and military prestige, not a relation between identifiable entities.",
    "st-chp9-p255-allusive-forms-of-patron-flattery": "This is a general observation about ways of flattering patrons, with no specific patron, artist, or work identified.",
    "st-chp9-p255-few-model-decoration-discrepancies": "This is a general comparison of proposed modelli and completed decorations; it does not identify a particular model-work pair.",
    "st-chp9-p255-lorenzi-story-qualified-as-possibly-apocryphal": "This is Haskell's qualification and inference about artistic freedom; the reported Tiepolo scheme is separately recorded as a relation candidate.",
    "st-chp9-p255-modelli-presented-for-inspection": "Haskell explicitly describes a work process in which Venetian artists prepare modelli for patrons to inspect; the participants are generic and remain open.",
    "st-chp9-p255-novelli-chose-collalto-subject": "Haskell reports a specific artist-to-subject choice attributed to Novelli's Memoirs; the cited page was not independently consulted.",
    "st-chp9-p255-painter-not-bound-too-rigidly": "This is Haskell's general inference about artistic freedom, not a specific artist-patron relationship.",
    "st-chp9-p255-contracts-and-consultation-limits": "This is a methodological caveat and generalized inference about consultation; no specific patron-painter pair is identified.",
    "st-chp9-p255-note2-da-canal-citation": "This is a bibliographic citation locator only; the cited page was not independently consulted.",
    "st-chp9-p255-note4-contarini-work-location-label": "Haskell's note gives a location label for the Contarini work; this remains a source-reported location candidate, not present-day collection verification.",
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
for sid, expected in ((P255, P255_SEGMENT_HASH), (NOTES, NOTES_SEGMENT_HASH)):
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

recovered = [r for r in backup_mentions if r["mention_id"].startswith("m-chp9-p255-")]
if len(recovered) != 74 or len({r["mention_id"] for r in recovered}) != 74:
    raise SystemExit(f"expected 74 unique p.255 mentions in recovery source, found {len(recovered)}")
if Counter(r["segment_id"] for r in recovered) != Counter({P255: 60, NOTES: 14}):
    raise SystemExit("unexpected p.255 mention distribution between body and consolidated notes")

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

body_rows = [r for r in statement_rows if r.get("segment_id") == P255]
note_rows = [r for r in statement_rows if r.get("segment_id") == NOTES and r.get("statement_id", "").startswith("st-chp9-p255-")]
unset_ids = {
    r["statement_id"] for r in body_rows + note_rows
    if r.get("qualifiers", {}).get("relation_candidate") is None
}
if len(body_rows) != 24 or len(note_rows) != 5 or unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.255 statement state: body={len(body_rows)}, notes={len(note_rows)}, unset={sorted(unset_ids)}")

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
if len(statement_rows) != 14829 or status_counts_after.get(None, 0) != status_counts_before.get(None, 0) - 17:
    raise SystemExit(f"unexpected global statement totals: {len(statement_rows)} {status_counts_after}")
if status_counts_after[True] != status_counts_before[True] + 6 or status_counts_after[False] != status_counts_before[False] + 11:
    raise SystemExit(f"unexpected classification totals: {status_counts_after}")

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "recovered_mentions": len(recovered),
    "mention_distribution": dict(Counter(r["segment_id"] for r in recovered)),
    "p255_body_statements": len(body_rows),
    "p255_footnote_statements_in_notes_segment": len(note_rows),
    "p255_classifications_after": {"true": 17, "false": 12, "unset": 0},
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
