"""Controlled S2 migration for chapter 8 printed p.208 body text.

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
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l53-60"
PREVIOUS_SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l43-51"
PREVIOUS_STATEMENT_ID = "st-chp8-p207-haskell-questioned-roomer-reaction-to-preti-venetian-picture-open"
CONTINUATION_STATEMENT_ID = "st-chp8-p208-p207-preti-question-continued"
BACKUP_SUFFIX = ".bak-s2-chp8-p208-body-20260930"
EXPECTED_MAX_CANDIDATE = 7454


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
if not meta or meta["source_file"] != SOURCE_REL or (int(meta["line_start"]), int(meta["line_end"])) != (53, 60):
    raise SystemExit("p.208 segment metadata changed; review before migration")
raw_source = SOURCE_PATH.read_bytes()
if hashlib.sha256(raw_source).hexdigest() != meta["asset_sha256"]:
    raise SystemExit("source file fingerprint changed; rebuild segments and review")
source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[52:60]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != meta["sha256"]:
    raise SystemExit("p.208 segment text hash changed; review before migration")
if coverage_by_id.get(SEGMENT_ID, {}).get("disposition") != "queued":
    raise SystemExit("expected queued p.208 coverage; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("mentions already exist for p.208; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in statement_rows):
    raise SystemExit("statements already exist for p.208; inspect before rerunning")

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
    candidate("cand-7455", "Francesco di Maria", "person",
              "Named as Luca Giordano's critic in Haskell's account; no further identity detail is supplied in this passage.", 55),
    candidate("cand-7456", "Jean-Baptiste de Wael's print series of peasant life dedicated to Gaspar Roomer", "work",
              "The source describes a set of prints but supplies no titles, date, or number of sheets.", 55),
    candidate("cand-7457", "Unspecified still-life paintings by Giovan Battista Ruoppolo sent by Roomer to Flanders", "work",
              "No titles, dates, number, or individual shipment are identified; the passage says Roomer sent Ruoppolo's still lives to Flanders.", 55),
    candidate("cand-7458", "Flemish still-life pictures in Gaspar Roomer's gallery", "work",
              "An unspecified group used by Haskell to explain influence on Neapolitan painters; no artist or individual picture is named here.", 56),
    candidate("cand-7459", "Unspecified Neapolitan still-life pictures responding to Flemish examples", "work",
              "Haskell praises the quality of the pictures but names no painters or individual works in this sentence.", 56),
    candidate("cand-7460", "Artists said to have moved away from early-century Caravaggism under Rubens's influence", "term",
              "An unnamed group in Haskell's account; Roomer's own response to the trend is explicitly left open.", 56),
    candidate("cand-7461", "Ferdinand van den Einden's unidentified picture collection", "",
              "A large collection is mentioned, but the current entity taxonomy has no collection type; keep the type unresolved.", 59),
    candidate("cand-7462", "Later painters inspired by Venetian artists and patronised by Ferdinand van den Einden", "term",
              "The source names a generational and stylistic group but does not identify its members here.", 59),
    candidate("cand-7463", "Several very large Mattia Preti pictures ordered by Ferdinand van den Einden", "work",
              "The text identifies three subjects among several pictures but gives no individual dates or present locations.", 59),
    candidate("cand-7464", "Unidentified Luca Giordano pictures owned by Ferdinand van den Einden", "work",
              "Haskell explicitly says the pictures Ferdinand possessed are not known; no title or number is supplied.", 60),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates) or new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate IDs collide")

mention_specs = []


def add(line_number, surface, cid, note, occurrence=1):
    mention_specs.append((line_number, surface, cid, note, occurrence))


add(54, "Prcti", "cand-2056", "S0 OCR form; the printed page reads Preti.")
add(54, "Luca Giordano", "cand-1172", "Painter criticised by Roomer and discussed in the continuation from p.207.")
add(54, "his new manner", "cand-7451", "The stylistic description is presented as a question, not a settled explanation.")
add(54, "loose brushstrokes and lighter tonahty", "cand-7451", "S0 OCR has tonahty; the print reads tonality. Haskell poses this as a question.")
add(54, "Roomer’s", "cand-2223", "Gaspar Roomer, the patron whose reaction is questioned.")
add(55, "Francesco di Maria", "cand-7455", "Named as the person against whom Roomer backed Giordano.")
add(55, "naturalism", "cand-2231", "Topic indexed under Roomer's love of the grotesque and naturalism.")
add(55, "his gallery", "cand-7407", "Gaspar Roomer's picture collection; the source says it contained little else in his early days.")
add(55, "works by Codazzi", "cand-7447", "Unspecified architectural scenes by Viviano Codazzi discussed on p.207.")
add(55, "Codazzi", "cand-0794", "Viviano Codazzi, named as maker of the sought works.")
add(55, "Jean-Baptiste de Wael", "cand-2795", "Flemish artist who dedicated a print set to Roomer in Haskell's account.")
add(55, "a set of prints showing scenes from peasant Use", "cand-7456", "The print series is unidentified; S0 OCR has Use for printed life.")
add(55, "Ruoppolo", "cand-2310", "Giovan Battista Ruoppolo, named as Roomer's contact.")
add(55, "still lives", "cand-7457", "Unspecified still-life paintings by Ruoppolo that Roomer sent to Flanders.")
add(55, "Flanders", "cand-4652", "Destination named for the paintings Roomer sent.")
add(56, "His gallery", "cand-7407", "Gaspar Roomer's gallery/collection in Haskell's cultural interpretation.")
add(56, "the cultures of the South and North of Europe", "cand-2233", "Indexed subtopic under Roomer's collection and North-South cultural relations.")
add(56, "The Flemish still Eves", "cand-7458", "S0 OCR form; the print reads still lives.")
add(56, "many of the Neapolitan painters in this genre", "cand-7459", "An unnamed group of painters described as responding to Flemish examples.")
add(56, "such work", "cand-7458", "Anaphoric reference to the Flemish still-life pictures.")
add(56, "pictures of superb quality", "cand-7459", "Unspecified Neapolitan pictures said to repay the influence with superb quality.")
add(56, "Rubens’s Feast of Herod", "cand-4092", "Previously described Rubens picture; Haskell says it inspired artists leaving Caravaggism.")
add(56, "many artists breaking away from the Caravaggism of the early years of the century", "cand-7460", "Unnamed group and trend; Haskell leaves Roomer's personal view open.")
add(56, "Roomer himself", "cand-2223", "Gaspar Roomer; the source does not state his reaction to the trend.")
add(56, "Bernardo CavaUino", "cand-0613", "S0 OCR form; the print reads Bernardo Cavallino.")
add(56, "de Dominici", "cand-0942", "Bernardo de Dominici, identified by Haskell as the source of the reported influence claim.")
add(56, "this seminal picture", "cand-4092", "Anaphoric reference to Rubens's Feast of Herod.")
add(57, "Jan", "cand-0915", "Jan van den Einden, named with Ferdinand as a business partner of Roomer.")
add(58, "Ferdinand van den Einden", "cand-0914", "Ferdinand, son and heir of Jan in this account.")
add(58, "Jan van den Einden", "cand-0915", "Index-derived Jan van den Einden candidate; p.206's Jan Vandeneynde remains for S3 identity reconciliation.")
add(58, "Roomer", "cand-2223", "Gaspar Roomer, named as Jan's business partner.")
add(59, "Roomer", "cand-2223", "Gaspar Roomer, named in the account of Jan's partnership and Ferdinand's inheritance.")
add(59, "his son Ferdinand", "cand-0914", "Jan's son, identified by the source as the heir to his fortune.")
add(59, "a vast collection of pictures", "cand-7461", "Unidentified collection acquired by Ferdinand after inheriting his father's fortune.")
add(59, "Gaspar Roomer", "cand-2223", "Model for Ferdinand's taste and source of the seventy inherited pictures.")
add(59, "seventy of whose pictures", "cand-7407", "The source-specific collection of Gaspar Roomer; Haskell gives the number seventy.")
add(59, "the later painters, inspired by the Venetians", "cand-7462", "Unnamed group patronised by Ferdinand; the source does not enumerate them.")
add(59, "Mattia Preti", "cand-2056", "Painter whose Marriage at Cana impressed Ferdinand and whose large works he ordered.")
add(59, "Marriage at Cana", "cand-7448", "The Preti painting described on p.207 as the Marriage Feast at Cana; paragraph context indicates the same picture.")
add(59, "several very large pictures", "cand-7463", "Unspecified group of Preti pictures ordered by Ferdinand.")
add(59, "The Crucifixion of St Peter", "cand-2058", "One of the three subjects listed among Preti's large pictures.")
add(59, "The Beheading of St Paul", "cand-2057", "One of the three subjects listed among Preti's large pictures.")
add(59, "The\nMartyrdom of St Bartholomew", "cand-2061", "Title split across the source line break; footnote marker is OCR-corrected from 8 to 6.")
add(60, "Van den Einden", "cand-0914", "Ferdinand van den Einden; the passage attributes the inference about shared taste to him.")
add(60, "Roomer’s", "cand-2223", "Gaspar Roomer, whose taste for brutal realism is inferred by Haskell.")
add(60, "Luca Giordano", "cand-1172", "Painter admired by Ferdinand; the pictures he owned are explicitly unidentified.")
add(60, "which pictures by that artist he possessed", "cand-7464", "Unidentified Giordano works owned by Ferdinand; Haskell says their identities are unknown.")

new_mentions = []
line_offsets = {}
offset = 0
for line_number, line in zip(range(53, 61), segment_lines):
    line_offsets[line_number] = offset
    offset += len(line) + 1
for index, (line_number, surface, cid, note, occurrence) in enumerate(mention_specs, 1):
    if cid not in candidate_ids | new_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {cid}")
    search_text = segment_text if "\n" in surface else source_lines[line_number - 1]
    starts = []
    cursor = 0
    while True:
        found = search_text.find(surface, cursor)
        if found < 0:
            break
        starts.append(found)
        cursor = found + 1
    if occurrence > len(starts):
        raise SystemExit(f"line {line_number}: occurrence {occurrence} missing for {surface!r}; found {len(starts)}")
    start = starts[occurrence - 1] if "\n" in surface else line_offsets[line_number] + starts[occurrence - 1]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch for {surface!r}")
    new_mentions.append({
        "mention_id": f"m-chp8-p208-{index:03d}",
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
                   *, subject=None, obj=None, mentioned=(), quote=None, extra=None, speaker="Haskell"):
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 208,
        "pdf_physical_page": 6,
        "claim": claim,
        "speaker": speaker,
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
    {"source_line": 54, "ocr": "Prcti", "print": "Preti", "basis": "CHP-8.pdf physical page 6."},
    {"source_line": 54, "ocr": 'We"', "print": "We", "basis": "CHP-8.pdf physical page 6; no closing quotation mark follows We."},
    {"source_line": 54, "ocr": "He in the loose", "print": "lie in the loose", "basis": "CHP-8.pdf physical page 6."},
    {"source_line": 54, "ocr": "tonahty", "print": "tonality", "basis": "CHP-8.pdf physical page 6."},
    {"source_line": 55, "ocr": "Use", "print": "life", "basis": "CHP-8.pdf physical page 6."},
    {"source_line": 56, "ocr": "crystafosed", "print": "crystallised", "basis": "CHP-8.pdf physical page 6; retain British spelling."},
    {"source_line": 56, "ocr": "still Eves", "print": "still lives", "basis": "CHP-8.pdf physical page 6."},
    {"source_line": 56, "ocr": "CavaUino", "print": "Cavallino", "basis": "CHP-8.pdf physical page 6."},
    {"source_line": 60, "ocr": "8", "print": "6", "basis": "CHP-8.pdf physical page 6; the footnote marker after brutal realism is 6, matching the note list."},
]

body_statements = [
    make_statement(CONTINUATION_STATEMENT_ID, 54, 54,
                   "author_continued_rhetorical_question_about_roomer_and_preti",
                   "Haskell completes the p.207 question: was Roomer disappointed in the Venetian Preti picture and did that lead him to commission nothing further from the painter? Haskell says there is too little evidence to answer.",
                   "This remains an unanswered rhetorical question, not a factual claim that Roomer stopped commissioning Preti.",
                   subject="cand-2223", obj="cand-7448", mentioned=["cand-2223", "cand-2056", "cand-7448"],
                   quote='which Prcti then painted for him and that because of this he thereafter commissioned nothing for himself from the artist? We" know too little to say',
                   extra={"continuation_of_statement_id": PREVIOUS_STATEMENT_ID, "continuation_status": "closed", "ocr_corrections": ocr_corrections[:2]}),
    make_statement("st-chp8-p208-roomer-chided-giordano-new-manner", 54, 54,
                   "patron_chided_painter_for_new_manner",
                   "Haskell reports that Roomer chided Luca Giordano for a new manner described as contrary to the practice of good artists.",
                   "The quotation is Haskell's report, with footnote 1 still awaiting migration from the composite source.",
                   subject="cand-2223", obj="cand-1172", mentioned=["cand-2223", "cand-1172", "cand-7451"],
                   quote="he chided Luca Giordano ‘for his new manner which was contrary to those of good artists’.1",
                   extra={"relation_candidate": True, "footnote_marker": 1}),
    make_statement("st-chp8-p208-haskell-asks-if-manner-loose-brushstrokes-tonality", 54, 54,
                   "author_asked_whether_new_manner_lay_in_brushwork_and_tonality",
                   "Haskell asks whether Giordano's new manner lay in loose brushstrokes and lighter tonality that also offended other connoisseurs.",
                   "The passage frames this as a question and does not resolve the stylistic cause.",
                   subject="cand-1172", mentioned=["cand-1172", "cand-7451"],
                   quote="Did this new manner He in the loose brushstrokes and lighter tonahty adopted by the painter which offended other connoisseurs also?",
                   extra={"question": True, "ocr_corrections": ocr_corrections[2:4]}),
    make_statement("st-chp8-p208-roomer-backed-giordano-against-francesco", 54, 55,
                   "patron_backed_painter_against_critic",
                   "Haskell says Roomer later backed Giordano against Francesco di Maria, who is quoted as calling Giordano a great draughtsman but a weak colourist.",
                   "This is Haskell's report of Francesco di Maria's assessment; it is not an independent evaluation of Giordano's ability.",
                   subject="cand-2223", obj="cand-1172", mentioned=["cand-2223", "cand-1172", "cand-7455"],
                   quote="we hear that he later backed Giordano against\nFrancesco di Maria ‘who was a great draughtsman but a weak colourist’.",
                   extra={"relation_candidate": True, "embedded_speaker": "Francesco di Maria as quoted by Haskell"}),
    make_statement("st-chp8-p208-roomer-naturalism-longstanding-love", 55, 55,
                   "author_described_naturalism_as_roomers_longstanding_preference",
                   "Haskell says naturalism seems to have been Roomer's greatest love from his earliest days, when his gallery contained little else, through the end of his life.",
                   "The phrase 'seems to have been' marks Haskell's interpretation; the source gives no precise span or inventory definition of 'little else'.",
                   subject="cand-2223", obj="cand-2231", mentioned=["cand-2223", "cand-2231", "cand-7407"],
                   quote="it was naturalism that seems to have been Roomer’s greatest love from his earliest days when his gallery contained little else until the end of his life"),
    make_statement("st-chp8-p208-roomer-acquired-codazzi-scenes", 55, 55,
                   "patron_sought_codazzi_architectural_scenes_late_in_life",
                   "Haskell says Roomer was keen to acquire works by Codazzi toward the end of his life.",
                   "The statement continues the p.207 reference to architectural scenes; no individual work or transaction date is given.",
                   subject="cand-2223", obj="cand-7447", mentioned=["cand-2223", "cand-0794", "cand-7447"],
                   quote="when he was so keen to acquire works by Codazzi",
                   extra={"relation_candidate": True, "continuation_of_context": "st-chp8-p207-roomer-strenuously-sought-codazzi-architectural-scenes"}),
    make_statement("st-chp8-p208-de-wael-dedicated-print-series", 55, 55,
                   "artist_dedicated_print_series_to_patron",
                   "Haskell says Jean-Baptiste de Wael dedicated to Roomer a set of prints showing scenes from peasant life.",
                   "The prints are not individually titled or dated; footnote 3 remains pending.",
                   subject="cand-2795", obj="cand-7456", mentioned=["cand-2795", "cand-2223", "cand-7456"],
                   quote="when Jean-Baptiste de Wael dedicated to him a set of prints showing scenes from peasant Use",
                   extra={"relation_candidate": True, "footnote_marker": 3, "ocr_corrections": [ocr_corrections[4]]}),
    make_statement("st-chp8-p208-roomer-sent-ruoppolo-still-lives-to-flanders", 55, 55,
                   "patron_sent_artists_still_life_pictures_to_flanders",
                   "Haskell says Roomer was in touch with Ruoppolo and sent the painter's still-life pictures to Flanders.",
                   "No individual painting, date, quantity, or transaction record is supplied; do not infer that Roomer commissioned the works.",
                   subject="cand-2223", obj="cand-7457", mentioned=["cand-2223", "cand-2310", "cand-7457", "cand-4652"],
                   quote="when he was in touch with Ruoppolo, whose still lives he sent to Flanders.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p208-roomer-gallery-crystallized-north-south", 56, 56,
                   "author_interpreted_gallery_as_embodying_north_south_cultural_relation",
                   "Haskell says Roomer's gallery crystallised the longstanding relationship between the cultures of Southern and Northern Europe.",
                   "This is the author's cultural interpretation of the gallery, not a claim about a single exchange or a defined collection boundary.",
                   subject="cand-2223", obj="cand-2233", mentioned=["cand-2223", "cand-7407", "cand-2233"],
                   quote="His gallery crystafosed that close relationship which had for so long existed between the cultures of the South and North of Europe.",
                   extra={"ocr_corrections": [ocr_corrections[5]]}),
    make_statement("st-chp8-p208-flemish-still-life-influenced-neapolitans", 56, 56,
                   "flemish_still_lives_excited_neapolitan_painters",
                   "Haskell says Flemish still lifes must have excited many Neapolitan painters in the genre, who otherwise had little chance to see such work.",
                   "The text uses 'must have' as an inference; no painters or particular paintings are named.",
                   subject="cand-7458", obj="cand-7459", mentioned=["cand-7458", "cand-7459"],
                   quote="The Flemish still Eves must have excited many of the Neapolitan painters in this genre who would otherwise have had little chance to see such work",
                   extra={"modality": "must have", "ocr_corrections": [ocr_corrections[6]]}),
    make_statement("st-chp8-p208-neapolitan-painters-repaid-debt", 56, 56,
                   "neapolitan_painters_repaid_influence_with_superb_pictures",
                   "Haskell says the Neapolitan painters repaid their debt with pictures of superb quality.",
                   "The author gives no individual painter, work, or measure of quality.",
                   subject="cand-7459", mentioned=["cand-7459"],
                   quote="and they repaid their debt with pictures of superb quality"),
    make_statement("st-chp8-p208-rubens-feast-influenced-artists-leaving-caravaggism", 56, 56,
                   "rubens_picture_inspired_artists_breaking_from_caravaggism",
                   "Haskell says Rubens's Feast of Herod was certainly a source of inspiration to many artists breaking away from early-century Caravaggism, while leaving Roomer's own view of the trend open.",
                   "The source asserts influence but names no artists; Roomer's reaction is explicitly unknown.",
                   subject="cand-4092", obj="cand-7460", mentioned=["cand-4092", "cand-7460", "cand-2223"],
                   quote="and Rubens’s Feast of Herod was certainly a source of inspiration to many artists breaking away from the Caravaggism of the early years of the century, whatever Roomer himself may have felt about the trend.",
                   extra={"modality": "certainly", "relation_candidate": True, "footnote_marker": 4}),
    make_statement("st-chp8-p208-de-dominici-cavallino-affect", 56, 56,
                   "de_dominici_reported_rubens_picture_affected_cavallino",
                   "Haskell attributes to de Dominici the report that the picture's brilliant colouring profoundly affected Bernardo Cavallino.",
                   "The quotation is mediated through Haskell; the cited account is not independently inspected here.",
                   subject="cand-0942", obj="cand-0613", mentioned=["cand-0942", "cand-0613", "cand-4092"],
                   quote="‘The magic of its brilliant colouring laid on with such mastery’ profoundly affected Bernardo CavaUino, we learn from de Dominici",
                   extra={"embedded_speaker": "Bernardo de Dominici as quoted by Haskell", "quoted_by": "Haskell", "footnote_marker": 4,
                          "relation_candidate": True, "ocr_corrections": [ocr_corrections[7]]}),
    make_statement("st-chp8-p208-many-painters-studied-feast", 56, 56,
                   "many_painters_studied_rubens_picture",
                   "Haskell says many other painters also studied Rubens's Feast of Herod.",
                   "The source supplies no names or count for the painters; footnote 4 remains pending.",
                   subject="cand-4092", mentioned=["cand-4092"],
                   quote="and many other painters also studied this seminal picture.4",
                   extra={"footnote_marker": 4}),
    make_statement("st-chp8-p208-van-den-einden-men-business-partners", 57, 58,
                   "patron_had_two_business_partners",
                   "Haskell identifies Jan and Ferdinand van den Einden as Roomer's business partners and associates in patronage.",
                   "The passage later identifies Ferdinand as Jan's son. The spelling and identity relation to p.206's Jan Vandeneynde remain for S3 reconciliation.",
                   subject="cand-2223", mentioned=["cand-2223", "cand-0915", "cand-0914"],
                   quote="Closely associated with Roomer as patron were his business partners Jan and\nFerdinand van den Einden.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p208-jan-flemish-origin", 58, 58,
                   "person_described_as_flemish_with_seemingly_low_origins",
                   "Haskell says Jan van den Einden was Flemish and that his origins seemed lowly, unlike Roomer's.",
                   "The source qualifies the claim about his origins with 'seem'.",
                   subject="cand-0915", mentioned=["cand-0915", "cand-2223"],
                   quote="Jan van den Einden was also Flemish though, unlike Roomer, his origins seem to have been lowly.",
                   extra={"modality": "seem", "footnote_marker": 5}),
    make_statement("st-chp8-p208-jan-partnership-1630s-enriched", 58, 59,
                   "business_partnership_began_in_1630s_and_enriched_jan",
                   "Haskell says Jan's partnership with Roomer began in the 1630s and led to his enrichment after early struggles.",
                   "The start date is given by decade only; the passage does not specify the business form or exact financial outcome.",
                   subject="cand-0915", obj="cand-2223", mentioned=["cand-0915", "cand-2223"],
                   quote="After some early struggles his partnership with\nRoomer which began in the 1630s led to his enrichment",
                   extra={"date_text": "in the 1630s", "relation_candidate": True}),
    make_statement("st-chp8-p208-ferdinand-inherited-fortune-collected", 59, 59,
                   "son_inherited_fortune_bought_title_and_acquired_collection",
                   "Haskell says Jan's fortune was inherited by his son Ferdinand, who bought himself the title of Marquis and acquired a vast picture collection.",
                   "These are Haskell's reported claims; the passage supplies no sum, legal transaction, or collection inventory.",
                   subject="cand-0915", obj="cand-0914", mentioned=["cand-0915", "cand-0914", "cand-7461"],
                   quote="and his fortune was inherited by his son Ferdinand, who was thus able to buy himself the title of Marquis and to acquire a vast collection of pictures.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p208-ferdinand-taste-modeled-roomer-inherited-pictures", 59, 59,
                   "collector_taste_modeled_on_roomer_and_inherited_seventy_pictures",
                   "Haskell says Ferdinand's taste seems largely to have been modelled on Gaspar Roomer's and that he inherited seventy of Roomer's pictures.",
                   "The taste comparison is qualified by 'seems'; the count of seventy is Haskell's report, not independently checked against an inventory.",
                   subject="cand-0914", obj="cand-2223", mentioned=["cand-0914", "cand-2223", "cand-7407"],
                   quote="His taste seems to have been largely modelled on that of Gaspar Roomer, seventy of whose pictures he inherited.",
                   extra={"modality": "seems", "relation_candidate": True}),
    make_statement("st-chp8-p208-ferdinand-sponsored-later-venetian-inspired-painters", 59, 59,
                   "collector_patronised_later_painters_inspired_by_venetians",
                   "Haskell says Ferdinand, as a younger-generation collector, specially patronised later painters inspired by the Venetians.",
                   "The group is unnamed and no individual commission is identified.",
                   subject="cand-0914", obj="cand-7462", mentioned=["cand-0914", "cand-7462"],
                   quote="But, being of a younger generation, it was the later painters, inspired by the Venetians, whom he specially patronised.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p208-ferdinand-commissioned-large-preti-pictures", 59, 59,
                   "collector_ordered_several_large_pictures_by_preti",
                   "Haskell says Ferdinand was struck by Mattia Preti's Marriage at Cana and its general approval, and ordered several very large pictures by Preti.",
                   "The sentence does not say that the three named martyrdom subjects below are the only commissions; the Marriage at Cana is contextually the work described on p.207.",
                   subject="cand-0914", obj="cand-7463", mentioned=["cand-0914", "cand-2056", "cand-7448", "cand-7463"],
                   quote="Thus he was so struck by Mattia Preti’s Marriage at Cana and the general approval it met with that he ordered several very large pictures by that artist.",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p208-three-preti-paintings-brutal-realism", 59, 60,
                   "author_inferred_three_subjects_show_shared_taste_for_brutal_realism",
                   "Haskell infers from the subjects of three Preti pictures that Van den Einden must have shared Roomer's taste for brutal realism.",
                   "This is Haskell's interpretation marked 'must have'; the OCR footnote marker 8 is corrected to 6, which refers to a pending de Dominici note.",
                   subject="cand-0914", obj="cand-2223", mentioned=["cand-0914", "cand-2223", "cand-2058", "cand-2057", "cand-2061"],
                   quote="But the subjects of three of these, The Crucifixion of St Peter, The Beheading of St Paul and The\nMartyrdom of St Bartholomew, show that Van den Einden must have shared Roomer’s taste for brutal realism.8",
                   extra={"modality": "must have", "inference": True, "relation_candidate": True,
                          "footnote_marker": 6, "ocr_corrections": [ocr_corrections[8]]}),
    make_statement("st-chp8-p208-ferdinand-admired-giordano-works-unknown", 60, 60,
                   "collector_admired_giordano_but_owned_works_are_unidentified",
                   "Haskell says Ferdinand was a keen admirer of Luca Giordano but that the pictures he possessed are unknown.",
                   "The source explicitly states a knowledge gap; no Giordano work is identified.",
                   subject="cand-0914", obj="cand-7464", mentioned=["cand-0914", "cand-1172", "cand-7464"],
                   quote="He was also a keen admirer of Luca Giordano,7 but unfortunately we do not know which pictures by that artist he possessed.",
                   extra={"relation_candidate": True, "footnote_marker": 7}),
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
    if not (53 <= q["source_line_start"] <= q["source_line_end"] <= 60):
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
    if row["segment_id"] == PREVIOUS_SEGMENT_ID:
        row["note"] = "P.207 body was read against CHP-8.pdf physical p.5. The rhetorical question at L51 is closed by p.208 L54; p.207 notes 1-2 remain pending in the composite source."
    if row["segment_id"] == SEGMENT_ID:
        row.update({
            "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L54-60",
            "note": "P.208 body read against CHP-8.pdf physical p.6. Print readings corrected only in S2: Preti, We, lie, tonality, life, crystallised, still lives, Cavallino; the marker after brutal realism is 6 (S0 OCR 8). S0 remains unchanged. Footnotes 1-7 at composite source lines L114-120 remain pending migration.",
        })
    updated_coverage.append(row)

preview = {
    "mode": "dry-run",
    "segment": SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(body_statements),
    "coverage": {SEGMENT_ID: "reviewed/partial", PREVIOUS_SEGMENT_ID: "reviewed/partial"},
    "continuation_closed": {"previous_statement_id": PREVIOUS_STATEMENT_ID, "continuation_statement_id": CONTINUATION_STATEMENT_ID},
    "footnotes_pending": ["p.208 notes 1-7 at composite source lines L114-L120", "p.207 notes 1-2 at composite source lines L136-L137"],
    "ocr_corrections": ocr_corrections,
    "statement_ids": [row["statement_id"] for row in body_statements],
}

previous = next((row for row in statement_rows if row["statement_id"] == PREVIOUS_STATEMENT_ID), None)
if previous is None or previous["segment_id"] != PREVIOUS_SEGMENT_ID:
    raise SystemExit("p.207 open continuation statement not found; inspect before migration")
if previous["qualifiers"].get("continuation_status") != "open" or previous["qualifiers"].get("continuation_expected_segment_id") != SEGMENT_ID:
    raise SystemExit("p.207 continuation status changed; inspect before migration")
if CONTINUATION_STATEMENT_ID in existing_statement_ids:
    raise SystemExit("continuation statement already exists; inspect before rerunning")

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

previous["qualifiers"].update({
    "claim": "Haskell's rhetorical question about Roomer's disappointment in Preti's Venetian picture continues onto p.208 and is explicitly left unanswered for lack of evidence.",
    "qualification": "The question is not a settled report that Roomer stopped commissioning Preti. Its continuation and the author's statement that there is too little evidence are recorded in the linked p.208 statement.",
    "continuation_status": "closed",
    "continuation_segment_id": SEGMENT_ID,
    "continuation_statement_id": CONTINUATION_STATEMENT_ID,
})
previous["qualifiers"].pop("continuation_expected_segment_id", None)
previous["qualifiers"]["continuation_resolution"] = "Completed by p.208 L54; remains an unanswered rhetorical question."
for row in new_candidates:
    candidate_rows.append(row)
for row in new_mentions:
    mention_rows.append(row)
statement_rows.extend(body_statements)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, statement_rows)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
