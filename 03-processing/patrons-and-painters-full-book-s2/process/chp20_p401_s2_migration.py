#!/usr/bin/env python3
"""Controlled p.401 S2 migration and closure of the p.400 sentence."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
T = ROOT / "04-knowledge" / "tables"
SRC = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
P400 = "chp-20:20_CHP-20Postscript:l46-57"
P401 = "chp-20:20_CHP-20Postscript:l81-96"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
CH4 = "chp-4:04_CHP-4_sec_ii:l232-308"
PLATE65 = "chp-20:20_CHP-20Postscript:l59-67"
OPEN400 = "st-chp20-p400-cassiano-journal-publication-open"
BACKUP = ".bak-s2-chp20-p401-20261004"
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def read_csv(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)
def write_csv(p, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=p.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader(); w.writerows(rows); temp = Path(f.name)
    temp.replace(p)
def write_jsonl(p, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=p.parent, delete=False) as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(f.name)
    temp.replace(p)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

if sha(SRC) != "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90":
    raise SystemExit("source asset changed")
if sha(PDF) != "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788":
    raise SystemExit("PDF changed")
cp, candidates = read_csv(T / "entity-candidates.csv")
mp, mentions = read_csv(T / "mentions.csv")
statements = [json.loads(x) for x in (T / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if x.strip()]
vp, coverage = read_csv(T / "s2-coverage.csv")
segments = [json.loads(x) for x in (T / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if x.strip()]
segs = {x["segment_id"]: x for x in segments}
cand = {x["candidate_id"]: x for x in candidates}
cov = {x["segment_id"]: x for x in coverage}
stby = {x["statement_id"]: x for x in statements}
for sid in (P400, P401, NOTES, CH4, PLATE65):
    if sid not in segs: raise SystemExit(f"missing segment {sid}")
if (cov[P400]["disposition"], cov[P400]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.400 is not the expected partial segment")
if (cov[P401]["disposition"], cov[P401]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.401 is not queued")
if stby[OPEN400]["qualifiers"].get("continues_in_segment") != P401:
    raise SystemExit("open p.400 statement pointer changed")
if segs[P401]["sha256"] != "b0924c0681aefcbee3af02d1e06da6225ac6631d4331f5e256df2ad4e5f6a697":
    raise SystemExit("p.401 segment hash changed")
if segs[P400]["asset_sha256"] != sha(SRC) or segs[P401]["asset_sha256"] != sha(SRC):
    raise SystemExit("source asset registration mismatch")
lines = SRC.read_text(encoding="utf-8-sig").splitlines()
def text(sid):
    g = segs[sid]
    x = "\n".join(lines[g["line_start"]-1:g["line_end"]])
    if hashlib.sha256(x.encode("utf-8")).hexdigest() != g["sha256"]:
        raise SystemExit(f"segment hash mismatch {sid}")
    return x
body = text(P401)
if "Escorial has been published in full." not in lines[81]: raise SystemExit("p.401 opening changed")
if "Seven Sacraments" not in lines[83] or "Garrns" not in lines[232]: raise SystemExit("reviewed source lines changed")

lineoff = {}
offset = 0
for n in range(segs[P401]["line_start"], segs[P401]["line_end"]+1):
    lineoff[n] = offset; offset += len(lines[n-1])+1
candidate_specs = [
    ("cand-10965", "Small bronze portrait bust of Paolo Giordano II Orsini associated with Cyril Humphris (first version)", "work", 85, "The passage reports later possession by Humphris and a proposed Bernini attribution that Haskell says should be rejected; keep distinct from the other version."),
    ("cand-10966", "Another version of the Paolo Giordano II Orsini portrait bust in City Museum and Art Gallery, Plymouth", "work", 87, "Called another version and discussed by Radcliffe; do not merge it with the Humphris bust without object evidence."),
    ("cand-10967", "Cyril Humphris", "person", 86, "Named as the London possessor of the first bust; identity alignment is deferred to S3."),
    ("cand-10968", "Anthony Radcliffe", "person", 88, "Named as the scholar who discussed the Plymouth version in 1978 and 1979; identity alignment is deferred to S3."),
    ("cand-10969", "City Museum and Art Gallery, Plymouth", "institution", 87, "Named as the location of another bust version; institutional identity is deferred to S3."),
    ("cand-10970", "Drawings of plant and bird life in Mexico described in Cassiano's Escorial journal account", "work", 82, "A described group of drawings; no individual titles or authorship are supplied."),
    ("cand-10971", "Unnamed friend to whom Cassiano considered giving the Seven Sacraments in 1664", "person", 84, "The friend is unnamed; no identity is inferred."),
    ("cand-10972", "Unspecified family of Pope Innocent X mentioned in the Doria-Pamphili art-patronage context", "family", 95, "No family members or branch are specified in this passage."),
    ("cand-10973", "Doria-Pamphili archive documents relevant to Innocent X's art patronage (published 1972)", "archive", 95, "Haskell reports publication of these documents; they are not independently consulted here."),
    ("cand-10974", "Published extracts from Pope Alexander VII's diary concerning his interest in the arts", "archive", 96, "Edition details await the queued notes/bibliography pass."),
    ("cand-10975", "Economic history of seventeenth-century Rome (research subject identified as lacking by Haskell)", "term", 94, "A research subject whose absence Haskell says prevents adequate investigation; not a claim that no partial scholarship exists."),
    ("cand-10976", "Unspecified study of Clement IX's patronage of Bernini through Ponte S. Angelo decoration", "archive", 96, "Footnote 8 is linked but its citation has not yet been semantically processed."),
]
keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
for cid, name, kind, ln, detail in candidate_specs:
    if cid in cand: raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.casefold())
    if key in keys: raise SystemExit(f"candidate natural key already exists: {name}")
    r = {"candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
         "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
         "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
         "candidate_source_ref": f"{P401}#L{ln}"}
    candidates.append(r); cand[cid] = r; keys.add(key)

mention_specs = [
    ("cand-7140", "Escorial", 82, 82, "Reuse the El Escorial candidate; this is the journal destination.", 0),
    ("cand-2630", "Titians", 82, 82, "Reuse the index candidate with p.401 in its page range.", 0),
    ("cand-10970", "drawings of plant and bird life in Mexico", 82, 82, "Descriptive group; no authorship or individual titles supplied.", 0),
    ("cand-5281", "Mexico", 82, 82, "Reuse the existing Mexico place candidate.", 0),
    ("cand-2036", "Cassiano", 83, 83, "Reuse the Cassiano dal Pozzo candidate used on p.400.", 0),
    ("cand-1984", "Poussin", 83, 83, "Reuse the Poussin index candidate with p.401 in its page range.", 0),
    ("cand-5789", "Seven Sacraments", 84, 84, "The report concerns a possible gift, not a completed transfer.", 0),
    ("cand-10971", "un-named friend", 84, 84, "The friend is not identified.", 0),
    ("cand-10965", "small bronze bust", 85, 85, "First of two versions discussed in the paragraph.", 0),
    ("cand-0434", "Paolo\\nGiordano II Orsini", 85, 86, "Reuse the Orsini, Paolo Giordano candidate; the source supplies II and Duke of Bracciano.", 0),
    ("cand-10967", "Cyril Humphris", 86, 86, "Named as possessor after the first edition; London is the stated location.", 0),
    ("cand-2818", "Wittkower", 87, 87, "Reuse the Rudolf Wittkower candidate; this is his proposal.", 0),
    ("cand-0295", "Bernini", 87, 87, "Reuse the index candidate with p.401 in its page range.", 0),
    ("cand-10966", "another version", 87, 87, "Keep separate from the Humphris bust.", 0),
    ("cand-10969", "City\\nMuseum and Art Gallery, Plymouth", 87, 88, "Institution identified as the location of the second version.", 0),
    ("cand-10968", "Anthony Radcliffe", 88, 88, "Named as the scholar discussing the other version.", 0),
    ("cand-0295", "Bernini", 88, 88, "Mention in Haskell's reported rejection of the attribution.", 0),
    ("cand-10957", "double caricature", 90, 90, "Reuse the Plate 65a work candidate; p.401 adds friendship and authorship wording.", 0),
    ("cand-2434", "Niccolo Simonelli", 90, 90, "Reuse the indexed Simonelli candidate; OCR omits the printed accent.", 0),
    ("cand-1676", "Pierfrancesco Mola", 91, 91, "Reuse the indexed Pier Francesco Mola candidate.", 0),
    ("cand-10975", "economic history of\\nRome in the seventeenth century", 93, 94, "Haskell presents this as a gap limiting adequate investigation.", 0),
    ("cand-4490", "Rome", 94, 94, "Reuse the existing Rome place candidate.", 0),
    ("cand-9949", "Petrocchi", 94, 94, "Reuse the surname-only author candidate; identity remains unresolved.", 0),
    ("cand-10973", "Doria-Pamphili archives", 95, 95, "Documents are reported as published in 1972.", 0),
    ("cand-1819", "Innocent X", 95, 95, "Reuse the index candidate with p.401 in its page range.", 0),
    ("cand-10972", "his family", 95, 95, "Source-derived group; no members inferred.", 0),
    ("cand-0665", "Alexander\\nVII", 95, 96, "Reuse the Alexander VII index candidate; line break follows source layout.", 0),
    ("cand-10974", "his diary", 96, 96, "Published extracts are attributed to Alexander VII's diary.", 0),
    ("cand-0295", "Bernini", 96, 96, "The first mention reports frequent visits.", 0),
    ("cand-0295", "Bernini", 96, 96, "The second mention occurs in the editors' qualified comparison.", 1),
    ("cand-0342", "Cortona", 96, 96, "Reuse Pietro da Cortona candidate with p.401 in its index range.", 0),
    ("cand-2263", "Clement IX", 96, 96, "Reuse the Pope Clement IX candidate.", 0),
    ("cand-6465", "Ponte S. Angelo", 96, 96, "Reuse the bridge candidate from chapter 6.", 0),
    ("cand-10976", "study of the decoration of the Ponte S. Angelo", 96, 96, "An unspecified study; footnote 8 remains pending.", 0),
]
existing_mids = {r["mention_id"] for r in mentions}
new_mentions = []
for i, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, 1):
    mid = f"m-chp20-p401-{i:03d}"
    if mid in existing_mids: raise SystemExit(f"mention ID already exists: {mid}")
    if cid not in cand or cand[cid]["status"] != "open": raise SystemExit(f"unavailable candidate {cid}")
    surface = surface.replace("\\n", "\n")
    lo, hi = lineoff[first], lineoff[last] + len(lines[last-1])
    cursor = lo
    for _ in range(occurrence + 1):
        pos = body.find(surface, cursor, hi)
        if pos < 0: raise SystemExit(f"source surface absent at {first}-{last}: {surface!r}")
        cursor = pos + 1
    new_mentions.append({"mention_id": mid, "segment_id": P401, "candidate_id": cid,
        "surface_form": surface, "start_char": str(pos), "end_char": str(pos+len(surface)), "note": note})
    existing_mids.add(mid)

spans = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"]) for r in [*mentions, *new_mentions] if r["segment_id"] == P401)
for i, a in enumerate(spans):
    for b in spans[i+1:]:
        if b[0] >= a[1]: break
        nested = (a[0] <= b[0] and b[1] <= a[1]) or (b[0] <= a[0] and a[1] <= b[1])
        if a[:2] == b[:2] or not nested: raise SystemExit(f"overlapping spans {a[2]} / {b[2]}")
NOTE_LINES = {1: 231, 2: 231, 3: 232, 4: 232, 5: 233, 6: 233, 7: 234, 8: 234}
def make_statement(sid, first, last, subject, obj, predicate, claim, speaker, layer, qualification, ids, relation=False, notes=None, extra=None):
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 401, "pdf_physical_page": 10,
         "claim": claim, "speaker": speaker, "text_layer": layer, "qualification": qualification,
         "mentioned_candidate_ids": ids, "relation_candidate": relation}
    if notes:
        q.update({"footnote_markers": notes, "footnote_text_pending": True, "footnote_segment": NOTES,
                  "footnote_refs": [{"marker": n, "segment_id": NOTES, "source_line": NOTE_LINES[n]} for n in notes],
                  "footnote_statement_ids": [], "footnote_body_link_status": "pending"})
    if extra: q.update(extra)
    return {"statement_id": sid, "segment_id": P401, "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": q, "original_quote": "\n".join(lines[first-1:last]),
            "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "origin": "book"}

new_statements = [
 make_statement("st-chp20-p401-cassiano-escorial-account",82,82,"cand-2036","cand-10970",
  "cassiano_journal_account_describes_titian_pictures_and_mexican_plant_bird_drawings_at_escorial",
  "Haskell says the published account of Cassiano's visit to El Escorial shows his appreciation of Titian paintings and other pictures there, and his particular fascination with drawings of plant and bird life in Mexico.",
  "Haskell reporting on Cassiano's account","authorial report of a published journal account",
  "The journal account is reported through Haskell; its cited publication in footnote 1 remains pending. No authorship is assigned to the drawings.",
  ["cand-2036","cand-7140","cand-2630","cand-10970","cand-5281"],notes=[1],
  extra={"cited_material_not_independently_consulted":True}),
 make_statement("st-chp20-p401-cassiano-seven-sacraments-possible-gift",83,84,"cand-2036","cand-5789",
  "1664_report_says_cassiano_considered_giving_away_seven_sacraments",
  "Haskell says a report made in 1664 offers some support for his suggestion that Cassiano may not altogether have liked Poussin's austere style: Cassiano had at one time thought of giving away the Seven Sacraments to an unnamed friend.",
  "Haskell reporting a 1664 report","authorial interpretation supported by a reported event",
  "Both Cassiano's dislike and the contemplated gift remain qualified; the passage does not say the transfer occurred. Footnote 2 is pending, and the friend is unnamed.",
  ["cand-2036","cand-1984","cand-5789","cand-10971"],True,[2],
  {"cited_material_not_independently_consulted":True}),
 make_statement("st-chp20-p401-humphris-bust-possession",85,86,"cand-10965","cand-10967",
  "bronze_bust_came_into_cyril_humphris_possession_after_first_edition",
  "After the first edition, a small bronze bust of Paolo Giordano II Orsini, Duke of Bracciano came into Cyril Humphris's possession in London.",
  "Haskell","authorial report of object provenance",
  "No date is supplied for the transfer. Keep this object separate from the other version mentioned next.",
  ["cand-10965","cand-0434","cand-10967"],True),
 make_statement("st-chp20-p401-wittkower-bust-attribution-proposal",86,87,"cand-2818","cand-10965",
  "wittkower_proposed_humphris_bust_was_bernini_portrait_of_paolo_giordano_ii",
  "Haskell reports that in 1966 Rudolf Wittkower proposed that the Humphris bust was the portrait of Paolo Giordano II by Bernini for which Haskell had published documents.",
  "Haskell reporting Wittkower","authorial report of a scholarly attribution proposal",
  "This is Wittkower's proposal, not an accepted attribution. The documents are not inspected here; footnote 3 remains pending.",
  ["cand-2818","cand-10965","cand-0434","cand-0295"],True,[3],
  {"cited_material_not_independently_consulted":True,
   "ocr_corrections":[{"source_line":88,"ocr":"to.be rejected","print":"to be rejected","basis":"CHP-20Postscript.pdf physical page 10 image"}]}),
 make_statement("st-chp20-p401-plymouth-bust-version-discussed",87,88,"cand-10966","cand-10969",
  "another_bust_version_at_plymouth_discussed_by_anthony_radcliffe_1978_1979",
  "Haskell says another version of the bust was in the City Museum and Art Gallery, Plymouth, and was discussed by Anthony Radcliffe in 1978 and 1979.",
  "Haskell","authorial report of an object location and scholarship",
  "The source calls it another version; its identity and relation to the Humphris bust remain unresolved. Footnote 4 is pending.",
  ["cand-10966","cand-10969","cand-10968"],True,[4],
  {"cited_material_not_independently_consulted":True}),
 make_statement("st-chp20-p401-haskell-rejects-bernini-bust-attribution",88,88,"cand-0295","cand-10965",
  "haskell_reports_documentary_reasons_to_reject_bernini_attribution_of_bust",
  "Haskell says he understands there are convincing documentary reasons for rejecting the attribution of the attractive bust to Bernini.",
  "Haskell","authorial report of a documentary attribution judgment",
  "This reports Haskell's stated understanding; the documents and attribution dispute are not independently adjudicated here.",
  ["cand-0295","cand-10965"],True),
 make_statement("st-chp20-p401-simonelli-mola-double-caricature",90,91,"cand-10957","cand-2434",
  "double_caricature_made_by_niccolo_simonelli_and_his_friend_pierfrancesco_mola_came_to_light",
  "Haskell reports that an engaging double caricature made by Niccolò Simonelli and his friend Pier Francesco Mola had come to light; it is Plate 65a.",
  "Haskell","authorial report of a newly surfaced artwork",
  "The source identifies Mola as Simonelli's friend and both as makers. It supplies no date, present location, or further object details.",
  ["cand-10957","cand-2434","cand-1676"],True,
  extra={"cross_reference_segments":[{"segment_id":PLATE65,"source_line_start":64,"source_line_end":67}],
         "ocr_corrections":[{"source_line":90,"ocr":"Niccolo","print":"Niccolò","basis":"CHP-20Postscript.pdf physical page 10 image"}]}),
 make_statement("st-chp20-p401-economic-history-limitation",93,94,"cand-10975","cand-4490",
  "absence_of_economic_history_prevents_adequate_investigation_of_seventeenth_century_rome",
  "Haskell says the continued absence of an economic history of seventeenth-century Rome makes it impossible as yet to investigate the period adequately.",
  "Haskell","authorial assessment of a research limitation",
  "This is Haskell's assessment of scholarship in the new edition, not a claim that no relevant partial studies exist.",
  ["cand-10975","cand-4490"],False),
 make_statement("st-chp20-p401-petrocchi-economic-history-reference",94,94,"cand-9949","cand-10975",
  "petrocchi_work_contains_useful_information_but_acknowledges_limited_study_of_rome_economic_life",
  "Haskell says Petrocchi contains useful information and a bibliography, while Petrocchi acknowledges how little Rome's economic life has been studied.",
  "Haskell reporting Petrocchi","authorial report of cited scholarship",
  "The full citation is not reconciled and the work has not been independently consulted; footnote 5 remains pending.",
  ["cand-9949","cand-10975","cand-4490"],True,[5],
  {"cited_material_not_independently_consulted":True}),
 make_statement("st-chp20-p401-doria-pamphili-documents-innocent-x",95,95,"cand-10973","cand-1819",
  "doria_pamphili_documents_published_1972_for_serious_account_of_innocent_x_art_patronage",
  "Haskell says Doria-Pamphili archive documents needed for a serious account of Innocent X's and his family's art patronage were published in 1972.",
  "Haskell","authorial report of documentary publication",
  "The archives and publication are not independently consulted, and family members are not specified. Footnote 6 remains pending.",
  ["cand-10973","cand-1819","cand-10972"],True,[6],
  {"cited_material_not_independently_consulted":True,
   "ocr_corrections":[{"source_line":233,"ocr":"Garrns","print":"Garms","basis":"CHP-20Postscript.pdf physical page 10 image"}]}),
 make_statement("st-chp20-p401-alexander-diary-berninivisits",95,96,"cand-0665","cand-10974",
  "published_diary_extracts_offer_fresh_view_of_alexander_vii_arts_interest_and_berninivisits",
  "Haskell says published extracts from Alexander VII's diary give an unusually fresh view of his interest in the arts; the comments are terse and indicate that Bernini was a very frequent visitor.",
  "Haskell reporting on Alexander VII's diary","authorial report of published archival extracts",
  "Footnote 7 cites the diary edition; it remains pending and the extracts have not been independently consulted.",
  ["cand-0665","cand-10974","cand-0295"],True,[7],
  {"cited_material_not_independently_consulted":True,
   "cross_reference_segments":[{"segment_id":PLATE65,"source_line_start":68,"source_line_end":71}]}),
 make_statement("st-chp20-p401-alexander-diary-planning-agency",96,96,"cand-0665","cand-10974",
  "editors_emphasize_alexander_vii_apparently_claimed_final_building_planning_authority",
  "Haskell says the editors emphasize that Alexander VII apparently felt he, rather than Bernini or Cortona, ultimately decided the planning of a building.",
  "Haskell reporting the editors","reported editorial interpretation of diary extracts",
  "Preserve 'apparently felt'; the building is unnamed and the passage reports the editors' interpretation, not an independently verified decision.",
  ["cand-0665","cand-10974","cand-0295","cand-0342"],True,[7],
  {"cited_material_not_independently_consulted":True}),
 make_statement("st-chp20-p401-clement-ix-berniniponte-study",96,96,"cand-2263","cand-10976",
  "study_analyses_clement_ix_patronage_of_bernini_through_ponte_s_angelo_decoration",
  "Haskell says a careful study of the decoration of Ponte S. Angelo analysed the nature of Clement IX's patronage of Bernini.",
  "Haskell","authorial report of scholarship",
  "Footnote 8 remains pending; neither the study nor the decoration is independently examined here.",
  ["cand-2263","cand-0295","cand-6465","cand-10976"],True,[8],
  {"cited_material_not_independently_consulted":True}),
]

q = stby[OPEN400]["qualifiers"]
q["claim"] = "Haskell says only the section of Cassiano's journal describing his visit to El Escorial is published in full."
q["qualification"] = "The destination is supplied by p.401 L82; the journal is reported through Haskell and has not been independently consulted here."
q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), "cand-7140"]))
q.pop("open_across_segment", None); q.pop("continues_in_segment", None)
refs = q.setdefault("cross_reference_segments", [])
if not any(x.get("segment_id")==P401 and x.get("source_line_start")==82 for x in refs):
    refs.append({"segment_id":P401,"source_line_start":82,"source_line_end":82})
stby[OPEN400]["predicate"] = "only_section_of_cassianos_journal_describing_el_escorial_visit_published_in_full"

existing_sids = {r["statement_id"] for r in statements}
for r in new_statements:
    if r["statement_id"] in existing_sids: raise SystemExit(f"statement already exists: {r['statement_id']}")
    existing_sids.add(r["statement_id"])
    if r["original_quote"] not in body: raise SystemExit(f"quote absent from p.401: {r['statement_id']}")
    for cid in r["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in cand or cand[cid]["status"] != "open": raise SystemExit(f"statement candidate unavailable: {cid}")

cov[P400]["disposition"]="reviewed"; cov[P400]["migration_status"]="complete"
cov[P400]["note"]="Printed p.400 (PDF physical page 5) reviewed against the page image; its final journal-publication sentence is closed by p.401 L82. Footnotes 1-8 remain linked to queued notes; p.400 footnotes 9-10 are transcribed in its source segment."
cov[P401]["disposition"]="reviewed"; cov[P401]["migration_status"]="complete"; cov[P401]["source_line_ranges"]="L82-96"
cov[P401]["note"]="Printed p.401 (PDF physical page 10) visually checked. Records the Escorial journal account, qualified Seven Sacraments report, two distinct bust versions and disputed attribution, Plate 65a caricature/friendship, chapter 6 research limitation, Doria-Pamphili documents, Alexander VII diary reports, and Clement IX/Ponte S. Angelo scholarship. Footnotes 1-8 link to queued notes L231-234."

paths=[T/"entity-candidates.csv",T/"mentions.csv",T/"book-statements.jsonl",T/"s2-coverage.csv"]
backups=[p.with_name(p.name+BACKUP) for p in paths]
if args.apply:
    if any(p.exists() for p in backups): raise SystemExit("p.401 recovery backup already exists")
    for p,b in zip(paths,backups): shutil.copy2(p,b)
    write_csv(paths[0],cp,candidates); write_csv(paths[1],mp,[*mentions,*new_mentions])
    write_jsonl(paths[2],[*statements,*new_statements]); write_csv(paths[3],vp,coverage)
    print(f"applied p.401 S2 migration; recovery suffix {BACKUP}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("p.400 sentence closure, p.401 anchors, citation links, and object/attribution distinctions validated")
