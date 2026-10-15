from __future__ import annotations

import argparse
import copy
import csv
import difflib
import hashlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SEGMENTS = TABLE_DIR / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PAGE82 = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/.tmp_chp3_p82_phys24_20261010.png"

BODY_SEGMENT = "chp-3:03_CHP-3_sec_iv:l58-67"
NOTE_SEGMENT = "chp-3:03_CHP-3_sec_iv:l189-243"
NEW_CANDIDATE_IDS = {"cand-11607", "cand-11608"}
NEW_STATEMENT_IDS = {
    "st-chp3-seciv-l58-67-jesuit-influence-papal-court",
    "st-chp3-seciv-l58-67-jesuits-assert-power",
    "st-chp3-seciv-l58-67-bernin-treated-duplex",
    "st-chp3-seciv-notes-l189-204-p82-n3-drawings-held-in-dusseldorf",
}
REMOVE_MENTION_IDS = {
    "m-chp3-seciv-l58-67-0036",
    "m-s2-chp3-surface-bc15ba5de5bae625",
}
NEW_MENTION_ID = "m-chp3-seciv-l58-67-0037"
BERNINI_DUPLEX_MENTION_ID = "m-chp3-seciv-notes-l189-204-0041"
NOTE3_LOCATION_ID = "st-chp3-seciv-notes-l189-204-p82-n3-drawings-held-in-berlin-and-dusseldorf"
NOTE4_ADAPTATION_ID = "st-chp3-seciv-notes-l189-204-p82-n4-gaulli-adapted-bernini-duplex-intercessio"

EXPECTED_HASHES = {
    STATEMENTS: "5f58848b5f99154cecb4f573f615cb43c62bc9e47d6b364e165b0a7b4242ddc8",
    CANDIDATES: "beeff6f63d0ee3d17ff785f592fb4f48e3dfc88722ab0dd8e394da724e840dba",
    MENTIONS: "2878ea2d558927c8a7161b7e34b797c94ec852dc9960016a9d9a73829b473737",
    SOURCE: "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE82: "9001d203358712473696965959257a1700c1c3b6928bcac97389ab7238701595",
}

BACKUPS = {
    STATEMENTS: STATEMENTS.with_name(
        STATEMENTS.name + ".bak-s2-chp3-sec-iv-l58-67-relations-20261010"
    ),
    CANDIDATES: CANDIDATES.with_name(
        CANDIDATES.name + ".bak-s2-chp3-sec-iv-l58-67-iconographic-entities-20261010"
    ),
    MENTIONS: MENTIONS.with_name(
        MENTIONS.name + ".bak-s2-chp3-sec-iv-l58-67-mention-corrections-20261010"
    ),
}

