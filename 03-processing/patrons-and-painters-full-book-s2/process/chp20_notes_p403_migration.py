#!/usr/bin/env python3
"""Migrate printed p.403 notes 1-10; dry-run unless --apply is supplied."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]; T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"
PDF=ROOT/"02-sources"/"01-book"/"CHP-20Postscript.pdf"
NOTES="chp-20:20_CHP-20Postscript:l211-280"
SRC_SHA="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA="f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP=".bak-s2-chp20-notes-p403-20261004"
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
if (len(candidates),len(mentions),len(statements),len(coverage))!=(11159,25797,11150,832): raise SystemExit("unexpected S2 pre-state")
cb={r["candidate_id"]:r for r in candidates}; sb={r["statement_id"]:r for r in statements}; cv={r["segment_id"]:r for r in coverage}
if NOTES not in cv or (cv[NOTES]["disposition"],cv[NOTES]["migration_status"],cv[NOTES]["source_line_ranges"])!=("reviewed","partial","L212-238"):
    raise SystemExit(f"unexpected notes coverage state: {cv.get(NOTES)}")
lines=SRC.read_text(encoding="utf-8-sig").splitlines(); note_text="\n".join(lines[210:280])
offsets={}; pos=0
for n in range(211,281): offsets[n]=pos; pos+=len(lines[n-1])+1

candidate_specs=[
 ("cand-11181","Pierre Rosenberg publication cited at p.403 note 1 (title and year unspecified)","archive",239,"The note cites a publication by Pierre Rosenberg for the identification and publication of the Versailles Fame painting. Full citation details await bibliography review; work not independently consulted."),
 ("cand-11182","Lankheit publication cited at p.403 note 2, pp. 326-38 (title and year unspecified)","archive",239,"The note gives Lankheit and pages 326-38 but no title or year. Do not merge with other Lankheit works before bibliography review."),
 ("cand-11183","Eugen, Prinz, publication cited at p.403 note 3, pp. 115-41 (bibliographic role unresolved)","archive",240,"The italicized short citation is transcribed as printed. Whether this is a work title or author form remains unresolved pending bibliography review."),
]
natural={(r["canonical_name"].strip().casefold(),r["suggested_type"].strip().casefold()) for r in candidates}; newc=[]
for cid,name,kind,ln,detail in candidate_specs:
    if cid in cb or (name.strip().casefold(),kind.casefold()) in natural: raise SystemExit(f"candidate collision: {cid} {name}")
    row={f:"" for f in cp}; row.update(candidate_id=cid,canonical_name=name,suggested_type=kind,status="open",detail=detail,
      candidate_origin="body-mention",candidate_source_ref=f"{NOTES}#L{ln}")
    newc.append(row); cb[cid]=row; natural.add((name.strip().casefold(),kind.casefold()))

body_links={
 1:["st-chp20-p403-rosenberg-identifies-publishes-fame-picture"],
 2:["st-chp20-p403-lankheit-prince-liechtenstein-research"],
 3:["st-chp20-p403-prince-eugene-collecting-research"],
 4:["st-chp20-p403-levey-english-royal-patronage-survey"],
 5:["st-chp20-p403-croft-murray-verrio-restoration-patronage"],
 6:["st-chp20-p403-isham-exhibition-catalogue"],
 7:["st-chp20-p403-medici-court-survey-chiarini-catalogue"],
 8:["st-chp20-p403-campbell-ferdinand-ii-palazzo-pitti"],
 9:["st-chp20-p403-campbell-ferdinand-ii-palazzo-pitti"],
 10:["st-chp20-p403-borea-don-lorenzo-ferdinand-leopoldo-open"],
}
# id, marker, source line, exact S0 quote, cited work, author/related candidates, claim, OCR fix
notespecs=[
 ("st-chp20-p403-n01-citation",1,239,"1 Rosenberg.","cand-11181",["cand-10995"],"The note cites a Rosenberg publication concerning the identification and publication of the painting.",None),
 ("st-chp20-p403-n02-citation",2,239,"2 Lankheit, pp. 326-38.","cand-11182",["cand-10997"],"The note cites Lankheit, pp. 326-38, for the research on the Prince of Liechtenstein.",None),
 ("st-chp20-p403-n03-citation",3,240,"3 Eugen, Prinz, especially pp. 115-41.","cand-11183",[],"The note cites the work printed as 'Eugen, Prinz', especially pp. 115-41; author/title role remains unresolved.",None),
 ("st-chp20-p403-n04-citation",4,240,"4 Levey, 1964.","cand-11000",["cand-10999"],"The note cites Michael Levey's catalogue as Levey, 1964.",None),
 ("st-chp20-p403-n05-citation",5,241,"8 Croft-Murray, 1962, pp. 50-60 and pp. 236-42.","cand-11002",["cand-11001"],"The note cites Croft-Murray's account, 1962, pp. 50-60 and 236-42; the OCR footnote number is corrected from 8 to printed 5.",("8 Croft-Murray","5 Croft-Murray")),
 ("st-chp20-p403-n06-citation",6,241,"6 Sir Thomas Isham.","cand-11004",["cand-1315"],"The note cites the Sir Thomas Isham exhibition catalogue.",None),
 ("st-chp20-p403-n07-citation",7,242,"7 Chiarini, 1969.","cand-11007",["cand-11008"],"The note cites Marco Chiarini's 1969 exhibition catalogue.",None),
 ("st-chp20-p403-n08-citation",8,242,"8 Campbell, 1966.","cand-11010",["cand-11009"],"The note cites Malcolm Campbell's 1966 article.",None),
 ("st-chp20-p403-n09-citation",9,243,"9 Campbell, 1977.","cand-11011",["cand-11009"],"The note cites Malcolm Campbell's 1977 book.",None),
 ("st-chp20-p403-n10-citation",10,243,"10 Borea.","cand-11014",["cand-11013"],"The note cites Evelina Borea's exhibition catalogue.",None),
]
newm=[]; news=[]; old_mkeys={(r["segment_id"],r["candidate_id"],str(r["start_char"]),str(r["end_char"])) for r in mentions}
def addm(ln,surface,cid,marker,role,within=None):
    line=lines[ln-1]; container=line; base=0
    if within is not None:
        base=line.find(within)
        if base<0 or line.find(within,base+1)>=0: raise SystemExit(f"ambiguous span container L{ln}: {within}")
        container=within
    ix=container.find(surface)
    if ix<0 or container.find(surface,ix+1)>=0: raise SystemExit(f"missing/ambiguous mention L{ln}: {surface}")
    start=offsets[ln]+base+ix; end=start+len(surface)
    if note_text[start:end]!=surface: raise SystemExit(f"mention offset mismatch L{ln}: {surface}")
    key=(NOTES,cid,str(start),str(end))
    if key in old_mkeys or any((r["segment_id"],r["candidate_id"],str(r["start_char"]),str(r["end_char"]))==key for r in newm): raise SystemExit(f"duplicate mention L{ln}: {surface}")
    row={f:"" for f in mp}; row.update(mention_id=f"m-s2-chp20-notes-p403-{len(newm)+1:03d}",segment_id=NOTES,candidate_id=cid,
      surface_form=surface,start_char=start,end_char=end,note=f"Printed p.403 footnote {marker} {role}; citation is not independent consultation of the cited work.")
    newm.append(row)

# Nested person spans are distinct; exact citation/author spans keep only the archive mention.
for spec in [
 (239,"Rosenberg","cand-11181",1,"citation locator; person retained in statement",None),
 (239,"Lankheit, pp. 326-38","cand-11182",2,"citation locator",None),
 (239,"Lankheit","cand-10997",2,"surname-only author mention","Lankheit, pp. 326-38"),
 (240,"Eugen, Prinz, especially pp. 115-41","cand-11183",3,"citation locator",None),
 (240,"Levey, 1964","cand-11000",4,"catalogue citation",None),
 (240,"Levey","cand-10999",4,"author mention","Levey, 1964"),
 (241,"Croft-Murray, 1962, pp. 50-60 and pp. 236-42","cand-11002",5,"account citation",None),
 (241,"Croft-Murray","cand-11001",5,"surname-only author mention","Croft-Murray, 1962, pp. 50-60 and pp. 236-42"),
 (241,"Sir Thomas Isham","cand-11004",6,"catalogue title; subject person retained in statement",None),
 (242,"Chiarini, 1969","cand-11007",7,"catalogue citation",None),
 (242,"Chiarini","cand-11008",7,"surname-only author mention","Chiarini, 1969"),
 (242,"Campbell, 1966","cand-11010",8,"article citation",None),
 (242,"Campbell","cand-11009",8,"author mention","Campbell, 1966"),
 (243,"Campbell, 1977","cand-11011",9,"book citation",None),
 (243,"Campbell","cand-11009",9,"author mention","Campbell, 1977"),
 (243,"Borea","cand-11014",10,"catalogue citation; author retained in statement",None),
]: addm(*spec)

for sid,marker,ln,quote,archive,related,claim,fix in notespecs:
    if sid in sb: raise SystemExit(f"statement exists: {sid}")
    if quote not in lines[ln-1]: raise SystemExit(f"quote mismatch L{ln}: {quote}")
    if archive not in cb or cb[archive]["suggested_type"]!="archive": raise SystemExit(f"archive candidate missing: {archive}")
    for bid in body_links[marker]:
        if bid not in sb: raise SystemExit(f"body statement missing: {bid}")
        q=sb[bid].get("qualifiers",{}); refs=[r for r in q.get("footnote_refs",[]) if r.get("marker")==marker and r.get("segment_id")==NOTES]
        if len(refs)!=1 or refs[0].get("source_line")!=ln or q.get("footnote_text_pending") is not True: raise SystemExit(f"body link changed marker {marker}: {bid}")
    q={"source_line_start":ln,"source_line_end":ln,"printed_page":403,"pdf_physical_page":12,"footnote_marker":marker,
      "claim":claim,"speaker":"Haskell’s footnote apparatus","text_layer":"bibliographic citation",
      "qualification":"Short citation only; no unprinted title, edition, or author identity is inferred. Cited material was not independently consulted.",
      "mentioned_candidate_ids":list(dict.fromkeys([archive,*related])),"relation_candidate":False,
      "cited_material_not_independently_consulted":True}
    if fix:q["ocr_corrections"]=[{"source_line":ln,"ocr":fix[0],"print":fix[1],"basis":"CHP-20Postscript.pdf physical page 12 image"}]
    news.append({"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":None,"object_candidate_id":archive,
      "predicate":"footnote_cites_publication","qualifiers":q,"original_quote":quote,"origin":"book",
      "source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md"}); sb[sid]=news[-1]

for marker,body_ids in body_links.items():
    cite_ids=[x[0] for x in notespecs if x[1]==marker]
    for bid in body_ids:
        q=sb[bid]["qualifiers"]; q["footnote_text_pending"]=False; q["footnote_body_link_status"]="linked"
        linked=q.setdefault("footnote_statement_ids",[])
        for sid in cite_ids:
            if sid not in linked:linked.append(sid)

cv[NOTES]["source_line_ranges"]="L212-243"
cv[NOTES]["note"]=("P.396 notes 1-6 (L212-214), p.397 notes 1-12 (L215-220), p.398 notes 1-7 (L221-224), p.399 notes 1-3 (L225), "
 "p.400 notes 1-8 (L226-230), p.401 notes 1-8 (L231-234), p.402 notes 1-7 (L235-238), and p.403 notes 1-10 "
 "(L239-243) are reviewed, transcribed, and linked to body statements; p.400 notes 9-10 are captured at body L57. "
 "Cited works were not independently consulted. Page-image OCR corrections are in note statements while S0 is preserved. "
 "P.404 onward L244-280 remains queued.")
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
    print(f"applied p.403 notes 1-10: candidates +{len(newc)}, mentions +{len(newm)}, statements +{len(news)}; body marker links {sum(map(len,body_links.values()))}")
    print(f"recovery suffix {BACKUP}")
else:
    print(json.dumps({"mode":"dry-run","page":403,"notes":"1-10","candidates_added":len(newc),"mentions_added":len(newm),
      "citation_statements_added":len(news),"body_marker_links":sum(map(len,body_links.values())),"ocr_corrections":1,
      "coverage_after":"reviewed/partial through L243; L244-280 remain"},ensure_ascii=False,indent=2))
