#!/usr/bin/env python3
"""Controlled S2 relation review for Chapter 3, section IV, lines 83-94.

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
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l83-94"
SOURCE_SHA256 = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA256 = "d383eda7966545e3076939e047d68dd77ce6235bcbb92b5f76598e6af55cef67"
EXPECTED_FILE_SHA256 = {
    STATEMENTS: "d570f206e165b2b5c46f89de1c0dc2ffe0ae77214fb86937dfbe6286cf14bfd2",
    CANDIDATES: "2fdd08da3cbdac90b71a63612224dd2e1c910a805dc04280df483592d6b3ea59",
    MENTIONS: "527989c1c7c6add7b317e553612c664b64947a76830bdce288b501bafdec6f68",
}

EXISTING_STATEMENT_IDS = {
    "st-chp3-seciv-l83-94-bellarmine-monument",
    "st-chp3-seciv-l83-94-berni-advice",
    "st-chp3-seciv-l83-94-bernini-close",
    "st-chp3-seciv-l83-94-bernini-free-hand",
    "st-chp3-seciv-l83-94-bernini-supremacy",
    "st-chp3-seciv-l83-94-chapel-rights",
    "st-chp3-seciv-l83-94-chapel-upkeep",
    "st-chp3-seciv-l83-94-chose-painters",
    "st-chp3-seciv-l83-94-diplomatic-use",
    "st-chp3-seciv-l83-94-domenico-claim",
    "st-chp3-seciv-l83-94-essential-arrangement",
    "st-chp3-seciv-l83-94-jesuits-infuriated",
    "st-chp3-seciv-l83-94-last-clash",
    "st-chp3-seciv-l83-94-negroni-letter",
    "st-chp3-seciv-l83-94-negroni-papal-arms",
    "st-chp3-seciv-l83-94-negroni-stubborn",
    "st-chp3-seciv-l83-94-novitiate-rebuilding",
    "st-chp3-seciv-l83-94-oliva-agreed",
    "st-chp3-seciv-l83-94-oliva-general-friendship",
    "st-chp3-seciv-l83-94-ordered-memorial",
    "st-chp3-seciv-l83-94-patron-rights",
    "st-chp3-seciv-l83-94-relic-access",
    "st-chp3-seciv-l83-94-sat-for-portrait",
    "st-chp3-seciv-l83-94-sermon-illustrations",
    "st-chp3-seciv-l83-94-urban-poems-edition",
}
NEW_STATEMENT_IDS = {
    "st-chp3-seciv-l83-94-chooses-carlone",
    "st-chp3-seciv-l83-94-chooses-maratta",
    "st-chp3-seciv-l83-94-society-gave-bernini-free-hand",
    "st-chp3-seciv-l83-94-letter-addressed-to-oliva",
}
NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11614",
        "canonical_name": "Unidentified benefactors of the Jesuit Society in Haskell's account",
        "suggested_type": "",
        "candidate_source_ref": SEGMENT_ID + "#L89",
        "detail": "A source-bounded group named as the Society's counterpart in a long series of clashes. Members and number are unspecified; do not infer a complete patron list or assume that every nearby patron belongs to this group.",
    },
    {
        "candidate_id": "cand-11615",
        "canonical_name": "Unidentified public admitted to worship of the Holy Relic in Negroni's chapel",
        "suggested_type": "",
        "candidate_source_ref": SEGMENT_ID + "#L88",
        "detail": "Negroni says worship of the Holy Relic would be open to the public. The audience is a source-defined group with no supplied membership or count; its type remains unassigned.",
    },
]


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


def find_row(rows: list[dict], key: str, value: str) -> dict:
    matches = [row for row in rows if row.get(key) == value]
    require(len(matches) == 1, f"expected one {key}={value}, found {len(matches)}")
    return matches[0]


def quote(text: str, phrase: str) -> str:
    start = text.find(phrase)
    require(start >= 0, f"source phrase not found: {phrase!r}")
    return text[start:start + len(phrase)]


def new_statement(statement_id: str, subject: str, predicate: str, obj: str,
                  source_line: int, claim: str, source_quote: str,
                  qualification: str, **extra_qualifiers: object) -> dict:
    qualifiers = {
        "source_line_start": source_line,
        "source_line_end": source_line,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "print_page": 85,
        "pdf_physical_page": 27,
        "qualification": qualification,
        "relation_candidate": True,
        "relation_candidate_note": "This is a source-supported relationship candidate; it remains an S2 claim and does not create an S6 formal edge.",
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

    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment_matches = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    require(len(segment_matches) == 1, "expected one S0 segment")
    require(segment_matches[0].get("sha256") == SEGMENT_SHA256, "S0 segment hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[82:94])
    require(hashlib.sha256(text.encode("utf-8")).hexdigest() == SEGMENT_SHA256,
            "reconstructed segment text hash mismatch")
    require(len(text) == 2810, "unexpected reconstructed segment length")

    statement_rows = load_jsonl(STATEMENTS)
    candidate_fields, candidate_rows = load_csv(CANDIDATES)
    mention_fields, mention_rows = load_csv(MENTIONS)
    segment_statements = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    require({row["statement_id"] for row in segment_statements} == EXISTING_STATEMENT_IDS,
            "segment statement set changed")
    require(len(segment_statements) == 25, "expected 25 existing statements")
    require(all("relation_candidate" not in row.get("qualifiers", {}) for row in segment_statements),
            "a segment statement was already classified")

    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    require(max(int(cid[5:]) for cid in candidate_ids) == 11613, "candidate ID high-water mark changed")
    require(not (candidate_ids & {row["candidate_id"] for row in NEW_CANDIDATES}),
            "a planned candidate ID already exists")
    mention_ids = {row["mention_id"] for row in mention_rows}
    planned_mention_ids = {"m-chp3-seciv-l83-94-0058", "m-chp3-seciv-l83-94-0059"}
    require(not (mention_ids & planned_mention_ids), "a planned mention ID already exists")
    existing_segment_mentions = [row for row in mention_rows if row.get("segment_id") == SEGMENT_ID]
    require(max(int(row["mention_id"].rsplit("-", 1)[1]) for row in existing_segment_mentions) == 57,
            "segment mention ID high-water mark changed")

    new_mentions = [
        {
            "mention_id": "m-chp3-seciv-l83-94-0058",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-11614",
            "surface_form": text[1497:1512],
            "start_char": "1497",
            "end_char": "1512",
            "note": "Source-defined unnamed group; membership and count are unspecified.",
        },
        {
            "mention_id": "m-chp3-seciv-l83-94-0059",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-11615",
            "surface_form": text[899:909],
            "start_char": "899",
            "end_char": "909",
            "note": "Source-defined public audience; no membership or attendance is inferred.",
        },
    ]
    require(new_mentions[0]["surface_form"] == "its benefactors", "benefactors span mismatch")
    require(new_mentions[1]["surface_form"] == "the public", "public span mismatch")

    by_id = {row["statement_id"]: row for row in statement_rows}
    def change(statement_id: str, *, subject: str | None = None, obj: str | None = None,
               predicate: str | None = None, claim: str | None = None,
               source_quote: str | None = None, qualification: str | None = None,
               note: str | None = None, **qualifier_updates: object) -> dict:
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
        if note is not None:
            q["relation_candidate_note"] = note
        q.update(qualifier_updates)
        if source_quote is not None:
            row["original_quote"] = source_quote
        return row

    # Split coordinated roles and align statement endpoints with the asserted relation.
    change(
        "st-chp3-seciv-l83-94-bellarmine-monument",
        obj="cand-5316", predicate="helped_father_on_bellarmine_monument",
        claim="Haskell says Bernini helped his unnamed father on the monument to Cardinal Bellarmine in the Ges\u00f9.",
        qualification="The father remains unnamed. The monument is preserved as the work context (cand-5311); no maker or date is inferred.",
        work_candidate_id="cand-5311",
        note="Bernini's help to his father is the relation; the monument is the stated work context.",
    )
    change(
        "st-chp3-seciv-l83-94-bernini-free-hand",
        predicate="shared_ideals_with",
        claim="Haskell says Bernini profoundly shared Jesuit ideals.",
        source_quote=quote(text, "profoundly shared their ideals"),
        qualification="This is Haskell's characterization of Bernini's affinity with the Society.",
        event_candidate_id="cand-5309",
        note="The sentence contains two distinct relations; this row records the shared ideals, and a second statement records the free hand.",
    )
    change(
        "st-chp3-seciv-l83-94-chose-painters",
        obj="cand-1117", predicate="rejected_as_chapel_painter_by_negroni",
        claim="Haskell says Negroni did not wish Gaulli to paint his chapel.",
        source_quote=quote(text, "Negroni did not wish to have his chapel painted by the artist"),
        qualification="The pronoun 'the artist' refers to Gaulli. This records Negroni's stated preference, not a completed commission or painting.",
        chapel_candidate_id="cand-5300", project_candidate_id="cand-5308",
        note="The original clause coordinated Gaulli's rejection with the selection of Carlone and Maratta; the three artist claims are now separate.",
    )
    for key in ("footnote_markers", "footnote_source_lines", "footnote_segment_id",
                "footnote_pending", "footnote_statement_ids", "footnote_refs"):
        by_id["st-chp3-seciv-l83-94-chose-painters"]["qualifiers"].pop(key, None)
    change(
        "st-chp3-seciv-l83-94-diplomatic-use",
        qualification="Footnote 6 is linked to the note statement about Oliva's pressure on Bernini's French journey. It reports Haskell's account and does not establish the mission's outcome.",
        footnote_pending=False,
        note="Oliva's use of Bernini for diplomatic ends is distinct from the friendship and advice statements; the note remains a source-bound report.",
    )
    change(
        "st-chp3-seciv-l83-94-domenico-claim",
        subject="cand-0298", obj="cand-5200",
        predicate="visited_gesu_weekly_for_forty_years_as_claimed_by_domenico",
        claim="Haskell reports Domenico's claim that Bernini visited the Ges\u00f9 once a week for forty years.",
        qualification="Domenico is identified here only as Bernini's son; his surname and the dates of the forty-year span are not supplied.",
        speaker="Domenico", speaker_candidate_id="cand-5313",
        note="The proposition concerns Bernini's visits to the Ges\u00f9; Domenico is the attributed source, not the visiting subject.",
    )
    change(
        "st-chp3-seciv-l83-94-chapel-upkeep",
        subject="cand-3403", obj="cand-5300",
        predicate="responsible_for_chapel_upkeep_as_claimed_by_negroni",
        claim="Negroni says the Jesuit fathers will be responsible for upkeep of the chapel.",
        qualification="This is Negroni's quoted allocation of responsibility, not evidence that the fathers performed the maintenance.",
        speaker="Negroni", text_layer="quoted statement within Haskell narrative",
        note="The asserted responsibility runs from the Jesuit fathers to the chapel; Negroni remains the speaker.",
    )
    change(
        "st-chp3-seciv-l83-94-last-clash",
        obj="cand-11614", predicate="last_clash_between_jesuit_society_and_benefactors",
        qualification="Retrospective authorial characterization; the benefactor group's membership and number are not supplied.",
        note="The source explicitly names both the Society and its benefactors; the latter are recorded as a source-bounded open group.",
    )
    change(
        "st-chp3-seciv-l83-94-negroni-letter",
        subject="cand-5306", obj="cand-1732", predicate="authored_by",
        claim="Haskell says Negroni wrote to Oliva and quotes Negroni's letter about the papal arms.",
        qualification="The letter is quoted through Haskell; its manuscript identity is not supplied. The recipient is recorded separately.",
        recipient_candidate_id="cand-1771",
        note="Communication direction follows the archive relation contract: the letter points to its author, while a separate statement records its recipient.",
    )
    change(
        "st-chp3-seciv-l83-94-patron-rights",
        obj="cand-5300", predicate="haskell_interprets_patron_rights_over_chapel_decoration",
        claim="Haskell interprets the controversy as showing what rights a patron claimed over the decoration of Negroni's chapel.",
        qualification="This is Haskell's interpretation of the controversy, not an independent statement of law.",
        footnote_markers=[3], footnote_source_lines=[213],
        footnote_segment_id="chp-3:03_CHP-3_sec_iv:l189-243",
        footnote_pending=False,
        footnote_statement_ids=["st-chp3-seciv-notes-l205-243-p85-n3-pecchiai"],
        note="The phrase explicitly identifies the chapel as the object of the patron-rights interpretation; footnote 3 is linked as a source locator.",
    )
    change(
        "st-chp3-seciv-l83-94-relic-access",
        subject="cand-11615", obj="cand-5307",
        predicate="worship_of_relic_open_to_public_as_claimed_by_negroni",
        claim="Negroni says worship of the Holy Relic would be open to the public.",
        qualification="The audience is an unnamed source-defined group. The arrangement is Negroni's claim; actual attendance or implementation is not established. Footnote 4 identifies the relic as St Francis Xavier's arm, while its candidate type remains unresolved.",
        speaker="Negroni", text_layer="quoted statement within Haskell narrative",
        note="The claim's endpoints are the public audience and the relic; Negroni is the speaker, not the audience endpoint.",
    )
    change(
        "st-chp3-seciv-l83-94-sermon-illustrations",
        subject="cand-5315", obj="cand-0298", predicate="illustrated_by",
        claim="Haskell says Bernini produced illustrations for an edition of Oliva's sermons.",
        qualification="The illustration work and sermon edition are distinct candidates; bibliographic details and surviving status are not supplied.",
        edition_candidate_id="cand-5314",
        note="The illustrated work points to Bernini as creator; Oliva's sermon edition is retained as its publication context.",
    )
    change(
        "st-chp3-seciv-l83-94-urban-poems-edition",
        obj="cand-3403", predicate="collaborated_with_jesuits_on_illustrated_edition",
        claim="Haskell says Bernini collaborated with the Jesuits in producing an illustrated edition of Urban VIII's Latin poems.",
        qualification="The edition is the project context (cand-5312); bibliographic details are not supplied.",
        edition_candidate_id="cand-5312",
        note="The asserted collaboration is between Bernini and the Jesuits; the edition is context rather than the collaborator endpoint.",
    )

    # Put the added relational claims on their stated participants and preserve scope.
    new_statements = [
        new_statement(
            "st-chp3-seciv-l83-94-chooses-carlone", "cand-1732", "selected_as_chapel_painter",
            "cand-0562", 87,
            "Haskell says Negroni chose Gianandrea Carlone as a painter for his chapel.",
            quote(text, "he chose instead another Genoese painter, Gianandrea Carlone"),
            "This records a choice, not a completed painting. Footnote 1 describes Carlone's earlier painting at the Perugia Jesuit church and is linked as a locator.",
            project_candidate_id="cand-5308", chapel_candidate_id="cand-5300",
            footnote_markers=[1], footnote_source_lines=[211],
            footnote_segment_id="chp-3:03_CHP-3_sec_iv:l189-243", footnote_pending=False,
            footnote_statement_ids=[
                "st-chp3-seciv-notes-l205-243-p85-n1-carlone-painted-perugia-tribune",
                "st-chp3-seciv-notes-l205-243-p85-n1-perugia-ms",
            ],
        ),
        new_statement(
            "st-chp3-seciv-l83-94-chooses-maratta", "cand-1732", "selected_as_chapel_painter",
            "cand-1526", 87,
            "Haskell says Negroni chose Carlo Maratta as a painter for his chapel.",
            quote(text, "and the most famous artist of the day, Carlo Maratta"),
            "This records a choice, not a completed painting. Footnote 2 identifies a distinct Maratta painting, not the execution of the chapel commission.",
            project_candidate_id="cand-5308", chapel_candidate_id="cand-5300",
            footnote_markers=[2], footnote_source_lines=[212],
            footnote_segment_id="chp-3:03_CHP-3_sec_iv:l189-243", footnote_pending=False,
            footnote_statement_ids=["st-chp3-seciv-notes-l205-243-p85-n2-maratta-work"],
        ),
        new_statement(
            "st-chp3-seciv-l83-94-society-gave-bernini-free-hand", "cand-3403",
            "gave_free_hand_to_in_rebuilding", "cand-0298", 91,
            "Haskell says the Society gave Bernini a free hand in the rebuilding of S. Andrea al Quirinale.",
            quote(text, "he was given a free hand by the Society"),
            "The rebuilding of the novitiate church is the stated context; this does not establish details of the completed design.",
            event_candidate_id="cand-5309",
        ),
        new_statement(
            "st-chp3-seciv-l83-94-letter-addressed-to-oliva", "cand-5306", "addressed_to",
            "cand-1771", 85,
            "Haskell says Negroni's quoted letter was written to Oliva.",
            quote(text, "then wrote to Oliva"),
            "The letter is quoted through Haskell; no manuscript identity or date is supplied.",
            speaker="Haskell", text_layer="authorial narrative",
        ),
    ]

    # Attach relation/nonrelation labels and rationale to the existing statements.
    for row in segment_statements:
        q = row.setdefault("qualifiers", {})
        is_relation = row["statement_id"] != "st-chp3-seciv-l83-94-negroni-stubborn"
        q["relation_candidate"] = is_relation
        if not is_relation:
            q["relation_candidate_note"] = "Scalar authorial characterization of Negroni's persistence; it does not state a relationship between two entities."
        elif "relation_candidate_note" not in q:
            q["relation_candidate_note"] = "The statement expresses a source-bounded relation between the recorded endpoints; it remains an S2 candidate, not an S6 edge."

    for row in new_statements:
        row["qualifiers"]["relation_candidate_note"] = (
            "The coordinated source clause is represented as an atomic, source-bounded relationship candidate; no execution or external verification is inferred."
        )

    # Make the reached note links explicit and current for the existing quoted assertions.
    for statement_id in [
        "st-chp3-seciv-l83-94-chapel-rights",
        "st-chp3-seciv-l83-94-chapel-upkeep",
        "st-chp3-seciv-l83-94-relic-access",
        "st-chp3-seciv-l83-94-essential-arrangement",
    ]:
        q = by_id[statement_id]["qualifiers"]
        q["footnote_pending"] = False
        q["footnote_statement_ids"] = ["st-chp3-seciv-notes-l205-243-p85-n4-xavier-relic"]

    all_segment_rows = segment_statements + new_statements
    require(len(all_segment_rows) == 29, "expected 29 post-split statements")
    require(sum(row["qualifiers"]["relation_candidate"] is True for row in all_segment_rows) == 28,
            "expected 28 relation candidates")
    require(sum(row["qualifiers"]["relation_candidate"] is False for row in all_segment_rows) == 1,
            "expected one nonrelation")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    for row in NEW_CANDIDATES:
        candidate_rows.append({
            "candidate_id": row["candidate_id"],
            "index_entry_id": "",
            "canonical_name": row["canonical_name"],
            "index_page_range": "",
            "suggested_type": row["suggested_type"],
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": row["detail"],
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": row["candidate_source_ref"],
        })
    candidate_ids.update(row["candidate_id"] for row in NEW_CANDIDATES)
    mention_rows.extend(new_mentions)

    ordered_segment = sorted(all_segment_rows, key=lambda row: row["statement_id"])
    indices = [i for i, row in enumerate(statement_rows) if row.get("segment_id") == SEGMENT_ID]
    require(len(indices) == 25 and indices[-1] - indices[0] + 1 == len(indices),
            "segment statement rows are not contiguous")
    statement_rows[indices[0]:indices[-1] + 1] = ordered_segment

    relation_rows = [row for row in ordered_segment if row["qualifiers"]["relation_candidate"]]
    require(all(row.get("subject_candidate_id") in candidate_ids and row.get("object_candidate_id") in candidate_ids
                for row in relation_rows), "a relation candidate has a missing or unknown endpoint")
    require(len(candidate_rows) == 11593, "unexpected candidate total after plan")
    require(len(mention_rows) == 27529, "unexpected mention total after plan")
    require(len(statement_rows) == 12799, "unexpected statement total after plan")

    print("mode:", "apply" if args.apply else "dry-run")
    print("segment:", SEGMENT_ID, "source_sha256:", SOURCE_SHA256, "segment_sha256:", SEGMENT_SHA256)
    print("statements: 25 existing reviewed; four atomic statements added; 28 relation candidates, one nonrelation")
    print("endpoint repairs: Bellarmine father, Jesuit upkeep, public audience, Society benefactors, patron-rights, letter roles, collaboration/illustration roles")
    print("candidates: 2 added; mentions: 2 added; note links: 1 pending qualification corrected")
    print("post-plan totals: candidates=11593 mentions=27529 statements=12799; S2 relation candidates=5080")
    print("new candidate IDs:", ", ".join(row["candidate_id"] for row in NEW_CANDIDATES))
    print("new statement IDs:", ", ".join(sorted(NEW_STATEMENT_IDS)))
    if not args.apply:
        print("No files were written. Re-run with --apply to create recovery copies and write.")
        return

    backups = {
        STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp3-sec-iv-l83-94-relations-20261011"),
        CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp3-sec-iv-l83-94-relations-20261011"),
        MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp3-sec-iv-l83-94-relations-20261011"),
    }
    require(all(not backup.exists() for backup in backups.values()), "a recovery-copy path already exists")

    payloads: dict[Path, bytes] = {}
    payloads[STATEMENTS] = b"".join(
        (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        for row in statement_rows
    )
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
        require(len(load_jsonl(STATEMENTS)) == 12799, "post-write statement count mismatch")
        require(len(load_csv(CANDIDATES)[1]) == 11593, "post-write candidate count mismatch")
        require(len(load_csv(MENTIONS)[1]) == 27529, "post-write mention count mismatch")
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