RELATION_NOTES = {
    "st-chp3-seciv-l58-67-bernini-affected-uncertain-origin":
        "Haskell explicitly says Bernini was affected by the Blood of Christ theme while leaving derivation from Molinos unresolved.",
    "st-chp3-seciv-l58-67-bernini-blood-belief-quotation":
        "The attributed quotation reports Bernini's belief concerning the Blood of Christ; retain the second-level quotation and source boundary.",
    "st-chp3-seciv-l58-67-bernini-etching-1668":
        "Haskell reports that Bernini employed an unnamed etcher to reproduce the identified drawing; the etcher remains an unnamed agent, not a fabricated person endpoint.",
    "st-chp3-seciv-l58-67-bernini-suggested-blood-theme":
        "Haskell says Bernini presumably suggested to Gaulli that he adapt this theme for the Gesù dome; preserve the author's uncertainty.",
    "st-chp3-seciv-l58-67-blood-theme-dear-to-molinos":
        "Haskell explicitly describes the Blood of Christ as a theme especially dear to Molinos and says it was not new.",
    "st-chp3-seciv-l58-67-composition-figures-and-arrangement":
        "The composition's iconographic arrangement includes Adam and Eve; the note's generic groups of saints and kings remain a description, not a separately identified entity.",
    "st-chp3-seciv-l58-67-dome-suitability-more-likely-explanation":
        "Haskell's alternative explanation links the Jesuits' judgment to the theme's unsuitability for dome decoration; preserve 'more likely'.",
    "st-chp3-seciv-l58-67-etching-read_as_passive_quietist":
        "This records Haskell's interpretation of the etching as tinged with passivity and quietism, not an independently verified property.",
    "st-chp3-seciv-l58-67-final-scheme-different-but-linked":
        "The Gaulli scheme is distinct from the Blood of Christ theme but retains links to it; Bernini's separate treatment of the Duplex Intercessio is recorded in a companion statement.",
    "st-chp3-seciv-l58-67-gaulli-proposal-drawings-unused":
        "Haskell says Gaulli's drawings were almost certainly related to the proposed project and were unused; note 3 supplies only city-level locations.",
    "st-chp3-seciv-l58-67-jesuit-influence-spheres":
        "The clause states that Jesuit influence had extended over the Roman aristocratic milieu; the second object, the papal court, is split into its own statement.",
    "st-chp3-seciv-l58-67-jesuits-avoided-mystical":
        "The author explicitly describes the Jesuits as avoiding the mystical; retain this as Haskell's broad characterization.",
    "st-chp3-seciv-l58-67-molinos-association-possible-obstacle":
        "Haskell presents the theme's association with Molinos as a possible reason it was unacceptable to the Jesuits, not as a documented decision.",
    "st-chp3-seciv-l58-67-molinos-guida-quote":
        "This connects Molinos's quoted Guida Spirituale passage to that work; the biblical locator at note 1 remains unidentified.",
    "st-chp3-seciv-l58-67-oliva-turns-to-gesu":
        "Haskell infers that the influence concern weighed on Oliva as he turned to Gesù decoration; this is not Oliva's documented motive.",
    "st-chp3-seciv-l58-67-reaction-and-power-assertion":
        "The source links the influence concern to the violence of the Jesuit reaction; the separate determination to assert power is split below.",
    "st-chp3-seciv-l58-67-duplex-intercessio-composition":
        "The composition depicts the Virgin and Christ appealing to God; God is treated as the scene's divine addressee, not as a historical claim.",
}

