"""Reconcile Chapter 1 p.19 footnote links, citations, and relation candidates.

The script is hash-locked to the reviewed source and pre-migration tables.
It performs a dry-run by default; pass --apply only after reviewing the plan.
"""
from __future__ import annotations

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
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
CHAPTER = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md"
SECTION = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-1.pdf"

EXPECTED_HASHES = {
    STATEMENTS: "278fc5d4383edcea5e6c66b3121654235c014428805be2b9bb8b3b49ada83294",
    MENTIONS: "eca192c38952bef07c1fea00534ce123e8433f23b8d8a90c8ba10709ffed4a88",
    COVERAGE: "9ea7f371956b5abe277cd887f4d5f48d87f2dc205f01c4f0fc3885149e1d596a",
    CANDIDATES: "b45c5ad6c5be4f2e16ea51ed2c782aa06745d7b80af993066df42255395f570f",
    CHAPTER: "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
    SECTION: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    PDF: "0b9a3ca88e6f09209bd20185948e18a68f527d0628e893940a7e3f07f6d22c86",
}

BODY_SEGMENT = "chp-1:01_CHP-1_sec_ii:l129-135"
NOTES_SEGMENT = "chp-1:01_CHP-1_sec_ii:l168-239"
BODY_IDS = {
    "symbolic": "st-chp1-secii-l129-135-01",
    "titles": "st-chp1-secii-l129-135-02",
    "education": "st-chp1-secii-l129-135-03",
}
NOTE4_CONTEXT_ID = "st-chp1-secii-notes-early-honours"
RELATION_IDS = {
    "frederick": "st-chp1-secii-p19-n4-frederick-bellini-honor",
    "charles": "st-chp1-secii-p19-n4-charlesv-titian-honor",
}
NOTE6_ID = "st-chp1-secii-p19-n6-cerquozzi-passeri-citation"
MENTION_CERQUOZZI_ID = "m-chp1-secii-0543"
MENTION_PASCOLI_CITATION_ID = "m-chp1-secii-p19-n5-pascoli-vol2-p202"
MENTION_PASSERI_CITATION_ID = "m-chp1-secii-p19-n6-passeri-p285"

OLD_EDUCATION_QUALIFICATION = (
    "Passeri’s words are an attributed professional polemic, not an objective "
    "character assessment of unnamed painters. A footnote attribution is handled "
    "in the pending notes segment."
)
NEW_EDUCATION_QUALIFICATION = (
    "Passeri’s words are an attributed professional polemic, not an objective "
    "character assessment of unnamed painters. Note 5 cites Pascoli, vol. II, "
    "p. 202, for the Lauri anecdote; the cited page was not independently consulted. "
    "Note 6 labels the immediately preceding Passeri passage as concerning "
    "Michelangelo Cerquozzi and cites p. 285; Haskell’s attribution is preserved, "
    "but the cited page was not independently consulted."
)

EXPECTED_OCR_NOTES = [
    "1 Baldinucci, 1948, p. 78.",
    "2 Pascoli, l, p. 122, where the episode is specifically compared to Charles V’s famous gesture.",
    "3 Pascoli, I, p. 122; II, pp. 202 and 205.",
    "4 There had, of course, been cases long before the seventeenth century: the Emperor Frederick III",
    "had bestowed on Gentile Bellini the dignity of Count Palatine, and in 1533 Charles V created Titian a",
    "Count of the Lateran Palace, of his Court and of the Imperial Consistory. But such honours, deeply",
    "significant though they were, had always been marks of the most exceptional favour. Towards the end",
    "of the sixteenth century in Rome the granting of titles to artists became a more routine affair with some",
    "of the attributes of our modern civil service grading and honours lists.",
    "5 Pascoli, II, p. 202.",
    "6 Of Michelangelo Cerquozzi—Passeri, p. 285.",
]


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
if chapter_lines[795:806] != EXPECTED_OCR_NOTES:
    raise SystemExit("canonical full-chapter OCR notes L796-806 changed")
section_text = "\n".join(section_lines[167:239])
expected_spans = {
    "Pascoli, II, p. 202.": (8377, 8397),
    "Passeri, p. 285.": (8426, 8442),
    "Michelangelo Cerquozzi": (8403, 8425),
}
for surface, (start, end) in expected_spans.items():
    if section_text[start:end] != surface:
        raise SystemExit(f"canonical section span changed: {surface}")

