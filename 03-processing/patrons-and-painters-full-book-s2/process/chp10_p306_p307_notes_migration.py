"""Controlled S2 migration for p.306 notes 2-6 and p.307 notes 1-4.

Dry-run by default. Apply only after source, table, marker, and ID preconditions
match the reviewed snapshot.
"""
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
P306 = "chp-10:10_CHP-10_intro:l435-443"
P307 = "chp-10:10_CHP-10_intro:l445-454"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "04ece660f33cedc45ff150b2c7b69012a223613f2b6f520edac650768c4929e2"
EXPECTED_QUOTE_SHA = "ba45e483b1c4a43dc0bb1552e9b998679ef0a007a1e16eeee97750efec12314d"
BACKUP = ".bak-s2-chp10-p306-p307-notes-20261002"


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
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def segment_text(lines, first, last):
    return "\n".join(lines[first - 1:last])


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_span = segment_text(src, 612, 620)
quote_span = segment_text(src, 442, 443)
if sha(notes_span) != EXPECTED_NOTES_SHA:
    raise SystemExit(f"p.306-307 notes changed: {sha(notes_span)}")
if sha(quote_span) != EXPECTED_QUOTE_SHA:
    raise SystemExit(f"p.306 note-5 quote changed: {sha(quote_span)}")
if src[611].strip() != "2 See p. 299, note 4." or "Testa d’Adriano" not in src[615]:
    raise SystemExit("unexpected p.306 note text")

cp, mp, sp, vp = [TABLES / name for name in (
    "entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv"
)]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9545:
    raise SystemExit(f"candidate sequence changed: {maximum}")
if cov[NOTES]["source_line_ranges"] != "L492-611" or cov[NOTES]["migration_status"] != "partial":
    raise SystemExit(f"notes coverage changed: {cov[NOTES]}")
for seg, ranges in ((P306, "L436-441"), (P307, "L446-454")):
    if cov[seg]["source_line_ranges"] != ranges or cov[seg]["migration_status"] != "partial":
        raise SystemExit(f"body coverage changed: {seg}: {cov[seg]}")

newc = []
newm = []
newst = []
new_cids = set()
new_mids = set()
new_sids = set()


def add_candidate(cid, name, kind, detail, line, origin="body-mention"):
    if cid in cids or cid in new_cids:
        raise SystemExit(f"candidate ID already exists: {cid}")
    if any(row["canonical_name"] == name for row in candidates):
        raise SystemExit(f"duplicate candidate natural key: {name}")
    newc.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": origin,
        "candidate_source_ref": f"{NOTES}#L{line}",
    })
    new_cids.add(cid)


# New candidates are added only where S2 identifies a distinct object not yet
# present in the candidate table. No cross-chapter identity is adjudicated.
add_candidate("cand-9546", "Joseph Smith's referenced Head of Hadrian", "work",
              "Smith's 13 April 1737 letter calls the head of Hadrian more recent. The specific sculpture, version, and present identity are unresolved.", 616)
add_candidate("cand-9547", "Letter from Joseph Smith to A. F. Gori, 30 March 1737", "archive",
              "Letter quoted by Haskell and cross-referenced to p.299 note 4; cited repository is Biblioteca Marucelliana, but no shelfmark is supplied here and the manuscript was not independently consulted.", 613)
add_candidate("cand-9548", "Prosdocimo Zabeo, Memorie intorno l'antiquario Alvise Meneghetti (Venice, 1816)", "archive",
              "Possible source for the reported appraisal of Smith's medal cabinet at p.16; the cited page was not independently consulted.", 614)
add_candidate("cand-9549", "Prosdocimo Zabeo", "person",
              "Named as the author of the p.16 citation; identity is not independently checked in this S2 record.", 614)
add_candidate("cand-9550", "Letter from Girolamo Zanetti, 21 August 1751 (Biblioteca Marucelliana, B. VIII, 13, p.170)", "archive",
              "The cited shelfmark is split between the consolidated notes and the page-level OCR excerpt; manuscript not independently consulted.", 615)
add_candidate("cand-9551", "Letter from Joseph Smith to A. F. Gori, 13 April 1737", "archive",
              "Cited in the consolidated note with Biblioteca Marucelliana and an internal cross-reference to p.299 note 4; no shelfmark is supplied here and the manuscript was not independently consulted.", 616)
