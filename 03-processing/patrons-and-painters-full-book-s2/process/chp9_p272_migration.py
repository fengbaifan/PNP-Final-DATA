"""Controlled S2 migration for printed p.272 body; defaults to dry-run."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, shutil, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
SEGMENT = "chp-9:09_CHP-9_sec_ii:l53-60"
PREVIOUS = "chp-9:09_CHP-9_sec_ii:l38-51"
NEXT = "chp-9:09_CHP-9_sec_ii:l62-68"
PREVIOUS_STMT = "st-chp9-p271-hostile-pamphlet-introduction-partial"
ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
SEGMENT_SHA = "e3d0127b7c4570ec1a149a6b7a32502fec7af85a366dbd06f2e81be679f5bb17"
MAX_CANDIDATE = 8721
BACKUP_SUFFIX = ".bak-s2-chp9-p272-20261001"

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)

def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]

def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader(); w.writerows(rows); tmp = Path(f.name)
    tmp.replace(path)

def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)

raw = SOURCE.read_bytes()
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(raw).hexdigest() != ASSET_SHA:
    raise SystemExit("section-II source asset has changed")
segments = {x["segment_id"]: x for x in read_jsonl(TABLES / "segments.jsonl")}
if segments.get(SEGMENT, {}).get("sha256") != SEGMENT_SHA or segments[SEGMENT].get("asset_sha256") != ASSET_SHA:
    raise SystemExit("p.272 source segment missing or changed")
if NEXT not in segments or not lines[53].startswith("a hostile pamphlet") or not lines[57].startswith("This was true enough"):
    raise SystemExit("expected p.272 source text/continuation has changed")
segment_text = "\n".join(lines[52:60])
offsets, offset = {}, 0
for n in range(53, 61):
    offsets[n] = offset
    offset += len(lines[n-1]) + 1

cp = TABLES / "entity-candidates.csv"
mp = TABLES / "mentions.csv"
sp = TABLES / "book-statements.jsonl"
vp = TABLES / "s2-coverage.csv"
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
statements = read_jsonl(sp)
vf, coverage = read_csv(vp)
candidate_ids = {x["candidate_id"] for x in candidates}
mention_ids = {x["mention_id"] for x in mentions}
statement_ids = {x["statement_id"] for x in statements}
cov = {x["segment_id"]: x for x in coverage}
maximum = max(int(re.search(r"\d+", x["candidate_id"]).group()) for x in candidates)
if maximum != MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {MAX_CANDIDATE}, found {maximum}")
if (cov.get(PREVIOUS, {}).get("disposition"), cov.get(PREVIOUS, {}).get("migration_status")) != ("reviewed", "partial"):
    raise SystemExit("p.271 is not in expected reviewed/partial state")
if (cov.get(SEGMENT, {}).get("disposition"), cov.get(SEGMENT, {}).get("migration_status")) != ("queued", "pending"):
    raise SystemExit("p.272 is not queued/pending")
prev_stmt = next((x for x in statements if x["statement_id"] == PREVIOUS_STMT), None)
if not prev_stmt or prev_stmt["segment_id"] != PREVIOUS:
    raise SystemExit("p.271 unfinished statement is missing")

E = {
    "venice":"cand-2724", "jesuits":"cand-1322", "jesuit_church":"cand-0734",
    "fontebasso":"cand-1047", "three_angels":"cand-1049", "elijah":"cand-1048",
    "carmelites":"cand-0563", "religious_orders":"cand-8675", "dominicans":"cand-0941",
    "dominican_church":"cand-0737", "st_dominic":"cand-8713", "dominican_ceiling":"cand-2605",
    "pieta_church":"cand-8551", "doge_grimani":"cand-1234", "senate":"cand-8129",
    "massari":"cand-1562", "palladian":"cand-8699", "tiepolo":"cand-2569",
}
for k, v in E.items():
    if v not in candidate_ids: raise SystemExit(f"required candidate missing: {k}={v}")

SPECS = [
 ("pamphlet","Hostile pamphlet about Jesuit church expenditure (title pending p.272 note 1 migration)","archive","Unidentified pamphlet cited for a hostile claim that the Jesuits extracted the expense of their magnificent church from a single family. Exact title and edition await the consolidated notes segment.",54),
 ("assumption","Assumption of the Virgin as the dedication of S. Maria Assunta","term","Religious dedication named by Haskell for the Jesuit church; not an artwork.",54),
 ("jesuit_iconography","Jesuit iconography in the Venetian church comparison","term","Iconographic category explicitly named by Haskell.",55),
 ("jesuit_altarpieces","One or two unidentified Jesuit-saint altarpieces in S. Maria Assunta","work","Haskell supplies a range, not an exact number, title or artist.",55),
 ("dominican_ensemble","Painting ensemble in S. Maria del Rosario described as celebrating the Dominican Order","work","Collective description only; not an exhaustive catalogue of individual paintings.",55),
 ("refuge","Unnamed refuge for exposed children and orphans at the Pietà site","institution","Fourteenth-century refuge in Haskell's account; no formal name is supplied.",56),
 ("doge_office","Doge of Venice as an institutional office in the Pietà refuge account","institution","Generic office named as patron; distinct from the later named Doge Grimani.",56),
 ("gazzetta","Gazzetta Veneta (periodical cited for the Pietà church description in 1760)","archive","Periodical named by Haskell; issue and page are not supplied.",57),
 ("governors","Governors of the Pietà church project in Venice (as named by Haskell)","institution","Governing body said to have access to leading artists but insufficient funds; formal title unspecified.",58),
 ("facade","Façade of the Pietà church in Venice","work","Architectural component whose completion Haskell says was delayed for 150 years.",58),
 ("triumph","Tiepolo's Triumph of the Faith on the Pietà church's oval dome","work","Named work dated 1754–1755 by Haskell; identity relative to cand-8550 remains for S3.",58),
]
new_candidates, C = [], {}
for i,(key,name,kind,detail,line_no) in enumerate(SPECS,1):
    cid=f"cand-{MAX_CANDIDATE+i:04d}"
    if cid in candidate_ids or any(x["canonical_name"]==name and x["suggested_type"]==kind for x in candidates):
        raise SystemExit(f"candidate ID/natural key exists: {cid} {name}")
    C[key]=cid
    new_candidates.append({"candidate_id":cid,"index_entry_id":"","canonical_name":name,"index_page_range":"",
      "suggested_type":kind,"status":"open","index_source_file":"","sub_entry":"","detail":detail,
      "exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT}#L{line_no}"})
candidate_ids |= {x["candidate_id"] for x in new_candidates}

def c(k): return C[k]
def e(k): return E[k]
new_mentions=[]
def mention(mid, line_no, cid, surface, note="", occurrence=0):
    if mid in mention_ids or any(x["mention_id"]==mid for x in new_mentions): raise SystemExit(f"duplicate mention ID: {mid}")
    line=lines[line_no-1]; found=[]; pos=0
    while True:
        at=line.find(surface,pos)
        if at<0: break
        found.append(at); pos=at+1
    if occurrence>=len(found): raise SystemExit(f"surface absent on L{line_no}: {surface!r}")
    start=offsets[line_no]+found[occurrence]; end=start+len(surface)
    if segment_text[start:end]!=surface or cid not in candidate_ids: raise SystemExit(f"bad mention span/ref: {mid}")
    new_mentions.append({"mention_id":mid,"segment_id":SEGMENT,"candidate_id":cid,"surface_form":surface,
      "start_char":str(start),"end_char":str(end),"note":note})

def piece(n,start,end):
    s=lines[n-1]
    return s[s.index(start):s.index(end,s.index(start))+len(end)]

new_statements=[]
def statement(sid,a,b,sub,obj,pred,quote,claim,qual,refs=(),rel=False,fn=None,speaker="Haskell",layer="authorial narrative",cross=()):
    if sid in statement_ids or any(x["statement_id"]==sid for x in new_statements): raise SystemExit(f"duplicate statement ID: {sid}")
    if quote not in segment_text: raise SystemExit(f"quote not anchored: {sid}")
    refs=set(refs)|{x for x in (sub,obj) if x}
    if not refs<=candidate_ids: raise SystemExit(f"unknown candidate in {sid}: {sorted(refs-candidate_ids)}")
    q={"source_line_start":a,"source_line_end":b,"printed_page":272,"pdf_physical_page":38,"claim":claim,
       "speaker":speaker,"text_layer":layer,"qualification":qual,"mentioned_candidate_ids":sorted(refs)}
    if rel:q["relation_candidate"]=True
    if fn is not None:q["footnote_marker"]=fn;q["footnote_text_pending"]=True
    if cross:q["cross_reference_segments"]=list(cross)
    new_statements.append({"statement_id":sid,"segment_id":SEGMENT,"subject_candidate_id":sub,"object_candidate_id":obj,
       "predicate":pred,"qualifiers":q,"original_quote":quote,"source_file":SOURCE.relative_to(ROOT).as_posix(),"origin":"book"})

# Source-level mentions. Pronouns and image subjects are linked only where the antecedent is explicit.
mentions_to_add = [
 ("hostile",54,"pamphlet","a hostile pamphlet","Note 1 gives the cited item's title; notes migration remains pending."),
 ("jesuit_church",54,"jesuit_church","their magnificent church","Jesuit church referred to in the nested quotation."),
 ("assumption",54,"assumption","the Assumption of the Virgin","Church dedication, separate from any artwork."),
 ("orders",54,"religious_orders","religious Orders","Comparison group."),
 ("fontebasso",54,"fontebasso","Fontebasso","Painter named by Haskell."),
 ("three_angels",54,"three_angels","The Three Angels visiting Abraham","Reuse indexed work candidate."),
 ("iconography",55,"jesuit_iconography","Jesuit iconography","Named visual tradition."),
 ("elijah_continued",55,"elijah","Elijah carried to Heaven in a Chariot of Fire","Work named in the continuation on this line."),
 ("carmelites",55,"carmelites","Carmelites","Order in the iconographic comparison."),
 ("altarpiece_group",55,"jesuit_altarpieces","one or two of the altarpieces","Unidentified; source gives an interval rather than an exact count."),
 ("dominicans",55,"dominicans","the Dominicans","Order in the comparison."),
 ("dominican_church",55,"dominican_church","S. Maria del Rosario","Reuse existing church candidate."),
 ("ensemble",55,"dominican_ensemble","every painting","Collective description; no full work list."),
 ("dom_order",55,"dominicans","the Order","Explicit antecedent: Dominicans."),
 ("saint_dominic",55,"st_dominic","St Dominic","Figure represented in the ceiling image."),
 ("dom_fresco",55,"dominican_ceiling","St Dominic himself is shown instituting the Rosary","Reuse indexed fresco candidate."),
 ("jesuit_church_name",55,"jesuit_church","Santa Maria Assunta","Reuse indexed Jesuit church candidate."),
 ("pieta",56,"pieta_church","the Pietà","Reuse p.262 source-derived place candidate."),
 ("refuge",56,"refuge","a refuge on the site","Unnamed charitable institution."),
 ("doge_office",56,"doge_office","the Doge","Generic office; do not equate with Doge Grimani."),
 ("senate",57,"senate","Senate","Reuse Senate of Venice candidate; the source sentence crosses the line break."),
 ("doge_grimani",57,"doge_grimani","Doge Grimani","Named in the rebuilding account."),
 ("pieta_rebuild",57,"pieta_church","the church","Reference to the Pietà church."),
 ("gazette",57,"gazzetta","Gazzetta Veneta","Periodical named as source."),
 ("orders_again",58,"religious_orders","religious Orders","Orders contrasted with official patronage."),
 ("governors",58,"governors","The Governors of the Pietà","Governing body named by Haskell."),
 ("venice",58,"venice","Venice","City where artists were based."),
 ("massari",58,"massari","Massari","Architect named by Haskell."),
 ("palladian",58,"palladian","orthodox Palladian Unes","OCR surface retained; the scan confirms 'lines'."),
 ("facade",58,"facade","the façade","Architectural component, distinct from the church place."),
 ("tiepolo",58,"tiepolo","Tiepolo","Painter named by Haskell."),
 ("triumph",58,"triumph","a Triumph of the Faith","Named work; relation to cand-8550 awaits S3."),
]
for mid,n,key,surface,note in mentions_to_add: mention(f"m-chp9-p272-{mid}",n,c(key) if key in C else e(key),surface,note)
# The two 'they' pronouns in L54 refer to the Jesuits and are recorded explicitly.
mention("m-chp9-p272-jesuits-pronoun-quote",54,e("jesuits"),"they","Pronoun in the pamphlet quotation.",0)
mention("m-chp9-p272-jesuits-pronoun-precedent",54,e("jesuits"),"they","Pronoun in Haskell's following sentence.",1)
mention("m-chp9-p272-jesuit-saints",55,e("jesuits"),"the Jesuit saints","No individual saints are named.")
mention("m-chp9-p272-jesuits",55,e("jesuits"),"the Jesuits","Order whose presence is described as visually subdued.")

q_pamphlet=piece(54,"a hostile pamphlet","church’.1")
q_precedent=piece(54,"In fact","but although")
q_marble=piece(54,"both the exterior","the church, dedicated")
q_dedication=piece(54,"the church, dedicated","remains geographically")
q_isolation=piece(54,"remains geographically","None of the leading painters")
q_no_painters=piece(54,"None of the leading painters","and Fontebasso")
q_fontebasso=piece(54,"and Fontebasso, who frescoed the ceiling","relationship to")+"\n"+piece(55,"Jesuit iconography","Jesuit iconography")
q_elijah=piece(55,"and Elijah carried to Heaven","Though the Jesuit saints")
q_altarpieces=piece(55,"Though the Jesuit saints","The contrast with")
q_dominican=piece(55,"The contrast with","hi Santa Maria Assunta")
q_dominican_ceiling=piece(55,"St Dominic himself","hi Santa Maria Assunta")
q_jesuit_style=piece(55,"hi Santa Maria Assunta","style.")
q_refuge=lines[55][lines[55].index("The original foundation dated back"):].rstrip()+"\n"+lines[56].split("The first stone",1)[0].rstrip()
q_rebuild=piece(57,"The first stone was therefore laid","nearly completed")
q_gazette=piece(57,"by 1760 it was described","architecture’.")
q_patronage=piece(58,"This was true enough","religious Orders.")
q_governors=piece(58,"The Governors of the Pietà","but not to pay them.")
q_massari=piece(58,"Massari was the architect","orthodox Palladian Unes.6")
q_facade=piece(58,"He would, no doubt","for 150 years.")
q_tiepolo=piece(58,"Tiepolo painted one of his most striking works","between 1754 and 1755,")

statement("st-chp9-p272-hostile-pamphlet-allegation",54,54,c("pamphlet"),e("jesuits"),"pamphlet_accused_jesuits_of_extracting_church_expense_from_a_single_family",q_pamphlet,"Haskell quotes an unidentified hostile pamphlet alleging that the Jesuits extracted the enormous expense of their church from a single family.","The pamphlet does not name that family; do not automatically identify it with the Manin family in the preceding paragraph. Exact title is pending.",[c("pamphlet"),e("jesuits"),e("jesuit_church")],True,1,"hostile pamphlet quoted by Haskell","nested quotation",[{"segment_id":PREVIOUS,"source_line_start":51,"source_line_end":51}])
statement("st-chp9-p272-jesuit-funding-precedent",54,54,e("jesuits"),None,"haskell_says_jesuits_followed_a_general_funding_precedent",q_precedent,"Haskell says the Jesuits were following a general precedent.","The source does not specify the precedent's scope or provide independent verification.",[e("jesuits"),e("jesuit_church")])
statement("st-chp9-p272-jesuit-church-marble",54,54,e("jesuit_church"),None,"jesuit_church_marble_exterior_and_interior_reportedly_rivalled_venetian_churches",q_marble,"Haskell describes the exterior and richly coloured marble interior as among Venice's most splendid and reports a claim that the church put all others in the shade.","The superlative is partly attributed to an unspecified claim. Note 2 remains pending.",[e("jesuit_church"),e("venice")],fn=2)
statement("st-chp9-p272-jesuit-church-dedication",54,54,e("jesuit_church"),c("assumption"),"s_maria_assunta_dedicated_to_assumption_of_virgin",q_dedication,"Haskell identifies the Jesuit church as dedicated to the Assumption of the Virgin.","This records the dedication concept, not an artwork.",[e("jesuit_church"),c("assumption")],True)
statement("st-chp9-p272-jesuit-church-isolation",54,54,e("jesuit_church"),e("religious_orders"),"s_maria_assunta_geographically_and_artistically_isolated_from_churches_of_other_orders",q_isolation,"Haskell characterizes the church as geographically and artistically isolated from those of the other religious Orders.","This is the author's comparative characterization.",[e("jesuit_church"),e("religious_orders")])
statement("st-chp9-p272-no-leading-painters",54,54,e("jesuit_church"),None,"haskell_says_no_leading_painters_left_work_in_venetian_jesuit_church",q_no_painters,"Haskell says none of the leading painters left work in the Venetian Jesuit church.","Source-level negative claim; note 3 discusses a proposed exception but says there is no evidence its altarpiece was intended for this church. Note text remains pending.",[e("jesuit_church")],fn=3)
statement("st-chp9-p272-fontebasso-three-angels",54,55,e("fontebasso"),e("three_angels"),"fontebasso_frescoed_three_angels_visiting_abraham_on_jesuit_church_ceiling",q_fontebasso,"Haskell says Fontebasso frescoed the ceiling with The Three Angels visiting Abraham.","The work is distinct from the second subject named in the sentence.",[e("fontebasso"),e("three_angels"),e("jesuit_church")],True)
statement("st-chp9-p272-three-angels-iconography",54,55,e("three_angels"),c("jesuit_iconography"),"three_angels_ceiling_scene_had_no_specific_relation_to_jesuit_iconography",q_fontebasso,"Haskell says The Three Angels visiting Abraham had no specific relationship to Jesuit iconography.","This is Haskell's interpretation of the imagery.",[e("three_angels"),c("jesuit_iconography")],True)
statement("st-chp9-p272-fontebasso-elijah",55,55,e("fontebasso"),e("elijah"),"fontebasso_also_depicted_elijah_chariot_scene_on_jesuit_church_ceiling",q_elijah,"Haskell says Fontebasso also depicted Elijah carried to Heaven in a Chariot of Fire on the ceiling.","The artist is carried forward grammatically from p.272 L54.",[e("fontebasso"),e("elijah"),e("jesuit_church")],True,4)
statement("st-chp9-p272-elijah-carmelite-association",55,55,e("elijah"),e("carmelites"),"elijah_chariot_subject_hitherto_associated_almost_exclusively_with_carmelites",q_elijah,"Haskell says the Elijah subject had hitherto been associated almost exclusively with the Carmelites.","Preserve 'almost exclusively'; note 4 adds a Rubens/Jesuit church comparison and is still pending.",[e("elijah"),e("carmelites")],True,4)
statement("st-chp9-p272-jesuit-altarpieces",55,55,e("jesuit_church"),c("jesuit_altarpieces"),"jesuit_saints_appeared_in_one_or_two_altarpieces_without_prominence",q_altarpieces,"Haskell says Jesuit saints appeared in one or two altarpieces but were given no prominence; he characterizes the church's overall effect as wealth with anonymity.","Exact number, titles and artists are not supplied.",[e("jesuit_church"),e("jesuits"),c("jesuit_altarpieces")],True)
statement("st-chp9-p272-dominican-ensemble",55,55,c("dominican_ensemble"),e("dominican_church"),"s_maria_del_rosario_paintings_celebrated_order_and_grouped_saints_in_threes",q_dominican,"Haskell says the paintings in S. Maria del Rosario celebrate the Dominican Order, with great saints painted in threes by leading contemporary artists.","This is a comparative summary, not an exhaustive work catalogue.",[c("dominican_ensemble"),e("dominican_church"),e("dominicans")],True)
statement("st-chp9-p272-dominican-ceiling",55,55,e("dominican_church"),e("dominican_ceiling"),"s_maria_del_rosario_ceiling_depicts_st_dominic_instituting_rosary_as_climax",q_dominican_ceiling,"Haskell says the church's painting ensemble culminates in the ceiling where St Dominic is shown instituting the Rosary.","Reuse the indexed fresco candidate; no modern catalogue identity is asserted.",[e("dominican_church"),e("dominican_ceiling"),e("st_dominic")],True)
statement("st-chp9-p272-jesuit-visual-anonymity",55,55,e("jesuit_church"),e("jesuits"),"haskell_says_jesuit_presence_felt_only_through_foreign_style",q_jesuit_style,"Haskell says viewers are scarcely aware of the Jesuits in Santa Maria Assunta and feel their presence only through the foreignness of the style.","This is Haskell's visual interpretation.",[e("jesuit_church"),e("jesuits")])
statement("st-chp9-p272-pieta-new-church",56,56,e("pieta_church"),None,"pieta_new_church_erected_and_decorated_first_half_eighteenth_century",lines[55],"Haskell says one wholly new church, the Pietà, was erected and splendidly decorated in the first half of the eighteenth century.","Retain Haskell's periodization; note 5 remains pending.",[e("pieta_church")],fn=5)
statement("st-chp9-p272-pieta-refuge-foundation",56,57,c("refuge"),e("pieta_church"),"fourteenth_century_refuge_for_exposed_children_and_orphans_established_on_pieta_site",q_refuge,"Haskell says a fourteenth-century refuge for exposed children and orphans had been established on the site.","The refuge and later church are distinct candidates; the source gives no formal refuge name.",[c("refuge"),e("pieta_church")],True)
statement("st-chp9-p272-refuge-doge-patronage",56,57,c("refuge"),c("doge_office"),"pieta_refuge_came_under_direct_patronage_of_venetian_doge",q_refuge,"Haskell says the refuge soon came under the direct patronage of the Doge.","The officeholder is not named; keep distinct from Doge Grimani at the later rebuilding.",[c("refuge"),c("doge_office")],True)
statement("st-chp9-p272-refuge-senate-patronage",56,57,c("refuge"),e("senate"),"pieta_refuge_came_under_direct_patronage_of_senate",q_refuge,"Haskell says the refuge soon came under the direct patronage of the Senate.","No individual senator or formal act is named.",[c("refuge"),e("senate")],True)
statement("st-chp9-p272-doge-grimani-rebuild",57,57,e("doge_grimani"),e("pieta_church"),"doge_grimani_laid_first_stone_when_rebuild_decided_1745",q_rebuild,"Haskell says Doge Grimani laid the first stone when rebuilding was decided in 1745.","The sentence dates the decision to rebuild, not the exact ceremony.",[e("doge_grimani"),e("pieta_church")],True)
statement("st-chp9-p272-pieta-gazzetta-description",57,57,c("gazzetta"),e("pieta_church"),"gazzetta_veneta_described_pieta_nearly_complete_and_one_of_richest_modern_works_1760",q_gazette,"Haskell reports that the Gazzetta Veneta described the church as nearly complete in 1760 and called it one of the richest and most beautiful works of modern architecture.","Quoted report; issue and page are not supplied. Haskell follows with 'This was true enough'.",[c("gazzetta"),e("pieta_church")],True,None,"Gazzetta Veneta as cited by Haskell","quoted periodical report")
statement("st-chp9-p272-official-patronage-decline",58,58,e("pieta_church"),None,"haskell_contrasts_pieta_grandeur_with_declining_official_art_patronage",q_patronage,"Haskell says the church's grandeur followed difficulties revealing the poor state of official patronage compared with support from private families and religious Orders.","Authorial evaluation, not a quantified comparison.",[e("pieta_church"),e("religious_orders")])
statement("st-chp9-p272-pieta-governors-funding",58,58,c("governors"),None,"pieta_governors_could_draw_on_leading_venetian_artists_but_not_pay_them",q_governors,"Haskell says the Governors of the Pietà could draw on all leading artists in Venice but could not pay them.","This describes stated capacity, not evidence that every artist was approached.",[c("governors"),e("venice")])
statement("st-chp9-p272-massari-architect",58,58,e("massari"),e("pieta_church"),"giorgio_massari_architect_of_pieta_church",q_massari,"Haskell identifies Massari as the Pietà church's architect.","Reuse the index-derived person candidate.",[e("massari"),e("pieta_church")],True)
statement("st-chp9-p272-massari-palladian-lines",58,58,e("massari"),e("palladian"),"massari_said_conservative_pressures_compelled_orthodox_palladian_design",q_massari,"Haskell says Massari ruefully commented that conservative pressures compelled him to work in orthodox Palladian lines.","OCR 'Unes' is corrected to 'lines' against the scan; note 6 remains pending.",[e("massari"),e("palladian")],True,6)
statement("st-chp9-p272-pieta-facade-delay",58,58,c("facade"),e("pieta_church"),"pieta_facade_not_completed_for_150_years",q_facade,"Haskell says Massari would have been more rueful had he known the façade would not be completed for 150 years.","Retrospective counterfactual; retain the approximate duration, not an exact completion date.",[c("facade"),e("pieta_church")],True)
statement("st-chp9-p272-tiepolo-triumph-faith",58,58,e("tiepolo"),c("triumph"),"tiepolo_painted_triumph_of_faith_on_pieta_oval_dome_1754_to_1755",q_tiepolo,"Haskell says Tiepolo painted a Triumph of the Faith on the oval dome between 1754 and 1755.","Identity relative to cand-8550 remains for S3; p.273 continues the same sentence with payment and a later loan.",[e("tiepolo"),c("triumph"),e("pieta_church")],True,None,"Haskell","authorial narrative",[{"segment_id":NEXT,"source_line_start":63,"source_line_end":63}])

# The p.271 clause is no longer open; its cited endnote remains pending in the separate notes segment.
prev_stmt["qualifiers"]["claim"] = "Haskell introduces an unidentified hostile pamphlet's claim about the expense of the Jesuit church; the allegation itself is recorded in the linked p.272 continuation."
prev_stmt["qualifiers"]["qualification"] = "The introductory sentence begun at p.271 L51 is completed at p.272 L54 by the linked nested-quotation statement. The pamphlet's exact title remains pending from the consolidated notes segment."
prev_stmt["qualifiers"]["mentioned_candidate_ids"] = sorted(set(prev_stmt["qualifiers"].get("mentioned_candidate_ids",[])) | {c("pamphlet")})
cov[PREVIOUS].update({"disposition":"reviewed","migration_status":"complete","source_line_ranges":"L39-51","note":"Printed p.271 body read against scan. Its unfinished sentence at L51 is closed by the p.272 L54 hostile-pamphlet quotation and linked statement. Footnotes 1-6 remain in the consolidated notes segment."})
cov[SEGMENT].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L54-58","note":"Printed p.272 (PDF physical p.38) body L54-58 read against scan. Closes p.271 L51's hostile-pamphlet sentence. The Tiepolo sentence continues at p.273 L63; S0 L59-60 duplicates printed note 3 and remains for the consolidated notes segment. L53 is a page marker."})

if len({x["mention_id"] for x in mentions+new_mentions}) != len(mentions)+len(new_mentions): raise SystemExit("duplicate mention ID")
if len({x["statement_id"] for x in statements+new_statements}) != len(statements)+len(new_statements): raise SystemExit("duplicate statement ID")
summary={"segment":SEGMENT,"completed_previous":PREVIOUS,"next":NEXT,"status":"reviewed/partial",
 "new_candidates":len(new_candidates),"candidate_ids":[x["candidate_id"] for x in new_candidates],
 "new_mentions":len(new_mentions),"new_statements":len(new_statements),
 "ocr_corrections":[{"line":55,"ocr":"hi Santa Maria Assunta","print":"In Santa Maria Assunta"},{"line":58,"ocr":"Palladian Unes","print":"Palladian lines"}],
 "counts_after":{"candidates":len(candidates)+len(new_candidates),"mentions":len(mentions)+len(new_mentions),"statements":len(statements)+len(new_statements),"coverage_rows":len(coverage)}}
print(json.dumps(summary,ensure_ascii=False,indent=2))

parser=argparse.ArgumentParser(); parser.add_argument("--apply",action="store_true"); args=parser.parse_args()
if args.apply:
    paths=[cp,mp,sp,vp]; backups=[p.with_name(p.name+BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups): raise SystemExit("recovery backup already exists; inspect before retrying")
    for src,dst in zip(paths,backups): shutil.copy2(src,dst)
    try:
        write_csv(cp,cf,candidates+new_candidates); write_csv(mp,mf,mentions+new_mentions)
        write_jsonl(sp,statements+new_statements); write_csv(vp,vf,list(cov.values()))
    except Exception:
        for target,backup in zip(paths,backups): shutil.copy2(backup,target)
        raise
    print("APPLIED; recovery backups retained: "+", ".join(p.name for p in backups))
else: print("DRY RUN: no S2 table rows written")
