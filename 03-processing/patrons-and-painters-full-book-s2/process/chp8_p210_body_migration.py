"""Controlled S2 migration for chapter 8 printed p.210 body text.

Default invocation is a read-only dry run. Print readings and OCR corrections
are recorded in S2; immutable S0 source transcriptions are never edited here.
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
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE_PATH = ROOT / SOURCE_REL
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l72-82"
PREVIOUS_SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l62-70"
NEXT_SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l84-96"
PREVIOUS_STATEMENT_ID = "st-chp8-p209-ruffo-aimed-for-representative-collection-open"
CONTINUATION_STATEMENT_ID = "st-chp8-p210-ruffo-collection-of-leading-contemporaries"
BACKUP_SUFFIX = ".bak-s2-chp8-p210-body-20260930"
EXPECTED_MAX_CANDIDATE = 7475


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
if not meta or meta["source_file"] != SOURCE_REL or (int(meta["line_start"]), int(meta["line_end"])) != (72, 82):
    raise SystemExit("p.210 segment metadata changed; review before migration")
raw_source = SOURCE_PATH.read_bytes()
if hashlib.sha256(raw_source).hexdigest() != meta["asset_sha256"]:
    raise SystemExit("source file fingerprint changed; rebuild segments and review")
source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[71:82]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != meta["sha256"]:
    raise SystemExit("p.210 segment text hash changed; review before migration")
if coverage_by_id.get(SEGMENT_ID, {}).get("disposition") != "queued":
    raise SystemExit("expected queued p.210 coverage; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("mentions already exist for p.210; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in statement_rows):
    raise SystemExit("statements already exist for p.210; inspect before rerunning")

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
    candidate("cand-7476", "Unidentified agent who wrote Ruffo the Italian remark about famous pictures", "person",
              "The text identifies this person only as Ruffo's agent; do not merge with Abram Breughel or another agent without evidence.", 73),
    candidate("cand-7477", "Don Antonio Ruffo's collection of prints", "",
              "A distinct print collection is mentioned, but the current taxonomy has no collection type; retain type unresolved.", 76),
    candidate("cand-7478", "Spanish Empire (political context for Messina and Neapolitan painting)", "institution",
              "The phrase denotes the declining Spanish imperial sphere in Haskell's account; global identity alignment remains for S3.", 77),
    candidate("cand-7479", "Don Antonio Ruffo's unidentified brother", "person",
              "The passage says most of the listed Neapolitan and South Italian pictures were inherited from his brother but gives no name.", 75),
    candidate("cand-7480", "Neapolitan and South Italian painters represented in Ruffo's gallery (unnamed group)", "term",
              "A source-defined group of painters, not a single artist or a formal organization; individual named painters are recorded separately.", 75),
    candidate("cand-7481", "Unidentified flower pictures in Don Antonio Ruffo's collection", "work",
              "Haskell reports more than a dozen flower pictures by Abram Breughel alone; individual titles and objects are not identified.", 75),
    candidate("cand-7482", "Unidentified landscapes in Don Antonio Ruffo's collection", "work",
              "Landscape pictures are named as a collected subject group without individual titles or attributions in this passage.", 75),
    candidate("cand-7483", "Unidentified artists whose work for Ruffo was stimulated by his gallery's reputation", "term",
              "The passage refers collectively to artists who worked for Ruffo; no individual members are named here.", 77),
    candidate("cand-7484", "Italian patronage shift in which provincial centres challenged Rome's supremacy", "term",
              "Haskell's period-level characterization of provincial centres and the international prestige of Neapolitan artists; not a predeclared project theme.", 81),
    candidate("cand-7485", "Unidentified Florentine patrons appreciative of Neapolitan art", "term",
              "A source-described group whose appreciation is said to have generated important commissions; members and commissions are not named here.", 81),
    candidate("cand-7486", "Unidentified fine house in Via Chiara, Florence", "place",
              "The house is described as set in a garden with fountains and statues, near S. Maria Novella; no house name is supplied.", 81),
    candidate("cand-7487", "Via Chiara in Florence", "place",
              "Street named as the location of the unidentified house; exact modern street identification is not established here.", 81),
    candidate("cand-7488", "Church of S. Maria Novella in Florence", "place",
              "Church used as a location reference for the unidentified house; kept distinct from the church institution and its artworks.", 82),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates) or new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate IDs collide")
existing_natural = {(r["canonical_name"].casefold(), (r.get("suggested_type") or "").casefold())
                    for r in candidate_rows if not r.get("index_entry_id")}
for row in new_candidates:
    key = (row["canonical_name"].casefold(), row["suggested_type"].casefold())
    if key in existing_natural:
        raise SystemExit(f"candidate natural-key collision: {row['canonical_name']}")
    existing_natural.add(key)


mention_specs = []


def add(line_number, surface, cid, note, occurrence=1):
    mention_specs.append((line_number, surface, cid, note, occurrence))


# L73: continuation of the p.209 collection aim, an unnamed agent's words,
# the three named Rembrandt paintings, and Haskell's reception statement.
add(73, "contemporaries", "cand-2301", "The index subentry records Ruffo's interest in contemporary painters; this phrase completes the p.209 collecting aim.")
add(73, "his", "cand-2297", "Anaphoric reference to Don Antonio Ruffo.")
add(73, "agent", "cand-7476", "Unidentified Ruffo agent who wrote the Italian remark; not identified with Abram Breughel.")
add(73, "him", "cand-2297", "Recipient of the unnamed agent's remark: Don Antonio Ruffo.")
add(73, "this motive", "cand-2301", "Anaphoric reference to Ruffo's aim of collecting works by leading contemporaries.")
add(73, "Rembrandt", "cand-2117", "Artist whose three works are listed; use the index's person candidate.")
add(73, "Aristotle contemplating the Bust of Homer", "cand-2119", "First of the three Rembrandt pictures; Plate 35a is a cross-reference, not a second work.")
add(73, "Alexander the Great", "cand-2118", "Second named Rembrandt picture; the phrase is a work title, not a mention of the historical ruler.")
add(73, "The Blind Homer", "cand-2120", "Third named Rembrandt picture; later reference maps to this same indexed work candidate.")
add(73, "Italy", "cand-3461", "Place in Haskell's comparison of Rembrandt's reception; cross-chapter alignment remains for S3.")
add(73, "his etchings", "cand-2117", "Rembrandt's etchings are excepted from Haskell's claim about limited Italian appreciation.")
add(73, "Russo’s", "cand-2297", "S0 OCR form; the print reads Ruffo's. Correction is recorded in S2 only.")

# L74: Breughel's reported letter, Ruffo's reaction to The Blind Homer,
# Rembrandt's reception, classicist doctrine, and the Guercino comparison.
add(74, "Rome", "cand-4490", "Place where Abram Breughel is described as Ruffo's Flemish agent; candidate is a source-derived place.")
add(74, "Abram Breughel", "cand-0448", "Named Flemish agent in Rome; retain the report as Haskell's account of a 1665 letter.")
add(74, "he", "cand-0448", "Anaphoric reference to Abram Breughel, the writer of the 1665 letter as reported by Haskell.")
add(74, "Rembrandt", "cand-2117", "Artist whose reception Breughel reportedly described.", 1)
add(74, "Russo himself", "cand-2297", "S0 OCR form; the print reads Ruffo himself. This is the patron, not Rembrandt.")
add(74, "the great master’s", "cand-2117", "Anaphoric reference to Rembrandt and his late-period brushwork.")
add(74, "The Blind Homer", "cand-2120", "Work returned by Ruffo for completion, according to Haskell.")
add(74, "he", "cand-2297", "Anaphoric reference to Ruffo in the statement that he admired Rembrandt.", 2)
add(74, "Rembrandt", "cand-2117", "Artist Ruffo is said obviously to have admired.", 2)
add(74, "he", "cand-2297", "Anaphoric reference to Ruffo in the comparison with Roman classicist doctrines.", 3)
add(74, "classicist doctrines", "cand-4628", "Conceptual reference to the classicist tendency; S3 will decide whether it is the same indexed Roman-classicism candidate.")
add(74, "Rome", "cand-4490", "Centre in which the classicist doctrines gained force.", 2)
add(74, "He", "cand-2297", "Anaphoric reference to Ruffo, who deliberately asked Guercino to paint a matching picture.")
add(74, "Guercino", "cand-1258", "Painter asked to make a picture that matched Rembrandt's Aristotle.", 1)
add(74, "the picture", "cand-7471", "The unidentified Guercino picture already introduced in the p.209 match request.")
add(74, "Rembrandt’s Aristotle", "cand-2119", "Short reference to Aristotle contemplating the Bust of Homer; nested artist mention follows.")
add(74, "Rembrandt", "cand-2117", "Artist named within the shortened work reference; properly nested inside the work mention.", 3)
add(74, "this artist’s", "cand-1258", "Anaphoric reference to Guercino in the claim about early and robust-style works.")
add(74, "Guercino", "cand-1258", "Painter described as one of Ruffo's apparent favourites.", 2)
add(74, "his favourites", "cand-2297", "Ruffo's preference; the artist being compared is Guercino.")
add(74, "his pictures", "cand-1258", "The seven pictures are by Guercino, not a reference to Ruffo's ownership as creator.")
add(74, "Sacchi", "cand-2318", "Andrea Sacchi, whose one Ruffo picture is contrasted with Guercino's seven.")
add(74, "Maratta", "cand-1526", "Carlo Maratta, whose one Ruffo picture is contrasted with Guercino's seven.")
add(74, "Salvator Rosa", "cand-2236", "Named painter among those who especially appealed to Ruffo.")
add(74, "Giacinto Brandi", "cand-0446", "Named painter among those who especially appealed to Ruffo.")
add(74, "Michelangelo", "cand-0625", "First part of the printed name Michelangelo Cerquozzi, completed at the start of L75.")

# L75-L76: Neapolitan holdings, subject groups, Polidoro, and prints.
add(75, "Cerquozzi", "cand-0625", "Completes Michelangelo Cerquozzi's name across the S0 line break.")
add(75, "Rome", "cand-4490", "Location where these named painters were working.")
add(75, "him", "cand-2297", "Ruffo, to whom the named painters appealed.")
add(75, "Neapolitans", "cand-7480", "Painter group distinguished from the broader South Italian group in this sentence.")
add(75, "South Italians", "cand-7480", "Painter group whose works, along with Neapolitan works, were well represented.")
add(75, "his gallery", "cand-7468", "Ruffo's picture collection; candidate created on p.209.")
add(75, "Novelli", "cand-1757", "The p.210 index entry identifies this surname as Pietro Novelli (il Monrealese); external/global identity alignment remains for S3.")
add(75, "Ribera", "cand-2140", "The p.210 index entry maps this surname to Giuseppe Ribera; global identity alignment remains for S3.")
add(75, "Andrea Vaccaro", "cand-2673", "Named painter; the index entry specifically covers p.210.")
add(75, "Stanzione", "cand-2506", "Massimo Stanzione; the index entry covers pp.205 and 210.")
add(75, "most of these", "cand-7480", "Anaphoric reference to the listed Neapolitan and South Italian pictures; the source does not allocate inheritances by artist.")
add(75, "his brother", "cand-7479", "Ruffo's unnamed brother, from whom most of the preceding group of pictures was inherited.")
add(75, "Religious subjects", "cand-7468", "Subject category in Ruffo's collection; Haskell says it had a clear majority.")
add(75, "he", "cand-2297", "Anaphoric reference to Ruffo as collector.", 1)
add(75, "flower pictures", "cand-7481", "Unidentified collected work group; the quantity is more than a dozen by Abram Breughel alone.")
add(75, "his Flemish agent Abram Breughel", "cand-0448", "Abram Breughel, already named on this page as Ruffo's Flemish agent.")
add(75, "landscapes", "cand-7482", "Unidentified landscape paintings in Ruffo's collection.")
add(75, "Russo", "cand-2297", "S0 OCR form; the print reads Ruffo. Correction is recorded in S2 only.")
add(75, "Polidoro da", "cand-0553", "First part of Polidoro da Caravaggio's name; the surname continues on L76.")
add(76, "Caravaggio", "cand-0553", "Completes the name Polidoro da Caravaggio across the S0 line break.")
add(76, "he.", "cand-2297", "S0 OCR includes a stray period; the print reads 'he also'. Pronoun refers to Ruffo.")
add(76, "a collection of prints", "cand-7477", "Distinct print collection owned by Ruffo; its taxonomy type remains unresolved.")
add(76, "Rembrandt", "cand-2117", "Artist represented by 189 prints in Ruffo's collection.", 1)

# L77-L82: collection dispersal, cultural reach, Neapolitan prestige, and
# the open introduction of the three Rosso brothers.
add(77, "he", "cand-2297", "Anaphoric reference to Ruffo as the collector who assembled the pictures.")
add(77, "his death", "cand-2297", "Ruffo's death is the point after which the collection was gradually dispersed.")
add(77, "them", "cand-7468", "The pictures assembled in Ruffo's collection.")
add(77, "Russo’s", "cand-2297", "S0 OCR form; the print reads Ruffo's. Correction is recorded in S2 only.")
add(77, "gallery", "cand-7468", "Ruffo's gallery/collection, described as an isolated cultural stronghold.")
add(77, "Spanish empire", "cand-7478", "Political context; kept distinct from the geographic place Spain.")
add(77, "whose reputation", "cand-7468", "The relative pronoun refers to Ruffo's gallery and its reputation.")
add(77, "those artists who worked for him", "cand-7483", "Unnamed artist group said by Haskell to have been stimulated by the gallery's reputation.")
add(77, "him", "cand-2297", "Anaphoric reference to Ruffo, the patron for whom the artists worked.")
add(78, "Ruffo", "cand-2297", "Don Antonio Ruffo, who tried to obtain public commissions.")
add(78, "public commissions", "cand-2300", "Ruffo index subentry specifically covering attempts to obtain public commissions for Guercino and Preti.")
add(78, "Messina", "cand-1655", "City for which Ruffo sought public commissions.")
add(78, "Guercino", "cand-1258", "Painter for whom Ruffo tried to obtain public commissions.", 1)
add(78, "Mattia", "cand-2056", "First part of Mattia Preti's name, completed on L79.")
add(79, "Preti", "cand-2056", "Completes Mattia Preti's name across the S0 line break.")
add(80, "Neapolitan painting", "cand-1729", "Index candidate for the diffusion of Neapolitan painting, whose page range includes p.210.")
add(80, "Spanish empire", "cand-7478", "Political sphere whose frontiers Neapolitan painting is said to have crossed.")
add(81, "Italian patronage", "cand-7484", "The phase-level framework in which provincial centres challenge Rome's former primacy.")
add(81, "absolute supremacy of Rome", "cand-4490", "Rome as the artistic centre whose supremacy was being challenged.")
add(81, "provincial centres", "cand-7484", "Conceptual group within Haskell's account of changing Italian patronage.")
add(81, "Neapolitan artists", "cand-7480", "Artist group said to acquire international prestige.")
add(81, "Florence", "cand-1041", "The index candidate includes p.210; retain the city sense.")
add(81, "Italy", "cand-3461", "Geographic comparison with Naples.")
add(81, "Naples", "cand-1722", "City used in the comparison of spirit and traditions.")
add(81, "patrons", "cand-7485", "Unidentified Florentine patrons who appreciated Neapolitan art.")
add(81, "Neapolitan art", "cand-1729", "The art whose appreciation is linked by Haskell to important commissions.")
add(81, "a fine house", "cand-7486", "Unidentified house described as the principal outpost of this appreciation.")
add(81, "Via Chiara", "cand-7487", "Street named as the house's location.")
add(82, "S. Maria Novella", "cand-7488", "Church named as the nearby landmark; distinct from the house and from the institution, if any.")
add(82, "It", "cand-7486", "Anaphoric reference to the fine house on Via Chiara.")
add(82, "three brothers", "cand-7486", "The house's occupants are introduced as brothers; their full names continue across the page break.")
add(82, "Andrea", "cand-2275", "First name of Andrea del Rosso; the p.210 index entry covers this page, while p.211 supplies the surname in the text.")
add(82, "Lorenzo", "cand-2282", "First name of Lorenzo del Rosso; the p.210 index entry covers this page, while p.211 supplies the surname in the text.")
add(82, "Ottavio", "cand-2286", "First name of Ottavio del Rosso; the p.210 index entry covers this page, while p.211 supplies the surname in the text.")

new_mentions = []
line_offsets = {}
offset = 0
for line_number, line in zip(range(72, 83), segment_lines):
    line_offsets[line_number] = offset
    offset += len(line) + 1
for index, (line_number, surface, cid, note, occurrence) in enumerate(mention_specs, 1):
    if cid not in candidate_ids | new_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {cid}")
    source_line = source_lines[line_number - 1]
    if surface and surface[0].isalnum() and surface[-1].isalnum():
        starts = [match.start() for match in re.finditer(rf"(?<!\w){re.escape(surface)}(?!\w)", source_line)]
    else:
        starts = []
        cursor = 0
        while True:
            found = source_line.find(surface, cursor)
            if found < 0:
                break
            starts.append(found)
            cursor = found + 1
    if occurrence > len(starts):
        raise SystemExit(f"line {line_number}: occurrence {occurrence} missing for {surface!r}; found {len(starts)}")
    start = line_offsets[line_number] + starts[occurrence - 1]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch for {surface!r}")
    new_mentions.append({
        "mention_id": f"m-chp8-p210-{index:03d}",
        "segment_id": SEGMENT_ID,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })
new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["candidate_id"]))
for row in new_mentions:
    if row["mention_id"] in existing_mention_ids:
        raise SystemExit(f"mention ID collision: {row['mention_id']}")
for i, first in enumerate(new_mentions):
    a, b = int(first["start_char"]), int(first["end_char"])
    for second in new_mentions[i + 1:]:
        c, d = int(second["start_char"]), int(second["end_char"])
        if c >= b:
            break
        if (a, b) == (c, d):
            raise SystemExit(f"duplicate exact-span mentions: {first!r} / {second!r}")
        nested = (a <= c and d <= b) or (c <= a and b <= d)
        if not nested:
            raise SystemExit(f"overlapping non-nested mentions: {first!r} / {second!r}")


ocr_corrections = [
    {"source_line": 73, "ocr": "desiderate", "print": "desiderare", "basis": "CHP-8.pdf physical page 8."},
    {"source_line": 73, "ocr": "Russo’s", "print": "Ruffo’s", "basis": "CHP-8.pdf physical page 8."},
    {"source_line": 74, "ocr": "Russo", "print": "Ruffo", "basis": "CHP-8.pdf physical page 8."},
    {"source_line": 74, "ocr": "picture \" which", "print": "picture which", "basis": "CHP-8.pdf physical page 8; the stray quote is not present in print."},
    {"source_line": 75, "ocr": "Russo", "print": "Ruffo", "basis": "CHP-8.pdf physical page 8."},
    {"source_line": 76, "ocr": "he. also", "print": "he also", "basis": "CHP-8.pdf physical page 8."},
    {"source_line": 77, "ocr": "Russo’s", "print": "Ruffo’s", "basis": "CHP-8.pdf physical page 8."},
]


def make_statement(sid, line_start, line_end, predicate, claim, qualification,
                   *, subject=None, obj=None, mentioned=(), quote=None, extra=None, speaker="Haskell"):
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 210,
        "pdf_physical_page": 8,
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


body_statements = [
    make_statement(CONTINUATION_STATEMENT_ID, 73, 73,
                  "patron_aimed_for_representative_collection_of_leading_contemporaries_continuation",
                  "The p.209 sentence completes: Haskell says Ruffo was trying to assemble a representative collection of works by all the leading contemporaries.",
                  "This segment supplies the object and scope of the p.209 phrase 'representative collection'; it closes that sentence. The p.209 and p.210 fragments remain separately anchored to their source segments.",
                  subject="cand-2297", obj="cand-7468", mentioned=["cand-2297", "cand-7468", "cand-2301"],
                  quote="of works by all the leading contemporaries",
                  extra={"continuation_of_statement_id": PREVIOUS_STATEMENT_ID, "continuation_status": "closed",
                         "continuation_source_segment_id": PREVIOUS_SEGMENT_ID, "continuation_source_line": 70,
                         "continuation_fragment": "of works by all the leading contemporaries"}),
    make_statement("st-chp8-p210-unnamed-agent-italian-remark", 73, 73,
                  "unnamed_agent_wrote_patron_italian_remark_about_desire_for_famous_pictures",
                  "Haskell reports that Ruffo's unnamed agent wrote to him that desiring pictures by famous painters could not be called an illness.",
                  "The sentence is an Italian quotation reported by Haskell; the agent is not identified and must not be merged with Abram Breughel.",
                  subject="cand-7476", obj="cand-2297", mentioned=["cand-7476", "cand-2297"],
                  quote="‘non si può dire infermità il desiderate quadri di Pittori famosi’, his agent wrote to him",
                  extra={"quoted_speaker": "Ruffo's unnamed agent, as reported by Haskell",
                         "ocr_corrections": [ocr_corrections[0]]}),
    make_statement("st-chp8-p210-ruffo-bought-three-rembrandt-pictures", 73, 73,
                  "collector_bought_three_rembrandt_pictures_over_about_a_dozen_years",
                  "Haskell says Ruffo bought three pictures by Rembrandt over a period of a dozen years.",
                  "The purchase motive is given as probable in the adjacent clause; the works and approximate duration are listed, but no purchase dates are supplied.",
                  subject="cand-2297", obj=None, mentioned=["cand-2297", "cand-2117", "cand-2119", "cand-2118", "cand-2120"],
                  quote="the three pictures by Rembrandt—Aristotle contemplating the Bust of Homer (Plate 35a), Alexander the Great and The Blind Homer—bought over a period of a dozen years",
                  extra={"quantity": 3, "duration_text": "a dozen years", "relation_candidate": True,
                         "work_candidate_ids": ["cand-2119", "cand-2118", "cand-2120"], "plate_reference": "Plate 35a",
                         "modality": "bought; the causal motive is probably"}),
    make_statement("st-chp8-p210-rembrandt-reception-in-italy", 73, 73,
                  "author_assessed_rembrandts_reception_in_italy_except_for_etchings",
                  "Haskell says Rembrandt was fairly well known but not widely appreciated in Italy, with an exception for his etchings.",
                  "This is Haskell's generalization about reception, not a claim that no Italian appreciated Rembrandt or that etchings were universally accepted.",
                  subject="cand-2117", obj="cand-3461", mentioned=["cand-2117", "cand-3461"],
                  quote="Rembrandt was fairly well known but not widely appreciated in Italy (except for his etchings)"),
    make_statement("st-chp8-p210-breughel-reported-rembrandt-reception-1665", 74, 74,
                  "breughel_reported_low_local_regard_for_rembrandt_in_1665",
                  "Haskell reports that Abram Breughel wrote in 1665 that Rembrandt's pictures were not highly regarded 'here'.",
                  "Haskell says Breughel was probably not being insincere. Although Breughel is introduced as Ruffo's agent in Rome, the passage does not define the geographic scope of 'here'; the letter itself is not independently read here.",
                  subject="cand-0448", obj="cand-2117", mentioned=["cand-0448", "cand-2117", "cand-4490"],
                  quote="Abram Breughel was probably not being insincere (as has been suggested) when he wrote in 1665 that ‘the pictures of Rembrandt are not very highly thought of here’",
                  extra={"reported_date": "1665", "quoted_speaker": "Abram Breughel as reported by Haskell",
                         "modality": "probably not being insincere"}),
    make_statement("st-chp8-p210-ruffo-returned-blind-homer-for-completion", 74, 74,
                  "patron_returned_rembrandt_blind_homer_for_completion_after_rejecting_late_brushwork",
                  "Haskell says Ruffo found the free brush strokes of Rembrandt's last period unacceptable and sent The Blind Homer back to be completed.",
                  "The passage reports Ruffo's response and return of the picture; it does not establish a later conservation or provenance history.",
                  subject="cand-2297", obj="cand-2120", mentioned=["cand-2297", "cand-2117", "cand-2120"],
                  quote="Russo himself found the free brush strokes of the great master’s last period unacceptable and sent back The Blind Homer ‘to be completed’",
                  extra={"relation_candidate": True, "ocr_corrections": [ocr_corrections[2]]}),
    make_statement("st-chp8-p210-ruffo-admired-rembrandt-despite-reservation", 74, 74,
                  "patron_admired_artist_despite_reservation_about_late_work",
                  "Despite his reservation about The Blind Homer, Haskell says Ruffo obviously admired Rembrandt.",
                  "'Obviously' is Haskell's authorial characterization; it does not erase the stated rejection of the late brushwork.",
                  subject="cand-2297", obj="cand-2117", mentioned=["cand-2297", "cand-2117", "cand-2298"],
                  quote="Despite this it is obvious that he greatly admired Rembrandt",
                  extra={"modality": "obvious, as characterized by Haskell", "relation_candidate": True}),
    make_statement("st-chp8-p210-ruffo-comparatively-unaffected-by-classicism", 74, 74,
                  "patron_comparatively_unaffected_by_rising_roman_classicist_doctrines",
                  "Haskell says Ruffo was comparatively unaffected by the classicist doctrines gaining force in Rome in the second half of the seventeenth century.",
                  "The comparison is relative, not a claim that Ruffo had no classical preferences; the period is approximate and the doctrines are not defined further here.",
                  subject="cand-2297", obj="cand-4628", mentioned=["cand-2297", "cand-4628", "cand-4490"],
                  quote="he was comparatively unaffected by the classicist doctrines that gained such force in Rome during the second half of the-seventeenth century",
                  extra={"time_text": "during the second half of the seventeenth century", "modality": "comparatively"}),
    make_statement("st-chp8-p210-guercino-picture-to-match-rembrandt-aristotle", 74, 74,
                  "patron_deliberately_asked_guercino_to_paint_picture_matching_rembrandts_aristotle",
                  "Haskell says Ruffo deliberately asked Guercino to paint the unidentified picture that was to match Rembrandt's Aristotle in the painter's prima maniera gagliarda.",
                  "The p.209 passage separately says Guercino asked for a rough drawing and that his picture was required to match; this p.210 text clarifies that Ruffo deliberately requested the picture. Its title and subject remain unidentified.",
                  subject="cand-2297", obj="cand-7471", mentioned=["cand-2297", "cand-1258", "cand-7471", "cand-2117", "cand-2119"],
                  quote='He deliberately asked Guercino to paint the picture " which was to match Rembrandt’s Aristotle in his ‘prima maniera gagliarda’',
                  extra={"relation_candidate": True, "style_phrase": "prima maniera gagliarda",
                         "ocr_corrections": [ocr_corrections[3]]}),
    make_statement("st-chp8-p210-ruffo-sought-early-robust-guercino-works", 74, 74,
                  "patron_sought_examples_of_guercinos_early_robust_style",
                  "Haskell says Ruffo made special efforts at other times to obtain examples of Guercino's early and more robust style.",
                  "The works are not individually titled; the text distinguishes the particular matching picture from Ruffo's other efforts.",
                  subject="cand-2297", obj="cand-1258", mentioned=["cand-2297", "cand-1258"],
                  quote="at other times too he made special efforts to obtain examples of this artist’s early and more robust style",
                  extra={"relation_candidate": True}),
    make_statement("st-chp8-p210-guercino-apparent-favourite-and-counts", 74, 74,
                  "guercino_seems_among_ruffos_favourites_with_seven_pictures_vs_one_each",
                  "Haskell says Guercino seems to have been among Ruffo's favourites: Ruffo owned seven Guercino pictures and one each by Sacchi and Maratta.",
                  "The word 'seems' qualifies the favourite judgment; the stated counts are collection counts, not complete oeuvres.",
                  subject="cand-2297", obj="cand-1258", mentioned=["cand-2297", "cand-1258", "cand-2318", "cand-1526"],
                  quote="Guercino, indeed, seems to have been among his favourites for he owned seven of his pictures compared to only one each by Sacchi and Maratta",
                  extra={"modality": "seems", "picture_counts": {"Guercino": 7, "Andrea Sacchi": 1, "Carlo Maratta": 1},
                         "relation_candidate": True}),
    make_statement("st-chp8-p210-rosa-brandi-cerquozzi-appealed-to-ruffo", 74, 75,
                  "roman_painters_rosa_brandi_cerquozzi_especially_appealed_to_patron",
                  "Haskell says Salvator Rosa, Giacinto Brandi and Michelangelo Cerquozzi were among painters working in Rome who especially appealed to Ruffo.",
                  "The sentence crosses the line break between Michelangelo and Cerquozzi; it describes appeal, not a documented commission or friendship.",
                  subject="cand-2297", obj=None, mentioned=["cand-2297", "cand-2236", "cand-0446", "cand-0625", "cand-4490"],
                  quote="Salvator Rosa, Giacinto Brandi and Michelangelo\nCerquozzi were others among those working in Rome who especially appealed to him",
                  extra={"relation_candidate": True}),
    make_statement("st-chp8-p210-ruffo-gallery-neapolitan-and-south-italian-holdings", 75, 75,
                  "neapolitan_and_south_italian_painters_best_represented_in_ruffos_gallery",
                  "Haskell says Neapolitan and South Italian painters were best represented in Ruffo's gallery, listing seven Novelli pictures, twelve each by Ribera and Andrea Vaccaro, and nine by Stanzione.",
                  "The p.210 index entry points to Pietro Novelli (il Monrealese), but S3 must decide identity alignment. Counts are as reported; they do not identify individual works.",
                  subject="cand-2297", obj="cand-7480", mentioned=["cand-2297", "cand-7480", "cand-7468", "cand-1757", "cand-2140", "cand-2673", "cand-2506"],
                  quote="the Neapolitans and South Italians were those best represented in his gallery—seven pictures by Novelli, twelve each by Ribera and Andrea Vaccaro and nine by Stanzione",
                  extra={"picture_counts": {"Novelli": 7, "Ribera": 12, "Andrea Vaccaro": 12, "Massimo Stanzione": 9},
                         "index_page_mapping": {"Novelli": "N.csv#37; p.210", "Ribera": "Q-R.csv#67; p.210"},
                         "relation_candidate": True}),
    make_statement("st-chp8-p210-most-listed-south-italian-pictures-inherited-from-brother", 75, 75,
                  "gallery_includes_most_listed_south_italian_pictures_inherited_from_patron_brother",
                  "Haskell says most of the preceding group of Neapolitan and South Italian pictures in Ruffo's gallery were inherited from Ruffo's brother.",
                  "'Most of these' refers to the listed picture group; the source does not allocate the inherited works among the four named painters or explicitly name the recipient of the inheritance.",
                  subject="cand-7468", obj="cand-7479", mentioned=["cand-7479", "cand-2297", "cand-7480", "cand-7468"],
                  quote="though most of these were inherited from his brother",
                  extra={"quantity_qualifier": "most; no exact count", "relation_candidate": True}),
    make_statement("st-chp8-p210-ruffo-collected-religious-flower-landscape-subjects", 75, 75,
                  "religious_subjects_majority_with_flower_pictures_landscapes_and_other_themes",
                  "Haskell says religious subjects had a clear majority in Ruffo's collection; he also collected flower pictures, landscapes and other themes, with more than a dozen flower pictures by Abram Breughel alone.",
                  "The quantity applies to Breughel's flower pictures alone; individual works and the count of landscapes or other themes are not supplied.",
                  subject="cand-2297", obj="cand-7468", mentioned=["cand-2297", "cand-7468", "cand-7481", "cand-7482", "cand-0448"],
                  quote="Religious subjects have a clear majority over all others, but he also collected flower pictures (more than a dozen painted by his Flemish agent Abram Breughel alone), landscapes and other themes of all kinds",
                  extra={"quantity": "more than a dozen flower pictures by Abram Breughel alone",
                         "relation_candidate": True}),
    make_statement("st-chp8-p210-ruffo-interest-in-polidoro-da-caravaggio", 75, 76,
                  "collector_showed_special_interest_in_old_master_polidoro_da_caravaggio",
                  "Haskell says Ruffo showed special interest in the old master Polidoro da Caravaggio.",
                  "The OCR splits the artist's name across the page's source lines; the print spelling is confirmed in S2.",
                  subject="cand-2297", obj="cand-0553", mentioned=["cand-2297", "cand-0553"],
                  quote="Of old masters Russo showed a special interest in Polidoro da\nCaravaggio",
                  extra={"relation_candidate": True, "ocr_corrections": [ocr_corrections[4]]}),
    make_statement("st-chp8-p210-ruffo-owned-189-rembrandt-prints", 76, 76,
                  "collector_owned_print_collection_including_189_rembrandt_prints",
                  "Haskell says Ruffo owned a collection of prints that included 189 by Rembrandt.",
                  "The text does not identify the individual prints or state whether the count is exhaustive; the collection type remains unresolved in the taxonomy.",
                  subject="cand-2297", obj="cand-7477", mentioned=["cand-2297", "cand-7477", "cand-2117"],
                  quote="he. also owned a collection of prints which included 189 by Rembrandt",
                  extra={"quantity": 189, "quantity_unit": "prints attributed to Rembrandt in the reported collection",
                         "relation_candidate": True, "ocr_corrections": [ocr_corrections[5]]}),
    make_statement("st-chp8-p210-ruffo-picture-collection-dispersed", 77, 77,
                  "picture_collection_gradually_dispersed_after_patron_death_few_traced_now",
                  "Haskell says Ruffo's large picture collection was gradually dispersed after his death and that only a few pictures can now be traced.",
                  "The passage does not give an itemized dispersal history or identify the few traceable pictures.",
                  subject="cand-7468", obj=None, mentioned=["cand-7468", "cand-2297"],
                  quote="The astonishing number of pictures he had assembled was gradually dispersed after his death, and only a few of them can now be traced",
                  extra={"relation_candidate": True}),
    make_statement("st-chp8-p210-ruffo-gallery-isolated-cultural-stronghold", 77, 77,
                  "author_characterized_ruffo_gallery_as_isolated_cultural_stronghold_in_declining_spanish_empire",
                  "Haskell says Ruffo's gallery must have been an isolated stronghold of European culture in the backwater of the crumbling Spanish empire.",
                  "This is Haskell's retrospective characterization, qualified by 'must have been'; it is not an institutional status or an objective geographic classification.",
                  subject="cand-7468", obj="cand-7478", mentioned=["cand-7468", "cand-7478", "cand-2297"],
                  quote="even in its heyday Russo’s gallery must have been an isolated one, a stronghold of European culture in the backwater of the crumbling Spanish empire",
                  extra={"modality": "must have been", "ocr_corrections": [ocr_corrections[6]]}),
    make_statement("st-chp8-p210-gallery-reputation-stimulated-ruffo-artists", 77, 77,
                  "gallery_reputation_undoubtedly_stimulated_artists_working_for_ruffo",
                  "Haskell says the gallery's reputation undoubtedly stimulated the artists who worked for Ruffo.",
                  "The author marks the causal assessment as 'undoubtedly'; the artists are an unnamed group and no individual effect is specified.",
                  subject="cand-7468", obj="cand-7483", mentioned=["cand-7468", "cand-7483", "cand-2297"],
                  quote="whose reputation undoubtedly stimulated those artists who worked for him",
                  extra={"modality": "undoubtedly", "relation_candidate": True}),
    make_statement("st-chp8-p210-ruffo-gallery-limited-wider-significance", 77, 77,
                  "author_said_gallery_had_little_wider_significance",
                  "Haskell says Ruffo's gallery had little significance in any wider context.",
                  "The statement is immediately qualified by 'though' and p.210 L78's report that Ruffo tried hard to obtain public commissions; the contrast does not erase either claim.",
                  subject="cand-7468", obj=None, mentioned=["cand-7468"],
                  quote="which was of little significance in any wider context, though",
                  extra={"continuation_status": "closed", "continuation_segment_id": SEGMENT_ID,
                         "continuation_source_line": 78,
                         "continuation_statement_id": "st-chp8-p210-ruffo-tried-to-obtain-public-commissions",
                         "continuation_resolution": "The 'though' clause follows at p.210 L78."}),
    make_statement("st-chp8-p210-ruffo-tried-to-obtain-public-commissions", 78, 79,
                  "patron_tried_hard_to_obtain_public_commissions_for_guercino_and_mattia_preti_in_messina",
                  "Haskell says Ruffo tried hard to obtain public commissions in Messina for Guercino and Mattia Preti.",
                  "The text reports efforts to obtain public commissions; it does not state that the commissions were awarded or completed.",
                  subject="cand-2297", obj=None, mentioned=["cand-2297", "cand-2300", "cand-1655", "cand-1258", "cand-2056"],
                  quote="Ruffo tried hard to obtain public commissions in Messina for Guercino and Mattia\nPreti",
                  extra={"relation_candidate": True, "outcome": "attempt reported; award/completion not asserted"}),
    make_statement("st-chp8-p210-neapolitan-painting-crossed-spanish-imperial-frontiers", 80, 80,
                  "neapolitan_painting_spread_beyond_spanish_empire_frontiers",
                  "Haskell says Neapolitan painting spread far beyond the frontiers of the Spanish empire.",
                  "This is a broad historical generalization and does not name particular artists, works or destinations.",
                  subject="cand-1729", obj="cand-7478", mentioned=["cand-1729", "cand-7478"],
                  quote="Neapolitan painting spread far beyond the frontiers of the Spanish empire"),
    make_statement("st-chp8-p210-provincial-centres-and-neapolitan-prestige", 81, 81,
                  "provincial_centres_challenged_rome_and_neapolitan_artists_gained_international_prestige",
                  "Haskell characterizes this phase of Italian patronage as one in which provincial centres challenged Rome's absolute supremacy and Neapolitan artists acquired international prestige.",
                  "This is Haskell's period-level interpretation; it does not define every provincial centre or claim that Rome ceased to matter.",
                  subject=None, obj="cand-7484", mentioned=["cand-7484", "cand-4490", "cand-7480", "cand-1729"],
                  quote="one of the characteristics of this phase in Italian patronage, when the absolute supremacy of Rome was being challenged in various provincial centres, is the international prestige acquired by Neapolitan artists"),
    make_statement("st-chp8-p210-florentine-patrons-commissioned-neapolitan-art", 81, 81,
                  "florentine_patrons_appreciation_of_neapolitan_art_responsible_for_important_commissions",
                  "Despite Florence's distance from Naples in spirit and traditions, Haskell says there were Florentine patrons whose enthusiastic appreciation of Neapolitan art was responsible for vitally important commissions.",
                  "The patrons and commissions remain unnamed; Haskell's causal characterization is preserved without inventing specific works or commissioners.",
                  subject="cand-7485", obj="cand-1729", mentioned=["cand-1041", "cand-3461", "cand-1722", "cand-7485", "cand-1729"],
                  quote="Even in Florence, a city as far removed as any in Italy from the spirit and traditions of Naples, there existed patrons whose enthusiastic appreciation of Neapolitan art was responsible for vitally important commissions",
                  extra={"relation_candidate": True, "commission_outcome": "important commissions reported; objects not named"}),
    make_statement("st-chp8-p210-house-via-chiara-location-description", 81, 82,
                  "principal_outpost_of_neapolitan_art_appreciation_located_at_unidentified_house_near_santa_maria_novella",
                  "Haskell locates the principal outpost of this Florentine appreciation in a fine house on Via Chiara near S. Maria Novella, set in a beautiful garden with fountains and statues.",
                  "The house, street and church are distinct place candidates. The house has no supplied proper name; the garden and its features are descriptive setting, not separately named objects.",
                  subject="cand-7485", obj="cand-7486", mentioned=["cand-7485", "cand-7486", "cand-7487", "cand-7488", "cand-1041"],
                  quote="The principal outpost of this appreciation was to be found in a fine house, set in a beautiful garden with fountains and statues, in the Via Chiara near the church of\nS. Maria Novella"),
    make_statement("st-chp8-p210-house-inhabited-by-three-rosso-brothers-open", 82, 82,
                  "unidentified_florentine_house_inhabited_by_three_del_rosso_brothers_name_continuation_open",
                  "Haskell says the house was inhabited by three brothers, Andrea, Lorenzo and Ottavio; the surname is split onto p.211.",
                  "The p.210 index entries identify the three candidates as del Rosso, but the body text has not yet supplied the surname. Keep the segment and sentence open until p.211 is read.",
                  subject="cand-7486", obj=None, mentioned=["cand-7486", "cand-2275", "cand-2282", "cand-2286"],
                  quote="It was inhabited by three brothers, Andrea, Lorenzo and Ottavio",
                  extra={"relation_candidate": True, "person_candidate_ids": ["cand-2275", "cand-2282", "cand-2286"],
                         "continuation_status": "open", "continuation_expected_segment_id": NEXT_SEGMENT_ID,
                         "continuation_note": "p.211 begins with 'del Rosso', supplying the surname for the three brothers."}),
]

if len({row["statement_id"] for row in body_statements}) != len(body_statements):
    raise SystemExit("duplicate planned statement IDs")
new_statement_ids = {row["statement_id"] for row in body_statements}
if new_statement_ids & existing_statement_ids:
    raise SystemExit("planned statement ID collision")
if PREVIOUS_STATEMENT_ID not in existing_statement_ids:
    raise SystemExit("expected open p.209 continuation statement is missing")
updated_statements = []
closed_previous = False
for row in statement_rows:
    row = dict(row)
    if row["statement_id"] == PREVIOUS_STATEMENT_ID:
        q = dict(row["qualifiers"])
        if q.get("continuation_status") != "open" or q.get("continuation_expected_segment_id") != SEGMENT_ID:
            raise SystemExit("p.209 continuation state changed; inspect before closing")
        q.update({
            "claim": "Haskell says Ruffo was obviously trying to amass a representative collection of works by all the leading contemporaries.",
            "qualification": "The sentence closes on p.210 L73; the source fragments remain separately anchored and linked.",
            "continuation_status": "closed",
            "continuation_segment_id": SEGMENT_ID,
            "continuation_statement_id": CONTINUATION_STATEMENT_ID,
            "continuation_resolution": "Completed by p.210 L73: 'of works by all the leading contemporaries'.",
        })
        q.pop("continuation_expected_segment_id", None)
        q.pop("continuation_note", None)
        row["qualifiers"] = q
        closed_previous = True
    updated_statements.append(row)
if not closed_previous:
    raise SystemExit("failed to locate p.209 continuation statement")

for row in body_statements:
    q = row["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
    if not isinstance(row.get("original_quote"), str) or row["original_quote"] not in excerpt:
        raise SystemExit(f"quote is not reproducible in S0 source: {row['statement_id']}")
    if not (73 <= q["source_line_start"] <= q["source_line_end"] <= 82):
        raise SystemExit(f"statement line range outside p.210 body text: {row['statement_id']}")
    mentioned = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        mentioned.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        mentioned.add(row["object_candidate_id"])
    if not mentioned <= candidate_ids | new_candidate_ids:
        raise SystemExit(f"statement references missing candidate: {row['statement_id']}")
    if row["statement_id"] == CONTINUATION_STATEMENT_ID and q.get("continuation_of_statement_id") != PREVIOUS_STATEMENT_ID:
        raise SystemExit("p.209/p.210 continuation cross-reference is inconsistent")

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == SEGMENT_ID:
        row.update({
            "disposition": "reviewed",
            "migration_status": "partial",
            "source_line_ranges": "L73-82",
            "note": "P.210 body read against CHP-8.pdf physical p.8. S2 OCR readings: desiderate→desiderare; Russo→Ruffo at L73–77; remove stray quote after 'picture' at L74 and period in 'he. also' at L76; S0 remains unchanged. The p.209 representative-collection sentence closes at L73. The final sentence introduces three brothers and continues at p.211 L85 ('del Rosso'); p.210 has no printed footnote marker.",
        })
    updated_coverage.append(row)

preview = {
    "mode": "dry-run",
    "segment": SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(body_statements),
    "closed_previous_statement": PREVIOUS_STATEMENT_ID,
    "continuation_pending": {"statement_id": "st-chp8-p210-house-inhabited-by-three-rosso-brothers-open", "next_segment_id": NEXT_SEGMENT_ID},
    "coverage": {SEGMENT_ID: "reviewed/partial"},
    "ocr_corrections": ocr_corrections,
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
updated_statements.extend(body_statements)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, updated_statements)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