add_candidate("cand-9552", "Frances Vivian, Joseph Smith and Giovanni Antonio Pellegrini (1962)", "archive",
              "Article cited for the list of Smith's Dutch and Flemish pictures, pp.330-333; citation not independently consulted.", 619)
add_candidate("cand-9553", "Frances Vivian", "person",
              "Named as the author of the 1962 citation; author identity not independently checked in this S2 record.", 619)
add_candidate("cand-9554", "Cesare Brandi, Canaletto (possible bibliography match)", "archive",
              "Possible match to the Canaletto entry under Cesare Brandi in the local bibliography; OCR year is 'i960' and has not been checked against the page image. Citation identity remains open.", 620)
add_candidate("cand-9555", "Cesare Brandi", "person",
              "Author named in p.307 note 4. Kept distinct from Giacinto Brandi; cross-chapter identity remains for S3.", 620)
add_candidate("cand-9556", "Joseph Smith's medal cabinet", "",
              "Masini's reported appraisal describes Smith's medal cabinet. The source does not establish whether this denotes a physical cabinet, a group of medals, or a collection; current taxonomy has no collection type, so leave type unresolved.", 614)


def add_mention(mid, seg, seg_first, seg_last, line_no, surface, cid, note=""):
    if mid in mids or mid in new_mids:
        raise SystemExit(f"duplicate mention ID: {mid}")
    if cid not in cids | new_cids:
        raise SystemExit(f"mention candidate missing: {mid} -> {cid}")
    line = src[line_no - 1]
    local = line.find(surface)
    if local < 0:
        raise SystemExit(f"surface not found on L{line_no}: {surface!r}")
    segment = segment_text(src, seg_first, seg_last)
    prefix = segment_text(src, seg_first, line_no - 1) if line_no > seg_first else ""
    start = len(prefix) + (1 if prefix else 0) + local
    newm.append({
        "mention_id": mid, "segment_id": seg, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start),
        "end_char": str(start + len(surface)), "note": note,
    })
    new_mids.add(mid)


# p.306 notes and the note-5 quotation split into the body OCR segment.
add_mention("m-s2-p306n2-crossref", NOTES, 491, 634, 612, "p. 299, note 4", "cand-9229",
            "Internal cross-reference to the Smith-Gori correspondence record discussed at p.299 note 4.")
add_mention("m-s2-p306n3-date", NOTES, 491, 634, 613, "30 March 1737", "cand-9547", "Date of the quoted letter.")
add_mention("m-s2-p306n3-repository", NOTES, 491, 634, 613, "Biblioteca Marucelliana", "cand-9493", "Repository named by Haskell.")
add_mention("m-s2-p306n4-masini", NOTES, 491, 634, 614, "Lorenzo Masini", "cand-1561", "Dealer whose appraisal is reported by Haskell.")
add_mention("m-s2-p306n4-smith", NOTES, 491, 634, 614, "Smith", "cand-2440", "Owner in Haskell's report.")
add_mention("m-s2-p306n4-cabinet", NOTES, 491, 634, 614, "medal cabinet", "cand-9556", "Object category intentionally unresolved.")
add_mention("m-s2-p306n4-zabeo-work", NOTES, 491, 634, 614, "Zabeo, p. 16", "cand-9548", "Bibliographic locator; cited page not independently consulted.")
add_mention("m-s2-p306n4-zabeo-author", NOTES, 491, 634, 614, "Zabeo", "cand-9549", "Author named in the citation.")
add_mention("m-s2-p306n5-zanetti", NOTES, 491, 634, 615, "Girolamo Zanetti", "cand-2861", "Author of the cited 1751 letter; identity remains for S3.")
add_mention("m-s2-p306n5-date", NOTES, 491, 634, 615, "21 August 1751", "cand-9550", "Date of the cited letter.")
add_mention("m-s2-p306n5-repository", NOTES, 491, 634, 615, "Biblioteca Marucelliana", "cand-9493", "Repository named by Haskell.")
add_mention("m-s2-p306n5-letter-locator", P306, 435, 443, 442, "B. VIII, 13, p. 170", "cand-9550", "Shelfmark appears in the page-level OCR continuation of note 5.")
add_mention("m-s2-p306n5-brother-coreference", P306, 435, 443, 442, "Mio fratello", "cand-2838", "Haskell's adjacent narrative identifies the unnamed brother as Antonio Maria; the letter quote itself does not name him.")
add_mention("m-s2-p306n5-smith", P306, 435, 443, 442, "Console Brittanico Smith", "cand-2440", "Smith is identified in the Italian quotation as the British Consul.")
add_mention("m-s2-p306n6-date", NOTES, 491, 634, 616, "13 April 1737", "cand-9551", "Date of the cited Smith-Gori letter.")
add_mention("m-s2-p306n6-smith", NOTES, 491, 634, 616, "Smith", "cand-2440", "Sender named by Haskell.")
add_mention("m-s2-p306n6-gori", NOTES, 491, 634, 616, "Gori", "cand-1214", "Recipient named by Haskell.")
add_mention("m-s2-p306n6-repository", NOTES, 491, 634, 616, "Biblioteca Marucelliana", "cand-9493", "Repository named by Haskell.")
add_mention("m-s2-p306n6-hadrian-head", NOTES, 491, 634, 616, "Testa d’Adriano", "cand-9546", "Sculpture described in Smith's quoted letter; identity and version unresolved.")

