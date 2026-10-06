"""Controlled S2 migration for p.282; dry-run unless --apply is passed."""
import csv, hashlib, json, re, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
PREV = "chp-10:10_CHP-10_intro:l125-139"
SEG = "chp-10:10_CHP-10_intro:l141-149"
NEXT = "chp-10:10_CHP-10_intro:l151-165"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "813500dc1bffa25162b5ff929a4545f93048788e5a6a3cd4bad430c8428b7450"
OPEN_ID = "st-chp10-p281-johann-wilhelm-accession-revolt"
MAX_CAND = 8950
BACKUP = ".bak-s2-chp10-p282-20261002"

def read_csv(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)

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
body = "\n".join(src[140:149])
if hashlib.sha256(body.encode()).hexdigest() != SEG_SHA or src[140].strip() != "[Page 282]":
    raise SystemExit("p.282 source segment hash/page mismatch")
if not src[141].startswith("but soon after, his fortunes turned.") or not src[148].startswith("For references to Francesco Trevisani and Balestra"):
    raise SystemExit("expected p.282 text changed")

cp, mp, sp, vp = [TABLES / f for f in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp); mf, mentions = read_csv(mp); vf, coverage = read_csv(vp); statements = read_jsonl(sp)
cids = {r["candidate_id"] for r in candidates}; mids = {r["mention_id"] for r in mentions}
sids = {r["statement_id"] for r in statements}; cov = {r["segment_id"]: r for r in coverage}
if max(int(re.search(r"\d+", r["candidate_id"]).group()) for r in candidates) != MAX_CAND:
    raise SystemExit("candidate sequence changed")
for sid, state in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")), (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != state:
        raise SystemExit(f"unexpected coverage state {sid}: {row}")
old = next((r for r in statements if r["statement_id"] == OPEN_ID), None)
if not old or old["segment_id"] != PREV or not old["original_quote"].endswith("a serious revolt,"):
    raise SystemExit("p.281 cross-page statement changed or missing")

E = {"johann":"cand-1325", "rapparini":"cand-2107", "alexander":"cand-3442", "dusseldorf":"cand-0955",
     "gruppello":"cand-1236", "palatinate":"cand-3947", "flanders":"cand-4652", "anna":"cand-1606",
     "maratta":"cand-1526", "rome":"cand-4490", "italy":"cand-3461", "giordano":"cand-1172",
     "cignani":"cand-0748", "franceschini":"cand-1069", "dal_sole":"cand-2480", "trevisani":"cand-2650",
     "balestra":"cand-0168", "carriera":"cand-0581", "bologna":"cand-3398", "venice":"cand-3401"}
for k, v in E.items():
    if v not in cids: raise SystemExit(f"required candidate missing: {k}={v}")

newc = [{"candidate_id":"cand-8951", "index_entry_id":"", "canonical_name":"Bronze equestrian statue of Johann Wilhelm by Gabriel Gruppello",
         "index_page_range":"", "suggested_type":"work", "status":"open", "index_source_file":"", "sub_entry":"",
         "detail":"Haskell names it as an example of art at Düsseldorf inspired by Johann Wilhelm's passion for self-display; no date or current location is supplied.",
         "exclude_reason":"", "candidate_origin":"body-mention", "candidate_source_ref":f"{SEG}#L143"}]
if newc[0]["candidate_id"] in cids or any(r["canonical_name"] == newc[0]["canonical_name"] and r["suggested_type"] == "work" for r in candidates):
    raise SystemExit("statue candidate ID/natural key already exists")
