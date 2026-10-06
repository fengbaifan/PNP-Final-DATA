"""Controlled S2 migration for printed p.302; dry-run unless --apply."""
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
P301 = "chp-10:10_CHP-10_intro:l382-389"
P300 = "chp-10:10_CHP-10_intro:l368-380"
P302 = "chp-10:10_CHP-10_intro:l391-400"
P303 = "chp-10:10_CHP-10_intro:l402-409"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = "568d746907dc3255fd514cb8dc7a85111c7ec06aad071737c515acce7c0b71ce"
BACKUP = ".bak-s2-chp10-p302-20261002"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
first, last, PAGE, PHYSICAL = 391, 400, 302, 31
body = "\n".join(src[first - 1:last])
digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
if digest != EXPECTED_SEGMENT_SHA or src[390].strip() != "[Page 302]" or "Mary Wortley Montagu" not in body or "Sebastiano Ricci" not in body:
    raise SystemExit(f"p.302 source segment mismatch: {digest}")
line_offsets, offset = {}, 0
for line_no in range(first, last + 1):
    line_offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9185:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((P301,("reviewed","partial")),(P302,("queued","pending")),
                      (P303,("queued","pending")),(NOTES,("queued","pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"],row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] == P302 for row in mentions) or any(row["segment_id"] == P302 for row in statements):
    raise SystemExit("p.302 already has mention or statement rows")

E = {
    "smith":"cand-2440", "montagu":"cand-1688", "james_adam":"cand-0011",
    "tofts":"cand-2639", "wynne":"cand-2824", "john_murray":"cand-1719",
    "george_iii":"cand-1141", "boccage":"cand-0380", "venice":"cand-3401",
    "palazzo_balbi":"cand-2464", "ricci_smith":"cand-2183", "ricci_turin":"cand-2184",
    "lazzarini":"cand-1368", "tiepolo":"cand-2569", "catholic_church":"cand-3400",
    "turin":"cand-2662", "court_turin":"cand-8273", "veronese":"cand-2755",
    "cignani":"cand-0748", "british_residency":"cand-9174",
}
for key,cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("murray_sister","Unidentified sister of John Murray and second wife of Joseph Smith","person","Haskell identifies the woman only as John Murray’s sister and Smith’s second wife; her name and independent identity are not supplied.",393),
    ("english_taste","English taste as a style applied to Joseph Smith’s Venetian palace","term","Mme du Boccage’s quoted characterization; retained as her reported description, not an external style classification.",394),
    ("smith_italian_collection","Italian paintings filling Joseph Smith’s Venetian palace (collection type unresolved)","","Collective body of Italian paintings in the palace; the passage does not identify individual works or establish a collection-level knowledge-unit type.",395),
    ("smith_riccis","Joseph Smith’s paintings by Sebastiano Ricci (individual works not specified here)","work","Collective reference to Ricci paintings bought or commissioned by Smith; do not collapse it into the separately identified seven-picture New Testament group.",397),
    ("new_testament_pictures","Seven large New Testament pictures by Sebastiano Ricci for Joseph Smith","work","A group hung together in a special palace room and engraved/described in 1749; individual titles and present identities are not given here.",398),
    ("cignani_cartoons","Seven cartoons by Carlo Cignani in Joseph Smith’s collection","work","A separate group said to have been hung in another room; individual subjects and present identities are not supplied.",398),
    ("smith_1749_publication","Unidentified 1749 publication describing and engraving Smith’s picture groups","archive","Haskell says the New Testament pictures and Cignani cartoons were engraved and described in 1749; publication title and exact contents remain unresolved.",398),
    ("turin_series","Unidentified Sebastiano Ricci series for the court of Turin resembling Smith’s New Testament pictures","work","Haskell says the two series may be connected; retain the uncertainty and do not merge the groups.",398),
    ("special_room","Special room in Joseph Smith’s palace where the New Testament pictures hung","place","Interior room distinct from the palace and from the other room that held the Cignani cartoons; exact architectural identity is unknown.",398),
    ("second_room","Another room in Joseph Smith’s palace where the Cignani cartoons hung","place","Interior room distinct from the special room; no architectural name or location within the palace is supplied.",398),
]
newc, C = [], {}
for i,(key,name,kind,detail,line) in enumerate(NEW_SPECS,maximum+1):
    cid=f"cand-{i:04d}"
    if cid in cids: raise SystemExit(f"candidate id already exists: {cid}")
    C[key]=cid
    newc.append({"candidate_id":cid,"index_entry_id":"","canonical_name":name,
                 "index_page_range":"","suggested_type":kind,"status":"open",
                 "index_source_file":"","sub_entry":"","detail":detail,
                 "exclude_reason":"","candidate_origin":"body-mention",
                 "candidate_source_ref":f"{P302}#L{line}"})

