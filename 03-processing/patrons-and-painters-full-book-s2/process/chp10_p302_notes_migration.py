"""Controlled S2 migration for p.302 notes 1-5; dry-run unless --apply."""
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
VISUAL_SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro_p302_note4_visual-transcription.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
VISUAL_SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro_p302_note4_visual-transcription.md"
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
P302_BODY = "chp-10:10_CHP-10_intro:l391-400"
VISUAL_SEG = "chp-10:10_CHP-10_intro_p302_note4_visual-transcription:l1-1"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTE_LINES_SHA = "ba3dc12fb0f12fb187481f46ea3b02096fe50e50925891b2854b6720bcd19a16"
EXPECTED_VISUAL_TEXT_SHA = "86c3578555ec197c2e6d5048f6c7f431f31a9974558a79809957744c9bdd88ce"
EXPECTED_MAX_CANDIDATE = 9518
BACKUP_SUFFIX = ".bak-s2-chp10-p302-notes-20261002"


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
        temp = Path(stream.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(stream.name)
    temp.replace(path)


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write reviewed rows after all preconditions pass")
args = parser.parse_args()

source_bytes = SOURCE.read_bytes()
if hashlib.sha256(source_bytes).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("canonical S0 asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
note_text = "\n".join(source_lines[594:599])
if digest(note_text) != EXPECTED_NOTE_LINES_SHA:
    raise SystemExit("p.302 note lines L595-L599 changed")
visual_text = VISUAL_SOURCE.read_text(encoding="utf-8-sig").strip()
if digest(visual_text) != EXPECTED_VISUAL_TEXT_SHA:
    raise SystemExit("p.302 visual transcription changed")

cp, mp, sp, vp, segp = [
    TABLES / name for name in
    ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv", "segments.jsonl")
]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
segments = read_jsonl(segp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
seg_by_id = {row["segment_id"]: row for row in segments}
max_id = max(int(re.search(r"(\d+)$", row["candidate_id"]).group(1)) for row in candidates)
if max_id != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: {max_id}")
for seg, expected in (
    (NOTES_SEG, ("reviewed", "partial", "L492-594")),
    (P302_BODY, ("reviewed", "partial", "L391-399")),
):
    row = cov.get(seg)
    actual = (row["disposition"], row["migration_status"], row["source_line_ranges"]) if row else None
    if actual != expected:
        raise SystemExit(f"coverage changed: {seg}: {actual}")
if VISUAL_SEG not in seg_by_id or VISUAL_SEG in cov:
    raise SystemExit("visual transcript segment is missing or already has coverage")
if seg_by_id[VISUAL_SEG]["source_file"] != VISUAL_SOURCE_FILE:
    raise SystemExit("visual transcript segment points to an unexpected source")
if any(row["segment_id"] == NOTES_SEG and 595 <= int(row.get("qualifiers", {}).get("source_line_start", 0)) <= 599 for row in statements):
    raise SystemExit("p.302 notes already have statements")

body_by_id = {row["statement_id"]: row for row in statements}
BODY_LINKS = {
    1: ["st-chp10-p302-james-adam-criticism"],
    2: ["st-chp10-p302-boccage-palace-english-taste"],
    3: ["st-chp10-p302-smith-ricci-picture-style"],
    4: ["st-chp10-p302-seven-ricci-pictures-and-cignani-cartoons"],
    5: ["st-chp10-p302-possible-turin-series-connection"],
}
for marker, ids in BODY_LINKS.items():
    for sid in ids:
        row = body_by_id.get(sid)
        if not row or row["segment_id"] != P302_BODY:
            raise SystemExit(f"p.302 body marker target is missing: {sid}")
        if row["qualifiers"].get("footnote_marker") != marker or row["qualifiers"].get("footnote_text_pending") is not True:
            raise SystemExit(f"p.302 body marker {marker} is not pending as expected: {sid}")

REUSED = {
    "james_adam": "cand-0011", "robert_adam": "cand-0012", "boccage": "cand-0380",
    "blunt": "cand-5902", "burlington": "cand-5903", "gherardi": "cand-1155",
    "muratori": "cand-1717", "estense_letters": "cand-9498", "estense": "cand-8539",
    "galleria_volume": "cand-8231", "cignani": "cand-0748", "ricci_holdings": "cand-9189",
    "ricci_nt_group": "cand-9190", "cignani_group": "cand-9191", "1749_publication": "cand-9192",
    "turin_series": "cand-9193", "blunt_1957": "cand-9340",
}
if any(cid not in cids for cid in REUSED.values()):
    raise SystemExit("a required existing candidate is missing")
expected_details = {
    "cand-8231": "Publication identified by the p.251 note; article-level citation only.",
    "cand-9192": "Haskell says the New Testament pictures and Cignani cartoons were engraved and described in 1749; publication title and exact contents remain unresolved.",
    "cand-9340": "Matched to the joint local bibliography entry. P.284 note 5 cites pp.61–63 and p.300 note 2 cites pp.137 ff.; neither cited passage nor the book was independently consulted.",
    "cand-9498": "P.300 note 3 points to an unspecified plural set of letters and Chapter 13. Keep this locator distinct from individually cited dated Gherardi–Muratori letters; the correspondence was not consulted.",
}
by_cid = {row["candidate_id"]: row for row in candidates}
for cid, expected in expected_details.items():
    if by_cid[cid]["detail"] != expected:
        raise SystemExit(f"candidate changed since preflight: {cid}")

NEW_SPECS = [
    (
        "james_robert_adam_letter",
        "Letter from James Adam to Robert Adam dated 20 August 1760 (copy shown by John Fleming)",
        "archive",
        "P.302 note 1 identifies a letter from James to Robert Adam dated 20 August 1760 and says John Fleming showed Haskell a copy. No repository or manuscript identifier is supplied; the letter and copy were not independently consulted.",
        NOTES_SEG + "#L595",
    ),
    (
        "john_fleming",
        "John Fleming (named as showing Haskell a copy of the James–Robert Adam letter)",
        "person",
        "Named by Haskell in p.302 note 1 as the person who showed him a copy of the 20 August 1760 letter. Identity with the surname-only Fleming candidate cand-5929 is unresolved for S3.",
        NOTES_SEG + "#L595",
    ),
    (
        "boccage_letters_vol1",
        "Mme de Boccage, Letters concerning England, Holland and Italy, vol. I (London, 1770; cited p.146)",
        "archive",
        "P.302 note 2 cites Mme du Boccage, volume I, p.146. The local bibliography has a matching two-volume 1770 title; this is a possible bibliography match, not independent consultation of the cited passage.",
        NOTES_SEG + "#L596",
    ),
    (
        "blunt_ricci_royal_collections",
        "Anthony Blunt, Pictures by Sebastiano and Marco Ricci in the Royal Collections (Burlington Magazine, 1946–1947)",
        "archive",
        "P.302 note 3 directs readers to the two-part article. The local bibliography gives the matching title and author, 1946 pp.263–268 and 1947 pp.101–102; Haskell's note cites pp.262–268 and p.101, so the page ranges differ. Neither installment was independently consulted.",
        NOTES_SEG + "#L597",
    ),
    (
        "anonymous_cignani_galleria_passage",
        "Anonymous passage on Cignani in La Galleria di Minerva, volume VI (Venice, 1708), p.83",
        "archive",
        "P.302 note 4 quotes an anonymous writer's remark about Cignani and locates it at volume VI, 1708, p.83. This matches the issue/page cited for cand-8230 in p.251, but identity with that article is not established; neither item was independently consulted.",
        VISUAL_SEG + "#L1",
    ),
]
new_candidates = []
C = {}
for num, (key, name, kind, detail, source_ref) in enumerate(NEW_SPECS, max_id + 1):
    cid = f"cand-{num:04d}"
    if cid in cids or any(row["canonical_name"].casefold() == name.casefold() for row in candidates):
        raise SystemExit(f"candidate duplicate: {cid} / {name}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": source_ref,
    })

source_by_id = {row["segment_id"]: row for row in segments}
def get_segment_text(segment_id):
    row = source_by_id[segment_id]
    lines = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    return "\n".join(lines[row["line_start"] - 1:row["line_end"]])

note_segment_text = get_segment_text(NOTES_SEG)
visual_segment_text = get_segment_text(VISUAL_SEG)
if note_segment_text != "\n".join(source_lines[490:634]) or visual_segment_text != visual_text:
    raise SystemExit("segment text differs from the preflighted source")

line_offsets = {}
offset = 0
for line_no in range(491, 635):
    line_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1
new_mentions = []
new_statements = []
new_mids = set()
new_sids = set()
all_cids = cids | {row["candidate_id"] for row in new_candidates}


def add_mention(local_id, segment_id, line_no, surface, candidate_id, note="", source_lines_for_segment=None, base_line=1):
    mention_id = "m-chp10-p302-" + local_id
    if mention_id in mids or mention_id in new_mids:
        raise SystemExit(f"duplicate mention id: {mention_id}")
    if candidate_id not in all_cids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    if segment_id == NOTES_SEG:
        local_lines = source_lines
        local_start = line_offsets[line_no]
        segment_text = note_segment_text
    else:
        local_lines = source_lines_for_segment or VISUAL_SOURCE.read_text(encoding="utf-8-sig").splitlines()
        local_start = 0
        segment_text = visual_segment_text
    line = local_lines[line_no - 1] if segment_id == NOTES_SEG else local_lines[line_no - base_line]
    positions, cursor = [], 0
    while True:
        found = line.find(surface, cursor)
        if found < 0:
            break
        positions.append(found)
        cursor = found + max(1, len(surface))
    if len(positions) != 1:
        raise SystemExit(f"expected one exact occurrence of {surface!r} on line {line_no}, found {len(positions)}")
    start = local_start + positions[0]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mids.add(mention_id)


def add_statement(local_id, marker, predicate, claim, subject=None, obj=None, mentioned=(),
                  relation=False, speaker="Haskell, footnote", layer="footnote citation",
                  qualification="", citations=(), related_body_ids=(), segment_id=NOTES_SEG,
                  start_line=None, end_line=None, source_file=SOURCE_FILE, extra=None):
    statement_id = "st-chp10-p302-note" + str(marker) + "-" + local_id
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement id: {statement_id}")
    if start_line is None:
        start_line = marker_line[marker]
    if end_line is None:
        end_line = start_line
    if segment_id == NOTES_SEG:
        original_quote = "\n".join(source_lines[start_line - 1:end_line])
        printed_page, physical_page = 302, 31
    else:
        original_quote = visual_segment_text
        printed_page, physical_page = 302, 31
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": printed_page, "pdf_physical_page": physical_page,
        "claim": claim, "speaker": speaker, "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation, "footnote_marker": marker,
        "footnote_text_pending": False,
        "related_body_statement_ids": list(related_body_ids),
    }
    if citations:
        qualifiers["citations"] = list(citations)
        qualifiers["cited_material_not_independently_consulted"] = True
    if extra:
        qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": original_quote, "origin": "book", "source_file": source_file,
    }
    new_statements.append(row)
    new_sids.add(statement_id)
    return statement_id


