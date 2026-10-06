"""Controlled S2 migration for chapter 13 Plate 57 captions; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
VISUAL = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro_plates_visual-transcription.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
ORIGINAL_SEGMENT = "chp-13:13_CHP-13_intro:l124-139"
VISUAL_SEGMENT = "chp-13:13_CHP-13_intro_plates_visual-transcription:l1-3"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
VISUAL_SHA = "e850d580c38fac4b1b81942181e3f9178edb4cd5895e8c898a233241fec4c0a6"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p344-plate57-final-20261003"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the reviewed Plate 57 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


def check_sha(path, expected, label):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"{label} SHA changed: {actual}")


check_sha(SOURCE, SOURCE_SHA, "canonical chapter 13 Markdown")
check_sha(VISUAL, VISUAL_SHA, "Plate 57 visual transcription")
check_sha(PDF, PDF_SHA, "registered CHP-13 PDF")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
segments = read_jsonl(segment_path)

state = (len(candidates), len(mentions), len(statements), len(coverage))
if state != (10100, 21796, 9724, 826):
    raise SystemExit(f"unexpected pre-state: candidates/mentions/statements/coverage={state}")
segment_by_id = {row["segment_id"]: row for row in segments}
if ORIGINAL_SEGMENT not in segment_by_id or VISUAL_SEGMENT not in segment_by_id:
    raise SystemExit("expected original or visual transcription segment is missing")
if segment_by_id[ORIGINAL_SEGMENT]["sha256"] != "e4d6fc61fc705a289b439ccfe51f5686f00912bbb41570cec66e44a2c9bcab7b":
    raise SystemExit("original Plate 57 OCR segment changed")
if segment_by_id[VISUAL_SEGMENT]["sha256"] != VISUAL_SHA:
    raise SystemExit("Plate 57 visual transcription segment changed")
coverage_by_id = {row["segment_id"]: row for row in coverage}
if ORIGINAL_SEGMENT not in coverage_by_id or coverage_by_id[ORIGINAL_SEGMENT]["disposition"] != "queued":
    raise SystemExit("original reversed OCR coverage row is not queued as expected")
if VISUAL_SEGMENT in coverage_by_id:
    raise SystemExit("Plate 57 visual transcription already has a coverage row")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
if "cand-10114" in candidate_by_id:
    raise SystemExit("cand-10114 already exists")
required_candidates = {"cand-0025", "cand-1205", "cand-1760", "cand-1844", "cand-1907", "cand-3602", "cand-4079", "cand-9990"}
if not required_candidates.issubset(candidate_by_id):
    raise SystemExit(f"required existing candidate missing: {sorted(required_candidates - candidate_by_id.keys())}")

visual_text = VISUAL.read_text(encoding="utf-8-sig")
visual_lines = visual_text.splitlines()
caption_a = visual_lines[1]
caption_b = visual_lines[2]
if not caption_a.startswith("a. PIAZZETTA:") or not caption_b.startswith("b. NOVELLI:"):
    raise SystemExit("visual transcription caption anchors changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
p335_lines = source_lines[31:39]
p335_text = "\n".join(p335_lines)
ref_start = p335_text.find("Plate 57a")
if ref_start < 0 or p335_text.find("Plate 57a", ref_start + 1) >= 0:
    raise SystemExit("expected unique p.335 Plate 57a cross-reference was not found")

new_candidate = {field: "" for field in candidate_fields}
new_candidate.update({
    "candidate_id": "cand-10114",
    "canonical_name": "Plate 57a: portraits of the artist and publisher Albrizzi (endpiece to Gerusalemme Liberata, 1745)",
    "suggested_type": "work",
    "status": "open",
    "detail": "A discrete endpiece identified by the printed Plate 57a caption. The caption describes portraits of the artist and his publisher Albrizzi and places the image in the 1745 Gerusalemme Liberata edition; it does not give an independent title.",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{VISUAL_SEGMENT}#L2",
})

mention_specs = [
    ("m-s2-ch13-p344-plate57-001", "cand-10114", "Portraits of the artist and his publisher Albrizzi", 23, 73, "Descriptive caption wording for the Plate 57a endpiece; not an independent printed title."),
    ("m-s2-ch13-p344-plate57-002", "cand-1907", "PIAZZETTA", 12, 21, "Printed artist attribution in the plate caption; identity remains subject to S3 alignment."),
    ("m-s2-ch13-p344-plate57-003", "cand-0025", "Albrizzi", 65, 73, "The caption identifies the artist's publisher as Albrizzi."),
    ("m-s2-ch13-p344-plate57-004", "cand-9990", "Gerusalemme Liberata", 86, 106, "The edition named in the Plate 57a caption."),
    ("m-s2-ch13-p344-plate57-005", "cand-1760", "NOVELLI", 116, 123, "Printed artist attribution in the Plate 57b caption; mapped to the chapter's recurring Novelli candidate pending S3."),
    ("m-s2-ch13-p344-plate57-006", "cand-4079", "frontispiece", 166, 178, "Caption identifies the existing Plate 57b frontispiece candidate."),
    ("m-s2-ch13-p344-plate57-007", "cand-1205", "Goldoni", 125, 132, "The caption describes a school episode involving Goldoni; it is an image description, not independent biographical evidence."),
    ("m-s2-ch13-p344-plate57-008", "cand-3602", "Vol. 2 of his works", 182, 201, "Goldoni's volume 2 edition identified by the caption."),
    ("m-s2-ch13-p344-plate57-009", "cand-1844", "Pasquali", 215, 223, "Publisher named in the Plate 57b caption; identity remains subject to S3 alignment."),
]
for mid, cid, surface, start, end, note in mention_specs:
    if mid in mention_ids or visual_text[start:end] != surface:
        raise SystemExit(f"mention anchor mismatch or duplicate: {mid}")
    if cid not in candidate_by_id and cid != "cand-10114":
        raise SystemExit(f"mention references missing candidate: {mid} {cid}")

ref_mid = "m-s2-ch13-p335-038"
if ref_mid in mention_ids or p335_text[ref_start:ref_start + len("Plate 57a")] != "Plate 57a":
    raise SystemExit("p.335 Plate 57a cross-reference mention collision")


def make_statement(statement_id, subject, object_id, predicate, line, quote, claim, qualification, mentioned, layer="plate caption"):
    return {
        "statement_id": statement_id,
        "segment_id": VISUAL_SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line,
            "source_line_end": line,
            "pdf_physical_page": 14,
            "plate_ref": "57a" if line == 2 else "57b",
            "claim": claim,
            "speaker": "printed plate caption",
            "text_layer": layer,
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro_plates_visual-transcription.md",
    }

new_statements = [
    make_statement("st-chp13-p344-plate57a-endpiece-in-edition", "cand-10114", "cand-9990", "caption_identifies_endpiece_of_edition", 2, caption_a, "The printed caption identifies the Plate 57a image as an endpiece to the 1745 Gerusalemme Liberata edition.", "The caption names the edition and year; this statement does not identify the source drawing among the approximately seventy drawings discussed on p.335.", ["cand-10114", "cand-9990"]),
    make_statement("st-chp13-p344-plate57a-attribution", "cand-10114", "cand-1907", "caption_attribution", 2, caption_a, "The printed caption attributes the endpiece to Piazzetta.", "Caption attribution only; no external attribution verification is implied.", ["cand-10114", "cand-1907"]),
    make_statement("st-chp13-p344-plate57a-depicts-piazzetta", "cand-10114", "cand-1907", "caption_depicts_person", 2, caption_a, "The caption describes the endpiece as including a portrait of the artist, understood from its attribution as Piazzetta.", "This is the caption's internal identification; it does not independently verify the sitter.", ["cand-10114", "cand-1907"]),
    make_statement("st-chp13-p344-plate57a-depicts-albrizzi", "cand-10114", "cand-0025", "caption_depicts_person", 2, caption_a, "The caption describes the endpiece as including a portrait of Piazzetta's publisher Albrizzi.", "The caption gives only the surname Albrizzi; the chapter candidate is reused pending S3 alignment.", ["cand-10114", "cand-1907", "cand-0025"]),
    make_statement("st-chp13-p344-plate57b-depicts-goldoni-at-school", "cand-4079", "cand-1205", "caption_depicts_episode", 3, caption_b, "The caption describes the frontispiece image as showing Goldoni passing his Latin examinations at school.", "This records the image caption, not independent proof of the biographical episode.", ["cand-4079", "cand-1205"]),
    make_statement("st-chp13-p344-plate57b-frontispiece-of-volume", "cand-4079", "cand-3602", "caption_identifies_frontispiece_of", 3, caption_b, "The caption identifies the image as the frontispiece to volume 2 of Goldoni's works.", "The caption calls the publication 'his works'; Goldoni is resolved from the sentence itself.", ["cand-4079", "cand-1205", "cand-3602"]),
    make_statement("st-chp13-p344-plate57b-attribution", "cand-4079", "cand-1760", "caption_attribution", 3, caption_b, "The printed caption attributes the frontispiece to Novelli.", "Caption attribution only; the surname form is retained and no external verification is implied.", ["cand-4079", "cand-1760"]),
    make_statement("st-chp13-p344-plate57b-publication-imprint", "cand-3602", "cand-1844", "caption_bibliographic_imprint", 3, caption_b, "The caption states that volume 2 of Goldoni's works was published by Pasquali in 1761.", "Retain the printed volume and date; the statement does not resolve any discrepancy with the chapter's endnote until that note is processed.", ["cand-3602", "cand-1205", "cand-1844"]),
]
for statement in new_statements:
    if statement["statement_id"] in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement['statement_id']}")
    line = statement["qualifiers"]["source_line_start"]
    quote = statement["original_quote"]
    if quote != visual_lines[line - 1]:
        raise SystemExit(f"statement quote does not match visual transcription: {statement['statement_id']}")

crossref_statement_id = "st-chp13-p335-gerusalemme-1745-edition-and-patronage-climax"
crossref_statement = statement_by_id.get(crossref_statement_id)
if not crossref_statement or "cand-10114" in crossref_statement["qualifiers"].get("mentioned_candidate_ids", []):
    raise SystemExit("expected p.335 Plate 57a statement is missing or already linked")

coverage_by_id[ORIGINAL_SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L124-139",
    "note": "no_semantic_content: the original OCR segment contains reversed figure-label fragments only; the legible printed captions are represented in the derived visual transcription segment. CHP-13.pdf physical page 14 was inspected upright. Canonical OCR and PDF remain unchanged.",
})
coverage.append({
    "chapter": "chp-13",
    "segment_id": VISUAL_SEGMENT,
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L1-3",
    "note": "Plate 57a and 57b captions were transcribed from CHP-13.pdf physical page 14 and semantically recorded with attribution, depicted subject, work/edition, and imprint distinctions. Image descriptions are not independent biographical evidence; source and publication differences remain for later note review.",
})

new_mentions = []
for mid, cid, surface, start, end, note in mention_specs:
    new_mentions.append({
        "mention_id": mid,
        "segment_id": VISUAL_SEGMENT,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })
new_mentions.append({
    "mention_id": ref_mid,
    "segment_id": "chp-13:13_CHP-13_intro:l32-39",
    "candidate_id": "cand-10114",
    "surface_form": "Plate 57a",
    "start_char": str(ref_start),
    "end_char": str(ref_start + len("Plate 57a")),
    "note": "Explicit cross-reference to the caption transcribed in the derived Plate 57 visual transcription segment.",
})

new_candidate_rows = candidates + [new_candidate]
new_mentions_rows = mentions + new_mentions
new_statement_rows = statements + new_statements
crossref_statement["qualifiers"]["mentioned_candidate_ids"] = list(crossref_statement["qualifiers"].get("mentioned_candidate_ids", [])) + ["cand-10114"]
new_coverage_rows = coverage

for mention in new_mentions:
    if mention["candidate_id"] not in {row["candidate_id"] for row in new_candidate_rows}:
        raise SystemExit(f"dangling candidate reference in mention {mention['mention_id']}")

print(f"candidate +{len([new_candidate])}; mentions +{len(new_mentions)}; statements +{len(new_statements)}; coverage {state[3]} -> {len(new_coverage_rows)}")
print(f"p.335 cross-reference local span={ref_start}:{ref_start + len('Plate 57a')}; Plate 57 captions visually anchored and internally consistent")
if not args.apply:
    print("dry-run only; pass --apply to write")
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = Path(str(path) + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, new_candidate_rows)
write_csv(mention_path, mention_fields, new_mentions_rows)
write_jsonl(statement_path, new_statement_rows)
write_csv(coverage_path, coverage_fields, new_coverage_rows)
print("applied; recovery backups saved for candidate, mention, statement, and coverage tables")