C = {"statue":"cand-8951"}
offsets = {}; offset = 0
for n in range(141, 150): offsets[n] = offset; offset += len(src[n-1]) + 1
newm = []
def m(local, line, surface, key, note, occurrence=0, new=False):
    mid = f"m-chp10-p282-{local}"
    cid = C[key] if new else E[key]
    if mid in mids or any(r["mention_id"] == mid for r in newm) or cid not in (cids | {"cand-8951"}):
        raise SystemExit(f"duplicate ID or missing candidate: {mid} -> {cid}")
    pos = []; at = 0
    while True:
        at = src[line-1].find(surface, at)
        if at < 0: break
        pos.append(at); at += 1
    if occurrence >= len(pos): raise SystemExit(f"surface absent at L{line}: {surface!r}")
    a = offsets[line] + pos[occurrence]; b = a + len(surface)
    if body[a:b] != surface: raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id":mid,"segment_id":SEG,"candidate_id":cid,"surface_form":surface,
                 "start_char":str(a),"end_char":str(b),"note":note})

MENTIONS = [
 ("he_politics",142,"he","johann","Pronoun continues the Johann Wilhelm account from p.281."),
 ("intrigues",142,"his intrigues","johann","Refers to Johann Wilhelm."),
 ("palatinate",142,"the Palatinate","palatinate","Territory in a qualified political prospect."),
 ("love_glory",142,"His love of glory","johann","Refers to Johann Wilhelm."),
 ("surrounded",142,"him","johann","Refers to Johann Wilhelm."),
 ("rapparini",142,"Giorgio MariaRapparini","rapparini","OCR merges the printed line-break name; normalized boundary noted."),
 ("master",142,"his master’s name","johann","Johann Wilhelm is Rapparini's master in this account."),
 ("alexander",142,"Alexander the Great","alexander","Rapparini's comparison for Johann Wilhelm."),
 ("dusseldorf",143,"Dusseldorf","dusseldorf","OCR omits the printed umlaut."),
 ("statue_elector",143,"the Elector’s","johann","Refers to Johann Wilhelm."),
 ("statue",143,"the bronze equestrian statue","statue","The work by Gabriel Gruppello.",0,True),
 ("gruppello",143,"Gabriel Gruppello","gruppello","Sculptor named by Haskell."),
 ("he_art",143,"he","johann","Refers to Johann Wilhelm."),
 ("flanders",143,"Flandre","flanders","French reference to Flanders in Rapparini's nested quotation."),
 ("marriage",143,"Johann Wilhelm’s","johann","Marriage is presented as a possible stimulus to collecting and patronage."),
 ("anna",143,"Anna Maria Ludovica","anna","Named as Johann Wilhelm's wife and the last of the Medici."),
 ("rapparini_guidance",143,"Rapparini","rapparini","Named as guiding the patronage."),
 ("maratta",143,"Carlo Maratta","maratta","Named as Rapparini's teacher."),
 ("rome",143,"Rome","rome","Location of Rapparini's study under Maratta."),
 ("rapparini_writings",143,"Rapparini","rapparini","Subject of Haskell's assessment of the writings.",1),
 ("rapparini_possessive",143,"his","rapparini","Refers to Rapparini's writings."),
 ("johann_collection",145,"Johann Wilhelm","johann","Collector and patron."),
 ("italy",146,"Italy","italy","Source region for works; note marker 2 follows."),
 ("giordano",146,"Luca Giordano","giordano","Especially prominent among works from Italy."),
 ("cignani",146,"Cignani","cignani","Painter commissioned to work for Johann Wilhelm."),
 ("franceschini",147,"Franceschini","franceschini","Marcantonio Franceschini, provisionally as indexed."),
 ("dal_sole",147,"Gian Gioseffo dal Sole","dal_sole","Painter named in the commission passage."),
 ("trevisani",147,"Francesco Trevisani","trevisani","Painter named in the commission passage."),
 ("bologna",147,"Bologna","bologna","One of the two named work locations."),
 ("rome_commission",147,"Rome","rome","One of the two named work locations."),
 ("balestra",147,"Antonio Balestra","balestra","Artist whom Johann Wilhelm unsuccessfully tried to invite."),
 ("carriera",148,"Rosalba Camera","carriera","Print reads Carriera; OCR reads Camera."),
 ("carriera_who",148,"who","carriera","Refers to Rosalba Carriera."),
 ("johann_for_him",148,"him","johann","Refers to Johann Wilhelm."),
 ("venice",148,"Venice","venice","Place where Carriera acquired pictures for Johann Wilhelm."),
 ("dusseldorf_invitation",148,"Dusseldorf","dusseldorf","OCR omits the printed umlaut; footnote 3 follows."),
 ("trevisani_footer",149,"Francesco Trevisani","trevisani","Named in an unnumbered incomplete footer fragment."),
 ("balestra_footer",149,"Balestra","balestra","Named in an unnumbered incomplete footer fragment."),
]
for row in MENTIONS: m(*row)

