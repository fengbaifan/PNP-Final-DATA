"""Controlled p.305 note 1 migration; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
SOURCE_REL = "02-sources/02-Markdown/10_CHP-10_intro.md"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
P305_BODY = "chp-10:10_CHP-10_intro:l423-433"
P306_BODY = "chp-10:10_CHP-10_intro:l435-443"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
LINE_SHA = {
    428: "f3a343d1853ff01439ff9eeca049ca49c132d404a3f5e3fb3c00b884eba3a9b5",
    441: "93d8dbb555f0e2858637ad778789429d26eb7d30cb133f6ea9062a12e10a02f2",
    611: "d797ad9a7ce48ade35922558c2a8f6b27d3bc33d494dcd8a19fa0151251c065e",
}
BACKUP_SUFFIX = ".bak-s2-chp10-p305-note1-20261002"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(f.name)
    temp.replace(path)


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(f.name)
    temp.replace(path)


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def offset(lines, segment_start, line_number, surface):
    local = lines[line_number - 1].find(surface)
    if local < 0:
        raise SystemExit(f"surface not found on L{line_number}: {surface!r}")
    return sum(len(x) + 1 for x in lines[segment_start - 1:line_number - 1]) + local


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("canonical OCR asset changed")
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for n, expected in LINE_SHA.items():
    if digest(lines[n - 1]) != expected:
        raise SystemExit(f"source line L{n} changed")
if lines[610].strip() != "1 Constable, 1976.":
    raise SystemExit("p.305 note 1 text changed")

cp, mp, sp, vp = [TABLES / x for x in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {x["candidate_id"] for x in candidates}
mids = {x["mention_id"] for x in mentions}
by_statement = {x["statement_id"]: x for x in statements}
by_coverage = {x["segment_id"]: x for x in coverage}
next_id = max(int(re.search(r"(\d+)$", x).group(1)) for x in cids) + 1
if next_id != 9545 or "cand-9545" in cids:
    raise SystemExit(f"candidate sequence changed: next={next_id}")
for sid, status, source_range in ((NOTES, "partial", "L492-610"), (P305_BODY, "partial", "L424-433"), (P306_BODY, "partial", "L436-441")):
    row = by_coverage.get(sid)
    actual = (row["migration_status"], row["source_line_ranges"]) if row else None
    if actual != (status, source_range):
        raise SystemExit(f"coverage changed for {sid}: {actual}")
for cid in ("cand-9368", "cand-0379", "cand-9339", "cand-9340", "cand-9214", "cand-9230"):
    if cid not in cids:
        raise SystemExit(f"required candidate missing: {cid}")
pub = next(x for x in candidates if x["candidate_id"] == "cand-9340")
pub_detail = ("Matched to the joint local bibliography entry. P.284 note 5 and p.300 note 2 cite pp.61-63 and pp.137 ff.; "
              "p.302 note 5 gives the short form Blunt, 1957, p.12, note 6, a possible reference to this volume. "
              "Neither cited passage nor the book was independently consulted.")
if pub["detail"] != pub_detail:
    raise SystemExit("cand-9340 changed; inspect before adding the p.306 locator")
expected_markers = {
    "st-chp10-p305-smith-first-six-views": 1,
    "st-chp10-p305-visentini-tourist-access": 2,
    "st-chp10-p305-tessin-and-working-pause": 2,
    "st-chp10-p306-pasquali-visentini-drawings": 1,
}
for sid, marker in expected_markers.items():
    row = by_statement.get(sid)
    if not row or row["qualifiers"].get("footnote_marker") != marker or row["qualifiers"].get("footnote_text_pending") is not True:
        raise SystemExit(f"body marker state changed: {sid}")
new_sids = {"st-chp10-p305-note1-constable-citation", "st-chp10-p306-note1-blunt-citation"}
new_mids = {
    "m-chp10-p305-note1-constable-author", "m-chp10-p305-note1-1976-source",
    "m-chp10-p306-note1-blunt-author", "m-chp10-p306-note1-croft-murray-author",
    "m-chp10-p306-note1-joint-publication",
}
if new_sids.intersection(by_statement) or new_mids.intersection(mids):
    raise SystemExit("p.305/p.306 note-1 rows already exist")


def add_mention(mid, segment, cid, segment_start, line_no, surface, note):
    start = offset(lines, segment_start, line_no, surface)
    mentions.append({"mention_id": mid, "segment_id": segment, "candidate_id": cid, "surface_form": surface,
                     "start_char": str(start), "end_char": str(start + len(surface)), "note": note})


candidates.append({
    "candidate_id": "cand-9545", "index_entry_id": "",
    "canonical_name": "Constable, 1976 (citation locator; work and page unspecified)", "index_page_range": "",
    "suggested_type": "archive", "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": "Haskell’s p.305 note 1 gives only Constable, 1976, after the account of Canaletto’s first six S. Marco views. The publication title and cited page are unspecified; the source was not independently consulted. Do not identify it from the author-year form alone.",
    "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTES}#L611",
})
add_mention("m-chp10-p305-note1-constable-author", NOTES, "cand-9368", 491, 611, "Constable", "Surname-only cited author; identity is unresolved and is not merged with John Constable.")
add_mention("m-chp10-p305-note1-1976-source", NOTES, "cand-9545", 491, 611, "1976", "Year in the p.305 note-1 citation; publication title and page are not supplied.")
add_mention("m-chp10-p306-note1-blunt-author", P306_BODY, "cand-0379", 435, 441, "Blunt", "Co-author named in p.306 note 1; the joint book is candidate cand-9340.")
add_mention("m-chp10-p306-note1-croft-murray-author", P306_BODY, "cand-9339", 435, 441, "Croft-Murray", "Surname-only co-author; identity remains unresolved.")
add_mention("m-chp10-p306-note1-joint-publication", P306_BODY, "cand-9340", 435, 441, "Blunt and Croft-Murray, pp. 67 if", "OCR-inline citation on L441; the page scan reads pp.67 ff.")

pub["detail"] = pub_detail[:-1] + " P.306 note 1 cites pp.67 ff.; scan reads ff. where OCR L441 has ‘if’. The cited pages remain unread."
first_q = by_statement["st-chp10-p305-smith-first-six-views"]["qualifiers"]
first_q["footnote_text_pending"] = False
first_q["qualification"] = "‘First’ is Haskell’s ordering and S. Marco’s precise spatial scope remains open. Printed footnote 1 cites only Constable, 1976; its title and page are unspecified and the citation was not independently checked."
if NOTES not in first_q.setdefault("cross_reference_segments", []):
    first_q["cross_reference_segments"].append(NOTES)

for sid, text in (
    ("st-chp10-p305-visentini-tourist-access", "The page scan shows no footnote marker after ‘get to know it’; the OCR apostrophe is not a marker. The 1735 publication claim remains Haskell’s narrative and has no p.305 note reference."),
    ("st-chp10-p305-tessin-and-working-pause", "The page scan shows no footnote marker after ‘get to know it’; the OCR apostrophe is not a marker. Preserve the reported exclusive engagement and Haskell’s apparent-work-pause tension."),
):
    q = by_statement[sid]["qualifiers"]
    for key in ("footnote_marker", "footnote_text_pending", "cross_reference_segments", "cross_reference_printed_pages"):
        q.pop(key, None)
    q["qualification"] = text

p306_drawing = by_statement["st-chp10-p306-pasquali-visentini-drawings"]
p306_drawing["qualifiers"]["footnote_text_pending"] = False
p306_drawing["qualifiers"]["qualification"] = "Haskell says Smith retained original drawings, most by Visentini. Printed note 1 follows ‘Visentini’ on L437; OCR places its citation text inline after the Breval passage at L441. The scan reads pp.67 ff.; the cited pages were not consulted."
p306_body = by_statement["st-chp10-p306-breval-statuette"]
p306_q = p306_body["qualifiers"]
p306_q.pop("footnote_marker", None)
p306_q.pop("footnote_text_pending", None)
p306_q["qualification"] = "The p.307 continuation calls the same quoted object Priapus after p.306’s ‘seemingly an Aesculapius’; preserve both labels without resolving the statuette. The p.306 scan shows no footnote marker after this passage."
p306_q["cross_reference_segments"] = [x for x in p306_q.get("cross_reference_segments", []) if x != NOTES]
if not p306_q["cross_reference_segments"]:
    p306_q.pop("cross_reference_segments", None)
p306_body["original_quote"] = ("It was at about this time too that the connoisseur John Breval visited Smith’s collection and was shown "
                                "a little statuette which represented ‘seemingly an Aesculapio")

p305_statement = {
    "statement_id": "st-chp10-p305-note1-constable-citation", "segment_id": NOTES,
    "subject_candidate_id": "cand-9545", "object_candidate_id": "cand-9214",
    "predicate": "cited_source_for_first_six_views_account",
    "qualifiers": {"source_line_start": 611, "source_line_end": 611, "printed_page": 305, "pdf_physical_page": 34,
                   "claim": "Haskell cites Constable, 1976, after describing Canaletto’s first six views of S. Marco and their scale and style.",
                   "speaker": "Haskell citation", "text_layer": "bibliographic locator",
                   "qualification": "The publication title and page are unspecified; neither the source nor cited passage was independently consulted.",
                   "mentioned_candidate_ids": ["cand-9368", "cand-9545", "cand-9214"], "relation_candidate": False,
                   "cross_reference_segments": [P305_BODY], "cross_reference_printed_pages": [305]},
    "original_quote": "1 Constable, 1976.", "source_file": SOURCE_REL, "origin": "book",
}
p306_statement = {
    "statement_id": "st-chp10-p306-note1-blunt-citation", "segment_id": P306_BODY,
    "subject_candidate_id": "cand-9340", "object_candidate_id": "cand-9227",
    "predicate": "cited_source_for_smiths_retention_of_original_visentini_drawings",
    "qualifiers": {"source_line_start": 441, "source_line_end": 441, "printed_page": 306, "pdf_physical_page": 35,
                   "claim": "Haskell cites Blunt and Croft-Murray, pp.67 ff., in connection with Smith retaining the original drawings, most of which were by Visentini.",
                   "speaker": "Haskell citation", "text_layer": "bibliographic locator",
                   "qualification": "The printed marker follows ‘Visentini’ on L437; OCR places the citation text inline after the Breval passage at L441. The scan reads ‘ff.’ where OCR has ‘if’; the cited pages were not independently consulted.",
                   "mentioned_candidate_ids": ["cand-0379", "cand-9339", "cand-9340", "cand-2440", "cand-9227", "cand-2783"],
                   "printed_marker_line": 437,
                   "body_statement_id": "st-chp10-p306-pasquali-visentini-drawings",
                   "relation_candidate": False},
    "original_quote": "Blunt and Croft-Murray, pp. 67 if.", "source_file": SOURCE_REL, "origin": "book",
}
statements.extend([p305_statement, p306_statement])

by_coverage[NOTES]["source_line_ranges"] = "L492-611"
by_coverage[NOTES]["note"] = ("Merged notes processed through p.305 note 1 at L611. P.305 has only this printed note; p.306 note 1 is "
                              "OCR-inline in body L441 and reconciled there, so L612 begins p.306 note 2. Next: p.306 notes 2-6, L612-L616.")
by_coverage[P305_BODY]["note"] = ("Printed p.305 checked against CHP-10.pdf physical page 34. Its only marker is note 1 after ‘almost impressionistic’ "
                                  "at L425, linked to L611. The scan confirms no marker after ‘get to know it’; the OCR apostrophe is not a footnote. "
                                  "The body continues through p.306, so coverage remains partial. Scan-only OCR corrections remain at S2; S0 is unchanged.")
by_coverage[P306_BODY]["note"] += (" Printed p.306 note 1 follows ‘Visentini’ at L437 and is linked to the original-drawings statement. "
                                   "OCR places its citation text at L441; the Breval statuette passage has no marker. Notes 2-6 remain for L612-L616.")

print("dry-run: add 1 candidate, 5 mentions and 2 statements; correct p.305 markers and reconcile p.306 note 1")
if not args.apply:
    raise SystemExit(0)
for path in (cp, mp, sp, vp):
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print("applied; four table backups saved with suffix", BACKUP_SUFFIX)
