"""Controlled S2 migration for chapter 10 Plates 49–52; defaults to dry-run."""
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
OCR_FILE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
VISUAL_FILE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro_plates_visual-transcription.md"
OCR_SEGMENTS = {
    "chp-10:10_CHP-10_intro:l63-89": "22c9dddb1063ee6d45fffd656824e1a414e9f78ee82bdb4f93a7a3879d325a77",
    "chp-10:10_CHP-10_intro:l91-112": "997e03e9074203c1c8b25476a48aac1dcce9493ef063677ee199fac27429162b",
    "chp-10:10_CHP-10_intro:l114-119": "8d034aa91d98cdee1e3921102d11a4fe1cd61d4534e11d5e3d3f34b208dbc66f",
    "chp-10:10_CHP-10_intro:l121-123": "90f8ad2291e878358861e1beabb3abcbf8acf9f6d6292236cfc1446677ebd1ba",
}
VISUAL_SEGMENTS = {
    "chp-10:10_CHP-10_intro_plates_visual-transcription:l1-4": ("78005ac3dc55c38003c3bb8df10a7c954400d4df4cb461baec2e541a2010fa81", 1, 4),
    "chp-10:10_CHP-10_intro_plates_visual-transcription:l6-7": ("8b5da96e5d594df1f63ff675f5f1af82f39fa80fd05f357957aa87c42a7bbe0a", 6, 7),
    "chp-10:10_CHP-10_intro_plates_visual-transcription:l9-10": ("29a283034c5843e85df456fd77705216dd5fc3c68a09ddb53361bf7b26385450", 9, 10),
    "chp-10:10_CHP-10_intro_plates_visual-transcription:l12-15": ("db336a4bc83a676c21911c5d4972f214ab073ef15069d208aaf4cf8a537cdfee", 12, 15),
}
EXPECTED_VISUAL_ASSET = "163e94e2ebaad7cdd6a5bc2e57842103749ddb37f410af0fabfad3a4ea5e2e65"
EXPECTED_TRANSCRIPTION = [
    "Venetian artists in Germany and England in the first half of the eighteenth century",
    "Plate 49",
    "a. Pellegrini: Allegory of the Education of the Crown Prince of the Palatinate",
    "b. Amigoni: Jupiter and Io at Moor Park",
    "",
    "Venetian artists in Germany and England in the middle of the eighteenth century (see Plates 50 and 51)",
    "Plate 50",
    "",
    "Plate 51",
    "Canaletto: View from Badminton, 1748",
    "",
    "OWEN McSWINY AND HIS PATRONAGE",
    "Plate 52",
    "b. Canaletto, Cimaroli, and Pittoni: Allegorical tomb to the memory of Archbishop Tillotson",
    "a. P. van Bleek: Detail from portrait of Owen McSwiney",
]
BACKUP_SUFFIX = ".bak-s2-chp10-plates49-52-20261002"


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(VISUAL_FILE.read_bytes()).hexdigest() != EXPECTED_VISUAL_ASSET:
    raise SystemExit("Plate 49–52 visual-transcription asset changed")
visual_lines = VISUAL_FILE.read_text(encoding="utf-8-sig").splitlines()
if visual_lines != EXPECTED_TRANSCRIPTION:
    raise SystemExit("Plate 49–52 visual transcription differs from the reviewed print captions")
ocr_lines = OCR_FILE.read_text(encoding="utf-8-sig").splitlines()
segments_path = TABLES / "segments.jsonl"
segment_meta = {row["segment_id"]: row for row in read_jsonl(segments_path)}
for segment_id, expected_hash in OCR_SEGMENTS.items():
    if segment_meta.get(segment_id, {}).get("sha256") != expected_hash:
        raise SystemExit(f"chapter 10 OCR segment changed: {segment_id}")
for segment_id, (expected_hash, start, end) in VISUAL_SEGMENTS.items():
    meta = segment_meta.get(segment_id)
    if not meta or meta.get("sha256") != expected_hash or meta.get("asset_sha256") != EXPECTED_VISUAL_ASSET:
        raise SystemExit(f"visual transcription segment changed: {segment_id}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
_, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidates}
required_candidates = {
    "cand-4072", "cand-3859", "cand-4177", "cand-3947", "cand-4000", "cand-3717",
    "cand-4178", "cand-4179", "cand-3939", "cand-4015", "cand-3738", "cand-3903",
    "cand-3853", "cand-4070", "cand-3854", "cand-4012", "cand-3748", "cand-3870", "cand-3726",
}
if not required_candidates <= candidate_ids:
    raise SystemExit(f"required existing caption candidates missing: {required_candidates - candidate_ids}")

