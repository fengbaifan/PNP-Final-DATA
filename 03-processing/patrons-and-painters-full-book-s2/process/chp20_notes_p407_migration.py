#!/usr/bin/env python3
"""Controlled migration of printed p.407 footnotes 1-6; dry-run by default."""
import argparse,csv,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"; PDF=ROOT/"02-sources"/"01-book"/"CHP-20Postscript.pdf"
NOTES="chp-20:20_CHP-20Postscript:l211-280"
SRC_SHA="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA="f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP=".bak-s2-chp20-notes-p407-20261004"
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
if (len(candidates),len(mentions),len(statements),len(coverage))!=(11187,25871,11199,832): raise SystemExit("unexpected S2 pre-state")
cb={r["candidate_id"]:r for r in candidates}; sb={r["statement_id"]:r for r in statements}; cv={r["segment_id"]:r for r in coverage}
if NOTES not in cv or (cv[NOTES]["disposition"],cv[NOTES]["migration_status"],cv[NOTES]["source_line_ranges"])!=("reviewed","partial","L212-263"):
 raise SystemExit(f"unexpected annotation coverage state: {cv.get(NOTES)}")
lines=SRC.read_text(encoding="utf-8-sig").splitlines(); note_text="\n".join(lines[210:280]); offsets={}; pos=0
for n in range(211,281): offsets[n]=pos; pos+=len(lines[n-1])+1
body_links={
 1:["st-chp20-p407-daniels-origin-of-smith-ricci-pictures"],
 2:["st-chp20-p407-constable-links-rome-visit-doubt"],
 3:["st-chp20-p407-levey-smith-view-alteration-1751"],
 4:["st-chp20-p407-smith-palladian-overdoor-commission"],
 5:["st-chp20-p407-binion-schulenburg-collection-assessment"],
 6:["st-chp20-p407-rossi-minor-genres-schulenburg"],
}
# statement id, marker, source line, exact S0 quote, cited work, related candidates, claim, optional OCR correction
notespecs=[
 ("st-chp20-p407-n01-citation",1,264,"1 Daniels, p. xv.","cand-11075",["cand-11093"],"Cites Daniels, p. xv, for his view that Smith was the originator of the Ricci picture group.",None),
 ("st-chp20-p407-n02-citation",2,264,"2 Constable (revised by Links), p. 32.","cand-11105",["cand-9913","cand-11104","cand-11095"],"Cites Constable's assessment, revised by Links, on the possible Rome visit.",None),
 ("st-chp20-p407-n03-citation",3,265,"3 Levey, 1962, p. 338.","cand-11097",["cand-10999","cand-11096"],"Cites Michael Levey's 1962 study of the Canaletto view altered for Smith.",None),
 ("st-chp20-p407-n04-citation",4,265,"4 Barcham.","cand-11099",["cand-11098"],"Cites William Barcham's analysis of Smith's Palladian overdoor commission.",None),
 ("st-chp20-p407-n05-citation",5,266,"8 Binion.","cand-11101",["cand-11100"],"Cites Alice Binion's article on Marshal Schulenburg's collection; the S0 note number is OCR-read as 8 but the print shows 5.",("8 Binion","5 Binion")),
 ("st-chp20-p407-n06-citation",6,266,"6 Rossi.","cand-11103",["cand-11102"],"Cites Elizabetta Antoniazzi Rossi's article on minor genres in Schulenburg's collection.",None),
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
 row={f:"" for f in mp}; row.update(mention_id=f"m-s2-chp20-notes-p407-{len(newm)+1:03d}",segment_id=NOTES,candidate_id=cid,surface_form=surface,start_char=start,end_char=end,
   note=f"Printed p.407 footnote {marker} {role}; cited work not independently consulted.")
 newm.append(row)
for spec in [
 (264,"Daniels, p. xv","cand-11075",1,"publication citation"),
 (264,"Daniels","cand-11093",1,"author mention","Daniels, p. xv"),
 (264,"Constable (revised by Links), p. 32","cand-11105",2,"publication citation"),
 (264,"Constable","cand-9913",2,"author mention","Constable (revised by Links), p. 32"),
 (264,"Links","cand-11104",2,"revising author mention","Constable (revised by Links), p. 32"),
 (265,"Levey, 1962, p. 338","cand-11097",3,"publication citation"),
 (265,"Levey","cand-10999",3,"author mention","Levey, 1962, p. 338"),
 (265,"Barcham","cand-11099",4,"publication citation"),
 (266,"Binion","cand-11101",5,"publication citation; printed marker 5"),
 (266,"Rossi","cand-11103",6,"publication citation"),
]: addm(*spec)
for sid,marker,ln,quote,archive,related,claim,fix in notespecs:
 if sid in sb: raise SystemExit(f"statement exists: {sid}")
 if quote not in lines[ln-1]: raise SystemExit(f"source quote mismatch L{ln}: {quote}")
 if archive not in cb or cb[archive]["suggested_type"]!="archive": raise SystemExit(f"archive candidate missing: {archive}")
 for cid in related:
  if cid not in cb: raise SystemExit(f"related candidate missing: {cid}")
 for bid in body_links[marker]:
  if bid not in sb: raise SystemExit(f"body statement missing: {bid}")
  q=sb[bid].get("qualifiers",{}); refs=[r for r in q.get("footnote_refs",[]) if isinstance(r,dict) and r.get("marker")==marker and r.get("segment_id")==NOTES]
  if len(refs)!=1 or refs[0].get("source_line")!=ln or q.get("footnote_text_pending") is not True: raise SystemExit(f"body link changed marker {marker}: {bid}")
 q={"source_line_start":ln,"source_line_end":ln,"printed_page":407,"pdf_physical_page":16,"footnote_marker":marker,
    "claim":claim,"speaker":"Haskell's footnote apparatus","text_layer":"bibliographic citation",
    "qualification":"Short citations only; missing titles, editions, and full identities are not inferred. Cited works were not independently consulted.",
    "mentioned_candidate_ids":list(dict.fromkeys([archive,*related])),"relation_candidate":False,"cited_material_not_independently_consulted":True}
 if fix:q["ocr_corrections"]=[{"source_line":ln,"ocr":fix[0],"print":fix[1],"basis":"CHP-20Postscript.pdf physical page 16 image"}]
 row={"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":None,"object_candidate_id":archive,"predicate":"footnote_cites_publication","qualifiers":q,"original_quote":quote,"origin":"book","source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md"}
 news.append(row); sb[sid]=row
for marker,body_ids in body_links.items():
 cite_ids=[x[0] for x in notespecs if x[1]==marker]
 for bid in body_ids:
  q=sb[bid]["qualifiers"]; q["footnote_text_pending"]=False; q["footnote_body_link_status"]="linked"
  linked=q.setdefault("footnote_statement_ids",[])
  for sid in cite_ids:
   if sid not in linked: linked.append(sid)
cv[NOTES]["source_line_ranges"]="L212-266"
oldtail="P.407 onward L264-280 remains queued."
if cv[NOTES].get("note","").count(oldtail)!=1: raise SystemExit("unexpected coverage note tail")
cv[NOTES]["note"]=cv[NOTES]["note"].replace(oldtail,"P.407 notes 1-6 (L264-266) are reviewed, transcribed, and linked to body statements. Printed note 5 is Binion; S0 OCR read 8, and the correction is recorded in the note statement without changing S0. P.408 onward L267-280 remains queued.")
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
 wcsv(paths[0],cp,candidates); wcsv(paths[1],mp,[*mentions,*newm]); wjsonl(paths[2],[*statements,*news]); wcsv(paths[3],vp,coverage)
 print(f"applied p.407 notes 1-6: candidates +0, mentions +{len(newm)}, statements +{len(news)}; body markers linked {sum(map(len,body_links.values()))}")
 print(f"recovery suffix {BACKUP}")
else:
 print(json.dumps({"mode":"dry-run","page":407,"notes":"1-6","candidates_added":0,"mentions_added":len(newm),"citation_statements_added":len(news),
   "body_statements_linked":sum(map(len,body_links.values())),"ocr_corrections":1,"coverage_after":"reviewed/partial through L266; L267-280 remain"},ensure_ascii=False,indent=2))
