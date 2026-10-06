"""Controlled S2 migration for Appendix I, printed p.386 (excluding the receipt opening)."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md"
SIGNATURE_SOURCE = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix_p386_receipt_visual-transcription.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-19Appendix.pdf"
EXPECTED_HASHES = {
    SOURCE: "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    SIGNATURE_SOURCE: "4fa4f3d98471fbdaff06490217fee4a416e71ee8b1df9385c5b279846c3be550",
    PDF: "2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb",
}
TITLE = "chp-19:19_CHP-19Appendix:l1-1"
P386 = "chp-19:19_CHP-19Appendix:l3-20"
P386_SIGNATURE = "chp-19:19_CHP-19Appendix_p386_receipt_visual-transcription:l1-2"
P386_RECEIPT = "chp-19:19_CHP-19Appendix_p386_receipt_visual-transcription:l4-4"
P387 = "chp-19:19_CHP-19Appendix:l22-41"
BACKUP_SUFFIX = ".bak-s2-chp19-p386-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
parser.add_argument("--repair-coverage", action="store_true")
args = parser.parse_args()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}

if args.repair_coverage:
    expected = {
        P386: ("L4-L20", "L4-20"),
        P386_SIGNATURE: ("L1-L2", "L1-2"),
    }
    for sid, (old_range, _) in expected.items():
        row = coverage_by_id.get(sid)
        if not row or row.get("disposition") != "reviewed" or row.get("migration_status") != "complete":
            raise SystemExit(f"coverage repair precondition changed: {sid}")
        if row.get("source_line_ranges") != old_range:
            raise SystemExit(f"coverage range no longer matches repair target: {sid}")
    if args.apply:
        backup = Path(str(coverage_path) + ".bak-s2-chp19-p386-coveragefix-20261004")
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(coverage_path, backup)
        for sid, (_, corrected_range) in expected.items():
            coverage_by_id[sid]["source_line_ranges"] = corrected_range
        write_csv(coverage_path, coverage_fields, coverage)
        print("applied p.386 coverage range format repair; one backup created")
    else:
        print("dry-run p.386 coverage range format repair")
        print("ranges: L4-L20 -> L4-20; L1-L2 -> L1-2")
    raise SystemExit(0)

for sid in (TITLE, P386, P386_SIGNATURE, P386_RECEIPT, P387):
    if sid not in segment_by_id or sid not in coverage_by_id:
        raise SystemExit(f"missing S0 or S2 row: {sid}")
for sid in (TITLE, P386, P386_SIGNATURE):
    row = coverage_by_id[sid]
    if row["disposition"] != "queued" or row["migration_status"] != "pending":
        raise SystemExit(f"coverage precondition changed: {sid}")
if coverage_by_id[P386_RECEIPT]["disposition"] != "queued" or coverage_by_id[P387]["disposition"] != "queued":
    raise SystemExit("receipt continuation segments must remain queued for their joint reading")


def segment_text(sid: str) -> str:
    row = segment_by_id[sid]
    lines = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[row["line_start"] - 1:row["line_end"]])
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if digest != row["sha256"]:
        raise SystemExit(f"segment hash mismatch: {sid}")
    return text


texts = {sid: segment_text(sid) for sid in (P386, P386_SIGNATURE, P386_RECEIPT, P387)}

new_candidate_specs = [
    ("cand-10746", "D. Lerio Licà", "person", P386, 10,
     "Name as printed in Giacinto Brandi's October 1675 letter. Identity and spelling are not externally checked."),
    ("cand-10747", "Rev. P. Loro (rector named in Brandi's letter)", "person", P386, 10,
     "Named as rector of the S. Andrea novitiate. Keep separate from the earlier unnamed-rector candidate pending S3 alignment."),
    ("cand-10748", "Mattia di Rossi (named in Brandi's February 1676 letter)", "person", P386, 14,
     "The same letter later says Signor Derossi; that local coreference is retained, while any match to the indexed Mattia de' Rossi remains for S3."),
    ("cand-10749", "Unidentified Giacinto Brandi painting for the S. Andrea novitiate (letters of 1675–1676)", "work", P386, 10,
     "The adjacent letters appear to concern one painting for the S. Andrea church/novitiate. No exact title, completion, or iconographic identification is asserted; the 1682 receipt is not merged here."),
    ("cand-10750", "Madalena figure mentioned in Brandi's unidentified painting", "", P386, 20,
     "The letter names a Magdalene figure within an unidentified painting. Type and external identity remain open; this is not a separate artwork."),
]

existing_candidate_keys = {
    ((row.get("canonical_name") or "").strip().casefold(), (row.get("suggested_type") or "").strip().casefold())
    for row in candidates
}
for cid, name, kind, sid, line, detail in new_candidate_specs:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.strip().casefold())
    if key in existing_candidate_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{sid}#L{line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_candidate_keys.add(key)


new_mention_specs = [
    ("m-chp19-p386-001", P386, "cand-0695", "S. Andrea al Quirinale", 0, "Church named in the appendix heading."),
    ("m-chp19-p386-002", P386, "cand-0447", "Giacinto Brandi", 0, "Artist named in the appendix heading."),
    ("m-chp19-p386-003", P386, "cand-1532", "Carlo", 0, "First part of the line-broken name Carlo Maratta."),
    ("m-chp19-p386-004", P386, "cand-1532", "Maratta", 0, "Second part of the line-broken name Carlo Maratta."),
    ("m-chp19-p386-005", P386, "cand-5338", "Jesuit Archives", 0, "Repository named in the source locator."),
    ("m-chp19-p386-006", P386, "cand-5338", "Fondo di Gesù—N. 865-13", 0, "Exact archival series/item locator in the heading."),
    ("m-chp19-p386-007", P386, "cand-4490", "Rome", 0, "City in the printed archive address."),
    ("m-chp19-p386-008", P386, "cand-0447", "Brandi", 0, "Heading for the letter excerpts."),
    ("m-chp19-p386-009", P386, "cand-10746", "D. Lerio Licà", 0, "Name as read in the printed letter; identity remains open."),
    ("m-chp19-p386-010", P386, "cand-5080", "Noviziato di S. Andrea", 0, "Place/institution wording retained from the letter; do not collapse into the church candidate before S3."),
    ("m-chp19-p386-011", P386, "cand-10747", "P. Loro", 0, "Named rector; identity remains open."),
    ("m-chp19-p386-012", P386, "cand-10749", "quadro che devo fare", 0, "The unnamed painting planned for the novitiate."),
    ("m-chp19-p386-013", P386, "cand-0447", "Giacinto Brandi", 1, "Signature of the October 1675 letter."),
    ("m-chp19-p386-014", P386, "cand-10748", "Mattia di Rossi", 0, "Name as printed in the February 1676 letter."),
    ("m-chp19-p386-015", P386, "cand-10749", "quadro che io faccio", 0, "The painting for their church; locally linked to the preceding Brandi commission with qualification."),
    ("m-chp19-p386-016", P386, "cand-10748", "Derossi", 0, "Later spelling in the same letter; mapped to Mattia di Rossi by local context only."),
    ("m-chp19-p386-017", P386, "cand-0447", "Giacinto Brandi", 2, "Signature of the February 1676 letter."),
    ("m-chp19-p386-018", P386, "cand-10749", "quadro sborzato", 0, "The sketched/underpainted picture in the March 1676 letter."),
    ("m-chp19-p386-019", P386, "cand-10749", "tutto il Redentore", 0, "Source wording may describe subject matter rather than a formal title."),
    ("m-chp19-p386-020", P386, "cand-10750", "Madalena", 0, "Figure named in the description; type remains unresolved."),
    ("m-chp19-p386-021", P386_SIGNATURE, "cand-0447", "Giacinto Brandi", 0, "Signature on the visually transcribed date/signature block for the March letter."),
]

mention_keys = {(row["segment_id"], int(row["start_char"]), int(row["end_char"])) for row in mentions}
for mid, sid, cid, surface, occurrence, note in new_mention_specs:
    if any(row.get("mention_id") == mid for row in mentions):
        raise SystemExit(f"mention ID already exists: {mid}")
    text = texts[sid]
    starts = []
    pos = 0
    while True:
        pos = text.find(surface, pos)
        if pos < 0:
            break
        starts.append(pos)
        pos += 1
    if occurrence >= len(starts):
        raise SystemExit(f"surface not found for {mid}: {surface!r}")
    start = starts[occurrence]
    end = start + len(surface)
    key = (sid, start, end)
    if key in mention_keys:
        raise SystemExit(f"mention natural key already exists: {sid} {start}:{end} {surface!r}")
    if cid not in candidate_by_id:
        raise SystemExit(f"mention foreign key missing: {mid} -> {cid}")
    mentions.append({
        "mention_id": mid, "segment_id": sid, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_keys.add(key)


def quote_for(sid: str, start_line: int, end_line: int) -> str:
    row = segment_by_id[sid]
    source_lines = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    quote = "\n".join(source_lines[start_line - 1:end_line])
    if quote not in texts[sid]:
        raise SystemExit(f"quote does not reproduce in segment {sid}: L{start_line}-L{end_line}")
    return quote


def make_statement(statement_id, sid, source_start, source_end, predicate, subject, obj, claim,
                   speaker, text_layer, qualification, candidate_ids, relation_candidate, cross_refs=None):
    if any(row.get("statement_id") == statement_id for row in statements):
        raise SystemExit(f"statement ID already exists: {statement_id}")
    if any(row.get("segment_id") == sid and row.get("qualifiers", {}).get("claim", "").strip().casefold() == claim.strip().casefold() for row in statements):
        raise SystemExit(f"statement natural key already exists: {sid} / {claim}")
    missing = [cid for cid in candidate_ids if cid not in candidate_by_id]
    if missing:
        raise SystemExit(f"statement candidate foreign keys missing: {statement_id}: {missing}")
    segment_row = segment_by_id[sid]
    quote = quote_for(sid, source_start, source_end)
    qualifiers = {
        "source_line_start": source_start, "source_line_end": source_end,
        "printed_page": 386, "pdf_physical_page": 1,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation_candidate,
        "cited_material_not_independently_consulted": True,
    }
    if cross_refs:
        qualifiers["cross_reference_segments"] = cross_refs
    row = {
        "statement_id": statement_id, "segment_id": sid,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "source_file": segment_row["source_file"],
        "origin": "book",
    }
    statements.append(row)


new_statement_specs = [
    ("st-chp19-p386-appendix-archive-locator", P386, 5, 7,
     "appendix_locates_material_about_s_andrea_altarpieces_in_jesuit_archives",
     "cand-5338", "cand-0695",
     "The appendix heading identifies documents concerning S. Andrea al Quirinale altarpieces by Giacinto Brandi and Carlo Maratta and locates the material in the Jesuit Archives, Fondo di Gesù N. 865-13, Rome.",
     "Appendix heading", "editorial source locator",
     "This is the locator as printed in Haskell's appendix; the archival file and address were not independently checked. The Chapter 3 pointer is navigational and does not add another fact.",
     ["cand-5338", "cand-0695", "cand-0447", "cand-1532", "cand-4490"], False, None),
    ("st-chp19-p386-oct1675-repeated-request", P386, 10, 10,
     "lerio_lica_repeatedly_urged_brandi_about_novitiate_painting_on_loros_behalf",
     "cand-10746", "cand-0447",
     "In the letter reproduced under Brandi's name, D. Lerio Licà is said to have repeatedly pressed Brandi about a painting for the S. Andrea novitiate on behalf of its rector, P. Loro.",
     "Giacinto Brandi", "quoted archival letter",
     "The wording reports Brandi's account of repeated pressure; it does not establish a completed commission or identify the recipient of the letter. Candidate identities remain open for S3.",
     ["cand-10746", "cand-0447", "cand-10747", "cand-5080"], True, None),
    ("st-chp19-p386-oct1675-painting-plan", P386, 10, 10,
     "brandi_deferred_novitiate_painting_until_chapel_was_ready_then_planned_to_finish_and_revise_sketch",
     "cand-0447", "cand-10749",
     "Brandi says he had thought the painting need not be provided until the chapel was furnished; after receiving notice, he would hurry to finish it and change the idea already sketched.",
     "Giacinto Brandi", "quoted archival letter",
     "The letter expresses a plan and a changed sketch, not proof of completion. OCR spellings are preserved in the quote; print corrections are recorded in the process note.",
     ["cand-0447", "cand-10749", "cand-5080"], True, None),
    ("st-chp19-p386-feb1676-canvas-arrangement", P386, 14, 16,
     "brandi_asked_mattia_di_rossi_to_prepare_canvas_at_intended_frame_and_site_before_painting",
     "cand-0447", "cand-10748",
     "Brandi says he had asked Mattia di Rossi the previous November to arrange the canvas in the intended frame and church location before painting so it would not need to be moved afterward; he attributes the delay to Rossi's many occupations and asks the Father to have it done.",
     "Giacinto Brandi", "quoted archival letter",
     "The source spells the name first as Mattia di Rossi and later as Derossi; both are mapped to one local candidate in this letter only. No cross-chapter identity match is made here.",
     ["cand-0447", "cand-10748", "cand-10749", "cand-5080"], True, None),
    ("st-chp19-p386-mar1676-letter-signature", P386_SIGNATURE, 1, 2,
     "third_brandi_letter_is_dated_8_march_1676_and_signed_giacinto_brandi",
     "cand-0447", None,
     "The letter excerpt immediately above the receipt is dated 8 March 1676 and signed Giacinto Brandi.",
     "Document dateline and signature", "printed letter signature",
     "The date/signature block was absent from canonical OCR and is transcribed from CHP-19Appendix.pdf physical page 1. It belongs to the preceding letter, not to the receipt below.",
     ["cand-0447"], False, [P386]),
    ("st-chp19-p386-mar1676-view-and-magdalen", P386, 20, 20,
     "brandi_invited_recipient_to_view_sketch_and_said_madalena_was_not_to_his_taste",
     "cand-0447", "cand-10749",
     "Brandi invites the recipient to view the sketched picture and says the Madalena figure was not to his taste.",
     "Giacinto Brandi", "quoted archival letter",
     "The phrase tutto il Redentore is retained as printed wording and not treated as a formal title. The figure's type and identity remain open. The letter's date/signature is linked from the adjacent visual transcription.",
     ["cand-0447", "cand-10749", "cand-10750"], False, [P386_SIGNATURE]),
    ("st-chp19-p386-mar1676-work-started", P386, 20, 20,
     "brandi_reassured_recipient_that_painting_had_been_started",
     "cand-0447", "cand-10749",
     "Brandi tells the recipient not to remain apprehensive that the painting had not been begun and says the recipient can see for himself.",
     "Giacinto Brandi", "quoted archival letter",
     "This records Brandi's reassurance, not independent confirmation of the painting's progress. The dated signature is in the adjacent visual transcription.",
     ["cand-0447", "cand-10749"], False, [P386_SIGNATURE]),
]

for spec in new_statement_specs:
    make_statement(*spec)

coverage_by_id[TITLE].update({
    "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
    "note": "Generated Markdown filename heading only; not printed book text and contains no claim or entity mention.",
})
coverage_by_id[P386].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L4-20",
    "note": "Printed p.386 body read against CHP-19Appendix.pdf physical page 1; the 8 March 1676 dateline/signature is in a separate visual-transcription segment. The receipt opening below it remains a separate queued segment and continues on p.387.",
})
coverage_by_id[P386_SIGNATURE].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L1-2",
    "note": "Printed p.386 date/signature omitted from canonical OCR; transcribed from CHP-19Appendix.pdf physical page 1 and linked to the preceding Brandi letter. The receipt begins after this signature.",
})

for cid, *_ in new_candidate_specs:
    assert cid in candidate_by_id
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    for path in paths:
        backup = Path(str(path) + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print("applied p.386 S2 migration; backups created for four tables")
else:
    print("dry-run p.386 S2 migration")
    print(f"candidates +{len(new_candidate_specs)}; mentions +{len(new_mention_specs)}; statements +{len(new_statement_specs)}")
    print("coverage: title excluded; canonical p.386 body complete; omitted date/signature complete; receipt opening and p.387 remain queued")
