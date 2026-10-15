"""Recover p.262 mentions and finish its S2 relation-candidate decisions.

Defaults to a read-only preflight. The printed page and its footnotes were
reviewed against CHP-9.pdf physical page 24, including visual note 2.
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
NOTE2_SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro_notes_p262_visual-transcription.md"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BACKUP_SOURCE = TABLES / "mentions.csv.bak-s2-chp9-p263-p264-20261001"
P262 = "chp-9:09_CHP-9_intro:l218-229"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
NOTE2 = "chp-9:09_CHP-9_intro_notes_p262_visual-transcription:l1-1"
SOURCE_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
NOTE2_SOURCE_HASH = "19d871e4a76f86368b71b4f11528fab11181863a2361ed2b8d46407408a73e8f"
SEGMENT_HASHES = {
    P262: "19071349bda95267fa463da2c9c65c3af827a9e978d3585bdbb715e08831f9dc",
    NOTES: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
    NOTE2: "d9671b7aaf07a56182e74a19842dd35ebcf312f7feb8827d8676dbfa828de3c3",
}
EXPECTED_HASHES = {
    MENTIONS: "5bd02adb1cb52c2c8bc1e9abb6762439cd750cc1eabe8f415e8971038a910d13",
    STATEMENTS: "1418166a05ec80158935357432c134b69701f2da437e0696ae9a04bb742b9e5f",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    BACKUP_SOURCE: "ea443c7bc69e728214922ec4d025f84b0df0979b951aaa19078bf5197542153b",
    SOURCE: SOURCE_HASH,
    NOTE2_SOURCE: NOTE2_SOURCE_HASH,
}
BACKUP_SUFFIX = ".bak-s2-chp9-p262-recovery-20261014"

# True marks a source-grounded relation candidate for later S6 review. False
# keeps an assertion, citation, or methodological statement in S2 content.
CLASSIFICATIONS = {
    "st-chp9-p262-ancestral-portraits-question": False,
    "st-chp9-p262-canaletto-career-price": True,
    "st-chp9-p262-carriera-miniature-and-pastel-prices": True,
    "st-chp9-p262-cignaroli-labia-employment": True,
    "st-chp9-p262-foreign-competition-price-context": True,
    "st-chp9-p262-foscarini-income": True,
    "st-chp9-p262-gallery-as-corollary-of-nobility": True,
    "st-chp9-p262-grassi-old-masters-preference": True,
    "st-chp9-p262-grassi-only-patrician-collection": True,
    "st-chp9-p262-new-nobles-collection-paradox": False,
    "st-chp9-p262-new-nobles-enrolment": True,
    "st-chp9-p262-note1-currency-table-locator": False,
    "st-chp9-p262-note1-currency-value-caveat": False,
    "st-chp9-p262-note2-berengo-subsistence-locator": False,
    "st-chp9-p262-note3-price-crossreferences": False,
    "st-chp9-p262-note4-meschini-grassi-locator": False,
    "st-chp9-p262-note6-biffi-palazzo-collection": True,
    "st-chp9-p262-small-fashionable-works-price-comparison": True,
    "st-chp9-p262-subsistence-estimate": False,
}

REASONS = {
    "st-chp9-p262-ancestral-portraits-question": "S2: this is Haskell's rhetorical question and identifies no painter, family, or particular portrait; do not invent an answer or relation.",
    "st-chp9-p262-canaletto-career-price": "S2: Haskell gives Canaletto's changing per-picture price across an approximate career interval; retain the artist-to-price relation and its reported, approximate figures.",
    "st-chp9-p262-carriera-miniature-and-pastel-prices": "S2: the source explicitly relates Carriera's miniature and pastel formats to different prices; no individual work is identified.",
    "st-chp9-p262-cignaroli-labia-employment": "S2: Haskell explicitly reports Cignaroli working for the Labia; note 5 supplies a four-year duration, while no specific commission is named.",
    "st-chp9-p262-foreign-competition-price-context": "S2: this is Haskell's explicit causal account linking foreign competition with high prices for successful artists; retain the qualification and lack of comparative price data.",
    "st-chp9-p262-foscarini-income": "S2: the reported 32,000-zecchini income is explicitly tied to the Foscarini and to Visconti's 1749 letter; preserve the nested source and do not treat it as verified accounts.",
    "st-chp9-p262-gallery-as-corollary-of-nobility": "S2: Haskell explicitly links extensive galleries with noble status as a necessary corollary; retain this broad authorial relation without assigning it to every family.",
    "st-chp9-p262-grassi-old-masters-preference": "S2: Haskell relates the Grassi family's apparent avoidance of contemporary artists to collecting old masters; preserve 'seem' and 'perhaps' and the listed artist candidates.",
    "st-chp9-p262-grassi-only-patrician-collection": "S2: Haskell explicitly relates the Grassi to building a picture collection in the eighteenth century; preserve the bounded 'only family' claim as the author's comparison, not a verified census.",
    "st-chp9-p262-new-nobles-collection-paradox": "S2: this is Haskell's interpretive contrast about new nobles' unexplained reluctance to buy contemporary pictures, not a positive purchase or collection relation; no individual works or buyers are identified.",
    "st-chp9-p262-new-nobles-enrolment": "S2: the text explicitly links new families' admission to the aristocracy with an approximate payment of nearly 30,000 zecchini; retain the collective scope and amount qualification.",
    "st-chp9-p262-note1-currency-table-locator": "S2: this is a locator for De La Lande's conversion tables; the tables were not independently consulted.",
    "st-chp9-p262-note1-currency-value-caveat": "S2: this methodological caveat warns that currency conversion does not adjust for changes in money value; it is not a historical entity relation.",
    "st-chp9-p262-note2-berengo-subsistence-locator": "S2: bibliographic locator only; the cited Berengo page was not independently consulted, and the separate visual transcription preserves its printed wording.",
    "st-chp9-p262-note3-price-crossreferences": "S2: internal pointers to other page notes only; the referenced price notes were not independently consulted here.",
    "st-chp9-p262-note4-meschini-grassi-locator": "S2: bibliographic locator only; Meschini's cited work and page were not independently consulted.",
    "st-chp9-p262-note6-biffi-palazzo-collection": "S2: Biffi's 1773 letter explicitly describes paintings and panels in Palazzo Giovanelli; retain the attributed collection/location testimony and leave given-name or surname-only artists unresolved.",
    "st-chp9-p262-small-fashionable-works-price-comparison": "S2: Haskell explicitly compares prices and formats for small fashionable works against large history pictures and full-scale decorations; preserve it as a relative market claim, not a universal price rule.",
    "st-chp9-p262-subsistence-estimate": "S2: this is an approximate subsistence estimate attributed to the cited Berengo page, with no named household or measured individual; preserve it as content without an entity relation candidate.",
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
for sid, expected in SEGMENT_HASHES.items():
    meta = segments.get(sid)
    expected_asset = NOTE2_SOURCE_HASH if sid == NOTE2 else SOURCE_HASH
    if not meta or meta["sha256"] != expected or meta["asset_sha256"] != expected_asset:
        raise SystemExit(f"unexpected source-segment metadata: {sid}")

_, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
_, backup_mentions = read_csv(BACKUP_SOURCE)
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
if len(statement_by_id) != len(statement_rows):
    raise SystemExit("statement IDs are not unique")

recovered = [row for row in backup_mentions if row["mention_id"].startswith("m-chp9-p262-")]
if len(recovered) != 79 or len({row["mention_id"] for row in recovered}) != 79:
    raise SystemExit(f"expected 79 unique p.262 backup mentions, found {len(recovered)}")
expected_distribution = Counter({P262: 70, NOTES: 7, NOTE2: 2})
if Counter(row["segment_id"] for row in recovered) != expected_distribution:
    raise SystemExit(f"unexpected p.262 mention distribution: {Counter(row['segment_id'] for row in recovered)}")

current_ids = {row["mention_id"] for row in current_mentions}
current_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in current_mentions}
main_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
note2_lines = NOTE2_SOURCE.read_text(encoding="utf-8-sig").splitlines()
source_text_by_segment = {
    P262: "\n".join(main_lines[segments[P262]["line_start"] - 1 : segments[P262]["line_end"]]),
    NOTES: "\n".join(main_lines[segments[NOTES]["line_start"] - 1 : segments[NOTES]["line_end"]]),
    NOTE2: "\n".join(note2_lines[segments[NOTE2]["line_start"] - 1 : segments[NOTE2]["line_end"]]),
}
for row in recovered:
    sid = row["segment_id"]
    if sid not in source_text_by_segment or row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"missing source segment or candidate for {row['mention_id']}")
    text = source_text_by_segment[sid]
    start, end = int(row["start_char"]), int(row["end_char"])
    if start < 0 or end <= start or text[start:end] != row["surface_form"]:
        raise SystemExit(f"source-span mismatch for {row['mention_id']}")
    if row["mention_id"] in current_ids or (sid, row["start_char"], row["end_char"]) in current_spans:
        raise SystemExit(f"mention ID or source span already exists: {row['mention_id']}")

page_rows = [row for row in statement_rows if row.get("segment_id") == P262]
page_and_note_rows = [row for row in statement_rows if row.get("statement_id", "").startswith("st-chp9-p262-")]
unset_ids = {row["statement_id"] for row in page_and_note_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
if len(page_rows) != 25 or len(page_and_note_rows) != 29 or unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.262 statement state: body-plus-page-notes={len(page_rows)}, all={len(page_and_note_rows)}, unset={sorted(unset_ids)}")

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
if before.get(None, 0) - after.get(None, 0) != 19:
    raise SystemExit(f"unexpected global classification delta: before={before}, after={after}")
if after[True] != before[True] + 11 or after[False] != before[False] + 8:
    raise SystemExit(f"unexpected global classification counts: {after}")

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "page": 262,
    "recovered_mentions": len(recovered),
    "mention_distribution": dict(Counter(row["segment_id"] for row in recovered)),
    "p262_page_segment_statements": len(page_rows),
    "p262_statement_classifications_after": {
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
        raise SystemExit("a p.262 recovery backup already exists; inspect before applying")
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