def q(first, last):
    a = body.find(first)
    if a < 0: raise SystemExit(f"quote start missing: {first!r}")
    b = body.find(last, a)
    if b < 0: raise SystemExit(f"quote end missing: {last!r}")
    return body[a:b+len(last)]

news = []
def s(sid, ls, le, sub, obj, pred, first, last, claim, qual, refs=(), relation=False,
      foot=None, speaker="Haskell", layer="authorial narrative", ocr=()):
    if sid in sids or any(r["statement_id"] == sid for r in news): raise SystemExit(f"duplicate statement: {sid}")
    linked = set(refs) | {x for x in (sub,obj) if x}
    if not linked <= (cids | {"cand-8951"}): raise SystemExit(f"missing linked candidate for {sid}: {linked-(cids|{'cand-8951'})}")
    qual = {"source_line_start":ls,"source_line_end":le,"printed_page":282,"pdf_physical_page":11,
            "claim":claim,"speaker":speaker,"text_layer":layer,"qualification":qual,
            "mentioned_candidate_ids":sorted(linked)}
    if relation: qual["relation_candidate"] = True
    if foot is not None: qual.update({"footnote_marker":foot,"footnote_text_pending":True,"footnote_link_status":"pending_source_migration"})
    if ocr: qual["ocr_corrections"] = [{"source_file":SOURCE_FILE,"source_line":ln,"ocr":raw,"print":printed,"basis":"CHP-10.pdf physical page 11."} for ln,raw,printed in ocr]
    news.append({"statement_id":sid,"segment_id":SEG,"subject_candidate_id":sub,"object_candidate_id":obj,
                 "predicate":pred,"qualifiers":qual,"original_quote":q(first,last),"source_file":SOURCE_FILE,"origin":"book"})

old["qualifiers"].update({"continuation_quote":"but soon after, his fortunes turned.","continuation_source_segment_id":SEG,
 "cross_reference_segments":[{"segment_id":SEG,"source_line_start":142,"source_line_end":142}],
 "claim":"Haskell says Johann Wilhelm came to power in 1690 in a state devastated by Louis XIV's troops and was almost at once forced to quell a serious revolt; the narrative then says his fortunes soon turned.",
 "qualification":"The revolt remains unnamed; p.282 closes the sentence but supplies no further identity for the event."})