marker_line = {1: 595, 2: 596, 3: 597, 4: 598, 5: 599}
# Note 1: the footnote abbreviates James Adam to James and thanks John Fleming for showing a copy.
add_mention("n1-james", NOTES_SEG, 595, "James", REUSED["james_adam"], "Footnote short form; body line 392 names James Adam.")
add_mention("n1-robert-adam", NOTES_SEG, 595, "Robert Adam", REUSED["robert_adam"], "Recipient index candidate from the p.301 entry; another Robert Adam index candidate remains for S3.")
add_mention("n1-letter-coreference", NOTES_SEG, 595, "this letter", C["james_robert_adam_letter"], "Corefers to the letter identified at the start of the note.")
add_mention("n1-john-fleming", NOTES_SEG, 595, "John Fleming", C["john_fleming"], "Acknowledged for showing Haskell a copy; identity with surname-only Fleming remains unresolved.")
# Note 2: local bibliography supplies a possible full title for the short citation.
add_mention("n2-boccage", NOTES_SEG, 596, "Mme du Boccage", REUSED["boccage"], "Author of the short-form citation.")
add_mention("n2-volume-page", NOTES_SEG, 596, "I, p. 146", C["boccage_letters_vol1"], "Short-form volume and page locator; local bibliography match is not independently verified.")
# Note 3: match the two-part reference to the local bibliography, retaining the page discrepancy.
add_mention("n3-blunt-author", NOTES_SEG, 597, "Blunt", REUSED["blunt"], "Author named in the note.")
add_mention("n3-journal", NOTES_SEG, 597, "Burlington Magazine", REUSED["burlington"], "Publication venue.")
add_mention("n3-two-part-pages", NOTES_SEG, 597, "1946, pp. 262-8, and 1947, p. 101", C["blunt_ricci_royal_collections"], "Citation locator; bibliography gives 263-268 and 101-102.")
# Note 4: the scan gives an omitted continuation; its separate segment is linked below.
add_mention("n4-gherardi", NOTES_SEG, 598, "Abate Pietro Ercole Gherardi", REUSED["gherardi"], "Writer of the Descrizione as stated by Haskell.")
add_mention("n4-description", NOTES_SEG, 598, "Descrizione", REUSED["1749_publication"], "The work's generic designation; provisional connection to the 1749 publication candidate.")
add_mention("n4-cignani-works", NOTES_SEG, 598, "Cignanis", REUSED["cignani_group"], "Smith's group of Cignani cartoons; no individual works named.")
add_mention("n4-ricci-works", NOTES_SEG, 598, "Riccis", REUSED["ricci_holdings"], "Smith's Ricci works; no individual works named.")
add_mention("n4-muratori", NOTES_SEG, 598, "Muratori", REUSED["muratori"], "Friend and correspondent named by Haskell.")
add_mention("n4-long-correspondence", NOTES_SEG, 598, "long correspondence", REUSED["estense_letters"], "General, undated correspondence locator; exact contents are not known.")
add_mention("n4-estense", NOTES_SEG, 598, "Biblioteca Estense, Modena", REUSED["estense"], "Repository named by Haskell; no shelfmark or dates supplied.")
# Note 5 is printed as 5 on physical page 31, although canonical OCR line L599 reads 6.
add_mention("n5-blunt-author", NOTES_SEG, 599, "Blunt", REUSED["blunt"], "Author named in the short citation.")
add_mention("n5-blunt-book-locator", NOTES_SEG, 599, "1957, p. 12, note 6", REUSED["blunt_1957"], "Likely local bibliography match to the 1957 Blunt and Croft-Murray volume; cited passage not consulted.")
# Visually transcribed continuation absent from the base OCR; source PDF p.302, physical p.31.
visual_lines = VISUAL_SOURCE.read_text(encoding="utf-8-sig").splitlines()
add_mention("n4-galleria", VISUAL_SEG, 1, "Galleria di Minerva", REUSED["galleria_volume"], "Volume VI, 1708, named in the visually transcribed continuation.", visual_lines)
add_mention("n4-cignani-quote-subject", VISUAL_SEG, 1, "Cignani", REUSED["cignani"], "Subject of the anonymous writer's quoted remark.", visual_lines)
add_mention("n4-anonymous-passage", VISUAL_SEG, 1, "p. 83", C["anonymous_cignani_galleria_passage"], "Page locator for the anonymous quoted passage; do not merge with the p.251 letter candidate without S3 review.", visual_lines)