NONRELATION_NOTES = {
    "st-chp3-seciv-l58-67-dispute-not-clear-cut":
        "This is Haskell's scalar assessment of the dispute's clarity, with no second entity endpoint.",
    "st-chp3-seciv-l58-67-shared-climate-and-nuance":
        "This is a summary of the dispute's shared intellectual climate and nuanced doctrines, not a relation between two identified entities.",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(rows: list[dict]) -> bytes:
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    return text.encode("utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(headers: list[str], rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + stream.getvalue()).encode("utf-8")


def by_id(rows: list[dict], key: str, label: str) -> dict:
    matches = [row for row in rows if row.get(key) == label]
    if len(matches) != 1:
        raise ValueError(f"expected one {key}={label}, found {len(matches)}")
    return matches[0]


def source_segment(segment_id: str) -> tuple[dict, str]:
    segment = by_id(read_jsonl(SEGMENTS), "segment_id", segment_id)
    source_path = ROOT / segment["source_file"]
    lines = source_path.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != segment["sha256"]:
        raise ValueError(f"S0 segment text hash mismatch: {segment_id}")
    return segment, text


def set_relation(row: dict, value: bool, note: str) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    if qualifiers.get("relation_candidate") is not None:
        raise ValueError(f"{row['statement_id']} was already classified")
    qualifiers["relation_candidate"] = value
    qualifiers["relation_candidate_note"] = note


def make_related_copy(
    parent: dict,
    statement_id: str,
    object_candidate_id: str,
    predicate: str,
    claim: str,
    note: str,
    *,
    source_quote: str | None = None,
    subject_candidate_id: str | None = None,
) -> dict:
    row = copy.deepcopy(parent)
    row["statement_id"] = statement_id
    if subject_candidate_id is not None:
        row["subject_candidate_id"] = subject_candidate_id
    row["object_candidate_id"] = object_candidate_id
    row["predicate"] = predicate
    if source_quote is not None:
        row["original_quote"] = source_quote
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers.pop("relation_candidate", None)
    qualifiers.pop("relation_candidate_note", None)
    qualifiers["claim"] = claim
    set_relation(row, True, note)
    return row


def preflight() -> None:
    for path, expected in EXPECTED_HASHES.items():
        actual = digest(path)
        if actual != expected:
            raise ValueError(f"preflight hash mismatch for {path.relative_to(ROOT)}: {actual}")
    for target, backup in BACKUPS.items():
        if backup.exists() and digest(backup) != EXPECTED_HASHES[target]:
            raise ValueError(f"existing recovery copy differs from the expected prewrite file: {backup.name}")
    _, body_text = source_segment(BODY_SEGMENT)
    _, note_text = source_segment(NOTE_SEGMENT)
    if body_text.count("God") != 1 or body_text.count("Duplex Intercessio") != 1:
        raise ValueError("expected unique God and Duplex Intercessio mentions in the body segment")
    if "adapicd Bernini’s Duplex Intercessio" not in note_text:
        raise ValueError("unexpected S0 OCR text in the p.82 note segment")
    if "Bernini’s Duplex Intercessio" not in note_text:
        raise ValueError("the p.82 note does not explicitly identify Bernini's composition")
    if body_text[2431:2438] != "subject":
        raise ValueError("candidate-surface false mention span changed")
    if body_text[2879:2895] != "saints and kings":
        raise ValueError("iconographic group mention span changed")
    if body_text[2740:2743] != "God":
        raise ValueError("God mention offset changed")


def build_changes() -> tuple[dict[Path, bytes], dict[str, list[dict]], dict[str, list[dict]]]:
    statements = read_jsonl(STATEMENTS)
    candidate_headers, candidates = read_csv(CANDIDATES)
    mention_headers, mentions = read_csv(MENTIONS)
    original = {
        "statements": copy.deepcopy(statements),
        "candidates": copy.deepcopy(candidates),
        "mentions": copy.deepcopy(mentions),
    }

    statement_by_id = {row["statement_id"]: row for row in statements}
    body_rows = [row for row in statements if row.get("segment_id") == BODY_SEGMENT]
    if len(body_rows) != 19:
        raise ValueError(f"expected 19 original body statements, found {len(body_rows)}")
    if set(statement_by_id) & NEW_STATEMENT_IDS:
        raise ValueError("one or more planned statement IDs already exist")
    if len([row for row in candidates if row["candidate_id"] in NEW_CANDIDATE_IDS]) != 0:
        raise ValueError("one or more planned candidate IDs already exist")
    if len([row for row in mentions if row["mention_id"] == NEW_MENTION_ID]) != 0:
        raise ValueError("planned mention ID already exists")

    for statement_id, note in RELATION_NOTES.items():
        row = statement_by_id[statement_id]
        set_relation(row, True, note)
    for statement_id, note in NONRELATION_NOTES.items():
        row = statement_by_id[statement_id]
        set_relation(row, False, note)

    influence = statement_by_id["st-chp3-seciv-l58-67-jesuit-influence-spheres"]
    iq = influence["qualifiers"]
    iq.pop("second_object_candidate_id", None)
    iq.pop("possible_existing_candidate_id", None)
    iq["claim"] = "Haskell says the Roman aristocratic milieu had hitherto been subject almost exclusively to Jesuit influence."
    iq["qualification"] = "This clause closes the preceding segment's reference to 'those very spheres'; the social-milieu candidate remains untyped."
    influence["predicate"] = "influenced_roman_aristocratic_milieu"

    papal = make_related_copy(
        influence,
        "st-chp3-seciv-l58-67-jesuit-influence-papal-court",
        "cand-5261",
        "influenced_papal_court",
        "Haskell says the papal court itself had hitherto been subject almost exclusively to Jesuit influence.",
        "The papal-court target is explicit; its identity may overlap cand-4241 and remains for S3 alignment.",
    )
    papal_q = papal["qualifiers"]
    papal_q["possible_existing_candidate_id"] = "cand-4241"
    papal_q["qualification"] = "The surrounding paragraph dates the controversy to the 1670s; the papal-court candidate's identity awaits S3 alignment."

    reaction = statement_by_id["st-chp3-seciv-l58-67-reaction-and-power-assertion"]
    rq = reaction["qualifiers"]
    rq["claim"] = "Haskell says the change in the Jesuits' influence contributed to the violence of their reaction in the Molinos dispute."
    reaction["predicate"] = "influence_change_contributed_to_violent_reaction"

    assert_power = make_related_copy(
        reaction,
        "st-chp3-seciv-l58-67-jesuits-assert-power",
        "cand-5253",
        "became_more_determined_to_assert_power_ostentatiously",
        "Haskell says the influence change made the Jesuits more determined to assert their power ostentatiously.",
        "This is the second consequence in Haskell's sentence; retain the author's causal interpretation and the event context.",
    )

    final_scheme = statement_by_id["st-chp3-seciv-l58-67-final-scheme-different-but-linked"]
    fsq = final_scheme["qualifiers"]
    fsq["claim"] = "Haskell says Gaulli's eventual dome scheme used a subject different from the Blood of Christ theme while retaining links to that theme."
    fsq["qualification"] = "The following clause says the Duplex Intercessio had also been treated by Bernini; it is represented by a separate source-work statement."

    duplex = statement_by_id["st-chp3-seciv-l58-67-duplex-intercessio-composition"]
    duplex["object_candidate_id"] = "cand-11607"
    duplex["predicate"] = "depicts_intercession_addressed_to"
    dq = duplex["qualifiers"]
    dq["claim"] = "Haskell names the final dome subject as the Duplex Intercessio: the kneeling Virgin and Christ appeal to God for mercy for suffering humanity."
    dq["qualification"] = "God is the divine addressee in the iconographic scene; this records Haskell's description, not a theological or historical assertion. Footnote 4 is migrated at L204; its cited books were not independently consulted."
    dq["linked_footnote_statement_ids"] = [
        "st-chp3-seciv-notes-l189-204-p82-n4-panofsky",
        "st-chp3-seciv-notes-l189-204-p82-n4-gaulli-adapted-bernini-duplex-intercessio",
    ]

    body_text = source_segment(BODY_SEGMENT)[1]
    final_quote = final_scheme["original_quote"]
    quote_start = body_text.index(final_quote)
    duplex_end = body_text.index("Duplex Intercessio", quote_start) + len("Duplex Intercessio")
    bernini_quote = body_text[quote_start:duplex_end]
    bernini_treated = make_related_copy(
        final_scheme,
        "st-chp3-seciv-l58-67-bernin-treated-duplex",
        "cand-11608",
        "treated_duplex_intercessio_composition",
        "Haskell says the Duplex Intercessio subject of Gaulli's eventual scheme had also been treated by Bernini.",
        "The body pronoun is resolved by the following title; footnote 4 explicitly identifies Gaulli's adaptation of Bernini's composition.",
        source_quote=bernini_quote,
        subject_candidate_id="cand-0295",
    )
    bernini_treated_q = bernini_treated["qualifiers"]
    bernini_treated_q["source_line_start"] = 65
    bernini_treated_q["source_line_end"] = 65
    bernini_treated_q.pop("artist_candidate_id", None)
    bernini_treated_q["linked_footnote_statement_ids"] = [NOTE4_ADAPTATION_ID]

    note3 = statement_by_id[NOTE3_LOCATION_ID]
    note3["subject_candidate_id"] = "cand-5258"
    note3["object_candidate_id"] = "cand-5476"
    note3["predicate"] = "located_in"
    n3q = note3["qualifiers"]
    n3q["claim"] = "Haskell's note 3 says the Gaulli drawings are in Berlin."
    n3q["qualification"] = "The note gives a city-level location only; it supplies no institution, catalogue number, count, or mapping of an individual drawing."
    n3q.pop("mentioned_candidate_ids", None)
    set_relation(note3, True, "The footnote's 'These drawings' refers to Gaulli's proposed-dome drawings in the immediately linked body statement.")
    note3_dusseldorf = make_related_copy(
        note3,
        "st-chp3-seciv-notes-l189-204-p82-n3-drawings-held-in-dusseldorf",
        "cand-5477",
        "located_in",
        "Haskell's note 3 says the Gaulli drawings are in Dusseldorf.",
        "The footnote's 'These drawings' refers to Gaulli's proposed-dome drawings; the cited city is not mapped to an individual drawing.",
    )

    adaptation = statement_by_id[NOTE4_ADAPTATION_ID]
    adaptation["object_candidate_id"] = "cand-11608"
    adaptation["predicate"] = "adapted_source_composition"
    aq = adaptation["qualifiers"]
    aq["claim"] = "Haskell says Gaulli adapted Bernini's Duplex Intercessio to place Adam at the foot of the Cross instead of Christ while retaining Christ's pose almost exactly."
    aq["resulting_work_candidate_id"] = "cand-5259"
    aq["source_transcription_correction"] = "S0 OCR reads 'adapicd'; the p.82 scan reads 'adapted'. The S0 source text and original_quote remain unchanged."
    set_relation(
        adaptation,
        True,
        "Haskell explicitly names Bernini's source composition and Gaulli's adaptation; the resulting Gesù dome scheme remains the distinct candidate cand-5259.",
    )

    new_candidates = [
        {
            "candidate_id": "cand-11607",
            "index_entry_id": "",
            "canonical_name": "God, divine addressee in the Duplex Intercessio",
            "index_page_range": "",
            "suggested_type": "person",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "God is named as the addressee of the Virgin and Christ's appeal in Haskell's iconographic description. Record the figure in the described scene without making a theological or historical assertion.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-3:03_CHP-3_sec_iv:l58-67#L66",
        },
        {
            "candidate_id": "cand-11608",
            "index_entry_id": "",
            "canonical_name": "Bernini's Duplex Intercessio composition (source for Gaulli's adaptation)",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell's p.82 footnote 4 names Bernini's Duplex Intercessio as the composition Gaulli adapted; distinguish this source composition from Gaulli's resulting Gesù dome scheme cand-5259. Brauer and Wittkower plate 128 is cited but was not independently consulted.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": "chp-3:03_CHP-3_sec_iv:l189-243#L204",
        },
    ]
    candidates.extend(new_candidates)

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_by_id["cand-5258"]["detail"] = (
        "A number of Gaulli's drawings were almost certainly connected with the proposed Blood of Christ dome project; "
        "Haskell says they survived unused. Footnote 3 (L203) places the drawings at city level in Berlin and Dusseldorf; "
        "it gives no institution, catalogue number, count, or individual drawing-to-city mapping."
    )
    candidate_by_id["cand-5476"]["canonical_name"] = "Berlin, city identified as a location of Gaulli's drawings"
    candidate_by_id["cand-5476"]["detail"] = (
        "Haskell's footnote 3 says the plural Gaulli drawings are in Berlin. The source gives no institution, "
        "catalogue identifier, count, or mapping of a particular drawing to this city."
    )
    candidate_by_id["cand-5477"]["canonical_name"] = "Dusseldorf, city identified as a location of Gaulli's drawings"
    candidate_by_id["cand-5477"]["detail"] = (
        "Haskell's footnote 3 says the plural Gaulli drawings are in Dusseldorf. Preserve the S0 form pending S3 normalization; "
        "the source gives no institution, catalogue identifier, count, or mapping of a particular drawing to this city."
    )

    body_mentions = [row for row in mentions if row.get("segment_id") == BODY_SEGMENT]
    _, body_text = source_segment(BODY_SEGMENT)
    god_start = body_text.index("God")
    mentions = [row for row in mentions if row["mention_id"] not in REMOVE_MENTION_IDS]
    if len(body_mentions) != 37:
        raise ValueError(f"expected 37 existing body mentions before correction, found {len(body_mentions)}")
    mentions.append(
        {
            "mention_id": NEW_MENTION_ID,
            "segment_id": BODY_SEGMENT,
            "candidate_id": "cand-11607",
            "surface_form": "God",
            "start_char": str(god_start),
            "end_char": str(god_start + 3),
            "note": "Divine addressee in the iconographic scene; not a theological or historical claim.",
        }
    )
    bernini_mention = by_id(mentions, "mention_id", BERNINI_DUPLEX_MENTION_ID)
    if bernini_mention["candidate_id"] != "cand-5259" or bernini_mention["surface_form"] != "Duplex Intercessio":
        raise ValueError("unexpected Bernini Duplex Intercessio note mention")
    bernini_mention["candidate_id"] = "cand-11608"
    bernini_mention["note"] = "Bernini's source composition named in footnote 4; distinct from Gaulli's resulting dome scheme."

    statements.extend([papal, assert_power, bernini_treated, note3_dusseldorf])

    proposed: dict[Path, bytes] = {}
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        before = original[
            "statements" if path == STATEMENTS else "candidates" if path == CANDIDATES else "mentions"
        ]
        after = statements if path == STATEMENTS else candidates if path == CANDIDATES else mentions
        if path == STATEMENTS:
            target_bytes = write_jsonl(after)
        else:
            headers = candidate_headers if path == CANDIDATES else mention_headers
            target_bytes = write_csv(headers, after)
        proposed[path] = target_bytes
    return proposed, original, {
        "statements": statements,
        "candidates": candidates,
        "mentions": mentions,
    }


def validate_rows(rows: dict[str, list[dict]]) -> dict:
    statements = rows["statements"]
    candidates = rows["candidates"]
    mentions = rows["mentions"]
    ids = {row["statement_id"] for row in statements}
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    if len(ids) != len(statements) or len(candidate_ids) != len(candidates) or len(mention_ids) != len(mentions):
        raise ValueError("duplicate row IDs after planned changes")
    if not NEW_STATEMENT_IDS.issubset(ids) or not NEW_CANDIDATE_IDS.issubset(candidate_ids):
        raise ValueError("new IDs missing after planned changes")
    if REMOVE_MENTION_IDS & mention_ids:
        raise ValueError("false/incorrect mentions remain")
    if NEW_MENTION_ID not in mention_ids:
        raise ValueError("God mention missing")

    candidate_set = candidate_ids
    for row in mentions:
        if row["candidate_id"] not in candidate_set:
            raise ValueError(f"mention references missing candidate: {row['mention_id']}")

    body = [row for row in statements if row.get("segment_id") == BODY_SEGMENT]
    body_states = [row.get("qualifiers", {}).get("relation_candidate") for row in body]
    if len(body) != 22 or body_states.count(True) != 20 or body_states.count(False) != 2:
        raise ValueError(f"body classification mismatch: count={len(body)} states={collections_counter(body_states)}")
    note_relations = [
        row for row in statements
        if row["statement_id"] in {
            NOTE3_LOCATION_ID,
            "st-chp3-seciv-notes-l189-204-p82-n3-drawings-held-in-dusseldorf",
            NOTE4_ADAPTATION_ID,
        }
    ]
    if len(note_relations) != 3 or any(row.get("qualifiers", {}).get("relation_candidate") is not True for row in note_relations):
        raise ValueError("p.82 note 3/4 relation updates are incomplete")

    _, body_text = source_segment(BODY_SEGMENT)
    segment_row, _ = source_segment(NOTE_SEGMENT)
    note_lines = (ROOT / segment_row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    note_text = "\n".join(note_lines[int(segment_row["line_start"]) - 1:int(segment_row["line_end"])])
    if hashlib.sha256(note_text.encode("utf-8")).hexdigest() != segment_row["sha256"]:
        raise ValueError("note segment text hash mismatch")
    for row in mentions:
        if row["segment_id"] not in {BODY_SEGMENT, NOTE_SEGMENT}:
            continue
        text = body_text if row["segment_id"] == BODY_SEGMENT else note_text
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise ValueError(f"mention anchor mismatch: {row['mention_id']}")
    for row in statements:
        if row.get("segment_id") not in {BODY_SEGMENT, NOTE_SEGMENT}:
            continue
        q = row.get("qualifiers", {})
        source_file = ROOT / row["source_file"]
        source_lines = source_file.read_text(encoding="utf-8-sig").splitlines()
        start, end = int(q["source_line_start"]), int(q["source_line_end"])
        anchor = "\n".join(source_lines[start - 1:end])
        if row["original_quote"] not in anchor:
            raise ValueError(f"statement quote not found in declared source lines: {row['statement_id']}")

    all_true = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in statements)
    bilateral = [
        row for row in statements
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
    ]
    bilateral_true = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in bilateral)
    bilateral_false = sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in bilateral)
    open_true = sum(
        row.get("qualifiers", {}).get("relation_candidate") is True
        and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
        for row in statements
    )
    summary = {
        "statements": len(statements),
        "candidates": len(candidates),
        "mentions": len(mentions),
        "relation_candidates": all_true,
        "bilateral": len(bilateral),
        "bilateral_relation_candidates": bilateral_true,
        "bilateral_nonrelations": bilateral_false,
        "bilateral_unclassified": len(bilateral) - bilateral_true - bilateral_false,
        "open_relation_candidates": open_true,
    }
    expected = {
        "statements": 12791,
        "candidates": 11586,
        "mentions": 27524,
        "relation_candidates": 5008,
        "bilateral": 8586,
        "bilateral_relation_candidates": 4956,
        "bilateral_nonrelations": 479,
        "bilateral_unclassified": 3151,
        "open_relation_candidates": 52,
    }
    if summary != expected:
        raise ValueError(f"postwrite global counts differ: {summary!r}")
    return summary


