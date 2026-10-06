"""Controlled S2 migration for p.285; dry-run unless --apply is passed."""
import csv, hashlib, json, re, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
PREV = "chp-10:10_CHP-10_intro:l167-176"
SEG = "chp-10:10_CHP-10_intro:l178-188"
NEXT = "chp-10:10_CHP-10_intro:l190-204"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "fe0b7c76df4864bfaaa923d9841aca2064faaee70662231b71abd74444a8f5ee"
MAX_CAND = 8966
BACKUP = ".bak-s2-chp10-p285-20261002"


def read_csv(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def read_jsonl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def write_csv(p, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=p.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(p)


def write_jsonl(p, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=p.parent, delete=False) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(p)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(src[177:188])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != SEG_SHA or src[177].strip() != "[Page 285]":
    raise SystemExit("p.285 source segment hash/page mismatch")

cp, mp, sp, vp = [TABLES / n for n in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {r["candidate_id"] for r in candidates}
mids = {r["mention_id"] for r in mentions}
sids = {r["statement_id"] for r in statements}
cov = {r["segment_id"]: r for r in coverage}
maximum = max(int(re.search(r"\d+", r["candidate_id"]).group()) for r in candidates)
if maximum != MAX_CAND:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")), (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "pellegrini":"cand-1862", "mississippi_gallery":"cand-8963", "mississippi_programme":"cand-8964",
    "banque_royale":"cand-8965", "systeme":"cand-8966", "crozat":"cand-0894",
    "crozat_house":"cand-8846", "carriera":"cand-0581", "john_law":"cand-1367",
    "regent":"cand-1786", "king":"cand-1448", "louis_xiv":"cand-1447",
    "paris":"cand-4653", "london":"cand-1422", "dusseldorf":"cand-0955",
    "seine":"cand-6872", "mariette":"cand-1547", "rigaud":"cand-2198",
    "watteau":"cand-2804", "coypel":"cand-0866", "vleughels":"cand-2789",
    "oppenord":"cand-1781", "troy":"cand-2656",
}
for k, v in E.items():
    if v not in cids:
        raise SystemExit(f"missing candidate {k}={v}")

NEW_SPECS = [
    ("mississippi_river","Mississippi River depicted in Pellegrini's gallery frescoes","place",
     "The river is named as a figure in the fresco scene; the representation is distinguished from the Mississippi Gallery and John Law's scheme.",179),
    ("bourse","Paris Bourse depicted in the Mississippi Gallery frescoes","place",
     "Haskell describes a view of the Bourse with men bargaining as part of the fresco imagery; no specific building or institution identity is supplied.",179),
    ("academie","Académie to which Rosalba Carriera was admitted (p.285; identity pending)","institution",
     "The source calls it the Académie without a full name; formal identity is deferred to S3.",185),
    ("carriera_portrait_group","Unidentified informal Paris portraits by Rosalba Carriera, including sitters named by Haskell","work",
     "Haskell describes Carriera's informal Paris portraits and names several sitters painted within two or three months of her arrival; individual portraits are not titled or located.",185),
    ("pellegrini_altarpiece","Unidentified altarpiece painted by Giovanni Antonio Pellegrini in Paris","work",
     "Haskell says Pellegrini painted at least one altarpiece in Paris; no title, date, patron, or location is supplied.",183),
    ("french_painting_early18","French painting of the first half of the eighteenth century","term",
     "Art-historical field used in Haskell's qualified claim about the frescoes' influence.",182),
    ("elegant_intimate_portraiture","Elegant yet intimate portraiture as a French eighteenth-century style","term",
     "Stylistic category in Haskell's interpretation of Carriera's influence; not treated as a pre-set project theme.",187),
    ("religion_role","Religion personified in Pellegrini's Mississippi Gallery iconography","",
     "Image role in the fresco scheme; current taxonomy does not represent personified iconographic roles distinctly, so type remains undecided.",179),
    ("commerce_role","Commerce personified in Pellegrini's Mississippi Gallery iconography","",
     "Image role in the fresco scheme; current taxonomy does not represent personified iconographic roles distinctly, so type remains undecided.",179),
    ("richesse_role","Richesse (Wealth) personified in Pellegrini's Mississippi Gallery iconography","",
     "Image role named in the French inscription; type remains undecided pending an adequate iconographic-role representation.",179),
    ("surete_role","Sûreté (Security) personified in Pellegrini's Mississippi Gallery iconography","",
     "Image role named in the French inscription; type remains undecided pending an adequate iconographic-role representation.",179),
    ("credit_role","Crédit (Credit) personified in Pellegrini's Mississippi Gallery iconography","",
     "Image role named in the French inscription; type remains undecided pending an adequate iconographic-role representation.",179),
    ("olympian_group","Unspecified gods of Olympus called into Pellegrini's Mississippi Gallery iconography","",
     "Collective mythological image role; individual gods are unnamed and current taxonomy does not represent depicted roles distinctly.",179),
    ("munificence_role","Munificence represented by an unnamed Olympian figure in the Mississippi Gallery scheme","",
     "Personified virtue in Haskell's description; image role remains type-undecided.",179),
    ("magnanimity_role","Magnanimity represented by an unnamed Olympian figure in the Mississippi Gallery scheme","",
     "Personified virtue in Haskell's description; image role remains type-undecided.",179),
    ("river_embrace_role","Embracing Seine and Mississippi river figures in the Mississippi Gallery frescoes","",
     "Haskell describes the rivers as seen embracing; this is iconographic content, not a claim that the geographical rivers meet.",179),
]
newc, C = [], {}
for i, (key,name,kind,detail,line) in enumerate(NEW_SPECS, MAX_CAND+1):
    cid=f"cand-{i:04d}"
    if cid in cids or any(r["canonical_name"]==name and r["suggested_type"]==kind for r in candidates):
        raise SystemExit(f"candidate already exists: {cid} {name}")
    C[key]=cid
    newc.append({"candidate_id":cid,"index_entry_id":"","canonical_name":name,"index_page_range":"",
                 "suggested_type":kind,"status":"open","index_source_file":"","sub_entry":"",
                 "detail":detail,"exclude_reason":"","candidate_origin":"body-mention",
                 "candidate_source_ref":f"{SEG}#L{line}"})

offsets, offset = {}, 0
for n in range(178,189):
    offsets[n]=offset
    offset += len(src[n-1])+1
newm=[]


def add_m(local,line,surface,cid,note="",occurrence=0):
    mid=f"m-chp10-p285-{local}"
    if mid in mids or any(r["mention_id"]==mid for r in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {r["candidate_id"] for r in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    positions, at=[],0
    while True:
        at=src[line-1].find(surface,at)
        if at<0: break
        positions.append(at)
        at+=max(1,len(surface))
    if occurrence>=len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}")
    a=offsets[line]+positions[occurrence]; b=a+len(surface)
    if body[a:b]!=surface: raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id":mid,"segment_id":SEG,"candidate_id":cid,"surface_form":surface,
                 "start_char":str(a),"end_char":str(b),"note":note})


MENTIONS = [
("pellegrini_he",179,"He",E["pellegrini"],"Continuation refers to Pellegrini."),
("banque",179,"Banque",E["banque_royale"],"French name in the programme quotation."),
("roi",179,"Roi",E["king"],"French term for the King in the commission's quoted programme."),
("regent_fr",179,"Régent",E["regent"],"French title refers to the Regent; identity remains for S3."),
("king",179,"The King",E["king"],"Depicted king, linked to the indexed Louis XV candidate for S3 review."),
("religion",179,"Religion",C["religion_role"],"Personified iconographic role, not an ordinary person."),
("regent",179,"the Régent",E["regent"],"Depicted Regent; preserve source title."),
("commerce",179,"le Commerce",C["commerce_role"],"Personified image role in the French description."),
("richesse",179,"la Richesse",C["richesse_role"],"Personified image role; retain French wording."),
("surete",179,"la Sûreté",C["surete_role"],"Personified image role; retain French wording."),
("credit",179,"du Crédit",C["credit_role"],"Personified image role; not financial evidence."),
("olympus",179,"all the gods of Olympus",C["olympian_group"],"Collective depicted roles; individual gods unnamed."),
("munificence",179,"Munificence",C["munificence_role"],"Virtue personified by an unspecified Olympian figure."),
("magnanimity",179,"Magnanimity",C["magnanimity_role"],"Virtue personified by an unspecified Olympian figure."),
("seine",179,"the Seine",E["seine"],"Geographical river represented in the fresco scene."),
("mississippi",179,"the Mississippi",C["mississippi_river"],"River shown as embracing the Seine; distinct from the Gallery."),
("bourse",179,"the Bourse",C["bourse"],"Market/building depicted in a view; exact identity remains open."),
("systeme",180,"Système",E["systeme"],"John Law's scheme, not the Gallery or its frescoes."),
("frescoes",180,"the frescoes",E["mississippi_programme"],"The destroyed fresco cycle is the p.284 programme work."),
("mariette",180,"Mariette",E["mariette"],"Later commentator on the frescoes."),
("french_painting",182,"French painting",C["french_painting_early18"],"Field in Haskell's qualified influence claim."),
("pellegrini_paris",183,"Pellegrini",E["pellegrini"],"Artist's other Paris works."),
("paris_altarpiece",183,"Paris",E["paris"],"City of the reported altarpiece."),
("altarpiece",183,"altarpiece",C["pellegrini_altarpiece"],"At least one unidentified work; not expanded into multiple altarpieces."),
("rosalba",183,"Rosalba",E["carriera"],"Carriera identified by the current context."),
("crozat_welcome",183,"Crozat",E["crozat"],"Host and patron named in Haskell's account."),
("crozat_house",184,"his house",E["crozat_house"],"Possessive refers to Crozat's Paris house."),
("carriera_portraits",184,"her informal portraits",C["carriera_portrait_group"],"Work group described by Haskell."),
("louis_xiv",185,"Louis XIV",E["louis_xiv"],"Named as the court whose style the society opposed."),
("law_portrait",185,"John Law",E["john_law"],"Named portrait sitter."),
("regent_portrait",185,"the Régent",E["regent"],"Named by title as a portrait sitter."),
("little_king",185,"the little King",E["king"],"Title-only sitter; identity not independently aligned here."),
("crozat_portraits",185,"Crozat",E["crozat"],"Crozat and his family are among the portrait sitters."),
("carria_admission",185,"the Académie",C["academie"],"Institution named without its full formal title."),
("rigaud",186,"Rigaud",E["rigaud"],"Named artist who met Carriera and expressed admiration."),
("watteau",186,"Watteau",E["watteau"],"Named artist who met Carriera and expressed admiration."),
("coypel",186,"Coypel",E["coypel"],"Named among artists and connoisseurs."),
("vleughels",186,"Vleughels",E["vleughels"],"Named among artists and connoisseurs."),
("oppenord",186,"Oppenord",E["oppenord"],"Named among artists and connoisseurs."),
("troy",186,"de Troy",E["troy"],"Named among artists and connoisseurs; candidate identity is deferred to S3."),
("mariette_list",186,"Mariette",E["mariette"],"Named among artists and connoisseurs."),
("paris_departure",187,"Paris",E["paris"],"City Carriera left in March 1721."),
    ("intimate_portraiture",187,"intiniate portraiture",C["elegant_intimate_portraiture"],"OCR typo; print reads 'intimate portraiture'."),
("french_eighteenth",187,"French eighteenth-century painting",C["french_painting_early18"],"Art-historical field in Haskell's evaluation."),
("london_centres",188,"London",E["london"],"City named as a centre in the next section's opening."),
("dusseldorf_centres",188,"Diisseldorf",E["dusseldorf"],"Printed Düsseldorf is OCRed as Diisseldorf; correction logged at S2 only."),
("paris_centres",188,"Paris",E["paris"],"City named as a centre in the next section's opening."),
]
for m in MENTIONS:
    add_m(*m)

new_s=[]


def q(start,end):
    a=body.find(start)
    if a<0: raise SystemExit(f"quote start absent: {start!r}")
    b=body.find(end,a)
    if b<0: raise SystemExit(f"quote end absent: {end!r}")
    return body[a:b+len(end)]


def add_s(sid,lo,hi,subj,obj,pred,start,end,claim,qualification,mentioned,
          speaker="Haskell",layer="authorial narrative",relation=False,cross=None,footnote=None):
    if sid in sids or any(r["statement_id"]==sid for r in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    quals={"source_line_start":lo,"source_line_end":hi,"printed_page":285,"pdf_physical_page":14,
           "claim":claim,"speaker":speaker,"text_layer":layer,"qualification":qualification,
           "mentioned_candidate_ids":mentioned,"relation_candidate":relation}
    if footnote is not None:
        quals["footnote_marker"]=footnote
        quals["footnote_text_pending"]=True
    if cross: quals["cross_reference_segments"]=cross
    new_s.append({"statement_id":sid,"segment_id":SEG,"subject_candidate_id":subj,
                  "object_candidate_id":obj,"predicate":pred,"qualifiers":quals,
                  "original_quote":q(start,end),"source_file":SOURCE_FILE,"origin":"book"})


# The p.284 opening statement closes at p.285 L179.
p284_open=next((r for r in statements if r["statement_id"]=="st-chp10-p284-mississippi-programme-open"),None)
if not p284_open or p284_open["segment_id"]!=PREV:
    raise SystemExit("expected p.284 open Mississippi programme statement missing")
p284_open["qualifiers"]["claim"]="Haskell describes Pellegrini's Mississippi Gallery programme as combining royal glorification in the Versailles manner with allegorical tributes to commerce, which he says became general only in the second half of the eighteenth century."
p284_open["qualifiers"]["qualification"]="The sentence is now closed by p.285 L179; retain Haskell's periodizing comparison."
p284_open["qualifiers"]["continuation_quote"]="eighteenth century."
p284_open["qualifiers"]["cross_reference_segments"]=[{"segment_id":SEG,"source_line_start":179,"source_line_end":179}]
p284_open["qualifiers"]["footnote_marker"]=1
p284_open["qualifiers"]["footnote_text_pending"]=True
add_s("st-chp10-p285-french-gallery-inscription",179,179,E["pellegrini"],E["mississippi_programme"],
      "programme_instruction_glorified_bank_king_and_regent","He was to express","Mgr le Régent’.",
      "Haskell quotes the programme as directing Pellegrini to express the Bank's advantages and refer them to the glory of the King and Regent.",
      "The French wording is a nested programme quotation; note 1's cited document is not yet consulted.",
      [E["banque_royale"],E["king"],E["regent"]],layer="authorial report of quoted programme",relation=True,footnote=1)
add_s("st-chp10-p285-mythological-iconography",179,179,E["mississippi_programme"],None,
      "mississippi_programme_used_strained_mythological_iconography","This extraordinary task was achieved",
      "the countless other virtues which characterised the scheme.",
      "Haskell says the programme used what he calls a somewhat strained mythological iconography: the King was central with Religion and the Regent; Commerce, Wealth, Security and Credit surrounded them; Olympian gods represented Munificence, Magnanimity and other virtues.",
      "These are depicted iconographic roles, not independent real persons; retain type-undecided candidate records for personifications.",
      [E["king"],C["religion_role"],E["regent"],C["commerce_role"],C["richesse_role"],C["surete_role"],C["credit_role"],C["olympian_group"],C["munificence_role"],C["magnanimity_role"]],layer="authorial iconographic description")
add_s("st-chp10-p285-rivers-bourse-imagery",179,179,E["mississippi_programme"],None,
      "frescoes_depicted_river_embrace_ports_ships_and_bourse","Elsewhere the Seine and the Mississippi were seen embracing",
      "made the same points in more concrete terms.",
      "Haskell says the frescoes showed the Seine and Mississippi embracing, along with views of ports and ships and the Bourse with men bargaining.",
      "This describes imagery within the frescoes, not a real meeting of the rivers or a specified Bourse building.",
      [E["seine"],C["mississippi_river"],C["bourse"],C["river_embrace_role"],E["mississippi_programme"]],layer="authorial iconographic description")
add_s("st-chp10-p285-fresco-destruction-after-systeme-collapse",180,180,E["mississippi_programme"],E["systeme"],
      "mississippi_frescoes_destroyed_soon_after_systeme_collapse","Exactly how well he coped with the commission",
      "had celebrated.",
      "Haskell says the frescoes were destroyed soon after the collapse of the Système they had celebrated.",
      "The source gives relative sequence only; it does not specify a destruction date or mechanism.",
      [E["pellegrini"],E["systeme"]],relation=True)
add_s("st-chp10-p285-mariette-assessment",180,181,E["mariette"],E["mississippi_programme"],
      "mariette_condemned_destruction_but_criticised_frescoes","Years later, when the whole climate of taste had changed",
      "but he criticised the drawing and colour.",
      "Haskell says Mariette later condemned the frescoes' destruction, praised their invention and agreeable grouping in a quoted passage, but criticized drawing and colour.",
      "Mariette is reported through Haskell; the cited Abecedario passage in note 2 remains unread.",
      [E["mariette"],E["mississippi_programme"]],speaker="Haskell reporting Mariette",layer="authorial report with nested quotation",footnote=2)
add_s("st-chp10-p285-likely-influence-french-painting",181,182,E["mississippi_programme"],C["french_painting_early18"],
      "mississippi_frescoes_likely_influenced_french_painting","None the less it seems likely",
      "French painting of the first half of the eighteenth century.",
      "Haskell says it seems likely that the frescoes had considerable influence on French painting in the first half of the eighteenth century.",
      "Preserve 'seems likely' as Haskell's qualified art-historical interpretation.",
      [E["mississippi_programme"],C["french_painting_early18"]],layer="authorial interpretation")
add_s("st-chp10-p285-pellegrini-other-paris-works",183,183,E["pellegrini"],E["paris"],
      "pellegrini_painted_other_paris_works_including_at_least_one_altarpiece","Pellegrini painted other works in Paris",
      "including at least one altarpiece,",
      "Haskell says Pellegrini painted other works in Paris, including at least one altarpiece.",
      "Only a minimum count is stated; the altarpiece is unidentified and note 3 remains pending.",
      [C["pellegrini_altarpiece"]],relation=True,footnote=3)
add_s("st-chp10-p285-carriera-trip-success",183,183,E["carriera"],None,
      "haskell_attributes_real_success_of_paris_trip_to_rosalba","but the real success of the trip was due to Rosalba.",
      "but the real success of the trip was due to Rosalba.",
      "Haskell attributes the real success of the Paris trip to Rosalba Carriera.",
      "This is Haskell's evaluative conclusion, not a measurable outcome.",
      [E["pellegrini"],E["carriera"]],layer="authorial interpretation")
add_s("st-chp10-p285-crozat-welcomed-and-hosted-carriera",183,184,E["crozat"],E["carriera"],
      "crozat_welcomed_lodged_and_hosted_carriera","She was welcomed by Crozat",
      "in her honour,",
      "Haskell says Crozat welcomed Carriera, lodged her in his house, and organized receptions in her honour.",
      "The house is the previously reused Paris residence candidate; no new residence is inferred.",
      [E["crozat_house"]],relation=True)
add_s("st-chp10-p285-carriera-portrait-response",184,185,E["carriera"],None,
      "carriera_informal_portraits_welcomed_by_society_opposed_to_louis_xiv_style",
      "the delicate and subtle flattery of her informal portraits",
      "Louis XIV and his court.",
      "Haskell says Carriera's informal portraits were enthusiastically received by a society revolting against the artificiality and stiffness associated with Louis XIV and his court.",
      "Retain Haskell's characterization of the society and court style.",
      [E["crozat"],E["louis_xiv"],C["carriera_portrait_group"]],layer="authorial interpretation")
add_s("st-chp10-p285-carriera-painted-sitters",185,185,E["carriera"],C["carriera_portrait_group"],
      "carriera_painted_portraits_of_law_regent_king_crozat_family",
      "Within two or three months of her arrival she had painted the portraits of John Law",
      "Crozat and his family.",
      "Haskell says that within two or three months of arriving, Carriera painted portraits of John Law, the Regent, the young King, Crozat and his family.",
      "No titles, exact dates, or current locations are supplied for these portraits.",
      [E["john_law"],E["regent"],E["king"],E["crozat"]],relation=True)
add_s("st-chp10-p285-sitters-during-painting",185,185,E["king"],None,
      "young_king_kept_quiet_during_portrait_sitting","who kept flatteringly quiet",
      "during the sittings—",
      "Haskell says the young King kept quiet during the portrait sittings, a behavior he calls flattering.",
      "The source does not identify the sitter by name in this sentence; the linked candidate remains pending S3.",
      [C["carriera_portrait_group"]],layer="authorial interpretation")
add_s("st-chp10-p285-portrait-demand",185,185,None,C["carriera_portrait_group"],
      "aristocrats_and_ambassadors_sought_carriera_portraits",
      "Round these central figures flocked the aristocrats and the ambassadors",
      "portraits or little mythological pictures.",
      "Haskell says aristocrats and ambassadors flocked around the central figures, competing for portraits or small mythological pictures.",
      "The groups and individual pictures are not named; do not create one entity per unnamed sitter or picture.",
      [E["carriera"],E["john_law"],E["regent"],E["king"],E["crozat"]],layer="authorial report")
add_s("st-chp10-p285-carriera-academie-admission",185,185,E["carriera"],C["academie"],
      "carriera_admitted_unanimously_to_academie_by_october",
      "By October, four months after her arrival, she heard the news",
      "No vote was taken, as no-one wanted to make use of a black ball.",
      "Haskell quotes Carriera saying she had been unanimously admitted to the Académie by October, four months after her arrival.",
      "The quoted letter is reported through Haskell; the institution's full identity and note 4's source remain pending.",
      [E["paris"]],speaker="Rosalba Carriera as quoted by Haskell",layer="nested letter quotation",relation=True,footnote=4)
add_s("st-chp10-p285-carriera-met-artists",186,186,E["carriera"],None,
      "carriera_met_rigaud_watteau_and_other_artists_connoisseurs",
      "She met Rigaud and Watteau",
      "Coypel, Vleughels, Oppenord, de Troy, Mariette.",
      "Haskell says Carriera met Rigaud and Watteau, who expressed admiration, and lists Coypel, Vleughels, Oppenord, de Troy and Mariette among the other artists and connoisseurs.",
      "The list is preserved as Haskell's account of her Paris contacts; no individual encounter details are added.",
      [E["rigaud"],E["watteau"],E["coypel"],E["vleughels"],E["oppenord"],E["troy"],E["mariette"]],relation=True)
add_s("st-chp10-p285-carriera-departure-legacy",187,187,E["carriera"],E["paris"],
      "carriera_left_paris_1721_and_kept_friends_until_death_1757",
      "When she left Paris in March 1721",
      "through every change of taste until her death in 1757.",
      "Haskell says Carriera left Paris in March 1721 and made friends and admirers who remained loyal to her through changes of taste until her death in 1757.",
      "Haskell's phrase that she 'conquered the city' is rhetorical; it is not treated as a literal institutional outcome.",
      [],layer="authorial narrative")
add_s("st-chp10-p285-carriera-stylistic-influence",187,187,E["carriera"],C["elegant_intimate_portraiture"],
      "carriera_stimulated_elegant_intimate_portraiture",
      "More importantly she gave a stimulus",
      "one of the triumphs of French eighteenth-century painting.",
      "Haskell says Carriera stimulated an elegant yet intimate portraiture that others developed to greater heights, and calls it one of the triumphs of French eighteenth-century painting.",
      "This is Haskell's evaluative interpretation, not a pre-set theme or verified influence chain.",
      [C["french_painting_early18"]],layer="authorial interpretation")
add_s("st-chp10-p285-next-section-opening",188,188,None,None,
      "london_dusseldorf_paris_as_exciting_centres_open",
      "The cities of London, Diisseldorf and Paris were the most exciting centres of",
      "The cities of London, Diisseldorf and Paris were the most exciting centres of",
      "The next subsection opens by calling London, Düsseldorf and Paris the most exciting centres of an as-yet-unfinished subject.",
      "The sentence continues at p.286; the centered section marker is layout, not prose.",
      [E["london"],E["dusseldorf"],E["paris"]],layer="section-opening authorial generalization",
      cross=[{"segment_id":NEXT,"source_line_start":190,"source_line_end":204}])

# Close the p.284 sentence with p.285 L179 and set the p.285 next continuation.
if "p.285" not in cov[PREV]["note"]:
    raise SystemExit("p.284 coverage note does not contain the expected open continuation")
cov[PREV].update({"migration_status":"complete","source_line_ranges":"L168-176; p.285 L179",
 "note":"Printed p.284 was read against physical page 13. Its Mississippi Gallery programme sentence closes at p.285 L179; continuation is cross-linked. The page's notes 1-5 remain pending in the consolidated notes segment."})
cov[SEG].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L179-188",
 "note":"Printed p.285 read against CHP-10.pdf physical page 14. Closed the p.284 programme comparison; recorded the quoted French brief, iconographic personifications and river/Bourse imagery, destruction after the Système collapse, Mariette's later mixed assessment, and Haskell's qualified influence claim. Also recorded Pellegrini's Paris work, Carriera's reception and named portrait sitters, her Académie admission quotation, Paris contacts, departure and stylistic legacy. Personified visual roles remain type-undecided rather than being forced into person/work; unnamed sitters and works stay grouped. Scan-only corrections: L181 'saidThat'->'said that'; L184 stray apostrophe before 'her' removed; L187 'a. number'->'a number' and 'intiniate'->'intimate'; L188 separates the centered section marker from text and corrects 'Diisseldorf' to 'Düsseldorf'. S0 unchanged. Notes 1-4 at consolidated source L528-531 remain pending. The new section sentence at L188 continues at p.286 L190, so coverage remains partial."})
cov[NEXT]["note"]="Next source-order segment is printed p.286 at L190; close the p.285 opening sentence about London, Düsseldorf and Paris before marking p.285 complete."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:]==["--apply"] else "DRY-RUN",
 "segment":SEG,"new_candidates":len(newc),"new_mentions":len(newm),"new_statements":len(new_s),
 "candidate_range":[newc[0]["candidate_id"],newc[-1]["candidate_id"]],
 "coverage":{"p284":cov[PREV]["migration_status"],"p285":cov[SEG]["migration_status"],"p286":cov[NEXT]["migration_status"]}},
 ensure_ascii=False,indent=2))

if sys.argv[-1:]==["--apply"]:
    for p in (cp,mp,sp,vp):
        b=Path(str(p)+BACKUP)
        if b.exists(): raise SystemExit(f"backup already exists: {b}")
        shutil.copy2(p,b)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[r["segment_id"]] for r in coverage])
    print("Applied p.285 S2 migration and closed p.284 programme sentence; backups retained.")
