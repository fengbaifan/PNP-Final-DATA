"""Controlled S2 migration for printed p.262; defaults to a read-only dry run."""
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
BODY_SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
VISUAL_SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro_notes_p262_visual-transcription.md"
P261 = "chp-9:09_CHP-9_intro:l212-216"
P262 = "chp-9:09_CHP-9_intro:l218-229"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
VISUAL = "chp-9:09_CHP-9_intro_notes_p262_visual-transcription:l1-1"
EXPECTED_HASHES = {
    P261: "e94cea1632b183f4153ca8a3fef9cba2f227692c01e4c904a018c000303fa97b",
    P262: "19071349bda95267fa463da2c9c65c3af827a9e978d3585bdbb715e08831f9dc",
    NOTES: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
    VISUAL: "d9671b7aaf07a56182e74a19842dd35ebcf312f7feb8827d8676dbfa828de3c3",
}
EXPECTED_ASSETS = {
    BODY_SOURCE: "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    VISUAL_SOURCE: "19d871e4a76f86368b71b4f11528fab11181863a2361ed2b8d46407408a73e8f",
}
BACKUP_SUFFIX = ".bak-s2-chp9-p262-20261001"
PHYSICAL_PAGE = 24


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {r["segment_id"]: r for r in segments}
for sid, expected_hash in EXPECTED_HASHES.items():
    if sid not in segment_by_id or segment_by_id[sid]["sha256"] != expected_hash:
        raise SystemExit(f"missing or changed source segment: {sid}")
for path, expected_hash in EXPECTED_ASSETS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise SystemExit(f"S0 source asset changed: {path.name}")

body_lines = BODY_SOURCE.read_text(encoding="utf-8-sig").splitlines()
visual_lines = VISUAL_SOURCE.read_text(encoding="utf-8-sig").splitlines()
source_lines_by_id = {P261: body_lines, P262: body_lines, NOTES: body_lines, VISUAL: visual_lines}


def quote(segment_id, first, last):
    lines = source_lines_by_id[segment_id]
    return "\n".join(lines[n - 1] for n in range(first, last + 1))


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {r["segment_id"]: r for r in coverage}
expected_coverage = {
    P261: ("reviewed", "partial", "L213-216"),
    P262: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-409; p.255 L155 continuation"),
}
for sid, expected in expected_coverage.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage for {sid}: {row}")
if VISUAL in coverage_by_id:
    raise SystemExit(f"visual segment already has coverage; inspect before retrying: {VISUAL}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8543:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")

