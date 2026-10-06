"""Record the two personal collections on p.344 without forcing a type."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l116-122"
SEGMENT_SHA = "2eee99ac3f4b0588c8491bc9a2987eb8817d8e07774747df9d898967e4fcc16b"
BACKUP_SUFFIX = ".bak-s2-chp13-p344-collection-refinement-20261003"
SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed collection refinement")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[115:122])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("p.344 source segment changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
state = (len(candidates), len(mentions), len(statements))
if state != (10099, 21795, 9723):
    raise SystemExit(f"unexpected table pre-state: {state}")
if "cand-10113" in candidate_by_id:
    raise SystemExit("collection candidate cand-10113 already exists")

work_collection = candidate_by_id.get("cand-10112")
if not work_collection or work_collection["suggested_type"] != "":
    raise SystemExit("p.344 Felicita collection candidate changed")
catalogue_statement = statement_by_id.get("st-chp13-p344-dactyliotheca-catalogue")
if not catalogue_statement or catalogue_statement["object_candidate_id"] is not None:
    raise SystemExit("p.344 Dactyliotheca catalogue statement changed")
if any(row["segment_id"] == SEGMENT_ID and row["surface_form"] == "his own collection of-gems and medals" for row in mentions):
    raise SystemExit("p.344 gem and medal collection mention already exists")

work_collection["canonical_name"] = "Collection of Felicita Sartori’s works owned by A. M. Zanetti"
work_collection["suggested_type"] = ""
work_collection["detail"] = (
    "A personal art collection, distinct from the individual works. The current taxonomy has no personal "
    "collection type, so type remains undecided; no individual works or count are specified."
)

new_candidate = {field: "" for field in candidate_fields}
new_candidate.update({
    "candidate_id": "cand-10113",
    "canonical_name": "Collection of gems and medals owned by A. M. Zanetti",
    "suggested_type": "",
    "status": "open",
    "detail": (
        "A personal collection catalogued in the Dactyliotheca, distinct from the archive/catalogue itself. "
        "The current taxonomy has no personal collection type, so type remains undecided."
    ),
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT_ID}#L117",
})

raw_line = source_lines[116]
surface = "his own collection of-gems and medals"
at = raw_line.find(surface)
if at < 0:
    raise SystemExit("p.344 gem/medal collection anchor missing")
line_offset = len(source_lines[115]) + 1
mention = {field: "" for field in mention_fields}
mention.update({
    "mention_id": "m-s2-ch13-p344-033",
    "segment_id": SEGMENT_ID,
    "candidate_id": "cand-10113",
    "surface_form": surface,
    "start_char": line_offset + at,
    "end_char": line_offset + at + len(surface),
    "note": "The printed phrase has an apparent join hyphen; collection type remains undecided.",
})

catalogue_statement["object_candidate_id"] = "cand-10113"
catalogue_statement["predicate"] = "illustrated_catalogue_of"
catalogue_statement["qualifiers"]["claim"] = (
    "Haskell identifies the 1749 Dactyliotheca as an illustrated catalogue of A. M. Zanetti's collection of gems and medals."
)
catalogue_statement["qualifiers"]["mentioned_candidate_ids"] = ["cand-10012", "cand-10113"]
catalogue_statement["qualifiers"]["relation_candidate"] = True

ownership_statement = {
    "statement_id": "st-chp13-p344-zanetti-owned_gem_medal_collection",
    "segment_id": SEGMENT_ID,
    "subject_candidate_id": "cand-2838",
    "object_candidate_id": "cand-10113",
    "predicate": "owned_collection_of_gems_and_medals",
    "qualifiers": {
        "source_line_start": 117,
        "source_line_end": 117,
        "printed_page": 344,
        "pdf_physical_page": 13,
        "claim": "Haskell describes the gems and medals as A. M. Zanetti's own collection.",
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": "The collection is distinct from its 1749 catalogue; the taxonomy does not currently provide a personal-collection type.",
        "mentioned_candidate_ids": ["cand-2838", "cand-10113"],
        "relation_candidate": True,
        "note_refs_pending": [{"printed_note": 1, "segment_id": "chp-13:13_CHP-13_intro:l179-251", "line": 239, "status": "pending"}],
    },
    "original_quote": source_lines[116],
    "origin": "book",
    "source_file": SOURCE_FILE,
}

all_candidates = candidates + [new_candidate]
all_mentions = mentions + [mention]
all_statements = statements + [ownership_statement]
if args.apply:
    for path in (candidate_path, mention_path, statement_path):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    print("Applied p.344 collection refinement.")
else:
    print("Dry run only; no files changed. Use --apply after reviewing this preview.")
print(f"Candidates: {len(candidates)} -> {len(all_candidates)} (+1).")
print(f"Mentions: {len(mentions)} -> {len(all_mentions)} (+1).")
print(f"Statements: {len(statements)} -> {len(all_statements)} (+1).")
print("Two personal art/object collections retain type undecided under the current taxonomy.")
