"""Controlled S2 migration for printed p.289; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l218-227"
SEG = "chp-10:10_CHP-10_intro:l229-238"
NEXT = "chp-10:10_CHP-10_intro:l240-251"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "fc2d2cf00ac9cb0a80e837abec720a8373b7472e5fe45595f85bb1bcdd2b9446"
BACKUP = ".bak-s2-chp10-p289-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(src[228:238])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != SEG_SHA or src[228].strip() != "[Page 289]":
    raise SystemExit("p.289 source segment hash/page mismatch")
if "theme of Memento Mori." not in src[240]:
    raise SystemExit("p.290 continuation no longer matches the inspected scan")

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
if maximum != 9015:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")), (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "canaletto": "cand-0498", "cimaroli": "cand-0758", "mcswiny": "cand-1466",
    "marco_ricci": "cand-2151", "sebastiano_ricci": "cand-2171", "devonshire": "cand-0918",
    "richmond": "cand-2193", "bologna": "cand-0381", "venice": "cand-2719",
    "scheme": "cand-9007", "artist_group": "cand-9009", "british_worthies": "cand-9013",
    "england": "cand-8983",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
if next(row for row in candidates if row["candidate_id"] == E["marco_ricci"])["sub_entry"] != "Monuments to (McSwiny's British Worthies)":
    raise SystemExit("Marco Ricci index sub-entry changed")
if next(row for row in candidates if row["candidate_id"] == E["sebastiano_ricci"])["sub_entry"] != "Monuments to (McSwiny's British Worthies)":
    raise SystemExit("Sebastiano Ricci index sub-entry changed")

NEW_SPECS = [
    ("devonshire_monument", "McSwiny's monument to the Duke of Devonshire (untitled)", "work",
     "An individual work in McSwiny's British Worthies scheme; Haskell says Marco and Sebastiano Ricci collaborated on it. No title, date, or location is specified in the p.289 body. The artist table in note 1 remains to be migrated from the consolidated notes segment.", 230),
    ("capricci_genre", "Capricci with picturesque ruins and spectators (art genre)", "term",
     "Haskell uses capricci for a later-century taste in pictures of crumbling ruins and elegant spectators, marked by romantic melancholy and a picturesque adaptation of the memento mori theme. This is a genre-level reference, distinct from the specifically attributed Capriccio pittoresco candidate.", 232),
]
newc, C = [], {}
for i, (key, name, kind, detail, line) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{i:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    newc.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                 "index_page_range": "", "suggested_type": kind, "status": "open",
                 "index_source_file": "", "sub_entry": "", "detail": detail,
                 "exclude_reason": "", "candidate_origin": "body-mention",
                 "candidate_source_ref": f"{SEG}#L{line}"})

scheme = next(row for row in candidates if row["candidate_id"] == E["scheme"])
if scheme["canonical_name"] != "McSwiny's proposed allegorical tomb series for England's recent great men":
    raise SystemExit("unexpected McSwiny scheme candidate")
old_scheme_detail = "Proposed commission on behalf of Lord March; p.288 describes intended subjects, political scope, format and division of roles. Proposals and intended designs are not all proof of execution."
if scheme["detail"] != old_scheme_detail:
    raise SystemExit("McSwiny scheme detail changed")
scheme["detail"] = "Proposed commission on behalf of Lord March; p.288 describes intended subjects, political scope, format and division of roles. P.289 reports fifteen pictures begun by 1722 and Haskell's judgement that the series failed its declared purpose; the extent of acquisition is qualified by note 2, pending migration. Not all proposals or intended designs prove completion."
artist_group = next(row for row in candidates if row["candidate_id"] == E["artist_group"])
old_group_detail = "Collective artists proposed for McSwiny's scheme. Haskell names painters from Bologna and Venice, but this passage does not assign every individual role or identify which artists were the one or two exceptions; note 2 remains pending."
if artist_group["detail"] != old_group_detail:
    raise SystemExit("Italian artist group detail changed")
artist_group["detail"] = "Collective artists proposed for McSwiny's scheme. Haskell names painters from Bologna and Venice, does not assign every individual role, and says the four Venetian artists were beginning their careers while Canaletto was almost unknown; note 2 remains pending."

offsets, offset = {}, 0
for line in range(229, 239):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p289-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    positions, at = [], 0
    while True:
        at = src[line - 1].find(surface, at)
        if at < 0:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}")
    start = offsets[line] + positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTIONS = [
    ("canaletto-careers", 230, "Canaletto", E["canaletto"], "Name in the continuation of the p.288 sentence; Haskell says he was almost unknown."),
    ("sebastiano-ricci", 230, "Sebastiano", E["sebastiano_ricci"], "Mapped to the index sub-entry for the McSwiny monument to the Duke of Devonshire; global identity alignment remains S3."),
    ("marco-ricci", 230, "Marco Ricci", E["marco_ricci"], "Mapped to the index sub-entry for the McSwiny monument to the Duke of Devonshire; global identity alignment remains S3."),
    ("monument", 230, "the monument", C["devonshire_monument"], "Untitled individual work in the proposed series; note 1's artist table remains pending."),
    ("devonshire", 230, "Duke of Devonshire", E["devonshire"], "Title-only reference; personal identity is not inferred here."),
    ("scheme-began", 230, "The scheme", E["scheme"], "Refers to McSwiny's proposed British Worthies monument series."),
    ("fifteen-pictures", 230, "fifteen pictures", E["scheme"], "The source reports that fifteen pictures had been started by 1722; note 2 qualifies later acquisition."),
    ("richmond", 230, "Duke of Richmond", E["richmond"], "Haskell says most pictures were later acquired by the Duke; note 2 discusses uncertainty over the list."),
    ("mcswiny-conception", 231, "McSwiny’s", E["mcswiny"], "Authorial attribution of the scheme's conception."),
    ("paintings", 231, "the paintings", E["scheme"], "Refers to the pictures in McSwiny's series."),
    ("pieces", 231, "many of the pieces", E["scheme"], "Works within the proposed monument series."),
    ("british-worthies", 231, "a Set of British Worthies", E["british_worthies"], "Quoted declared purpose of the scheme; quotation is reported by Haskell."),
    ("country", 232, "their Country", E["england"], "In the quoted statement, refers to England."),
    ("monumental-pieces", 232, "these ‘monumental pieces’", E["scheme"], "Haskell's characterization of works in the series."),
    ("capricci", 232, "capricci", C["capricci_genre"], "Genre term in Haskell's comparison; not an identified individual painting."),
]
for item in MENTIONS:
    add_m(*item)

new_s = []


def quote(start, end):
    first = body.find(start)
    if first < 0:
        raise SystemExit(f"quote start absent: {start!r}")
    last = body.find(end, first)
    if last < 0:
        raise SystemExit(f"quote end absent: {end!r}")
    return body[first:last + len(end)]


def add_s(sid, lo, hi, subject, obj, predicate, start, end, claim, qualification,
          mentioned, speaker="Haskell", layer="authorial narrative", relation=False,
          footnote=None, cross=None, continuation=None):
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 289,
                  "pdf_physical_page": 18, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
    if cross:
        qualifiers["cross_reference_segments"] = cross
    if continuation:
        qualifiers["continuation_quote"] = continuation
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


career = next((row for row in statements if row["statement_id"] == "st-chp10-p288-venetian-careers-open"), None)
if not career or career["segment_id"] != PREV:
    raise SystemExit("expected p.288 Venetian-careers open statement missing")
career["qualifiers"]["claim"] = "Haskell says the four Venetian artists were beginning their careers and that Canaletto was as yet almost unknown."
career["qualifiers"]["qualification"] = "The sentence opens on p.288 L227 and closes at p.289 L230; this remains Haskell's characterization, not an independent career chronology."
career["qualifiers"]["continuation_quote"] = "careers and Canaletto was as yet almost unknown."
career["qualifiers"]["cross_reference_segments"] = [{"segment_id": SEG, "source_line_start": 230, "source_line_end": 230}]
career["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(career["qualifiers"].get("mentioned_candidate_ids", []) + [E["canaletto"]]))

add_s("st-chp10-p289-devonshire-monument-subject",230,230,C["devonshire_monument"],E["devonshire"],
      "monument_commemorates_duke_of_devonshire",
      "the monument to the Duke of Devonshire", "the monument to the Duke of Devonshire",
      "Haskell identifies an untitled monument in McSwiny's series to the Duke of Devonshire.",
      "The page's note 1 artist table remains pending in the consolidated notes segment; the duke's personal identity is not inferred.",
      [C["devonshire_monument"],E["devonshire"],E["scheme"]],relation=True,footnote=1)
add_s("st-chp10-p289-marco-ricci-collaborated",230,230,E["marco_ricci"],C["devonshire_monument"],
      "marco_ricci_collaborated_on_monument",
      "Sebastiano and Marco Ricci who collaborated on the monument", "collaborated on the monument",
      "Haskell says Marco Ricci collaborated on the monument to the Duke of Devonshire.",
      "The exact work title and individual identity resolution remain open; note 1's artist list is pending.",
      [E["marco_ricci"],E["sebastiano_ricci"],C["devonshire_monument"]],relation=True,footnote=1)
add_s("st-chp10-p289-sebastiano-ricci-collaborated",230,230,E["sebastiano_ricci"],C["devonshire_monument"],
      "sebastiano_ricci_collaborated_on_monument",
      "Sebastiano and Marco Ricci who collaborated on the monument", "collaborated on the monument",
      "Haskell says Sebastiano Ricci collaborated on the monument to the Duke of Devonshire.",
      "The exact work title and individual identity resolution remain open; note 1's artist list is pending.",
      [E["sebastiano_ricci"],E["marco_ricci"],C["devonshire_monument"]],relation=True,footnote=1)
add_s("st-chp10-p289-ricci-fee-inference",230,230,C["devonshire_monument"],None,
      "haskell_infers_established_riccis_required_substantial_fee_for_menial_work_for_a_commoner",
      "were already well", "for a commoner.",
      "Haskell describes the Riccis as already well-established painters and infers that they must have required a substantial fee to produce what he calls menial work for a commoner.",
      "This is the author's inference and evaluative language; it does not establish a fee amount or independently classify the patron's legal status. The print hyphenates well-established; S0 OCR is left unchanged.",
      [E["sebastiano_ricci"],E["marco_ricci"],C["devonshire_monument"],E["devonshire"]],
      layer="authorial assessment and inference",footnote=1)
add_s("st-chp10-p289-pictures-started-richmond-acquisition",230,230,E["scheme"],E["richmond"],
      "fifteen_pictures_started_by_1722_and_most_later_acquired_by_duke_of_richmond",
      "The scheme began well", "the Duke of Richmond.",
      "Haskell says the scheme began well, fifteen pictures had been started by 1722, and most were later acquired by the Duke of Richmond.",
      "The count and acquisition are Haskell's account. Note 2 explicitly discusses confusion about which pictures the Duke acquired and remains pending in the consolidated notes segment.",
      [E["scheme"],E["richmond"]],relation=True,footnote=2)
add_s("st-chp10-p289-project-difficulties",231,231,E["scheme"],E["mcswiny"],
      "haskell_attributes_project_difficulties_to_mcswinys_conception",
      "Yet it ran into difficulties", "McSwiny’s conception of the paintings.",
      "Haskell says the scheme ran into difficulties that were almost inseparable from McSwiny's conception of the paintings.",
      "This is Haskell's interpretive causal assessment, not an independently demonstrated cause.",
      [E["scheme"],E["mcswiny"]],layer="authorial interpretation")
add_s("st-chp10-p289-declared-aim-failure",231,232,E["scheme"],E["british_worthies"],
      "haskell_says_pictures_failed_declared_aim_to_preserve_memory_of_british_worthies",
      "For attractive as many of the pieces are", "Ornaments to their Country",
      "Haskell says that although many pieces were attractive, they entirely failed their declared purpose of preserving the memory of British Worthies who had been ornaments to their country.",
      "This is Haskell's evaluation of how successfully the works met the quoted aim; the quoted purpose is not treated as a completed outcome.",
      [E["scheme"],E["british_worthies"],E["england"]],layer="authorial evaluation with quoted purpose")
add_s("st-chp10-p289-picturesque-capricci",232,232,E["scheme"],C["capricci_genre"],
      "haskell_says_monumental_pieces_anticipate_later_capricci_and_picturesque_memento_mori_melancholy",
      "Rather, these", "the old",
      "Haskell says the monumental pieces anticipate a later-century taste for capricci whose romantic melancholy arises from the contrast between ruins and elegantly dressed spectators, a picturesque adaptation of the old theme of Memento Mori.",
      "The sentence closes at p.290 L241 with 'theme of Memento Mori'; that continuation has been checked against the scan and is cross-linked. This is Haskell's art-historical interpretation, not a claim about every individual work.",
      [E["scheme"],C["capricci_genre"]],layer="authorial interpretation",
      cross=[{"segment_id":NEXT,"source_line_start":241,"source_line_end":241}],
      continuation="theme of Memento Mori.")

if career["qualifiers"].get("continuation_quote") not in body:
    raise SystemExit("p.288 career continuation is absent from p.289")
if cov[PREV]["note"] and "p.289 L230" not in cov[PREV]["note"]:
    raise SystemExit("p.288 coverage note lacks the cross-page closure")
cov[PREV].update({"migration_status":"complete","source_line_ranges":"L219-227; p.289 L230",
                  "note":"Printed p.288 was read against physical page 17. Its final career sentence closes at p.289 L230; Haskell says Canaletto was as yet almost unknown. Notes 1-3 are a separate consolidated notes segment (L540-542) and are tracked there, not duplicated in this body segment."})
cov[SEG].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L230-232; p.290 L241",
                 "note":"Printed p.289 was checked against CHP-10.pdf physical page 18. Closed p.288 L227's sentence: Haskell says the four Venetian artists were beginning their careers and Canaletto was almost unknown. Recorded the Riccis' collaboration on the Duke of Devonshire monument, Haskell's fee inference, fifteen pictures begun by 1722 and most later acquired by the Duke of Richmond (note 2 pending), the scheme's difficulties and failure to meet its declared purpose, and Haskell's capricci/picturesque comparison. The final sentence continues at p.290 L241 ('theme of Memento Mori'). Scan correction only: OCR 'wellestablished' is printed 'well-established'; S0 remains unchanged. L233-238 are partial page-note excerpts; their full contents are in consolidated notes L543-544 and remain pending there, so this segment stays partial."})
cov[NEXT]["note"] = "Next source-order segment is printed p.290 at L240-251; L241 closes p.289's capricci/picturesque sentence. P.289 note excerpts L233-238 still await consolidated notes L543-544."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"new_candidates":len(newc),"updated_candidates":[E["scheme"],E["artist_group"]],
                  "new_mentions":len(newm),"new_statements":len(new_s),
                  "new_candidate_ids":[row["candidate_id"] for row in newc],
                  "coverage":{"p288":cov[PREV]["migration_status"],"p289":cov[SEG]["migration_status"],"p290":cov[NEXT]["migration_status"]}},ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup=Path(str(path)+BACKUP)
        if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.289 S2 migration; p.288 is complete, p.289 remains partial pending consolidated notes.")
