#!/usr/bin/env python3
"""Migrate printed p.401 notes 1-8; dry-run unless --apply is supplied."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
T = ROOT / "04-knowledge" / "tables"
SRC = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
BACKUP = ".bak-s2-chp20-notes-p401-20261004"
SRC_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
ap = argparse.ArgumentParser()
ap.add_argument("--apply", action="store_true")
args = ap.parse_args()

def rcsv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)

def rjsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]

def wcsv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader(); w.writerows(rows); tmp = Path(f.name)
    tmp.replace(path)

def wjsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)

if hashlib.sha256(SRC.read_bytes()).hexdigest() != SRC_SHA: raise SystemExit("source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA: raise SystemExit("registered PDF changed")
cp, candidates = rcsv(T / "entity-candidates.csv")
mp, mentions = rcsv(T / "mentions.csv")
vp, coverage = rcsv(T / "s2-coverage.csv")
statements = rjsonl(T / "book-statements.jsonl")
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11143, 25771, 11134, 832):
    raise SystemExit("unexpected S2 table pre-state")
cb = {r["candidate_id"]: r for r in candidates}
sb = {r["statement_id"]: r for r in statements}
cov = {r["segment_id"]: r for r in coverage}
if NOTES not in cov or (cov[NOTES]["disposition"], cov[NOTES]["migration_status"], cov[NOTES]["source_line_ranges"]) != ("reviewed", "partial", "L212-230"):
    raise SystemExit(f"unexpected notes coverage: {cov.get(NOTES)}")
lines = SRC.read_text(encoding="utf-8-sig").splitlines()
note_text = "\n".join(lines[210:280])
offsets, pos = {}, 0
for n in range(211, 281): offsets[n] = pos; pos += len(lines[n-1]) + 1

# Candidate identity remains local to this citation; global identity alignment is S3.
candidate_specs = [
    ("cand-11165", "Harris and de Andrés, publication cited at p.401 note 1 (title and year unresolved)", "archive", 231, "The note cites Harris and de Andrés for Cassiano's Escorial account. Title, year, and Harris's identity are not supplied; reconcile with the bibliography and defer identity to S3."),
    ("cand-11166", "Harris (author cited in p.401 note 1; identity unresolved)", "person", 231, "Surname-only author form; do not merge with another Harris candidate without bibliography evidence."),
    ("cand-11167", "de Andrés (author cited in p.401 note 1; identity unresolved)", "person", 231, "Surname-only author form; given name and identity are not supplied."),
    ("cand-11168", "Pierre du Colombier, publication cited in p.401 note 2 (title and year unspecified)", "archive", 231, "Short citation only; title and date are absent and the work was not independently consulted."),
    ("cand-11169", "Pierre du Colombier", "person", 231, "Named as author in p.401 note 2; global identity alignment is deferred to S3."),
    ("cand-11170", "Wittkower, 1966 publication cited at p.401 note 3 (title and edition unspecified)", "archive", 232, "The note gives pp. 203-4 but no title or edition; reconcile with the bibliography."),
    ("cand-11171", "Radcliffe, 1978 publication cited at p.401 note 4 (title unspecified)", "archive", 232, "Short citation; title is not supplied and the work was not independently consulted."),
    ("cand-11172", "Sotheby's 1979 publication cited at p.401 note 4, pp. 31-2 (title unspecified)", "archive", 232, "Publication citation is distinct from the Sotheby's institution; title and edition await bibliography review."),
    ("cand-11173", "Petrocchi, 1970 publication cited at p.401 note 5, p.158 (title unspecified)", "archive", 233, "Reuses existing surname-only author cand-9949; title and edition await bibliography review."),
    ("cand-11174", "Garms publication cited in p.401 note 6 for Doria-Pamphili documents (title and year unspecified)", "archive", 233, "Citation title and year are absent; keep distinct from the archival-document group candidate."),
    ("cand-11175", "Garms (author cited in p.401 note 6; identity unresolved)", "person", 233, "The page image confirms the surname spelling; full identity is unresolved."),
    ("cand-11176", "Krautheimer (author or editor cited in p.401 note 7; identity unresolved)", "person", 234, "The note supplies only the surname; bibliographic role and full identity await review."),
    ("cand-11177", "Jones (author or editor cited with Krautheimer in p.401 note 7; identity unresolved)", "person", 234, "The note supplies only the surname; bibliographic role and full identity await review."),
    ("cand-11178", "Weil (author cited in p.401 note 8; identity unresolved)", "person", 234, "The note supplies only the surname; full identity awaits bibliography review and S3."),
]
natural = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
newc = []
for cid, name, kind, ln, detail in candidate_specs:
    if cid in cb or (name.strip().casefold(), kind.casefold()) in natural: raise SystemExit(f"candidate collision: {cid} {name}")
    row = {f: "" for f in cp}; row.update(candidate_id=cid, canonical_name=name, suggested_type=kind,
        status="open", detail=detail, candidate_origin="body-mention", candidate_source_ref=f"{NOTES}#L{ln}")
    newc.append(row); cb[cid] = row; natural.add((name.strip().casefold(), kind.casefold()))

body_links = {
    1: ["st-chp20-p401-cassiano-escorial-account"],
    2: ["st-chp20-p401-cassiano-seven-sacraments-possible-gift"],
    3: ["st-chp20-p401-wittkower-bust-attribution-proposal"],
    4: ["st-chp20-p401-plymouth-bust-version-discussed"],
    5: ["st-chp20-p401-petrocchi-economic-history-reference"],
    6: ["st-chp20-p401-doria-pamphili-documents-innocent-x"],
    7: ["st-chp20-p401-alexander-diary-berninivisits", "st-chp20-p401-alexander-diary-planning-agency"],
    8: ["st-chp20-p401-clement-ix-berniniponte-study"],
}
# id, marker, source line, exact quote/subquote, cited-work candidate, author/institution candidates, claim, OCR fixes
note_specs = [
    ("st-chp20-p401-n01-citation", 1, 231, "1 Harris and de Andres.", "cand-11165", ["cand-11166", "cand-11167"], "The note cites an unresolved Harris and de Andrés publication for Cassiano's Escorial account.", [("de Andres", "de Andrés")]),
    ("st-chp20-p401-n02-citation", 2, 231, "2 Pierre du Colombier.", "cand-11168", ["cand-11169"], "The note cites a publication by Pierre du Colombier; title and date are absent.", []),
    ("st-chp20-p401-n03-citation", 3, 232, "3 Wittkower, 1966, pp. 203-4.", "cand-11170", ["cand-2818"], "The note cites Wittkower, 1966, pp. 203-4; title and edition are absent.", []),
    ("st-chp20-p401-n04a-citation", 4, 232, "Radcliffe, 1978", "cand-11171", ["cand-10968"], "The first note 4 reference is a 1978 work by Radcliffe; title is absent.", []),
    ("st-chp20-p401-n04b-citation", 4, 232, "Sotheby’s, 1979, pp. 31-2", "cand-11172", ["cand-9307"], "The second note 4 reference is a Sotheby's 1979 publication, pp. 31-2; title is absent.", []),
    ("st-chp20-p401-n05-citation", 5, 233, "5 Petrocchi, 1970, p. 158.", "cand-11173", ["cand-9949"], "The note cites Petrocchi, 1970, p.158; title and edition are absent.", []),
    ("st-chp20-p401-n06-citation", 6, 233, "6 Garrns.", "cand-11174", ["cand-11175"], "The note cites an unspecified Garms publication concerning the Doria-Pamphili documents.", [("Garrns", "Garms")]),
    ("st-chp20-p401-n07-citation", 7, 234, "7 Krautheimer and Jones.", "cand-10974", ["cand-11176", "cand-11177"], "The note attributes the existing Alexander VII diary-extract publication to Krautheimer and Jones.", []),
    ("st-chp20-p401-n08-citation", 8, 234, "8 Weil.", "cand-10976", ["cand-11178"], "The note attributes the study described in the body to Weil; full identity is unresolved.", []),
]
existing_mkeys = {(r["segment_id"], r["candidate_id"], str(r["start_char"]), str(r["end_char"])) for r in mentions}
newm, news = [], []

def addm(ln, surface, cid, marker, role, within=None):
    line = lines[ln-1]; container = line; base = 0
    if within is not None:
        base = line.find(within)
        if base < 0 or line.find(within, base+1) >= 0: raise SystemExit(f"ambiguous span container at L{ln}: {within}")
        container = within
    start0 = container.find(surface)
    if start0 < 0 or container.find(surface, start0+1) >= 0: raise SystemExit(f"ambiguous/missing mention at L{ln}: {surface}")
    start = offsets[ln] + base + start0; end = start + len(surface)
    if note_text[start:end] != surface: raise SystemExit(f"mention offset mismatch at L{ln}: {surface}")
    key = (NOTES, cid, str(start), str(end))
    if key in existing_mkeys or any((r["segment_id"],r["candidate_id"],str(r["start_char"]),str(r["end_char"])) == key for r in newm):
        raise SystemExit(f"duplicate mention at L{ln}: {surface}")
    row = {f: "" for f in mp}; row.update(mention_id=f"m-s2-chp20-notes-p401-{len(newm)+1:03d}",
        segment_id=NOTES, candidate_id=cid, surface_form=surface, start_char=start, end_char=end,
        note=f"Printed p.401 footnote {marker} {role}; citation is not independent consultation of the cited work.")
    newm.append(row)

# Nested author spans are kept; exact-span author duplicates are omitted.
mention_specs = [
    (231,"Harris and de Andres","cand-11165",1,"citation locator",None),
    (231,"Harris","cand-11166",1,"surname-only author mention","Harris and de Andres"),
    (231,"de Andres","cand-11167",1,"surname-only author mention","Harris and de Andres"),
    (231,"Pierre du Colombier","cand-11168",2,"citation locator; exact author span",None),
    (232,"Wittkower, 1966, pp. 203-4","cand-11170",3,"citation locator",None),
    (232,"Wittkower","cand-2818",3,"author mention","Wittkower, 1966, pp. 203-4"),
    (232,"Radcliffe, 1978","cand-11171",4,"first citation locator",None),
    (232,"Radcliffe","cand-10968",4,"author mention","Radcliffe, 1978"),
    (232,"Sotheby’s, 1979, pp. 31-2","cand-11172",4,"second citation locator",None),
    (232,"Sotheby’s","cand-9307",4,"institution in citation","Sotheby’s, 1979, pp. 31-2"),
    (233,"Petrocchi, 1970, p. 158","cand-11173",5,"citation locator",None),
    (233,"Petrocchi","cand-9949",5,"surname-only author mention","Petrocchi, 1970, p. 158"),
    (233,"Garrns","cand-11175",6,"surname-only author mention; print spelling Garms",None),
    (234,"Krautheimer and Jones","cand-10974",7,"citation locator for diary extracts",None),
    (234,"Krautheimer","cand-11176",7,"surname-only author/editor mention","Krautheimer and Jones"),
    (234,"Jones","cand-11177",7,"surname-only author/editor mention","Krautheimer and Jones"),
    (234,"Weil","cand-10976",8,"citation locator; author candidate retained in statement",None),
]
for spec in mention_specs: addm(*spec)

for sid, marker, ln, quote, archive, authors, claim, fixes in note_specs:
    if sid in sb: raise SystemExit(f"statement already exists: {sid}")
    if quote not in lines[ln-1]: raise SystemExit(f"quote mismatch at L{ln}: {quote}")
    if archive not in cb or cb[archive]["suggested_type"] != "archive": raise SystemExit(f"archive candidate missing: {archive}")
    for bid in body_links[marker]:
        if bid not in sb: raise SystemExit(f"body statement missing: {bid}")
        q = sb[bid].get("qualifiers", {})
        refs = [x for x in q.get("footnote_refs",[]) if x.get("marker")==marker and x.get("segment_id")==NOTES]
        if len(refs)!=1 or refs[0].get("source_line")!=ln or q.get("footnote_text_pending") is not True:
            raise SystemExit(f"p.401 body link changed for marker {marker}: {bid}")
    statement = {"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":None,"object_candidate_id":archive,
        "predicate":"footnote_cites_publication","qualifiers":{"source_line_start":ln,"source_line_end":ln,
        "printed_page":401,"pdf_physical_page":10,"footnote_marker":marker,"claim":claim,
        "speaker":"Haskell’s footnote apparatus","text_layer":"bibliographic citation",
        "qualification":"Short citation only; absent title, edition, and other bibliographic details are not inferred. Cited material was not independently consulted.",
        "mentioned_candidate_ids":list(dict.fromkeys([archive,*authors])),"relation_candidate":False,
        "cited_material_not_independently_consulted":True},"original_quote":quote,"origin":"book",
        "source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md"}
    if fixes:
        statement["qualifiers"]["ocr_corrections"]=[{"source_line":ln,"ocr":a,"print":b,"basis":"CHP-20Postscript.pdf physical page 10 image"} for a,b in fixes]
    news.append(statement); sb[sid]=statement

# Move the Garms print correction from the body statement to note 6, its proper anchor.
doria = sb.get("st-chp20-p401-doria-pamphili-documents-innocent-x")
if doria is None: raise SystemExit("p.401 Doria-Pamphili statement missing")
q = doria.setdefault("qualifiers", {})
fixes = q.get("ocr_corrections", [])
garms = [x for x in fixes if x.get("source_line")==233 and x.get("ocr")=="Garrns"]
if len(garms)!=1: raise SystemExit(f"expected one misplaced Garms correction, found {len(garms)}")
left = [x for x in fixes if x not in garms]
if left: q["ocr_corrections"] = left
else: q.pop("ocr_corrections", None)

for marker, body_ids in body_links.items():
    note_ids = [x[0] for x in note_specs if x[1] == marker]
    for bid in body_ids:
        q = sb[bid]["qualifiers"]; q["footnote_text_pending"] = False; q["footnote_body_link_status"] = "linked"
        linked = q.setdefault("footnote_statement_ids", [])
        for sid in note_ids:
            if sid not in linked: linked.append(sid)

cov[NOTES]["source_line_ranges"] = "L212-234"
cov[NOTES]["note"] = cov[NOTES].get("note", "").rstrip() + (
    " Printed p.401 notes 1-8 (PDF physical page 10) transcribed and linked to body statements; "
    "page-image readings de Andrés and Garms are recorded as OCR corrections while S0 is preserved. L235-280 remain queued."
)

# Persist the citation rows alongside the in-place updates to existing body rows.
statements.extend(news)

spans = sorted((int(r["start_char"]),int(r["end_char"]),r["mention_id"]) for r in [*mentions,*newm] if r["segment_id"]==NOTES)
for i,a in enumerate(spans):
    for b in spans[i+1:]:
        if b[0]>=a[1]: break
        nested=(a[0]<=b[0] and b[1]<=a[1]) or (b[0]<=a[0] and a[1]<=b[1])
        if a[:2]==b[:2] or not nested: raise SystemExit(f"overlapping note spans: {a[2]} / {b[2]}")

paths=[T/"entity-candidates.csv",T/"mentions.csv",T/"book-statements.jsonl",T/"s2-coverage.csv"]
backs=[p.with_name(p.name+BACKUP) for p in paths]
if args.apply:
    present = [b.exists() for b in backs]
    if any(present) and not all(present): raise SystemExit("incomplete recovery backup set exists")
    if all(present):
        if any(hashlib.sha256(p.read_bytes()).digest() != hashlib.sha256(b.read_bytes()).digest() for p,b in zip(paths,backs)):
            raise SystemExit("existing recovery backups do not match the current pre-apply tables")
    else:
        for p,b in zip(paths,backs): shutil.copy2(p,b)
    wcsv(paths[0],cp,[*candidates,*newc]); wcsv(paths[1],mp,[*mentions,*newm])
    wjsonl(paths[2],statements); wcsv(paths[3],vp,coverage)
    print(f"applied p.401 notes 1-8: candidates +{len(newc)}, mentions +{len(newm)}, citation statements +{len(news)}")
    print(f"recovery suffix {BACKUP}")
else:
    print(json.dumps({"mode":"dry-run","page":401,"notes":"1-8","candidates_added":len(newc),
        "mentions_added":len(newm),"citation_statements_added":len(news),
        "body_statements_linked":sum(map(len,body_links.values())),"ocr_correction_moved":1,
        "coverage_after":"reviewed/partial through L234; L235-280 remain"},ensure_ascii=False,indent=2))