add_statement(
    "letter-locator", 1, "letter_from_james_adam_to_robert_adam",
    "Haskell identifies a letter from James to Robert Adam dated 20 August 1760 and thanks John Fleming for showing him a copy.",
    subject=C["james_robert_adam_letter"], obj=REUSED["robert_adam"],
    mentioned=[C["james_robert_adam_letter"], REUSED["james_adam"], REUSED["robert_adam"], C["john_fleming"]],
    relation=True, layer="footnote source locator and acknowledgement",
    qualification="The footnote shortens James Adam's name to James; its contextual link to James Adam named in body line 392 is recorded, with cross-context identity alignment left to S3. No repository or manuscript identifier is supplied, and neither letter nor copy was independently consulted. The scan reads 'I am' where S0 OCR line L595 reads '1 am'; S0 is unchanged.",
    citations=[{"source_candidate_id": C["james_robert_adam_letter"], "author_candidate_id": REUSED["james_adam"], "recipient_candidate_id": REUSED["robert_adam"], "date": "1760-08-20", "copy_shown_by_candidate_id": C["john_fleming"], "repository": "not supplied"}],
    related_body_ids=BODY_LINKS[1],
)
add_statement(
    "boccage-source", 2, "short_form_citation_for_palace_description",
    "P.302 note 2 cites Mme du Boccage, volume I, page 146, for the description of Smith's palace as being entirely in the English taste.",
    subject=REUSED["boccage"], obj=C["boccage_letters_vol1"],
    mentioned=[REUSED["boccage"], C["boccage_letters_vol1"]],
    related_body_ids=BODY_LINKS[2],
    qualification="The local bibliography lists Letters concerning England, Holland and Italy in two volumes (London, 1770), a possible match to this short citation. The volume and cited page were not independently checked.",
    citations=[{"source_candidate_id": C["boccage_letters_vol1"], "volume": "I", "page": "146", "local_bibliography_title": "Letters concerning England, Holland and Italy", "local_bibliography_year": "1770", "match": "possible"}],
)
add_statement(
    "blunt-ricci-article", 3, "full_account_cited_to_blunt",
    "For a full account of the cited Ricci pictures, Haskell directs readers to Anthony Blunt's two-part article in Burlington Magazine, cited as 1946 pages 262-268 and 1947 page 101.",
    subject=REUSED["ricci_holdings"], obj=C["blunt_ricci_royal_collections"],
    mentioned=[REUSED["ricci_holdings"], REUSED["blunt"], REUSED["burlington"], C["blunt_ricci_royal_collections"]],
    related_body_ids=BODY_LINKS[3],
    qualification="The local bibliography gives the title Pictures by Sebastiano and Marco Ricci in the Royal Collections, 1946 pages 263-268 and 1947 pages 101-102. The differing first page and abbreviated second page are retained; neither installment was read.",
    citations=[{"source_candidate_id": C["blunt_ricci_royal_collections"], "note_locator": "Burlington Magazine, 1946, pp.262-268; 1947, p.101", "bibliography_locator": "1946, pp.263-268; 1947, pp.101-102", "match": "title, author and year match; page-range discrepancy"}],
)
add_statement(
    "gherardi-descrizione-authorship", 4, "authored_by",
    "Haskell identifies Abate Pietro Ercole Gherardi as the writer of the Descrizione of Smith's Cignanis and Riccis.",
    subject=REUSED["1749_publication"], obj=REUSED["gherardi"],
    mentioned=[REUSED["1749_publication"], REUSED["gherardi"], REUSED["cignani_group"], REUSED["ricci_holdings"]],
    relation=True, layer="footnote attribution",
    qualification="The note gives no exact title, date or edition. Its connection to the 1749 publication described in the adjacent body passage is contextual and provisional; compare with cand-8005 at S3. Neither account was independently consulted.",
    citations=[{"source_candidate_id": REUSED["1749_publication"], "author_candidate_id": REUSED["gherardi"], "title_as_printed": "Descrizione", "scope_as_printed": "Smith's Cignanis and Riccis", "date": "not supplied"}],
    related_body_ids=BODY_LINKS[4],
)
add_statement(
    "gherardi-muratori-correspondence", 4, "friend_and_long_correspondent_of",
    "Haskell describes Gherardi as a Modenese friend of Muratori with whom he engaged in a long correspondence, then says the correspondence is at Biblioteca Estense, Modena.",
    subject=REUSED["gherardi"], obj=REUSED["muratori"],
    mentioned=[REUSED["gherardi"], REUSED["muratori"], REUSED["estense_letters"], REUSED["estense"]],
    relation=True, layer="reported biographical and correspondence statement",
    qualification="The note supplies no dates, item identifiers or shelfmark. The general correspondence locator may overlap the publishing-related letters cited in p.300 note 3; individual letters were not consulted and the exact corpus scope remains open.",
    citations=[{"source_candidate_id": REUSED["estense_letters"], "repository_candidate_id": REUSED["estense"], "dates": "unspecified", "locator": "general correspondence; p.302 note 4", "identity_with_p.300_locator": "possible overlap"}],
    related_body_ids=BODY_LINKS[4],
)
add_statement(
    "anonymous-cignani-quotation", 4, "anonymous_cited_remark_about_cignani",
    "Haskell quotes an anonymous writer in La Galleria di Minerva as saying of Cignani: “nessuno hà saputo fin’ora vendere in vita i suoi Quadri a sì alto prezzo”.",
    subject=REUSED["cignani"], obj=C["anonymous_cignani_galleria_passage"],
    mentioned=[REUSED["cignani"], REUSED["galleria_volume"], C["anonymous_cignani_galleria_passage"]],
    layer="visually transcribed nested quotation",
    qualification="Transcribed from CHP-10.pdf, printed p.302, physical p.31, footnote 4 continuation omitted from the canonical OCR. The statement is preserved as an anonymous writer's quoted remark, not an independently verified market fact. It is located at volume VI (1708), p.83; possible overlap with cand-8230 remains unresolved.",
    citations=[{"source_candidate_id": C["anonymous_cignani_galleria_passage"], "publication_candidate_id": REUSED["galleria_volume"], "volume": "VI", "year": "1708", "page": "83", "other_candidate_at_same_locator": "cand-8230", "item_identity": "unresolved"}],
    related_body_ids=BODY_LINKS[4],
    segment_id=VISUAL_SEG, start_line=1, end_line=1, source_file=VISUAL_SOURCE_FILE,
    extra={"scan_transcription": True, "base_ocr_continuation_missing": True},
)
add_statement(
    "blunt-turin-hypothesis-source", 5, "hypothesis_attributed_to_blunt",
    "Haskell says the proposed connection between Smith's New Testament pictures and a similar Ricci series for the court of Turin was suggested by Blunt in 1957, page 12, note 6.",
    subject=REUSED["turin_series"], obj=REUSED["blunt_1957"],
    mentioned=[REUSED["turin_series"], REUSED["blunt"], REUSED["blunt_1957"]],
    related_body_ids=BODY_LINKS[5],
    qualification="The local bibliography has one 1957 Blunt and Croft-Murray title, a possible match to this short form. Its cited page and note were not consulted; the possible relation between the two work groups remains tentative.",
    citations=[{"source_candidate_id": REUSED["blunt_1957"], "short_form": "Blunt, 1957, p.12, note 6", "local_bibliography_title": "Venetian drawings of the XVII and XVIII centuries in the collection of Her Majesty the Queen at Windsor Castle", "match": "possible"}],
)

