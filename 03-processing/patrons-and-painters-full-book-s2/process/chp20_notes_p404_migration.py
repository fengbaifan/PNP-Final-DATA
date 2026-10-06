#!/usr/bin/env python3
"""Migrate printed p.404 notes 1-19; dry-run unless --apply is supplied."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]; T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"
PDF=ROOT/"02-sources"/"01-book"/"CHP-20Postscript.pdf"
NOTES="chp-20:20_CHP-20Postscript:l211-280"
SRC_SHA="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA="f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP=".bak-s2-chp20-notes-p404-20261004"
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
if (len(candidates),len(mentions),len(statements),len(coverage))!=(11162,25813,11160,832): raise SystemExit("unexpected S2 pre-state")
cb={r["candidate_id"]:r for r in candidates}; sb={r["statement_id"]:r for r in statements}; cv={r["segment_id"]:r for r in coverage}
if NOTES not in cv or (cv[NOTES]["disposition"],cv[NOTES]["migration_status"],cv[NOTES]["source_line_ranges"])!=("reviewed","partial","L212-243"):
    raise SystemExit(f"unexpected note coverage state: {cv.get(NOTES)}")
lines=SRC.read_text(encoding="utf-8-sig").splitlines(); note_text="\n".join(lines[210:280])
offsets={}; pos=0
for n in range(211,281): offsets[n]=pos; pos+=len(lines[n-1])+1

candidate_specs=[
 ("cand-11184","Omaggio a Leopoldo de’ Medici (exhibition catalogue cited at p.404 note 1)","archive",244,"Printed title of the exhibition catalogue cited for the discussion of Cardinal Leopoldo's taste; the catalogue was not independently consulted."),
 ("cand-11185","Procacci, Lucia e Ugo, publication cited at p.404 note 2 (title and year unspecified)","archive",244,"The note cites a publication by Lucia and Ugo Procacci; individual identity and full bibliographic details await the bibliography pass."),
 ("cand-11186","Lucia Procacci","person",244,"Given name and shared surname are explicit in p.404 note 2; identity alignment is deferred to S3."),
 ("cand-11187","Ugo Procacci","person",244,"Given name and shared surname are explicit in p.404 note 2; identity alignment is deferred to S3."),
 ("cand-11188","Muraro, 1965 publication cited at p.404 note 3 (title unspecified)","archive",245,"Short citation only; title and edition are not supplied and the work was not independently consulted."),
 ("cand-11189","Meloni Trkulja, 1975 publication cited at p.404 note 4 (title unspecified)","archive",245,"Short citation only; title and edition are not supplied. Do not merge the surname with Silvia Meloni before bibliography review and S3."),
 ("cand-11190","Meloni Trkulja (author cited in p.404 notes 4, 15, and 18; identity unresolved)","person",245,"Surname form cited in the footnotes; possible relation to body candidate Silvia Meloni is unresolved and must be decided at S3."),
 ("cand-11191","Lankheit publication cited at p.404 note 8 (title and year unspecified)","archive",247,"Short citation only; reconcile title and edition against the bibliography."),
 ("cand-11192","Twilight of the Medici (catalogue cited at p.404 note 9)","archive",248,"Printed title associated with the 1974 Florence/Detroit exhibition; do not treat the title as the event itself."),
 ("cand-11193","Rudolph, 1971 publication cited at p.404 note 10 (title unspecified)","archive",248,"The note distinguishes a 1971 item from Rudolph's 1973 item; title and edition await bibliography review."),
 ("cand-11194","Rudolph, 1973 publication cited at p.404 note 10 (title unspecified)","archive",248,"The note distinguishes a 1973 item from Rudolph's 1971 item; title and edition await bibliography review."),
 ("cand-11195","Strocchi publication cited at p.404 note 12 (title and year unspecified)","archive",249,"Short citation only; author identity and publication details are unresolved."),
 ("cand-11196","Borroni Salvadori (author cited at p.404 note 14; identity unresolved)","person",250,"Surname pair named in the citation; full identity alignment is deferred to S3."),
 ("cand-11197","Meloni Trkulja, 1972 publication cited at p.404 notes 15 and 18 (title unspecified)","archive",251,"Both notes cite the same author and year; retain one provisional publication candidate until bibliography evidence confirms whether the locators refer to one work."),
 ("cand-11198","Urbino: Restauri, publication cited at p.404 note 19, pp. 532-52","archive",253,"Printed title and page range of the cited source; the source was not independently consulted."),
]
natural={(r["canonical_name"].strip().casefold(),r["suggested_type"].strip().casefold()) for r in candidates}; newc=[]
for cid,name,kind,ln,detail in candidate_specs:
    if cid in cb or (name.strip().casefold(),kind.casefold()) in natural: raise SystemExit(f"candidate collision: {cid} {name}")
    row={f:"" for f in cp}; row.update(candidate_id=cid,canonical_name=name,suggested_type=kind,status="open",detail=detail,
      candidate_origin="body-mention",candidate_source_ref=f"{NOTES}#L{ln}")
    newc.append(row); cb[cid]=row; natural.add((name.strip().casefold(),kind.casefold()))

body_links={
 1:["st-chp20-p404-leopoldo-exhibition-articles-taste"],2:["st-chp20-p404-leopoldo-exhibition-articles-taste"],
 3:["st-chp20-p404-leopoldo-exhibition-articles-taste"],4:["st-chp20-p404-leopoldo-exhibition-articles-taste"],
 5:["st-chp20-p404-leopoldo-exhibition-articles-taste"],6:["st-chp20-p404-leopoldo-exhibition-articles-taste"],
 7:["st-chp20-p404-prinz-uffizi-self-portrait-gallery-analysis"],8:["st-chp20-p404-lankheit-reassesses-cosimo-iii"],
 9:["st-chp20-p404-late-baroque-florence-detroit-exhibition"],10:["st-chp20-p404-rudolph-florentine-provincial-culture"],
 11:["st-chp20-p404-inventories-magnasco-limited-patronage"],12:["st-chp20-p404-inventories-magnasco-limited-patronage"],
 13:["st-chp20-p404-inventories-magnasco-limited-patronage"],14:["st-chp20-p404-1706-role-corrected-by-1705-catalogue"],
 15:["st-chp20-p404-1706-role-corrected-by-1705-catalogue"],16:["st-chp20-p404-gabbiani-cleaning-and-scholarship"],
 17:["st-chp20-p404-gabbiani-cleaning-and-scholarship"],18:["st-chp20-p404-meloni-del-rosso-giordano-context"],
 19:["st-chp20-p404-buonaccorsi-gallery-acquisition-dispersal"],
}
# id, marker, source line, exact S0 quote or citation subquote, cited work, related authors/entities, claim, correction
notespecs=[
 ("st-chp20-p404-n01-citation",1,244,"1 Omaggio a Leopoldo de’ Medici.","cand-11184",["cand-11023"],"The note cites the exhibition catalogue Omaggio a Leopoldo de’ Medici.",None),
 ("st-chp20-p404-n02-citation",2,244,"2 Procacci, Lucia e Ugo.","cand-11185",["cand-11025","cand-11186","cand-11187"],"The note cites a publication by Lucia and Ugo Procacci; the two author candidates remain subject to S3 identity alignment.",None),
 ("st-chp20-p404-n03-citation",3,245,"3 Muraro, 1965.","cand-11188",["cand-11026"],"The note cites Muraro, 1965.",None),
 ("st-chp20-p404-n04-citation",4,245,"4 Meloni Trkulja, 1975.","cand-11189",["cand-11190"],"The note cites Meloni Trkulja, 1975; identity is not merged with Silvia Meloni in S2.",None),
 ("st-chp20-p404-n05-citation",5,246,"6 Chiarini de Anna.","cand-11024",["cand-11028"],"The note cites a Chiarini de Anna article in the article series on Cardinal Leopoldo; the OCR note number is corrected from 6 to printed 5.",("6 Chiarini de Anna","5 Chiarini de Anna")),
 ("st-chp20-p404-n06-citation",6,246,"8 Bandera.","cand-11024",["cand-11029"],"The note cites a Bandera article in the article series on Cardinal Leopoldo; the OCR note number is corrected from 8 to printed 6.",("8 Bandera","6 Bandera")),
 ("st-chp20-p404-n07-citation",7,247,"7 Prinz.","cand-11031",["cand-11030"],"The note cites Prinz's analysis of the formation of the Uffizi self-portrait gallery.",None),
 ("st-chp20-p404-n08-citation",8,247,"8 Lankheit.","cand-11191",["cand-10997"],"The note cites a Lankheit publication on Cosimo III's role.",None),
 ("st-chp20-p404-n09-citation",9,248,"9 Twilight of the Medici.","cand-11192",["cand-11033"],"The note cites the catalogue titled Twilight of the Medici for the Florence/Detroit exhibition.",None),
 ("st-chp20-p404-n10a-citation",10,248,"Rudolph, 1971","cand-11193",["cand-11035"],"The first reference in note 10 is a 1971 publication by Stella Rudolph.",None),
 ("st-chp20-p404-n10b-citation",10,248,"1973","cand-11194",["cand-11035"],"The second year in note 10 identifies a separate 1973 publication by Stella Rudolph.",None),
 ("st-chp20-p404-n11-citation",11,249,"11 Chiarini, 1975.","cand-11039",["cand-11040"],"The note cites Chiarini's 1975 inventories of Grand Prince Ferdinand.",None),
 ("st-chp20-p404-n12-citation",12,249,"12 Strocchi.","cand-11195",["cand-11041"],"The note cites a Strocchi publication; full bibliographic identity remains unresolved.",None),
 ("st-chp20-p404-n13-citation",13,250,"13 Guelfi, pp. 65 ff.","cand-11044",["cand-11043"],"The note cites Guelfi's monograph, pp. 65 ff.",None),
 ("st-chp20-p404-n14-citation",14,250,"14 Borroni Salvadori.","cand-11045",["cand-11196"],"The note attributes the account of Florence art exhibitions to Borroni Salvadori.",None),
 ("st-chp20-p404-n15-citation",15,251,"15 Meloni Trkulja, 1972, p. 53.","cand-11197",["cand-11190"],"The note cites Meloni Trkulja, 1972, p.53.",None),
 ("st-chp20-p404-n16-citation",16,251,"16 Chiarini, 1976.","cand-11050",["cand-11040"],"The note cites Chiarini's 1976 articles on Antonio Domenico Gabbiani.",None),
 ("st-chp20-p404-n17-citation",17,252,"17 Ewald, 1976.","cand-11052",["cand-11051"],"The note cites Ewald's 1976 articles on Antonio Domenico Gabbiani.",None),
 ("st-chp20-p404-n18-citation",18,252,"18 Meloni Trkulja, 1972.","cand-11197",["cand-11190"],"The note cites the same provisional 1972 Meloni Trkulja publication candidate as note 15; bibliography review will confirm whether it is the same work.",None),
 ("st-chp20-p404-n19-citation",19,253,"19 Urbino: Restauri, pp. 532-52.","cand-11198",["cand-11054"],"The note cites Urbino: Restauri, pp.532-52, in connection with the Gallery of the Aeneid.",None),
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
    row={f:"" for f in mp}; row.update(mention_id=f"m-s2-chp20-notes-p404-{len(newm)+1:03d}",segment_id=NOTES,candidate_id=cid,
      surface_form=surface,start_char=start,end_char=end,note=f"Printed p.404 footnote {marker} {role}; citation is not independent consultation of the cited work.")
    newm.append(row)

for spec in [
 (244,"Omaggio a Leopoldo de’ Medici","cand-11184",1,"catalogue title",None),
 (244,"Procacci, Lucia e Ugo","cand-11185",2,"publication citation",None),
 (244,"Procacci","cand-11025",2,"plural author-group mention","Procacci, Lucia e Ugo"),
 (244,"Lucia","cand-11186",2,"named author mention","Procacci, Lucia e Ugo"),
 (244,"Ugo","cand-11187",2,"named author mention","Procacci, Lucia e Ugo"),
 (245,"Muraro, 1965","cand-11188",3,"publication citation",None),
 (245,"Muraro","cand-11026",3,"surname-only author mention","Muraro, 1965"),
 (245,"Meloni Trkulja, 1975","cand-11189",4,"publication citation",None),
 (245,"Meloni Trkulja","cand-11190",4,"surname-only author mention","Meloni Trkulja, 1975"),
 (246,"Chiarini de Anna","cand-11028",5,"surname-form author mention; print marker is 5",None),
 (246,"Bandera","cand-11029",6,"surname-only author mention; print marker is 6",None),
 (247,"Prinz","cand-11030",7,"surname-only author mention",None),
 (247,"Lankheit","cand-10997",8,"surname-only author mention",None),
 (248,"Twilight of the Medici","cand-11192",9,"catalogue title",None),
 (248,"Rudolph, 1971","cand-11193",10,"first publication citation",None),
 (248,"Rudolph","cand-11035",10,"author mention","Rudolph, 1971"),
 (248,"1973","cand-11194",10,"second publication year in the citation group","Rudolph, 1971 and 1973"),
 (249,"Chiarini, 1975","cand-11039",11,"inventory citation",None),
 (249,"Chiarini","cand-11040",11,"surname-only author mention","Chiarini, 1975"),
 (249,"Strocchi","cand-11041",12,"surname-only author mention",None),
 (250,"Guelfi, pp. 65 ff","cand-11044",13,"monograph citation",None),
 (250,"Guelfi","cand-11043",13,"surname-only author mention","Guelfi, pp. 65 ff"),
 (250,"Borroni Salvadori","cand-11196",14,"surname-form author mention",None),
 (251,"Meloni Trkulja, 1972, p. 53","cand-11197",15,"publication citation",None),
 (251,"Meloni Trkulja","cand-11190",15,"surname-only author mention","Meloni Trkulja, 1972, p. 53"),
 (251,"Chiarini, 1976","cand-11050",16,"publication citation",None),
 (251,"Chiarini","cand-11040",16,"surname-only author mention","Chiarini, 1976"),
 (252,"Ewald, 1976","cand-11052",17,"publication citation",None),
 (252,"Ewald","cand-11051",17,"surname-only author mention","Ewald, 1976"),
 (252,"Meloni Trkulja, 1972","cand-11197",18,"publication citation",None),
 (252,"Meloni Trkulja","cand-11190",18,"surname-only author mention","Meloni Trkulja, 1972"),
 (253,"Urbino: Restauri, pp. 532-52","cand-11198",19,"publication title and locator",None),
]: addm(*spec)

for sid,marker,ln,quote,archive,related,claim,fix in notespecs:
    if sid in sb: raise SystemExit(f"statement exists: {sid}")
    if quote not in lines[ln-1]: raise SystemExit(f"quote mismatch L{ln}: {quote}")
    if archive not in cb or cb[archive]["suggested_type"]!="archive": raise SystemExit(f"archive candidate missing: {archive}")
    for bid in body_links[marker]:
        if bid not in sb: raise SystemExit(f"body statement missing: {bid}")
        q=sb[bid].get("qualifiers",{}); refs=[r for r in q.get("footnote_refs",[]) if r.get("marker")==marker and r.get("segment_id")==NOTES]
        if len(refs)!=1 or refs[0].get("source_line")!=ln or q.get("footnote_text_pending") is not True:
            raise SystemExit(f"body link changed marker {marker}: {bid}")
    q={"source_line_start":ln,"source_line_end":ln,"printed_page":404,"pdf_physical_page":13,"footnote_marker":marker,
      "claim":claim,"speaker":"Haskell’s footnote apparatus","text_layer":"bibliographic citation",
      "qualification":"Short citation only; absent titles, editions, and identities are not inferred. Cited material was not independently consulted.",
      "mentioned_candidate_ids":list(dict.fromkeys([archive,*related])),"relation_candidate":False,
      "cited_material_not_independently_consulted":True}
    if fix:q["ocr_corrections"]=[{"source_line":ln,"ocr":fix[0],"print":fix[1],"basis":"CHP-20Postscript.pdf physical page 13 image"}]
    news.append({"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":None,"object_candidate_id":archive,
      "predicate":"footnote_cites_publication","qualifiers":q,"original_quote":quote,"origin":"book",
      "source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md"}); sb[sid]=news[-1]

for marker,body_ids in body_links.items():
    cite_ids=[x[0] for x in notespecs if x[1]==marker]
    for bid in body_ids:
        q=sb[bid]["qualifiers"]; q["footnote_text_pending"]=False; q["footnote_body_link_status"]="linked"
        linked=q.setdefault("footnote_statement_ids",[])
        for sid in cite_ids:
            if sid not in linked: linked.append(sid)

cv[NOTES]["source_line_ranges"]="L212-253"
cv[NOTES]["note"]=("P.396 notes 1-6 (L212-214), p.397 notes 1-12 (L215-220), p.398 notes 1-7 (L221-224), p.399 notes 1-3 (L225), "
 "p.400 notes 1-8 (L226-230), p.401 notes 1-8 (L231-234), p.402 notes 1-7 (L235-238), p.403 notes 1-10 (L239-243), "
 "and p.404 notes 1-19 (L244-253) are reviewed, transcribed, and linked to body statements; p.400 notes 9-10 are captured at body L57. "
 "Cited works were not independently consulted. Printed p.404 notes 5 and 6 were OCR-misnumbered in S0 as 6 and 8; page-image corrections are in note statements, S0 is preserved. "
 "P.405 onward L254-280 remains queued.")
statements.extend(news)

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
        if any(hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(b.read_bytes()).digest() for p,b in zip(paths,backs)):
            raise SystemExit("existing backups do not match current pre-apply state")
    else:
        for p,b in zip(paths,backs): shutil.copy2(p,b)
    wcsv(paths[0],cp,[*candidates,*newc]); wcsv(paths[1],mp,[*mentions,*newm]); wjsonl(paths[2],statements); wcsv(paths[3],vp,coverage)
    print(f"applied p.404 notes 1-19: candidates +{len(newc)}, mentions +{len(newm)}, statements +{len(news)}; body marker links 20")
    print(f"recovery suffix {BACKUP}")
else:
    print(json.dumps({"mode":"dry-run","page":404,"notes":"1-19","candidates_added":len(newc),"mentions_added":len(newm),
      "citation_statements_added":len(news),"body_marker_links":sum(map(len,body_links.values())),"ocr_corrections":2,
      "coverage_after":"reviewed/partial through L253; L254-280 remain"},ensure_ascii=False,indent=2))
