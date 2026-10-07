"""Close the reviewed Chapter 2 p.40 footnote links and relation candidates.

Hash-locked to the source, PDF, pre-migration tables, and current candidates.
Dry-run is the default; pass --apply only after reviewing the plan.
"""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-2.pdf"

EXPECTED_HASHES = {
    STATEMENTS: "d322e3b1be951ec0c6e8ca44cae4e9c0ae5ff5bf68a5da944895c0ec432e5448",
    MENTIONS: "68fd3fd001a75f775121c62611aac6ca0871218d30968a63881164e955b4378d",
    COVERAGE: "44487e05a6e3c4e7c594861bb3b202dd8e417de8ce8c5424de2feeaf7fe20566",
    CANDIDATES: "b45c5ad6c5be4f2e16ea51ed2c782aa06745d7b80af993066df42255395f570f",
    SOURCE: "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
    PDF: "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
}

BODY_SEGMENT = "chp-2:02_CHP-2_sec_ii:l91-104"
NOTES_SEGMENT = "chp-2:02_CHP-2_sec_ii:l147-193"
BODY_IDS = {
    "poems": "st-chp2-secii-l91-104-urban-poems-nature-and-country-life",
    "villa": "st-chp2-secii-l91-104-urban-villa-added-to-castle",
    "diplomats": "st-chp2-secii-l91-104-urban-delegates-business-audiences-to-nephew",
    "astrology": "st-chp2-secii-l91-104-urban-religion-superstition-and-astrology",
    "rule": "st-chp2-secii-l91-104-urban-rule-and-papacy-aggrandizement",
    "busts": "st-chp2-secii-l91-104-bernini-makes-urban-portrait-busts",
}
NOTE_IDS = {
    1: ["st-chp2-secii-l147-193-cite-bonomelli-p41-69"],
    2: ["st-chp2-secii-l147-193-cite-terrebasse-p40"],
    3: [
        "st-chp2-secii-l147-193-astrology-surveillance-inference",
        "st-chp2-secii-l147-193-campanella-surveillance",
        "st-chp2-secii-l147-193-campanella-urban-research",
        "st-chp2-secii-l147-193-cite-walker-p205ff",
        "st-chp2-secii-l147-193-cite-bazzoni-surveillance",
        "st-chp2-secii-l147-193-cite-bertolotti1878",
    ],
    4: ["st-chp2-secii-l147-193-galileo-example"],
    5: ["st-chp2-secii-l147-193-cite-wittkower55-p184"],
}
SURVEILLANCE_ID = "st-chp2-secii-l147-193-campanella-surveillance"
RESEARCH_ID = "st-chp2-secii-l147-193-campanella-urban-research"
WALKER_PERSON_MENTION_ID = "m-chp2-secii-l147-193-dp-walker-person"