def collections_counter(values: list) -> dict:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return result


def show_preview(before: dict[str, list[dict]], after: dict[str, list[dict]], summary: dict) -> None:
    print("DRY-RUN: no table files written")
    print("planned summary:", json.dumps(summary, ensure_ascii=False, sort_keys=True))
    print("remove mentions:", ", ".join(sorted(REMOVE_MENTION_IDS)))
    print("add mentions:", NEW_MENTION_ID)
    print("add candidates:", ", ".join(sorted(NEW_CANDIDATE_IDS)))
    print("add statements:", ", ".join(sorted(NEW_STATEMENT_IDS)))
    print("corrected body segment: 22 statements, 20 relation candidates, 2 nonrelations")
    print("split note 3 location statement into Berlin and Dusseldorf endpoints")
    for key in ("statements", "candidates", "mentions"):
        old_rows = before[key]
        new_rows = after[key]
        id_field = {"statements": "statement_id", "candidates": "candidate_id", "mentions": "mention_id"}[key]
        old_map = {row[id_field]: row for row in old_rows}
        new_map = {row[id_field]: row for row in new_rows}
        changed = [identity for identity in new_map.keys() & old_map.keys() if new_map[identity] != old_map[identity]]
        added = sorted(new_map.keys() - old_map.keys())
        removed = sorted(old_map.keys() - new_map.keys())
        print(f"{key}: changed={len(changed)} added={added} removed={removed}")
        for identity in sorted(changed):
            print("  UPDATED", identity)


