"""Controlled S2 migration for printed p.294; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l279-290"
SEG = "chp-10:10_CHP-10_intro:l292-302"
NEXT = "chp-10:10_CHP-10_intro:l304-316"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEG_SHA = "645d30776574018f0232546bba9f6c649b4bb473769d5a44bde73b2d95ab2e42"
BACKUP = ".bak-s2-chp10-p294-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(src[291:302])
SEG_SHA = hashlib.sha256(body.encode("utf-8")).hexdigest()
if SEG_SHA != EXPECTED_SEG_SHA or src[291].strip() != "[Page 294]" or "Frederick Augustus I" not in body or "Pietro Guarienti" not in body:
    raise SystemExit("p.294 source segment/page mismatch")

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
if maximum != 9074:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")),
                      (NEXT, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "pellegrini": "cand-1862", "pellegrini_dresden": "cand-1868",
    "augustus_ii": "cand-0146", "augustus_ii_venetian_patronage": "cand-0147",
    "augustus_iii": "cand-0148", "augustus_iii_algarotti": "cand-0149",
    "augustus_iii_gallery": "cand-0151", "augustus_iii_modena_pictures": "cand-0152",
    "algarotti": "cand-0041", "algarotti_purchases": "cand-0073",
    "diziani": "cand-0922", "dresden": "cand-0947", "popp": "cand-1974",
    "ricci_sebastiano": "cand-2154", "ricci_ascension": "cand-2157",
    "zucchi": "cand-2887", "pittoni": "cand-1950",
    "pittoni_nero_seneca": "cand-1959", "pittoni_agrippina": "cand-1951",
    "negri": "cand-1731", "zanchi": "cand-2834", "benefial": "cand-0288",
    "migliori": "cand-1664", "molinari": "cand-1679", "bellucci": "cand-0282",
    "bruehl": "cand-0458", "germany": "cand-5529", "rossi_brothers": "cand-2274",
    "marco_ricci": "cand-2149", "venice": "cand-2719", "venetian_school": "cand-8094",
    "german_patronage": "cand-1146", "seneca": "cand-2418",
    "europe": "cand-3462", "old_masters": "cand-4288",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
for key, cid, page, sub in (
    ("augustus_ii", E["augustus_ii"], "266, 278, 294", ""),
    ("augustus_ii_venetian_patronage", E["augustus_ii_venetian_patronage"], "294", "patronage of Venetian artists"),
    ("augustus_iii", E["augustus_iii"], "277, 294, 295, 298, 307, 344, 349, 350, 351", ""),
    ("augustus_iii_algarotti", E["augustus_iii_algarotti"], "294, 295, 298, 349, 350, 351, 353, 355", "F. Algarotti and"),
    ("augustus_iii_gallery", E["augustus_iii_gallery"], "294, 295, 350, 351", "Dresden Gallery"),
    ("augustus_iii_modena_pictures", E["augustus_iii_modena_pictures"], "294", "pictures from collections of Dukes of Modena"),
    ("algarotti_purchases", E["algarotti_purchases"], "294, 295, 298, 349, 356", "purchases of pictures for Augustus III"),
    ("pellegrini_dresden", E["pellegrini_dresden"], "293, 294", "work in Dresden"),
    ("pittoni_nero_seneca", E["pittoni_nero_seneca"], "294", "Nero being shown the corpse of Seneca"),
    ("pittoni_agrippina", E["pittoni_agrippina"], "294", "Agrippina being killed on the orders of her son Nero"),
    ("ricci_ascension", E["ricci_ascension"], "280, 294", "Ascension"),
):
    row = next(row for row in candidates if row["candidate_id"] == cid)
    if row["index_page_range"] != page or row["sub_entry"] != sub:
        raise SystemExit(f"unexpected page-specific index candidate {key}={cid}")

NEW_SPECS = [
    ("dresden_court", "Dresden court of Augustus the Strong (court praised in the p.294 account)", "institution",
     "The court that Haskell describes as exceptionally brilliant under Augustus the Strong. Keep this court distinct from the city, the ruler and the Dresden Gallery.", 293),
    ("zwinger", "Zwinger (Rococo pavilion in Dresden)", "place",
     "The recently completed Rococo pavilion in Dresden where Pellegrini was considered as a possible room decorator.", 293),
    ("pellegrini_zwinger_project", "Unidentified proposed room decoration by Pellegrini for the Zwinger (later destroyed in Haskell's account)", "work",
     "A decoration project for one room in the Zwinger; the source says Pellegrini was considered for it and that the project was later destroyed, without identifying the room or the specific decorative work.", 293),
    ("dresden_church", "Unnamed Catholic church in Dresden associated with Pellegrini's two paintings", "place",
     "An unnamed Catholic church in Dresden for which Pellegrini painted two works; do not infer its identity from the separate Ricci Ascension reference.", 293),
    ("pellegrini_church_pair", "Two unidentified paintings by Giovanni Antonio Pellegrini in a Catholic church in Dresden", "work",
     "A pair of paintings attributed to Pellegrini and located in an unnamed church in Haskell's Dresden account. The titles and church identity are not supplied; the text does not say they were commissioned for it.", 293),
    ("german_audience", "Germans named collectively as favoring the Agrippina subject and related paintings", "",
     "An unnamed collective in Haskell's description of the gruesome subject's appeal. Membership and its relation to the broader German taste account are unspecified.", 294),
    ("print_cabinet", "Famous print cabinet in Dresden's court (institutional identity and type unresolved)", "",
     "The workplace where Antonio Zucchi was employed. The passage calls it a print cabinet but does not identify its formal organization or whether the referent is a room, collection or administrative unit.", 294),
    ("augustus_ii_gallery", "Inherited picture gallery enlarged by Augustus the Strong (collection type unresolved)", "",
     "A gallery of pictures Augustus the Strong had inherited and considerably enlarged. Keep the inherited collection distinct from the later Dresden Gallery institution; the source does not specify a formal collection title.", 294),
    ("nero_person", "Nero named in Pittoni's p.294 painting titles (identity not independently resolved here)", "person",
     "Named in the titles of two Pittoni pictures on p.294. Retain the name as printed and leave historical identity alignment to S3.", 294),
    ("agrippina_person", "Agrippina named in Pittoni's p.294 painting title (identity not independently resolved here)", "person",
     "Named in the title of Pittoni's picture about her death on Nero's orders. The passage supplies no further personal identifier; resolve identity in S3.", 294),
    ("negri_agrippina_version", "Second version of Pittoni's Agrippina subject by Pietro Negri", "work",
     "A second version of the gruesome subject that Augustus the Strong owned, attributed in the source to Pietro Negri. Its title, date and location are not supplied.", 294),
    ("benefial_agrippina_version", "Third Agrippina painting by Marco Benefial, given away after arriving in Dresden", "work",
     "A third version of the subject attributed to Marco Benefial. Haskell says Augustus III's son clearly judged that its possibilities were exhausted and gave it away; preserve this reported interpretation.", 295),
    ("migliori_paintings", "Six unidentified mythological and Biblical paintings by Francesco Migliori acquired by Augustus the Strong", "work",
     "A group of six paintings acquired by Augustus the Strong. The source describes their subject categories but gives no individual titles.", 297),
    ("molinari_bellucci_pictures", "Unidentified paintings by Antonio Molinari and Antonio Bellucci acquired by Augustus the Strong", "work",
     "The source mentions additional works by Molinari and Bellucci alongside Migliori's six paintings without giving titles or counts.", 298),
    ("nudite_ideal", "Ideal of 'nudité' in painting discussed as appealing to German taste", "term",
     "The French term names an aesthetic ideal Haskell says appealed to German taste; retain the source's term and authorial framing without expanding its definition.", 298),
    ("seven_years_war", "Seven Years' War (named as the later disaster affecting Augustus III's collecting period)", "event",
     "The historical event named as a turning point in the account of Augustus III and Count Brühl's collecting activity. The source does not specify a date here.", 298),
    ("dresden_gallery", "Dresden Gallery (art gallery under Pietro Guarienti's direction)", "institution",
     "The art gallery in Dresden whose pre-eminence Haskell associates with Guarienti's direction and Augustus III's purchases. Do not conflate the institution with the ruler's inherited picture collection.", 299),
    ("guarienti", "Pietro Guarienti (Venetian artist directing the Dresden Gallery)", "person",
     "Named as the Venetian artist under whose direction the Dresden Gallery achieved prominence. The passage supplies no further biography.", 299),
    ("modena_pictures", "Hundred finest pictures from collections of the Dukes of Modena acquired for Dresden Gallery", "work",
     "A group of pictures cited as an example of Augustus III's purchases for Dresden. Haskell calls them the hundred finest from the Dukes of Modena's collections but does not list individual titles here.", 299),
    ("modena_dukes", "Dukes of Modena named as former picture-collection owners (individuals and group identity unresolved)", "",
     "The plural title appears in the provenance of the hundred pictures; do not infer the specific dukes, a family identity, or the exact collections from this passage alone.", 299),
    ("augustus_iii_agents", "Unidentified agents acquiring artworks for Augustus III across Europe", "",
     "A collective of unnamed purchasing agents acting for Augustus III. Its membership and organization are not given; keep it separate from the named Rossi brothers.", 299),
    ("suitable_pictures", "Unidentified pictures sought by the Rossi brothers for Augustus III in Venice", "work",
     "The Rossi brothers were looking for suitable pictures as agents for Augustus III. The passage does not identify individual works or say which were acquired.", 300),
    ("ricci_six_landscapes", "Six landscapes by Marco Ricci acquired in Venice in 1738 for Augustus III", "work",
     "A group of six landscapes acquired by the Rossi brothers for Augustus III. The source gives the artist and year but no titles or present locations.", 301),
]
newc, C = [], {}
for i, (key, name, kind, detail, line) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{i:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    newc.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                 "index_page_range": "", "suggested_type": kind, "status": "open",
                 "index_source_file": "", "sub_entry": "", "detail": detail,
                 "exclude_reason": "", "candidate_origin": "body-mention",
                 "candidate_source_ref": f"{SEG}#L{line}"})

offsets, offset = {}, 0
for line in range(292, 303):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p294-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    line_start, line_end = offsets[line], offsets[line] + len(src[line - 1])
    positions, at = [], line_start
    while True:
        at = body.find(surface, at)
        if at < 0 or at >= line_end:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTIONS = [
    ("pellegrini-dresden",293,"Pellegrini",E["pellegrini"],"Closes p.293 L290 'And in-1725'; the completed sentence states that Pellegrini went to Dresden in 1725."),
    ("dresden-journey",293,"Dresden",E["dresden"],"Destination of Pellegrini's 1725 journey."),
    ("pellegrini-dresden-index",293,"Pellegrini",E["pellegrini_dresden"],"Maps the page-specific index entry 'work in Dresden'.",1),
    ("frederick-augustus",293,"Frederick Augustus I",E["augustus_ii"],"Index identifies him as Augustus II of Poland and Elector of Saxony."),
    ("elector-saxony",293,"Elector of Saxony",E["augustus_ii"],"Office/title of Frederick Augustus I."),
    ("king-poland",293,"King of Poland",E["augustus_ii"],"The same ruler under his Polish kingship."),
    ("augustus-ii-name",293,"Augustus II",E["augustus_ii"],"Name attached to Frederick Augustus I in the source."),
    ("the-strong",293,"‘the Strong’",E["augustus_ii"],"Epithet of Augustus II as printed."),
    ("court",293,"his court",C["dresden_court"],"Court of Augustus the Strong; keep it distinct from the Dresden Gallery."),
    ("europe",293,"Europe",E["europe"],"Regional context of the court's reputation."),
    ("dresden-policy",293,"Dresden",E["dresden"],"City transformed by Augustus's architectural policy.",1),
    ("venetian-art",293,"contemporary Venetian art",E["venetian_school"],"Artistic context of Augustus's limited interest."),
    ("diziani",293,"Gaspare Diziani",E["diziani"],"Named artist employed by Augustus the Strong."),
    ("zwinger",293,"the Zwinger",C["zwinger"],"Rococo pavilion in Dresden."),
    ("popp",293,"Pöppelmann",E["popp"],"Architect named as the pavilion's recent completer."),
    ("pellegrini-project",293,"his project",C["pellegrini_zwinger_project"],"Pronoun refers to Pellegrini's proposed room decoration; later destruction is reported without details."),
    ("pellegrini-city",293,"his activities in the city",E["pellegrini"],"Pellegrini's activity in Dresden after the Zwinger project."),
    ("dresden-city",293,"the city",E["dresden"],"Corefers to Dresden."),
    ("pellegrini-pair",293,"two paintings",C["pellegrini_church_pair"],"Unidentified pair attributed to Pellegrini."),
    ("dresden-church",293,"the Catholic church",C["dresden_church"],"Unnamed church building; keep distinct from the Catholic Church as institution."),
    ("ricci",293,"Sebastiano Ricci",E["ricci_sebastiano"],"Named painter with an earlier painting at the same church."),
    ("ascension",294,"Ascension",E["ricci_ascension"],"Page-specific index sub-entry for Ricci's work."),
    ("pellegrini-year-after",294,"Pellegrini",E["pellegrini"],"Reference point for the relative arrival date of Zucchi."),
    ("zucchi",294,"Antonio Zucchi",E["zucchi"],"Named engraver arriving after Pellegrini."),
    ("print-cabinet",294,"the famous print cabinet",C["print_cabinet"],"Workplace in which Zucchi was employed; identity and entity type remain unresolved."),
    ("augustus-gallery",294,"Augustus",E["augustus_ii"],"Corefers to Augustus the Strong."),
    ("inherited-gallery",294,"the gallery of pictures he had inherited",C["augustus_ii_gallery"],"Collection distinct from the later Dresden Gallery institution."),
    ("venetian-patronage-index",294,"his purchases did not very much affect Venetian painters",E["augustus_ii_venetian_patronage"],"Maps the p.294 index sub-entry 'patronage of Venetian artists'."),
    ("pittoni",294,"Pittoni",E["pittoni"],"Named painter of the two large pictures."),
    ("germans",294,"the Germans",C["german_audience"],"Unnamed collective described as favoring the gruesome subject; membership is not specified."),
    ("pittoni-nero-work",294,"Nero being shown the Corpse of Seneca",E["pittoni_nero_seneca"],"Title listed in the index; source's capitalization retained."),
    ("nero",294,"Nero",C["nero_person"],"Named within the painting title; historical identity left for S3."),
    ("seneca",294,"Seneca",E["seneca"],"Named within the painting title; no new identity claim."),
    ("pittoni-agrippina-work",294,"Agrippina being killed on the orders of her son Nero",E["pittoni_agrippina"],"Title listed in the index; preserve wording and attribution."),
    ("agrippina",294,"Agrippina",C["agrippina_person"],"Person named within the painting title; identity left for S3."),
    ("nero-son",294,"her son Nero",C["nero_person"],"Nero named as her son within the title."),
    ("gruesome-subject",294,"This gruesome subject",E["pittoni_agrippina"],"Haskell's description of the Agrippina subject."),
    ("negri-version",294,"a second version of it",C["negri_agrippina_version"],"The version owned by Augustus the Strong, attributed below to Pietro Negri."),
    ("negri-first-name",294,"Pietro",E["negri"],"First part of the painter's name before the OCR line break."),
    ("negri-surname",295,"Negri",E["negri"],"Surname completing the painter's name across the OCR line break."),
    ("zanchi",295,"Zanchi",E["zanchi"],"Named as Negri's teacher; do not infer additional biographical detail."),
    ("third-version",295,"a third",C["benefial_agrippina_version"],"Third painting/version of the Agrippina subject in the account."),
    ("benefial-first-name",295,"Marco",E["benefial"],"First part of the painter's name before the OCR line break."),
    ("benefial-surname",296,"Benefial",E["benefial"],"Surname completing the painter's name across the OCR line break."),
    ("dresden-arrival",296,"Dresden",E["dresden"],"Place where the Benefial painting arrived."),
    ("augustus-son",296,"his son",E["augustus_iii"],"Corefers to Augustus the Strong's son, Augustus III."),
    ("benefial-picture",296,"the picture",C["benefial_agrippina_version"],"The third Agrippina painting attributed to Benefial."),
    ("augustus-strong-acquired",297,"Augustus the Strong",E["augustus_ii"],"Alias of Augustus II in this paragraph."),
    ("migliori",298,"Francesco Migliori",E["migliori"],"Named artist of six paintings."),
    ("migliori-six",297,"six mythological and Biblical paintings",C["migliori_paintings"],"Unidentified group; individual titles are not supplied."),
    ("molinari",298,"Molinari",E["molinari"],"Named among artists whose pictures were acquired."),
    ("bellucci",298,"Bellucci",E["bellucci"],"Named among artists whose pictures were acquired."),
    ("molinari-bellucci-pictures",298,"others by Molinari and Bellucci",C["molinari_bellucci_pictures"],"Unspecified works, with no count or titles in this passage."),
    ("nudite",298,"‘nudité’",C["nudite_ideal"],"French term preserved as printed."),
    ("augustus-iii",298,"Augustus III",E["augustus_iii"],"Son of Augustus the Strong and successor in 1733."),
    ("seven-years-war",298,"Seven Years War",C["seven_years_war"],"Event named as a later turning point."),
    ("bruehl",298,"Count Brühl",E["bruehl"],"Count named as minister and co-subject of collecting activity."),
    ("german-patronage-index",298,"The patronage of his son Augustus III",E["german_patronage"],"Maps the indexed topic of German patronage of Venetian artists."),
    ("guarienti",299,"Pietro Guarienti",C["guarienti"],"Named Venetian artist directing the Dresden Gallery."),
    ("dresden-gallery",299,"the Dresden Gallery",C["dresden_gallery"],"Institution distinct from the city's buildings and Augustus II's inherited picture gallery."),
    ("germany-gallery",299,"Germany",E["germany"],"Region used for comparison of gallery pre-eminence."),
    ("augustus-gallery-purchases",299,"His fabulous purchases for it",E["augustus_iii_gallery"],"Maps the index sub-entry for Augustus III's Dresden Gallery."),
    ("modena-pictures",299,"the hundred finest pictures from the collections of the Dukes of Modena",C["modena_pictures"],"Group named as an example of purchases for the gallery; individual dukes and pictures remain unidentified."),
    ("modena-dukes",299,"the Dukes of Modena",C["modena_dukes"],"Collective provenance reference; do not infer specific dukes or a family identity."),
    ("augustus-modena-index",299,"the hundred finest pictures",E["augustus_iii_modena_pictures"],"Maps the p.294 Augustus III index sub-entry for these purchases."),
    ("agents",299,"Agents",C["augustus_iii_agents"],"Unnamed collective acquiring art on Augustus III's behalf."),
    ("augustus-agents",299,"for him",E["augustus_iii"],"Pronoun refers to Augustus III."),
    ("europe-agents",299,"throughout Europe",E["europe"],"Broad geographic scope of the agents' activity."),
    ("venice-agents",299,"in Venice itself",E["venice"],"Named location of the brothers' agency."),
    ("rossi-brothers",299,"the brothers Ventura and Lorenzo",E["rossi_brothers"],"The two brothers are indexed as a joint entry; no unsupported individual given names are added."),
    ("rossi-surname",300,"Rossi",E["rossi_brothers"],"Surname continuation of the brothers' joint mention."),
    ("rossi-role",300,"who acted in this capacity",E["rossi_brothers"],"Corefers to the brothers' role as purchasing agents."),
    ("rossi-pictures",300,"suitable pictures",C["suitable_pictures"],"Works sought by the brothers as agents; no individual title is supplied."),
    ("rossi-six-landscapes",301,"six landscapes for him",C["ricci_six_landscapes"],"Six works acquired by the Rossi brothers for Augustus III."),
    ("old-masters-term",301,"old masters",E["old_masters"],"Existing term candidate for the broad class of older artworks."),
    ("marco-ricci",302,"Marco Ricci",E["marco_ricci"],"Named landscape painter; page-specific index candidate."),
    ("algarotti",302,"Francesco Algarotti",E["algarotti"],"Named in the transition to purchases for Augustus III."),
    ("algarotti-index-purchase",302,"especially to",E["algarotti_purchases"],"Maps the index sub-entry about Algarotti's purchases for Augustus III; the sentence continues on p.295."),
    ("native-city",302,"his native city",E["venice"],"Algarotti's native city is identified by the immediate account as Venice; retain the source's coreference."),
]
for item in MENTIONS:
    add_m(*item)

new_s = []


def quote(start, end):
    first = body.find(start)
    if first < 0:
        raise SystemExit(f"quote start absent: {start!r}")
    last = body.find(end, first)
    if last < 0:
        raise SystemExit(f"quote end absent: {end!r}")
    return body[first:last + len(end)]


def add_s(sid, lo, hi, subject, obj, predicate, start, end, claim, qualification,
          mentioned, speaker="Haskell", layer="authorial narrative", relation=False,
          footnote=None, cross=None):
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 294,
                  "pdf_physical_page": 23, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        qualifiers["cross_reference_printed_pages"] = [293 if PREV in cross else 295]
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


add_s("st-chp10-p294-pellegrini-dresden-1725",293,293,E["pellegrini"],E["dresden"],
      "pellegrini_went_to_dresden_in_1725",
      "Pellegrini went to Dresden", "international attention.",
      "In 1725 Pellegrini went to Dresden, where another sovereign was attracting international attention as a patron.",
      "The date fragment 'in-1725' begins on p.293 L290 and is closed by this p.294 sentence; the year is linked back to the preceding source segment.",
      [E["pellegrini"],E["dresden"],E["augustus_ii"]],relation=True,cross=[PREV])
add_s("st-chp10-p294-augustus-court-and-city",293,293,E["augustus_ii"],C["dresden_court"],
      "augustus_the_strong_made_his_court_exceptionally_brilliant_and_his_architectural_policy_transformed_dresden",
      "had made his court", "dazzling beauty.",
      "Haskell says Augustus the Strong made his court the most brilliant in Europe and that his munificent architectural policy transformed Dresden into a city of dazzling beauty.",
      "This is Haskell's evaluative account; 'most brilliant' and 'dazzling beauty' are not treated as measured facts.",
      [E["augustus_ii"],C["dresden_court"],E["dresden"]],layer="authorial interpretation",relation=True)
add_s("st-chp10-p294-augustus-venetian-interest",293,294,E["augustus_ii"],E["venetian_school"],
      "augustus_the_strongs_interest_in_contemporary_venetian_art_was_limited_and_his_purchases_had_little_effect_on_venetian_painters",
      "But his interest in contemporary Venetian art", "Venetian painters.",
      "Haskell describes Augustus the Strong's interest in contemporary Venetian art as limited and says his purchases did not very much affect Venetian painters.",
      "The source gives no quantitative measure of either interest or effect; 'limited' and 'not very much' remain attributed evaluations.",
      [E["augustus_ii"],E["venetian_school"],E["augustus_ii_venetian_patronage"]],layer="authorial interpretation")
add_s("st-chp10-p294-diziani-employment",293,293,E["augustus_ii"],E["diziani"],
      "augustus_employed_diziani_for_three_years_mainly_as_theatre_and_festival_scenery_painter",
      "He employed Gaspare Diziani", "his special delight.",
      "Augustus employed Gaspare Diziani for three years almost exclusively to paint scenery for the theatre and festivals that especially delighted him.",
      "'Almost exclusively' and the special delight are preserved as stated; the source supplies no exact start or end dates.",
      [E["augustus_ii"],E["diziani"],E["dresden"]],relation=True)
add_s("st-chp10-p294-pellegrini-zwinger-project",293,293,E["pellegrini"],C["pellegrini_zwinger_project"],
      "pellegrini_was_considered_to_decorate_a_room_in_the_zwinger_but_his_project_was_later_destroyed",
      "Pellegrini was considered as a possible decorator", "but his project was later destroyed",
      "Pellegrini was considered as a possible decorator for one room in the Zwinger; Haskell says the project was later destroyed.",
      "The proposal, room and project are not identified further; preserve the source's wording without inferring that Pellegrini completed the decoration.",
      [E["pellegrini"],C["zwinger"],E["popp"],C["pellegrini_zwinger_project"]],relation=True)
add_s("st-chp10-p294-pellegrini-church-pictures",293,294,E["pellegrini"],C["pellegrini_church_pair"],
      "pellegrinis_dresden_activity_included_two_paintings_in_an_unnamed_catholic_church",
      "his activities in the city were otherwise confined", "in the Catholic church",
      "Haskell says Pellegrini's other activities in Dresden were confined to two paintings in an unnamed Catholic church.",
      "The church and pictures are unidentified; this does not establish that they were the same work as Ricci's Ascension.",
      [E["pellegrini"],E["dresden"],C["dresden_church"],C["pellegrini_church_pair"]],relation=True,footnote=1)
add_s("st-chp10-p294-ricci-ascension",293,294,E["ricci_sebastiano"],E["ricci_ascension"],
      "sebastiano_ricci_painted_an_ascension_for_the_dresden_catholic_church_three_years_earlier",
      "Sebastiano Ricci had three years earlier painted", "Ascension.",
      "Sebastiano Ricci had painted an Ascension for the Catholic church three years earlier.",
      "The church is not independently named here; do not merge this work with Pellegrini's two paintings. Note 1 remains pending in the consolidated notes segment.",
      [E["ricci_sebastiano"],E["ricci_ascension"],C["dresden_church"]],relation=True,footnote=1)
add_s("st-chp10-p294-zucchi-print-cabinet",294,294,E["zucchi"],C["print_cabinet"],
      "a_year_after_pellegrini_antonio_zucchi_arrived_and_was_employed_in_the_print_cabinet",
      "A year after Pellegrini came Antonio Zucchi", "print cabinet,2",
      "A year after Pellegrini, Antonio Zucchi came to Dresden and was employed in the famous print cabinet.",
      "The relative year and the cabinet's institutional identity are not specified further; note 2 is linked to the consolidated notes segment.",
      [E["zucchi"],E["pellegrini"],E["dresden"],C["print_cabinet"]],relation=True,footnote=2)
add_s("st-chp10-p294-augustus-picture-gallery",294,294,E["augustus_ii"],C["augustus_ii_gallery"],
      "augustus_considerably_enlarged_his_inherited_picture_gallery",
      "Augustus considerably enlarged", "he had inherited,",
      "Augustus considerably enlarged the gallery of pictures he had inherited.",
      "The passage does not name the collection or identify the earlier owner; keep it distinct from the Dresden Gallery discussed under Augustus III.",
      [E["augustus_ii"],C["augustus_ii_gallery"]],relation=True)
add_s("st-chp10-p294-pittoni-nero-picture",294,294,E["augustus_ii"],E["pittoni_nero_seneca"],
      "before_1722_augustus_acquired_pittonis_nero_and_seneca_picture",
      "Two large pictures by Pittoni", "Nero being shown the Corpse of Seneca",
      "Before 1722 Augustus acquired a large Pittoni picture showing Nero with the corpse of Seneca.",
      "The source gives no acquisition date beyond 'before 1722'; the work remains distinct from Pittoni's Agrippina picture.",
      [E["augustus_ii"],E["pittoni"],E["pittoni_nero_seneca"],C["nero_person"],E["seneca"]],relation=True)
add_s("st-chp10-p294-pittoni-agrippina-picture",294,294,E["augustus_ii"],E["pittoni_agrippina"],
      "before_1722_augustus_acquired_pittonis_agrippina_picture",
      "and Agrippina being killed", "her son Nero.",
      "Before 1722 Augustus acquired a large Pittoni picture showing Agrippina killed on the orders of her son Nero.",
      "The source gives no acquisition date beyond 'before 1722'; the work remains distinct from Pittoni's Nero and Seneca picture.",
      [E["augustus_ii"],E["pittoni"],E["pittoni_agrippina"],C["agrippina_person"],C["nero_person"]],relation=True)
add_s("st-chp10-p294-negri-second-version",294,295,E["augustus_ii"],C["negri_agrippina_version"],
      "augustus_owned_a_second_version_of_the_agrippina_subject_by_pietro_negri",
      "he owned a second version of it", "a pupil of Zanchi.",
      "Augustus owned a second version of the Agrippina subject by Pietro Negri, a pupil of Zanchi.",
      "The source calls this a second version and names Negri; no title, date or location is provided. Keep the attribution and pupil statement at the source's level.",
      [E["augustus_ii"],C["agrippina_person"],C["negri_agrippina_version"],E["negri"],E["zanchi"]],relation=True)
add_s("st-chp10-p294-benefial-third-version-given-away",295,296,E["augustus_iii"],C["benefial_agrippina_version"],
      "a_third_benefial_painting_of_the_agrippina_subject_arrived_in_dresden_and_was_given_away_by_augustus_iii",
      "a third, painted by the Roman Marco", "he gave the picture away.",
      "A third painting of the Agrippina subject by the Roman Marco Benefial arrived in Dresden; Haskell says Augustus III's son clearly felt its possibilities were exhausted and gave it away.",
      "The son is understood from the immediately preceding account as Augustus III; 'clearly felt' is Haskell's interpretation, not a documented statement by the son. Note 3 remains pending.",
      [C["benefial_agrippina_version"],E["benefial"],E["dresden"],E["augustus_iii"]],layer="authorial interpretation",relation=True,footnote=3)
add_s("st-chp10-p294-migliori-acquisition",297,298,E["augustus_ii"],C["migliori_paintings"],
      "augustus_the_strong_acquired_six_mythological_and_biblical_paintings_by_migliori",
      "Augustus the Strong also acquired six mythological and Biblical paintings", "by\nFrancesco Migliori,",
      "Augustus the Strong acquired six mythological and Biblical paintings by Francesco Migliori.",
      "The source gives the count and broad subjects but no individual titles.",
      [E["augustus_ii"],E["migliori"],C["migliori_paintings"]],relation=True)
add_s("st-chp10-p294-molinari-bellucci-acquisition",298,298,E["augustus_ii"],C["molinari_bellucci_pictures"],
      "augustus_the_strong_acquired_other_pictures_by_molinari_and_bellucci",
      "and others by Molinari and Bellucci", "Bellucci.",
      "Augustus the Strong also acquired other paintings by Antonio Molinari and Antonio Bellucci.",
      "The source gives neither titles nor counts for these works.",
      [E["augustus_ii"],E["molinari"],E["bellucci"],C["molinari_bellucci_pictures"]],relation=True)
add_s("st-chp10-p294-nudite-and-german-taste",298,298,C["migliori_paintings"],C["nudite_ideal"],
      "haskell_says_the_acquired_pictures_conformed_to_an_ideal_of_nudite_that_appealed_to_german_taste",
      "Virtually all these conform", "German taste.",
      "Haskell says virtually all the paintings just discussed conform to an ideal of 'nudité' that appealed to German taste.",
      "'Virtually all' is preserved; the aesthetic characterization is the author's judgment, not an independently verified account of German taste.",
      [C["migliori_paintings"],C["molinari_bellucci_pictures"],C["nudite_ideal"]],layer="authorial interpretation")
add_s("st-chp10-p294-augustusiii-bruehl-collecting",298,298,E["augustus_iii"],E["bruehl"],
      "augustus_iii_and_count_bruehl_had_outstanding_collecting_activities_until_the_seven_years_war",
      "the collecting activities of this man and his dictatorial minister Count Brühl", "among the most outstanding in Europe,",
      "Until the Seven Years War, Augustus III and his minister Count Brühl had collecting activities Haskell ranks among the most outstanding in Europe.",
      "The ranking is Haskell's assessment; 'nearly a quarter of a century later' is approximate and is not converted to an exact date.",
      [E["augustus_iii"],E["bruehl"],C["seven_years_war"]],layer="authorial interpretation",relation=True)
add_s("st-chp10-p294-guarienti-dresden-gallery",298,299,C["guarienti"],C["dresden_gallery"],
      "under_guarientis_direction_the_dresden_gallery_achieved_preeminence_in_germany",
      "under the direction of a Venetian artist", "others in Germany.",
      "Under the direction of the Venetian artist Pietro Guarienti, the Dresden Gallery achieved great pre-eminence over nearly all other galleries in Germany.",
      "The comparative status is Haskell's assessment; the source supplies no ranking method.",
      [C["guarienti"],C["dresden_gallery"],E["germany"]],relation=True,layer="authorial interpretation")
add_s("st-chp10-p294-modena-purchases",299,299,E["augustus_iii"],C["modena_pictures"],
      "augustus_iii_acquired_the_hundred_finest_pictures_from_the_dukes_of_modenas_collections_for_the_dresden_gallery",
      "His fabulous purchases for it", "from the collections of the Dukes of Modena—",
      "Haskell cites the hundred finest pictures from the collections of the Dukes of Modena as an example of Augustus III's purchases for the Dresden Gallery.",
      "The passage does not list the pictures or identify the Dukes; it says this example cannot be discussed in detail here.",
      [E["augustus_iii"],C["dresden_gallery"],C["modena_pictures"],C["modena_dukes"]],relation=True)
add_s("st-chp10-p294-unnamed-agents-across-europe",299,299,C["augustus_iii_agents"],E["augustus_iii"],
      "unnamed_agents_acquired_artworks_for_augustus_iii_throughout_europe",
      "Agents acquired works of art for him", "throughout Europe,",
      "Unnamed agents acquired works of art for Augustus III throughout Europe.",
      "The passage does not identify these agents; the Rossi brothers are separately named as acting in Venice.",
      [E["augustus_iii"],C["augustus_iii_agents"],E["europe"]],relation=True)
add_s("st-chp10-p294-rossi-agency",299,300,E["rossi_brothers"],E["augustus_iii"],
      "rossi_brothers_acted_as_augustus_iiis_agents_in_venice_and_sought_suitable_pictures",
      "the brothers Ventura and Lorenzo", "suitable pictures.",
      "The brothers Ventura and Lorenzo Rossi acted as agents for Augustus III in Venice and looked for suitable pictures.",
      "The source does not say that every picture sought was acquired; keep the named brothers separate from unnamed agents elsewhere.",
      [E["rossi_brothers"],E["augustus_iii"],E["venice"],C["suitable_pictures"]],relation=True)
add_s("st-chp10-p294-rossi-six-landscapes",301,302,E["rossi_brothers"],C["ricci_six_landscapes"],
      "in_1738_rossi_brothers_acquired_six_marco_ricci_landscapes_for_augustus_iii",
      "they acquired six landscapes for him by", "Marco Ricci in 1738.",
      "The Rossi brothers acquired six landscapes by Marco Ricci for Augustus III in 1738.",
      "The landscapes are not individually titled; this statement preserves the work, maker, buyer and date given in the source.",
      [E["rossi_brothers"],E["augustus_iii"],C["ricci_six_landscapes"],E["marco_ricci"]],relation=True)
add_s("st-chp10-p294-algarotti-return-open",302,302,E["algarotti"],E["augustus_iii"],
      "in_1743_algarotti_returned_to_venice_to_buy_pictures_for_the_king_he_served",
      "when Francesco Algarotti returned to his native city in 1743", "especially to",
      "In 1743 Francesco Algarotti returned to Venice especially to purchase pictures for the King he was serving.",
      "The source sentence continues onto p.295; the king is identified from the preceding context as Augustus III. This statement is partial until the continuation is processed.",
      [E["algarotti"],E["augustus_iii"],E["venice"],E["algarotti_purchases"]],relation=True,cross=[NEXT])

prev_statement = next((row for row in statements if row["segment_id"] == PREV and row.get("qualifiers", {}).get("source_line_end") == 290 and "1725" in row.get("qualifiers", {}).get("claim", "")), None)
if prev_statement:
    raise SystemExit(f"unexpected pre-existing p.293 1725 statement: {prev_statement['statement_id']}")

cov[PREV].update({"migration_status":"complete", "source_line_ranges":"L280-290",
                  "note":"Printed p.293 body is complete; the open 'And in-1725' fragment at L290 is closed by p.294 L293, now linked from statement st-chp10-p294-pellegrini-dresden-1725. The final p.293 note locator was separately captured. Consolidated notes remain pending."})
cov[SEG].update({"disposition":"reviewed", "migration_status":"partial", "source_line_ranges":"L293-302",
                 "note":"Printed p.294 was checked against CHP-10.pdf physical page 23. Closed p.293 L290 'And in-1725' as Pellegrini's 1725 journey to Dresden. Recorded Augustus II's court and architectural patronage; Diziani's scenery work; Pellegrini's proposed Zwinger project and two church paintings; Ricci's Ascension; Zucchi's print-cabinet employment; Augustus's gallery and purchases, Pittoni/Nero/Seneca/Agrippina versions, Negri, Benefial, Migliori, Molinari and Bellucci; Augustus III and Count Brühl's collecting; Guarienti and the Dresden Gallery; Modena pictures; Rossi brothers as agents and Marco Ricci landscapes. Preserved unnamed buildings, works, cabinet, collection, agents and Modena dukes without forcing unresolved types. Footnotes 1-3 remain linked to the consolidated notes segment. The final Algarotti sentence ends at 'especially to' and continues on p.295, so p.294 remains partial."})
cov[NEXT]["note"] = "Next source-order segment is printed p.295 at L304-316; it completes the p.294 Algarotti sentence and continues the account of purchases for Augustus III."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"segment_sha256":SEG_SHA,"new_candidates":len(newc),
                  "candidate_ids":[row["candidate_id"] for row in newc],"new_mentions":len(newm),
                  "new_statements":len(new_s),"coverage":{"p293":cov[PREV]["migration_status"],
                  "p294":cov[SEG]["migration_status"],"p295":cov[NEXT]["migration_status"]}},
                 ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup=Path(str(path)+BACKUP)
        if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.294 S2 migration; p.294 remains partial pending p.295 and consolidated notes.")
