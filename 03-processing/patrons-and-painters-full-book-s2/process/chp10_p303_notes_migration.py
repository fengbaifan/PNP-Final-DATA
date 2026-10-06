"""Controlled p.303 note migration; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
T = ROOT / "04-knowledge" / "tables"
SRC = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
SRC_REL = "02-sources/02-Markdown/10_CHP-10_intro.md"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
BODY = "chp-10:10_CHP-10_intro:l402-409"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
NOTES_SHA = "9438d05e9bedcf9093e352c763d2075f29988f84f4bcf283cfdc8fdb7085a6dc"
BACKUP = ".bak-s2-chp10-p303-notes-20261002"

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)

def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader(); w.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)

def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]

def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for x in rows:
            f.write(json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)

def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--apply", action="store_true")
args = ap.parse_args()
raw = SRC.read_bytes()
if hashlib.sha256(raw).hexdigest() != ASSET_SHA:
    raise SystemExit("canonical OCR asset changed")
lines = SRC.read_text(encoding="utf-8-sig").splitlines()
if sha("\n".join(lines[599:604])) != NOTES_SHA:
    raise SystemExit("p.303 note source L600-L604 changed")

cp, mp, sp, vp = [T / x for x in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, cs = read_csv(cp); mf, ms = read_csv(mp); vf, covrows = read_csv(vp); ss = read_jsonl(sp)
cids = {x["candidate_id"] for x in cs}; mids = {x["mention_id"] for x in ms}; sids = {x["statement_id"] for x in ss}
cov = {x["segment_id"]: x for x in covrows}
maxid = max(int(re.search(r"(\d+)$", x).group(1)) for x in cids)
if maxid != 9523:
    raise SystemExit(f"candidate sequence changed: {maxid}")
for sid, expected in ((NOTES, ("reviewed", "partial", "L492-599")), (BODY, ("reviewed", "partial", "L403-408"))):
    r = cov.get(sid)
    got = (r["disposition"], r["migration_status"], r["source_line_ranges"]) if r else None
    if got != expected: raise SystemExit(f"coverage precondition changed for {sid}: {got}")
if any(x["segment_id"] == NOTES and x["qualifiers"].get("source_line_start") in range(600, 605) for x in ss):
    raise SystemExit("p.303 notes already migrated")

body = {x["statement_id"]: x for x in ss if x["segment_id"] == BODY}
links = {
  1: ["st-chp10-p303-zanetti-engraving-book"],
  2: ["st-chp10-p303-smith-carriera-early-work", "st-chp10-p303-carriera-sale-to-george"],
  3: ["st-chp10-p303-smith-paid-carriera", "st-chp10-p303-smith-arranged-english-commissions"],
  4: ["st-chp10-p303-winter-description"],
  5: ["st-chp10-p303-smith-commissioned-winter-versions"],
  6: ["st-chp10-p303-dingley-requested-similar-picture"],
}
for marker, ids in links.items():
    for sid in ids:
        r = body.get(sid)
        if not r or r["qualifiers"].get("footnote_marker") != marker or r["qualifiers"].get("footnote_text_pending") is not True:
            raise SystemExit(f"body marker {marker} changed: {sid}")

specs = [
 ("Ricci 24-plate group named in Zanetti's 1743 dedication", "work", "The p.303 dedication describes 24 plates after Marco Ricci, printed at Venice in 1743 and associated with Smith's and Zanetti's houses. Its exact identity with the book described in the body remains provisional; no maker role is inferred from the ambiguous Latin imprint.", 600),
 ("L. Cust (author cited at p.303 notes 2 and 4)", "person", "Surname-only reference in p.303 notes 2 and 4. Reconcile identity globally at S3.", 601),
 ("L. Cust publication cited at p.303 p.153", "archive", "Short-form citation only; possible match to a local bibliography item is not independently confirmed, and the cited page was not consulted.", 601),
 ("Carriera account entry dated 21 May 1726", "archive", "Quoted secondhand by Malamani 1899, p.147. The entry records Le Quattro Stagioni for dispatch to London to Smith; it gives no amount and does not itself establish payment or completed shipment.", 602),
 ("Carriera, Le Quattro Stagioni (account entry for dispatch to London, 1726)", "work", "Work named in a 21 May 1726 account entry as to be sent to London to Smith. Identity with other Four Seasons candidates remains for S3.", 602),
 ("V. Malamani, Rosalba Carriera (1899), cited p.147", "archive", "Possible match to the local bibliography entry Rosalba Carriera (1899), pp.27-149. Haskell cites p.147; that page was not independently consulted.", 602),
 ("Undated Joseph Smith letter to Rosalba Carriera (Cod. Ashburn 1781, vol. IV)", "archive", "Located by Haskell in Biblioteca Laurenziana, Florence, Cod. Ashburn 1781, vol. IV. Letter is undated and was not independently consulted.", 604),
 ("Biblioteca Laurenziana (repository named in p.303 note 5)", "institution", "Repository named by Haskell for an undated Smith-Carriera letter; no shelfmark beyond Cod. Ashburn 1781, vol. IV is supplied.", 604),
 ("V. Malamani, Rosalba Carriera (1899), cited p.134", "archive", "Possible match to the local bibliography entry Rosalba Carriera (1899), pp.27-149. Haskell cites p.134; that page was not independently consulted.", 409),
 ("Unnamed friend intended to receive one of Carriera's Winter versions", "person", "Haskell calls the recipient a friend or client; the identity is not given. The undated letter's wording leaves the decision about which version to send open at that point.", 409),
]
newc=[]; C={}
for i,(key,kind,detail,line) in enumerate(specs, maxid+1):
    cid=f"cand-{i:04d}"
    name=key
    if name.casefold() in {x["canonical_name"].casefold() for x in cs}: raise SystemExit(f"candidate duplicate: {name}")
    C[key]=cid
    refseg=BODY if line==409 else NOTES
    newc.append({"candidate_id":cid,"index_entry_id":"","canonical_name":name,"index_page_range":"","suggested_type":kind,"status":"open","index_source_file":"","sub_entry":"","detail":detail,"exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{refseg}#L{line}"})
allc=cids|{x["candidate_id"] for x in newc}

note_text="\n".join(lines[490:634]); body_text="\n".join(lines[401:409])
lineoffs=[]; n=0
for x in note_text.splitlines(): lineoffs.append(n); n+=len(x)+1
bodyoffs=[]; n=0
for x in body_text.splitlines(): bodyoffs.append(n); n+=len(x)+1
newm=[]
def mention(local, seg, ln, surface, cid, note=""):
    mid="m-chp10-p303-note-"+local
    if mid in mids or any(x["mention_id"]==mid for x in newm): raise SystemExit(f"duplicate mention {mid}")
    text=note_text if seg==NOTES else body_text
    base=lineoffs[ln-491] if seg==NOTES else bodyoffs[ln-402]
    source_line=lines[ln-1]
    at=source_line.find(surface)
    if at<0 or source_line.find(surface,at+1)>=0: raise SystemExit(f"non-unique span on L{ln}: {surface}")
    start=base+at; end=start+len(surface)
    if text[start:end]!=surface: raise SystemExit(f"span mismatch {mid}")
    newm.append({"mention_id":mid,"segment_id":seg,"candidate_id":cid,"surface_form":surface,"start_char":str(start),"end_char":str(end),"note":note})

M={
 "portfolio":C[specs[0][0]],"cust":C[specs[1][0]],"custpub":C[specs[2][0]],"account":C[specs[3][0]],"four":C[specs[4][0]],"mal147":C[specs[5][0]],"letter":C[specs[6][0]],"library":C[specs[7][0]],"mal134":C[specs[8][0]],"friend":C[specs[9][0]],
 "algarotti":"cand-0041","marco":"cand-2153","smith":"cand-2440","zanetti":"cand-2838","venice":"cand-3401","carriera":"cand-0588","london":"cand-1422","winter":"cand-9203","versions":"cand-9204","dingley":"cand-0921","malamani":"cand-9433","florence":"cand-3397","book":"cand-9201"
}
for argsm in [
 ("n1-algarotto",NOTES,600,"Algarotto",M["algarotti"],"Latin form in dedication."),("n1-plates",NOTES,600,"XXIV Tabulas",M["portfolio"],"Twenty-four plates named in dedication."),("n1-marco",NOTES,600,"Marco Ricci",M["marco"],""),("n1-smith",NOTES,600,"Joseph Smith",M["smith"],""),("n1-zanetti",NOTES,600,"Antonio Mariae Zanetti",M["zanetti"],""),("n1-venice",NOTES,600,"Venetiis",M["venice"],""),
 ("n2-cust",NOTES,601,"Cust",M["cust"],"Surname-only author reference."),("n2-page",NOTES,601,"p. 153",M["custpub"],"Citation locator, not page consultation."),
 ("n3-her",NOTES,602,"her",M["carriera"],"Corefers to Rosalba Carriera."),("n3-account",NOTES,602,"accounts for 21 May 1726",M["account"],"Account citation."),("n3-malamani",NOTES,602,"Malamani",M["malamani"],""),("n3-pubpage",NOTES,602,"1899, p. 147",M["mal147"],"Citation locator."),("n3-four-seasons",NOTES,602,"Quattro Stagioni",M["four"],""),("n3-london",NOTES,602,"Londra",M["london"],""),("n3-smith",NOTES,602,"Smith",M["smith"],""),
 ("n4-cust",NOTES,603,"Cust",M["cust"],"Surname-only author reference."),("n4-page",NOTES,603,"p. 153",M["custpub"],"Citation locator."),
 ("n5-letter",NOTES,604,"Letter from",M["letter"],"Document type and locator."),("n5-smith",NOTES,604,"Smith",M["smith"],""),("n5-carriera",NOTES,604,"Rosalba Carriera",M["carriera"],""),("n5-repository",NOTES,604,"Biblioteca Laurenziana",M["library"],""),("n5-florence",NOTES,604,"Florence",M["florence"],"Repository location."),("n5-cod",NOTES,604,"Cod.",M["letter"],"Shelfmark continuation."),
 ("n5-ashburn",BODY,409,"Ashburn, 1781, Vol. IV",M["letter"],"Continuation of note 5 locator at L604."),("n5-winter1",BODY,409,"l’altro Inverno",M["winter"],"OCR spelling retained; scan reads l’altro Inverno."),("n5-winter2",BODY,409,"dell’altro",M["winter"],"Corefers to the other Winter version."),("n5-two-versions",BODY,409,"di Due",M["versions"],"The letter refers to a choice between two versions."),("n5-friend",BODY,409,"all’atnico",M["friend"],"OCR reading; scan reads all’amico."),("n6-malamani",BODY,409,"Malamani",M["malamani"],""),("n6-page",BODY,409,"p. 134",M["mal134"],"Citation locator."),
]: mention(*argsm)

newst=[]; newids=set()
def statement(local, marker, ln, predicate, claim, subject=None, obj=None, mentioned=(), qualification="", related=(), quote_lines=None, extra=None):
    sid=f"st-chp10-p303-note{marker}-{local}"
    if sid in sids or sid in newids: raise SystemExit(f"duplicate statement {sid}")
    q={"source_line_start":ln,"source_line_end":quote_lines[-1] if quote_lines else ln,"printed_page":303,"pdf_physical_page":32,"claim":claim,"speaker":"Haskell, footnote" if ln!=409 else "Joseph Smith as quoted in Haskell, footnote 5","text_layer":"footnote citation or quoted source","qualification":qualification,"mentioned_candidate_ids":list(dict.fromkeys(mentioned)),"relation_candidate":predicate in {"dedicated_to","account_entry_records_work_for_dispatch","identifies_letter_locator","letter_describes_open_choice_between_two_versions"},"footnote_marker":marker,"footnote_text_pending":False,"related_body_statement_ids":related}
    if extra:q.update(extra)
    sl=quote_lines or [ln]
    orig="\n".join(lines[x-1] for x in sl)
    newst.append({"statement_id":sid,"segment_id":NOTES if ln!=409 else BODY,"subject_candidate_id":subject,"object_candidate_id":obj,"predicate":predicate,"qualifiers":q,"original_quote":orig,"origin":"book","source_file":SRC_REL})
    newids.add(sid); return sid

statement("dedication",1,600,"dedicated_to","The p.303 Latin dedication addresses Francesco Algarotti and presents a set of 24 plates after Marco Ricci.",M["portfolio"],M["algarotti"],[M["portfolio"],M["algarotti"],M["marco"]],"The plate group's identity with the publication described in the body is not established by this line alone.")
statement("imprint-and-plate-description",1,600,"describes_plate_group_and_1743_imprint","The imprint describes 24 plates after Marco Ricci, associated with the houses of Joseph Smith and Antonio Maria Zanetti, and gives Venice, 1743.",M["portfolio"],None,[M["portfolio"],M["marco"],M["smith"],M["zanetti"],M["venice"]],"Do not infer an individual engraver from the ambiguous 'Qui eas del. incid.' clause or equate this plate group with cand-9201 without S3.")
statement("cust-citation",2,601,"cites_work_page","Haskell cites Cust, page 153.",M["custpub"],None,[M["cust"],M["custpub"]],"Short-form citation only; the work and cited page were not independently consulted.",links[2],extra={"citations":[{"author_candidate_id":M["cust"],"page":"153","match":"possible local bibliography match"}],"cited_material_not_independently_consulted":True})
statement("account-entry",3,602,"account_entry_records_work_for_dispatch","Malamani's publication of Carriera's account records Le Quattro Stagioni for dispatch to London to Mr Smith.",M["account"],M["four"],[M["account"],M["four"],M["malamani"],M["mal147"],M["london"],M["smith"]],"The entry says 'per spedire' (for sending); it gives no amount and does not itself establish payment or completed shipment. It only narrows the p.303 general payment claim to one cited 21 May 1726 account entry.",links[3],extra={"citations":[{"source_candidate_id":M["mal147"],"author_candidate_id":M["malamani"],"page":"147","quoted_text":"Dato le Quattro Stagioni, per spedire a Londra, al Sig. Smith.","cited_material_not_independently_consulted":True}],"cited_material_not_independently_consulted":True})
statement("cust-citation",4,603,"cites_work_page","Haskell again cites Cust, page 153, for the description of Winter.",M["custpub"],None,[M["cust"],M["custpub"],M["winter"]],"Short-form citation only; the work and cited page were not independently consulted.",links[4],extra={"citations":[{"author_candidate_id":M["cust"],"page":"153","match":"possible local bibliography match"}],"cited_material_not_independently_consulted":True})
statement("letter-locator",5,604,"identifies_letter_locator","Haskell locates an undated letter from Joseph Smith to Rosalba Carriera in Biblioteca Laurenziana, Florence, Cod. Ashburn 1781, volume IV.",M["letter"],M["library"],[M["letter"],M["smith"],M["carriera"],M["library"],M["florence"]],"Letter not independently consulted; line L409 continues the quotation and locator.",links[5],quote_lines=[604],extra={"cited_material_not_independently_consulted":True})
statement("letter-quote",5,409,"letter_describes_open_choice_between_two_versions","In the undated letter, Smith says he would like to compare the other Winter with the first before deciding which of the two to send to his friend.",M["smith"],M["friend"],[M["smith"],M["carriera"],M["winter"],M["versions"],M["friend"]],"The OCR has 'Lunedi desiderei ... à confronto ... all’atnico'; the scan reads 'Lunedì desidererei ... a confronto ... all’amico'. The letter leaves the choice and recipient unresolved at that point, creating an apparent temporal tension with Haskell's body statement that the other version was sent. The letter is undated; do not harmonize chronology or infer the outcome.",links[5],quote_lines=[409],extra={"scan_reading":"Lunedì desidererei molto volentieri vederlo a confronto dell’altro per poter allora con più fondamento risolvere quali di Due inviare all’amico.","cited_material_not_independently_consulted":True})
statement("malamani-citation",6,409,"cites_work_page","Haskell cites Malamani 1899, page 134, for Robert Dingley's 1735 request.",M["mal134"],None,[M["malamani"],M["mal134"],M["dingley"]],"Possible local bibliography match only; the cited page and letter were not independently consulted.",links[6],quote_lines=[409],extra={"citations":[{"author_candidate_id":M["malamani"],"year":"1899","page":"134","match":"possible local bibliography match"}],"cited_material_not_independently_consulted":True})

for r in newst:
    q=r["qualifiers"]
    for cid in [r["subject_candidate_id"],r["object_candidate_id"],*q["mentioned_candidate_ids"]]:
        if cid and cid not in allc: raise SystemExit(f"missing candidate {cid} in {r['statement_id']}")
for seg in (NOTES,BODY):
    old=[(int(x["start_char"]),int(x["end_char"]),x["mention_id"]) for x in ms if x["segment_id"]==seg]
    added=sorted((int(x["start_char"]),int(x["end_char"]),x["mention_id"]) for x in newm if x["segment_id"]==seg)
    for i,a in enumerate(added):
        if any(a[0]<b[1] and b[0]<a[1] for b in old): raise SystemExit(f"new mention overlaps existing span: {a[2]}")
        if i and added[i-1][1]>a[0]: raise SystemExit(f"new mentions overlap: {added[i-1][2]} / {a[2]}")

body["st-chp10-p303-smith-paid-carriera"]["qualifiers"]["qualification"]="Haskell summarizes payments in 1725, 1726 and 1728, but note 3 cites only a 21 May 1726 account entry. That entry names Four Seasons for dispatch to London to Smith, with no amount; it does not itself prove payment or completed shipment. The broader chronology is not established by this note."
body["st-chp10-p303-smith-commissioned-winter-versions"]["qualifiers"]["qualification"]="Haskell says Smith commissioned two versions, kept the preferred one and sent the other to a friend or client. The undated letter quoted in note 5 says he wished to compare both before deciding which to send to his friend; the chronology and outcome are unresolved, so preserve the apparent tension. The recipient and physical versions are unidentified."
body["st-chp10-p303-smith-commissioned-winter-versions"]["qualifiers"]["mentioned_candidate_ids"].append(M["friend"])
for m in ms:
    if m["mention_id"]=="m-chp10-p303-friend-or-client":
        m["candidate_id"]=M["friend"]
        m["note"]="Haskell leaves the unnamed recipient as friend or client; note 5's letter uses amico but does not identify the person."
if not any(m["mention_id"]=="m-chp10-p303-friend-or-client" for m in ms): raise SystemExit("expected existing friend-or-client mention missing")
byc={x["candidate_id"]:x for x in cs}
byc["cand-9201"]["detail"]+=" P.303 note 1 describes a 24-plate group after Marco Ricci dedicated to Algarotti in a Venice 1743 imprint; identity with this publication remains unconfirmed."
byc["cand-9204"]["detail"]+=" P.303 note 5's undated letter leaves which of two Winter versions to send undecided at that point; do not reconcile with the body's sent-version statement until chronology/outcome are known."
cov[NOTES].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L492-604","note":"Merged notes processed through p.303 notes 1-6, including the Italian continuation at canonical OCR L409. Scan corrections at L600 and L409 are recorded in S2; no duplicate transcript is needed. P.303 markers 1-6 are linked. Next note range: p.304 note 1 at L605."})
cov[BODY].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L403-409","note":"P.303 body and its note links are processed. L409 contains the continuation of p.303 note 5 and all of note 6; it is retained under this canonical source segment without a duplicate transcript. The body sentence at L408 continues on p.304 L412, so keep partial until closed."})
for marker,ids in links.items():
    for sid in ids: body[sid]["qualifiers"]["footnote_text_pending"]=False

print(json.dumps({"mode":"APPLY" if args.apply else "DRY-RUN","new_candidates":len(newc),"new_mentions":len(newm),"new_statements":len(newst),"candidate_ids":[x["candidate_id"] for x in newc],"coverage":{"notes":"L492-604","body":"L403-409 partial"}},indent=2))
if args.apply:
    for p in (cp,mp,sp,vp):
        b=Path(str(p)+BACKUP)
        if b.exists(): raise SystemExit(f"backup exists: {b}")
        shutil.copy2(p,b)
    write_csv(cp,cf,cs+newc); write_csv(mp,mf,ms+newm); write_jsonl(sp,ss+newst); write_csv(vp,vf,covrows)
    print("Applied; next source cursor is p.304 note 1 at L605.")
