"""Repair omitted p.361 relation decisions and split two compound claims; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE_BODY = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md"
SOURCE_NOTES = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
TABLE_SHA256 = "29faf8ed9976fb1ecd6d354fd12b7152c6f9cee58efcd70eb6e244d4b6baec5c"
BODY_SHA256 = "798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624"
NOTES_SHA256 = "015d35e467ad4cca8a4029d62aeb9469e49b4619e8c0c6916f46b0e0e019830b"
PDF_SHA256 = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
BODY = "chp-15:15_CHP-15_sec_i:l3-14"
NOTES = "chp-15:15_CHP-15_intro:l7-9"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp15-p361-semantic-reconcile-20261014"

TRUE_EXISTING = {
    "st-chp15-p361-tiepolo-in-spain-no-desire-return",
    "st-chp15-p361-pittoni-president-neglected",
    "st-chp15-p361-most-schulenburg-collection-sent-to-germany",
    "st-chp15-p361-men-encouraged-revival-venetian-painting",
}
FALSE_EXISTING_BODY = {
    "st-chp15-p361-flowering-nearly-ended-1764",
    "st-chp15-p361-piazzetta-dead-ten-years",
    "st-chp15-p361-new-history-painters-imitation",
    "st-chp15-p361-canaletto-repeated-himself-died-1769",
    "st-chp15-p361-guardi-unknown-to-great-patrons-different-public",
    "st-chp15-p361-zuccarelli-mostly-out-of-venice",
    "st-chp15-p361-zais-poverty-neglected",
    "st-chp15-p361-pietro-longhi-carried-on-twenty-years",
    "st-chp15-p361-alessandro-longhi-detached-observation",
    "st-chp15-p361-artists-patrons-collections-vanishing",
    "st-chp15-p361-sagredo-pictures-dispersing",
    "st-chp15-p361-schulenburg-collection-broken-up-1775",
    "st-chp15-p361-zanetti-died-1767",
    "st-chp15-p361-mariette-assumed-zanetti-pictures-leaving-venice",
    "st-chp15-p361-enlightenment-different-patronage-partial",
}
FALSE_EXISTING_NOTES = {
    "st-chp15-p361-note1-moschini-1810",
    "st-chp15-p361-note2-mariette-letter",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write reviewed p.361 semantic repairs")
ARGS = parser.parse_args()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as f:
        f.write(data)
        temp = Path(f.name)
    temp.replace(path)


if sha(TABLE.read_bytes()) != TABLE_SHA256:
    raise SystemExit("book-statements baseline changed; refusing to write")
if sha(SOURCE_BODY.read_bytes()) != BODY_SHA256 or sha(SOURCE_NOTES.read_bytes()) != NOTES_SHA256:
    raise SystemExit("chapter 15 Markdown source changed; refusing to write")
if sha(PDF.read_bytes()) != PDF_SHA256:
    raise SystemExit("CHP-15.pdf changed; refusing to write")

body_lines = SOURCE_BODY.read_text(encoding="utf-8-sig").splitlines()
note_lines = SOURCE_NOTES.read_text(encoding="utf-8-sig").splitlines()
body_segment = "\n".join(body_lines[2:14])
if not body_segment.startswith("FILIPPO FARSETTI\n") or "Tiepolo was in Spain" not in body_segment:
    raise SystemExit("registered p.361 source segment changed")

rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
body_rows = [row for row in rows if row.get("segment_id") == BODY]
note_rows = [row for row in rows if row.get("segment_id") == NOTES and row.get("statement_id", "").startswith("st-chp15-p361-")]
body_unset = {row["statement_id"] for row in body_rows if "relation_candidate" not in row.get("qualifiers", {})}
note_unset = {row["statement_id"] for row in note_rows if "relation_candidate" not in row.get("qualifiers", {})}
if len(body_rows) != 25 or body_unset != TRUE_EXISTING | FALSE_EXISTING_BODY:
    raise SystemExit(f"p.361 body review set changed: total={len(body_rows)}, symmetric_difference={sorted(body_unset ^ (TRUE_EXISTING | FALSE_EXISTING_BODY))}")
if len(note_rows) != 4 or note_unset != FALSE_EXISTING_NOTES:
    raise SystemExit(f"p.361 note review set changed: total={len(note_rows)}, symmetric_difference={sorted(note_unset ^ FALSE_EXISTING_NOTES)}")
if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in body_rows) != 6:
    raise SystemExit("p.361 existing body relation count differs from the reviewed baseline")
if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in note_rows) != 2:
    raise SystemExit("p.361 note endpoint relation count differs from the reviewed baseline")

for statement_id in FALSE_EXISTING_BODY | FALSE_EXISTING_NOTES:
    by_id[statement_id]["qualifiers"]["relation_candidate"] = False

tie = by_id["st-chp15-p361-tiepolo-in-spain-no-desire-return"]
tie.update({
    "predicate": "was_located_in_spain",
    "original_quote": "Tiepolo was in Spain",
})
tie["qualifiers"].update({
    "claim": "Haskell says Tiepolo was in Spain.",
    "qualification": "The passage gives no exact date; it records Tiepolo’s location at the point described without inferring a departure or return date.",
    "mentioned_candidate_ids": ["cand-2569", "cand-10409"],
    "relation_candidate": True,
})

pittoni = by_id["st-chp15-p361-pittoni-president-neglected"]
pittoni.update({
    "predicate": "held_presidency_of_accademia",
    "original_quote": "Pittoni, though president of the Accademia",
})
pittoni["qualifiers"].update({
    "claim": "Haskell identifies Pittoni as president of the Accademia.",
    "qualification": "The office is explicit, but the text gives neither the appointment authority nor exact tenure.",
    "mentioned_candidate_ids": ["cand-1950", "cand-0005"],
    "relation_candidate": True,
})

schulenburg = by_id["st-chp15-p361-most-schulenburg-collection-sent-to-germany"]
schulenburg["qualifiers"]["relation_candidate"] = True

these_men = by_id["st-chp15-p361-men-encouraged-revival-venetian-painting"]
these_men["qualifiers"]["relation_candidate"] = True
these_men["qualifiers"]["qualification"] = (
    "The text explicitly says the men encouraged the revival, but ‘these men’ has no complete roster here. "
    "Keep the subject endpoint unresolved; do not assign named people or infer membership."
)

new_rows = [
    {
        "statement_id": "st-chp15-p361-tiepolo-no-desire-to-return-to-italy",
        "segment_id": BODY,
        "subject_candidate_id": "cand-2569",
        "object_candidate_id": None,
        "predicate": "showed_no_desire_to_return_to_italy",
        "qualifiers": {
            "source_line_start": 5, "source_line_end": 5, "printed_page": 361,
            "pdf_physical_page": 1,
            "claim": "Haskell says Tiepolo showed no desire to return to Italy.",
            "speaker": "Haskell", "text_layer": "authorial report",
            "qualification": "This reports an expressed inclination, not a travel or residence relation.",
            "mentioned_candidate_ids": ["cand-2569", "cand-3461"],
            "relation_candidate": False,
            "ocr_corrections": [{"source_line": 5, "ocr": "to.return", "print": "to return", "basis": "CHP-15.pdf physical page 1."}],
        },
        "original_quote": "showed no desire to.return to Italy;",
        "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp15-p361-pittoni-neglect-with-declining-powers",
        "segment_id": BODY,
        "subject_candidate_id": "cand-1950",
        "object_candidate_id": None,
        "predicate": "increasingly_neglected_as_powers_declined",
        "qualifiers": {
            "source_line_start": 5, "source_line_end": 5, "printed_page": 361,
            "pdf_physical_page": 1,
            "claim": "Haskell says Pittoni was increasingly neglected as his powers declined.",
            "speaker": "Haskell", "text_layer": "authorial report",
            "qualification": "The source does not identify who neglected Pittoni; this is kept as a narrative evaluation, separate from his Accademia office.",
            "mentioned_candidate_ids": ["cand-1950"],
            "relation_candidate": False,
        },
        "original_quote": "was increasingly neglected as his powers declined.",
        "origin": "book", "source_file": SOURCE_FILE,
    },
]

if any(row["statement_id"] in by_id for row in new_rows):
    raise SystemExit("split p.361 statement ID already exists")
for row in new_rows:
    lines = body_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]]
    if row["original_quote"] not in "\n".join(lines):
        raise SystemExit(f"split quote is not present in source: {row['statement_id']}")
    if row["subject_candidate_id"] not in {candidate["candidate_id"] for candidate in csv.DictReader(open(ROOT / "04-knowledge/tables/entity-candidates.csv", encoding="utf-8-sig"))}:
        raise SystemExit(f"split statement subject candidate missing: {row['statement_id']}")
    rows.append(row)

fields, mention_rows = None, []
with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    mention_rows = list(reader)
required_anchors = {
    (BODY, "cand-2569", "Tiepolo"), (BODY, "cand-10409", "Spain"),
    (BODY, "cand-3461", "Italy"), (BODY, "cand-1950", "Pittoni"),
    (BODY, "cand-0005", "Accademia"), (BODY, "cand-9622", "Schulenburg collection"),
    (BODY, "cand-5529", "Germany"), (BODY, "cand-10429", "revival of Venetian painting"),
}
available_anchors = {(row["segment_id"], row["candidate_id"], row["surface_form"]) for row in mention_rows}
missing_anchors = required_anchors - available_anchors
if missing_anchors:
    raise SystemExit(f"required reviewed p.361 mention anchors missing: {sorted(missing_anchors)}")

output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
segment_rows_after = [row for row in rows if row.get("segment_id") == BODY]
note_rows_after = [row for row in rows if row.get("segment_id") == NOTES and row.get("statement_id", "").startswith("st-chp15-p361-")]
report = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "body": {"statements": len(segment_rows_after), "true": sum(row["qualifiers"].get("relation_candidate") is True for row in segment_rows_after), "false": sum(row["qualifiers"].get("relation_candidate") is False for row in segment_rows_after), "unset": sum("relation_candidate" not in row["qualifiers"] for row in segment_rows_after)},
    "notes": {"statements": len(note_rows_after), "true": sum(row["qualifiers"].get("relation_candidate") is True for row in note_rows_after), "false": sum(row["qualifiers"].get("relation_candidate") is False for row in note_rows_after), "unset": sum("relation_candidate" not in row["qualifiers"] for row in note_rows_after)},
    "added_atomic_statements": [row["statement_id"] for row in new_rows],
    "new_open_endpoint_candidate": "st-chp15-p361-men-encouraged-revival-venetian-painting",
    "before_sha256": TABLE_SHA256, "after_sha256": sha(output),
    "backup": TABLE.name + BACKUP_SUFFIX,
}
print(json.dumps(report, ensure_ascii=False, indent=2))

if ARGS.apply:
    original = TABLE.read_bytes()
    backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
    if backup.exists():
        if backup.read_bytes() != original:
            raise SystemExit(f"existing recovery copy differs from current file: {backup.name}")
    else:
        shutil.copy2(TABLE, backup)
    try:
        atomic_write(TABLE, output)
    except Exception:
        TABLE.write_bytes(original)
        raise
