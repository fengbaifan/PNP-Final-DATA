"""Controlled S2 migration for Chapter 8 printed page 236 and notes 1-3.

The default invocation is a read-only dry run. Source OCR remains unchanged;
print readings are recorded in statement qualifiers after image comparison.
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
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
P236 = "chp-8:08_CHP-8_sec_ii:l303-309"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P236, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p236-20261001"
PAGE_SCAN = PROCESS / "p236_page_review.png"
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments) or not TARGET_IDS <= set(segment_by_id):
    raise SystemExit("missing or duplicate target segment metadata")
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    if hashlib.sha256(asset.read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")
if not PAGE_SCAN.is_file() or not PDF.is_file():
    raise SystemExit("page 236 PDF or review image is missing")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
line_offsets = {}
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    lines = source_lines[meta["line_start"] - 1:meta["line_end"]]
    if hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), lines):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(line) + 1

candidate_fields, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
mention_fields, mention_rows = read_csv(TABLES / "mentions.csv")
statement_rows = read_jsonl(TABLES / "book-statements.jsonl")
coverage_fields, coverage_rows = read_csv(TABLES / "s2-coverage.csv")
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("duplicate S2 coverage segment IDs")
expected = {
    P236: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L373-435"),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")

new_candidates = [
    ("cand-7989", "Ricci’s ceiling scene showing Venus taking leave of Adonis in the Pitti room", "work", 306,
     "The central ceiling scene is described in the text; its exact catalogue title and present object identity are not supplied."),
    ("cand-7990", "Diana and Callisto wall scene in Ricci’s Pitti decoration", "work", 306,
     "One of four further wall scenes named by Haskell; no separate object title or present location is supplied."),
    ("cand-7991", "Pan and Syrinx wall scene in Ricci’s Pitti decoration", "work", 306,
     "One of four further wall scenes named by Haskell; no separate object title or present location is supplied."),
    ("cand-7992", "Europa and the Bull wall scene in Ricci’s Pitti decoration", "work", 307,
     "One of four further wall scenes named by Haskell; the Bull is not further identified in this passage."),
    ("cand-7993", "Diana and Actaeon wall scene in Ricci’s Pitti decoration", "work", 307,
     "One of four further wall scenes named by Haskell; no separate object title or present location is supplied."),
    ("cand-7994", "Callisto, figure in the Diana wall scene", "person", 306,
     "Named as a subject in the wall scene; no further identity or attributes are inferred."),
    ("cand-7995", "Actaeon, figure in the Diana wall scene", "person", 307,
     "Named as a subject in the wall scene; no further identity or attributes are inferred."),
    ("cand-7996", "Painted corner busts of unnamed men and women evoking antiquity in Ricci’s Pitti decoration", "work", 307,
     "The sitters are not identified; the source describes the busts as vaguely evoking the antique."),
    ("cand-7997", "Over-door composition with Medici arms, angels, putti, and crown in Ricci’s Pitti decoration", "work", 307,
     "A described part of the room decoration; no separate title is given."),
    ("cand-7998", "House of Medici represented by the arms in Ricci’s Pitti room", "family", 307,
     "The arms identify the Medici house in the described iconography; no specific person is implied."),
    ("cand-7999", "Orleans Museum named as holding a sketch for the fresco", "institution", 437,
     "The English institutional label is retained as Haskell gives it; current official name and present custody were not checked."),
    ("cand-8000", "Unidentified sketch for the fresco illustrated in Plate 39", "work", 437,
     "The note says a sketch for the fresco is at the Orleans Museum; the exact scope and object identity are not established."),
    ("cand-8001", "Ricci’s small-figure pictures with architectural backgrounds for Ferdinand", "work", 309,
     "Haskell describes a group and refers to one pair shown to Ferdinand; titles, number, and object identities remain unspecified."),
    ("cand-8002", "Macchiette: small-figure pictures of the type described by Haskell", "term", 309,
     "Retains Haskell’s genre term without treating it as the title of a particular work."),
    ("cand-8003", "Unidentified collaborators who usually painted architectural backgrounds for the small-figure pictures", "term", 309,
     "The collaborators are unnamed; the passage describes a usual division of work, not a named partnership."),
    ("cand-8004", "Intimate rococo style attributed to Ricci’s Pitti frescoes by Haskell", "term", 308,
     "A contextual term for Haskell’s description; identity with other Rococo candidates is left to S3."),
    ("cand-8005", "Abate Gherardi’s anonymous 1749 account of some of Consul Smith’s pictures in Venice", "archive", 436,
     "The work is identified only as an anonymous account in Haskell’s note; its exact title and text were not independently consulted."),
    ("cand-8006", "Fogolari (1937), Letter 106 of 3 April 1705", "archive", 438,
     "Citation locator reported by Haskell; the letter and Fogolari edition were not independently consulted."),
    ("cand-8007", "Pictures mentioned in Fogolari Letter 106, with Ricci attribution unresolved", "work", 438,
     "Haskell explicitly says it is unclear whether the pictures in the letter were by Ricci."),
    ("cand-8008", "Architectural painting by Saluzzi with figures by Sebastiano Ricci, initialled and dated 1706", "work", 438,
     "Haskell reports the 1716 inventory description and locates the painting at Lucca; no title or further object identity is given."),
    ("cand-8009", "Pinacoteca at Lucca named as the location of the architectural painting", "institution", 438,
     "Institutional label as cited by Haskell; present official name and current custody were not checked."),
    ("cand-8010", "Ferdinand’s court as the artistic setting characterized by Haskell", "institution", 304,
     "The court is the setting whose atmosphere Haskell invokes; its membership and institutional boundaries are not specified here."),
    ("cand-8011", "European art as a field in Haskell’s stylistic comparison", "term", 308,
     "A broad artistic field in the author’s evaluative comparison, not a political or geographic entity."),
]

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows}
new_keys = set()
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 372 else P236
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{source_line}",
    })
    candidate_ids.add(candidate_id)

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
new_mentions = []


def mention(segment_id, source_line, suffix, candidate_id, surface, note, occurrence=0):
    mention_id = f"m-chp8-p236-{suffix}"
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    line = source_lines[source_line - 1]
    search_at = 0
    found_at = -1
    for _ in range(occurrence + 1):
        found_at = line.find(surface, search_at)
        if found_at < 0:
            raise SystemExit(f"surface not found at L{source_line}: {surface!r} #{occurrence}")
        search_at = found_at + 1
    start = line_offsets[(segment_id, source_line)] + found_at
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span
                                     for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


mention_specs = [
    (P236, 304, "ferdinand-patronage", "cand-1609", "Ferdinand", "Grand Prince Ferdinand de’ Medici.", 0),
    (P236, 304, "pitti-work", "cand-7967", "the work", "Contextual reference to Ricci’s decoration for Ferdinand at the Pitti described on p.235."),
    (P236, 304, "ricci-writer", "cand-2179", "Ricci", "The writer is said to have known Sebastiano Ricci personally.", 0),
    (P236, 304, "grand-prince-instructions", "cand-1609", "the Grand Prince", "Ferdinand de’ Medici, in the report about instructions."),
    (P236, 304, "decoration-instructions", "cand-7967", "the decoration", "The decoration at the Pitti described on the preceding page."),
    (P236, 304, "ricci-frescoes", "cand-2179", "Ricci", "Artist named in the possessive phrase about the frescoes.", 1),
    (P236, 304, "frescoes-pitti", "cand-7967", "frescoes", "The frescoes in the Pitti decoration."),
    (P236, 304, "ferdinand-court", "cand-1609", "Ferdinand", "Ferdinand in the phrase naming the atmosphere of his court.", 1),
    (P236, 304, "prince-character", "cand-1609", "The Prince", "Coreference to Ferdinand de’ Medici."),
    (P236, 304, "baroque-ceiling", "cand-4723", "Baroque ceiling decoration", "Art-historical category in Haskell’s stylistic comparison."),
    (P236, 304, "ricci-previous-ventures", "cand-2179", "Ricci", "Artist whose earlier ceiling work is compared.", 2),
    (P236, 304, "palazzo", "cand-1558", "Palazzo", "Begins the cross-line name Palazzo Marucelli; completed at L305."),
    (P236, 304, "ricci-marucelli-work", "cand-2179", "Ricci", "Artist named in the possessive phrase about his nearly contemporary work.", 3),
    (P236, 305, "marucelli-palace", "cand-1558", "Marucelli", "Completes the cross-line name Palazzo Marucelli."),
    (P236, 305, "central-ceiling", "cand-7989", "The ceiling", "The described ceiling scene within the Pitti decoration."),
    (P236, 306, "venus", "cand-4171", "Venus", "Mythological figure in the ceiling scene."),
    (P236, 306, "adonis", "cand-4172", "Adonis", "Mythological figure in the ceiling scene."),
    (P236, 306, "diana-callisto-scene", "cand-7990", "Diana and Callisto", "Named wall-scene subject; nested character mentions are separately recorded."),
    (P236, 306, "diana", "cand-4136", "Diana", "Mythological figure in the wall scene."),
    (P236, 306, "callisto", "cand-7994", "Callisto", "Mythological figure in the wall scene."),
    (P236, 306, "pan-syrinx-scene-start", "cand-7991", "Pan and", "Wall-scene phrase continues with Syrinx at L307."),
    (P236, 306, "pan", "cand-4169", "Pan", "Mythological figure in the wall scene."),
    (P236, 306, "ovid", "cand-6777", "Ovid", "The source names Ovid but not a specific work."),
    (P236, 307, "syrinx", "cand-4170", "Syrinx", "Mythological figure continuing the wall-scene phrase from L306."),
    (P236, 307, "europa-bull-scene", "cand-7992", "Europa and the Bull", "Named wall-scene subject; the Bull is not further identified."),
    (P236, 307, "europa", "cand-4168", "Europa", "Mythological figure in the wall scene."),
    (P236, 307, "diana-actaeon-scene", "cand-7993", "Diana and Actaeon", "Named wall-scene subject; nested character mentions are separately recorded."),
    (P236, 307, "diana-actaeon", "cand-4136", "Diana", "Mythological figure in the wall scene."),
    (P236, 307, "actaeon", "cand-7995", "Actaeon", "Mythological figure in the wall scene."),
    (P236, 307, "corner-busts", "cand-7996", "busts", "Painted busts in the four corners; the people represented are unnamed."),
    (P236, 307, "overdoor-composition", "cand-7997", "the whole", "Refers to the asymmetrical over-door composition with arms, angels, putti, and crown."),
    (P236, 307, "medici-arms", "cand-7998", "the Medici", "The arms identify the Medici house in the room’s iconography."),
    (P236, 307, "florence", "cand-3397", "Florence", "City in Haskell’s stylistic assessment."),
    (P236, 308, "european-art", "cand-8011", "European art", "Broad artistic field named in Haskell’s stylistic comparison."),
    (P236, 308, "frescoes-delighted", "cand-7967", "The frescoes", "The Pitti decoration described on p.235."),
    (P236, 308, "ferdinand-delighted", "cand-1609", "Ferdinand", "Patron reported as delighted by the frescoes."),
    (P236, 308, "rococo-style", "cand-8004", "their intimate, rococo style", "Haskell’s characterization of the frescoes’ style."),
    (P236, 308, "paris", "cand-4653", "Paris", "Place in Haskell’s comparison with Parisian boudoirs."),
    (P236, 308, "italy", "cand-3461", "Italy", "Place in Haskell’s assessment of the style’s prospects."),
    (P236, 309, "ricci-small-pictures", "cand-2179", "Ricci", "Artist named in the sentence about other pictures.", 0),
    (P236, 309, "picture-group", "cand-8001", "various pictures", "Unspecified group of pictures described by subject and setting."),
    (P236, 309, "ferdinand-recipient", "cand-1609", "him", "Coreference to Ferdinand as patron.", 0),
    (P236, 309, "little-figures", "cand-8001", "little figures", "Description of the subject matter of the picture group."),
    (P236, 309, "architectural-backgrounds", "cand-8001", "architectural backgrounds", "Setting within the described picture group."),
    (P236, 309, "collaborator", "cand-8003", "a collaborator", "Unidentified collaborator said usually to have painted the architectural backgrounds."),
    (P236, 309, "quoted-scenes", "cand-8001", "le figurette", "Italian wording refers to one pair of the small-figure scenes."),
    (P236, 309, "pair-of-scenes", "cand-8001", "one pair of such scenes", "The pair is not individually identified."),
    (P236, 309, "macchiette", "cand-8002", "macchiette", "Haskell’s genre term for this kind of picture."),
    (P236, 309, "ricci-letter-tail", "cand-2179", "Ricci", "Begins a sentence continuing on p.237.", 1),
    (P236, 309, "ferdinand-letter-tail", "cand-1609", "Ferdinand", "Addressee in the incomplete sentence continuing on p.237."),
    (NOTES, 436, "gherardi", "cand-1155", "The Abate Gherardi", "Index candidate for Abate Gherardi; identity matching is deferred to S3."),
    (NOTES, 436, "anonymous-account", "cand-8005", "anonymous account", "Unidentified 1749 account described in the footnote."),
    (NOTES, 436, "consul-smith", "cand-2440", "Consul Smith", "Index candidate for Joseph Smith at p.236n; this mention remains at the source’s title-only form."),
    (NOTES, 436, "venice", "cand-3401", "Venice", "Place associated with the pictures in the anonymous account."),
    (NOTES, 436, "gherardi-ricci", "cand-2179", "Ricci", "Subject of the reported account."),
    (NOTES, 436, "florence-note", "cand-3397", "Florence", "Place named in the quoted report."),
    (NOTES, 436, "grand-prince", "cand-1609", "Gran Principe", "Ferdinand de’ Medici in the Italian quotation."),
    (NOTES, 437, "sketch", "cand-8000", "The sketch", "Unidentified sketch mentioned in note 2."),
    (NOTES, 437, "fresco-sketch-referent", "cand-7989", "this fresco", "Footnote follows Plate 39 and likely refers to the Venus and Adonis ceiling scene; scope remains provisional."),
    (NOTES, 437, "orleans-museum", "cand-7999", "Orleans Museum", "Holding institution as reported in the 1980 source; not checked as current custody."),
    (NOTES, 438, "fogolari", "cand-7894", "Fogolari", "Cited publication candidate already used for the 1937 volume."),
    (NOTES, 438, "letter106", "cand-8006", "Letter 106", "Specific letter locator, dated 3 April 1705."),
    (NOTES, 438, "pictures-letter106", "cand-8007", "the pictures in question", "Pictures mentioned in the cited letter; Haskell leaves Ricci’s authorship uncertain."),
    (NOTES, 438, "ricci-letter106", "cand-2179", "Ricci", "Artist whose possible authorship is explicitly left uncertain."),
    (NOTES, 438, "inventory1716", "cand-7936", "The 1716 inventory", "Reuse the existing inventory candidate; date range and source caveat remain as recorded there."),
    (NOTES, 438, "architectural-painting", "cand-8008", "an architectural painting", "Painting described in the inventory note."),
    (NOTES, 438, "saluzzi", "cand-2346", "Saluzzi", "Index candidate at p.236n; the footnote gives no first name."),
    (NOTES, 438, "ricci-figures", "cand-2179", "Sebastiano Ricci", "Painter of figures according to the inventory as reported by Haskell."),
    (NOTES, 438, "pinacoteca", "cand-8009", "Pinacoteca", "Institution named as the painting’s location."),
    (NOTES, 438, "lucca", "cand-1454", "Lucca", "City where the Pinacoteca is located."),
    (NOTES, 438, "painting-pronoun", "cand-8008", "It", "Coreference to the architectural painting."),
]
for spec in mention_specs:
    mention(*spec)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 236,
        "pdf_physical_page": 42, "claim": claim, "speaker": "Haskell",
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote(segment_id, first, last), "origin": "book",
            "source_file": meta["source_file"]}


new_statements = [
    make_statement(
        "st-chp8-p236-ferdinand-collaboration-in-pitti-work", P236, 304, 304,
        "cand-1609", "cand-7967", "collaborated_extensively_in_decoration",
        "Haskell argues that Ferdinand must have collaborated extensively in Ricci’s Pitti decoration. He adds that a later writer who knew Ricci said Ricci followed specific instructions from the Grand Prince.",
        "The first clause is Haskell’s inference, not a surviving record of the instructions. The cited writer is identified only in footnote 1; that report is separately recorded and linked.",
        ["cand-1609", "cand-7967", "cand-2179"],
        extras={"relation_candidate": True, "linked_note_statement_ids": ["st-chp8-p236-note1-gherardi-report"]}),
    make_statement(
        "st-chp8-p236-ricci-frescoes-and-court-atmosphere", P236, 304, 304,
        "cand-7967", "cand-8010", "interpreted_as_reflecting_court_atmosphere",
        "Haskell presents Ricci’s Pitti frescoes as a new departure that reflects the more lighthearted and avant-garde atmosphere of Ferdinand’s court, and reads the Prince’s character as symbolizing a change between centuries.",
        "This is Haskell’s interpretation. The statements about the new century are not treated as independently established historical facts.",
        ["cand-7967", "cand-2179", "cand-8010", "cand-1609"],
        extras={"relation_candidate": False, "ocr_corrections": [
            {"source_line": 304, "ocr": "avantgarde", "print": "avant-garde", "basis": "CHP-8.pdf physical page 42"}]}),
    make_statement(
        "st-chp8-p236-style-contrast-with-earlier-work", P236, 304, 305,
        "cand-7967", "cand-4723", "contrasted_with_heavy_baroque_ceiling_decoration",
        "Haskell contrasts the Pitti decoration’s delicacy and lightness with the heavy drama and solid figures of Baroque ceiling decoration, including Ricci’s earlier work and his nearly contemporary work at Palazzo Marucelli.",
        "The comparison is Haskell’s formal analysis. The p.236 reference to Palazzo Marucelli is linked to the existing indexed place and p.235 group-work candidate without asserting that every work in the group is the specific comparison.",
        ["cand-7967", "cand-4723", "cand-2179", "cand-1558", "cand-7966"],
        extras={"relation_candidate": False, "ocr_corrections": [
            {"source_line": 305, "ocr": "ofsun", "print": "of sun", "basis": "CHP-8.pdf physical page 42"},
            {"source_line": 305, "ocr": "air��a", "print": "air—a", "basis": "CHP-8.pdf physical page 42"}]}),
    make_statement(
        "st-chp8-p236-ceiling-venus-adonis-scene", P236, 305, 306,
        "cand-7967", "cand-7989", "contains_ceiling_scene_of_venus_and_adonis",
        "The ceiling is described as a pale blue sky with pink clouds, showing Venus taking leave of Adonis; putti and two greyhounds appear below, and the lovers’ look is described without a hint of coming tragedy.",
        "The scene is identified by its described subject rather than a separate title. Greyhounds and putti are recorded as image content, not promoted to independent entities. The footnote marker after Plate 39 is read as note 2.",
        ["cand-7967", "cand-7989", "cand-4171", "cand-4172"],
        extras={"relation_candidate": True, "ocr_corrections": [
            {"source_line": 306, "ocr": "Plate 39)?", "print": "Plate 39).²", "basis": "CHP-8.pdf physical page 42"}]}),
    make_statement(
        "st-chp8-p236-wall-scene-diana-callisto", P236, 306, 307,
        "cand-7967", "cand-7990", "includes_wall_scene",
        "Haskell names a wall scene of Diana and Callisto among the further scenes from Ovid in the Pitti decoration.",
        "The work is a scene within the larger decoration; the named figures remain distinct candidates. The source does not give a separate title.",
        ["cand-7967", "cand-7990", "cand-6777", "cand-4136", "cand-7994"],
        extras={"relation_candidate": True, "text_layer": "body and continued line"}),
    make_statement(
        "st-chp8-p236-wall-scene-pan-syrinx", P236, 306, 307,
        "cand-7967", "cand-7991", "includes_wall_scene",
        "Haskell names a wall scene of Pan and Syrinx among the further scenes from Ovid in the Pitti decoration.",
        "The name begins at L306 and continues at L307; the work is a scene within the larger decoration and is not given a separate title.",
        ["cand-7967", "cand-7991", "cand-6777", "cand-4169", "cand-4170"],
        extras={"relation_candidate": True, "text_layer": "body and continued line"}),
    make_statement(
        "st-chp8-p236-wall-scene-europa-bull", P236, 307, 307,
        "cand-7967", "cand-7992", "includes_wall_scene",
        "Haskell names a wall scene of Europa and the Bull among the further scenes from Ovid in the Pitti decoration.",
        "The Bull is not identified further and is not mapped to Zeus or another named figure.",
        ["cand-7967", "cand-7992", "cand-6777", "cand-4168"],
        extras={"relation_candidate": True}),
    make_statement(
        "st-chp8-p236-wall-scene-diana-actaeon", P236, 307, 307,
        "cand-7967", "cand-7993", "includes_wall_scene",
        "Haskell names a wall scene of Diana and Actaeon among the further scenes from Ovid in the Pitti decoration.",
        "The work is a scene within the larger decoration; the named figures remain distinct candidates and the source gives no separate title.",
        ["cand-7967", "cand-7993", "cand-6777", "cand-4136", "cand-7995"],
        extras={"relation_candidate": True}),
    make_statement(
        "st-chp8-p236-corner-busts", P236, 307, 307,
        "cand-7967", "cand-7996", "includes_corner_busts",
        "The decoration includes painted busts of unnamed men and women in the four corners, vaguely evoking the antique.",
        "The sitters are not identified; no named antique figure is inferred.",
        ["cand-7967", "cand-7996"], extras={"relation_candidate": True}),
    make_statement(
        "st-chp8-p236-overdoor-composition", P236, 307, 307,
        "cand-7967", "cand-7997", "includes_overdoor_medici_heraldic_composition",
        "Above the main door, angels support a shield bearing the Medici arms while putti with a crown hover above, forming an asymmetrical composition.",
        "The passage describes iconography in the room; it does not identify individual angels or putti.",
        ["cand-7967", "cand-7997", "cand-7998"], extras={"relation_candidate": True}),
    make_statement(
        "st-chp8-p236-rococo-style-and-reception", P236, 307, 308,
        "cand-7967", "cand-8004", "described_as_new_to_florence_and_of_limited_future_in_italy",
        "Haskell says the frescoes’ fluent manner was entirely new to Florence and European art, that Ferdinand delighted in them, and that their intimate Rococo style would become popular in Parisian boudoirs but had little future in Italy.",
        "This is Haskell’s stylistic and reception assessment. The page image corrects the OCR ‘suture’ to ‘future’; this is not an independently verified prediction about later Italian art.",
        ["cand-7967", "cand-8004", "cand-8011", "cand-1609", "cand-3397", "cand-4653", "cand-3461"],
        extras={"relation_candidate": False, "ocr_corrections": [
            {"source_line": 308, "ocr": "little suture in Italy", "print": "little future in Italy", "basis": "CHP-8.pdf physical page 42"}]}),
    make_statement(
        "st-chp8-p236-ricci-small-figure-pictures", P236, 309, 309,
        "cand-2179", "cand-8001", "painted_small_figure_pictures_for_ferdinand",
        "Haskell says Ricci painted various pictures for Ferdinand, especially scenes of little figures against architectural backgrounds usually painted by a collaborator; a letter quotation records Ricci’s approval of one pair, and Haskell says this kind of macchiette later became popular.",
        "The collaborators and the pair of pictures are not identified. The final clause beginning ‘Ricci wrote again ... after’ is incomplete at the page break and is not converted into a completed claim here. Italian accents, quotation marks, and the page’s footnote marker 3 are corrected against the scan.",
        ["cand-2179", "cand-8001", "cand-1609", "cand-8003", "cand-8002"],
        extras={"relation_candidate": True, "ocr_corrections": [
            {"source_line": 309, "ocr": "replacement glyphs around quoted text; perche", "print": "taste—‘le figurette ... poco’; perchè", "basis": "CHP-8.pdf physical page 42"}]}),
    make_statement(
        "st-chp8-p236-note1-gherardi-publication", NOTES, 436, 436,
        None, "cand-8005", "footnote_cites_gherardi_account_about_smith_pictures",
        "Haskell identifies Abate Gherardi as the author of an anonymous account published in 1749 about some of Consul Smith’s pictures in Venice.",
        "The account’s exact title and the cited page were not independently consulted. The source’s indexed name forms for Gherardi and Smith are retained without S3 identity resolution.",
        ["cand-1155", "cand-8005", "cand-2440", "cand-3401"],
        text_layer="footnote citation and report",
        extras={"relation_candidate": False, "linked_body_statement_ids": ["st-chp8-p236-ferdinand-collaboration-in-pitti-work"],
                "ocr_corrections": [
                    {"source_line": 436, "ocr": "footnote marker 3", "print": "footnote marker 1", "basis": "CHP-8.pdf physical page 42"}]}),
    make_statement(
        "st-chp8-p236-note1-gherardi-report", NOTES, 436, 436,
        "cand-2179", "cand-1609", "followed_specific_instructions_for_decoration",
        "In the passage quoted by Haskell, Gherardi says Ricci learned the Grand Prince’s wishes for the proposed work, followed them, completed the work promptly, and received payment and gifts that showed Ferdinand’s satisfaction.",
        "This is Gherardi’s report as quoted through Haskell, not an independently checked account. The unnamed ‘work’ is linked to the immediately preceding Pitti decoration context with that scope stated as contextual.",
        ["cand-1155", "cand-2179", "cand-1609", "cand-7967", "cand-3397"],
        text_layer="footnote nested quotation",
        extras={"relation_candidate": True, "quoted_speaker": "Abate Gherardi",
                "linked_body_statement_ids": ["st-chp8-p236-ferdinand-collaboration-in-pitti-work"]}),
    make_statement(
        "st-chp8-p236-note2-sketch-at-orleans", NOTES, 437, 437,
        "cand-8000", "cand-7999", "sketch_reported_at_orleans_museum",
        "Haskell’s note says that the sketch for the fresco is at the Orleans Museum.",
        "The note follows Plate 39 and likely refers to the Venus and Adonis ceiling scene, but the sketch’s exact scope and current custody are not independently established.",
        ["cand-8000", "cand-7999", "cand-7989"],
        text_layer="footnote report",
        extras={"relation_candidate": True, "linked_body_statement_ids": ["st-chp8-p236-ceiling-venus-adonis-scene"]}),
    make_statement(
        "st-chp8-p236-note3-letter106-attribution-uncertain", NOTES, 438, 438,
        "cand-8006", "cand-8007", "cites_pictures_with_ricci_attribution_uncertain",
        "Haskell cites Fogolari’s 1937 Letter 106 of 3 April 1705 and says it is unclear whether the pictures referred to there were by Ricci.",
        "The letter and Fogolari edition were not independently consulted; the uncertainty is preserved rather than assigning the pictures to Ricci.",
        ["cand-7894", "cand-8006", "cand-8007", "cand-2179"],
        text_layer="footnote report and citation",
        extras={"relation_candidate": False, "linked_body_statement_ids": ["st-chp8-p236-ricci-small-figure-pictures"]}),
    make_statement(
        "st-chp8-p236-note3-saluzzi-painting-at-lucca", NOTES, 438, 438,
        "cand-7936", "cand-8008", "inventory_describes_architectural_painting_and_lucca_location",
        "Haskell says the 1716 inventory describes an architectural painting by Saluzzi with figures by Sebastiano Ricci; he locates it at the Pinacoteca in Lucca and says it is initialled and dated 1706.",
        "This is Haskell’s report of the inventory and location. The inventory, painting, and present holding were not independently checked; this object is not identified with the uncertain pictures in Letter 106.",
        ["cand-7936", "cand-8008", "cand-2346", "cand-2179", "cand-8009", "cand-1454"],
        text_layer="footnote report",
        extras={"relation_candidate": True, "linked_body_statement_ids": ["st-chp8-p236-ricci-small-figure-pictures"]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")

for row in coverage_rows:
    if row["segment_id"] == P236:
        row.update({
            "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L303-309",
            "note": "p.236 body reviewed against CHP-8.pdf physical page 42; OCR corrections are recorded in S2 qualifiers. L309 ends with 'after' and continues at p.237 L312-313, so the segment remains partial.",
        })
    elif row["segment_id"] == NOTES:
        row.update({
            "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L373-438",
            "note": "Consolidated footnotes reviewed through p.236 note 3 at L438; notes 1-3 link to the p.236 body. Remaining consolidated notes L439-461 are queued for sequential review.",
        })

preview = {
    "mode": "dry-run",
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage_updates": {P236: "L303-309 partial", NOTES: "L373-438 partial; L439-461 remain"},
    "print_corrections": [
        "L304 avantgarde -> avant-garde",
        "L305 ofsun -> of sun; air��a -> air—a",
        "L306 footnote marker after Plate 39 -> note 2",
        "L308 little suture -> little future",
        "L436 OCR footnote marker 3 -> printed note 1",
        "L309 restore Italian quote punctuation and accent; note marker is printed as superscript 3",
    ],
    "ambiguities_preserved": [
        "Gherardi and Consul Smith identity matches remain at their indexed candidate entries for S3",
        "the exact scope of the sketch in note 2",
        "authorship of pictures cited by Fogolari Letter 106",
        "the painting in the 1716 inventory is not equated with the uncertain Letter 106 pictures",
        "Ricci's page-end 1708 sentence remains open to p.237",
    ],
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    raise SystemExit(0)

paths = (TABLES / "entity-candidates.csv", TABLES / "mentions.csv",
         TABLES / "book-statements.jsonl", TABLES / "s2-coverage.csv")
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv_atomic(TABLES / "entity-candidates.csv", candidate_fields, candidate_rows)
write_csv_atomic(TABLES / "mentions.csv", mention_fields, mention_rows + new_mentions)
write_jsonl_atomic(TABLES / "book-statements.jsonl", statement_rows + new_statements)
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, coverage_rows)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=True, indent=2))
