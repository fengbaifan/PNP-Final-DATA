"""Controlled S2 migration for Appendix I, printed p.388 (continuations and Orsini letters)."""
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
PDF = ROOT / "02-sources" / "01-book" / "CHP-19Appendix.pdf"
EXPECTED_HASHES = {
    SOURCE: "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    PDF: "2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb",
}
P387 = "chp-19:19_CHP-19Appendix:l22-41"
P388 = "chp-19:19_CHP-19Appendix:l43-63"
P389 = "chp-19:19_CHP-19Appendix:l65-84"
BACKUP_SUFFIX = ".bak-s2-chp19-p388-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
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

for sid in (P387, P388, P389):
    if sid not in segment_by_id or sid not in coverage_by_id:
        raise SystemExit(f"missing S0 or S2 row: {sid}")
if coverage_by_id[P387]["disposition"] != "reviewed" or coverage_by_id[P387]["migration_status"] != "partial":
    raise SystemExit("p.387 must remain reviewed/partial until this continuation is processed")
if coverage_by_id[P388]["disposition"] != "queued" or coverage_by_id[P388]["migration_status"] != "pending":
    raise SystemExit(f"coverage precondition changed: {P388}")
if coverage_by_id[P389]["disposition"] != "queued":
    raise SystemExit("p.389 continuation must remain queued for its own reading")


def segment_text(sid: str) -> str:
    row = segment_by_id[sid]
    lines = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[row["line_start"] - 1:row["line_end"]])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != row["sha256"]:
        raise SystemExit(f"segment hash mismatch: {sid}")
    return text


texts = {sid: segment_text(sid) for sid in (P388,)}

# The page image closes p.387's first-person letter with a signature read as
# Domenico Fedini. Canonical OCR line 48 merges that signature with the next
# locator and reads Pedini; preserve the local candidate until S3 alignment.
fedini = candidate_by_id.get("cand-10766")
if not fedini or fedini.get("canonical_name") != "Unidentified writer of Fondo Orsini 171, c. I":
    raise SystemExit("expected open local writer candidate cand-10766")
fedini["canonical_name"] = "Domenico Fedini (signature read on printed p.388)"
fedini["candidate_source_ref"] = f"{P388}#L48"
fedini["detail"] = "The p.388 signature image appears to read Domenico Fedini; canonical OCR line 48 reads Domenico Pedini and merges the name with the following ibid., c. 140 locator. Keep this local reading distinct from indexed cand-1014 (Fedini, Domenico) and from the separately signed Domenico Pedini until S3."
fedini["status"] = "open"

prior_letter_statement_ids = {
    "st-chp19-p387-orsini-letter-model-transfer",
    "st-chp19-p387-orsini-letter-four-models",
    "st-chp19-p387-orsini-letter-jewel-and-handle",
    "st-chp19-p387-orsini-letter-model-handle",
    "st-chp19-p387-orsini-letter-german-caster-death",
    "st-chp19-p387-orsini-letter-widow-first-remarriage",
    "st-chp19-p387-orsini-letter-widow-second-remarriage",
    "st-chp19-p387-orsini-letter-powder-report",
    "st-chp19-p387-orsini-letter-four-sapphires",
}
prior_letter_statements = {row["statement_id"]: row for row in statements if row.get("statement_id") in prior_letter_statement_ids}
if set(prior_letter_statements) != prior_letter_statement_ids:
    raise SystemExit("expected all nine p.387 Fondo Orsini letter statements before closing attribution")
for row in prior_letter_statements.values():
    qualifiers = row.get("qualifiers", {})
    if qualifiers.get("speaker") != "Unidentified writer of Fondo Orsini 171, c. I":
        raise SystemExit(f"p.387 speaker no longer matches repair target: {row['statement_id']}")
    qualifiers["speaker"] = "Domenico Fedini (signature read on printed p.388; OCR line 48 reads Pedini)"
    refs = qualifiers.setdefault("cross_reference_segments", [])
    if P388 not in refs:
        refs.append(P388)
    qualifiers["qualification"] = qualifiers.get("qualification", "") + " The printed p.388 signature appears to read Domenico Fedini; its local identity is recorded separately from the OCR's Pedini form and awaits S3 alignment."
    qualifiers.pop("migration_qualification", None)