s("st-chp10-p282-wilhelm-political-influence",142,142,E["johann"],None,"johann_wilhelm_gained_german_political_influence_1708_1714","For some years between 1708 and 1714","in German politics","Haskell says Johann Wilhelm achieved unparalleled influence in German politics for some years between 1708 and 1714.","Keep Haskell's stated range and superlative.")
s("st-chp10-p282-palatinate-great-power-prospect",142,142,E["johann"],E["palatinate"],"palatinate_might_have_become_great_power","with the growing success of his intrigues","one of the great powers","Haskell says growing intrigues and military success made it seem possible that the Palatinate might become a great power.","The outcome is tentative ('it seemed possible' and 'might'), not a realized status.",relation=True)
s("st-chp10-p282-wilhelm-love-of-glory",142,142,E["johann"],None,"johann_wilhelms_love_of_glory_reflected_in_artists_adulation","His love of glory","who surrounded him.","Haskell says Johann Wilhelm's love of glory was reflected in adulation by the artists around him.","Authorial characterization; the artists are unnamed.")
s("st-chp10-p282-rapparini-apotheosis",142,142,E["rapparini"],E["johann"],"rapparini_wrote_ancient_romans_would_have_formed_johann_wilhelms_apotheosis","S’il auroit vécu","son Apothéose’","Haskell quotes Rapparini imagining that ancient Romans would have formed an apotheosis for Johann Wilhelm.","Nested quotation attributed to Rapparini; footnote 1 remains pending the consolidated notes segment.",[E["alexander"]],True,1,"Giorgio Maria Rapparini, quoted by Haskell","nested direct quotation",[(142,"Giorgio MariaRapparini","Giorgio Maria Rapparini")])
s("st-chp10-p282-rapparini-alexander-comparison",142,142,E["rapparini"],E["johann"],"rapparini_compared_wilhelm_to_alexander_and_haskell_called_it_superstitious_veneration","but Rapparini himself","superstitious veneration,","Haskell says Rapparini repeatedly compared Johann Wilhelm to Alexander and hardly lagged the Romans in superstitious veneration.","Haskell's ironic characterization is distinct from Rapparini's quoted words.",[E["alexander"]],True)
s("st-chp10-p282-gruppello-statue",142,143,E["gruppello"],C["statue"],"gruppello_statue_reflected_wilhelms_self_display","much of the art created at","passion for self-display.","Haskell says art at Düsseldorf, including Gabriel Gruppello's bronze equestrian statue, was inspired by Johann Wilhelm's passion for self-display.","No date or present location is supplied for the statue.",[E["dusseldorf"],E["johann"]],True,ocr=[(143,"Dusseldorf","Düsseldorf")])
s("st-chp10-p282-wilhelm-love-of-art",143,143,E["johann"],None,"rapparini_described_wilhelms_intense_love_of_painting","à l’égard de la Peinture","à moitié’.","Haskell quotes Rapparini describing Johann Wilhelm's intense love of painting and willingness to sacrifice for a rare work by an excellent master.","Nested quotation attributed to Rapparini; its extravagant wording remains the quoted speaker's characterization.",[E["rapparini"],E["flanders"]],True,speaker="Giorgio Maria Rapparini, quoted by Haskell",layer="nested direct quotation")
s("st-chp10-p282-marriage-patronage",143,143,E["johann"],E["anna"],"marriage_may_have_spurred_wilhelms_collecting","This enthusiasm for collecting and patronage","the last of the Medici,","Haskell says Johann Wilhelm's collecting and patronage were no doubt spurred by his marriage to Anna Maria Ludovica.","Preserve the author's causal inference; it is not independently established here.",relation=True)
s("st-chp10-p282-rapparini-guided-study",143,143,E["rapparini"],E["maratta"],"rapparini_guided_patronage_and_studied_under_maratta","and it was guided by Rapparini","in Rome.","Haskell says Rapparini guided Johann Wilhelm's patronage, was a painter and writer, and had studied under Carlo Maratta in Rome.","No dates are supplied for the study or guidance.",[E["johann"],E["rome"]],True)
s("st-chp10-p282-rapparini-eclectic-taste",143,143,E["rapparini"],None,"haskell_judged_rapparinis_praise_to_produce_eclectic_taste","In his writings Rapparini shows himself","described as eclectic.","Haskell says Rapparini's unqualified praise made his taste describable only as eclectic.","This is Haskell's evaluative judgment about Rapparini's writings.",speaker="Haskell evaluating Rapparini's writings",layer="authorial evaluation")
s("st-chp10-p282-rapparini-aesthetic-theory",143,145,E["rapparini"],None,"rapparini_writings_advocated_chromatic_pleasure_facility_and_variety","Une austère régularité","d’un bout à l’autre de la Pièce.’","Haskell quotes Rapparini's writing that strict regularity repels amateurs, painting should attract through apparent ease, colour pleases the eye, and a cheerful manner should animate the picture.","French quotation attributed through Haskell; retain historical spelling and accents.",speaker="Giorgio Maria Rapparini, quoted by Haskell",layer="nested direct quotation")
s("st-chp10-p282-italian-collection-commissions",145,147,E["johann"],None,"wilhelm_collected_italian_art_and_commissioned_four_painters","It was in this spirit","in Bologna and Rome.","Haskell says Johann Wilhelm amassed Italian works, especially by Luca Giordano, and commissioned Cignani, Franceschini, dal Sole, and Trevisani to work for him in Bologna and Rome.","Footnotes 2 and 3 remain pending. No Giordano title is supplied here.",[E["italy"],E["giordano"],E["cignani"],E["franceschini"],E["dal_sole"],E["trevisani"],E["bologna"],E["rome"]],True,2)
s("st-chp10-p282-unsuccessful-invitations",147,148,E["johann"],E["balestra"],"wilhelm_unsuccessfully_invited_balestra_and_carriera_to_dusseldorf","He also tried, albeit without success","to come to Dusseldorf.3","Haskell says Johann Wilhelm tried unsuccessfully to persuade Antonio Balestra and Rosalba Carriera to come to Düsseldorf.","Failed invitations do not establish either artist visited; note 3 remains pending.",[E["carriera"],E["dusseldorf"]],True,3,ocr=[(148,"Rosalba Camera","Rosalba Carriera"),(148,"Dusseldorf","Düsseldorf")])
s("st-chp10-p282-carriera-acquired-pictures",148,148,E["carriera"],E["johann"],"carriera_acquired_pictures_for_wilhelm_in_venice","Rosalba Camera (who acquired pictures","in Venice)","Haskell says Rosalba Carriera acquired pictures for Johann Wilhelm in Venice.","OCR reads Camera; print reads Carriera. The pictures are not individually identified.",[E["venice"]],True,ocr=[(148,"Rosalba Camera","Rosalba Carriera")])

