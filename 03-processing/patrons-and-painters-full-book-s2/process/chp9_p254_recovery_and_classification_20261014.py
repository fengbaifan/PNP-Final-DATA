"""Recover p.254 S2 mentions and classify its remaining statements.

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
BACKUP_SOURCE = TABLES / "mentions.csv.bak-s2-chp9-p255-20261001"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
P254 = "chp-9:09_CHP-9_intro:l134-146"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SOURCE_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
P254_SEGMENT_HASH = "eb1487c89b2d4870fe0c30240ce67972acec96ea7dbbebbccd1192a691f43382"
NOTES_SEGMENT_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_HASHES = {
    MENTIONS: "2773871e5e8d463125fcc15ba323e342ccd9e7bd18552cbd728fb284601b6105",
    STATEMENTS: "48a9a6882a9cbdbf538c03f3e81e608f742fc3d3c9c335f8d379844e768ba01b",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    BACKUP_SOURCE: "a355d1022bc4c70255eb0efb14ecfefb9d9dc5e361fbf55c709ea6a4d2a29bc6",
    SOURCE: SOURCE_HASH,
}
BACKUP_SUFFIX = ".bak-s2-chp9-p254-recovery-20261014"

BODY_CLASSIFICATIONS = {
    "st-chp9-p254-family-virtues-and-pictorial-neighbours": True,
    "st-chp9-p254-living-family-portraits-in-frescoes": True,
    "st-chp9-p254-pisani-palace-comparison": False,
    "st-chp9-p254-private-deeds-and-dream-world": False,
    "st-chp9-p254-solar-chariot-scene": True,
    "st-chp9-p254-tense-world-and-life-fantasy-gap": False,
    "st-chp9-p254-tiepolo-allegorical-calendar": True,
}
NOTE_CLASSIFICATIONS = {
    "st-chp9-p254-note1-giussani-reference": False,
    "st-chp9-p254-note1-livan-reference": False,
    "st-chp9-p254-note3-brunelli-callegari-reference": False,
    "st-chp9-p254-note4-novelli-reference": False,
    "st-chp9-p254-note5-muraro-reference": False,
    "st-chp9-p254-note5-tabacco-reference": False,
    "st-chp9-p254-note6-gallo-reference": False,
    "st-chp9-p254-note7-moschini-reference": False,
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
for sid, expected in ((P254, P254_SEGMENT_HASH), (NOTES, NOTES_SEGMENT_HASH)):
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

recovered = [r for r in backup_mentions if r["mention_id"].startswith("m-chp9-p254-")]
if len(recovered) != 82 or len({r["mention_id"] for r in recovered}) != 82:
    raise SystemExit(f"expected 82 unique p.254 mentions in recovery source, found {len(recovered)}")
if Counter(r["segment_id"] for r in recovered) != Counter({P254: 71, NOTES: 11}):
    raise SystemExit("unexpected p.254 mention distribution between body and consolidated notes")

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

body_rows = [r for r in statement_rows if r.get("segment_id") == P254]
note_rows = [r for r in statement_rows if r.get("segment_id") == NOTES and r.get("statement_id", "").startswith("st-chp9-p254-")]
body_unset = {r["statement_id"] for r in body_rows if r.get("qualifiers", {}).get("relation_candidate") is None}
note_unset = {r["statement_id"] for r in note_rows if r.get("qualifiers", {}).get("relation_candidate") is None}
if len(body_rows) != 25 or body_unset != set(BODY_CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.254 body statement state: count={len(body_rows)}, unset={sorted(body_unset)}")
if len(note_rows) != 8 or note_unset != set(NOTE_CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.254 note statement state: count={len(note_rows)}, unset={sorted(note_unset)}")

source_line = source_lines[141]
virtue_start = source_line.index("Families could look up at the ceilings")
exotic_start = source_line.index("Admiring Red Indians")
grassi_start = source_line.index("The Grassi,")
virtue_quote = source_line[virtue_start:exotic_start].rstrip()
exotic_quote = source_line[exotic_start:grassi_start].rstrip()
if not virtue_quote.endswith("earth.") or not exotic_quote.endswith("Austria."):
    raise SystemExit("could not split the p.254 L142 compound statement at verified sentence boundaries")

family_row = statement_by_id["st-chp9-p254-family-virtues-and-pictorial-neighbours"]
family_row["original_quote"] = virtue_quote
family_row["qualifiers"].update({
    "claim": "Haskell says families could see constancy, strength and justice publicly proclaimed on the ceilings of their state rooms.",
    "qualification": "This generalized representational claim links aristocratic families with the virtues displayed in their state-room ceilings; no individual family or specific ceiling is identified here. The separate modal claim about exotic figures and foreign neighbours is recorded independently.",
    "mentioned_candidate_ids": ["cand-8108", "cand-8321"],
    "relation_candidate": True,
})

new_statement_id = "st-chp9-p254-exotic-figures-compensate-for-neighbours"
if new_statement_id in statement_by_id:
    raise SystemExit(f"new statement ID already exists: {new_statement_id}")
new_statement = {
    "statement_id": new_statement_id,
    "segment_id": P254,
    "subject_candidate_id": None,
    "object_candidate_id": None,
    "predicate": "exotic_figures_might_compensate_for_foreign_neighbour_coldness",
    "qualifiers": {
        "source_line_start": 142,
        "source_line_end": 142,
        "printed_page": 254,
        "pdf_physical_page": 16,
        "claim": "Haskell suggests that admiring depictions of Red Indians or black savages might compensate for the coldness and scorn of neighbours such as France or Austria.",
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": "This is a modal authorial interpretation, not a claim about an identified fresco, family, or viewing group. The source wording and 'might' are retained; no specific depicted people are inferred.",
        "mentioned_candidate_ids": ["cand-8306", "cand-8307", "cand-8308", "cand-8309"],
        "relation_candidate": False,
    },
    "original_quote": exotic_quote,
    "origin": "book",
    "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
}

classification_reasons = {
    "st-chp9-p254-family-virtues-and-pictorial-neighbours": "The source directly links aristocratic families with virtues publicly represented on state-room ceilings; no particular family or ceiling is identified, so this remains a generalized book-based relation candidate.",
    "st-chp9-p254-living-family-portraits-in-frescoes": "The source directly links the fresco group to portraits of living family members; the individuals and each work remain unnamed.",
    "st-chp9-p254-pisani-palace-comparison": "This is a comparative ranking of a palace, not an entity-to-entity relationship candidate.",
    "st-chp9-p254-private-deeds-and-dream-world": "This is a broad historical interpretation of aristocratic culture and private deeds, without a sufficiently specific entity-to-entity relation for the formal graph.",
    "st-chp9-p254-solar-chariot-scene": "The source describes the scene of the Rezzonico marriage fresco, preserving a work-to-subject relation candidate without claiming independent iconographic verification.",
    "st-chp9-p254-tense-world-and-life-fantasy-gap": "This is Haskell's evaluative comparison of everyday life and artistic fantasy, not a relational fact about identifiable entities.",
    "st-chp9-p254-tiepolo-allegorical-calendar": "The source identifies Tiepolo as recording events in a series of eulogistic allegories, an artist-to-work-group relation candidate.",
    "st-chp9-p254-note1-giussani-reference": "This is a bibliographic citation locator only; the cited content was not independently consulted and this note is not itself a substantive relation claim.",
    "st-chp9-p254-note1-livan-reference": "This is a bibliographic citation locator only; the cited content was not independently consulted and this note is not itself a substantive relation claim.",
    "st-chp9-p254-note3-brunelli-callegari-reference": "This is a bibliographic citation locator only; the cited content was not independently consulted and this note is not itself a substantive relation claim.",
    "st-chp9-p254-note4-novelli-reference": "This is a bibliographic citation locator only; the cited content was not independently consulted and this note is not itself a substantive relation claim.",
    "st-chp9-p254-note5-muraro-reference": "This is a bibliographic citation locator only; the cited content was not independently consulted and this note is not itself a substantive relation claim.",
    "st-chp9-p254-note5-tabacco-reference": "This is a bibliographic citation locator only; the cited content was not independently consulted and this note is not itself a substantive relation claim.",
    "st-chp9-p254-note6-gallo-reference": "This is a bibliographic citation locator only; the cited content was not independently consulted and this note is not itself a substantive relation claim.",
    "st-chp9-p254-note7-moschini-reference": "This is a bibliographic citation locator only; the cited content was not independently consulted and this note is not itself a substantive relation claim.",
}
for sid, value in {**BODY_CLASSIFICATIONS, **NOTE_CLASSIFICATIONS}.items():
    row = statement_by_id[sid]
    qualifiers = row["qualifiers"]
    qualifiers["relation_candidate"] = value
    reason = classification_reasons[sid]
    existing = qualifiers.get("qualification", "").strip()
    if reason not in existing:
        qualifiers["qualification"] = (existing + " " + reason).strip()

family_index = next(i for i, row in enumerate(statement_rows) if row["statement_id"] == family_row["statement_id"])
statement_rows.insert(family_index + 1, new_statement)
new_mentions = current_mentions + recovered

status_counts_before = Counter(r.get("qualifiers", {}).get("relation_candidate") for r in read_jsonl(STATEMENTS))
status_counts_after = Counter(r.get("qualifiers", {}).get("relation_candidate") for r in statement_rows)
if len(statement_rows) != 14829 or status_counts_after.get(None, 0) != status_counts_before.get(None, 0) - 15:
    raise SystemExit(f"unexpected statement totals after classification: {len(statement_rows)} {status_counts_after}")
if status_counts_after[True] != status_counts_before[True] + 4 or status_counts_after[False] != status_counts_before[False] + 12:
    raise SystemExit(f"unexpected classification totals after classification: {status_counts_after}")

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "recovered_mentions": len(recovered),
    "mention_distribution": dict(Counter(r["segment_id"] for r in recovered)),
    "p254_body_statements_after_split": len(body_rows) + 1,
    "p254_body_classifications_after": {"true": 21, "false": 5, "unset": 0},
    "p254_footnote_statements_classified_false": len(NOTE_CLASSIFICATIONS),
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
        write_csv(MENTIONS, mention_fields, new_mentions)
        write_jsonl(STATEMENTS, statement_rows)
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; recovery backups: " + ", ".join(str(path.relative_to(ROOT)) for path in backups))