addressee = candidate_by_id.get("cand-10777")
if not addressee or "V.E." not in addressee.get("canonical_name", ""):
    raise SystemExit("expected the unresolved V.E. addressee candidate cand-10777")
addressee["detail"] = "The Appendix 2 heading names Paolo Giordano Orsini, Duke of Bracciano; p.388 salutations also address a S.re Duca/V.E. The role likely refers to that duke, but the local endpoint remains separate pending S3."

new_candidate_specs = [
    ("cand-10781", "Domenico Pedini", "person", P388, 53,
     "Signed the Fondo Orsini c.140 letter dated 27 June 1623 and the c.173, c.2 letter dated 21 September 1624. Keep distinct from Domenico Fedini as printed on p.388 until S3."),
    ("cand-10782", "Bastiano Sebastiani (bronze caster named in the Orsini letters)", "person", P388, 50,
     "Named as the caster proposed for the Duke's bronze head and later as the gettatore. No external identity is asserted."),
    ("cand-10783", "Bronze head portrait of V.E. in the Orsini letters (c.140/c.173)", "work", P388, 50,
     "The c.140 letter proposes casting the head in bronze; c.173 reports the cast and finishing instructions. It may align with wax model cand-5546 and bronze cast cand-5547, but cross-chapter identity and version linkage are deferred to S3."),
    ("cand-10784", "Fonderia di S. Pietro (casting site named in the Orsini c.173 letter)", "place", P388, 57,
     "The letter says the bronze head was cast there. Keep distinct from the institution Fabbrica di S. Pietro (cand-3521) until alignment."),
    ("cand-10785", "Bronze head casting and finishing procedure described in the Orsini letters", "procedure", P388, 50,
     "The c.140 letter reports plaster/wax trials and estimated costs; c.173 reports cutting only surrounding sprues and finishing in Bernini's presence. Preserve the source's technical wording and stage sequence."),
    ("cand-10786", "Fondo Orsini letter, c. 140 (27 June 1623; Domenico Pedini)", "archive", P388, 48,
     "Distinct archival letter following the c.I item; the exact locator and date/signature are printed in the Appendix."),
    ("cand-10787", "Fondo Orsini letter, 173, c. 2 (21 September 1624; Domenico Pedini)", "archive", P388, 54,
     "Distinct archival letter reporting the bronze head casting and request for transfer/finishing."),
    ("cand-10788", "Fondo Orsini letter, 175, c. 463 (Appendix 2; continues onto p.389)", "archive", P388, 61,
     "Individually located letter in which Bernini asks the unnamed writer to accompany Gioì Paolo Baldi; text and author continue beyond p.388."),
    ("cand-10789", "Gioì Paolo Baldi", "person", P388, 63,
     "Named as the person whom Bernini asks the letter writer to accompany to conduct personal business. Do not normalize the given name or infer identity before S3."),
    ("cand-10790", "Unidentified work at the Altar of S. Pietro mentioned in the c.173 letter", "work", P388, 57,
     "The letter mentions work at the altar as a reason for the caster's location and reluctance to move the head; no specific altar project is identified."),
    ("cand-10791", "Unidentified writer of Fondo Orsini 175, c. 463", "person", P388, 63,
     "First-person writer reports Bernini's request to accompany Gioì Paolo Baldi. The signature is beyond this segment; keep separate from Pedini until p.389 is read."),
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
    ("m-chp19-p388-001", P388, "cand-10777", "V.E.", 0, "Honorific address in the p.387 letter's closing; name unresolved locally."),
    ("m-chp19-p388-002", P388, "cand-10777", "V.E.", 1, "The addressee is asked to view the four sapphires and see that they differ."),
    ("m-chp19-p388-003", P388, "cand-10777", "S:re Duca", 0, "Salutation identifies the addressee as a Duke; the Appendix heading's Paolo Giordano Orsini match remains for S3."),
    ("m-chp19-p388-004", P388, "cand-10766", "Domenico Pedini", 0, "Canonical OCR merges this signature with the next c.140 locator and reads Pedini; the printed signature appears to read Fedini."),
    ("m-chp19-p388-005", P388, "cand-10786", "ibid., c. 140", 0, "Locator for the next, distinct letter."),
    ("m-chp19-p388-006", P388, "cand-0295", "Cavai:re Bernino", 0, "Bernini named in the c.140 letter."),
    ("m-chp19-p388-007", P388, "cand-10782", "m.r Bastiano Sebastiani", 0, "Named proposed bronze caster."),
    ("m-chp19-p388-008", P388, "cand-10783", "testa di", 0, "The head phrase immediately precedes the V.E. addressee mention."),
    ("m-chp19-p388-009", P388, "cand-10777", "V.E.", 2, "The head's addressee/commissioning authority in the letter."),
    ("m-chp19-p388-010", P388, "cand-10777", "V.E.", 3, "Pedini says he is informing the Duke about the cost and seeking an order."),
    ("m-chp19-p388-011", P388, "cand-0295", "Cavalire", 0, "Local reference to Bernini, who made the portrait; name is given earlier in the same sentence."),
    ("m-chp19-p388-012", P388, "cand-10783", "il ritratto", 0, "Portrait described as made to the Duke's satisfaction; its relation to the bronze head is local and qualified."),
    ("m-chp19-p388-013", P388, "cand-10777", "V.E.", 4, "Honorific address at the close of Pedini's c.140 letter."),
    ("m-chp19-p388-014", P388, "cand-10781", "Domenico Pedini", 1, "Signature of the c.140 letter; local attribution only."),
    ("m-chp19-p388-015", P388, "cand-4490", "Roma", 0, "City in the 27 June 1623 dateline."),
    ("m-chp19-p388-016", P388, "cand-10781", "Domenico Pedini", 2, "Signature of the separate c.173 letter."),
    ("m-chp19-p388-017", P388, "cand-10787", "173» c. 2", 0, "OCR form; the printed locator appears as 173, c. 2."),
    ("m-chp19-p388-018", P388, "cand-0295", "Caval.re Bernino", 0, "Bernini named in the c.173 letter."),
    ("m-chp19-p388-019", P388, "cand-10783", "testa di", 1, "Head phrase at the p.388 line break before V.E.; continuation is linked across the OCR wrap."),
    ("m-chp19-p388-020", P388, "cand-10777", "V.E.", 5, "The Duke's head and satisfaction are discussed."),
    ("m-chp19-p388-021", P388, "cand-10782", "Gettatore", 0, "Caster instructed to remove only the surrounding sprues."),
    ("m-chp19-p388-022", P388, "cand-10784", "fonderia di S. Pietro", 0, "Physical casting site named in the letter."),
    ("m-chp19-p388-023", P388, "cand-10790", "Altare di S. Pietro", 0, "Nearby altar work cited as a logistical reason; OCR reads deh’Altare, while the page image reads dell’Altare; exact project unresolved."),
    ("m-chp19-p388-024", P388, "cand-10777", "V.E.", 6, "Pedini requests a written order to move the head."),
    ("m-chp19-p388-025", P388, "cand-0295", "s:r Caval.re Bernino", 0, "Bernini's house is the proposed destination for finishing the cast."),
    ("m-chp19-p388-026", P388, "cand-10777", "V.E.", 7, "Pedini awaits further instructions from the addressee."),
    ("m-chp19-p388-027", P388, "cand-10777", "S:re Duca", 1, "Salutation of the c.173 letter."),
    ("m-chp19-p388-029", P388, "cand-4490", "Roma", 1, "City in the 27 June 1623 dateline."),
    ("m-chp19-p388-030", P388, "cand-10777", "S.r Duca", 0, "Duke salutation in the c.173 letter's closing."),
    ("m-chp19-p388-031", P388, "cand-10777", "V. Ecciza", 0, "OCR form of the honorific in the c.173 letter."),
    ("m-chp19-p388-032", P388, "cand-10777", "V. Ecciza", 1, "OCR form of the honorific in the c.173 letter."),
    ("m-chp19-p388-033", P388, "cand-10777", "V. Eccrza", 0, "OCR form of the honorific in the c.173 closing."),
    ("m-chp19-p388-034", P388, "cand-10788", "175, c. 463", 0, "Archival locator for the next letter."),
    ("m-chp19-p388-035", P388, "cand-0295", "Caval.re Bernino", 1, "Bernini makes the request concerning Baldi."),
    ("m-chp19-p388-036", P388, "cand-10789", "Gioì Paolo Baldi", 0, "Person Bernini asks the letter writer to accompany."),
    ("m-chp19-p388-037", P388, "cand-10777", "V. Ecciza", 2, "The Duke's authority is invoked in the c.463 letter."),
    ("m-chp19-p388-038", P388, "cand-10785", "getto di Bronzo", 0, "Casting process named in the c.140 letter."),
    ("m-chp19-p388-039", P388, "cand-10785", "getto di Bronzo", 1, "Casting process named again in the c.173 letter."),
    ("m-chp19-p388-040", P388, "cand-0295", "Cavalire", 1, "Local reference to Bernini in the c.173 finishing instruction."),
    ("m-chp19-p388-041", P388, "cand-0295", "Cavallire", 0, "OCR variant referring to Cavalier Bernini in the c.463 letter."),
    ("m-chp19-p388-042", P388, "cand-4490", "Roma", 2, "City in the 21 September 1624 dateline."),
    ("m-chp19-p388-043", P388, "cand-10782", "Gettatore", 1, "Caster in the c.173 finishing instruction."),
    ("m-chp19-p388-044", P388, "cand-10782", "Gettatore", 2, "Caster in the c.173 transport discussion."),
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
        pos += len(surface)
    if occurrence >= len(starts):
        raise SystemExit(f"surface not found for {mid}: {surface!r} (count={len(starts)})")
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
                   speaker, text_layer, qualification, candidate_ids, relation_candidate, cross_refs=None,
                   migration_qualification="complete"):
    if any(row.get("statement_id") == statement_id for row in statements):
        raise SystemExit(f"statement ID already exists: {statement_id}")
    if any(row.get("segment_id") == sid and row.get("qualifiers", {}).get("claim", "").strip().casefold() == claim.strip().casefold() for row in statements):
        raise SystemExit(f"statement natural key already exists: {sid} / {claim}")
    missing = [cid for cid in candidate_ids if cid not in candidate_by_id]
    if missing:
        raise SystemExit(f"statement candidate foreign keys missing: {statement_id}: {missing}")
    segment_row = segment_by_id[sid]
    qualifiers = {
        "source_line_start": source_start, "source_line_end": source_end,
        "printed_page": 388, "pdf_physical_page": 3,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation_candidate,
        "cited_material_not_independently_consulted": True,
    }
    if cross_refs:
        qualifiers["cross_reference_segments"] = cross_refs
    if migration_qualification != "complete":
        qualifiers["migration_qualification"] = migration_qualification
    statements.append({
        "statement_id": statement_id, "segment_id": sid,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote_for(sid, source_start, source_end),
        "source_file": segment_row["source_file"], "origin": "book",
    })