newm=[]
def add_m(local,line,surface,cid,note="",occurrence=0):
    mid=f"m-chp10-p302-{local}"
    if mid in mids or any(row["mention_id"]==mid for row in newm): raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}: raise SystemExit(f"missing candidate for {mid}: {cid}")
    line_start,line_end=line_offsets[line],line_offsets[line]+len(src[line-1])
    positions,at=[],line_start
    while True:
        at=body.find(surface,at)
        if at<0 or at+len(surface)>line_end: break
        positions.append(at); at+=max(1,len(surface))
    if occurrence>=len(positions): raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start=positions[occurrence]; end=start+len(surface)
    if body[start:end]!=surface: raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id":mid,"segment_id":P302,"candidate_id":cid,
                 "surface_form":surface,"start_char":str(start),"end_char":str(end),"note":note})

M = [
    ("montagu",392,"Mary Wortley Montagu",E["montagu"],"Closes the page-end ‘Lady’ at p.301; cross-page subject resolution is recorded in the statement."),
    ("smith-service",392,"he rendered her a service",E["smith"],"Pronoun corefers to Joseph Smith; the service is not specified here."),
    ("james-adam",392,"James Adam",E["james_adam"],"Named speaker of the quoted criticism; footnote 1 identifies a letter to Robert Adam."),
    ("smith-flummery",392,"Smith’s flummery",E["smith"],"Smith is the subject of James Adam’s quoted criticism."),
    ("smith-favour",392,"he has some favour to ask",E["smith"],"Pronoun inside James Adam’s quotation corefers to Smith; preserve as the writer’s judgment."),
    ("smith-king",392,"the King",E["george_iii"],"Context refers to Smith’s dealings with George III; no separate royal identity inferred."),
    ("first-marriage",392,"first marriage",E["smith"],"Smith’s first marriage, as described by Haskell."),
    ("tofts",393,"Katherine Tofts",E["tofts"],"Named operatic singer; ‘rich but mad’ is Haskell’s characterization."),
    ("wynne-pursuit",393,"Giustiniana Wynne",E["wynne"],"Named object of Smith’s pursuit, as reported by Haskell."),
    ("smith-pursuit-coref",393,"his grotesque though pathetic pursuit",E["smith"],"Corefers to Smith in Haskell’s characterization of the pursuit."),
    ("second-marriage",393,"second marriage",E["smith"],"Smith’s second marriage, stated to have occurred when he was 82."),
    ("murray-sister",393,"the sister",C["murray_sister"],"Unidentified second wife; do not infer her name from the family relationship."),
    ("john-murray",393,"John Murray",E["john_murray"],"Named as the Resident; index candidate reused, identity alignment deferred to S3."),
    ("resident",393,"the Resident",E["john_murray"],"Appositional role of John Murray in this passage."),
    ("residency-job",393,"the very job that he had wanted", E["british_residency"], "The position Smith had sought; connects to the earlier Residency reference, not to John Murray’s personal identity."),
    ("smith-insisted-english",394,"he insisted on retaining",E["smith"],"Corefers to Smith in the account of retaining an English atmosphere abroad."),
    ("boccage",394,"Mme du Boccage",E["boccage"],"Visitor to Venice in 1757; the cited account is pending in the consolidated notes segment."),
    ("venice",394,"Venice",E["venice"],"City visited by Mme du Boccage."),
    ("palace-english-taste",394,"Smith’s palace",E["palazzo_balbi"],"Index subentry points to Palazzo Balbi; this passage does not name the palace, so identification with that building awaits S3."),
    ("english-taste",394,"English taste",C["english_taste"],"Phrase in Mme du Boccage’s quotation; footnote 2 remains pending."),
    ("italian-pictures",395,"Italian paintings",C["smith_italian_collection"],"Collective contents of Smith’s palace; individual works are not identified in this phrase."),
    ("palace-full",395,"this palace",E["palazzo_balbi"],"Corefers to Smith’s palace; same-building identity across dates remains for S3."),
    ("smith-collecting",395,"Smith turned first",E["smith"],"Named subject of the collecting account."),
    ("ricci-smith",395,"Sebastiano Ricci",E["ricci_smith"],"Index candidate for Ricci’s work for Smith reused."),
    ("venice-finest",395,"Venice",E["venice"],"City in Haskell’s comparison of Ricci’s standing."),
    ("lazzarini",395,"Lazzarini",E["lazzarini"],"Veteran painter described as virtually retired."),
    ("lazzarini-pupil",395,"his pupil",E["lazzarini"],"Possessive coreference to Lazzarini; the pupil is Tiepolo in the following clause."),
    ("tiepolo",396,"Tiepolo",E["tiepolo"],"Giambattista Tiepolo; the passage says he was not yet known beyond a restricted circle."),
    ("ricci-turin",396,"Ricci",E["ricci_turin"],"Sebastiano Ricci as artist in the Turin-employment comparison."),
    ("turin-court",396,"the court",E["court_turin"],"Institutional employer named by Haskell; the locative Turin is anchored separately."),
    ("turin-city",396,"Turin",E["turin"],"City in the employment and commission comparison."),
    ("church",396,"the Church",E["catholic_church"],"Institutional patronage referent; distinct from a church building."),
    ("smith-church-commissions",396,"Smith",E["smith"],"Named recipient/employer in Haskell’s contrast with Church commissions."),
    ("smith-bought-pictures",397,"Smith bought or commissioned",E["smith"],"Named buyer/commissioner of Ricci pictures."),
    ("ricci-artist",397,"the artist",E["ricci_smith"],"Corefers to Sebastiano Ricci."),
    ("smith-riccis",397,"many of them",C["smith_riccis"],"Corefers to the pictures bought or commissioned from Ricci."),
    ("veronese",397,"Veronese",E["veronese"],"Paolo Veronese, whose compositions are named as a source of adaptation."),
    ("seven-nt",398,"seven large pictures of themes from the New Testament",C["new_testament_pictures"],"Collective work candidate; no individual titles are given."),
    ("smith-hung-pictures",398,"he hung together",E["smith"],"Corefers to Smith as the person arranging the pictures in his palace."),
    ("special-room",398,"a special room",C["special_room"],"Interior space in the palace, distinct from the palace as a place."),
    ("palace-room",398,"his palace",E["palazzo_balbi"],"Smith’s palace; index suggests Palazzo Balbi but this passage alone does not settle identity."),
    ("engraved-described",398,"which he had engraved and described in 1749",C["smith_1749_publication"],"Unidentified publication/engraving activity; title and physical edition remain unresolved."),
    ("seven-cignani-cartoons",398,"seven cartoons",C["cignani_cartoons"],"Distinct group from the Ricci New Testament paintings; artist name is anchored separately."),
    ("cignani",398,"Carlo Cignani",E["cignani"],"Artist identified as Bolognese and admired in early eighteenth-century Venice."),
    ("another-room",398,"another room",C["second_room"],"Different room from the special room; exact architectural identity unknown."),
    ("these-paintings",398,"These paintings",C["new_testament_pictures"],"Corefers to the seven New Testament pictures by Ricci."),
    ("ricci-turin-series",398,"a similar series",C["turin_series"],"Potentially distinct Turin series; connection is qualified by Haskell as ‘may well’."),
    ("court-turin-series",398,"the court of Turin",E["court_turin"],"Institutional context of the possibly related series."),
    ("smith-riccis-group",399,"all Smith’s Riccis",C["smith_riccis"],"Collective group in Haskell’s acquisition hypothesis; the sentence continues on p.303."),
    ("artist-or-heirs",399,"the artist",E["ricci_smith"],"Sebastiano Ricci; the heirs mentioned in the alternative are unidentified and are not merged with him."),
]
for row in M: add_m(*row)

