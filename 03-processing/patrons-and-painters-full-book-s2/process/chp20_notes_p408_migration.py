#!/usr/bin/env python3
"""Controlled migration of printed p.408 footnotes 1-7; dry-run by default."""
import argparse,csv,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"; PDF=ROOT/"02-sources"/"01-book"/"CHP-20Postscript.pdf"
NOTES="chp-20:20_CHP-20Postscript:l211-280"
SRC_SHA="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA="f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP=".bak-s2-chp20-notes-p408-20261004"
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
if (len(candidates),len(mentions),len(statements),len(coverage))!=(11187,25881,11205,832): raise SystemExit("unexpected S2 pre-state")
cb={r["candidate_id"]:r for r in candidates}; sb={r["statement_id"]:r for r in statements}; cv={r["segment_id"]:r for r in coverage}
if NOTES not in cv or (cv[NOTES]["disposition"],cv[NOTES]["migration_status"],cv[NOTES]["source_line_ranges"])!=("reviewed","partial","L212-266"):
 raise SystemExit(f"unexpected annotation coverage state: {cv.get(NOTES)}")
lines=SRC.read_text(encoding="utf-8-sig").splitlines(); note_text="\n".join(lines[210:280]); offsets={}; pos=0
for n in range(211,281): offsets[n]=pos; pos+=len(lines[n-1])+1
candidate_specs=[
 ("cand-11209","Franco Venturi, 1969 publication cited at p.408 notes 1-2 (title unspecified)","archive",267,"A short citation in note 1 and pinpoint in note 2; exact title and edition await bibliography review."),
 ("cand-11210","Franco Venturi, 1976 publication cited at p.408 note 1 (title unspecified)","archive",267,"A second short citation in note 1; exact title and edition await bibliography review."),
]
natural={(r["canonical_name"].strip().casefold(),r["suggested_type"].strip().casefold()) for r in candidates}; newc=[]
for cid,name,kind,ln,detail in candidate_specs:
 if cid in cb or (name.strip().casefold(),kind.casefold()) in natural: raise SystemExit(f"candidate collision: {cid} {name}")
 row={f:"" for f in cp}; row.update(candidate_id=cid,canonical_name=name,suggested_type=kind,status="open",detail=detail,candidate_origin="body-mention",candidate_source_ref=f"{NOTES}#L{ln}")
 newc.append(row); cb[cid]=row; natural.add((name.strip().casefold(),kind.casefold()))