new_statement_specs = [
    ("st-chp19-p388-171-sapphires-close", P388, 44, 47,
     "fedini_closed_sapphire_request_and_dated_letter_3_may_1623",
     "cand-10766", "cand-10776",
     "The writer asks the recipient to return the sapphires not selected and say whether payment is due, dates the letter Rome, 3 May 1623, and adds that he will be present at an illegible time/place so the Duke can see the sapphires differ.",
     "Domenico Fedini (signature read on printed p.388)", "quoted archival letter and signature",
     "This closes the p.387 sentence. The time/place wording at L46 is partly illegible. The printed signature appears to read Fedini; the OCR line merges it with the following c.140 locator.",
     ["cand-10766", "cand-10776", "cand-10777", "cand-10765"], True, [P387]),
    ("st-chp19-p388-171-fedini-signature", P388, 47, 48,
     "printed_p388_signature_appears_to_name_domenico_fedini_on_fondo_orsini_171_ci_letter",
     "cand-10766", "cand-10765",
     "The signature on the letter continued from p.387 appears in the print to read Domenico Fedini; the canonical OCR line reads Domenico Pedini and merges the signature with the next ibid., c. 140 locator.",
     "Printed signature / OCR comparison", "source-page signature and editorial locator",
     "This visual reading is kept as a local candidate, distinct from indexed cand-1014 and from the subsequent Domenico Pedini signature, until S3 alignment.",
     ["cand-10766", "cand-10765", "cand-10786"], False, [P387]),
    ("st-chp19-p388-c140-bronze-head-casting-plan", P388, 50, 51,
     "pedini_reported_plan_to_pay_up_to_25_scudi_to_bastiano_sebastiani_for_bronze_head_casting",
     "cand-10781", "cand-10783",
     "Domenico Pedini says he and Cavalier Bernino discussed paying up to 25 scudi to Bastiano Sebastiani to cast the Duke's bronze head; plaster and wax trials with at least two and perhaps three waxes would account for the cost, and Pedini asks for the necessary order.",
     "Domenico Pedini", "quoted archival letter, Fondo Orsini c.140",
     "The letter proposes/estimates casting; it does not say the head was cast at this date. The Duke is the Appendix 2 addressee candidate; identity alignment remains for S3.",
     ["cand-10781", "cand-0295", "cand-10782", "cand-10783", "cand-10785", "cand-10777", "cand-10786"], True, None),
    ("st-chp19-p388-c140-portrait-and-caster-praise", P388, 50, 51,
     "pedini_said_bernini_had_made_the_portrait_to_the_dukes_great_satisfaction",
     "cand-0295", "cand-10783",
     "Pedini reports that Bernini made the portrait to the Duke's great satisfaction and that the caster was ambitious to demonstrate diligence and art.",
     "Domenico Pedini", "quoted archival letter, Fondo Orsini c.140",
     "The source does not name the Duke in this letter. The portrait and bronze head are locally linked but their relation to the separately indexed wax/bronze candidates remains for S3.",
     ["cand-10781", "cand-0295", "cand-10782", "cand-10783", "cand-10777"], True, None),
    ("st-chp19-p388-c140-date-signature", P388, 51, 53,
     "domenico_pedini_signed_c140_letter_in_rome_on_27_june_1623",
     "cand-10781", "cand-10786",
     "The c.140 letter is dated Rome, 27 June 1623 and signed Domenico Pedini.",
     "Domenico Pedini", "quoted archival letter signature/dateline",
     "This is distinct from the preceding p.387 letter whose signature appears to read Domenico Fedini.",
     ["cand-10781", "cand-10786", "cand-4490"], False, None),
    ("st-chp19-p388-c173-cast-result-and-instructions", P388, 56, 57,
     "pedini_reported_successful_bronze_cast_and_berninis_limited_sprue_removal_order",
     "cand-10781", "cand-10783",
     "Pedini says he and Bernini viewed the bronze head cast, which was judged exceptionally clean; Bernini ordered the caster to cut only the surrounding sprues and not otherwise touch the head with tools or files without the Duke's order.",
     "Domenico Pedini", "quoted archival letter, Fondo Orsini 173 c.2",
     "This is a report of the result and Bernini's instruction, not independent appraisal. The earlier uncast proposal and this 1624 cast are locally linked; version alignment remains for S3.",
     ["cand-10781", "cand-0295", "cand-10782", "cand-10783", "cand-10777", "cand-10787", "cand-10785"], True, None),
    ("st-chp19-p388-c173-foundry-and-transfer-request", P388, 57, 59,
     "head_was_cast_at_s_pietro_foundry_and_pedini_requested_ducal_order_to_move_it_to_berninis_house_for_finishing",
     "cand-10781", "cand-10783",
     "Pedini says the head was cast at the Fonderia di S. Pietro; because of nearby Altar of S. Pietro work the caster might resist moving it, so Pedini asks the Duke for a written order to take it to Bernini's house for finishing in Bernini's presence.",
     "Domenico Pedini", "quoted archival letter, Fondo Orsini 173 c.2",
     "The altar work is unidentified; the foundry is kept distinct from the institution Fabbrica di S. Pietro. The requested transfer is not recorded as completed here.",
     ["cand-10781", "cand-0295", "cand-10783", "cand-10784", "cand-10787", "cand-10790", "cand-10777"], True, None),
    ("st-chp19-p388-c173-date-signature", P388, 58, 60,
     "domenico_pedini_signed_c173_letter_in_rome_on_21_september_1624",
     "cand-10781", "cand-10787",
     "The c.173, c.2 letter is dated Rome, 21 September 1624 and signed Domenico Pedini.",
     "Domenico Pedini", "quoted archival letter signature/dateline",
     "The OCR layout combines the left-hand S.r Duca salutation with the right-hand signature; they refer to addressee and writer respectively.",
     ["cand-10781", "cand-10787", "cand-4490", "cand-10777"], False, None),
    ("st-chp19-p388-c463-baldi-recommendation", P388, 62, 63,
     "bernini_asked_unidentified_writer_to_accompany_gio_paolo_baldi_and_sought_ducal_authority",
     "cand-0295", "cand-10789",
     "In the c.463 letter, Bernini asks the writer to accompany Gioì Paolo Baldi, who is travelling to conduct personal business quickly, and recommends him to the authority of V.E.",
     "Unidentified writer of Fondo Orsini 175, c.463", "quoted archival letter",
     "The sentence and signature continue onto p.389; do not identify the writer or record the requested accompaniment as completed.",
     ["cand-0295", "cand-10777", "cand-10788", "cand-10789", "cand-10791"], True, [P389], "partial"),
]

for spec in new_statement_specs:
    make_statement(*spec)

coverage_by_id[P387].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L23-41",
    "note": "Printed p.387 receipt and Appendix 2 letter were read; the sapphires sentence is now closed by p.388 L44-L47. The letter's print signature on p.388 appears to read Domenico Fedini, while canonical OCR merges it with the following c.140 locator as Domenico Pedini; local identity remains for S3.",
})
coverage_by_id[P388].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L44-63",
    "note": "Printed p.388 (PDF physical page 3) read against CHP-19Appendix.pdf. Closes Fondo Orsini 171 c.I letter and records its signature; processes c.140 and 173 c.2 letters signed Domenico Pedini; begins c.463 letter concerning Gioì Paolo Baldi. The c.463 sentence and writer attribution continue in p.389 segment L65-84; retain partial status and cross-reference until read.",
})

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
    print("applied p.388 S2 migration and p.387 signature attribution repair; backups created for four tables")
else:
    print("dry-run p.388 S2 migration")
    print(f"candidates +{len(new_candidate_specs)}; mentions +{len(new_mention_specs)}; statements +{len(new_statement_specs)}")
    print("coverage: p.387 complete; p.388 reviewed/partial pending p.389 closure")