coverage_by_id = {row["segment_id"]: row for row in coverage}
for segment_id in OCR_SEGMENTS:
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != ("queued", "pending", ""):
        raise SystemExit(f"unexpected Plate 49–52 OCR coverage: {row}")
for segment_id in VISUAL_SEGMENTS:
    if segment_id in coverage_by_id:
        raise SystemExit(f"Plate 49–52 visual coverage already exists: {segment_id}")

crossrefs = {
    49: [{"segment_id": "front-matter:00_05_List_of_Plates:l123-138", "source_line_start": 127, "source_line_end": 127}],
    51: [{"segment_id": "front-matter:00_05_List_of_Plates:l123-138", "source_line_start": 129, "source_line_end": 129}],
    52: [{"segment_id": "front-matter:00_05_List_of_Plates:l123-138", "source_line_start": 130, "source_line_end": 130}],
}
segment_bounds = {segment_id: (start, end) for segment_id, (_, start, end) in VISUAL_SEGMENTS.items()}
new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mentions}


def add_mention(mention_id, segment_id, candidate_id, surface, source_line, note):
    if mention_id in existing_mention_ids:
        raise SystemExit(f"duplicate mention id: {mention_id}")
    start_line, end_line = segment_bounds[segment_id]
    if not start_line <= source_line <= end_line:
        raise SystemExit(f"mention line outside segment: {mention_id}")
    line = visual_lines[source_line - 1]
    local = line.find(surface)
    if local < 0 or line.find(surface, local + len(surface)) >= 0:
        raise SystemExit(f"surface missing or ambiguous: {mention_id} / {surface}")
    offset = sum(len(item) + 1 for item in visual_lines[start_line - 1:source_line - 1]) + local
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(offset),
        "end_char": str(offset + len(surface)),
        "note": note,
    })
    existing_mention_ids.add(mention_id)


plate49 = "chp-10:10_CHP-10_intro_plates_visual-transcription:l1-4"
plate51 = "chp-10:10_CHP-10_intro_plates_visual-transcription:l9-10"
plate52 = "chp-10:10_CHP-10_intro_plates_visual-transcription:l12-15"
for args in [
    ("m-chp10-p49a-work", plate49, "cand-4072", "Allegory of the Education of the Crown Prince of the Palatinate", 3, "Printed Plate 49a title; reuse the existing index-derived work candidate."),
    ("m-chp10-p49a-artist", plate49, "cand-3859", "Pellegrini", 3, "Printed attribution; global identity and attribution alignment remain for S3."),
    ("m-chp10-p49a-prince", plate49, "cand-4177", "Crown Prince of the Palatinate", 3, "Title-only subject; retain unresolved identity and do not infer which prince."),
    ("m-chp10-p49a-territory", plate49, "cand-3947", "Palatinate", 3, "Place name occurs in the work title; it is not a sitter or a current location claim."),
    ("m-chp10-p49b-work", plate49, "cand-4000", "Jupiter and Io", 4, "Printed Plate 49b title; reuse the existing index-derived work candidate."),
    ("m-chp10-p49b-artist", plate49, "cand-3717", "Amigoni", 4, "Printed attribution; global identity and attribution alignment remain for S3."),
    ("m-chp10-p49b-jupiter", plate49, "cand-4178", "Jupiter", 4, "Mythological figure named in the title; not a historical event claim."),
    ("m-chp10-p49b-io", plate49, "cand-4179", "Io", 4, "Mythological figure named in the title; not a historical event claim."),
    ("m-chp10-p49b-moor-park", plate49, "cand-3939", "Moor Park", 4, "Place association in the printed title; do not infer a commission or ownership."),
    ("m-chp10-p51-work", plate51, "cand-4015", "View from Badminton, 1748", 10, "Printed Plate 51 title; retain the caption wording as a source-specific work label."),
    ("m-chp10-p51-artist", plate51, "cand-3738", "Canaletto", 10, "Printed attribution; global identity and attribution alignment remain for S3."),
    ("m-chp10-p51-site", plate51, "cand-3903", "Badminton", 10, "Place named in the view title; do not infer a collection or commission."),
    ("m-chp10-p52-heading-owen", plate52, "cand-3853", "OWEN McSWINY", 12, "Named person in an editorial plate-group heading; no patronage relation is derived from the heading."),
    ("m-chp10-p52b-work", plate52, "cand-4012", "Allegorical tomb to the memory of Archbishop Tillotson", 14, "Printed Plate 52b caption; reuse the existing index-derived work candidate."),
    ("m-chp10-p52b-artist-canaletto", plate52, "cand-3738", "Canaletto", 14, "Printed attribution in the multi-artist caption; no individual role beyond attribution is inferred."),
    ("m-chp10-p52b-artist-cimaroli", plate52, "cand-3748", "Cimaroli", 14, "Printed attribution in the multi-artist caption; no individual role beyond attribution is inferred."),
    ("m-chp10-p52b-artist-pittoni", plate52, "cand-3870", "Pittoni", 14, "Printed attribution in the multi-artist caption; no individual role beyond attribution is inferred."),
    ("m-chp10-p52b-tillotson", plate52, "cand-3726", "Archbishop Tillotson", 14, "The caption states a commemorative subject, not the existence of a tomb building."),
    ("m-chp10-p52a-work", plate52, "cand-4070", "portrait of Owen McSwiney", 15, "The caption describes a detail from a portrait; preserve this printed spelling variant for S3 review."),
    ("m-chp10-p52a-artist", plate52, "cand-3854", "P. van Bleek", 15, "Printed attribution; global identity and attribution alignment remain for S3."),
    ("m-chp10-p52a-sitter", plate52, "cand-3853", "Owen McSwiney", 15, "Printed spelling differs from the plate-list form McSwiny; preserve the variant for S3 review."),
]:
    add_mention(*args)

