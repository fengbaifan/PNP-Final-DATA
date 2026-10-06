"""Controlled S2 migration for printed p.296; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l304-316"
SEG = "chp-10:10_CHP-10_intro:l318-330"
NEXT = "chp-10:10_CHP-10_intro:l332-343"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEG_SHA = "9b78eeb58e0f2a805f17499460a4cf76f21530f849917beb42329bbad5b2205c"
BACKUP = ".bak-s2-chp10-p296-20261002"


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
body = "\n".join(src[317:330])
SEG_SHA = hashlib.sha256(body.encode("utf-8")).hexdigest()
if SEG_SHA != EXPECTED_SEG_SHA or src[317].strip() != "[Page 296]" or "Karl Philip von Greiffenklau" not in body or "Sebastiano" not in body:
    raise SystemExit("p.296 source segment/page mismatch")

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
if maximum != 9116:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")),
                      (NEXT, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "carriera": "cand-0581", "clemens_august": "cand-0788", "german_patronage": "cand-1146",
    "karl_philip": "cand-1230", "juvarra": "cand-1339", "neumann": "cand-1736",
    "pellegrini": "cand-1862", "piazzetta": "cand-1901", "piazzetta_index": "cand-1905",
    "pittoni": "cand-1950", "marco_ricci": "cand-2149", "sebastiano_ricci": "cand-2154",
    "frederick_karl": "cand-2397", "schonborn_family": "cand-2400", "tiepolo": "cand-2569",
    "turin": "cand-2662", "venice": "cand-2719", "residenz": "cand-2822",
    "virgin_mary": "cand-3427", "staircase_fresco": "cand-4180", "rezzonico_work": "cand-4105",
    "rezzonico_family": "cand-3615", "absolutism": "cand-6923", "venetian_art": "cand-8094",
    "germany": "cand-5529", "carriera_collection": "cand-8851",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
for key, cid, page, sub in (
    ("clemens_august", E["clemens_august"], "295, 296", ""),
    ("karl_philip", E["karl_philip"], "296", ""),
    ("neumann", E["neumann"], "296", ""),
    ("piazzetta_assumption_index", E["piazzetta_index"], "296", "Assumption of the Virgin"),
    ("tiepolo", E["tiepolo"], "xvii, 192, 214, 246, 248, 250, 252, 254, 255, 256, 262, 264, 265, 266, 267, 268, 269n, 270, 271, 272, 276, 279, 293, 296, 297, 302, 309, 315, 322, 323, 332, 333, 342, 343, 344, 345, 361, 374, 376, 377, 383n, 393, 405n, 406, 409", ""),
    ("residenz", E["residenz"], "296", ""),
    ("turin", E["turin"], "", ""),
):
    row = next(row for row in candidates if row["candidate_id"] == cid)
    if row["index_page_range"] != page or row["sub_entry"] != sub:
        raise SystemExit(f"unexpected candidate {key}={cid}: {row}")

NEW_SPECS = [
    ("wurzburg_city", "Würzburg city (distinct from the Residenz palace)", "place",
     "The city where Tiepolo was persuaded to work and where the Residenz stands; keep distinct from the palace and Kaisersaal.", 320),
    ("wurzburg_bishopric", "Bishopric of Würzburg (institutional see discussed on p.296)", "institution",
     "The bishopric described as passing from the Schönborn family through an unnamed successor to Karl Philip von Greiffenklau.", 320),
    ("unnamed_successor", "Unnamed successor to Frederick Karl in the Würzburg bishopric", "person",
     "A successor who held the bishopric for a short interval after Frederick Karl's death in 1746; the source does not give a name.", 320),
    ("clemens_pastels", "Unidentified pastels by Rosalba Carriera owned by Clemens August", "work",
     "Pastel works by Carriera that Haskell says Clemens August owned; no titles, dates or number are supplied.", 319),
    ("clemens_altarpieces", "Unidentified altar paintings commissioned by Clemens August for churches under his patronage", "work",
     "An unspecified group of altar paintings by Pittoni, Piazzetta and Tiepolo; the passage gives no titles or church locations.", 319),
    ("piazzetta_assumption", "Assumption of the Virgin painted by Giovanni Battista Piazzetta in 1735", "work",
     "A work named by subject and artist; Haskell dates it to 1735 and says it showed the first signs of Piazzetta's lighter manner, but gives no location here.", 319),
    ("kaisersaal", "Kaisersaal in the Würzburg Residenz", "place",
     "The room Tiepolo was persuaded to decorate inside the Würzburg Residenz; distinguish it from the palace and its staircase.", 321),
    ("kaisersaal_cycle", "Tiepolo's decoration of the Kaisersaal in the Würzburg Residenz", "work",
     "A group of Kaisersaal paintings described on p.296, including ceiling and wall scenes; keep the specific scenes distinct.", 321),
    ("apollo_ceiling", "Tiepolo's Kaisersaal ceiling scene of Apollo leading Beatrice to Frederick Barbarossa", "work",
     "The ceiling composition described by Haskell; its later Rezzonico adaptation is reported separately and not treated as the same work.", 322),
    ("apollo_figure", "Apollo represented in Tiepolo's Würzburg Kaisersaal ceiling scene", "person",
     "A mythological figure in this particular painting; cross-work identity with Apollo candidates elsewhere is for S3.", 322),
    ("frederick_barbarossa", "Frederick Barbarossa named in the Würzburg fresco narrative", "person",
     "The historical emperor whose bride Beatrice is shown in Tiepolo's ceiling scene; later 'the Emperor' in the 1163 clause is linked to this context, subject to S3 identity review.", 322),
    ("beatrice_burgundy", "Beatrice of Burgundy, identified as Frederick Barbarossa's bride in the fresco narrative", "person",
     "A historical person named as the bride in Tiepolo's Würzburg ceiling composition; the passage does not independently verify the iconography.", 322),
    ("marriage_scene", "Kaisersaal wall scene of a marriage blessed by the Bishop of Würzburg in 1156", "work",
     "A wall painting described by subject and date; the couple is not named in this clause and no title or version is supplied.", 323),
    ("unnamed_bishop_1156", "Unnamed Bishop of Würzburg associated with the marriage scene of 1156", "person",
     "A bishop identified by office, see and date but not by personal name in Haskell's description.", 323),
    ("investiture_scene", "Kaisersaal wall scene of Bishop Harold von Hocheim's investiture in 1163", "work",
     "A wall painting described by subject, participant and date; no title or independent iconographic source is supplied.", 323),
    ("harold_hocheim", "Bishop Harold von Hocheim named in the Kaisersaal investiture scene", "person",
     "A bishop whose investiture is dated to 1163 in Haskell's account; spelling and historical identity remain for S3 verification.", 323),
    ("scagliola", "Scagliola used in the ornamentation of the Kaisersaal", "term",
     "A decorative material named in Haskell's description of the Kaisersaal; this mention does not identify a particular maker or technique.", 321),
    ("german_medieval_history", "German medieval history as a source for the Kaisersaal painting subjects", "term",
     "The historical subject field Haskell says was unfamiliar to Tiepolo; no specific chronicle or event is cited in this clause.", 321),
    ("german_princely_clergy", "German princely clergy discussed in Haskell's comparison with Venetian clients", "term",
     "A collective category used in the author's contrast about ancestry and feudal society; do not infer membership from this phrase.", 325),
    ("ancien_regime", "Ancien régime represented in Tiepolo's Würzburg staircase fresco", "term",
     "Haskell's interpretive characterization of the political society represented in the fresco; retain as the author's language.", 328),
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
for line in range(318, 331):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p296-{local}"
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
    ("rosalba",319,"Rosalba",E["carriera"],"The p.295 subject 'He too' resolves to Clemens August; Carriera is named here."),
    ("pastels",319,"pastels",C["clemens_pastels"],"Unidentified Carriera pastels owned by Clemens August."),
    ("altar-paintings",319,"altar paintings",C["clemens_altarpieces"],"Unidentified group commissioned for churches under Clemens August's patronage."),
    ("pittoni",319,"Pittoni",E["pittoni"],"Named among painters of the altar works."),
    ("piazzetta",319,"Piazzetta",E["piazzetta"],"Named before the description of his Assumption."),
    ("assumption",320,"Assumption of the Virgin",C["piazzetta_assumption"],"Named work; no church location is supplied here."),
    ("tiepolo-altar",320,"Tiepolo",E["tiepolo"],"Named among painters of Clemens August's altar works."),
    ("german-patronage",320,"German patronage of Venetian art",E["german_patronage"],"Matches the indexed topic of German patronage of Venetian artists."),
    ("venetian-art",320,"Venetian art itself",E["venetian_art"],"The artistic field said to reach a climax in 1750."),
    ("tiepolo-residenz-commission",320,"Tiepolo",E["tiepolo"],"Artist named in the 1750 Residenz commission clause.",1),
    ("residenz",320,"Residenz",E["residenz"],"Würzburg palace, distinct from the city."),
    ("wurzburg",320,"Würzburg",C["wurzburg_city"],"City; not the Residenz building."),
    ("bishopric",320,"bishopric",C["wurzburg_bishopric"],"Institutional see, not a building or person."),
    ("schonborn-family",320,"Schonborn family",E["schonborn_family"],"S0 OCR omits the umlaut; the scan reads Schönborn."),
    ("frederick-karl",320,"Frederick Karl",E["frederick_karl"],"Named as the previous holder of the bishopric."),
    ("successor",320,"his successor",C["unnamed_successor"],"Unnamed successor who held the see for a short interval."),
    ("karl-philip",320,"Karl Philip von Greiffenklau",E["karl_philip"],"Named as the person who took over the see."),
    ("tiepolo-persuaded",320,"Tiepolo",E["tiepolo"],"Artist persuaded to come to Würzburg and work in the Kaisersaal.",2),
    ("wurzburg-persuaded",321,"Wurzburg",C["wurzburg_city"],"S0 omits the umlaut; the scan reads Würzburg."),
    ("kaisersaal",321,"Kaisersaal",C["kaisersaal"],"Room inside the Residenz, distinct from the palace."),
    ("neumann",321,"Balthasar Neumann",E["neumann"],"Named architect of the palace."),
    ("palace",321,"magnificent palace",E["residenz"],"The Würzburg Residenz, not a separate building candidate."),
    ("tiepolo-foreign-room",321,"Tiepolo",E["tiepolo"],"Named as the artist for whom the room was unfamiliar."),
    ("scagliola",321,"scagliola",C["scagliola"],"Material named in the room description."),
    ("medieval-history",321,"German mediaeval history",C["german_medieval_history"],"Subject field of the paintings, described as unfamiliar to Tiepolo."),
    ("apollo",322,"Apollo",C["apollo_figure"],"Mythological figure depicted in this specific ceiling scene; identity alignment remains for S3."),
    ("barbarossa",322,"Frederick Barbarossa",C["frederick_barbarossa"],"Historical figure named in the ceiling scene."),
    ("beatrice",322,"Beatrice of Burgundy",C["beatrice_burgundy"],"Named as Frederick Barbarossa's bride in the depicted scene."),
    ("awaiting-emperor",322,"awaiting Emperor",C["frederick_barbarossa"],"The Emperor is linked to Frederick Barbarossa from the same fresco clause."),
    ("rezzonico-family",322,"Rezzonico family",E["rezzonico_family"],"Family for whom Haskell says the composition was later adapted."),
    ("venice-rezzonico",322,"Venice",E["venice"],"Place associated with the Rezzonico adaptation."),
    ("marriage-scene",322,"Marriage of the couple",C["marriage_scene"],"Unidentified Kaisersaal wall painting, described by subject and date."),
    ("bishop-1156",322,"Bishop of",C["unnamed_bishop_1156"],"Unnamed bishop; the location continues on the next OCR line."),
    ("wurzburg-bishop",323,"Würzburg",C["wurzburg_city"],"City named in the printed text; OCR spelling is checked against the scan."),
    ("harold",323,"Bishop Harold von Hocheim",C["harold_hocheim"],"Named participant in the investiture scene; identity alignment remains for S3."),
    ("investiture-scene",323,"being invested with the princedom",C["investiture_scene"],"Describes the subject of a separate Kaisersaal wall painting."),
    ("emperor-1163",324,"Emperor",C["frederick_barbarossa"],"The clause appears in the same Barbarossa narrative; retain identity as an S3-checkable candidate."),
    ("princely-clergy",324,"German princely clergy",C["german_princely_clergy"],"Collective category in Haskell's social and historical interpretation."),
    ("tiepolo-clients",325,"Tiepolo’s Venetian clients",E["tiepolo"],"Tiepolo is named as the artist with Venetian clients."),
    ("tiepolo-quote",325,"Tiepolo",E["tiepolo"],"Person named in the reported quoted characterization.",1),
    ("kaisersaal-complete",326,"Kaisersaal",C["kaisersaal"],"Room whose decoration had been completed."),
    ("tiepolo-staircase",326,"Tiepolo",E["tiepolo"],"Artist agreeing to the subsequent staircase ceiling."),
    ("staircase-fresco",326,"ceiling of the great staircase",E["staircase_fresco"],"Reuses the existing Plate 50 whole-fresco candidate cand-4180."),
    ("four-continents",326,"The Four Continents",E["staircase_fresco"],"Subject/title phrase for the Plate 50 staircase fresco, not Carriera's subject group."),
    ("karl-philip-homage",327,"Philip von Greiffenklau",E["karl_philip"],"Name continues across the OCR line break; person honoured in the staircase fresco."),
    ("theme",327,"this theme",E["staircase_fresco"],"Refers back to the staircase fresco subject."),
    ("tiepolo-absolutism",327,"Tiepolo",E["tiepolo"],"Subject of Haskell's interpretive comparison."),
    ("absolutism",327,"absolutism",E["absolutism"],"Political idea invoked in Haskell's interpretation of the fresco."),
    ("pellegrini",328,"Pellegrini",E["pellegrini"],"Artist used in Haskell's generational comparison."),
    ("fresco",328,"this fresco",E["staircase_fresco"],"The Würzburg staircase fresco."),
    ("ancien-regime",328,"ancien régime",C["ancien_regime"],"Haskell's characterization of the society represented."),
    ("germany",329,"Germany",E["germany"],"Political/geographic comparator in the account of other courts."),
    ("venice-talent",329,"Venice",E["venice"],"Place from which other courts sought artists."),
    ("turin",330,"Turin",E["turin"],"City whose rise is referenced from an earlier chapter."),
    ("juvarra",330,"Filippo Juvarra",E["juvarra"],"Architect described as artistic director of Turin."),
    ("city-juvarra",330,"the city",E["turin"],"Corefers to Turin."),
    ("sebastiano",330,"Sebastiano",E["sebastiano_ricci"],"P.296 sentence stops at his given name; p.297 continuation is needed to verify the full reference."),
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
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 296,
                  "pdf_physical_page": 25, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        qualifiers["cross_reference_printed_pages"] = [295 if PREV in cross else 297]
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


add_s("st-chp10-p296-clemens-carriera-pastels",319,319,E["clemens_august"],C["clemens_pastels"],
      "clemens_august_owned_pastels_by_rosalba_carriera",
      "admirer of Rosalba", "pastels by her.",
      "The p.295 sentence closes by identifying Clemens August as an admirer of Rosalba Carriera who owned pastels by her.",
      "The subject is resolved from p.295 'He too'; no pastel titles or number are supplied.",
      [E["clemens_august"],E["carriera"],C["clemens_pastels"]],relation=True,cross=[PREV])
add_s("st-chp10-p296-clemens-altar-commissions",319,320,E["clemens_august"],C["clemens_altarpieces"],
      "clemens_august_commissioned_altar_paintings_for_churches_under_his_patronage_by_pittoni_piazzetta_and_tiepolo",
      "Soon after 1730", "and by Tiepolo.",
      "Soon after 1730 Clemens August began commissioning altar paintings for churches under his patronage by Pittoni, Piazzetta and Tiepolo.",
      "The passage supplies no titles or church locations; the approximate date is retained.",
      [E["clemens_august"],C["clemens_altarpieces"],E["pittoni"],E["piazzetta"],E["tiepolo"]],relation=True)
add_s("st-chp10-p296-piazzetta-assumption",319,320,E["piazzetta"],C["piazzetta_assumption"],
      "piazzettas_assumption_of_the_virgin_was_painted_in_1735_and_showed_early_signs_of_his_lighter_manner",
      "Piazzetta—whose\nAssumption of the Virgin", "his lighter manner—",
      "Haskell identifies Piazzetta's Assumption of the Virgin, painted in 1735, as containing the first signs of the artist's lighter manner.",
      "No location or version is supplied; 'first signs' is Haskell's art-historical judgement.",
      [E["piazzetta"],C["piazzetta_assumption"],E["virgin_mary"]],layer="authorial interpretation")
add_s("st-chp10-p296-german-patronage-residenz-1750",320,320,E["tiepolo"],E["residenz"],
      "tiepolo_was_commissioned_to_decorate_the_residenz_at_the_1750_climax_of_german_patronage_of_venetian_art",
      "But German patronage", "in Würzburg.1",
      "Haskell says German patronage of Venetian art, and Venetian art itself, reached a climax in 1750 when Tiepolo was commissioned to decorate the Würzburg Residenz.",
      "The climax is the author's periodization; the commission is cross-referenced to note 1, not independently verified here.",
      [E["german_patronage"],E["venetian_art"],E["tiepolo"],E["residenz"],C["wurzburg_city"]],
      layer="authorial interpretation",relation=True,footnote=1)
add_s("st-chp10-p296-schonborn-bishopric",320,320,C["wurzburg_bishopric"],E["schonborn_family"],
      "the_wurzburg_bishopric_had_belonged_to_the_schonborn_family",
      "The bishopric had belonged", "whose vast patronage",
      "Haskell says the bishopric had belonged to the Schönborn family.",
      "'Belonged' is preserved as a statement about the see's dynastic control, not literal property ownership.",
      [C["wurzburg_bishopric"],E["schonborn_family"]],relation=True)
add_s("st-chp10-p296-bishopric-transfer",320,320,C["wurzburg_bishopric"],E["karl_philip"],
      "the_wurzburg_bishopric_passed_to_karl_philip_after_frederick_karl_and_a_short_successor_interval",
      "after the death of Frederick Karl in 1746", "taken over by Karl Philip von Greiffenklau.",
      "After Frederick Karl's death in 1746 and a short interval under an unnamed successor, the Würzburg bishopric was taken over by Karl Philip von Greiffenklau.",
      "The interim successor remains unidentified; the passage gives no exact dates for the interval or transfer.",
      [C["wurzburg_bishopric"],E["frederick_karl"],C["unnamed_successor"],E["karl_philip"]],relation=True)
add_s("st-chp10-p296-karl-philip-persuades-tiepolo",320,321,E["karl_philip"],E["tiepolo"],
      "karl_philip_persuaded_tiepolo_to_come_to_wurzburg_and_decorate_the_kaisersaal",
      "It was he who", "for his predecessors.",
      "Haskell says Karl Philip von Greiffenklau, with great difficulty and expense, persuaded Tiepolo to come to Würzburg and decorate the Kaisersaal in the palace.",
      "The statement reports Haskell's account of the commission; the room, palace and city are separate candidates.",
      [E["karl_philip"],E["tiepolo"],C["wurzburg_city"],C["kaisersaal"],E["residenz"]],relation=True)
add_s("st-chp10-p296-neumann-builds-residenz",321,321,E["residenz"],E["neumann"],
      "the_wurzburg_residenz_was_built_by_balthasar_neumann_for_its_predecessors",
      "magnificent palace that had been built", "for his predecessors.",
      "The Würzburg Residenz had been built by Balthasar Neumann for the predecessors of Karl Philip von Greiffenklau.",
      "The passage does not name those predecessors individually.",
      [E["residenz"],E["neumann"],E["karl_philip"]],relation=True)
add_s("st-chp10-p296-kaisersaal-material-and-subjects",321,321,C["kaisersaal"],C["german_medieval_history"],
      "the_kaisersaal_had_rich_scagliola_ornament_and_german_medieval_history_painting_subjects_unfamiliar_to_tiepolo",
      "The beautiful rococo room", "were equally foreign.",
      "Haskell describes the Kaisersaal's rich scagliola ornament and says its subjects, drawn from German medieval history, were unfamiliar to Tiepolo.",
      "The comparison is limited to Tiepolo's prior experience; no specific source text or maker of the ornament is given.",
      [C["kaisersaal"],C["scagliola"],C["german_medieval_history"],E["tiepolo"]],layer="authorial narrative")
add_s("st-chp10-p296-unfamiliarity-stimulates-tiepolo",322,322,E["tiepolo"],C["kaisersaal_cycle"],
      "the_unfamiliar_subjects_stimulated_tiepolo_to_higher_peaks_of_brilliance",
      "But this unfamiliarity", "of brilliance.",
      "Haskell says the unfamiliarity of the subjects stimulated Tiepolo to higher peaks of brilliance.",
      "This is the author's evaluation, not a measurable property of the work.",
      [E["tiepolo"],C["kaisersaal_cycle"]],layer="authorial interpretation")
add_s("st-chp10-p296-apollo-ceiling-scene",322,322,C["apollo_ceiling"],C["apollo_figure"],
      "tiepolo_painted_apollo_leading_frederick_barbarossas_bride_beatrice_of_burgundy_to_the_emperor",
      "On the ceiling he painted Apollo", "to the awaiting Emperor",
      "Haskell describes the Kaisersaal ceiling as showing Apollo conducting Frederick Barbarossa's bride Beatrice of Burgundy to the awaiting Emperor.",
      "This records Haskell's description of the scene; the named participants are represented figures, and no independent iconographic source is consulted.",
      [E["tiepolo"],C["kaisersaal"],C["apollo_ceiling"],C["apollo_figure"],C["frederick_barbarossa"],C["beatrice_burgundy"]],relation=True)
add_s("st-chp10-p296-apollo-scheme-rezzonico-adaptation",322,322,C["apollo_ceiling"],E["rezzonico_family"],
      "tiepolo_later_adapted_the_apollo_ceiling_scheme_with_modifications_for_the_rezzonico_family_in_venice",
      "which he later adapted", "in Venice.",
      "Haskell says Tiepolo later adapted this scheme, with suitable modifications, for the Rezzonico family in Venice.",
      "The passage does not name the later painting; the related Rezzonico marriage fresco candidate cand-4105 remains a cross-chapter comparison rather than an asserted exact identity.",
      [E["tiepolo"],C["apollo_ceiling"],E["rezzonico_family"],E["venice"]],relation=True)
add_s("st-chp10-p296-marriage-wall-scene",322,323,C["kaisersaal_cycle"],C["marriage_scene"],
      "a_kaisersaal_wall_painting_depicted_a_marriage_blessed_by_the_bishop_of_wurzburg_in_1156",
      "On the walls he was required to paint the Marriage", "in 1156",
      "Tiepolo was required to paint a Kaisersaal wall scene of a marriage blessed by the Bishop of Würzburg in 1156.",
      "The couple is not named in this clause, and the candidate does not assume their identity from the preceding ceiling scene.",
      [E["tiepolo"],C["kaisersaal_cycle"],C["marriage_scene"],C["unnamed_bishop_1156"],C["wurzburg_city"]],relation=True)
add_s("st-chp10-p296-harold-investiture-wall-scene",322,324,C["kaisersaal_cycle"],C["investiture_scene"],
      "a_kaisersaal_wall_painting_depicted_bishop_harold_von_hocheim_invested_with_the_princedom_by_the_emperor_in_1163",
      "and Bishop Harold von Hocheim", "Emperor in 1163.",
      "A separate Kaisersaal wall scene showed Bishop Harold von Hocheim being invested with the princedom by the Emperor in 1163.",
      "The source does not identify the Emperor in this clause by name; its relation to Frederick Barbarossa remains an S3 identity check.",
      [E["tiepolo"],C["kaisersaal_cycle"],C["investiture_scene"],C["harold_hocheim"],C["frederick_barbarossa"]],relation=True)
add_s("st-chp10-p296-german-clergy-historical-context",324,325,C["german_princely_clergy"],C["kaisersaal_cycle"],
      "haskell_contrasts_german_princely_clergy_without_roman_ancestry_with_medieval_precedents_for_feudal_life",
      "The German princely clergy", "Age of Enlightenment.",
      "Haskell says the German princely clergy could not boast the Roman ancestry of Tiepolo's Venetian clients and that medieval life was the only suitable precedent for their feudal existence in the Age of Enlightenment.",
      "This is the author's historical interpretation; it does not identify a specific lineage or political doctrine.",
      [C["german_princely_clergy"],E["tiepolo"],E["venice"],C["kaisersaal_cycle"]],layer="authorial interpretation")
add_s("st-chp10-p296-tiepolo-scene-venice-quote",325,325,E["tiepolo"],C["kaisersaal_cycle"],
      "tiepolo_placed_the_scene_firmly_in_sixteenth_century_venice_where_he_said_all_history_took_place",
      "None of this worried-Tiepolo", "all history took place",
      "Haskell reports Tiepolo as saying that he placed the scene firmly in sixteenth-century Venice, where for him all history took place.",
      "The wording is an embedded quotation cited in footnote 2; the cited source has not yet been independently read.",
      [E["tiepolo"],C["kaisersaal_cycle"],E["venice"]],speaker="Tiepolo as quoted by Haskell",
      layer="embedded quotation",footnote=2)
add_s("st-chp10-p296-staircase-ceiling-commission",326,326,E["tiepolo"],E["staircase_fresco"],
      "after_completing_the_kaisersaal_tiepolo_agreed_to_paint_the_residenz_great_staircase_ceiling",
      "As soon as the decoration of the Kaisersaal had been completed", "ever undertaken—",
      "After the Kaisersaal decoration was completed, Tiepolo agreed to paint the ceiling of the Residenz's great staircase, the largest expanse he had undertaken.",
      "The work candidate is reused from the Plate 50 whole-fresco record; 'largest' is Haskell's comparison.",
      [E["tiepolo"],C["kaisersaal"],E["residenz"],E["staircase_fresco"]],relation=True)
add_s("st-chp10-p296-four-continents-fresco",326,327,E["tiepolo"],E["staircase_fresco"],
      "tiepolo_painted_the_four_continents_paying_homage_to_karl_philip_von_greiffenklau",
      "with a fresco depicting The Four Continents", "(Plate 50).",
      "The staircase fresco depicted The Four Continents paying homage to Karl Philip von Greiffenklau.",
      "The Plate 50 parent work is reused; it is distinct from Carriera's Four Continents allegories on p.295.",
      [E["tiepolo"],E["staircase_fresco"],E["karl_philip"]],relation=True)
add_s("st-chp10-p296-absolutism-theme",327,327,E["tiepolo"],E["absolutism"],
      "haskell_calls_the_theme_anachronistic_in_1752_and_says_tiepolo_delighted_in_dreams_of_absolutism",
      "It would be charitable to describe this theme", "dreams of absolutism.",
      "Haskell says it would be charitable to call the theme anachronistic in 1752 and characterizes Tiepolo as delighting in dreams of absolutism.",
      "Both the anachronism and the political characterization are Haskell's interpretation.",
      [E["tiepolo"],E["staircase_fresco"],E["absolutism"]],layer="authorial interpretation")
add_s("st-chp10-p296-tiepolo-generational-comparison",327,328,E["tiepolo"],E["pellegrini"],
      "haskell_contrasts_tiepolo_with_pellegrini_and_the_riccis_in_a_more_autocratic_backward_looking_society",
      "Unlike\nPellegrini and the Riccis", "backward looking society.",
      "Haskell contrasts Pellegrini and the Riccis, who had worked two generations earlier amid change and relatively free enquiry, with Tiepolo as most at home in the last bastions of an autocratic and backward-looking society.",
      "The contrast is Haskell's generational and political interpretation; the plural Riccis is retained as the source's collective wording.",
      [E["tiepolo"],E["pellegrini"],E["marco_ricci"],E["sebastiano_ricci"]],layer="authorial interpretation")
add_s("st-chp10-p296-ancien-regime-vision",328,328,E["tiepolo"],C["ancien_regime"],
      "haskell_describes_the_staircase_fresco_as_tiepolos_supreme_imaginative_vision_of_the_ancien_regime",
      "In this fresco", "ancien régime.",
      "Haskell calls the staircase fresco Tiepolo's supreme and most imaginative vision of the ancien régime.",
      "This is an explicit authorial evaluation, not an independently measured ranking.",
      [E["tiepolo"],E["staircase_fresco"],C["ancien_regime"]],layer="authorial interpretation")
add_s("st-chp10-p296-turin-rise",329,330,E["german_patronage"],E["turin"],
      "other_courts_looked_to_venice_for_talent_and_turin_had_become_a_powerful_attractor_by_the_second_decade",
      "Other courts besides those of Germany", "from all over the peninsula.",
      "Haskell says other courts besides Germany looked to Venice for talent and that Turin had become powerful enough by the second decade of the century to attract artists from across the peninsula.",
      "The source gives a relative period and an authorial account of Turin's attraction; no exact year range is added.",
      [E["turin"],E["venice"],E["germany"]],layer="authorial narrative",footnote=3)
add_s("st-chp10-p296-juvarra-artistic-director-and-commissions-open",330,330,E["juvarra"],E["sebastiano_ricci"],
      "juvarra_was_artistic_director_of_turin_and_his_authority_led_to_many_commissions_for_sebastiano_ricci",
      "During most of the 1720s and early 1730s", "Sebastiano",
      "Haskell says Filippo Juvarra was Turin's artistic director during most of the 1720s and early 1730s and begins to attribute many commissions to his authority, naming Sebastiano Ricci.",
      "The sentence is cut off at p.296 L330 and continues at p.297; do not infer the commission subject or complete the wording until the next segment.",
      [E["juvarra"],E["turin"],E["sebastiano_ricci"]],layer="authorial narrative",relation=True,cross=[NEXT])

new_ids = {row["candidate_id"] for row in newc}
all_ids = cids | new_ids
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < 319 or q["source_line_end"] > 330:
        raise SystemExit(f"statement range outside p.296: {row['statement_id']}")
    if row["subject_candidate_id"] not in all_ids or row["object_candidate_id"] not in all_ids:
        raise SystemExit(f"statement foreign key missing: {row['statement_id']}")
    if not all(cid in all_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"mentioned candidate missing: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping new mentions: {left[2]} / {right[2]}")

cov[PREV].update({"migration_status":"complete", "source_line_ranges":"L305-316",
                  "note":"Printed p.295 body is complete after p.296 closes the final 'He too was naturally an admirer...' sentence. OCR footnote after Venice reads 6, but scan confirms note 5; p.295 notes 1-5 remain pending in the consolidated notes segment."})
cov[SEG].update({"disposition":"reviewed", "migration_status":"partial", "source_line_ranges":"L319-330",
                 "note":"Printed p.296 checked against CHP-10.pdf physical page 25. Closed p.295's Clemens August sentence: he admired Rosalba Carriera and owned pastels by her. Recorded his post-1730 altar-painting commissions; Piazzetta's 1735 Assumption; German patronage and the Würzburg Residenz/Kaisersaal; the Schönborn bishopric succession and Karl Philip's patronage; Neumann's palace; the Kaisersaal scenes of Apollo/Beatrice, the marriage and Harold von Hocheim's investiture; Tiepolo's staircase fresco and its Four Continents subject; and Turin/Juvarra context. Distinguished Würzburg city, Residenz, Kaisersaal and artworks; retained the unnamed successor and 1156 bishop, and did not identify the wall-scene couple from the ceiling scene. The Juvarra sentence ends at 'Sebastiano' and continues p.297. Footnotes 1-3 link to the consolidated notes segment. S2 scan corrections: OCR 'Schonborn' reads 'Schönborn'; 'Wurzburg' reads 'Würzburg'."})
cov[NEXT]["note"] = "Next source-order segment is p.297 at L332-343; it continues the p.296 sentence that Juvarra's authority led to commissions for Sebastiano Ricci."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"segment_sha256":SEG_SHA,"new_candidates":len(newc),
                  "candidate_ids":[row["candidate_id"] for row in newc],"new_mentions":len(newm),
                  "new_statements":len(new_s),"coverage":{"p295":cov[PREV]["migration_status"],
                  "p296":cov[SEG]["migration_status"],"p297":cov[NEXT]["migration_status"]}},
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
    print("Applied p.296 S2 migration; p.296 remains partial pending p.297 and consolidated notes.")
