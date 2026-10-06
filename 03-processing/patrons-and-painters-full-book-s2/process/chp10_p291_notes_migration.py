"""Controlled S2 migration for p.291 footnotes L551-L553; dry-run unless --apply."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
BODY_SEG = "chp-10:10_CHP-10_intro:l253-266"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_LINES_SHA = "8878257f455a7a29688aaa742f00b5d099e54d6854139beb8714e1e46d599d00"
BACKUP_SUFFIX = ".bak-s2-chp10-p291-notes-20261002"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(stream.name)
    temp_path.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(stream.name)
    temp_path.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256("\n".join(source_lines[550:553]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.291 note lines L551-L553 changed")
if not source_lines[550].startswith("1 The inscription plate to Sir Isaac Newton"):
    raise SystemExit("p.291 note 1 anchor changed")
if not source_lines[551].startswith("2 Malamani, 1899, p. 142"):
    raise SystemExit("p.291 note 2 anchor changed")
if not source_lines[552].startswith("3 Letter tom McSwiny"):
    raise SystemExit("p.291 note 3 OCR anchor changed")

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9428:
    raise SystemExit(f"candidate sequence changed: {maximum}")
note_cov = cov.get(NOTES_SEG)
if not note_cov or (note_cov["disposition"], note_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes coverage changed")
if note_cov["source_line_ranges"] != "L492-550":
    raise SystemExit(f"consolidated notes range changed: {note_cov['source_line_ranges']}")
if cov.get(BODY_SEG, {}).get("migration_status") != "complete":
    raise SystemExit("p.291 body is not complete")

BODY_LINKS = {
    1: ["st-chp10-p291-inscription-plate-production"],
    2: ["st-chp10-p291-mcswiny-smith-trade"],
    3: ["st-chp10-p291-canaletto-letter-assessment"],
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(sum(BODY_LINKS.values(), [])) <= by_sid.keys():
    raise SystemExit("p.291 body footnote targets changed")
for sid, marker in ((sid, marker) for marker, ids in BODY_LINKS.items() for sid in ids):
    qualifiers = by_sid[sid].get("qualifiers", {})
    if qualifiers.get("footnote_marker") != marker or not qualifiers.get("footnote_text_pending"):
        raise SystemExit(f"p.291 body footnote state changed: {sid}")

E = {
    "boucher": "cand-0423", "carriera": "cand-0581", "john_conduitt": "cand-0820",
    "fontenelle": "cand-1050", "fontenelle_eloge": "cand-1051", "mcswiny": "cand-1466",
    "newton": "cand-1739", "tombeaux": "cand-9032", "canaletto_letter": "cand-9034",
    "malamani_existing": "cand-8664", "newton_tomb": "cand-9375", "same_date_letter": "cand-9425",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("perrot", "Joseph Perrot (designer named in p.291 note 1)", "person",
     "Haskell names Perrot as the designer of the inscription plate to Newton's monument. No independent attribution source was consulted.", 551),
    ("newton_monument", "Monument to Sir Isaac Newton referred to in p.291 note 1", "work",
     "The monument named as the subject of an inscription plate. Do not merge with cand-9375, the separately described unspecified Newton tomb, until S3 resolves the object identity.", 551),
    ("newton_inscription_plate", "Inscription plate to Sir Isaac Newton's monument (p.291 note 1)", "work",
     "Haskell describes this plate as more restrained than the others and says Joseph Perrot designed it. Keep it distinct from the monument and from the separate Newton medallion design; the plate was not independently examined.", 551),
    ("newton_medallion_page", "Newton medallion and Zodiac design above Fontenelle's Eloge (separate page; p.291 note 1)", "work",
     "Haskell says Boucher drew the medallion of Newton and signs of the Zodiac above extracts from Fontenelle's Eloge on a separate page. The exact page or design was not independently identified.", 551),
    ("malamani_person", "Malamani (surname-only author cited at p.291 note 2)", "person",
     "The note supplies only the surname and year. Possible identity with cand-8664 and other Malamani citations is deferred to the global S3 alignment.", 552),
    ("malamani_1899_p142", "Malamani, 1899, p.142 (citation locator; title unresolved)", "archive",
     "Short-form citation in p.291 note 2 for a reported 1753 letter. The cited page and full bibliographic identity were not independently checked; align with other Malamani locators in S3.", 552),
    ("carriera_letter_1753", "Unidentified-sender letter of 1753 to Rosalba Carriera (p.291 note 2)", "archive",
     "Haskell, citing Malamani 1899 p.142, reports a letter addressed to Rosalba Carriera that refers to McSwiny and an apparently unsettled account. The sender and the letter's exact contents remain unknown; neither the letter nor cited page was consulted.", 552),
]
new_candidates = []
C = {}
for index, (key, name, kind, detail, line_no) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{index:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES_SEG}#L{line_no}",
    })

SEGMENT_START, SEGMENT_END = 491, 634
segment_text = "\n".join(source_lines[SEGMENT_START - 1:SEGMENT_END])
segment_offsets = {}
offset = 0
for line_no in range(SEGMENT_START, SEGMENT_END + 1):
    segment_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1

new_mentions = []
new_mids = set()


def add_mention(local_id, line_no, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p291-notes-{local_id}"
    if mention_id in mids or mention_id in new_mids:
        raise SystemExit(f"duplicate mention: {mention_id}")
    if candidate_id not in cids | {row["candidate_id"] for row in new_candidates}:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    source_line = source_lines[line_no - 1]
    positions, start_at = [], 0
    while True:
        found = source_line.find(surface, start_at)
        if found < 0:
            break
        positions.append(found)
        start_at = found + max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = segment_offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": NOTES_SEG, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mids.add(mention_id)


add_mention("n1-inscription-plate", 551, "inscription plate", C["newton_inscription_plate"], "Separate work in the Tombeaux context; not the entire monument.")
add_mention("n1-newton-person", 551, "Sir Isaac Newton", E["newton"], "Monument subject named in Haskell's footnote.")
add_mention("n1-monument", 551, "monument", C["newton_monument"], "Keep distinct from cand-9375 until S3 identity alignment.")
add_mention("n1-perrot", 551, "Joseph Perrot", C["perrot"], "Designer named by Haskell; attribution not independently verified.")
add_mention("n1-boucher", 551, "Boucher", E["boucher"], "Existing index candidate reused.")
add_mention("n1-medallion", 551, "medallion", C["newton_medallion_page"], "Component of the separate-page design described in the footnote.")
add_mention("n1-newton-medallion", 551, "Newton", E["newton"], "Person depicted in the medallion; second mention in this note.", occurrence=1)
add_mention("n1-fontenelle", 551, "Fontenelle", E["fontenelle"], "Existing index candidate reused.")
add_mention("n1-eloge", 551, "Eloge", E["fontenelle_eloge"], "Existing index candidate for Fontenelle's Eloge in the Tombeaux reused.")

add_mention("n2-malamani", 552, "Malamani", C["malamani_person"], "Surname-only author; possible identity with cand-8664 deferred to S3.")
add_mention("n2-citation-locator", 552, "1899, p. 142", C["malamani_1899_p142"], "Citation locator; the publication was not independently consulted.")
add_mention("n2-letter-date", 552, "letter of 1753", C["carriera_letter_1753"], "Year and document type reported by Haskell through Malamani.")
add_mention("n2-carriera", 552, "Rosalba Garriera", E["carriera"], "S0 OCR form; the print scan reads Rosalba Carriera.")
add_mention("n2-mcswiny", 552, "McSwiny", E["mcswiny"], "Named in Haskell's qualified summary of the letter.")

add_mention("n3-mcswiny", 553, "McSwiny", E["mcswiny"], "Sender named in the printed note; S0 OCR reads 'tom' for 'from'.")
add_mention("n3-conduitt", 553, "John Conduits", E["john_conduitt"], "S0 OCR form; print reads John Conduitt.")
add_mention("n3-letter-date", 553, "27 September 1730", E["canaletto_letter"], "Date specified in note 3 for the body quotation; preserve conflict with the body's 1727 date.")

new_statements = []
new_sids = set()


def add_statement(local_id, line_no, subject, obj, predicate, claim, qualification,
                  mentioned, speaker, layer, marker, relation=False, citations=None,
                  corrections=None, cited_not_consulted=False, cross_reference=None):
    statement_id = f"st-chp10-p291-note{marker}-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement: {statement_id}")
    quote = source_lines[line_no - 1]
    if quote not in segment_text:
        raise SystemExit(f"source quote missing: {statement_id}")
    qualifiers = {
        "source_line_start": line_no, "source_line_end": line_no,
        "printed_page": 291, "pdf_physical_page": 20, "claim": claim,
        "speaker": speaker, "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation, "footnote_marker": marker,
        "related_body_statement_ids": BODY_LINKS[marker],
    }
    if citations:
        qualifiers["citations"] = citations
    if corrections:
        qualifiers["ocr_corrections"] = corrections
    if cross_reference:
        qualifiers["cross_reference"] = cross_reference
    if cited_not_consulted:
        qualifiers["cited_material_not_independently_consulted"] = True
    statement = {
        "statement_id": statement_id, "segment_id": NOTES_SEG,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
    }
    new_statements.append(statement)
    new_sids.add(statement_id)
    return statement_id


S = {}
S["n1-plate-monument"] = add_statement(
    "plate-monument", 551, C["newton_inscription_plate"], C["newton_monument"],
    "inscription_plate_to_newton_monument",
    "Haskell identifies the inscription plate as belonging to Sir Isaac Newton's monument and describes it as more restrained than the others.",
    "The description and comparison are Haskell's report; the plate and monument were not independently examined. Keep this monument distinct from cand-9375, the separately described intended Newton tomb, until S3 resolves identity.",
    [C["newton_inscription_plate"], E["newton"], C["newton_monument"], E["tombeaux"]],
    "Haskell, footnote", "authorial footnote describing a work", 1, relation=True,
)
S["n1-plate-designer"] = add_statement(
    "plate-designer", 551, C["newton_inscription_plate"], C["perrot"],
    "newton_monument_inscription_plate_designed_by_joseph_perrot",
    "Haskell says Joseph Perrot designed the inscription plate to Newton's monument.",
    "This is Haskell's attribution; the plate or a corroborating source was not independently examined.",
    [C["newton_inscription_plate"], C["perrot"], C["newton_monument"], E["tombeaux"]],
    "Haskell, footnote", "authorial footnote attribution", 1, relation=True,
)
S["n1-boucher-medallion"] = add_statement(
    "boucher-medallion", 551, C["newton_medallion_page"], E["boucher"],
    "newton_medallion_and_zodiac_design_drawn_by_boucher",
    "Haskell says Boucher drew a medallion of Newton and Zodiac signs above extracts from Fontenelle's Eloge, which were published on a separate page.",
    "This records Haskell's description of the separate-page design; the page and its attribution were not independently examined. Do not treat the medallion as the inscription plate or the monument itself.",
    [C["newton_medallion_page"], E["newton"], E["boucher"], E["fontenelle"], E["fontenelle_eloge"], E["tombeaux"]],
    "Haskell, footnote", "authorial footnote attribution and publication description", 1, relation=True,
)
S["n2-account-report"] = add_statement(
    "account-report", 552, E["mcswiny"], E["carriera"],
    "haskell_reports_apparently_unsettled_account_between_mcswiny_and_carriera",
    "Haskell says Malamani (1899, p.142) publishes a 1753 letter addressed to Rosalba Carriera that refers to McSwiny, who had apparently not settled some account with her.",
    "The note leaves the letter's sender, the account's nature and the exact basis of Haskell's summary unspecified. Preserve 'apparently' and 'some account'; this is a source-reported relation candidate, not a verified debt. The printed name is Carriera; S0 OCR reads Garriera. Malamani's page and the letter were not independently consulted.",
    [C["malamani_person"], C["malamani_1899_p142"], C["carriera_letter_1753"], E["carriera"], E["mcswiny"]],
    "Haskell, footnote summarizing Malamani", "authorial footnote reporting a published letter", 2,
    relation=True,
    citations=[{"source_candidate_id": C["malamani_1899_p142"], "page": "142"}],
    corrections=[{"source_line": 552, "ocr": "Garriera", "print": "Carriera", "basis": "CHP-10.pdf physical page 20"}],
    cited_not_consulted=True,
)
S["n3-letter-citation"] = add_statement(
    "letter-citation", 553, None, E["canaletto_letter"], "footnote_citation",
    "P.291 note 3 identifies the quoted McSwiny letter as addressed to John Conduitt and dated 27 September 1730, and prints a cross-reference to p.290 note 1.",
    "The body dates the quoted letter to 1727, while this note gives 27 September 1730. The printed cross-reference points to p.290 note 1, which describes a different 4 June 1729 letter; preserve the cross-reference without treating it as identity evidence. P.290 note 4 has a same-date McSwiny-Conduitt candidate (cand-9425); its identity with this Canaletto-letter candidate remains for S3.",
    [E["canaletto_letter"], E["mcswiny"], E["john_conduitt"]],
    "Haskell, footnote", "bibliographic pointer identifying quoted correspondence", 3,
    corrections=[
        {"source_line": 553, "ocr": "tom", "print": "from", "basis": "CHP-10.pdf physical page 20"},
        {"source_line": 553, "ocr": "Conduits", "print": "Conduitt", "basis": "CHP-10.pdf physical page 20"},
    ],
    cited_not_consulted=True,
    cross_reference={"printed_page": 290, "printed_note": 1, "target": "p.290 note 1"},
)

# Attach the note statements to their body markers and clear only the resolved pending flags.
note_statement_ids = {marker: [] for marker in BODY_LINKS}
for statement in new_statements:
    marker = statement["qualifiers"]["footnote_marker"]
    note_statement_ids[marker].append(statement["statement_id"])
for marker, body_ids in BODY_LINKS.items():
    for sid in body_ids:
        qualifiers = by_sid[sid]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers["footnote_segment"] = NOTES_SEG
        qualifiers["footnote_source_line"] = 550 + marker
        qualifiers["footnote_note_statement_ids"] = note_statement_ids[marker]
        qualifiers["cited_material_not_independently_consulted"] = True

trade = by_sid["st-chp10-p291-mcswiny-smith-trade"]["qualifiers"]
trade["qualification"] = (
    "Haskell reports the trade; printed p.291 note 2 cites Malamani, 1899, p.142, whose page and letter were not independently consulted. "
    "The scan reads Carriera where S0 OCR reads Garriera; the correction is recorded in S2 only."
)
trade["ocr_corrections"] = [{
    "source_line": 264, "ocr": "Garriera", "print": "Carriera",
    "basis": "CHP-10.pdf physical page 20",
}]
letter_body = by_sid["st-chp10-p291-canaletto-letter-assessment"]["qualifiers"]
letter_body["qualification"] = (
    "The quoted passage attributes these opinions to McSwiny. The body dates the letter to 1727; printed note 3 names a letter to John Conduitt dated 27 September 1730. "
    "Preserve both source statements; the cross-reference and possible match to p.290 note 4 do not settle document identity before S3."
)

by_candidate = {row["candidate_id"]: row for row in candidates}
newton_tomb_addition = (
    " P.291 note 1 also refers to a Newton monument and its inscription plate; whether that is the same object as this unspecified intended tomb remains unresolved for S3."
)
if newton_tomb_addition.strip() not in by_candidate[E["newton_tomb"]].get("detail", ""):
    by_candidate[E["newton_tomb"]]["detail"] = (by_candidate[E["newton_tomb"]].get("detail", "").rstrip() + newton_tomb_addition).strip()

body_note = cov[BODY_SEG].get("note", "")
pending_clause = "Footnotes 1-3 remain pending in the consolidated notes segment but do not duplicate into the body tables."
if pending_clause not in body_note:
    raise SystemExit("p.291 body coverage note no longer has the expected pending clause")
cov[BODY_SEG]["note"] = body_note.replace(
    pending_clause,
    "Footnotes 1-3 at L551-L553 are migrated in the consolidated notes segment and linked to their body statements; their text is not duplicated into the body tables.",
)
notes = cov[NOTES_SEG]
if "L551 onward remains pending." not in notes.get("note", ""):
    raise SystemExit("consolidated-notes coverage note changed")
notes["source_line_ranges"] = "L492-553"
notes["note"] = notes["note"].replace("L551 onward remains pending.", "L554 onward remains pending.")
notes["note"] += (
    " P.291 notes 1-3 at L551-L553 are migrated and linked to body markers 1-3. Note 1 records Perrot's plate attribution and Boucher's separate-page Newton medallion design; "
    "the Newton monument, inscription plate, and medallion design remain separate work candidates. Note 2 reports a 1753 Carriera letter through Malamani 1899 p.142; "
    "the sender is unidentified and the apparently unsettled account remains a qualified relation candidate. Note 3's print reads 'from'/'Conduitt' where S0 OCR reads 'tom'/'Conduits'; "
    "its 1730 date conflicts with the body's 1727 date, and its printed cross-reference to p.290 note 1 does not identify the same letter. The possible match with the same-date p.290 note 4 candidate is deferred to S3."
)

new_candidate_ids = {row["candidate_id"] for row in new_candidates}
all_candidate_ids = cids | new_candidate_ids
for mention in new_mentions:
    if mention["candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"unresolved mention candidate: {mention['mention_id']}")
by_segment = {}
for mention in new_mentions:
    by_segment.setdefault(mention["segment_id"], []).append(mention)
for segment_id, rows in by_segment.items():
    rows.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"])))
    for left, right in zip(rows, rows[1:]):
        if int(right["start_char"]) < int(left["end_char"]):
            raise SystemExit(f"overlapping mention anchors: {left['mention_id']} / {right['mention_id']}")
for statement in new_statements:
    for cid in (statement["subject_candidate_id"], statement["object_candidate_id"]):
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"unknown statement endpoint: {statement['statement_id']} {cid}")
    for cid in statement["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in all_candidate_ids:
            raise SystemExit(f"unknown statement mention candidate: {statement['statement_id']} {cid}")
    for citation in statement["qualifiers"].get("citations", []):
        if citation["source_candidate_id"] not in all_candidate_ids:
            raise SystemExit(f"unknown citation candidate: {statement['statement_id']}")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the validated p.291 note migration")
args = parser.parse_args()
print(json.dumps({
    "mode": "APPLY" if args.apply else "DRY-RUN",
    "source_segment": NOTES_SEG,
    "new_candidates": [row["candidate_id"] for row in new_candidates],
    "new_candidate_count": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "body_markers_linked": {str(marker): len(ids) for marker, ids in BODY_LINKS.items()},
    "coverage": {"notes_ranges": notes["source_line_ranges"], "notes_status": notes["migration_status"]},
    "ocr_corrections": [
        "L552 Garriera -> printed Carriera",
        "L553 tom -> printed from",
        "L553 Conduits -> printed Conduitt",
        "body L264 Garriera -> printed Carriera",
    ],
}, ensure_ascii=False, indent=2))
if not args.apply:
    print("dry-run only; no tables written")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
write_csv(cp, cf, candidates + new_candidates)
write_csv(mp, mf, mentions + new_mentions)
write_jsonl(sp, statements + new_statements)
write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
print(f"applied; four recovery copies use suffix {BACKUP_SUFFIX}")
