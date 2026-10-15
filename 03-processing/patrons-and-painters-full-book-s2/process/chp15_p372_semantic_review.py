"""Controlled semantic refinement for the already-migrated printed p.372."""
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
BODY = "chp-15:15_CHP-15_sec_ii:l85-88"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
TABLE_SHA = "587ec6ca072a237dff3b6288ead4c615847e72bb2467d197d268dfdc8d56b01c"
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
BACKUP_SUFFIX = ".bak-s2-chp15-p372-semantic-review-20261009"

OLD_MAFFEI_ID = "st-chp15-p372-maffei-collected-sculpture-and-recorded-past"
OLD_COMPARISON_ID = "st-chp15-p372-querini-returned-to-ideal-past-compared-with-winckelmann"
NEW_IDS = {
    "st-chp15-p372-pagan-shrines-lacked-significance-for-most-contemporaries",
    "st-chp15-p372-maffei-recorded-evidence-of-the-past",
    "st-chp15-p372-querini-retired-from-contemporary-politics",
    "st-chp15-p372-querini-returned-to-ideal-world-of-past",
}
PREV_STATEMENT = "st-chp15-p371-querini-renier-canova-bust-commission-partial"
DOGE_STATEMENT = "st-chp15-p372-renier-became-doge-1779"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.372 statements")
args = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


for path, expected, label in (
    (TABLE, TABLE_SHA, "statement table"),
    (SOURCE, SOURCE_SHA, "chapter 15 source"),
    (PDF, PDF_SHA, "registered CHP-15 PDF"),
):
    if sha(path) != expected:
        raise SystemExit(f"{label} changed since this review's dry-run baseline")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_text = "\n".join(source_lines[84:88])
note_text = "\n".join(source_lines[89:113])

rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
if len(rows) != 12562:
    raise SystemExit(f"unexpected statement-table size: {len(rows)}")
by_id = {row["statement_id"]: row for row in rows}
if len(by_id) != len(rows):
    raise SystemExit("statement IDs are not unique")

expected_existing = {
    "st-chp15-p372-renier-became-doge-1779",
    "st-chp15-p372-renier-compromised-with-opposing-forces",
    "st-chp15-p372-querini-threw-renier-bust-at-furies-altar",
    "st-chp15-p372-querini-pagan-shrines-personal-significance",
    OLD_MAFFEI_ID,
    "st-chp15-p372-querini-distinguished-from-maffei",
    OLD_COMPARISON_ID,
    "st-chp15-p372-rousseau-influence-on-querini-view-of-past",
    "st-chp15-p372-querini-heart-buried-at-temple-of-pallas",
    "st-chp15-p372-note1-cites-brunelli-bonetti-1951",
    "st-chp15-p372-note1-bust-at-museo-civico-padua",
    "st-chp15-p372-note1-suggested-servants-lavatories",
}
actual_existing = {row["statement_id"] for row in rows if row.get("segment_id") in {BODY, NOTES}
                   and row["statement_id"].startswith("st-chp15-p372-")}
if actual_existing != expected_existing:
    raise SystemExit(f"p.372 statement set changed: {sorted(actual_existing ^ expected_existing)}")
if NEW_IDS & by_id.keys():
    raise SystemExit("one or more reviewed statement IDs already exist")
previous = by_id.get(PREV_STATEMENT)
if (previous is None
        or previous.get("qualifiers", {}).get("predicate_status") != "complete"
        or previous.get("qualifiers", {}).get("cross_reference_statement_ids") != [DOGE_STATEMENT]):
    raise SystemExit("p.371-to-p.372 continuation link is not in the expected complete state")

def assert_quote(text, segment_text, label):
    if normalized(text) not in normalized(segment_text):
        raise SystemExit(f"quote no longer matches its source segment: {label}")