all_candidates = cids | {row["candidate_id"] for row in new_candidates}
for row in new_statements:
    q = row["qualifiers"]
    for endpoint in (row["subject_candidate_id"], row["object_candidate_id"]):
        if endpoint is not None and endpoint not in all_candidates:
            raise SystemExit(f"statement foreign key missing: {row['statement_id']} -> {endpoint}")
    if not all(cid in all_candidates for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"mentioned candidate missing: {row['statement_id']}")

all_mentions = mentions + new_mentions
for segment_id in (NOTES_SEG, VISUAL_SEG):
    prior_spans = [
        (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
        for row in mentions if row["segment_id"] == segment_id
    ]
    added_spans = sorted(
        (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
        for row in new_mentions if row["segment_id"] == segment_id
    )
    for index, left in enumerate(added_spans):
        for right in added_spans[index + 1:]:
            if right[0] < left[1]:
                raise SystemExit(f"overlapping new mentions in {segment_id}: {left[2]} / {right[2]}")
        for old in prior_spans:
            if left[0] < old[1] and old[0] < left[1]:
                raise SystemExit(f"new mention overlaps existing span in {segment_id}: {left[2]} / {old[2]}")

# Add one reviewed source segment for the omitted footnote continuation and close markers 1-5.
new_coverage = {
    "chapter": "chp-10", "segment_id": VISUAL_SEG, "disposition": "reviewed",
    "migration_status": "complete", "source_line_ranges": "L1-1",
    "note": "Derived visual transcription of the continuation of p.302 footnote 4, absent from canonical OCR L598-L599; checked against CHP-10.pdf physical page 31. Records the Galleria di Minerva VI (1708), p.83 citation and anonymous Cignani quotation. Original OCR asset unchanged.",
}
coverage[coverage.index(cov[NOTES_SEG])]["migration_status"] = "partial"
cov[NOTES_SEG].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L492-599",
    "note": "Merged notes processed through p.302 notes 1-5 at L595-L599. P.302 note 4 continues in the derived visual transcription segment because its Galleria di Minerva quotation is absent from canonical OCR; p.302 note 5 is printed as 5 although OCR L599 reads 6. P.302 markers 1-5 are linked to body statements. Next source range: p.303 note 1 at L600.",
})
cov[P302_BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L391-399",
    "note": "P.302 body is semantically processed against CHP-10.pdf physical page 31 and p.302 notes 1-5 are now linked. Its last sentence ends 'or that, if' at L399 and continues on p.303; retain partial until the cross-page statement closes. L400 is a p.303 note excerpt handled in the consolidated notes segment. Scan-only corrections are recorded in process; S0 unchanged.",
})
for marker, ids in BODY_LINKS.items():
    for sid in ids:
        body_by_id[sid]["qualifiers"]["footnote_text_pending"] = False

