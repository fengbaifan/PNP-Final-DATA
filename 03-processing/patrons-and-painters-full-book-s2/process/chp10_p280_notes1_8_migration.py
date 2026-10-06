"""Controlled S2 migration for p.280 footnotes 1-8; dry-run unless --apply."""
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
BODY = "chp-10:10_CHP-10_intro:l51-61"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINES_SHA = "93429fd81d159163723d9e5dc2a48a162783a0a1580848790c8f1cabc63ccdf9"
BACKUP = ".bak-s2-chp10-p280-notes1-8-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_body = "\n".join(src[490:634])
if hashlib.sha256(notes_body.encode("utf-8")).hexdigest() != EXPECTED_NOTES_SHA:
    raise SystemExit("merged note segment changed")
if hashlib.sha256("\n".join(src[509:516]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.280 notes 1-8 changed")
if not src[509].startswith("1 Verme") or "Turberville" not in src[509] or "Charlton" not in src[514]:
    raise SystemExit("p.280 note text mismatch")

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
if maximum != 9302:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("reviewed", "partial"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-509":
    raise SystemExit("notes coverage pre-state changed")

body_targets = [row for row in statements if row["segment_id"] == BODY
                and row.get("qualifiers", {}).get("footnote_marker") in range(1, 9)]
if len(body_targets) != 8 or {row["qualifiers"]["footnote_marker"] for row in body_targets} != set(range(1, 9)):
    raise SystemExit("p.280 footnote body links changed")
if any(not row["qualifiers"].get("footnote_text_pending") for row in body_targets):
    raise SystemExit("one or more p.280 footnotes are already resolved")

existing_needed = {"cand-7255", "cand-8840", "cand-2154", "cand-0470", "cand-0471", "cand-8913", "cand-8914",
                   "cand-8919", "cand-8923", "cand-1979", "cand-8931", "cand-2175", "cand-2177", "cand-2818"}
if not existing_needed <= cids:
    raise SystemExit(f"existing candidates missing: {existing_needed-cids}")
cand_by_id = {row["candidate_id"]: row for row in candidates}
for cid in ("cand-2175", "cand-2177"):
    if cand_by_id[cid].get("suggested_type"):
        raise SystemExit(f"index work candidate already typed: {cid}")
if cand_by_id["cand-0471"].get("suggested_type"):
    raise SystemExit("Chiswick house subentry already typed")
if "p.280 notes 1-8" in cand_by_id["cand-7255"].get("detail", ""):
    raise SystemExit("Vertue p.280 note locators already recorded")

NEW_CANDIDATES = [
    ("cand-9303", "Turberville, vol. II, p.14 (citation locator; work and edition unresolved)", "archive",
     "Short-form citation in Haskell's p.280 note 2 concerning William Bentinck. Print scan reads vol. II; S0 OCR reads H. Cited page not independently consulted."),
    ("cand-9304", "Sketch for The Last Supper (artist and object identity unresolved; p.280 note 3)", "work",
     "Haskell's note reports a sketch for the Bulstrode Park chapel painting in the National Gallery of Art, Washington. No artist, medium, inventory number, or current location is supplied."),
    ("cand-9305", "Sketch for The Baptism of Christ (auction object identity unresolved; p.280 note 3)", "work",
     "Haskell's note reports that a sketch for the Bulstrode Park chapel painting was sold at Sotheby's on 7 December 1960. No lot number, artist, medium, or current owner is supplied."),
    ("cand-9306", "National Gallery of Art, Washington (p.280 note 3)", "institution",
     "Named as the reported location of a Last Supper sketch; the footnote was not independently checked and does not establish present custody."),
    ("cand-9307", "Sotheby's (auction house named in p.280 note 3)", "institution",
     "Named as the venue through which a Baptism sketch was reportedly sold on 7 December 1960; sale documentation not independently checked."),
    ("cand-9308", "Chatsworth (country house named in p.280 note 5)", "place",
     "Haskell reports the two Sebastiano Ricci pictures there. This is the source's location statement, not current collection verification."),
    ("cand-9309", "Dukes of Devonshire (plural title reference in p.280 note 5; identities unresolved)", "",
     "The source refers collectively to successive holders by title; do not identify a specific duke or infer a family node before S3."),
    ("cand-9310", "Burlington's estate (scope and object type unresolved; p.280 note 5)", "",
     "Haskell says the Dukes of Devonshire inherited Burlington's estate but does not specify whether this means land, a collection, or a broader asset set."),
    ("cand-9311", "Wittkower, 1948 (citation locator; title unresolved)", "archive",
     "Short-form citation in Haskell's p.280 note 6; work and edition are not identified and the reference was not independently consulted."),
    ("cand-9312", "Charlton (citation locator in p.280 note 7; work unresolved)", "archive",
     "Short-form citation for the Chiswick villa chronology and Haskell's probable transfer hypothesis; cited source not independently consulted."),
    ("cand-9313", "The Complete Peerage (citation locator in p.280 note 8; edition unresolved)", "archive",
     "Bibliographic pointer in Haskell's p.280 note 8; no volume/page is supplied and the reference was not independently consulted."),
    ("cand-9314", "H. Clifford Smith, p.26 (citation locator; work unresolved)", "archive",
     "Bibliographic pointer in Haskell's p.280 note 8; title and edition are unresolved and the cited page was not independently consulted."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
source_lines = {
    "cand-9303": 510, "cand-9304": 511, "cand-9305": 511, "cand-9306": 511, "cand-9307": 511,
    "cand-9308": 513, "cand-9309": 513, "cand-9310": 513, "cand-9311": 514,
    "cand-9312": 515, "cand-9313": 516, "cand-9314": 516,
}
newc = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES}#L{source_lines[cid]}",
} for cid, name, kind, detail in NEW_CANDIDATES]

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1
newm = []


def add_mention(local, line_no, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p280notes-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in newm):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[line_no - 1]
    positions, at = [], 0
    while True:
        at = line.find(surface, at)
        if at < 0:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    newm.append({
        "mention_id": mention_id, "segment_id": NOTES, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention("vertue-i", 510, "Verme, I, p. 38.", "cand-7255", "Print scan reads Vertue; source OCR retained in mention anchor.")
add_mention("turberville", 510, "Turberville, H, p. 14.", "cand-9303", "Print scan reads vol. II; OCR reads H.")
add_mention("last-supper-sketch", 511, "A sketch for the Last Supper", "cand-9304")
add_mention("last-supper-work", 511, "the Last Supper", "cand-8913")
add_mention("national-gallery", 511, "National Gallery of Art in Washington", "cand-9306")
add_mention("baptism-sketch", 511, "one for The Baptism", "cand-9305")
add_mention("baptism-work", 511, "The Baptism", "cand-8914")
add_mention("sothebys", 511, "Sotheby", "cand-9307", "S0 OCR has replacement characters for the possessive apostrophe.")
add_mention("vertue-iv", 512, "Vertue, IV, p. 48.", "cand-7255")
add_mention("ricci-artist", 513, "Ricci", "cand-2154")
add_mention("burlington-person-date", 513, "Burlington", "cand-0470", occurrence=0)
add_mention("presentation", 513, "The Presentation in the Temple", "cand-2175")
add_mention("susanna", 513, "Susanna and the Elders", "cand-2177")
add_mention("chatsworth", 513, "Chatsworth", "cand-9308")
add_mention("devonshire-dukes", 513, "Dukes of Devonshire", "cand-9309", "Plural title reference; member identities unresolved.")
add_mention("burlington-estate-owner", 513, "Burlington", "cand-0470", occurrence=1)
add_mention("estate", 513, "estate", "cand-9310", "Object scope and type remain unresolved.")
add_mention("osti", 513, "Osti, 1951, pp. 119-23.", "cand-8840", "Short-form citation only; cited pages not independently consulted.")
add_mention("wittkower-work", 514, "Wittkower, 1948.", "cand-9311")
add_mention("wittkower-person", 514, "Wittkower", "cand-2818")
add_mention("charlton", 515, "Charlton", "cand-9312")
add_mention("burlington-villa", 515, "his villa", "cand-0471", "The possessive antecedent is Lord Burlington.")
add_mention("ricci-works", 515, "the works by him there", "cand-8923", "'Him' refers to Sebastiano Ricci; 'there' refers to Burlington's Chiswick villa.")
add_mention("earl-town-house", 515, "town house", "cand-8919", "The exact house is inferred from the nearby p.280 Piccadilly mansion context; the transfer remains probable.")
add_mention("complete-peerage", 516, "Complete Peerage", "cand-9313")
add_mention("clifford-smith", 516, "H. Clifford Smith, p. 26.", "cand-9314")

for cid, detail in {
    "cand-2175": "Index subentry for The Presentation in the Temple; p.280 note 5 says Ricci dated it in 1713 and reports it at Chatsworth. Do not treat the book's location as current verification.",
    "cand-2177": "Index subentry for Susanna and the Elders; p.280 note 5 says Ricci dated it in 1713 and reports it at Chatsworth. Distinguish from same-titled works by other artists; location not current-verified.",
}.items():
    cand_by_id[cid]["suggested_type"] = "work"
    cand_by_id[cid]["detail"] = detail
cand_by_id["cand-0471"]["suggested_type"] = "place"
cand_by_id["cand-0471"]["detail"] = "Index subentry for Burlington's house at Chiswick; p.280 note 7 calls it his villa and distinguishes it from the Piccadilly town house."
cand_by_id["cand-7255"]["detail"] = (cand_by_id["cand-7255"].get("detail", "") +
    " P.280 notes 1 and 4 cite vols. I, p.38, and IV, p.48; print scan resolves OCR 'Verme' as Vertue. These passages were not independently consulted.").strip()
cand_by_id["cand-8840"]["detail"] = (cand_by_id["cand-8840"].get("detail", "") +
    " P.280 note 5 cites pp.119-123 for Ricci's two Burlington pictures; these pages were not independently consulted.").strip()
cand_by_id["cand-8913"]["detail"] += " Keep the sketch mentioned in p.280 note 3 as a distinct work candidate."
cand_by_id["cand-8914"]["detail"] += " Keep the auctioned sketch mentioned in p.280 note 3 as a distinct work candidate."
cand_by_id["cand-8919"]["detail"] += " P.280 note 7 calls this the Earl's town house; its identification as the source house for a probable transfer remains Haskell's hypothesis."
cand_by_id["cand-8923"]["detail"] += " P.280 note 7 proposes, with 'probable', transfer from the Earl's town house to Chiswick; do not state as confirmed provenance."

targets = {row["qualifiers"]["footnote_marker"]: row for row in body_targets}
line3 = src[510]
line5 = src[512]
line7 = src[514]
quote_last_supper = line3[line3.index("A sketch"):line3.index(" and one for")]
quote_baptism = line3[line3.index("one for"):line3.rfind(".") + 1]
quote_date = line5[line5.index("Ricci dated"):line5.index(" These pictures")]
quote_chatsworth = line5[line5.index("These pictures"):line5.index("Chatsworth") + len("Chatsworth")]
inherit_start = line5.index("who inherited")
inherit_end = line5.index(" estate", inherit_start) + len(" estate")
quote_inheritance = line5[inherit_start:inherit_end]
quote_villa = line7[line7.index("As Lord"):line7.index(", by which")]
quote_transfer = line7[line7.index("it is probable"):line7.rfind(".") + 1]

newstatements = []


def make_statement(statement_id, line_no, subject, object_, predicate, quote, claim, qualification, mentioned,
                   footnote_number, relation=False):
    if statement_id in sids or any(r["statement_id"] == statement_id for r in newstatements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in src[line_no - 1]:
        raise SystemExit(f"quote is not anchored: {statement_id}")
    return {
        "statement_id": statement_id, "segment_id": NOTES,
        "subject_candidate_id": subject, "object_candidate_id": object_, "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_no, "source_line_end": line_no, "printed_page": 280, "pdf_physical_page": 5,
            "claim": claim, "speaker": "Haskell, footnote", "text_layer": "authorial note",
            "qualification": qualification, "mentioned_candidate_ids": mentioned,
            "footnote_number": footnote_number,
            "related_body_statement_ids": [targets[footnote_number]["statement_id"]],
            "cited_material_not_independently_consulted": True, "relation_candidate": relation,
        },
        "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
    }


newstatements.extend([
    make_statement("st-chp10-notes-p280n3-lastsupper-sketch-location", 511, "cand-9304", "cand-9306",
        "haskell_reports_lastsupper_sketch_at_national_gallery_of_art_washington", quote_last_supper,
        "Haskell's note reports a sketch for The Last Supper at the National Gallery of Art in Washington.",
        "The artist, medium, inventory identity, and date of this location report are not supplied. It is not current custody verification; the final chapel painting is a separate candidate. No external source was consulted.",
        ["cand-9304", "cand-8913", "cand-9306"], 3, True),
    make_statement("st-chp10-notes-p280n3-baptism-sketch-sale", 511, "cand-9305", "cand-9307",
        "haskell_reports_baptism_sketch_sold_at_sothebys_on_1960_12_07", quote_baptism,
        "Haskell's note reports that a sketch for The Baptism was sold at Sotheby's on 7 December 1960.",
        "No auction lot, artist, medium, or subsequent owner is identified. S0 OCR reads 'i960' and the scan reads 1960; the sale was not independently verified. Keep the sketch distinct from the final chapel painting.",
        ["cand-9305", "cand-8914", "cand-9307"], 3, True),
    make_statement("st-chp10-notes-p280n5-presentation-dated-1713", 513, "cand-2175", "",
        "ricci_dated_presentation_in_temple_to_1713", quote_date,
        "Haskell's note says Ricci dated The Presentation in the Temple to 1713.",
        "The note is a cited report, not an independently checked date. The work candidate is the index subentry, with identity to be resolved globally.",
        ["cand-2154", "cand-2175", "cand-8840"], 5, True),
    make_statement("st-chp10-notes-p280n5-susanna-dated-1713", 513, "cand-2177", "",
        "ricci_dated_susanna_and_the_elders_to_1713", quote_date,
        "Haskell's note says Ricci dated Susanna and the Elders to 1713.",
        "The date applies to both pictures named in the next sentence; the cited Osti pages were not independently consulted. Distinguish same-titled works pending S3.",
        ["cand-2154", "cand-2177", "cand-8840"], 5, True),
    make_statement("st-chp10-notes-p280n5-presentation-chatsworth", 513, "cand-2175", "cand-9308",
        "book_note_reports_presentation_at_chatsworth", quote_chatsworth,
        "Haskell's note reports The Presentation in the Temple at Chatsworth.",
        "'Are at' reflects the source's report; the note's exact date and present-day custody were not independently verified.",
        ["cand-2175", "cand-9308", "cand-9309", "cand-8840"], 5, True),
    make_statement("st-chp10-notes-p280n5-susanna-chatsworth", 513, "cand-2177", "cand-9308",
        "book_note_reports_susanna_and_the_elders_at_chatsworth", quote_chatsworth,
        "Haskell's note reports Susanna and the Elders at Chatsworth.",
        "'Are at' reflects the source's report; the note's exact date and present-day custody were not independently verified.",
        ["cand-2177", "cand-9308", "cand-9309", "cand-8840"], 5, True),
    make_statement("st-chp10-notes-p280n5-devonshire-inherited-burlington-estate", 513, "cand-9309", "cand-9310",
        "haskell_reports_dukes_of_devonshire_inherited_burlington_estate", quote_inheritance,
        "Haskell's note says the Dukes of Devonshire inherited Burlington's estate.",
        "The plural title does not identify individual holders; the estate's scope and object type are unspecified. Osti 1951, pp.119-123, is cited but not independently consulted.",
        ["cand-9309", "cand-9310", "cand-0470", "cand-8840"], 5, True),
    make_statement("st-chp10-notes-p280n7-chiswick-villa-began-1725", 515, "cand-0471", "",
        "burlington_chiswick_villa_began_in_1725", quote_villa,
        "Haskell's note says Lord Burlington only began his villa in 1725.",
        "Charlton is cited but was not independently consulted; villa construction is not equated with completion.",
        ["cand-0470", "cand-0471", "cand-9312"], 7, False),
    make_statement("st-chp10-notes-p280n7-probable-transfer-to-chiswick", 515, "cand-8923", "cand-0471",
        "haskell_probably_transferred_ricci_paintings_from_burlington_house_to_chiswick", quote_transfer,
        "Haskell judges it probable that Ricci's works at Burlington's Chiswick villa had been transferred from the Earl's town house.",
        "This is explicitly a probability, not confirmed provenance. 'There' means Chiswick; the town house is contextually linked to Burlington House in Piccadilly. Charlton is cited but not independently consulted; Haskell's earlier p.280 report that Ricci left England in 1716 is already recorded separately.",
        ["cand-8923", "cand-0471", "cand-8919", "cand-0470", "cand-2154", "cand-9312"], 7, True),
])

note_statement_ids = {
    3: ["st-chp10-notes-p280n3-lastsupper-sketch-location", "st-chp10-notes-p280n3-baptism-sketch-sale"],
    5: ["st-chp10-notes-p280n5-presentation-dated-1713", "st-chp10-notes-p280n5-susanna-dated-1713",
        "st-chp10-notes-p280n5-presentation-chatsworth", "st-chp10-notes-p280n5-susanna-chatsworth",
        "st-chp10-notes-p280n5-devonshire-inherited-burlington-estate"],
    7: ["st-chp10-notes-p280n7-chiswick-villa-began-1725", "st-chp10-notes-p280n7-probable-transfer-to-chiswick"],
}
source_line_by_marker = {1: 510, 2: 510, 3: 511, 4: 512, 5: 513, 6: 514, 7: 515, 8: 516}
for marker, row in targets.items():
    q = row["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES
    q["footnote_source_line"] = source_line_by_marker[marker]
    q["footnote_note_statement_ids"] = note_statement_ids.get(marker, [])
    correction = {
        1: "The print reads Vertue, vol. I, p.38; S0 OCR reads Verme.",
        2: "The print numbers this note 2 and reads Turberville, vol. II, p.14; S0 OCR merges a 4 marker and reads H.",
        3: "The scan reads 1960; S0 OCR reads i960. The reported sketch objects remain distinct from the final paintings.",
        4: "The citation points to Vertue, vol. IV, p.48; the passage was not independently read.",
        5: "Osti 1951, pp.119-123, is a citation trail only; the two work dates and Chatsworth report remain Haskell's claims.",
        6: "The print marker is 6; S0 OCR reads 8. Wittkower 1948 remains an unresolved citation locator.",
        7: "Charlton is cited; the transfer from the town house is explicitly probable, not confirmed.",
        8: "Complete Peerage and H. Clifford Smith p.26 are citation pointers, not independent verification.",
    }[marker]
    if marker in (1, 2, 3, 5, 6, 7, 8):
        q["qualification"] = (q.get("qualification", "") + " " + correction).strip()

notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-516"
notes_cov["note"] = (notes_cov.get("note", "") +
    " Processed p.280 notes 1-8 at L510-L516. Print resolves OCR errors: Vertue/Verme, note 2 misread as 4 and vol. II as H, note 6 misread as 8, and sale year 1960 misread as i960. Notes 1,2,4,6,8 are source pointers; notes 3,5,7 contain claims and qualifications recorded in book-statements. No cited publication was independently consulted. L517 onward remains pending.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p280 notes 1-8 hashes verified; planned new candidates=12, mentions=26, statements=9")
print("three work sketches/paintings are kept distinct; location and sale statements remain source-reported")
print("the Devonshire title group and Burlington estate remain type/scope unresolved; transfer remains probable")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
candidates.extend(newc)
mentions.extend(newm)
statements.extend(newstatements)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print(f"applied; recovery copies use suffix {BACKUP}")
