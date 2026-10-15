"""Recover p.261 mentions and finish its S2 relation-candidate decisions.

Defaults to a read-only preflight. The printed page and consolidated footnotes
were reviewed against CHP-9.pdf physical page 23; source spans are checked.
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
BACKUP_SOURCE = TABLES / "mentions.csv.bak-s2-chp9-p262-20261001"
P261 = "chp-9:09_CHP-9_intro:l212-216"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SOURCE_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
P261_SEGMENT_HASH = "e94cea1632b183f4153ca8a3fef9cba2f227692c01e4c904a018c000303fa97b"
NOTES_SEGMENT_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_HASHES = {
    MENTIONS: "925df65fb6940541c0a8af22dc17cbd405d9b8d8fbf06d05a9b1b20952d38cb2",
    STATEMENTS: "573b120d54362c6bd505a813fcafb3cf1ce3ec32937b848ea9684fc480ec1658",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    BACKUP_SOURCE: "d2a003ba2a0e4a5cb7447b33aea3abe20ab66f1f159284af816b305fda85636d",
    SOURCE: SOURCE_HASH,
}
BACKUP_SUFFIX = ".bak-s2-chp9-p261-recovery-20261014"

# True marks a source-grounded relationship candidate for later S6 review.
# Generic argument, reputation, knowledge-gap and citation statements remain
# represented in S2 without being promoted to entity relations.
CLASSIFICATIONS = {
    "st-chp9-p261-caution-corruption-explanation": False,
    "st-chp9-p261-concrete-causes-hard-to-find": False,
    "st-chp9-p261-corrupt-age-explanations": False,
    "st-chp9-p261-decline-debated": False,
    "st-chp9-p261-decorative-aim-achieved": False,
    "st-chp9-p261-decorative-hanging-report": False,
    "st-chp9-p261-display-factors-not-decisive": False,
    "st-chp9-p261-economic-assessment-difficult": False,
    "st-chp9-p261-foscarini-rumoured-richest": False,
    "st-chp9-p261-gherardi-observer-quote": True,
    "st-chp9-p261-important-families-lost-wealth": True,
    "st-chp9-p261-interior-fashions-limited-wall-space": False,
    "st-chp9-p261-inventories-contemporary-pictures-decline": True,
    "st-chp9-p261-last-represented-artists": True,
    "st-chp9-p261-note1-traveller-source": False,
    "st-chp9-p261-note3-muraro-emporium": False,
    "st-chp9-p261-note4-gallo-1945-pages_140ff": False,
    "st-chp9-p261-note6-beltrami-1954": False,
    "st-chp9-p261-old-palace-galleries-already-filled": False,
    "st-chp9-p261-pisani-described-as-lavish": False,
    "st-chp9-p261-stra-house-painting-comparison": True,
    "st-chp9-p261-traveller-wall-display-quotation": True,
    "st-chp9-p261-wealth-restricted-inner-group": True,
}

REASONS = {
    "st-chp9-p261-caution-corruption-explanation": "S2: this is Haskell's methodological caution about causal explanations, not a positive relation among historical entities.",
    "st-chp9-p261-concrete-causes-hard-to-find": "S2: this records the author's stated limit on identifying causes; it is an acknowledged evidence gap, not a relation candidate.",
    "st-chp9-p261-corrupt-age-explanations": "S2: this summarizes Haskell's criticism of contemporary explanations, not an endorsed causal relation between corruption and patronage decline.",
    "st-chp9-p261-decline-debated": "S2: this reports that the decline was discussed, without identifying a specific source or substantive relation to preserve as an entity edge.",
    "st-chp9-p261-decorative-aim-achieved": "S2: this is Haskell's broad historical interpretation of an aesthetic objective among older families; no specific work or collection endpoint is identified.",
    "st-chp9-p261-decorative-hanging-report": "S2: this is a generic authorial summary of travellers' reports, without a mapped speaker, work, wall, or other distinct endpoint; the detailed attributed quotation is retained separately.",
    "st-chp9-p261-display-factors-not-decisive": "S2: this explicitly limits the proposed causal role of interior fashions and accumulated collections; retain the qualification rather than creating a positive causal edge.",
    "st-chp9-p261-economic-assessment-difficult": "S2: this is an epistemic qualification about the difficulty of assessing economic conditions, not a historical relation.",
    "st-chp9-p261-foscarini-rumoured-richest": "S2: this is a source-marked rumour and superlative property claim about the family, not a relation candidate; preserve the Carmini location separately.",
    "st-chp9-p261-gherardi-observer-quote": "S2: the identified Gherardi letter attributes an opinion about Venetian nobles' spending on pictures; retain it as a source-to-group testimony candidate, not a universal fact about all nobles.",
    "st-chp9-p261-important-families-lost-wealth": "S2: Haskell explicitly reports a temporal decline in wealth among important families; keep the collective endpoint unnamed and the claim unquantified.",
    "st-chp9-p261-interior-fashions-limited-wall-space": "S2: this is one qualified explanatory factor in Haskell's broader argument, without a separately identified endpoint for wall space; retain it as an attributed claim rather than an entity edge.",
    "st-chp9-p261-inventories-contemporary-pictures-decline": "S2: Haskell explicitly interprets inventories as showing reduced commissioning or purchase of contemporary pictures; the corpus is cited but was not independently inspected.",
    "st-chp9-p261-last-represented-artists": "S2: Haskell explicitly relates an unnamed last generation of artists to representation in Venetian collections; retain the group, location, and end-of-seventeenth-century qualification.",
    "st-chp9-p261-note1-traveller-source": "S2: bibliographic locator only; the cited travel book and page were not independently consulted.",
    "st-chp9-p261-note3-muraro-emporium": "S2: bibliographic locator only; the cited article was not independently consulted.",
    "st-chp9-p261-note4-gallo-1945-pages_140ff": "S2: bibliographic locator only; the title and cited pages were not independently consulted.",
    "st-chp9-p261-note6-beltrami-1954": "S2: citation locator only; the author's identity, title, and cited work remain unresolved.",
    "st-chp9-p261-old-palace-galleries-already-filled": "S2: this is a general condition of older family galleries with no identified gallery or collection endpoint; retain the contextual statement without a formal relation candidate.",
    "st-chp9-p261-pisani-described-as-lavish": "S2: this is Haskell's comparative description of a family, not a relation or independently measured ranking.",
    "st-chp9-p261-stra-house-painting-comparison": "S2: the source explicitly compares contemporary paintings in two identified Pisani residences with earlier holdings; preserve the relative, unquantified comparison.",
    "st-chp9-p261-traveller-wall-display-quotation": "S2: the cited travel account explicitly describes Venetian picture-display practice; retain the source-to-group account while keeping its broad generalization attributed and unverified.",
    "st-chp9-p261-wealth-restricted-inner-group": "S2: Haskell explicitly relates the concentration of money to a small, unnamed group of families; retain this as an attributed distribution claim and preserve the continuation to p.262.",
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
for sid, expected in ((P261, P261_SEGMENT_HASH), (NOTES, NOTES_SEGMENT_HASH)):
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

recovered = [row for row in backup_mentions if row["mention_id"].startswith("m-chp9-p261-")]
if len(recovered) != 47 or len({row["mention_id"] for row in recovered}) != 47:
    raise SystemExit(f"expected 47 unique p.261 backup mentions, found {len(recovered)}")
if Counter(row["segment_id"] for row in recovered) != Counter({P261: 24, NOTES: 23}):
    raise SystemExit("unexpected p.261 mention distribution across body and consolidated notes")

current_ids = {row["mention_id"] for row in current_mentions}
current_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in current_mentions}
for row in recovered:
    sid = row["segment_id"]
    meta = segments.get(sid)
    if not meta or row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"missing source segment or candidate for {row['mention_id']}")
    text = "\n".join(source_lines[meta["line_start"] - 1 : meta["line_end"]])
    start, end = int(row["start_char"]), int(row["end_char"])
    if start < 0 or end <= start or text[start:end] != row["surface_form"]:
        raise SystemExit(f"source-span mismatch for {row['mention_id']}")
    if row["mention_id"] in current_ids or (sid, row["start_char"], row["end_char"]) in current_spans:
        raise SystemExit(f"mention ID or source span already exists: {row['mention_id']}")

page_rows = [row for row in statement_rows if row.get("segment_id") == P261]
page_and_note_rows = [row for row in statement_rows if row.get("statement_id", "").startswith("st-chp9-p261-")]
unset_ids = {row["statement_id"] for row in page_and_note_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
if len(page_rows) != 21 or len(page_and_note_rows) != 28 or unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.261 statement state: body={len(page_rows)}, all={len(page_and_note_rows)}, unset={sorted(unset_ids)}")

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
if before.get(None, 0) - after.get(None, 0) != 23:
    raise SystemExit(f"unexpected global classification delta: before={before}, after={after}")
if after[True] != before[True] + 7 or after[False] != before[False] + 16:
    raise SystemExit(f"unexpected global classification counts: {after}")

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "page": 261,
    "recovered_mentions": len(recovered),
    "mention_distribution": dict(Counter(row["segment_id"] for row in recovered)),
    "p261_body_statements": len(page_rows),
    "p261_statement_classifications_after": {
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
        raise SystemExit("a p.261 recovery backup already exists; inspect before applying")
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
