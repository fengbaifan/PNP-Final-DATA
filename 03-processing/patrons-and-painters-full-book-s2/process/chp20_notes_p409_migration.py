#!/usr/bin/env python3
"""Controlled migration of printed p.409 footnotes 1-9; dry-run by default."""
import argparse,csv,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"; PDF=ROOT/"02-sources"/"01-book"/"CHP-20Postscript.pdf"
NOTES="chp-20:20_CHP-20Postscript:l211-280"
SRC_SHA="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA="f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP=".bak-s2-chp20-notes-p409-20261004"
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
if (len(candidates),len(mentions),len(statements),len(coverage))!=(11189,25895,11213,832): raise SystemExit("unexpected S2 pre-state")
cb={r["candidate_id"]:r for r in candidates}; sb={r["statement_id"]:r for r in statements}; cv={r["segment_id"]:r for r in coverage}
if NOTES not in cv or (cv[NOTES]["disposition"],cv[NOTES]["migration_status"],cv[NOTES]["source_line_ranges"])!=("reviewed","partial","L212-270"):
 raise SystemExit(f"unexpected annotation coverage state: {cv.get(NOTES)}")
lines=SRC.read_text(encoding="utf-8-sig").splitlines(); note_text="\n".join(lines[210:280]); offsets={}; pos=0
for n in range(211,281): offsets[n]=pos; pos+=len(lines[n-1])+1
candidate_specs=[("cand-11211","Matina volume cited at p.409 note 1 (title unspecified)","archive",271,"Surname-only citation to the volume of Doge medal portraits; full bibliographic identity awaits the bibliography pass.")]
natural={(r["canonical_name"].strip().casefold(),r["suggested_type"].strip().casefold()) for r in candidates}; newc=[]
for cid,name,kind,ln,detail in candidate_specs:
 if cid in cb or (name.strip().casefold(),kind.casefold()) in natural: raise SystemExit(f"candidate collision: {cid} {name}")
 row={f:"" for f in cp}; row.update(candidate_id=cid,canonical_name=name,suggested_type=kind,status="open",detail=detail,candidate_origin="body-mention",candidate_source_ref=f"{NOTES}#L{ln}")
 newc.append(row); cb[cid]=row; natural.add((name.strip().casefold(),kind.casefold()))