body_links={
 1:["st-chp20-p408-venetian-enlightenment-recent-scholarship","st-chp20-p408-haskell-qualifies-enlightenment-term"],
 2:["st-chp20-p408-venetian-enlightenment-recent-scholarship","st-chp20-p408-haskell-qualifies-enlightenment-term"],
 3:["st-chp20-p408-venetian-enlightenment-recent-scholarship","st-chp20-p408-haskell-qualifies-enlightenment-term"],
 4:["st-chp20-p408-byam-shaw-identifies-le-blon"],
 5:["st-chp20-p408-mccormick-boscarati-canvas"],
 6:["st-chp20-p408-olivato-casual-picture-selection","st-chp20-p408-olivato-boscarati-trial-testimony","st-chp20-p408-olivato-boscarati-subversive-opinions"],
 7:["st-chp20-p408-zanetti-caricature-album-presented-to-cini","st-chp20-p408-bettagno-zanetti-exhibition-catalogue"],
}
# id, marker, source line, exact S0 quote/subquote, cited source, related candidates, claim
notespecs=[
 ("st-chp20-p408-n01a-citation",1,267,"1 Venturi, 1969","cand-11209",["cand-2751","cand-11108","cand-11109"],"First citation in note 1: Venturi's 1969 study; note 2 supplies a page locator to this same candidate."),
 ("st-chp20-p408-n01b-citation",1,267,"1976","cand-11210",["cand-2751","cand-11108","cand-11109"],"Second citation in note 1: a distinct Venturi 1976 publication; title awaits bibliography review."),
 ("st-chp20-p408-n02-citation",2,267,"2 Venturi, 1969, pp. 295-99.","cand-11209",["cand-2751","cand-11108"],"Cites the 1969 Venturi study at pp.295-99 for the significance of Lodoli."),
 ("st-chp20-p408-n03-citation",3,268,"3 Torcellan, 1969.","cand-11110",["cand-2644","cand-11108"],"Cites Gianfranco Torcellan's 1969 publication."),
 ("st-chp20-p408-n04-citation",4,268,"4 Byam Shaw, 1967, pp. 21-6.","cand-11113",["cand-8432","cand-1375","cand-11112"],"Cites James Byam Shaw's 1967 study of Le Blon's invention, pp.21-26."),
 ("st-chp20-p408-n05-citation",5,269,"5 Vassar College Art Gallery, p. 24.","cand-11116",["cand-11114","cand-11115","cand-11117"],"Cites the Vassar College Art Gallery catalogue at p.24 for the Boscarati canvas."),
 ("st-chp20-p408-n06-citation",6,269,"6 Olivato, 1977.","cand-11119",["cand-11118","cand-11117","cand-9792"],"Cites Loredana Olivato's 1977 article on Boscarati and Pisani."),
 ("st-chp20-p408-n07-citation",7,270,"7 Bettagno.","cand-11123",["cand-9321","cand-11122","cand-2838"],"Cites Alessandro Bettagno's exhibition catalogue about the Zanetti album gift."),
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
 row={f:"" for f in mp}; row.update(mention_id=f"m-s2-chp20-notes-p408-{len(newm)+1:03d}",segment_id=NOTES,candidate_id=cid,surface_form=surface,start_char=start,end_char=end,
   note=f"Printed p.408 footnote {marker} {role}; cited work not independently consulted.")
 newm.append(row)
for spec in [
 (267,"Venturi, 1969","cand-11209",1,"publication citation","1 Venturi, 1969 and 1976"),
 (267,"Venturi","cand-2751",1,"author mention","1 Venturi, 1969 and 1976"),
 (267,"1976","cand-11210",1,"second publication year in the citation group","1 Venturi, 1969 and 1976"),
 (267,"Venturi, 1969, pp. 295-99","cand-11209",2,"publication citation and locator","2 Venturi, 1969, pp. 295-99."),
 (267,"Venturi","cand-2751",2,"author mention","2 Venturi, 1969, pp. 295-99."),
 (268,"Torcellan, 1969","cand-11110",3,"publication citation"),
 (268,"Torcellan","cand-2644",3,"author mention","Torcellan, 1969"),
 (268,"Byam Shaw, 1967, pp. 21-6","cand-11113",4,"publication citation"),
 (268,"Byam Shaw","cand-8432",4,"author mention","Byam Shaw, 1967, pp. 21-6"),
 (269,"Vassar College Art Gallery, p. 24","cand-11116",5,"catalogue citation"),
 (269,"Vassar College Art Gallery","cand-11115",5,"institution mention","Vassar College Art Gallery, p. 24"),
 (269,"Olivato, 1977","cand-11119",6,"publication citation"),
 (269,"Olivato","cand-11118",6,"author mention","Olivato, 1977"),
 (270,"Bettagno","cand-11123",7,"catalogue citation"),
]: addm(*spec)
for sid,marker,ln,quote,archive,related,claim in notespecs:
 if sid in sb: raise SystemExit(f"statement exists: {sid}")
 if quote not in lines[ln-1]: raise SystemExit(f"source quote mismatch L{ln}: {quote}")
 if archive not in cb or cb[archive]["suggested_type"]!="archive": raise SystemExit(f"archive candidate missing: {archive}")
 for cid in related:
  if cid not in cb: raise SystemExit(f"related candidate missing: {cid}")
 for bid in body_links[marker]:
  if bid not in sb: raise SystemExit(f"body statement missing: {bid}")
  q=sb[bid].get("qualifiers",{}); refs=[r for r in q.get("footnote_refs",[]) if isinstance(r,dict) and r.get("marker")==marker and r.get("segment_id")==NOTES]
  if len(refs)!=1 or refs[0].get("source_line")!=ln or q.get("footnote_text_pending") is not True: raise SystemExit(f"body link changed marker {marker}: {bid}")
 q={"source_line_start":ln,"source_line_end":ln,"printed_page":408,"pdf_physical_page":17,"footnote_marker":marker,
    "claim":claim,"speaker":"Haskell's footnote apparatus","text_layer":"bibliographic citation",
    "qualification":"Short citations only; missing titles and editions are not inferred. Cited works were not independently consulted.",
    "mentioned_candidate_ids":list(dict.fromkeys([archive,*related])),"relation_candidate":False,"cited_material_not_independently_consulted":True}
 row={"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":None,"object_candidate_id":archive,"predicate":"footnote_cites_publication","qualifiers":q,"original_quote":quote,"origin":"book","source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md"}
 news.append(row); sb[sid]=row
for marker,body_ids in body_links.items():
 cite_ids=[x[0] for x in notespecs if x[1]==marker]
 for bid in body_ids:
  q=sb[bid]["qualifiers"]; q["footnote_text_pending"]=False; q["footnote_body_link_status"]="linked"
  linked=q.setdefault("footnote_statement_ids",[])
  for sid in cite_ids:
   if sid not in linked: linked.append(sid)
cv[NOTES]["source_line_ranges"]="L212-270"
oldtail="P.408 onward L267-280 remains queued."
if cv[NOTES].get("note","").count(oldtail)!=1: raise SystemExit("unexpected coverage note tail")
cv[NOTES]["note"]=cv[NOTES]["note"].replace(oldtail,"P.408 notes 1-7 (L267-270) are reviewed, transcribed, and linked to body statements. Note 1 is represented as separate 1969 and 1976 citations; note 2 reuses the 1969 candidate with its page locator. P.409 onward L271-280 remains queued.")
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
 print(f"applied p.408 notes 1-7: candidates +{len(newc)}, mentions +{len(newm)}, citation statements +{len(news)}; body statements linked {sum(map(len,body_links.values()))}")
 print(f"recovery suffix {BACKUP}")
else:
 print(json.dumps({"mode":"dry-run","page":408,"notes":"1-7, with note1 split into 1969/1976 works","candidates_added":len(newc),"mentions_added":len(newm),"citation_statements_added":len(news),
   "body_statements_linked":sum(map(len,body_links.values())),"ocr_corrections":0,"coverage_after":"reviewed/partial through L270; L271-280 remain"},ensure_ascii=False,indent=2))