OLD_QUALIFICATIONS = {
    BODY_IDS["poems"]: "This is Haskell’s account of the poems and their setting. Footnote 1 awaits cross-linking.",
    BODY_IDS["villa"]: "The villa and castle are distinct place candidates; neither castle identity nor the villa’s date is specified. Footnote 1 awaits cross-linking.",
    BODY_IDS["diplomats"]: "Nephew, diplomats and occasions are not identified. Footnote 2 awaits cross-linking.",
    BODY_IDS["astrology"]: "“Crude” is Haskell’s evaluative wording. Footnote 3 awaits cross-linking.",
    BODY_IDS["rule"]: "This is Haskell’s assessment. Footnote 4 qualifies “petty meanness”; it is not independent validation of the broader evaluation.",
    BODY_IDS["busts"]: "OCR reads “his.career”; print p.40 reads “his career.” Individual works and dates are not identified. Footnote 5 awaits cross-linking.",
}
NEW_QUALIFICATIONS = {
    BODY_IDS["poems"]: "This is Haskell’s account of the poems and their setting. Note 1 cites Bonomelli, pp. 41–69; the cited pages were not independently consulted.",
    BODY_IDS["villa"]: "The villa and castle are distinct place candidates; neither castle identity nor the villa’s date is specified. Note 1 cites Bonomelli, pp. 41–69; the cited pages were not independently consulted.",
    BODY_IDS["diplomats"]: "Nephew, diplomats and occasions are not identified. Note 2 cites Alfred de Terrebasse, p. 40; the cited page was not independently consulted.",
    BODY_IDS["astrology"]: "“Crude” is Haskell’s evaluative wording. Note 3 cites D. P. Walker, pp. 205 ff., Bazzoni, and A. Bertolotti (1878); these cited materials were not independently consulted. Haskell reports Walker’s material as showing Campanella’s help with Urban VIII’s astrological research and explicitly presents the surveillance connection as his inference.",
    BODY_IDS["rule"]: "This is Haskell’s assessment. Note 4 identifies Urban VIII’s treatment of Galileo as an example of “petty meanness,” while acknowledging its deeper implications; it does not independently validate Haskell’s broader evaluation.",
    BODY_IDS["busts"]: "OCR reads “his.career”; print p.40 reads “his career.” Individual works and dates are not identified. Note 5 cites Wittkower (1955), p. 184; the cited page was not independently consulted.",
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

source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
expected_fragments = {
    97: "simple country life",
    98: "literary discussions which were nearer his heart.2",
    99: "dabbled extensively in astrology.3",
    101: "his.career.5",
    180: "1 Bonomelli, pp. 41-69.",
    181: "2 Alfred de Terrebasse, p. 40.",
    182: "3 Urban VIII’s astrological pursuits are well documented",
    183: "4 Such as",
    184: "5 Wittkower, 1955, p. 184.",
}
for line_number, fragment in expected_fragments.items():
    if fragment not in source_lines[line_number - 1]:
        raise SystemExit(f"expected canonical S0 text changed at L{line_number}: {fragment}")
if "D. P. Walker, pp. 205 if." not in source_lines[181] or "Campanella hi Paris" not in source_lines[181]:
    raise SystemExit("expected p.40 OCR forms for page-image correction changed")

section_text = "\n".join(source_lines[146:193])
walker_start = section_text.find("D. P. Walker, pp. 205 if.")
if walker_start < 0 or section_text[walker_start : walker_start + len("D. P. Walker")] != "D. P. Walker":
    raise SystemExit("D. P. Walker person mention span changed")
walker_end = walker_start + len("D. P. Walker")

statements = read_jsonl(STATEMENTS)
old_statements = copy.deepcopy(statements)
statement_by_id = by_key(statements, "statement_id")
body_markers = {
    BODY_IDS["poems"]: (1, 180),
    BODY_IDS["villa"]: (1, 180),
    BODY_IDS["diplomats"]: (2, 181),
    BODY_IDS["astrology"]: (3, 182),
    BODY_IDS["rule"]: (4, 183),
    BODY_IDS["busts"]: (5, 184),
}
for statement_id, (marker, note_line) in body_markers.items():
    row = statement_by_id.get(statement_id)
    if not row or row.get("segment_id") != BODY_SEGMENT:
        raise SystemExit(f"body statement missing or moved: {statement_id}")
    q = row.get("qualifiers", {})
    if q.get("footnote_marker") != marker or q.get("footnote_segment") != NOTES_SEGMENT:
        raise SystemExit(f"footnote marker/segment changed: {statement_id}")
    if q.get("footnote_link_status") != "pending_source_migration":
        raise SystemExit(f"footnote status is no longer pending: {statement_id}")
    if q.get("footnote_refs") or q.get("footnote_statement_ids"):
        raise SystemExit(f"body footnote links already exist: {statement_id}")
    if q.get("qualification") != OLD_QUALIFICATIONS[statement_id]:
        raise SystemExit(f"body qualification changed since review: {statement_id}")
    if not any(statement_id in statement_by_id[nid]["qualifiers"].get("linked_body_statement_ids", []) for nid in NOTE_IDS[marker]):
        raise SystemExit(f"matching note statement does not link back to body: {statement_id}")

required_candidates = {
    "cand-0209": "person",
    "cand-0491": "person",
    "cand-1105": "person",
    "cand-3464": "family",
    "cand-4383": "archive",
    "cand-4568": "archive",
    "cand-4569": "archive",
    "cand-4570": "archive",
    "cand-4571": "person",
    "cand-4573": "archive",
    "cand-4574": "archive",
}
candidate_rows = read_csv(CANDIDATES)[1]
candidates = by_key(candidate_rows, "candidate_id")
for candidate_id, candidate_type in required_candidates.items():
    candidate = candidates.get(candidate_id)
    if not candidate or candidate.get("suggested_type") != candidate_type:
        raise SystemExit(f"required candidate missing/type changed: {candidate_id}")
if candidates["cand-4571"].get("canonical_name") != "D. P. Walker":
    raise SystemExit("the note-specific D. P. Walker person candidate changed")

for note_id in {sid for values in NOTE_IDS.values() for sid in values}:
    row = statement_by_id.get(note_id)
    if not row or row.get("segment_id") != NOTES_SEGMENT:
        raise SystemExit(f"existing p.40 note statement missing or moved: {note_id}")

surveillance = statement_by_id.get(SURVEILLANCE_ID)
research = statement_by_id.get(RESEARCH_ID)
if not surveillance or not research:
    raise SystemExit("note 3 relation statements are missing")
if surveillance.get("subject_candidate_id") != "cand-3464" or surveillance.get("object_candidate_id") != "cand-0491":
    raise SystemExit("surveillance relation endpoints changed")
if research.get("subject_candidate_id") != "cand-0491" or research.get("object_candidate_id") != "cand-0209":
    raise SystemExit("research-assistance relation endpoints changed")
for row in (surveillance, research):
    if row["qualifiers"].get("relation_candidate") is not None:
        raise SystemExit(f"relation-candidate status already set: {row['statement_id']}")
if research["qualifiers"].get("qualification") != "This is Haskell’s account of Walker’s publication; source title and edition remain unresolved.":
    raise SystemExit("Walker source qualification changed since review")

mention_fields, mentions, mention_bom, mention_newline = read_csv(MENTIONS)
old_mentions = copy.deepcopy(mentions)
mention_by_id = by_key(mentions, "mention_id")
if WALKER_PERSON_MENTION_ID in mention_by_id:
    raise SystemExit("planned D. P. Walker person mention already exists")
if any(m.get("candidate_id") == "cand-4571" and m.get("segment_id") == NOTES_SEGMENT for m in mentions):
    raise SystemExit("a D. P. Walker person mention already exists in the note segment")
walker_archive = mention_by_id.get("m-chp2-secii-l147-193-0065")
if not walker_archive or walker_archive.get("candidate_id") != "cand-4570" or walker_archive.get("start_char") != str(walker_start):
    raise SystemExit("existing Walker publication citation mention changed")

coverage_fields, coverage_rows, coverage_bom, coverage_newline = read_csv(COVERAGE)
old_coverage = copy.deepcopy(coverage_rows)
coverage_by_id = by_key(coverage_rows, "segment_id")
body_coverage = coverage_by_id.get(BODY_SEGMENT)
if not body_coverage or body_coverage.get("migration_status") != "complete":
    raise SystemExit("p.40 body coverage row missing or incomplete")
pending_phrase = "Five footnotes await processing/cross-linking to sec_ii:l147-193."
if pending_phrase not in body_coverage.get("note", ""):
    raise SystemExit("expected stale p.40 coverage note not found")

for statement_id, (marker, note_line) in body_markers.items():
    q = statement_by_id[statement_id]["qualifiers"]
    q.update(
        {
            "footnote_text_pending": False,
            "footnote_link_status": "resolved_source_migration",
            "footnote_body_link_status": "linked",
            "footnote_segment": NOTES_SEGMENT,
            "footnote_source_line": note_line,
            "footnote_refs": [{"marker": marker, "segment_id": NOTES_SEGMENT, "source_line": note_line}],
            "footnote_statement_ids": NOTE_IDS[marker],
            "qualification": NEW_QUALIFICATIONS[statement_id],
        }
    )

surveillance["qualifiers"].update(
    {
        "relation_candidate": True,
        "relation_candidate_note": (
            "Reported family-level agency in Haskell’s footnote: the source says the Barberini "
            "ordered surveillance of Campanella. No individual or date is identified; the cited "
            "Bazzoni source and underlying record were not independently consulted."
        ),
        "qualification": (
            "The note attributes the account to Bazzoni and quotes the stated purpose; no date or "
            "archival record is identified. “The Barberini” is retained as the family-level wording; "
            "no individual is named, and neither Bazzoni nor the underlying record was independently consulted."
        ),
    }
)
research["qualifiers"].update(
    {
        "relation_candidate": True,
        "relation_candidate_note": (
            "Reported research assistance in Haskell’s summary of D. P. Walker: Campanella helped "
            "Urban VIII in astrological researches. Walker and pp. 205 ff. were not independently consulted."
        ),
        "qualification": (
            "This is Haskell’s account of Walker’s publication. The bibliography identifies the work as "
            "Spiritual and demonic magic from Ficino to Campanella (London, 1958); Walker and the cited "
            "pp. 205 ff. were not independently consulted."
        ),
    }
)

mentions.append(
    {
        "mention_id": WALKER_PERSON_MENTION_ID,
        "segment_id": NOTES_SEGMENT,
        "candidate_id": "cand-4571",
        "surface_form": "D. P. Walker",
        "start_char": str(walker_start),
        "end_char": str(walker_end),
        "note": (
            "Named scholar reported as publishing material on Urban VIII and Campanella; identity "
            "remains unresolved. The overlapping full citation span is separately mapped to archive candidate cand-4570."
        ),
    }
)

body_coverage["note"] = body_coverage["note"].replace(
    pending_phrase,
    "Printed p.40 footnotes 1–5 are linked to their note statements at L180–184; marker 1 supports both the nature-poem and villa statements. Note 3 records Walker’s reported assistance and the attributed surveillance account, while Haskell’s connection between surveillance and astrology remains explicitly an inference. The cited works, materials, and pages were not independently consulted.",
)

changed_statement_ids = set(BODY_IDS.values()) | {SURVEILLANCE_ID, RESEARCH_ID}
old_by_id = by_key(old_statements, "statement_id")
new_by_id = by_key(statements, "statement_id")
if set(old_by_id) != set(new_by_id):
    raise SystemExit("statement row IDs/count changed unexpectedly")
for statement_id in old_by_id:
    if statement_id not in changed_statement_ids:
        if old_by_id[statement_id] != new_by_id[statement_id]:
            raise SystemExit(f"unexpected statement delta: {statement_id}")
        continue
    old_row, new_row = old_by_id[statement_id], new_by_id[statement_id]
    if {k for k in old_row if old_row.get(k) != new_row.get(k)} != {"qualifiers"}:
        raise SystemExit(f"unexpected top-level statement delta: {statement_id}")
if len(mentions) != len(old_mentions) + 1 or len(coverage_rows) != len(old_coverage):
    raise SystemExit("unexpected mention or coverage count delta")
old_coverage_by_id = by_key(old_coverage, "segment_id")
for segment_id, old_row in old_coverage_by_id.items():
    new_row = coverage_by_id[segment_id]
    expected_fields = {"note"} if segment_id == BODY_SEGMENT else set()
    changed = {k for k in old_row if old_row.get(k) != new_row.get(k)}
    if changed != expected_fields:
        raise SystemExit(f"unexpected coverage delta: {segment_id}: {changed}")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.40 link closure")
args = parser.parse_args()
relation_count_before = sum(bool(r.get("qualifiers", {}).get("relation_candidate")) for r in old_statements)
print("verified CHP-2.pdf physical p.21, S0 p.40 body/notes, existing note statements, candidate FKs, and citation spans")
print("planned body closure: 6 statements link markers 1-5 to note statements L180-184; marker 1 has two body targets")
print("planned semantic correction: mark Campanella→Urban VIII research assistance and Barberini-family→Campanella surveillance as S2 relation candidates; preserve Haskell's separate inference")
print("planned entity coverage: add one D. P. Walker person mention overlapping the existing archive citation mention")
print("planned counts: statements unchanged; mentions +1; S2 relation candidates +2; no formal relations written")
print(f"relation candidates before: {relation_count_before}")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp2-p40-footnotes-"))
for path in (STATEMENTS, MENTIONS, COVERAGE):
    shutil.copy2(path, backup_dir / path.name)
write_jsonl(STATEMENTS, statements)
write_csv(MENTIONS, mention_fields, mentions, mention_bom, mention_newline)
write_csv(COVERAGE, coverage_fields, coverage_rows, coverage_bom, coverage_newline)

written_statements = by_key(read_jsonl(STATEMENTS), "statement_id")
written_mentions = by_key(read_csv(MENTIONS)[1], "mention_id")
written_coverage = by_key(read_csv(COVERAGE)[1], "segment_id")
for statement_id in BODY_IDS.values():
    q = written_statements[statement_id]["qualifiers"]
    if q.get("footnote_link_status") != "resolved_source_migration" or q.get("footnote_body_link_status") != "linked":
        raise SystemExit(f"post-write footnote link failed: {statement_id}; recovery copies retained")
if not all(written_statements[sid]["qualifiers"].get("relation_candidate") is True for sid in (SURVEILLANCE_ID, RESEARCH_ID)):
    raise SystemExit("post-write relation-candidate flags failed; recovery copies retained")
if written_mentions[WALKER_PERSON_MENTION_ID].get("candidate_id") != "cand-4571":
    raise SystemExit("post-write D. P. Walker person mention failed; recovery copies retained")
if pending_phrase in written_coverage[BODY_SEGMENT].get("note", ""):
    raise SystemExit("post-write coverage note still claims the footnotes are pending; recovery copies retained")
relation_count_after = sum(bool(r.get("qualifiers", {}).get("relation_candidate")) for r in written_statements.values())
if relation_count_after != relation_count_before + 2:
    raise SystemExit("post-write relation-candidate count failed; recovery copies retained")
print(
    f"applied p.40 footnote and relation-candidate reconciliation; relation candidates now {relation_count_after}; "
    f"recovery copies: {backup_dir}"
)