C = {
    "zecchino": "cand-8544",
    "berengo_1956": "cand-8545",
    "de_la_lande_tables": "cand-8546",
    "meschini_1806": "cand-8547",
    "labia_inventory_1749": "cand-8548",
    "bevilacqua_reference": "cand-8549",
    "pieta_dome_frescoes": "cand-8550",
    "church_pieta": "cand-8551",
    "labia_tiepolo_portrait": "cand-8552",
    "labia_tiepolo_frescoes": "cand-8553",
    "labia_cignaroli_paintings": "cand-8554",
    "palazzo_giovanelli": "cand-8555",
    "biblioteca_cremona": "cand-8556",
    "biffi_correspondence": "cand-8557",
    "biffi_paolo": "cand-8558",
    "biffi_palma": "cand-8559",
    "biffi_farinato": "cand-8560",
    "biffi_tempesta": "cand-8561",
    "biffi_zelotti": "cand-8562",
    "giovanelli_greek_panels": "cand-8563",
    "ancestral_portraits": "cand-8564",
    "bergamo_cathedral": "cand-8565",
    "labia_ritratto": "cand-8566",
    "labia_palla": "cand-8567",
    "foreign_price_competition": "cand-8568",
    "angelo_custode_work": "cand-8569",
    "martyrdom_work": "cand-8570",
}
candidate_specs = [
    (8544, "Zecchino (currency unit used in Haskell's p.262 comparisons)", "term", P262, 219,
     "Currency unit to which Haskell converts the cited monetary estimates; values from different points in the century are not adjusted for changing purchasing power."),
    (8545, "Berengo, 1956, p. 86 (citation locator; title not supplied)", "archive", P262, 226,
     "Citation locator given for the estimate of bare subsistence; title and cited page were not independently consulted."),
    (8546, "De La Lande, volume VII, page 81 (currency tables cited by Haskell)", "archive", NOTES, 410,
     "Haskell says the currency conversion uses tables in De La Lande, volume VII, page 81; the cited tables were not independently consulted."),
    (8547, "Meschini, 1806, volume II, page 105 (citation locator)", "archive", NOTES, 412,
     "Citation locator in Haskell's note 4; title and cited page were not independently consulted."),
    (8548, "Unpublished Labia inventory of 1749 (as cited by Haskell)", "archive", NOTES, 413,
     "Inventory cited for Tiepolo entries and Cignaroli's work for the Labia; Haskell points back to p.250 note 8. The inventory was not independently consulted."),
    (8549, "Bevilacqua (reference for Cignaroli; title not supplied)", "archive", P262, 227,
     "Surname-only reference named in Haskell's note 5 for Cignaroli; no title or fuller citation is supplied."),
    (8550, "Tiepolo's frescoes in the dome of the church of the Pietà, Venice", "work", P262, 221,
     "Frescoes reported by Haskell as painted in 1754 for 500 zecchini; do not infer exact scope or a modern catalogue identity."),
    (8551, "Church of the Pietà, Venice (as named by Haskell)", "place", P262, 221,
     "Church identified as the setting for Tiepolo's dome frescoes; S3 may align this source-level place candidate."),
    (8552, "Unidentified Tiepolo portrait in the Labia collection (p.262)", "work", P262, 223,
     "The source reports a portrait by Tiepolo but supplies no title or identity. Do not equate it with an inventory entry without evidence."),
    (8553, "Unidentified Tiepolo frescoes in the Labia collection (p.262)", "work", P262, 223,
     "Plural frescoes reported in the Labia collection; exact cycle, location and identity are not specified in this sentence."),
    (8554, "Unidentified Cignaroli oil paintings inserted into Labia Palace ceilings", "work", P262, 227,
     "Haskell's note reports several oil paintings inserted into palace ceilings, some still in situ; no titles or precise count are given."),
    (8555, "Palazzo Giovanelli, Venice (named in Biffi's 1773 report)", "place", P262, 228,
     "Palace named as the setting of Giambattista Biffi's description; exact identification is left to S3."),
    (8556, "Biblioteca Governativa, Cremona", "institution", P262, 229,
     "Repository named in Haskell's note 6 for the Biffi correspondence; keep distinct from other libraries with the same institutional wording."),
    (8557, "Giambattista Biffi correspondence on Palazzo Giovanelli (1773; manuscript locator)", "archive", P262, 228,
     "Correspondence quoted by Haskell from Biblioteca Governativa, Cremona, MSS. aa.I.4.1; the manuscript was not independently consulted."),
    (8558, "Paolo, painter named only by given name in Biffi's 1773 quotation", "person", P262, 228,
     "Retain the source's given-name-only form; identity is not resolved by this quotation."),
    (8559, "Palma, painter named only by surname in Biffi's 1773 quotation", "person", P262, 228,
     "Retain the source's surname-only form; do not choose between same-named artists at S2."),
    (8560, "Farinato, painter named in Biffi's 1773 quotation", "person", P262, 228,
     "Source spelling and identity retained as quoted; no fuller name is given here."),
    (8561, "Tempesta, painter named in Biffi's 1773 quotation", "person", P262, 228,
     "Surname-only name in a nested quotation; identity is unresolved."),
    (8562, "Zelotti, painter named in Biffi's 1773 quotation", "person", P262, 228,
     "Surname-only name in a nested quotation; identity is unresolved."),
    (8563, "Greek panels of the Quattrocento in Palazzo Giovanelli (unnamed group)", "work", P262, 228,
     "Unnamed group described in Biffi's quotation; preserve the original period term without resolving individual panels."),
    (8564, "Unidentified ancestral portraits in Venetian patrician galleries", "work", P262, 222,
     "Haskell poses a question about who began painting ancestral portraits; no artist, family, or portrait is identified."),
    (8565, "Bergamo Cathedral (as named by Haskell; exact building identity unresolved)", "place", P262, 221,
     "Building named as the setting of Tiepolo's Martyrdom of St John the Bishop; do not infer a more specific cathedral identity from this passage."),
    (8566, "Unidentified Tiepolo inventory entry 'Ritratto con cristallo' in Labia collection", "work", NOTES, 413,
     "The unpublished Labia inventory's description is recorded verbatim; do not infer a catalogue identity or equate it with the p.262 body portrait."),
    (8567, "Unidentified Tiepolo inventory entry 'Una Palla' in Labia collection", "work", NOTES, 413,
     "The unpublished Labia inventory's description is recorded verbatim; do not infer a catalogue identity."),
    (8568, "Foreign competition as a factor keeping prices high for successful Venetian artists", "term", P262, 219,
     "Haskell's explanation for high prices in the most successful cases; no market data or causal measure is supplied here."),
    (8569, "Piazzetta's large picture of the Angelo Custode (work as described on p.262)", "work", P262, 220,
     "Work-level candidate for the picture valued at about 100 zecchini; title and attribution are recorded as Haskell gives them, without external verification."),
    (8570, "Tiepolo's Martyrdom of St John the Bishop in Bergamo Cathedral", "work", P262, 221,
     "Work-level candidate for the painting for which Haskell reports a 1743 payment; catalogue identity and payment record were not independently verified."),
]
natural_keys = {(r["canonical_name"], r["suggested_type"]) for r in candidates}
for n, name, kind, source_segment, line_no, detail in candidate_specs:
    cid = f"cand-{n:04d}"
    if cid in candidate_ids or (name, kind) in natural_keys:
        raise SystemExit(f"candidate ID/natural-key collision: {cid} {name} / {kind}")
    candidates.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                       "index_page_range": "", "suggested_type": kind, "status": "open",
                       "index_source_file": "", "sub_entry": "", "detail": detail,
                       "exclude_reason": "", "candidate_origin": "body-mention",
                       "candidate_source_ref": f"{source_segment}#L{line_no}"})
    candidate_ids.add(cid)
    natural_keys.add((name, kind))

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []
offset_cache = {}


def segment_offsets(segment_id):
    if segment_id not in offset_cache:
        meta = segment_by_id[segment_id]
        lines = source_lines_by_id[segment_id]
        offset = 0
        offsets = {}
        for n in range(meta["line_start"], meta["line_end"] + 1):
            offsets[n] = offset
            offset += len(lines[n - 1]) + 1
        offset_cache[segment_id] = offsets
    return offset_cache[segment_id]


