"""Controlled S2 migration for p.283; dry-run unless --apply is passed."""
import csv, hashlib, json, re, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
T = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
PREV = "chp-10:10_CHP-10_intro:l141-149"
SEG = "chp-10:10_CHP-10_intro:l151-165"
NEXT = "chp-10:10_CHP-10_intro:l167-176"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "fe70838d7bc6f4712b673c0589cccd39b21644c66c43030ce002057fc126a7c6"
MAX_CAND = 8951
BACKUP = ".bak-s2-chp10-p283-reapply-20261002"

def read_csv(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f); return r.fieldnames, list(r)

def read_jsonl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8-sig").splitlines() if x.strip()]

def write_csv(p, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=p.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader(); w.writerows(rows); tmp = Path(f.name)
    tmp.replace(p)

def write_jsonl(p, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=p.parent, delete=False) as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(p)

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(src[150:165])
if hashlib.sha256(body.encode()).hexdigest() != SEG_SHA or src[150].strip() != "[Page 283]":
    raise SystemExit("p.283 source segment hash/page mismatch")
if "but employment under him" not in src[162] or not src[163].startswith("MSS. 1383"):
    raise SystemExit("expected p.283 open body / p.282 note continuation changed")

cp, mp, sp, vp = [T / x for x in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp); mf, mentions = read_csv(mp); vf, coverage = read_csv(vp); statements = read_jsonl(sp)
cids = {r["candidate_id"] for r in candidates}; mids = {r["mention_id"] for r in mentions}
sids = {r["statement_id"] for r in statements}; cov = {r["segment_id"]: r for r in coverage}
max_id = max(int(re.search(r"\d+", r["candidate_id"]).group()) for r in candidates)
if max_id != MAX_CAND: raise SystemExit(f"candidate sequence changed: {max_id}")
for sid, expected in ((PREV,("reviewed","partial")),(SEG,("queued","pending")),(NEXT,("queued","pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"],row["migration_status"]) != expected: raise SystemExit(f"coverage changed: {sid} {row}")
for mid in ("m-chp10-p282-trevisani_footer","m-chp10-p282-balestra_footer"):
    if mid not in mids: raise SystemExit(f"p.282 footer mention is missing: {mid}")

E = {"johann":"cand-1325","holland":"cand-6084","weenix":"cand-2807","werff":"cand-2808",
"dusseldorf":"cand-0955","flanders":"cand-4652","van_dyck":"cand-0958","rubens":"cand-2293",
"rapparini":"cand-2107","munich":"cand-7155","venice":"cand-3401","pellegrini":"cand-1862",
"pollnitz":"cand-1969","palatinate":"cand-3947","raphael":"cand-2098","veronese":"cand-2755",
"titian":"cand-2630","carracci":"cand-4318","correggio":"cand-0852","reni":"cand-2124",
"rembrandt":"cand-2117","rome":"cand-4490","florence":"cand-3397","phaeton":"cand-1864",
"bellucci":"cand-0282","foggini":"cand-1043","soldani":"cand-2479","augusta":"cand-3531",
"trevisani":"cand-2650","balestra":"cand-0168","trevisani_ms":"cand-3533","balestra_ms":"cand-7767"}
for key, val in E.items():
    if val not in cids: raise SystemExit(f"required candidate missing: {key}={val}")

NEW_SPECS = [
 ("museum","Alte Pinakothek, Munich","institution","Haskell says the Van Dyck and Rubens paintings were among its treasures at the time of writing; no individual works are identified.",153),
 ("castle","Elector's castle at Bensburg (as printed on p.283)","place","Source-bounded location for Pellegrini's staircase fresco; printed spelling retained pending identity alignment.",160),
 ("pellegrini_series","Allegorical canvases depicting the benefits of Johann Wilhelm's rule (Pellegrini series; Plate 49a)","work","Collective series described by Haskell; individual canvas titles are not supplied.",161),
 ("bellucci_group","Unspecified allegories and group portraits celebrating Johann Wilhelm by Antonio Bellucci", "work","Collective works described by Haskell; individual titles and count are not supplied.",163),
 ("lankheit_article","K. Lankheit, 'Florentiner Bronze-arbeiten für Kurfürst Johann Wilhelm von der Pfalz' (1956)","archive","Matched to the book bibliography at 21_CHP-21Bibliography.md L662-663 by title, year, and pp.185-210; cited work not independently read.",165),
]
newc=[]; C={}
for i,(key,name,kind,detail,line) in enumerate(NEW_SPECS,MAX_CAND+1):
    cid=f"cand-{i:04d}"
    if cid in cids or any(r["canonical_name"]==name and r["suggested_type"]==kind for r in candidates): raise SystemExit(f"candidate exists: {cid} {name}")
    C[key]=cid
    newc.append({"candidate_id":cid,"index_entry_id":"","canonical_name":name,"index_page_range":"","suggested_type":kind,
      "status":"open","index_source_file":"","sub_entry":"","detail":detail,"exclude_reason":"","candidate_origin":"body-mention",
      "candidate_source_ref":f"{SEG}#L{line}"})

offsets={}; offset=0
for n in range(151,166): offsets[n]=offset; offset+=len(src[n-1])+1
newm=[]
def m(local,line,surface,key,note,occ=0,new=False):
    mid=f"m-chp10-p283-{local}"; cid=C[key] if new else E[key]
    if mid in mids or any(x["mention_id"]==mid for x in newm) or cid not in (cids|set(C.values())): raise SystemExit(f"duplicate/missing mention {mid}->{cid}")
    positions=[]; at=0
    while True:
        at=src[line-1].find(surface,at)
        if at<0: break
        positions.append(at); at+=1
    if occ>=len(positions): raise SystemExit(f"surface absent L{line}: {surface!r}")
    a=offsets[line]+positions[occ]; b=a+len(surface)
    if body[a:b]!=surface: raise SystemExit(f"span mismatch {mid}")
    newm.append({"mention_id":mid,"segment_id":SEG,"candidate_id":cid,"surface_form":surface,"start_char":str(a),"end_char":str(b),"note":note})

MENTIONS=[
 ("johann_dutch",152,"He","johann","Pronoun refers to Johann Wilhelm."),("holland",152,"Holland","holland","Place visited in 1696."),
 ("weenix",153,"Jan Weenix","weenix","Dutch artist whose works Johann Wilhelm collected."),("werff",153,"Adrian van der Werff","werff","Dutch artist and court-painter invitee."),
 ("weenix_invited",153,"Weenix","weenix","Surname reference to Jan Weenix."),("werff_invited",153,"Van det Werff","werff","OCR reads det; print reads der."),
 ("johann_invited",153,"him","johann","Refers to Johann Wilhelm."),("dusseldorf",153,"Düsseldorf","dusseldorf","Destination for the artists."),
 ("werff_latter",153,"the latter","werff","Refers to Adrian van der Werff."),("werff_he",153,"he","werff","Refers to Adrian van der Werff."),
 ("elector",153,"the Elector","johann","Johann Wilhelm."),("werff_his",153,"his","werff","Refers to van der Werff's paintings."),
 ("johann_gallery",153,"Johann Wilhelm’s","johann","Owner associated with the gallery."),("johann_for_gallery",153,"Johann Wilhelm","johann","Collector in Rapparini's quoted claim."),
 ("flandre",153,"Flandre","flanders","French form of Flanders in a nested quotation."),("hollande",153,"Hollande","holland","French form of Holland in a nested quotation."),
 ("van_dyck_count",153,"Van Dyck","van_dyck","Seventeen paintings attributed to Van Dyck."),("rubens_count",153,"Rubens","rubens","Forty paintings attributed to Rubens."),
 ("museum",153,"Alte Pinakothek","museum","Named museum holding the paintings at the time of Haskell's writing.",0,True),("munich",153,"Munich","munich","Location of the Alte Pinakothek."),
 ("rapparini_claim",153,"Rapparini’s","rapparini","Refers to Rapparini's claims about the gallery."),
 ("venetian_city",154,"that city","venice","Anaphoric reference to Venice."),
 ("pellegrini_effect",155,"Pellegrini","pellegrini","Artist whose response to the two painters is assessed."),
 ("johann_death",156,"the Elector’s","johann","Johann Wilhelm; the source gives his death year as 1716."),("pollnitz",156,"Baron de Pöllnitz","pollnitz","Visitor and source of the nested praise."),
 ("palatinate",156,"the Palatinate","palatinate","Region through which Pöllnitz passed."),("gallery_rubens_1",157,"Rubens","rubens","First room's focus."),
 ("gallery_vandyck",157,"Van Dyck","van_dyck","Named in the second room's holdings."),("gallery_werff",157,"Van der Werff","werff","Named as focus of the fourth room."),
 ("raphael",157,"Raphael","raphael","Named among old masters in the fifth room."),("veronese",158,"Veronese","veronese","Named among old masters in the fifth room."),
 ("titian",158,"Titian","titian","Named among old masters in the fifth room."),("carracci",158,"Carracci","carracci","Collective Carracci reference in the fifth-room list."),
 ("correggio",158,"Correggio","correggio","Named among old masters in the fifth room."),("reni",158,"Guido Reni","reni","Named among old masters in the fifth room."),
 ("rubens_2",158,"Rubens","rubens","Named among old masters in the fifth-room list."),("rembrandt",158,"Rembrandt","rembrandt","Named among old masters in the fifth room."),
 ("florence",159,"Florence","florence","Place whose principal sculptures were represented by casts."),("rome",159,"Rome","rome","Place whose principal sculptures were represented by casts."),
 ("pellegrini_three_years",160,"Pellegrini","pellegrini","Artist employed for three years."),("castle",160,"Bensburg","castle","Printed place spelling; identity remains open.",0,True),
 ("fall_phaethon",160,"Fall of Phaethon","phaeton","Fresco subject; index sub-entry spells Phaeton.",0,False),("elector_rule",161,"the Elector’s","johann","Refers to Johann Wilhelm."),
 ("johann_rule_first",161,"Johann","johann","First part of the name at a source-line break."),("johann_rule_second",162,"Wilhelm’s","johann","Continuation of the name across the source-line break."),
 ("canvases",161,"a series of canvases","pellegrini_series","Unspecified allegorical series depicting benefits of Johann Wilhelm's rule.",0,True),
 ("plate49a",162,"Plate 49a","pellegrini_series","Cross-reference to the illustrated series.",0,True),("pellegrini_gallery",162,"Pellegrini","pellegrini","Haskell discusses possible influence of the collection on the painter."),
 ("elector_gallery",163,"Elector’s","johann","Continuation of the source-line break 'the / Elector’s'; refers to Johann Wilhelm's gallery."),("bellucci",163,"Bellucci","bellucci","Artist described as celebrating Johann Wilhelm."),
 ("german_patron",163,"his German patron","johann","Refers to Johann Wilhelm."),("pellegrini_compare",163,"Pellegrini’s","pellegrini","Comparison with Bellucci's works."),
 ("bellucci_works",163,"allegories and group portraits","bellucci_group","Collective works; no individual titles or count are supplied.",0,True),
 ("augusta",163,"Bibhoteca Augusta","augusta","OCR spelling of the repository named in the continuation of p.282's unnumbered note."),
 ("trevisani_ms",164,"MSS. 1383","trevisani_ms","Shared manuscript locator for the two artist lives; the statement records the second source candidate too.",0,False),
 ("foggini",165,"Foggini","foggini","Named in an unnumbered bibliographic locator, not migrated as independent evidence."),
 ("soldani",165,"Soldani","soldani","Named in an unnumbered bibliographic locator, not migrated as independent evidence."),
 ("johann_sculptors",165,"Johann Wilhelm","johann","Person named in the bibliographic locator."),
 ("lankheit",165,"Lankheit, 1956","lankheit_article","Bibliographic source matched to the book's bibliography at L662-663.",0,True),
]
for row in MENTIONS: m(*row)

def q(text, first, last):
    a=text.find(first)
    if a<0: raise SystemExit(f"quote start missing: {first!r}")
    b=text.find(last,a)
    if b<0: raise SystemExit(f"quote end missing: {last!r}")
    return text[a:b+len(last)]

new_s=[]
def add_statement(sid,segment,ls,le,sub,obj,pred,first,last,claim,qualification,refs=(),relation=False,
                  foot=None,speaker="Haskell",layer="authorial narrative",ocr=(),cross=(),source_text=body):
    if sid in sids or any(r["statement_id"]==sid for r in new_s): raise SystemExit(f"duplicate statement: {sid}")
    linked=set(refs)|{x for x in (sub,obj) if x}
    known=cids|set(C.values())
    if not linked<=known: raise SystemExit(f"missing statement candidate: {sid} {linked-known}")
    qual={"source_line_start":ls,"source_line_end":le,"printed_page":282 if segment==PREV else 283,
          "pdf_physical_page":11 if segment==PREV else 12,"claim":claim,"speaker":speaker,"text_layer":layer,
          "qualification":qualification,"mentioned_candidate_ids":sorted(linked)}
    if relation: qual["relation_candidate"]=True
    if foot is not None: qual.update({"footnote_marker":foot,"footnote_text_pending":True,"footnote_link_status":"pending_source_migration"})
    if cross: qual["cross_reference_segments"]=cross
    if ocr: qual["ocr_corrections"]=[{"source_file":SOURCE_FILE,"source_line":ln,"ocr":raw,"print":printed,"basis":"CHP-10.pdf physical page 12."} for ln,raw,printed in ocr]
    new_s.append({"statement_id":sid,"segment_id":segment,"subject_candidate_id":sub,"object_candidate_id":obj,
       "predicate":pred,"qualifiers":qual,"original_quote":q(source_text,first,last),"source_file":SOURCE_FILE,"origin":"book"})

# Close the unnamed, unnumbered footnote fragment begun at p.282 L149.
footer_quote=src[148].strip()
footer_cont=src[162].split("but ",1)[1] + "\n" + src[163].strip()
footer_mentions=["cand-1325","cand-2650","cand-0168","cand-3531","cand-3533","cand-7767"]
for sid,sub,pred,claim in [
 ("st-chp10-p282-trevisani-refused-regular-employment","cand-2650","trevisani_refused_regular_employment_under_johann_wilhelm","Haskell's unnumbered note says Francesco Trevisani refused regular employment under Johann Wilhelm and points to a manuscript life."),
 ("st-chp10-p282-balestra-refused-regular-employment","cand-0168","balestra_refused_regular_employment_under_johann_wilhelm","Haskell's unnumbered note says Antonio Balestra refused regular employment under Johann Wilhelm and points to a manuscript life.")]:
 if sid in sids: raise SystemExit(f"footer statement already exists: {sid}")
 new_s.append({"statement_id":sid,"segment_id":PREV,"subject_candidate_id":sub,"object_candidate_id":"cand-1325","predicate":pred,
  "qualifiers":{"source_line_start":149,"source_line_end":149,"printed_page":282,"pdf_physical_page":11,"claim":claim,
   "speaker":"Haskell's footnote","text_layer":"cross-page footnote continuation","qualification":"The printed fragment continues at p.283 L164. No footnote number is visible; the two named artists and citation are kept distinct.",
   "footnote_marker_status":"unidentified","mentioned_candidate_ids":footer_mentions,"relation_candidate":True,
   "ocr_corrections":[{"source_file":SOURCE_FILE,"source_line":163,"ocr":"Eves","print":"lives","basis":"CHP-10.pdf physical page 12."},
    {"source_file":SOURCE_FILE,"source_line":163,"ocr":"Bibhoteca","print":"Biblioteca","basis":"CHP-10.pdf physical page 12."}],
   "continuation_quote":footer_cont,"continuation_source_segment_id":SEG,
   "cross_reference_segments":[{"segment_id":SEG,"source_line_start":163,"source_line_end":164}]},
  "original_quote":footer_quote,"source_file":SOURCE_FILE,"origin":"book"})

add_statement("st-chp10-p283-wilhelm-dutch-collecting",SEG,152,153,E["johann"],None,"wilhelm_visited_holland_and_collected_dutch_paintings",
 "He was just as enthusiastic","many others.","Haskell says Johann Wilhelm was enthusiastic about Dutch art, visited Holland in 1696, and avidly collected works by Jan Weenix, Adrian van der Werff and other artists.",
 "The unnamed 'many others' are not expanded.",[E["holland"],E["weenix"],E["werff"]],True)
add_statement("st-chp10-p283-weenix-werff-invited",SEG,153,153,E["johann"],E["weenix"],"wilhelm_invited_weenix_and_van_der_werff_to_dusseldorf",
 "Both Weenix and Van det Werff","to Düsseldorf,","Haskell says Johann Wilhelm invited Jan Weenix and Adrian van der Werff to Düsseldorf.",
 "OCR 'det' is corrected to printed 'der'; the invitation does not establish that Weenix accepted.",[E["werff"],E["dusseldorf"]],True,ocr=[(153,"Van det Werff","Van der Werff")])
add_statement("st-chp10-p283-werff-refused-office-agreed-exclusive-work",SEG,153,153,E["werff"],E["johann"],"van_der_werff_declined_court_post_but_agreed_exclusive_seasonal_work",
 "though the latter refused","six months in every year,","Haskell says van der Werff declined an official court-painter post but agreed to work exclusively for Johann Wilhelm six months each year.",
 "The source does not state whether this arrangement was completed in every year.",[E["dusseldorf"]],True)
add_statement("st-chp10-p283-werff-paintings-entered-gallery",SEG,153,153,E["werff"],E["johann"],"many_van_der_werff_paintings_entered_wilhelms_gallery",
 "and large numbers of his smooth","Johann Wilhelm’s gallery.","Haskell says many of van der Werff's smooth, light, enamelled paintings entered Johann Wilhelm's gallery.",
 "The aesthetic description is nested and its quoted speaker is not identified.",speaker="Haskell with an unattributed nested quotation",layer="authorial report with nested quotation")
add_statement("st-chp10-p283-wilhelm-flanders-holland-collection",SEG,153,153,E["johann"],C["museum"],"wilhelm_gallery_included_large_van_dyck_and_rubens_holdings_now_at_alte_pinakothek",
 "For it Johann Wilhelm had","not excessively exaggerated.","Haskell says Johann Wilhelm's gallery contained works amassed from Flanders and Holland, including seventeen paintings by Van Dyck and forty by Rubens, which he says were then among the treasures of the Alte Pinakothek in Munich; this, he argues, shows Rapparini's claims were not excessively exaggerated.",
 "The collection counts and museum location are reported at the time of the book; Rapparini's quoted claim is not treated as a catalogue inventory.",[E["flanders"],E["holland"],E["van_dyck"],E["rubens"],E["munich"],E["rapparini"]],True)
add_statement("st-chp10-p283-venetian-influence-on-pellegrini",SEG,153,155,E["pellegrini"],None,"van_dyck_and_rubens_owed_debt_to_venetian_painting_and_affected_pellegrini",
 "Despite the debt that both artists owed to","Pellegrini was considerable.","Haskell says Van Dyck and Rubens owed a debt to Venetian painting, were little known in Venice, and had a considerable effect on the receptive Pellegrini.",
 "This is Haskell's art-historical assessment; 'both artists' means Van Dyck and Rubens.",[E["van_dyck"],E["rubens"],E["venice"]])
add_statement("st-chp10-p283-pollnitz-praise",SEG,156,157,E["pollnitz"],E["johann"],"pollnitz_described_wilhelms_achievements_and_praised_his_rule",
 "Some sixteen years after the Elector’s death","Tamour de ses Sujets.’1","Haskell says Baron de Pöllnitz passed through the Palatinate some sixteen years after Johann Wilhelm's death in 1716 and quotes his praise of the Elector.",
 "Retain the approximate interval, nested attribution, and Pöllnitz's French wording; note 1 remains pending the consolidated notes segment.",[E["palatinate"]],True,1,"Baron de Pöllnitz, quoted by Haskell","nested quotation",[(156,"Aencreux","généreux"),(157,"Tamour","l’amour")])
add_statement("st-chp10-p283-five-room-gallery",SEG,157,158,E["johann"],None,"wilhelm_gallery_arranged_flemish_dutch_and_italian_paintings_in_five_rooms",
 "The gallery consisted of five great rooms","Rubens and Rembrandt.","Haskell describes a five-room gallery: one room for Rubens; a second for Van Dyck and other Flemish and Dutch artists; a third for Italian paintings; a fourth for van der Werff; and a fifth for major Flemish, Dutch and Italian masters including Raphael, Veronese, Titian, Carracci, Correggio, Guido Reni, Rubens and Rembrandt.",
 "The source gives room contents, not a complete catalogue; the fifth-room list repeats Rubens.",[E["rubens"],E["van_dyck"],E["werff"],E["raphael"],E["veronese"],E["titian"],E["carracci"],E["correggio"],E["reni"],E["rembrandt"]])
add_statement("st-chp10-p283-sculpture-casts-in-gallery",SEG,159,159,E["johann"],None,"wilhelm_gallery_displayed_bronzes_miniature_cabinets_and_sculpture_casts",
 "In all the rooms were displayed","Florence and Rome.","Haskell says the rooms displayed bronzes and cabinets of miniatures, with another gallery below containing casts of principal sculptures in Florence and Rome.",
 "The sculptural originals and individual bronzes are not identified.",[E["florence"],E["rome"]])
add_statement("st-chp10-p283-pellegrini-fall-of-phaethon",SEG,160,160,E["pellegrini"],C["castle"],"pellegrini_painted_fall_of_phaethon_fresco_at_bensburg_castle",
 "In this exhilarating atmosphere Pellegrini worked for three years","strength of drawing.","Haskell says Pellegrini worked for Johann Wilhelm for three years and painted a large staircase-ceiling fresco of the Fall of Phaethon at the Elector's castle at Bensburg.",
 "The printed place spelling is Bensburg; the location's modern identity remains for S3. Note 2 is pending the consolidated notes segment.",[E["johann"],E["phaeton"]],True,2)
add_statement("st-chp10-p283-pellegrini-allegorical-benefits-series",SEG,161,162,E["pellegrini"],C["pellegrini_series"],"pellegrini_painted_allegorical_series_on_benefits_of_wilhelms_rule",
 "But, above all, he was called upon","Plate 49a).","Haskell says Pellegrini was asked to glorify the Elector and painted a series of canvases allegorically depicting the benefits of Johann Wilhelm's rule.",
 "The series is collectively identified and cross-referenced to Plate 49a; no individual canvas titles are supplied.",[E["johann"]],True)
add_statement("st-chp10-p283-pellegrini-gallery-influence-and-style",SEG,162,163,E["pellegrini"],None,"wilhelm_gallery_may_have_shaped_pellegrini_style_and_haskell_praised_its_colour",
 "There is a certain awkwardness","at this date.","Haskell says awkwardness and stylistic mixture in some canvases may reflect the Elector's varied gallery, especially its Flemish artists, while praising the paintings' freshness, buoyancy and delicate colour as unmatched in Venice at that date.",
 "Preserve 'may reflect' as a qualified interpretation and the comparison as Haskell's judgment.",[E["johann"],E["venice"]])
add_statement("st-chp10-p283-bellucci-celebrated-wilhelm-open",SEG,163,163,E["bellucci"],C["bellucci_group"],"bellucci_painted_allegories_and_group_portraits_for_wilhelm_open_sentence",
 "Bellucci, too, celebrated his German patron","but","Haskell says Bellucci celebrated Johann Wilhelm with allegories and group portraits, judged more clumsy than Pellegrini's; the sentence continues on p.284.",
 "This is Haskell's comparative evaluation; read the continuation before closing the statement.",[E["johann"],E["pellegrini"]],True,
 cross=[{"segment_id":NEXT,"source_line_start":167,"source_line_end":176}])
add_statement("st-chp10-p283-lankheit-citation-locator",SEG,165,165,None,C["lankheit_article"],"footnote_citation",
 "For a long and fully documented account","pp. 185-210.","The unnumbered p.283 note directs readers to Lankheit's 1956 article, pages 185–210, for a documented account of Florentine sculptors' work for Johann Wilhelm.",
 "Citation locator only; the cited article is matched to the book bibliography at L662–663 but was not independently read.",[E["foggini"],E["soldani"],E["johann"]],speaker="book footnote",layer="bibliographic citation locator")

# The p.282 note fragment is now complete across the page break.
cov[PREV]["migration_status"]="complete"
old_note=cov[PREV]["note"]
old_note=old_note.replace("L149 is an unnumbered footer fragment ending 'refused regular'; its continuation and note identity are unresolved, so coverage remains partial.",
 "L149's unnumbered footer fragment ending 'refused regular' continues at p.283 L163-164 ('employment under him'); both artist-specific refusal statements are now recorded with the cross-page span. The footnote number remains unidentified.")
if old_note==cov[PREV]["note"]: raise SystemExit("could not update p.282 unresolved-fragment note")
cov[PREV]["note"]=old_note
cov[SEG].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L152-165",
 "note":"Printed p.283 body and footer read against CHP-10.pdf physical page 12. Recorded Johann Wilhelm's Dutch collecting and 1696 Holland visit; the Weenix/van der Werff invitations, van der Werff's declined court post and exclusive six-month arrangement; Flemish/Dutch collection and Van Dyck/Rubens holdings; Pöllnitz's nested praise; the five-room gallery and sculpture casts; Pellegrini's Bensburg fresco and allegorical series, Haskell's qualified style judgments, and Bellucci's open-ended comparison. Corrected only in S2 against print: L153 'Van det Werff'->'Van der Werff'; L156 'Aencreux'->'généreux'; L157 'Tamour'->'l’amour'; L163 'Eves'->'lives', 'Bibhoteca'->'Biblioteca'; S0 unchanged. The p.282 L149 footnote continuation occupies the footnote text at p.283 L163-164; p.283 notes 1-2 at consolidated source L523 remain pending. L165 is an unnumbered Lankheit citation locator matched to bibliography L662-663, not independent factual evidence. The main-text sentence at L163 ends 'but' and continues at p.284 L167, so coverage remains partial."})
cov[NEXT]["note"]="Next source-order body segment is printed p.284 at L167; read to close the p.283 Bellucci sentence before marking p.283 complete."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:]==["--apply"] else "DRY-RUN","segment":SEG,
 "new_candidates":len(newc),"new_mentions":len(newm),"new_statements":len(new_s),
 "candidate_range":[newc[0]["candidate_id"],newc[-1]["candidate_id"]],"p282_fragment_closed":True,
 "coverage":{"p282":cov[PREV]["migration_status"],"p283":cov[SEG]["migration_status"],"p284":cov[NEXT]["migration_status"]}},ensure_ascii=False,indent=2))
if sys.argv[-1:]==["--apply"]:
    for p in (cp,mp,sp,vp):
        b=Path(str(p)+BACKUP)
        if b.exists(): raise SystemExit(f"backup already exists: {b}")
        shutil.copy2(p,b)
    write_csv(cp,cf,candidates+newc); write_csv(mp,mf,mentions+newm); write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[r["segment_id"]] for r in coverage])
    print("Applied p.283 S2 migration and closed p.282 footer; backups retained.")