def apply_changes(proposed: dict[Path, bytes], summary: dict) -> None:
    for path, expected in EXPECTED_HASHES.items():
        if digest(path) != expected:
            raise ValueError(f"write-time hash mismatch for {path.relative_to(ROOT)}")
    backups_written: list[Path] = []
    temp_paths: dict[Path, Path] = {}
    try:
        for path, backup in BACKUPS.items():
            if not backup.exists():
                shutil.copy2(path, backup)
            if digest(backup) != EXPECTED_HASHES[path]:
                raise ValueError(f"backup verification failed: {backup.name}")
            backups_written.append(backup)
        for path, data in proposed.items():
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=path.name + ".tmp-", dir=path.parent, delete=False
            ) as handle:
                handle.write(data)
                temp_paths[path] = Path(handle.name)
        for path, temp_path in temp_paths.items():
            temp_path.replace(path)
        post = {
            STATEMENTS: digest(STATEMENTS),
            CANDIDATES: digest(CANDIDATES),
            MENTIONS: digest(MENTIONS),
        }
        written = {
            STATEMENTS: proposed[STATEMENTS],
            CANDIDATES: proposed[CANDIDATES],
            MENTIONS: proposed[MENTIONS],
        }
        for path in post:
            if hashlib.sha256(written[path]).hexdigest() != post[path]:
                raise ValueError(f"postwrite hash mismatch for {path.relative_to(ROOT)}")
        actual = {
            "statements": read_jsonl(STATEMENTS),
            "candidates": read_csv(CANDIDATES)[1],
            "mentions": read_csv(MENTIONS)[1],
        }
        actual_summary = validate_rows(actual)
        if actual_summary != summary:
            raise ValueError("postwrite data differs from planned summary")
        print("APPLY SUCCEEDED")
        for path, value in post.items():
            print(value, path.relative_to(ROOT))
        for backup in backups_written:
            print("recovery copy:", backup.relative_to(ROOT), digest(backup))
    except Exception:
        for path, backup in BACKUPS.items():
            if backup.exists() and path in proposed:
                shutil.copy2(backup, path)
        raise
    finally:
        for temp_path in temp_paths.values():
            if temp_path.exists():
                temp_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflights and backups")
    args = parser.parse_args()
    preflight()
    changes, before, after = build_changes()
    summary = validate_rows(after)
    show_preview(before, after, summary)
    if args.apply:
        apply_changes(changes, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