new_s=[]
def add_s(local,lo,hi,subject,obj,predicate,claim,qualification,relation=False,
          footnote=None,cross=None,layer="authorial narrative",speaker="Haskell"):
    sid=f"st-chp10-p302-{local}"
    if sid in sids or any(row["statement_id"]==sid for row in new_s): raise SystemExit(f"duplicate statement: {sid}")
    mentioned=[]
    for mention in newm:
        start=int(mention["start_char"])
        line_no=max((n for n,off in line_offsets.items() if off<=start),default=first)
        if lo<=line_no<=hi and mention["candidate_id"] not in mentioned: mentioned.append(mention["candidate_id"])
    qualifiers={"source_line_start":lo,"source_line_end":hi,"printed_page":PAGE,
                "pdf_physical_page":PHYSICAL,"claim":claim,"speaker":speaker,
                "text_layer":layer,"qualification":qualification,
                "mentioned_candidate_ids":mentioned,"relation_candidate":relation}
    if footnote is not None:
        qualifiers["footnote_marker"]=footnote
        qualifiers["footnote_text_pending"]=True
        qualifiers["cross_reference_segments"]=[NOTES]
    if cross:
        qualifiers["cross_reference_segments"]=list(dict.fromkeys(qualifiers.get("cross_reference_segments",[])+cross))
        qualifiers["cross_reference_printed_pages"]=[303 if P303 in cross else 301 if P301 in cross else 300 if P300 in cross else 302]
    new_s.append({"statement_id":sid,"segment_id":P302,"subject_candidate_id":subject,
                  "object_candidate_id":obj,"predicate":predicate,"qualifiers":qualifiers,
                  "original_quote":"\n".join(src[lo-1:hi]),"source_file":SOURCE_FILE,"origin":"book"})

