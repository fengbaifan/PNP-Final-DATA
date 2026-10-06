"""Controlled S2 migration for p.204 notes 1-3 in the composite note segment.

Default invocation validates and previews only. --apply writes the S2 tables
with recoverable backups after checking both source fingerprints and the
expected current table state.
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
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l126-157"
P204_BODY_ID = "chp-8:08_CHP-8_sec_i:l14-21"
EXPECTED_MAX_CANDIDATE = 7577
BACKUP_SUFFIX = ".bak-s2-chp8-p204-notes-20260930"

NOTE1_BODY = "st-chp8-p204-ricci-leading-patron"
NOTE2_BODY = "st-chp8-p204-crespi-paintings-reflect-travel-influences"
NOTE3_GIORDANO_BODY = "st-chp8-p204-valletta-patron-of-giordano"
NOTE3_SOLIMENA_BODY = "st-chp8-p204-valletta-patron-of-solimena"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)

segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}

segment = segments.get(SEGMENT_ID)
if not segment or segment["source_file"] != SOURCE_REL:
    raise SystemExit(f"source segment metadata missing or changed: {SEGMENT_ID}")
if (int(segment["line_start"]), int(segment["line_end"])) != (126, 157):
    raise SystemExit(f"source segment line range changed: {SEGMENT_ID}")

source_path = ROOT / SOURCE_REL
source_bytes = source_path.read_bytes()
if hashlib.sha256(source_bytes).hexdigest() != segment["asset_sha256"]:
    raise SystemExit(f"source asset fingerprint changed: {SOURCE_REL}")
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[125:157]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit(f"source line-slice hash changed: {SEGMENT_ID}")
if segment_lines[1:4] != [
    "1 Zanotti, II, p. 3 5, and L. Crespi, pp. 204 and 244.",
    "2 See especially The Marriage at Cana of about 1686, now in Chicago, which shows the impact of Veronese and Barocci—van der Rohe, pp. 6-9.",
    "3 De Dominici, IV, p. 141, and Bologna, pp. 181 and 203. Valletta used to help Luca Giordano with his problems of iconography (de Dominici, IV, p. 196) and bought from another collector a number of architectural paintings by Codazzi with figures by Cerquozzi and Micco Spadaro (ibid., Ill, p. 421).",
]:
    raise SystemExit("p.204 note source text changed; re-review before migration")

note_coverage = coverage_by_id.get(SEGMENT_ID)
if not note_coverage or (note_coverage["disposition"], note_coverage["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"unexpected composite-note coverage state: {note_coverage}")
if note_coverage.get("source_line_ranges"):
    raise SystemExit("composite-note coverage already has processed ranges; review before continuing")

body_coverage = coverage_by_id.get(P204_BODY_ID)
if not body_coverage or (body_coverage["disposition"], body_coverage["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"unexpected p.204 body coverage state: {body_coverage}")

body_statement_ids = {row["statement_id"] for row in statement_rows if row["segment_id"] == P204_BODY_ID}
required_body_statements = {NOTE1_BODY, NOTE2_BODY, NOTE3_GIORDANO_BODY, NOTE3_SOLIMENA_BODY}
if not required_body_statements <= body_statement_ids:
    raise SystemExit(f"p.204 body statements missing: {sorted(required_body_statements - body_statement_ids)}")

current_max = max(
    int(row["candidate_id"].split("-")[1])
    for row in candidate_rows
    if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()
)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")

EXISTING = {
    "zanotti_book": "cand-7115",
    "de_dominici": "cand-4835",
    "bologna_book": "cand-7348",
    "chicago": "cand-4624",
    "veronese": "cand-2755",
    "barocci": "cand-0247",
    "valletta": "cand-2686",
    "giordano": "cand-1172",
    "codazzi": "cand-0794",
    "cerquozzi": "cand-0625",
    "spadaro": "cand-2495",
}
if not set(EXISTING.values()) <= candidate_ids:
    raise SystemExit("one or more planned existing candidate IDs are absent")

CANDIDATE_SPECS = [
    (
        "lcrespi_cited_work",
        "Unidentified work cited as L. Crespi, pp. 204 and 244 (p.204 n.1)",
        "archive",
        "The p.204 note supplies only the abbreviated citation and page numbers, not a title, edition, or resolved author identity. Do not equate this reference with Giuseppe Maria Crespi; bibliography review and global identity alignment remain open.",
        127,
    ),
    (
        "van_der_rohe_cited_work",
        "Unidentified publication cited as van der Rohe, pp. 6-9 (p.204 n.2)",
        "archive",
        "The p.204 note gives only a short citation and page range. The full author form, title, edition, and bibliographic identity are unresolved; the cited pages have not been independently read.",
        128,
    ),
    (
        "marriage_at_cana",
        "The Marriage at Cana (reported c.1686, Chicago; p.204 n.2)",
        "work",
        "Haskell identifies a Marriage at Cana of about 1686, then in Chicago, as showing the impact of Veronese and Barocci. The note follows the p.204 discussion of Crespi's pictures for Ricci, and the index has a Crespi subentry for Marriage at Cana; retain this as a distinct work candidate, not the artist index candidate. Exact work identity and attribution alignment remain for S3.",
        128,
    ),
    (
        "unidentified_collector",
        "Unidentified collector from whom Giuseppe Valletta bought Codazzi paintings (p.204 n.3)",
        "person",
        "Haskell reports that Valletta bought a number of architectural paintings from another collector but gives no name or further identifying detail. Preserve the seller role as an unresolved relation endpoint.",
        129,
    ),
    (
        "codazzi_architectural_paintings",
        "Unidentified architectural paintings by Viviano Codazzi with figures by Cerquozzi and Micco Spadaro (p.204 n.3)",
        "work",
        "A number of architectural paintings are reported as bought by Valletta from another collector; Codazzi is named for the architecture and Cerquozzi and Micco Spadaro for the figures. No individual title, count, date, or current location is supplied.",
        129,
    ),
]

candidate_by_key = {}
new_candidates = []
next_number = current_max + 1
for key, name, suggested_type, detail, line_number in CANDIDATE_SPECS:
    candidate_id = f"cand-{next_number:04d}"
    next_number += 1
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID collision: {candidate_id}")
    if any(row.get("canonical_name") == name for row in candidate_rows):
        raise SystemExit(f"candidate natural key already exists; reuse or reconcile: {name}")
    candidate_by_key[key] = candidate_id
    new_candidates.append(
        {
            "candidate_id": candidate_id,
            "index_entry_id": "",
            "canonical_name": name,
            "index_page_range": "",
            "suggested_type": suggested_type,
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": detail,
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line_number}",
        }
    )


def cid(key: str) -> str:
    return candidate_by_key[key] if key in candidate_by_key else EXISTING[key]


MENTION_SPECS = [
    (127, "Zanotti", "zanotti_book", 0, "Short author citation for the two-volume Storia dell’Accademia Clementina; vol. II p.35 is a locator, not independently read."),
    (127, "L. Crespi", "lcrespi_cited_work", 0, "Abbreviated bibliographic citation only; do not identify with Giuseppe Maria Crespi or expand the title."),
    (128, "The Marriage at Cana", "marriage_at_cana", 0, "Named painting described in p.204 note 2; kept distinct from the artist's index candidate."),
    (128, "Chicago", "chicago", 0, "Reported current location in Haskell’s note; reuse the existing Chicago place candidate."),
    (128, "Veronese", "veronese", 0, "Painter named as an influence on the referenced painting."),
    (128, "Barocci", "barocci", 0, "Painter named as an influence on the referenced painting."),
    (128, "van der Rohe", "van_der_rohe_cited_work", 0, "Short bibliographic citation; full work and author identity unresolved."),
    (129, "De Dominici", "de_dominici", 0, "First citation to the four-volume Vite; vol. IV p.141."),
    (129, "Bologna", "bologna_book", 0, "Short citation to Ferdinando Bologna’s Francesco Solimena; cited pages not independently read."),
    (129, "Valletta", "valletta", 0, "Giuseppe Valletta, already identified in the p.204 body."),
    (129, "Luca Giordano", "giordano", 0, "Artist named in Haskell’s report of Valletta’s help with iconography."),
    (129, "de Dominici", "de_dominici", 0, "Second citation to de Dominici, vol. IV p.196."),
    (129, "another collector", "unidentified_collector", 0, "Unnamed seller from whom Valletta reportedly bought the paintings; identity unresolved."),
    (129, "a number of architectural paintings", "codazzi_architectural_paintings", 0, "Unspecified group of architectural paintings; individual works and exact count are not given."),
    (129, "Codazzi", "codazzi", 0, "Viviano Codazzi, named for the architectural paintings."),
    (129, "Cerquozzi", "cerquozzi", 0, "Michelangelo Cerquozzi, named for figures in the paintings."),
    (129, "Micco Spadaro", "spadaro", 0, "Micco Spadaro, named for figures in the paintings."),
    (129, "ibid.", "de_dominici", 0, "Anaphoric citation to de Dominici, here volume III p.421."),
]

line_offsets = {}
offset = 0
for number in range(126, 158):
    line_offsets[number] = offset
    offset += len(source_lines[number - 1]) + 1

new_mentions = []
for index, (line_number, surface, key, occurrence, note) in enumerate(MENTION_SPECS, 1):
    line = source_lines[line_number - 1]
    spans = [match.span() for match in __import__("re").finditer(__import__("re").escape(surface), line)]
    if occurrence >= len(spans):
        raise SystemExit(
            f"mention not found: L{line_number} {surface!r}; found {len(spans)} occurrence(s)"
        )
    local_start, local_end = spans[occurrence]
    start_char = line_offsets[line_number] + local_start
    end_char = line_offsets[line_number] + local_end
    if segment_text[start_char:end_char] != surface:
        raise SystemExit(f"mention offset mismatch: L{line_number} {surface!r}")
    new_mentions.append(
        {
            "mention_id": f"m-chp8-p204-note-{index:03d}",
            "segment_id": SEGMENT_ID,
            "candidate_id": cid(key),
            "surface_form": surface,
            "start_char": str(start_char),
            "end_char": str(end_char),
            "note": note,
        }
    )


def make_statement(
    statement_id,
    subject_candidate_id,
    object_candidate_id,
    predicate,
    line_start,
    line_end,
    claim,
    qualification,
    original_quote,
    mentioned_candidate_ids,
    footnote_number,
    *,
    text_layer="footnote",
    speaker="Haskell",
    linked_body_statement_ids=None,
    citations=None,
    relation_candidate=False,
    ocr_corrections=None,
    extra_qualifiers=None,
):
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 204,
        "pdf_physical_page": 2,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned_candidate_ids,
        "footnote_number": footnote_number,
    }
    if linked_body_statement_ids:
        qualifiers["linked_body_statement_ids"] = linked_body_statement_ids
    if citations is not None:
        qualifiers["citations"] = citations
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if ocr_corrections:
        qualifiers["ocr_corrections"] = ocr_corrections
    if extra_qualifiers:
        qualifiers.update(extra_qualifiers)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject_candidate_id,
        "object_candidate_id": object_candidate_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": original_quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


new_statements = [
    make_statement(
        "st-chp8-p204-n1-citations",
        None,
        cid("zanotti_book"),
        "footnote_citation",
        127,
        127,
        "P.204 note 1 cites Zanotti, volume II page 35, and an L. Crespi reference at pages 204 and 244, alongside Haskell’s identification of Giovanni Ricci.",
        "The cited pages are bibliographic locators and were not independently read. The L. Crespi work is cited only by an abbreviated reference; its title and author identity remain unresolved.",
        "Zanotti, II, p. 3 5, and L. Crespi, pp. 204 and 244.",
        [cid("zanotti_book"), cid("lcrespi_cited_work")],
        1,
        text_layer="bibliographic citation",
        speaker="Haskell footnote",
        linked_body_statement_ids=[NOTE1_BODY],
        citations=[
            {"source_candidate_id": cid("zanotti_book"), "volume": "II", "page": "35"},
            {"source_candidate_id": cid("lcrespi_cited_work"), "pages": ["204", "244"]},
        ],
        ocr_corrections=[
            {
                "source_file": SOURCE_REL,
                "source_line": 127,
                "ocr": "p. 3 5",
                "print": "p. 35",
                "basis": "CHP-8.pdf physical page 2.",
            }
        ],
    ),
    make_statement(
        "st-chp8-p204-n2-citation",
        None,
        cid("van_der_rohe_cited_work"),
        "footnote_citation",
        128,
        128,
        "P.204 note 2 cites van der Rohe, pages 6-9, for the painting and its stylistic impact.",
        "The cited work is not identified beyond the short citation; cited pages were not independently read.",
        "van der Rohe, pp. 6-9.",
        [cid("van_der_rohe_cited_work")],
        2,
        text_layer="bibliographic citation",
        speaker="Haskell footnote",
        linked_body_statement_ids=[NOTE2_BODY],
        citations=[{"source_candidate_id": cid("van_der_rohe_cited_work"), "pages": ["6", "9"]}],
    ),
    make_statement(
        "st-chp8-p204-marriage-at-cana-date-and-location",
        cid("marriage_at_cana"),
        cid("chicago"),
        "painting_reported_as_about_1686_and_now_in_chicago",
        128,
        128,
        "Haskell identifies The Marriage at Cana as dating to about 1686 and says it was then in Chicago.",
        "The note follows the p.204 discussion of pictures Crespi painted for Ricci and the index has a Crespi subentry for Marriage at Cana; preserve this contextual attribution without aligning the exact work identity before S3.",
        "The Marriage at Cana of about 1686, now in Chicago",
        [cid("marriage_at_cana"), cid("chicago")],
        2,
        linked_body_statement_ids=[NOTE2_BODY],
        relation_candidate=True,
        extra_qualifiers={"reported_date": "about 1686"},
    ),
    make_statement(
        "st-chp8-p204-marriage-at-cana-influence",
        cid("marriage_at_cana"),
        cid("veronese"),
        "painting_said_to_show_impact_of_veronese_and_barocci",
        128,
        128,
        "Haskell says the painting shows the impact of Veronese and Barocci.",
        "This is Haskell’s stylistic assessment as reported in the footnote; neither this judgment nor the cited source pages are independently verified here. Barocci is retained as a second mentioned artist in the statement.",
        "which shows the impact of Veronese and Barocci",
        [cid("marriage_at_cana"), cid("veronese"), cid("barocci")],
        2,
        linked_body_statement_ids=[NOTE2_BODY],
        relation_candidate=True,
    ),
    make_statement(
        "st-chp8-p204-n3-patronage-citations",
        None,
        cid("de_dominici"),
        "footnote_citation",
        129,
        129,
        "P.204 note 3 cites De Dominici, volume IV page 141, and Bologna, pages 181 and 203, alongside Haskell’s characterization of Valletta as a patron.",
        "These are source locators in Haskell’s note; the cited passages are not independently read.",
        "De Dominici, IV, p. 141, and Bologna, pp. 181 and 203.",
        [cid("de_dominici"), cid("bologna_book")],
        3,
        text_layer="bibliographic citation",
        speaker="Haskell footnote",
        linked_body_statement_ids=[NOTE3_GIORDANO_BODY, NOTE3_SOLIMENA_BODY],
        citations=[
            {"source_candidate_id": cid("de_dominici"), "volume": "IV", "page": "141"},
            {"source_candidate_id": cid("bologna_book"), "pages": ["181", "203"]},
        ],
    ),
    make_statement(
        "st-chp8-p204-valletta-helps-giordano-iconography",
        cid("valletta"),
        cid("giordano"),
        "valletta_reported_to_help_giordano_with_iconography",
        129,
        129,
        "Haskell reports that Valletta used to help Luca Giordano with iconographic problems.",
        "This is Haskell’s report citing De Dominici, volume IV page 196; the cited page is not independently read. Preserve the past-tense report and do not infer a particular commission or work.",
        "Valletta used to help Luca Giordano with his problems of iconography",
        [cid("valletta"), cid("giordano")],
        3,
        linked_body_statement_ids=[NOTE3_GIORDANO_BODY],
        relation_candidate=True,
    ),
    make_statement(
        "st-chp8-p204-n3-giordano-iconography-citation",
        None,
        cid("de_dominici"),
        "footnote_citation",
        129,
        129,
        "P.204 note 3 cites De Dominici, volume IV page 196, for Haskell’s report that Valletta helped Giordano with iconographic problems.",
        "Citation location only; the cited page is not independently read.",
        "de Dominici, IV, p. 196",
        [cid("de_dominici"), cid("valletta"), cid("giordano")],
        3,
        text_layer="bibliographic citation",
        speaker="Haskell footnote",
        linked_body_statement_ids=[NOTE3_GIORDANO_BODY, "st-chp8-p204-valletta-helps-giordano-iconography"],
        citations=[{"source_candidate_id": cid("de_dominici"), "volume": "IV", "page": "196"}],
    ),
    make_statement(
        "st-chp8-p204-valletta-bought-codazzi-paintings",
        cid("valletta"),
        cid("codazzi_architectural_paintings"),
        "valletta_bought_codazzi_paintings_from_another_collector",
        129,
        129,
        "Haskell reports that Valletta bought a number of architectural paintings from another collector; Codazzi is named for the architecture and Cerquozzi and Micco Spadaro for the figures.",
        "The note cites De Dominici, volume III page 421, which Haskell uses as his source; the page is not independently read. The seller is unnamed, the works are not individually identified, and the statement remains an S2 relation candidate rather than a formal edge.",
        "and bought from another collector a number of architectural paintings by Codazzi with figures by Cerquozzi and Micco Spadaro",
        [
            cid("valletta"),
            cid("unidentified_collector"),
            cid("codazzi_architectural_paintings"),
            cid("codazzi"),
            cid("cerquozzi"),
            cid("spadaro"),
        ],
        3,
        linked_body_statement_ids=[NOTE3_GIORDANO_BODY, NOTE3_SOLIMENA_BODY],
        relation_candidate=True,
    ),
    make_statement(
        "st-chp8-p204-n3-codazzi-paintings-citation",
        None,
        cid("de_dominici"),
        "footnote_citation",
        129,
        129,
        "P.204 note 3 cites De Dominici, volume III page 421, for the Codazzi architectural paintings and their figure painters.",
        "The abbreviation ibid. refers back to De Dominici; volume III is read from the printed page image, while the cited page itself is not independently read.",
        "ibid., Ill, p. 421",
        [cid("de_dominici"), cid("codazzi_architectural_paintings")],
        3,
        text_layer="bibliographic citation",
        speaker="Haskell footnote",
        linked_body_statement_ids=["st-chp8-p204-valletta-bought-codazzi-paintings"],
        citations=[{"source_candidate_id": cid("de_dominici"), "volume": "III", "page": "421"}],
        ocr_corrections=[
            {
                "source_file": SOURCE_REL,
                "source_line": 129,
                "ocr": "ibid., Ill, p. 421",
                "print": "ibid., III, p. 421",
                "basis": "CHP-8.pdf physical page 2.",
            }
        ],
    ),
]

planned_candidate_ids = {row["candidate_id"] for row in new_candidates}
planned_mention_ids = {row["mention_id"] for row in new_mentions}
planned_statement_ids = {row["statement_id"] for row in new_statements}
if len(planned_candidate_ids) != len(new_candidates) or candidate_ids & planned_candidate_ids:
    raise SystemExit("planned candidate IDs collide")
if len(planned_mention_ids) != len(new_mentions) or mention_ids & planned_mention_ids:
    raise SystemExit("planned mention IDs collide")
if len(planned_statement_ids) != len(new_statements) or statement_ids & planned_statement_ids:
    raise SystemExit("planned statement IDs collide")

all_candidate_ids = candidate_ids | planned_candidate_ids
for row in new_mentions:
    if row["candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"mention has unknown candidate: {row['mention_id']}")
for row in new_statements:
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in all_candidate_ids:
            raise SystemExit(f"statement has unknown candidate: {row['statement_id']} -> {candidate_id}")

candidate_new = candidate_rows + new_candidates
mention_new = mention_rows + new_mentions
statement_new = statement_rows + new_statements
coverage_new = []
for row in coverage_rows:
    copied = dict(row)
    if copied["segment_id"] == SEGMENT_ID:
        copied["disposition"] = "reviewed"
        copied["migration_status"] = "partial"
        copied["source_line_ranges"] = "L127-129"
        copied["note"] = (
            "P.204 footnotes 1-3 read against CHP-8.pdf physical p.2 and migrated. "
            "Zanotti II p.35, Bologna pp.181/203, and de Dominici III/IV references are locators only; "
            "the cited pages were not independently read. Added the c.1686 Marriage at Cana work candidate, "
            "the unresolved L. Crespi and van der Rohe citation candidates, Valletta's iconography help for "
            "Giordano, and the unnamed collector/Codazzi painting group. Printed p.35 and III were corrected "
            "in S2 only. L130-L157 remain pending."
        )
    elif copied["segment_id"] == P204_BODY_ID:
        copied["migration_status"] = "complete"
        copied["note"] = (
            "P.204 body read against CHP-8.pdf physical p.2. Footnotes 1-3 have now been migrated from "
            "the composite source segment L127-L129 and linked to their body statements. Citation locators "
            "are not independent verification; S0 OCR remains unchanged."
        )
    coverage_new.append(copied)


def preview():
    print(f"validated segment: {SEGMENT_ID} lines 126-157")
        print(f"processed source range: L127-129 (p.204 notes 1-3)")
    print(f"new candidates: {len(new_candidates)}; IDs {new_candidates[0]['candidate_id']}..{new_candidates[-1]['candidate_id']}")
    print(f"new mentions: {len(new_mentions)}")
    print(f"new statements: {len(new_statements)}")
    print(f"p.204 body coverage: reviewed/complete")
        print(f"composite note coverage: reviewed/partial, L127-129; L130-157 pending")


def apply():
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    write_csv_atomic(candidate_path, candidate_fields, candidate_new)
    write_csv_atomic(mention_path, mention_fields, mention_new)
    write_jsonl_atomic(statement_path, statement_new)
    write_csv_atomic(coverage_path, coverage_fields, coverage_new)
    print("APPLIED; recovery backups retained pending audits:")
    for backup in backups:
        print(backup.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks pass")
    args = parser.parse_args()
    preview()
    if args.apply:
        apply()
    else:
        print("DRY RUN: no files written")


if __name__ == "__main__":
    main()
