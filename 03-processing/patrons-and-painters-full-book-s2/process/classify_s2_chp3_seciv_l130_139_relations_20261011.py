from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l130-139"
PREFIX = "st-chp3-seciv-l130-139-"
SOURCE_SHA = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA = "a79d7913c72e8efa785f510fd23415563725a4e6b77bb06b533a6c1eae10fd8f"
PRE_HASHES = {
    STATEMENTS.name: "80f8c67638915537e0b707c20fd1024d7a5820053498be286a4d80d7c6987e66",
    CANDIDATES.name: "b92c1568ce1cd156a990ac2feeb17f8be9f2b5ef4f98be510cb6e1a492b804dc",
    MENTIONS.name: "22baacbcf297ec4e01f47b40e323540c9e045a94551fce6ce5a057433420053a",
}
BACKUP_SUFFIX = ".bak-s2-chp3-seciv-l130-139-relations-20261011"


RELATION_NOTES = {
    "artists-consulted": "The source says various artists and architects were consulted about filling the unbuilt dome gap. The source does not name the consulting authority or the group members.",
    "corridor-layout": "Haskell describes frames and putti as separators in the corridor decoration; this records a work-to-motif relation, not separately identified works.",
    "cycle-culminates-in-la-storta-promise": "Haskell says the fresco cycle culminated in the promise narrative at La Storta; the religious account is not independently verified.",
    "cycle-depicts-early-society-events": "Haskell says the frescoes represent principal events in the early history of the Jesuit Society.",
    "device-shown-june-1685": "The source says Pozzo's canvas device was shown to the public in June 1685; no separate exhibition event or exact venue is supplied.",
    "duke-appealed-to-pope": "Haskell reports the Duke's appeal to the unnamed Pope after Pozzo explained the Pope's intervention; the Pope's identity remains unresolved.",
    "duke-pressured-jesuits": "Haskell reports the Duke's hostile treatment of Jesuits in his dominions; the particular acts and territories are not specified.",
    "duke-recalled-pozzo": "The source says the Duke called Pozzo back to decorate an unnamed gallery; this does not establish that the decoration was completed.",
    "general-lawful-demands": "The unnamed General told Pozzo that satisfying princes' lawful demands was his duty; the quotation does not establish that the Duke's request was lawful or fulfilled.",
    "giacomo-began-decoration": "Haskell identifies Giacomo Borgognone as the person who began the corridor decoration; its unfinished state at his death is recorded separately.",
    "jesuits-blamed-pozzo": "Haskell reports that the Jesuits in the Duke's dominions blamed Pozzo for their difficulties; this preserves the reported attribution.",
    "mattia-advice-plan-accepted": "Haskell says Pozzo's plan was accepted on Mattia de' Rossi's advice; the person or body that accepted it is not named.",
    "pope-authorized-refusal": "Haskell says the unnamed Pope authorized Pozzo to turn down the Duke's request; the passage does not identify the Pope.",
    "pope-confirmed-instructions": "Haskell says the Pope confirmed instructions to Pozzo; no further identity or date is inferred.",
    "pozzo-appealed-to-pope": "Haskell reports Pozzo's secret appeal to the unnamed Pope over the General's head; the Pope remains unidentified.",
    "pozzo-asked-general-to-refuse": "Haskell says Pozzo asked the unnamed Jesuit General to refuse the Duke's request; no identity is inferred.",
    "pozzo-derided": "Haskell reports derision from Pozzo's fellow Jesuits; the passage does not name individual critics.",
    "pozzo-painted-later-cycle": "Haskell says Pozzo painted the fresco cycle some years after 1685; the exact date is not supplied.",
    "pozzo-proposed-painted-dome": "Haskell says Pozzo proposed painting a perspective illusion on canvas; this is a proposal and does not imply completion or survival.",
    "pozzo-required-to-paint-corridor": "Haskell says Pozzo was required to paint the corridor decoration; the authority requiring it is not named.",
    "rector-wanted-dome-substitute": "Haskell says the unnamed Rector sought a substitute to fill the gap left by the unbuilt dome; the Rector's identity remains unresolved.",
    "rooms-preserved-and-converted": "Haskell says the former rooms were converted into chapels. The chapel group is unnamed and uncounted; preservation during Casa Professa construction is recorded separately.",
    "s-ignazio-incomplete": "Haskell attributes S. Ignazio's noncompletion partly to disputes with Ludovisi descendants. This does not establish ownership, legal rights, or the identity of every disputing party.",
    "scenes-depict-ignatius": "Haskell says the corridor scenes depict aspects of St Ignatius's sojourn in this world and the next.",
}