add_s("montagu-service",392,392,E["montagu"],E["smith"],"found_smiths_self_congratulation_over_service_overwhelming",
      "Mary Wortley Montagu found Smith’s self-congratulation over the service he rendered her overwhelming.",
      "The service and context are not specified in this passage; this sentence closes the p.301 page-end ‘Lady’. ",relation=True,cross=[P301])
add_s("james-adam-criticism",392,392,E["james_adam"],E["smith"],"criticized_smiths_flummery_as_empty_words_used_to_seek_favour",
      "James Adam wrote that Smith’s ‘flummery’ was empty words with no meaning except when he wanted a favour.",
      "Nested quotation from a letter to Robert Adam cited in footnote 1; the letter is not independently read here.",relation=True,footnote=1,layer="nested correspondence quotation",speaker="James Adam")
add_s("haskell-unattractive-character",392,393,E["smith"],None,"authorial_portrait_of_unattractive_character",
      "Haskell says Smith seems vaguely unattractive across the centuries, citing his dealings with the King, first marriage, pursuit of Giustiniana Wynne and second marriage.",
      "Explicitly Haskell’s retrospective evaluation; the listed details are not independent proof of motive or character.",layer="authorial interpretation")
add_s("smith-first-marriage",392,393,E["smith"],E["tofts"],"first_marriage_to_katherine_tofts",
      "Haskell identifies Smith’s first marriage as being to Katherine Tofts, described by him as a rich but mad operatic singer.",
      "‘Rich but mad’ is Haskell’s characterization; the source does not independently establish a diagnosis.",relation=True)
add_s("smith-wynne-pursuit",393,393,E["smith"],E["wynne"],"pursued_giustiniana_wynne",
      "Haskell characterizes Smith’s pursuit of Giustiniana Wynne as grotesque though pathetic.",
      "The wording is Haskell’s evaluation; no private correspondence is read here.",relation=True,layer="authorial interpretation")
