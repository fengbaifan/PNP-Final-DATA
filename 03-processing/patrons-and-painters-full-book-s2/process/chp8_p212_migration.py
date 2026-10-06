"""Controlled S2 migration for chapter 8 printed p.212.

The default invocation is read-only. It checks the canonical section OCR,
current table state, cross-page continuation from p.211, and all planned
mentions/statements before any write. Footnotes 1-5 remain in the later S0
footnote segment and are deliberately not migrated here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
BODY_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
P211_NOTES_REL = "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p211_visual-transcription.md"
P211_BODY_ID = "chp-8:08_CHP-8_sec_i:l84-96"
P211_NOTES_ID = "chp-8:08_CHP-8_sec_i_notes_p211_visual-transcription:l1-4"
BODY_ID = "chp-8:08_CHP-8_sec_i:l98-106"
NEXT_ID = "chp-8:08_CHP-8_sec_i:l108-118"
P211_OPEN = "st-chp8-p211-forebears-grandfather-open"
P211_COLLECTION_MENTION = "m-chp8-p211-016"
BACKUP_SUFFIX = ".bak-s2-chp8-p212-20260930"
EXPECTED_MAX_CANDIDATE = 7519


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
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


def load_segment(segment_id: str, relative_path: str, start: int, end: int, expected_status: tuple[str, str]):
    meta = segments.get(segment_id)
    if not meta or meta["source_file"] != relative_path or (int(meta["line_start"]), int(meta["line_end"])) != (start, end):
        raise SystemExit(f"segment metadata changed; review before migration: {segment_id}")
    path = ROOT / relative_path
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset fingerprint changed: {relative_path}")
    all_lines = path.read_text(encoding="utf-8-sig").splitlines()
    sliced = all_lines[start - 1:end]
    text = "\n".join(sliced)
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"source line-slice hash changed: {segment_id}")
    cov = coverage_by_id.get(segment_id, {})
    if (cov.get("disposition"), cov.get("migration_status")) != expected_status:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {cov}")
    return meta, all_lines, sliced, text


p211_meta, p211_all_lines, p211_lines, p211_text = load_segment(
    P211_BODY_ID, BODY_REL, 84, 96, ("reviewed", "partial"))
p211_notes_meta, p211_notes_all_lines, p211_notes_lines, p211_notes_text = load_segment(
    P211_NOTES_ID, P211_NOTES_REL, 1, 4, ("reviewed", "complete"))
body_meta, body_all_lines, body_lines, body_text = load_segment(
    BODY_ID, BODY_REL, 98, 106, ("queued", "pending"))

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")


CANDIDATE_SPECS = [
    ("del_rosso_collection", "Del Rosso brothers' picture collection (type unresolved)", "",
     "The brothers' picture collection is explicit in p.211 and p.211 note 1. Collection is not a current KU type; preserve as an untyped candidate pending the project's taxonomy decision.", P211_BODY_ID, 88),
    ("gaetano_church", "Theatine church of S. Gaetano in Florence (building identity unverified)", "place",
     "The passage names the church and situates it in the Florentine family context; no external building identification is asserted.", BODY_ID, 99),
    ("family_chapel", "Del Rosso family chapel in the Theatine church of S. Gaetano", "place",
     "Interior chapel described as built for Andrea del Rosso and dedicated to his name-saint; keep spatial unit distinct from the church and its artworks.", BODY_ID, 99),
    ("andrea_name_saint", "Unidentified name-saint of Andrea del Rosso", "person",
     "Haskell says the family chapel was dedicated to Andrea's name-saint but does not name the saint.", BODY_ID, 99),
    ("vannini_frescoes", "Unidentified Ottavio Vannini frescoes in the Del Rosso family chapel", "work",
     "Plural chapel frescoes; no individual subjects or surviving state identified in this passage.", BODY_ID, 99),
    ("altar_picture", "Unidentified altar picture for the Del Rosso family chapel", "work",
     "Vannini left the altar picture to be completed by a pupil; the text does not say that completion occurred.", BODY_ID, 99),
    ("pupil", "Unidentified pupil of Ottavio Vannini connected with the chapel altar picture", "person",
     "Unnamed pupil whom Vannini left to complete the altar picture; no identity or completed outcome is given.", BODY_ID, 99),
    ("four_vannini_scenes", "Four Old Testament scenes made by Ottavio Vannini for the Del Rosso house", "work",
     "Group candidate for the four individually named pictures listed in p.212; keep the individual works as separate candidates too.", BODY_ID, 100),
    ("sacrifice_isaac", "The Sacrifice of Isaac (Vannini scene for the Del Rosso house)", "work",
     "One of the four Old Testament scenes Haskell says Vannini produced for the house; no present location is stated here.", BODY_ID, 101),
    ("fall_manna", "The Fall of Manna (Vannini scene for the Del Rosso house)", "work",
     "One of the four Old Testament scenes Haskell says Vannini produced for the house; p.212 footnote 2 later cites publication of this picture.", BODY_ID, 101),
    ("moses_rock", "Moses striking the Rock (Vannini scene for the Del Rosso house)", "work",
     "One of the four Old Testament scenes Haskell says Vannini produced for the house; p.212 footnote 2 later cites publication of this picture.", BODY_ID, 101),
    ("susanna_elders", "Susanna and the Elders (Vannini scene for the Del Rosso house)", "work",
     "One of the four Old Testament scenes Haskell says Vannini produced for the house; no present location is stated here.", BODY_ID, 101),
    ("other_vannini_pictures", "Other Ottavio Vannini pictures owned by the Del Rosso family, mainly saints", "work",
     "Unidentified group of pictures distinct from the four named Old Testament scenes.", BODY_ID, 101),
    ("disegno_tradition", "Florentine disegno tradition described on p.212", "term",
     "Artistic tradition named in Haskell's evaluative description; not treated as a pre-established hierarchy node.", BODY_ID, 101),
    ("neapolitan_pictures", "More than one hundred Neapolitan pictures introduced into the Del Rosso household", "work",
     "Group of pictures; Haskell says some came from the dispersed Roomer collection and more than sixty were by Luca Giordano. Do not infer individual titles or acquisition routes for the whole group.", BODY_ID, 102),
    ("roomer_subset", "Unidentified Del Rosso pictures said to come from the dispersed Roomer collection", "work",
     "An unspecified subset of the Neapolitan pictures; Haskell does not give its count or individual identities.", BODY_ID, 103),
    ("roomer_dispersal", "Dispersal of Gaspar Roomer's picture collection in 1674", "event",
     "Dated collection-dispersal event as reported by Haskell; no further process or date is inferred.", BODY_ID, 103),
    ("giordano_pictures", "Luca Giordano pictures in the Del Rosso holdings (more than sixty)", "work",
     "Unidentified group; Haskell gives a lower-bound count and says some were already owned before Giordano's 1679 visit.", BODY_ID, 103),
    ("grand_duke_1613", "Unnamed Grand Duke of Tuscany in the 1613 letter", "person",
     "Office-holder in the source's 1613 report; do not identify with a named duke without later evidence.", BODY_ID, 103),
    ("viceroy_1613", "Unnamed Spanish Viceroy addressed in the 1613 letter", "person",
     "Viceroy named by office only; do not merge with other Spanish viceroy candidates before global alignment.", BODY_ID, 103),
    ("antonio_1613", "Antonio del Rosso named in the 1613 letter (identity unresolved)", "person",
     "Father of the quoted sons and heirs in Haskell's report; keep distinct from the later Antonio among Nicola's heirs until S3 resolves identity.", BODY_ID, 103),
    ("sons_heirs_1613", "Unidentified sons and heirs of Antonio del Rosso in the 1613 report", "term",
     "Plural persons described as Florentines living and trading in Naples; do not identify them as Andrea and Lorenzo solely from adjacency.", BODY_ID, 103),
    ("letter_1613", "1613 Grand Duke of Tuscany letter to the Spanish Viceroy about Antonio del Rosso's sons and heirs", "archive",
     "Document described in the body; p.212 footnote 4 gives Biblioteca Nazionale, Florence, Poligrafo Gargano as its locator. The document itself is not independently consulted.", BODY_ID, 103),
    ("family_house_1679", "Del Rosso family house in Florence where Luca Giordano stayed in 1679", "place",
     "Haskell does not name the house here. It may be the Via Chiara house mentioned at p.210, but keep identity open for S3.", BODY_ID, 105),
    ("giordano_visit_1679", "Luca Giordano's visit to Florence and stay with the Del Rosso family in 1679", "event",
     "Visit and lodging reported by Haskell; no exact dates beyond the year are given.", BODY_ID, 105),
    ("carmine_church", "Church of the Carmine in Florence (as named by Haskell)", "place",
     "Church containing the Corsini chapel; keep church building distinct from its interior chapel and frescoes.", BODY_ID, 105),
    ("corsini_chapel", "Corsini chapel in the Church of the Carmine, Florence", "place",
     "Interior chapel referred to as the subject of a possible Giordano commission; distinct from the church and the paintings.", BODY_ID, 105),
    ("corsini_commission", "Possible Luca Giordano commission for the Corsini chapel in the Carmine", "event",
     "Haskell says it may well have been arranged by the Del Rosso brothers; preserve the uncertainty and do not treat the commissioning agent as settled.", BODY_ID, 105),
    ("corsini_paintings", "Unidentified Luca Giordano paintings for the Corsini chapel in the Carmine", "work",
     "Group implied by the commission and chapel reference; no individual painting title or count is given.", BODY_ID, 105),
    ("corsini_bozzetto", "Original bozzetto for one pendentive in the Corsini chapel", "work",
     "The Del Rosso brothers reportedly owned it; the sentence does not independently name its maker or identify the corresponding finished pendentive image.", BODY_ID, 105),
    ("corsini_pendentive", "Unidentified pendentive image in the Corsini chapel associated with the bozzetto", "work",
     "The source identifies only one of the chapel pendentives; do not assign a subject or finished-work identity.", BODY_ID, 105),
    ("giordano_erotic_group", "Unidentified erotic paintings by Luca Giordano for the Del Rosso brothers", "work",
     "A large but unnumbered subset of Giordano's pictures for the brothers; examples continue on p.213.", BODY_ID, 106),
    ("venus_amor_theme", "Venus and Amor pictorial theme in Luca Giordano's paintings for the Del Rosso brothers", "term",
     "Theme named in an unfinished sentence; p.213 is required to complete the example and its referent.", BODY_ID, 106),
]

new_candidates = []
candidate_by_key = {}
next_candidate_number = current_max + 1
for key, name, typ, detail, source_segment, source_line in CANDIDATE_SPECS:
    cid = f"cand-{next_candidate_number:04d}"
    next_candidate_number += 1
    candidate_by_key[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": typ, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{source_segment}#L{source_line}",
    })

EXISTING = {
    "family": "cand-7489",
    "roomer_collection": "cand-7407",
    "grandfather_andrea": "cand-2279",
    "andrea": "cand-2275",
    "lorenzo": "cand-2282",
    "vannini": "cand-2694",
    "theatines": "cand-3404",
    "dolci": "cand-0923",
    "giordano": "cand-1172",
    "roomer_person": "cand-2223",
    "florence": "cand-1041",
    "naples": "cand-3534",
    "tuscany": "cand-6232",
    "riccardi_palace": "cand-2145",
    "riccardi_frescoes": "cand-7234",
    "corsini_family": "cand-0863",
}


def cid(key: str) -> str:
    return candidate_by_key[key] if key in candidate_by_key else EXISTING[key]


def source_text_and_lines(segment_id: str):
    if segment_id == P211_BODY_ID:
        return p211_text, p211_all_lines, 84, 96
    if segment_id == P211_NOTES_ID:
        return p211_notes_text, p211_notes_all_lines, 1, 4
    if segment_id == BODY_ID:
        return body_text, body_all_lines, 98, 106
    raise SystemExit(f"unrecognized source segment: {segment_id}")


def add_mentions(segment_id: str, specs, prefix: str, first_number: int = 1):
    segment_text, all_lines, seg_start, seg_end = source_text_and_lines(segment_id)
    if not (seg_start <= min(s[0] for s in specs) and max(s[0] for s in specs) <= seg_end):
        raise SystemExit(f"mention line outside source segment: {segment_id}")
    line_offsets = {}
    offset = 0
    for line_no in range(seg_start, seg_end + 1):
        line_offsets[line_no] = offset
        offset += len(all_lines[line_no - 1]) + 1
    result = []
    for idx, (line_no, surface, key, occurrence, note) in enumerate(specs, start=first_number):
        line = all_lines[line_no - 1]
        # Printed footnote markers are attached directly to the cited word in
        # this source (for example, "family3"). Permit a trailing digit while
        # still anchoring the entity span before the marker.
        spans = [m.span() for m in re.finditer(r"(?<!\w)" + re.escape(surface) + r"(?=$|[^\w]|\d)", line)]
        if occurrence >= len(spans):
            raise SystemExit(f"mention not found: {segment_id} L{line_no} {surface!r} occurrence {occurrence}; found {len(spans)}")
        start_local, end_local = spans[occurrence]
        start_char = line_offsets[line_no] + start_local
        end_char = line_offsets[line_no] + end_local
        if segment_text[start_char:end_char] != surface:
            raise SystemExit(f"mention offset mismatch: {segment_id} L{line_no} {surface!r}")
        result.append({
            "mention_id": f"{prefix}-{idx:03d}", "segment_id": segment_id,
            "candidate_id": cid(key), "surface_form": surface,
            "start_char": str(start_char), "end_char": str(end_char), "note": note,
        })
    return result


P211_BACKFILL_SPECS = [
    (88, "their", "family", 0, "Possessive referent is the Del Rosso brothers; the following noun refers to their distinct, currently untyped collection."),
]
P211_NOTES_BACKFILL_SPECS = [
    (1, "collection of the del Rosso brothers", "del_rosso_collection", 0,
     "The collection is an entity distinct from the Del Rosso family; its type is not represented in the current taxonomy."),
]
P212_MENTION_SPECS = [
    (99, "Andrea", "grandfather_andrea", 0, "Names the grandfather introduced at p.211 L89; distinct from the younger Andrea del Rosso named later on this page."),
    (99, "Theatine", "theatines", 0, "The religious order used adjectivally for the church; the building is a separate place candidate."),
    (99, "S. Gaetano", "gaetano_church", 0, "Named church building; no external building identification is assumed."),
    (99, "family chapel", "family_chapel", 0, "Chapel space within the S. Gaetano church, distinct from the church and its artworks."),
    (99, "his", "grandfather_andrea", 0, "Anaphoric reference to the grandfather Andrea identified at the start of the cross-page sentence."),
    (99, "name-saint", "andrea_name_saint", 0, "Unidentified saint to whom the chapel was dedicated; the passage does not name the saint."),
    (99, "This", "family_chapel", 0, "Anaphoric reference to the family chapel."),
    (99, "frescoes", "vannini_frescoes", 0, "Unidentified chapel fresco group."),
    (99, "Ottavio Vannini", "vannini", 0, "Artist named as the chapel fresco painter."),
    (99, "himself", "vannini", 0, "Anaphoric reference to Ottavio Vannini."),
    (99, "altar picture", "altar_picture", 0, "Unidentified chapel altar picture; completion is not established."),
    (99, "pupil", "pupil", 0, "Unidentified pupil whom Vannini left to complete the altar picture."),
    (100, "Vannini", "vannini", 0, "Anaphoric surname reference to Ottavio Vannini."),
    (100, "family painter", "family", 0, "Describes Vannini's role for the Del Rosso family."),
    (100, "four large scenes", "four_vannini_scenes", 0, "Group label for the four individually named paintings on the next source line."),
    (100, "Old Testament", "four_vannini_scenes", 0, "Subject category of the four named scenes; mapped to this source-specific work group."),
    (101, "The Sacrifice of Isaac", "sacrifice_isaac", 0, "Individually named Vannini picture in the four-scene group."),
    (101, "The Fall of Manna", "fall_manna", 0, "Individually named Vannini picture in the four-scene group."),
    (101, "Moses striking the Rock", "moses_rock", 0, "Individually named Vannini picture in the four-scene group."),
    (101, "Susanna and the Elders", "susanna_elders", 0, "Individually named Vannini picture in the four-scene group."),
    (101, "he", "vannini", 0, "Anaphoric subject of the claim that he produced the four pictures."),
    (101, "the house", "family_house_1679", 0, "Del Rosso family house; possibly the Via Chiara house at p.210, but identity remains open."),
    (101, "his", "vannini", 0, "Anaphoric reference to Vannini in Haskell's evaluation of the four works."),
    (101, "finest works", "four_vannini_scenes", 0, "Refers to the four named Old Testament pictures."),
    (101, "del Rosso", "family", 0, "The Del Rosso family that owned the other Vannini pictures."),
    (101, "him", "vannini", 0, "Anaphoric reference to Vannini as painter of the other pictures."),
    (101, "other pictures", "other_vannini_pictures", 0, "Unidentified group distinct from the four named Old Testament scenes."),
    (101, "Florentine", "florence", 0, "Gentilic reference to Florence in the phrase 'Florentine disegno'."),
    (101, "disegno", "disegno_tradition", 0, "Italian art-theoretical term as used in Haskell's description."),
    (101, "that city", "florence", 0, "Anaphoric reference to Florence in the description of one section of its painting."),
    (102, "household", "family", 0, "Refers to the Del Rosso family household."),
    (102, "Carlo Dolci", "dolci", 0, "Painter said to have painted for the Del Rosso family."),
    (102, "del Rosso family", "family", 0, "Family for whom Carlo Dolci painted."),
    (102, "new generation", "family", 0, "Later generation of the Del Rosso family; individuals are not identified by this phrase."),
    (102, "over a hundred Neapolitan pictures", "neapolitan_pictures", 0, "Unidentified picture group introduced into the household; count is 'over a hundred'."),
    (102, "Neapolitan", "naples", 0, "Origin adjective in the picture-group description; it does not prove that every work was made in Naples."),
    (102, "Roomer collection", "roomer_collection", 0, "Gaspar Roomer's collection as the source of an unspecified subset of pictures; collection type remains unresolved."),
    (102, "its", "roomer_collection", 0, "Anaphoric possessive referring to the Roomer collection."),
    (102, "dispersal", "roomer_dispersal", 0, "The collection dispersal reported as occurring in 1674."),
    (102, "more than sixty", "giordano_pictures", 0, "Lower-bound count of pictures by Luca Giordano within the larger Neapolitan group."),
    (102, "Luca Giordano", "giordano", 0, "Artist named as maker of more than sixty pictures."),
    (102, "the family history", "family", 0, "The family whose Naples connections are discussed."),
    (102, "Naples", "naples", 0, "City named as the locus of the family's connections."),
    (102, "Grand Duke of", "grand_duke_1613", 0, "Unnamed 1613 office-holder; the title continues with Tuscany at the start of the next S0 line."),
    (103, "Tuscany", "tuscany", 0, "Geographic/political territory in the duke's title."),
    (103, "Spanish Viceroy", "viceroy_1613", 0, "Unnamed addressee identified by office only."),
    (103, "some subjects of his", "sons_heirs_1613", 0, "Collective referent explained by the following quotation; 'his' most naturally points to the Viceroy, but no further office relationship is inferred."),
    (103, "his", "viceroy_1613", 0, "Anaphoric possessive in 'subjects of his'; antecedent is the Spanish Viceroy in the sentence."),
    (103, "the sons and heirs", "sons_heirs_1613", 0, "Unidentified plural group in the quoted 1613 report; OCR inserts a stray apostrophe before 'of Antonio del Rosso'; not equated with Andrea and Lorenzo."),
    (103, "Antonio del Rosso", "antonio_1613", 0, "Named father of the sons and heirs; keep distinct from the later Antonio named as Nicola's heir pending S3."),
    (103, "Florentines", "florence", 0, "Gentilic description of the sons and heirs."),
    (103, "living and trading in Naples", "sons_heirs_1613", 0, "Predicate describing the quoted sons and heirs, not a claim about every Del Rosso family member."),
    (103, "Naples", "naples", 0, "City where the quoted sons and heirs were said to live and trade."),
    (103, "Andrea", "andrea", 0, "Younger Andrea del Rosso; distinct from the grandfather at p.212 L99."),
    (103, "Lorenzo", "lorenzo", 0, "Lorenzo del Rosso named alongside the younger Andrea."),
    (103, "themselves", "family", 0, "Jointly refers to the younger Andrea and Lorenzo; the sentence does not identify them as the 1613 sons and heirs."),
    (103, "that city", "naples", 0, "Anaphoric reference to Naples."),
    (105, "Luca Giordano", "giordano", 0, "Artist named as principal agent in Naples for the family."),
    (105, "their", "family", 0, "Possessive reference to the Del Rosso brothers."),
    (105, "Naples", "naples", 0, "City where Giordano was the family's principal artistic agent."),
    (105, "their", "family", 1, "Possessive reference to the Del Rosso brothers in the claim about their relationship with Giordano."),
    (105, "him", "giordano", 0, "Anaphoric reference to Luca Giordano."),
    (105, "their", "family", 2, "Possessive reference to the Del Rosso brothers' pictures."),
    (105, "him", "giordano", 1, "Anaphoric reference to Giordano as the intermediary through whom many pictures were acquired."),
    (105, "he", "giordano", 0, "Anaphoric reference to Giordano visiting Florence in 1679."),
    (105, "Florence", "florence", 0, "City Giordano visited in 1679."),
    (105, "he", "giordano", 1, "Anaphoric reference to Giordano staying at the family's house."),
    (105, "their", "family", 3, "Possessive referent is the Del Rosso brothers in 'their house'."),
    (105, "their house", "family_house_1679", 0, "Unidentified Del Rosso family house where Giordano stayed; possible relation to the Via Chiara house remains open."),
    (105, "they", "family", 0, "Anaphoric reference to the Del Rosso brothers, who already owned some Giordano works."),
    (105, "his", "giordano", 0, "Anaphoric reference to Luca Giordano's works."),
    (105, "they", "family", 1, "Anaphoric reference to the brothers who may have arranged the chapel commission."),
    (105, "him", "giordano", 2, "Anaphoric reference to Giordano as the possible recipient of the chapel commission."),
    (105, "Corsini", "corsini_family", 0, "Family name embedded in the chapel's designation."),
    (105, "Corsini chapel", "corsini_chapel", 0, "Interior chapel; separate from the Carmine church and the paintings."),
    (105, "commission to paint the Corsini chapel", "corsini_commission", 0, "Possible commission; Haskell qualifies the brothers' role with 'may well have been'."),
    (105, "Carmine", "carmine_church", 0, "Church containing the Corsini chapel."),
    (105, "his", "giordano", 1, "Anaphoric reference to Giordano in the claim about the Palazzo Riccardi frescoes."),
    (105, "great frescoes", "riccardi_frescoes", 0, "Existing candidate for Giordano's unidentified Palazzo Riccardi frescoes."),
    (105, "Palazzo Riccardi", "riccardi_palace", 0, "Place named as the site of Giordano's frescoes."),
    (105, "they", "family", 2, "Anaphoric reference to the brothers who owned the bozzetto."),
    (105, "original bozzetto", "corsini_bozzetto", 0, "Preparatory work reportedly owned by the brothers; maker not explicitly stated in this clause."),
    (105, "one of the pendentives", "corsini_pendentive", 0, "Unidentified chapel pendentive image associated with the bozzetto."),
    (105, "the chapel", "corsini_chapel", 0, "Anaphoric reference to the Corsini chapel."),
    (106, "Luca Giordano", "giordano", 0, "Artist whose paintings for the brothers are described."),
    (106, "the brothers", "family", 0, "The Del Rosso brothers."),
    (106, "paintings", "giordano_pictures", 0, "Unidentified Luca Giordano pictures in the brothers' holdings."),
    (106, "erotic works", "giordano_erotic_group", 0, "Unidentified subset described as a large number; examples continue to the next page."),
    (106, "Venus and Amor", "venus_amor_theme", 0, "Pictorial subject named as a theme, not as a claim about the mythological figures themselves."),
]

P211_BACKFILL = add_mentions(P211_BODY_ID, P211_BACKFILL_SPECS, "m-chp8-p211", 78)
P211_NOTES_BACKFILL = add_mentions(P211_NOTES_ID, P211_NOTES_BACKFILL_SPECS, "m-chp8-p211", 79)
P212_MENTIONS = add_mentions(BODY_ID, P212_MENTION_SPECS, "m-chp8-p212", 1)
new_mentions = P211_BACKFILL + P211_NOTES_BACKFILL + P212_MENTIONS

if P211_COLLECTION_MENTION not in existing_mention_ids:
    raise SystemExit("expected p.211 'their collection' mention to reclassify was not found")
collection_mention = next(row for row in mention_rows if row["mention_id"] == P211_COLLECTION_MENTION)
if collection_mention["segment_id"] != P211_BODY_ID or collection_mention["surface_form"] != "their collection" or collection_mention["candidate_id"] != "cand-7489":
    raise SystemExit("p.211 collection mention changed; inspect before reclassifying")
collection_mention_update = dict(collection_mention)
collection_mention_update["candidate_id"] = cid("del_rosso_collection")
collection_mention_update["note"] = "The picture collection is a distinct source object from the Del Rosso family; its type is absent from the current taxonomy. The nested possessive referent is recorded separately."
updated_mentions = [collection_mention_update if row["mention_id"] == P211_COLLECTION_MENTION else dict(row) for row in mention_rows]


def make_statement(tail, start, end, predicate, claim, qualification, quote,
                   subject=None, object_=None, mentioned=(), extra=None):
    row = {
        "statement_id": f"st-chp8-p212-{tail}", "segment_id": BODY_ID,
        "subject_candidate_id": cid(subject) if subject else None,
        "object_candidate_id": cid(object_) if object_ else None,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": start, "source_line_end": end,
            "printed_page": 212, "pdf_physical_page": 10,
            "claim": claim, "speaker": "Haskell", "text_layer": "body",
            "qualification": qualification,
            "mentioned_candidate_ids": list(dict.fromkeys(cid(key) for key in mentioned)),
        },
        "original_quote": quote, "origin": "book", "source_file": BODY_REL,
    }
    if extra:
        row["qualifiers"].update(extra)
    return row


statements = [
    make_statement("grandfather-andrea-built-chapel", 99, 99,
        "grandfather_andrea_had_family_chapel_built_for_his_name_saint",
        "The p.211 clause continues by identifying the Del Rosso brothers' grandfather as Andrea, who had a sumptuous family chapel built in the Theatine church of S. Gaetano and dedicated it to his name-saint.",
        "This statement closes the p.211 phrase 'their grandfather'. It identifies this Andrea as cand-2279, distinct from the younger Andrea and Lorenzo named in the 1613/Naples discussion. The saint remains unnamed.",
        "Andrea had had built in the Theatine church of S. Gaetano a sumptuous family chapel dedicated to his name-saint",
        subject="grandfather_andrea", object_="family_chapel",
        mentioned=["grandfather_andrea","theatines","gaetano_church","family_chapel","andrea_name_saint"],
        extra={"continues_statement_id":P211_OPEN,"footnote_numbers":[1]}),
    make_statement("chapel-decorated-with-vannini-frescoes", 99, 99,
        "chapel_decorated_with_frescoes_by_vannini",
        "Haskell says the chapel was decorated with frescoes by Ottavio Vannini.",
        "The frescoes are not individually identified in this sentence.",
        "This was decorated with frescoes by Ottavio Vannini",
        subject="vannini_frescoes", object_="vannini",
        mentioned=["family_chapel","vannini_frescoes","vannini"],
        extra={"footnote_numbers":[1]}),
    make_statement("vannini-died-a-year-later", 99, 99,
        "vannini_died_a_year_later",
        "Haskell says Vannini died a year later.",
        "The relative time anchor is not made more precise here; no absolute death year is inferred.",
        "who himself died a year later",
        subject="vannini", mentioned=["vannini"], extra={"footnote_numbers":[1]}),
    make_statement("altar-picture-left-for-pupil-completion", 99, 99,
        "vannini_left_altar_picture_for_pupil_to_complete",
        "Haskell says Vannini left the chapel altar picture to be completed by a pupil.",
        "The pupil is unnamed, and the wording does not establish that the picture was in fact completed.",
        "leaving the altar picture to be completed by a pupil",
        subject="vannini", object_="altar_picture",
        mentioned=["vannini","altar_picture","pupil"], extra={"footnote_numbers":[1]}),
    make_statement("four-scenes-made-for-house-and-considered-finest", 100, 101,
        "vannini_produced_four_named_old_testament_scenes_for_house_and_they_were_considered_his_finest",
        "Haskell says Vannini produced four large Old Testament scenes for the Del Rosso house—The Sacrifice of Isaac, The Fall of Manna, Moses striking the Rock and Susanna and the Elders—and that these were considered his finest works.",
        "The four titles are separate work candidates within one group. 'Considered his finest' is Haskell's report, not an external assessment verified here; footnote 2 supplies cited sources to process later.",
        "the four large scenes from the Old Testament—\nThe Sacrifice of Isaac, The Fall of Manna, Moses striking the Rock and Susanna and the Elders—which he produced for the house were considered his finest works",
        subject="vannini", object_="four_vannini_scenes",
        mentioned=["vannini","four_vannini_scenes","sacrifice_isaac","fall_manna","moses_rock","susanna_elders","family_house_1679"],
        extra={"footnote_numbers":[2]}),
    make_statement("other-vannini-pictures-owned-by-family", 101, 101,
        "del_rosso_family_owned_other_vannini_pictures_mainly_saints",
        "Haskell says the Del Rosso family owned many other pictures by Vannini, mainly of saints.",
        "The other pictures are not individually identified and are distinct from the four named Old Testament scenes.",
        "the del Rosso also owned a large number of other pictures by him, mainly of saints",
        subject="family", object_="other_vannini_pictures",
        mentioned=["family","vannini","other_vannini_pictures"]),
    make_statement("vannini-style-and-florentine-disegno-assessment", 101, 101,
        "haskell_characterizes_vannini_as_academic_florentine_disegno_artist_in_provincial_backwater",
        "Haskell characterizes Vannini as methodical, correct and academic in the Florentine disegno tradition, and describes one section of the city's painting as a provincial backwater during the first half of the seventeenth century.",
        "This is Haskell's evaluative language and is limited in the sentence to one section of Florentine painting; it is not a general fact about all Florentine art.",
        "He was a methodical, correct, academic artist in the true tradition of Florentine ‘disegno’— characteristic in every way of the provincial backwater into which one section of that city’s painting had sunk during the first half of the seventeenth century",
        subject="vannini", object_="disegno_tradition",
        mentioned=["vannini","disegno_tradition","florence"]),
    make_statement("carlo-dolci-painted-for-del-rosso-family", 102, 102,
        "carlo_dolci_also_painted_for_del_rosso_family",
        "Haskell says Carlo Dolci also painted for the Del Rosso family.",
        "The works and number are not specified in this body sentence; footnote 3 supplies further detail and remains to be migrated with the later notes segment.",
        "Carlo Dolci also painted for the del Rosso family",
        subject="dolci", object_="family",
        mentioned=["dolci","family"], extra={"footnote_numbers":[3]}),
    make_statement("over-hundred-neapolitan-pictures-introduced", 102, 102,
        "new_del_rosso_generation_introduced_over_hundred_neapolitan_pictures",
        "Haskell says the new Del Rosso generation introduced over a hundred Neapolitan pictures into the household.",
        "The source gives a lower-bound count and group-level regional description, not titles, makers or creation places for every picture.",
        "the new generation introduced over a hundred Neapolitan pictures",
        subject="family", object_="neapolitan_pictures",
        mentioned=["family","neapolitan_pictures","naples"]),
    make_statement("some-pictures-came-from-roomer-collection", 102, 102,
        "some_neapolitan_pictures_acquired_from_dispersed_roomer_collection",
        "Haskell says some of the Neapolitan pictures were acquired from the Roomer collection after its dispersal in 1674.",
        "'Some' is not assigned a number; no claim is made that the whole group came from Roomer. The collection itself has no current taxonomy type.",
        "(some acquired from the Roomer collection after its dispersal in 1674)",
        subject="roomer_subset", object_="roomer_collection",
        mentioned=["neapolitan_pictures","roomer_subset","roomer_collection","roomer_dispersal","roomer_person"]),
    make_statement("more-than-sixty-by-luca-giordano", 102, 102,
        "more_than_sixty_neapolitan_pictures_by_luca_giordano",
        "Haskell says more than sixty of the Neapolitan pictures were by Luca Giordano.",
        "This is a lower-bound count for the subset; it does not identify the individual paintings.",
        "of which more than sixty were by Luca Giordano",
        subject="giordano_pictures", object_="giordano",
        mentioned=["neapolitan_pictures","giordano_pictures","giordano"]),
    make_statement("business-connections-probably-outweighed-taste", 102, 102,
        "business_connections_probably_more_important_than_aesthetic_taste_in_collection_shift",
        "Haskell says aesthetic taste alone is unlikely to explain the departure from traditional collecting patterns and that business connections were probably more important.",
        "Both clauses are qualified by 'unlikely' and 'probably'; this remains Haskell's interpretation, not a proven motive for every acquisition.",
        "Aesthetic taste alone is unlikely to have caused such a spectacular departure from traditional patterns; business connections were probably of greater importance",
        subject="del_rosso_collection", mentioned=["del_rosso_collection","family"]),
    make_statement("links-with-naples-in-family-history", 102, 102,
        "various_links_with_naples_appear_in_del_rosso_family_history",
        "Haskell says various links with Naples appear from time to time in the family history.",
        "The sentence introduces examples; it does not describe every family member as a Naples resident.",
        "various links with Naples turn up from time to time in the family history",
        subject="family", object_="naples", mentioned=["family","naples"]),
    make_statement("1613-grand-duke-letter-about-antonio-sons", 102, 103,
        "grand_duke_wrote_viceroy_in_1613_about_antonio_del_rosso_sons_and_heirs",
        "Haskell reports that in 1613 the Grand Duke of Tuscany wrote to the Spanish Viceroy about some subjects, quoting the sons and heirs of Antonio del Rosso as Florentines living and trading in Naples.",
        "The addressee is named only by office. The group in the quotation is not equated with the younger Andrea and Lorenzo; the footnote 4 document locator is in the later notes segment and will be linked then.",
        "In 1613, for instance, we find the Grand Duke of Tuscany writing to the Spanish Viceroy about some subjects of his, ‘the sons and heirs ' of Antonio del Rosso, Florentines, but living and trading in Naples’",
        subject="grand_duke_1613", object_="letter_1613",
        mentioned=["grand_duke_1613","tuscany","viceroy_1613","sons_heirs_1613","antonio_1613","florence","naples"],
        extra={"footnote_numbers":[4],"pronoun_resolution":"'his' in 'subjects of his' is treated as referring to the immediately preceding Spanish Viceroy; the office-holder remains unidentified.",
               "ocr_corrections":[{"source_line":103,"ocr":"heirs ' of","print":"heirs of","basis":"CHP-8.pdf physical page 10; the quotation continues across the source line."}]}),
    make_statement("andrea-and-lorenzo-may-have-started-careers-in-naples", 103, 103,
        "andrea_and_lorenzo_may_have_started_careers_in_naples",
        "Haskell says it is perfectly possible that Andrea and Lorenzo themselves may have started their careers in Naples.",
        "The double qualification is preserved; the sentence does not identify them as the sons and heirs named in the 1613 quotation.",
        "it is perfectly possible that Andrea and Lorenzo themselves may have started their careers in that city",
        subject="andrea", object_="naples", mentioned=["andrea","lorenzo","family","naples"]),
    make_statement("luca-giordano-principal-agent-in-naples", 105, 105,
        "luca_giordano_principal_artistic_agent_for_del_rosso_family_in_naples",
        "Haskell calls Luca Giordano the family's principal artistic agent in Naples.",
        "The agent role and city are source-reported; no formal relation edge is created in S2.",
        "Luca Giordano was their principal artistic agent in Naples",
        subject="giordano", object_="family",
        mentioned=["giordano","family","naples"]),
    make_statement("luca-giordano-family-relationship-close", 105, 105,
        "relationship_between_giordano_and_del_rosso_family_particularly_close",
        "Haskell says the Del Rosso family's relationship with Giordano was particularly close.",
        "This is Haskell's characterization; it does not specify one exclusive role or a precise start date.",
        "their relationship with him was particularly close",
        subject="family", object_="giordano", mentioned=["family","giordano"]),
    make_statement("many-family-pictures-acquired-through-giordano", 105, 105,
        "many_del_rosso_pictures_acquired_through_giordano",
        "Haskell says many of the family's pictures were acquired through Giordano.",
        "The number, transaction dates and individual pictures are not specified; the wording does not make Giordano the owner or final buyer.",
        "Many of their pictures were acquired through him",
        subject="del_rosso_collection", object_="giordano_pictures",
        mentioned=["del_rosso_collection","family","giordano","giordano_pictures"]),
    make_statement("giordano-visited-florence-and-stayed-at-family-house-1679", 105, 105,
        "giordano_came_to_florence_and_stayed_at_del_rosso_house_in_1679",
        "Haskell says Giordano came to Florence in 1679 and stayed at the family's house.",
        "The house is not named here; it may be the Via Chiara house at p.210 but the passage does not expressly equate them.",
        "when he came to Florence in 1679 he stayed at their house",
        subject="giordano_visit_1679", object_="family_house_1679",
        mentioned=["giordano","florence","family","family_house_1679"],
        extra={"footnote_numbers":[5]}),
    make_statement("family-already-owned-several-giordano-works", 105, 105,
        "del_rosso_family_owned_a_number_of_giordano_works_before_1679",
        "Haskell says the family already owned a number of Giordano's works before his 1679 visit.",
        "The number is not specified and no individual work is identified.",
        "as they already owned a number of his works before then",
        subject="family", object_="giordano_pictures",
        mentioned=["family","giordano","giordano_pictures"], extra={"footnote_numbers":[5]}),
    make_statement("family-may-have-arranged-corsini-chapel-commission", 105, 105,
        "del_rosso_brothers_may_have_arranged_giordano_corsini_chapel_commission",
        "Haskell says it may well have been the brothers who arranged for Giordano to receive the commission to paint the Corsini chapel in the Carmine.",
        "'May well have been' marks the proposed arranging role as uncertain; preserve the chapel, church and commission as distinct candidates.",
        "it may well have been they who arranged for him to be given.the commission to paint the Corsini chapel in the Carmine",
        subject="family", object_="corsini_commission",
        mentioned=["family","giordano","corsini_commission","corsini_chapel","carmine_church"],
        extra={"footnote_numbers":[5],"ocr_corrections":[{"source_line":105,"ocr":"given.the","print":"given the","basis":"CHP-8.pdf physical page 10."}]}),
    make_statement("corsini-commission-in-turn-led-to-palazzo-riccardi-frescoes", 105, 105,
        "corsini_chapel_commission_said_to_lead_to_giordano_palazzo_riccardi_frescoes",
        "Haskell says the Corsini commission in turn led to Giordano's great frescoes in Palazzo Riccardi.",
        "The causal sequence is Haskell's source statement; the frescoes remain a group with no individual subjects specified here.",
        "which in turn led to his great frescoes in the Palazzo Riccardi",
        subject="corsini_commission", object_="riccardi_frescoes",
        mentioned=["corsini_commission","giordano","riccardi_frescoes","riccardi_palace"]),
    make_statement("family-owned-original-bozzetto-for-chapel-pendentive", 105, 105,
        "del_rosso_brothers_owned_original_bozzetto_for_one_corsini_chapel_pendentive",
        "Haskell says the brothers certainly owned the original bozzetto for one of the chapel's pendentives.",
        "The maker and the finished pendentive image are not explicitly identified by this sentence; do not infer the bozzetto's authorship from adjacent discussion alone.",
        "Certainly they owned the original bozzetto for one of the pendentives in the chapel",
        subject="family", object_="corsini_bozzetto",
        mentioned=["family","corsini_bozzetto","corsini_pendentive","corsini_chapel"]),
    make_statement("giordano-pictures-included-many-erotic-works-open", 106, 106,
        "giordano_paintings_for_brothers_included_many_erotic_works_fragment_continues",
        "Haskell says Giordano's paintings for the brothers were varied and included a large number of erotic works; the sentence continues with an example on p.213.",
        "This is an open cross-page statement, ending at 'one'; do not complete the example from whole-chapter OCR without checking the next S0 segment and page image.",
        "Luca Giordano’s paintings for the brothers were of various kinds and included a large number of erotic works—many versions of the theme of Venus and Amor, one",
        subject="giordano", object_="giordano_erotic_group",
        mentioned=["giordano","family","giordano_pictures","giordano_erotic_group","venus_amor_theme"],
        extra={"continuation_status":"open","continuation_expected_segment_id":NEXT_ID,
               "continuation_note":"p.212 L106 ends with 'one'; p.213 S0 begins the continuation. Read and visually check the continuation before closing."}),
]

if len({row["candidate_id"] for row in new_candidates}) != len(new_candidates) or candidate_ids & {row["candidate_id"] for row in new_candidates}:
    raise SystemExit("planned candidate ID collision")
if len({row["mention_id"] for row in new_mentions}) != len(new_mentions) or existing_mention_ids & {row["mention_id"] for row in new_mentions}:
    raise SystemExit("planned mention ID collision")
if len({row["statement_id"] for row in statements}) != len(statements) or existing_statement_ids & {row["statement_id"] for row in statements}:
    raise SystemExit("planned statement ID collision")


def update_p211_collection_mentions(row):
    row = dict(row)
    if row["mention_id"] == P211_COLLECTION_MENTION:
        row["candidate_id"] = cid("del_rosso_collection")
        row["note"] = collection_mention_update["note"]
    return row


closed_previous = False
updated_statements = []
collection_statement_updates = {
    "st-chp8-p211-del-rosso-inventory-reports-glass-and-durer-pairs": "subject",
    "st-chp8-p211-principal-sources-for-del-rosso-collection": "subject",
}
for original in statement_rows:
    row = dict(original)
    qualifiers = dict(row.get("qualifiers", {}))
    if row["statement_id"] == P211_OPEN:
        if qualifiers.get("continuation_status") != "open" or qualifiers.get("continuation_expected_segment_id") != BODY_ID:
            raise SystemExit("p.211 grandfather continuation changed; inspect before closing")
        qualifiers.update({
            "continuation_status": "closed",
            "continuation_source_segment_id": BODY_ID,
            "continuation_source_line": 99,
            "continuation_statement_id": "st-chp8-p212-grandfather-andrea-built-chapel",
            "continuation_resolution": "p.212 L99 supplies 'Andrea had had built', identifying the grandfather and closing the p.211 clause; the sentence crosses the page break despite the paragraph indentation.",
        })
        qualifiers.pop("continuation_expected_segment_id", None)
        qualifiers.pop("continuation_note", None)
        closed_previous = True
    if row["statement_id"] in collection_statement_updates:
        if row.get("subject_candidate_id") != "cand-7489":
            raise SystemExit(f"p.211 collection statement subject changed: {row['statement_id']}")
        row["subject_candidate_id"] = cid("del_rosso_collection")
        ids = list(qualifiers.get("mentioned_candidate_ids", []))
        if "cand-7489" not in ids:
            ids.append("cand-7489")
        if cid("del_rosso_collection") not in ids:
            ids.append(cid("del_rosso_collection"))
        qualifiers["mentioned_candidate_ids"] = ids
    if row["statement_id"] == "st-chp8-p211-collection-records-indicate-brothers-travelled":
        ids = list(qualifiers.get("mentioned_candidate_ids", []))
        if cid("del_rosso_collection") not in ids:
            ids.append(cid("del_rosso_collection"))
        qualifiers["mentioned_candidate_ids"] = ids
    if qualifiers:
        row["qualifiers"] = qualifiers
    updated_statements.append(row)
if not closed_previous:
    raise SystemExit("expected p.211 open grandfather statement not found")
if set(collection_statement_updates) - {r["statement_id"] for r in statement_rows}:
    raise SystemExit("expected p.211 collection statement for correction not found")

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
for row in new_mentions:
    if row["candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"missing candidate FK for mention {row['mention_id']}")
all_mentions_by_id = {row["mention_id"]: row for row in mention_rows}
all_mentions_by_id.update({row["mention_id"]: row for row in new_mentions})
all_mentions_by_id[P211_COLLECTION_MENTION] = collection_mention_update

for row in statements:
    seg = row["segment_id"]
    _, all_lines, seg_start, _ = source_text_and_lines(seg)
    q = row["qualifiers"]
    start, end = q["source_line_start"], q["source_line_end"]
    if start < seg_start or end < start:
        raise SystemExit(f"statement source range is invalid: {row['statement_id']}")
    cited = "\n".join(all_lines[start - 1:end])
    if " ".join(row["original_quote"].split()) not in " ".join(cited.split()):
        raise SystemExit(f"quote not reproducible: {row['statement_id']}\n{row['original_quote']}")
    referenced = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        referenced.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        referenced.add(row["object_candidate_id"])
    if not referenced <= all_candidate_ids:
        raise SystemExit(f"missing candidate FK: {row['statement_id']}: {referenced - all_candidate_ids}")

coverage_updates = {
    P211_BODY_ID: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L85-96",
        "note": "P.211 body and its footnotes are complete. The p.211 clause ending 'their grandfather' is closed by p.212 L99, whose 'Andrea had had built' identifies the grandfather. The p.211 collection mentions are linked to a separate untyped collection candidate; notes 1-3 remain represented by the supplemental visual-transcription segment.",
    },
    BODY_ID: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L99-106",
        "note": "P.212 body read against CHP-8.pdf physical p.10. L99 closes p.211's grandfather clause; the older Andrea (cand-2279) is distinct from the younger Andrea/Lorenzo. PDF confirms S0's 'given.the' should be read 'given the'; S0 remains unchanged. The sentence at L106 ends 'one' and continues on p.213; printed notes 1-5 are in the later canonical footnote segment and remain to be migrated.",
    },
}
updated_coverage = []
found_coverage = set()
for original in coverage_rows:
    row = dict(original)
    if row["segment_id"] in coverage_updates:
        row.update(coverage_updates[row["segment_id"]])
        found_coverage.add(row["segment_id"])
    updated_coverage.append(row)
if found_coverage != set(coverage_updates):
    raise SystemExit(f"coverage update targets not found: {set(coverage_updates) - found_coverage}")

preview = {
    "mode": "dry-run", "source_segments": [P211_BODY_ID, P211_NOTES_ID, BODY_ID],
    "new_candidates": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "untyped_candidates": [row["candidate_id"] for row in new_candidates if not row["suggested_type"]],
    "new_mentions": len(new_mentions),
    "backfilled_mentions": [row["mention_id"] for row in P211_BACKFILL + P211_NOTES_BACKFILL],
    "reclassified_existing_mention": P211_COLLECTION_MENTION,
    "new_statements": len(statements),
    "closed_previous_statement": P211_OPEN,
    "closed_collection_statements": sorted(collection_statement_updates),
    "open_continuation": {"statement_id": "st-chp8-p212-giordano-pictures-included-many-erotic-works-open", "next_segment_id": NEXT_ID},
    "coverage": coverage_updates,
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
updated_mentions = [update_p211_collection_mentions(row) for row in updated_mentions]
updated_mentions.extend(new_mentions)
updated_statements.extend(statements)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, updated_mentions)
write_jsonl_atomic(statement_path, updated_statements)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
