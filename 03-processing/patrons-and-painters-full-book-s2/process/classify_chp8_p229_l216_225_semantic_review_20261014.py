"""Guarded S2 semantic review for printed p.229, body lines 216-223 and note 2."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p229_review.png"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l216-225"
NEXT_SEGMENT = "chp-8:08_CHP-8_sec_ii:l227-236"
BACKUP_SUFFIX = ".bak-s2-chp8-p229-l216-225-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "0d51c488a2bd0c0b48fe460a3a3a1c1f645104c77baa6a444b67fd464f8065b0",
    CANDIDATES: "ce5b72264b5b831ea33452d807fad5539d98e8e3a70f824f8ef35e0bc600bafd",
    MENTIONS: "c7966d534d3915a6a136cab87dffe4a03196e666d5e56163cdf3375fd49492c1",
    COVERAGE: "607342f702dafa6672481b4d0e71703a0427fc2e898242d816f13ad4465117f1",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PAGE_IMAGE: "42cc35ddeb6a036f215a32a4fc064ffcfbce2921f5c6f71a6eb2fcfb7669a1a7",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    temporary.replace(path)


def fragment(line: str, start: str, end: str | None = None) -> str:
    a = line.find(start)
    if a < 0:
        raise SystemExit(f"source fragment not found: {start!r}")
    if end is None:
        return line[a:].rstrip()
    b = line.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f"source end fragment not found after {start!r}: {end!r}")
    return line[a:b].rstrip()


def new_statement(statement_id, subject, object_, predicate, lines, claim, quote, *,
                  relation, note, mentioned, speaker="Haskell", text_layer="body", extra=None):
    qualifiers = {
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 229, "pdf_physical_page": 31,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": note, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": note,
    }
    if extra:
        qualifiers.update(extra)
    return {"statement_id": statement_id, "segment_id": SEGMENT,
            "subject_candidate_id": subject, "object_candidate_id": object_,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote, "origin": "book", "source_file": SOURCE_REL}


def plan():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")
    segments = read_jsonl(SEGMENTS)
    by_segment = {row["segment_id"]: row for row in segments}
    meta = by_segment.get(SEGMENT)
    if not meta or (meta["line_start"], meta["line_end"]) != (216, 225):
        raise SystemExit("unexpected p.229 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[215:225])
    if sha(text.encode("utf-8")) != meta["sha256"]:
        raise SystemExit("p.229 source segment hash mismatch")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    coverage_fields, coverage = read_csv(COVERAGE)
    by_id = {row["statement_id"]: row for row in statements}
    target_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(target_rows) != 23:
        raise SystemExit(f"expected 23 migrated p.229 statements; got {len(target_rows)}")
    expected_unset = {
        "st-chp8-p229-brothers-personalities",
        "st-chp8-p229-character-reconsidered",
        "st-chp8-p229-ferdinand-character",
        "st-chp8-p229-ferdinand-patronage-quote",
        "st-chp8-p229-ferdinand-revival",
        "st-chp8-p229-florence-revival",
        "st-chp8-p229-heir-expectation",
        "st-chp8-p229-parental-climate",
        "st-chp8-p229-second-bachelor-visit",
        "st-chp8-p229-taste-influenced-painting",
    }
    for statement_id in expected_unset:
        if statement_id not in by_id or by_id[statement_id]["qualifiers"].get("relation_candidate") is not None:
            raise SystemExit(f"unexpected status or missing statement: {statement_id}")
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"], coverage_row["source_line_ranges"]) != ("reviewed", "complete", "L216-225"):
        raise SystemExit(f"unexpected p.229 coverage: {coverage_row}")

    lines = {i + 1: line for i, line in enumerate(source_lines)}
    l217, l218, l219, l220, l221, l222, l223 = (lines[n] for n in range(217, 224))
    q_florence = fragment(l217, "For a few years Florence", "In the Grand Prince")
    q_revival = fragment(l217, "In the Grand Prince Ferdinand", "we can see, as in no other single figure")
    q_taste_shift = fragment(l217, "the tastes of the seventeenth century", "and this alone")
    q_munificent = fragment(l217, "And he was a munificent patron", "the only support of all the sine arts in Italy")
    q_contemporary = fragment(l217, "the only support of all the sine arts in Italy")
    q_tastes_painting = fragment(l217, "His individual tastes", "development of painting.") + " development of painting."
    q_birth_father = fragment(l218, "He was born in 1663, the son of Cosimo III", "and Marguerite")
    q_birth_mother = fragment(l218, "and Marguerite d’Orléans")
    q_parents_marriage = fragment(l218, "The tempestuous relationship between his parents", "his mother")
    q_parental_effect = fragment(l218, "and the bigoted pomposity of Cosimo himself", ": Ferdinand")
    q_personality = fragment(l218, "Both were highly intelligent", "which in Gian Gastone")
    q_gian_debauchery = fragment(l218, "which in Gian Gastone eventually led to paralysing debauchery")
    q_character = fragment(l218, "He became a highly cultivated", "and the great hope")
    q_hope = fragment(l218, "and the great hope of all those")
    q_public_private = fragment(l219, "This is the side of him", "another aspect of his character") + " another aspect of his character"
    q_reaction = (
        fragment(l219, "another aspect of his character") +
        "\n" + l220[:l220.index("pleasures.") + len("pleasures.")]
    )
    q_sibling = fragment(l218, "the two sons of the marriage:", "Both were highly intelligent")
    q_opposition = fragment(l220, "With his uncle Francesco Maria", "this took the form")
    q_opposition_behavior = fragment(l220, "this took the form of licence", "much as Marguerite")
    q_second_visit = fragment(l223, "A second reckless", "was scarcely calculated")
    q_visit_judgment = fragment(l223, "was scarcely calculated to promote this end")
    q_heir = fragment(l223, "Year after year the court", "A second reckless")

    classifications = {
        "st-chp8-p229-brothers-personalities": (False, "The intelligence and instability are Haskell's attributed character assessments; sibling identity is recorded in a separate statement."),
        "st-chp8-p229-character-reconsidered": (False, "This is Haskell's retrospective account of how letters and memoirs complicate contemporaries' view of Ferdinand."),
        "st-chp8-p229-ferdinand-character": (False, "These are Haskell's descriptive judgments about Ferdinand, not formal relationships."),
        "st-chp8-p229-ferdinand-patronage-quote": (False, "Haskell's description of Ferdinand as munificent is an evaluation; the contemporary quotation is recorded separately."),
        "st-chp8-p229-ferdinand-revival": (True, "Haskell explicitly says Ferdinand was responsible for the short-lived artistic revival; the event receives its own open candidate."),
        "st-chp8-p229-florence-revival": (False, "The claim that Florence was Italy's most interesting city and then provincial is Haskell's historical evaluation."),
        "st-chp8-p229-heir-expectation": (False, "This summarizes the court's and Europe's expectation but has no individually identifiable heir as an endpoint."),
        "st-chp8-p229-parental-climate": (True, "The phrase explicitly characterizes the relationship between Ferdinand's named parents; the separate claim about influence on their sons is recorded below."),
        "st-chp8-p229-second-bachelor-visit": (True, "The passage directly reports Ferdinand's second visit to Venice in 1696 while he remained a bachelor; Haskell's judgment about its purpose is separated below."),
        "st-chp8-p229-taste-influenced-painting": (False, "This is Haskell's broad interpretation of the importance of Ferdinand's tastes for painting, with no specific work or artist endpoint."),
    }
    for statement_id, (value, note) in classifications.items():
        q = by_id[statement_id]["qualifiers"]
        q["relation_candidate"] = value
        q["relation_candidate_note"] = note

    birth = by_id["st-chp8-p229-birth-and-parentage"]
    birth["predicate"] = "born_in_1663_son_of_cosimo_iii"
    birth["object_candidate_id"] = "cand-1607"
    birth["original_quote"] = q_birth_father
    birth["qualifiers"].update({"claim": "Ferdinand was born in 1663 as the son of Cosimo III.",
                                "mentioned_candidate_ids": ["cand-1609", "cand-1607"],
                                "qualification": "The statement is narrowed to the named father; Marguerite d’Orléans is recorded separately as his mother."})

    brothers = by_id["st-chp8-p229-brothers-personalities"]
    brothers["predicate"] = "both_brothers_described_as_intelligent_and_unstable"
    brothers["original_quote"] = q_personality
    brothers["qualifiers"].update({"claim": "Haskell says both brothers were highly intelligent but each had a streak of instability.",
                                   "mentioned_candidate_ids": ["cand-1609", "cand-1627"],
                                   "qualification": "This preserves the author's description of both brothers; Gian Gastone's later debauchery is split into its own statement."})

    parental = by_id["st-chp8-p229-parental-climate"]
    parental["object_candidate_id"] = "cand-7830"
    parental["predicate"] = "parents_relationship_described_as_tempestuous"
    parental["original_quote"] = q_parents_marriage
    parental["qualifiers"].update({"claim": "Haskell describes the relationship between Cosimo III and Marguerite d’Orléans as tempestuous.",
                                   "mentioned_candidate_ids": ["cand-1607", "cand-7830"],
                                   "qualification": "The direct description of the parents' relationship is separated from Haskell's causal interpretation about the sons."})

    reconsidered = by_id["st-chp8-p229-character-reconsidered"]
    reconsidered["original_quote"] = q_public_private
    reconsidered["qualifiers"].update({"claim": "Haskell says most contemporaries saw one side of Ferdinand, while letters, private memoirs and other records allow a later reader to detect another aspect of his character.",
                                       "mentioned_candidate_ids": ["cand-1609"],
                                       "qualification": "This records Haskell's stated evidentiary contrast; the cited letters and memoirs are not individually identified or independently consulted."})

    ferdinand_character = by_id["st-chp8-p229-ferdinand-character"]
    ferdinand_character["predicate"] = "described_as_cultivated_accomplished_handsome_and_good_horseman"
    ferdinand_character["original_quote"] = q_character
    ferdinand_character["qualifiers"].update({"claim": "Haskell describes Ferdinand as highly cultivated and accomplished, handsome, good-humoured and an excellent horseman.",
                                              "mentioned_candidate_ids": ["cand-1609"],
                                              "qualification": "The social expectation that he would bring change to his father's rule is split into a separate statement."})

    patronage = by_id["st-chp8-p229-ferdinand-patronage-quote"]
    patronage["predicate"] = "haskell_describes_ferdinand_as_munificent_patron"
    patronage["object_candidate_id"] = None
    patronage["original_quote"] = q_munificent
    patronage["qualifiers"].update({"claim": "Haskell describes Ferdinand as a munificent patron when patronage seemed to have died out.",
                                    "speaker": "Haskell", "text_layer": "body",
                                    "mentioned_candidate_ids": ["cand-1609"],
                                    "qualification": "Haskell's evaluation is kept separate from the reported contemporary quotation that follows."})

    revival = by_id["st-chp8-p229-ferdinand-revival"]
    revival["object_candidate_id"] = "cand-12093"
    revival["predicate"] = "responsible_for_short_lived_florentine_artistic_revival"
    revival["original_quote"] = q_revival
    revival["qualifiers"].update({"claim": "Haskell says Grand Prince Ferdinand was responsible for a short-lived and profoundly important artistic revival in Florence.",
                                  "mentioned_candidate_ids": ["cand-1609", "cand-12093", "cand-3397"],
                                  "qualification": "The Florence setting is resolved from the immediately preceding sentence; the event is kept distinct from Haskell's broader city and periodization judgments.",
                                  "ocr_corrections": [{"source_line": 217, "ocr": "the closest to study", "print": "the closest study", "basis": "CHP-8.pdf physical page 31"}]})

    florence = by_id["st-chp8-p229-florence-revival"]
    florence["original_quote"] = q_florence
    florence["qualifiers"].update({"claim": "Haskell says Florence was again Italy's most interesting city for a few years before sinking into provincialism.",
                                   "mentioned_candidate_ids": ["cand-3397", "cand-3461"],
                                   "qualification": "This is an evaluative characterization of Florence's changing status."})

    heir = by_id["st-chp8-p229-heir-expectation"]
    heir["original_quote"] = q_heir
    heir["qualifiers"].update({"claim": "Haskell says the court and Europe waited year after year for an heir to ensure the Medici line's survival.",
                               "mentioned_candidate_ids": ["cand-5520", "cand-3462", "cand-5179"],
                               "qualification": "The expected heir is unnamed and is not converted into a speculative person candidate."})

    visit = by_id["st-chp8-p229-second-bachelor-visit"]
    visit["predicate"] = "made_second_bachelor_visit_to_venice_in_1696"
    visit["original_quote"] = q_second_visit
    visit["qualifiers"].update({"claim": "Ferdinand made a second visit to Venice in 1696 while still a bachelor.",
                                "mentioned_candidate_ids": ["cand-1609", "cand-3401"],
                                "qualification": "The visit itself is separated from Haskell's judgment that it was unlikely to promote the production of an heir."})

    taste = by_id["st-chp8-p229-taste-influenced-painting"]
    taste["original_quote"] = q_tastes_painting
    taste["qualifiers"].update({"claim": "Haskell says Ferdinand's individual tastes were of considerable importance for the development of painting.",
                                "mentioned_candidate_ids": ["cand-1609"],
                                "qualification": "This remains an attributed, broad art-historical assessment without a specified artist or work endpoint."})

    opposition = by_id["st-chp8-p229-ferdinand-francesco-opposition"]
    opposition["predicate"] = "ferdinand_led_opposition_with_francesco_maria_to_cosimo"
    opposition["original_quote"] = q_opposition
    opposition["qualifiers"].update({"claim": "Haskell says Ferdinand led opposition to Cosimo III with his uncle Francesco Maria, who was three years older.",
                                     "mentioned_candidate_ids": ["cand-1609", "cand-1626", "cand-1607"],
                                     "qualification": "This row records the named co-leadership; Haskell's account of how the opposition was expressed is separated below."})

    continuation = by_id["st-chp8-p229-family-called-to-provide-heir-open"]
    continuation["qualifiers"].update({"continuation_status": "closed",
                                       "continuation_to_segment_id": NEXT_SEGMENT,
                                       "continuation_to_source_line": 228,
                                       "continued_to_segment_id": NEXT_SEGMENT,
                                       "continued_to_source_line": 228,
                                       "continuation_closed_by_statement_id": "st-chp8-p230-heir-attempts-closed",
                                       "qualification": "The sentence closes at p.230 L228 ('had failed'); unnamed family members and their unsuccessful effort remain unexpanded."})

    candidate_ids = {row["candidate_id"] for row in candidates}
    for candidate_id in ("cand-12092", "cand-12093"):
        if candidate_id in candidate_ids:
            raise SystemExit(f"candidate ID already exists: {candidate_id}")
    candidates.extend([
        {"candidate_id": "cand-12092", "index_entry_id": "", "canonical_name": "Unidentified contemporary quoted by Haskell on Grand Prince Ferdinand's patronage",
         "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "",
         "sub_entry": "", "detail": "Haskell attributes the words 'the only support of all the fine arts in Italy' to an unnamed contemporary; the speaker is not identified in this passage.",
         "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L217"},
        {"candidate_id": "cand-12093", "index_entry_id": "", "canonical_name": "Short-lived Florentine artistic revival under Grand Prince Ferdinand",
         "index_page_range": "", "suggested_type": "event", "status": "open", "index_source_file": "",
         "sub_entry": "", "detail": "Haskell calls it a short-lived, profoundly important artistic revival and says Ferdinand was responsible; the immediately preceding sentence locates it in Florence.",
         "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L217"},
    ])

    statement_ids = {row["statement_id"] for row in statements}
    additions = [
        new_statement("st-chp8-p229-ferdinand-gian-gastone-siblings", "cand-1609", "cand-1627", "sibling_of", (218, 218),
                      "Ferdinand and Gian Gastone are identified as the two sons of Cosimo III and Marguerite d’Orléans.",
                      q_sibling, relation=True,
                      note="The page explicitly names both as the two sons of the marriage; the siblings' character descriptions are separate.",
                      mentioned=["cand-1609", "cand-1627", "cand-1607", "cand-7830"]),
        new_statement("st-chp8-p229-gian-gastone-instability-debauchery", "cand-1627", None, "instability_led_to_debauchery",
                      (218, 218), "Haskell says Gian Gastone's streak of instability eventually led to paralysing debauchery.",
                      q_gian_debauchery, relation=False,
                      note="This is Haskell's attributed psychological characterization, not a formal relationship.",
                      mentioned=["cand-1627"]),
        new_statement("st-chp8-p229-ferdinand-reaction-to-father", "cand-1609", None, "artistic_tastes_interpreted_as_reaction_to_fathers_culture",
                      (219, 220), "Haskell interprets Ferdinand's fin-de-siècle preciosity, love of frisson and equivocal pleasures as a reaction against his father's Victorian surroundings, reflected in his artistic tastes.",
                      q_reaction, relation=False,
                      note="This is Haskell's retrospective psychological interpretation; the source OCR punctuation and 'fife' are corrected only in this qualifier.",
                      mentioned=["cand-1609", "cand-1607"],
                      extra={"ocr_corrections": [{"source_line": 220, "ocr": "surroundings,. a", "print": "surroundings, a", "basis": "CHP-8.pdf physical page 31"},
                             {"source_line": 220, "ocr": "fife", "print": "life", "basis": "CHP-8.pdf physical page 31"}]}),
        new_statement("st-chp8-p229-ferdinand-hope-for-change", "cand-1609", None, "seen_as_hope_for_change_from_cosimos_rule",
                      (218, 218), "Haskell says Ferdinand was the great hope of those who wanted change from his father's rule.",
                      q_hope, relation=False,
                      note="The unnamed group remains an authorial social characterization and is not expanded into an entity candidate.",
                      mentioned=["cand-1609", "cand-1607"]),
        new_statement("st-chp8-p229-contemporary-patronage-quote", "cand-12092", "cand-1609",
                      "contemporary_describes_ferdinand_as_only_support_of_fine_arts", (217, 217),
                      "An unidentified contemporary calls Ferdinand 'the only support of all the fine arts in Italy' when patronage seemed to have died out.",
                      q_contemporary, relation=True,
                      note="The source is attributed only as 'a contemporary'; the speaker's identity remains open. Page image corrects OCR 'sine arts' to 'fine arts'.",
                      mentioned=["cand-12092", "cand-1609"], speaker="Unidentified contemporary (quoted by Haskell)",
                      text_layer="reported direct speech",
                      extra={"ocr_corrections": [{"source_line": 217, "ocr": "sine arts", "print": "fine arts", "basis": "CHP-8.pdf physical page 31"}]}),
        new_statement("st-chp8-p229-ferdinand-tastes-change-century", "cand-1609", None,
                      "embodies_transition_from_seventeenth_to_eighteenth_century_tastes", (217, 217),
                      "Haskell presents Ferdinand as embodying a change from seventeenth-century to eighteenth-century tastes.",
                      q_taste_shift, relation=False,
                      note="This is Haskell's periodization judgment, distinct from the claim that Ferdinand was responsible for the artistic revival.",
                      mentioned=["cand-1609"]),
        new_statement("st-chp8-p229-marguerite-mother-of-ferdinand", "cand-1609", "cand-7830", "child_of", (218, 218),
                      "Ferdinand was born as the son of Marguerite d’Orléans.", q_birth_mother,
                      relation=True, note="The mother is stated explicitly alongside Cosimo III in the source.",
                      mentioned=["cand-1609", "cand-7830"]),
        new_statement("st-chp8-p229-parental-climate-left-mark-on-sons", "cand-1607", None,
                      "cosimos_pomposity_and_household_atmosphere_left_mark_on_sons", (218, 218),
                      "Haskell says Cosimo's pomposity and the suffocating family atmosphere left a mark on Ferdinand and Gian Gastone.",
                      q_parental_effect, relation=False,
                      note="This is Haskell's causal interpretation about both sons; it is not converted into a formal influence edge.",
                      mentioned=["cand-1607", "cand-1609", "cand-1627", "cand-3397"]),
        new_statement("st-chp8-p229-second-visit-heir-judgment", "cand-1609", None,
                      "haskell_judges_bachelor_visit_unlikely_to_promote_heir", (223, 223),
                      "Haskell says Ferdinand's second bachelor visit to Venice was scarcely calculated to promote the production of an heir.",
                      q_visit_judgment, relation=False,
                      note="This preserves Haskell's judgment separately from the visit fact; the future heir is not identified.",
                      mentioned=["cand-1609", "cand-3401"]),
        new_statement("st-chp8-p229-francesco-opposition-behavior", "cand-1609", "cand-1626",
                      "opposition_manifested_as_license_and_wild_behavior", (220, 220),
                      "Haskell says that when political activity was impossible, Ferdinand and Francesco Maria's opposition took the form of licence and wild behavior that offended court decorum.",
                      q_opposition_behavior, relation=False,
                      note="The source's behavioral and decorum judgments are kept apart from the named co-leadership of the opposition.",
                      mentioned=["cand-1609", "cand-1626"]),
    ]
    for row in additions:
        if row["statement_id"] in statement_ids:
            raise SystemExit(f"statement ID already exists: {row['statement_id']}")
        statement_ids.add(row["statement_id"])

    mention_ids = {row["mention_id"] for row in mentions}
    spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mentions}
    offsets = {}
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), source_lines[meta["line_start"] - 1:meta["line_end"]]):
        offsets[line_no] = offset
        offset += len(line) + 1
    new_mentions = []
    def add_mention(mention_id, line_no, candidate_id, surface, note):
        if mention_id in mention_ids:
            raise SystemExit(f"mention ID already exists: {mention_id}")
        line = lines[line_no]
        start_local = line.find(surface)
        if start_local < 0:
            raise SystemExit(f"mention surface missing at L{line_no}: {surface!r}")
        start, end = offsets[line_no] + start_local, offsets[line_no] + start_local + len(surface)
        span = (SEGMENT, str(start), str(end))
        if span in spans:
            raise SystemExit(f"duplicate mention span: {span}")
        new_mentions.append({"mention_id": mention_id, "segment_id": SEGMENT, "candidate_id": candidate_id,
                             "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})
        mention_ids.add(mention_id)
        spans.add(span)

    add_mention("m-chp8-p229-contemporary-speaker", 217, "cand-12092", "a contemporary",
                "Unidentified source of the quoted assessment of Ferdinand's patronage.")
    add_mention("m-chp8-p229-artistic-revival-event", 217, "cand-12093", "this short-lived but profoundly important revival",
                "The Florentine artistic revival Haskell attributes to Grand Prince Ferdinand.")

    totals = {"true": 0, "false": 0, "unset": 0}
    for row in statements + additions:
        if row.get("segment_id") != SEGMENT:
            continue
        value = row.get("qualifiers", {}).get("relation_candidate")
        totals["true" if value is True else "false" if value is False else "unset"] += 1
    if totals["unset"]:
        raise SystemExit(f"p.229 remains unclassified: {totals}")

    preview = {
        "mode": "dry-run", "segment": SEGMENT, "page_image": PAGE_IMAGE.relative_to(ROOT).as_posix(),
        "existing_statements_reviewed": len(target_rows), "new_statements": [row["statement_id"] for row in additions],
        "new_candidates": ["cand-12092", "cand-12093"],
        "new_mentions": [row["mention_id"] for row in new_mentions],
        "p229_final_statement_counts": totals,
        "cross_page_continuation": {"statement_id": "st-chp8-p229-family-called-to-provide-heir-open", "closed_by": "st-chp8-p230-heir-attempts-closed", "line": 228},
        "semantic_fixes": [
            "separate parentage, sibling identity, character assessments and psychological interpretations",
            "separate Ferdinand's patronage characterization from the unidentified contemporary's quote",
            "anchor the Florentine artistic revival event and its explicit attribution to Ferdinand",
            "separate the 1696 Venice visit from Haskell's judgment about its effect on succession",
            "narrow evidence quotes and retain page-image OCR corrections as qualifiers",
        ],
    }
    payload = {
        STATEMENTS: jsonl_bytes(statements + additions),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions + new_mentions),
        COVERAGE: csv_bytes(coverage_fields, coverage),
    }
    return preview, payload


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.229 S2 review")
args = parser.parse_args()
preview, payload = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
for path in (STATEMENTS, CANDIDATES, MENTIONS, COVERAGE):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
for path, data in payload.items():
    atomic_write(path, data)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