add_s("smith-second-marriage",393,393,E["smith"],C["murray_sister"],"second_marriage_at_82_to_sister_of_john_murray",
      "Haskell says Smith married at age 82 the sister of John Murray, identified as the Resident—the very post Smith had wanted.",
      "The wife’s name and identity remain unknown; John Murray is reused from the index, while ‘Resident’ is a role, not a second person.",relation=True,cross=[P300])
add_s("smith-retained-english-atmosphere",393,394,E["smith"],E["venice"],"retained_atmosphere_of_native_land_while_living_abroad",
      "Despite living abroad virtually all his life, Smith insisted on retaining the atmosphere of his native land, in Haskell’s comparison with Englishmen in similar circumstances.",
      "This is Haskell’s generalization; it should not be converted into a claim about all English expatriates.",layer="authorial generalization")
add_s("boccage-palace-english-taste",394,394,E["boccage"],E["palazzo_balbi"],"described_smiths_palace_as_entirely_in_english_taste_in_1757",
      "When Mme du Boccage visited Venice in 1757, she described Smith’s palace as entirely in the English taste, including its tables and gate locks.",
      "Quoted observation as reported by Haskell; footnote 2 remains pending, and the palace’s identity as Palazzo Balbi awaits S3.",relation=True,footnote=2,layer="nested travel observation")
add_s("palace-italian-paintings",395,395,E["palazzo_balbi"],C["smith_italian_collection"],"palace_filled_with_italian_paintings_not_all_suited_to_english_gentlemanly_taste",
      "Haskell says the palace was full of Italian paintings, not all of which would have suited the taste of an English gentleman at home.",
      "This is a general contrast, not an attribution of a particular taste to every English viewer.",layer="authorial interpretation")
add_s("smith-started-collecting-ricci",395,396,E["smith"],E["ricci_smith"],"began_collecting_in_1720s_and_first_turned_to_sebastiano_ricci",
      "When Smith began collecting in the 1720s, he first turned to Sebastiano Ricci, whom Haskell calls the finest painter in Venice at that time.",
      "The decade is approximate; ‘finest’ is Haskell’s evaluation.",relation=True,layer="authorial interpretation")
add_s("lazzarini-tiepolo-status",395,396,E["lazzarini"],E["tiepolo"],"lazzarini_nearly_retired_and_pupil_tiepolo_not_yet_known_beyond_small_circle",
      "Haskell says veteran Lazzarini had virtually retired and his pupil Tiepolo was still too young to be known outside a restricted circle.",
      "This is a time-specific account of their status in the passage, not a general assessment of either career.",relation=True)
add_s("ricci-employment-venice-turin",396,396,E["ricci_turin"],E["court_turin"],"employed_more_outside_venice_principally_by_court_of_turin",
      "Ricci was employed more outside Venice, principally by the court of Turin; in Venice his most important commissions were largely confined to the Church and thereafter Smith.",
      "‘Largely’ is retained; ‘the Church’ is treated as an institutional patron, not a specific church building.",relation=True)
add_s("smith-ricci-picture-style",397,397,E["smith"],C["smith_riccis"],"bought_or_commissioned_ricci_pictures_in_scintillating_manner_adapted_from_veronese",
      "Smith bought or commissioned Ricci pictures painted in what Haskell calls the artist’s most scintillating manner; many were freely adapted from Veronese.",
      "‘Many’ is not a count and the passage identifies no individual painting; footnote 3 remains pending.",relation=True,footnote=3)
add_s("seven-ricci-pictures-and-cignani-cartoons",398,398,E["smith"],C["new_testament_pictures"],"seven_new_testament_pictures_and_seven_cignani_cartoons_displayed_and_published",
      "Smith hung seven large Ricci pictures with New Testament themes in a special palace room and had them engraved and described in 1749; seven cartoons by Carlo Cignani were hung in another room.",
      "The work groups and rooms remain unidentified beyond this description; footnote 4 and the cited publication evidence remain pending.",relation=True,footnote=4)
add_s("possible-turin-series-connection",398,398,C["new_testament_pictures"],C["turin_series"],"may_be_connected_to_similar_ricci_series_for_court_of_turin",
      "Haskell says the Smith New Testament pictures may well be connected with a similar Ricci series for the court of Turin at about the same moment.",
      "The proposed connection is explicitly tentative; the two work groups remain separate candidates. The scanned footnote marker is 5; S0 OCR reads 6.",relation=True,footnote=5,layer="authorial hypothesis")