def mention(segment_id, line, suffix, cid, surface, note="", occurrence=0):
    mid = f"m-chp9-p262-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    lines = source_lines_by_id[segment_id]
    line_text = lines[line - 1]
    start_at, pos = 0, -1
    for _ in range(occurrence + 1):
        pos = line_text.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found at {segment_id} L{line}: {surface!r}")
        start_at = pos + len(surface)
    start = segment_offsets(segment_id)[line] + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


# Mentions preserve individual source occurrences, including repeated quotations and OCR spellings.
M = [
    (P262,219,"currency-32k","cand-8544","zecchini","Currency unit in the reported annual income."),
    (P262,219,"currency-15","cand-8544","zecchini","Currency unit in the estimated subsistence figure.",1),
    (P262,219,"currency-canaletto-22","cand-8544","zecchini","Currency unit in Canaletto's initial price.",2),
    (P262,219,"currency-canaletto-120","cand-8544","zecchini","Currency unit in Canaletto's later price.",3),
    (P262,219,"currency-carriera-50","cand-8544","zecchini","Currency unit in Carriera's miniature price.",4),
    (P262,219,"foreign-competition","cand-8568","foreign competition","Haskell's explanation for high prices in the most successful cases."),
    (P262,219,"canaletto-price","cand-0513","Canaletto","Use the index entry for prices pending S3 identity alignment."),
    (P262,219,"carriera-price","cand-0586","Rosalba Carriera","Use the index entry for prices pending S3 identity alignment."),
    (P262,220,"piazzetta-price","cand-1919","Piazzetta","Use the index entry for prices pending S3 identity alignment."),
    (P262,220,"angelo-custode","cand-8569","Angelo Custode","Work title as named by Haskell."),
    (P262,220,"currency-angelo","cand-8544","zecchini","Currency unit in Piazzetta price report."),
    (P262,221,"tiepolo-price","cand-2603","Tiepolo","Use the index entry for prices pending S3 identity alignment."),
    (P262,221,"martyrdom","cand-8570","Martyrdom of St John the Bishop","Specific work as named by Haskell; no external catalogue verification."),
    (P262,221,"bergamo-cathedral","cand-8565","Bergamo Cathedral","Building named as the work's setting; exact cathedral identity unresolved."),
    (P262,221,"currency-tiepolo-same-sum","cand-2062","same sum","Cross-reference to the 100-zecchini valuation on the preceding line."),
    (P262,221,"currency-tiepolo-500","cand-8544","zecchini","Currency unit in the 1754 payment report."),
    (P262,221,"pieta-frescoes","cand-8550","frescoes","Unnamed fresco group in the church dome."),
    (P262,221,"church-pieta","cand-8551","church of the Piet","OCR span; page image reads Pietà."),
    (P262,221,"venice-in-pieta-location","cand-2743","Venice","Existing page-specific Venice candidate reused."),
    (P262,222,"new-nobles","cand-8134","new nobles","Collective new entrants to the Venetian nobility; no individuals named."),
    (P262,222,"enrolment-procedure","cand-8135","enrolled","Admission procedure, not an identified institution."),
    (P262,222,"noble-entry-amount","cand-8544","zecchini","Currency unit in the nearly 30,000 payment."),
    (P262,222,"grassi-family","cand-1228","Grassi","Family candidate; keep distinct from the collection object."),
    (P262,222,"grassi-collection","cand-1227","collection of pictures","The collection attributed to the Grassi family."),
    (P262,222,"aristocracy","cand-8108","aristocracy","Venetian nobility as a social estate."),
    (P262,222,"old-families","cand-8137","older families","Collective old Venetian patrician families."),
    (P262,222,"titian","cand-2630","Titian","Named among the old masters in Haskell's account."),
    (P262,222,"veronese","cand-2755","Veronese","Named among the old masters; candidate is Paolo Veronese."),
    (P262,222,"bassano","cand-0257","Bassano","Named among the old masters; indexed as Jacopo Bassano."),
    (P262,222,"van-dyck","cand-0958","Van Dyck","Named among the old masters; indexed as Anthony van Dyck."),
    (P262,222,"guido-reni","cand-2124","Guido Reni","Named among the old masters."),
    (P262,222,"guercino-ocr","cand-1258","GuerCino","OCR capitalization retained; scan reads Guercino."),
    (P262,222,"schiavone","cand-2395","Schiavone","Named among the old masters; indexed as Andrea Schiavone."),
    (P262,222,"fetti","cand-1033","Fetti","Printed source form; candidate follows index form Feti, Domenico."),
    (P262,222,"rubens","cand-2293","Rubens","Named among the old masters; indexed as Peter Paul Rubens."),
    (P262,222,"ancestral-portraits","cand-8564","ancestral portraits","Rhetorical question; no portraits or makers are identified."),
    (P262,223,"labia-family","cand-1349","Labia","Existing family candidate reused."),
    (P262,223,"labia-collection","cand-1348","choice of pictures","Labia collection context; no exact collection identity implied."),
    (P262,223,"tiepolo-labia","cand-2593","Tiepolo","Indexed p.262 Labia frescoes and portraits entry."),
    (P262,223,"labia-portrait","cand-8552","portrait","Unidentified Tiepolo portrait in the Labia collection."),
    (P262,223,"labia-frescoes","cand-8553","frescoes","Unidentified Tiepolo frescoes in the Labia collection."),
    (P262,223,"cignaroli-labia","cand-0755","Cignaroli","Page-specific index entry for work for Labia."),
    (P262,223,"giovanelli-family","cand-7617","Giovanelli","Existing family candidate from p.214 reused; S3 must align."),
    (P262,223,"tiepolo-giovanelli","cand-2569","Tiepolo","Artist named in the Giovanelli sentence.",1),
    (P262,223,"piazzetta-giovanelli","cand-1901","Piazzetta","Artist named in the Giovanelli sentence."),
    (P262,223,"canaletto-giovanelli","cand-0498","Canaletto","Artist named in the Giovanelli sentence."),
    (P262,224,"zuccarelli-giovanelli","cand-2879","Zuccarelli","Artist named in the Giovanelli sentence."),
    (P262,225,"de-la-lande-page","cand-8546","De La Lande","Citation to tables used for currency conversion."),
    (P262,225,"zecchino-unit","cand-8544","zecchino","Singular name of the monetary unit."),
    (P262,226,"visconti-page","cand-8465","Pietro Visconti","Existing cited-person candidate from p.259 note 3."),
    (P262,226,"visconti-letter","cand-8466","letter of Pietro Visconti","Existing published-letter locator reused."),
    (P262,226,"berengo-page","cand-8545","Berengo, 1956, p. 86","Citation locator visible in OCR and confirmed against the page image."),
    (P262,227,"ceiling-paintings","cand-8554","oil paintings","Unnamed paintings inserted into ceilings at the palace."),
    (P262,228,"palazzo-giovanelli","cand-8555","Palazzo Giovanelli","Place named in the nested Biffi quotation."),
    (P262,228,"biffi","cand-0373","Gio. Battista Biffi","Existing indexed person candidate; printed short form retained."),
    (P262,228,"paolo-quote","cand-8558","Paolo","Given-name-only painter in Biffi's quotation."),
    (P262,228,"palma-quote","cand-8559","Palma","Surname-only painter in Biffi's quotation."),
    (P262,228,"tiepolo-quote","cand-2569","Tiepolo","Painter named in Biffi's quotation."),
    (P262,228,"farinato-quote","cand-8560","Farinato","Surname form in Biffi's quotation."),
    (P262,228,"greek-panels","cand-8563","Le tavole greche del quattrocento","Unidentified group of panels in the quoted inventory."),
    (P262,228,"tempesta-quote","cand-8561","Tempesta","Surname-only artist named in Biffi's quotation."),
    (P262,228,"zelotti-quote","cand-8562","Zelotti","Surname-only artist named in Biffi's quotation."),
    (P262,228,"canaletto-quote","cand-0498","Canaletto","Artist named in Biffi's quotation."),
    (P262,228,"piazzetta-quote","cand-1901","Piazzetta","Artist named in Biffi's quotation."),
    (P262,228,"zuccarelli-quote","cand-2879","Zuccharelli","OCR form; page image reads Zuccharelli in the quotation."),
    (P262,229,"biblioteca-cremona","cand-8556","Biblioteca Governativa","Institution named as repository."),
    (P262,229,"cremona","cand-7660","Cremona","Place of the named repository."),
    (P262,229,"biffi-ms","cand-8557","MSS. aa.I.4.1","Manuscript locator as OCRed; page image shows spaced punctuation."),
    (P262,229,"venturi","cand-2751","Professor Franco Venturi","Existing indexed person candidate; identity not independently revisited."),
    (P262,229,"correspondence-ref","cand-8557","this correspondence","Reference to Biffi's correspondence shown to Haskell on microfilm."),
    (NOTES,412,"meschini","cand-8547","Meschini, 1806, II, p. 105","Citation locator for the Grassi statement."),
    (NOTES,413,"labia-inventory-notes","cand-8548","unpublished Labia inventory of 1749","Canonical note 5 locator."),
    (NOTES,413,"tiepolo-inventory-notes","cand-2593","The Tiepolos","Inventory descriptions for unnamed works."),
    (NOTES,413,"ritratto-notes","cand-8566","Ritratto con cristallo","Inventory description; identity unverified."),
    (NOTES,413,"palla-notes","cand-8567","Una Palla","Inventory description; identity unverified."),
    (NOTES,413,"cignaroli-notes","cand-0754","Cignaroli","Canonical note 5 reference."),
    (NOTES,413,"bevilacqua-notes","cand-8549","Bevilacqua","Surname-only reference."),
    (VISUAL,1,"berengo-visual-person","cand-8291","Berengo","Author surname in the visually transcribed note 2."),
    (VISUAL,1,"berengo-visual-locator","cand-8545","Berengo, 1956, p. 86.","Exact visual transcription of the omitted consolidated note 2."),
]
for row in M:
    mention(*row)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="authorial narrative", extras=None):
    sid = f"st-chp9-p262-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement span out of segment: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 262,
         "pdf_physical_page": PHYSICAL_PAGE, "claim": claim, "speaker": speaker,
         "text_layer": text_layer, "qualification": qualification,
         "mentioned_candidate_ids": list(dict.fromkeys(x for x in mentioned if x))}
    if marker is not None:
        q["footnote_marker"] = marker
    if extras:
        q.update(extras)
    new_statements.append({"statement_id": sid, "segment_id": segment_id,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": q,
                           "original_quote": quote(segment_id, first, last), "origin": "book",
                           "source_file": meta["source_file"]})