new_statements = []
existing_statement_ids = {row["statement_id"] for row in statements}


def add_statement(statement_id, segment_id, source_line, plate_number, work_id, object_id, predicate, claim, qualification, mentioned, quote, crossref_segment=None, crossref_line=None, extra=None):
    if statement_id in existing_statement_ids:
        raise SystemExit(f"duplicate statement id: {statement_id}")
    refs = [work_id] + ([object_id] if object_id else []) + list(mentioned)
    if not set(refs) <= candidate_ids:
        raise SystemExit(f"statement foreign key missing: {statement_id}")
    expected_quote = visual_lines[source_line - 1]
    if quote != expected_quote:
        raise SystemExit(f"statement quote does not match printed transcription: {statement_id}")
    qualifiers = {
        "source_line_start": source_line,
        "source_line_end": source_line,
        "plate_number": plate_number,
        "pdf_physical_page": {49: 6, 50: 7, 51: 8, 52: 9}[plate_number],
        "claim": claim,
        "speaker": "printed plate caption",
        "text_layer": "visual transcription",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(refs)),
        "relation_candidate": True,
    }
    if crossref_segment and crossref_line:
        qualifiers["cross_reference_segments"] = [{"segment_id": crossref_segment, "source_line_start": crossref_line, "source_line_end": crossref_line}]
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": work_id,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "source_file": VISUAL_FILE.relative_to(ROOT).as_posix(),
        "origin": "book",
    })
    existing_statement_ids.add(statement_id)


add_statement("st-chp10-p49a-attribution", plate49, 3, 49, "cand-4072", "cand-3859", "caption_attribution", "The Plate 49a caption credits Pellegrini with Allegory of the Education of the Crown Prince of the Palatinate.", "This records the printed caption attribution only; no external attribution or identity judgment is added.", ["cand-3859", "cand-4177", "cand-3947"], visual_lines[2], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=127)
add_statement("st-chp10-p49a-subject", plate49, 3, 49, "cand-4072", "cand-4177", "caption_iconographic_subject", "The Plate 49a title names the Crown Prince of the Palatinate as the subject of the allegory.", "The caption supplies a title, not the prince's personal identity; do not infer which member of the Palatinate dynasty is meant.", ["cand-3859", "cand-4177", "cand-3947"], visual_lines[2], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=127)
add_statement("st-chp10-p49a-title-context", plate49, 3, 49, "cand-4072", "cand-3947", "caption_title_context", "The Plate 49a title places the Crown Prince in the Palatinate context.", "The place name occurs in the title and is not evidence of a specific territory, court, or current location beyond that wording.", ["cand-3859", "cand-4177", "cand-3947"], visual_lines[2], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=127)
add_statement("st-chp10-p49b-attribution", plate49, 4, 49, "cand-4000", "cand-3717", "caption_attribution", "The Plate 49b caption credits Amigoni with Jupiter and Io at Moor Park.", "This records the printed caption attribution only; it does not infer commission or ownership.", ["cand-3717", "cand-4178", "cand-4179", "cand-3939"], visual_lines[3], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=127)
add_statement("st-chp10-p49b-jupiter", plate49, 4, 49, "cand-4000", "cand-4178", "caption_iconographic_subject", "The Plate 49b title names Jupiter as an iconographic subject.", "Mythological subject identification follows the printed title; it does not document a historical event.", ["cand-3717", "cand-4178", "cand-4179", "cand-3939"], visual_lines[3], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=127)
add_statement("st-chp10-p49b-io", plate49, 4, 49, "cand-4000", "cand-4179", "caption_iconographic_subject", "The Plate 49b title names Io as an iconographic subject.", "Mythological subject identification follows the printed title; it does not document a historical event.", ["cand-3717", "cand-4178", "cand-4179", "cand-3939"], visual_lines[3], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=127)
add_statement("st-chp10-p49b-place", plate49, 4, 49, "cand-4000", "cand-3939", "caption_location_or_collection", "The Plate 49b title associates Jupiter and Io with Moor Park.", "The title gives a place association but does not establish a commission, ownership, or current custody.", ["cand-3717", "cand-4178", "cand-4179", "cand-3939"], visual_lines[3], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=127)

