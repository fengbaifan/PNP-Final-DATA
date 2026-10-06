#!/usr/bin/env python3
"""Controlled S2 migration for printed page 402."""
import argparse,csv,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"
PDF=ROOT/"02-sources"/"01-book"/"CHP-20Postscript.pdf"
P402="chp-20:20_CHP-20Postscript:l98-108"
P403="chp-20:20_CHP-20Postscript:l110-121"
P401="chp-20:20_CHP-20Postscript:l81-96"
NOTES="chp-20:20_CHP-20Postscript:l211-280"
BACKUP=".bak-s2-chp20-p402-20261004"
parser=argparse.ArgumentParser()
parser.add_argument("--apply",action="store_true")
args=parser.parse_args()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rcsv(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f);return r.fieldnames,list(r)
def wc(p,fields,rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=p.parent,delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n")
        w.writeheader();w.writerows(rows);tmp=Path(f.name)
    tmp.replace(p)
def wj(p,rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=p.parent,delete=False) as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
        tmp=Path(f.name)
    tmp.replace(p)
if sha(SRC)!="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90":raise SystemExit("source asset changed")
if sha(PDF)!="f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788":raise SystemExit("PDF changed")
cp,candidates=rcsv(T/"entity-candidates.csv")
mp,mentions=rcsv(T/"mentions.csv")
sp=T/"book-statements.jsonl"
statements=[json.loads(x) for x in sp.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
vp,coverage=rcsv(T/"s2-coverage.csv")
segments=[json.loads(x) for x in (T/"segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if x.strip()]
segs={x["segment_id"]:x for x in segments}
cand={x["candidate_id"]:x for x in candidates}
cov={x["segment_id"]:x for x in coverage}
for sid in (P402,P403,NOTES):
    if sid not in segs:raise SystemExit(f"missing segment {sid}")
if cov[P401]["migration_status"]!="complete":raise SystemExit("p.401 must be complete before p.402")
if (cov[P402]["disposition"],cov[P402]["migration_status"])!=("queued","pending"):raise SystemExit("p.402 is not queued")
if cov[P403]["disposition"]!="queued":raise SystemExit("p.403 must remain queued as p.402 continuation")
if segs[P402]["sha256"]!="64eb2299cfe55d839d396f3ac35f345ecc661c6ccde89528b08263d70b99e765":raise SystemExit("p.402 S0 hash changed")
lines=SRC.read_text(encoding="utf-8-sig").splitlines()
body="\n".join(lines[97:108])
if hashlib.sha256(body.encode("utf-8")).hexdigest()!=segs[P402]["sha256"]:raise SystemExit("p.402 segment hash mismatch")
if segs[P402]["asset_sha256"]!=sha(SRC):raise SystemExit("p.402 asset registration mismatch")
lineoff={};offset=0
for n in range(segs[P402]["line_start"],segs[P402]["line_end"]+1):
    lineoff[n]=offset;offset+=len(lines[n-1])+1

candidate_specs=[
("cand-10977","Council of Europe exhibition on Queen Christina's life and patronage in Rome (Stockholm, 1966)","event",99,"The source says relevant material was assembled at this exhibition; it is not the exhibition's complete catalogue or proceedings."),
("cand-10978","Council of Europe","institution",99,"Named as the exhibition sponsor/organizer in the source wording; institutional identity awaits S3."),
("cand-10979","Catalogue of the 1966 Stockholm exhibition on Queen Christina","archive",100,"The catalogue is cited as one location for information; it has not been independently consulted."),
("cand-10980","Related publication from the 1966 Stockholm exhibition","archive",100,"The source scan appears to read 'volume or studies and documents'; retain this ambiguous wording until a better copy can resolve it. Bibliographic details await the notes pass."),
("cand-10981","New critical edition of Bellori's Lives discussed in the second-edition postscript","archive",101,"The source says Giovanni Previtali wrote its introduction; exact edition data await the notes/bibliography pass."),
("cand-10982","Giovanni Previtali","person",101,"Named as the author of the critical edition's introduction; identity alignment is deferred to S3."),
("cand-10983","Ferrante Carlo","person",102,"Named as the writer from whom Bellori's comments were derived; identity alignment is deferred to S3."),
("cand-10984","Nicholas Turner","person",102,"Named as the scholar whose demonstration revises Haskell's earlier assessment; identity alignment is deferred to S3."),
("cand-10985","Nicholas Turner's demonstration concerning Bellori's comments on Lanfranco","archive",102,"The source describes a scholarly finding; footnote 4 remains pending and the publication is not independently consulted."),
("cand-10986","Italian Baroque artists introduced into France under Richelieu and Mazarin (unnamed group)","term",106,"A source-derived group; no individual artists are identified here."),
("cand-10987","Finest examples of Italian Baroque art sought for France by Mazarin (unnamed group)","work",107,"A group of works, not individually titled or located in this passage."),
("cand-10988","Perez Sanchez","person",105,"Named as author of the Spanish-paintings catalogue; retain source form and defer identity alignment to S3."),
("cand-10989","Catalogue of Italian seventeenth-century paintings still in Spain by Perez Sanchez","archive",105,"The catalogue and its documents/bibliography are described as providing information; they are not independently consulted."),
("cand-10990","Wethey","person",105,"Surname-only scholar cited for information about Naples viceroys; full identity is not inferred."),
("cand-10992","Madeleine Laurain-Portemer","person",106,"Named as author of later documented articles on Mazarin; identity alignment is deferred to S3."),
("cand-10993","Madeleine Laurain-Portemer's documented articles on Mazarin's artistic policy (group)","archive",106,"A series of articles published after Haskell's book; the complete list is deferred to the cited note and bibliography pass."),
("cand-10994","Unspecified picture in Alazard's commissioned-work reference (commissioner, title, and artist unresolved)","work",108,"The sentence ends at 'commissioned'; do not infer who commissioned the picture before p.403 is read."),
]
keys={(r["canonical_name"].strip().casefold(),r["suggested_type"].strip().casefold()) for r in candidates}
for cid,name,kind,ln,detail in candidate_specs:
    if cid in cand:raise SystemExit(f"candidate ID exists: {cid}")
    key=(name.strip().casefold(),kind.casefold())
    if key in keys:raise SystemExit(f"candidate natural key exists: {name}")
    row={"candidate_id":cid,"index_entry_id":"","canonical_name":name,"index_page_range":"",
         "suggested_type":kind,"status":"open","index_source_file":"","sub_entry":"",
         "detail":detail,"exclude_reason":"","candidate_origin":"body-mention",
         "candidate_source_ref":f"{P402}#L{ln}"}
    candidates.append(row);cand[cid]=row;keys.add(key)

mention_specs=[
("cand-0675","Queen Christina",99,99,"Reuse the Queen Christina of Sweden index candidate.",0),
("cand-4490","Rome",99,99,"Reuse the existing Rome place candidate.",0),
("cand-10978","Council of Europe",99,99,"Named in connection with the exhibition.",0),
("cand-10977","Council of Europe exhibition",99,99,"A 1966 exhibition in Stockholm.",0),
("cand-4790","Stockholm",99,99,"Reuse the Stockholm place candidate.",0),
("cand-10979","catalogue",100,100,"The exhibition catalogue is one cited source of information.",0),
("cand-10980","related volume or studies and documents",100,100,"The S0 text and scan appear to read 'or'; preserve this ambiguous source wording.",0),
("cand-0272","Bellori",101,101,"Reuse the Bellori index candidate with p.402 in its page range.",0),
("cand-10982","Giovanni Previtali",101,101,"Named as author of the edition's introduction.",0),
("cand-10981","new critical edition of the Lives",101,101,"The edition is discussed by Previtali's introduction.",0),
("cand-10984","Nicholas Turner",102,102,"Named as the scholar whose finding is summarized.",0),
("cand-10985","demonstration",102,102,"Turner's reported scholarly finding; the publication identity remains deferred to the notes/bibliography pass.",0),
("cand-0272","Bellori",102,102,"Reuse the Bellori candidate; this is his criticism of Lanfranco.",0),
("cand-1359","Lanfranco",102,102,"Reuse the indexed Giovanni Lanfranco candidate.",0),
("cand-10983","Ferrante Carlo",102,102,"Named as the writer from whom comments were derived.",0),
("cand-7272","Italianisation",104,104,"Reuse the chapter 7 Italianising-of-Europe term candidate.",0),
("cand-2500","Spanish patronage",105,105,"Reuse the index candidate with p.402 in its page range.",0),
("cand-10988","Perez Sanchez",105,105,"Named as the catalogue author; retain source spelling.",0),
("cand-10989","catalogue itself",105,105,"The source distinguishes the catalogue from its preliminary chapters.",0),
("cand-4132","Italian Baroque art",105,105,"Reuse the existing Baroque art in Italy term candidate.",0),
("cand-5120","Spain",105,105,"Reuse the existing geographic Spain candidate.",0),
("cand-6624","individual Viceroys in Naples",105,105,"Reuse the existing candidate for the unnamed Spanish viceroys governing Naples; no individuals are specified here.",0),
("cand-3534","Naples",105,105,"Reuse the existing Naples place candidate.",0),
("cand-10990","Wethey",105,105,"Surname-only scholar; identity remains unresolved.",0),
("cand-1588","Cardinal Mazarin",106,106,"Reuse the Mazarin index candidate with p.402 in its page range.",0),
("cand-5317","France",106,106,"Reuse the existing France geographic-place candidate.",0),
("cand-10986","Italian Baroque artists",106,107,"An unnamed group described as Mazarin's intended imports.",0),
("cand-2189","Richelieu",107,107,"Reuse the Richelieu index candidate with p.402 in its page range.",0),
("cand-10987","finest examples of Italian Baroque art",107,107,"Unidentified group of works sought for France.",0),
("cand-4132","Italian Baroque art",107,107,"Second mention in the phrase about examples of Italian Baroque art.",0),
("cand-10992","Madeleine Laurain-Portemer",106,106,"Named author of the articles.",0),
("cand-10993","series of very fully documented articles",106,106,"Later scholarly article series described by Haskell.",0),
("cand-1588","the Cardinal",107,107,"Anaphoric reference to Cardinal Mazarin.",0),
("cand-10992","Mme .LaurainPortemer",107,107,"Second mention in the parenthetical evaluation; S0 OCR drops the printed hyphen and inserts a spurious period.",0),
("cand-1447","Louis XIV",107,107,"Reuse the Louis XIV index candidate with p.402 in its page range.",0),
("cand-3461","Italy",108,108,"Reuse the Italy place candidate.",0),
("cand-7098","Alazard",108,108,"Reuse the Jean Alazard candidate.",0),
("cand-10994","a picture commissioned",108,108,"The sentence continues on p.403; do not resolve commissioner or work identity.",0),
]
mids={r["mention_id"] for r in mentions};new_mentions=[]
for i,(cid,surface,first,last,note,occ) in enumerate(mention_specs,1):
    mid=f"m-chp20-p402-{i:03d}"
    if mid in mids:raise SystemExit(f"mention ID exists: {mid}")
    if cid not in cand or cand[cid]["status"]!="open":raise SystemExit(f"unavailable mention candidate {cid}")
    lo,hi=lineoff[first],lineoff[last]+len(lines[last-1]);pos=lo
    for _ in range(occ+1):
        pos=body.find(surface,pos,hi)
        if pos<0:raise SystemExit(f"surface absent L{first}-{last}: {surface!r}")
        pos+=len(surface)
    pos-=len(surface)
    new_mentions.append({"mention_id":mid,"segment_id":P402,"candidate_id":cid,"surface_form":surface,
        "start_char":str(pos),"end_char":str(pos+len(surface)),"note":note})
    mids.add(mid)

NOTE_LINES={1:235,2:235,3:236,4:236,5:237,6:237,7:238}
CH5="chp-5:05_CHP-5_sec_i:l125-147"
def make_statement(sid,first,last,subject,obj,predicate,claim,speaker,layer,qualification,ids,relation=False,notes=None,extra=None):
    q={"source_line_start":first,"source_line_end":last,"printed_page":402,"pdf_physical_page":11,
       "claim":claim,"speaker":speaker,"text_layer":layer,"qualification":qualification,
       "mentioned_candidate_ids":ids,"relation_candidate":relation}
    if notes:
        q.update({"footnote_markers":notes,"footnote_text_pending":True,"footnote_segment":NOTES,
          "footnote_refs":[{"marker":n,"segment_id":NOTES,"source_line":NOTE_LINES[n]} for n in notes],
          "footnote_statement_ids":[],"footnote_body_link_status":"pending"})
    if extra:q.update(extra)
    return {"statement_id":sid,"segment_id":P402,"subject_candidate_id":subject,"object_candidate_id":obj,
      "predicate":predicate,"qualifiers":q,"original_quote":"\n".join(lines[first-1:last]),
      "source_file":"02-sources/02-Markdown/20_CHP-20Postscript.md","origin":"book"}

new_statements=[
 make_statement("st-chp20-p402-christina-exhibition-materials",99,100,"cand-10977","cand-0675",
  "christina_patronage_material_assembled_at_1966_council_of_europe_exhibition",
  "Haskell says material on Queen Christina's life and artistic patronage in Rome was assembled at the Council of Europe exhibition in Stockholm in 1966; he identifies the catalogue and related material described in the source as 'a related volume or studies and documents' as essential starting points for further research.",
  "Haskell","authorial report on research resources",
  "The catalogue and related material are cited but not independently consulted; footnotes 1-2 remain pending. Both S0 and the scan appear to read 'volume or studies and documents'; retain the ambiguity pending a better copy.",
  ["cand-10977","cand-0675","cand-4490","cand-10978","cand-4790","cand-10979","cand-10980"],True,[1,2],
  {"cited_material_not_independently_consulted":True,
   "ocr_corrections":[{"source_line":99,"ocr":"Christinas","print":"Christina's","basis":"CHP-20Postscript.pdf physical page 11 image"}]}),
 make_statement("st-chp20-p402-previtali-bellori-edition",101,101,"cand-10982","cand-10981",
  "previtali_introduction_discusses_recent_bellori_research",
  "Haskell says important contributions to understanding Bellori are discussed in Giovanni Previtali's spirited and polemical introduction to a new critical edition of the Lives, and therefore are not mentioned in this passage.",
  "Haskell","authorial report of editorial coverage",
  "The edition is cited as Bellori 1976 in footnote 3; neither edition nor introduction is independently consulted here.",
  ["cand-0272","cand-10982","cand-10981"],True,[3],
  {"cited_material_not_independently_consulted":True}),
 make_statement("st-chp20-p402-turner-ferrante-carlo-bellori-lanfranco",102,102,"cand-10984","cand-10983",
  "turner_finds_bellori_lanfranco_comments_derived_from_ferrante_carlo",
  "Haskell reports Nicholas Turner's demonstration that some of Bellori's best-known critical comments on Lanfranco were very closely derived from Ferrante Carlo's writing; he says this showed he had not fully appreciated Carlo's significance when writing about him in chapter 5.",
  "Haskell reporting Nicholas Turner","authorial report of a scholarly source finding",
  "The derivation is reported through Turner, not independently checked. Footnote 4 remains pending; Ferrante Carlo's identity awaits S3.",
  ["cand-10984","cand-0272","cand-1359","cand-10983","cand-10985"],True,[4],
  {"cited_material_not_independently_consulted":True,
   "cross_reference_segments":[{"segment_id":CH5,"source_line_start":139,"source_line_end":140}]}),
 make_statement("st-chp20-p402-chapter7-scope",104,104,"cand-7272","cand-3462",
  "haskell_limits_chapter7_to_indications_for_future_survey",
  "Haskell describes the Italianisation of European culture in the seventeenth century as too vast a subject for comprehensive treatment and says he can offer only indications of material for a future general survey.",
  "Haskell","authorial statement of scope",
  "This records the author's stated scope, not a conclusion about the completeness of the existing scholarship.",
  ["cand-7272","cand-3462"],False,
  extra={"ocr_corrections":[{"source_line":104,"ocr":"concerned��the ��Italianisation��","print":"concerned—the 'Italianisation'","basis":"CHP-20Postscript.pdf physical page 11 image"}]}),
 make_statement("st-chp20-p402-perez-sanchez-spanish-patronage-catalogue",105,105,"cand-10989","cand-2500",
  "perez_sanchez_catalogue_and_documents_enable_study_of_spanish_patronage_of_italian_art",
  "Haskell says Perez Sanchez summarizes Spanish patronage of Italian Baroque art and that his catalogue of Italian seventeenth-century paintings in Spain, together with its documents and bibliography, makes a broader study possible by providing previously inaccessible information.",
  "Haskell reporting Perez Sanchez","authorial report on scholarship and research access",
  "The catalogue and cited materials have not been independently consulted; footnote 5 remains pending.",
  ["cand-10988","cand-10989","cand-2500","cand-4132","cand-5120"],True,[5],
  {"cited_material_not_independently_consulted":True,
   "ocr_corrections":[{"source_line":237,"ocr":"6 Perez Sanchez","print":"5 Perez Sanchez","basis":"CHP-20Postscript.pdf physical page 11 image"}]}),
 make_statement("st-chp20-p402-wethey-naples-viceroy-information",105,105,"cand-10990","cand-6624",
  "wethey_published_information_about_individual_viceroys_in_naples",
  "Haskell says Wethey has published notable information about individual Viceroys in Naples.",
  "Haskell","authorial report of scholarship",
  "The source names no individual viceroys; footnote 6 is linked to the queued notes segment and remains pending.",
  ["cand-10990","cand-6624","cand-3534"],True,[6],
  {"cited_material_not_independently_consulted":True}),
 make_statement("st-chp20-p402-mazarin-art-policy-in-france",106,107,"cand-1588","cand-5317",
  "mazarin_introduced_italian_baroque_artists_or_works_to_france_under_richelieu_and_his_own_power",
  "Haskell describes Mazarin as the most enterprising patron and collector of Italian art in France; reporting Laurain-Portemer's articles, he says Mazarin was determined to introduce Italian Baroque artists or the finest Italian Baroque art under Richelieu and later when he held supreme power.",
  "Haskell reporting Madeleine Laurain-Portemer","authorial synthesis of later scholarship",
  "Keep the two political periods distinct and the works/artists unnamed. Footnote 7 remains pending; the articles were not independently consulted.",
  ["cand-1588","cand-5317","cand-2189","cand-10986","cand-10987","cand-10992","cand-10993","cand-4132"],True,[7],
  {"cited_material_not_independently_consulted":True}),
 make_statement("st-chp20-p402-laurain-portemer-broadens-mazarin-interpretation",107,107,"cand-10993","cand-1588",
  "laurain_portemer_articles_support_mazarin_taste_but_show_wider_policy_than_personal_hedonism",
  "Haskell says Laurain-Portemer's articles endorse his view of Mazarin's individual taste but show that Mazarin's artistic policy had wider ends than the personal hedonism to which Haskell says he had implicitly attributed his ambitions.",
  "Haskell reporting Laurain-Portemer","authorial comparison with later scholarship",
  "The claim about wider ends is attributed to the articles; the phrase 'by implication' remains part of Haskell's self-qualification. Footnote 7 remains pending.",
  ["cand-10992","cand-10993","cand-1588"],True,[7],
  {"cited_material_not_independently_consulted":True,
   "ocr_corrections":[{"source_line":107,"ocr":"Mme .Laurain-Portemer","print":"Mme Laurain-Portemer","basis":"CHP-20Postscript.pdf physical page 11 image"}]}),
 make_statement("st-chp20-p402-louisxiv-alazard-commissioned-picture-open",107,108,"cand-1447","cand-10994",
  "haskell_says_young_louis_xiv_looked_to_italy_and_begins_alazard_picture_reference",
  "Haskell says the young Louis XIV continued to look to Italy for artistic talent and begins to refer to Alazard's account of a commissioned picture.",
  "Haskell","authorial report with sentence continuing across pages",
  "The sentence stops at 'commissioned'. The picture, commissioner, and full point of the Alazard reference remain unresolved until p.403 is read.",
  ["cand-1447","cand-3461","cand-7098","cand-10994"],False,
  extra={"open_across_segment":True,"continues_in_segment":P403,
         "cross_reference_segments":[{"segment_id":P403,"source_line_start":110,"source_line_end":121}]})
]
existing_sids={r["statement_id"] for r in statements}
for r in new_statements:
    if r["statement_id"] in existing_sids:raise SystemExit(f"statement exists: {r['statement_id']}")
    existing_sids.add(r["statement_id"])
    if r["original_quote"] not in body:raise SystemExit(f"quote absent from p.402: {r['statement_id']}")
    for cid in r["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in cand or cand[cid]["status"]!="open":raise SystemExit(f"statement candidate unavailable: {cid}")
spans=sorted((int(r["start_char"]),int(r["end_char"]),r["mention_id"]) for r in [*mentions,*new_mentions] if r["segment_id"]==P402)
for i,a in enumerate(spans):
    for b in spans[i+1:]:
        if b[0]>=a[1]:break
        nested=(a[0]<=b[0] and b[1]<=a[1]) or (b[0]<=a[0] and a[1]<=b[1])
        if a[:2]==b[:2] or not nested:raise SystemExit(f"crossing/duplicate mention spans: {a[2]} / {b[2]}")
cov[P402]["disposition"]="reviewed";cov[P402]["migration_status"]="partial";cov[P402]["source_line_ranges"]="L99-108"
cov[P402]["note"]="Printed p.402 (PDF physical page 11) visually checked. Records Queen Christina resources, Bellori/Previtali and Turner updates, chapter 7 scope, Spanish patronage, Mazarin and Laurain-Portemer; the Louis XIV/Alazard commissioned-picture sentence continues on p.403. Footnotes 1-7 link to queued notes L235-238."
paths=[T/"entity-candidates.csv",T/"mentions.csv",sp,T/"s2-coverage.csv"]
backups=[p.with_name(p.name+BACKUP) for p in paths]
if args.apply:
    if any(p.exists() for p in backups):raise SystemExit("p.402 recovery backup already exists")
    for p,b in zip(paths,backups):shutil.copy2(p,b)
    wc(paths[0],cp,candidates);wc(paths[1],mp,[*mentions,*new_mentions]);wj(sp,[*statements,*new_statements]);wc(paths[3],vp,coverage)
    print(f"applied p.402 S2 migration; backup suffix {BACKUP}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("source/PDF/S0 hashes, exact anchors, footnote links, and the p.403 continuation validated")