def body(suffix, first, last, subject, obj, predicate, claim, qualification, mentioned,
         marker=None, speaker="Haskell", text_layer="authorial narrative", extras=None):
    statement(suffix, P262, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker, speaker, text_layer, extras)


def note(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
         mentioned, marker, *, speaker="Haskell's footnote", text_layer="footnote claim", extras=None):
    statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker, speaker, text_layer, extras)


body("foscarini-income",219,219,"cand-1057",None,
     "foscarini_family_income_reported_at_32000_zecchini_per_year",
     "The continuation reports that the Foscarini had an annual income of 32,000 zecchini.",
     "The sentence continues p.261 L216; Haskell attributes the estimate to a 1749 letter by Pietro Visconti in note 1. It remains a reported estimate, not verified household accounts.",
     ["cand-1057","cand-8544","cand-8465","cand-8466"],marker=1,
     extras={"cross_reference_segments":[{"segment_id":P261,"source_line_start":216,"source_line_end":216},{"segment_id":NOTES,"source_line_start":410,"source_line_end":410}],
             "ocr_corrections":[{"source_line":218,"ocr":"[Page 202]","print":"[Page 262]","basis":"CHP-9.pdf physical page 24."}]})
body("subsistence-estimate",219,219,None,"cand-8544",
     "bare_subsistence_estimated_at_15_zecchini_per_year",
     "Bare subsistence is estimated at about 15 zecchini a year.",
     "The wording is explicitly an estimate attributed to a cited source; the cited Berengo page was not independently consulted.",
     ["cand-8544","cand-8545"],marker=2,
     extras={"cross_reference_segments":[{"segment_id":P262,"source_line_start":226,"source_line_end":226},{"segment_id":VISUAL,"source_line_start":1,"source_line_end":1}]})