statements = read_jsonl(STATEMENTS)
statement_by_id = by_key(statements, "statement_id")
expected_body_rows = {
    BODY_IDS["symbolic"]: (BODY_SEGMENT, 763, 777),
    BODY_IDS["titles"]: (BODY_SEGMENT, 771, 777),
    BODY_IDS["education"]: (BODY_SEGMENT, 778, 790),
}
for statement_id, (segment_id, line_start, line_end) in expected_body_rows.items():
    row = statement_by_id.get(statement_id)
    if not row or row.get("segment_id") != segment_id:
        raise SystemExit(f"body statement anchor changed: {statement_id}")
    q = row.get("qualifiers", {})
    if (q.get("source_line_start"), q.get("source_line_end")) != (line_start, line_end):
        raise SystemExit(f"body source lines changed: {statement_id}")
education = statement_by_id[BODY_IDS["education"]]
if education["qualifiers"].get("qualification") != OLD_EDUCATION_QUALIFICATION:
    raise SystemExit("p.19 education-statement qualification changed")
note4 = statement_by_id.get(NOTE4_CONTEXT_ID)
if not note4 or note4.get("segment_id") != NOTES_SEGMENT:
    raise SystemExit("existing note 4 statement missing or moved")
if (note4["qualifiers"].get("source_line_start"), note4["qualifiers"].get("source_line_end")) != (796, 806):
    raise SystemExit("existing note 4 statement source lines changed")
if NOTE6_ID in statement_by_id or any(sid in statement_by_id for sid in RELATION_IDS.values()):
    raise SystemExit("planned statement id already exists")

candidate_fields, candidate_rows, candidate_bom, candidate_newline = read_csv(CANDIDATES)
candidates = by_key(candidate_rows, "candidate_id")
required_candidates = {
    "cand-1077": "person",
    "cand-0269": "person",
    "cand-3019": "person",
    "cand-2630": "person",
    "cand-3539": "place",
    "cand-3524": "institution",
    "cand-0625": "person",
    "cand-1856": "person",
    "cand-4552": "archive",
    "cand-4376": "archive",
}
for candidate_id, suggested_type in required_candidates.items():
    candidate = candidates.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != suggested_type:
        raise SystemExit(f"required candidate missing or type changed: {candidate_id}")

mention_fields, mentions, mention_bom, mention_newline = read_csv(MENTIONS)
mention_by_id = by_key(mentions, "mention_id")
cerquozzi_mention = mention_by_id.get(MENTION_CERQUOZZI_ID)
if not cerquozzi_mention or cerquozzi_mention.get("candidate_id") != "cand-0633":
    raise SystemExit("p.19 Cerquozzi mention mapping changed")
if (cerquozzi_mention.get("surface_form"), cerquozzi_mention.get("start_char"), cerquozzi_mention.get("end_char")) != (
    "Michelangelo Cerquozzi", "8403", "8425"
):
    raise SystemExit("p.19 Cerquozzi mention span changed")
for mention_id in (MENTION_PASCOLI_CITATION_ID, MENTION_PASSERI_CITATION_ID):
    if mention_id in mention_by_id:
        raise SystemExit(f"planned mention id already exists: {mention_id}")

coverage_fields, coverage_rows, coverage_bom, coverage_newline = read_csv(COVERAGE)
coverage_by_id = by_key(coverage_rows, "segment_id")
body_coverage = coverage_by_id.get(BODY_SEGMENT)
notes_coverage = coverage_by_id.get(NOTES_SEGMENT)
if not body_coverage or not notes_coverage:
    raise SystemExit("p.19 coverage rows missing")
if body_coverage["migration_status"] != "complete" or notes_coverage["migration_status"] != "complete":
    raise SystemExit("p.19 coverage is no longer complete")
if "L763-797" not in body_coverage["source_line_ranges"] or "L796-806" not in notes_coverage["source_line_ranges"]:
    raise SystemExit("p.19 coverage source ranges changed")


def body_footnote_fields(markers: list[int], note_lines: list[int], statement_ids: list[str]) -> dict:
    refs = [
        {"marker": marker, "segment_id": NOTES_SEGMENT, "source_line": source_line}
        for marker, source_line in zip(markers, note_lines, strict=True)
    ]
    return {
        "footnote_marker": markers[0],
        "footnote_text_pending": False,
        "footnote_link_status": "resolved_source_migration",
        "footnote_body_link_status": "linked",
        "footnote_segment": NOTES_SEGMENT,
        "footnote_source_line": note_lines[0],
        "footnote_refs": refs,
        "footnote_statement_ids": statement_ids,
    }


body1 = statement_by_id[BODY_IDS["symbolic"]]
body1["qualifiers"].update(body_footnote_fields([1, 2, 3], [796, 797, 798], []))
body2 = statement_by_id[BODY_IDS["titles"]]
body2["qualifiers"].update(
    body_footnote_fields(
        [4],
        [799],
        [NOTE4_CONTEXT_ID, RELATION_IDS["frederick"], RELATION_IDS["charles"]],
    )
)
education["qualifiers"]["qualification"] = NEW_EDUCATION_QUALIFICATION
education["qualifiers"].update(body_footnote_fields([5, 6], [805, 806], [NOTE6_ID]))

