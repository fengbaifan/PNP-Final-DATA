"""Controlled S2 migration for printed p.345; dry-run by default."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
SEGMENT = "chp-13:13_CHP-13_intro:l161-171"
P344_SEGMENT = "chp-13:13_CHP-13_intro:l116-122"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
SEGMENT_SHA = "3b428ba03ee1060eafa7b250f5ad4831613f35cc4ab909b49703bf20a35bd37c"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p345-final-20261003"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.345 migration")
args = parser.parse_args()


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader=csv.DictReader(f); return reader.fieldnames, list(reader)
def read_jsonl(path): return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=path.parent,delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n"); w.writeheader(); w.writerows(rows); tmp=Path(f.name)
    tmp.replace(path)
def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=path.parent,delete=False) as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
        tmp=Path(f.name)
    tmp.replace(path)

if sha(SOURCE)!=SOURCE_SHA or sha(PDF)!=PDF_SHA: raise SystemExit("source Markdown or registered PDF SHA changed")
source_lines=SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text="\n".join(source_lines[160:171])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest()!=SEGMENT_SHA: raise SystemExit("p.345 source segment changed")
for line, token in {162:"or three times before being ready",164:"Varíe Pitture a Fresco",166:"112?",168:"John Strange",169:"Don Pietro Antonio Toni",170:"Novelli to whom he left his collections",171:"written in 1790"}.items():
    if token not in source_lines[line-1]: raise SystemExit(f"required printed-page text missing at L{line}")

candidate_path=TABLES/"entity-candidates.csv"; mention_path=TABLES/"mentions.csv"; statement_path=TABLES/"book-statements.jsonl"; coverage_path=TABLES/"s2-coverage.csv"
candidate_fields,candidates=read_csv(candidate_path); mention_fields,mentions=read_csv(mention_path); statements=read_jsonl(statement_path); coverage_fields,coverage=read_csv(coverage_path)
state=(len(candidates),len(mentions),len(statements),len(coverage))
if state!=(10101,21824,9744,830): raise SystemExit(f"unexpected pre-state {state}")
coverage_by_id={r["segment_id"]:r for r in coverage}
if SEGMENT not in coverage_by_id or coverage_by_id[SEGMENT]["disposition"]!="queued": raise SystemExit("p.345 coverage is not queued")
segment_rows=read_jsonl(TABLES/"segments.jsonl")
seg=next((r for r in segment_rows if r["segment_id"]==SEGMENT),None)
if not seg or seg["sha256"]!=SEGMENT_SHA: raise SystemExit("p.345 segment row/hash changed")
candidate_by_id={r["candidate_id"]:r for r in candidates}; statement_by_id={r["statement_id"]:r for r in statements}
required={"cand-0025","cand-0041","cand-0413","cand-1682","cand-1727","cand-1907","cand-1950","cand-2154","cand-2569","cand-2640","cand-2719","cand-2773","cand-2830","cand-2838","cand-2854","cand-2855","cand-2858","cand-2859","cand-3416","cand-3461","cand-7618","cand-9837","cand-2516","cand-1760","cand-2838"}
if not required.issubset(candidate_by_id): raise SystemExit(f"required existing candidates missing: {sorted(required-candidate_by_id.keys())}")
new_candidate_ids=[f"cand-{n}" for n in range(10115,10126)]
if any(cid in candidate_by_id for cid in new_candidate_ids): raise SystemExit("one or more new candidate IDs already exist")

new_candidate_specs=[
("cand-10115","Pietro Monaco's 1743 collection of fifty-five prints from religious pictures","archive","The 1743 collection described by Haskell; its title is not supplied in this passage. Prints were taken mostly from religious pictures in Venetian private collections.","L165"),
("cand-10116","Pietro Monaco's posthumous 1779 edition of the 112-plate print collection","archive","Later edition of Monaco's print collection, published posthumously by Viero in 1779. The printed note cites Raccolta di centododici stampe, but its edition-specific title mapping remains pending.","L165"),
("cand-10117","Varie Pitture a Fresco (1760)","archive","Publication of the younger A. M. Zanetti's copies after classic artists; the printed title is Varie Pitture a Fresco. The source OCR has Varíe.","L164"),
("cand-10118","Boschini's Ricche Miniere, revised by A. M. Zanetti the Younger (1733)","archive","The passage describes the younger Zanetti's 1733 revision/editing of Boschini's Ricche Miniere and a friendly dedication to his elder cousin.","L164"),
("cand-10119","Pietro Monaco letter to John Strange concerning seventeen pictures (1763)","archive","A letter written in 1763 to John Strange, enclosing a list of seventeen pictures described as singolari e scielti, owned by Monaco and offered for sale. The printed note's shelfmark and exact date remain pending.","L168"),
("cand-10120","Collections left by Don Pietro Antonio Toni to Pietro Antonio Novelli (1748)","","An unspecified set of collections inherited by Novelli at Toni's death. The text does not identify contents or a formal collection title; the current taxonomy has no personal-collection type.","L170"),
("cand-10121","Engravings after Sebastiano Ricci's works given to Don Pietro Antonio Toni","work","A group of engravings after Ricci's works that the passage says Ricci gave to Toni; individual print titles and count are not supplied.","L169"),
("cand-10122","Modello of the Adoration of the Magi by Sebastiano Ricci","work","A modello of an Adoration of the Magi that Ricci gave to Toni. No date, medium beyond modello, or present location is supplied.","L169"),
("cand-10123","Eight drawings by Giambattista Tiepolo reproduced in Pietro Monaco's print collection","work","A group of eight drawings by Tiepolo among the contemporary works reproduced in Monaco's collection; individual titles are not given.","L167"),
("cand-10124","Nine paintings by Giovan Battista Pittoni reproduced in Pietro Monaco's print collection","work","A group of nine Pittoni paintings among the contemporary works reproduced in Monaco's collection; individual titles are not given.","L167"),
("cand-10125","Three paintings, one each by Zais, Piazzetta, and Nazari, reproduced in Pietro Monaco's print collection","work","A group of three paintings, one each by Zais, Piazzetta, and Nazari, listed among contemporary works reproduced in Monaco's collection; individual titles are not supplied.","L167"),
]
new_candidates=[]
for cid,name,kind,detail,line in new_candidate_specs:
    r={f:"" for f in candidate_fields}; r.update({"candidate_id":cid,"canonical_name":name,"suggested_type":kind,"status":"open","detail":detail,"candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT}#{line}"}); new_candidates.append(r)

mention_specs=[
("cand-2838","Zanetti died in 1767","Haskell's statement about the elder Zanetti; not independently verified here."),
("cand-2854","identically named younger cousin","The younger Antonio Maria Zanetti, distinguished in the passage from the elder cousin."),
("cand-2854","Antonio Maria the Younger","Explicit name used for the younger cousin."),
("cand-10117","Varíe Pitture a Fresco","S0 OCR form; the printed title reads Varie Pitture a Fresco."),
("cand-10118","Boschini’s Ricche Miniere","Named work revised by the younger Zanetti."),
("cand-0413","Boschini","Nested author name in the book title."),
("cand-2854","admirable revision of Boschini’s Ricche Miniere","The younger Zanetti's editorial work; Haskell's evaluation 'admirable' is retained as source wording."),
("cand-9837","Della Pittura Veneziana","The 1771 publication named by Haskell."),
("cand-10115","collection of fifty-five prints","The 1743 publication described without a title."),
("cand-1682","Pietro Monaco","Publisher/engraver named in the passage."),
("cand-2719","Venetian","Geographic adjective in the description of the private collections from which pictures were taken."),
("cand-7618","1763","The first later edition year; maps to the existing 1763 archive candidate."),
("cand-10116","1779","The posthumous later edition year."),
("cand-2773","Viero","Named publisher of the 1779 posthumous edition."),
("cand-10116","112?","S0 OCR form; the printed count is 112, followed by footnote marker 1."),
("cand-10123","eight drawings by Tiepolo","Group of eight reproduced drawings; individual titles are unknown."),
("cand-2569","Tiepolo","Artist named for the group of eight drawings."),
("cand-10124","nine paintings by Pittoni","Group of nine reproduced paintings; individual titles are unknown."),
("cand-1950","Pittoni","Artist named for the group of nine paintings."),
("cand-10125","one each by Zais, Piazzetta and Nazari","Group of three distinct paintings, one by each artist; the source does not give individual titles."),
("cand-2830","Zais","Artist named for the single painting."),
("cand-1907","Piazzetta","Artist named for the single painting."),
("cand-1727","Nazari","The index candidate for Bartolommeo Nazari is reused pending S3."),
("cand-1682","Monaco himself","Haskell says a strikingly high proportion of reproduced contemporary works belonged to Monaco."),
("cand-0025","Albrizzi","Comparison in Haskell's discussion of Monaco's possible patronage."),
("cand-2838","Zanetti","Comparison in Haskell's discussion of Monaco's possible patronage."),
("cand-10119","a letter written in 1763 to","The letter associated with Monaco's list of pictures; the printed note with its shelfmark remains pending."),
("cand-2516","John Strange","Recipient named in the narrative; index candidate reused pending S3."),
("cand-10119","list of seventeen pictures ‘singolari e scielti’","Description of the contents enclosed with the letter; not treated as a separate archive object."),
("cand-2640","Don Pietro Antonio Toni","Named priest and collector."),
("cand-3416","Modena","Toni was born near Modena, according to Haskell."),
("cand-2719","Venice","Toni settled in Venice thirty years after his birth, according to Haskell."),
("cand-2640","a keen collector","Toni's activity as characterized by Haskell despite his financial hardship."),
("cand-2154","Sebastiano Ricci","Toni's closest friend and named recipient of care during illness."),
("cand-10121","engravings after his works","Group of engravings after Ricci's works that Ricci gave Toni."),
("cand-10122","a modello of an Adoration of the Magi","Named model work given to Toni by Ricci."),
("cand-1950","Toni was also in close touch with Pittoni","Artist with whom Toni was also in close touch."),
("cand-1760","the young Pietro Antonio","Young Pietro Antonio Novelli, identified from the following line; identity remains mapped to the chapter candidate pending S3."),
("cand-1760","Novelli","Continuation of the split name at the beginning of line 170."),
("cand-10120","his collections","Unspecified collections Toni left to Novelli; type remains unresolved."),
("cand-2640","Toni was a learned man","Haskell's characterization."),
]

def span(text, needle, occurrence=0):
    start=-1; pos=0
    for _ in range(occurrence+1):
        start=text.find(needle,pos)
        if start<0: raise SystemExit(f"mention not found: {needle!r}")
        pos=start+1
    return start,start+len(needle)
mention_ids={r["mention_id"] for r in mentions}; new_mentions=[]
for i,(cid,surface,note) in enumerate(mention_specs,1):
    mid=f"m-s2-ch13-p345-{i:03d}"
    if mid in mention_ids: raise SystemExit(f"mention ID exists: {mid}")
    # Repeated short person names are anchored to a complete surrounding phrase where possible.
    start,end=span(segment_text,surface)
    if cid not in candidate_by_id and cid not in {r["candidate_id"] for r in new_candidates}: raise SystemExit(f"missing candidate {cid}")
    new_mentions.append({"mention_id":mid,"segment_id":SEGMENT,"candidate_id":cid,"surface_form":surface,"start_char":str(start),"end_char":str(end),"note":note})

pending_notes={1:{"printed_note":1,"segment_id":"chp-13:13_CHP-13_intro:l179-251","line":249,"status":"pending"},2:{"printed_note":2,"segment_id":"chp-13:13_CHP-13_intro:l179-251","line":250,"status":"pending"},3:{"printed_note":3,"segment_id":"chp-13:13_CHP-13_intro:l179-251","line":251,"status":"pending"}}
new_statements=[]
def quote(start,end): return "\n".join(source_lines[start-1:end])
def add_statement(sid,start,end,subject,obj,predicate,claim,speaker="Haskell",layer="authorial narrative",qualification="",mentioned=(),relation=False,notes=()):
    if sid in statement_by_id or any(x["statement_id"]==sid for x in new_statements): raise SystemExit(f"statement exists: {sid}")
    q={"source_line_start":start,"source_line_end":end,"printed_page":345,"pdf_physical_page":18,"claim":claim,"speaker":speaker,"text_layer":layer,"qualification":qualification,"mentioned_candidate_ids":list(mentioned)}
    if relation: q["relation_candidate"]=True
    if notes: q["note_refs_pending"]=[dict(pending_notes[n]) for n in notes]
    new_statements.append({"statement_id":sid,"segment_id":SEGMENT,"subject_candidate_id":subject,"object_candidate_id":obj,"predicate":predicate,"qualifiers":q,"original_quote":quote(start,end),"origin":"book","source_file":"02-sources/02-Markdown/13_CHP-13_intro.md"})

add_statement("st-chp13-p345-zanetti-1752-quote-continuation",162,162,"cand-2838","cand-3461","reported_few_amateurs_or_patrons_interested_in_fine_arts_in_italy","The 1752 letter quote from p.344 continues: the few interested patrons turned each zecchino two or three times before spending it on art.",speaker="A. M. Zanetti, quoted by Haskell",layer="quoted first-person continuation",qualification="This line closes the sentence begun on p.344. The quote describes the few remaining art patrons; it is not an independently measured economic behavior.",mentioned=["cand-2838","cand-3461"],relation=True)
add_statement("st-chp13-p345-haskell-qualifies-italian-situation",162,162,"cand-2838","cand-2719","authorial_qualification_of_geographic_scope","Haskell qualifies the preceding 1752 statement as describing the Venetian situation rather than Italy generally.",layer="authorial qualification",qualification="This is Haskell's distinction, not a correction to Zanetti's quoted wording.",mentioned=["cand-2838","cand-2719","cand-3461"])
add_statement("st-chp13-p345-zanetti-death-age",162,162,"cand-2838",None,"died_in_year_at_reported_age","Haskell says A. M. Zanetti died in 1767 at age 89 and that the quoted words were even truer by then.",qualification="Retain the book's reported age and retrospective judgment; no external verification is claimed.",mentioned=["cand-2838"])
add_statement("st-chp13-p345-younger-zanetti-cousin",163,163,"cand-2854","cand-2838","younger_cousin_of","The passage identifies A. M. Zanetti the Younger as the elder Zanetti's identically named younger cousin.",qualification="Kinship and shared name are stated by Haskell; S3 identity alignment remains pending.",mentioned=["cand-2854","cand-2838"],relation=True)
add_statement("st-chp13-p345-zanettis-collaborated-on-two-books",163,163,"cand-2854","cand-2838","collaborated_on_two_main_books_with","Haskell says the two cousins collaborated on their two main books.",qualification="The passage does not identify which two books in this sentence; no titles are inferred.",mentioned=["cand-2854","cand-2838"],relation=True)
add_statement("st-chp13-p345-younger-zanetti-critical-role",163,163,"cand-2854",None,"characterized_as_critic_not_patron_or_connoisseur","Haskell characterizes the younger Zanetti as an extremely perceptive critic rather than a patron or connoisseur.",qualification="Authorial evaluation; not a universal assessment of the person's activities.",mentioned=["cand-2854"])
add_statement("st-chp13-p345-varie-pitture-1760",163,164,"cand-10117","cand-2854","published_copies_after_classic_artists_by","The younger Zanetti published his copies after classic artists as Varie Pitture a Fresco in 1760.",qualification="The title is corrected from the OCR form Varíe to the printed Varie; the copies' individual sources are not identified.",mentioned=["cand-10117","cand-2854"])
add_statement("st-chp13-p345-ricche-miniere-edited-1733",164,164,"cand-10118","cand-2854","edited_by","The younger Zanetti revised/edited Boschini's Ricche Miniere in 1733 and dedicated it in a friendly manner to his elder cousin.",qualification="The title remains as Haskell gives it; no edition was independently consulted.",mentioned=["cand-10118","cand-2854","cand-0413","cand-2838"])
add_statement("st-chp13-p345-della-pittura-veneziana-1771",164,164,"cand-9837","cand-2854","authored_by","Haskell names Della Pittura Veneziana (1771) as the younger Zanetti's own work.",qualification="The archive candidate is reused from the p.329 bibliographic mention; source identity remains for S3.",mentioned=["cand-9837","cand-2854"])
add_statement("st-chp13-p345-younger-zanetti-limited-contemporary-role",164,164,"cand-2854",None,"authorial_assessment_limited_part_in_contemporary_artistic_life","Haskell says the younger Zanetti played little part in contemporary artistic life.",qualification="Authorial assessment, not an independently established measure.",mentioned=["cand-2854"])
add_statement("st-chp13-p345-younger-zanetti-prevent-export",164,164,"cand-2854",None,"made_responsible_for_preventing_export_of_old_masterworks","Haskell says the younger Zanetti's taste and scholarship were put to practical use and that he was made responsible for preventing export of great past masterpieces.",qualification="The responsible office or appointing authority is not named here.",mentioned=["cand-2854"])
add_statement("st-chp13-p345-monaco-1743-collection",165,165,"cand-10115","cand-1682","published_by","Pietro Monaco published a collection of fifty-five prints in 1743, taken from religious pictures mostly in Venetian private collections.",qualification="The publication title is not supplied for the 1743 collection; do not equate it with a later edition without further evidence.",mentioned=["cand-10115","cand-1682","cand-2719"])
add_statement("st-chp13-p345-monaco-1763-1779-editions",165,166,"cand-10116","cand-2773","posthumously_published_by","Haskell says later editions in 1763 and 1779 increased the number of plates to 112, with the 1779 edition published posthumously by Viero.",qualification="The 1763 edition is represented by the existing archive candidate cand-7618; this row represents the 1779 edition. The exact title is confirmed in p.345 note 1, which remains pending.",mentioned=["cand-10115","cand-7618","cand-10116","cand-2773"],notes=[1])
add_statement("st-chp13-p345-monaco-reproduced-work-groups",166,167,"cand-7618","cand-1682","collection_contains_named_reproduced_work_groups","Haskell lists eight Tiepolo drawings, nine Pittoni paintings, and one painting each by Zais, Piazzetta, and Nazari among the contemporary works reproduced; a strikingly high proportion belonged to Monaco himself.",qualification="The OCR form 112? is corrected against print to 112 followed by note marker 1. Group candidates preserve the unnamed individual works and counts.",mentioned=["cand-7618","cand-1682","cand-10123","cand-10124","cand-10125","cand-2569","cand-1950","cand-2830","cand-1907","cand-1727"],relation=True,notes=[1])
add_statement("st-chp13-p345-monaco-collection-advertised-dealer",167,168,"cand-7618","cand-1682","almost_certainly_used_plates_to_advertise_dealer_activity","Haskell says the collection might suggest patronage like Albrizzi's or Zanetti's, but that Monaco was almost certainly using the plates to advertise his dealer activity.",qualification="Preserve the contrast and Haskell's 'almost certainly'; this is not a verified statement of Monaco's intent.",mentioned=["cand-7618","cand-1682","cand-0025","cand-2838"],relation=True)
add_statement("st-chp13-p345-monaco-letter-to-strange-seventeen-pictures",168,169,"cand-1682","cand-10119","wrote_letter_to_with_list_of_pictures_for_sale","The passage says Monaco's dealer activity is known from a 1763 letter to John Strange enclosing a list of seventeen selected pictures that Monaco owned and wanted to sell.",qualification="The printed note 2 gives the archival locator and exact date notation; it remains pending. The phrase singolari e scielti is retained as source wording.",mentioned=["cand-1682","cand-10119","cand-2516"],relation=True,notes=[2])
add_statement("st-chp13-p345-toni-born-near-modena",169,169,"cand-2640","cand-3416","born_near","Haskell says Don Pietro Antonio Toni was born near Modena in 1692.",qualification="Retain 'near Modena'; no more precise birthplace is inferred.",mentioned=["cand-2640","cand-3416"],relation=True,notes=[3])
add_statement("st-chp13-p345-toni-settled-in-venice",169,169,"cand-2640","cand-2719","settled_in","Haskell says Toni settled in Venice thirty years after his birth.",qualification="The source gives a relative interval; no arithmetic year is added.",mentioned=["cand-2640","cand-2719"],relation=True,notes=[3])
add_statement("st-chp13-p345-toni-collector",169,169,"cand-2640",None,"keen_collector_amassed_prints","Despite being desperately short of money, Toni was a keen collector and amassed prints through friendships with leading artists.",qualification="Haskell's characterization; the text does not enumerate the prints here.",mentioned=["cand-2640"])
add_statement("st-chp13-p345-toni-ricci-friendship-and-care",169,169,"cand-2640","cand-2154","close_friend_cared_for_during_illness","Toni's closest friend was Sebastiano Ricci; Toni cared for Ricci during an illness.",qualification="The source reports care and friendship; the return gifts are recorded separately.",mentioned=["cand-2640","cand-2154"],relation=True,notes=[3])
add_statement("st-chp13-p345-ricci-engravings-given-to-toni",169,169,"cand-10121","cand-2640","given_to_by_sebastiano_ricci","Ricci gave Toni engravings after Ricci's works.",qualification="Individual engravings and their count are not supplied in this passage.",mentioned=["cand-10121","cand-2154","cand-2640"],relation=True,notes=[3])
add_statement("st-chp13-p345-ricci-modello-given-to-toni",169,169,"cand-10122","cand-2640","given_to_by_sebastiano_ricci","Ricci also gave Toni a modello of an Adoration of the Magi.",qualification="The model's present location, date, and medium are not stated.",mentioned=["cand-10122","cand-2154","cand-2640"],relation=True,notes=[3])
add_statement("st-chp13-p345-toni-gambled-on-ricci-behalf",169,169,"cand-2640","cand-2154","gambled_on_behalf_of","Haskell says Toni would gamble on Ricci's behalf; he describes Ricci as a 'voyeur' who preferred to watch rather than participate.",qualification="Retain Haskell's characterization and reported preference; do not infer financial representation or a diagnosis.",mentioned=["cand-2640","cand-2154"],relation=True,notes=[3])
add_statement("st-chp13-p345-toni-contact-with-pittoni",169,169,"cand-2640","cand-1950","in_close_contact_with","Toni was also in close touch with Pittoni.",qualification="The passage gives no further description of this contact.",mentioned=["cand-2640","cand-1950"],relation=True,notes=[3])
add_statement("st-chp13-p345-toni-adviser-and-patron-to-novelli",169,170,"cand-2640","cand-1760","adviser_and_patron_to","Toni acted as adviser and patron to his special protégé, the young Pietro Antonio Novelli.",qualification="The role is recorded as Haskell describes it; no specific commission is inferred.",mentioned=["cand-2640","cand-1760"],relation=True,notes=[3])
add_statement("st-chp13-p345-toni-collections-left-to-novelli-1748",170,170,"cand-10120","cand-1760","left_to_novelli_when_toni_died","Toni left his collections to Novelli when he died in 1748.",qualification="The collections' contents are not specified; their type remains unresolved.",mentioned=["cand-10120","cand-2640","cand-1760"],relation=True,notes=[3])
add_statement("st-chp13-p345-toni-discussions-may-have-shaped-novelli",170,170,"cand-2640","cand-1760","may_have_contributed_to_later_pedantry","Haskell says Toni's discussions with Novelli and explanations of pictures they visited together may have helped produce Novelli's later pedantry.",qualification="The source explicitly marks this as possible; it is not stated as a certain causal relation.",mentioned=["cand-2640","cand-1760"],relation=True,notes=[3])
add_statement("st-chp13-p345-note3-date-continuation",171,171,None,None,"continuation_of_printed_note3","The continuation of p.345 printed note 3 says the referenced account was written in 1790 but sketched out by 1762.",speaker="Haskell, printed note 3",layer="footnote continuation",qualification="The antecedent of 'This' is the manuscript life identified in consolidated note L251, which remains pending.",mentioned=[],notes=[3])

# Link the p.344 quotation fragment to this actual continuation; keep each quote anchored to its own segment.
p344_statement_id="st-chp13-p344-zanetti-1752-incomplete_letter_fragment"
p344_statement=statement_by_id.get(p344_statement_id)
if not p344_statement or p344_statement["qualifiers"].get("quote_truncated_at_source") is not True: raise SystemExit("expected p.344 open quote statement changed")
p344_statement["qualifiers"]["claim"]="In a 1752 letter, Zanetti says the few remaining amateurs or patrons interested in fine arts turn each zecchino over two or three times before spending it on art; the quoted sentence continues on p.345."
p344_statement["qualifiers"]["qualification"]="The quote ends at 'two' on p.344 and continues at p.345 L162 with 'or three times before being ready to spend it on that sort of thing'. Haskell immediately distinguishes the Venetian situation from Italy generally."
p344_statement["qualifiers"].pop("quote_truncated_at_source",None)
p344_statement["qualifiers"]["quote_continuation_statement_id"]="st-chp13-p345-zanetti-1752-quote-continuation"
p344_statement["qualifiers"]["cross_reference_segments"]=[SEGMENT]

coverage_by_id[SEGMENT].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L161-171","note":"Printed p.345 was checked against CHP-13.pdf physical page 18. The 1752 quotation from p.344 closes at L162; p.344 is now cross-linked to this continuation. Recorded the younger Zanetti, Monaco's publication history and dealer evidence, Don Pietro Antonio Toni, Ricci/Novelli relations and note 3's dated continuation. Printed notes 1-3 map to consolidated L249-L251 and remain pending; the final dealer/agent sentence continues at p.346 L174, so this segment remains partial. S2-only OCR corrections: L164 Varíe→Varie and Use→life; L166 112?→112 with printed note marker 1. No changes to canonical OCR."})

new_candidate_rows=candidates+new_candidates
new_mention_rows=mentions+new_mentions
new_statement_rows=statements+new_statements
print(f"candidates +{len(new_candidates)}; mentions +{len(new_mentions)}; statements +{len(new_statements)}; p.345 coverage reviewed/partial")
print("p.344 quote continuation linked; p.345 printed notes 1-3 remain pending")
if not args.apply: print("dry-run only; pass --apply to write"); raise SystemExit(0)
for path in (candidate_path,mention_path,statement_path,coverage_path):
    backup=Path(str(path)+BACKUP_SUFFIX)
    if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path,backup)
write_csv(candidate_path,candidate_fields,new_candidate_rows); write_csv(mention_path,mention_fields,new_mention_rows); write_jsonl(statement_path,new_statement_rows); write_csv(coverage_path,coverage_fields,coverage)
print("applied; recovery backups saved for candidate, mention, statement, and coverage tables")