body("canaletto-career-price",219,219,"cand-0513","cand-8544",
     "canaletto_picture_price_rose_from_22_to_120_zecchini_within_ten_years",
     "At the outset of his career Canaletto charged about 22 zecchini per picture and within ten years had raised the price to 120, which Haskell says was considered exorbitant.",
     "The passage gives approximate amounts and a relative career interval, not calendar dates; foreign competition and cosmopolitan demand are Haskell's framing.",
     ["cand-0513","cand-8544","cand-2062"])
body("carriera-miniature-and-pastel-prices",219,219,"cand-0586","cand-8544",
     "carriera_miniature_50_zecchini_pastel_20_or_30",
     "A miniature by Rosalba Carriera cost 50 zecchini, while a pastel cost 20 or 30 depending on whether it included one or both hands or flowers.",
     "The price and format details are reported by Haskell; no specific miniature or pastel is identified.",
     ["cand-0586","cand-8544","cand-2062"])
body("small-fashionable-works-price-comparison",219,219,None,"cand-2062",
     "small_fashionable_works_cost_more_relative_to_large_history_paintings_and_decorations",
     "Haskell contrasts expensive small works by fashionable artists serving a cosmopolitan clientele with comparatively less expensive large history paintings and full-scale decorations.",
     "Comparative rather than a claim that every large work cost less; no universal price series is supplied.",
     ["cand-2062","cand-0513","cand-0586","cand-1919","cand-2603"])
body("foreign-competition-price-context",219,219,None,"cand-8568",
     "foreign_competition_kept_prices_high_for_most_successful_artists",
     "Haskell says that in the most successful cases foreign competition kept artists' prices very high.",
     "This is the author's market explanation; the passage supplies no comparative price data or measure of competition.",
     ["cand-8568","cand-2062","cand-0513","cand-0586"])
body("piazzetta-angelo-custode-price",220,220,"cand-1919","cand-8569",
     "piazzetta_angelo_custode_valued_at_about_100_zecchini",
     "Piazzetta's large picture of the Angelo Custode was valued at about 100 zecchini.",
     "The source reports a valuation, not a documented sale; the cited price note is an internal cross-reference.",
     ["cand-8569","cand-1919","cand-8544","cand-2062"],
     extras={"relation_candidate":True})
body("tiepolo-martyrdom-payment",221,221,"cand-2603","cand-8570",
     "tiepolo_paid_100_zecchini_for_martyrdom_in_1743_after_paying_material_costs",
     "In 1743 Tiepolo received the same 100 zecchini for the Martyrdom of St John the Bishop in Bergamo Cathedral, while being required to pay for the canvas and pigments himself.",
     "The amount is linked to the preceding Piazzetta valuation; this is Haskell's report, with no contract or payment record independently checked.",
     ["cand-8570","cand-2603","cand-8544","cand-8565","cand-2062"],marker=3,
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":411,"source_line_end":411}]})
body("tiepolo-pieta-dome-payment",221,221,"cand-2603","cand-8550",
     "tiepolo_received_500_zecchini_for_pieta_dome_frescoes_in_1754",
     "In 1754 Tiepolo received 500 zecchini for his frescoes in the dome of the church of the Pietà in Venice.",
     "The amount and commission are reported by Haskell; exact fresco scope and payment evidence are not supplied.",
     ["cand-8550","cand-8551","cand-2569","cand-8544","cand-2062"],marker=3,
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":411,"source_line_end":411}],
             "ocr_corrections":[{"source_line":221,"ocr":"domeof","print":"dome of","basis":"CHP-9.pdf physical page 24."}]})
