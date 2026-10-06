"""Controlled S2 migration for chapter 8 printed p.207 body text.

Default invocation is a read-only dry run. Printed-page readings are recorded
in S2; immutable S0 source transcriptions are never edited by this script.
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
SOURCE_PATH = ROOT / SOURCE_REL
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l43-51"
NEXT_SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l53-60"
BACKUP_SUFFIX = ".bak-s2-chp8-p207-body-20260930"
EXPECTED_MAX_CANDIDATE = 7439


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

meta = segments.get(SEGMENT_ID)
if not meta or meta["source_file"] != SOURCE_REL or (int(meta["line_start"]), int(meta["line_end"])) != (43, 51):
    raise SystemExit("p.207 segment metadata changed; review before migration")
raw_source = SOURCE_PATH.read_bytes()
if hashlib.sha256(raw_source).hexdigest() != meta["asset_sha256"]:
    raise SystemExit("source file fingerprint changed; rebuild segments and review")
source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[42:51])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != meta["sha256"]:
    raise SystemExit("p.207 segment text hash changed; review before migration")
if coverage_by_id.get(SEGMENT_ID, {}).get("disposition") != "queued":
    raise SystemExit("expected queued p.207 coverage; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("mentions already exist for p.207; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in statement_rows):
    raise SystemExit("statements already exist for p.207; inspect before rerunning")

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")


def candidate(cid, name, typ, detail, line):
    return {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": typ,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    }


new_candidates = [
    candidate("cand-7440", "Gaspar Roomer's unidentified private chapel", "place",
              "The text says it was dedicated to S. Maria Maddalena dei Pazzi but gives no building or address.", 44),
    candidate("cand-7441", "Saint Mary Magdalene de' Pazzi (named in Roomer's chapel dedication)", "person",
              "Named as the saint to whom the unidentified private chapel was dedicated; no further biography or image is described here.", 44),
    candidate("cand-7442", "Unidentified altarpiece by Giacinto Brandi for Roomer's private chapel", "work",
              "The altarpiece has no title or date in this passage; the source identifies its maker and chapel context.", 44),
    candidate("cand-7443", "Unspecified paintings commissioned or bought by Roomer from Guercino, Giacinto Brandi and Andrea Sacchi", "work",
              "The source gives no titles, quantities, dates, or transactions; it says acquisition probably occurred through Roomer's Flemish agents.", 44),
    candidate("cand-7444", "Gaspar Roomer's unidentified Flemish agents in Rome and elsewhere", "term",
              "Unnamed intermediary group through whom Haskell says Roomer probably commissioned and bought works.", 44),
    candidate("cand-7445", "Unspecified animal pictures by Giovanni Benedetto Castiglione obtained by Roomer", "work",
              "No individual work is named; the body characterizes Castiglione as an animal specialist.", 44),
    candidate("cand-7446", "Unspecified Bamboccianti and battle-painter pictures obtained by Roomer", "work",
              "A source-specific group of works; named examples of the battle painters are Pieter van Laer, Jan Miel and Borgognone.", 44),
    candidate("cand-7447", "Unspecified architectural scenes by Viviano Codazzi sought by Roomer", "work",
              "The source says Roomer made strenuous efforts to acquire such scenes during the last ten years of his life; individual works are not identified.", 44),
    candidate("cand-7448", "Marriage Feast at Cana (Mattia Preti painting commissioned by Roomer)", "work",
              "The body names the subject and describes an open-loggia composition; no date, current location, or exact version is given.", 45),
    candidate("cand-7449", "Further Mattia Preti pictures apparently acquired by Roomer for export", "work",
              "The text says Roomer seems to have acquired further Preti works only to export them; no works, destinations, or transactions are specified.", 46),
    candidate("cand-7450", "Unidentified old-master pictures Luca Giordano apparently forged to tease Roomer", "work",
              "Haskell says Giordano apparently forged a number of old masters, but names no source paintings or surviving versions. The wording remains an attributed report, not an authentication finding.", 47),
    candidate("cand-7451", "New, light and rich Venetian manner in Haskell's question about Giordano", "term",
              "An alternative stylistic description floated by Haskell; the passage does not identify particular Giordano works.", 48),
    candidate("cand-7452", "Tradition of violence in Roomer's early collecting", "term",
              "A second alternative in Haskell's rhetorical question about Giordano's unknown pictures; it is not a settled attribution.", 48),
    candidate("cand-7453", "Maniera grande ascribed to Mattia Preti by de Dominici", "term",
              "Italian phrase in a report quoted by Haskell; preserve the source's wording and accompanying description rather than imposing a modern definition.", 51),
    candidate("cand-7454", "Picture lovers said by de Dominici to have followed Roomer's advice", "term",
              "An unspecified group described with a universal quantifier in a quotation reported more than fifty years after Roomer's death.", 50),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates) or new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate IDs collide")

mention_specs = []


def add_mention(surface, cid, note, occurrence=1):
    mention_specs.append((surface, cid, note, occurrence))


add_mention("Rubens", "cand-2293", "Artist named in the reference to the previously described Feast of Herod.")
add_mention("Rubens’s great picture", "cand-4092", "Anaphoric reference to the Feast of Herod described on p.206.")
add_mention("Roomer", "cand-2227", "Index subentry for Roomer and Rubens's Feast of Herod.", 1)
add_mention("his collection", "cand-7407", "Roomer's collection, described as containing the bulk of his earlier pictures.", 1)
add_mention("Flemish agents", "cand-7444", "Unidentified intermediary group through whom Roomer probably acquired works.")
add_mention("Pome", "cand-4490", "S0 OCR form; the print reads Rome.")
add_mention("commissioned and bought pictures from Guercino, Giacinto Brandi (who painted an altarpiece for his private chapel dedicated to S. Maria Maddalena dei Pazzi) and Sacchi", "cand-7443", "Unspecified works and transactions described under Haskell's explicit probability qualification.")
add_mention("Guercino", "cand-1258", "Artist named among painters from whom Roomer probably commissioned and bought pictures.")
add_mention("Giacinto Brandi", "cand-0446", "Artist named among painters from whom Roomer probably commissioned and bought pictures.")
add_mention("his private chapel", "cand-7440", "Unidentified chapel associated with Roomer.")
add_mention("S. Maria Maddalena dei Pazzi", "cand-7441", "Saint named in the dedication; no further identity claim is made here.")
add_mention("an altarpiece", "cand-7442", "Unidentified Brandi work for Roomer's private chapel.")
add_mention("Sacchi", "cand-2318", "Andrea Sacchi, named among the artists whose pictures Roomer probably acquired.")
add_mention("Roomer", "cand-2226", "Index subentry concerns Roomer and Mattia Preti.", 2)
add_mention("works by the animal specialist Castiglione", "cand-7445", "Unnamed group of works; Castiglione is described as an animal specialist.")
add_mention("Castiglione", "cand-0602", "Giovanni Benedetto Castiglione, named as an animal specialist.")
add_mention("bamboccianti and battle painters such as Pieter van Laer, Jan Miel and Borgognone", "cand-7446", "Unspecified works by painter groups and named examples.")
add_mention("bamboccianti", "cand-0173", "Painter group named in the source.")
add_mention("Pieter van Laer", "cand-1351", "Named example of a battle painter.")
add_mention("Jan Miel", "cand-1662", "Named example of a battle painter.")
add_mention("Borgognone", "cand-0399", "Giacomo Borgognone, named as a battle painter.")
add_mention("architectural scenes", "cand-7447", "Unspecified works by Viviano Codazzi that Roomer sought to acquire.")
add_mention("Viviano Codazzi", "cand-0794", "Artist named as maker of the architectural scenes.")
add_mention("Mattia Preti", "cand-2056", "Painter who returned to Naples in 1656 and received Roomer's commission.", 1)
add_mention("Naples", "cand-1722", "City to which Preti returned in 1656.")
add_mention("Marriage Feast at Cana", "cand-7448", "Named subject of Preti's commission for Roomer.")
add_mention("Veronese", "cand-2755", "Artist whose work the open-loggia composition is said deliberately to recall.")
add_mention("Naples", "cand-1722", "City where the picture attracted attention.", 2)
add_mention("Roomer", "cand-2226", "Index subentry concerns Roomer and Mattia Preti.", 3)
add_mention("further works by Preti", "cand-7449", "Unnamed pictures Haskell says Roomer seems to have acquired only to export.")
add_mention("Preti", "cand-2056", "Mattia Preti, named in the report about works acquired for export.", 3)
add_mention("Roomer", "cand-2225", "Index subentry concerns Roomer and Luca Giordano.", 4)
add_mention("Luca Giordano", "cand-1172", "Painter whose relationship with Roomer began in the middle 1650s.")
add_mention("the ageing collector", "cand-2223", "Anaphoric reference to Gaspar Roomer in Haskell's report.")
add_mention("a number of old masters", "cand-7450", "Pictures Giordano apparently forged; Haskell names no works.")
add_mention("Roomer", "cand-2225", "Index subentry concerns Roomer and Luca Giordano.", 5)
add_mention("Giordano", "cand-1172", "Surname reference to Luca Giordano in the statement about unidentified pictures.", 2)
add_mention("Roomer", "cand-2223", "Reference to Roomer's death in 1674.", 6)
add_mention("Venetian manner", "cand-7451", "A stylistic alternative posed by Haskell, not assigned to any identified work.")
add_mention("tradition of violence", "cand-7452", "The contrasting alternative in Haskell's rhetorical question.")
add_mention("Roomer", "cand-2232", "Index subentry concerns Roomer's place in Neapolitan culture.", 7)
add_mention("Neapolitan culture", "cand-2232", "Topical phrase indexed under Roomer's place in Neapolitan culture.")
add_mention("Naples", "cand-1722", "City where the source says Roomer was regarded as the richest man.", 3)
add_mention("his collection", "cand-7407", "Roomer's picture collection, described as the largest in Naples.", 2)
add_mention("Spanish viceroys", "cand-6624", "Unidentified office-holders described as Roomer's changing rivals.")
add_mention("Roomer", "cand-2223", "Reference to Roomer as the Spanish viceroys' rival.", 8)
add_mention("picture lovers of the day", "cand-7454", "Unspecified group in the quotation attributed by Haskell to de Dominici.")
add_mention("de Dominici", "cand-0942", "Bernardo de Dominici, named as the source of the quotation.")
add_mention("Roomer", "cand-2223", "Reference to Roomer's death more than fifty years before de Dominici wrote.", 9)
add_mention("the same source", "cand-4835", "Anaphoric reference to de Dominici's Vite; p.207 note 2 remains pending.")
add_mention("Mattia Preti", "cand-2056", "Artist whom de Dominici is reported to have praised at their first meeting.", 2)
add_mention("maniera grande", "cand-7453", "Quoted Italian description of Preti.")
add_mention("‘Venetian’ picture", "cand-7448", "Anaphoric reference to the Preti painting whose title is named earlier in the segment.")

new_mentions = []
for index, (surface, cid, note, occurrence) in enumerate(mention_specs, 1):
    if cid not in candidate_ids | new_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {cid}")
    starts = []
    cursor = 0
    while True:
        found = segment_text.find(surface, cursor)
        if found < 0:
            break
        starts.append(found)
        cursor = found + 1
    if occurrence > len(starts):
        raise SystemExit(f"surface occurrence {occurrence} missing for {surface!r}; found {len(starts)}")
    start = starts[occurrence - 1]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch for {surface!r}")
    new_mentions.append({
        "mention_id": f"m-chp8-p207-{index:03d}",
        "segment_id": SEGMENT_ID,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for i, first in enumerate(new_mentions):
    if first["mention_id"] in existing_mention_ids:
        raise SystemExit(f"mention ID collision: {first['mention_id']}")
    for second in new_mentions[i + 1:]:
        a, b = int(first["start_char"]), int(first["end_char"])
        c, d = int(second["start_char"]), int(second["end_char"])
        if a < d and c < b:
            nested = (a <= c and d <= b and (a, b) != (c, d)) or (c <= a and b <= d and (a, b) != (c, d))
            if not nested:
                raise SystemExit(f"overlapping non-nested mentions: {first!r} / {second!r}")


def make_statement(sid, line_start, line_end, predicate, claim, qualification,
                   *, subject=None, obj=None, mentioned=(), quote=None, extra=None):
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 207,
        "pdf_physical_page": 5,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


ocr_corrections = [
    {"source_line": 44, "ocr": "subjectmatter", "print": "subject-matter", "basis": "CHP-8.pdf physical page 5; printed word is hyphenated at the line break."},
    {"source_line": 44, "ocr": "Pome", "print": "Rome", "basis": "CHP-8.pdf physical page 5."},
    {"source_line": 47, "ocr": "note...", "print": "note.", "basis": "CHP-8.pdf physical page 5."},
    {"source_line": 48, "ocr": "’ virtuosity", "print": "virtuosity", "basis": "CHP-8.pdf physical page 5; the stray leading mark is absent in print."},
    {"source_line": 49, "ocr": "Use", "print": "life", "basis": "CHP-8.pdf physical page 5."},
    {"source_line": 50, "ocr": "one-—", "print": "one—", "basis": "CHP-8.pdf physical page 5."},
    {"source_line": 51, "ocr": "- on", "print": "on", "basis": "CHP-8.pdf physical page 5."},
]

body_statements = [
    make_statement("st-chp8-p207-rubens-feast-may-have-shifted-roomer-taste", 44, 44,
                   "painting_may_have_stimulated_or_coincided_with_patron_taste",
                   "Haskell says the pageantry and colour of Rubens's Feast of Herod may have stimulated or merely coincided with Roomer's taste for works less realistic in subject or treatment than most of his collection.",
                   "Haskell expressly gives two alternatives, 'may' and 'a certain taste'; the passage does not establish which occurred or identify the later works.",
                   subject="cand-2223", obj="cand-4092",
                   mentioned=["cand-2223", "cand-4092", "cand-7407", "cand-7451"],
                   quote="The pageantry and colour of Rubens’s great picture may either have stimulated or coincided with a certain taste on Roomer’s part for paintings less ‘realistic’ in subjectmatter or treatment than those that had hitherto formed the bulk of his collection.",
                   extra={"alternatives": ["stimulated", "coincided"], "ocr_corrections": [ocr_corrections[0]]}),
    make_statement("st-chp8-p207-roomer-probably-commissioned-through-flemish-agents", 44, 44,
                   "probably_commissioned_and_bought_pictures_through_agents",
                   "Haskell says it seems probable that Roomer commissioned and bought pictures from Guercino, Giacinto Brandi and Andrea Sacchi through Flemish agents in Rome and elsewhere.",
                   "The source marks the whole account as probable and gives no work titles, quantities, dates, or named agents.",
                   subject="cand-2223", obj="cand-7443",
                   mentioned=["cand-2223", "cand-7443", "cand-7444", "cand-4490", "cand-1258", "cand-0446", "cand-2318"],
                   quote="It seems probable that through his Flemish agents in Pome and elsewhere he commissioned and bought pictures from Guercino, Giacinto Brandi (who painted an altarpiece for his private chapel dedicated to S. Maria Maddalena dei Pazzi) and Sacchi;",
                   extra={"probability": "seems probable", "relation_candidate": True, "ocr_corrections": [ocr_corrections[1]]}),
    make_statement("st-chp8-p207-brandi-painted-chapel-altarpiece", 44, 44,
                   "artist_painted_altarpiece_for_patron_private_chapel",
                   "Haskell says Giacinto Brandi painted an altarpiece for Roomer's private chapel dedicated to Saint Mary Magdalene de' Pazzi.",
                   "The title and date of the work and the location of the chapel are not supplied.",
                   subject="cand-0446", obj="cand-7442",
                   mentioned=["cand-0446", "cand-7442", "cand-2223", "cand-7440", "cand-7441"],
                   quote="Giacinto Brandi (who painted an altarpiece for his private chapel dedicated to S. Maria Maddalena dei Pazzi)",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p207-roomer-sought-castiglione-bamboccianti-and-battle-painter-works", 44, 44,
                   "patron_sought_works_by_animal_bamboccianti_and_battle_painters",
                   "Haskell says Roomer was also keen to obtain works by the animal specialist Castiglione, Bamboccianti painters and battle painters including Pieter van Laer, Jan Miel and Borgognone.",
                   "The source gives no titles or quantities; the named painters are examples rather than a complete list.",
                   subject="cand-2223", mentioned=["cand-2223", "cand-7445", "cand-0602", "cand-7446", "cand-0173", "cand-1351", "cand-1662", "cand-0399"],
                   quote="he was, however, just as keen to obtain works by the animal specialist Castiglione and by bamboccianti and battle painters such as Pieter van Laer, Jan Miel and Borgognone.1",
                   extra={"footnote_marker": 1, "relation_candidate": True}),
    make_statement("st-chp8-p207-roomer-strenuously-sought-codazzi-architectural-scenes", 44, 44,
                   "patron_strenuously_sought_architectural_scenes",
                   "Haskell says Roomer made strenuous efforts to acquire architectural scenes by Viviano Codazzi during the last ten years of his life.",
                   "The time span is relative to Roomer's life; the passage names no specific painting.",
                   subject="cand-2223", obj="cand-7447", mentioned=["cand-2223", "cand-0794", "cand-7447"],
                   quote="And during the last ten years of his life he made strenuous efforts to acquire architectural scenes by Viviano Codazzi.",
                   extra={"period_text": "during the last ten years of his life", "relation_candidate": True}),
    make_statement("st-chp8-p207-roomer-commissioned-preti-marriage-feast-at-cana", 45, 45,
                   "patron_commissioned_painting_and_left_subject_to_artist",
                   "When Mattia Preti returned to Naples in 1656, Roomer commissioned a picture and left its subject to the artist, who chose the Marriage Feast at Cana.",
                   "The date is 1656 for Preti's return; no separate commission date is supplied. The choice of subject is attributed to Preti.",
                   subject="cand-2223", obj="cand-7448",
                   mentioned=["cand-2223", "cand-2056", "cand-1722", "cand-7448"],
                   quote="When Mattia Preti returned to Naples in 1656 Roomer commissioned a picture from him and left the subject to the artist, who chose the Marriage Feast at Cana:",
                   extra={"date": 1656, "relation_candidate": True}),
    make_statement("st-chp8-p207-preti-cana-picture-recalls-veronese", 45, 45,
                   "painting_described_as_colourful_open_loggia_recalling_veronese",
                   "Haskell describes the Marriage Feast at Cana as a rich, colourful scene in an open loggia that deliberately looked back to Veronese.",
                   "This is Haskell's description and art-historical interpretation; it does not identify a specific Veronese painting as a direct model.",
                   subject="cand-7448", mentioned=["cand-7448", "cand-2755"],
                   quote="it was a rich, colourful scene set in an open loggia which deliberately looked back to Veronese."),
    make_statement("st-chp8-p207-preti-picture-attracted-attention-and-was-exported", 46, 46,
                   "painting_attracted_attention_and_patron_seems_to_export_later_works",
                   "Haskell says the picture attracted attention in Naples, while Roomer seems to have acquired later Preti works only to export them.",
                   "The later acquisitions and export purpose are explicitly qualified as seeming; no destinations or individual pictures are named.",
                   subject="cand-2223", obj="cand-7449",
                   mentioned=["cand-2223", "cand-7448", "cand-1722", "cand-2056", "cand-7449"],
                   quote="The picture attracted attention in Naples, but Roomer himself seems to have acquired further works by Preti only to export them.",
                   extra={"modality": "seems", "relation_candidate": True}),
    make_statement("st-chp8-p207-roomer-giordano-relations-began-uneasily", 47, 47,
                   "patron_artist_relationship_began_uneasily",
                   "Haskell says Roomer's relationship with Luca Giordano began on an uneasy note in the middle 1650s, when Giordano was some forty years younger.",
                   "The age gap is approximate and the passage gives no exact start date or specific cause for the uneasy beginning.",
                   subject="cand-2223", obj="cand-1172", mentioned=["cand-2223", "cand-1172"],
                   quote="Roomer’s relations with Luca Giordano, who was some forty years younger than himself, began in the middle 1650s on an uneasy note...",
                   extra={"approximate_age_difference": "some forty years", "date_text": "middle 1650s", "relation_candidate": True,
                          "ocr_corrections": [ocr_corrections[2]]}),
    make_statement("st-chp8-p207-giordano-apparently-forged-old-masters-to-prove-virtuosity", 47, 48,
                   "painter_apparently_forged_old_master_pictures_to_prove_skill_and_tease_patron",
                   "Haskell reports that Giordano resented being treated as a beginner and apparently forged a number of old-master pictures to prove his virtuosity and tease Roomer.",
                   "The alleged forgeries are Haskell's reported account, not a modern authentication finding; no particular original or copy is identified.",
                   subject="cand-1172", obj="cand-7450", mentioned=["cand-1172", "cand-7450", "cand-2223"],
                   quote="The painter resented ‘being treated as a beginner’, and apparently forged a number of old masters both to prove his\n’ virtuosity and to tease the ageing collector.",
                   extra={"modality": "apparently", "relation_candidate": True,
                          "ocr_corrections": [ocr_corrections[3]]}),
    make_statement("st-chp8-p207-roomer-forgave-giordano-and-became-staunch-supporter", 48, 48,
                   "patron_forgave_artist_and_supported_him_amid_feuds",
                   "Haskell says Giordano was forgiven and Roomer thereafter became his staunch supporter in the many envious feuds inspired by the successful artist.",
                   "No individual feud or participant is named; the event and evaluation remain in Haskell's account.",
                   subject="cand-2223", obj="cand-1172", mentioned=["cand-2223", "cand-1172"],
                   quote="He was forgiven and thereafter Roomer became his staunch supporter in the many envious feuds which the prodigiously successful artist inspired.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p207-giordano-pictures-for-roomer-unknown-two-styles-proposed", 48, 48,
                   "author_cannot_identify_pictures_and_poses_two_stylistic_alternatives",
                   "Haskell says it is impossible to tell which pictures Giordano painted for Roomer and asks whether they followed a new, light Venetian manner or continued a tradition of violence.",
                   "The source explicitly leaves the works unidentified and poses alternatives as questions. Do not assign either style to a specific painting.",
                   subject="cand-1172", obj="cand-7450",
                   mentioned=["cand-1172", "cand-2223", "cand-7450", "cand-7451", "cand-7452"],
                   quote="Unfortunately it is impossible to tell what pictures Giordano painted for him. Were they in the new, light, rich, Venetian manner that the artist was already practising long before Roomer’s death in 1674, or did they carry on for him the tradition of violence which he had so fostered in the early years of his collecting?",
                   extra={"knowledge_gap": True, "alternatives": ["new light Venetian manner", "tradition of violence"],
                          "ocr_corrections": [ocr_corrections[3]]}),
    make_statement("st-chp8-p207-roomer-patronage-scantily-known-but-important", 49, 49,
                   "author_said_patronage_evidence_is_scant_but_culturally_important",
                   "Haskell says knowledge of Roomer's patronage in the last forty years of his life is scant and makes it difficult to understand his place in Neapolitan culture, which he nevertheless calls unquestionably important.",
                   "This is the author's assessment; the source OCR 'Use' is corrected to print 'life'.",
                   subject="cand-2223", mentioned=["cand-2223", "cand-2232"],
                   quote="In fact our scanty knowledge of Roomer’s patronage during the last forty years of his Use makes it very difficult for us to understand his place in Neapolitan culture. It was unquestionably of great importance.",
                   extra={"ocr_corrections": [ocr_corrections[4]]}),
    make_statement("st-chp8-p207-roomer-held-richest-and-largest-collection-permanent", 49, 50,
                   "patron_held_to_be_richest_and_collection_largest_and_permanent",
                   "Haskell says Roomer was held to be the richest man in Naples and his picture collection was certainly the city's largest and, above all, permanent, unlike the changing Spanish viceroys who rivalled his claims on painters.",
                   "The richest-man description is reported as a contemporary belief; 'certainly' and 'above all' are Haskell's emphases. The source gives no measured comparison.",
                   subject="cand-2223", obj="cand-7407",
                   mentioned=["cand-2223", "cand-7407", "cand-1722", "cand-6624"],
                   quote="He was held to be the richest man in Naples and his collection of pictures was certainly the largest in the city. Above all it was permanent\n—for the Spanish viceroys, the only rivals to Roomer in the claims they made on painters, were always changing.",
                   extra={"ocr_corrections": []}),
    make_statement("st-chp8-p207-de-dominici-said-picture-lovers-followed-roomer-advice", 50, 50,
                   "de_dominici_reported_picture_lovers_followed_patron_advice",
                   "Haskell quotes de Dominici as writing that all picture lovers of the day followed Roomer's advice, more than fifty years after Roomer's death.",
                   "The universal wording is de Dominici's quotation as transmitted by Haskell, not an independently surveyed population. Footnote marker 2 points to a note still pending in the composite source segment.",
                   subject="cand-0942", obj="cand-2223",
                   mentioned=["cand-0942", "cand-4835", "cand-7454", "cand-2223"],
                   quote="‘All picture lovers of the day followed his advice’, wrote de Dominici more than fifty years after Roomer’s death.2",
                   extra={"speaker": "Bernardo de Dominici, as quoted by Haskell", "quoted_by": "Haskell",
                          "footnote_marker": 2, "time_after_death": "more than fifty years", "relation_candidate": True}),
    make_statement("st-chp8-p207-de-dominici-praised-preti-maniera-grande", 50, 51,
                   "de_dominici_reportedly_praised_preti_at_first_meeting",
                   "Haskell says de Dominici was the only source for Roomer's advice and reports that he praised Mattia Preti at their first meeting for a maniera grande based on drawing, nature and chiaroscuro.",
                   "The description is a quotation reported by Haskell from de Dominici; the source is not independently inspected here. OCR has an extra dash before 'on' and duplicates a dash after 'one'.",
                   subject="cand-0942", obj="cand-2056",
                   mentioned=["cand-0942", "cand-4835", "cand-2056", "cand-7453"],
                   quote="From the same source—our only one-—we hear of him praising Mattia Preti\n- on their first meeting for his ‘maniera grande which was firmly based on drawing, on nature and on chiaroscuro’.",
                   extra={"speaker": "Bernardo de Dominici, as quoted by Haskell", "quoted_by": "Haskell",
                          "ocr_corrections": [ocr_corrections[5], ocr_corrections[6]]}),
    make_statement("st-chp8-p207-haskell-questioned-roomer-reaction-to-preti-venetian-picture-open", 51, 51,
                   "author_questioned_whether_patron_disliked_venetian_picture",
                   "Haskell asks whether Roomer may have been disappointed in the Venetian picture Preti painted for him; the question continues on p.208.",
                   "This is an open rhetorical question, not a settled report of Roomer's reaction. p.208 begins with the completion of the same sentence.",
                   subject="cand-2223", obj="cand-7448", mentioned=["cand-2223", "cand-7448"],
                   quote="Can it be that he was disappointed in the ‘Venetian’ picture",
                   extra={"continuation_status": "open", "continuation_expected_segment_id": NEXT_SEGMENT_ID,
                          "continuation_note": "p.208 L54 begins 'which Preti then painted for him'; read the next segment before resolving the question."}),
]

if len({row["statement_id"] for row in body_statements}) != len(body_statements):
    raise SystemExit("duplicate planned statement IDs")
new_statement_ids = {row["statement_id"] for row in body_statements}
if new_statement_ids & existing_statement_ids:
    raise SystemExit("planned statement ID collision")
for row in body_statements:
    q = row["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
    if not isinstance(row.get("original_quote"), str) or row["original_quote"] not in excerpt:
        raise SystemExit(f"quote is not reproducible in S0 source: {row['statement_id']}")
    if not (43 <= q["source_line_start"] <= q["source_line_end"] <= 51):
        raise SystemExit(f"statement line range outside segment: {row['statement_id']}")
    mentioned = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        mentioned.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        mentioned.add(row["object_candidate_id"])
    if not mentioned <= candidate_ids | new_candidate_ids:
        raise SystemExit(f"statement references missing candidate: {row['statement_id']}")

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == SEGMENT_ID:
        row.update({
            "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L44-51",
            "note": "P.207 body read against CHP-8.pdf physical p.5. Print readings corrected only in S2: subject-matter, Rome, note., virtuosity, life, one—we, and no leading dash before 'on'; S0 remains unchanged. The open question at L51 continues to p.208 L54. Footnotes 1–2 remain in composite source lines L136–137.",
        })
    updated_coverage.append(row)

preview = {
    "mode": "dry-run",
    "segment": SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(body_statements),
    "coverage": {SEGMENT_ID: "reviewed/partial"},
    "continuation_pending": {"statement_id": "st-chp8-p207-haskell-questioned-roomer-reaction-to-preti-venetian-picture-open", "next_segment_id": NEXT_SEGMENT_ID},
    "footnotes_pending": ["p.207 notes 1-2 at composite source lines 136-137"],
    "ocr_corrections": ocr_corrections,
    "mention_preview": [{"candidate_id": row["candidate_id"], "surface": row["surface_form"], "start": int(row["start_char"]), "end": int(row["end_char"])} for row in new_mentions[:20]],
    "statement_ids": [row["statement_id"] for row in body_statements],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write validated tables and create recovery backups")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
statement_rows.extend(body_statements)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, statement_rows)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
