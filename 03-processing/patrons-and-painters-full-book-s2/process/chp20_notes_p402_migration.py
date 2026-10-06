#!/usr/bin/env python3
"""Migrate printed p.402 notes 1-7; dry-run unless --apply is supplied."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]; T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"
PDF=ROOT/"02-sources"/"01-book"/"CHP-20Postscript.pdf"
NOTES="chp-20:20_CHP-20Postscript:l211-280"
SRC_SHA="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA="f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP=".bak-s2-chp20-notes-p402-20261004"
ap=argparse.ArgumentParser(); ap.add_argument("--apply",action="store_true"); args=ap.parse_args()

def rcsv(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f); return r.fieldnames,list(r)
def rjsonl(p): return [json.loads(x) for x in p.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
def wcsv(p,fields,rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=p.parent,delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n"); w.writeheader(); w.writerows(rows); tmp=Path(f.name)
    tmp.replace(p)
def wjsonl(p,rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=p.parent,delete=False) as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
        tmp=Path(f.name)
    tmp.replace(p)

if hashlib.sha256(SRC.read_bytes()).hexdigest()!=SRC_SHA: raise SystemExit("source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest()!=PDF_SHA: raise SystemExit("registered PDF changed")
cp,candidates=rcsv(T/"entity-candidates.csv"); mp,mentions=rcsv(T/"mentions.csv")
vp,coverage=rcsv(T/"s2-coverage.csv"); statements=rjsonl(T/"book-statements.jsonl")
if (len(candidates),len(mentions),len(statements),len(coverage))!=(11157,25788,11143,832): raise SystemExit("unexpected S2 pre-state")
cb={r["candidate_id"]:r for r in candidates}; sb={r["statement_id"]:r for r in statements}; cv={r["segment_id"]:r for r in coverage}
if NOTES not in cv or (cv[NOTES]["disposition"],cv[NOTES]["migration_status"],cv[NOTES]["source_line_ranges"])!=("reviewed","partial","L212-234"):
    raise SystemExit(f"unexpected notes coverage state: {cv.get(NOTES)}")
lines=SRC.read_text(encoding="utf-8-sig").splitlines(); note_text="\n".join(lines[210:280])
offsets={}; pos=0
for n in range(211,281): offsets[n]=pos; pos+=len(lines[n-1])+1

candidate_specs=[
 ("cand-11179","Von Platen (author cited in p.402 note 2; identity unresolved)","person",235,"The footnote attributes the related exhibition publication to Von Platen; no given name or full bibliographic role is supplied. Identity alignment is deferred to S3."),
 ("cand-11180","Wethey publication cited at p.402 note 6 (title and year unspecified)","archive",237,"The short note cites Wethey without title, year, or locator. The cited publication was not independently consulted; reconcile with the bibliography."),
]
natural={(r["canonical_name"].strip().casefold(),r["suggested_type"].strip().casefold()) for r in candidates}; newc=[]
for cid,name,kind,ln,detail in candidate_specs:
    if cid in cb or (name.strip().casefold(),kind.casefold()) in natural: raise SystemExit(f"candidate collision: {cid} {name}")
    row={f:"" for f in cp}; row.update(candidate_id=cid,canonical_name=name,suggested_type=kind,status="open",detail=detail,
      candidate_origin="body-mention",candidate_source_ref=f"{NOTES}#L{ln}")
    newc.append(row); cb[cid]=row; natural.add((name.strip().casefold(),kind.casefold()))

body_links={
 1:["st-chp20-p402-christina-exhibition-materials"],
 2:["st-chp20-p402-christina-exhibition-materials"],
 3:["st-chp20-p402-previtali-bellori-edition"],
 4:["st-chp20-p402-turner-ferrante-carlo-bellori-lanfranco"],
 5:["st-chp20-p402-perez-sanchez-spanish-patronage-catalogue"],
 6:["st-chp20-p402-wethey-naples-viceroy-information"],
 7:["st-chp20-p402-mazarin-art-policy-in-france","st-chp20-p402-laurain-portemer-broadens-mazarin-interpretation"],
}
# id, marker, line, exact source quote, archive object, named author candidates, claim, OCR correction.
notespecs=[
 ("st-chp20-p402-n01-citation",1,235,"1 Christina of Sweden.","cand-10979",[],"The note cites the catalogue of the 1966 Christina of Sweden exhibition.",None),
 ("st-chp20-p402-n02-citation",2,235,"2 Von Platen.","cand-10980",["cand-11179"],"The note attributes the related exhibition volume or studies/documents to Von Platen; the exact work remains unresolved.",None),
 ("st-chp20-p402-n03-citation",3,236,"3 Bellori, 1976.","cand-10981",["cand-0272"],"The note cites the critical edition of Bellori's Lives as Bellori, 1976; title details await bibliography reconciliation.",None),
 ("st-chp20-p402-n04-citation",4,236,"4 Turner.","cand-10985",["cand-10984"],"The note cites Turner's publication reporting the derivation of Bellori's comments from Ferrante Carlo.",None),
 ("st-chp20-p402-n05-citation",5,237,"6 Perez Sanchez.","cand-10989",["cand-10988"],"The note cites the Perez Sanchez catalogue; the OCR note number is corrected from 6 to printed 5.",("6","5")),
 ("st-chp20-p402-n06-citation",6,237,"6 Wethey.","cand-11180",["cand-10990"],"The note cites an unspecified Wethey publication for information about Naples viceroys.",None),
 ("st-chp20-p402-n07-citation",7,238,"7 Laurain-Portemer (with a list of her other important articles on the subject).","cand-10993",["cand-10992"],"The note cites Laurain-Portemer's article group and states that it includes a list of her other important articles on the subject.",None),
]
newm=[]; news=[]
existing_mkeys={(r["segment_id"],r["candidate_id"],str(r["start_char"]),str(r["end_char"])) for r in mentions}
def addm(ln,surface,cid,marker,role,within=None):
    line=lines[ln-1]; container=line; base=0
    if within is not None:
        base=line.find(within)
        if base<0 or line.find(within,base+1)>=0: raise SystemExit(f"ambiguous mention container at L{ln}: {within}")
        container=within
    ix=container.find(surface)
    if ix<0 or container.find(surface,ix+1)>=0: raise SystemExit(f"missing/ambiguous mention at L{ln}: {surface}")
    start=offsets[ln]+base+ix; end=start+len(surface)
    if note_text[start:end]!=surface: raise SystemExit(f"mention offset mismatch at L{ln}: {surface}")
    key=(NOTES,cid,str(start),str(end))
    if key in existing_mkeys or any((r["segment_id"],r["candidate_id"],str(r["start_char"]),str(r["end_char"]))==key for r in newm):
        raise SystemExit(f"duplicate mention at L{ln}: {surface}")
    row={f:"" for f in mp}; row.update(mention_id=f"m-s2-chp20-notes-p402-{len(newm)+1:03d}",segment_id=NOTES,
      candidate_id=cid,surface_form=surface,start_char=start,end_char=end,
      note=f"Printed p.402 footnote {marker} {role}; cited material was not independently consulted.")
    newm.append(row)

# Nested author mentions are retained; where the citation and author are the same span, keep one mention.
for spec in [
 (235,"Christina of Sweden","cand-10979",1,"catalogue title",None),
 (235,"Von Platen","cand-11179",2,"author mention",None),
 (236,"Bellori, 1976","cand-10981",3,"edition citation",None),
 (236,"Bellori","cand-0272",3,"author mention","Bellori, 1976"),
 (236,"Turner","cand-10984",4,"surname-only author mention",None),
 (237,"Perez Sanchez","cand-10989",5,"catalogue citation; author retained in statement",None),
 (237,"Wethey","cand-10990",6,"surname-only author mention",None),
 (238,"Laurain-Portemer (with a list of her other important articles on the subject)","cand-10993",7,"article group citation and note description",None),
 (238,"Laurain-Portemer","cand-10992",7,"author mention","Laurain-Portemer (with a list of her other important articles on the subject)"),
]: addm(*spec)

for sid,marker,ln,quote,archive,authors,claim,correction in notespecs:
    if sid in sb: raise SystemExit(f"statement exists: {sid}")
    if quote not in lines[ln-1]: raise SystemExit(f"quote mismatch at L{ln}: {quote}")
    if archive not in cb or cb[archive]["suggested_type"]!="archive": raise SystemExit(f"archive candidate missing: {archive}")
    for bid in body_links[marker]:
        if bid not in sb: raise SystemExit(f"body statement missing: {bid}")
        q=sb[bid].get("qualifiers",{}); refs=[r for r in q.get("footnote_refs",[]) if r.get("marker")==marker and r.get("segment_id")==NOTES]
        if len(refs)!=1 or refs[0].get("source_line")!=ln or q.get("footnote_text_pending") is not True:
            raise SystemExit(f"body note {marker} link changed: {bid}")
    q={"source_line_start":ln,"source_line_end":ln,"printed_page":402,"pdf_physical_page":11,"footnote_marker":marker,
      "claim":claim,"speaker":"Haskell’s footnote apparatus","text_layer":"bibliographic citation",
      "qualification":"Short citation only; missing titles, editions, and other bibliographic details are not inferred. Cited material was not independently consulted.",
      "mentioned_candidate_ids":list(dict.fromkeys([archive,*authors])),"relation_candidate":False,
      "cited_material_not_independently_consulted":True}
    if correction: q["ocr_corrections"]=[{"source_line":ln,"ocr":correction[0]+" Perez Sanchez","print":correction[1]+" Perez Sanchez","basis":"CHP-20Postscript.pdf physical page 11 image"}]
    news.append({"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":None,"object_candidate_id":archive,
      "predicate":"footnote_cites_publication","qualifiers":q,"original_quote":quote,"origin":"book",
      "source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md"}); sb[sid]=news[-1]

# Move the note-number OCR correction from the body statement to note 5.
perez=sb.get("st-chp20-p402-perez-sanchez-spanish-patronage-catalogue")
if perez is None: raise SystemExit("p.402 Perez Sanchez body statement missing")
q=perez.setdefault("qualifiers",{}); fixes=q.get("ocr_corrections",[])
numberfix=[x for x in fixes if x.get("source_line")==237 and x.get("ocr")=="6 Perez Sanchez" and x.get("print")=="5 Perez Sanchez"]
if len(numberfix)!=1: raise SystemExit(f"expected one misplaced note-number correction, found {len(numberfix)}")
left=[x for x in fixes if x not in numberfix]
if left:q["ocr_corrections"]=left
else:q.pop("ocr_corrections",None)

for marker,body_ids in body_links.items():
    citation_ids=[x[0] for x in notespecs if x[1]==marker]
    for bid in body_ids:
        q=sb[bid]["qualifiers"]; q["footnote_text_pending"]=False; q["footnote_body_link_status"]="linked"
        linked=q.setdefault("footnote_statement_ids",[])
        for sid in citation_ids:
            if sid not in linked:linked.append(sid)

# Current coverage note replaces stale p.401-pending wording from the earlier partial state.
cv[NOTES]["source_line_ranges"]="L212-238"
cv[NOTES]["note"]=("P.396 notes 1-6 (L212-214), p.397 notes 1-12 (L215-220), p.398 notes 1-7 (L221-224), "
 "p.399 notes 1-3 (L225), p.400 notes 1-8 (L226-230), and p.401 notes 1-8 (L231-234) are reviewed, "
 "transcribed, and linked to body statements; p.400 notes 9-10 are captured at body L57. P.402 notes 1-7 "
 "(L235-238) are now transcribed and linked. Cited works were not independently consulted. Page-image OCR "
 "corrections are recorded in note statements while S0 is preserved. P.403 onward L239-280 remains queued.")
statements.extend(news)

spans=sorted((int(r["start_char"]),int(r["end_char"]),r["mention_id"]) for r in [*mentions,*newm] if r["segment_id"]==NOTES)
for i,a in enumerate(spans):
    for b in spans[i+1:]:
        if b[0]>=a[1]:break
        nested=(a[0]<=b[0] and b[1]<=a[1]) or (b[0]<=a[0] and a[1]<=b[1])
        if a[:2]==b[:2] or not nested:raise SystemExit(f"overlapping note mentions: {a[2]} / {b[2]}")

paths=[T/"entity-candidates.csv",T/"mentions.csv",T/"book-statements.jsonl",T/"s2-coverage.csv"]
backs=[p.with_name(p.name+BACKUP) for p in paths]
if args.apply:
    present=[p.exists() for p in backs]
    if any(present) and not all(present):raise SystemExit("incomplete recovery backup set exists")
    if all(present):
        if any(hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(b.read_bytes()).digest() for p,b in zip(paths,backs)):
            raise SystemExit("existing backups do not match current pre-apply state")
    else:
        for p,b in zip(paths,backs):shutil.copy2(p,b)
    wcsv(paths[0],cp,[*candidates,*newc]);wcsv(paths[1],mp,[*mentions,*newm]);wjsonl(paths[2],statements);wcsv(paths[3],vp,coverage)
    print(f"applied p.402 notes 1-7: candidates +{len(newc)}, mentions +{len(newm)}, statements +{len(news)}; body links {sum(map(len,body_links.values()))}")
    print(f"recovery suffix {BACKUP}")
else:
    print(json.dumps({"mode":"dry-run","page":402,"notes":"1-7","candidates_added":len(newc),"mentions_added":len(newm),
      "citation_statements_added":len(news),"body_statement_marker_links":sum(map(len,body_links.values())),
      "ocr_correction_moved":1,"coverage_after":"reviewed/partial through L238; L239-280 remain"},ensure_ascii=False,indent=2))