add_s("smith-ricci-acquisition-hypothesis",399,399,C["smith_riccis"],E["ricci_smith"],"possible_purchase_from_ricci_or_his_heirs_after_death",
      "Haskell says the quality of Smith’s Ricci paintings suggests they were bought from the artist or his heirs after his death, or that—if commissioned—Smith had not yet formed a distinctive taste.",
      "The sentence is incomplete at the p.302 page break and continues on p.303; preserve the alternative hypotheses without resolving them.",relation=True,cross=[P303],layer="authorial hypothesis")

all_ids=cids | {row["candidate_id"] for row in newc}
for row in new_s:
    q=row["qualifiers"]
    if q["source_line_start"]<first or q["source_line_end"]>last: raise SystemExit(f"statement range outside p.302: {row['statement_id']}")
    for cid in (row["subject_candidate_id"],row["object_candidate_id"]):
        if cid is not None and cid not in all_ids: raise SystemExit(f"missing statement FK {row['statement_id']} -> {cid}")
    if not q["mentioned_candidate_ids"]: raise SystemExit(f"statement has no anchored mention: {row['statement_id']}")
spans=sorted((int(r["start_char"]),int(r["end_char"]),r["mention_id"]) for r in newm)
for left,right in zip(spans,spans[1:]):
    if right[0]<left[1]: raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

cov[P301]["note"]="Printed p.301 body checked against CHP-10.pdf physical page 30. p.302 closes the p.301 continuation beginning ‘Lady’; footnotes 1–7 are still pending in the consolidated notes segment, so p.301 remains partial. Scan-only corrections include ‘Efe’→‘life’, ‘Eterature’→‘literature’, ‘LodoE’→‘Lodoli’, ‘EngEsh’→‘English’, ‘aU’→‘all’, and the line-end split ‘Rey-nolds’→‘Reynolds’; S0 unchanged."
cov[P302].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L391-399",
    "note":"Printed p.302 body checked against CHP-10.pdf physical page 31. Closed p.301’s dangling ‘Lady’ as Mary Wortley Montagu; recorded James Adam’s quoted criticism, Haskell’s evaluative portrait of Smith and his two marriages, the sister of John Murray as an unnamed second-wife candidate, Mme du Boccage’s 1757 description of Smith’s palace, the 1720s collecting account, Ricci’s Church/Turin/Smith commissions, Veronese adaptations, seven New Testament pictures, seven Cignani cartoons, their separate palace rooms, the 1749 engraving/description, and Haskell’s tentative link to a Turin series. Reused indexed candidates for Montagu, Adam, Smith, Tofts, Wynne, John Murray, George III, du Boccage, Venice, Palazzo Balbi cue, Ricci, Lazzarini, Tiepolo, Turin, the Catholic Church, Veronese and Cignani; added distinct candidates for the unnamed wife, English taste, Smith’s Ricci holdings, both work groups, 1749 publication and separate rooms. Scan-only corrections: L398 footnote OCR ‘6’ reads printed note 5; L399 ‘sine quality’ reads ‘fine quality’. L400 is a note excerpt reserved for the consolidated notes segment; L399’s acquisition hypothesis continues at p.303, so this segment remains partial."})

summary={"mode":"APPLY" if sys.argv[-1:]==["--apply"] else "DRY-RUN","segment":P302,
         "segment_sha256":digest,"new_candidates":len(newc),"candidate_ids":[r["candidate_id"] for r in newc],
         "new_mentions":len(newm),"new_statements":len(new_s),"coverage":{"p301":cov[P301]["migration_status"],"p302":cov[P302]["migration_status"],"p303":cov[P303]["migration_status"]}}
print(json.dumps(summary,ensure_ascii=False,indent=2))
if sys.argv[-1:]==["--apply"]:
    for path in (cp,mp,sp,vp):
        backup=Path(str(path)+BACKUP)
        if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.302 S2 body migration; p.302 footnotes remain in the consolidated notes segment.")