def edit(statement_id, *, new_id=None, predicate=None, claim=None, qualification=None,
         quote=None, subject=..., object_id=..., mentioned_ids=None, text_layer=None,
         source_line_start=None, source_line_end=None):
    row = by_id[statement_id]
    if quote is not None:
        segment_text = body_text if row["segment_id"] == BODY else note_text
        assert_quote(quote, segment_text, statement_id)
        row["original_quote"] = quote
    if new_id:
        if new_id in by_id and new_id != statement_id:
            raise SystemExit(f"replacement statement ID already exists: {new_id}")
        del by_id[statement_id]
        row["statement_id"] = new_id
        by_id[new_id] = row
    if predicate is not None:
        row["predicate"] = predicate
    if subject is not ...:
        row["subject_candidate_id"] = subject
    if object_id is not ...:
        row["object_candidate_id"] = object_id
    q = row["qualifiers"]
    if claim is not None:
        q["claim"] = claim
    if qualification is not None:
        q["qualification"] = qualification
    if mentioned_ids is not None:
        q["mentioned_candidate_ids"] = mentioned_ids
    if text_layer is not None:
        q["text_layer"] = text_layer
    if source_line_start is not None:
        q["source_line_start"] = source_line_start
    if source_line_end is not None:
        q["source_line_end"] = source_line_end


def make_statement(statement_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, text_layer, qualification, mentioned_ids, quote):
    assert_quote(quote, body_text, statement_id)
    return {
        "statement_id": statement_id,
        "segment_id": BODY,
        "subject_candidate_id": subject_id,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": start_line,
            "source_line_end": end_line,
            "printed_page": 372,
            "pdf_physical_page": 12,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": text_layer,
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned_ids,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
    }


edits = {
    "st-chp15-p372-renier-compromised-with-opposing-forces": dict(
        quote="When, later, Renier compromised with the forces that he had once attacked,",
    ),
    "st-chp15-p372-querini-threw-renier-bust-at-furies-altar": dict(
        quote="Querini flung the bust in a rage of disappointment against the Altar of\nFuries in his garden.",
    ),
    "st-chp15-p372-querini-pagan-shrines-personal-significance": dict(
        claim="Haskell says the shrines and temples of paganism had real significance for Querini, whether sentimental or romantic.",
        qualification="This is Haskell's interpretation of Querini's relation to pagan antiquity; it does not establish his formal religious beliefs.",
        quote="For him the shrines and temples of paganism had a real significance, however sentimental or romantic",
    ),
    OLD_MAFFEI_ID: dict(
        new_id="st-chp15-p372-maffei-collected-antique-sculpture",
        predicate="collected_antique_sculpture",
        claim="Haskell says Scipione Maffei, in an earlier generation, also collected antique sculpture.",
        qualification="This is Haskell's comparison; the passage does not specify particular objects collected by Maffei.",
        quote="Scipione Maffei who in an earlier generation had also collected antique sculpture",
    ),
    "st-chp15-p372-querini-distinguished-from-maffei": dict(
        quote="It is this that distinguishes his activities so greatly from those of a man like Scipione Maffei",
    ),
    OLD_COMPARISON_ID: dict(
        new_id="st-chp15-p372-querini-return-compared-with-winckelmann",
        predicate="querini_return_to_ideal_past_compared_with_winckelmann_despite_less_insight",
        claim="Haskell places Querini's return to an ideal world of the past above Winckelmann's, while qualifying that Querini had far less intellectual or critical insight.",
        qualification="This records Haskell's comparative judgment and explicit qualification; it is not an independent assessment of either man's insight.",
        quote="More even than Winckelmann\n\u2014though, of course, with far less intellectual or critical insight\u2014",
        mentioned_ids=["cand-2075", "cand-2816"],
        text_layer="authorial interpretation",
    ),
    "st-chp15-p372-rousseau-influence-on-querini-view-of-past": dict(
        quote="And his view of it was inextricably bound up with the influence of Rousseau.",
    ),
    "st-chp15-p372-querini-heart-buried-at-temple-of-pallas": dict(
        quote="When he died in 1796 his heart was, at his request, buried in the Temple of Pallas in his garden.",
    ),
    "st-chp15-p372-note1-cites-brunelli-bonetti-1951": dict(
        quote="1 Brunelli Bonetti, 1951.",
    ),
    "st-chp15-p372-note1-bust-at-museo-civico-padua": dict(
        quote="what must be the bust (in terracotta) survives in the Museo Civico at Padua",
    ),
    "st-chp15-p372-note1-suggested-servants-lavatories": dict(
        quote="and as it shows no obvious signs of irreparable damage it has been suggested that Querini kept it in the servants\u2019 lavatories.",
    ),
}

