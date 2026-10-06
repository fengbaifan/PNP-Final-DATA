"""Controlled S2 migration for chapter 8 printed p.213.

Default invocation is read-only. It validates the canonical S0 segment,
cross-page continuation from p.212, mentions, quotations, candidate keys and
coverage before --apply writes the four S2 tables.
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
BODY_ID = "chp-8:08_CHP-8_sec_i:l108-118"
PREVIOUS_ID = "chp-8:08_CHP-8_sec_i:l98-106"
NEXT_ID = "chp-8:08_CHP-8_sec_i:l120-124"
PREVIOUS_STATEMENT = "st-chp8-p212-giordano-pictures-included-many-erotic-works-open"
CURRENT_MAX_CANDIDATE = 7552
BACKUP_SUFFIX = ".bak-s2-chp8-p213-20260930"


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

segment = segments.get(BODY_ID)
if not segment or segment["source_file"] != BODY_REL or (int(segment["line_start"]), int(segment["line_end"])) != (108, 118):
    raise SystemExit(f"segment metadata changed; review before migration: {BODY_ID}")
source_path = ROOT / BODY_REL
source_bytes = source_path.read_bytes()
if hashlib.sha256(source_bytes).hexdigest() != segment["asset_sha256"]:
    raise SystemExit(f"source asset fingerprint changed: {BODY_REL}")
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[107:118]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit(f"source line-slice hash changed: {BODY_ID}")
if (coverage_by_id.get(BODY_ID, {}).get("disposition"), coverage_by_id.get(BODY_ID, {}).get("migration_status")) != ("queued", "pending"):
    raise SystemExit(f"unexpected coverage state for {BODY_ID}")

candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != CURRENT_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {CURRENT_MAX_CANDIDATE}, found {current_max}")

candidate_specs = [
    ("ignudo_picture", "Unidentified Luca Giordano Venus and Amor painting described with a distant ignudo", "work",
     "One picture in the Del Rosso collection, described in Haskell's continuing sentence; neither its title nor present location is given.", 109),
    ("deianira_nessus_pictures", "Unidentified Giordano picture or set with Deianira and Nessus", "work",
     "A fable subject in the Del Rosso collection; the text gives no item-level title or number.", 109),
    ("galatea_tritons_pictures", "Unidentified Giordano picture or set with Galatea and Tritons", "work",
     "A fable subject in the Del Rosso collection; the text gives no item-level title or number.", 109),
    ("rape_proserpina_picture", "Unidentified Giordano picture of The Rape of Proserpina", "work",
     "A named fable subject in the Del Rosso collection; do not identify it with other paintings of this subject.", 109),
    ("religious_paintings", "Unidentified religious paintings by Luca Giordano with Old and New Testament scenes", "work",
     "Group of religious paintings reported in the Del Rosso collection; no individual titles are given.", 109),
    ("devotional_pictures", "Unidentified devotional pictures by Luca Giordano in the Del Rosso collection", "work",
     "A group distinct in the sentence from the religious paintings described with Old and New Testament scenes; no titles are given.", 109),
    ("altarpiece_modelli", "Luca Giordano modelli for altarpieces and other works owned by the Del Rosso brothers", "work",
     "Preparatory models in the collection; no individual altarpiece or modello is identified.", 109),
    ("sketchy_brushwork", "Sketchy, unfinished and lively brushwork valued by the Del Rosso brothers", "term",
     "Aesthetic qualities characterized by Haskell as a new appreciation; preserve as a source-specific art concept.", 110),
    ("neapolitan_school", "Neapolitan school as applied to François Nomé by Haskell", "term",
     "Source-specific school label used for Nomé; it does not assert that he was born in Naples or studied in a formal institution there.", 110),
    ("colore_value", "The value of colore in the Del Rosso collection's shift from Florentine disegno", "term",
     "Artistic value named in Haskell's contrast; do not treat as a formal school or a later synthesis node.", 114),
    ("international_taste", "Advanced international taste at the end of the seventeenth century", "term",
     "Haskell's characterization of the collection's taste; retain its source-specific evaluative scope.", 115),
    ("venetian_revival", "The great Venetian revival near the end of the seventeenth century", "term",
     "Art-historical development named as an approaching context by Haskell; no causal relation is asserted here.", 115),
    ("giordano_joint_decoration", "Giordano's decorative works for the Corsini chapel and Palazzo Riccardi", "work",
     "Group reference to the two decorations discussed together by Haskell; keep the interior Corsini chapel and Palazzo Riccardi building distinct from the artworks.", 115),
    ("nome_ruin_pictures", "Eleven mannered, visionary ruin pictures by François Nomé in the Del Rosso collection", "work",
     "Group of eleven pictures described by Haskell; individual inventory descriptions remain separately identifiable candidates where available.", 111),
    ("nome_palazzi", "Unidentified François Nomé picture described as antichità di palazzi", "work",
     "Inventory description quoted by Haskell; preserve the Italian wording and do not normalize it to a known title.", 111),
    ("nome_gran_temple", "Unidentified François Nomé picture described as a gran Tempio antico", "work",
     "Inventory description quoted by Haskell; preserve the Italian wording and do not identify the ancient temple.", 111),
    ("nome_venice_view", "François Nomé's imaginary view of Venice in the Del Rosso collection", "work",
     "One of the ruin pictures described by Haskell; no title or present location is supplied.", 111),
    ("callot_printing_plate", "Original plate for Jacques Callot's La Fiera dell'Impruneta (type unresolved)", "",
     "Haskell says the brothers possessed what was apparently the original plate; keep the plate distinct from Callot's print because the project has no printing-matrix type.", 112),
    ("mehus_pictures", "Three unidentified pictures by Livio Mehus owned by the Del Rosso brothers in 1677", "work",
     "Group reported as owned in 1677 and absent from the collection twelve years later; individual titles are not given.", 116),
    ("durazzo_local_collection", "Unidentified Durazzo family collection of local Genoese art (type unresolved)", "",
     "Haskell describes a leading patrician family building an extensive collection of local art over centuries; the present taxonomy has no collection type.", 118),
    ("durazzo_giordano_pictures", "Unidentified Luca Giordano pictures acquired by Girolamo Durazzo for the Durazzo family", "work",
     "The p.213 sentence says Durazzo turned to Bologna for many pictures and continues on p.214 to Naples; keep the group open until p.214 is processed.", 118),
]

candidate_by_key = {}
new_candidates = []
next_number = current_max + 1
for key, name, typ, detail, line in candidate_specs:
    cid = f"cand-{next_number:04d}"
    next_number += 1
    candidate_by_key[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": typ, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_ID}#L{line}",
    })

EXISTING = {
    "family": "cand-7489", "del_rosso_collection": "cand-7520",
    "roomer_collection": "cand-7407", "giordano": "cand-1172",
    "giordano_pictures": "cand-7537", "erotic_group": "cand-7551",
    "venus_amor": "cand-7552", "disegno": "cand-7533",
    "corsini_commission": "cand-7547", "corsini_chapel": "cand-7546",
    "carmine": "cand-7545", "riccardi_palace": "cand-2145",
    "riccardi_frescoes": "cand-7234", "nom": "cand-1749",
    "babylon": "cand-1750", "temple_solomon": "cand-1751",
    "inventory": "cand-7500", "mannerist": "cand-1516",
    "callot_print": "cand-0483", "ferdinand": "cand-1609",
    "mehus": "cand-1632", "durazzo": "cand-0953",
    "durazzo_family": "cand-7360", "naples": "cand-3534",
    "rome": "cand-4490", "florence": "cand-1041",
    "central_italy": "cand-7392", "neapolitan_painting": "cand-1729",
    "italy": "cand-3461", "genoa": "cand-1131",
    "bologna": "cand-0381", "venice": "cand-2719",
    "mythological_fables": "cand-6335",
}


def cid(key: str) -> str:
    return candidate_by_key[key] if key in candidate_by_key else EXISTING[key]


mention_specs = [
    (109, "which", "ignudo_picture", 0, "Relative pronoun continues p.212's 'one'; the referent is this one unidentified picture."),
    (109, "ignudo in atto assai lussurioso che si strugge per lui", "ignudo_picture", 0, "Quoted Italian description of a figure in the unidentified picture; the pronoun's referent is not independently resolved."),
    (109, "sets of fables", "mythological_fables", 0, "Plural group of mythological picture subjects in the continuing Giordano passage."),
    (109, "Deianira and Nessus", "deianira_nessus_pictures", 0, "Named fable subject in the Del Rosso collection."),
    (109, "Galatea and Tritons", "galatea_tritons_pictures", 0, "Named fable subject in the Del Rosso collection."),
    (109, "The Rape of Proserpina", "rape_proserpina_picture", 0, "Named fable subject in the Del Rosso collection; do not merge with other works of the same subject."),
    (109, "religious paintings", "religious_paintings", 0, "Group of Giordano paintings identified by subject matter."),
    (109, "him", "giordano", 0, "Anaphoric reference to Luca Giordano."),
    (109, "scenes from the Old and New Testaments", "religious_paintings", 0, "Description of the religious-painting group; no individual scenes are named."),
    (109, "more purely devotional pictures", "devotional_pictures", 0, "Separate devotional group in the wording; no titles are given."),
    (109, "Giordano’s modelli", "altarpiece_modelli", 0, "Preparatory models by Luca Giordano; the original Italian plural is retained."),
    (109, "altarpieces", "altarpiece_modelli", 0, "Works for which Giordano's modelli were made; individual altarpieces are not named."),
    (109, "other works", "altarpiece_modelli", 0, "Additional works for which Giordano's modelli were made; no titles are specified."),
    (110, "This new appreciation", "sketchy_brushwork", 0, "Anaphoric reference to the aesthetic preference described as sketchy, unfinished and lively brushwork."),
    (110, "the sketchy", "sketchy_brushwork", 0, "One of the aesthetic qualities named by Haskell."),
    (110, "the unfinished", "sketchy_brushwork", 0, "One of the aesthetic qualities named by Haskell."),
    (110, "lively brush stroke", "sketchy_brushwork", 0, "Aesthetic quality named by Haskell."),
    (110, "eighteenth-century art", "sketchy_brushwork", 0, "Period and field in which Haskell says this quality would become important."),
    (110, "Grand Prince Ferdinand de’ Medici", "ferdinand", 0, "Ferdinand is named as another Florentine devotee of this aesthetic."),
    (110, "Florentine", "florence", 0, "Gentilic description of Ferdinand's artistic context."),
    (110, "their collecting", "family", 0, "The Del Rosso brothers' collecting activity; the sentence presents its cause as possible."),
    (110, "through the intervention of Luca Giordano", "giordano", 0, "Possible intermediary role; do not convert this wording to a settled formal relation."),
    (110, "the work of another artist", "nom", 0, "Introduces François Nomé, identified in the following sentence."),
    (110, "Neapolitan school", "neapolitan_school", 0, "School designation used for Nomé; no institutional entity is implied."),
    (111, "Frenchman François Nome", "nom", 0, "Artist identified as François Nomé; S0 omits the accent in Nomé, corrected in the page image."),
    (111, "Monsù Desiderio", "nom", 0, "Alias introduced by 'generally known as'; mapped to the same indexed candidate as François Nomé."),
    (111, "their inventory", "inventory", 0, "Andrea del Rosso's 1689 inventory, already registered from p.211 notes."),
    (111, "Lorenese", "nom", 0, "Inventory designation attached to Nomé; it is retained as the source's label, not expanded into a separate identity claim."),
    (111, "eleven of his mannered, visionary ruin pictures", "nome_ruin_pictures", 0, "Group quantity and characterization reported by Haskell; individual pictures follow."),
    (111, "fatta di colpi", "nome_ruin_pictures", 0, "Quoted inventory description of the group; no broader stylistic definition is inferred."),
    (111, "Babylon", "babylon", 0, "Specific Del Rosso inventory sub-entry already present in the index-derived candidate list."),
    (111, "antichità di palazzi", "nome_palazzi", 0, "Italian inventory description; preserved without converting it to a known title."),
    (111, "gran Tempio antico", "nome_gran_temple", 0, "Italian inventory description; the building is not identified."),
    (111, "Temple of Solomon", "temple_solomon", 0, "Specific Del Rosso inventory sub-entry already present in the index-derived candidate list."),
    (111, "imaginary view of Venice", "nome_venice_view", 0, "Unidentified imaginative view described as one of Nomé's ruin pictures."),
    (111, "Venice", "venice", 0, "City represented in the imaginary view."),
    (111, "Mannerist", "mannerist", 0, "Style label used by Haskell; not a claim about all works in the collection."),
    (111, "their possession", "family", 0, "The Del Rosso brothers' possession of an original plate."),
    (111, "the original plate", "callot_printing_plate", 0, "Physical printing matrix reported as apparently original; distinct from the printed work."),
    (112, "Callot’s print", "callot_print", 0, "Print by Jacques Callot, distinct from the original plate reportedly held by the brothers."),
    (112, "La Fiera dellTmpruneta", "callot_print", 0, "Title as present in S0; the page image reads La Fiera dell'Impruneta."),
    (113, "the del Rosso collection", "del_rosso_collection", 0, "The brothers' picture collection, kept distinct from the family entity."),
    (114, "Naples", "naples", 0, "City emphasized in Haskell's description of the collection."),
    (114, "total neglect of Rome", "rome", 0, "City omitted from the collection according to Haskell; no claim about all Roman art is implied."),
    (114, "its", "del_rosso_collection", 0, "Possessive reference to the Del Rosso collection, whose motives Haskell leaves unresolved."),
    (114, "their sudden conversion", "family", 0, "The Del Rosso brothers' collecting shift, characterized by Haskell."),
    (114, "Florentine tradition of ‘disegno’", "disegno", 0, "Artistic tradition already represented by a p.212 candidate."),
    (114, "disegno", "disegno", 0, "Italian art-theoretical term used in the comparison."),
    (115, "‘colore’", "colore_value", 0, "Value named as the other side of Haskell's disegno/colore contrast."),
    (115, "advanced international taste", "international_taste", 0, "Haskell's evaluation of late-seventeenth-century artistic taste."),
    (115, "seventeenth century", "international_taste", 0, "Chronological qualifier for Haskell's taste characterization."),
    (115, "great Venetian revival", "venetian_revival", 0, "Art-historical development named by Haskell as approaching context."),
    (115, "the collection", "del_rosso_collection", 0, "The Del Rosso picture collection."),
    (115, "cultural life of Florence", "florence", 0, "Cultural context whose relation to the collection Haskell says is difficult to assess."),
    (115, "del Rosso", "family", 0, "The Del Rosso brothers referred to in the conditional account of Giordano's commissions."),
    (115, "Luca Giordano", "giordano", 0, "Artist in Haskell's conditional commission account."),
    (115, "commissioned to decorate the Corsini chapel in the Carmine", "corsini_commission", 0, "Haskell frames the Del Rosso role conditionally; the commission candidate remains possible, not established."),
    (115, "Corsini chapel", "corsini_chapel", 0, "Interior chapel already represented by a p.212 candidate."),
    (115, "Carmine", "carmine", 0, "Church containing the Corsini chapel."),
    (115, "the ceiling of the Palazzo Riccardi", "riccardi_frescoes", 0, "Interior work/location reference associated with the already registered Giordano fresco group; it is not a separate building."),
    (115, "Palazzo Riccardi", "riccardi_palace", 0, "Building named as the location of Giordano's ceiling decoration."),
    (115, "the brothers", "family", 0, "The Del Rosso brothers, for whom Haskell says influence could be claimed if the commissions came through them."),
    (115, "These works", "giordano_joint_decoration", 0, "Collective reference to Giordano's Corsini and Riccardi decorations just named."),
    (115, "Florentine painting", "florence", 0, "Local painting context said to have been little affected by the works."),
    (115, "central Italy", "central_italy", 0, "Region in which Haskell says the works were crucially important."),
    (115, "del Rosso brothers’ taste", "family", 0, "Collective collecting taste characterized as puzzling by Haskell."),
    (115, "Florence", "florence", 0, "City in which Haskell says only one artist had the freshness and vitality in question."),
    (115, "the friends and patrons of Luca", "family", 0, "Phrase begins the reference to the Del Rosso brothers in this local context; the artist's surname completes on the next line."),
    (116, "Giordano", "giordano", 0, "Completes Luca Giordano's name across the line break."),
    (116, "Livio Mehus", "mehus", 0, "Artist identified by name."),
    (116, "they", "family", 0, "Anaphoric reference to the Del Rosso brothers."),
    (116, "three pictures", "mehus_pictures", 0, "Numbered group of Mehus pictures reportedly owned in 1677."),
    (116, "him", "mehus", 0, "Anaphoric reference to Livio Mehus."),
    (116, "these", "mehus_pictures", 0, "The three Mehus pictures, reported to have disappeared from the collection."),
    (116, "their special patronage of Luca Giordano", "family", 0, "The brothers' patronage; Haskell frames a possible financial explanation rather than a proven motive."),
    (117, "Neapolitan painting", "neapolitan_painting", 0, "Artistic field whose diffusion Haskell says had become widespread across Italy."),
    (117, "all over Italy", "italy", 0, "Geographical scope of Haskell's diffusion claim."),
    (117, "Genoa", "genoa", 0, "City in which the next example is set."),
    (117, "Marchese Girolamo Durazzo", "durazzo", 0, "Named Genoese patron; use the existing index-derived person candidate."),
    (117, "a member", "durazzo_family", 0, "Links Girolamo Durazzo to his patrician family without asserting a formal organizational relation."),
    (118, "one of the leading patrician families", "durazzo_family", 0, "Durazzo family identified as a leading Genoese patrician family."),
    (118, "an extensive collection of local art", "durazzo_local_collection", 0, "Collection built up by the family over centuries; its type remains unresolved."),
    (118, "local art", "durazzo_local_collection", 0, "Content description of the family collection."),
    (118, "Bologna", "bologna", 0, "City from which Durazzo obtained many pictures; the sentence continues on p.214."),
    (118, "many of his pictures", "durazzo_giordano_pictures", 0, "The quantity and phrase remain open until p.214 names the works and the Naples connection."),
]


def add_mentions():
    line_offsets = {}
    offset = 0
    for number in range(108, 119):
        line_offsets[number] = offset
        offset += len(source_lines[number - 1]) + 1
    result = []
    for number, surface, key, occurrence, note in mention_specs:
        spans = [m.span() for m in re.finditer(r"(?<!\w)" + re.escape(surface) + r"(?=$|[^\w]|\d)", source_lines[number - 1])]
        if occurrence >= len(spans):
            raise SystemExit(f"mention not found: {BODY_ID} L{number} {surface!r} occurrence {occurrence}; found {len(spans)}")
        start_local, end_local = spans[occurrence]
        start_char = line_offsets[number] + start_local
        end_char = line_offsets[number] + end_local
        if segment_text[start_char:end_char] != surface:
            raise SystemExit(f"mention offset mismatch: {BODY_ID} L{number} {surface!r}")
        result.append({
            "mention_id": f"m-chp8-p213-{len(result)+1:03d}", "segment_id": BODY_ID,
            "candidate_id": cid(key), "surface_form": surface,
            "start_char": str(start_char), "end_char": str(end_char), "note": note,
        })
    return result


new_mentions = add_mentions()
if len({row["candidate_id"] for row in new_candidates}) != len(new_candidates) or candidate_ids & {row["candidate_id"] for row in new_candidates}:
    raise SystemExit("planned candidate ID collision")
if len({row["mention_id"] for row in new_mentions}) != len(new_mentions) or mention_ids & {row["mention_id"] for row in new_mentions}:
    raise SystemExit("planned mention ID collision")

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
previous = next((row for row in statement_rows if row["statement_id"] == PREVIOUS_STATEMENT), None)
if not previous:
    raise SystemExit(f"previous open statement not found: {PREVIOUS_STATEMENT}")
previous_qualifiers = dict(previous.get("qualifiers", {}))
if previous_qualifiers.get("continuation_status") != "open" or previous_qualifiers.get("continuation_expected_segment_id") != BODY_ID:
    raise SystemExit("p.212 erotic-painting continuation changed; inspect before closing")


def make_statement(tail, start, end, predicate, claim, qualification, quote,
                   subject=None, object_=None, mentioned=(), extra=None):
    row = {
        "statement_id": f"st-chp8-p213-{tail}", "segment_id": BODY_ID,
        "subject_candidate_id": cid(subject) if subject else None,
        "object_candidate_id": cid(object_) if object_ else None,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": start, "source_line_end": end,
            "printed_page": 213, "pdf_physical_page": 11,
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
    make_statement("giordano-erotic-subjects-and-ignudo", 109, 109,
        "giordano_erotic_picture_description_continues_from_previous_page",
        "Haskell continues the p.212 account of Giordano's erotic paintings: one picture showed a distant nude figure described in Italian, followed by sets of fable subjects including Deianira and Nessus, Galatea and Tritons, and the Rape of Proserpina.",
        "The Italian quotation is retained without a translated gloss or independent iconographic identification. The source OCR begins 'os which'; the printed page reads 'of which', closing the p.212 phrase 'one of'. The listed scenes remain source-level work candidates.",
        "os which showed in the distance an ‘ignudo in atto assai lussurioso che si strugge per lui’, and sets of fables—Deianira and Nessus, Galatea and Tritons, The Rape of Proserpina",
        subject="giordano", object_="erotic_group",
        mentioned=["giordano","erotic_group","venus_amor","ignudo_picture","mythological_fables","deianira_nessus_pictures","galatea_tritons_pictures","rape_proserpina_picture"],
        extra={"continues_statement_id":PREVIOUS_STATEMENT,"ocr_corrections":[{"source_line":109,"ocr":"os which","print":"of which","basis":"CHP-8.pdf physical page 11; the p.212 'one' continues as 'of which' in print."}]}),
    make_statement("giordano-religious-and-devotional-pictures", 109, 109,
        "del_rosso_brothers_owned_giordano_religious_and_devotional_pictures",
        "Haskell says the brothers also owned Giordano religious paintings with Old and New Testament scenes and more purely devotional pictures.",
        "No individual painting or number is supplied; the devotional group remains distinct in the source wording.",
        "But they also owned religious paintings by him with scenes from the Old and New Testaments, as well as more purely devotional pictures",
        subject="family", object_="religious_paintings",
        mentioned=["family","giordano","religious_paintings","devotional_pictures"]),
    make_statement("giordano-modelli-favored", 109, 109,
        "del_rosso_brothers_favored_giordano_modelli_for_altarpieces_and_other_works",
        "Haskell says the brothers showed a particular fondness for Giordano's modelli for altarpieces and other works.",
        "The models and intended works are not individually identified.",
        "and they showed a particular fondness for Giordano’s modelli for altarpieces and other works",
        subject="family", object_="altarpiece_modelli",
        mentioned=["family","giordano","altarpiece_modelli"]),
    make_statement("new-appreciation-of-brushwork", 110, 110,
        "new_appreciation_of_sketchy_unfinished_lively_brushwork_would_matter_in_eighteenth_century_art",
        "Haskell says the brothers' new appreciation of sketchy, unfinished and lively brushwork would become important in eighteenth-century art.",
        "This is Haskell's historical interpretation; no specific work or causal path is established by this sentence alone.",
        "This new appreciation of the sketchy, the unfinished, lively brush stroke, which was to be so important in eighteenth-century art",
        subject="sketchy_brushwork", mentioned=["sketchy_brushwork","family"]),
    make_statement("ferdinand-another-florentine-devotee", 110, 110,
        "grand_prince_ferdinand_another_great_florentine_devotee_of_brushwork",
        "Haskell says Grand Prince Ferdinand de' Medici would become another great Florentine devotee of this aesthetic.",
        "The source identifies him by title and name; no external identity or date is added here.",
        "and was to have another great Florentine devotee in the Grand Prince Ferdinand de’ Medici",
        subject="ferdinand", object_="sketchy_brushwork", mentioned=["ferdinand","sketchy_brushwork","florence"]),
    make_statement("nome-collecting-may-have-followed-giordano-intervention", 110, 111,
        "brushwork_appreciation_may_have_led_to_collecting_nome_through_giordano",
        "Haskell suggests that the brothers' appreciation may have led them, through Luca Giordano's intervention, to collect the work of another Neapolitan-school artist, François Nomé.",
        "The causal and intermediary roles are explicitly qualified by 'may have'; the source's contemporary popularity claim is Haskell's own framing.",
        "may have led to their collecting (through the intervention of Luca Giordano) the work of another artist of the Neapolitan school who has acquired enormous popularity in our own day. This was the",
        subject="family", object_="nom",
        mentioned=["family","giordano","neapolitan_school","nom"]),
    make_statement("nome-alias-and-inventory-description", 111, 111,
        "francois_nome_known_as_monsu_desiderio_and_described_as_lorenese_in_inventory",
        "Haskell names the artist François Nomé, says he was generally known as Monsù Desiderio, and reports that the brothers' inventory described him as 'Lorenese'.",
        "The inventory designation is reported through Haskell and is not expanded into an independent nationality or identity claim. S0 omits the accent in Nome; the print reads Nomé.",
        "Frenchman François Nome, generally known as ‘Monsù Desiderio’, and described in their inventory as ‘Lorenese’",
        subject="nom", object_="inventory", mentioned=["nom","inventory"],
        extra={"ocr_corrections":[{"source_line":111,"ocr":"François Nome","print":"François Nomé","basis":"CHP-8.pdf physical page 11."}]}),
    make_statement("nome-eleven-visionary-ruin-pictures", 111, 111,
        "del_rosso_inventory_included_eleven_nome_ruin_pictures",
        "Haskell reports eleven mannered, visionary ruin pictures by Nomé in the Del Rosso collection and gives several inventory descriptions.",
        "The individual descriptions are preserved as source-specific candidates; they are not assigned to known surviving works. 'Fatta di colpi' is retained as the inventory wording.",
        "They owned eleven of his mannered, visionary ruin pictures ‘fatta di colpi’, including a Babylon, an ‘antichità di palazzi’, a ‘gran Tempio antico’, a Temple of Solomon and an imaginary view of Venice",
        subject="family", object_="nome_ruin_pictures",
        mentioned=["family","nom","nome_ruin_pictures","babylon","nome_palazzi","nome_gran_temple","temple_solomon","nome_venice_view","venice","inventory"]),
    make_statement("callot-print-and-original-plate", 111, 112,
        "del_rosso_brothers_possessed_apparently_original_plate_for_callot_print",
        "Haskell says the brothers apparently possessed the original plate for Callot's print La Fiera dell'Impruneta.",
        "'Apparently' qualifies the plate's originality. The printing matrix and the print are distinct objects; S0 misreads the title, corrected against the page image.",
        "And the same taste for the Mannerist is shown in their possession of what was apparently the original plate for\nCallot’s print of La Fiera dellTmpruneta.",
        subject="family", object_="callot_printing_plate",
        mentioned=["family","mannerist","callot_printing_plate","callot_print"],
        extra={"ocr_corrections":[{"source_line":112,"ocr":"La Fiera dellTmpruneta","print":"La Fiera dell'Impruneta","basis":"CHP-8.pdf physical page 11."}]}),
    make_statement("collection-emphasis-on-naples-and-neglect-of-rome", 113, 114,
        "del_rosso_collection_emphasized_naples_and_neglected_rome",
        "Haskell calls the Del Rosso collection an isolated phenomenon of great emphasis on Naples and total neglect of Rome, and says this is of outstanding interest.",
        "'Total neglect' describes this collection's reported contents and is not generalized to Neapolitan or Florentine collecting as a whole.",
        "As an isolated phenomenon the del Rosso collection with its great emphasis on\nNaples and its total neglect of Rome is of outstanding interest",
        subject="del_rosso_collection", object_="naples",
        mentioned=["del_rosso_collection","family","naples","rome"],
        extra={"footnote_numbers":[1]}),
    make_statement("collection-shift-from-disegno-to-colore", 114, 115,
        "del_rosso_collection_shifted_from_florentine_disegno_to_colore",
        "Haskell describes the brothers' sudden conversion from the Florentine tradition of disegno to colore as symptomatic of advanced international taste near the Venetian revival.",
        "This is Haskell's art-historical interpretation. Preserve the comparison and timing without making it a formal period boundary.",
        "Whatever its motives, their sudden conversion from the Florentine tradition of ‘disegno’ to the values of\n‘colore’ was symptomatic of the most advanced international taste towards the end of the seventeenth century on the verge of the great Venetian revival.",
        subject="del_rosso_collection", object_="colore_value",
        mentioned=["del_rosso_collection","family","disegno","colore_value","international_taste","venetian_revival"]),
    make_statement("collection-contribution-to-florence-difficult-to-assess", 115, 115,
        "author_said_collection_contribution_to_florentine_cultural_life_difficult_to_assess",
        "Haskell says it is difficult to assess how far the collection made a direct and influential contribution to Florence's cultural life.",
        "The source explicitly marks the assessment as difficult; this does not settle whether the contribution occurred.",
        "But it is difficult to assess how far the collection represented something more important—a direct and influential contribution to the cultural life of Florence.",
        subject="del_rosso_collection", object_="florence", mentioned=["del_rosso_collection","florence"]),
    make_statement("conditional-rosso-role-in-giordano-commissions", 115, 115,
        "del_rosso_influence_depended_on_possible_role_in_giordano_commissions",
        "Haskell says that if Giordano was commissioned through del Rosso to decorate the Corsini chapel and Palazzo Riccardi ceiling, influence could be claimed for the brothers.",
        "Both the brothers' intermediary role and the resulting influence are conditional in the source; keep this separate from established commission facts.",
        "If it was through del Rosso that Luca Giordano was commissioned to decorate the Corsini chapel in the Carmine and the ceiling of the Palazzo Riccardi, we can certainly claim such an influence for the brothers.",
        subject="family", object_="corsini_commission",
        mentioned=["family","giordano","corsini_commission","corsini_chapel","carmine","riccardi_palace","riccardi_frescoes"]),
    make_statement("giordano-works-regional-importance", 115, 115,
        "corsini_and_riccardi_works_limited_effect_in_florence_but_crucial_in_central_italy",
        "Haskell says the works had disappointingly little effect on Florentine painting but were crucially important to central Italy and ranked among the century's masterpieces.",
        "These are Haskell's evaluations of the preceding works, not independent measures of reception or ranking.",
        "These works, though they had disappointingly little effect on Florentine painting, were of crucial importance to central Italy, and in their own right they rank among the masterpieces of the century.",
        subject="giordano_joint_decoration", object_="central_italy",
        mentioned=["giordano_joint_decoration","riccardi_frescoes","corsini_commission","florence","central_italy"]),
    make_statement("mehus-freshness-would-suit-giordano-patrons", 115, 116,
        "haskell_said_mehus_freshness_could_suit_giordano_friends_and_patrons_but_was_ignored",
        "Haskell says Livio Mehus was the only Florentine artist whose freshness and vitality could surely have satisfied Giordano's friends and patrons, yet the Del Rosso brothers largely ignored him.",
        "'Could surely have satisfied' is Haskell's counterfactual assessment; do not convert it into an actual commission or relationship.",
        "There was, for instance, in Florence only one artist whose freshness and vitality could surely have satisfied the friends and patrons of Luca\nGiordano. Yet Livio Mehus they largely ignored.",
        subject="mehus", object_="family", mentioned=["florence","giordano","mehus","family"]),
    make_statement("mehus-three-pictures-disappeared", 116, 116,
        "three_mehus_pictures_owned_in_1677_had_disappeared_twelve_years_later",
        "Haskell reports that the brothers owned three Mehus pictures in 1677 and that they had disappeared twelve years later.",
        "The later date is expressed relatively in the source; no cause, destination or inventory comparison is supplied.",
        "In 1677 they owned three pictures by him; twelve years later these had disappeared.",
        subject="mehus_pictures", object_="family",
        mentioned=["mehus_pictures","family","mehus"], extra={"date_text":"1677; twelve years later"}),
    make_statement("financial-interest-belief-about-giordano-patronage", 116, 116,
        "haskell_entertained_disturbing_belief_that_giordano_patronage_may_have_financial_motive",
        "Haskell says a disturbing belief persists that the brothers' special patronage of Giordano may have been dictated more by financial interests than aesthetic taste.",
        "This is explicitly a belief and a possibility, not an established motive or fact about the brothers' decisions.",
        "Somewhere, at the back of the mind, there persists the disturbing belief that their special patronage of Luca Giordano may have Been dictated more by financial interests than by aesthetic taste.",
        subject="family", object_="giordano",
        mentioned=["family","giordano"],
        extra={"ocr_corrections":[{"source_line":116,"ocr":"Been","print":"been","basis":"CHP-8.pdf physical page 11."}]}),
    make_statement("neapolitan-painting-diffused-through-patrons", 117, 117,
        "other_patron_collections_showed_neapolitan_painting_diffusion_across_italy",
        "Haskell says the importance Neapolitan painting had acquired across Italy was shown by patrons' collections beyond their native cities.",
        "This is Haskell's generalizing interpretation; the sentence introduces examples and does not claim every collection contained Neapolitan works.",
        "The importance that Neapolitan painting had acquired all over Italy towards the end of the seventeenth century is shown by the collections of other patrons who looked beyond their native cities.",
        subject="neapolitan_painting", object_="italy",
        mentioned=["neapolitan_painting","italy"]),
    make_statement("durazzo-local-collection-and-bologna-open", 117, 118,
        "girolamo_durazzo_family_collection_local_art_and_bologna_purchases_sentence_open",
        "Haskell introduces Girolamo Durazzo in Genoa as a member of a leading patrician family that built up a large local-art collection and says he turned to Bologna for many pictures.",
        "The sentence ends at 'as was' and continues on p.214; its contrast with Naples and the full account of Durazzo's pictures remain open.",
        "Thus in Genoa the Marchese Girolamo Durazzo, a member\n. of one of the leading patrician families which over the centuries had built up an extensive collection of local art, turned not only to Bologna for many of his pictures (as was",
        subject="durazzo", object_="durazzo_local_collection",
        mentioned=["durazzo","durazzo_family","durazzo_local_collection","genoa","bologna","durazzo_giordano_pictures"],
        extra={"continuation_status":"open","continuation_expected_segment_id":NEXT_ID,
               "continuation_note":"p.213 L118 ends at 'as was'; read p.214 L121 onward before resolving the sentence.",
               "ocr_corrections":[{"source_line":118,"ocr":". of one","print":"of one","basis":"CHP-8.pdf physical page 11; the initial mark is not printed sentence punctuation."}]}),
]

if len({row["statement_id"] for row in statements}) != len(statements) or statement_ids & {row["statement_id"] for row in statements}:
    raise SystemExit("planned statement ID collision")
for row in statements:
    q = row["qualifiers"]
    start, end = q["source_line_start"], q["source_line_end"]
    cited = "\n".join(source_lines[start - 1:end])
    if " ".join(row["original_quote"].split()) not in " ".join(cited.split()):
        raise SystemExit(f"quote not reproducible: {row['statement_id']}\n{row['original_quote']}")
    referenced = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        referenced.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        referenced.add(row["object_candidate_id"])
    if not referenced <= all_candidate_ids:
        raise SystemExit(f"missing candidate FK: {row['statement_id']}: {referenced - all_candidate_ids}")

updated_statements = []
closed_previous = False
for original in statement_rows:
    row = dict(original)
    if row["statement_id"] == PREVIOUS_STATEMENT:
        q = dict(row.get("qualifiers", {}))
        q.update({
            "continuation_status": "closed",
            "continuation_source_segment_id": BODY_ID,
            "continuation_source_line": 109,
            "continuation_statement_id": "st-chp8-p213-giordano-erotic-subjects-and-ignudo",
            "continuation_resolution": "p.213 L109 begins 'of which' in print (S0 OCR 'os which'), completing p.212's 'one of which'.",
        })
        q.pop("continuation_expected_segment_id", None)
        q.pop("continuation_note", None)
        ids = list(q.get("mentioned_candidate_ids", []))
        if candidate_by_key["ignudo_picture"] not in ids:
            ids.append(candidate_by_key["ignudo_picture"])
        q["mentioned_candidate_ids"] = ids
        row["qualifiers"] = q
        closed_previous = True
    updated_statements.append(row)
if not closed_previous:
    raise SystemExit("expected p.212 open statement was not closed")

coverage_updates = {
    PREVIOUS_ID: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L99-106",
        "note": "p.212 body read against CHP-8.pdf physical p.10. L99 closes p.211's grandfather clause; p.213 L109 closes the p.212 sentence ending 'one' (printed 'of which', S0 OCR 'os which'). OCR corrections 'given.the'→'given the' and 'heirs ' of'→'heirs of' are recorded in S2 only. Printed notes 1-5 remain in the later canonical notes segment.",
    },
    BODY_ID: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L109-118",
        "note": "p.213 body read against CHP-8.pdf physical p.11. L109 closes p.212's 'one of which' and lists Giordano erotic, fable, religious and devotional works; p.110-116 discusses the Del Rosso collection, Nomé, collecting taste and Haskell's qualified account of Giordano and Mehus. L117-118 begins Girolamo Durazzo's Genoa example and remains open at 'as was' into p.214 L121. Notes are in the later canonical footnotes segment. S0 OCR corrections ('os'→'of', 'Nome'→'Nomé', 'dellTmpruneta'→'dell'Impruneta', 'Been'→'been') are recorded only in S2.",
    },
}
updated_coverage = []
found = set()
for original in coverage_rows:
    row = dict(original)
    if row["segment_id"] in coverage_updates:
        row.update(coverage_updates[row["segment_id"]])
        found.add(row["segment_id"])
    updated_coverage.append(row)
if found != set(coverage_updates):
    raise SystemExit(f"coverage update targets not found: {set(coverage_updates)-found}")

preview = {
    "mode": "dry-run", "segment_id": BODY_ID,
    "new_candidates": len(new_candidates), "candidate_ids": [r["candidate_id"] for r in new_candidates],
    "untyped_candidates": [r["candidate_id"] for r in new_candidates if not r["suggested_type"]],
    "new_mentions": len(new_mentions), "new_statements": len(statements),
    "closed_previous_statement": PREVIOUS_STATEMENT,
    "open_continuation": {"statement_id":"st-chp8-p213-durazzo-local-collection-and-bologna-open", "next_segment_id":NEXT_ID},
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
updated_mentions = [dict(row) for row in mention_rows] + new_mentions
updated_statements.extend(statements)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, updated_mentions)
write_jsonl_atomic(statement_path, updated_statements)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