# p.307 citation notes.
add_mention("m-s2-p307n1-breval", NOTES, 491, 634, 617, "Breval, 1738,1, p. 230", "cand-7713", "OCR reads numeral 1; the scan shows Roman I in the volume designation.")
add_mention("m-s2-p307n2-blunt-croft", NOTES, 491, 634, 618, "Blunt and Croft-Murray", "cand-9340", "Cited work; p.11 not independently consulted.")
add_mention("m-s2-p307n3-ibid", NOTES, 491, 634, 619, "ibid.", "cand-9340", "Internal reference to the Blunt and Croft-Murray work in note 2.")
add_mention("m-s2-p307n3-vivian-work", NOTES, 491, 634, 619, "Vivian, 1962", "cand-9552", "Article cited for the related picture list; not independently consulted.")
add_mention("m-s2-p307n3-vivian-author", NOTES, 491, 634, 619, "Vivian", "cand-9553", "Author named in the citation.")
add_mention("m-s2-p307n4-brandi", NOTES, 491, 634, 620, "Brandi", "cand-9555", "Author named by Haskell; kept distinct from Giacinto Brandi pending S3.")
add_mention("m-s2-p307n4-brandi-work", NOTES, 491, 634, 620, "pp. 60 if", "cand-9554", "OCR reads 'if'; the scan reads 'ff.'; possible Canaletto bibliography match remains open.")


def add_statement(sid, seg, line_start, line_end, subject, obj, predicate, claim,
                  speaker, text_layer, qualification, mentioned, relation=False,
                  marker=None, printed_marker_line=None, body_ids=(), citations=(),
                  crossrefs=(), original_quote=None, extra=None):
    if sid in sids or sid in new_sids:
        raise SystemExit(f"duplicate statement ID: {sid}")
    source_lines = segment_text(src, line_start, line_end)
    if original_quote is None:
        original_quote = source_lines
    if original_quote not in source_lines:
        raise SystemExit(f"statement quote is not contained in source lines: {sid}")
    ids = [row["candidate_id"] for row in newm if row["segment_id"] == seg
           and any(int(row["start_char"]) < len(segment_text(src, line_start, line_end))
                   for _ in [0])]
    # Use the explicitly supplied candidate set so each statement records only
    # entities relevant to that claim, including resolved coreferences.
    q = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 306 if seg == P306 else 307,
        "pdf_physical_page": 35 if seg == P306 else 36,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation,
    }
    if marker is not None:
        q.update({"footnote_marker": marker, "footnote_text_pending": False})
    if printed_marker_line is not None:
        q["printed_marker_line"] = printed_marker_line
    if body_ids:
        q["related_body_statement_ids"] = list(body_ids)
    if citations:
        q["citations"] = list(citations)
        q["cited_material_not_independently_consulted"] = True
    if crossrefs:
        q["cross_reference_segments"] = list(crossrefs)
    if extra:
        q.update(extra)
    newst.append({
        "statement_id": sid, "segment_id": seg,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": q,
        "original_quote": original_quote, "source_file": SOURCE_FILE, "origin": "book",
    })
    new_sids.add(sid)


