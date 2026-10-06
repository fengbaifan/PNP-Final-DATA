#!/usr/bin/env python3
"""Controlled migration of printed p.406 footnotes 1-9; dry-run by default."""
import argparse,csv,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"; PDF=ROOT/"02-sources"/"01-book"/"CHP-20Postscript.pdf"
NOTES="chp-20:20_CHP-20Postscript:l211-280"
SRC_SHA="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA="f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP=".bak-s2-chp20-notes-p406-20261004"
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
if (len(candidates),len(mentions),len(statements),len(coverage))!=(11179,25858,11189,832): raise SystemExit("unexpected S2 pre-state")
cb={r["candidate_id"]:r for r in candidates}; sb={r["statement_id"]:r for r in statements}; cv={r["segment_id"]:r for r in coverage}
if NOTES not in cv or (cv[NOTES]["disposition"],cv[NOTES]["migration_status"],cv[NOTES]["source_line_ranges"])!=("reviewed","partial","L212-258"):
 raise SystemExit(f"unexpected note coverage state: {cv.get(NOTES)}")
lines=SRC.read_text(encoding="utf-8-sig").splitlines(); note_text="\n".join(lines[210:280]); offsets={}; pos=0
for n in range(211,281): offsets[n]=pos; pos+=len(lines[n-1])+1
candidate_specs=[
 ("cand-11201","D’Arcais (surname-only author cited at p.406 note 5; identity unresolved)","person",261,"The printed footnote gives only a surname; do not infer full identity before bibliography review and S3."),
 ("cand-11202","D’Arcais publication cited at p.406 note 5 (title and year unspecified)","archive",261,"Surname-only short citation; title, year, and full bibliographic identity await the bibliography pass."),
 ("cand-11203","Konopleva (surname-only author cited at p.406 note 7; identity unresolved)","person",262,"The printed footnote gives only a surname; do not infer full identity before bibliography review and S3."),
 ("cand-11204","Konopleva publication cited at p.406 note 7 (title and year unspecified)","archive",262,"Surname-only short citation; title, year, and full bibliographic identity await the bibliography pass."),
 ("cand-11205","Ernst (surname-only author cited at p.406 note 8; identity unresolved)","person",262,"The printed footnote gives only a surname; do not infer full identity before bibliography review and S3."),
 ("cand-11206","Ernst publication cited at p.406 note 8 (title and year unspecified)","archive",262,"One of two semicolon-separated short citations; title, year, and full identity await bibliography review."),
 ("cand-11207","Fomiciova (surname-only author cited at p.406 note 8; identity unresolved)","person",262,"The printed footnote gives only a surname; do not infer full identity before bibliography review and S3."),
 ("cand-11208","Fomiciova publication cited at p.406 note 8 (title and year unspecified)","archive",262,"One of two semicolon-separated short citations; title, year, and full identity await bibliography review."),
]
natural={(r["canonical_name"].strip().casefold(),r["suggested_type"].strip().casefold()) for r in candidates}; newc=[]
for cid,name,kind,ln,detail in candidate_specs:
 if cid in cb or (name.strip().casefold(),kind.casefold()) in natural: raise SystemExit(f"candidate collision: {cid} {name}")
 row={f:"" for f in cp}; row.update(candidate_id=cid,canonical_name=name,suggested_type=kind,status="open",detail=detail,candidate_origin="body-mention",candidate_source_ref=f"{NOTES}#L{ln}")
 newc.append(row); cb[cid]=row; natural.add((name.strip().casefold(),kind.casefold()))
