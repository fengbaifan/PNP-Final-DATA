"""Controlled S2 migration for printed p.295; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l292-302"
SEG = "chp-10:10_CHP-10_intro:l304-316"
NEXT = "chp-10:10_CHP-10_intro:l318-330"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEG_SHA = "3ea63b6be08469c90ed3a0f6245fbe4d9f740b11617b55fe56e211cb9f80d064"
BACKUP = ".bak-s2-chp10-p295-20261002"


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
body = "\n".join(src[303:316])
SEG_SHA = hashlib.sha256(body.encode("utf-8")).hexdigest()
if SEG_SHA != EXPECTED_SEG_SHA or src[303].strip() != "[Page 295]" or "Felicita Sartori" not in body or "Church of the Cross" not in body:
    raise SystemExit("p.295 source segment/page mismatch")

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
if maximum != 9097:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")),
                      (NEXT, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "algarotti": "cand-0041", "algarotti_augustus_pictures": "cand-0073",
    "augustus_iii": "cand-0148", "augustus_iii_algarotti": "cand-0149",
    "augustus_iii_carriera": "cand-0150", "augustus_iii_gallery": "cand-0151",
    "amigoni": "cand-0094", "bellotto": "cand-0279", "bellotto_cross_work": "cand-0280",
    "bruehl": "cand-0458", "canaletto": "cand-0498", "carriera": "cand-0581",
    "carriera_augustus": "cand-0582", "clemens_august": "cand-0788",
    "dresden": "cand-0947", "frederick_great": "cand-1079",
    "german_patronage": "cand-1146", "nazari": "cand-1727", "nogari": "cand-1743",
    "piazzetta": "cand-1901", "standard_bearer": "cand-1923", "pittoni": "cand-1950",
    "ricci": "cand-2154", "sartori": "cand-2363", "tiepolo": "cand-2569",
    "venice": "cand-2719", "seven_years_war": "cand-9090",
    "venetian_school": "cand-8094", "carriera_collection": "cand-8851",
    "flanders": "cand-4652", "europe": "cand-3462", "germany": "cand-5529",
    "virgin_mary": "cand-3427", "magdalene": "cand-5861",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
for key, cid, page, sub in (
    ("algarotti_augustus_pictures", E["algarotti_augustus_pictures"], "294, 295, 298, 349, 356", "purchases of pictures for Augustus III"),
    ("augustus_iii", E["augustus_iii"], "277, 294, 295, 298, 307, 344, 349, 350, 351", ""),
    ("augustus_iii_algarotti", E["augustus_iii_algarotti"], "294, 295, 298, 349, 350, 351, 353, 355", "F. Algarotti and"),
    ("augustus_iii_carriera", E["augustus_iii_carriera"], "295", "and Rosalba Carriera"),
    ("bellotto", E["bellotto"], "295", ""),
    ("bellotto_cross_work", E["bellotto_cross_work"], "295", "painting of ruins of Church of the Cross, Dresden"),
    ("carriera_augustus", E["carriera_augustus"], "295", "and Augustus III of Poland"),
    ("clemens_august", E["clemens_august"], "295, 296", ""),
    ("standard_bearer", E["standard_bearer"], "295", "Standard Bearer"),
    ("sartori", E["sartori"], "295, 344n", ""),
):
    row = next(row for row in candidates if row["candidate_id"] == cid)
    if row["index_page_range"] != page or row["sub_entry"] != sub:
        raise SystemExit(f"unexpected page-specific index candidate {key}={cid}")

NEW_SPECS = [
    ("zuccarelli", "Zuccarelli (artist named by surname in Algarotti's p.295 commission list; given name unresolved)", "person",
     "An artist named only by surname among Algarotti's commissions for Augustus III. Leave given-name and identity alignment for S3.", 306),
    ("private_venetian_pictures", "Contemporary Venetian pictures bought by Augustus III from private collections on p.295", "work",
     "A group of contemporary pictures Augustus III bought from private collections, including works by Piazzetta, Sebastiano Ricci, Nogari and Nazari. Individual works are separated where the text identifies them.", 306),
    ("piazzetta_pair", "Two Piazzetta paintings bought for Augustus III, including the Standard Bearer", "work",
     "A pair of paintings bought from private collections; one is identified as the Standard Bearer and the other remains unnamed.", 306),
    ("ricci_mythologies", "Two unidentified mythological paintings by Sebastiano Ricci bought for Augustus III", "work",
     "A pair of mythological paintings bought from private collections. The passage gives no titles.", 306),
    ("nogari_nazari_heads", "Portraits and fantasy heads by Nogari and Nazari bought for Augustus III", "work",
     "Unspecified portraits and fantasy heads by the two named artists. The passage identifies no individual sitters or titles.", 306),
    ("carriera_four_seasons", "Four Seasons allegories by Rosalba Carriera (mentioned as examples of Augustus III's collection)", "work",
     "A group of allegorical works named as one subject category in Carriera's oeuvre; the passage gives no titles or dates.", 309),
    ("carriera_four_continents", "Four Continents allegories by Rosalba Carriera (mentioned on p.295)", "work",
     "A group of allegorical works named as an example of Carriera's subjects; no individual titles or dates are supplied.", 310),
    ("carriera_four_elements", "Four Elements allegories by Rosalba Carriera (mentioned on p.295)", "work",
     "A group of allegorical works named as an example of Carriera's subjects; no individual titles or dates are supplied.", 310),
    ("carriera_religious_works", "Unidentified religious works by Rosalba Carriera with Magdalene or Virgin subjects", "work",
     "Religious pictures in Carriera's oeuvre described by subject only; the passage gives no title, date or location.", 310),
    ("unnamed_augustus_councillor", "Unnamed councillor of Augustus III who married Felicita Sartori", "person",
     "Sartori is said to have married one of Augustus III's councillors; the councillor is not named and is not identified with a specific officeholder.", 312),
    ("court_painter_role", "Pittore di corte (court-painter post held by Bernardo Bellotto in Dresden)", "term",
     "The printed Italian title for Bellotto's court-painter post. The source says he was appointed within a year of arriving in Dresden in 1747 and held the post until the court broke up after the Seven Years War.", 315),
    ("dresden_court_augustus_iii", "Dresden court under Augustus III served by Bernardo Bellotto", "institution",
     "The court Bellotto served as pittore di corte, which Haskell says broke up after the disasters of the Seven Years War. Keep distinct from the earlier court under Augustus the Strong pending S3 alignment.", 315),
    ("bellotto_views", "Bernardo Bellotto's views of Dresden produced in three sizes for royal, ministerial and other clients", "work",
     "A body of city views painted during Bellotto's Dresden court service. Haskell says they were often made in three sizes for the King, Count Brühl and other clients; individual titles are not given.", 315),
    ("church_cross", "Church of the Cross in Dresden (ruined in Frederick the Great's bombardment)", "place",
     "The Dresden church whose ruins Bellotto painted after a bombardment wrecked it. Keep the building distinct from Bellotto's painting of its ruins.", 315),
    ("frederick_bombardment", "Frederick the Great's bombardment of Dresden that wrecked the Church of the Cross", "event",
     "A bombardment attributed by Haskell to Frederick the Great; the passage says it wrecked the Church of the Cross and shocked Europe but gives no date here.", 315),
    ("unnamed_bavarian_elector", "Unnamed Elector of Bavaria described as Clemens August's younger brother", "person",
     "An elector named only by office and territory as Clemens August's younger brother. Do not infer a personal identity from this passage.", 316),
    ("bamboccianti", "Bamboccianti (artistic comparison invoked for the everyday realism of Bellotto's Dresden views)", "term",
     "The art-historical group/style used by Haskell as a comparison for the everyday observation in Bellotto's views. The passage does not identify individual Bamboccianti artists.", 315),
    ("carriera_portraits", "Unidentified portraits by Rosalba Carriera of friends, acquaintances and unfamiliar women", "work",
     "Portraits identified only by sitter relationship or broad description in Haskell's account of Carriera's subject range; no individual title, sitter or date is given.", 309),
    ("archbishop_elector_cologne_role", "Archbishop-Elector of Cologne (title held by Clemens August)", "term",
     "The ecclesiastical and electoral title Haskell gives for Clemens August; this term records the title without creating a second person identity.", 316),
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
for line in range(304, 317):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p295-{local}"
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
    ("algarotti-king-purchase",305,"purchase pictures for the King whom he was then serving",E["algarotti_augustus_pictures"],"Closes p.294 L302 'especially to'; the King is Augustus III in the preceding context."),
    ("king",305,"the King",E["augustus_iii"],"Ruler whom Algarotti was serving; linked to the preceding Augustus III context."),
    ("algarotti-commissions",305,"Algarotti’s commissions",E["algarotti"],"Commission activity described as related to Augustus III's purchases."),
    ("tiepolo",306,"Tiepolo",E["tiepolo"],"Named among artists receiving Algarotti commissions."),
    ("piazzetta-commission",306,"Piazzetta",E["piazzetta"],"Named among artists receiving Algarotti commissions."),
    ("amigoni-commission",306,"Amigoni",E["amigoni"],"Named among artists receiving Algarotti commissions."),
    ("pittoni-commission",306,"Pittoni",E["pittoni"],"Named among artists receiving Algarotti commissions."),
    ("zuccarelli",306,"Zuccarelli",C["zuccarelli"],"Artist is named only by surname in the source."),
    ("private-contemporary-pictures",306,"many pictures by these and other contemporary artists from private collections",C["private_venetian_pictures"],"Group of acquisitions from private collections, distinct from commissions."),
    ("piazzettas",306,"two superb Piazzettas",C["piazzetta_pair"],"Two paintings; one is identified below as the Standard Bearer."),
    ("piazzetta-standard",306,"Standard Bearer",E["standard_bearer"],"Page-specific index sub-entry for one of the two Piazzetta pictures."),
    ("ricci",306,"Sebastiano Ricci",E["ricci"],"Named painter of two mythological pictures."),
    ("ricci-mythologies",306,"two fine mythologies",C["ricci_mythologies"],"Two unnamed works by Ricci."),
    ("nogari",306,"Nogari",E["nogari"],"Named artist of portraits and fantasy heads."),
    ("nazari",306,"Nazari",E["nazari"],"Named artist of portraits and fantasy heads."),
    ("nogari-nazari-works",306,"portraits and fantasy heads by Nogari and Nazari",C["nogari_nazari_heads"],"Unidentified group of works; no sitter or title is supplied."),
    ("flanders",307,"Flanders",E["flanders"],"Named as the source from which this type of picture was ultimately derived."),
    ("augustus-appeal",308,"Augustus",E["augustus_iii"],"Corefers to Augustus III; he is the King in the preceding sentence."),
    ("carriera-favourite",308,"Rosalba Carriera",E["carriera"],"Named as Augustus III's special favourite."),
    ("carriera-collection",308,"whose works he collected avidly on his own account",E["carriera_collection"],"Maps Augustus III's own collection of Carriera works; collection type remains unresolved."),
    ("they-met",308,"They had met",E["carriera"],"Carriera is one of the two people in this meeting statement; the other is Augustus III."),
    ("venice-visits",308,"Venice",E["venice"],"Place of Augustus III's early-century visits while crown prince."),
    ("crown-prince",308,"as crown prince",E["augustus_iii"],"Role of Augustus III during the early-century Venice visits."),
    ("carriera-recorded",308,"whose features she recorded",E["carriera"],"Pronoun refers to Rosalba Carriera; the quoted description of the ladies remains Haskell's wording."),
    ("pastels",308,"the number of pastels he had acquired from her on those occasions",E["carriera_collection"],"Unspecified works acquired during Augustus III's early visits; the passage says he was dissatisfied with their number."),
    ("reign",309,"Throughout his reign",E["augustus_iii"],"Corefers to Augustus III."),
    ("artist-herself",309,"the artist herself",E["carriera"],"Rosalba Carriera as the direct source of further acquisitions."),
    ("carriera-portraits",309,"portraits of friends and acquaintances or of pretty women he had never known",C["carriera_portraits"],"Unidentified portrait works in Carriera's described subject range; no sitter or title is supplied."),
    ("four-seasons",309,"the Four Seasons",C["carriera_four_seasons"],"Named allegorical group in Carriera's subject range."),
    ("four-continents",309,"the Four\nContinents",C["carriera_four_continents"],"Named allegorical group across an OCR line break in Carriera's subject range."),
    ("four-elements",310,"the Four Elements",C["carriera_four_elements"],"Named allegorical group in Carriera's subject range."),
    ("magdalene",310,"the Magdalene",E["magdalene"],"Religious subject named in Carriera's oeuvre; historical identity alignment remains for S3."),
    ("virgin-mary",310,"the Virgin\nMary",E["virgin_mary"],"Religious subject across an OCR line break; no individual painting is named."),
    ("carriera-religious-pictures",310,"religious subjects such as the Magdalene or the Virgin\nMary",C["carriera_religious_works"],"Group of unidentified works described by subject only."),
    ("carriera-work-count",311,"over 150 examples of her work",E["carriera_collection"],"The author gives a lower-bound count of works acquired by Augustus III by the end of his life."),
    ("sartori",312,"Felicita Sartori",E["sartori"],"Page-specific index entry; source spells the name without an accent."),
    ("sartori-pupil",312,"Rosalba’s best pupil",E["sartori"],"Relation to Carriera as stated by Haskell."),
    ("unnamed-councillor",312,"one of his councillors",C["unnamed_augustus_councillor"],"Unnamed person whom Sartori had married; do not infer identity."),
    ("dresden-sartori",313,"Dresden",E["dresden"],"Place Sartori came to in 1741."),
    ("sartori-work",313,"worked extensively for him",E["augustus_iii"],"Haskell says Sartori worked extensively for Augustus III."),
    ("bellotto-reference",314,"Another Venetian artist",E["bellotto"],"Sentence refers forward to Bernardo Bellotto, named in the next line."),
    ("augustus-output",314,"Augustus III",E["augustus_iii"],"Patron for whom the artist produced a large part of his output."),
    ("bellotto",315,"Bernardo Bellotto",E["bellotto"],"Named artist arriving in Dresden in 1747."),
    ("canaletto-nephew",315,"Canaletto",E["canaletto"],"Named as Bellotto's uncle."),
    ("bellotto-dresden-arrival",315,"Dresden",E["dresden"],"Destination of Bellotto's 1747 arrival."),
    ("court-painter",315,"‘pittore di corte’",C["court_painter_role"],"Printed Italian title of Bellotto's court post."),
    ("dresden-court",315,"that court",C["dresden_court_augustus_iii"],"Corefers to the court in Dresden under Augustus III."),
    ("seven-years-war",315,"the Seven Years War",E["seven_years_war"],"Named context of the court's break-up; footnote 3 remains pending."),
    ("bellotto-views",315,"large numbers of views",C["bellotto_views"],"Unidentified city views painted during Bellotto's Dresden period."),
    ("bamboccianti",315,"the bamboccianti",C["bamboccianti"],"Stylistic comparison in Haskell's account; not asserted as a direct influence."),
    ("dresden-capital",315,"the busy brilliant capital",E["dresden"],"Dresden as the subject of Bellotto's views; 'brilliant' and 'at the height of its glory' remain authorial characterization."),
    ("series-three-sizes",315,"series of three sizes",C["bellotto_views"],"Formats and patron classes for Bellotto's city-view series."),
    ("king-large-size",315,"the King",E["augustus_iii"],"Recipient for the largest format."),
    ("bruehl-small-size",315,"Count Briihl",E["bruehl"],"S0 OCR form; scan reads Count Brühl. Correction is recorded only in S2."),
    ("bellotto-return",315,"Bellotto returned to Dresden",E["bellotto"],"Return in 1765 after prior employment elsewhere."),
    ("dresden-return",315,"Dresden",E["dresden"],"Place of Bellotto's 1765 return.",1),
    ("augustus-dead",315,"Augustus, his great patron",E["augustus_iii"],"The passage states Augustus III had been dead for two years by Bellotto's 1765 return."),
    ("church-cross",315,"the Church of the Cross",C["church_cross"],"Dresden church, distinct from Bellotto's painting of its ruins."),
    ("bellotto-cross-index",315,"paint the ruins of the Church of the Cross",E["bellotto_cross_work"],"Maps the p.295 index sub-entry for Bellotto's painting."),
    ("frederick-bombardment",315,"a bombardment of Frederick the Great",C["frederick_bombardment"],"Source attributes the bombardment to Frederick the Great; footnote 4 remains pending."),
    ("frederick-great",315,"Frederick the Great",E["frederick_great"],"Named as the ruler whose bombardment wrecked the church."),
    ("europe-shocked",315,"Europe",E["europe"],"Geographic scope of the reported shock at the bombardment."),
    ("no-sovereign-germany",316,"No sovereign in Germany",E["germany"],"Opening of Haskell's comparison of Augustus III's patronage with other rulers."),
    ("augustus-german-patronage",316,"Augustus",E["augustus_iii"],"Corefers to Augustus III, Bellotto's great patron."),
    ("german-patronage-index",316,"his patronage or collecting",E["german_patronage"],"Maps the index topic of German patronage of Venetian artists."),
    ("venetian-painting",316,"contemporary Venetian painting",E["venetian_school"],"Artistic field in the comparison of German patrons."),
    ("clemens-august",316,"Clemens August",E["clemens_august"],"Named Archbishop-Elector of Cologne and frequent visitor to Venice."),
    ("archbishop-elector",316,"Archbishop-Elector of Cologne",C["archbishop_elector_cologne_role"],"Title given for Clemens August; preserved as a term rather than duplicated as another person candidate."),
    ("bavaria-elector",316,"the Elector of Bavaria",C["unnamed_bavarian_elector"],"Unnamed younger brother of Clemens August; identity remains unresolved."),
    ("amigoni-bavaria-clause",316,"who had employed Amigoni",E["amigoni"],"The source clause does not make clear whether 'who' refers to Clemens August or the Elector of Bavaria."),
    ("clemens-venice-visitor",316,"a frequent visitor to Venice",E["clemens_august"],"Footnote 5 remains pending in the consolidated notes segment."),
    ("venice-clemens",316,"Venice",E["venice"],"Destination Clemens August frequently visited."),
    ("he-too",316,"He too",E["clemens_august"],"Open sentence continues on p.296; do not complete its predicate yet.")
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
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 295,
                  "pdf_physical_page": 24, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        qualifiers["cross_reference_printed_pages"] = [294 if PREV in cross else 296]
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


close_statement = next(row for row in statements if row["statement_id"] == "st-chp10-p294-algarotti-return-open")
if close_statement["segment_id"] != PREV or close_statement["qualifiers"]["source_line_end"] != 302:
    raise SystemExit("p.294 open Algarotti statement changed")
close_statement["qualifiers"]["claim"] = "In 1743 Francesco Algarotti returned to Venice especially to purchase pictures for Augustus III, the King he was serving."
close_statement["qualifiers"]["qualification"] = "The sentence opened on p.294 and closes at p.295 L305. The King is identified from the preceding passage as Augustus III."
close_statement["qualifiers"]["cross_reference_segments"] = [SEG]
close_statement["qualifiers"]["cross_reference_printed_pages"] = [295]

for artist_key, artist_cid, display in (
    ("tiepolo", E["tiepolo"], "Tiepolo"), ("piazzetta", E["piazzetta"], "Piazzetta"),
    ("amigoni", E["amigoni"], "Amigoni"), ("pittoni", E["pittoni"], "Pittoni"),
    ("zuccarelli", C["zuccarelli"], "Zuccarelli"),
):
    add_s(f"st-chp10-p295-algarotti-commission-{artist_key}",305,306,E["algarotti"],artist_cid,
          f"algarotti_commissioned_or_arranged_a_commission_to_{artist_key}_for_augustus_iii",
          "Algarotti’s commissions to", "Zuccarelli are discussed in a later chapter",
          f"Haskell refers to Algarotti's commissions to {display} in the context of purchasing pictures for Augustus III.",
          "The source says the commissions are discussed in a later chapter but gives no work titles or dates here.",
          [E["algarotti"],E["augustus_iii"],artist_cid],layer="authorial report",relation=True,footnote=1)

add_s("st-chp10-p295-private-contemporary-acquisitions",305,306,E["augustus_iii"],C["private_venetian_pictures"],
      "augustus_iii_bought_contemporary_pictures_by_named_venetian_artists_from_private_collections",
      "but he also bought many pictures", "from private collections—",
      "Augustus III also bought many pictures by these and other contemporary artists from private collections.",
      "The source distinguishes these purchases from Algarotti's commissions; the artists and identified work groups are specified in the following list.",
      [E["augustus_iii"],E["algarotti"],C["private_venetian_pictures"],E["tiepolo"],E["piazzetta"],E["amigoni"],E["pittoni"],C["zuccarelli"]],relation=True)
add_s("st-chp10-p295-piazzetta-pair",306,306,E["augustus_iii"],C["piazzetta_pair"],
      "augustus_iii_bought_two_piazzetta_pictures_one_the_standard_bearer",
      "two superb Piazzettas", "one of them the famous Standard Bearer,",
      "Among the pictures bought from private collections were two Piazzetta paintings, one identified as the Standard Bearer.",
      "The other Piazzetta picture is not identified; 'superb' is Haskell's evaluation.",
      [E["augustus_iii"],C["piazzetta_pair"],E["standard_bearer"],E["piazzetta"]],relation=True)
add_s("st-chp10-p295-ricci-mythologies",306,306,E["augustus_iii"],C["ricci_mythologies"],
      "augustus_iii_bought_two_sebastiano_ricci_mythologies_from_private_collections",
      "two fine mythologies by Sebastiano Ricci", "two fine mythologies by Sebastiano Ricci",
      "Augustus III bought two mythological pictures by Sebastiano Ricci from private collections.",
      "The works have no titles in this passage; 'fine' remains the author's evaluation.",
      [E["augustus_iii"],C["ricci_mythologies"],E["ricci"]],relation=True)
add_s("st-chp10-p295-nogari-nazari-pictures",306,307,E["augustus_iii"],C["nogari_nazari_heads"],
      "augustus_iii_bought_portraits_and_fantasy_heads_by_nogari_and_nazari_from_private_collections",
      "portraits and fantasy heads by Nogari and Nazari", "derived from\nFlanders.",
      "Augustus III bought portraits and fantasy heads by Nogari and Nazari; Haskell says this type of picture ultimately derived from Flanders.",
      "No individual portrait, sitter or title is given. The derivation claim is Haskell's account, not independently verified here.",
      [E["augustus_iii"],C["nogari_nazari_heads"],E["nogari"],E["nazari"],E["flanders"]],layer="authorial interpretation",relation=True)
add_s("st-chp10-p295-pictures-appealed",308,308,E["augustus_iii"],C["private_venetian_pictures"],
      "the_contemporary_pictures_appealed_to_augustus_despite_his_initial_reluctance",
      "No doubt all these appealed to Augustus", "works of contemporaries,",
      "Haskell says these contemporary pictures appealed to Augustus despite his initial reluctance to attend to contemporary art.",
      "'No doubt' marks Haskell's inference; retain it as the author's interpretation.",
      [E["augustus_iii"],C["private_venetian_pictures"]],layer="authorial interpretation")
add_s("st-chp10-p295-carriera-favourite",308,308,E["augustus_iii"],E["carriera"],
      "augustus_iii_had_a_special_favourite_rosalba_carriera_whose_works_he_collected_avidly_for_himself",
      "he had one special favourite", "on his own account—Rosalba Carriera.",
      "Haskell describes Rosalba Carriera as Augustus III's special favourite and says he avidly collected her works for his own account.",
      "'Special favourite' and 'avidly' are Haskell's characterizations.",
      [E["augustus_iii"],E["carriera"],E["carriera_collection"]],relation=True)
add_s("st-chp10-p295-carriera-augustus-venice-meeting",308,308,E["carriera"],E["augustus_iii"],
      "carriera_and_augustus_iii_met_during_his_early_century_visits_to_venice_as_crown_prince",
      "They had met during his own visits to Venice", "as crown prince,",
      "Carriera and Augustus III had met during his visits to Venice early in the century, when he was crown prince.",
      "The source gives only an approximate period and describes the ladies' company in Haskell's own evaluative language.",
      [E["carriera"],E["augustus_iii"],E["venice"]],relation=True)
add_s("st-chp10-p295-carriera-pastels-early-visits",308,308,E["augustus_iii"],E["carriera_collection"],
      "augustus_iii_was_dissatisfied_with_the_number_of_carriera_pastels_he_had_acquired_during_early_venice_visits",
      "But he was far from satisfied", "on those occasions.",
      "Augustus III was far from satisfied with the number of pastels he had acquired from Carriera during those early visits.",
      "The source gives no count or titles for these pastels; the collection's type remains unresolved.",
      [E["augustus_iii"],E["carriera"],E["carriera_collection"],E["venice"]],layer="authorial report")
add_s("st-chp10-p295-carriera-continuing-acquisitions",309,309,E["augustus_iii"],E["carriera_collection"],
      "throughout_his_reign_augustus_iii_sought_more_carriera_works_from_the_artist_and_private_collections",
      "Throughout his reign he was always keen to get more", "from private collections.",
      "Throughout his reign Augustus III remained keen to acquire more of Carriera's works, either from the artist or from private collections.",
      "No individual dates, works or private owners are named.",
      [E["augustus_iii"],E["carriera"],E["carriera_collection"]],relation=True)
add_s("st-chp10-p295-carriera-subject-range",309,311,E["carriera"],C["carriera_religious_works"],
      "carriera_made_portraits_allegories_and_religious_works_across_a_wide_range_of_subjects",
      "His choice was catholic", "religious subjects such as the Magdalene or the Virgin\nMary.",
      "Haskell describes Carriera's subjects as catholic in range: portraits of friends, acquaintances and unfamiliar women; allegories including the Four Seasons, Four Continents and Four Elements; and religious subjects such as the Magdalene and Virgin Mary.",
      "The source expresses breadth, not Roman Catholic affiliation. It names subject categories rather than individual work titles.",
      [E["carriera"],C["carriera_portraits"],C["carriera_four_seasons"],C["carriera_four_continents"],C["carriera_four_elements"],C["carriera_religious_works"],E["magdalene"],E["virgin_mary"]])
add_s("st-chp10-p295-carriera-collection-size",311,311,E["augustus_iii"],E["carriera_collection"],
      "by_the_end_of_augustus_iiis_life_he_had_acquired_over_150_carriera_works",
      "by the end of his life he had acquired over 150 examples", "of her work,",
      "By the end of Augustus III's life he had acquired over 150 examples of Carriera's work.",
      "The source gives a lower-bound count; the collection type remains unresolved.",
      [E["augustus_iii"],E["carriera"],E["carriera_collection"]],relation=True)
add_s("st-chp10-p295-sartori-marriage",312,312,E["sartori"],C["unnamed_augustus_councillor"],
      "felicita_sartori_married_an_unnamed_councillor_of_augustus_iii",
      "who had married one of his councillors", "one of his councillors,",
      "Haskell says Felicita Sartori had married one of Augustus III's councillors.",
      "The councillor is not named, and the passage provides no further office or identity.",
      [E["sartori"],C["unnamed_augustus_councillor"],E["augustus_iii"]],relation=True)
add_s("st-chp10-p295-sartori-dresden-work",312,313,E["sartori"],E["augustus_iii"],
      "felicita_sartori_came_to_dresden_in_1741_and_worked_extensively_for_augustus_iii",
      "came to", "worked extensively for him.2",
      "Felicita Sartori came to Dresden in 1741 and worked extensively for Augustus III.",
      "Footnote 2 remains pending in the consolidated notes segment; the source gives no exact start or end date for her work.",
      [E["sartori"],E["dresden"],E["augustus_iii"]],relation=True,footnote=2)
add_s("st-chp10-p295-bellotto-output-for-augustus",314,314,E["bellotto"],E["augustus_iii"],
      "bellotto_produced_a_great_proportion_of_his_output_for_augustus_iii",
      "Another Venetian artist produced a great proportion", "for Augustus III.",
      "Haskell says another Venetian artist produced a great proportion of his output for Augustus III; the following sentence identifies him as Bernardo Bellotto.",
      "The sentence refers forward to Bellotto; 'great proportion' is not quantified.",
      [E["bellotto"],E["augustus_iii"]],relation=True)
add_s("st-chp10-p295-bellotto-arrival-and-court-post",315,315,E["bellotto"],C["court_painter_role"],
      "bellotto_arrived_in_dresden_in_1747_and_within_a_year_was_appointed_pittore_di_corte",
      "In 1747 Bernardo Bellotto", "appointed ‘pittore di corte’",
      "Bernardo Bellotto arrived in Dresden in 1747 and was appointed pittore di corte within a year.",
      "The source gives an interval, not an exact appointment year. Footnote 3 remains pending.",
      [E["bellotto"],E["dresden"],C["court_painter_role"],C["dresden_court_augustus_iii"]],relation=True,footnote=3)
add_s("st-chp10-p295-bellotto-court-service",315,315,E["bellotto"],C["dresden_court_augustus_iii"],
      "bellotto_held_the_dresden_court_painter_post_until_the_court_broke_up_after_the_seven_years_war",
      "a post which he held", "after the disasters of the Seven Years War.",
      "Bellotto held the Dresden court-painter post until that court broke up after the disasters of the Seven Years War.",
      "The source does not give the break-up date; footnote 3 remains pending.",
      [E["bellotto"],C["court_painter_role"],C["dresden_court_augustus_iii"],E["seven_years_war"]],relation=True,footnote=3)
add_s("st-chp10-p295-bellotto-city-views",315,315,E["bellotto"],C["bellotto_views"],
      "bellotto_painted_many_dresden_views_with_everyday_observation_haskell_compared_to_the_bamboccianti",
      "During that time he painted large numbers of views", "the height of its glory.",
      "During his Dresden court service Bellotto painted large numbers of views of the capital; Haskell praises their everyday observation and compares it with the Bamboccianti, describing Dresden as busy, brilliant and at the height of its glory.",
      "The comparison is not asserted as direct influence; the evaluative descriptions remain Haskell's.",
      [E["bellotto"],C["bellotto_views"],E["dresden"],C["bamboccianti"]],layer="authorial interpretation")
add_s("st-chp10-p295-bellotto-view-formats",315,315,E["bellotto"],C["bellotto_views"],
      "bellotto_often_produced_his_views_in_three_sizes_for_the_king_count_bruehl_and_other_clients",
      "They were often produced in series of three sizes", "and a third example for other clients.",
      "Bellotto's views were often produced in three sizes: the largest for the King, a smaller version for Count Brühl and a third example for other clients.",
      "'Often' is retained; the source does not say that every view existed in all three sizes. S0 OCR 'Briihl' is checked against the scan and corrected only in S2.",
      [E["bellotto"],C["bellotto_views"],E["augustus_iii"],E["bruehl"]],relation=True)
add_s("st-chp10-p295-bellotto-return-1765",315,315,E["bellotto"],E["dresden"],
      "bellotto_returned_to_dresden_in_1765_after_finding_employment_elsewhere",
      "In 1765", "Bellotto returned to Dresden.",
      "Bellotto returned to Dresden in 1765 after he had found employment elsewhere.",
      "The source does not name the other employment.",
      [E["bellotto"],E["dresden"]],relation=True,footnote=4)
add_s("st-chp10-p295-augustus-death-before-return",315,315,E["augustus_iii"],E["bellotto"],
      "augustus_iii_had_been_dead_two_years_when_bellotto_returned_in_1765",
      "Augustus, his great patron, had been dead two years", "two years",
      "Augustus III, Bellotto's great patron, had been dead for two years when Bellotto returned in 1765.",
      "The two-year interval is the source's relative chronology; it is not expanded here to an exact death date.",
      [E["augustus_iii"],E["bellotto"]],relation=True)
add_s("st-chp10-p295-cross-church-painting",315,315,E["bellotto"],E["bellotto_cross_work"],
      "bellotto_painted_the_ruins_of_the_church_of_the_cross_after_its_destruction_by_bombardment",
      "paint the ruins of the Church of the Cross", "Then he left.",
      "Bellotto stayed just long enough after his 1765 return to paint the ruins of Dresden's Church of the Cross, which had been wrecked in a bombardment attributed to Frederick the Great.",
      "The building and painting are distinct candidates. Footnote 4 remains pending in the consolidated notes segment.",
      [E["bellotto"],E["dresden"],C["church_cross"],E["bellotto_cross_work"],C["frederick_bombardment"],E["frederick_great"]],relation=True,footnote=4)
add_s("st-chp10-p295-bombardment-shocked-europe",315,315,C["frederick_bombardment"],E["europe"],
      "frederick_the_greats_bombardment_of_dresden_shocked_europe",
      "a bombardment of Frederick the Great", "that had shocked Europe.",
      "Haskell says Frederick the Great's bombardment that wrecked the Church of the Cross had shocked Europe.",
      "The source supplies no date in this passage; 'shocked Europe' is preserved as Haskell's characterization.",
      [C["frederick_bombardment"],E["frederick_great"],C["church_cross"],E["europe"]],layer="authorial interpretation")
add_s("st-chp10-p295-augustus-german-patronage-comparison",316,316,E["augustus_iii"],E["germany"],
      "haskell_says_no_sovereign_in_germany_could_rival_augustus_iiis_patronage_or_collecting",
      "No sovereign in Germany could rival Augustus", "contemporary Venetian painting.",
      "Haskell says no sovereign in Germany could rival Augustus III in patronage or collecting, while other rulers of more limited means showed equal enthusiasm for contemporary Venetian painting.",
      "This is an authorial comparison without a measure of resources or enthusiasm; 'Augustus' is identified as Augustus III from the preceding account.",
      [E["augustus_iii"],E["germany"],E["german_patronage"],E["venetian_school"]],layer="authorial interpretation")
add_s("st-chp10-p295-clemens-title",316,316,E["clemens_august"],C["archbishop_elector_cologne_role"],
      "clemens_august_held_the_title_archbishop_elector_of_cologne",
      "Thus Clemens August", "Archbishop-Elector of Cologne",
      "Haskell identifies Clemens August by the title Archbishop-Elector of Cologne.",
      "The title is recorded as a term; it does not establish an additional personal identity.",
      [E["clemens_august"],C["archbishop_elector_cologne_role"]],relation=True)
add_s("st-chp10-p295-clemens-sibling",316,316,E["clemens_august"],C["unnamed_bavarian_elector"],
      "clemens_august_was_the_younger_brother_of_the_elector_of_bavaria",
      "younger brother of the Elector of Bavaria", "of Bavaria,",
      "Haskell says Clemens August was the younger brother of the Elector of Bavaria.",
      "The Elector of Bavaria is not named; do not infer a personal identity from the title alone.",
      [E["clemens_august"],C["unnamed_bavarian_elector"]],relation=True)
add_s("st-chp10-p295-clemens-venice-visits",316,316,E["clemens_august"],E["venice"],
      "clemens_august_was_a_frequent_visitor_to_venice",
      "was also a frequent visitor", "to Venice.",
      "Haskell describes Clemens August as a frequent visitor to Venice.",
      "The passage gives no dates or duration; footnote 5 remains pending in the consolidated notes segment.",
      [E["clemens_august"],E["venice"]],relation=True,footnote=5)
add_s("st-chp10-p295-amigoni-employment-ambiguous",316,316,E["clemens_august"],E["amigoni"],
      "the_relative_who_had_employed_amigoni_is_ambiguous_between_clemens_august_and_the_elector_of_bavaria",
      "who had employed Amigoni", "who had employed Amigoni",
      "The sentence says that a person in the Clemens August/Elector of Bavaria clause had employed Amigoni, but its relative pronoun does not clearly identify which person.",
      "Keep the antecedent unresolved; do not convert this clause into a settled employment relation.",
      [E["clemens_august"],C["unnamed_bavarian_elector"],E["amigoni"]],layer="ambiguous reported narrative")

cov[PREV].update({"migration_status":"complete", "source_line_ranges":"L293-302",
                  "note":"Printed p.294 final Algarotti sentence opened at L302 and closes at p.295 L305; closure is linked from st-chp10-p294-algarotti-return-open. The p.294 body is complete; notes 1-3 remain pending in the consolidated notes segment."})
cov[SEG].update({"disposition":"reviewed", "migration_status":"partial", "source_line_ranges":"L305-316",
                 "note":"Printed p.295 was checked against CHP-10.pdf physical page 24. Closed the p.294 Algarotti sentence at L305 and recorded commissions for Tiepolo, Piazzetta, Amigoni, Pittoni and surname-only Zuccarelli; Augustus III's contemporary purchases from private collections; Piazzetta's Standard Bearer, Ricci mythologies, Nogari/Nazari portraits and fantasy heads; Carriera's portrait, allegorical and religious subject range, early pastels and over-150-work count; Felicita Sartori's marriage and Dresden employment; Bellotto's court service, views, patron formats, 1765 return and painting of the bomb-damaged Church of the Cross; Haskell's German-patronage comparison and Clemens August's title, sibling and Venice-visit claims. Kept the Bellotto court distinct from Augustus the Strong's earlier court, separated building from painting, and retained uncertainty about the unnamed Bavarian elector and the Amigoni clause antecedent. S2 scan corrections: OCR 'Count Briihl' reads 'Count Brühl'; 'ofhis' reads 'of his'; and superscript 6 after Venice is superscript 5 in print. Footnotes 1-5 link to the consolidated notes segment; the last sentence is unfinished, not a footnote 6. The page ends 'He too was naturally an' and continues on p.296, so p.295 remains partial."})
cov[NEXT]["note"] = "Next source-order segment is printed p.296 at L318-330; it closes the p.295 'He too was naturally an' fragment and the remaining p.295 footnote 6 context."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"segment_sha256":SEG_SHA,"new_candidates":len(newc),
                  "candidate_ids":[row["candidate_id"] for row in newc],"new_mentions":len(newm),
                  "new_statements":len(new_s),"coverage":{"p294":cov[PREV]["migration_status"],
                  "p295":cov[SEG]["migration_status"],"p296":cov[NEXT]["migration_status"]}},
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
    print("Applied p.295 S2 migration; p.295 remains partial pending p.296 and consolidated notes.")
