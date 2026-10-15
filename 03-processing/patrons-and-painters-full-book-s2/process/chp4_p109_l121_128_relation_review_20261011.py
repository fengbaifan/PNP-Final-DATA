#!/usr/bin/env python3
"""Classify p.109 S2 statements and repair portrait-collection mappings."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l121-128"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "0b07b284662fa705b1b4e46e7eb35db51c5d358d231c7fa4019efcc6572bca46"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "efe359665864acd01ee8a74e1a21c94c7eb0101ed8ece6bb71f23c2c1b335042",
    "mentions.csv": "d6361735cb65a9fc81c605ac9cfb9e122e38d8535a293d087bba0ab9562b1669",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l121-128-relations-20261011"
PORTRAIT_GROUP_ID = "cand-5831"

ORIGINAL_IDS = {
    "st-chp4-sec-ii-p109-antique-collection-imagery",
    "st-chp4-sec-ii-p109-cassiano-correspondence-expenses",
    "st-chp4-sec-ii-p109-cassiano-helped-gaudenzi",
    "st-chp4-sec-ii-p109-cassiano-interest-religions",
    "st-chp4-sec-ii-p109-cassiano-petau-preface-analogy",
    "st-chp4-sec-ii-p109-classical-devotion-not-neopaganism",
    "st-chp4-sec-ii-p109-dispassionate-inquiry-fragment",
    "st-chp4-sec-ii-p109-drawing-volume-deity-sacrifice",
    "st-chp4-sec-ii-p109-gaudenzi-background",
    "st-chp4-sec-ii-p109-gaudenzi-baronio-jesuits",
    "st-chp4-sec-ii-p109-gaudenzi-copy-after-saracini",
    "st-chp4-sec-ii-p109-gaudenzi-history-conclusions",
    "st-chp4-sec-ii-p109-gaudenzi-papal-patronage",
    "st-chp4-sec-ii-p109-gaudenzi-portrait-acknowledged",
    "st-chp4-sec-ii-p109-gaudenzi-portrait-request",
    "st-chp4-sec-ii-p109-interest-early-church-contemporary-life",
    "st-chp4-sec-ii-p109-petau-preface-argument",
    "st-chp4-sec-ii-p109-portrait-collection",
    "st-chp4-sec-ii-p109-sacrements-inference",
}
NEW_IDS = {
    "st-chp4-sec-ii-p109-gaudenzi-grison-origin",
    "st-chp4-sec-ii-p109-gaudenzi-enemy-of-jesuits",
}
MENTION_UPDATES = {
    "m-chp4-sec-ii-p109-portraits-naude": ("cand-5832", PORTRAIT_GROUP_ID),
    "m-chp4-sec-ii-p109-cassiano-collection-illustrious": ("cand-5832", PORTRAIT_GROUP_ID),
}

RELATION_NOTES = {
    "st-chp4-sec-ii-p109-cassiano-correspondence-expenses":
        "Cassiano's reported letter is addressed to Gaudenzi; the financial context and promise are preserved as one communication, with no unlisted gentlemen identified.",
    "st-chp4-sec-ii-p109-cassiano-helped-gaudenzi":
        "Haskell explicitly says Cassiano had done most to help Gaudenzi through his troubles; the kind and extent of help remain unspecified.",
    "st-chp4-sec-ii-p109-cassiano-petau-preface-analogy":
        "Cassiano's quoted plan compares the preface for his drawing volumes with Petau's preface in the cited edition; the editions have not been independently checked.",
    "st-chp4-sec-ii-p109-gaudenzi-background":
        "This records only Haskell's description of Gaudenzi as a former Calvinist; its chronology and precise meaning are not independently resolved.",
    "st-chp4-sec-ii-p109-gaudenzi-baronio-jesuits":
        "This retains only Gaudenzi's quoted disrespect toward Baronio; the separately stated hostility to the Jesuits is recorded separately.",
    "st-chp4-sec-ii-p109-gaudenzi-copy-after-saracini":
        "The copy-to-original relation and Saracini attribution occur in Cassiano's letter as quoted by Haskell and are not independently verified.",
    "st-chp4-sec-ii-p109-gaudenzi-history-conclusions":
        "Haskell says the history's conclusions displeased unnamed local ecclesiastics; the affected group remains an open endpoint.",
    "st-chp4-sec-ii-p109-gaudenzi-papal-patronage":
        "Haskell reports difficulty securing patronage at the papal court; this does not assert a specific appointment, request, or grant.",
    "st-chp4-sec-ii-p109-gaudenzi-portrait-acknowledged":
        "Cassiano's quoted letter acknowledges the portrait copy with pleasure; neither the copy nor original is identified as a surviving object.",
    "st-chp4-sec-ii-p109-gaudenzi-portrait-request":
        "Haskell reports that Cassiano pressed Gaudenzi to send his likeness for the collection of illustrious men.",
    "st-chp4-sec-ii-p109-petau-preface-argument":
        "This summarizes an argument in the preface included with Petau's edition; it is not an independently consulted statement by Petau.",
    "st-chp4-sec-ii-p109-portrait-collection":
        "Haskell identifies the portraits as evidence for Cassiano's relation with Gaudenzi; the collection and portraits remain source-bounded.",
    "st-chp4-sec-ii-p109-sacrements-inference":
        "The link between Cassiano's religious inquiry and the commission is explicitly Haskell's qualified inference, not independent evidence about the commission.",
    "st-chp4-sec-ii-p109-gaudenzi-grison-origin":
        "This records Haskell's wording only; the precise geographic scope of Grison is unresolved.",
    "st-chp4-sec-ii-p109-gaudenzi-enemy-of-jesuits":
        "Haskell describes Gaudenzi as a bitter enemy of the Jesuits; the statement preserves the author's wording and does not independently verify the relationship.",
}
NONRELATION_NOTES = {
    "st-chp4-sec-ii-p109-antique-collection-imagery":
        "This is a scalar property reported for Cassiano's antiquities collection; the imagery is not identified as a bounded work group.",
    "st-chp4-sec-ii-p109-cassiano-interest-religions":
        "This is Haskell's scalar characterization of Cassiano's intellectual interest.",
    "st-chp4-sec-ii-p109-classical-devotion-not-neopaganism":
        "This records Haskell's interpretive contrast about Cassiano's classical devotion, not an asserted affiliation.",
    "st-chp4-sec-ii-p109-dispassionate-inquiry-fragment":
        "This is Haskell's scalar interpretation of Cassiano's inquiry; the sentence continues on p.110.",
    "st-chp4-sec-ii-p109-drawing-volume-deity-sacrifice":
        "This states the subject matter of one volume of drawings; no separate bounded entity for the depicted ancient views is identified.",
    "st-chp4-sec-ii-p109-interest-early-church-contemporary-life":
        "This is Haskell's interpretation of the scope of Cassiano's interests, not a relation to a named institution or group.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def quote_between(text: str, start: str, end: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at) + len(end)
    return text[start_at:end_at]


def classify(row: dict, relation: bool, note: str) -> None:
    q = row.setdefault("qualifiers", {})
    q["relation_candidate"] = relation
    q["relation_candidate_note"] = note


def set_statement(
    row: dict,
    *,
    predicate: str,
    subject: str | None,
    object_: str | None,
    claim: str,
    quote: str,
    qualification: str | None = None,
    line_start: int | None = None,
    line_end: int | None = None,
) -> None:
    row["predicate"] = predicate
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["original_quote"] = quote
    q = row["qualifiers"]
    q["claim"] = claim
    if qualification is not None:
        q["qualification"] = qualification
    if line_start is not None:
        q["source_line_start"] = line_start
    if line_end is not None:
        q["source_line_end"] = line_end


def make_statement(
    statement_id: str,
    *,
    subject: str | None,
    object_: str | None,
    predicate: str,
    claim: str,
    quote: str,
    line: int,
    speaker: str,
    relation: bool,
    note: str,
    mentions: list[str],
    qualification: str,
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line,
            "source_line_end": line,
            "pdf_physical_page": 20,
            "printed_page_locator": "p.109",
            "claim": claim,
            "speaker": speaker,
            "text_layer": "authorial narrative",
            "mentioned_candidate_ids": mentions,
            "qualification": qualification,
            "relation_candidate": relation,
            "relation_candidate_note": note,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


def segment_counts(rows: list[dict]) -> dict[str, int]:
    dual = [
        row for row in rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
    ]
    return {
        "statements": len(rows),
        "dual": len(dual),
        "relation_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in rows),
        "relation_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in rows),
        "dual_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual),
        "dual_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual),
        "unclassified": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in rows),
    }


def global_counts(rows: list[dict], candidate_count: int, mention_count: int) -> dict[str, int]:
    dual = [
        row for row in rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
    ]
    return {
        "all_statements": len(rows),
        "all_candidates": candidate_count,
        "all_mentions": mention_count,
        "dual_statements": len(dual),
        "dual_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual),
        "dual_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual),
        "dual_unclassified": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in dual),
        "relation_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in rows),
        "relation_true_open": sum(
            row.get("qualifiers", {}).get("relation_candidate") is True
            and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
            for row in rows
        ),
    }


def patched_jsonl_bytes(path: Path, updates: dict[str, dict], additions: list[dict]) -> bytes:
    serialized = {
        statement_id: json.dumps(row, ensure_ascii=False) + "\n"
        for statement_id, row in updates.items()
    }
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    output = []
    for line in lines:
        if not line.strip():
            output.append(line)
            continue
        statement_id = json.loads(line)["statement_id"]
        output.append(serialized.get(statement_id, line))
    if output and not output[-1].endswith(("\n", "\r")):
        output[-1] += "\n"
    output.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in additions)
    return "".join(output).encode("utf-8")


def patched_csv_bytes(path: Path, updates: dict[str, dict[str, str]]) -> bytes:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fields = list(reader.fieldnames or [])
    if not fields:
        raise SystemExit("preflight failed: mentions.csv has no header")
    previous_line = reader.line_num
    seen = set()
    for row in reader:
        end_line = reader.line_num
        mention_id = row["mention_id"]
        if mention_id in updates:
            if row["candidate_id"] != updates[mention_id]["expected_candidate_id"]:
                raise SystemExit(f"preflight failed: mention candidate changed: {mention_id}")
            changed = dict(row)
            changed["candidate_id"] = updates[mention_id]["candidate_id"]
            buffer = io.StringIO(newline="")
            writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
            writer.writerow(changed)
            lines[previous_line:end_line] = buffer.getvalue().splitlines(keepends=True)
            seen.add(mention_id)
        previous_line = end_line
    if seen != set(updates):
        raise SystemExit(f"preflight failed: mention rows missing: {sorted(set(updates) - seen)}")
    result = "".join(lines).encode("utf-8")
    return (b"\xef\xbb\xbf" + result) if has_bom else result


def count_mentions(path: Path) -> int:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted changes")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    mention_path = TABLES / "mentions.csv"
    for name, expected in EXPECTED_SHA256.items():
        path = TABLES / name
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"preflight failed: {name} hash changed: {actual}")
    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source asset hash changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[120:128])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("preflight failed: segment text hash changed")

    statements = read_jsonl(statement_path)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("preflight failed: statement IDs are not unique")
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if {row["statement_id"] for row in segment_rows} != ORIGINAL_IDS:
        raise SystemExit("preflight failed: p.109 original statement set changed")
    original_projection = {
        row["statement_id"]: {
            "subject": row.get("subject_candidate_id"),
            "predicate": row.get("predicate"),
            "object": row.get("object_candidate_id"),
            "relation_candidate": row.get("qualifiers", {}).get("relation_candidate"),
        }
        for row in segment_rows
    }
    dual_unclassified = [
        row for row in segment_rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
        and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if len(dual_unclassified) != 14 or any(
        row.get("qualifiers", {}).get("relation_candidate") is not None for row in segment_rows
    ):
        raise SystemExit("preflight failed: p.109 classification state changed")
    if NEW_IDS.intersection(by_id):
        raise SystemExit("preflight failed: a planned statement ID already exists")

    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    for row in segment_rows:
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"preflight failed: existing endpoint is missing: {endpoint}")
    if PORTRAIT_GROUP_ID not in candidate_ids:
        raise SystemExit("preflight failed: portrait group candidate is missing")

    with mention_path.open(encoding="utf-8-sig", newline="") as handle:
        all_mentions = list(csv.DictReader(handle))
    segment_mentions = [row for row in all_mentions if row["segment_id"] == SEGMENT_ID]
    span_errors = [
        row["mention_id"] for row in segment_mentions
        if segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]
    ]
    if span_errors:
        raise SystemExit(f"preflight failed: p.109 mention span errors: {span_errors}")
    for mention_id, expectation in MENTION_UPDATES.items():
        row = next((m for m in segment_mentions if m["mention_id"] == mention_id), None)
        if row is None or row["candidate_id"] != expectation[0]:
            raise SystemExit(f"preflight failed: expected mention mapping changed: {mention_id}")

    for statement_id, note in RELATION_NOTES.items():
        if statement_id in by_id:
            classify(by_id[statement_id], True, note)
    for statement_id, note in NONRELATION_NOTES.items():
        if statement_id in by_id:
            classify(by_id[statement_id], False, note)

    q = quote_between
    updates = {
        "st-chp4-sec-ii-p109-antique-collection-imagery": {
            "predicate": "collection_contains_many_examples_of_strange_pagan_imagery",
            "subject": "cand-5654", "object_": None,
            "claim": "Haskell says Cassiano's private antiquities collection contained many examples of unusual pagan imagery.",
            "quote": q(segment_text, "His collection of antiques contained many examples", "strange pagan imagery"),
        },
        "st-chp4-sec-ii-p109-cassiano-correspondence-expenses": {
            "predicate": "reports_cassiano_explained_financial_strain_and_promised_to_help_gaudenzi",
            "subject": "cand-2036", "object_": "cand-1116",
            "claim": "Haskell reports Cassiano explaining to Gaudenzi that money was tight because of the gentlemen's expenses, especially Cardinal Francesco Barberini's, but he would do his best.",
            "quote": q(segment_text, "Money was tight, he explained", "he would do his best.4"),
        },
        "st-chp4-sec-ii-p109-cassiano-helped-gaudenzi": {
            "predicate": "reports_cassiano_helped_gaudenzi_through_his_troubles",
            "subject": "cand-2036", "object_": "cand-1116",
            "claim": "Haskell says Cassiano had done most to help Gaudenzi through his troubles.",
            "quote": q(segment_text, "The man who had done most to help", "had been Cassiano."),
        },
        "st-chp4-sec-ii-p109-cassiano-interest-religions": {
            "predicate": "author_describes_cassiano_interest_in_religious_beliefs_and_rituals",
            "subject": "cand-2036", "object_": None,
            "claim": "Haskell says Cassiano was fascinated by the religious beliefs and rituals of different societies.",
            "quote": q(segment_text, "he was always fascinated by the religious beliefs", "different societies."),
        },
        "st-chp4-sec-ii-p109-cassiano-petau-preface-analogy": {
            "predicate": "drawing_volumes_plan_preface_by_analogy_with_petau_edition_preface",
            "subject": "cand-5850", "object_": "cand-5851",
            "claim": "Cassiano's quoted plan compares the preface for his drawing volumes with the preface Petau wrote for his 1630 Paris edition of Julian's works.",
            "quote": q(segment_text, "To explain the purpose of my collecting them", "republished in Paris in 1630."),
            "qualification": "Cassiano's words are quoted by Haskell; the manuscript volumes and cited edition were not independently checked.",
        },
        "st-chp4-sec-ii-p109-classical-devotion-not-neopaganism": {
            "predicate": "author_says_classical_devotion_did_not_lead_cassiano_to_neopaganism",
            "subject": "cand-2036", "object_": None,
            "claim": "Haskell says Cassiano's devotion to the classics did not lead him to a form of neopaganism.",
            "quote": q(segment_text, "His devotion to the classics did not", "a sort of neopaganism."),
        },
        "st-chp4-sec-ii-p109-dispassionate-inquiry-fragment": {
            "predicate": "author_attributes_dispassionate_inquiry_to_cassiano",
            "subject": "cand-2036", "object_": None,
            "claim": "Haskell says Cassiano's devotion to the classics encouraged a dispassionate inquiry into the fundamental subject continued on p.110.",
            "quote": q(segment_text, "Rather, it encouraged in him a dispassionate enquiry", "fundamental"),
        },
        "st-chp4-sec-ii-p109-drawing-volume-deity-sacrifice": {
            "predicate": "drawing_volume_is_devoted_to_ancient_views_of_deity_and_sacrifice",
            "subject": "cand-5849", "object_": None,
            "claim": "Haskell says one unidentified volume of Cassiano's drawings was devoted to objects concerning ancient views of deity and sacrifice.",
            "quote": q(segment_text, "one of his volumes of drawings was entirely devoted", "Deity and sacrifices"),
        },
        "st-chp4-sec-ii-p109-gaudenzi-background": {
            "predicate": "describes_gaudenzi_as_former_calvinist",
            "subject": "cand-1116", "object_": "cand-5845",
            "claim": "Haskell describes Gaudenzi as a former Calvinist.",
            "quote": "former Calvinist",
            "qualification": "This is Haskell's description; its chronology and precise meaning are not independently resolved.",
        },
        "st-chp4-sec-ii-p109-gaudenzi-baronio-jesuits": {
            "predicate": "quoted_gaudenzi_as_disrespectful_toward_baronio",
            "subject": "cand-1116", "object_": "cand-0250",
            "claim": "Haskell quotes Gaudenzi as disrespectful toward Baronio.",
            "quote": q(segment_text, "hardi et peu respectueux au Baronio", "Baronio"),
            "qualification": "The phrase is reported through Haskell and Pintard and is not independently checked.",
        },
        "st-chp4-sec-ii-p109-gaudenzi-copy-after-saracini": {
            "predicate": "portrait_copy_derived_from_original_attributed_to_saracini",
            "subject": "cand-5842", "object_": "cand-5843",
            "claim": "Cassiano's quoted letter says the portrait copy derives from a 'most perfect original' by the late Gherardo Saracini.",
            "quote": q(segment_text, "as it is derived from a most perfect original", "the copy cannot help being good."),
        },
        "st-chp4-sec-ii-p109-gaudenzi-history-conclusions": {
            "predicate": "history_conclusions_displease_unnamed_local_ecclesiastics",
            "subject": "cand-5844", "object_": None,
            "claim": "Haskell says Gaudenzi's History of the early church reached conclusions that displeased local ecclesiastics.",
            "quote": q(segment_text, "had come to conclusions in his History of the early church", "ce pays"),
            "qualification": "The local ecclesiastics are unnamed; their identity and number are not inferred.",
        },
        "st-chp4-sec-ii-p109-gaudenzi-papal-patronage": {
            "predicate": "reports_gaudenzi_found_papal_court_patronage_difficult_to_secure",
            "subject": "cand-1116", "object_": "cand-5847",
            "claim": "Haskell says Gaudenzi had difficulty securing patronage at the papal court.",
            "quote": q(segment_text, "Not surprisingly he had found it difficult", "at the papal court."),
        },
        "st-chp4-sec-ii-p109-gaudenzi-portrait-acknowledged": {
            "predicate": "cassiano_acknowledges_gaudenzi_portrait_copy_with_pleasure",
            "subject": "cand-2036", "object_": "cand-5842",
            "claim": "Cassiano's quoted letter acknowledges Gaudenzi's likeness with pleasure and says it is very like him.",
            "quote": q(segment_text, "Some weeks later he acknowledges", "very like"),
        },
        "st-chp4-sec-ii-p109-gaudenzi-portrait-request": {
            "predicate": "cassiano_pressed_gaudenzi_to_send_likeness_for_portrait_collection",
            "subject": "cand-2036", "object_": "cand-1116",
            "claim": "Haskell reports that in 1647 Cassiano pressed Gaudenzi to send his likeness for Cassiano's collection of illustrious men.",
            "quote": q(segment_text, "In 1647 we find him pressing the scholar Paganino Gaudenzi", "collection I have of the most illustrious men"),
        },
        "st-chp4-sec-ii-p109-interest-early-church-contemporary-life": {
            "predicate": "author_says_cassiano_extended_interest_to_early_church_and_contemporary_society",
            "subject": "cand-2036", "object_": None,
            "claim": "Haskell says Cassiano extended this interest to forms of the early church and the society of his own day.",
            "quote": q(segment_text, "By extension he carried this interest", "the society of his own day."),
        },
        "st-chp4-sec-ii-p109-petau-preface-argument": {
            "predicate": "preface_in_petau_edition_defends_reading_julians_work",
            "subject": "cand-5851", "object_": "cand-1336",
            "claim": "Haskell summarizes Petau's preface in the edition: despite objections, Julian's works could be read for information on early Christian practices without endangering true religion.",
            "quote": q(segment_text, "There were people, he wrote in the preface", "early Christian practices."),
            "qualification": "This is Haskell's summary of the preface, not an independently consulted statement by Petau.",
        },
        "st-chp4-sec-ii-p109-portrait-collection": {
            "predicate": "portraits_in_cassianos_collection_reveal_relation_with_gaudenzi",
            "subject": "cand-2036", "object_": "cand-1116",
            "claim": "Haskell says the portraits represented in Cassiano's collection allow the reader to trace another of Cassiano's relations, then identifies Gaudenzi.",
            "quote": q(segment_text, "represented in Cassiano", "unorthodox relationships."),
            "qualification": "This is Haskell's framing of the transition to Gaudenzi; the portrait group and relationship remain source-bounded.",
        },
        "st-chp4-sec-ii-p109-sacrements-inference": {
            "predicate": "author_infers_interest_in_early_church_led_cassiano_to_commission_sacraments",
            "subject": "cand-2036", "object_": "cand-5789",
            "claim": "Haskell says, with 'no doubt', that this interest led Cassiano to commission the Sacraments.",
            "quote": q(segment_text, "This, no doubt, was what led Cassiano to commission", "the Sacraments."),
            "qualification": "Explicitly Haskell's inference; it does not independently establish who selected particular subjects.",
        },
    }
    for statement_id, values in updates.items():
        set_statement(by_id[statement_id], **values)

    by_id["st-chp4-sec-ii-p109-portrait-collection"]["qualifiers"]["mentioned_candidate_ids"] = [
        candidate_id
        for candidate_id in by_id["st-chp4-sec-ii-p109-portrait-collection"]["qualifiers"].get("mentioned_candidate_ids", [])
        if candidate_id != "cand-5832"
    ]
    for candidate_id in (PORTRAIT_GROUP_ID, "cand-1116", "cand-2036"):
        if candidate_id not in by_id["st-chp4-sec-ii-p109-portrait-collection"]["qualifiers"]["mentioned_candidate_ids"]:
            by_id["st-chp4-sec-ii-p109-portrait-collection"]["qualifiers"]["mentioned_candidate_ids"].append(candidate_id)

    new_rows = [
        make_statement(
            "st-chp4-sec-ii-p109-gaudenzi-grison-origin",
            subject="cand-1116", object_="cand-5846",
            predicate="describes_gaudenzi_as_of_grison_origin",
            claim="Haskell describes Gaudenzi as being of Grison origin.",
            quote=q(segment_text, "of Grison origin", "origin"),
            line=123, speaker="Haskell", relation=True,
            note=RELATION_NOTES["st-chp4-sec-ii-p109-gaudenzi-grison-origin"],
            mentions=["cand-1116", "cand-5846"],
            qualification="The exact geographic scope of Grison is unresolved.",
        ),
        make_statement(
            "st-chp4-sec-ii-p109-gaudenzi-enemy-of-jesuits",
            subject="cand-1116", object_="cand-1319",
            predicate="describes_gaudenzi_as_bitter_enemy_of_jesuits",
            claim="Haskell describes Gaudenzi as a bitter enemy of the Jesuits.",
            quote=q(segment_text, "a bitter enemy of the Jesuits", "the Jesuits"),
            line=123, speaker="Haskell", relation=True,
            note=RELATION_NOTES["st-chp4-sec-ii-p109-gaudenzi-enemy-of-jesuits"],
            mentions=["cand-1116", "cand-1319"],
            qualification="This is Haskell's description; no specific Jesuit individual or encounter is identified.",
        ),
    ]
    for row in new_rows:
        if row["statement_id"] not in NEW_IDS:
            raise SystemExit(f"preflight failed: unexpected new ID: {row['statement_id']}")
        if row["original_quote"] not in segment_text:
            raise SystemExit(f"preflight failed: new quote not in source: {row['statement_id']}")
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"preflight failed: missing endpoint: {row['statement_id']} -> {endpoint}")
        by_id[row["statement_id"]] = row
    if {row["statement_id"] for row in new_rows} != NEW_IDS:
        raise SystemExit("preflight failed: new statement IDs differ from declared set")

    for mention in all_mentions:
        if mention["mention_id"] in MENTION_UPDATES:
            expected_old, new_id = MENTION_UPDATES[mention["mention_id"]]
            if mention["candidate_id"] != expected_old or new_id not in candidate_ids:
                raise SystemExit(f"preflight failed: invalid mention update: {mention['mention_id']}")
            mention["candidate_id"] = new_id
    by_mention_id = {row["mention_id"]: row for row in all_mentions}

    after_segment = [row for row in by_id.values() if row.get("segment_id") == SEGMENT_ID]
    expected_segment = {
        "statements": 21, "dual": 14, "relation_true": 15, "relation_false": 6,
        "dual_true": 14, "dual_false": 0, "unclassified": 0,
    }
    if segment_counts(after_segment) != expected_segment:
        raise SystemExit(f"preflight failed: unexpected p.109 result: {segment_counts(after_segment)}")

    expected_global = {
        "all_statements": 12997,
        "all_candidates": 11626,
        "all_mentions": 27564,
        "dual_statements": 8798,
        "dual_true": 5666,
        "dual_false": 515,
        "dual_unclassified": 2617,
        "relation_true": 5728,
        "relation_true_open": 62,
    }
    projected_global = global_counts(list(by_id.values()), len(candidate_ids), len(all_mentions))
    if projected_global != expected_global:
        raise SystemExit(f"preflight failed: unexpected projected global totals: {projected_global}")
    mention_span_errors = [
        row["mention_id"] for row in all_mentions
        if row["segment_id"] == SEGMENT_ID
        and segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]
    ]
    if mention_span_errors:
        raise SystemExit(f"preflight failed: mention spans changed: {mention_span_errors}")

    statement_updates = {statement_id: by_id[statement_id] for statement_id in updates}
    projected_statement_bytes = patched_jsonl_bytes(statement_path, statement_updates, new_rows)
    mention_updates = {
        mention_id: {"expected_candidate_id": old, "candidate_id": new}
        for mention_id, (old, new) in MENTION_UPDATES.items()
    }
    projected_mention_bytes = patched_csv_bytes(mention_path, mention_updates)
    projected_mention_count = count_mentions(mention_path)
    if projected_mention_count != 27564:
        raise SystemExit(f"preflight failed: unexpected mention row count: {projected_mention_count}")

    changes = []
    for statement_id in sorted(ORIGINAL_IDS):
        row = by_id[statement_id]
        changes.append({
            "statement_id": statement_id,
            "before": original_projection[statement_id],
            "after": {
                "subject": row.get("subject_candidate_id"),
                "predicate": row.get("predicate"),
                "object": row.get("object_candidate_id"),
                "relation_candidate": row.get("qualifiers", {}).get("relation_candidate"),
            },
        })
    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "table_sha256_before": EXPECTED_SHA256,
        "original_statements_reviewed": len(ORIGINAL_IDS),
        "existing_statement_changes": changes,
        "new_statements": [
            {
                "statement_id": row["statement_id"],
                "subject": row["subject_candidate_id"],
                "predicate": row["predicate"],
                "object": row["object_candidate_id"],
                "relation_candidate": row["qualifiers"]["relation_candidate"],
            }
            for row in new_rows
        ],
        "mention_repairs": MENTION_UPDATES,
        "segment_after": expected_segment,
        "global_after": expected_global,
        "backups": [
            f"book-statements.jsonl.{BACKUP_SUFFIX}",
            f"mentions.csv.{BACKUP_SUFFIX}",
        ],
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    statement_backup = statement_path.with_name(statement_path.name + "." + BACKUP_SUFFIX)
    mention_backup = mention_path.with_name(mention_path.name + "." + BACKUP_SUFFIX)
    backups = {statement_backup: statement_path, mention_backup: mention_path}
    for backup, original in backups.items():
        if backup.exists():
            if sha(backup.read_bytes()) != EXPECTED_SHA256[original.name]:
                raise SystemExit(f"apply refused: existing backup differs from prewrite file: {backup.name}")
        else:
            shutil.copy2(original, backup)

    statement_temp = statement_path.with_name(statement_path.name + ".tmp-write")
    mention_temp = mention_path.with_name(mention_path.name + ".tmp-write")
    statement_temp.write_bytes(projected_statement_bytes)
    mention_temp.write_bytes(projected_mention_bytes)
    try:
        statement_temp.replace(statement_path)
        mention_temp.replace(mention_path)
        written = read_jsonl(statement_path)
        with mention_path.open(encoding="utf-8-sig", newline="") as handle:
            written_mentions = list(csv.DictReader(handle))
        actual_global = global_counts(written, len(candidate_ids), len(written_mentions))
        actual_segment = segment_counts([row for row in written if row.get("segment_id") == SEGMENT_ID])
        actual_mentions = {row["mention_id"]: row["candidate_id"] for row in written_mentions}
        if (
            actual_global != expected_global
            or actual_segment != expected_segment
            or any(actual_mentions.get(mid) != expected_new for mid, (_, expected_new) in MENTION_UPDATES.items())
        ):
            raise RuntimeError(f"postwrite mismatch: segment={actual_segment}, global={actual_global}")
    except Exception:
        shutil.copy2(statement_backup, statement_path)
        shutil.copy2(mention_backup, mention_path)
        statement_temp.unlink(missing_ok=True)
        mention_temp.unlink(missing_ok=True)
        raise

    print(json.dumps({
        "apply": "written",
        "backup_hashes": {
            statement_backup.name: sha(statement_backup.read_bytes()),
            mention_backup.name: sha(mention_backup.read_bytes()),
        },
        "sha256_after": {
            statement_path.name: sha(statement_path.read_bytes()),
            mention_path.name: sha(mention_path.read_bytes()),
        },
        "segment_after": actual_segment,
        "global_after": actual_global,
        "mention_repairs": {
            mid: actual_mentions[mid] for mid in MENTION_UPDATES
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