NONRELATION_NOTES = {
    "device-initially-justified": "This is Haskell's assessment of Pozzo's optimism about the device, not a relationship between Pozzo and the work; the Euclid comparison is retained as a rhetorical reference.",
    "device-nearly-invisible": "This is a reported condition of the painted canvas within a few years; no exact disappearance date or removal is stated.",
    "distorted-from-wrong-viewpoint": "This is Haskell's visual evaluation of the decoration, not a relation between two entities.",
    "duke-misunderstood-and-wrote": "This records the Duke's reported belief that the Jesuits had refused permission; it does not assert that the Jesuits actually refused. The letter action is recorded separately.",
    "later-writer-predicted-darkening": "This is an unnamed writer's prediction about deterioration of the canvas, not an entity-to-entity relation.",
    "pozzo-confidence-euclid": "This is a rhetorical comparison to a proposition of Euclid, not a historical relation between Pozzo and Euclid.",
    "quoted-description-praised-device": "This is an attributed aesthetic description and forecast about the device, not a relation to an identified evaluator or decision-maker.",
}

NEW_STATEMENT_IDS = [
    "rooms-preserved-at-casa-professa-construction",
    "casa-professa-adjoins-gesu",
    "s-ignazio-financial-difficulties",
    "pozzo-served-duke-of-savoy",
    "duke-permitted-pozzo-to-obey-oliva-summons",
    "oliva-summoned-pozzo-to-rome",
    "duke-wrote-unidentified-personal-letter",
    "corridor-left-incomplete-at-borgognone-death",
    "pozzo-painted-frescoes-in-tribune",
    "pozzo-painted-frescoes-in-apse",
    "jesuits-began-to-appreciate-pozzo",
    "promise-event-at-la-storta",
]
NEW_CANDIDATES = {
    "cand-11620": {
        "candidate_id": "cand-11620", "index_entry_id": "",
        "canonical_name": "Unidentified chapels converted from St Ignatius's former rooms at Casa Professa",
        "index_page_range": "", "suggested_type": "place", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says the former rooms where St Ignatius lived were converted into chapels. No chapel name, number, or individual identity is supplied; this place group remains source-bounded and open.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L132",
    },
    "cand-11621": {
        "candidate_id": "cand-11621", "index_entry_id": "",
        "canonical_name": "Unnamed artists and architects consulted about the S. Ignazio dome substitute",
        "index_page_range": "", "suggested_type": "", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell refers to various artists and architects consulted while the Rector sought a substitute for the planned dome. No members, count, consulting authority, or institution are named; the collective remains untyped and open.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L136",
    },
    "cand-11622": {
        "candidate_id": "cand-11622", "index_entry_id": "",
        "canonical_name": "Unidentified personal letter written by the Duke of Savoy in the Pozzo recall episode",
        "index_page_range": "", "suggested_type": "archive", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell's narrative says the Duke wrote another personal letter after believing that the Jesuits had refused permission. The passage gives no date, addressee, text, archival identifier, or evidence that a surviving document was consulted; this records only the source-bounded communication reference.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L134",
    },
}
NEW_MENTIONS = [
    {"mention_id": "m-chp3-seciv-l130-139-0065", "segment_id": SEGMENT_ID, "candidate_id": "cand-11620", "surface_form": "chapels", "start_char": "214", "end_char": "221", "note": "Plural, unnamed chapel group into which the former rooms were converted; count and individual identities are not given."},
    {"mention_id": "m-chp3-seciv-l130-139-0066", "segment_id": SEGMENT_ID, "candidate_id": "cand-11621", "surface_form": "Various artists and architects", "start_char": "2028", "end_char": "2058", "note": "Unnamed collective consulted about the S. Ignazio dome substitute; no members or consulting authority are specified."},
    {"mention_id": "m-chp3-seciv-l130-139-0067", "segment_id": SEGMENT_ID, "candidate_id": "cand-11622", "surface_form": "another personal letter", "start_char": "1404", "end_char": "1427", "note": "Source-bounded reference to the Duke's letter; addressee, date, contents, and survival are unknown."},
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], bytes]:
    raw = path.read_bytes()
    records = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return records, raw