note4_context_quote = "\n".join(
    ["But such honours, deeply", *chapter_lines[801:804]]
)
note4["qualifiers"].update(
    {
        "source_line_start": 801,
        "source_line_end": 804,
        "printed_page": 19,
        "pdf_physical_page": 18,
        "claim": (
            "Haskell's footnote distinguishes exceptional earlier honours from the more routine "
            "granting of artist titles in Rome by the late sixteenth century."
        ),
        "speaker": "Haskell, footnote",
        "text_layer": "authorial note",
        "qualification": (
            "This is Haskell's contextual generalization about the change from exceptional honours "
            "to more routine title-granting; it is not a complete history of artist titles."
        ),
        "mentioned_candidate_ids": [
            "cand-1077", "cand-0269", "cand-3019", "cand-2630", "cand-3539", "cand-3524"
        ],
        "footnote_number": 4,
        "related_body_statement_ids": [BODY_IDS["titles"]],
        "relation_candidate": False,
    }
)
note4["original_quote"] = note4_context_quote

new_statements = [
    {
        "statement_id": RELATION_IDS["frederick"],
        "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-1077",
        "object_candidate_id": "cand-0269",
        "predicate": "frederick_iii_bestowed_count_palatine_dignity_on_gentile_bellini",
        "qualifiers": {
            "source_line_start": 799,
            "source_line_end": 800,
            "printed_page": 19,
            "pdf_physical_page": 18,
            "claim": (
                "Haskell's footnote says Frederick III bestowed on Gentile Bellini the dignity "
                "of Count Palatine."
            ),
            "speaker": "Haskell, footnote",
            "text_layer": "authorial note",
            "qualification": (
                "The note supplies no exact year and frames the honour as a pre-seventeenth-century "
                "exceptional precedent."
            ),
            "mentioned_candidate_ids": ["cand-1077", "cand-0269"],
            "footnote_number": 4,
            "related_body_statement_ids": [BODY_IDS["titles"]],
            "time_qualifier": "before the seventeenth century; exact date not specified",
            "relation_candidate": True,
        },
        "original_quote": (
            "There had, of course, been cases long before the seventeenth century: the Emperor "
            "Frederick III\nhad bestowed on Gentile Bellini the dignity of Count Palatine"
        ),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/01_CHP-1.md",
    },
    {
        "statement_id": RELATION_IDS["charles"],
        "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-3019",
        "object_candidate_id": "cand-2630",
        "predicate": "charles_v_created_titian_count_of_lateran_palace_court_and_imperial_consistory_in_1533",
        "qualifiers": {
            "source_line_start": 800,
            "source_line_end": 801,
            "printed_page": 19,
            "pdf_physical_page": 18,
            "claim": (
                "Haskell's footnote says Charles V created Titian a Count of the Lateran Palace, "
                "of his Court and of the Imperial Consistory in 1533."
            ),
            "speaker": "Haskell, footnote",
            "text_layer": "authorial note",
            "qualification": (
                "Preserve the title's wording as Haskell gives it; do not parse the three institutional "
                "phrases into separate offices. Haskell frames this as exceptional favour."
            ),
            "mentioned_candidate_ids": ["cand-3019", "cand-2630", "cand-3539", "cand-3524"],
            "footnote_number": 4,
            "related_body_statement_ids": [BODY_IDS["titles"]],
            "time_qualifier": "1533",
            "relation_candidate": True,
        },
        "original_quote": (
            "and in 1533 Charles V created Titian a\n"
            + chapter_lines[800].split(" But such honours", 1)[0]
        ),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/01_CHP-1.md",
    },
    {
        "statement_id": NOTE6_ID,
        "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": "cand-4376",
        "predicate": "haskell_footnote_cites_passeri_p285_in_connection_with_cerquozzi",
        "qualifiers": {
            "source_line_start": 806,
            "source_line_end": 806,
            "printed_page": 19,
            "pdf_physical_page": 18,
            "claim": (
                "Haskell's footnote identifies Michelangelo Cerquozzi in connection with the "
                "immediately preceding passage attributed to Passeri and cites p. 285."
            ),
            "speaker": "Haskell, footnote",
            "text_layer": "bibliographic note / attribution",
            "qualification": (
                "This records Haskell's attribution only; the note does not independently establish "
                "the quoted assessment of Cerquozzi. Passeri p. 285 and the cited edition were not "
                "independently consulted."
            ),
            "mentioned_candidate_ids": ["cand-0625", "cand-1856", "cand-4376"],
            "footnote_number": 6,
            "related_body_statement_ids": [BODY_IDS["education"]],
            "cited_material_not_independently_consulted": True,
            "relation_candidate": False,
        },
        "original_quote": "Of Michelangelo Cerquozzi—Passeri, p. 285.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/01_CHP-1.md",
    },
]
statements.extend(new_statements)
statement_by_id = by_key(statements, "statement_id")

