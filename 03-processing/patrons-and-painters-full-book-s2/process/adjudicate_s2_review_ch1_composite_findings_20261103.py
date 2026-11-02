#!/usr/bin/env python3
"""Apply the reviewed Chapter 1 composite-finding split as one S2 stage."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
EVENTS_PATH = PROCESS / "s2-history-9622-review-events.csv"
SOURCE_FILE = "02-sources/02-Markdown/01_CHP-1.md"
SOURCE_SHA256 = "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb"
SECTION_FILE = "02-sources/02-Markdown/01_CHP-1_sec_ii.md"
SECTION_SHA256 = "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268"
PDF_FILE = "02-sources/01-book/CHP-1.pdf"
PDF_SHA256 = "0b9a3ca88e6f09209bd20185948e18a68f527d0628e893940a7e3f07f6d22c86"
BASE_HEAD = "0bedbd2229e24378d63a99216e9a21a632e21d0a"
STAGE_ID = "2026-11-03-s2-current-review-ch1-composite-findings"
STAGE_MARKER = f"stages.md#{STAGE_ID}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
    return sha256(data)


def read_jsonl(path: Path) -> tuple[list[dict], list[str], bytes]:
    raw = path.read_bytes()
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    rows = [json.loads(line) for line in lines if line.strip()]
    return rows, lines, raw


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fields = list(reader.fieldnames or [])
    rows = list(reader)
    terminator = "\r\n" if "\r\n" in text else "\n"
    return rows, fields, raw, terminator


def csv_bytes(rows: list[dict[str, str]], fields: list[str], terminator: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=terminator,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8")


def git_mentions(revision: str, segment_id: str) -> dict[str, dict[str, str]]:
    raw = subprocess.check_output(
        ["git", "show", f"{revision}:04-knowledge/tables/mentions.csv"], cwd=ROOT
    ).decode("utf-8-sig")
    return {
        row["mention_id"]: row
        for row in csv.DictReader(io.StringIO(raw, newline=""))
        if row["segment_id"] == segment_id
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the prepared stage")
    args = parser.parse_args()

    require(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT)
            .decode().strip() == BASE_HEAD, "Unexpected base HEAD")
    require(sha256((ROOT / SOURCE_FILE).read_bytes()) == SOURCE_SHA256,
            "Chapter 1 OCR source changed")
    require(sha256((ROOT / SECTION_FILE).read_bytes()) == SECTION_SHA256,
            "Chapter 1 section transcription changed")
    require(sha256((ROOT / PDF_FILE).read_bytes()) == PDF_SHA256,
            "Chapter 1 authority PDF changed")

    statements_path = TABLES / "book-statements.jsonl"
    mentions_path = TABLES / "mentions.csv"
    alignment_path = TABLES / "alignment.csv"
    candidate_path = TABLES / "entity-candidates.csv"
    manifest_path = TABLES / "ku-manifest.csv"
    enrichment_path = TABLES / "enrichment.jsonl"
    relations_path = TABLES / "relations.csv"

    statements, statement_lines, statement_raw = read_jsonl(statements_path)
    segments, _, _ = read_jsonl(TABLES / "segments.jsonl")
    mentions, mention_fields, mentions_raw, mentions_eol = read_csv(mentions_path)
    alignments, alignment_fields, alignment_raw, alignment_eol = read_csv(alignment_path)
    candidates, candidate_fields, candidate_raw, candidate_eol = read_csv(candidate_path)
    manifest, manifest_fields, manifest_raw, manifest_eol = read_csv(manifest_path)
    enrichment, enrichment_lines, enrichment_raw = read_jsonl(enrichment_path)
    relations, relation_fields, relations_raw, relations_eol = read_csv(relations_path)
    roster, roster_fields, roster_raw, roster_eol = read_csv(ROSTER_PATH)
    events, _, events_raw, _ = read_csv(EVENTS_PATH)

    statement_by_id = {row["statement_id"]: row for row in statements}
    segment_by_id = {row["segment_id"]: row for row in segments}
    mention_ids = {row["mention_id"] for row in mentions}
    roster_by_id = {row["statement_id"]: row for row in roster}
    require(len(statement_by_id) == len(statements), "Duplicate statement IDs")
    require(len(mention_ids) == len(mentions), "Duplicate mention IDs")
    require(len(roster_by_id) == len(roster), "Duplicate roster statement IDs")
    require(len(statements) == 15505 and len(mentions) == 27328,
            "Unexpected current S2 table baseline")
    require(sum(r["current_review_status"] == "reviewed_current_pass" for r in roster) == 8660,
            "Unexpected current PASS baseline")
    require(sum(r["current_review_status"] == "reviewed_current_pending" for r in roster) == 6845,
            "Unexpected current pending baseline")
    require(all(r["current_order"] == str(i) for i, r in enumerate(roster, 1)),
            "Current roster order is not contiguous before stage")

    old_ids = [
        "st-chp1-secii-l28-38-04",
        "st-chp1-secii-l62-71-09",
        "st-chp1-secii-l86-94-06",
        "st-chp1-secii-l118-127-05",
    ]
    new_ids = [
        "st-chp1-secii-l28-38-04a",
        "st-chp1-secii-l28-38-04b",
        "st-chp1-secii-l62-71-09b",
        "st-chp1-secii-l86-94-06b",
        "st-chp1-secii-l118-127-05b",
    ]
    require(all(sid in statement_by_id for sid in old_ids), "A target statement is missing")
    require(not set(new_ids) & statement_by_id.keys(), "A new statement ID already exists")
    require(all(sid in roster_by_id for sid in old_ids), "A target roster row is missing")
    require(not set(new_ids) & roster_by_id.keys(), "A new roster ID already exists")
    require(all(roster_by_id[sid]["current_review_status"] == "reviewed_current_pending"
                for sid in old_ids), "A target finding is no longer pending")
    require(all(roster_by_id[sid]["history_9622_event_count"] == "1"
                for sid in old_ids), "Target historical event mapping changed")
    require(not any(STAGE_MARKER in r.get("review_evidence_ref", "") for r in roster),
            "This stage has already been applied")

    # Exact quotes come from the full-chapter OCR named by each statement locator.
    source_lines = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").splitlines()
    section_lines = (ROOT / SECTION_FILE).read_text(encoding="utf-8-sig").splitlines()
    def quote(first: int, last: int) -> str:
        return "\n".join(source_lines[first - 1:last])

    quote_commission = quote(312, 313)
    quote_request = quote(313, 315)
    quote_iconography = quote(315, 319)
    quote_market = quote(607, 609)
    for expected in [
        "commissioned Pier Francesco Mola", "asked to borrow",
        "Basing himself", "on these books", "art dealing and art exhibitions",
        "financial benefits that accrued from Urban VIII",
        "Academicians showed an unresting", "concern for their own social status",
    ]:
        require(expected in "\n".join(source_lines), f"Expected source wording missing: {expected}")

    segment_text: dict[str, str] = {}
    for segment_id in {
        "chp-1:01_CHP-1_sec_ii:l28-38",
        "chp-1:01_CHP-1_sec_ii:l86-94",
    }:
        seg = segment_by_id[segment_id]
        segment_text[segment_id] = "\n".join(
            section_lines[int(seg["line_start"]) - 1:int(seg["line_end"])]
        )

    new_mentions = [
        {
            "mention_id": "m-chp1-secii-20261103-genealogy-gods",
            "segment_id": "chp-1:01_CHP-1_sec_ii:l28-38",
            "candidate_id": "cand-2956",
            "surface_form": "a genealogy of the gods",
            "start_char": "2262", "end_char": "2285",
            "note": "Book referent Mola asked to borrow; the source does not state that the loan was completed.",
        },
        {
            "mention_id": "m-chp1-secii-20261103-annotated-virgil",
            "segment_id": "chp-1:01_CHP-1_sec_ii:l28-38",
            "candidate_id": "cand-2957",
            "surface_form": "a Virgil with a commentary",
            "start_char": "2290", "end_char": "2316",
            "note": "Book referent Mola asked to borrow; Virgil author mention remains separately nested in the span; edition unidentified and loan completion unconfirmed.",
        },
        {
            "mention_id": "m-chp1-secii-20261103-roman-social-political-pattern",
            "segment_id": "chp-1:01_CHP-1_sec_ii:l86-94",
            "candidate_id": "cand-11855",
            "surface_form": "the shifting social and political pattern of Roman life in the seventeenth century",
            "start_char": "2772", "end_char": "2854",
            "note": "Exact referent of Haskell's causal interpretation; keep the source-derived term candidate unresolved at S3.",
        },
    ]
    for row in new_mentions:
        require(row["mention_id"] not in mention_ids, f"Mention ID already exists: {row['mention_id']}")
        text = segment_text[row["segment_id"]]
        require(text[int(row["start_char"]):int(row["end_char"])] == row["surface_form"],
                f"Mention span mismatch: {row['mention_id']}")

    # Narrow the four existing rows; retain their IDs and their historical outcomes.
    edits = {
        old_ids[0]: {
            "subject_candidate_id": "cand-1814",
            "object_candidate_id": "cand-1677",
            "predicate": "pamfili_commissioned_four_elements",
            "qualifiers": {
                "source_line_start": 312, "source_line_end": 313,
                "claim": "Haskell says Prince Camillo Pamfili commissioned Pier Francesco Mola to paint the Four Elements at the country house in Valmontone.",
                "speaker": "Haskell", "text_layer": "authorial claim",
                "qualification": "This statement records the commission only; completion of the decorative programme is not established here.",
                "relation_candidate": True,
                "relation_candidate_note": "The source supports existing formal S6 rel-0807 (created_by) and rel-0808 (commissioned_by); rel-0034 patron_of is a separate supported relation. Do not add duplicate edges.",
                "mentioned_candidate_ids": ["cand-1814", "cand-1676", "cand-1677", "cand-3431"],
            },
            "original_quote": quote_commission,
        },
        old_ids[1]: {
            "subject_candidate_id": "cand-3456", "object_candidate_id": "cand-11836",
            "predicate": "pamfili_family_responsible_for_sagnes_cupola_commission",
            "qualifiers": {
                "source_line_start": 441, "source_line_end": 441,
                "claim": "Haskell identifies the Pamfili family as responsible for the S. Agnese cupola commission.",
                "speaker": "Haskell", "text_layer": "authorial claim",
                "qualification": "The family is named collectively; its type and identity boundary remain unresolved. This does not assert that the family was unhappy with this specific commission.",
                "relation_candidate": True,
                "relation_candidate_note": "The S. Agnese work endpoint is aligned to the existing cupola fresco; the Pamfili family endpoint remains S3 undecided and untyped, so no formal family-to-work edge is created.",
                "mentioned_candidate_ids": ["cand-3456", "cand-11836"],
            },
            "original_quote": "the Pamfili family, who were responsible for this commission",
        },
        old_ids[2]: {
            "subject_candidate_id": "cand-11855", "object_candidate_id": "cand-3573",
            "predicate": "social_change_and_art_dealing_importance",
            "qualifiers": {
                "source_line_start": 607, "source_line_end": 609,
                "print_page": 15, "pdf_physical_page": 14,
                "claim": "Haskell attributes the growing importance of art dealing to changes in Roman social and political life in the seventeenth century.",
                "speaker": "Haskell", "text_layer": "authorial claim",
                "qualification": "This is Haskell's causal interpretation. Footnote 3 is a forward reference to chapter 5, not evidence used here. Art dealing and exhibitions are distinct activities.",
                "relation_candidate": True,
                "relation_candidate_note": "Source-level causal interpretation only; it creates no controlled S6 edge. The identity boundary of the art-dealing term remains open at S3.",
                "mentioned_candidate_ids": ["cand-11855", "cand-3126", "cand-3573"],
                "footnote_marker": 3,
                "footnote_refs": [{"marker": 3, "segment_id": "chp-1:01_CHP-1_sec_ii:l168-239", "source_line": 615}],
                "footnote_segment": "chp-1:01_CHP-1_sec_ii:l168-239",
                "linked_note_statement_ids": ["st-chp1-secii-l615-n3-forward-reference-ch5"],
                "footnote_link_status": "linked_forward_reference",
                "linked_statement_ids": [new_ids[3]],
            },
            "original_quote": quote_market,
        },
        old_ids[3]: {
            "subject_candidate_id": None, "object_candidate_id": "cand-3582",
            "predicate": "urban_viii_brief_financial_benefits",
            "qualifiers": {
                "source_line_start": 720, "source_line_end": 720,
                "printed_page": 18, "pdf_physical_page": 17,
                "claim": "Haskell states that financial benefits accrued from an unidentified brief issued by Urban VIII.",
                "speaker": "Haskell", "text_layer": "authorial historical account",
                "qualification": "The brief, beneficiary wording, and precise legal scope are not supplied by this sentence; do not infer a formal relation to the Accademia.",
                "relation_candidate": True,
                "relation_candidate_note": "The source-derived brief candidate remains identity-undecided; no beneficiary endpoint or formal S6 relation is established.",
                "mentioned_candidate_ids": ["cand-3582"],
                "linked_statement_ids": ["st-chp1-secii-l118-127-04b", new_ids[4]],
            },
            "original_quote": quote(720, 720),
        },
    }
    changed_statements: set[str] = set()
    for sid, values in edits.items():
        row = statement_by_id[sid]
        before = canonical_hash(row)
        row.update({k: v for k, v in values.items() if k != "qualifiers"})
        row["qualifiers"] = values["qualifiers"]
        if canonical_hash(row) != before:
            changed_statements.add(sid)
    require(changed_statements == set(old_ids), "Unexpected changed statement set")

    new_statements = [
        {
            "statement_id": new_ids[0],
            "segment_id": "chp-1:01_CHP-1_sec_ii:l28-38",
            "subject_candidate_id": "cand-1676", "object_candidate_id": None,
            "predicate": "mola_asked_to_borrow_reference_books",
            "qualifiers": {
                "source_line_start": 313, "source_line_end": 315,
                "claim": "Haskell reports that Mola asked a respected local lawyer to lend him a genealogy of the gods and an annotated Virgil text so he could choose suitable myths.",
                "speaker": "Haskell", "text_layer": "authorial claim",
                "qualification": "This records a request, not confirmed completion of the loan. The lawyer is unnamed; both book referents remain unidentified or unversioned.",
                "relation_candidate": True,
                "relation_candidate_note": "Keep rel-1129 and rel-1130 pending: the source says asked to borrow, not that either requested book was lent.",
                "mentioned_candidate_ids": ["cand-1676", "cand-2956", "cand-2957", "cand-2777"],
                "open_endpoint_reason": "The request concerns two books and an unnamed lawyer; it does not define a single formal relation endpoint or prove a completed loan.",
                "linked_statement_ids": [new_ids[1]],
            },
            "original_quote": quote_request,
            "origin": "book", "source_file": SOURCE_FILE,
        },
        {
            "statement_id": new_ids[1],
            "segment_id": "chp-1:01_CHP-1_sec_ii:l28-38",
            "subject_candidate_id": "cand-1676", "object_candidate_id": "cand-1677",
            "predicate": "mola_four_elements_iconography",
            "qualifiers": {
                "source_line_start": 315, "source_line_end": 319,
                "claim": "Haskell says Mola drew on the books and friendly conversations when he chose the mythological subjects for Air.",
                "speaker": "Haskell", "text_layer": "authorial claim",
                "qualification": "The source reports choices, not verified completion. It attributes the choices jointly to the books and conversations, so no individual motif is assigned to a particular volume. The section transcription reads 'his to Turnus'; full-chapter OCR and the printed page read 'Iris to Turnus'.",
                "relation_candidate": True,
                "relation_candidate_note": "Existing formal work and commission edges rel-0805, rel-0807, and rel-0808 remain unchanged; this split adds no S6 edge.",
                "mentioned_candidate_ids": ["cand-1676", "cand-1677", "cand-2956", "cand-2957", "cand-3432", "cand-3433", "cand-3434", "cand-3435", "cand-3436", "cand-3440", "cand-3437"],
                "footnote_marker": 4, "footnote_number": 4,
                "footnote_segment": "chp-1:01_CHP-1_sec_ii:l168-239",
                "footnote_refs": [{"marker": 4, "segment_id": "chp-1:01_CHP-1_sec_ii:l168-239", "source_line": 329}],
                "footnote_link_status": "linked", "footnote_text_pending": False,
                "footnote_statement_ids": [
                    "st-chp1-secii-p9-n4-cites-montalto-p290",
                    "st-chp1-secii-p9-n4-cites-armanni-letter-vol1-p215",
                    "st-chp1-secii-p9-n4-armanni-letter-authored-by",
                    "st-chp1-secii-p9-n4-armanni-letter-addressed-to",
                    "st-chp1-secii-p9-n4-armanni-letter-concerns-valmontone-palace",
                ],
                "linked_statement_ids": [new_ids[0]],
            },
            "original_quote": quote_iconography,
            "origin": "book", "source_file": SOURCE_FILE,
        },
        {
            "statement_id": new_ids[2],
            "segment_id": "chp-1:01_CHP-1_sec_ii:l62-71",
            "subject_candidate_id": "cand-3456", "object_candidate_id": None,
            "predicate": "pamfili_family_relations_with_artists_general_characterization",
            "qualifiers": {
                "source_line_start": 441, "source_line_end": 442,
                "claim": "Haskell characterizes the Pamfili family's relations with artists generally as never altogether happy.",
                "speaker": "Haskell", "text_layer": "authorial characterization",
                "qualification": "This is a general statement, not a claim that the S. Agnese cupola commission involved a specific dispute. The artist group and family type remain unresolved.",
                "relation_candidate": True,
                "relation_candidate_note": "The broad, unnamed artist group has no resolved endpoint; retain as a source-level relation candidate without a formal S6 edge.",
                "mentioned_candidate_ids": ["cand-3456"],
                "open_endpoint_reason": "The sentence refers to artists collectively without identifying a bounded group or individual.",
                "linked_statement_ids": [old_ids[1]],
            },
            "original_quote": "the Pamfili family, who were responsible for this commission, were never\naltogether happy in their relations with artists.",
            "origin": "book", "source_file": SOURCE_FILE,
        },
        {
            "statement_id": new_ids[3],
            "segment_id": "chp-1:01_CHP-1_sec_ii:l86-94",
            "subject_candidate_id": "cand-11855", "object_candidate_id": "cand-3574",
            "predicate": "social_change_and_art_exhibition_importance",
            "qualifiers": {
                "source_line_start": 607, "source_line_end": 609,
                "print_page": 15, "pdf_physical_page": 14,
                "claim": "Haskell attributes the growing importance of art exhibitions to changes in Roman social and political life in the seventeenth century.",
                "speaker": "Haskell", "text_layer": "authorial claim",
                "qualification": "This is Haskell's causal interpretation. Footnote 3 is a forward reference to chapter 5, not evidence used here. Art exhibitions remain distinct from art dealing.",
                "relation_candidate": True,
                "relation_candidate_note": "Source-level causal interpretation only; it creates no controlled S6 edge. The art-exhibitions identity is same to the existing generic term KU.",
                "mentioned_candidate_ids": ["cand-11855", "cand-3126", "cand-3574"],
                "footnote_marker": 3,
                "footnote_refs": [{"marker": 3, "segment_id": "chp-1:01_CHP-1_sec_ii:l168-239", "source_line": 615}],
                "footnote_segment": "chp-1:01_CHP-1_sec_ii:l168-239",
                "linked_note_statement_ids": ["st-chp1-secii-l615-n3-forward-reference-ch5"],
                "footnote_link_status": "linked_forward_reference",
                "linked_statement_ids": [old_ids[2]],
            },
            "original_quote": quote_market,
            "origin": "book", "source_file": SOURCE_FILE,
        },
        {
            "statement_id": new_ids[4],
            "segment_id": "chp-1:01_CHP-1_sec_ii:l118-127",
            "subject_candidate_id": None, "object_candidate_id": None,
            "predicate": "academicians_complaints_show_social_status_concern",
            "qualifiers": {
                "source_line_start": 721, "source_line_end": 722,
                "printed_page": 18, "pdf_physical_page": 17,
                "claim": "Haskell says the Academicians' complaints showed their persistent concern for their own social status.",
                "speaker": "Haskell", "text_layer": "authorial interpretation",
                "qualification": "This is Haskell's reading of the Academicians' complaints; the members are not conflated with the Accademia institution, and no specific artist or recipient is identified.",
                "relation_candidate": False,
                "relation_candidate_note": "No specific person or institutional relation is asserted; do not create an S6 edge.",
                "open_endpoint_reason": "The source names Academicians collectively but does not define a member-group endpoint distinct from the Accademia institution.",
                "linked_statement_ids": [old_ids[3]],
            },
            "original_quote": "one of their aims, for in all their complaints the Academicians showed an unresting\nconcern for their own social status.",
            "origin": "book", "source_file": SOURCE_FILE,
        },
    ]

    statement_changes_by_parent: dict[str, list[dict]] = {
        old_ids[0]: new_statements[:2],
        old_ids[1]: [new_statements[2]],
        old_ids[2]: [new_statements[3]],
        old_ids[3]: [new_statements[4]],
    }
    for row in new_statements:
        require(row["statement_id"] not in statement_by_id, "New statement ID collision")
        require(row["segment_id"] in segment_by_id, "New statement source segment is missing")
        statement_by_id[row["statement_id"]] = row
    for sid, row in edits.items():
        require(row["original_quote"] in "\n".join(source_lines),
                f"Edited quote is not in the source: {sid}")
    for row in new_statements:
        require(row["original_quote"] in "\n".join(source_lines),
                f"New quote is not in the source: {row['statement_id']}")

    # Update affected S3 evidence notes, without changing identity decisions.
    alignment_by_id = {row["alignment_id"]: row for row in alignments}
    expected_alignment = {
        "aln-0026": ("cand-2956", "same", "units/archives/mola-borrowed-genealogy-gods"),
        "aln-0027": ("cand-2957", "same", "units/archives/mola-borrowed-virgil-commentary"),
        "aln-2012": ("cand-1677", "undecided", ""),
        "aln-3641": ("cand-3456", "undecided", ""),
        "aln-3757": ("cand-3573", "undecided", ""),
        "aln-3758": ("cand-3574", "same", "units/terms/art-exhibitions"),
        "aln-3766": ("cand-3582", "undecided", ""),
        "aln-11999": ("cand-11836", "same", "units/works/ferri-sant-agnese-cupola"),
        "aln-12018": ("cand-11855", "undecided", ""),
    }
    additions = {
        "aln-0026": "S2 current statement st-chp1-secii-l28-38-04a and exact mention m-chp1-secii-20261103-genealogy-gods@chp-1:01_CHP-1_sec_ii:l28-38[chars=2262-2285] show that Mola asked to borrow this source-defined book referent. Same identity mapping is unchanged; the completed-loan relation rel-1129 remains pending.",
        "aln-0027": "S2 current statement st-chp1-secii-l28-38-04a and exact mention m-chp1-secii-20261103-annotated-virgil@chp-1:01_CHP-1_sec_ii:l28-38[chars=2290-2316] show that Mola asked to borrow this source-defined text. Same identity mapping is unchanged; the completed-loan relation rel-1130 remains pending.",
        "aln-2012": "Current S2 statement st-chp1-secii-l28-38-04 and mention m-chp1-secii-0042 anchor the indexed Four Elements referent; retain undecided pending identity/type adjudication and do not register a KU.",
        "aln-3641": "Current S2 statement st-chp1-secii-l62-71-09 now isolates responsibility for the S. Agnese commission; st-chp1-secii-l62-71-09b separately records the general family-artist characterization. Keep the family candidate untyped and undecided; no family relation is formal.",
        "aln-3757": "Current S2 statement st-chp1-secii-l86-94-06 isolates art dealing and new statement st-chp1-secii-l86-94-06b isolates exhibitions. The identity boundary of the art-dealing term remains unresolved; no KU or relation is forced.",
        "aln-3758": "Current S2 statement st-chp1-secii-l86-94-06b and existing exact mention m-chp1-secii-0612 anchor generic art-exhibition practice. Existing same mapping is unchanged; individual events and venues remain distinct.",
        "aln-3766": "Current S2 statement st-chp1-secii-l118-127-05 isolates the financial-benefit attribution to the brief. Keep the brief identity, beneficiary wording, and legal scope unresolved; no formal relation is added.",
        "aln-11999": "Current S2 statement st-chp1-secii-l62-71-09 now states only the Pamfili family's responsibility for this commission; its work identity remains same to units/works/ferri-sant-agnese-cupola. Family candidate cand-3456 remains untyped/undecided and no family-to-work relation is formal.",
        "aln-12018": "A new exact S2 body mention m-chp1-secii-20261103-roman-social-political-pattern@chp-1:01_CHP-1_sec_ii:l86-94[chars=2772-2854] anchors the source-defined term in statement st-chp1-secii-l86-94-06. Retain undecided because the candidate's identity boundary and taxonomy match remain unresolved.",
    }
    for aid, expected in expected_alignment.items():
        row = alignment_by_id.get(aid)
        require(row is not None, f"Missing alignment {aid}")
        require((row["candidate_id"], row["decision"], row["ku_id"]) == expected,
                f"Alignment decision or mapping changed: {aid}")
        require(STAGE_ID not in row["resolution_note"], f"Alignment already updated: {aid}")
        if aid == "aln-11999":
            row["resolution_note"] = row["resolution_note"].replace(
                "The compound S2 statement remains pending.",
                "The prior compound S2 finding is resolved by split statements st-chp1-secii-l62-71-09 and st-chp1-secii-l62-71-09b; only the family endpoint and any family relation remain unresolved.",
            )
        if aid == "aln-2012":
            row["resolution_note"] = row["resolution_note"].replace(
                "候选来源不是可核的 S2 body-mention，且无现成对齐；保留待证，不凭索引/类型字段推新。",
                "已有精确 S2 source mention，但候选身份和类型仍须语义复核；保持 undecided，不凭索引/类型字段推新。",
            )
        if aid == "aln-12018":
            row["resolution_note"] = row["resolution_note"].replace(
                "Index locator only; no linked S2 mention establishes the referent sufficiently for same/new. Retain for source-level identity review.",
                "Current source-level S2 evidence is now linked; identity review remains open.",
            )
        row["resolution_note"] += f" | {STAGE_ID}: {additions[aid]}"

    # Keep archive identity/KU mappings, but reclassify unsupported completed loans.
    relation_by_id = {row["relation_id"]: row for row in relations}
    for rid, scope, note in [
        ("rel-1129", "Requested loan of the unidentified genealogy of the gods; whether it was lent is unstated.",
         "Haskell says Mola asked a local lawyer to lend him a genealogy of the gods and later says he based his choices on the books. The passage does not explicitly state that this requested loan was completed; retain borrowed_by as pending."),
        ("rel-1130", "Requested loan of an annotated Virgil text; work and edition are unidentified, and completion is unstated.",
         "Haskell says Mola asked a local lawyer to lend him an annotated Virgil text and later says he based his choices on the books. The passage does not explicitly state that this requested loan was completed; retain borrowed_by as pending."),
    ]:
        row = relation_by_id.get(rid)
        require(row is not None and row["status"] == "formal" and row["predicate"] == "borrowed_by",
                f"Unexpected current state for {rid}")
        row["status"] = "pending"
        row["role"] = "请求借阅者；出借完成未明"
        row["scope"] = scope
        row["note"] = note

    # Reflect the evidence boundary in current archive titles and structured S5 facts.
    title_updates = {
        "units/archives/mola-borrowed-genealogy-gods": {
            "zh": "莫拉请求借阅的神谱书（题名未明）",
            "en": "Genealogy of the Gods Mola Asked to Borrow (title unidentified)",
            "old_en": "Genealogy of the Gods Borrowed by Mola (title unidentified)",
        },
        "units/archives/mola-borrowed-virgil-commentary": {
            "zh": "莫拉请求借阅的维吉尔注释本（版本未明）",
            "en": "Annotated Virgil Mola Asked to Borrow (edition unidentified)",
            "old_en": "Annotated Virgil Borrowed by Mola (edition unidentified)",
        },
    }
    for ku_id, values in title_updates.items():
        cand_id = "cand-2956" if "genealogy" in ku_id else "cand-2957"
        candidate = next((r for r in candidates if r["candidate_id"] == cand_id), None)
        manifest_row = next((r for r in manifest if r["ku_id"] == ku_id), None)
        require(candidate is not None and manifest_row is not None, f"Missing current archive mapping: {ku_id}")
        require(candidate["candidate_source_ref"] == f"04-knowledge/units/archives/{Path(ku_id).name}.md",
                f"Candidate card path changed: {cand_id}")
        candidate["canonical_name"] = values["zh"]
        manifest_row["canonical_name"] = values["zh"]
        manifest_row["name_en"] = values["en"]

    enrichment_by_id = {row["enrichment_id"]: row for row in enrichment}
    enrichment_updates = {
        "enr-08808": ("Genealogy of the Gods Mola Asked to Borrow (title unidentified)", ["名称／对应英文", "Genealogy of the Gods Mola Asked to Borrow (title unidentified)", "S1"]),
        "enr-13847": ("请求借阅者｜Pier Francesco Mola｜S1", ["请求借阅者", "Pier Francesco Mola", "S1"]),
        "enr-13848": ("受请求的借阅对象｜Valmontone当地一位有一定地位的律师；姓名未给｜S1", ["受请求的借阅对象", "Valmontone当地一位有一定地位的律师；姓名未给", "S1"]),
        "enr-08817": ("Annotated Virgil Mola Asked to Borrow (edition unidentified)", ["名称／对应英文", "Annotated Virgil Mola Asked to Borrow (edition unidentified)", "S1"]),
        "enr-13855": ("请求借阅者｜Pier Francesco Mola｜S1", ["请求借阅者", "Pier Francesco Mola", "S1"]),
        "enr-13856": ("受请求的借阅对象｜Valmontone当地律师；姓名未给｜S1", ["受请求的借阅对象", "Valmontone当地律师；姓名未给", "S1"]),
    }
    for eid, (value, cells) in enrichment_updates.items():
        row = enrichment_by_id.get(eid)
        require(row is not None, f"Missing enrichment {eid}")
        row["value"] = value
        if cells is not None:
            row["cells"] = cells

    archive_card_updates: dict[Path, bytes] = {}
    card_specs = [
        (
            "04-knowledge/units/archives/mola-borrowed-genealogy-gods.md",
            "莫拉借阅的神谱书（题名未明）", "莫拉请求借阅的神谱书（题名未明）",
            "Genealogy of the Gods Borrowed by Mola (title unidentified)",
            "Genealogy of the Gods Mola Asked to Borrow (title unidentified)",
            "Mola 为选择图像内容借阅这部未具题名的神谱。",
            "Mola 请求当地律师借给他这部未具题名的神谱；原文未明言出借完成。",
            "为选择图像内容借阅的未具题名神谱",
            "为选择图像内容请求借阅的未具题名神谱；出借完成未明",
            "borrowed", "asked to borrow",
        ),
        (
            "04-knowledge/units/archives/mola-borrowed-virgil-commentary.md",
            "莫拉借阅的维吉尔注释本（版本未明）", "莫拉请求借阅的维吉尔注释本（版本未明）",
            "Annotated Virgil Borrowed by Mola (edition unidentified)",
            "Annotated Virgil Mola Asked to Borrow (edition unidentified)",
            "Mola 借阅的带注释 Virgil 文本，不指定某部作品或版本。",
            "Mola 请求当地律师借給他一部带注释的 Virgil 文本；原文未明言出借完成。",
            "带注释的Virgil文本；作品及版本未定",
            "请求借阅的带注释Virgil文本；作品及版本未定，出借完成未明",
            "borrowed", "asked to borrow",
        ),
    ]
    for spec in card_specs:
        path, old_zh, new_zh, old_en, new_en, old_note, new_note, old_scope, new_scope, old_word, new_word = spec
        card_path = ROOT / path
        original = card_path.read_bytes()
        text = original.decode("utf-8-sig")
        for old, new in [
            (old_zh, new_zh), (old_en, new_en),
            (f"name_en: \"{old_en}\"", f"name_en: \"{new_en}\""),
            (old_note, new_note), (old_scope, new_scope),
            ("updated: 2026-09-14", "updated: 2026-11-03"),
            ('"review_status":"evidence_backed_relation"', '"review_status":"needs_evidence"'),
            (f'"role":"借阅者"', '"role":"请求借阅者；出借完成未明"'),
        ]:
            if old in text:
                text = text.replace(old, new)
        if old_word == "borrowed":
            replacements = [
                (
                    "Haskell records Mola borrowing a genealogy of the gods from a local lawyer to choose imagery for Valmontone.",
                    "Haskell reports that Mola asked a local lawyer to lend him a genealogy of the gods for choosing Valmontone imagery; the source does not explicitly state that the loan was completed.",
                ),
                (
                    "The chapter mentions only a Virgil with a commentary, used in choosing myths for the Four Elements decoration. No title, commentator or edition is supplied; it is not automatically identified as an edition of the Aeneid.",
                    "The chapter reports that Mola asked to borrow a Virgil with a commentary for choosing Four Elements myths. It does not state that the request was fulfilled; no title, commentator or edition is supplied, and the text is not automatically identified as an edition of the Aeneid.",
                ),
                (
                    "Mola 为选择图像内容借阅 a genealogy of the gods，",
                    "Mola 为选择图像内容请求借阅 a genealogy of the gods；原文未明言出借完成，",
                ),
                (
                    "Haskell 记 Mola 向当地律师借阅 a genealogy of the gods，用于选择 Valmontone 的图像内容。",
                    "Haskell 记载 Mola 向当地律师请求借阅 a genealogy of the gods，用于选择 Valmontone 的图像内容；原文未明言请求获准或完成出借。",
                ),
                (
                    "可保留该借阅语境中的文献指代",
                    "可保留该请求借阅语境中的文献指代",
                ),
                (
                    "本章只说 a Virgil with a commentary，用于选择四元素装饰神话；",
                    "本章记载 Mola 请求借阅 a Virgil with a commentary 以选择四元素装饰神话；原文未明言出借完成，",
                ),
                (
                    "The source records Mola borrowing a Virgil with a commentary for choosing myths; it does not supply a title, commentator, or edition.",
                    "The source records that Mola asked to borrow a Virgil with a commentary for choosing myths; it does not say the request was fulfilled or supply a title, commentator, or edition.",
                ),
            ]
            for old_phrase, new_phrase in replacements:
                text = text.replace(old_phrase, new_phrase)
        require(new_zh in text and new_en in text, f"Card title update did not apply: {path}")
        require('"review_status":"needs_evidence"' in text,
                f"Migration relation was not marked pending: {path}")
        if original.startswith(b"\xef\xbb\xbf"):
            archive_card_updates[card_path] = b"\xef\xbb\xbf" + text.encode("utf-8")
        else:
            archive_card_updates[card_path] = text.encode("utf-8")

    # Append three exact mentions; the two split claims use the existing book candidates.
    mentions_after = mentions + new_mentions
    require(len({row["mention_id"] for row in mentions_after}) == len(mentions_after),
            "Mention IDs are not unique after stage")
    mention_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in mentions_after:
        mention_by_segment[row["segment_id"]].append(row)

    # New rows enter the source-ordered current-version roster beside their parent.
    roster_insertions = {
        old_ids[0]: new_statements[:2],
        old_ids[1]: [new_statements[2]],
        old_ids[2]: [new_statements[3]],
        old_ids[3]: [new_statements[4]],
    }
    evidence_ref = f"stages.md#{STAGE_ID}"
    outcomes = {
        old_ids[0]: "Split commission, request to borrow, and iconographic choice. The first claim is supported; both completed-loan relations remain pending; preserve the section-text 'his' versus printed-page/OCR 'Iris' variant.",
        old_ids[1]: "Split the family’s responsibility for the S. Agnese commission from Haskell’s general characterization of family relations with artists. The family remains untyped at S3; no family relation is formal.",
        old_ids[2]: "Split art dealing and art exhibitions as two activities attributed to the Roman social and political pattern; keep their term candidates distinct and preserve footnote 3 as a forward reference.",
        old_ids[3]: "Split the unidentified Urban VIII brief’s financial benefits from Haskell’s interpretation of the Academicians’ complaints; keep beneficiary/scope and member-group endpoint unresolved.",
    }
    for sid, outcome in outcomes.items():
        row = roster_by_id[sid]
        row["current_review_status"] = "reviewed_current_pass"
        row["review_batch_id"] = "S2-B427-CH1-COMPOSITE-FINDINGS"
        row["review_outcome"] = "current_pending_finding_resolved_after_original_page_review"
        row["review_evidence_ref"] = evidence_ref
        prior = row.get("follow_up_note", "")
        row["follow_up_note"] = f"{outcome} Previous evidence: {prior}"

    for parent_id, additions_for_parent in roster_insertions.items():
        parent = roster_by_id[parent_id]
        for statement in additions_for_parent:
            seg = segment_by_id[statement["segment_id"]]
            row = dict(parent)
            row.update({
                "current_order": "",
                "statement_id": statement["statement_id"],
                "snapshot_statement_sha256": "",
                "current_statement_sha256": canonical_hash(statement),
                "history_9622_membership": "not_in_reconstructed_count",
                "prior_review_match": "no_exact_review_mapping",
                "prior_review_ref": "",
                "current_review_status": "reviewed_current_pass",
                "review_batch_id": "S2-B427-CH1-COMPOSITE-FINDINGS",
                "review_outcome": "current_statement_semantic_pass_source_claim_and_printed_page_verified",
                "review_evidence_ref": evidence_ref,
                "follow_up_note": outcomes[parent_id],
                "history_9622_event_count": "0",
                "history_9622_latest_review_commit": "",
                "history_9622_latest_statement_sha256": "",
                "history_9622_current_statement_match": "",
                "history_9622_source_match": "",
                "history_9622_mention_delta": "",
                "history_9622_evidence_ref": "",
                "segment_sha256": seg["sha256"],
                "source_asset_sha256": seg.get("asset_sha256", ""),
            })
            require(statement["statement_id"] not in roster_by_id,
                    f"New roster ID collision: {statement['statement_id']}")
            roster_by_id[statement["statement_id"]] = row

    roster_after: list[dict[str, str]] = []
    for row in roster:
        roster_after.append(row)
        for statement in roster_insertions.get(row["statement_id"], []):
            roster_after.append(roster_by_id[statement["statement_id"]])
    require(len(roster_after) == 15510, "Unexpected roster size after statement split")

    statement_hashes = {sid: canonical_hash(row) for sid, row in statement_by_id.items()}
    changed_segments = {
        "chp-1:01_CHP-1_sec_ii:l28-38",
        "chp-1:01_CHP-1_sec_ii:l86-94",
    }
    # Re-number only after source-adjacent insertions; original order remains stable.
    for index, row in enumerate(roster_after, 1):
        row["current_order"] = str(index)

    for row in roster_after:
        sid = row["statement_id"]
        statement = statement_by_id[sid]
        segment_id = statement["segment_id"]
        seg = segment_by_id[segment_id]
        current_segment_mentions = mention_by_segment.get(segment_id, [])
        if segment_id in changed_segments:
            row["current_segment_mention_count"] = str(len(current_segment_mentions))
            row["current_segment_mentions_sha256"] = canonical_hash(
                sorted(current_segment_mentions, key=lambda m: m["mention_id"])
            )
        if sid in changed_statements and row["history_9622_event_count"] != "0":
            row["current_statement_sha256"] = statement_hashes[sid]
            row["history_9622_current_statement_match"] = (
                "exact" if row["history_9622_latest_statement_sha256"] == statement_hashes[sid]
                else "changed"
            )
            row["prior_review_match"] = (
                "exact_object_and_source_segment"
                if row["history_9622_current_statement_match"] == "exact"
                and row["history_9622_source_match"] == "true"
                else "historical_object_or_source_differs"
            )
        if int(row["history_9622_event_count"] or "0") > 0 and segment_id in changed_segments:
            revision = row["history_9622_latest_review_commit"]
            old_mentions = git_mentions(revision, segment_id)
            current_mentions = {m["mention_id"]: m for m in current_segment_mentions}
            changed = sorted(mid for mid in old_mentions.keys() & current_mentions.keys()
                             if old_mentions[mid] != current_mentions[mid])
            removed = sorted(old_mentions.keys() - current_mentions.keys())
            added = sorted(current_mentions.keys() - old_mentions.keys())
            row["history_9622_mention_delta"] = json.dumps(
                {"changed": changed, "removed": removed, "added": added},
                ensure_ascii=False, separators=(",", ":"),
            )

    # Preserve untouched JSONL lines byte-for-byte and insert reviewed statements at source position.
    newline = "\r\n" if any(line.endswith("\r\n") for line in statement_lines) else "\n"
    rewritten_statement_lines: list[str] = []
    inserted = set()
    for line in statement_lines:
        if not line.strip():
            rewritten_statement_lines.append(line)
            continue
        old = json.loads(line)
        sid = old["statement_id"]
        if sid in changed_statements:
            rewritten_statement_lines.append(json.dumps(statement_by_id[sid], ensure_ascii=False,
                                                        separators=(",", ":")) + newline)
        else:
            rewritten_statement_lines.append(line)
        for new_row in statement_changes_by_parent.get(sid, []):
            rewritten_statement_lines.append(json.dumps(new_row, ensure_ascii=False,
                                                        separators=(",", ":")) + newline)
            inserted.add(new_row["statement_id"])
    require(inserted == set(new_ids), "Not all new statements were inserted")
    statement_output = (b"\xef\xbb\xbf" if statement_raw.startswith(b"\xef\xbb\xbf") else b"") + "".join(rewritten_statement_lines).encode("utf-8")

    # Source-derived candidate names and archive-card metadata follow the corrected claim boundary.
    for row in candidates:
        if row["candidate_id"] == "cand-2956":
            row["canonical_name"] = title_updates["units/archives/mola-borrowed-genealogy-gods"]["zh"]
        elif row["candidate_id"] == "cand-2957":
            row["canonical_name"] = title_updates["units/archives/mola-borrowed-virgil-commentary"]["zh"]

    alignment_output = csv_bytes(alignments, alignment_fields, alignment_eol)
    mentions_output = csv_bytes(mentions_after, mention_fields, mentions_eol)
    relations_output = csv_bytes(relations, relation_fields, relations_eol)
    candidates_output = csv_bytes(candidates, candidate_fields, candidate_eol)
    manifest_output = csv_bytes(manifest, manifest_fields, manifest_eol)
    roster_output = csv_bytes(roster_after, roster_fields, roster_eol)
    updated_enrichment_ids = set(enrichment_updates)
    rewritten_enrichment_lines: list[str] = []
    for line in enrichment_lines:
        if not line.strip():
            rewritten_enrichment_lines.append(line)
            continue
        original_row = json.loads(line)
        eid = original_row.get("enrichment_id")
        if eid not in updated_enrichment_ids:
            rewritten_enrichment_lines.append(line)
            continue
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        rewritten_enrichment_lines.append(
            json.dumps(enrichment_by_id[eid], ensure_ascii=False) + ending
        )
    enrichment_output = (b"\xef\xbb\xbf" if enrichment_raw.startswith(b"\xef\xbb\xbf") else b"") + "".join(rewritten_enrichment_lines).encode("utf-8")

    planned: dict[Path, bytes] = {
        statements_path: statement_output,
        mentions_path: mentions_output,
        alignment_path: alignment_output,
        relations_path: relations_output,
        candidate_path: candidates_output,
        manifest_path: manifest_output,
        ROSTER_PATH: roster_output,
        enrichment_path: enrichment_output,
        **archive_card_updates,
    }
    before = {
        statements_path: statement_raw,
        mentions_path: mentions_raw,
        alignment_path: alignment_raw,
        relations_path: relations_raw,
        candidate_path: candidate_raw,
        manifest_path: manifest_raw,
        ROSTER_PATH: roster_raw,
        enrichment_path: enrichment_raw,
        **{path: path.read_bytes() for path in archive_card_updates},
    }

    # Invariants for the complete batch before any write.
    final_pass = sum(r["current_review_status"] == "reviewed_current_pass" for r in roster_after)
    final_pending = sum(r["current_review_status"] == "reviewed_current_pending" for r in roster_after)
    require((final_pass, final_pending) == (8669, 6841), "Unexpected final PASS/pending totals")
    require(len(mentions_after) == 27331, "Unexpected final mention total")
    require(sum(r["status"] == "formal" for r in relations) == 2585,
            "Unexpected formal relation total")
    require(sum(r["status"] == "pending" for r in relations) == 61,
            "Unexpected pending relation total")
    require(len(events) == 9622 and sha256(events_raw) == "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89",
            "Historical H9622 ledger changed")
    require(len({r["statement_id"] for r in statement_by_id.values()}) == 15510,
            "Final statement IDs are not unique")
    require(len({r["current_order"] for r in roster_after}) == 15510,
            "Final current_order values are not unique")

    print(json.dumps({
        "stage": STAGE_ID,
        "base_head": BASE_HEAD,
        "statements_before_after": [15505, 15510],
        "mentions_before_after": [27328, 27331],
        "old_pending_resolved": 4,
        "new_statements_pass": len(new_statements),
        "final_current_pass_pending": [final_pass, final_pending],
        "new_mentions": [r["mention_id"] for r in new_mentions],
        "changed_existing_statements": sorted(changed_statements),
        "relations_changed_to_pending": ["rel-1129", "rel-1130"],
        "alignment_decisions_changed": 0,
        "historical_events_changed": 0,
        "files_planned": len(planned),
        "apply": args.apply,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    written: list[Path] = []
    try:
        for path, content in planned.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".stage-tmp", dir=path.parent)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(tmp_name, path)
                written.append(path)
            except Exception:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
                raise
    except Exception:
        for path in reversed(written):
            path.write_bytes(before[path])
        raise

    require(EVENTS_PATH.read_bytes() == events_raw, "Historical event ledger was modified")
    print("applied_chapter1_composite_findings_as_single_stage")


if __name__ == "__main__":
    main()
