"""Controlled p.304 note migration; dry-run unless --apply."""
import argparse, csv, hashlib, json, re, shutil, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]; T=ROOT/"04-knowledge/tables"
SRC=ROOT/"02-sources/02-Markdown/10_CHP-10_intro.md"; SRC_REL="02-sources/02-Markdown/10_CHP-10_intro.md"
NOTES="chp-10:10_CHP-10_intro:l491-634"; BODY="chp-10:10_CHP-10_intro:l411-421"
ASSET_SHA="f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
NOTES_SHA="3ad6287ab1e72915e2975d70e7e1aaca58e9ea13b2658f53875840ae8a9cafce"
BACKUP=".bak-s2-chp10-p304-notes-20261002"

def rcsv(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f); return r.fieldnames,list(r)
def wc(p,fields,rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=p.parent,delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows);q=Path(f.name)
    q.replace(p)
def rjson(p): return [json.loads(x) for x in p.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
def wjson(p,rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=p.parent,delete=False) as f:
        for x in rows:f.write(json.dumps(x,ensure_ascii=False,separators=(",",":"))+"\n")
        q=Path(f.name)
    q.replace(p)
def sha(x):return hashlib.sha256(x.encode("utf-8")).hexdigest()

pa=argparse.ArgumentParser(description=__doc__);pa.add_argument("--apply",action="store_true");args=pa.parse_args()
if hashlib.sha256(SRC.read_bytes()).hexdigest()!=ASSET_SHA:raise SystemExit("canonical OCR asset changed")
lines=SRC.read_text(encoding="utf-8-sig").splitlines()
if sha("\n".join(lines[604:610]))!=NOTES_SHA:raise SystemExit("p.304 notes L605-L610 changed")
cp,mp,sp,vp=[T/x for x in ("entity-candidates.csv","mentions.csv","book-statements.jsonl","s2-coverage.csv")]
cf,cs=rcsv(cp);mf,ms=rcsv(mp);vf,vs=rcsv(vp);ss=rjson(sp)
cids={x["candidate_id"] for x in cs};mids={x["mention_id"] for x in ms};sids={x["statement_id"] for x in ss};cov={x["segment_id"]:x for x in vs}
maxid=max(int(re.search(r"(\d+)$",x).group(1)) for x in cids)
if maxid!=9533:raise SystemExit(f"candidate sequence changed: {maxid}")
for sid,state,rng in ((NOTES,"partial","L492-604"),(BODY,"partial","L412-421")):
    r=cov.get(sid);got=(r["migration_status"],r["source_line_ranges"]) if r else None
    if got!=(state,rng):raise SystemExit(f"coverage changed for {sid}: {got}")
if any(x["segment_id"]==NOTES and x["qualifiers"].get("source_line_start") in range(605,611) for x in ss):raise SystemExit("p.304 notes already migrated")
body={x["statement_id"]:x for x in ss if x["segment_id"]==BODY}
links={
 1:["st-chp10-p304-smith-country-house-lease-purchase"],
 2:["st-chp10-p304-smith-displayed-works","st-chp10-p304-smith-piazzetta-contact"],
 3:["st-chp10-p304-canaletto-work-start-date","st-chp10-p304-smith-directed-output"],
 4:["st-chp10-p304-smith-controlled-commissions"],
 5:["st-chp10-p304-smith-1729-complaint"],
 6:["st-chp10-p304-tessin-four-year-engagement"],
 7:["st-chp10-p304-smith-held-canalettos-versus-royal"],
}
for k,ids in links.items():
    for sid in ids:
        r=body.get(sid)
        if not r or r["qualifiers"].get("footnote_marker")!=k or r["qualifiers"].get("footnote_text_pending") is not True:raise SystemExit(f"body marker {k} changed: {sid}")

specs=[
 ("Dieci Savi alle Decime, record no. 1309, folio 84v (Venice)","archive","Archival locator cited for Smith's lease/purchase of the Mogliano house; do not assign this record to one leg of the transaction without reading it.",605),
 ("Notarial act by Vettor Todeschini, Atti 12,727, folio 135v", "archive", "One of two Sezione Notarile locators cited for the Mogliano lease/purchase claim; the act was not consulted.",605),
 ("Notarial act by Vettor Todeschini, Atti 12,731, folio 306v", "archive", "One of two Sezione Notarile locators cited for the Mogliano lease/purchase claim; the act was not consulted.",605),
 ("Vettor Todeschini (notary named in p.304 note 1)","person","Named in the archive locator; identity and biographical context remain for S3.",605),
 ("K. T. Parker (author cited for Canaletto, p.304 note 3)","person","Author of the locally matched Canaletto drawings publication candidate cand-9484; identity with other Parker candidates remains for S3.",607),
 ("Piazzetta works reportedly sent by Joseph Smith to Samuel Hill in November 1729", "work", "Haskell reports that Smith sent works by Piazzetta to Hill in November 1729, citing Chaloner. The individual works are unidentified; the cited article was not independently consulted.",606),
 ("Reported John Conduitt request for Smith to procure three Canaletto pictures, June 1730", "archive", "Quoted by Haskell at p.304 note 4. The note points to p.290 note 1, whose locator is a different 4 June 1729 Conduitt letter to McSwiny; source identity and cross-reference are unresolved.",608),
 ("Three unidentified Canaletto pictures requested by John Conduitt in June 1730", "work", "Unidentified group in Haskell's quoted report; do not infer titles, completion, or delivery.",608),
 ("Joseph Smith letter to Samuel Hill, 17 July 1730 (published by Chaloner)","archive","Letter identified in p.304 note 5; cited publication cand-9428 is reused. Letter and cited page were not independently consulted.",609),
 ("Christie's catalogue of Joseph Smith's pictures, 16 May 1776", "archive", "Auction catalogue named in p.304 note 7; cited as containing fourteen further pictures. Catalogue was not independently consulted.",610),
 ("Fourteen further pictures attributed to the 16 May 1776 Smith sale catalogue", "work", "Haskell says that fourteen further pictures appear in one sale catalogue; individual works are not identified. Implications are deferred to Appendix 5, which remains unread in this S2 pass.",610),
]
newc=[];C={}
for i,(name,kind,detail,ln) in enumerate(specs,maxid+1):
    if name.casefold() in {x["canonical_name"].casefold() for x in cs}:raise SystemExit(f"candidate duplicate: {name}")
    cid=f"cand-{i:04d}";C[name]=cid
    ref=f"{NOTES}#L{ln}"
    newc.append({"candidate_id":cid,"index_entry_id":"","canonical_name":name,"index_page_range":"","suggested_type":kind,"status":"open","index_source_file":"","sub_entry":"","detail":detail,"exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":ref})
M={
 "dsa":C[specs[0][0]],"act1":C[specs[1][0]],"act2":C[specs[2][0]],"todeschini":C[specs[3][0]],"parker":C[specs[4][0]],"piazworks":C[specs[5][0]],"conduitt_request":C[specs[6][0]],"three_pictures":C[specs[7][0]],"letter":C[specs[8][0]],"catalogue":C[specs[9][0]],"fourteen":C[specs[10][0]],
 "archive":"cand-8592","venice":"cand-3401","smith":"cand-2440","hill":"cand-1300","piazzetta":"cand-1901","chaloner":"cand-9427","chaloner_work":"cand-9428","parker_work":"cand-9484","conduitt":"cand-0820","canaletto":"cand-0514","conduitt_1729":"cand-9420","siren":"cand-9446","siren_work":"cand-9066","christies":"cand-9400"
}
note_text="\n".join(lines[490:634]); offsets=[];n=0
for x in note_text.splitlines():offsets.append(n);n+=len(x)+1
newm=[]
def mention(local,ln,surface,cid,note=""):
    mid="m-chp10-p304-note-"+local
    if mid in mids or any(x["mention_id"]==mid for x in newm):raise SystemExit(f"duplicate mention {mid}")
    row=lines[ln-1];at=row.find(surface)
    if at<0 or row.find(surface,at+1)>=0:raise SystemExit(f"non-unique L{ln} span: {surface}")
    start=offsets[ln-491]+at;end=start+len(surface)
    if note_text[start:end]!=surface:raise SystemExit(f"mention span mismatch: {mid}")
    newm.append({"mention_id":mid,"segment_id":NOTES,"candidate_id":cid,"surface_form":surface,"start_char":str(start),"end_char":str(end),"note":note})

for x in [
 ("n1-archive","Archivio di Stato",M["archive"],"Repository; archival record not independently consulted."),("n1-venice","Venice",M["venice"],""),("n1-dieci","Dieci Savi alle Decime",M["dsa"],""),("n1-no1309","No. 1309",M["dsa"],""),("n1-sezione","Sezione Notarile",M["archive"],"Repository subdivision."),("n1-todeschini","Vettor Todeschini",M["todeschini"],""),("n1-atti1","Atti 12,727",M["act1"],""),("n1-folio1","c. 13 5V",M["act1"],"OCR locator; scan reads c.135v."),("n1-atti2","12,731",M["act2"],""),("n1-folio2","c. 306V",M["act2"],"OCR locator; scan reads c.306v."),
 ("n2-smith","Smith",M["smith"],""),("n2-piazzetta","Piazzetta",M["piazzetta"],""),("n2-hill","Samuel Hill",M["hill"],""),("n2-chaloner","Chaloner",M["chaloner"],""),
 ("n3-parker","Parker",M["parker"],"Author identity candidate; S3 alignment pending."),("n3-pages","pp. 9 ff.",M["parker_work"],"Citation locator only."),
 ("n4-conduitt","John Conduitt",M["conduitt"],""),("n4-smith","Mr S[mith]",M["smith"],"Expansion is explicit in the printed bracket."),("n4-three-pictures","3 pictures",M["three_pictures"],""),("n4-canaletto","Canaletto",M["canaletto"],""),("n4-p290","p. 290, note 1",M["conduitt_1729"],"Internal citation points to a 1729 letter, not an identified June 1730 record."),
 ("n5-letter","Letter from",M["letter"],""),("n5-smith","Smith",M["smith"],""),("n5-hill","Samuel Hill",M["hill"],""),("n5-chaloner","Chaloner",M["chaloner"],""),("n6-siren","Siren",M["siren"],"Scan prints Sirén; source spelling retained."),("n6-page","p. 107",M["siren_work"],"Citation locator only."),
 ("n7-christies","Christie’s, 16 May 1776",M["catalogue"],""),("n7-catalogue-title","A Catalogue of the Capital and Valuable Collection of Italian, French, Flemish and Dutch Pictures",M["catalogue"],""),("n7-fourteen","fourteen",M["fourteen"],""),("n7-smith","foseph Smith",M["smith"],"OCR error; scan reads Joseph Smith."),
]:mention(x[0],{1:605,2:606,3:607,4:608,5:609,6:609,7:610}[int(x[0][1])],x[1],x[2],x[3])

allc=cids|{x["candidate_id"] for x in newc};newst=[];newids=set()
def statement(local,marker,ln,pred,claim,sub=None,obj=None,mentioned=(),qual="",related=(),citations=(),quote=None,relation=False,crossrefs=()):
    sid=f"st-chp10-p304-note{marker}-{local}"
    if sid in sids or sid in newids:raise SystemExit(f"duplicate statement {sid}")
    q={"source_line_start":ln,"source_line_end":ln,"printed_page":304,"pdf_physical_page":33,"claim":claim,"speaker":"Haskell, footnote","text_layer":"footnote quotation or citation","qualification":qual,"mentioned_candidate_ids":list(dict.fromkeys(mentioned)),"relation_candidate":relation,"footnote_marker":marker,"footnote_text_pending":False,"related_body_statement_ids":related}
    if citations:q["citations"]=list(citations);q["cited_material_not_independently_consulted"]=True
    if crossrefs:q["cross_reference_segments"]=list(crossrefs)
    newst.append({"statement_id":sid,"segment_id":NOTES,"subject_candidate_id":sub,"object_candidate_id":obj,"predicate":pred,"qualifiers":q,"original_quote":quote or lines[ln-1],"origin":"book","source_file":SRC_REL});newids.add(sid);return sid

statement("property-records",1,605,"cites_archival_records","Haskell cites three Venice archival locators for Smith's lease and later purchase of the Mogliano country house.",M["dsa"],M["act1"],[M["dsa"],M["act1"],M["act2"],M["archive"],M["todeschini"]],"The note does not identify which locator supports which transaction; no archival record was consulted.",links[1],citations=[{"repository_candidate_id":M["archive"],"record_candidates":[M["dsa"],M["act1"],M["act2"]],"locators_as_printed":["Dieci Savi alle Decime, no.1309, f.84v","Todeschini, Atti 12,727, c.135v","Todeschini, Atti 12,731, c.306v"]}])
statement("piazzetta-works-to-hill",2,606,"sent_work_group_to_person","Haskell says Smith sent works by Piazzetta to Samuel Hill in November 1729.",M["smith"],M["hill"],[M["smith"],M["piazzetta"],M["hill"],M["piazworks"],M["chaloner"]],"The individual works are unidentified; cited Chaloner passage was not independently consulted.",links[2],citations=[{"publication_candidate_id":M["chaloner_work"],"short_form":"Chaloner"}],relation=True)
statement("parker-reference",3,607,"cites_work_pages","Haskell directs readers to Parker, pages 9 and following.",M["parker_work"],None,[M["parker"],M["parker_work"],M["canaletto"]],"Citation locator only; cited pages were not independently consulted.",links[3],citations=[{"author_candidate_id":M["parker"],"publication_candidate_id":M["parker_work"],"pages":"9 ff."}])
statement("conduitt-procurement-request",4,608,"requested_procurement_of_works","Haskell quotes John Conduitt in June 1730 as desiring Mr Smith to procure three pictures from Canaletto.",M["conduitt"],M["smith"],[M["conduitt"],M["smith"],M["three_pictures"],M["canaletto"],M["conduitt_request"],M["conduitt_1729"]],"Haskell's internal reference points to p.290 note 1, which identifies a 4 June 1729 letter from Conduitt to McSwiny, not the quoted June 1730 request. Preserve the cross-reference discrepancy; the quoted record's identity and provenance remain unresolved.",links[4],citations=[{"internal_reference":"p.290 note 1","candidate_id":M["conduitt_1729"],"identity_with_reported_june_1730_request":"unresolved"}],relation=True,crossrefs=[NOTES])
statement("smith-hill-letter",5,609,"identifies_letter_and_publication","Haskell identifies a letter from Smith to Samuel Hill dated 17 July 1730 and says Chaloner published it.",M["letter"],M["chaloner_work"],[M["letter"],M["smith"],M["hill"],M["chaloner"],M["chaloner_work"]],"Letter and cited publication page not independently consulted; keep distinct from the 26 November 1729 Smith-Hill letter candidate.",links[5],citations=[{"publication_candidate_id":M["chaloner_work"],"date":"17 July 1730","letter_candidate":M["letter"]}],relation=True)
statement("siren-reference",6,609,"cites_work_page","Haskell cites Sirén, page 107.",M["siren_work"],None,[M["siren"],M["siren_work"]],"The scan reads Sirén; the cited page was not independently consulted.",links[6],citations=[{"author_candidate_id":M["siren"],"publication_candidate_id":M["siren_work"],"page":"107"}])
statement("christies-sale-catalogue",7,610,"reports_pictures_in_sale_catalogue","Haskell says fourteen further pictures appear in the 16 May 1776 Christie's catalogue for Joseph Smith's collection.",M["catalogue"],M["fourteen"],[M["catalogue"],M["fourteen"],M["christies"],M["smith"]],"Catalogue and lots were not independently consulted; the fourteen individual works are unidentified. Haskell defers implications to Appendix 5, which has not yet been processed.",links[7],citations=[{"institution_candidate_id":M["christies"],"catalogue_candidate_id":M["catalogue"],"date":"16 May 1776","appendix_cross_reference":"Appendix 5"}],relation=True)

for r in newst:
    for cid in [r["subject_candidate_id"],r["object_candidate_id"],*r["qualifiers"]["mentioned_candidate_ids"]]:
        if cid and cid not in allc:raise SystemExit(f"candidate foreign key missing: {cid}")
for k,ids in links.items():
    for sid in ids:body[sid]["qualifiers"]["footnote_text_pending"]=False
cov[NOTES].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L492-610","note":"Merged notes processed through p.304 notes 1-7 at L605-L610. P.304 note 4 quotes a June 1730 procurement request but its internal pointer to p.290 note 1 identifies a different June 1729 letter; retain the source discrepancy. Scan-only readings at L605, L609 and L610 are recorded in S2. P.304 markers 1-7 are linked. Next note range: p.305 note 1 at L611."})
cov[BODY].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L412-421","note":"P.304 notes 1-7 are processed and linked. Its final sentence continues at p.305 L424, so retain partial until that continuation is closed."})

for seg in [NOTES]:
    old=[(int(x["start_char"]),int(x["end_char"]),x["mention_id"]) for x in ms if x["segment_id"]==seg]
    added=sorted((int(x["start_char"]),int(x["end_char"]),x["mention_id"]) for x in newm if x["segment_id"]==seg)
    for i,a in enumerate(added):
        if any(a[0]<b[1] and b[0]<a[1] for b in old):raise SystemExit(f"new mention overlaps prior anchor: {a[2]}")
        if i and added[i-1][1]>a[0]:raise SystemExit(f"new mentions overlap: {added[i-1][2]} / {a[2]}")

print(json.dumps({"mode":"APPLY" if args.apply else "DRY-RUN","new_candidates":len(newc),"new_mentions":len(newm),"new_statements":len(newst),"candidate_ids":[x["candidate_id"] for x in newc],"coverage":{"notes":"L492-610","body":"L412-421 partial"}},indent=2))
if args.apply:
    for p in (cp,mp,sp,vp):
        b=Path(str(p)+BACKUP)
        if b.exists():raise SystemExit(f"backup exists: {b}")
        shutil.copy2(p,b)
    wc(cp,cf,cs+newc);wc(mp,mf,ms+newm);wjson(sp,ss+newst);wc(vp,vf,vs)
    print("Applied; next cursor is p.305 note 1 at L611.")