cerquozzi_mention["candidate_id"] = "cand-0625"
cerquozzi_mention["note"] = (
    "Footnote 6 identifies Cerquozzi in connection with the immediately preceding Passeri passage; "
    "the p.19 index-wide candidate is used, not the p.138-139 situation subentry."
)
mentions.extend(
    [
        {
            "mention_id": MENTION_PASCOLI_CITATION_ID,
            "segment_id": NOTES_SEGMENT,
            "candidate_id": "cand-4552",
            "surface_form": "Pascoli, II, p. 202.",
            "start_char": "8377",
            "end_char": "8397",
            "note": (
                "Exact p.19 note 5 citation locator for the Lauri anecdote; bibliography identifies "
                "Pascoli's Vite, vol. II; cited p.202 was not independently consulted."
            ),
        },
        {
            "mention_id": MENTION_PASSERI_CITATION_ID,
            "segment_id": NOTES_SEGMENT,
            "candidate_id": "cand-4376",
            "surface_form": "Passeri, p. 285.",
            "start_char": "8426",
            "end_char": "8442",
            "note": (
                "Exact p.19 note 6 citation locator; bibliography identifies the Jacob Hess 1934 "
                "edition; cited p.285 was not independently consulted."
            ),
        },
    ]
)

body_coverage["note"] = (
    f"{body_coverage['note'].rstrip()} Printed p.19 markers 1-3 link to notes L796-798; marker 4 "
    f"links to the artist-title statement, while marker 3 remains with the preceding Ghezzi anecdote. "
    f"Markers 5-6 link to the Lauri/Passeri passage and notes L805-806."
)
notes_coverage["note"] = (
    f"{notes_coverage['note'].rstrip()} Printed p.19 notes 1-6 were rechecked against CHP-1.pdf "
    f"physical p.18. Note 4 is represented by two explicit honour relation candidates and a separate "
    f"context statement; note 6 records Haskell's Cerquozzi attribution to Passeri p.285. Exact "
    f"Pascoli II p.202 and Passeri p.285 citation locators link to archive candidates; cited pages "
    f"were not independently consulted. No formal relations were written."
)

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated p.19 reconciliation")
args = parser.parse_args()
print("verified p.19 print page, canonical OCR lines, section spans, statement anchors, candidates, and coverage")
print("body links: note markers 1-3 -> the Ghezzi/symbolic-anecdote statement; 4 -> artist-title statement; 5-6 -> Lauri/Passeri statement")
print("note 4: two explicit relation candidates plus the separate exceptional-honour context statement")
print("note 6: Haskell's Cerquozzi attribution and Passeri p.285 locator; cited page remains unconsulted")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp1-p19-footnotes-"))
for path in (STATEMENTS, MENTIONS, COVERAGE):
    shutil.copy2(path, backup_dir / path.name)
write_jsonl(STATEMENTS, statements)
write_csv(MENTIONS, mention_fields, mentions, mention_bom, mention_newline)
write_csv(COVERAGE, coverage_fields, coverage_rows, coverage_bom, coverage_newline)

written_statements = by_key(read_jsonl(STATEMENTS), "statement_id")
written_mentions = by_key(read_csv(MENTIONS)[1], "mention_id")
if written_statements[NOTE6_ID]["qualifiers"]["related_body_statement_ids"] != [BODY_IDS["education"]]:
    raise SystemExit("post-write note 6 linkage failed; recovery copies retained")
if written_statements[BODY_IDS["titles"]]["qualifiers"]["footnote_statement_ids"] != [
    NOTE4_CONTEXT_ID, RELATION_IDS["frederick"], RELATION_IDS["charles"]
]:
    raise SystemExit("post-write note 4 body links failed; recovery copies retained")
if written_mentions[MENTION_CERQUOZZI_ID]["candidate_id"] != "cand-0625":
    raise SystemExit("post-write Cerquozzi candidate mapping failed; recovery copies retained")
if written_mentions[MENTION_PASCOLI_CITATION_ID]["candidate_id"] != "cand-4552":
    raise SystemExit("post-write Pascoli citation mapping failed; recovery copies retained")
if written_mentions[MENTION_PASSERI_CITATION_ID]["candidate_id"] != "cand-4376":
    raise SystemExit("post-write Passeri citation mapping failed; recovery copies retained")
print(
    "applied p.19 footnote, citation, and relation-candidate reconciliation; "
    f"recovery copies: {backup_dir}"
)