add_statement("st-chp10-p51-attribution", plate51, 10, 51, "cand-4015", "cand-3738", "caption_attribution", "The Plate 51 caption credits Canaletto with View from Badminton, 1748.", "This records the printed caption attribution only; no external attribution judgment is added.", ["cand-3738", "cand-3903"], visual_lines[9], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=129)
add_statement("st-chp10-p51-viewpoint", plate51, 10, 51, "cand-4015", "cand-3903", "caption_location_or_collection", "The Plate 51 title names Badminton in the view title.", "Badminton is preserved as the title's place reference; the caption does not name a collection or prove a commission.", ["cand-3738", "cand-3903"], visual_lines[9], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=129)
add_statement("st-chp10-p51-caption-date", plate51, 10, 51, "cand-4015", None, "caption_view_date", "The Plate 51 caption attaches the year 1748 to View from Badminton.", "The printed year is retained as a caption date; it is not independently established as the work's execution date.", ["cand-3738", "cand-3903"], visual_lines[9], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=129, extra={"date_as_printed": "1748"})

add_statement("st-chp10-p52b-attribution-canaletto", plate52, 14, 52, "cand-4012", "cand-3738", "caption_attribution", "The Plate 52b caption names Canaletto as one of three painters credited with the allegorical tomb to the memory of Archbishop Tillotson.", "All three artists are retained as caption attributions; the caption does not allocate separate parts among them.", ["cand-3738", "cand-3748", "cand-3870", "cand-3726"], visual_lines[13], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=130)
add_statement("st-chp10-p52b-attribution-cimaroli", plate52, 14, 52, "cand-4012", "cand-3748", "caption_attribution", "The Plate 52b caption names Cimaroli as one of three painters credited with the allegorical tomb to the memory of Archbishop Tillotson.", "All three artists are retained as caption attributions; the caption does not allocate separate parts among them.", ["cand-3738", "cand-3748", "cand-3870", "cand-3726"], visual_lines[13], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=130)
add_statement("st-chp10-p52b-attribution-pittoni", plate52, 14, 52, "cand-4012", "cand-3870", "caption_attribution", "The Plate 52b caption names Pittoni as one of three painters credited with the allegorical tomb to the memory of Archbishop Tillotson.", "All three artists are retained as caption attributions; the caption does not allocate separate parts among them.", ["cand-3738", "cand-3748", "cand-3870", "cand-3726"], visual_lines[13], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=130)
add_statement("st-chp10-p52b-memorial-subject", plate52, 14, 52, "cand-4012", "cand-3726", "caption_iconographic_subject", "The Plate 52b caption says the allegorical tomb commemorates Archbishop Tillotson.", "The caption identifies a memorial subject; it does not establish that the pictured tomb is a real building or identify its location.", ["cand-3738", "cand-3748", "cand-3870", "cand-3726"], visual_lines[13], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=130)

add_statement("st-chp10-p52a-attribution", plate52, 15, 52, "cand-4070", "cand-3854", "caption_attribution", "The Plate 52a caption credits P. van Bleek with the pictured detail from a portrait of Owen McSwiney.", "The wording describes a detail from a portrait rather than supplying a formal title; retain the printed spelling variant for identity review.", ["cand-3854", "cand-3853"], visual_lines[14], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=130)
add_statement("st-chp10-p52a-sitter", plate52, 15, 52, "cand-4070", "cand-3853", "caption_subject", "The Plate 52a caption identifies Owen McSwiney as the subject of the portrait from which the detail is taken.", "The plate prints McSwiney, while the plate list gives McSwiny; preserve both source forms and defer identity alignment to S3.", ["cand-3854", "cand-3853"], visual_lines[14], crossref_segment="front-matter:00_05_List_of_Plates:l123-138", crossref_line=130)

