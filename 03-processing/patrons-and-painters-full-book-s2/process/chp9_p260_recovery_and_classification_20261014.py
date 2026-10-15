"""Recover p.260 mentions and finish its S2 relation-candidate decisions.

Defaults to a read-only preflight. Review covers CHP-9.pdf physical page 22,
including footnotes 1-9 and the separate visual transcription of note 8.
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
NOTE8_SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro_notes_p260_visual-transcription.md"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BACKUP_SOURCE = TABLES / "mentions.csv.bak-s2-chp9-p261-20261001"
P260 = "chp-9:09_CHP-9_intro:l202-210"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
NOTE8 = "chp-9:09_CHP-9_intro_notes_p260_visual-transcription:l1-1"
SOURCE_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
NOTE8_SOURCE_HASH = "7b2cec96604bd1dad6609e67c9f94d771b36b4ec975cf05f410f711ffceab95d"
SEGMENT_HASHES = {
    P260: "ffbd53ac783c55a991bc4629b6bde3328e0708acce1819a1412f55607387ce6d",
    NOTES: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
    NOTE8: "88f6aedbfcbc999f20c7b4965c2ed50c3507df155b810b589ac921b1a3ebbfa0",
}
EXPECTED_HASHES = {
    MENTIONS: "fb12ae2247449d8f95b7ab054231c846605ad58da27e6d5cddb4ece1889bc8d3",
    STATEMENTS: "3815811862396293cb12b07e31a4a906603d1d7d172672ac971cad6512fdfb46",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    BACKUP_SOURCE: "6f4c17be2066c83004e8907fb8e9a4850c12494dcda08e2dfa1026a917615ac9",
    SOURCE: SOURCE_HASH,
    NOTE8_SOURCE: NOTE8_SOURCE_HASH,
}
BACKUP_SUFFIX = ".bak-s2-chp9-p260-recovery-20261014"

# True means a source-grounded relation candidate for later S6 review. False
# retains the assertion as content without proposing a formal relation.
CLASSIFICATIONS = {
    "st-chp9-p260-academy-lessons-end": True,
    "st-chp9-p260-books-and-manuscripts-returned": True,
    "st-chp9-p260-contemporary-rooms-description": True,
    "st-chp9-p260-first-half-patronage-moschini": True,
    "st-chp9-p260-foscarini-prestige-native-city": True,
    "st-chp9-p260-guarana-frescoes": True,
    "st-chp9-p260-household-employment-general": True,
    "st-chp9-p260-narrower-patronage-scope": False,
    "st-chp9-p260-nogari-portrait": True,
    "st-chp9-p260-note1-arnaldi-and-de-brosses": False,
    "st-chp9-p260-note2-novelli-page": False,
    "st-chp9-p260-note3-moschini-1808": False,
    "st-chp9-p260-note4-gradenigo": False,
    "st-chp9-p260-note5-tiepolo-dedicated-prints": True,
    "st-chp9-p260-note6-molino-orazione": False,
    "st-chp9-p260-note7-moschini-volume-iii-page-49": False,
    "st-chp9-p260-note8-miani-baglione-list": True,
    "st-chp9-p260-note9-gallo-page-53": False,
    "st-chp9-p260-novelli-description-foscarini": True,
    "st-chp9-p260-novelli-history-picture-request": True,
    "st-chp9-p260-novelli-s-marco-kept-four-days": True,
    "st-chp9-p260-patrician-glorification-ceiling-fresco": True,
    "st-chp9-p260-pictures-seem-painted-rome": True,
    "st-chp9-p260-sculptors-and-past-images": True,
    "st-chp9-p260-sculptural-images-now-gone": False,
    "st-chp9-p260-venetian-painters-limited-role": True,
    "st-chp9-p260-writers-pictures": True,
}

REASONS = {
    "st-chp9-p260-academy-lessons-end": "S2: the claim links the Pisani academy to Almorò's drawing lessons and its end at his death; preserve the source's 'seems' and the unresolved personal identity without asserting more activity.",
    "st-chp9-p260-books-and-manuscripts-returned": "S2: Haskell explicitly links Foscarini's acquisition of books and manuscripts in Rome to their return to the family palace; retain the source's quantity wording and quoted phrase.",
    "st-chp9-p260-contemporary-rooms-description": "S2: the attributed contemporary description explicitly links rooms with portraits and busts and uses writers and Muses as its rhetorical image; retain the anonymous speaker and do not literalize the Muses.",
    "st-chp9-p260-first-half-patronage-moschini": "S2: the passage reports artists receiving patronage and Moschini's attributed claim about support for the arts; keep the patron group open and the nested attribution explicit.",
    "st-chp9-p260-foscarini-prestige-native-city": "S2: Haskell explicitly links Foscarini's actions to maintaining the prestige of his native city, which context identifies as Venice; keep the de Brosses wording as nested testimony.",
    "st-chp9-p260-guarana-frescoes": "S2: the source explicitly identifies Guarana as painter of frescoes in the Foscarini palace; preserve Tiepolo as a follower context, not a co-author.",
    "st-chp9-p260-household-employment-general": "S2: the author reports families employing established artists as household members; retain this general relation with its specific examples in note 8.",
    "st-chp9-p260-narrower-patronage-scope": "S2: this is Haskell's broad analytical comparison of patronage scope and required art forms; its more specific support and patronage relations are recorded separately.",
    "st-chp9-p260-nogari-portrait": "S2: Haskell explicitly names Nogari as painter of Foscarini's portrait; the portrait remains unidentified and distinct from Batoni's portrait.",
    "st-chp9-p260-note1-arnaldi-and-de-brosses": "S2: note 1 supplies bibliographic locators only; the cited oration and De Brosses page were not independently consulted.",
    "st-chp9-p260-note2-novelli-page": "S2: note 2 is a page locator for the nested recollection; the cited page was not independently consulted.",
    "st-chp9-p260-note3-moschini-1808": "S2: note 3 is a bibliographic locator only; the cited work and page were not independently consulted.",
    "st-chp9-p260-note4-gradenigo": "S2: note 4 is an incomplete bibliographic locator; the identity, work, and cited page remain unresolved and unread.",
    "st-chp9-p260-note5-tiepolo-dedicated-prints": "S2: the note explicitly relates prints made from Tiepolo's drawings to Foscarini as dedicatee; keep the print group unnamed and source-reported.",
    "st-chp9-p260-note6-molino-orazione": "S2: note 6 is a citation to Molino's oration, not an independently consulted claim about the historical relationship.",
    "st-chp9-p260-note7-moschini-volume-iii-page-49": "S2: note 7 provides a bibliographic locator only; the cited page was not independently consulted.",
    "st-chp9-p260-note8-miani-baglione-list": "S2: note 8 includes the Miani and Baglione families among household-employment examples; preserve the family-level candidate while leaving individual members and exact artist-family pairing unresolved.",
    "st-chp9-p260-note9-gallo-page-53": "S2: note 9 is a bibliographic locator for the Pisani academy account; the cited publication and page were not independently consulted.",
    "st-chp9-p260-novelli-description-foscarini": "S2: Haskell attributes a recollected description of Foscarini to Novelli; retain the person-to-person testimony candidate and the nested, unverified status of the quotation.",
    "st-chp9-p260-novelli-history-picture-request": "S2: the recollection explicitly says Foscarini asked Novelli for a history picture; retain the request as a commission candidate while leaving subject and completion unresolved.",
    "st-chp9-p260-novelli-s-marco-kept-four-days": "S2: the recollection explicitly links Foscarini to temporary keeping of Novelli's Saint Mark painting for four days; this does not establish an ownership transfer.",
    "st-chp9-p260-patrician-glorification-ceiling-fresco": "S2: Haskell explicitly connects patrician self-glorification with concentration on ceiling frescoes; retain it as an authorial tendency, not an exclusive rule.",
    "st-chp9-p260-pictures-seem-painted-rome": "S2: the source links an unnamed group of Foscarini's pictures to Rome as their likely production location; retain 'seem' and leave individual works unresolved.",
    "st-chp9-p260-sculptors-and-past-images": "S2: Haskell explicitly relates Foscarini's employment of sculptors in Rome and Venice to making images of historical figures; retain the group work and unnamed authors/subjects.",
    "st-chp9-p260-sculptural-images-now-gone": "S2: this records Haskell's statement about lost works and missing authorship evidence, not a positive relation; it is not a current-condition check.",
    "st-chp9-p260-venetian-painters-limited-role": "S2: preserve Haskell's qualified claim about the limited part played by leading Venetian painters and the reported effect of Foscarini's patronage on fellow citizens; leave the audience generic.",
    "st-chp9-p260-writers-pictures": "S2: Haskell explicitly links Foscarini's pictures to represented Venetian writers and locates them in rooms where he kept their books; no titles or individual writers are named.",
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
    expected_asset = NOTE8_SOURCE_HASH if sid == NOTE8 else SOURCE_HASH
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

recovered = [row for row in backup_mentions if row["mention_id"].startswith("m-chp9-p260-")]
if len(recovered) != 74 or len({row["mention_id"] for row in recovered}) != 74:
    raise SystemExit(f"expected 74 unique p.260 backup mentions, found {len(recovered)}")
expected_distribution = Counter({P260: 41, NOTES: 22, NOTE8: 11})
if Counter(row["segment_id"] for row in recovered) != expected_distribution:
    raise SystemExit(f"unexpected p.260 mention distribution: {Counter(row['segment_id'] for row in recovered)}")

current_ids = {row["mention_id"] for row in current_mentions}
current_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in current_mentions}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
note8_text = NOTE8_SOURCE.read_text(encoding="utf-8-sig").splitlines()
source_text_by_segment = {
    P260: "\n".join(source_lines[segments[P260]["line_start"] - 1 : segments[P260]["line_end"]]),
    NOTES: "\n".join(source_lines[segments[NOTES]["line_start"] - 1 : segments[NOTES]["line_end"]]),
    NOTE8: "\n".join(note8_text[segments[NOTE8]["line_start"] - 1 : segments[NOTE8]["line_end"]]),
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

page_rows = [row for row in statement_rows if row.get("segment_id") == P260 and row.get("statement_id", "").startswith("st-chp9-p260-")]
all_page_rows = [row for row in statement_rows if row.get("statement_id", "").startswith("st-chp9-p260-")]
unset_ids = {row["statement_id"] for row in all_page_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
if len(page_rows) != 19 or len(all_page_rows) != 30 or unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.260 statement state: body={len(page_rows)}, all={len(all_page_rows)}, unset={sorted(unset_ids)}")

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
if before.get(None, 0) - after.get(None, 0) != 27:
    raise SystemExit(f"unexpected global classification delta: before={before}, after={after}")
if after[True] != before[True] + 18 or after[False] != before[False] + 9:
    raise SystemExit(f"unexpected global classification counts: {after}")

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "page": 260,
    "recovered_mentions": len(recovered),
    "mention_distribution": dict(Counter(row["segment_id"] for row in recovered)),
    "p260_body_statements": len(page_rows),
    "p260_statement_classifications_after": {
        "true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in all_page_rows),
        "false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in all_page_rows),
        "unset": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in all_page_rows),
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
        raise SystemExit("a p.260 recovery backup already exists; inspect before applying")
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