add_statement("st-chp10-p306-note2-crossref", NOTES, 612, 612, "cand-9229", None,
              "cross_references_internal_note",
              "The footnote directs the reader to p.299 note 4 for the Smith-Gori correspondence context.",
              "Haskell, footnote", "internal cross-reference",
              "This is an internal pointer, not independent confirmation of the letters.",
              ["cand-9229"], marker=2, printed_marker_line=438,
              body_ids=["st-chp10-p306-smith-gems-correspondence"], crossrefs=[NOTES],
              citations=[{"internal_reference": "p.299 note 4", "candidate_id": "cand-9229"}])

add_statement("st-chp10-p306-note3-gori-letter", NOTES, 613, 613, "cand-9547", "cand-9493",
              "identifies_quoted_letter_and_repository",
              "Haskell dates the quoted letter to 30 March 1737, attributes it to the Biblioteca Marucelliana, and points to p.299 note 4.",
              "Haskell, footnote", "archival citation and letter quotation",
              "The manuscript was not independently consulted; no shelfmark is supplied in this note.",
              ["cand-9547", "cand-9493"], relation=True, marker=3, printed_marker_line=438,
              body_ids=["st-chp10-p306-smith-stated-artistic-preferences"], crossrefs=[NOTES],
              citations=[{"letter_candidate_id": "cand-9547", "repository_candidate_id": "cand-9493",
                          "date": "30 March 1737", "internal_reference": "p.299 note 4"}])

add_statement("st-chp10-p306-note4-masini-appraisal", NOTES, 614, 614, "cand-1561", "cand-9556",
              "reported_appraisal_of_medal_cabinet",
              "Haskell reports that dealer Lorenzo Masini considered Smith's medal cabinet outstanding in quality for its day.",
              "Lorenzo Masini as reported by Haskell", "reported appraisal",
              "This is a reported historical judgment, not an independent assessment. The object type remains unresolved; Zabeo p.16 was not consulted.",
              ["cand-1561", "cand-2440", "cand-9556", "cand-9548", "cand-9549"],
              marker=4, printed_marker_line=439,
              body_ids=["st-chp10-p306-praise-and-contested-taste"], crossrefs=[NOTES],
              citations=[{"author_candidate_id": "cand-9549", "publication_candidate_id": "cand-9548",
                          "page": "16"}])

add_statement("st-chp10-p306-note5-zanetti-letter-citation", NOTES, 615, 615, "cand-9550", "cand-9493",
              "identifies_letter_and_repository",
              "Haskell identifies a letter by Girolamo Zanetti dated 21 August 1751 in the Biblioteca Marucelliana.",
              "Haskell, footnote", "archival citation",
              "The inline OCR continuation at p.306 L442-443 supplies shelfmark B.VIII,13, p.170 and the Italian quotation; the manuscript was not independently consulted.",
              ["cand-9550", "cand-2861", "cand-9493"], relation=True,
              marker=5, printed_marker_line=440,
              body_ids=["st-chp10-p306-zanetti-criticism-of-gems"], crossrefs=[P306],
              citations=[{"letter_candidate_id": "cand-9550", "author_candidate_id": "cand-2861",
                          "repository_candidate_id": "cand-9493", "shelfmark": "B.VIII,13, p.170",
                          "date": "21 August 1751"}])

add_statement("st-chp10-p306-note5-letter-quote", P306, 442, 443, "cand-2861", "cand-2838",
              "reports_brother_designed_gems_for_smith",
              "In the letter quoted by Haskell, Girolamo Zanetti says his brother designed the gems and cameos associated with the British Consul Smith; the marginal note says the brother was badly rewarded.",
              "Girolamo Zanetti in a letter quoted by Haskell", "archival quotation",
              "The quote names the speaker's brother only by kinship term. Haskell's adjacent narrative identifies him as Antonio Maria; the manuscript was not independently consulted.",
              ["cand-2861", "cand-2838", "cand-2440", "cand-9228", "cand-9550"], relation=True,
              citations=[{"letter_candidate_id": "cand-9550", "date": "21 August 1751",
                          "shelfmark": "B.VIII,13, p.170"}],
              crossrefs=[NOTES], original_quote=quote_span,
              extra={"printed_page": 306, "pdf_physical_page": 35,
                     "duplicate_ocr_of_consolidated_note": "L615"})