body_links={
 1:["st-chp20-p408-parker-piccinio-engraving-models-partial","st-chp20-p409-maggiotto-historical-portraiture"],
 2:["st-chp20-p409-da-pozzo-edition-and-will-publication"],
 3:["st-chp20-p409-da-pozzo-edition-and-will-publication","st-chp20-p409-tesi-painted-pitt-bequests","st-chp20-p409-tiepolo-pictures-bequeathed-to-cosimo-mari"],
 4:["st-chp20-p409-tiepolo-subjects-explain-catalogue-absence"],
 5:["st-chp20-p409-road-to-calvary-berlin-sketch-identification","st-chp20-p409-banquet-sketch-cognacq-jay-possibility"],
 6:["st-chp20-p409-santifaller-algarotti-portraits-schmidt-print","st-chp20-p409-schmidt-salimbeni-etching"],
 7:["st-chp20-p409-santifaller-algarotti-etchings-collaboration"],
 8:["st-chp20-p409-levey-corrects-tiepolo-algarotti-portrait-theory"],
 9:["st-chp20-p409-santifaller-algarotti-tomb-painting-partial"],
}
# id, marker, source line, exact S0 quote/subquote, citation candidate, related candidates, claim, OCR fixes
notespecs=[
 ("st-chp20-p409-n01-citation",1,271,"1 Matins.","cand-11211",["cand-1578","cand-11124"],"Cites the source volume for the Doge medal portraits; print reads Matina, while S0 OCR reads Matins.",[("Matins","Matina")]),
 ("st-chp20-p409-n02-citation",2,271,"3 Algarotti, 1963.","cand-11126",["cand-0041","cand-11125"],"Cites the 1963 critical edition of Algarotti's essays by Giovanni da Pozzo; S0 OCR footnote number 3 is corrected to printed 2.",[("3 Algarotti","2 Algarotti")]),
 ("st-chp20-p409-n03-citation",3,272,"3 Da Pozzo.","cand-11127",["cand-11125","cand-10333"],"Cites da Pozzo's publication of the full text of Algarotti's will.",[]),
 ("st-chp20-p409-n04a-citation",4,272,"4 Haskell, 1958, p. 213","cand-9559",["cand-0041","cand-2569"],"First publication cited in note 4: Haskell's 1958 article at p.213.",[]),
 ("st-chp20-p409-n04b-citation",4,272,"Levey, i960, p. 250.","cand-10302",["cand-10999","cand-0041","cand-2569"],"Second publication cited in note 4: Levey's 1960 article at p.250; S0 OCR reads i960.",[("i960","1960")]),
 ("st-chp20-p409-n05-citation",5,273,"5 Haskell, 1958, p. 213.","cand-9559",["cand-0041","cand-2569"],"Cites the same Haskell 1958 article at p.213 as the first citation in note 4.",[]),
 ("st-chp20-p409-n06-citation",6,273,"6 Santifaller, 1976.","cand-11137",["cand-11134","cand-0041","cand-11135"],"Cites Maria Santifaller's 1976 article on portraits of Francesco Algarotti.",[]),
 ("st-chp20-p409-n07-citation",7,274,"7 Santifaller, 1977.","cand-11139",["cand-11134","cand-11138"],"Cites Santifaller's 1977 article on Algarotti's etchings.",[]),
 ("st-chp20-p409-n08-citation",8,274,"8 Levey, 1978.","cand-11140",["cand-10999","cand-2569","cand-0041"],"Cites Michael Levey's 1978 article on the Tiepolo portrait theory.",[]),
 ("st-chp20-p409-n09-citation",9,275,"9 Santifaller, 1978.","cand-11146",["cand-11134","cand-11141","cand-11142"],"Cites Santifaller's 1978 article on Algarotti's tomb painting.",[]),
]
newm=[]; news=[]; oldkeys={(r["segment_id"],r["candidate_id"],str(r["start_char"]),str(r["end_char"])) for r in mentions}
def addm(ln,surface,cid,marker,role,within=None):
 line=lines[ln-1]; container=line; base=0
 if within is not None:
  base=line.find(within)
  if base<0 or line.find(within,base+1)>=0: raise SystemExit(f"ambiguous container L{ln}: {within}")
  container=within
 ix=container.find(surface)
 if ix<0 or container.find(surface,ix+1)>=0: raise SystemExit(f"missing/ambiguous mention L{ln}: {surface}")
 start=offsets[ln]+base+ix; end=start+len(surface)
 if note_text[start:end]!=surface: raise SystemExit(f"mention offset mismatch L{ln}: {surface}")
 key=(NOTES,cid,str(start),str(end))
 if key in oldkeys or any((r["segment_id"],r["candidate_id"],str(r["start_char"]),str(r["end_char"]))==key for r in newm): raise SystemExit(f"duplicate mention L{ln}: {surface}")
 row={f:"" for f in mp}; row.update(mention_id=f"m-s2-chp20-notes-p409-{len(newm)+1:03d}",segment_id=NOTES,candidate_id=cid,surface_form=surface,start_char=start,end_char=end,
   note=f"Printed p.409 footnote {marker} {role}; cited work not independently consulted.")
 newm.append(row)
for spec in [
 (271,"Matins","cand-11211",1,"surname-form citation; S0 corrected to Matina"),
 (271,"Algarotti, 1963","cand-11126",2,"publication citation; printed marker 2"),
 (271,"Algarotti","cand-0041",2,"author/work subject mention","Algarotti, 1963"),
 (272,"Da Pozzo","cand-11127",3,"publication citation"),
 (272,"Haskell, 1958, p. 213","cand-9559",4,"publication citation and locator"),
 (272,"Levey, i960, p. 250","cand-10302",4,"publication citation and locator; OCR year corrected"),
 (272,"Levey","cand-10999",4,"surname-only author mention","Levey, i960, p. 250"),
 (273,"Haskell, 1958, p. 213","cand-9559",5,"publication citation and locator"),
 (273,"Santifaller, 1976","cand-11137",6,"publication citation"),
 (273,"Santifaller","cand-11134",6,"surname-only author mention","Santifaller, 1976"),
 (274,"Santifaller, 1977","cand-11139",7,"publication citation"),
 (274,"Santifaller","cand-11134",7,"surname-only author mention","Santifaller, 1977"),
 (274,"Levey, 1978","cand-11140",8,"publication citation"),
 (274,"Levey","cand-10999",8,"surname-only author mention","Levey, 1978"),
 (275,"Santifaller, 1978","cand-11146",9,"publication citation"),
 (275,"Santifaller","cand-11134",9,"surname-only author mention","Santifaller, 1978"),
]: addm(*spec)
for sid,marker,ln,quote,archive,related,claim,fixes in notespecs:
 if sid in sb: raise SystemExit(f"statement exists: {sid}")
 if quote not in lines[ln-1]: raise SystemExit(f"source quote mismatch L{ln}: {quote}")
 if archive not in cb or cb[archive]["suggested_type"]!="archive": raise SystemExit(f"archive candidate missing: {archive}")
 for cid in related:
  if cid not in cb: raise SystemExit(f"related candidate missing: {cid}")
 for bid in body_links[marker]:
  if bid not in sb: raise SystemExit(f"body statement missing: {bid}")
  q=sb[bid].get("qualifiers",{}); refs=[r for r in q.get("footnote_refs",[]) if isinstance(r,dict) and r.get("marker")==marker and r.get("segment_id")==NOTES]
  if len(refs)!=1 or refs[0].get("source_line")!=ln or q.get("footnote_text_pending") is not True: raise SystemExit(f"body link changed marker {marker}: {bid}")
 q={"source_line_start":ln,"source_line_end":ln,"printed_page":409,"pdf_physical_page":18,"footnote_marker":marker,
    "claim":claim,"speaker":"Haskell's footnote apparatus","text_layer":"bibliographic citation",
    "qualification":"Short citations only; missing titles and editions are not inferred. Cited works were not independently consulted.",
    "mentioned_candidate_ids":list(dict.fromkeys([archive,*related])),"relation_candidate":False,"cited_material_not_independently_consulted":True}
 if fixes:q["ocr_corrections"]=[{"source_line":ln,"ocr":a,"print":b,"basis":"CHP-20Postscript.pdf physical page 18 image"} for a,b in fixes]
 row={"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":None,"object_candidate_id":archive,"predicate":"footnote_cites_publication","qualifiers":q,"original_quote":quote,"origin":"book","source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md"}
 news.append(row); sb[sid]=row