by_cid["cand-8231"]["detail"] = (
    "Publication identified by the p.251 note; article-level citation only. P.302 note 4 also locates an anonymous Cignani remark at volume VI, 1708, p.83; identity between the two cited items at that locator is unresolved."
)
by_cid["cand-9192"]["detail"] = (
    "Haskell says the New Testament pictures and Cignani cartoons were engraved and described in 1749; p.302 note 4 identifies Gherardi as writer of the Descrizione of Smith's Cignanis and Riccis. The note gives no exact title or date, so the contextual link to this 1749 candidate is provisional. Compare with cand-8005 at S3; source texts were not consulted."
)
by_cid["cand-9340"]["detail"] = (
    "Matched to the joint local bibliography entry. P.284 note 5 and p.300 note 2 cite pp.61-63 and pp.137 ff.; p.302 note 5 gives the short form Blunt, 1957, p.12, note 6, a possible reference to this volume. Neither cited passage nor the book was independently consulted."
)
by_cid["cand-9498"]["detail"] = (
    "P.300 note 3 points to an unspecified plural set of letters on publishing activities and Chapter 13; p.302 note 4 describes a long Gherardi-Muratori correspondence at Biblioteca Estense. The references may overlap, but exact corpus scope is not established. Keep distinct from individually dated letters; the correspondence was not consulted."
)