def read_csv(path: Path) -> tuple[list[str], list[dict], str, bool, bytes]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), eol, bom, raw


def encode_csv(fields: list[str], rows: list[dict], eol: str, bom: bool) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="raise", lineterminator=eol)
    writer.writeheader()
    writer.writerows(rows)
    return (("\ufeff" if bom else "") + output.getvalue()).encode("utf-8")


def encode_jsonl_preserving_unchanged(records: list[dict], raw: bytes) -> bytes:
    raw_lines = raw.splitlines(keepends=True)
    current_by_id = {row["statement_id"]: row for row in records}
    if len(current_by_id) != len(records):
        raise SystemExit("duplicate statement IDs in prepared JSONL")
    eol = "\r\n" if b"\r\n" in raw else "\n"
    bom = raw.startswith(b"\xef\xbb\xbf")
    output: list[bytes] = []
    original_ids: set[str] = set()
    for line_index, line in enumerate(raw_lines):
        if not line.strip():
            output.append(line)
            continue
        original = json.loads(line.decode("utf-8-sig"))
        statement_id = original["statement_id"]
        if statement_id in original_ids:
            raise SystemExit(f"duplicate statement ID in source JSONL: {statement_id}")
        original_ids.add(statement_id)
        record = current_by_id.get(statement_id)
        if record is None:
            raise SystemExit(f"existing statement was removed from prepared JSONL: {statement_id}")
        if original == record:
            output.append(line)
        else:
            encoded = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + eol).encode("utf-8")
            if line_index == 0 and bom:
                encoded = b"\xef\xbb\xbf" + encoded
            output.append(encoded)
    new_ids = set(current_by_id) - original_ids
    if len(new_ids) != len(records) - len(original_ids):
        raise SystemExit("prepared JSONL contains unexpected or missing records")
    if new_ids and output and not output[-1].endswith((b"\n", b"\r")):
        output.append(eol.encode("ascii"))
    for record in records:
        if record["statement_id"] not in new_ids:
            continue
        line = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + eol).encode("utf-8")
        if not original_ids and not output and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line)
    return b"".join(output)


