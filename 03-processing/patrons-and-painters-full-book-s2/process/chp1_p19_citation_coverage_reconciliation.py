"""Finish p.19 citation coverage and remove footnote text duplicated in body S2."""
from __future__ import annotations

import argparse
import copy
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
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
CHAPTER = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md"
SECTION = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-1.pdf"

EXPECTED_HASHES = {
    STATEMENTS: "fcfc726b65fca418bd6ec2787c94385b074e61e30bc5b2e3b404663521e72bc6",
    MENTIONS: "4c3819877ef5c8c7f0fabb4dc1f8abcede1d0e5e866c4bdbe9e413e4cd2767c9",
    COVERAGE: "092f341b98f7119ae9ee6e14b1f15a035c00316af7ac7cd1daf1b0f914daeb8a",
    CANDIDATES: "b45c5ad6c5be4f2e16ea51ed2c782aa06745d7b80af993066df42255395f570f",
    CHAPTER: "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
    SECTION: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    PDF: "0b9a3ca88e6f09209bd20185948e18a68f527d0628e893940a7e3f07f6d22c86",
}

BODY_SEGMENT = "chp-1:01_CHP-1_sec_ii:l129-135"
NOTES_SEGMENT = "chp-1:01_CHP-1_sec_ii:l168-239"
BODY4_ID = "st-chp1-secii-l129-135-04"
NOTE1_ID = "m-chp1-secii-p19-n1-baldinucci-p78"
NOTE2_ID = "m-chp1-secii-p19-n2-pascoli-vol1-p122"
NOTE3_I_ID = "m-chp1-secii-p19-n3-pascoli-vol1-p122"
NOTE3_II_ID = "m-chp1-secii-p19-n3-pascoli-vol2-pp202-205"

EXPECTED_SPANS = {
    "Baldinucci, 1948, p. 78.": (7633, 7657),
    "Pascoli, l, p. 122": (7660, 7678),
    "Pascoli, I, p. 122": (7756, 7774),
    "II, pp. 202 and 205": (7776, 7795),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(stream.name)
    temp_path.replace(path)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames or [], list(reader), had_bom, newline


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]], had_bom: bool, newline: str) -> None:
    encoding = "utf-8-sig" if had_bom else "utf-8"
    with tempfile.NamedTemporaryFile("w", encoding=encoding, newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(stream.name)
    temp_path.replace(path)


def by_key(rows: list[dict], key: str) -> dict[str, dict]:
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise SystemExit(f"duplicate {key}")
    return result


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"input hash changed: {path.relative_to(ROOT)}")

chapter_lines = CHAPTER.read_text(encoding="utf-8").splitlines()
section_lines = SECTION.read_text(encoding="utf-8").splitlines()
section_text = "\n".join(section_lines[167:239])
for surface, (start, end) in EXPECTED_SPANS.items():
    if section_text[start:end] != surface:
        raise SystemExit(f"canonical citation span changed: {surface}")

statements = read_jsonl(STATEMENTS)
old_statements = copy.deepcopy(statements)
statement_by_id = by_key(statements, "statement_id")
body4 = statement_by_id.get(BODY4_ID)
if not body4 or body4.get("segment_id") != BODY_SEGMENT:
    raise SystemExit("p.19 closing body statement missing or moved")
if (body4["qualifiers"].get("source_line_start"), body4["qualifiers"].get("source_line_end")) != (791, 797):
    raise SystemExit("p.19 closing body statement source lines changed")
if body4.get("original_quote", "").count("\n1 Baldinucci, 1948, p. 78.") != 1:
    raise SystemExit("expected duplicate footnote tail is missing or changed")
body_quote = "\n".join(chapter_lines[790:795])

candidate_fields, candidate_rows, candidate_bom, candidate_newline = read_csv(CANDIDATES)
candidates = by_key(candidate_rows, "candidate_id")
for candidate_id in ("cand-4548", "cand-4834", "cand-4552"):
    if candidates.get(candidate_id, {}).get("suggested_type") != "archive":
        raise SystemExit(f"citation archive candidate missing or type changed: {candidate_id}")

mention_fields, mentions, mention_bom, mention_newline = read_csv(MENTIONS)
old_mentions = copy.deepcopy(mentions)
mention_by_id = by_key(mentions, "mention_id")
new_mention_ids = [NOTE1_ID, NOTE2_ID, NOTE3_I_ID, NOTE3_II_ID]
if any(mention_id in mention_by_id for mention_id in new_mention_ids):
    raise SystemExit("a planned note 1-3 citation mention id already exists")

coverage_fields, coverage_rows, coverage_bom, coverage_newline = read_csv(COVERAGE)
old_coverage = copy.deepcopy(coverage_rows)
coverage_by_id = by_key(coverage_rows, "segment_id")
body_coverage = coverage_by_id.get(BODY_SEGMENT)
notes_coverage = coverage_by_id.get(NOTES_SEGMENT)
if not body_coverage or not notes_coverage:
    raise SystemExit("p.19 coverage rows missing")
if body_coverage.get("source_line_ranges") != "L763-797":
    raise SystemExit("body coverage range changed before footnote-boundary correction")
