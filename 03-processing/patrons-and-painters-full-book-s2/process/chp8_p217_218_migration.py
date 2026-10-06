"""Controlled S2 migration for Chapter 8 printed pages 217-218.

Default invocation performs a read-only preflight. The canonical OCR remains
unchanged; visual corrections are recorded in S2 qualifiers.
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
NOTES_SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8.md"
SEGMENTS_PATH = TABLES / "segments.jsonl"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
BACKUP_SUFFIX = ".bak-s2-chp8-p217-218-20261001"

P216 = "chp-8:08_CHP-8_sec_ii:l21-35"
P217 = "chp-8:08_CHP-8_sec_ii:l69-76"
P218 = "chp-8:08_CHP-8_sec_ii:l78-84"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P217, P218, NOTES}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(SEGMENTS_PATH)
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments):
    raise SystemExit("segments.jsonl contains duplicate segment IDs")
if not TARGET_IDS | {P216} <= set(segment_by_id):
    raise SystemExit("one or more source segments are missing")

for segment_id in TARGET_IDS | {P216}:
    meta = segment_by_id[segment_id]
    if hashlib.sha256((ROOT / meta["source_file"]).read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_lines = NOTES_SOURCE.read_text(encoding="utf-8-sig").splitlines()
candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
mention_fields, mention_rows = read_csv(MENTION_PATH)
statement_rows = read_jsonl(STATEMENT_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

for segment_id in (P217, P218):
    current = coverage_by_id.get(segment_id)
    if not current or (current["disposition"], current["migration_status"]) != ("queued", "pending"):
        raise SystemExit(f"expected queued/pending coverage: {segment_id}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-374":
    raise SystemExit("notes segment has changed since p.215 note migration; inspect before proceeding")
if any(row["segment_id"] in {P217, P218} for row in mention_rows):
    raise SystemExit("mentions already exist for a body segment; inspect before rerunning")
if any(row["segment_id"] in {P217, P218} for row in statement_rows):
    raise SystemExit("statements already exist for a body segment; inspect before rerunning")
if any(row["segment_id"] == NOTES and row["qualifiers"].get("source_line_start", 0) >= 375
       for row in statement_rows):
    raise SystemExit("p.217/218 note statements already exist; inspect before rerunning")


def segment_text(segment_id):
    meta = segment_by_id[segment_id]
    lines = source_lines if meta["source_file"].endswith("08_CHP-8_sec_ii.md") else notes_lines
    return "\n".join(lines[meta["line_start"] - 1:meta["line_end"]])


def lines_quote(segment_id, first, last):
    lines = source_lines if segment_by_id[segment_id]["source_file"].endswith("08_CHP-8_sec_ii.md") else notes_lines
    return "\n".join(lines[first - 1:last])


new_candidates = [
    ["cand-7662", "", "Palazzo Pitti", "", "place", "open", "", "", "",
     "Named as the site of Pietro da Cortona's frescoes being completed by Ciro Ferri; no further location or commission details are inferred.",
     "body-mention", f"{P217}#L75"],
    ["cand-7663", "", "Sixteen-picture decoration scheme for the northern transept and doors of Santa Maria Maggiore, Bergamo", "", "work", "open", "", "", "",
     "The group of sixteen pictures contracted first to Pietro Liberi and later to Ciro Ferri; keep this group distinct from the 1653 general decoration programme and from named individual paintings.",
     "body-mention", f"{P217}#L70"],
    ["cand-7664", "", "The Flood (Pietro Liberi painting for Santa Maria Maggiore, Bergamo)", "", "work", "open", "", "", "",
     "Liberi's first canvas for the sixteen-picture church commission. Haskell reports that it was repainted after the committee's objection and placed above the south door; no external identity or current condition is asserted.",
     "body-mention", f"{P217}#L71"],
    ["cand-7665", "", "The Last Judgement (Pietro Liberi sketch for Santa Maria Maggiore, Bergamo)", "", "work", "open", "", "", "",
     "The second subject in Liberi's commission, for which he sent a sketch rather than a completed painting; Haskell says the committee rejected it and cancelled the contract.",
     "body-mention", f"{P217}#L72"],
    ["cand-7666", "", "Committee letter to Pietro Liberi objecting to The Flood", "", "archive", "open", "", "", "",
     "An undated letter sent by the Santa Maria Maggiore committee after rejecting the first canvas; sender is attributed collectively to the committee, and the letter itself has not been independently consulted.",
     "body-mention", f"{P217}#L72"],
    ["cand-7667", "", "Ciro Ferri's private letters about the Santa Maria Maggiore commission", "", "archive", "open", "", "", "",
     "Haskell quotes Ferri's private correspondence about the commission, including his assessment of the large picture and his impatience. Dates, recipients, and the mapping of quotations to individual letters are not supplied here.",
     "body-mention", f"{P218}#L80"],
    ["cand-7668", "", "Crossing of the Red Sea (large picture planned for Santa Maria Maggiore by Ciro Ferri)", "", "work", "open", "", "", "",
     "The intended subject of the large picture over a door in Ferri's commission. This passage does not unambiguously identify which contracted oil painting was completed.",
     "body-mention", f"{P218}#L80"],
    ["cand-7669", "", "Two unidentified large door paintings remaining after Ciro Ferri left Santa Maria Maggiore", "", "work", "open", "", "", "",
     "The two large pictures for the north and west doors still to be painted after Ferri left; their subjects and later completion are not specified in this passage.",
     "body-mention", f"{P218}#L84"],
    ["cand-7670", "", "Moses striking the Rock (Antonio Zanchi painting for Santa Maria Maggiore, Bergamo)", "", "work", "open", "", "", "",
     "A specific painting accepted by the committee from Zanchi for the remaining decoration; keep distinct from Vannini's separate Del Rosso-house painting with the same biblical subject (cand-7530).",
     "body-mention", f"{P218}#L84"],
    ["cand-7671", "", "Cappella Colleoni adjoining Santa Maria Maggiore, Bergamo", "", "place", "open", "", "", "",
     "Named as the chapel adjoining the side-door site of a painting in Ferri's commission; no further building identity is asserted.",
     "body-mention", f"{P218}#L83"],
    ["cand-7672", "", "Inner wall of the northern transept of Santa Maria Maggiore, Bergamo", "", "place", "open", "", "", "",
     "Interior site identified for one of the remaining pictures; distinct from the northern transept as a whole.",
     "body-mention", f"{P218}#L84"],
    ["cand-7673", "", "Side door adjoining the Cappella Colleoni at Santa Maria Maggiore, Bergamo", "", "place", "open", "", "", "",
     "Location for a picture whose quality the committee questioned in 1667; exact orientation of the door is not supplied.",
     "body-mention", f"{P218}#L83"],
    ["cand-7674", "", "Main north door of Santa Maria Maggiore, Bergamo", "", "place", "open", "", "", "",
     "One of the two main doors identified as a picture location in the northern transept scheme.",
     "body-mention", f"{P217}#L70"],
    ["cand-7675", "", "Main west door of Santa Maria Maggiore, Bergamo", "", "place", "open", "", "", "",
     "One of the two door locations identified for the two remaining large pictures after Ferri left.",
     "body-mention", f"{P218}#L84"],
    ["cand-7676", "", "Committee letters urging Antonio Zanchi to finish his canvas", "", "archive", "open", "", "", "",
     "Plural letters mentioned by Haskell as pressing Zanchi to hurry; dates, senders, and individual documents are unspecified.",
     "body-mention", f"{P218}#L84"],
    ["cand-7677", "", "Old Testament", "", "term", "open", "", "", "",
     "The scriptural corpus named as the subject matter of Ferri's frescoes; no specific narrative cycle is inferred beyond the source wording.",
     "body-mention", f"{P218}#L81"],
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
new_candidate_ids = [row[0] for row in new_candidates]
if len(set(new_candidate_ids)) != len(new_candidate_ids) or candidate_ids.intersection(new_candidate_ids):
    raise SystemExit("duplicate candidate IDs")
if max(int(cid.split("-")[1]) for cid in candidate_ids) != 7661:
    raise SystemExit("candidate sequence changed; allocate IDs from the current table")
candidate_ids.update(new_candidate_ids)

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_mention_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


def mention(segment_id, mention_id, candidate_id, surface, note, occurrence=0):
    if mention_id in existing_mention_ids or any(r["mention_id"] == mention_id for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    text = segment_text(segment_id)
    starts = []
    at = 0
    while True:
        found = text.find(surface, at)
        if found < 0:
            break
        starts.append(found)
        at = found + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention surface occurrence not found: {segment_id} {surface!r} #{occurrence}")
    start = starts[occurrence]
    key = (segment_id, str(start), str(start + len(surface)))
    if key in existing_mention_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == key for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {key}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
    })


# Printed p.217: close the p.216 north-transept sentence and process the Liberi episode.
mention(P217, "m-chp8-p217-scheme-south", "cand-7643", "those in the south", "Anaphoric reference to the southern transept paintings.")
mention(P217, "m-chp8-p217-scheme-north-door", "cand-7674", "main North", "Location phrase for one of the two main doors; the source capitalizes North.")
mention(P217, "m-chp8-p217-scheme-south-door", "cand-7631", "South doors", "Location phrase for the main south door; reuse the church south-entrance candidate.")
mention(P217, "m-chp8-p217-guercino", "cand-1258", "Guercino", "Earlier painter whose reluctance contextualizes the revised placement plan.")
mention(P217, "m-chp8-p217-milan", "cand-3418", "Milan", "City previously approached for artists in the first stage.")
mention(P217, "m-chp8-p217-venice-1", "cand-3401", "Venice", "City selected as the committee's next source of artists.")
mention(P217, "m-chp8-p217-liberi-1", "cand-1401", "Pietro Liberi", "Artist contracted in 1660.")
mention(P217, "m-chp8-p217-smm", "cand-7627", "Santa Maria Maggiore", "Church commissioning the decoration.")
mention(P217, "m-chp8-p217-sixteen", "cand-7663", "entire sixteen pictures", "The sixteen-picture commission contracted to Liberi.")
mention(P217, "m-chp8-p217-flood-1", "cand-7664", "The\nFlood", "Title split across an OCR line break; first canvas in Liberi's contract.")
mention(P217, "m-chp8-p217-bergamo-1", "cand-6208", "Bergamo", "City where the first canvas arrived.")
mention(P217, "m-chp8-p217-committee-1", "cand-7641", "the committee", "Committee that rejected the first canvas.")
mention(P217, "m-chp8-p217-liberi-letter", "cand-7666", "A cold letter", "Specific undated committee letter concerning The Flood.")
mention(P217, "m-chp8-p217-liberi-2", "cand-1401", "Liberi", "Recipient of the committee's letter.")
mention(P217, "m-chp8-p217-bergamo-2", "cand-6208", "Bergamo", "Arrival location for Liberi after the committee's letter.", occurrence=1)
mention(P217, "m-chp8-p217-south-door-placement", "cand-7631", "South door", "Reported location of The Flood after repainting.")
mention(P217, "m-chp8-p217-venice-2", "cand-3401", "Venice", "Liberi's return destination.", occurrence=1)
mention(P217, "m-chp8-p217-last-judgement-1", "cand-7665", "The Last Judgement", "Second subject in Liberi's commission.")
mention(P217, "m-chp8-p217-committee-2", "cand-7641", "The committee", "Committee rejecting the sketch and cancelling Liberi's contract.")
mention(P217, "m-chp8-p217-bergamasque", "cand-6208", "Bergamasque", "Regional adjective; linked to Bergamo as a geographic origin, not a separate polity.")
mention(P217, "m-chp8-p217-liberi-3", "cand-1401", "Pietro Liberi", "Artist discussed in Haskell's explanation of the hostile reception.", occurrence=1)
mention(P217, "m-chp8-p217-flood-4", "cand-7664", "The Flood", "Subject named in Haskell's interpretation of Liberi's erotic imagery.")
mention(P217, "m-chp8-p217-last-judgement-2", "cand-7665", "The Last Judgement", "Subject named in Haskell's interpretation of Liberi's erotic imagery.", occurrence=1)
mention(P217, "m-chp8-p217-venice-3", "cand-3401", "Venice", "Failure of the committee's attempts in Venice.", occurrence=2)
mention(P217, "m-chp8-p217-ferri-1", "cand-1027", "Ciro Ferri", "Painter selected to replace Liberi.")
mention(P217, "m-chp8-p217-liberi-4", "cand-1401", "Pietro Liberi", "Predecessor Ferri was selected to replace.", occurrence=2)
mention(P217, "m-chp8-p217-cortona-1", "cand-0342", "Pietro da Cortona", "Named as Ferri's master and artistic model.")
mention(P217, "m-chp8-p217-florence-1", "cand-3397", "Florence", "City where Ferri was completing the frescoes.")
mention(P217, "m-chp8-p217-florence-2", "cand-3397", "Florence", "City Ferri says he cannot leave immediately.", occurrence=1)
mention(P217, "m-chp8-p217-master-frescoes", "cand-0365", "his master’s frescoes", "Pietro da Cortona's fresco work at Palazzo Pitti.")
mention(P217, "m-chp8-p217-pitti", "cand-7662", "Palazzo Pitti", "Named site of Pietro da Cortona's frescoes.")
mention(P217, "m-chp8-p217-bergamo-3", "cand-6208", "Bergamo", "Destination of Ferri's requested visit.", occurrence=2)

# Printed p.218: continue the Ferri invitation, process the contract, departure, and Zanchi replacement.
mention(P218, "m-chp8-p218-bergamo-1", "cand-6208", "Bergamo", "City Ferri reaches after the invitation exchange.")
mention(P218, "m-chp8-p218-sketch-artist", "cand-1027", "Ciro Ferri", "Artist preparing sketches for committee approval.")
mention(P218, "m-chp8-p218-committee-1", "cand-7641", "the committee", "Committee approving the sketches.")
mention(P218, "m-chp8-p218-ferri-16", "cand-7663", "sixteen pictures", "Same northern-transept decoration scheme as Liberi's earlier contract.")
mention(P218, "m-chp8-p218-ferri-letters", "cand-7667", "private letters", "Unspecified private correspondence by Ferri; no date or recipient inferred.")
mention(P218, "m-chp8-p218-ferri-pleasure", "cand-1027", "Ferri", "Writer of the quoted private correspondence.", occurrence=1)
mention(P218, "m-chp8-p218-fresco-sites", "cand-7644", "sites for the frescoes", "Sites within the northern-transept decoration; exact individual surfaces are not enumerated here.")
mention(P218, "m-chp8-p218-crossing", "cand-7668", "Crossing of the Red Sea", "Intended subject of the large overdoor picture.")
mention(P218, "m-chp8-p218-moses", "cand-4144", "Moses", "Biblical figure named within Ferri's description of the composition.")
mention(P218, "m-chp8-p218-old-testament", "cand-7677", "Old Testament", "Scriptural corpus named as subject matter of the completed frescoes.")
mention(P218, "m-chp8-p218-cortona-style", "cand-0342", "Pietro’s style", "Stylistic referent is Pietro da Cortona; this is not modeled as a formal teacher-pupil relation.")
mention(P218, "m-chp8-p218-oil-paintings", "cand-7663", "one of the large oil paintings", "One of two oil paintings within the sixteen-picture commission.")
mention(P218, "m-chp8-p218-committee-2", "cand-7641", "the committee", "Committee consulting experts about a painting's quality.", occurrence=1)
mention(P218, "m-chp8-p218-side-door", "cand-7673", "side door adjoining the Colleoni chapel", "Specific picture site queried by the committee.")
mention(P218, "m-chp8-p218-chapel", "cand-7671", "Colleoni chapel", "Named chapel adjoining the door.")
mention(P218, "m-chp8-p218-ferri-2", "cand-1027", "Ciro Ferri", "Painter who left Bergamo before completing the contract.", occurrence=1)
mention(P218, "m-chp8-p218-bergamo-3", "cand-6208", "Bergamo", "City Ferri left.", occurrence=1)
mention(P218, "m-chp8-p218-unfinished-two", "cand-7669", "two large ones", "The unnamed North- and West-door pictures remaining after Ferri left.")
mention(P218, "m-chp8-p218-north-door", "cand-7674", "North", "One of the two door locations.")
mention(P218, "m-chp8-p218-west-door", "cand-7675", "West doors", "The second door location.")
mention(P218, "m-chp8-p218-inner-wall", "cand-7672", "inner wall of the North transept", "Location of the smaller remaining picture.")
mention(P218, "m-chp8-p218-committee-3", "cand-7641", "The committee", "Committee selecting the next painter.")
mention(P218, "m-chp8-p218-zanchi", "cand-2834", "Antonio Zanchi", "Painter accepted for the remaining commission.")
mention(P218, "m-chp8-p218-moses-work", "cand-7670", "Moses striking the Rock", "Specific Zanchi painting; distinct from Vannini's Del Rosso-house painting.")
mention(P218, "m-chp8-p218-bergamo-4", "cand-6208", "Bergamo", "Place where the painting would be made under the first proposed terms.", occurrence=2)
mention(P218, "m-chp8-p218-committee-4", "cand-7641", "the cautious committee", "Committee deciding whether to accept the completed canvas.")
mention(P218, "m-chp8-p218-zanchi-letters", "cand-7676", "letters complaining of the delay", "Unspecified correspondence urging Zanchi to hurry.")
mention(P218, "m-chp8-p218-venice", "cand-3401", "Venice", "City where Zanchi received permission to paint.")


def make_statement(statement_id, segment_id, first_line, last_line, subject, obj, predicate,
                   claim, qualification, mentioned, page, physical, speaker="Haskell",
                   text_layer="body", extras=None):
    qualifiers = {
        "source_line_start": first_line, "source_line_end": last_line,
        "printed_page": page, "pdf_physical_page": physical,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": lines_quote(segment_id, first_line, last_line),
        "origin": "book",
        "source_file": segment_by_id[segment_id]["source_file"],
    }


new_statements = [
    make_statement("st-chp8-p217-north-transept-scheme", P217, 70, 70, "cand-7641", "cand-7663",
                   "decoration_scheme_requirements",
                   "The committee's northern-transept scheme required thirteen pictures corresponding to the southern ones, one on the inner wall, and two over the main north and south doors, in response to Guercino's reluctance.",
                   "Closes the sentence begun at p.216 L35. The source's count and placement plan are preserved; no individual authorship is assigned.",
                   ["cand-7641", "cand-7643", "cand-7644", "cand-7663", "cand-7674", "cand-7631", "cand-1258"],
                   217, 19, extras={"continued_from_segment_id": P216, "continued_from_source_line": 35,
                                    "continuation_status": "closed", "continuation_resolved_by_statement_id": "st-chp8-p216-next-north-transept-phase-open"}),
    make_statement("st-chp8-p217-liberi-contract", P217, 71, 71, "cand-1401", "cand-7663",
                   "painting_contract",
                   "In 1660 Pietro Liberi contracted to paint the sixteen pictures for 3,800 ducats, receiving 500 ducats as an advance; Haskell says the committee had turned from Milan to Venice and calls Liberi the best-known artist in Venice at the time.",
                   "Preserve the reported contract values and Haskell's description. The text does not identify a surviving contract document.",
                   ["cand-1401", "cand-7663", "cand-3418", "cand-3401", "cand-7627"],
                   217, 19, extras={"qualification_terms": ["at that time", "best known in the city"]}),
    make_statement("st-chp8-p217-flood-rejected", P217, 71, 72, "cand-7641", "cand-7664",
                   "painting_rejected_and_rework_requested",
                   "Seven months after the contract, Liberi's first canvas, The Flood, arrived in Bergamo; the committee rejected it, sent a letter demanding a satisfactory repainting, and suspended work and payments on the other contracted pictures.",
                   "The letter is known here only through Haskell's report; the quoted complaint is not independently verified against the document.",
                   ["cand-1401", "cand-7663", "cand-7664", "cand-6208", "cand-7641", "cand-7666"],
                   217, 19, extras={"footnote_markers": []}),
    make_statement("st-chp8-p217-flood-repainted-placed", P217, 72, 72, "cand-1401", "cand-7664",
                   "painting_repainted_and_placed",
                   "Haskell reports that Liberi arrived in Bergamo a year after the first canvas, repainted The Flood as demanded, and that the painting was placed above the south door, where it still was at the time of his account.",
                   "No exact year is supplied for the repainting or placement; 'still is' is Haskell's time-bound report, not a claim about present location.",
                   ["cand-1401", "cand-7664", "cand-6208", "cand-7631", "cand-7627"],
                   217, 19, extras={"qualification_terms": ["a year", "still is"]}),
    make_statement("st-chp8-p217-last-judgement-cancelled", P217, 72, 72, "cand-1401", "cand-7665",
                   "sketch_rejected_and_contract_cancelled",
                   "For the second picture, The Last Judgement, Liberi sent a sketch rather than a finished painting; the committee found it deficient and cancelled his contract.",
                   "The account describes a rejected sketch and cancellation, not an executed painting.",
                   ["cand-1401", "cand-7663", "cand-7665", "cand-7641"], 217, 19),
    make_statement("st-chp8-p217-liberi-reception-uncertain-cause", P217, 73, 74, "cand-1401", None,
                   "authorial_interpretation_of_rejection",
                   "Haskell says the precise reason for the hostile reception of Liberi's canvases is unknowable; he considers stylistic objection uncommon among the clerical patrons and suggests that the erotic nudes may have offended Bergamasque sensibilities, while judging that Liberi used the two subjects to full advantage.",
                   "This is explicitly Haskell's interpretation, including the probable-cause language and evaluation of Liberi. It is not a documented statement by the committee.",
                   ["cand-1401", "cand-7664", "cand-7665", "cand-6208", "cand-3401"],
                   217, 19, extras={"qualification_terms": ["unfortunately", "more likely", "must have seemed", "most probable", "we can be sure"]}),
    make_statement("st-chp8-p217-ferri-selected-invited-open", P217, 75, 76, "cand-7641", "cand-1027",
                   "replacement_artist_selected_and_invited",
                   "After the failure in Venice the committee selected Ciro Ferri to replace Liberi; Haskell describes Ferri as Pietro da Cortona's most faithful follower, then completing Cortona's frescoes in Palazzo Pitti, and says he was asked to come to Bergamo.",
                   "The invitation closes within L76; Ferri's separate inability-to-leave and request-for-materials clause continues to p.218 L79. 'Follower' is Haskell's stylistic description and is not converted into a formal teacher-pupil relation.",
                   ["cand-7641", "cand-1027", "cand-1401", "cand-0342", "cand-3397", "cand-7662", "cand-6208"],
                   217, 19, extras={"footnote_markers": [1], "footnote_link_status": "linked",
                                    "footnote_segment": NOTES, "footnote_target_line": 375,
                                    "footnote_citation_statement_ids": ["st-chp8-p217-bottari-citation"],
                                    "footnote_pending": False}),
    make_statement("st-chp8-p217-ferri-cannot-leave-open", P217, 76, 76, "cand-1027", "cand-7641",
                   "invitation_response_and_request_for_materials",
                   "Ferri replied that he could not leave Florence immediately and asked the committee to send the measurements, subjects, and other details so he could begin the sketches.",
                   "The final clause ends at 'at' in this segment and is completed at p.218 L79; the timing of his unavailability is not specified.",
                   ["cand-1027", "cand-3397", "cand-7641"],
                   217, 19, extras={"continuation_to_segment_id": P218, "continuation_to_source_line": 79,
                                    "continuation_fragment": "at once begin work on the sketches",
                                    "continuation_status": "open"}),
    make_statement("st-chp8-p217-bottari-citation", NOTES, 375, 375, None, None,
                   "footnote_citation",
                   "Footnote 1 points to a number of letters published by Bottari, volume II pages 47-56 and volume III pages 352-4.",
                   "The p.217 page image reads II where S0 OCR has H. This is a citation locator; the letters and cited pages have not been independently consulted, and the note does not identify which letter supports each nearby claim.",
                   ["cand-7516", "cand-5461"],
                   217, 19, text_layer="bibliographic citation",
                   extras={"printed_page_locator": "p.217 n.1", "footnote_marker": 1,
                           "ocr_corrections": [{"source_file": NOTES_SOURCE.relative_to(ROOT).as_posix(), "source_line": 375,
                                                "ocr": "Bottari, H", "print": "Bottari, II",
                                                "basis": "CHP-8.pdf physical page 19."}],
                           "footnote_body_link_status": "linked",
                           "linked_body_statement_ids": ["st-chp8-p217-ferri-selected-invited-open",
                                                         "st-chp8-p217-ferri-cannot-leave-open",
                                                         "st-chp8-p218-ferri-private-letters-and-subject",
                                                         "st-chp8-p218-ferri-schedule-and-work-progress"]}),
    make_statement("st-chp8-p218-ferri-invitation-response", P218, 79, 79, "cand-1027", "cand-7641",
                   "invitation_response_and_sketch_submission",
                   "Ferri asked for the dimensions and subjects so that he could begin sketches for the committee's approval; this was agreed, although delay followed and relations between the artist and patrons cooled.",
                   "Continues the request made at p.217 L76. The names and contents of any sketches are not specified.",
                   ["cand-1027", "cand-7641", "cand-6208"], 218, 20,
                   extras={"continued_from_segment_id": P217, "continued_from_source_line": 76,
                           "continued_from_statement_id": "st-chp8-p217-ferri-cannot-leave-open",
                           "continuation_status": "closed"}),
    make_statement("st-chp8-p218-ferri-arrival-contract", P218, 79, 80, "cand-1027", "cand-7663",
                   "painting_contract",
                   "Ciro Ferri arrived in Bergamo in September 1665 and signed in December to paint the sixteen pictures partly in oil and partly in fresco.",
                   "The source reports contract timing and medium but does not supply the contract text.",
                   ["cand-1027", "cand-6208", "cand-7663", "cand-7627"], 218, 20),
    make_statement("st-chp8-p218-ferri-private-letters-and-subject", P218, 80, 81, "cand-1027", "cand-7668",
                   "reported_private_letters_and_planned_picture",
                   "Haskell says Ferri's private letters conveyed pleasure but noted that the fresco sites were too small; the large overdoor picture was to represent the Crossing of the Red Sea, which Ferri called his grandest composition and described as including Hebrews who had crossed and Moses raising his rod.",
                   "The letter dates and recipients are not supplied, and the quoted wording is transmitted through Haskell. The subject is a plan; this passage does not conclusively identify the specific completed oil painting.",
                   ["cand-1027", "cand-7667", "cand-7668", "cand-7644", "cand-4144", "cand-7663"],
                   218, 20, speaker="Ciro Ferri, quoted by Haskell",
                   text_layer="authorial report with nested quotation",
                   extras={"qualification_terms": ["was to represent", "grandest composition"]}),
    make_statement("st-chp8-p218-ferri-schedule-and-work-progress", P218, 81, 82, "cand-1027", "cand-7663",
                   "estimated_duration_and_work_progress",
                   "Ferri estimated about two and a half years for the commission; Haskell reports that four frescoes were complete by May 1666 and six more by November, then quotes Ferri saying he was working day and night but bored and unable to stay longer.",
                   "The OCR phrase 'T ana' is read as 'I am' in the page image and retained unchanged in original_quote. The dates and counts are Haskell's reported chronology; the first-person words are attributed to Ferri.",
                   ["cand-1027", "cand-7663", "cand-7667"],
                   218, 20, extras={"ocr_corrections": [{"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 81,
                                                        "ocr": "T ana working day and night", "print": "I am working day and night",
                                                        "basis": "CHP-8.pdf physical page 20."}]}),
    make_statement("st-chp8-p218-ferri-completion-status-1667", P218, 82, 82, "cand-1027", "cand-7663",
                   "commission_progress_and_partial_completion",
                   "By June 1667, eighteen months after Ferri's arrival, Haskell says all thirteen frescoed compartments were complete, one of the large oil paintings was finished, and the second was still awaited so the pair could be shown together.",
                   "The statement does not identify which large oil picture was finished or assert completion of the second; Haskell's negative stylistic evaluation is attributed to him.",
                   ["cand-1027", "cand-7663", "cand-0342", "cand-7668"],
                   218, 20, extras={"qualification_terms": ["nearly over", "mannered", "insipid"]}),
    make_statement("st-chp8-p218-ferri-leaves", P218, 83, 83, "cand-7641", "cand-1027",
                   "painting_quality_review_and_artist_departure",
                   "In September the committee questioned the quality of a picture intended above the side door adjoining the Colleoni chapel and consulted experts; Ferri angrily left Bergamo before completing his contract.",
                   "The picture's identity and the experts are not named; no conclusion about the unfinished work's later fate is drawn.",
                   ["cand-7641", "cand-1027", "cand-7673", "cand-7671", "cand-6208"],
                   218, 20),
    make_statement("st-chp8-p218-zanchi-selected-for-moses", P218, 84, 84, "cand-7641", "cand-7670",
                   "replacement_painting_commission",
                   "After Ferri left, three pictures remained: two large works for the north and west doors and a smaller one for the northern transept inner wall. The committee accepted Antonio Zanchi to paint Moses striking the Rock.",
                   "This does not identify the two large pictures' subjects or establish their later completion. Distinguish the Zanchi painting from Vannini's same-subject work at another site.",
                   ["cand-7641", "cand-1027", "cand-7669", "cand-7674", "cand-7675", "cand-7672", "cand-2834", "cand-7670"],
                   218, 20, extras={"footnote_markers": [1], "footnote_link_status": "linked",
                                    "footnote_segment": NOTES, "footnote_target_line": 376,
                                    "footnote_citation_statement_ids": ["st-chp8-p218-bottari-citation"],
                                    "footnote_pending": False,
                                    "ocr_corrections": [{"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 84,
                                                         "ocr": "Moses striking the RockJ", "print": "Moses striking the Rock¹",
                                                         "basis": "CHP-8.pdf physical page 20."}]}),
    make_statement("st-chp8-p218-zanchi-terms", P218, 84, 84, "cand-7641", "cand-7670",
                   "conditional_payment_and_acceptance_terms",
                   "Zanchi was to receive no fee for submitting drawings; even an approved picture painted in Bergamo could be returned without payment if judged unsatisfactory, while experts would set the price only if it were accepted.",
                   "Terms are reported by Haskell as exceptionally hard; the source does not provide the contract document or name the experts.",
                   ["cand-7641", "cand-2834", "cand-7670", "cand-6208"],
                   218, 20),
    make_statement("st-chp8-p218-zanchi-canvas-accepted", P218, 84, 84, "cand-2834", "cand-7670",
                   "painting_execution_and_acceptance",
                   "Zanchi agreed to the terms, obtained permission to paint the canvas in Venice, completed it within four months after letters urged him to hurry, and the committee accepted it enthusiastically and paid 825 ducats.",
                   "The concluding evaluative praise ('well deserved') is Haskell's judgment. The source page ends mid-sentence after 'richly'; the remaining description continues on p.219.",
                   ["cand-2834", "cand-7670", "cand-3401", "cand-7641", "cand-7676"],
                   218, 20, extras={"continuation_to_segment_id": "chp-8:08_CHP-8_sec_ii:l87-95",
                                    "continuation_to_source_line": 87,
                                    "continuation_fragment": "richly", "continuation_status": "open"}),
    make_statement("st-chp8-p218-bottari-citation", NOTES, 376, 376, None, None,
                   "footnote_citation",
                   "Footnote 1 cites Bottari, volume III, pages 355-6.",
                   "The page image reads III where S0 OCR has HI. The cited pages have not been independently consulted; this locator does not validate the nearby attribution or commission details.",
                   ["cand-5461"], 218, 20, text_layer="bibliographic citation",
                   extras={"printed_page_locator": "p.218 n.1", "footnote_marker": 1,
                           "ocr_corrections": [{"source_file": NOTES_SOURCE.relative_to(ROOT).as_posix(), "source_line": 376,
                                                "ocr": "Bottari, HI", "print": "Bottari, III",
                                                "basis": "CHP-8.pdf physical page 20."}],
                           "footnote_body_link_status": "linked",
                           "linked_body_statement_ids": ["st-chp8-p218-zanchi-selected-for-moses",
                                                         "st-chp8-p218-zanchi-terms",
                                                         "st-chp8-p218-zanchi-canvas-accepted"]}),
]

existing_statement_ids = {row["statement_id"] for row in statement_rows}
new_statement_ids = [row["statement_id"] for row in new_statements]
if len(set(new_statement_ids)) != len(new_statement_ids) or existing_statement_ids.intersection(new_statement_ids):
    raise SystemExit("duplicate statement ID")
for row in new_statements:
    if row["segment_id"] not in segment_by_id:
        raise SystemExit(f"statement source segment missing: {row['statement_id']}")
    text = segment_text(row["segment_id"])
    if row["original_quote"] not in text:
        raise SystemExit(f"statement quote is not an exact source span: {row['statement_id']}")
    for candidate_id in row["qualifiers"]["mentioned_candidate_ids"]:
        if candidate_id not in candidate_ids:
            raise SystemExit(f"missing statement candidate: {row['statement_id']} -> {candidate_id}")

coverage_updates = {
    P216: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L22-35",
        "note": "The p.216 sentence ending at 'thirteen' is closed by p.217 L70; see the linked continuation statement. The remainder of the p.216 passage and its existing mentions/statements are unchanged.",
    },
    P217: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L70-76",
        "note": "Printed p.217 body processed against CHP-8.pdf physical p.19. Closes the p.216 northern-transept count/placement sentence; records Liberi's 1660 contract, The Flood rejection and repainting, The Last Judgement sketch and cancellation, Haskell's qualified interpretation, and Ferri's invitation. Ferri's request and the final sentence continue on p.218; note 1 is separately covered at L375.",
    },
    P218: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L79-84",
        "note": "Printed p.218 body processed against CHP-8.pdf physical p.20. Continues Ferri's invitation response, contract, quoted letters, progress, departure and Zanchi's replacement commission. The source segment ends mid-sentence at 'richly' and continues on p.219; note 1 is separately covered at L376. OCR correction is recorded only in S2.",
    },
    NOTES: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L373-376",
        "note": "Adds p.217 n.1 (L375) and p.218 n.1 (L376), linked respectively to the Ferri and Zanchi body statements. The page images correct Bottari H to II and HI to III in S2 only; cited letters and pages were not independently consulted. Later notes L377-461 remain pending.",
    },
}

updated_coverage = []
for segment in segments:
    sid = segment["segment_id"]
    if sid in coverage_updates:
        updated_coverage.append({"chapter": segment["chapter"], "segment_id": sid, **coverage_updates[sid]})
    elif sid in coverage_by_id:
        updated_coverage.append(dict(coverage_by_id[sid]))
    else:
        raise SystemExit(f"coverage row missing: {sid}")
if {row["segment_id"] for row in updated_coverage} != set(segment_by_id):
    raise SystemExit("coverage and source segment IDs do not match")

by_id = {row["statement_id"]: row for row in statement_rows}
prior = by_id.get("st-chp8-p216-next-north-transept-phase-open")
if prior is None or prior["qualifiers"].get("continuation_status") not in {"open", None}:
    raise SystemExit("expected open p.216 continuation statement is missing or changed")
patched_prior = json.loads(json.dumps(prior, ensure_ascii=False))
patched_prior["qualifiers"].update({
    "continuation_status": "closed",
    "continuation_resolved_by_segment": P217,
    "continuation_resolved_by_source_line": 70,
    "continuation_resolved_by_statement_id": "st-chp8-p217-north-transept-scheme",
    "continuation_fragment": "paintings were required to correspond to those in the south",
})
patched_prior["qualifiers"].pop("continuation_in", None)

preview = {
    "mode": "dry-run", "candidate_additions": len(new_candidates),
    "mention_additions": len(new_mentions), "statement_additions": len(new_statements),
    "coverage_updates": list(coverage_updates), "coverage_total": len(updated_coverage),
    "prior_statement_updated": prior["statement_id"],
    "ocr_corrections": ["p.217 n.1 Bottari H -> II", "p.218 n.1 Bottari HI -> III",
                        "p.218 L81 T ana -> I am"],
    "open_continuations": [P217, P218],
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (CANDIDATE_PATH, MENTION_PATH, STATEMENT_PATH, COVERAGE_PATH):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

candidate_rows.extend(dict(zip(candidate_fields, row)) for row in new_candidates)
write_csv_atomic(CANDIDATE_PATH, candidate_fields, candidate_rows)
mention_rows.extend(new_mentions)
write_csv_atomic(MENTION_PATH, mention_fields, mention_rows)
statement_rows = [patched_prior if row["statement_id"] == prior["statement_id"] else row for row in statement_rows]
statement_rows.extend(new_statements)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENT_PATH.parent,
                                 delete=False, suffix=".tmp") as stream:
    for row in statement_rows:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary = Path(stream.name)
temporary.replace(STATEMENT_PATH)
write_csv_atomic(COVERAGE_PATH, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