ocr_notes = {
    "chp-10:10_CHP-10_intro:l63-89": "no_semantic_content: rotated Plate 49 OCR is reversed/corrupt; inspected CHP-10.pdf physical p.6 and represented the printed heading and captions in derived visual transcription segments l1-4. OCR and PDF remain unchanged.",
    "chp-10:10_CHP-10_intro:l91-112": "no_semantic_content: rotated Plate 50 OCR is reversed/truncated; inspected CHP-10.pdf physical p.7 and represented its editorial grouping title in derived visual transcription l6-7. The image has no independent caption; do not infer a work from the image.",
    "chp-10:10_CHP-10_intro:l114-119": "no_semantic_content: rotated Plate 51 OCR is reversed; inspected CHP-10.pdf physical p.8 and represented the printed caption in derived visual transcription l9-10. OCR and PDF remain unchanged.",
    "chp-10:10_CHP-10_intro:l121-123": "no_semantic_content: Plate 52 OCR reverses caption order and runs lines together; inspected CHP-10.pdf physical p.9 and represented the printed heading and captions in derived visual transcription l12-15. OCR and PDF remain unchanged.",
}
for segment_id, note in ocr_notes.items():
    row = coverage_by_id[segment_id]
    row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L" + segment_id.rsplit("l", 1)[1], "note": note})

visual_notes = {
    "chp-10:10_CHP-10_intro_plates_visual-transcription:l1-4": "Printed Plate 49 heading and captions inspected on CHP-10.pdf physical p.6. The grouping title is editorial navigation; statements capture only captioned works, artists, named subject/title context, mythological subjects, and place wording. The repeated plate-list entry at L127 is cross-referenced; no commission, ownership, or external attribution is inferred.",
    "chp-10:10_CHP-10_intro_plates_visual-transcription:l6-7": "no_semantic_content: Printed Plate 50 grouping title and plate number inspected on CHP-10.pdf physical p.7. The grouping is editorial navigation; the image itself has no independent caption. Work identity and description remain in the already processed Plate 50 list entry at L128; no visual inference is added.",
    "chp-10:10_CHP-10_intro_plates_visual-transcription:l9-10": "Printed Plate 51 caption inspected on CHP-10.pdf physical p.8. Reuses the existing caption work, artist, and Badminton candidates and records the printed 1748 with a qualification; cross-references the plate-list entry at L129.",
    "chp-10:10_CHP-10_intro_plates_visual-transcription:l12-15": "Printed Plate 52 heading and captions inspected on CHP-10.pdf physical p.9. The heading yields only a person mention, not a patronage claim. Captions preserve all three attributions to Plate 52b and the memorial subject; the Plate 52a spelling McSwiney is retained beside plate-list form McSwiny for S3 review. Cross-references the plate-list entry at L130.",
}
for segment_id, (_, start, end) in VISUAL_SEGMENTS.items():
    chapter, note = "chp-10", visual_notes[segment_id]
    row = {"chapter": chapter, "segment_id": segment_id, "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": f"L{start}-{end}", "note": note}
    coverage.append(row)
    coverage_by_id[segment_id] = row

all_mentions = mentions + new_mentions
all_statements = statements + new_statements
required_foreign_keys = candidate_ids
for row in new_mentions:
    if row["candidate_id"] not in required_foreign_keys:
        raise SystemExit(f"mention foreign key missing: {row['mention_id']}")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
print(json.dumps({
    "mode": "APPLY" if args.apply else "DRY-RUN",
    "ocr_segments_completed": len(OCR_SEGMENTS),
    "visual_segments_added": len(VISUAL_SEGMENTS),
    "new_candidates": 0,
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "next_narrative_segment": "chp-10:10_CHP-10_intro:l125-139",
}, ensure_ascii=True, indent=2))
if not args.apply:
    raise SystemExit(0)

for path in (mention_path, statement_path, coverage_path):
    backup = Path(str(path) + BACKUP_SUFFIX)
    if backup.exists():
        if hashlib.sha256(backup.read_bytes()).digest() != hashlib.sha256(path.read_bytes()).digest():
            raise SystemExit(f"existing recovery copy differs from the current source table: {backup}")
    else:
        shutil.copy2(path, backup)
write_csv(mention_path, mention_fields, all_mentions)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, coverage)
print("Applied chapter 10 Plates 49–52 S2 migration; backups retained.")
