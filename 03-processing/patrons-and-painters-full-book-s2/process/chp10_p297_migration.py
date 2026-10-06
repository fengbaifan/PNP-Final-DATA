"""Controlled S2 migration for printed p.297; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l318-330"
SEG = "chp-10:10_CHP-10_intro:l332-343"
NEXT = "chp-10:10_CHP-10_intro:l345-352"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEG_SHA = "81af3bc3b79a7865e6b8e62785315511c00a9e128d9d8982e28cf3afc3b739ac"
BACKUP = ".bak-s2-chp10-p297-20261002"


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
body = "\n".join(src[331:343])
SEG_SHA = hashlib.sha256(body.encode("utf-8")).hexdigest()
if SEG_SHA != EXPECTED_SEG_SHA or src[331].strip() != "[Page 297]" or "Sebastiano Ricci" not in body or "Winter Palace" not in body:
    raise SystemExit("p.297 source segment/page mismatch")

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
if maximum != 9136:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")),
                      (NEXT, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "turin": "cand-2662", "venice": "cand-2719", "sebstiano_ricci": "cand-2154", "juvarra": "cand-1339",
    "veronese": "cand-2755", "amigoni": "cand-0094", "tiepolo": "cand-2569",
    "venetian_school": "cand-8094", "venetian_government": "cand-8105", "spain_place": "cand-5120",
    "madrid": "cand-1481", "pietro_rotari": "cand-2288", "st_petersburg": "cand-2343",
    "verona": "cand-8681", "fontebasso": "cand-1047", "mengs": "cand-1652",
    "guarana": "cand-1237", "moscow": "cand-1710", "pittoni": "cand-1950",
    "grand_manner": "cand-4489",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
for key, cid, page, sub in (
    ("sebstiano_ricci", E["sebstiano_ricci"], "9n, 165, 199, 214, 226, 228, 251, 269n, 270, 271, 273, 276n, 279, 284, 286, 293, 295, 296, 297, 304, 311, 313, 315, 337, 341, 342, 374, 376, 377, 394, 405, 407", ""),
    ("juvarra", E["juvarra"], "164, 165, 202, 296, 297", ""),
    ("pietro_rotari", E["pietro_rotari"], "295n, 297", ""),
    ("st_petersburg", E["st_petersburg"], "297, 298", ""),
    ("madrid", E["madrid"], "", ""),
):
    row = next(row for row in candidates if row["candidate_id"] == cid)
    if row["index_page_range"] != page or row["sub_entry"] != sub:
        raise SystemExit(f"unexpected candidate {key}={cid}: {row}")

open_statement = next((row for row in statements if row["statement_id"] == "st-chp10-p296-juvarra-artistic-director-and-commissions-open"), None)
if not open_statement or open_statement["segment_id"] != PREV or open_statement["qualifiers"]["source_line_end"] != 330:
    raise SystemExit("p.296 open Juvarra statement changed")

NEW_SPECS = [
    ("turin_royal_palace", "Unidentified Royal Palace associated with Sebastiano Ricci's Turin commissions", "place",
     "The Royal Palace named in the continuation of the Turin commission sentence; the source does not supply a formal palace name, so identity remains open.", 333),
    ("turin_ricci_paintings", "Unidentified Sebastiano Ricci paintings for the Royal Palace and churches in Turin", "work",
     "A group of paintings associated with Juvarra's commissions to Ricci for a Royal Palace and various churches; titles and exact locations are not supplied.", 333),
    ("madrid_royal_palace", "Royal Palace in Madrid named in Juvarra's proposed decoration scheme", "place",
     "The palace Juvarra devised a scheme to decorate in 1735; the passage gives no formal building title.", 334),
    ("unnamed_king_spain_1735", "Unnamed King of Spain who asked Juvarra to commission paintings from Italian schools", "person",
     "The King is identified only by office and country in the 1735 commission account; no personal identity is inferred.", 335),
    ("madrid_school_commissions", "Unidentified paintings proposed for the Royal Palace in Madrid from Italian schools", "work",
     "The proposed group includes one Venetian, four Roman and one each from Genoese, Neapolitan and Bolognese artists; no titles are named in the passage.", 335),
    ("roman_painters_group", "Roman painters included in Juvarra's Madrid commission list", "term",
     "A group of four Roman painters or works in the list; the passage does not name them here.", 336),
    ("genoese_artist_group", "Unnamed Genoese artist represented in Juvarra's Madrid commission list", "term",
     "One work by a Genoese is listed; the artist is not named in the body passage.", 336),
    ("neapolitan_artist_group", "Unnamed Neapolitan artist represented in Juvarra's Madrid commission list", "term",
     "One work by a Neapolitan is listed; the artist is not named in the body passage.", 336),
    ("bolognese_artist_group", "Unnamed Bolognese artist represented in Juvarra's Madrid commission list", "term",
     "One work by a Bolognese is listed; the artist is not named in the body passage.", 336),
    ("tiepolo_sons", "Unnamed sons of Giambattista Tiepolo who assisted on his final Madrid mission", "term",
     "A plural group whom Haskell says helped Tiepolo on his last mission; no names or number are supplied here.", 339),
    ("spanish_monarchy", "Spanish monarchy described by Haskell as formerly powerful and declining", "institution",
     "The monarchy Tiepolo's Madrid mission is said to glorify; Haskell characterizes it as formerly powerful but declining.", 339),
    ("aranjuez", "Aranjuez as the location of Tiepolo's royal-chapel altarpieces", "place",
     "The place named for the royal chapel receiving Tiepolo's late altarpieces; distinguish it from the chapel building.", 339),
    ("aranjuez_royal_chapel", "Royal chapel at Aranjuez for which Tiepolo painted altarpieces", "place",
     "The chapel identified as the destination of Tiepolo's religious altarpiece series; the source gives no formal dedication here.", 339),
    ("tiepolo_aranjuez_altarpieces", "Tiepolo's religious altarpieces for the royal chapel at Aranjuez", "work",
     "A series described as Tiepolo's most personal and deeply felt religious painting; the individual altarpiece titles are not given.", 339),
    ("mengs_aranjuez_replacements", "Unidentified works by Anton Rafael Mengs that replaced Tiepolo's Aranjuez altarpieces", "work",
     "The source says these works replaced Tiepolo's removed altarpieces; it does not name their subjects or number.", 339),
    ("rotari_pictures", "Unidentified pictures by Pietro Rotari in St Petersburg", "work",
     "Several hundred pictures of varied kinds, including portraits and mythologies, attributed to Rotari in Haskell's account; individual titles are not supplied.", 340),
    ("st_petersburg_winter_palace", "Winter Palace in St Petersburg decorated by Francesco Fontebasso", "place",
     "The Winter Palace mentioned in connection with Fontebasso; keep distinct from Prince Eugene's Winter Palace in Vienna.", 341),
    ("guarana_iphigenia", "Sacrifice of Iphigenia painted by Giacomo Guarana for Moscow in 1762", "work",
     "A work named by subject, artist and destination; the passage supplies no further title, date beyond the year, or location within Moscow.", 342),
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
for line in range(332, 344):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p297-{local}"
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
    ("ricci-palace",333,"Ricci",E["sebstiano_ricci"],"Continuation of the p.296 given name 'Sebastiano'; this mention closes the reference."),
    ("royal-palace-turin",333,"the Royal Palace",C["turin_royal_palace"],"Palace in the Turin commission context; exact building identity is unresolved."),
    ("ricci-judgement",333,"Ricci",E["sebstiano_ricci"],"Subject of Haskell's comment on the effect of patronage.",1),
    ("turin-misconduct",333,"Turin",E["turin"],"Destination Ricci was prevented from visiting."),
    ("veronese-style",333,"Veronese",E["veronese"],"Named as a stylistic comparison for Ricci's Turin scenes."),
    ("turin-city",333,"the city",E["turin"],"Corefers to Turin."),
    ("ricci-scenes",333,"the grandiose scenes",C["turin_ricci_paintings"],"Unidentified works Ricci sent to Turin."),
    ("juvarra-painting",334,"Juvarra",E["juvarra"],"Named as the architect proposing the Madrid decoration scheme."),
    ("venetian-painting",334,"Venetian painting",E["venetian_school"],"Artistic field toward which Juvarra showed qualified attachment."),
    ("royal-palace-madrid",334,"Royal\nPalace in Madrid",C["madrid_royal_palace"],"Building name crosses the OCR line boundary."),
    ("king-spain",335,"King of Spain",C["unnamed_king_spain_1735"],"Unnamed ruler; no personal identity inferred."),
    ("school-commission",335,"commission pictures from all the different schools in Italy",C["madrid_school_commissions"],"Proposed group of works for different Italian schools."),
    ("venetian-work",335,"one work by a Venetian",E["venetian_school"],"One work in the Madrid list; Pittoni is named on the next OCR line."),
    ("pittoni",336,"Pittoni",E["pittoni"],"Named Venetian artist in the list."),
    ("roman-four",336,"four Romans",C["roman_painters_group"],"Four Roman artists or works in the list; individual names are not given here."),
    ("genoese-one",336,"a Genoese",C["genoese_artist_group"],"One unnamed Genoese artist/work in the list."),
    ("neapolitan-one",336,"a Neapolitan",C["neapolitan_artist_group"],"One unnamed Neapolitan artist/work in the list."),
    ("bolognese-one",336,"a Bolognese",C["bolognese_artist_group"],"One unnamed Bolognese artist/work in the list."),
    ("roman-painters",337,"Roman painters",C["roman_painters_group"],"Collective group in Haskell's account of artistic prestige."),
    ("grand-manner",338,"Grand Manner",E["grand_manner"],"Stylistic category in the author's characterization."),
    ("venice-hostility",338,"Venice",E["venice"],"Place at the target of Haskell's conditional account of Spanish hostility."),
    ("amigoni",339,"Amigoni",E["amigoni"],"Artist who went to Madrid in 1739."),
    ("madrid-amigoni",339,"Madrid",E["madrid"],"Destination of Amigoni's 1739 move."),
    ("tiepolo-followed",339,"Tiepolo",E["tiepolo"],"Artist who followed Amigoni to Madrid."),
    ("venetian-style",339,"Venetian",E["venetian_school"],"Haskell's characterization of Tiepolo's artistic identity."),
    ("madrid-tiepolo",339,"Madrid",E["madrid"],"Destination of Tiepolo's 1762 mission.",1),
    ("venetian-government",339,"Venetian government",E["venetian_government"],"Political institution described as making a diplomatic move."),
    ("great-artist",339,"the great artist",E["tiepolo"],"Corefers to Tiepolo in Haskell's statement about the nobility's possible preference."),
    ("tiepolo-final-mission",339,"Tiepolo",E["tiepolo"],"Artist on his final mission to Spain.",1),
    ("tiepolo-sons",339,"his sons",C["tiepolo_sons"],"Unnamed group said to help Tiepolo on his final mission."),
    ("monarchy",339,"monarchy",C["spanish_monarchy"],"The political institution the mission was said to glorify."),
    ("spain-fervour",339,"Spain",E["spain_place"],"Country invoked in Haskell's qualified explanation of the painting's religious character."),
    ("altarpieces",339,"series of altarpieces",C["tiepolo_aranjuez_altarpieces"],"Unidentified religious works for the royal chapel."),
    ("royal-chapel",339,"royal chapel",C["aranjuez_royal_chapel"],"Building named as the altarpiece destination."),
    ("aranjuez",339,"Aranjuez",C["aranjuez"],"Place associated with the chapel."),
    ("mengs-works",339,"works",C["mengs_aranjuez_replacements"],"Works that replaced Tiepolo's removed altarpieces."),
    ("mengs",339,"Anton Rafael Mengs",E["mengs"],"Artist named as the maker of the replacement works."),
    ("tiepolo-died",340,"Tiepolo",E["tiepolo"],"Artist whose death is dated to 1770."),
    ("spain-active",340,"Spain",E["spain_place"],"Place where Tiepolo remained active."),
    ("rotari",340,"Pietro Rotari",E["pietro_rotari"],"Named painter who travelled to St Petersburg."),
    ("st-petersburg",340,"St Petersburg",E["st_petersburg"],"Destination of Rotari's move."),
    ("verona",340,"Verona",E["verona"],"Rotari's native place in the narrative."),
    ("rotari-pictures",340,"several hundred pictures",C["rotari_pictures"],"Unidentified group of Rotari's paintings."),
    ("fontebasso",340,"Francesco Fontebasso",E["fontebasso"],"Named painter who followed Rotari in 1762."),
    ("ricci-tutor",341,"Sebastiano Ricci",E["sebstiano_ricci"],"Artist identified as Fontebasso's teacher."),
    ("winter-palace",341,"the Winter Palace",C["st_petersburg_winter_palace"],"Palace in St Petersburg, not the Winter Palace in Vienna."),
    ("giacomo",341,"Giacomo",E["guarana"],"Given name at the end of the OCR line; surname follows on the next line."),
    ("guarana",342,"Guaraña",E["guarana"],"S0 spelling checked against the scan; printed surname is Guarana."),
    ("ricci-guarana",342,"Ricci",E["sebstiano_ricci"],"Named as one of Guarana's teachers."),
    ("tiepolo-guarana",342,"Tiepolo",E["tiepolo"],"Named as one of Guarana's teachers."),
    ("iphigenia",342,"Sacrifice of Iphigenia",C["guarana_iphigenia"],"Work title as reported in the source."),
    ("moscow",342,"Moscow",E["moscow"],"Destination named for Guarana's painting."),
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
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 297,
                  "pdf_physical_page": 26, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        qualifiers["cross_reference_printed_pages"] = [296 if PREV in cross else 298]
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


open_statement["qualifiers"]["claim"] = "During most of the 1720s and early 1730s Juvarra was Turin's artistic director; by his authority a vast number of commissions for Sebastiano Ricci were given for paintings in the Royal Palace and various churches."
open_statement["qualifiers"]["qualification"] = "The sentence opened on p.296 and closes at p.297 L333. The Royal Palace is not formally identified. Footnote 1's supporting discussion is pending in the consolidated note segment; its OCR excerpt at L343 is not migrated twice."
open_statement["qualifiers"]["mentioned_candidate_ids"] = [E["juvarra"],E["turin"],E["sebstiano_ricci"],C["turin_royal_palace"],C["turin_ricci_paintings"]]
open_statement["qualifiers"]["relation_candidate"] = True
open_statement["qualifiers"]["footnote_marker"] = 1
open_statement["qualifiers"]["footnote_text_pending"] = True
open_statement["qualifiers"]["cross_reference_segments"] = [SEG,NOTES]
open_statement["qualifiers"]["cross_reference_printed_pages"] = [297]

add_s("st-chp10-p297-ricci-turin-quality",333,333,E["sebstiano_ricci"],C["turin_ricci_paintings"],
      "haskell_says_turin_patronage_no_longer_stimulated_ricci_and_his_scenes_seemed_hardened_and_academic",
      "But the effects of this patronage", "betrays a lack of inspiration.",
      "Haskell says the Turin patronage no longer stimulated Ricci as his earlier travels had; he reports that a youthful misdemeanour prevented Ricci from visiting Turin and judges the grandiose Veronese-style scenes he sent there as hardened and academic, betraying a lack of inspiration.",
      "The prohibition and stylistic judgement are Haskell's report and interpretation; the youthful misdemeanour is not specified.",
      [E["sebstiano_ricci"],C["turin_ricci_paintings"],E["turin"],E["veronese"]],layer="authorial interpretation")
add_s("st-chp10-p297-juvarra-qualified-venetian-attachment",334,334,E["juvarra"],E["venetian_school"],
      "haskell_describes_juvarras_attachment_to_venetian_painting_as_qualified",
      "Moreover, Juvarra himself showed", "Venetian painting.",
      "Haskell describes Juvarra's attachment to Venetian painting as only very qualified.",
      "This is an authorial characterization, not a direct statement by Juvarra.",
      [E["juvarra"],E["venetian_school"]],layer="authorial interpretation")
add_s("st-chp10-p297-madrid-decoration-plan",334,335,E["juvarra"],C["madrid_school_commissions"],
      "toward_the_end_of_1735_juvarra_devised_a_royal_palace_madrid_decoration_scheme_and_the_king_asked_him_to_commission_works_from_italian_schools",
      "When, towards the end of 1735", "different schools in Italy.2",
      "Toward the end of 1735 Juvarra devised a scheme to decorate the Royal Palace in Madrid; the King of Spain asked him to commission paintings from the different schools in Italy.",
      "The source does not name the King or identify the proposed individual works; footnote 2 remains pending.",
      [E["juvarra"],C["madrid_royal_palace"],E["madrid"],C["unnamed_king_spain_1735"],C["madrid_school_commissions"]],
      relation=True,footnote=2)
add_s("st-chp10-p297-madrid-school-allocation",335,336,C["madrid_school_commissions"],C["venetian_school"] if "venetian_school" in C else E["venetian_school"],
      "juvarras_list_had_one_venetian_four_romans_and_one_each_genoese_neapolitan_and_bolognese",
      "The fist he drew up included", "a Bolognese.",
      "The list had one work by a Venetian—Pittoni—compared with four Romans and one each by a Genoese, Neapolitan and Bolognese.",
      "The source OCR reads 'fist'; the scan reads 'list'. The passage names only Pittoni among the artists in this comparison; footnote 2 is pending.",
      [C["madrid_school_commissions"],E["pittoni"],E["venetian_school"],C["roman_painters_group"],C["genoese_artist_group"],C["neapolitan_artist_group"],C["bolognese_artist_group"]],
      footnote=2)
add_s("st-chp10-p297-roman-seriousness",336,338,E["grand_manner"],C["roman_painters_group"],
      "in_some_circles_roman_painters_were_regarded_as_the_most_serious_grand_manner_artists",
      "The proportion is extraordinary", "Grand Manner;",
      "Haskell says that in some circles Roman painters were still regarded as the most 'serious' artists working in the Grand Manner.",
      "The phrase 'in some circles' limits the claim; 'serious' is Haskell's reported characterization.",
      [C["roman_painters_group"],E["grand_manner"]],layer="authorial interpretation")
add_s("st-chp10-p297-spanish-hostility-hypothesis",337,338,E["spain_place"],E["turin"],
      "haskell_says_old_spanish_hostility_to_venice_may_have_influenced_juvarras_school_choice",
      "though it is also possible", "determining the choice.",
      "Haskell says it is possible that old Spanish hostility toward Venice played some part in determining Juvarra's selection.",
      "Both 'possible' and 'some part' preserve the author's uncertainty and limited causal claim.",
      [E["spain_place"],E["venetian_school"],C["madrid_school_commissions"]],layer="authorial interpretation")
add_s("st-chp10-p297-amigoni-madrid",339,339,E["amigoni"],E["madrid"],
      "amigoni_went_to_madrid_in_1739_as_court_painter",
      "1739 when Amigoni went to Madrid", "as court painter.3",
      "Amigoni went to Madrid in 1739 as a court painter.",
      "Footnote 3 remains pending in the consolidated notes segment.",
      [E["amigoni"],E["madrid"]],relation=True,footnote=3)
add_s("st-chp10-p297-tiepolo-spain-mission",339,339,E["tiepolo"],E["venetian_government"],
      "tiepolo_was_sent_to_madrid_in_1762_after_pressure_as_part_of_a_venetian_government_diplomatic_move",
      "There he was followed", "by the Venetian government.4",
      "Tiepolo followed Amigoni to Madrid and was sent there in 1762 after ruthless pressure, as part of what Haskell calls an astute diplomatic move by the Venetian government.",
      "The quoted pressure phrase 'da chi puo comandare' is preserved as reported; its agent is not identified. Footnote 4 remains pending.",
      [E["amigoni"],E["tiepolo"],E["madrid"],E["venetian_school"],E["venetian_government"]],
      layer="authorial interpretation",relation=True,footnote=4)
add_s("st-chp10-p297-nobility-political-cunning",339,339,E["tiepolo"],C["spanish_monarchy"],
      "haskell_says_the_nobility_might_want_tiepolo_to_immortalise_them_but_a_tradition_of_political_cunning_prevailed",
      "However much the nobility might still want", "political cunning prevailed.",
      "Haskell says the nobility might still have wanted Tiepolo to immortalise them at the height of his powers, but that an older tradition of political cunning prevailed.",
      "'Might' is retained; the passage does not identify particular nobles or specify the political decision.",
      [E["tiepolo"],C["spanish_monarchy"]],layer="authorial interpretation")
add_s("st-chp10-p297-tiepolo-last-mission",339,339,E["tiepolo"],C["spanish_monarchy"],
      "tiepolo_with_help_from_his_sons_used_his_resources_to_glorify_a_formerly_powerful_but_declining_monarchy",
      "On this his last mission", "now declining, monarchy.",
      "On his last mission Tiepolo, helped by his sons, used his resources to glorify a monarchy Haskell calls formerly powerful but then declining.",
      "The sons are unnamed; the monarchy is identified from the Madrid/Spain context without assigning a dynasty.",
      [E["tiepolo"],C["tiepolo_sons"],C["spanish_monarchy"]],layer="authorial narrative")
add_s("st-chp10-p297-aranjuez-altarpieces",339,339,E["tiepolo"],C["tiepolo_aranjuez_altarpieces"],
      "near_the_end_of_his_life_tiepolo_produced_a_personal_religious_altarpiece_series_for_the_royal_chapel_at_aranjuez",
      "And then, at the very end", "at Aranjuez.",
      "Near the end of his life, and perhaps inspired by Spain's traditional religious fervour, Tiepolo produced what Haskell calls his most personal and deeply felt religious painting in a series of altarpieces for the royal chapel at Aranjuez.",
      "'Perhaps' remains explicit; no individual altarpiece titles or exact production dates are supplied.",
      [E["tiepolo"],E["spain_place"],C["tiepolo_aranjuez_altarpieces"],C["aranjuez_royal_chapel"],C["aranjuez"]],
      layer="authorial interpretation",relation=True)
add_s("st-chp10-p297-aranjuez-works-replaced",339,339,C["tiepolo_aranjuez_altarpieces"],C["mengs_aranjuez_replacements"],
      "tiepolo_altarpieces_were_removed_and_replaced_with_works_by_anton_rafael_mengs",
      "Soon afterwards they were removed", "Anton Rafael Mengs.",
      "Soon afterward Tiepolo's altarpieces were removed and replaced with works by Anton Rafael Mengs.",
      "The source does not date the removal or specify the number and subjects of Mengs's works.",
      [C["tiepolo_aranjuez_altarpieces"],C["mengs_aranjuez_replacements"],E["mengs"]],relation=True)
add_s("st-chp10-p297-tiepolo-death-and-spanish-work",340,340,E["tiepolo"],E["spain_place"],
      "tiepolo_died_in_1770_while_venetian_artists_prepared_new_work_in_europes_distant_outposts_and_he_remained_active_in_spain",
      "Tiepolo died in 1770", "most distant outposts of Europe.",
      "Tiepolo died in 1770; while he was still active in Spain, Venetian artists were preparing new work in Europe's distant outposts.",
      "This is Haskell's transition between Tiepolo's Spanish work and other artists' activity; 'conquests' is his metaphor.",
      [E["tiepolo"],E["spain_place"],E["venetian_school"]],layer="authorial narrative")
add_s("st-chp10-p297-rotari-st-petersburg",340,340,E["pietro_rotari"],E["st_petersburg"],
      "rotari_went_from_native_verona_to_st_petersburg_in_1756_and_died_there_six_years_later",
      "Pietro Rotari had gone", "1756,",
      "Pietro Rotari went from his native Verona to St Petersburg as early as 1756 and died there six years later.",
      "The relative death interval is retained; it is not converted to a precise death year in this statement.",
      [E["pietro_rotari"],E["verona"],E["st_petersburg"]],relation=True)
add_s("st-chp10-p297-rotari-pictures",340,340,E["pietro_rotari"],C["rotari_pictures"],
      "rotari_painted_several_hundred_pictures_of_various_kinds_in_st_petersburg",
      "until his death there six years later", "portraits to mythologies.",
      "Until his death in St Petersburg, Rotari painted several hundred pictures of many kinds, ranging from portraits to mythologies.",
      "The count is the source's rounded quantity; no individual pictures are identified.",
      [E["pietro_rotari"],E["st_petersburg"],C["rotari_pictures"]],relation=True)
add_s("st-chp10-p297-fontebasso-winter-palace",340,341,E["fontebasso"],C["st_petersburg_winter_palace"],
      "fontebasso_followed_rotari_to_st_petersburg_in_1762_and_decorated_the_winter_palace",
      "He was followed in 1762", "the Winter Palace,",
      "Francesco Fontebasso followed Rotari in 1762; Haskell says Fontebasso decorated the Winter Palace.",
      "The palace is in the St Petersburg context and is kept distinct from the Winter Palace in Vienna; the sentence continues with Guarana on the same page.",
      [E["fontebasso"],E["pietro_rotari"],E["st_petersburg"],C["st_petersburg_winter_palace"]],relation=True,footnote=5)
add_s("st-chp10-p297-guarana-iphigenia",341,342,E["guarana"],C["guarana_iphigenia"],
      "in_1762_giacomo_guarana_painted_the_sacrifice_of_iphigenia_for_moscow_after_training_with_ricci_and_tiepolo",
      "and in the same year Giacomo", "for Moscow.6",
      "In 1762 Giacomo Guarana, described as a pupil of Ricci and Tiepolo, painted a Sacrifice of Iphigenia for Moscow.",
      "The source OCR gives 'Guaraña'; the scan reads Guarana. Footnote 6 remains pending in the consolidated notes segment.",
      [E["guarana"],E["sebstiano_ricci"],E["tiepolo"],C["guarana_iphigenia"],E["moscow"]],relation=True,footnote=6)

new_ids = {row["candidate_id"] for row in newc}
all_ids = cids | new_ids
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < 333 or q["source_line_end"] > 342:
        raise SystemExit(f"statement range outside p.297 body: {row['statement_id']}")
    if row["subject_candidate_id"] not in all_ids or row["object_candidate_id"] not in all_ids:
        raise SystemExit(f"statement foreign key missing: {row['statement_id']}")
    if not all(cid in all_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"mentioned candidate missing: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping new mentions: {left[2]} / {right[2]}")

cov[PREV].update({"migration_status":"complete", "source_line_ranges":"L319-330",
                  "note":"Printed p.296 body is complete after p.297 L333 closes the Juvarra/Sebastiano Ricci sentence. Footnote 1 on p.297 is linked to the consolidated note segment; its OCR excerpt is deferred there and not duplicated."})
cov[SEG].update({"disposition":"reviewed", "migration_status":"partial", "source_line_ranges":"L333-342",
                 "note":"Printed p.297 body L333-342 checked against CHP-10.pdf physical page 26. Closed p.296's Juvarra/Ricci commission sentence and recorded Ricci's Turin work and Haskell's qualified artistic judgement; Juvarra's 1735 Madrid scheme and school allocations; Haskell's qualified account of Roman prestige and possible Spanish hostility to Venice; Amigoni and Tiepolo in Madrid, the Venetian government's diplomatic move, Tiepolo's final mission and Aranjuez altarpieces; and Rotari, Fontebasso and Guarana in St Petersburg/Moscow. Reused named-person and city candidates; separated Turin and Madrid palaces, the St Petersburg Winter Palace from the Vienna palace, and the Tiepolo/Mengs work groups. S2 scan corrections: OCR 'fist' reads 'list', 'fife' reads 'life', and 'Guaraña' reads 'Guarana'. L343 is an OCR excerpt of p.297 footnote 1, also captured in composite notes L570; it remains pending there to avoid duplicate migration. Footnotes 1-6 await the consolidated note segment."})
cov[NEXT]["note"] = "Next source-order segment is printed p.298 at L345-352; p.297 body is semantically read, with only its duplicated footnote excerpt at L343 pending in the consolidated notes segment."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"segment_sha256":SEG_SHA,"new_candidates":len(newc),
                  "candidate_ids":[row["candidate_id"] for row in newc],"new_mentions":len(newm),
                  "new_statements":len(new_s),"coverage":{"p296":cov[PREV]["migration_status"],
                  "p297":cov[SEG]["migration_status"],"p298":cov[NEXT]["migration_status"]}},
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
    print("Applied p.297 S2 body migration; p.297 remains partial until its note excerpt is processed.")