body("new-nobles-enrolment",222,222,"cand-8134","cand-8135",
     "new_nobles_paid_nearly_30000_zecchini_for_enrolment",
     "Haskell says new nobles had to pay nearly 30,000 zecchini to be enrolled.",
     "The passage gives an approximate collective figure and does not identify particular entrants or individual payments.",
     ["cand-8134","cand-8135","cand-8544","cand-2741"])
body("new-nobles-collection-paradox",222,222,"cand-8134","cand-1227",
     "new_nobles_reluctance_to_buy_contemporary_pictures_is_harder_to_explain",
     "Haskell says new nobles appeared unconstrained by space or money, making their reluctance to buy contemporary pictures harder to explain.",
     "This is the author's interpretive contrast, not evidence about every new noble family.",
     ["cand-8134","cand-8544","cand-1227"])
body("gallery-as-corollary-of-nobility",222,222,"cand-8108",None,
     "extensive_gallery_described_as_necessary_corollary_of_nobility",
     "Haskell describes an extensive gallery as a necessary corollary of nobility.",
     "General authorial claim about aristocratic display, not an individual family's documented gallery inventory.",
     ["cand-8108","cand-8134"])
body("grassi-only-patrician-collection",222,222,"cand-1228","cand-1227",
     "grassi_only_patrician_family_said_to_build_collection_in_eighteenth_century",
     "Haskell identifies the Grassi as the only patrician family to have built up a picture collection in the eighteenth century.",
     "Retain the author's striking but bounded claim; it is not a verified census of every Venetian collection.",
     ["cand-1228","cand-1227"])
body("grassi-entry-1699",222,222,"cand-1228","cand-8135",
     "grassi_bought_their_way_into_aristocracy_in_1699",
     "Haskell says the Grassi bought their way into the aristocracy in 1699.",
     "The claim is attributed to Haskell and is linked to note 4; no underlying record was independently consulted.",
     ["cand-1228","cand-8135","cand-8547"],marker=4,
     extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":412,"source_line_end":412}],
             "relation_candidate":True,
             "ocr_corrections":[{"source_line":222,"ocr":"seem��deliberately, perhaps, so as to emphasise their ancient lineage��-to","print":"seem—deliberately, perhaps, so as to emphasise their ancient lineage—to","basis":"CHP-9.pdf physical page 24."}]})
body("grassi-old-masters-preference",222,222,"cand-1228","cand-1227",
     "grassi_may_have_ignored_contemporary_artists_to_emphasise_ancient_lineage_and_chose_old_masters",
     "Haskell says the Grassi seem—deliberately, perhaps, to emphasise ancient lineage—to have ignored contemporary artists and instead turned to old masters found in older family galleries.",
     "Preserve the author's explicit uncertainty about motive; the old-master list is not a verified inventory of every Grassi holding.",
     ["cand-1228","cand-1227","cand-8137","cand-2630","cand-2755","cand-0257","cand-0958","cand-2124","cand-1258","cand-2395","cand-1033","cand-2293"],
     extras={"ocr_corrections":[{"source_line":222,"ocr":"GuerCino","print":"Guercino","basis":"CHP-9.pdf physical page 24."}]})
body("ancestral-portraits-question",222,222,None,"cand-8564",
     "haskell_poses_question_who_began_painting_ancestral_portraits",
     "Haskell asks who began painting ancestral portraits.",
     "Rhetorical question only; no maker, family, or portrait is identified.",
     ["cand-8564"])
body("labia-collection-era-and-tiepolo",223,223,"cand-1349","cand-1348",
     "labia_choice_of_pictures_described_as_less_adventurous_with_tiepolo_portrait_and_frescoes",
     "Haskell says the Labia were not much more adventurous in picture choice; their art seemed to stop at the seventeenth century's end, though they owned a Tiepolo portrait and frescoes.",
     "The phrase 'seemed to stop' is Haskell's characterization, not a claim that the family owned no later works. The portrait and frescoes remain unidentified.",
     ["cand-1349","cand-1348","cand-8552","cand-8553","cand-2593"],
     extras={"relation_candidate":True,"ocr_corrections":[{"source_line":223,"ocr":"art seemed, to stop","print":"art seemed to stop","basis":"CHP-9.pdf physical page 24."}]})
body("cignaroli-labia-employment",223,223,"cand-0754","cand-1349",
     "cignaroli_employed_by_labia_for_a_time",
     "Haskell says the Labia employed Cignaroli for a time.",
     "The duration is supplied only by footnote 5 as four years; no specific commission is named in the body sentence.",
     ["cand-0754","cand-0755","cand-1349","cand-8548"],marker=5,
     extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":413,"source_line_end":413},{"segment_id":P262,"source_line_start":227,"source_line_end":227}],
             "ocr_corrections":[{"source_line":223,"ocr":"Cignaroli for a time6","print":"Cignaroli for a time⁵","basis":"CHP-9.pdf physical page 24."}]})
