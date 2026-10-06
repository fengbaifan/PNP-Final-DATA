"""Controlled S2 migration for p.284 notes 1-5 (merged source L524-L527)."""
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
BODY = "chp-10:10_CHP-10_intro:l167-176"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINES_SHA = "ca8e1a9485c4da58c1b161645bc2351ee69ff50e19248f679a300c9f4be1ab01"
BACKUP = ".bak-s2-chp10-p284-notes1-5-20261002"


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
if hashlib.sha256("\n".join(src[523:527]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.284 source lines 524-527 changed")
if not src[523].startswith("1 Another Venetian painter") or not src[524].startswith("2 See the letter from Rosalba Carriera"):
    raise SystemExit("p.284 notes 1-2 changed")
if not src[525].startswith("3 For Crozat see Mariette") or not src[526].startswith("4 De La Fosse"):
    raise SystemExit("p.284 notes 3-5 changed")

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
if maximum != 9331:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("reviewed", "partial"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-523":
    raise SystemExit("notes coverage pre-state changed")

target_ids = {
    "st-chp10-p284-bellucci-veronese-appreciation": 1,
    "st-chp10-p284-pellegrini-low-countries": 2,
    "st-chp10-p284-crozat-mansion-collection": 3,
    "st-chp10-p284-la-fosse-lodged-and-aged": 4,
    "st-chp10-p284-la-fosse-view-of-ricci": 4,
    "st-chp10-p284-ricci-copied-watteau-drawing": 5,
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(target_ids) <= by_sid.keys():
    raise SystemExit(f"p.284 body targets missing: {set(target_ids)-by_sid.keys()}")
body_targets = {sid: by_sid[sid] for sid in target_ids}
for sid, marker in target_ids.items():
    q = body_targets[sid].get("qualifiers", {})
    if q.get("footnote_marker") != marker or not q.get("footnote_text_pending"):
        raise SystemExit(f"p.284 body footnote state changed: {sid}: {q}")
# The same-numbered marker on the p.285 continuation belongs to the next note at L528.
p285_target = by_sid.get("st-chp10-p284-mississippi-programme-open")
if not p285_target or p285_target.get("qualifiers", {}).get("footnote_marker") != 1 or not p285_target.get("qualifiers", {}).get("footnote_text_pending"):
    raise SystemExit("p.285 continuation marker 1 state changed")

required = {"cand-2860", "cand-0955", "cand-1325", "cand-9322", "cand-0581", "cand-1547",
            "cand-9290", "cand-9291", "cand-0894", "cand-1343", "cand-2154", "cand-2755",
            "cand-2798", "cand-7058", "cand-0379"}
if not required <= cids:
    raise SystemExit(f"existing S2 candidates missing: {required-cids}")

NEW_CANDIDATES = [
    ("cand-9332", "de Pigage (surname-only source/attribution in p.284 note 1; identity unresolved)", "person",
     "Haskell's note appends 'de Pigage' after Domenico Zanetti. Its function and identity, including possible relation to Nicolas de Pigage (cand-9322), remain unresolved; do not treat it as an alias."),
    ("cand-9333", "Letter from Rosalba Carriera to Pierre-Jean Mariette (published by Sensier, p.95)", "archive",
     "Cited in Haskell's p.284 note 2; the letter and Sensier's publication were not independently consulted."),
    ("cand-9334", "Mariette, vol. II, pp.43-53 (citation locator in p.284 note 3)", "archive",
     "Short-form source pointer in the Crozat note; cited pages not independently consulted."),
    ("cand-9335", "H. Adhémar, p.82 (citation locator in p.284 note 3)", "archive",
     "Short-form source pointer in the Crozat note; title and edition are not supplied here and the page was not consulted."),
    ("cand-9336", "Stuffman (citation locator in p.284 note 3; work unresolved)", "archive",
     "Surname-only reference in Haskell's Crozat note; no title, year, or page is given and no identity is inferred."),
    ("cand-9337", "Levey, 1959, p.22 (citation locator in p.284 note 4)", "archive",
     "Haskell says Levey quotes Walpole's Anecdotes for the reported remark; the cited page was not independently consulted."),
    ("cand-9338", "Levey (author named in p.284 note 4; identity unresolved)", "person",
     "The note supplies surname and year only. Keep distinct from other Levey candidates until bibliography review and S3 alignment."),
    ("cand-9339", "Croft-Murray (author named in p.284 note 5; identity unresolved)", "person",
     "The note supplies surname only; no personal identity is inferred."),
    ("cand-9340", "Blunt and Croft-Murray, 1957, pp.61-63 (citation locator in p.284 note 5)", "archive",
     "Short-form bibliographic reference; title and cited pages were not independently consulted."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
newc = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES}#L{524 if cid == 'cand-9332' else 525 if cid == 'cand-9333' else 526 if cid in {'cand-9334','cand-9335','cand-9336'} else 527}",
} for cid, name, kind, detail in NEW_CANDIDATES]

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1
newm = []


def add_mention(local, line_no, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p284notes-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in newm):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[line_no - 1]
    at = line.find(surface)
    if at < 0:
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = offsets[line_no] + at
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    newm.append({
        "mention_id": mention_id, "segment_id": NOTES, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention("zanetti-city", 524, "Diisseldorf", "cand-0955", "Print reads Düsseldorf; S0 OCR remains unchanged.")
add_mention("zanetti-elector", 524, "the Elector", "cand-1325")
add_mention("zanetti", 524, "Domenico Zanetti", "cand-2860")
add_mention("de-pigage", 524, "de Pigage", "cand-9332", "Surname-only attribution/reference; possible identity with cand-9322 held for S3.")
add_mention("carriera", 525, "Rosalba Carriera", "cand-0581")
add_mention("carriera-letter", 525, "the letter from Rosalba Carriera to Mariette", "cand-9333")
add_mention("mariette-letter", 525, "Mariette", "cand-1547")
add_mention("sensier-letter-author", 525, "Sensier", "cand-9291")
add_mention("sensier-letter-source", 525, "Sensier, p. 95", "cand-9290", "Citation locator only; cited letter was not consulted.")
add_mention("crozat", 526, "Crozat", "cand-0894")
add_mention("mariette-crozat-author", 526, "Mariette", "cand-1547")
add_mention("mariette-volume2", 526, "Mariette, II, pp. 43-53", "cand-9334", "Citation locator only; cited pages were not consulted.")
add_mention("sensier-crozat-source", 526, "Sensier", "cand-9290", "Short-form citation only; cited material was not consulted.")
add_mention("adhemar", 526, "H. Adhémar, p. 82", "cand-9335", "Citation locator only; cited page was not consulted.")
add_mention("stuffman", 526, "Stuffman", "cand-9336", "Surname-only citation locator; no identity inferred.")
add_mention("de-la-fosse", 527, "De La Fosse", "cand-1343")
add_mention("ricci-remark", 527, "Ricci", "cand-2154")
add_mention("veronese-works", 527, "Paul Veroneses", "cand-2755", "Plural refers to works associated with Paolo Veronese; no individual work is named.")
add_mention("ricci-works", 527, "Riccis", "cand-2154", "Plural in the reported quotation refers to works associated with Sebastiano Ricci.")
add_mention("levey-author", 527, "Levey", "cand-9338")
add_mention("levey-locator", 527, "Levey, 1959, p. 22", "cand-9337", "Citation locator only; cited page was not consulted.")
add_mention("walpole-author", 527, "Walpole", "cand-2798")
add_mention("walpole-anecdotes", 527, "Walpole’s Anecdotes", "cand-7058", "Source named through Levey; the cited passage was not consulted.")
add_mention("blunt-author", 527, "Blunt", "cand-0379")
add_mention("croft-murray-author", 527, "Croft-Murray", "cand-9339")
add_mention("blunt-croft-locator", 527, "Blunt and Croft-Murray, 1957, pp. 61-3.", "cand-9340", "Citation locator only; cited pages were not consulted.")

target_by_id = {sid: by_sid[sid] for sid in target_ids}
note1_body_ids = ["st-chp10-p284-bellucci-veronese-appreciation"]
note4_body_ids = ["st-chp10-p284-la-fosse-lodged-and-aged", "st-chp10-p284-la-fosse-view-of-ricci"]
statement_ids = [
    "st-chp10-notes-p284n1-zanetti-elector-dusseldorf",
    "st-chp10-notes-p284n4-la-fosse-remark-to-ricci",
]
if set(statement_ids) & sids:
    raise SystemExit("one or more planned statement IDs already exist")
quote1 = src[523][2:]
line4 = src[526]
quote4_start = line4.index("De La Fosse")
quote4_end = line4.index(". 5 Blunt", quote4_start) + 1
quote4 = line4[quote4_start:quote4_end]
if "Domenico Zanetti" not in quote1 or "Diisseldorf" not in quote1:
    raise SystemExit("p.284 note 1 statement text is not anchored")
if "Paint nothing but Paul Veroneses" not in quote4 or "must presumably have been made on this occasion" not in quote4:
    raise SystemExit("p.284 note 4 quotation/inference is not anchored")

newstatements = [
    {
        "statement_id": statement_ids[0], "segment_id": NOTES,
        "subject_candidate_id": "cand-2860", "object_candidate_id": "cand-1325",
        "predicate": "domenico_zanetti_worked_extensively_for_johann_wilhelm_at_dusseldorf",
        "qualifiers": {
            "source_line_start": 524, "source_line_end": 524, "printed_page": 284, "pdf_physical_page": 13,
            "claim": "Haskell identifies Domenico Zanetti as another Venetian painter who worked extensively for the Elector at Düsseldorf.",
            "speaker": "Haskell, footnote", "text_layer": "authorial note",
            "qualification": "The trailing '—de Pigage' is preserved as a surname-only attribution/reference. Its function and possible identity with Nicolas de Pigage in p.282 note 2 remain unresolved; it is not treated as Zanetti's alias. The claim is not independently verified.",
            "mentioned_candidate_ids": ["cand-2860", "cand-1325", "cand-0955", "cand-9332"],
            "possible_identity_candidates": ["cand-9322"],
            "footnote_number": 1, "related_body_statement_ids": note1_body_ids,
            "relation_candidate": True,
            "ocr_corrections": [{"source_file": SOURCE_FILE, "source_line": 524, "ocr": "Diisseldorf", "print": "Düsseldorf", "basis": "CHP-10.pdf physical page 13."}],
        },
        "original_quote": quote1, "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": statement_ids[1], "segment_id": NOTES,
        "subject_candidate_id": "cand-1343", "object_candidate_id": "cand-2154",
        "predicate": "haskell_reports_de_la_fosse_remark_to_ricci_and_probably_places_it_at_crozat_house",
        "qualifiers": {
            "source_line_start": 527, "source_line_end": 527, "printed_page": 284, "pdf_physical_page": 13,
            "claim": "Haskell reports a remark attributed to Charles de La Fosse telling Ricci to paint Veronese works rather than Ricci works, and says it must presumably have been made on this occasion.",
            "speaker": "Charles de La Fosse, as reported through Haskell's nested citation",
            "text_layer": "reported quotation mediated by Levey from Walpole, plus Haskell's authorial inference",
            "qualification": "The wording is reported through Levey (1959, p.22) from Walpole's Anecdotes, neither consulted here. Haskell's 'must presumably' marks the timing as inference; 'this occasion' refers to the surrounding account of Ricci's arrival and La Fosse lodging at Crozat's house, not a separately dated event.",
            "mentioned_candidate_ids": ["cand-1343", "cand-2154", "cand-2755", "cand-9337", "cand-9338", "cand-2798", "cand-7058", "cand-0894"],
            "footnote_number": 4, "related_body_statement_ids": note4_body_ids,
            "relation_candidate": True, "cited_material_not_independently_consulted": True,
        },
        "original_quote": quote4, "origin": "book", "source_file": SOURCE_FILE,
    },
]

by_new_sid = {row["statement_id"]: row for row in newstatements}
note_statement_for_marker = {1: [statement_ids[0]], 2: [], 3: [], 4: [statement_ids[1]], 5: []}
marker_to_line = {1: 524, 2: 525, 3: 526, 4: 527, 5: 527}
for sid, marker in target_ids.items():
    q = target_by_id[sid]["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES
    q["footnote_source_line"] = marker_to_line[marker]
    q["footnote_note_statement_ids"] = note_statement_for_marker[marker]
    q["qualification"] = (q.get("qualification", "") +
        (" P.284 note 1 adds Haskell's account of Domenico Zanetti at Düsseldorf; the trailing de Pigage attribution remains unresolved."
         if marker == 1 else
         " P.284 note 2 is a Carriera-to-Mariette letter locator published by Sensier; the cited letter was not consulted."
         if marker == 2 else
         " P.284 note 3 contains short-form Crozat bibliography locators; cited material was not consulted."
         if marker == 3 else
         " P.284 note 4 preserves a nested reported saying and Haskell's explicitly probable timing inference."
         if marker == 4 else
         " P.284 note 5 is a Blunt/Croft-Murray citation locator; cited pages were not consulted.")).strip()

cand_by_id = {row["candidate_id"]: row for row in candidates}
cand_by_id["cand-2860"]["suggested_type"] = "person"
cand_by_id["cand-2860"]["detail"] = "Index candidate for Domenico Zanetti; p.284 note 1 reports that he worked extensively for the Elector at Düsseldorf. The appended de Pigage attribution remains ambiguous."
cand_by_id["cand-0955"]["suggested_type"] = "place"
cand_by_id["cand-0955"]["detail"] += " P.284 note 1 has OCR 'Diisseldorf'; the print reads Düsseldorf, recorded in S2 without changing S0."
cand_by_id["cand-9290"]["detail"] += " P.284 notes 2-3 cite Sensier at p.95 and without a locator respectively; cited material not consulted."
cand_by_id["cand-7058"]["detail"] += " P.284 note 4 again names Walpole's Anecdotes as the source quoted by Levey (1959, p.22); exact volume/page for Walpole is not supplied in this note."
cand_by_id["cand-0379"]["suggested_type"] = "person"
cand_by_id["cand-2798"]["suggested_type"] = "person"

notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-527"
notes_cov["note"] = (notes_cov.get("note", "") +
    " P.284 notes 1-5 at L524-L527 are migrated. Note 1 adds the Domenico Zanetti claim and preserves de Pigage as an unresolved attribution; note 2 cites Carriera's letter to Mariette via Sensier; note 3 gives Crozat source locators; note 4 preserves a nested reported saying and Haskell's probable timing inference; note 5 is a Blunt/Croft-Murray locator. Cited texts were not consulted. The p.285 continuation marker 1 on st-chp10-p284-mississippi-programme-open is a separate footnote and remains pending L528.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p284 source L524-L527 hashes verified; planned new candidates=9, mentions=26, statements=2")
print("all five p284 note markers are linked; the p285 continuation marker 1 remains pending for L528")
print("kept de Pigage identity, nested La Fosse attribution, and probable timing unresolved")
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
