"""Correct the p.306 note-1 body anchor from direct page-image evidence."""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
BODY = "chp-10:10_CHP-10_intro:l435-443"
BACKUP = ".bak-s2-chp10-p306-note1-anchor-repair-20261002"


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(f.name)
    temp.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if not lines[436].endswith("Visentini.1 ,") or "Aesculapio1 Blunt and Croft-Murray" not in lines[440]:
    raise SystemExit("p.306 OCR marker/citation evidence changed")

statements_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
statements = read_jsonl(statements_path)
by_id = {x["statement_id"]: x for x in statements}
citation = by_id.get("st-chp10-p306-note1-blunt-citation")
drawings = by_id.get("st-chp10-p306-pasquali-visentini-drawings")
breval = by_id.get("st-chp10-p306-breval-statuette")
if not citation or citation["object_candidate_id"] != "cand-9230":
    raise SystemExit("p.306 note-1 citation is not in the expected pre-repair state")
if not drawings or drawings["qualifiers"].get("footnote_marker") != 1 or drawings["qualifiers"].get("footnote_text_pending") is not True:
    raise SystemExit("Visentini drawings marker state changed")
if not breval or breval["qualifiers"].get("footnote_marker") != 1:
    raise SystemExit("Breval statuette has no erroneous marker to remove")

with coverage_path.open(encoding="utf-8-sig", newline="") as f:
    coverage_reader = csv.DictReader(f)
    coverage_fields = coverage_reader.fieldnames
    coverage_rows = list(coverage_reader)
coverage = next((x for x in coverage_rows if x["segment_id"] == BODY), None)
if not coverage or coverage["migration_status"] != "partial" or coverage["source_line_ranges"] != "L436-441":
    raise SystemExit("p.306 coverage state changed")
old_coverage_note = " P.306 note 1 is the OCR-inline citation at L441, visually confirmed as Blunt and Croft-Murray, pp.67 ff.; its body marker is resolved. Notes 2-6 remain for L612-L616."
if old_coverage_note not in coverage["note"]:
    raise SystemExit("p.306 coverage note differs from the expected pre-repair state")

print("dry-run: move p.306 note 1 to the Visentini drawings claim at L437 and remove it from the Breval claim at L441")
if not args.apply:
    raise SystemExit(0)

draw_q = drawings["qualifiers"]
draw_q["footnote_text_pending"] = False
draw_q["qualification"] = "Haskell says Smith retained original drawings, most by Visentini. Printed note 1 follows ‘Visentini’ on L437; its citation is OCR-inline after the Breval passage on L441. The scan reads pp.67 ff.; the cited pages were not consulted."

breval_q = breval["qualifiers"]
breval_q.pop("footnote_marker", None)
breval_q.pop("footnote_text_pending", None)
breval_q["qualification"] = "The p.307 continuation calls this same quoted object Priapus after p.306’s ‘seemingly an Aesculapio’; preserve both labels without resolving the statuette. The p.306 scan shows no footnote marker after this passage."

citation["object_candidate_id"] = "cand-9227"
citation["predicate"] = "cited_source_for_smiths_retention_of_original_visentini_drawings"
cq = citation["qualifiers"]
cq["claim"] = "Haskell cites Blunt and Croft-Murray, pp.67 ff., in connection with Smith retaining the original drawings, most of which were by Visentini."
cq["qualification"] = "The printed marker follows ‘Visentini’ on L437; OCR has placed the citation text inline after the Breval passage at L441. The scan reads ‘ff.’ where OCR reads ‘if’; the cited pages were not independently consulted."
cq["mentioned_candidate_ids"] = ["cand-0379", "cand-9339", "cand-9340", "cand-2440", "cand-9227", "cand-2783"]
cq["printed_marker_line"] = 437
cq["body_statement_id"] = "st-chp10-p306-pasquali-visentini-drawings"

coverage["note"] = coverage["note"].replace(
    old_coverage_note,
    " Physical note 1 follows ‘Visentini’ at L437 and is linked to the original-drawings statement. OCR places its citation text at L441; the Breval statuette passage has no marker. Notes 2-6 remain for L612-L616.",
)

shutil.copy2(statements_path, statements_path.with_name(statements_path.name + BACKUP))
shutil.copy2(coverage_path, coverage_path.with_name(coverage_path.name + BACKUP))
write_jsonl(statements_path, statements)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=coverage_path.parent, delete=False) as f:
    writer = csv.DictWriter(f, fieldnames=coverage_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(coverage_rows)
    temp = Path(f.name)
temp.replace(coverage_path)
print("applied; statement and coverage backups saved with suffix", BACKUP)
