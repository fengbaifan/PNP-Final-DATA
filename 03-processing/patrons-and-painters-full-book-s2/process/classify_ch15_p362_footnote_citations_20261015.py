import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md"
EXPECTED = {
    "statements": "8a09d55614676fa2387689b2fe9c96eae010ab770b3c377eab595c79ddbab87e",
    "mentions": "55f053d311aa8f34104c4993a71d11bde1ab64bc27d1d392de6eab223c8fa4c7",
}
BACKUP_TAG = ".bak-s2-ch15-p362-footnote-citations-20261015"
SEGMENT_ID = "chp-15:15_CHP-15_sec_i:l43-56"
BOOK = "cand-2962"
TARGETS = {
    "st-chp15-p362-note1-family-history": (
        "cand-10443", "family history (1778); relevant passages",
        "m-chp15-p362-0097", "family history", "Haskell's printed p.362 note 1",
    ),
    "st-chp15-p362-note1-paravia-pamphlet": (
        "cand-10444", "P. A. Paravia pamphlet (1829)",
        "m-chp15-p362-0098", "pamphlet of 1829", "Haskell's printed p.362 note 1",
    ),
    "st-chp15-p362-note1-sforza-article": (
        "cand-10447", "Giovanni Sforza article (1911), pp. 153-95",
        "m-chp15-p362-0099", "article by Giovanni Sforza, 1911, pp. 153-95", "Haskell's printed p.362 note 1",
    ),
    "st-chp15-p362-note2-memmo-1786": (
        "cand-8812", "Andrea Memmo, 1786, p. 60",
        "m-chp15-p362-0100", "[Andrea Memmo], 1786, p. 60", "Haskell's printed p.362 note 2",
    ),
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

for key, path in (("statements", STATEMENTS), ("mentions", MENTIONS)):
    if sha(path.read_bytes()) != EXPECTED[key]:
        raise SystemExit(f"unexpected pre-write hash: {key}")

statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
statement_by_id = {row["statement_id"]: row for row in statements}
if not set(TARGETS).issubset(statement_by_id):
    raise SystemExit("missing expected p362 footnote statements")

segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment = next(row for row in segments if row["segment_id"] == SEGMENT_ID)
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])

for sid, (archive, locator, *_rest) in TARGETS.items():
    row = statement_by_id[sid]
    if row["segment_id"] != SEGMENT_ID or row["qualifiers"].get("relation_candidate") is not None:
        raise SystemExit(f"unexpected source or classification: {sid}")
    if archive not in row["qualifiers"].get("mentioned_candidate_ids", []):
        raise SystemExit(f"citation archive is not referenced by {sid}")
    row["subject_candidate_id"] = BOOK
    row["object_candidate_id"] = archive
    row["predicate"] = "cites"
    row["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "The printed footnote explicitly cites this identified publication. This is a book-to-source bibliographic candidate; the cited work and cited contents were not independently consulted.",
        "citation_locator": locator,
        "footnote_marker": "1" if "note1" in sid else "2",
        "footnote_segment_id": SEGMENT_ID,
        "footnote_source_lines": [44 if "note1" in sid else 45],
        "footnote_text_pending": False,
        "cited_source_independently_consulted": False,
    })
    mids = row["qualifiers"].setdefault("mentioned_candidate_ids", [])
    if BOOK not in mids:
        mids.append(BOOK)

with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    mention_fields = reader.fieldnames
    mentions = list(reader)
candidate_ids = {row["candidate_id"] for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))}
if len({row["mention_id"] for row in mentions}) != len(mentions):
    raise SystemExit("duplicate existing mention IDs")
new_mentions = []
for sid, (archive, locator, mid, surface, note) in TARGETS.items():
    if mid in {row["mention_id"] for row in mentions}:
        raise SystemExit(f"mention ID already exists: {mid}")
    start = source_text.index(surface)
    end = start + len(surface)
    if source_text[start:end] != surface or archive not in candidate_ids:
        raise SystemExit(f"invalid citation mention: {mid}")
    new_mentions.append({
        "mention_id": mid, "segment_id": SEGMENT_ID, "candidate_id": archive,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })

combined = mentions + new_mentions
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
               for row in combined if row["segment_id"] == SEGMENT_ID)
for first, second in zip(spans, spans[1:]):
    if second[0] < first[1]:
        raise SystemExit(f"overlapping note mentions: {first[2]} / {second[2]}")

statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
mention_output = __import__("io").StringIO(newline="")
writer = csv.DictWriter(mention_output, fieldnames=mention_fields, lineterminator="\n")
writer.writeheader()
writer.writerows(combined)
mention_bytes = mention_output.getvalue().encode("utf-8")
outputs = {STATEMENTS: statement_bytes, MENTIONS: mention_bytes}
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "citations": [{"statement_id": sid, "book": BOOK, "archive": target[0], "predicate": "cites"} for sid, target in TARGETS.items()],
    "new_mentions": [{"mention_id": row["mention_id"], "surface_form": row["surface_form"], "start_char": row["start_char"], "end_char": row["end_char"]} for row in new_mentions],
    "after_sha256": {str(path.relative_to(ROOT)): sha(data) for path, data in outputs.items()},
}, ensure_ascii=False, indent=2))

if args.apply:
    temporary = {}
    for path, data in outputs.items():
        backup = path.with_name(path.name + BACKUP_TAG)
        key = "statements" if path == STATEMENTS else "mentions"
        if backup.exists():
            if sha(backup.read_bytes()) != EXPECTED[key]:
                raise SystemExit(f"backup differs: {backup.name}")
        else:
            shutil.copy2(path, backup)
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent) as handle:
            handle.write(data)
            temporary[path] = Path(handle.name)
    for path, temp_path in temporary.items():
        temp_path.replace(path)
    print(json.dumps({"written_sha256": {str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in outputs}}, indent=2))
