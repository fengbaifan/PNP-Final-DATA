#!/usr/bin/env python3
"""Controlled migration of printed p.405 footnotes 1-9; dry-run by default."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"
PDF=ROOT/"02-sources"/"01-book"/"CHP-20Postscript.pdf"
NOTES="chp-20:20_CHP-20Postscript:l211-280"
SRC_SHA="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA="f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP=".bak-s2-chp20-notes-p405-20261004"
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
if (len(candidates),len(mentions),len(statements),len(coverage))!=(11177,25845,11180,832): raise SystemExit("unexpected S2 pre-state")
cb={r["candidate_id"]:r for r in candidates}; sb={r["statement_id"]:r for r in statements}; cv={r["segment_id"]:r for r in coverage}
if NOTES not in cv or (cv[NOTES]["disposition"],cv[NOTES]["migration_status"],cv[NOTES]["source_line_ranges"])!=("reviewed","partial","L212-253"):
    raise SystemExit(f"unexpected annotation coverage state: {cv.get(NOTES)}")
lines=SRC.read_text(encoding="utf-8-sig").splitlines(); note_text="\n".join(lines[210:280]); offsets={}; pos=0
for n in range(211,281): offsets[n]=pos; pos+=len(lines[n-1])+1
candidate_specs=[
 ("cand-11199","Merriman publication cited at p.405 note 1 (title and year unspecified)","archive",254,"Surname-only short citation; full publication identity awaits bibliography review; cited work not independently consulted."),
 ("cand-11200","Aikema publication cited at p.405 note 4 (title and year unspecified)","archive",255,"Surname-only short citation; full publication identity awaits bibliography review; cited work not independently consulted."),
]
natural={(r["canonical_name"].strip().casefold(),r["suggested_type"].strip().casefold()) for r in candidates}; newc=[]
for cid,name,kind,ln,detail in candidate_specs:
    if cid in cb or (name.strip().casefold(),kind.casefold()) in natural: raise SystemExit(f"candidate collision: {cid} {name}")
    row={f:"" for f in cp}; row.update(candidate_id=cid,canonical_name=name,suggested_type=kind,status="open",detail=detail,candidate_origin="body-mention",candidate_source_ref=f"{NOTES}#L{ln}")
    newc.append(row); cb[cid]=row; natural.add((name.strip().casefold(),kind.casefold()))
body_links={
 1:["st-chp20-p405-conti-crespi-jupiter-commission-found"],
 2:["st-chp20-p405-davis-venetian-aristocracy"],
 3:["st-chp20-p405-country-villa-research-pallucchini-volume"],
 4:["st-chp20-p405-zenobio-patronage-study"],
 5:["st-chp20-p405-puppi-corrects-valmarana-fresco-commission"],
 6:["st-chp20-p405-cordellina-vicenza-palace"],
 7:["st-chp20-p405-croft-murray-british-venetian-painters"],
 8:["st-chp20-p405-daniels-monograph-sebastiano-ricci"],
 9:["st-chp20-p405-shipley-amigoni-hostility"],
}
# statement id, marker, source line, exact S0 quote, citation candidate, related author candidates, claim
notespecs=[
 ("st-chp20-p405-n01-citation",1,254,"1 Merriman.","cand-11199",[],"Cites a Merriman publication for the newly surfaced Crespi painting; full identity awaits bibliography review."),
 ("st-chp20-p405-n02-citation",2,254,"2 Davis.","cand-11060",["cand-11059"],"Cites James C. Davis's study of the Venetian aristocracy."),
 ("st-chp20-p405-n03-citation",3,255,"3 Pallucchini, 1978.","cand-11063",["cand-11062"],"Cites the Pallucchini-edited volume on country-villa decoration."),
 ("st-chp20-p405-n04-citation",4,255,"4 Aikema.","cand-11200",[],"Cites an Aikema publication for the Zenobio family; full identity awaits bibliography review."),
 ("st-chp20-p405-n05-citation",5,256,"5 Puppi, 1968, pp. 211-50.","cand-11066",["cand-11065"],"Cites Puppi, 1968, pp. 211-50, for the Valmarana fresco commission."),
 ("st-chp20-p405-n06-citation",6,256,"6 Puppi, 1968, pp. 212-16.","cand-11066",["cand-11065"],"Cites the same provisional Puppi, 1968 publication candidate with a separate page locator for Cordellina."),
 ("st-chp20-p405-n07-citation",7,257,"7 Croft-Murray, 1970.","cand-11070",["cand-11001"],"Cites volume two of Croft-Murray's Decorative Painting in England."),
 ("st-chp20-p405-n08-citation",8,257,"8 Daniels.","cand-11075",["cand-11074"],"Cites Daniels's monograph on Sebastiano Ricci."),
 ("st-chp20-p405-n09-citation",9,258,"9 Shipley.","cand-11077",["cand-11076"],"Cites Shipley's article on hostility toward Amigoni."),
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
    row={f:"" for f in mp}; row.update(mention_id=f"m-s2-chp20-notes-p405-{len(newm)+1:03d}",segment_id=NOTES,candidate_id=cid,surface_form=surface,start_char=start,end_char=end,
       note=f"Printed p.405 footnote {marker} {role}; citation is not independent consultation of the cited work.")
    newm.append(row)
for spec in [
 (254,"Merriman","cand-11199",1,"surname-only citation"),
 (254,"Davis","cand-11060",2,"surname-only citation"),
 (255,"Pallucchini, 1978","cand-11063",3,"publication citation"),
 (255,"Pallucchini","cand-11062",3,"surname-only editor mention","Pallucchini, 1978"),
 (255,"Aikema","cand-11200",4,"surname-only citation"),
 (256,"Puppi, 1968, pp. 211-50","cand-11066",5,"publication citation"),
 (256,"Puppi","cand-11065",5,"surname-only author mention","Puppi, 1968, pp. 211-50"),
 (256,"Puppi, 1968, pp. 212-16","cand-11066",6,"publication citation"),
 (256,"Puppi","cand-11065",6,"surname-only author mention","Puppi, 1968, pp. 212-16"),
 (257,"Croft-Murray, 1970","cand-11070",7,"publication citation"),
 (257,"Croft-Murray","cand-11001",7,"surname-only author mention","Croft-Murray, 1970"),
 (257,"Daniels","cand-11075",8,"surname-only citation"),
 (258,"Shipley","cand-11077",9,"surname-only citation"),
]: addm(*spec)
for sid,marker,ln,quote,archive,related,claim in notespecs:
    if sid in sb: raise SystemExit(f"statement exists: {sid}")
    if quote not in lines[ln-1]: raise SystemExit(f"quote mismatch L{ln}: {quote}")
    if archive not in cb or cb[archive]["suggested_type"]!="archive": raise SystemExit(f"archive candidate missing: {archive}")
    for cid in related:
        if cid not in cb: raise SystemExit(f"related candidate missing: {cid}")
    for bid in body_links[marker]:
        if bid not in sb: raise SystemExit(f"body statement missing: {bid}")
        q=sb[bid].get("qualifiers",{}); refs=[r for r in q.get("footnote_refs",[]) if r.get("marker")==marker and r.get("segment_id")==NOTES]
        if len(refs)!=1 or refs[0].get("source_line")!=ln or q.get("footnote_text_pending") is not True: raise SystemExit(f"body link changed marker {marker}: {bid}")
    q={"source_line_start":ln,"source_line_end":ln,"printed_page":405,"pdf_physical_page":14,"footnote_marker":marker,
       "claim":claim,"speaker":"Haskell's footnote apparatus","text_layer":"bibliographic citation",
       "qualification":"Short citations only; missing title, edition, and full identity are not inferred. Cited works were not independently consulted.",
       "mentioned_candidate_ids":list(dict.fromkeys([archive,*related])),"relation_candidate":False,"cited_material_not_independently_consulted":True}
    row={"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":None,"object_candidate_id":archive,"predicate":"footnote_cites_publication",
         "qualifiers":q,"original_quote":quote,"origin":"book","source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md"}
    news.append(row); sb[sid]=row
for marker,body_ids in body_links.items():
    cite_ids=[x[0] for x in notespecs if x[1]==marker]
    for bid in body_ids:
        q=sb[bid]["qualifiers"]; q["footnote_text_pending"]=False; q["footnote_body_link_status"]="linked"
        linked=q.setdefault("footnote_statement_ids",[])
        for sid in cite_ids:
            if sid not in linked: linked.append(sid)
cv[NOTES]["source_line_ranges"]="L212-258"
oldtail="P.405 onward L254-280 remains queued."
if cv[NOTES].get("note","").count(oldtail)!=1: raise SystemExit("unexpected coverage note tail")
cv[NOTES]["note"]=cv[NOTES]["note"].replace(oldtail,"P.405 notes 1-9 (L254-258) are reviewed, transcribed, and linked to body statements; printed p.405 footnotes 1-9 agree with their body markers. P.406 onward L259-280 remains queued.")
spans=sorted((int(r["start_char"]),int(r["end_char"]),r["mention_id"]) for r in [*mentions,*newm] if r["segment_id"]==NOTES)
for i,a in enumerate(spans):
    for b in spans[i+1:]:
        if b[0]>=a[1]: break
        nested=(a[0]<=b[0] and b[1]<=a[1]) or (b[0]<=a[0] and a[1]<=b[1])
        if a[:2]==b[:2] or not nested: raise SystemExit(f"overlapping note mentions: {a[2]} / {b[2]}")
paths=[T/"entity-candidates.csv",T/"mentions.csv",T/"book-statements.jsonl",T/"s2-coverage.csv"]
backs=[p.with_name(p.name+BACKUP) for p in paths]
if args.apply:
    present=[p.exists() for p in backs]
    if any(present) and not all(present): raise SystemExit("incomplete recovery backup set exists")
    if all(present):
        if any(hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(b.read_bytes()).digest() for p,b in zip(paths,backs)): raise SystemExit("existing backups differ from current pre-state")
    else:
        for p,b in zip(paths,backs): shutil.copy2(p,b)
    wcsv(paths[0],cp,[*candidates,*newc]); wcsv(paths[1],mp,[*mentions,*newm]); wjsonl(paths[2],[*statements,*news]); wcsv(paths[3],vp,coverage)
    print(f"applied p.405 notes 1-9: candidates +{len(newc)}, mentions +{len(newm)}, statements +{len(news)}; body markers linked {sum(map(len,body_links.values()))}")
    print(f"recovery suffix {BACKUP}")
else:
    print(json.dumps({"mode":"dry-run","page":405,"notes":"1-9","candidates_added":len(newc),"mentions_added":len(newm),"citation_statements_added":len(news),
       "body_marker_links":sum(map(len,body_links.values())),"ocr_corrections":0,"coverage_after":"reviewed/partial through L258; L259-280 remain"},ensure_ascii=False,indent=2))