cov[PREV]["migration_status"] = "complete"
cov[PREV]["note"] += " Closed the Johann Wilhelm accession/revolt sentence with p.282 L142; the revolt remains unnamed, and the existing statement was completed in place with cross-page provenance retained."
cov[SEG].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L142-149",
 "note":"Printed p.282 body and footer read against CHP-10.pdf physical page 11. Closed the p.281 accession/revolt sentence; recorded Johann Wilhelm's 1708-1714 political influence and qualified Palatinate great-power prospect, artist adulation, Rapparini's nested praise and aesthetic writing, Gruppello's equestrian statue, collecting and patronage, marriage context, Italian works and commissions, and unsuccessful invitations to Balestra and Carriera. S2-only scan corrections: L142 Giorgio MariaRapparini->Giorgio Maria Rapparini; L143 Dusseldorf->Düsseldorf; L148 Rosalba Camera->Rosalba Carriera and Dusseldorf->Düsseldorf; S0 unchanged. Notes 1-3 point to consolidated notes L520-522 and remain pending. L149 is an unnumbered footer fragment ending 'refused regular'; its continuation and note identity are unresolved, so coverage remains partial."})
cov[NEXT]["note"] = "Next source-order body segment is p.283 at L152. The unnumbered p.282 footer fragment at L149 remains unresolved and is not completed by inference."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN","segment":SEG,
 "new_candidates":len(newc),"new_mentions":len(newm),"new_statements":len(news),"candidate_range":["cand-8951","cand-8951"],
 "completed_in_place":OPEN_ID,"coverage":{"p281":cov[PREV]["migration_status"],"p282":cov[SEG]["migration_status"],"next":cov[NEXT]["migration_status"]}},ensure_ascii=False,indent=2))
if sys.argv[-1:] != ["--apply"]: raise SystemExit(0)
for p in (cp,mp,sp,vp):
    b = Path(str(p)+BACKUP)
    if b.exists(): raise SystemExit(f"backup already exists: {b}")
    shutil.copy2(p,b)
write_csv(cp,cf,candidates+newc); write_csv(mp,mf,mentions+newm); write_jsonl(sp,statements+news)
write_csv(vp,vf,[cov[r["segment_id"]] for r in coverage])
print("Applied p.282 S2 migration; backups retained.")