add_statement("st-chp10-p306-note6-smith-gori-letter", NOTES, 616, 616, "cand-9551", "cand-9493",
              "identifies_letter_and_quoted_artistic_judgment",
              "Haskell cites a letter from Smith to Gori dated 13 April 1737 and quotes Smith distinguishing excellent sixteenth-century works from a more recent Head of Hadrian.",
              "Joseph Smith as quoted by Haskell", "letter quotation and archival citation",
              "The manuscript was not independently consulted; no shelfmark is supplied here. The referenced sculpture's identity and version remain unresolved.",
              ["cand-9551", "cand-2440", "cand-1214", "cand-9493", "cand-9546"], relation=True,
              marker=6, printed_marker_line=440,
              body_ids=["st-chp10-p306-smith-distinguished-antique-art"], crossrefs=[NOTES],
              citations=[{"letter_candidate_id": "cand-9551", "sender_candidate_id": "cand-2440",
                          "recipient_candidate_id": "cand-1214", "repository_candidate_id": "cand-9493",
                          "date": "13 April 1737", "internal_reference": "p.299 note 4"}])

add_statement("st-chp10-p307-note1-breval-reference", NOTES, 617, 617, "cand-7713", None,
              "cites_source_for_statuette_description",
              "Haskell cites Breval's 1738 account, volume I, page 230, for the continuation of the statuette description.",
              "Haskell, footnote", "bibliographic locator",
              "The cited page was not independently consulted.", ["cand-7713"],
              marker=1, printed_marker_line=446,
              body_ids=["st-chp10-p307-breval-statuette-continuation"], crossrefs=[P307],
              citations=[{"publication_candidate_id": "cand-7713", "volume": "I", "page": "230", "year": "1738"}])

add_statement("st-chp10-p307-note2-blunt-reference", NOTES, 618, 618, "cand-9340", None,
              "cites_source_for_smith_sale_to_elector",
              "Haskell cites Blunt and Croft-Murray, page 11, for Smith's sale of paintings to the Elector of Saxony.",
              "Haskell, footnote", "bibliographic locator",
              "The cited page was not independently consulted.", ["cand-9340"],
              marker=2, printed_marker_line=447,
              body_ids=["st-chp10-p307-smith-sale-to-elector"], crossrefs=[P307],
              citations=[{"publication_candidate_id": "cand-9340", "page": "11"}])

add_statement("st-chp10-p307-note3-picture-list-citations", NOTES, 619, 619, "cand-9340", "cand-9552",
              "cites_picture_list_and_related_study",
              "Haskell cites Blunt and Croft-Murray page 14 and pages 19-23 for Smith's Dutch and Flemish pictures, alongside Frances Vivian's 1962 article, pages 330-333.",
              "Haskell, footnote", "bibliographic locators",
              "The cited pages and Vivian article were not independently consulted; the entry 'ibid.' refers to Blunt and Croft-Murray. The scan reads pp.330-333 where OCR has 'PP330-3'.",
              ["cand-9340", "cand-9552", "cand-9553", "cand-2440"],
              marker=3, printed_marker_line=447,
              body_ids=["st-chp10-p307-smith-bought-dutch-flemish-collection",
                        "st-chp10-p307-pellegrini-widow-identity",
                        "st-chp10-p307-smith-acquired-vermeer"], crossrefs=[P307],
              citations=[{"publication_candidate_id": "cand-9340", "pages": ["14", "19-23"]},
                         {"publication_candidate_id": "cand-9552", "author_candidate_id": "cand-9553",
                          "year": "1962", "pages": "330-333"}])

add_statement("st-chp10-p307-note4-brandi-reference", NOTES, 620, 620, "cand-9555", "cand-9554",
              "cites_critical_account_of_vermeer_influence",
              "Haskell cites Cesare Brandi, pages 60 and following, as the strongest but least convincing proponent of the Vermeer-to-Canaletto influence claim.",
              "Haskell, footnote", "reported scholarly position and bibliographic locator",
              "The cited pages were not independently consulted. Brandi's identity and the possible match to the local Canaletto bibliography entry remain open for S3; the OCR bibliography year 'i960' has not been visually checked.",
              ["cand-9555", "cand-9554", "cand-9234", "cand-0514"],
              marker=4, printed_marker_line=448,
              body_ids=["st-chp10-p307-claimed-vermeer-influence"], crossrefs=[P307],
              citations=[{"author_candidate_id": "cand-9555", "publication_candidate_id": "cand-9554",
                          "pages": "60 ff.", "bibliography_match": "possible; unresolved"}])