body_links={
 1:["st-chp20-p405-mazza-mcswiny-pictures-catalogue-open","st-chp20-p406-mazza-mcswiny-catalogue-coverage"],
 2:["st-chp20-p406-ivanov-french-interest-survey"],
 3:["st-chp20-p406-garas-banque-royale-account","st-chp20-p406-garas-vienna-employment"],
 4:["st-chp20-p406-garas-zwinger-frescoes"],
 5:["st-chp20-p406-bellucci-vienna-dates"],
 6:["st-chp20-p406-bjurstrom-tessin-drawings"],
 7:["st-chp20-p406-russian-court-valeriani-book"],
 8:["st-chp20-p406-russian-court-later-articles"],
 9:["st-chp20-p406-vivian-scholarship-and-open-question","st-chp20-p406-vivian-partial-sale-hypothesis"],
}
# statement id, marker, source line, exact S0 quote or citation subquote, cited source candidate, related candidates, claim, optional OCR correction
notespecs=[
 ("st-chp20-p406-n01-citation",1,259,"1 Mazza.","cand-11079",["cand-11078","cand-11080","cand-1466"],"Cites Barbara Mazza's survey and catalogue of the commemorative pictures painted for Owen McSwiny.",None),
 ("st-chp20-p406-n02-citation",2,259,"2 Venise au dix-huitième siècle.","cand-11082",["cand-11081","cand-11083","cand-2719"],"Cites the survey described in the body as Ivanov's account of contemporary French interest in eighteenth-century Venetian art.",None),
 ("st-chp20-p406-n03-citation",3,260,"3 Garas, 1962.","cand-9343",["cand-9342"],"Cites Garas, 1962, for the Banque Royale account and related employment discussion.",None),
 ("st-chp20-p406-n04-citation",4,260,"4 Garas, 1971.","cand-9456",["cand-9342","cand-1862","cand-11084"],"Cites Garas's 1971 article on Pellegrini in Germany and the Zwinger frescoes.",None),
 ("st-chp20-p406-n05-citation",5,261,"5 D’Arcáis.","cand-11202",["cand-11201","cand-0282","cand-2772"],"Cites a D’Arcais publication concerning Bellucci in Vienna; S0's accent is corrected from the page image.",("D’Arcáis","D’Arcais")),
 ("st-chp20-p406-n06-citation",6,261,"6 Bjurstrom, 1967.","cand-9445",["cand-7076","cand-11086"],"Cites Per Bjurström's 1967 article on Tessin as a collector of drawings.",None),
 ("st-chp20-p406-n07-citation",7,262,"7 Konopleva.","cand-11204",["cand-11203","cand-11089","cand-11087"],"Cites one of the later articles on the Russian court's interest in Venetian artists; full item awaits bibliography review.",None),
 ("st-chp20-p406-n08a-citation",8,262,"8 Ernst","cand-11206",["cand-11205","cand-11089","cand-11087"],"First semicolon-separated short citation in note 8; full item awaits bibliography review.",None),
 ("st-chp20-p406-n08b-citation",8,262,"Fomiciova","cand-11208",["cand-11207","cand-11089","cand-11087"],"Second semicolon-separated short citation in note 8; full item awaits bibliography review.",None),
 ("st-chp20-p406-n09-citation",9,263,"9 Vivian (with references to earlier articles).","cand-11092",["cand-9553","cand-11091","cand-2440","cand-9178","cand-1141"],"Cites Frances Vivian's scholarship on Consul Smith, with references to earlier articles, as the note states.",None),
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
 row={f:"" for f in mp}; row.update(mention_id=f"m-s2-chp20-notes-p406-{len(newm)+1:03d}",segment_id=NOTES,candidate_id=cid,surface_form=surface,start_char=start,end_char=end,
   note=f"Printed p.406 footnote {marker} {role}; cited work not independently consulted.")
 newm.append(row)
for spec in [
 (259,"Mazza","cand-11078",1,"author mention"),
 (259,"Venise au dix-huitième siècle","cand-11082",2,"publication title"),
 (260,"Garas, 1962","cand-9343",3,"publication citation"),
 (260,"Garas","cand-9342",3,"surname-only author mention","Garas, 1962"),
 (260,"Garas, 1971","cand-9456",4,"publication citation"),
 (260,"Garas","cand-9342",4,"surname-only author mention","Garas, 1971"),
 (261,"D’Arcáis","cand-11201",5,"surname-only author mention; OCR accent corrected in statement"),
 (261,"Bjurstrom, 1967","cand-9445",6,"publication citation"),
 (261,"Bjurstrom","cand-7076",6,"surname-only author mention","Bjurstrom, 1967"),
 (262,"Konopleva","cand-11203",7,"surname-only author mention"),
 (262,"Ernst","cand-11205",8,"first surname-only author mention"),
 (262,"Fomiciova","cand-11207",8,"second surname-only author mention"),
 (263,"Vivian","cand-9553",9,"surname-only author mention"),
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
 q={"source_line_start":ln,"source_line_end":ln,"printed_page":406,"pdf_physical_page":15,"footnote_marker":marker,
    "claim":claim,"speaker":"Haskell's footnote apparatus","text_layer":"bibliographic citation",
    "qualification":"Short citations only; missing titles, editions, and full identities are not inferred. Cited works were not independently consulted.",
    "mentioned_candidate_ids":list(dict.fromkeys([archive,*related])),"relation_candidate":False,"cited_material_not_independently_consulted":True}
 if fix:q["ocr_corrections"]=[{"source_line":ln,"ocr":fix[0],"print":fix[1],"basis":"CHP-20Postscript.pdf physical page 15 image"}]
 row={"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":None,"object_candidate_id":archive,"predicate":"footnote_cites_publication","qualifiers":q,"original_quote":quote,"origin":"book","source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md"}
 news.append(row); sb[sid]=row
for marker,body_ids in body_links.items():
 cite_ids=[x[0] for x in notespecs if x[1]==marker]
 for bid in body_ids:
  q=sb[bid]["qualifiers"]; q["footnote_text_pending"]=False; q["footnote_body_link_status"]="linked"
  linked=q.setdefault("footnote_statement_ids",[])
  for sid in cite_ids:
   if sid not in linked: linked.append(sid)
cv[NOTES]["source_line_ranges"]="L212-263"
oldtail="P.406 onward L259-280 remains queued."
if cv[NOTES].get("note","").count(oldtail)!=1: raise SystemExit("unexpected coverage note tail")
cv[NOTES]["note"]=cv[NOTES]["note"].replace(oldtail,"P.406 notes 1-9 (L259-263) are reviewed, transcribed, and linked to body statements; note 8 is preserved as two semicolon-separated citations. Printed note 5 reads D’Arcais; S0's accent is corrected in that note statement without changing S0. P.407 onward L264-280 remains queued.")
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
 print(f"applied p.406 notes 1-9: candidates +{len(newc)}, mentions +{len(newm)}, citation statements +{len(news)}; body statements linked {sum(map(len,body_links.values()))}")
 print(f"recovery suffix {BACKUP}")
else:
 print(json.dumps({"mode":"dry-run","page":406,"notes":"1-9 (note8 split into two citations)","candidates_added":len(newc),"mentions_added":len(newm),"citation_statements_added":len(news),
   "body_statements_linked":sum(map(len,body_links.values())),"ocr_corrections":1,"coverage_after":"reviewed/partial through L263; L264-280 remain"},ensure_ascii=False,indent=2))
