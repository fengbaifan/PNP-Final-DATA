#!/usr/bin/env python3
"""Controlled S2 relation review for Chapter 3, section IV, lines 96-104.

Default mode is dry-run. --apply writes only after source/table/hash preflight.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l96-104"
SOURCE_SHA256 = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA256 = "c283eee6bcdc66e73eda228b1b020385823b9a8d369948e3914658c32b9a7d31"
EXPECTED_FILE_SHA256 = {
    STATEMENTS: "5330d661d86a72b4711277995304f94c4c1826c8efb960490a92e9a8b8e7b58e",
    CANDIDATES: "a1debcdd198d742a72438bd5167694468853e19ca692ead9beb182f94e9359be",
    MENTIONS: "8587fbb5efe60b6a03f1b3c32e0b6e249f00286d4412bce6227ddbb092894831",
}

EXISTING_STATEMENT_IDS = {
    "st-chp3-seciv-l96-104-alexander-approved-after-view-review",
    "st-chp3-seciv-l96-104-bandino-refused-land-sale",
    "st-chp3-seciv-l96-104-bernini-began-s-andrea-1658",
    "st-chp3-seciv-l96-104-bernini-consolation-quote",
    "st-chp3-seciv-l96-104-bernini-france-jesuit-links",
    "st-chp3-seciv-l96-104-bernini-pleased-discovered-by-son",
    "st-chp3-seciv-l96-104-camillo-declared-rivalry-ambition",
    "st-chp3-seciv-l96-104-camillo-fulfilled-intentions",
    "st-chp3-seciv-l96-104-camillo-largest-sum-and-patronage",
    "st-chp3-seciv-l96-104-camillo-nephew-of-innocent-x",
    "st-chp3-seciv-l96-104-camillo-son-followed-example",
    "st-chp3-seciv-l96-104-ceva-chose-borromini",
    "st-chp3-seciv-l96-104-fewer-financial-troubles",
    "st-chp3-seciv-l96-104-historians-jesuit-ideals",
    "st-chp3-seciv-l96-104-innocent-forbade-borromini-drawings",
    "st-chp3-seciv-l96-104-interdiction-remained-after-land-acquired",
    "st-chp3-seciv-l96-104-jesuits-increased-power-numbers",
    "st-chp3-seciv-l96-104-ludovisi-s-ignazio-site",
    "st-chp3-seciv-l96-104-ludovisi-s-ignazio-stopped",
    "st-chp3-seciv-l96-104-old-novitiate-unusable-1642",
    "st-chp3-seciv-l96-104-oliva-spiritual-understanding",
    "st-chp3-seciv-l96-104-pope-obstructed-view-objection",
    "st-chp3-seciv-l96-104-rector-appealed-to-alexander",
    "st-chp3-seciv-l96-104-s-andrea-ranked-among-finest",
}

NEW_CANDIDATE = {
    "candidate_id": "cand-11616",
    "canonical_name": "Unidentified entourage of Alexander VII encouraged to contribute to the S. Andrea project",
    "suggested_type": "",
    "candidate_source_ref": SEGMENT_ID + "#L101",
    "detail": "Haskell says Alexander VII encouraged his entourage to contribute toward the project expense. Members, number, and actual contributions are not given; do not infer that the group donated.",
}
NEW_MENTION_ID = "m-chp3-seciv-l96-104-0049"
NEW_STATEMENT_IDS = {
    "st-chp3-seciv-l96-104-alexander-encouraged-entourage",
    "st-chp3-seciv-l96-104-bernini-consolation-visit",
    "st-chp3-seciv-l96-104-bernini-greatest-opportunity",
    "st-chp3-seciv-l96-104-bernini-jesuit-sympathy",
    "st-chp3-seciv-l96-104-camillo-assumed-patronage",
    "st-chp3-seciv-l96-104-ceva-agreed-to-build",
    "st-chp3-seciv-l96-104-drawings-made",
    "st-chp3-seciv-l96-104-rector-close-friend",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("PREFLIGHT FAILED: " + message)


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    ids = [row["statement_id"] for row in rows]
    require(len(ids) == len(set(ids)), f"duplicate statement_id in {path.name}")
    return rows


def load_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def quote(text: str, phrase: str) -> str:
    start = text.find(phrase)
    require(start >= 0, f"source phrase not found: {phrase!r}")
    require(text.find(phrase, start + 1) < 0, f"source phrase is ambiguous: {phrase!r}")
    return text[start:start + len(phrase)]


def new_statement(
    statement_id: str,
    subject: str,
    predicate: str,
    obj: str | None,
    source_line_start: int,
    source_line_end: int,
    claim: str,
    source_quote: str,
    qualification: str,
    relation_candidate: bool,
    relation_candidate_note: str,
    **extra_qualifiers: object,
) -> dict:
    qualifiers: dict[str, object] = {
        "source_line_start": source_line_start,
        "source_line_end": source_line_end,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "print_page": 86,
        "pdf_physical_page": 28,
        "qualification": qualification,
        "relation_candidate": relation_candidate,
        "relation_candidate_note": relation_candidate_note,
    }
    qualifiers.update(extra_qualifiers)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": source_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted changes")
    args = parser.parse_args()

    require(digest(SOURCE) == SOURCE_SHA256, "source file SHA-256 changed")
    for path, expected in EXPECTED_FILE_SHA256.items():
        require(digest(path) == expected, f"{path.name} SHA-256 changed")

    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment_matches = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    require(len(segment_matches) == 1, "expected one S0 segment")
    require(segment_matches[0].get("sha256") == SEGMENT_SHA256, "S0 segment hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[95:104])
    require(hashlib.sha256(text.encode("utf-8")).hexdigest() == SEGMENT_SHA256,
            "reconstructed segment text hash mismatch")
    require(len(text) == 2989, "unexpected reconstructed segment length")
    require(text[2331:2348] == "all his entourage", "planned group mention span mismatch")

    statement_rows = load_jsonl(STATEMENTS)
    candidate_fields, candidate_rows = load_csv(CANDIDATES)
    mention_fields, mention_rows = load_csv(MENTIONS)
    segment_statements = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    require({row["statement_id"] for row in segment_statements} == EXISTING_STATEMENT_IDS,
            "segment statement set changed")
    require(len(segment_statements) == 24, "expected 24 existing statements")
    require(all("relation_candidate" not in row.get("qualifiers", {}) for row in segment_statements),
            "a segment statement was already classified")
    require(not (NEW_STATEMENT_IDS & {row["statement_id"] for row in statement_rows}),
            "a planned statement ID already exists")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    require(max(int(cid[5:]) for cid in candidate_by_id) == 11615, "candidate high-water mark changed")
    require(NEW_CANDIDATE["candidate_id"] not in candidate_by_id, "planned candidate ID already exists")
    require(candidate_by_id["cand-2889"]["status"] == "excluded"
            and "cand-0665" in candidate_by_id["cand-2889"]["exclude_reason"],
            "Alexander VII index cross-reference changed")
    require(candidate_by_id["cand-0665"]["status"] == "open"
            and "Pope Alexander VII" in candidate_by_id["cand-0665"]["canonical_name"],
            "Alexander VII target candidate changed")
    require(candidate_by_id["cand-2911"]["status"] == "excluded"
            and "Pamfili, Giambattista" in candidate_by_id["cand-2911"]["exclude_reason"],
            "Innocent X index cross-reference changed")
    require(candidate_by_id["cand-1819"]["status"] == "open"
            and "Pope Innocent X" in candidate_by_id["cand-1819"]["canonical_name"],
            "Innocent X target candidate changed")
    require(candidate_by_id["cand-5321"]["status"] == "open", "drawings candidate is not open")

    mention_ids = {row["mention_id"] for row in mention_rows}
    require(NEW_MENTION_ID not in mention_ids, "planned mention ID already exists")
    existing_segment_mentions = [row for row in mention_rows if row.get("segment_id") == SEGMENT_ID]
    require(len(existing_segment_mentions) == 48, "unexpected segment mention count")
    require(max(int(row["mention_id"].rsplit("-", 1)[1]) for row in existing_segment_mentions) == 48,
            "segment mention high-water mark changed")
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    alias_remap = {
        "m-chp3-seciv-l96-104-0038": ("cand-2889", "cand-0665"),
        "m-chp3-seciv-l96-104-0039": ("cand-2889", "cand-0665"),
        "m-chp3-seciv-l96-104-0040": ("cand-2889", "cand-0665"),
        "m-chp3-seciv-l96-104-0036": ("cand-2911", "cand-1819"),
        "m-chp3-seciv-l96-104-0042": ("cand-2911", "cand-1819"),
    }
    for mention_id, (old, new) in alias_remap.items():
        require(mention_by_id[mention_id]["candidate_id"] == old,
                f"unexpected candidate mapping for {mention_id}")
        mention_by_id[mention_id]["candidate_id"] = new

    by_id = {row["statement_id"]: row for row in statement_rows}

    def change(
        statement_id: str,
        *,
        subject: str | None = None,
        obj: str | None = None,
        predicate: str | None = None,
        claim: str | None = None,
        source_quote: str | None = None,
        qualification: str | None = None,
        **qualifier_updates: object,
    ) -> dict:
        row = by_id[statement_id]
        if subject is not None:
            row["subject_candidate_id"] = subject
        if obj is not None:
            row["object_candidate_id"] = obj
        if predicate is not None:
            row["predicate"] = predicate
        q = row.setdefault("qualifiers", {})
        if claim is not None:
            q["claim"] = claim
        if qualification is not None:
            q["qualification"] = qualification
        q.update(qualifier_updates)
        if source_quote is not None:
            row["original_quote"] = source_quote
        return row

    # Keep each statement on one source-supported proposition and use active index targets.
    change(
        "st-chp3-seciv-l96-104-alexander-approved-after-view-review",
        subject="cand-5322",
        obj="cand-5309",
        predicate="rector_succeeded_in_appeal_for_rebuilding_after_papal_view_review",
        claim="Haskell says the novitiate Rector’s appeal for the rebuilding succeeded after the Pope confirmed that the project would not obstruct the view from his palace.",
        source_quote=quote(text, "This time he was successful, and after the Pope had satisfied himself that his view would not be disturbed"),
        qualification="The grammatical subject of “he was successful” is the unnamed Rector. Alexander VII is the reviewing authority named in the preceding clause; the source does not identify a separate permit document.",
        authority_candidate_id="cand-0665",
        relation_candidate_note="The claim links the unnamed Rector’s appeal to the rebuilding project; the Pope’s view review is qualifying context. It remains an S2 candidate, not an S6 edge.",
    )
    change(
        "st-chp3-seciv-l96-104-bandino-refused-land-sale",
        claim="Haskell identifies Cardinal Bandino’s refusal to sell his surrounding land as one of two obstacles to rebuilding or expanding the novitiate.",
        qualification="The source does not specify the parcel boundaries or identify who later acquired the property.",
        relation_candidate_note="The source directly states Bandino’s refusal concerning land surrounding the novitiate; the parcel remains a distinct open candidate.",
    )
    change(
        "st-chp3-seciv-l96-104-bernini-began-s-andrea-1658",
        claim="Haskell says Bernini began building the S. Andrea novitiate church in 1658.",
        source_quote=quote(text, "In the novitiate church of S. Andrea which he began to build in\n1658"),
        qualification="The sentence’s separate assessment of this as Bernini’s greatest opportunity to fulfil Jesuit ideals is recorded in its own statement.",
        event_candidate_id="cand-5309",
        relation_candidate_note="The statement records Bernini’s building relation to S. Andrea; the source does not give a completion date.",
    )
    bernini_quote = change(
        "st-chp3-seciv-l96-104-bernini-consolation-quote",
        predicate="expressed_special_satisfaction_with_s_andrea_architecture",
        claim="Bernini says this is the only piece of his architecture for which he feels special satisfaction.",
        source_quote=quote(text, "My son, this is the only piece of my architecture for which I feel special satisfaction in the depth of my heart"),
        qualification="Retain Bernini’s reported first-person assessment. Printed note 2 is linked as a source locator; its cited work was not independently consulted.",
        event_candidate_id="cand-5309",
        relation_candidate_note="Bernini’s reported assessment directly concerns his architectural work; it is a source-bounded artist–work relation, not independent evaluation.",
    )
    change(
        "st-chp3-seciv-l96-104-bernini-france-jesuit-links",
        predicate="visited_jesuit_churches_in_france",
        claim="Haskell says Bernini often visited Jesuit churches in France.",
        source_quote=quote(text, "In France he often visited Jesuit churches"),
        qualification="Haskell introduces this as an example of Bernini’s relationship with the Jesuit Society; no individual church is identified.",
        location_candidate_id="cand-5317",
        relation_candidate_note="The source explicitly frames the visits as part of Bernini’s relationship with the Jesuit Society; France is location context.",
    )
    change(
        "st-chp3-seciv-l96-104-bernini-pleased-discovered-by-son",
        subject="cand-5313",
        obj="cand-0298",
        predicate="discovered_bernini_in_s_andrea",
        claim="Haskell says Bernini’s son, identified as Domenico in the preceding sentence, discovered him in a corner of S. Andrea years later.",
        source_quote=quote(text, "when many years later he was discovered by his own son in a corner of the church"),
        qualification="The local antecedent identifies the son as Domenico; no date for the discovery is supplied. The church is the location context.",
        location_candidate_id="cand-0694",
        relation_candidate_note="This records the stated discovery by Bernini’s son; the unnamed event date and the church location remain context.",
    )
    change(
        "st-chp3-seciv-l96-104-camillo-declared-rivalry-ambition",
        qualification="This is Camillo’s stated ambition for the project, not evidence that it achieved the proposed comparison.",
        project_candidate_id="cand-5309",
        relation_candidate_note="The passage directly records a patron’s intention concerning the S. Andrea project; the comparison buildings are not individually identified.",
    )
    change(
        "st-chp3-seciv-l96-104-camillo-fulfilled-intentions",
        project_candidate_id="cand-5309",
        relation_candidate_note="Haskell reports Camillo carrying out his intentions for the project through his death in 1665; the separate clause about his son is recorded separately.",
    )
    change(
        "st-chp3-seciv-l96-104-camillo-largest-sum-and-patronage",
        predicate="gave_largest_sum_to_rebuilding_project",
        claim="Haskell says Prince Camillo Pamfili gave by far the largest sum toward the S. Andrea rebuilding project.",
        source_quote=quote(text, "By far the largest sum was given by Prince Camillo Pamfili"),
        qualification="The amount is not stated. Camillo’s assumption of patronage for himself and his family is recorded separately.",
        project_candidate_id="cand-5309",
        relation_candidate_note="The statement records a source-supported contribution to the rebuilding project; it does not infer an amount.",
    )
    change(
        "st-chp3-seciv-l96-104-camillo-nephew-of-innocent-x",
        obj="cand-1819",
        claim="Haskell identifies Prince Camillo Pamfili as the nephew of Pope Innocent X.",
        qualification="The Innocent X mention is mapped through the index cross-reference to the active Pamfili candidate.",
        relation_candidate_note="The passage directly states this kinship; the excluded index cross-reference is redirected to its named Pamfili target.",
    )
    change(
        "st-chp3-seciv-l96-104-camillo-son-followed-example",
        project_candidate_id="cand-5309",
        relation_candidate_note="Haskell says Camillo’s unnamed son continued his father’s patronage example; the son remains unidentified.",
    )
    change(
        "st-chp3-seciv-l96-104-ceva-chose-borromini",
        predicate="selected_borromini_for_proposed_church_and_lodgings",
        claim="Haskell says Cardinal Ceva chose Borromini for the proposed new church and lodgings.",
        source_quote=quote(text, "he chose for the purpose Borromini"),
        qualification="The selection does not establish that Borromini’s drawings were executed. Printed note 5 is linked as a source locator, not independent verification.",
        project_candidate_id="cand-5309",
        relation_candidate_note="This is Ceva’s explicit architect selection for the proposed project; the selection is distinct from his agreement to build.",
    )
    change(
        "st-chp3-seciv-l96-104-fewer-financial-troubles",
        claim="Haskell says fewer financial troubles were reported for S. Andrea than for the other churches previously considered.",
        qualification="Comparative authorial assessment of the project’s financial history; the comparison set is not individually enumerated.",
        relation_candidate_note="This is a comparative scalar assessment of the project, not a directed relation between two identified entities.",
    )
    change(
        "st-chp3-seciv-l96-104-historians-jesuit-ideals",
        qualification="Preserve Haskell’s report of modern historians’ interpretation and the wording “seems”; no independent historian or artwork is identified here.",
        relation_candidate_note="The reported interpretation connects Bernini’s work with Jesuit ideals; its attribution and uncertainty remain explicit.",
    )
    change(
        "st-chp3-seciv-l96-104-innocent-forbade-borromini-drawings",
        subject="cand-1819",
        predicate="forbade_execution_of_proposed_drawings",
        claim="Haskell says Innocent X forbade execution of the proposed drawings for the church and lodgings.",
        source_quote=quote(text, "The drawings were made, but Innocent\nX forbade their being executed"),
        qualification="The drawings’ authorship is not explicit in this sentence; completion and survival are not established.",
        relation_candidate_note="The source directly records Innocent X’s prohibition concerning the proposed drawings; the work remains distinct from the rebuilding project.",
    )
    change(
        "st-chp3-seciv-l96-104-interdiction-remained-after-land-acquired",
        claim="Haskell says the papal interdiction remained strictly enforced even after the Bandino property had been acquired.",
        qualification="The Pope remains unidentified; the property, view, and proposed rebuilding are not collapsed into a single place candidate.",
        relation_candidate_note="The source records continued enforcement of a papal restriction over the site after the property acquisition; the issuing Pope is not identified.",
    )
    change(
        "st-chp3-seciv-l96-104-jesuits-increased-power-numbers",
        qualification="Scalar description of institutional growth in Haskell’s narrative; no separate institution-to-object relation is asserted.",
        relation_candidate_note="This is a scalar change in the Jesuits’ power and numbers, not a relation between two entities.",
    )
    change(
        "st-chp3-seciv-l96-104-ludovisi-s-ignazio-site",
        qualification="The site is a source-bounded open candidate; the text does not establish its precise location or identity with the Bandino property.",
        relation_candidate_note="The source states Ludovisi’s intention to found S. Ignazio at an unspecified site; the site remains distinct from nearby properties.",
    )
    change(
        "st-chp3-seciv-l96-104-ludovisi-s-ignazio-stopped",
        qualification="The Pope is unidentified; the site is not resolved to the Quirinal novitiate or Bandino property.",
        relation_candidate_note="Haskell directly links the unnamed Pope’s view objection to stopping Ludovisi’s proposed foundation; no identity or site merger is inferred.",
    )
    change(
        "st-chp3-seciv-l96-104-old-novitiate-unusable-1642",
        qualification="This is the Jesuits’ reported claim about the old building’s condition. Printed note 3 is linked as a source locator; the archival file was not independently consulted.",
        reported_claimant_candidate_id="cand-3403",
        relation_candidate_note="The Jesuits are the claimants and the old novitiate is the subject of their reported condition claim; these endpoints do not establish a direct Jesuit–building relation.",
    )
    change(
        "st-chp3-seciv-l96-104-oliva-spiritual-understanding",
        qualification="Haskell attributes this assessment to Oliva; note 1 is linked as a source locator, not independent verification.",
        relation_candidate_note="Oliva is the reporter and Bernini is the subject of an assessment of his understanding; the endpoints do not state a direct historical relation.",
    )
    change(
        "st-chp3-seciv-l96-104-pope-obstructed-view-objection",
        obj="cand-5309",
        claim="Haskell identifies the unnamed Pope’s objection to obstruction of the view from his palace as an obstacle to rebuilding or expansion.",
        qualification="The Pope and palace remain unidentified. The palace is the view context; the proposed rebuilding is the object of the objection.",
        palace_candidate_id="cand-5319",
        relation_candidate_note="The objection concerns the proposed rebuilding project; the palace supplies the protected-view context, not the relation endpoint.",
    )
    change(
        "st-chp3-seciv-l96-104-rector-appealed-to-alexander",
        obj="cand-0665",
        claim="Haskell says the unidentified Rector appealed again to Alexander VII concerning the novitiate project.",
        source_quote=quote(text, "the Rector of the novitiate appealed once again to the new Pope, Alexander VII"),
        qualification="The Rector is unnamed. Alexander VII is mapped through the index cross-reference to the active Fabio Chigi candidate; the appeal’s success is recorded separately.",
        relation_candidate_note="The source explicitly records an appeal from the novitiate Rector to Alexander VII; the Rector’s identity remains open.",
    )
    change(
        "st-chp3-seciv-l96-104-s-andrea-ranked-among-finest",
        claim="Haskell says S. Andrea was already considered one of the finest buildings in Rome.",
        qualification="This is an evaluative reputation claim; Rome is the comparison scope, not a separate participant in a relation.",
        relation_candidate_note="The statement evaluates the building’s standing within Rome; the city supplies comparison context rather than a directed entity relation.",
    )

    # The index aliases are explicit cross-references, not relation endpoints.
    by_id["st-chp3-seciv-l96-104-bernini-consolation-quote"]["qualifiers"]["footnote_pending"] = False
    for mention_id, note in {
        "m-chp3-seciv-l96-104-0012": "The preceding sentence identifies Domenico as Bernini’s son; this occurrence is read in that local context. Note 2 is linked as a locator for Bernini’s reported saying; its source was not independently consulted.",
        "m-chp3-seciv-l96-104-0013": "Bernini’s quoted address to his son. Note 2 is linked as a locator for the reported saying; its source was not independently consulted.",
    }.items():
        require(mention_by_id[mention_id]["note"].endswith("footnote 2 remains pending."),
                f"stale note text changed for {mention_id}")
        mention_by_id[mention_id]["note"] = note

    # Refresh the existing drawing candidate name so it does not claim an unstated draftsman.
    candidate_by_id["cand-5321"]["canonical_name"] = (
        "Drawings for Cardinal Ceva’s proposed church and lodgings at the Jesuit novitiate"
    )
    candidate_by_id["cand-5321"]["detail"] = (
        "Haskell says the drawings were made after Cardinal Ceva selected Borromini and that Innocent X "
        "forbade their execution. The passage does not explicitly identify the draftsman; completion and "
        "survival are not established."
    )
    candidate_by_id["cand-5313"]["detail"] = (
        "Haskell identifies Domenico as Bernini’s son and attributes the weekly-visit claim to him. The "
        "following phrase “his own son” is read as the same local antecedent; no surname is supplied."
    )
    candidate_by_id["cand-5322"]["detail"] = (
        "The Rector appealed to Alexander VII and is described as the Pope’s close friend. Haskell does "
        "not give the Rector’s name."
    )

    # Classify every existing statement after the proposition-level revisions.
    relation_ids = EXISTING_STATEMENT_IDS - {
        "st-chp3-seciv-l96-104-fewer-financial-troubles",
        "st-chp3-seciv-l96-104-jesuits-increased-power-numbers",
        "st-chp3-seciv-l96-104-old-novitiate-unusable-1642",
        "st-chp3-seciv-l96-104-oliva-spiritual-understanding",
        "st-chp3-seciv-l96-104-s-andrea-ranked-among-finest",
    }
    default_relation_note = (
        "The statement expresses a source-bounded relation between its recorded endpoints; "
        "it remains an S2 candidate and does not create an S6 edge."
    )
    false_notes = {
        "st-chp3-seciv-l96-104-fewer-financial-troubles":
            "This is a comparative scalar assessment of the project, not a directed relation between two identified entities.",
        "st-chp3-seciv-l96-104-jesuits-increased-power-numbers":
            "This is a scalar change in the Jesuits’ power and numbers, not a relation between two entities.",
        "st-chp3-seciv-l96-104-old-novitiate-unusable-1642":
            "The Jesuits are the claimants and the old novitiate is the subject of their reported condition claim; these endpoints do not establish a direct Jesuit–building relation.",
        "st-chp3-seciv-l96-104-oliva-spiritual-understanding":
            "Oliva is the reporter and Bernini is the subject of an assessment of his understanding; the endpoints do not state a direct historical relation.",
        "st-chp3-seciv-l96-104-s-andrea-ranked-among-finest":
            "The statement evaluates the building’s standing within Rome; the city supplies comparison context rather than a directed entity relation.",
    }
    for statement_id in EXISTING_STATEMENT_IDS:
        q = by_id[statement_id].setdefault("qualifiers", {})
        q["relation_candidate"] = statement_id in relation_ids
        if not q.get("relation_candidate_note"):
            q["relation_candidate_note"] = (
                false_notes[statement_id] if statement_id in false_notes else default_relation_note
            )

    new_statements = [
        new_statement(
            "st-chp3-seciv-l96-104-alexander-encouraged-entourage",
            "cand-0665", "encouraged_to_contribute_toward_project_expense", "cand-11616",
            101, 101,
            "Haskell says Alexander VII encouraged his entourage to contribute toward the S. Andrea project expense.",
            quote(text, "he strongly encouraged all his entourage to contribute towards the expense"),
            "The group’s members and number are unspecified; encouragement does not establish that anyone contributed.",
            True,
            "The source names Alexander VII and his entourage as the participants in an encouragement relation; the rebuilding project is context, and actual contributions are not asserted.",
            project_candidate_id="cand-5309",
        ),
        new_statement(
            "st-chp3-seciv-l96-104-bernini-consolation-visit",
            "cand-0298", "returned_to_s_andrea_for_consolation_from_work", "cand-0694",
            98, 98,
            "Bernini says he often came to the church to gain consolation from his work.",
            quote(text, "often when I need rest from my troubles I come here to gain consolation from my work."),
            "The quotation gives no dates or count for these visits. Printed note 2 is a locator and was not independently consulted.",
            True,
            "Bernini’s reported visits directly connect him with S. Andrea; no particular visit or external verification is inferred.",
            speaker="Bernini",
            text_layer="quoted first-person statement relayed by Haskell",
            event_candidate_id="cand-5309",
        ),
        new_statement(
            "st-chp3-seciv-l96-104-bernini-greatest-opportunity",
            "cand-0298", "had_greatest_opportunity_to_fulfil_jesuit_ideals_at", "cand-5309",
            98, 98,
            "Haskell says the S. Andrea project gave Bernini his greatest opportunity to fulfil Jesuit ideals.",
            quote(text, "he had his greatest opportunity of doing so."),
            "This is Haskell’s interpretation of the project’s importance to Bernini; it does not establish that every element fulfilled Jesuit ideals.",
            True,
            "The passage directly links Bernini’s opportunity to the S. Andrea project; the interpretation remains attributed to Haskell.",
            institution_candidate_id="cand-3403",
        ),
        new_statement(
            "st-chp3-seciv-l96-104-bernini-jesuit-sympathy",
            "cand-0298", "expressed_sympathy_with_jesuit_ideas", "cand-3403",
            97, 97,
            "Haskell says Bernini spoke much of his sympathy with Jesuit ideas.",
            quote(text, "talked much of his sympathy with Jesuit ideas."),
            "This records Haskell’s account of Bernini’s expressed affinity; it does not establish a formal Jesuit role or membership.",
            True,
            "The source explicitly presents this as part of Bernini’s relationship with the Society; the ideas are kept within the Jesuit institutional context.",
        ),
        new_statement(
            "st-chp3-seciv-l96-104-camillo-assumed-patronage",
            "cand-1814", "assumed_patronage_of_project_for_himself_and_family", "cand-5309",
            103, 103,
            "Haskell says Camillo assumed patronage of the church for himself and his family.",
            quote(text, "who assumed the patronage for himself and his family."),
            "The family is a beneficiary group named collectively; this does not establish that it independently undertook the act.",
            True,
            "The source states Camillo’s patronage of the project and names his family as beneficiaries; their role is not converted into an independent act.",
            beneficiary_group_candidate_id="cand-3456",
        ),
        new_statement(
            "st-chp3-seciv-l96-104-ceva-agreed-to-build",
            "cand-0642", "agreed_to_build_new_church_and_lodgings", "cand-5309",
            100, 100,
            "Haskell says Cardinal Ceva agreed in 1649 to build a new church and lodgings.",
            quote(text, "In 1649 Cardinal Ceva agreed to build a new church and lodgings"),
            "Agreement is not evidence that the project was carried out. Printed note 5 is linked as a source locator, not independent verification.",
            True,
            "The source records Ceva’s agreement to build the project; architect selection is recorded separately.",
            footnote_markers=[5],
            footnote_source_lines=[221],
            footnote_segment_id="chp-3:03_CHP-3_sec_iv:l189-243",
            footnote_pending=False,
            footnote_statement_ids=["st-chp3-seciv-notes-l205-243-p86-n5-86518"],
        ),
        new_statement(
            "st-chp3-seciv-l96-104-drawings-made",
            "cand-5321", "drawings_were_made_for_proposed_project", None,
            100, 100,
            "Haskell says drawings for the proposed church and lodgings had been made.",
            quote(text, "The drawings were made"),
            "The passage does not identify the draftsman; the drawing candidate is not treated as a completed building or executed design.",
            False,
            "This records the work candidate’s reported state, not a directed relationship between two entities.",
        ),
        new_statement(
            "st-chp3-seciv-l96-104-rector-close-friend",
            "cand-5322", "was_close_friend_of", "cand-0665",
            101, 101,
            "Haskell says Alexander VII was a close friend of the novitiate’s Rector.",
            quote(text, "Alexander VII, whose close friend he was"),
            "The Rector is unnamed; “he” refers locally to the Rector. Alexander VII is mapped through the index cross-reference to the active Fabio Chigi candidate.",
            True,
            "The source explicitly states a friendship between the Rector and Alexander VII; the Rector remains unidentified.",
        ),
    ]
    new_by_id = {row["statement_id"]: row for row in new_statements}
    require(set(new_by_id) == NEW_STATEMENT_IDS, "new statement ID set differs from plan")

    # The quotation note after Bernini's saying supports both atomized clauses.
    footnote_keys = (
        "footnote_markers",
        "footnote_source_lines",
        "footnote_segment_id",
        "footnote_pending",
        "footnote_statement_ids",
        "footnote_refs",
    )
    for key in footnote_keys:
        if key in bernini_quote["qualifiers"]:
            new_by_id["st-chp3-seciv-l96-104-bernini-consolation-visit"]["qualifiers"][key] = deepcopy(
                bernini_quote["qualifiers"][key]
            )

    new_mentions = [{
        "mention_id": NEW_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": NEW_CANDIDATE["candidate_id"],
        "surface_form": text[2331:2348],
        "start_char": "2331",
        "end_char": "2348",
        "note": "The pronoun “his” refers to Alexander VII. The entourage is unnamed; members, number, and actual contributions are not given.",
    }]
    require(new_mentions[0]["surface_form"] == "all his entourage", "planned mention surface mismatch")

    # Refresh the existing drawing candidate name so it does not claim an unstated draftsman.
    candidate_by_id["cand-5321"]["canonical_name"] = (
        "Drawings for Cardinal Ceva’s proposed church and lodgings at the Jesuit novitiate"
    )
    candidate_by_id["cand-5321"]["detail"] = (
        "Haskell says the drawings were made after Cardinal Ceva selected Borromini and that Innocent X "
        "forbade their execution. The passage does not explicitly identify the draftsman; completion and "
        "survival are not established."
    )
    candidate_rows.append({
        "candidate_id": NEW_CANDIDATE["candidate_id"],
        "index_entry_id": "",
        "canonical_name": NEW_CANDIDATE["canonical_name"],
        "index_page_range": "",
        "suggested_type": NEW_CANDIDATE["suggested_type"],
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": NEW_CANDIDATE["detail"],
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": NEW_CANDIDATE["candidate_source_ref"],
    })
    mention_rows.append(new_mentions[0])
    all_segment_rows = segment_statements + new_statements
    require(len(all_segment_rows) == 32, "expected 32 post-review statements")
    require(sum(row["qualifiers"]["relation_candidate"] is True for row in all_segment_rows) == 26,
            "expected 26 relation candidates")
    require(sum(row["qualifiers"]["relation_candidate"] is False for row in all_segment_rows) == 6,
            "expected six nonrelations")
    require(all("relation_candidate" in row["qualifiers"] for row in all_segment_rows),
            "segment retains unclassified statements")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    for row in all_segment_rows:
        if row["qualifiers"]["relation_candidate"]:
            subject_id, object_id = row.get("subject_candidate_id"), row.get("object_candidate_id")
            require(subject_id in candidate_by_id and object_id in candidate_by_id,
                    f"relation candidate has an unresolved endpoint: {row['statement_id']}")
            require(candidate_by_id[subject_id]["status"] != "excluded"
                    and candidate_by_id[object_id]["status"] != "excluded",
                    f"relation candidate uses an excluded endpoint: {row['statement_id']}")
    require(not any(row["candidate_id"] in {"cand-2889", "cand-2911"} for row in mention_rows),
            "an excluded alias is still used by a mention")
    require(not any(
        cid in {"cand-2889", "cand-2911"}
        for row in statement_rows
        for cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    ), "an excluded alias is still used by a statement endpoint")

    segment_indices = [i for i, row in enumerate(statement_rows) if row.get("segment_id") == SEGMENT_ID]
    require(len(segment_indices) == 24 and segment_indices[-1] - segment_indices[0] + 1 == 24,
            "segment statement rows are not contiguous")
    ordered_segment = sorted(all_segment_rows, key=lambda row: row["statement_id"])
    statement_rows[segment_indices[0]:segment_indices[-1] + 1] = ordered_segment
    require(len(statement_rows) == 12807, "unexpected post-plan statement total")
    require(len(candidate_rows) == 11594, "unexpected post-plan candidate total")
    require(len(mention_rows) == 27530, "unexpected post-plan mention total")

    print("mode:", "apply" if args.apply else "dry-run")
    print("segment:", SEGMENT_ID, "source_sha256:", SOURCE_SHA256, "segment_sha256:", SEGMENT_SHA256)
    print("p.86 visual check: printed p.86 / PDF physical p.28; p.87 checked for the L104 continuation")
    print("statements: 24 existing reviewed; 8 atomic statements added; 26 relation candidates, 6 nonrelations")
    print("endpoint repairs: Alexander VII and Innocent X index aliases redirected; Pope view objection linked to project")
    print("candidate update: cand-5321 no longer asserts an unproven draftsman")
    print("candidates: 1 added; mentions: 1 added; stale footnote-pending notes corrected")
    print("post-plan totals: candidates=11594 mentions=27530 statements=12807")
    print("No S6 relations are written.")
    if not args.apply:
        print("No files were written. Re-run with --apply to create recovery copies and write.")
        return

    backups = {
        STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp3-seciv-l96-104-relations-20261011"),
        CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp3-seciv-l96-104-relations-20261011"),
        MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp3-seciv-l96-104-relations-20261011"),
    }
    require(all(not backup.exists() for backup in backups.values()), "a recovery-copy path already exists")

    payloads: dict[Path, bytes] = {
        STATEMENTS: b"".join(
            (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            for row in statement_rows
        )
    }
    for path, fields, rows in (
        (CANDIDATES, candidate_fields, candidate_rows),
        (MENTIONS, mention_fields, mention_rows),
    ):
        buffer = StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        payloads[path] = b"\xef\xbb\xbf" + buffer.getvalue().encode("utf-8")

    temp_paths: dict[Path, Path] = {}
    try:
        for path, payload in payloads.items():
            fd, name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=path.parent)
            os.close(fd)
            temp = Path(name)
            temp.write_bytes(payload)
            temp_paths[path] = temp
        for path, backup in backups.items():
            shutil.copy2(path, backup)
        for path, temp in temp_paths.items():
            os.replace(temp, path)

        post_statements = load_jsonl(STATEMENTS)
        post_candidates = load_csv(CANDIDATES)[1]
        post_mentions = load_csv(MENTIONS)[1]
        reviewed = [row for row in post_statements if row.get("segment_id") == SEGMENT_ID]
        require(len(reviewed) == 32, "post-write segment statement count mismatch")
        require(sum(row["qualifiers"].get("relation_candidate") is True for row in reviewed) == 26,
                "post-write relation candidate count mismatch")
        require(sum(row["qualifiers"].get("relation_candidate") is False for row in reviewed) == 6,
                "post-write nonrelation count mismatch")
        require(len(post_candidates) == 11594 and len(post_mentions) == 27530,
                "post-write candidate/mention count mismatch")
        print("apply complete; recovery copies:")
        for path, backup in backups.items():
            print(" ", backup.relative_to(ROOT))
            print("   pre-write sha256:", EXPECTED_FILE_SHA256[path])
            print("   post-write sha256:", digest(path))
    finally:
        for temp in temp_paths.values():
            temp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
