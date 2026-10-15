#!/usr/bin/env python3
"""Review p.107 S2 relations, repair the prior-series endpoint, and preserve OCR evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l101-107"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "1a388b01323331b59dfef89a1df6f3545745e1fbf178394b49219c84d2f3bba7"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "6fb77b8a4b38c59f454f6685568ffc656fc96eb1b2d476311be008383d968e1f",
    "entity-candidates.csv": "7ea09293bda6e942ba6ebd19085126df10be4ab853341851d6078ad031aa607f",
    "mentions.csv": "43c8cb6ea1bbf2652d527bc7f63e99b1185df014e927635869fb4d764d8adcbe",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l101-107-relations-20261011"
NEW_CANDIDATE_ID = "cand-11648"
NEW_MENTION_ID = "m-chp4-sec-ii-l101-107-oderisi-frescoes"
NEW_STATEMENT_IDS = {
    "st-chp4-sec-ii-l101-107-possible-echoes-in-other-works",
    "st-chp4-sec-ii-l101-107-possible-schismatic-sect",
    "st-chp4-sec-ii-l101-107-medieval-northern-precedents",
    "st-chp4-sec-ii-l101-107-oderisi-frescoes-ascribed",
}

ORIGINAL_IDS = {
    "st-chp4-sec-ii-l101-107-bouchard-bequest-fragment",
    "st-chp4-sec-ii-l101-107-bouchard-naude-libertins-close-friends",
    "st-chp4-sec-ii-l101-107-cassiano-contact-and-possible-echoes",
    "st-chp4-sec-ii-l101-107-cassiano-knew-their-beliefs",
    "st-chp4-sec-ii-l101-107-cassiano-motives-remain-speculative",
    "st-chp4-sec-ii-l101-107-cassiano-originated-series-idea",
    "st-chp4-sec-ii-l101-107-cassiano-possible-libertin-unlikely",
    "st-chp4-sec-ii-l101-107-cassiano-prominent-in-barberini-entourage",
    "st-chp4-sec-ii-l101-107-cassiano-temperament-grave",
    "st-chp4-sec-ii-l101-107-cassiano-vital-development-role-likely",
    "st-chp4-sec-ii-l101-107-entourage-does-not-establish-orthodoxy",
    "st-chp4-sec-ii-l101-107-investigation-framed-as-fragmentary",
    "st-chp4-sec-ii-l101-107-italian-sacrament-series-precedents",
    "st-chp4-sec-ii-l101-107-jansenism-possible-interpretation",
    "st-chp4-sec-ii-l101-107-jottings-decorum-and-church-misbehaviour",
    "st-chp4-sec-ii-l101-107-no-direct-attribution-of-beliefs",
    "st-chp4-sec-ii-l101-107-poussin-iconography-new",
    "st-chp4-sec-ii-l101-107-poussin-independent-thought",
    "st-chp4-sec-ii-l101-107-sacraments-studied-for-religious-views",
    "st-chp4-sec-ii-l101-107-seven-sacraments-general-subject",
}

RELATION_NOTES = {
    "st-chp4-sec-ii-l101-107-bouchard-bequest-fragment":
        "Haskell reports the bequest to Cassiano; the papers clause continues on p.108 and the conflicting will accounts remain attributed reports.",
    "st-chp4-sec-ii-l101-107-bouchard-naude-libertins-close-friends":
        "The relation is limited to the source-referred group of Bouchard, Naude, and other French libertins; it does not make every person in the broader category a friend.",
    "st-chp4-sec-ii-l101-107-cassiano-contact-and-possible-echoes":
        "Haskell explicitly reports contact with unnamed artists and scholars; the endpoint remains open because no bounded group or individual is named.",
    "st-chp4-sec-ii-l101-107-cassiano-knew-their-beliefs":
        "This is Haskell's strong inference about Cassiano's knowledge of the group, not a claim that he shared its beliefs.",
    "st-chp4-sec-ii-l101-107-cassiano-originated-series-idea":
        "This records Haskell's strong attribution of the idea to Cassiano; it is not an independently documented commission record.",
    "st-chp4-sec-ii-l101-107-cassiano-prominent-in-barberini-entourage":
        "Haskell reports Cassiano's prominence in this source-bounded, unnamed entourage; do not merge it with a broader Barberini circle.",
    "st-chp4-sec-ii-l101-107-cassiano-vital-development-role-likely":
        "The likelihood marker is preserved; Haskell does not present the role as independently documented.",
    "st-chp4-sec-ii-l101-107-italian-sacrament-series-precedents":
        "Haskell presents the Italian fresco series as a precedent for Poussin's series; the earlier cycle is unidentified beyond this passage.",
    "st-chp4-sec-ii-l101-107-jansenism-possible-interpretation":
        "Jansenism is raised as a possible interpretation only; Haskell does not assert Poussin's affiliation.",
    "st-chp4-sec-ii-l101-107-jottings-decorum-and-church-misbehaviour":
        "Haskell attributes these views to Cassiano's unidentified jottings; the notes are not quoted directly and the Bouchard comparison is contextual.",
    "st-chp4-sec-ii-l101-107-sacraments-studied-for-religious-views":
        "This reports the interpretive use of the series in scholarship, not a conclusion that the paintings establish Poussin's beliefs.",
}

NONRELATION_NOTES = {
    "st-chp4-sec-ii-l101-107-cassiano-motives-remain-speculative":
        "This is Haskell's proposal for a speculative inquiry, not a relation asserted between the named endpoints.",
    "st-chp4-sec-ii-l101-107-cassiano-possible-libertin-unlikely":
        "Haskell raises and then judges the affiliation unlikely; the passage does not assert Cassiano's membership in the group.",
    "st-chp4-sec-ii-l101-107-cassiano-temperament-grave":
        "This is an authorial comparison of temperament, retained as a scalar characterization rather than a social relation.",
    "st-chp4-sec-ii-l101-107-entourage-does-not-establish-orthodoxy":
        "This is Haskell's caution about what group association can establish; it does not assert a specific religious affiliation.",
    "st-chp4-sec-ii-l101-107-investigation-framed-as-fragmentary":
        "This characterizes the evidentiary situation and has no entity endpoints.",
    "st-chp4-sec-ii-l101-107-no-direct-attribution-of-beliefs":
        "This is Haskell's report of absent direct attribution in the cited libertins' accounts, not an affirmative relation.",
    "st-chp4-sec-ii-l101-107-poussin-iconography-new":
        "This is Haskell's evaluative property claim about the Seven Sacraments iconography, not a relation between artist and work.",
    "st-chp4-sec-ii-l101-107-poussin-independent-thought":
        "This is an authorial characterization of Poussin, not an entity relation.",
    "st-chp4-sec-ii-l101-107-seven-sacraments-general-subject":
        "This is Haskell's evaluation of the subject and treatment as revolutionary, not a relation between Poussin and the series.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def set_classification(row: dict, is_relation: bool, note: str) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = is_relation
    qualifiers["relation_candidate_note"] = note


def append_mentioned_ids(row: dict, *candidate_ids: str) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    current = qualifiers.setdefault("mentioned_candidate_ids", [])
    qualifiers["mentioned_candidate_ids"] = list(dict.fromkeys([*current, *candidate_ids]))


def statement(
    statement_id: str,
    subject_id: str | None,
    object_id: str | None,
    predicate: str,
    quote: str,
    claim: str,
    qualification: str,
    mentioned_ids: list[str],
    *,
    line: int = 102,
    is_relation: bool,
    relation_note: str,
    text_layer: str = "authorial narrative",
    footnote_source: dict | None = None,
    ocr_corrections: list[dict] | None = None,
) -> dict:
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "pdf_physical_page": 18,
        "printed_page_locator": "p.107",
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": text_layer,
        "mentioned_candidate_ids": mentioned_ids,
        "qualification": qualification,
        "relation_candidate": is_relation,
        "relation_candidate_note": relation_note,
    }
    if footnote_source:
        qualifiers.update(footnote_source)
    if ocr_corrections:
        qualifiers["ocr_corrections"] = ocr_corrections
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject_id,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted change set")
    args = parser.parse_args()

    paths = {
        name: TABLES / name
        for name in ("book-statements.jsonl", "entity-candidates.csv", "mentions.csv")
    }
    for name, expected in EXPECTED_SHA256.items():
        actual = sha(paths[name].read_bytes())
        if actual != expected:
            raise SystemExit(f"preflight failed: {name} hash changed: {actual}")

    source_bytes = SOURCE.read_bytes()
    if sha(source_bytes) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source asset hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[100:107])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("preflight failed: segment text hash changed")
    if "veryrare examples in Northern painting" not in segment_text:
        raise SystemExit("preflight failed: expected OCR form is absent")
    if "some frescoes ascribed to Roberto Oderisi in fourteenth-century Naples" not in segment_text:
        raise SystemExit("preflight failed: expected earlier-series phrase is absent")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates, candidate_fields = read_csv(paths["entity-candidates.csv"])
    mentions, mention_fields = read_csv(paths["mentions.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise SystemExit("preflight failed: statement IDs are not unique")
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if {row["statement_id"] for row in segment_rows} != ORIGINAL_IDS:
        raise SystemExit("preflight failed: p.107 statement set changed")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in segment_rows):
        raise SystemExit("preflight failed: p.107 statements are no longer all unclassified")
    if NEW_STATEMENT_IDS.intersection(statement_by_id):
        raise SystemExit("preflight failed: one or more new statement IDs already exist")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(candidate_by_id) != len(candidates):
        raise SystemExit("preflight failed: candidate IDs are not unique")
    if NEW_CANDIDATE_ID in candidate_by_id or max(int(row["candidate_id"][5:]) for row in candidates) != 11647:
        raise SystemExit("preflight failed: candidate sequence changed")
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("preflight failed: mention IDs are not unique")
    if NEW_MENTION_ID in mention_by_id:
        raise SystemExit("preflight failed: new mention ID already exists")
    segment_mentions = [row for row in mentions if row["segment_id"] == SEGMENT_ID]
    span_errors = [
        row["mention_id"] for row in segment_mentions
        if segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]
    ]
    if span_errors:
        raise SystemExit(f"preflight failed: existing p.107 mention spans mismatch: {span_errors}")
    new_surface = "some frescoes"
    new_start = segment_text.index(new_surface)
    new_end = new_start + len(new_surface)

    new_candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Italian Sacrament fresco series ascribed to Roberto Oderisi (fourteenth-century Naples; identity unresolved)",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell reports that an Italian Sacrament series had been painted in some frescoes ascribed to Roberto Oderisi in fourteenth-century Naples. The church, exact cycle identity, and attribution are not independently established.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L102",
    }
    if set(new_candidate) != set(candidate_fields):
        raise SystemExit("preflight failed: candidate schema differs from the planned row")
    candidates.append(new_candidate)
    mentions.append({
        "mention_id": NEW_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": NEW_CANDIDATE_ID,
        "surface_form": new_surface,
        "start_char": str(new_start),
        "end_char": str(new_end),
        "note": "Source-specific mention of the earlier Italian Sacrament fresco series; the exact cycle and church are unresolved.",
    })

    for statement_id, note in RELATION_NOTES.items():
        set_classification(statement_by_id[statement_id], True, note)
    for statement_id, note in NONRELATION_NOTES.items():
        set_classification(statement_by_id[statement_id], False, note)

    contact = statement_by_id["st-chp4-sec-ii-l101-107-cassiano-contact-and-possible-echoes"]
    contact["predicate"] = "in_touch_with_unnamed_artists_and_scholars"
    contact["original_quote"] = "For Cassiano was in touch with artists and scholars of all kinds"
    contact["qualifiers"]["claim"] = "Haskell says Cassiano was in touch with artists and scholars of all kinds."
    contact["qualifiers"]["qualification"] = "The individuals and any bounded group are not identified in this passage."
    contact["qualifiers"]["relation_candidate_note"] = RELATION_NOTES[contact["statement_id"]]

    jansenism = statement_by_id["st-chp4-sec-ii-l101-107-jansenism-possible-interpretation"]
    jansenism["original_quote"] = "Jansenism?"
    jansenism["predicate"] = "raises_possible_jansenist_interpretation_of_poussins_views"
    jansenism["qualifiers"]["claim"] = "Haskell raises Jansenism as one possible interpretation of Poussin's religious views."
    jansenism["qualifiers"]["qualification"] = "The source poses this as a question and adds 'Possibly'; it does not assert an affiliation."

    precedent = statement_by_id["st-chp4-sec-ii-l101-107-italian-sacrament-series-precedents"]
    precedent["object_candidate_id"] = NEW_CANDIDATE_ID
    precedent["predicate"] = "has_precedent_in_italian_sacrament_fresco_series"
    precedent["original_quote"] = "in Italy the Sacraments had only once been painted as a series—in some frescoes ascribed to Roberto Oderisi in fourteenth-century Naples."
    precedent["qualifiers"]["claim"] = "Haskell identifies an earlier Italian Sacrament series in frescoes ascribed to Roberto Oderisi in fourteenth-century Naples."
    precedent["qualifiers"]["qualification"] = "The earlier cycle is not identified beyond the source wording; the 'ascribed to' attribution remains attributed, and the cycle is distinct from Poussin's."
    append_mentioned_ids(precedent, NEW_CANDIDATE_ID, "cand-1767", "cand-3534")

    jottings = statement_by_id["st-chp4-sec-ii-l101-107-jottings-decorum-and-church-misbehaviour"]
    jottings["object_candidate_id"] = "cand-5810"
    jottings["predicate"] = "jottings_report_cassianos_emphasis_on_decorum_and_distaste"
    append_mentioned_ids(jottings, "cand-5810", "cand-0419")

    iconography = statement_by_id["st-chp4-sec-ii-l101-107-poussin-iconography-new"]
    iconography["subject_candidate_id"] = "cand-5789"
    iconography["object_candidate_id"] = None
    iconography["predicate"] = "author_assesses_series_iconography_as_new"
    append_mentioned_ids(iconography, "cand-1984", "cand-5789")

    general_subject = statement_by_id["st-chp4-sec-ii-l101-107-seven-sacraments-general-subject"]
    general_subject["subject_candidate_id"] = "cand-5789"
    general_subject["object_candidate_id"] = None
    general_subject["predicate"] = "author_assesses_subject_and_treatment_as_revolutionary"
    append_mentioned_ids(general_subject, "cand-1984", "cand-5789")

    additions = [
        statement(
            "st-chp4-sec-ii-l101-107-possible-echoes-in-other-works",
            "cand-2036", None,
            "author_considers_possible_echoes_of_cassianos_ideas_in_other_works",
            "we can perhaps trace echoes of his ideas in other works apart from those he ordered for himself.",
            "Haskell suggests that echoes of Cassiano's ideas may be traced in works beyond those he commissioned for himself.",
            "The claim is expressly tentative and no target work is named; the endpoint remains open.",
            ["cand-2036"],
            line=105,
            is_relation=True,
            relation_note="This is Haskell's tentative influence hypothesis; no target work is identified, so the endpoint remains open.",
            text_layer="authorial hypothesis",
        ),
        statement(
            "st-chp4-sec-ii-l101-107-possible-schismatic-sect",
            "cand-1984", None,
            "raises_possible_affiliation_with_unspecified_schismatic_sect",
            "Some schismatic sect? Possibly.",
            "Haskell raises an unspecified schismatic sect as an alternative possible interpretation of Poussin's religious views.",
            "The sect is unnamed and the statement remains a possibility, not an affiliation claim.",
            ["cand-1984"],
            line=104,
            is_relation=True,
            relation_note="This is a possible interpretive link only; the sect is not named and no affiliation is asserted.",
            text_layer="authorial hypothesis",
            footnote_source={
                "footnote_marker": 1,
                "footnote_segment": "chp-4:04_CHP-4_sec_ii:l232-308",
                "footnote_source_line": 260,
                "footnote_link_status": "linked",
                "footnote_statement_id": "st-chp4-sec-ii-notes-l260-264-fn260-blunt",
            },
        ),
        statement(
            "st-chp4-sec-ii-l101-107-medieval-northern-precedents",
            "cand-5789", None,
            "author_reports_medieval_sculptural_and_rare_northern_precedents",
            "There are mediaeval precedents in sculpture, and veryrare examples in Northern painting",
            "Haskell notes medieval sculptural precedents and very rare examples in Northern painting before identifying the Italian fresco series.",
            "The source does not identify the individual sculptures or Northern paintings; this remains a contextual, scalar statement.",
            ["cand-5789"],
            line=102,
            is_relation=False,
            relation_note="This records broad historical context without an identified work or artist endpoint.",
            ocr_corrections=[{"source_line": 102, "source_form": "veryrare", "print_form": "very rare"}],
        ),
        statement(
            "st-chp4-sec-ii-l101-107-oderisi-frescoes-ascribed",
            NEW_CANDIDATE_ID, "cand-1767",
            "ascribed_to",
            "some frescoes ascribed to Roberto Oderisi in fourteenth-century Naples",
            "Haskell says the earlier Sacrament frescoes were ascribed to Roberto Oderisi.",
            "This preserves Haskell's attribution wording only; the fresco cycle and attribution are not independently verified.",
            [NEW_CANDIDATE_ID, "cand-1767", "cand-3534"],
            line=102,
            is_relation=True,
            relation_note="Source attribution only: the frescoes are 'ascribed to' Oderisi; this is not independent authorship verification.",
        ),
    ]
    if {row["statement_id"] for row in additions} != NEW_STATEMENT_IDS:
        raise SystemExit("preflight failed: new statement set differs from the declared change set")
    for row in additions:
        if row["original_quote"] not in segment_text:
            raise SystemExit(f"preflight failed: quote is outside source segment: {row['statement_id']}")
    statements.extend(additions)

    candidate_ids = set(candidate_by_id) | {NEW_CANDIDATE_ID}
    for row in statements:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"preflight failed: missing p.107 endpoint {endpoint}")
    segment_after = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    dual_after = [row for row in segment_after if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    segment_counts = {
        "statements": len(segment_after),
        "dual": len(dual_after),
        "true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_after),
        "false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment_after),
        "dual_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual_after),
        "dual_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual_after),
        "unclassified": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in segment_after),
    }
    expected_segment_counts = {
        "statements": 24, "dual": 13, "true": 14, "false": 10,
        "dual_true": 11, "dual_false": 2, "unclassified": 0,
    }
    if segment_counts != expected_segment_counts:
        raise SystemExit(f"preflight failed: unexpected p.107 result: {segment_counts}")
    if any(row.get("qualifiers", {}).get("relation_candidate") not in (True, False) for row in segment_after):
        raise SystemExit("preflight failed: p.107 relation classification is incomplete")
    mention_errors = [
        row["mention_id"] for row in mentions
        if row["segment_id"] == SEGMENT_ID
        and segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]
    ]
    if mention_errors or segment_text[new_start:new_end] != new_surface:
        raise SystemExit(f"preflight failed: p.107 mention span errors: {mention_errors}")

    relation_totals = {
        "all_statements": len(statements),
        "all_candidates": len(candidates),
        "all_mentions": len(mentions),
        "dual_statements": sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in statements),
        "dual_true": sum(
            bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
            and (row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements
        ),
        "dual_false": sum(
            bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
            and (row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements
        ),
        "dual_unclassified": sum(
            bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
            and (row.get("qualifiers") or {}).get("relation_candidate") is None for row in statements
        ),
        "relation_true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements),
        "relation_true_open": sum(
            (row.get("qualifiers") or {}).get("relation_candidate") is True
            and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
            for row in statements
        ),
    }
    expected_totals = {
        "all_statements": 12987, "all_candidates": 11626, "all_mentions": 27564,
        "dual_statements": 8800, "dual_true": 5635, "dual_false": 515,
        "dual_unclassified": 2650, "relation_true": 5696, "relation_true_open": 61,
    }
    if relation_totals != expected_totals:
        raise SystemExit(f"preflight failed: unexpected global totals: {relation_totals}")

    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "table_sha256_before": EXPECTED_SHA256,
        "existing_statements_reviewed": len(ORIGINAL_IDS),
        "new_candidate": NEW_CANDIDATE_ID,
        "new_mention": {"id": NEW_MENTION_ID, "surface": new_surface, "span": [new_start, new_end]},
        "new_statements": sorted(NEW_STATEMENT_IDS),
        "segment_after": segment_counts,
        "global_after": relation_totals,
        "ocr_correction": {"source_line": 102, "source_form": "veryrare", "print_form": "very rare"},
        "backups": [f"{name}.{BACKUP_SUFFIX}" for name in paths],
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = [paths[name].with_name(paths[name].name + "." + BACKUP_SUFFIX) for name in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("apply refused: a recovery backup with this suffix already exists")
    for source_path, backup_path in zip(paths.values(), backups):
        shutil.copy2(source_path, backup_path)
    write_csv(paths["entity-candidates.csv"], candidates, candidate_fields)
    write_csv(paths["mentions.csv"], mentions, mention_fields)
    write_jsonl(paths["book-statements.jsonl"], statements)

    written_statements = read_jsonl(paths["book-statements.jsonl"])
    written_candidates, _ = read_csv(paths["entity-candidates.csv"])
    written_mentions, _ = read_csv(paths["mentions.csv"])
    written_segment = [row for row in written_statements if row.get("segment_id") == SEGMENT_ID]
    if len(written_segment) != 24 or any(
        (row.get("qualifiers") or {}).get("relation_candidate") not in (True, False)
        for row in written_segment
    ):
        raise SystemExit("post-write verification failed: p.107 classification is incomplete; backups retained")
    if NEW_CANDIDATE_ID not in {row["candidate_id"] for row in written_candidates}:
        raise SystemExit("post-write verification failed: new work candidate is missing; backups retained")
    new_written_mention = next((row for row in written_mentions if row["mention_id"] == NEW_MENTION_ID), None)
    if not new_written_mention or new_written_mention["candidate_id"] != NEW_CANDIDATE_ID:
        raise SystemExit("post-write verification failed: work mention is missing or mis-mapped; backups retained")
    print("apply complete")
    for name, path in paths.items():
        print(f"{name}_sha256={sha(path.read_bytes())}")
    print("backups=" + ",".join(path.name for path in backups))


if __name__ == "__main__":
    main()