body("giovanelli-purchases",223,224,"cand-7617","cand-1192",
     "giovanelli_only_family_said_to_buy_contemporary_works_by_named_artists_and_old_masters",
     "Haskell says the Giovanelli, ennobled in 1668, were the only family in this comparison to buy works by Tiepolo, Piazzetta, Canaletto and Zuccarelli as well as old masters.",
     "This is a bounded authorial comparison; the sentence does not identify individual purchases or document the family's full collection.",
     ["cand-7617","cand-1192","cand-8134","cand-2569","cand-1901","cand-0498","cand-2879"],marker=6,
     extras={"cross_reference_segments":[{"segment_id":P262,"source_line_start":228,"source_line_end":229}],
             "relation_candidate":True,
             "ocr_corrections":[{"source_line":224,"ocr":"old masters [no footnote marker]","print":"old masters⁶","basis":"CHP-9.pdf physical page 24."}]})

note("note1-currency-value-caveat",NOTES,410,410,None,None,
     "monetary_figures_do_not_adjust_for_changes_in_money_value_over_the_century",
     "Haskell warns that the monetary figures do not account for changes in the value of money at different times in the century.",
     "This note qualifies the comparisons on p.262; the specific conversion method is recorded in the page OCR at L225.",
     [],1,
     extras={"cross_reference_segments":[{"segment_id":P262,"source_line_start":225,"source_line_end":225}]})
note("note1-currency-table-locator",P262,225,225,None,"cand-8546",
     "currency_converted_using_de_la_lande_tables_volume_vii_page_81",
     "Haskell says he converted the currencies to zecchini using the tables in De La Lande, volume VII, page 81.",
     "Citation locator only; the tables were not independently consulted. The warning about century-wide changes in monetary value is preserved in consolidated note line 410.",
     ["cand-8544","cand-8546"],1,text_layer="footnote citation",
     extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":410,"source_line_end":410}]})
note("note1-visconti-income-source",P262,226,226,"cand-8465","cand-8466",
     "foscarini_income_estimate_derived_from_visconti_1749_letter",
     "Haskell says the Foscarini income estimate is derived from a letter by Pietro Visconti, who was working there in 1749.",
     "The letter is identified through Haskell's citation at p.259 note 3; it was not independently consulted.",
     ["cand-1057","cand-8465","cand-8466"],1,text_layer="footnote claim",
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":P261,"source_line_start":216,"source_line_end":216}]})
note("note2-berengo-subsistence-locator",P262,226,226,"cand-8291","cand-8545",
     "citation_locator_for_bare_subsistence_estimate",
     "Haskell cites Berengo, 1956, p.86 for the estimate of bare subsistence.",
     "Citation locator only; the work and page were not independently consulted. The same note is preserved as a one-line visual transcription because it was omitted from the consolidated OCR notes segment.",
     ["cand-8291","cand-8545"],2,text_layer="footnote citation",
     extras={"cross_reference_segments":[{"segment_id":VISUAL,"source_line_start":1,"source_line_end":1}]})
note("note3-price-crossreferences",NOTES,411,411,None,"cand-2062",
     "internal_cross_references_for_price_examples",
     "Haskell's note 3 directs readers to p.264 note 6, p.273 note 1, p.276 note 1 and p.292 note 4 for the prices mentioned.",
     "Internal citation trail only; none of the referenced notes were independently consulted here.",
     ["cand-2062"],3,text_layer="footnote citation")
note("note4-meschini-grassi-locator",NOTES,412,412,"cand-1228","cand-8547",
     "citation_locator_for_grassi_entry_into_aristocracy",
     "Haskell's note 4 cites Meschini, 1806, volume II, page 105 in connection with the Grassi statement.",
     "Citation locator only; the cited work and page were not independently consulted.",
     ["cand-1228","cand-8547"],4,text_layer="footnote citation")
note("note5-labia-inventory",NOTES,413,413,"cand-1349","cand-8548",
     "unpublished_1749_labia_inventory_cited_for_tiepolo_entries_and_cignaroli",
     "Haskell cites an unpublished 1749 Labia inventory, describing two Tiepolo entries as Ritratto con cristallo and Una Palla and directing readers to Bevilacqua for Cignaroli.",
     "The inventory and Bevilacqua reference were not independently consulted; preserve the inventory descriptions rather than assigning catalogue identities.",
     ["cand-1349","cand-8548","cand-2593","cand-8566","cand-8567","cand-8549","cand-0754"],5,
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":P262,"source_line_start":227,"source_line_end":227}]})
note("note5-cignaroli-ceiling-paintings",P262,227,227,"cand-0754","cand-8554",
     "cignaroli_worked_for_labia_four_years_and_some_ceiling_paintings_remain_in_situ",
     "Haskell says Cignaroli worked for the Labia for four years and that some oil paintings he inserted into palace ceilings remained in situ.",
     "The duration and survival statement are reported through Haskell's note; the inventory and present condition were not independently checked.",
     ["cand-0754","cand-1349","cand-8554"],5,text_layer="footnote claim",
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":413,"source_line_end":413}]})
note("note6-biffi-palazzo-collection",P262,228,228,"cand-0373","cand-8555",
     "biffi_1773_described_pictures_in_palazzo_giovanelli_upper_rooms",
     "In a 1773 quotation, Giambattista Biffi describes the upper mezzanine rooms of Palazzo Giovanelli as crowded with pictures by Paolo, Palma, Tiepolo and Farinato, Greek Quattrocento panels, and numerous originals by Tempesta, Zelotti, Canaletto, Piazzetta and 'my Zuccarelli'.",
     "Nested quotation cited by Haskell from a manuscript locator; it is Biffi's description, not an independently checked inventory. Paolo, Palma, Farinato, Tempesta and Zelotti remain unresolved at S2.",
     ["cand-0373","cand-8555","cand-8558","cand-8559","cand-2569","cand-8560","cand-8563","cand-8561","cand-8562","cand-0498","cand-1901","cand-2879"],6,
     speaker="Giambattista Biffi, as quoted by Haskell",text_layer="nested archival quotation",
     extras={"cross_reference_segments":[{"segment_id":P262,"source_line_start":229,"source_line_end":229}]})
note("note6-biffi-manuscript-locator",P262,229,229,"cand-8557","cand-8556",
     "biffi_correspondence_located_at_biblioteca_governativa_cremona_mss_aa_i_4_1",
     "Haskell gives Biblioteca Governativa, Cremona, MSS. aa.I.4.1 as the location for the correspondence quoted from Biffi and thanks Professor Franco Venturi for showing him microfilms he had made.",
     "Repository and manuscript wording are reported by Haskell; the manuscript and microfilms were not independently examined.",
     ["cand-8557","cand-8556","cand-7660","cand-2751"],6,text_layer="footnote locator and author acknowledgement",
     extras={"relation_candidate":True,"ocr_corrections":[{"source_line":229,"ocr":"MSS. aa.I.4.1 am most grateful","print":"MSS. aa. I. 4. I. I am most grateful","basis":"CHP-9.pdf physical page 24."}]})

all_candidate_ids = {r["candidate_id"] for r in candidates}
if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")
for row in new_mentions:
    sid = row["segment_id"]
    start, end = int(row["start_char"]), int(row["end_char"])
    meta = segment_by_id[sid]
    text = "\n".join(source_lines_by_id[sid][n - 1] for n in range(meta["line_start"], meta["line_end"] + 1))
    if text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    refs = set(q.get("mentioned_candidate_ids", []))
    refs.update(x for x in [row.get("subject_candidate_id"), row.get("object_candidate_id")] if x)
    if not refs <= all_candidate_ids:
        raise SystemExit(f"statement foreign key error {row['statement_id']}: {refs-all_candidate_ids}")
    if row["original_quote"] != quote(row["segment_id"], q["source_line_start"], q["source_line_end"]):
        raise SystemExit(f"quote mismatch: {row['statement_id']}")

coverage_by_id[P261].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L213-216",
    "note": "Printed p.261 (CHP-9.pdf physical p.23) reviewed against scan. L213 closes p.260 L210; p.261 L216 continues at p.262 L219 and is now closed. Notes 1-6 are migrated at consolidated L404-409. Page-image OCR corrections are recorded in S2; source OCR is unchanged."})
coverage_by_id[P262].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L219-229",
    "note": "Printed p.262 (CHP-9.pdf physical p.24) reviewed against scan. L219 closes p.261 L216; all body, page-footnote text present in the OCR, and Biffi quotation lines are semantically represented. Notes 1, 3, 4 and 5 are also represented in consolidated L410-413; note 2 has a visual-transcription segment, note 6 remains anchored to page OCR L228-229. OCR corrections are recorded in S2; S0 source text is unchanged."})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L349-413; p.255 L155 continuation",
    "note": "Consolidated notes through p.262 notes 1, 3, 4 and 5 have been migrated at L410-413; p.262 note 2 is preserved in a visual-transcription segment and note 6 is anchored to the p.262 page OCR. P.255 note 1 continuation at L155 remains cross-linked to L370. Later notes from L414 remain queued."})