if "L796-806" not in notes_coverage.get("source_line_ranges", ""):
    raise SystemExit("canonical note coverage range changed")

body4["qualifiers"]["source_line_end"] = 795
body4["original_quote"] = body_quote
body_coverage["source_line_ranges"] = "L763-795"
body_coverage["note"] = (
    f"{body_coverage['note'].rstrip()} OCR L796-797 are footnotes, not body text; they are covered "
    f"only by the consolidated notes segment L796-806."
)
notes_coverage["note"] = (
    f"{notes_coverage['note'].rstrip()} Notes 1-3 citation locators link respectively to the "
    f"Baldinucci 1948, Pascoli vol. I, and Pascoli vols. I/II archive candidates. The p.19 scan "
    f"prints Roman I in note 2 while S0 OCR has lowercase l; OCR remains unchanged. The cited "
    f"pages were not independently consulted."
)

mentions.extend(
    [
        {
            "mention_id": NOTE1_ID,
            "segment_id": NOTES_SEGMENT,
            "candidate_id": "cand-4548",
            "surface_form": "Baldinucci, 1948, p. 78.",
            "start_char": "7633",
            "end_char": "7657",
            "note": (
                "Exact p.19 note 1 citation locator; the bibliography identifies Baldinucci's "
                "1948 Bernini biography; cited p.78 was not independently consulted."
            ),
        },
        {
            "mention_id": NOTE2_ID,
            "segment_id": NOTES_SEGMENT,
            "candidate_id": "cand-4834",
            "surface_form": "Pascoli, l, p. 122",
            "start_char": "7660",
            "end_char": "7678",
            "note": (
                "Exact p.19 note 2 locator mapped to the bibliography's Pascoli vol. I candidate; "
                "the scan prints Roman I while S0 OCR has lowercase l; p.122 was not consulted."
            ),
        },
        {
            "mention_id": NOTE3_I_ID,
            "segment_id": NOTES_SEGMENT,
            "candidate_id": "cand-4834",
            "surface_form": "Pascoli, I, p. 122",
            "start_char": "7756",
            "end_char": "7774",
            "note": (
                "Exact p.19 note 3 vol. I locator mapped to the bibliography's Pascoli vol. I "
                "candidate; cited p.122 was not independently consulted."
            ),
        },
        {
            "mention_id": NOTE3_II_ID,
            "segment_id": NOTES_SEGMENT,
            "candidate_id": "cand-4552",
            "surface_form": "II, pp. 202 and 205",
            "start_char": "7776",
            "end_char": "7795",
            "note": (
                "Exact continuation of p.19 note 3's Pascoli citation, mapped to the bibliography's "
                "vol. II candidate; cited pp.202 and 205 were not independently consulted."
            ),
        },
    ]
)

# Assert the planned delta before writing: one existing statement, four appended mentions,
# and two coverage rows with only the intended fields changed.
statement_by_id_after = by_key(statements, "statement_id")
if set(statement_by_id_after) - set(by_key(old_statements, "statement_id")):
    raise SystemExit("unexpected statement additions planned")
old_body4 = by_key(old_statements, "statement_id")[BODY4_ID]
if {
    key for key in old_body4 if old_body4.get(key) != body4.get(key)
} != {"qualifiers", "original_quote"}:
    raise SystemExit("unexpected p.19 body statement fields changed")
if body4["qualifiers"].get("source_line_end") != 795:
    raise SystemExit("planned body end line is not L795")
if len(mentions) != len(old_mentions) + 4:
    raise SystemExit("planned mention count is not +4")
if len(coverage_rows) != len(old_coverage):
    raise SystemExit("coverage row count changed")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated p.19 citation/coverage closure")
args = parser.parse_args()
print("verified four exact note 1-3 citation spans and archive candidate types")
print("planned body boundary: remove OCR footnotes L796-797 from the p.19 body statement and coverage range")
print("planned additions: 4 citation mentions; sources remain cited but unconsulted")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp1-p19-citation-coverage-"))
for path in (STATEMENTS, MENTIONS, COVERAGE):
    shutil.copy2(path, backup_dir / path.name)
write_jsonl(STATEMENTS, statements)
write_csv(MENTIONS, mention_fields, mentions, mention_bom, mention_newline)
write_csv(COVERAGE, coverage_fields, coverage_rows, coverage_bom, coverage_newline)

written_statements = by_key(read_jsonl(STATEMENTS), "statement_id")
written_mentions = by_key(read_csv(MENTIONS)[1], "mention_id")
written_coverage = by_key(read_csv(COVERAGE)[1], "segment_id")
if written_statements[BODY4_ID]["qualifiers"]["source_line_end"] != 795:
    raise SystemExit("post-write body source boundary failed; recovery copies retained")
if any(mention_id not in written_mentions for mention_id in new_mention_ids):
    raise SystemExit("post-write citation mention check failed; recovery copies retained")
if written_coverage[BODY_SEGMENT]["source_line_ranges"] != "L763-795":
    raise SystemExit("post-write coverage boundary failed; recovery copies retained")
print(f"applied citation/coverage closure; recovery copies: {backup_dir}")