body_links = {
    "st-chp10-p306-smith-gems-correspondence": (2, 438),
    "st-chp10-p306-smith-stated-artistic-preferences": (3, 438),
    "st-chp10-p306-praise-and-contested-taste": (4, 439),
    "st-chp10-p306-zanetti-criticism-of-gems": (5, 440),
    "st-chp10-p306-smith-distinguished-antique-art": (6, 440),
    "st-chp10-p307-breval-statuette-continuation": (1, 446),
    "st-chp10-p307-smith-sale-to-elector": (2, 447),
    "st-chp10-p307-smith-bought-dutch-flemish-collection": (3, 447),
    "st-chp10-p307-pellegrini-widow-identity": (3, 447),
    "st-chp10-p307-smith-acquired-vermeer": (3, 447),
    "st-chp10-p307-claimed-vermeer-influence": (4, 448),
}
for sid, (marker, marker_line) in body_links.items():
    row = next((item for item in statements if item["statement_id"] == sid), None)
    if row is None:
        raise SystemExit(f"missing body statement: {sid}")
    q = row["qualifiers"]
    if q.get("footnote_marker") != marker or q.get("footnote_text_pending") is not True:
        raise SystemExit(f"body footnote state changed: {sid}: {q}")
    q["footnote_text_pending"] = False
    q["printed_marker_line"] = marker_line
    if sid == "st-chp10-p306-zanetti-criticism-of-gems":
        q["qualification"] = "Haskell reports Zanetti's criticism; p.306 note 5 supplies the cited 1751 letter, shelfmark and quotation. The manuscript was not independently consulted."
    elif sid == "st-chp10-p306-smith-distinguished-antique-art":
        q["qualification"] = "The source passage presents this as Smith's distinction; p.306 note 6 identifies the 13 April 1737 letter. The manuscript was not independently consulted."

all_cids = cids | new_cids
for row in newm:
    if row["candidate_id"] not in all_cids:
        raise SystemExit(f"missing mention FK: {row['mention_id']}")
for row in newst:
    q = row["qualifiers"]
    for cid in [row["subject_candidate_id"], row["object_candidate_id"], *q["mentioned_candidate_ids"]]:
        if cid and cid not in all_cids:
            raise SystemExit(f"missing statement FK: {row['statement_id']} -> {cid}")
    body_ids = q.get("related_body_statement_ids", [])
    if any(sid not in sids for sid in body_ids):
        raise SystemExit(f"missing body-statement FK: {row['statement_id']} -> {body_ids}")

cov[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial",
    "source_line_ranges": "L492-620",
    "note": "Merged notes processed through p.307 note 4 at L620. P.306 notes 2-6 and p.307 notes 1-4 are linked to their body markers. P.306 note 5's shelfmark and Italian quotation are split across L615 and page-level OCR L442-443; p.307 note 3 cites Vivian (1962, pp.330-333). P.307 note 4's Brandi citation remains a possible, unverified bibliography match. Next note: p.308 note 1 at L621."
})
cov[P306].update({
    "disposition": "reviewed", "migration_status": "partial",
    "source_line_ranges": "L436-443",
    "note": "Printed p.306 notes 1-6 are linked. The page-level OCR lines L442-443 preserve the B.VIII,13 p.170 locator and Zanetti quotation for note 5; they are separately anchored to the cited 1751 letter. The Breval statuette sentence begins here and continues on p.307, so retain partial."
})

summary = {
    "mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
    "notes_sha256": sha(notes_span), "quote_sha256": sha(quote_span),
    "new_candidates": len(newc), "candidate_ids": [row["candidate_id"] for row in newc],
    "new_mentions": len(newm), "new_statements": len(newst),
    "coverage": {"notes": "L492-620 partial", "p306_body": "L436-443 partial",
                 "p307_body": "L446-454 partial"},
    "body_footnote_links": len(body_links),
}
print(json.dumps(summary, ensure_ascii=True, indent=2))
if sys.argv[-1:] == ["--apply"]:
    paths = (cp, mp, sp, vp)
    for path in paths:
        backup = Path(str(path) + BACKUP)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(cp, cf, candidates + newc)
    write_csv(mp, mf, mentions + newm)
    write_jsonl(sp, statements + newst)
    write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
    print("Applied with four recoverable table backups.")