original_ids = list(by_id)
for statement_id, values in edits.items():
    edit(statement_id, **values)

new_rows = [
    make_statement(
        "st-chp15-p372-pagan-shrines-lacked-significance-for-most-contemporaries",
        "cand-2075", None, "shrines_lacked_significance_for_most_scholars_and_antiquarians",
        87, 87,
        "Haskell contrasts Querini's relation to pagan shrines and temples with most scholars and antiquarians of his age, for whom they lacked comparable significance.",
        "authorial interpretation",
        "'Most' is retained as Haskell's qualification; the passage does not generalize the contrast to every scholar or antiquarian.",
        ["cand-2075"],
        "that they lacked for most of the scholars and antiquarians of his age.",
    ),
    make_statement(
        "st-chp15-p372-maffei-recorded-evidence-of-the-past",
        "cand-1487", None, "recorded_evidence_of_the_past",
        87, 87,
        "Haskell says Maffei, in an earlier generation, lovingly recorded evidence of the past.",
        "authorial comparison",
        "'Lovingly' is Haskell's characterization; the passage does not identify particular records.",
        ["cand-1487"],
        "lovingly recorded the evidences of the past.",
    ),
    make_statement(
        "st-chp15-p372-querini-retired-from-contemporary-politics",
        "cand-2075", None, "retired_from_contemporary_politics_and_unsolved_problems",
        87, 88,
        "Haskell describes Querini as baffled by contemporary politics and problems that henceforward admitted of no solution, before his return to the past.",
        "authorial interpretation",
        "The passage supplies no date or specific list of these political problems; 'baffled' follows Haskell's characterization.",
        ["cand-2075"],
        "Querini, after his baffled retirement from contemporary politics and problems that henceforward admitted of no solution,",
    ),
    make_statement(
        "st-chp15-p372-querini-returned-to-ideal-world-of-past",
        "cand-2075", None, "returned_to_ideal_world_of_the_past",
        88, 88,
        "Haskell says Querini returned to the ideal world of the past.",
        "authorial interpretation",
        "'Ideal world' is Haskell's interpretive description, not a named or independently identified place.",
        ["cand-2075"],
        "returned to the ideal world of the past.",
    ),
]

for row in new_rows:
    if row["statement_id"] in by_id:
        raise SystemExit(f"new statement ID already exists: {row['statement_id']}")

insert_after = "st-chp15-p372-querini-heart-buried-at-temple-of-pallas"
position = next(i for i, row in enumerate(rows) if row["statement_id"] == insert_after) + 1
rows[position:position] = new_rows

for row in rows:
    if row.get("segment_id") in {BODY, NOTES} and row.get("statement_id", "").startswith("st-chp15-p372-"):
        quote_source = body_text if row["segment_id"] == BODY else note_text
        assert_quote(row["original_quote"], quote_source, row["statement_id"])

if not args.apply:
    print(json.dumps({
        "mode": "dry-run",
        "table_sha256": TABLE_SHA,
        "p372_statements_before": 12,
        "p372_statements_after": 16,
        "new_statements": sorted(NEW_IDS),
        "renamed_statements": {
            OLD_MAFFEI_ID: "st-chp15-p372-maffei-collected-antique-sculpture",
            OLD_COMPARISON_ID: "st-chp15-p372-querini-return-compared-with-winckelmann",
        },
        "candidates_or_mentions_changed": False,
        "p371_cross_reference_preserved": previous["qualifiers"]["cross_reference_statement_ids"],
        "source_quotes_checked": 16,
        "backup": TABLE.name + BACKUP_SUFFIX,
    }, ensure_ascii=False, indent=2))
    raise SystemExit(0)

backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
if backup.exists() and sha(backup) != TABLE_SHA:
    raise SystemExit(f"recovery copy already exists: {backup.name}")
if not backup.exists():
    shutil.copy2(TABLE, backup)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as handle:
    for row in rows:
        handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(handle.name)
temporary.replace(TABLE)
print(json.dumps({
    "mode": "applied",
    "statements_before": 12562,
    "statements_after": len(rows),
    "new_statements": sorted(NEW_IDS),
    "renamed_statements": 2,
    "recovery_copy": str(backup.relative_to(ROOT)),
    "table_sha256_after": sha(TABLE),
}, ensure_ascii=False, indent=2))
