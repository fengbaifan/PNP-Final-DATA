"""Recover p.258 mentions and finish its S2 relation-candidate decisions.

Defaults to a read-only preflight. The source page and exact mention spans were
checked against CHP-9.pdf physical page 20 and the preserved S0 transcription.
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
BACKUP_SOURCE = TABLES / "mentions.csv.bak-s2-chp9-p259-20261001"
P258 = "chp-9:09_CHP-9_intro:l179-186"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SOURCE_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
P258_SEGMENT_HASH = "641f4a86d91e032087e759e6f7d7e3cf356c4cf622a4821ecebc507953276658"
NOTES_SEGMENT_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_HASHES = {
    MENTIONS: "c3b33a35fa1eb9d388f1d963139a97a5887a6ec3ea7198098d1c3e65b48dd21a",
    STATEMENTS: "c4fe2e25710146915e8036f016037ef63206a4fdd7dc0da062886c5d1ebbd217",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    BACKUP_SOURCE: "3b2717456782278005dcdf7f1353fcb49b68abace018a74915fe99b30551a4dd",
    SOURCE: SOURCE_HASH,
}
BACKUP_SUFFIX = ".bak-s2-chp9-p258-recovery-20261014"

# True marks an explicit or attributed relation candidate for later S6 review;
# false retains the statement as S2 content without promoting it to a relation.
CLASSIFICATIONS = {
    "st-chp9-p258-ancient-glories-shaped-foscarini-politics": True,
    "st-chp9-p258-erotic-subjects-less-common-later": True,
    "st-chp9-p258-funeral-orator-portrait-of-leonardo": True,
    "st-chp9-p258-guardi-venice-paris-career": True,
    "st-chp9-p258-haskell-weighs-funeral-oration-and-virtue": False,
    "st-chp9-p258-marco-foscarini-stands-out-among-patricians": False,
    "st-chp9-p258-marco-increasingly-identified-with-conservatism": True,
    "st-chp9-p258-marco-literary-history-interests-and-studies": True,
    "st-chp9-p258-mythologies-less-demanded-than-classical-history": True,
    "st-chp9-p258-note1-levey-article-citation": False,
    "st-chp9-p258-note2-valmarana-funeral-oration-citation": False,
    "st-chp9-p258-note3-general-foscarini-accounts-citation": False,
    "st-chp9-p258-pellegrini-carriera-more-success-abroad": True,
    "st-chp9-p258-tiepolo-rarely-left-grandeur": False,
    "st-chp9-p258-valmarana-commission-circumstances-unknown": False,
}

REASONS = {
    "st-chp9-p258-ancient-glories-shaped-foscarini-politics": "S2: Haskell explicitly attributes influence from Foscarini's sustained engagement with Venice's past to his political thinking; retain this as an attributed interpretive relation, not independently verified causation.",
    "st-chp9-p258-erotic-subjects-less-common-later": "S2: the passage links the named subjects to erotic use and compares their historical prevalence; this is a source-attributed subject/use trend, not an identified painting or quantitative count.",
    "st-chp9-p258-funeral-orator-portrait-of-leonardo": "S2: Haskell explicitly attributes the character portrait of Leonardo to a cited funeral oration; preserve the source-to-person attribution and the oration's non-impartial status.",
    "st-chp9-p258-guardi-venice-paris-career": "S2: Haskell compares Guardi's actual career in Venice with hypothetical success in Paris; retain both place contexts and the counterfactual qualification, without treating Paris success as an event.",
    "st-chp9-p258-haskell-weighs-funeral-oration-and-virtue": "S2: this is Haskell's source criticism and interpretive use of the reported virtue, not a historical entity relation; retain the explicit caveat about impartiality.",
    "st-chp9-p258-marco-foscarini-stands-out-among-patricians": "S2: this reports an attributed character assessment by unnamed contemporaries; it is an evaluative quality claim without a distinct relation endpoint.",
    "st-chp9-p258-marco-increasingly-identified-with-conservatism": "S2: the claim relates Foscarini to conservative causes as a political tendency; preserve Haskell's attribution and the source's lack of a named party or specified causes.",
    "st-chp9-p258-marco-literary-history-interests-and-studies": "S2: Haskell relates Foscarini to Venetian literature and history through his interests, planned studies, and partial publication; the studies are unnamed, so their endpoint remains open.",
    "st-chp9-p258-mythologies-less-demanded-than-classical-history": "S2: this is an explicit comparison of demand for two subject categories, attributed to Haskell and unsupported by quantitative counts.",
    "st-chp9-p258-note1-levey-article-citation": "S2: bibliographic locator only; the citation is retained as source evidence and is not itself a historical relation candidate.",
    "st-chp9-p258-note2-valmarana-funeral-oration-citation": "S2: bibliographic locator for the cited funeral oration; the specific citation is not itself a historical relation candidate.",
    "st-chp9-p258-note3-general-foscarini-accounts-citation": "S2: bibliographic locator and source recommendation only; it is not itself a historical relation candidate.",
    "st-chp9-p258-pellegrini-carriera-more-success-abroad": "S2: Haskell explicitly compares the named artists' relative success across localities; retain 'appear' and the unspecified abroad endpoint.",
    "st-chp9-p258-tiepolo-rarely-left-grandeur": "S2: this is an aesthetic characterization of Tiepolo's subject matter and its frequency, without a distinct relation endpoint.",
    "st-chp9-p258-valmarana-commission-circumstances-unknown": "S2: this records an acknowledged knowledge gap about the commission and its patrons, not a positive historical relation; keep the uncertainty explicit.",
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
for sid, expected in ((P258, P258_SEGMENT_HASH), (NOTES, NOTES_SEGMENT_HASH)):
    meta = segments.get(sid)
    if not meta or meta["sha256"] != expected or meta["asset_sha256"] != SOURCE_HASH:
        raise SystemExit(f"unexpected source-segment metadata: {sid}")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()

candidate_fields, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
_, backup_mentions = read_csv(BACKUP_SOURCE)
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
if len(statement_by_id) != len(statement_rows):
    raise SystemExit("statement IDs are not unique")

recovered = [row for row in backup_mentions if row["mention_id"].startswith("m-chp9-p258-")]
if len(recovered) != 53 or len({row["mention_id"] for row in recovered}) != 53:
    raise SystemExit(f"expected 53 unique p.258 backup mentions, found {len(recovered)}")
if Counter(row["segment_id"] for row in recovered) != Counter({P258: 44, NOTES: 9}):
    raise SystemExit("unexpected p.258 mention distribution across body and consolidated notes")

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

page_rows = [row for row in statement_rows if row.get("segment_id") == P258]
page_and_note_rows = [row for row in statement_rows if row.get("statement_id", "").startswith("st-chp9-p258-")]
unset_ids = {row["statement_id"] for row in page_and_note_rows if row.get("qualifiers", {}).get("relation_candidate") is None}
if len(page_rows) != 26 or len(page_and_note_rows) != 29 or unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.258 statement state: body={len(page_rows)}, all={len(page_and_note_rows)}, unset={sorted(unset_ids)}")

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
if before.get(None, 0) - after.get(None, 0) != 15:
    raise SystemExit(f"unexpected global classification delta: before={before}, after={after}")
if after[True] != before[True] + 8 or after[False] != before[False] + 7:
    raise SystemExit(f"unexpected global classification counts: {after}")

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "page": 258,
    "recovered_mentions": len(recovered),
    "mention_distribution": dict(Counter(row["segment_id"] for row in recovered)),
    "p258_body_statements": len(page_rows),
    "p258_statement_classifications_after": {
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
        raise SystemExit("a p.258 recovery backup already exists; inspect before applying")
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