for marker,body_ids in body_links.items():
 cite_ids=[x[0] for x in notespecs if x[1]==marker]
 for bid in body_ids:
  q=sb[bid]["qualifiers"]; q["footnote_text_pending"]=False; q["footnote_body_link_status"]="linked"
  linked=q.setdefault("footnote_statement_ids",[])
  for sid in cite_ids:
   if sid not in linked: linked.append(sid)
cv[NOTES]["source_line_ranges"]="L212-275"
oldtail="P.409 onward L271-280 remains queued."
if cv[NOTES].get("note","").count(oldtail)!=1: raise SystemExit("unexpected coverage note tail")
cv[NOTES]["note"]=cv[NOTES]["note"].replace(oldtail,"P.409 notes 1-9 (L271-275) are reviewed, transcribed, and linked to body statements; note 4 contains two citations. Page-image corrections record Matins→Matina, note number 3→2 for Algarotti 1963, and i960→1960 for Levey, without changing S0. P.410 onward L276-280 remains queued.")
spans=sorted((int(r["start_char"]),int(r["end_char"]),r["mention_id"]) for r in [*mentions,*newm] if r["segment_id"]==NOTES)
for i,a in enumerate(spans):
 for b in spans[i+1:]:
  if b[0]>=a[1]: break
  nested=(a[0]<=b[0] and b[1]<=a[1]) or (b[0]<=a[0] and a[1]<=b[1])
  if a[:2]==b[:2] or not nested: raise SystemExit(f"overlapping note mentions: {a[2]} / {b[2]}")
paths=[T/"entity-candidates.csv",T/"mentions.csv",T/"book-statements.jsonl",T/"s2-coverage.csv"]; backs=[p.with_name(p.name+BACKUP) for p in paths]
if args.apply:
 present=[p.exists() for p in backs]
 if any(present) and not all(present): raise SystemExit("incomplete recovery backup set exists")
 if all(present):
  if any(hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(b.read_bytes()).digest() for p,b in zip(paths,backs)): raise SystemExit("existing backups differ from current pre-state")
 else:
  for p,b in zip(paths,backs): shutil.copy2(p,b)
 wcsv(paths[0],cp,[*candidates,*newc]); wcsv(paths[1],mp,[*mentions,*newm]); wjsonl(paths[2],[*statements,*news]); wcsv(paths[3],vp,coverage)
 print(f"applied p.409 notes 1-9: candidates +{len(newc)}, mentions +{len(newm)}, citation statements +{len(news)}; body statements linked {sum(map(len,body_links.values()))}")
 print(f"recovery suffix {BACKUP}")
else:
 print(json.dumps({"mode":"dry-run","page":409,"notes":"1-9 (note4 split into two publications)","candidates_added":len(newc),"mentions_added":len(newm),"citation_statements_added":len(news),
   "body_statements_linked":sum(map(len,body_links.values())),"ocr_corrections":3,"coverage_after":"reviewed/partial through L275; L276-280 remain"},ensure_ascii=False,indent=2))