visual_coverage = {
    "chapter": "chp-9", "segment_id": VISUAL, "disposition": "reviewed", "migration_status": "complete",
    "source_line_ranges": "L1", "note": "One-line visual transcription of p.262 footnote 2, omitted from the consolidated OCR notes segment. The same printed locator is also represented in the p.262 page OCR; this derived segment supplies a second exact anchor only, not an independently verified source."}
coverage.append(visual_coverage)
coverage_by_id[VISUAL] = visual_coverage

# Close the exact p.261-to-p.262 sentence pointer at the first body line, not the OCR page label.
previous = next((r for r in statements if r["statement_id"] == "st-chp9-p261-foscarini-rumoured-richest"), None)
if not previous:
    raise SystemExit("missing p.261 Foscarini continuation statement")
previous["qualifiers"]["cross_reference_segments"] = [
    {"segment_id": P262, "source_line_start": 219, "source_line_end": 219}
]

summary = {
    "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"], coverage_by_id[sid]["source_line_ranges"]]
                 for sid in (P261, P262, NOTES, VISUAL)},
    "cross_page_closure": "p.261 L216 -> p.262 L219",
    "next_body_segment": "chp-9:09_CHP-9_intro:l231-238",
    "next_notes": "L414 onward",
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [p.with_name(p.name + BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for src, bak in zip(paths, backups):
        shutil.copy2(src, bak)
    try:
        write_csv(candidate_path, candidate_fields, candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for dst, bak in zip(paths, backups):
            shutil.copy2(bak, dst)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