def make_statement(
    suffix: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    quote: str,
    line_start: int,
    line_end: int,
    claim: str,
    qualification: str,
    relation_candidate: bool,
    relation_note: str,
    linked: list[str] | None = None,
) -> dict:
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "print_page": 89,
        "pdf_physical_page": 31,
        "qualification": qualification,
        "relation_candidate": relation_candidate,
        "relation_candidate_note": relation_note,
    }
    if linked:
        qualifiers["linked_body_statement_ids"] = linked
    return {
        "statement_id": PREFIX + suffix,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and atomize S2 statements on CHP-3 printed p.89.")
    parser.add_argument("--apply", action="store_true", help="write after all dry-run preconditions pass")
    args = parser.parse_args()

    source_raw = SOURCE.read_bytes()
    if sha(source_raw) != SOURCE_SHA:
        raise SystemExit("source file hash changed; re-review the source before applying")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    normalized_segment = "\n".join(source_lines[129:139])
    if sha(normalized_segment.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("normalized segment hash changed; re-review the segment before applying")
    segment_rows, _ = read_jsonl(SEGMENTS)
    segment = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment) != 1 or segment[0].get("sha256") != SEGMENT_SHA:
        raise SystemExit("segment inventory does not match the reviewed source segment")
    coverage_fields, coverage_rows, _, _, _ = read_csv(COVERAGE)
    coverage = [row for row in coverage_rows if row.get("segment_id") == SEGMENT_ID]
    if len(coverage) != 1 or (coverage[0].get("disposition"), coverage[0].get("migration_status")) != ("reviewed", "complete"):
        raise SystemExit("unexpected coverage state; preserve it and re-review before applying")

    statement_rows, statement_raw = read_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_eol, candidate_bom, _ = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_eol, mention_bom, _ = read_csv(MENTIONS)
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        if sha(path.read_bytes()) != PRE_HASHES[path.name]:
            raise SystemExit(f"unexpected {path.name} hash; table changed since review")

    segment_statements = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    expected_ids = set(RELATION_NOTES) | set(NONRELATION_NOTES)
    found_ids = {
        row["statement_id"][len(PREFIX):]
        for row in segment_statements
        if row.get("statement_id", "").startswith(PREFIX)
    }
    if len(segment_statements) != 31 or found_ids != expected_ids:
        raise SystemExit(f"unexpected segment statements: count={len(segment_statements)}, missing={sorted(expected_ids-found_ids)}, extra={sorted(found_ids-expected_ids)}")
    if set(RELATION_NOTES) & set(NONRELATION_NOTES):
        raise SystemExit("classification plans overlap")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in segment_statements):
        raise SystemExit("a statement in this segment is already classified")

    candidate_ids = {row.get("candidate_id") for row in candidate_rows}
    if candidate_ids & set(NEW_CANDIDATES):
        raise SystemExit("one or more planned candidate IDs already exist")
    all_statement_ids = {row.get("statement_id") for row in statement_rows}
    planned_statement_ids = {PREFIX + suffix for suffix in NEW_STATEMENT_IDS}
    if all_statement_ids & planned_statement_ids or len(planned_statement_ids) != len(NEW_STATEMENT_IDS):
        raise SystemExit("one or more planned statement IDs already exist or are duplicated")
    all_mention_ids = {row.get("mention_id") for row in mention_rows}
    planned_mention_ids = {row["mention_id"] for row in NEW_MENTIONS}
    if all_mention_ids & planned_mention_ids or len(planned_mention_ids) != len(NEW_MENTIONS):
        raise SystemExit("one or more planned mention IDs already exist or are duplicated")

    for mention in NEW_MENTIONS:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if normalized_segment[start:end] != mention["surface_form"]:
            raise SystemExit(f"mention span does not match source: {mention['mention_id']}")

    statement_map = {row["statement_id"]: row for row in segment_statements}
    for row in segment_statements:
        suffix = row["statement_id"][len(PREFIX):]
        q = row.setdefault("qualifiers", {})
        relation = suffix in RELATION_NOTES
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = (RELATION_NOTES if relation else NONRELATION_NOTES)[suffix]

    # Split independent facts and correct endpoints that currently conflate a
    # speaker, a rhetorical comparison, or a work's location with a relation.
    rooms = statement_map["st-chp3-seciv-l130-139-rooms-preserved-and-converted"]
    rooms["object_candidate_id"] = "cand-11620"
    rooms["predicate"] = "converted_into_unnamed_chapels"
    rooms["qualifiers"]["claim"] = "Haskell says the former rooms where St Ignatius lived were converted into chapels."
    rooms["qualifiers"]["qualification"] = "The chapel group is unnamed and uncounted. The rooms' preservation during Casa Professa construction is recorded separately."
    general = statement_map["st-chp3-seciv-l130-139-general-lawful-demands"]
    general["object_candidate_id"] = "cand-2034"
    general["predicate"] = "told_pozzo_of_duty_to_satisfy_great_princes_in_lawful_demands"
    general["qualifiers"]["claim"] = "The unnamed General told Pozzo that satisfying great princes in their lawful demands was his duty."
    general["qualifiers"]["qualification"] = "This is the General's reported response to Pozzo; it does not establish that the Duke's request was lawful or satisfied."
    artists = statement_map["st-chp3-seciv-l130-139-artists-consulted"]
    artists["subject_candidate_id"] = "cand-11621"
    artists["object_candidate_id"] = "cand-5367"
    artists["predicate"] = "consulted_about_s_ignazio_dome_substitute"
    artists["qualifiers"]["claim"] = "Haskell says various artists and architects were consulted about filling the gap left by the unbuilt S. Ignazio dome."
    artists["qualifiers"]["qualification"] = "The consulted group and the consulting authority are unnamed; Pozzo is separately identified among those who submitted plans."
    duke_letter = statement_map["st-chp3-seciv-l130-139-duke-misunderstood-and-wrote"]
    duke_letter["predicate"] = "believed_jesuits_had_refused_pozzo_permission"
    duke_letter["qualifiers"]["claim"] = "Haskell says the Duke thought the Jesuits had refused permission."
    duke_letter["qualifiers"]["qualification"] = "This records the Duke's reported belief and does not assert that the Jesuits actually refused. The letter action is recorded separately."
    duke_letter["original_quote"] = "This prince, thinking that it was the Jesuits who had refused permission"
    duke_recall = statement_map["st-chp3-seciv-l130-139-duke-recalled-pozzo"]
    duke_recall["predicate"] = "recalled_pozzo_to_decorate_an_unnamed_gallery"
    duke_recall["qualifiers"]["claim"] = "Haskell says the Duke of Savoy called Pozzo back to decorate a gallery."
    duke_recall["qualifiers"]["qualification"] = "The passage does not name the gallery or say that the decoration was completed; Pozzo's prior service and the Duke's permission concerning Oliva's summons are recorded separately."
    ignazio = statement_map["st-chp3-seciv-l130-139-s-ignazio-incomplete"]
    ignazio["predicate"] = "remained_incomplete_amid_disputes_with_ludovisi_descendants"
    ignazio["qualifiers"]["claim"] = "Haskell links S. Ignazio's noncompletion to disputes with Ludovisi descendants."
    ignazio["qualifiers"]["qualification"] = "The passage does not establish ownership, legal rights, or the identity of all disputing parties; financial difficulty is recorded separately."
    giacomo = statement_map["st-chp3-seciv-l130-139-giacomo-began-decoration"]
    giacomo["predicate"] = "begun_by_giacomo_borgognone"
    giacomo["qualifiers"]["claim"] = "Haskell says Giacomo Borgognone began decorating the corridor."
    giacomo["qualifiers"]["qualification"] = "The decoration's unfinished state at Borgognone's death is recorded separately."
    euclid = statement_map["st-chp3-seciv-l130-139-pozzo-confidence-euclid"]
    euclid["object_candidate_id"] = None
    euclid["predicate"] = "claimed_confidence_comparable_to_euclidean_proposition"
    euclid["qualifiers"]["claim"] = "Haskell says Pozzo claimed to be as sure of the result as of a proposition of Euclid."
    euclid["qualifiers"]["qualification"] = "Euclid is a rhetorical comparison, not the object of a historical relation."
    justified = statement_map["st-chp3-seciv-l130-139-device-initially-justified"]
    justified["object_candidate_id"] = None
    justified["predicate"] = "pozzo_optimism_about_device_initially_justified"
    justified["qualifiers"]["claim"] = "Haskell says Pozzo's optimism about the device was initially justified."
    justified["qualifiers"]["qualification"] = "This is an authorial assessment of the device's early reception, not a direct relation between Pozzo and the work."

    new_rows = [
        make_statement(
            "rooms-preserved-at-casa-professa-construction", "cand-5363", None,
            "former_rooms_preserved_when_casa_professa_was_built",
            "These had been preserved when the Casa Professa was built adjoining the Gesù in 1602.",
            131, 132,
            "Haskell says the former rooms where St Ignatius lived had been preserved when Casa Professa was built.",
            "This is a status claim about the rooms during construction; no separate construction date for the rooms is stated.",
            False, "This records the rooms' preservation as a single-entity status, not a relation to Casa Professa.",
            ["st-chp3-seciv-l130-139-rooms-preserved-and-converted"],
        ),
        make_statement(
            "casa-professa-adjoins-gesu", "cand-5206", "cand-5200",
            "casa_professa_built_adjoining_gesu_in_1602",
            "the Casa Professa was built adjoining the Gesù in 1602",
            131, 132,
            "Haskell says Casa Professa was built adjoining the Gesù in 1602.",
            "The statement preserves the source's adjacency and date without resolving the precise Casa Professa identity.",
            True, "This is an explicit place-to-place adjacency in the source; no further identity or current-status claim is added.",
        ),
        make_statement(
            "s-ignazio-financial-difficulties", "cand-0703", None,
            "church_incomplete_due_to_financial_difficulties",
            "The church of S. Ignazio had never been completed owing to financial difficulties",
            136, 136,
            "Haskell says S. Ignazio had never been completed owing to financial difficulties.",
            "The separate dispute with Ludovisi descendants remains recorded in the existing statement; no exact financial amount or period is given.",
            False, "This is a single-place construction-status claim.",
            ["st-chp3-seciv-l130-139-s-ignazio-incomplete"],
        ),
        make_statement(
            "pozzo-served-duke-of-savoy", "cand-2034", "cand-2388",
            "previously_worked_in_service_of_duke_of_savoy",
            "The Duke of Savoy, in whose service the artist had previously worked",
            133, 133,
            "Haskell says Pozzo had previously worked in the service of the Duke of Savoy.",
            "No role, date, or duration is supplied; the Duke's identity remains the S2 candidate's unresolved alignment question.",
            True, "The source explicitly states Pozzo's prior service to the Duke; no office or dates are inferred.",
            ["st-chp3-seciv-l130-139-duke-recalled-pozzo"],
        ),
        make_statement(
            "duke-permitted-pozzo-to-obey-oliva-summons", "cand-2388", "cand-2034",
            "reluctantly_permitted_pozzo_to_obey_olivas_summons_to_rome",
            "who had reluctantly given him permission to obey Oliva’s summons to Rome",
            133, 133,
            "Haskell says the Duke reluctantly permitted Pozzo to obey Oliva's summons to Rome.",
            "Permission is not treated as proof of employment terms or of a completed return; the summons is recorded separately.",
            True, "The passage explicitly gives the Duke as permission-giver and Pozzo as recipient.",
            ["st-chp3-seciv-l130-139-duke-recalled-pozzo", "st-chp3-seciv-l130-139-oliva-summoned-pozzo-to-rome"],
        ),
        make_statement(
            "oliva-summoned-pozzo-to-rome", "cand-1775", "cand-2034",
            "summoned_pozzo_to_rome",
            "Oliva’s summons to Rome",
            133, 133,
            "Haskell refers to Oliva's summons for Pozzo to go to Rome.",
            "The sentence does not date this summons or specify a separate commissioning scope.",
            True, "Oliva is explicitly identified as the source of the summons; Rome is retained as its stated destination in the linked permission claim.",
            ["st-chp3-seciv-l130-139-duke-permitted-pozzo-to-obey-oliva-summons"],
        ),
        make_statement(
            "duke-wrote-unidentified-personal-letter", "cand-2388", "cand-11622",
            "wrote_another_personal_letter",
            "wrote another personal letter",
            134, 134,
            "Haskell says the Duke wrote another personal letter after thinking the Jesuits had refused permission.",
            "The addressee, date, contents, and survival of the letter are not stated.",
            True, "The source explicitly reports a letter-writing act; its unidentified recipient is not inferred.",
            ["st-chp3-seciv-l130-139-duke-misunderstood-and-wrote"],
        ),
        make_statement(
            "corridor-left-incomplete-at-borgognone-death", "cand-5365", None,
            "corridor_decoration_left_incomplete_at_borgognones_death",
            "The task of decorating this corridor had been begun by Giacomo Borgognone, and left incomplete at his death.",
            132, 132,
            "Haskell says the corridor decoration remained incomplete when Borgognone died.",
            "No date for Borgognone's death or later completion is given in this sentence.",
            False, "This is a single-work status at an unspecified time, separated from the creator attribution.",
            ["st-chp3-seciv-l130-139-giacomo-began-decoration"],
        ),
        make_statement(
            "pozzo-painted-frescoes-in-tribune", "cand-5373", "cand-5372",
            "fresco_cycle_located_in_tribune",
            "Pozzo painted frescoes in the tribune",
            138, 138,
            "Haskell locates Pozzo's later frescoes in the tribune of S. Ignazio.",
            "The date is only given as some years after 1685 in the linked painting statement.",
            True, "The source explicitly locates the frescoes in the tribune; this records the work-to-place relation.",
            ["st-chp3-seciv-l130-139-pozzo-painted-later-cycle"],
        ),
        make_statement(
            "pozzo-painted-frescoes-in-apse", "cand-5373", "cand-5096",
            "fresco_cycle_located_in_apse",
            "Pozzo painted frescoes in the apse",
            138, 138,
            "Haskell locates Pozzo's later frescoes in the apse of S. Ignazio.",
            "The date is only given as some years after 1685 in the linked painting statement.",
            True, "The source explicitly locates the frescoes in the apse; this records the work-to-place relation.",
            ["st-chp3-seciv-l130-139-pozzo-painted-later-cycle"],
        ),
        make_statement(
            "jesuits-began-to-appreciate-pozzo", "cand-3403", "cand-2034",
            "began_to_appreciate_pozzo",
            "Pozzo was beginning to be appreciated by the Jesuits",
            133, 133,
            "Haskell says the Jesuits were beginning to appreciate Pozzo.",
            "This is a gradual, source-attributed description and not a claim of unanimous or permanent approval.",
            True, "The passage explicitly reports the Jesuits' emerging appreciation of Pozzo.",
            ["st-chp3-seciv-l130-139-duke-recalled-pozzo"],
        ),
        make_statement(
            "promise-event-at-la-storta", "cand-5375", "cand-5374",
            "promise_narrative_located_at_la_storta",
            "Christ’s amply fulfilled promise to St Ignatius at La Storta",
            138, 139,
            "Haskell says the fresco cycle culminates in Christ's promise to St Ignatius at La Storta.",
            "This preserves Haskell's religious narrative and is not an independent verification of the event.",
            True, "The source explicitly names La Storta as the setting of the depicted promise.",
            ["st-chp3-seciv-l130-139-cycle-culminates-in-la-storta-promise"],
        ),
    ]
    statement_rows.extend(new_rows)
    for row in new_rows:
        if row["statement_id"] in all_statement_ids:
            raise SystemExit(f"duplicate new statement ID: {row['statement_id']}")

    candidate_rows.extend(NEW_CANDIDATES.values())
    mention_rows.extend(NEW_MENTIONS)
    for mention in NEW_MENTIONS:
        candidate_id = mention["candidate_id"]
        if candidate_id not in NEW_CANDIDATES:
            raise SystemExit(f"new mention has no new candidate: {mention['mention_id']}")

    # Validate candidate endpoints used by newly classified statements and
    # location edges before serialization.
    candidate_id_set = {row["candidate_id"] for row in candidate_rows}
    for row in statement_rows:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_id_set:
                raise SystemExit(f"missing candidate endpoint {endpoint} in {row['statement_id']}")

    segment_after = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment_after) != 43 or any((row.get("qualifiers") or {}).get("relation_candidate") is None for row in segment_after):
        raise SystemExit("segment classification completeness check failed")
    segment_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in segment_after)
    segment_nonrelations = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in segment_after)
    bilateral = [row for row in statement_rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    bilateral_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral)
    bilateral_nonrelations = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral)
    bilateral_unclassified = len(bilateral) - bilateral_relations - bilateral_nonrelations
    total_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statement_rows)
    open_relations = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
        for row in statement_rows
    )
    if (len(statement_rows), len(candidate_rows), len(mention_rows)) != (12822, 11600, 27535):
        raise SystemExit("unexpected post-write row counts")
    if (segment_relations, segment_nonrelations) != (33, 10):
        raise SystemExit(f"unexpected segment classification totals: {segment_relations}/{segment_nonrelations}")
    if (len(bilateral), bilateral_relations, bilateral_nonrelations, bilateral_unclassified, total_relations, open_relations) != (8616, 5140, 490, 2986, 5192, 52):
        raise SystemExit("unexpected global relation classification totals")

    prepared = {
        STATEMENTS: encode_jsonl_preserving_unchanged(statement_rows, statement_raw),
        CANDIDATES: encode_csv(candidate_fields, candidate_rows, candidate_eol, candidate_bom),
        MENTIONS: encode_csv(mention_fields, mention_rows, mention_eol, mention_bom),
    }
    print("source and segment hashes match the reviewed CHP-3 p.89 passage")
    print("segment: 31 existing statements classified; 12 atomic statements added")
    print(f"classification: {segment_relations} relation candidates; {segment_nonrelations} nonrelations; 0 unclassified")
    print("candidates: 3 open source-bounded candidates added; mentions: 3 exact spans added")
    print("endpoint corrections: Jesuit General response -> Pozzo; Euclid comparison detached; chapel conversion and anonymous consultation linked")
    print(f"post totals: statements={len(statement_rows)} candidates={len(candidate_rows)} mentions={len(mention_rows)}")
    print(f"bilateral statements: {len(bilateral)}; relation={bilateral_relations}; nonrelation={bilateral_nonrelations}; unclassified={bilateral_unclassified}")
    print(f"relation candidates total={total_relations}; open endpoints={open_relations}")
    print("statement JSONL serializer preserves every unchanged row and blank line byte-for-byte")
    if not args.apply:
        print("DRY-RUN PASS; no files written")
        return

    backup_paths = {
        STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX),
        CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + BACKUP_SUFFIX),
        MENTIONS: MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX),
    }
    if any(path.exists() for path in backup_paths.values()):
        raise SystemExit("a recovery copy already exists; refusing to overwrite")
    for path, backup in backup_paths.items():
        shutil.copy2(path, backup)
    temps: list[tuple[Path, Path]] = []
    try:
        for path, data in prepared.items():
            temp = path.with_name(path.name + ".tmp-write")
            if temp.exists():
                raise SystemExit(f"temporary output already exists: {temp.name}")
            temp.write_bytes(data)
            temps.append((temp, path))
        for temp, path in temps:
            os.replace(temp, path)
        for path, data in prepared.items():
            if path.read_bytes() != data:
                raise SystemExit(f"post-write byte check failed: {path.name}")
    except Exception:
        for temp, _ in temps:
            if temp.exists():
                temp.unlink()
        for path, backup in backup_paths.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    print("APPLY PASS")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"post_sha256 {path.name} {sha(path.read_bytes())}")
    print("recovery copies:")
    for backup in backup_paths.values():
        print(backup.name)


if __name__ == "__main__":
    main()
