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
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
SEGMENT = "chp-15:15_CHP-15_sec_ii:l3-4"
BACKUP_TAG = ".bak-s2-ch15-p364-memmo-classification-20261015"
EXPECTED = {
    "statements": "6af595a66defd941d521354897e408915fe49973d1dd5d69c9b9098e959e4377",
    "coverage": "4e05433e4093e3e85adc3ac2a9ecc06ece1149b07781115b4e0d2861347eb458",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

paths = {"statements": STATEMENTS, "coverage": COVERAGE}
for key, path in paths.items():
    if sha(path.read_bytes()) != EXPECTED[key]:
        raise SystemExit(f"unexpected pre-write hash: {key}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[2:4])
if not all(fragment in segment_text for fragment in (
    "ANDREA MEMMO", "chaste", "the Venetian aristocracy", "French culture and ideas", "and he"
)):
    raise SystemExit("p.364 Andrea Memmo S0 source span changed")

statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in statements}
coverage_rows = list(csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline="")))

true_notes = {
    "st-chp15-p364-memmo-learned-chaste-architecture":
        "Memmo's reported self-statement links his first appreciation of the source-defined 'chaste' architecture to Consul Smith's library. Keep the term, library identity and location qualified; no formal school or specific building is inferred.",
    "st-chp15-p364-memmo-most-enlightened-member":
        "Haskell explicitly places Memmo within the Venetian aristocracy. Preserve this membership relation while retaining 'most enlightened' as Haskell's evaluation, not a formal title.",
    "st-chp15-p364-memmo-french-intellectual-formation":
        "The source links Memmo's intellectual formation to French culture and ideas. Keep the broad term at the wording's scope; the Tabacco locator is a citation trail, not independent verification.",
    "st-chp15-p364-memmo-political-reform-and-noble-isolation":
        "The source links the Memmo index-subentry candidate to political reform through a reported enthusiasm. Retain 'altogether exceptional' as Haskell's characterization; infer no specific proposal, action, or outcome, and leave candidate identity alignment to S3.",
    "st-chp15-p364-memmo-repeated-efforts-break-noble-isolation":
        "Haskell reports Memmo's repeated efforts in relation to the unnamed fellow-noble group. Keep the group source-defined; do not infer individual participants or a formal organization.",
}
false_notes = {
    "st-chp15-p364-memmo-prior-capacity":
        "This is a backward reference to Haskell's earlier narrative, with note 3 pointing to Chapter 12. It does not assert a relation beyond internal navigation; preserve the cross-reference without interpreting the earlier chapter here.",
    "st-chp15-p364-memmo-more-interesting-patron":
        "This is Haskell's comparative assessment of Memmo as a patron, not a relation between distinct entities.",
    "st-chp15-p364-memmo-born-1729":
        "A birth year is a biographical attribute, not an edge between entities. Preserve Haskell's statement and note 4 citation trail without adding an independently verified date fact.",
    "st-chp15-p364-memmo-aristocratic-pleasures":
        "This is a broad characterization of Memmo's social life; no distinct pleasure or activity is identified, and Casanova's friendship is already recorded separately. Do not turn the social context into a relation to the aristocracy as a group.",
    "st-chp15-p364-memmo-love-affairs-continuation-partial":
        "The cross-page sentence is complete, but it describes an unspecified series and Haskell's characterization of Memmo's enthusiasm. No individual affair or separate event group is identified here; named relations remain separately recorded.",
}
if len(true_notes) != 5 or len(false_notes) != 5:
    raise SystemExit("internal Memmo classification count changed")
target_ids = set(true_notes) | set(false_notes)
if len(target_ids) != 10 or not target_ids.issubset(by_id):
    raise SystemExit("p.364 Memmo unresolved statement set changed")
body_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
if len(body_rows) != 18:
    raise SystemExit(f"unexpected p.364 Memmo statement count: {len(body_rows)}")
for sid in target_ids:
    row = by_id[sid]
    if row.get("segment_id") != SEGMENT or row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit(f"unexpected p.364 Memmo statement pre-state: {sid}")

for sid, note in true_notes.items():
    q = by_id[sid].setdefault("qualifiers", {})
    q["relation_candidate"] = True
    q["relation_candidate_note"] = note
for sid, note in false_notes.items():
    q = by_id[sid].setdefault("qualifiers", {})
    q["relation_candidate"] = False
    q["relation_candidate_note"] = note

coverage_matches = [row for row in coverage_rows if row["segment_id"] == SEGMENT]
if len(coverage_matches) != 1:
    raise SystemExit("p.364 Memmo coverage row missing or duplicated")
append_note = (
    " 2026-10-15 semantic classification: all 18 paragraph statements are classified (13 relation candidates, 5 non-relational claims). "
    "The architecture, aristocratic membership, French intellectual formation, political-reform interest and efforts concerning fellow-noble isolation remain source-attributed; "
    "authorial judgments, birth-year attribute, general social-life description and unspecified love-affairs pattern do not become graph edges. Existing note links and OCR corrections are retained."
)
if "2026-10-15 semantic classification:" in coverage_matches[0]["note"]:
    raise SystemExit("Memmo coverage already contains this classification note")
coverage_matches[0]["note"] += append_note

body_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in body_rows)
if len(body_rows) != 18 or counts[True] != 13 or counts[False] != 5 or counts[None] != 0:
    raise SystemExit(f"unexpected p.364 Memmo closure: {len(body_rows)} {counts}")

from io import StringIO
stream = StringIO(newline="")
writer = csv.DictWriter(stream, fieldnames=list(coverage_rows[0]), lineterminator="\n", extrasaction="raise")
writer.writeheader()
writer.writerows(coverage_rows)
coverage_output = ("\ufeff" + stream.getvalue()).encode("utf-8")
statement_output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
outputs = {STATEMENTS: statement_output, COVERAGE: coverage_output}

print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "segment": SEGMENT,
    "statements": {"total": len(body_rows), "true": counts[True], "false": counts[False], "unset": counts[None]},
    "classified_true": sorted(true_notes),
    "classified_false": sorted(false_notes),
    "after_sha256": {path.name: sha(data) for path, data in outputs.items()},
}, ensure_ascii=False, indent=2))

if args.apply:
    for key, path in paths.items():
        backup = path.with_name(path.name + BACKUP_TAG)
        if backup.exists() and sha(backup.read_bytes()) != EXPECTED[key]:
            raise SystemExit(f"backup differs: {backup.name}")
        if not backup.exists():
            shutil.copy2(path, backup)
    for path, data in outputs.items():
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent) as handle:
            handle.write(data)
            temp = Path(handle.name)
        temp.replace(path)
    print(json.dumps({"written_sha256": {path.name: sha(path.read_bytes()) for path in outputs}}, ensure_ascii=False, indent=2))
