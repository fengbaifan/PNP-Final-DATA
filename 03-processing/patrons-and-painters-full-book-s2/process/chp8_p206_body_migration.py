"""Controlled S2 migration for chapter 8 printed p.206 body text.

Default invocation is a read-only dry run. Printed-page readings are documented
in S2; immutable S0 transcriptions are never edited by this script.
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
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l30-41"
PREVIOUS_SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l23-28"
OPEN_STATEMENT_ID = "st-chp8-p205-roomer-owned-three-saraceni-paintings-open"
BACKUP_SUFFIX = ".bak-s2-chp8-p206-body-20260930"
EXPECTED_MAX_CANDIDATE = 7420


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
if not meta or meta["source_file"] != SOURCE_REL or (int(meta["line_start"]), int(meta["line_end"])) != (30, 41):
    raise SystemExit("p.206 segment metadata changed; review before migration")
raw_source = SOURCE_PATH.read_bytes()
if hashlib.sha256(raw_source).hexdigest() != meta["asset_sha256"]:
    raise SystemExit("source file fingerprint changed; rebuild segments and review")
source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[29:41])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != meta["sha256"]:
    raise SystemExit("p.206 segment text hash changed; review before migration")
if coverage_by_id.get(SEGMENT_ID, {}).get("disposition") != "queued":
    raise SystemExit("expected queued p.206 coverage; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("mentions already exist for p.206; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in statement_rows):
    raise SystemExit("statements already exist for p.206; inspect before rerunning")

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
    candidate("cand-7421", "Valentin (surname-only painter reference in Roomer's p.206 list)", "person",
              "The body names only Valentin. The index points to Valentin de Boulogne on p.206, but this body reference is kept source-local pending S3 identity alignment.", 31),
    candidate("cand-7422", "Brussels", "place",
              "City identified as Jan Vandeneynde's origin in Haskell's quoted inventory request.", 34),
    candidate("cand-7423", "War-scene paintings in Gaspar Roomer's collection, including Aniello Falcone's battle scenes", "work",
              "A source-specific group of war pictures; the body gives no individual titles or count, except that Falcone painted a number of lively battle scenes for Roomer.", 31),
    candidate("cand-7424", "Neapolitan painters described as unfamiliar with Roomer's foreign pictures", "term",
              "Unnamed professional group used as the comparison audience in Roomer's quoted statement; no membership is supplied.", 33),
    candidate("cand-7425", "Unidentified written statement by Roomer quoted in Haskell's account of his collection", "archive",
              "Haskell says Roomer wrote the quoted words about his pictures and inventory. The underlying letter or document is not identified or independently inspected.", 33),
    candidate("cand-7426", "Foreign painters and artists mentioned in Roomer's inventory quotation", "term",
              "Unnamed collective reference to the foreign makers of many pictures and to the painters Roomer wanted to summon for the inventory; exact overlap and membership are unspecified.", 33),
    candidate("cand-7427", "Small landscapes, sea-storms, animals and still-life paintings in Roomer's collection", "work",
              "Source-specific group of picture subjects described as characteristic of Roomer's native Flemish painters; individual works are not named.", 33),
    candidate("cand-7428", "Bassano (surname-only painter reference in Roomer's collection)", "person",
              "The body supplies only the surname Bassano. Do not assume Jacopo Bassano without S3 identity alignment.", 37),
    candidate("cand-7429", "Roman painting in Haskell's p.206 comparison", "term",
              "Source-local reference to what Haskell calls characteristic of Roman painting at the time; separate from other Roman-painting candidates pending S3.", 37),
    candidate("cand-7430", "Venetian colour in Haskell's p.206 comparison", "term",
              "Source-local artistic concept contrasted with Roman painting and classical discipline; cross-chapter identity remains for S3.", 37),
    candidate("cand-7431", "Classical discipline as an influence on Venetian colour", "term",
              "Haskell's interpretive concept in the p.206 comparison; preserve as the author's account, not a measurable historical mechanism.", 37),
    candidate("cand-7432", "Neapolitan paintings sent by Roomer to the Low Countries", "work",
              "Unspecified group of pictures in Roomer's art trade; Haskell names works by Bartolommeo Passante as a notable subset.", 38),
    candidate("cand-7433", "Pictures by Roomer's fellow-countrymen presumably received in exchange", "work",
              "Hypothetical group in Haskell's account of Roomer's trade; the exchange is explicitly presumed and no works are identified.", 39),
    candidate("cand-7434", "Susanna and the Elders (Van Dyck painting in Roomer's collection)", "work",
              "A painting identified by subject in Haskell's p.206 account; no date, version, or current location is supplied here.", 39),
    candidate("cand-7435", "St Sebastian (Van Dyck painting in Roomer's collection)", "work",
              "A painting identified by subject in Haskell's p.206 account; no date, version, or current location is supplied here.", 39),
    candidate("cand-7436", "Eight animal pictures attributed in Haskell's account to Bassano", "work",
              "An unnamed group of pictures said to be among the almost-only old masters in Roomer's collection; artist identity and individual works remain unresolved.", 37),
    candidate("cand-7437", "Unidentified daughter of Herodias depicted in Rubens's Feast of Herod", "person",
              "Unnamed figure represented in the painting. Her actions and expression are image content described by Haskell, not independent evidence about a historical person.", 40),
    candidate("cand-7438", "Herodias as represented in Rubens's Feast of Herod", "person",
              "Named image figure in the painting's subject. This candidate represents the depicted figure, not a claim about the historical event.", 40),
    candidate("cand-7439", "Unidentified tall girl holding John the Baptist's head in Rubens's Feast of Herod", "person",
              "Haskell first describes a tall girl holding the severed head, then separately names Herodias's daughter. The source does not explicitly say whether these are the same depicted figure; retain the distinction pending image-level review.", 40),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates) or new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate IDs collide")

mention_specs = []


def add_mention(surface, cid, note, occurrence=1):
    mention_specs.append((surface, cid, note, occurrence))


add_mention("Saraceni", "cand-2358", "Surname closing the p.205 page-break name Carlo Saraceni; the index lists Saraceni on p.206.")
add_mention("Valentin", "cand-7421", "Surname-only body reference; keep distinct from the indexed Valentin de Boulogne until S3.")
add_mention("Simon Vouet", "cand-2792", "Artist named among painters whose pictures Roomer acquired.")
add_mention("David de Haen", "cand-1285", "Artist named among painters whose pictures Roomer acquired.")
add_mention("Masaniello", "cand-4150", "Person named in Haskell's interpretation of Roomer's attitude to war and non-commitment.")
add_mention("Aniello Falcone", "cand-0987", "Artist said to have painted battle scenes for Roomer.")
add_mention("battle scenes without a hero", "cand-7423", "Description of the lively war pictures Falcone painted for Roomer; not treated as a verified formal title.")
add_mention("Roomer", "cand-2224", "Index subentry concerns Roomer and Flemish painting.", 1)
add_mention("small landscapes and storms at sea, the animals and still Eves with fruit and game piling up on the table", "cand-7427", "Picture subjects as transcribed in S0; print reads 'still lives' rather than OCR 'still Eves'.")
add_mention("Flemish painters", "cand-1040", "Index candidate 'Flemish artists in Rome' is indexed on this page.")
add_mention("Rome", "cand-4490", "Place where Haskell says many native Flemish painters settled for a time.")
add_mention("his collection", "cand-7407", "Roomer's collection whose pictures were to be inventoried.")
add_mention("foreign artists", "cand-7426", "Unspecified foreign painters represented among Roomer's pictures; linked to but not assumed identical with the inventory group.")
add_mention("Neapolitan painters", "cand-7424", "Unnamed comparison group in the quoted statement.")
add_mention("foreign painters", "cand-7426", "Unnamed painters Roomer wanted to summon for the inventory.")
add_mention("Jan Vandeneynde", "cand-2691", "Painter named by Haskell as the preferred inventory-maker.")
add_mention("Brussels", "cand-7422", "City identified as Vandeneynde's origin.")
add_mention("Paul Brill", "cand-0453", "Artist listed among the hundreds of pictures in Roomer's collection.")
add_mention("Peter de Witte", "cand-2817", "Artist listed among the hundreds of pictures in Roomer's collection.")
add_mention("Velvet Breughel", "cand-0449", "Artist listed under this printed/index form; spelling is retained from S0.")
add_mention("Leonard Bramer", "cand-0444", "Artist listed among the hundreds of pictures in Roomer's collection.")
add_mention("Jacques Duyvelant", "cand-0957", "Artist listed among the hundreds of pictures in Roomer's collection.")
add_mention("Cornelius\nPoelenburgh", "cand-1965", "Artist listed among the hundreds of pictures in Roomer's collection; the printed name is split across source lines.")
add_mention("Corneille Schut", "cand-2415", "Artist listed among the hundreds of pictures in Roomer's collection.")
add_mention("Gioffredo Wals", "cand-2800", "Artist listed among the hundreds of pictures in Roomer's collection.")
add_mention("Gerard van dor Bos", "cand-0917", "S0 OCR form; the print reads Gerard van der Bos.")
add_mention("many others", "cand-1040", "Open-ended remainder of the Flemish artist list; membership is not specified.")
add_mention("distant birthplace", "cand-4983", "Anaphoric reference to Antwerp, named as Roomer's birthplace on p.205.")
add_mention("adopted home", "cand-1722", "Anaphoric reference to Naples, where Roomer had settled.")
add_mention("Roman painting", "cand-7429", "Source-local artistic category in Haskell's comparison.")
add_mention("classical discipline", "cand-7431", "Haskell's interpretive account of the clarity and serenity he associates with Venetian colour.")
add_mention("Venetian colour", "cand-7430", "Source-local concept in Haskell's comparison.")
add_mention("Roomer", "cand-2223", "Main Gaspar Roomer candidate; the sentence concerns Haskell's qualified comment on his intellectual interests.", 2)
add_mention("Bassano", "cand-7428", "Surname-only body reference; do not resolve to Jacopo Bassano before S3.")
add_mention("eight animal pieces", "cand-7436", "Unspecified group of animal pictures; no titles or individual identifications are supplied.")
add_mention("Roomer", "cand-2223", "Main Roomer candidate in the sentence about the later gallery.", 3)
add_mention("hundreds of pictures", "cand-7407", "Scale of later acquisitions; Haskell says their nature is less documented.")
add_mention("Neapolitan paintings", "cand-7432", "Unspecified paintings sent from Naples toward the Low Countries.")
add_mention("Low Countries", "cand-4342", "Destination region in Haskell's account of Roomer's trade.")
add_mention("Bartolommeo Passante", "cand-1854", "Named Neapolitan painter whose works are given as a notable example.")
add_mention("fellow-countrymen", "cand-7433", "Works by Roomer's fellow-countrymen are only presumed to have arrived in exchange.")
add_mention("Van Dycks", "cand-0962", "Index candidate for Van Dyck paintings on p.206; exact artist identity is to be reconciled in S3.")
add_mention("Susanna and the Elders", "cand-7434", "One of the two Van Dyck pictures Haskell says was probably acquired locally.")
add_mention("St Sebastian", "cand-7435", "One of the two Van Dyck pictures Haskell says was probably acquired locally.")
add_mention("Naples", "cand-1722", "Local acquisition context is Naples; the sentence does not identify a seller or transaction.")
add_mention("Roomer", "cand-2227", "Index subentry concerns Roomer and Rubens's Feast of Herod.", 4)
add_mention("Rubens", "cand-2295", "Index entry specifies Rubens's Feast of Herod on p.206.")
add_mention("Feast of Herod", "cand-4092", "Reuses the existing accepted work candidate; the p.206 passage is about the same painting.")
add_mention("Roomer’s gallery", "cand-7407", "Collection context used to explain the painting's impact.")
add_mention("John the Baptist", "cand-3429", "The severed head is depicted in the painting; this is image content.")
add_mention("a tall, blowsy girl", "cand-7439", "Image figure described holding the severed head; the text does not explicitly identify her with Herodias's daughter.")
add_mention("daughter of Herodias", "cand-7437", "Unnamed figure depicted in the painting.")
add_mention("Herodias", "cand-7438", "Named as the mother of the unnamed daughter in the depicted scene.")
add_mention("Roomer", "cand-2223", "Haskell's interpretation that the depicted cruelty would have appealed to Roomer.", 5)
add_mention("Herod", "cand-4165", "Figure depicted at the head of the table; mention the occurrence in the final sentence, not the title.", 3)

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
        "mention_id": f"m-chp8-p206-{index:03d}",
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
        "printed_page": 206,
        "pdf_physical_page": 4,
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
    {"source_line": 33, "ocr": "still Eves", "print": "still lives", "basis": "CHP-8.pdf physical page 4."},
    {"source_line": 33, "ocr": "very sine", "print": "very fine", "basis": "CHP-8.pdf physical page 4."},
    {"source_line": 36, "ocr": "van dor Bos", "print": "van der Bos", "basis": "CHP-8.pdf physical page 4."},
    {"source_line": 38, "ocr": "Naples-—thereafter", "print": "Naples—thereafter", "basis": "CHP-8.pdf physical page 4."},
]

body_statements = [
    make_statement("st-chp8-p206-saraceni-closes-three-paintings-continuation", 31, 31,
                   "owned_three_paintings_by_artist-continuation",
                   "The surname Saraceni completes the preceding p.205 statement: Haskell says Roomer owned three paintings by Carlo Saraceni.",
                   "This fragment closes the p.205 name at the page break; the full sentence is anchored to the preceding statement. The index independently lists Carlo Saraceni on p.206.",
                   subject="cand-2223", obj="cand-2358", mentioned=["cand-2223", "cand-2358"],
                   quote="Saraceni;",
                   extra={"continuation_of_statement_id": OPEN_STATEMENT_ID, "continuation_status": "closed",
                          "continuation_source_segment_id": PREVIOUS_SEGMENT_ID, "continuation_source_line": 28,
                          "quantity": 3, "relation_candidate": True}),
    make_statement("st-chp8-p206-roomer-acquired-pictures-by-three-painters", 31, 31,
                   "acquired_pictures_by_painters",
                   "Haskell says Roomer also acquired pictures by Valentin, Simon Vouet and David de Haen.",
                   "The passage gives no titles, number, date, or transaction details. Valentin remains a surname-only body reference pending S3.",
                   subject="cand-2223", mentioned=["cand-2223", "cand-7421", "cand-2792", "cand-1285"],
                   quote="and he also acquired pictures by the Frenchmen Valentin and Simon Vouet and the Dutch David de Haen."),
    make_statement("st-chp8-p206-roomer-preferred-war-as-safe-picturesque-subject", 31, 31,
                   "patron_appealed_to_war_pictures_without_participation",
                   "Haskell says war appealed to Roomer when it could be viewed as a picturesque muddle without active participation; he reads Roomer's escape from Masaniello as confirming the attractions of non-commitment.",
                   "This is Haskell's interpretation of Roomer's taste and attitude, not a claim that Roomer took part in the revolt or that the battle pictures document combat.",
                   subject="cand-2223", obj="cand-7423", mentioned=["cand-2223", "cand-7423", "cand-4150"],
                   quote="War, too, appealed to him when it could be looked at safely as a picturesque muddle and required no active participation—his narrow escape from Masaniello surely confirmed the advantages of non-commitment",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p206-falcone-painted-battle-scenes-for-roomer", 31, 32,
                   "artist_painted_war_scenes_for_patron",
                   "Haskell says Aniello Falcone, whom Roomer particularly liked, painted a number of lively 'battle scenes without a hero' for him.",
                   "The number is unspecified and the quoted phrase is descriptive, not established as a formal title. Footnote marker 1 points to a note still pending in the composite notes segment.",
                   subject="cand-0987", obj="cand-2223",
                   mentioned=["cand-0987", "cand-2223", "cand-7423"],
                   quote="he was particularly fond of the young Aniello Falcone who painted for him a number of lively\n‘battle scenes without a hero’.1 -",
                   extra={"footnote_marker": 1, "relation_candidate": True}),
    make_statement("st-chp8-p206-roomer-liked-flemish-subject-categories", 33, 33,
                   "patron_preferred_flemish_picture_subjects",
                   "Haskell says Roomer especially liked small landscapes, storms at sea, animals and still-life pictures with fruit and game, which he describes as characteristic subjects of native Flemish painters.",
                   "The printed page reads 'still lives'; the S0 OCR has 'still Eves'. The passage describes subject preferences and a broad painter group, not a complete inventory.",
                   subject="cand-2223", obj="cand-7427",
                   mentioned=["cand-2223", "cand-7427", "cand-1040", "cand-4490"],
                   quote="But, above all, Roomer liked the small landscapes and storms at sea, the animals and still Eves with fruit and game piling up on the table, that were the special subjects of his native Flemish painters, many of whom settled for a time in Rome.",
                   extra={"ocr_corrections": [ocr_corrections[0]]}),
    make_statement("st-chp8-p206-flemish-painters-settled-temporarily-in-rome", 33, 33,
                   "painter_group_settled_temporarily_in_city",
                   "Haskell says many of the Flemish painters who treated these subjects settled for a time in Rome.",
                   "The group is not enumerated; 'many' is retained as the author's non-quantified description.",
                   subject="cand-1040", obj="cand-4490", mentioned=["cand-1040", "cand-4490"],
                   quote="many of whom settled for a time in Rome."),
    make_statement("st-chp8-p206-roomer-quoted-inventory-request", 33, 34,
                   "collector_requested_foreign_painters_to_make_inventory",
                   "Haskell quotes Roomer as saying his pictures were very fine and mostly by foreign artists unfamiliar to Neapolitan painters, and that he wanted foreign painters, especially Jan Vandeneynde of Brussels, to draw up the inventory.",
                   "The speaker is Roomer as quoted by Haskell. The underlying document is not identified or independently inspected. OCR 'very sine' reads 'very fine' in print; the requested inventory is not evidence that it was completed.",
                   subject="cand-2223", obj="cand-7425",
                   mentioned=["cand-2223", "cand-7407", "cand-7424", "cand-7425", "cand-7426", "cand-2691", "cand-7422"],
                   quote="He was particularly proud of these—‘as all the pictures are very sine’, he wrote, ‘and as most of them are by foreign artists, unfamiliar to Neapolitan painters, I want foreign painters to be summoned to draw up the inventory; especially the painter Jan Vandeneynde of\nBrussels and others whom he chooses’",
                   extra={"speaker": "Roomer, as quoted by Haskell", "quoted_by": "Haskell",
                          "ocr_corrections": [ocr_corrections[1]]}),
    make_statement("st-chp8-p206-roomer-owned-hundreds-by-flemish-artists", 34, 36,
                   "owned_several_hundred_pictures_by_named_artists",
                   "Haskell says Roomer owned several hundreds of works by Paul Brill, Peter de Witte, Velvet Breughel, Leonard Bramer, Jacques Duyvelant, Cornelius Poelenburgh, Corneille Schut, Gioffredo Wals, Gerard van der Bos and many others.",
                   "The quantity is approximate and the list explicitly remains open. The print reads 'Gerard van der Bos'; S0 OCR has 'van dor Bos'.",
                   subject="cand-2223", obj="cand-7407",
                   mentioned=["cand-2223", "cand-7407", "cand-0453", "cand-2817", "cand-0449", "cand-0444",
                              "cand-0957", "cand-1965", "cand-2415", "cand-2800", "cand-0917", "cand-1040"],
                   quote="and he owned several hundreds by Paul Brill,\nPeter de Witte, Velvet Breughel, Leonard Bramer, Jacques Duyvelant, Cornelius\nPoelenburgh, Corneille Schut, Gioffredo Wals, Gerard van dor Bos and many others.",
                   extra={"quantity_text": "several hundreds", "relation_candidate": True,
                          "ocr_corrections": [ocr_corrections[2]]}),
    make_statement("st-chp8-p206-roomer-collection-bridged-flemish-and-neapolitan-cultures", 37, 37,
                   "author_interpreted_collection_as_cultural_intermixture",
                   "Haskell interprets images of plenty and wild fertility from Roomer's distant birthplace as mingling with cruelty and lusts associated with his adopted home.",
                   "This is Haskell's evaluative interpretation. 'Distant birthplace' refers back to Antwerp on p.205 and 'adopted home' to Naples; neither phrase names a new place.",
                   subject="cand-7407", mentioned=["cand-2223", "cand-7407", "cand-4983", "cand-1722"],
                   quote="Images of plenty and wild fertility, the landscapes and produce of his distant birthplace mingled with the cruelty and lusts of his adopted home."),
    make_statement("st-chp8-p206-haskell-compared-roman-painting-and-venetian-colour", 37, 37,
                   "author_compared_roman_painting_with_classical_venetian_colour",
                   "Haskell says the clarity and serenity he associates with Roman painting were missing, and describes classical discipline as having imposed them on Venetian colour.",
                   "This is Haskell's art-historical comparison. The concepts are source-local candidates pending S3; the sentence does not establish an objective measure of either tradition.",
                   subject="cand-7429", obj="cand-7430", mentioned=["cand-7429", "cand-7430", "cand-7431"],
                   quote="What was missing was just what was most characteristic of Roman painting at the time: the clarity and serenity which classical discipline had imposed on Venetian colour."),
    make_statement("st-chp8-p206-bassano-animal-pieces-qualified-authorial-inference", 37, 37,
                   "author_inferred_collection_had_almost_only_eight_animal_old_masters",
                   "Haskell suggests it was perhaps characteristic of Roomer's lack of intellectual interests that almost the only old masters in his collection were eight animal pictures attributed only by the surname Bassano.",
                   "Preserve 'perhaps' and 'almost' as Haskell's inference and qualifier; the source gives no titles and does not identify which Bassano.",
                   subject="cand-2223", obj="cand-7436",
                   mentioned=["cand-2223", "cand-7407", "cand-7428", "cand-7436"],
                   quote="It is perhaps characteristic of Roomer’s lack of intellectual interests that almost the only old masters in his collection were eight animal pieces by Bassano.",
                   extra={"inference": True, "ocr_corrections": []}),
    make_statement("st-chp8-p206-later-roomer-collection-less-documented", 38, 38,
                   "later_collection_growth_with_reduced_source_information",
                   "Haskell says Roomer continued to buy hundreds of pictures after his early Naples gallery, but their nature is much less documented and must be inferred from indirect sources.",
                   "This records Haskell's stated evidence gap; it does not treat the indirect sources as inspected in this passage.",
                   subject="cand-2223", obj="cand-7407", mentioned=["cand-2223", "cand-7407"],
                   quote="Such was Roomer’s gallery in his early days in Naples-—thereafter, although he went on buying hundreds of pictures, we have much less information about their nature, and have to rely on a variety of indirect sources.",
                   extra={"ocr_corrections": [ocr_corrections[3]]}),
    make_statement("st-chp8-p206-roomer-sent-neapolitan-paintings-to-low-countries", 38, 38,
                   "picture_trade_sent_neapolitan_works_to_low_countries",
                   "Haskell says Roomer traded pictures and sent Neapolitan paintings to the Low Countries, notably works by Ribera's pupil Bartolommeo Passante.",
                   "No shipment date, quantity, transaction, or named individual work is supplied.",
                   subject="cand-2223", obj="cand-7432",
                   mentioned=["cand-2223", "cand-7432", "cand-4342", "cand-1854"],
                   quote="We know that all this time he was keenly trading in pictures as well as in other goods—sending Neapolitan paintings to the Low Countries (notably those of Ribera’s pupil, Bartolommeo Passante)",
                   extra={"relation_candidate": True}),
    make_statement("st-chp8-p206-roomer-presumably-received-flemish-pictures-in-exchange", 38, 39,
                   "picture_trade_presumably_received_works_in_exchange",
                   "Haskell presumes Roomer received works by his fellow-countrymen in exchange for paintings sent to the Low Countries.",
                   "The exchange is explicitly presented as presumptive; no specific received work or transaction is identified.",
                   subject="cand-2223", obj="cand-7433",
                   mentioned=["cand-2223", "cand-7433", "cand-1040"],
                   quote="and, presumably, receiving in exchange works by his fellow-countrymen",
                   extra={"modality": "presumed", "relation_candidate": True}),
    make_statement("st-chp8-p206-van-dyck-pictures-probably-acquired-locally", 38, 39,
                   "two_van_dyck_pictures_probably_acquired_locally",
                   "Haskell says Roomer's two Van Dyck pictures, Susanna and the Elders and St Sebastian, were probably acquired locally.",
                   "Both local acquisition and the artist-to-work attribution are Haskell's qualified account; no seller, date, or current location is given.",
                   subject="cand-2223", mentioned=["cand-2223", "cand-0962", "cand-7434", "cand-7435", "cand-1722"],
                   quote="though his two\nVan Dycks—a Susanna and the Elders and a St Sebastian—were probably acquired locally.",
                   extra={"probability": "probably", "relation_candidate": True}),
    make_statement("st-chp8-p206-feast-of-herod-arrived-roomers-palace-c1640", 39, 40,
                   "painting_arrived_at_collectors_palace_approximately_1640",
                   "Haskell says Rubens's large Feast of Herod reached Roomer's palace in about 1640 and was one of the most important pictures in his collection.",
                   "The date is approximate. The palace is not identified as either Via Monteoliveto or Palazzo della Stella.",
                   subject="cand-2223", obj="cand-4092", mentioned=["cand-2223", "cand-2295", "cand-4092", "cand-7407"],
                   quote="In about 1640 one of the most important of all his pictures reached his palace—\nRubens’s large Feast of Herod",
                   extra={"date_text": "about 1640", "relation_candidate": True}),
    make_statement("st-chp8-p206-rubens-feast-of-herod-maturity-and-approximate-date", 40, 40,
                   "painting_described_as_mature_work_created_probably_six_years_earlier",
                   "Haskell calls the Feast of Herod a work of Rubens's full maturity, probably painted about half a dozen years before its arrival.",
                   "Both the maturity assessment and relative date are Haskell's; 'probably' and 'some half a dozen years' remain approximate. Plate 35b and footnote marker 2 are cited; the note remains pending.",
                   subject="cand-4092", obj="cand-2295", mentioned=["cand-4092", "cand-2295"],
                   quote="a work of the artist’s full maturity painted probably some half a dozen years earlier (Plate 35b).2",
                   extra={"footnote_marker": 2, "relative_date_text": "probably some half a dozen years earlier"}),
    make_statement("st-chp8-p206-feast-of-herod-made-impact-in-naples", 40, 40,
                   "painting_had_impact_because_it_was_unfamiliar_in_roomers_gallery",
                   "Haskell says the Feast of Herod made a great impact in Naples because it differed from anything previously seen in Roomer's gallery.",
                   "The claim is Haskell's assessment of reception, not a documented response by named viewers.",
                   subject="cand-4092", obj="cand-1722", mentioned=["cand-4092", "cand-1722", "cand-2223", "cand-7407"],
                   quote="It caused a great impact in Naples, for it was quite unlike anything that had hitherto been seen in Roomer’s gallery."),
    make_statement("st-chp8-p206-feast-of-herod-depicts-luxury-crowded-room-and-attendants", 40, 40,
                   "painting_depicts_crowded_luxurious_feast_and_attendants",
                   "Haskell describes the painting as a crowded, stifling, luxurious feast watched by richly dressed guests, a boy with a monkey and servants.",
                   "This is a description of the image, including the source's historical wording for the servants; it is not a claim about an independently verified historical event.",
                   subject="cand-4092", mentioned=["cand-4092"],
                   quote="The feast takes place in a crowded, stifling room full of luxury and extravagance while richly dressed guests, a boy with a monkey and negro servants all look on."),
    make_statement("st-chp8-p206-feast-of-herod-depicts-girl-holding-john-baptist-head", 40, 40,
                   "painting_depicts_tall_girl_holding_john_baptists_head",
                   "Haskell describes a tall girl in the foreground holding John the Baptist's severed head on a silver plate.",
                   "This is image content. The source does not explicitly identify this girl with the daughter of Herodias named in the next clause, so the two candidate figures remain separate.",
                   subject="cand-7439", obj="cand-4092", mentioned=["cand-4092", "cand-7439", "cand-3429"],
                   quote="In the foreground a tall, blowsy girl holds the severed head of John the Baptist on a silver plate"),
    make_statement("st-chp8-p206-feast-of-herod-depicts-daughter-of-herodias", 40, 40,
                   "painting_depicts_daughter_of_herodias_preparing_to_stab_tongue",
                   "Haskell describes the unnamed daughter of Herodias with a strange, flirtatious expression, preparing to stab the offending tongue with a fork.",
                   "This is image content, not evidence about a historical person's actions. The source does not explicitly identify the daughter with the tall girl described immediately before.",
                   subject="cand-7437", obj="cand-4092", mentioned=["cand-4092", "cand-7437", "cand-7438"],
                   quote="and the daughter of Herodias, with a strange, flirtatious expression, makes ready to stab the offending tongue with a fork"),
    make_statement("st-chp8-p206-haskell-suggested-depicted-cruelty-appealed-to-roomer", 40, 40,
                   "author_inferred_depicted_cruelty_would_appeal_to_patron",
                   "Haskell says the depicted cruelty must have appealed to Roomer.",
                   "This is the author's inference about a patron's taste, not a direct statement by Roomer.",
                   subject="cand-2223", obj="cand-4092", mentioned=["cand-2223", "cand-4092"],
                   quote="a touch of cruelty that must have appealed to Roomer",
                   extra={"inference": True, "relation_candidate": True}),
    make_statement("st-chp8-p206-herod-depicted-as-aware-of-injustice", 41, 41,
                   "painting_depicts_herod_as_anxiously_aware_of_injustice",
                   "Haskell reads the depicted Herod as the only figure anxiously aware that a terrible injustice has been done.",
                   "This is Haskell's interpretation of the figure's expression within the painting, not evidence about the historical Herod's thoughts.",
                   subject="cand-4165", obj="cand-4092", mentioned=["cand-4165", "cand-4092"],
                   quote="Only Herod, seated at the head of the table, with his chin cupped in his hand, looks anxiously aware that a terrible injustice has been done."),
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
    if not (30 <= q["source_line_start"] <= q["source_line_end"] <= 41):
        raise SystemExit(f"statement line range outside segment: {row['statement_id']}")
    mentioned = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        mentioned.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        mentioned.add(row["object_candidate_id"])
    if not mentioned <= candidate_ids | new_candidate_ids:
        raise SystemExit(f"statement references missing candidate: {row['statement_id']}")

open_row = next((row for row in statement_rows if row["statement_id"] == OPEN_STATEMENT_ID), None)
if not open_row or open_row.get("qualifiers", {}).get("continuation_status") != "open":
    raise SystemExit("p.205 continuation is not open as expected; inspect before migration")
if open_row.get("qualifiers", {}).get("continuation_expected_segment_id") != SEGMENT_ID:
    raise SystemExit("p.205 continuation target changed; inspect before migration")
updated_open = json.loads(json.dumps(open_row))
updated_open["qualifiers"].update({
    "claim": "Haskell says Roomer owned three paintings by Carlo Saraceni.",
    "qualification": "The printed name is split at the page break: p.205 ends with Carlo and p.206 L31 supplies Saraceni. The p.206 continuation statement records the closing fragment.",
    "continuation_status": "closed",
    "continuation_closed_by_segment_id": SEGMENT_ID,
    "continuation_closed_by_source_line": 31,
    "continuation_resolved_by_segment": SEGMENT_ID,
    "continuation_resolved_by_source_line": 31,
    "continuation_fragment": "Saraceni;",
})
updated_open["qualifiers"].pop("continuation_expected_segment_id", None)
updated_open["qualifiers"].pop("continuation_note", None)
if updated_open["object_candidate_id"] != "cand-2358":
    raise SystemExit("p.205 partial artist candidate is not Carlo Saraceni; inspect before closing")

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == SEGMENT_ID:
        row.update({
            "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L31-41",
            "note": "P.206 body read against CHP-8.pdf physical p.4. Print readings corrected only in S2: 'still lives', 'very fine', 'Gerard van der Bos', and 'Naples—thereafter'; S0 remains unchanged. The dash after note marker 1 at L32 is left unresolved. Footnotes 1–2 remain in composite source lines L134–135. P.205 Carlo Saraceni continuation is closed here.",
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
    "p205_continuation": {"statement_id": OPEN_STATEMENT_ID, "status": "closed", "by_segment": SEGMENT_ID, "by_source_line": 31},
    "footnotes_pending": ["p.206 notes 1-2 at composite source lines 134-135"],
    "ocr_corrections": ocr_corrections,
    "unresolved_scan_readings": ["dash after footnote marker 1 at p.206 L32"],
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
for row in statement_rows:
    if row["statement_id"] == OPEN_STATEMENT_ID:
        row.clear()
        row.update(updated_open)
statement_rows.extend(body_statements)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, statement_rows)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