coverage.insert(coverage.index(cov[NOTES_SEG]) + 1, new_coverage)
new_counts = {
    "new_candidates": len(new_candidates), "new_mentions": len(new_mentions),
    "new_statements": len(new_statements), "new_visual_segments": 1,
}
print(json.dumps({
    "mode": "APPLY" if args.apply else "DRY-RUN",
    "source_asset_sha256": EXPECTED_ASSET_SHA,
    "p302_note_lines_sha256": EXPECTED_NOTE_LINES_SHA,
    "visual_segment": VISUAL_SEG,
    "visual_text_sha256": EXPECTED_VISUAL_TEXT_SHA,
    "counts": new_counts,
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "resolved_body_markers": {str(key): value for key, value in BODY_LINKS.items()},
    "coverage": {
        NOTES_SEG: cov[NOTES_SEG]["source_line_ranges"],
        P302_BODY: cov[P302_BODY]["migration_status"],
        VISUAL_SEG: new_coverage["migration_status"],
    },
}, ensure_ascii=True, indent=2))

if args.apply:
    for path in (cp, mp, sp, vp):
        backup = Path(str(path) + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(cp, cf, candidates + new_candidates)
    write_csv(mp, mf, all_mentions)
    write_jsonl(sp, statements + new_statements)
    write_csv(vp, vf, coverage)
    print("Applied p.302 notes 1-5 and the missing visual continuation; next source range is p.303 note 1 at L600.")
