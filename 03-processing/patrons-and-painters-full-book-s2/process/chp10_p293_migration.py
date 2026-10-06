"""Controlled S2 migration for printed p.293; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l268-277"
SEG = "chp-10:10_CHP-10_intro:l279-290"
NEXT = "chp-10:10_CHP-10_intro:l292-302"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEG_SHA = "3dda2f13b5729946b282e62bdc0432548571110089883f75eb5704b33c8f0dd0"
BACKUP = ".bak-s2-chp10-p293-20261002"


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
body = "\n".join(src[278:290])
SEG_SHA = hashlib.sha256(body.encode("utf-8")).hexdigest()
if SEG_SHA != EXPECTED_SEG_SHA or src[278].strip() != "[Page 293]" or "Danaë" not in body or "hors de Paris point de salut" not in body:
    raise SystemExit("p.293 source segment/page mismatch")

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
if maximum != 9056:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")),
                      (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "tessin": "cand-2552", "tessin_tiepolo": "cand-2553", "boucher": "cand-0422",
    "tiepolo": "cand-2569", "tiepolo_danae": "cand-2584", "tiepolo_modello": "cand-2599",
    "gai": "cand-1099", "canaletto": "cand-0498", "cimaroli": "cand-0758",
    "richter": "cand-2196", "nazari": "cand-1727", "nogari": "cand-1743",
    "piazzetta": "cand-1901", "ricci": "cand-2154", "carriera": "cand-0581",
    "johann_wilhelm": "cand-1325", "schoenborn_family": "cand-2400",
    "hapsburgs": "cand-8856", "france": "cand-5317", "paris": "cand-4653",
    "venice": "cand-2719", "stockholm": "cand-4790", "london": "cand-1422",
    "germany": "cand-5529", "pellegrini": "cand-1862", "venetian_school": "cand-8094",
    "royal_palace": "cand-9056",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
for key, cid, page, sub in (
    ("boucher", E["boucher"], "293", "and Count Tessin"),
    ("tessin_tiepolo", E["tessin_tiepolo"], "293, 342", "and Tiepolo"),
    ("tiepolo_danae", E["tiepolo_danae"], "293", "Danaë"),
    ("tiepolo_modello", E["tiepolo_modello"], "293", "modello of Beheading of St John the Baptist"),
    ("gai", E["gai"], "293, 341", ""),
    ("johann_wilhelm", E["johann_wilhelm"], "277, 281, 282, 283, 284, 293", ""),
    ("canaletto", E["canaletto"], "226, 228, 262, 265, 270, 288, 289, 293, 314, 315, 319, 322, 330n, 342, 351, 355, 361, 374, 375, 377, 382n, 384, 392, 393, 407", ""),
):
    row = next(row for row in candidates if row["candidate_id"] == cid)
    if row["index_page_range"] != page or row["sub_entry"] != sub:
        raise SystemExit(f"unexpected page-specific index candidate {key}={cid}")

NEW_SPECS = [
    ("surintendant", "Surintendant des Bâtiments Royaux (Tessin's office from 1728)", "term",
     "French royal-buildings office title that Haskell says Tessin assumed in 1728 while in his native country. The passage does not specify the precise administrative jurisdiction; retain the printed title for S3 alignment.", 280),
    ("king_sweden", "King of Sweden served by Tessin in 1728 (identity unspecified in this passage)", "person",
     "Named only by royal title as the recipient of pictures and furniture bought by Tessin during his 1728 honeymoon in Paris; do not infer the monarch's personal identity here.", 280),
    ("french_artists_1728", "French artists Tessin encountered through his 1728 Paris purchases (unnamed group)", "term",
     "Haskell says Tessin's purchases for the King brought him into contact with a number of French artists; no members are named in this clause.", 280),
    ("tessin_collection", "Tessin's collection of contemporary drawings and paintings assembled in Paris (type pending)", "",
     "A collection described as including contemporary drawings and paintings by leading artists, especially Boucher. The current taxonomy has no collection type; retain the object with type unresolved rather than force it into work or institution.", 280),
    ("ambassador_role", "Swedish ambassador to France (office held by Tessin from 1739)", "term",
     "Role Haskell says Tessin assumed in 1739. The passage does not give a formal appointment title or exact tenure dates beyond three years in Paris.", 280),
    ("french_leading_artists", "Leading artists whose contemporary works Tessin collected in Paris (unnamed group)", "term",
     "Collective artists represented in Tessin's drawings and paintings; Boucher is singled out by name. Do not assume this group is identical to the French artists he encountered in 1728.", 280),
    ("boucher_wife", "Unnamed wife of François Boucher (in Haskell's qualified Tessin account)", "person",
     "Mentioned only through the qualified claim that Tessin apparently became her lover. Her name and identity are not supplied in this passage.", 280),
    ("boucher_picture", "Unidentified picture commissioned by Count Tessin from Boucher in 1737", "work",
     "A picture that Haskell says Tessin had commissioned from Boucher in 1737; no title, medium, or present location is given.", 280),
    ("tessin_painter_letter", "Tessin's letter evaluating Venetian painters for the Stockholm palace project (citation pending)", "archive",
     "A letter in which Tessin lists merits and drawbacks of leading artists and judges Tiepolo ideal for his immediate requirements. The passage calls it well known; the full locator is pending footnote review.", 280),
    ("siren_locator", "Siren, pp. 103 ff. (citation locator in p.293 note 1)", "archive",
     "Short reference printed for the Tessin/Tiepolo discussion. Title, edition, and full bibliographic identity are not supplied in this locator; reconcile it with the consolidated note and bibliography.", 290),
    ("swedish_buyers", "Swedes unable to match Tiepolo's prices (unnamed group)", "term",
     "Collective buyers whom Haskell says could not offer the prices Tiepolo commanded; do not collapse this group into the King of Sweden or the court.", 280),
    ("taraval", "Taraval (artist named in Tessin's comparison of Tiepolo; identity pending)", "person",
     "A person named in the quoted comparison 'accommodating like a Taraval'. The passage provides no given name or further identity; resolve in S3.", 280),
    ("french_sculptors", "French sculptors already engaged by the court (unnamed group)", "term",
     "Collective sculptors described in Tessin's quoted letter as having undertaken the most urgent court work; no members are named.", 284),
    ("swedish_court", "Swedish royal court referred to in Tessin's 1737 letter", "institution",
     "The court whose urgent sculptural projects Tessin says were already undertaken by French sculptors. Preserve it separately from the unnamed King of Sweden and individual artists.", 285),
    ("venetian_artists_germany", "Venetian artists finding patrons across Germany (unnamed collective, p.293)", "term",
     "Collective artists in Haskell's statement about continued German patronage amid stronger French competition. Named examples follow in the adjacent paragraph but the group itself is not enumerated.", 288),
    ("dusseldorf", "Düsseldorf (city in the p.293 patronage account)", "place",
     "City whose importance Haskell says declined after the Elector's death in 1716. Preserve the printed spelling; the source OCR reads 'Diisseldorf' in this line.", 290),
    ("berlin", "Berlin (city named as the setting of an opinion about Paris)", "place",
     "Haskell attributes the French phrase 'hors de Paris point de salut' to opinion in Berlin; the speaker is unnamed.", 288),
    ("sweden", "Sweden (Tessin's native country and the Swedish collecting context)", "place",
     "Geographic country identified in context by Tessin's Swedish identity, the King of Sweden, and Stockholm. Keep geographical place distinct from the Swedish crown and court.", 280),
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
for line in range(279, 291):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p293-{local}"
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
    ("native-country",280,"native country",C["sweden"],"Closes the p.292 'in his' phrase; context identifies Tessin as Swedish."),
    ("surintendant",280,"Surintendant des Bâtiments Royaux",C["surintendant"],"French office title as printed."),
    ("tessin-1728",280,"he became",E["tessin"],"Pronoun corefers to Count Tessin."),
    ("honeymoon-paris",280,"Paris",E["paris"],"First Paris mention in this line: Tessin's 1728 honeymoon."),
    ("king-sweden",280,"the King of Sweden",C["king_sweden"],"The ruler is named only by title; identity remains open."),
    ("french-artists-1728",280,"a number of French artists",C["french_artists_1728"],"Unnamed group encountered through the purchase activity."),
    ("ambassador-role",280,"ambassador to France",C["ambassador_role"],"Role from 1739; keep separate from a formal person or institution."),
    ("france-ambassador",280,"France",E["france"],"Destination of the ambassadorship."),
    ("paris-ambassador",280,"Paris",E["paris"],"Second Paris mention: Tessin's three-year stay beginning in 1739." ,1),
    ("paris-collection",280,"a superb collection of contemporary drawings and paintings",C["tessin_collection"],"Collection object retained with unresolved type."),
    ("leading-artists",280,"all the leading artists",C["french_leading_artists"],"Unnamed group of artists represented in the collection."),
    ("boucher",280,"Boucher",E["boucher"],"Mapped to the index entry 'and Count Tessin'."),
    ("boucher-wife",280,"wife’s lover",C["boucher_wife"],"Unnamed person; Haskell qualifies the claim with 'apparently'."),
    ("tessin-apparently",280,"he apparently became",E["tessin"],"Pronoun corefers to Tessin; preserve the qualification."),
    ("boucher-picture",280,"a picture in 1737",C["boucher_picture"],"Unidentified work commissioned before the 1739 Paris collection period."),
    ("tessin-commissioned",280,"he had already commissioned",E["tessin"],"Pronoun corefers to Tessin."),
    ("year-before-venice",280,"The year before this",E["tessin"],"Relative date points to the year before the 1739 ambassadorship; retain the source's relative wording."),
    ("venice",280,"Venice",E["venice"],"Destination for the painter search."),
    ("royal-palace",280,"the Royal Palace in Stockholm",E["royal_palace"],"Building named in the search for a decorator."),
    ("stockholm",280,"Stockholm",E["stockholm"],"City, distinct from its Royal Palace."),
    ("venetian-school",280,"l’école de Venise",E["venetian_school"],"French phrase as printed; OCR errors in the following sentence are recorded in S2."),
    ("there-venice",280,"there",E["venice"],"Corefers to Venice."),
    ("tessin-letter",280,"a well-known letter",C["tessin_painter_letter"],"Letter identity and complete locator remain pending note processing."),
    ("tiepolo-ideal",280,"Tiepolo",E["tessin_tiepolo"],"Mapped to the page-specific 'and Tiepolo' index entry."),
    ("tessin-tiepolo-quote",280,"ses Tableaux",E["tessin_tiepolo"],"French possessive in Tessin's quote; refers to Tiepolo's paintings."),
    ("taraval",280,"un Taraval",C["taraval"],"Artist named only by surname in Tessin's French comparison."),
    ("swedes",280,"the Swedes",C["swedish_buyers"],"Collective buyers; not the King or court."),
    ("stockholm-invitation",280,"invitation to Stockholm",E["stockholm"],"Destination of the unanswered invitation to Tiepolo."),
    ("tessin-taste",281,"Tessin",E["tessin"],"Subject of the contrast introduced by 'But'."),
    ("danae",282,"Danaë",E["tiepolo_danae"],"Mapped to the indexed Tiepolo work sub-entry."),
    ("tiepolo-works",282,"by Tiepolo",E["tessin_tiepolo"],"Artist attribution applies to both preceding works."),
    ("modello-st-john",282,"a modello of the Beheading of St John the Baptist",E["tiepolo_modello"],"Mapped to the indexed modello sub-entry; preserve the source's work wording."),
    ("personal-collection",282,"his personal collection",C["tessin_collection"],"Collection held for Tessin's own taste; type remains unresolved."),
    ("canaletto-views",282,"Canaletto",E["canaletto"],"Named among artists whose views Tessin collected."),
    ("cimaroli",282,"Cimaroli",E["cimaroli"],"Page-specific index candidate."),
    ("richter",282,"Richter",E["richter"],"Page-specific index candidate."),
    ("nazari",282,"Nazari",E["nazari"],"Page-specific index candidate."),
    ("nogari",282,"Nogari",E["nogari"],"Page-specific index candidate."),
    ("piazzetta",282,"Piazzetta",E["piazzetta"],"Page-specific index candidate."),
    ("gai",284,"the sculptor Gai",E["gai"],"Named sculptor in Tessin's letter; note 2 remains pending."),
    ("french-sculptors",284,"plusieurs sculpteurs\nFrançois",C["french_sculptors"],"Unnamed French sculptors in Tessin's quoted letter; the phrase spans a source line break."),
    ("swedish-court",285,"services de la cour",C["swedish_court"],"The court whose urgent projects are described in the letter."),
    ("tessin-friends",285,"Tessin",E["tessin"],"Subject of the Venetian friendships statement."),
    ("venice-friends",285,"Venice",E["venice"],"Place of Tessin's friendships."),
    ("french-collecting",285,"the French",C["french_leading_artists"],"Refers to French art within the collection contrast; group scope is broad."),
    ("berlin",288,"Berlin",C["berlin"],"Setting attributed for the anonymous opinion."),
    ("paris-quote",288,"Paris",E["paris"],"City in the French saying; not a literal location for the unnamed speaker."),
    ("venetian-artists-germany",288,"Venetian artists",C["venetian_artists_germany"],"Unnamed collective receiving German patronage."),
    ("germany",289,"Germany",E["germany"],"Geographic setting of patronage."),
    ("johann-wilhelm",289,"Johann\nWilhelm",E["johann_wilhelm"],"Name spans a source line break; the index identifies the Elector and the passage dates his death to 1716."),
    ("duesseldorf-ocr",290,"Diisseldorf",C["dusseldorf"],"S0 OCR spelling; the scan reads Düsseldorf. Correction is recorded only in S2."),
    ("hapsburgs",290,"the Hapsburgs",E["hapsburgs"],"Collective scope remains unresolved; use the existing p.278 candidate rather than infer a specific ruler."),
    ("schoenborns",290,"Schönborns",E["schoenborn_family"],"Plural family reference, not an individual member."),
    ("pellegrini",290,"Pellegrini",E["pellegrini"],"Named artist in the shifting patronage account."),
    ("ricci",290,"Ricci",E["ricci"],"The p.293 index has a Sebastiano Ricci entry; retain this mapping for later S3 identity review."),
    ("rosalba-camera",290,"Rosalba Camera",E["carriera"],"S0 OCR form; printed scan reads Carriera. Keep source surface and correct only in S2."),
    ("london-progressive",290,"London",E["london"],"One of the cities called progressive in Haskell's comparison."),
    ("paris-progressive",290,"Paris",E["paris"],"City in the progressive-towns comparison."),
    ("duesseldorf-progressive",290,"Düsseldorf",C["dusseldorf"],"Printed form in the progressive-towns comparison."),
    ("siren-note",290,"Siren, pp. 103 ff.",C["siren_locator"],"Footnote 1 locator merged into this OCR line; retain as citation locator, not independent verification."),
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
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 293,
                  "pdf_physical_page": 22, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
    if cross:
        qualifiers["cross_reference_segments"] = cross
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


add_s("st-chp10-p293-tessin-office",280,280,E["tessin"],C["surintendant"],
      "tessin_became_surintendant_des_batiments_royaux_in_1728",
      "and in 1728 he became", "Royaux.",
      "In 1728 Tessin became Surintendant des Bâtiments Royaux in his native country.",
      "The office is preserved in the printed French form; its administrative scope is not expanded beyond this passage.",
      [E["tessin"],C["sweden"],C["surintendant"]],relation=True)
add_s("st-chp10-p293-tessin-honeymoon-purchases",280,280,E["tessin"],C["king_sweden"],
      "during_his_1728_paris_honeymoon_tessin_bought_pictures_and_furniture_for_the_king_of_sweden",
      "During his honeymoon in Paris", "for the King of Sweden",
      "During his honeymoon in Paris in 1728, Tessin bought pictures and furniture for the King of Sweden.",
      "The monarch is not identified by name in this passage.",
      [E["tessin"],E["paris"],C["sweden"],C["king_sweden"]],relation=True)
add_s("st-chp10-p293-tessin-meets-french-artists",280,280,E["tessin"],C["french_artists_1728"],
      "tessins_1728_paris_purchases_brought_him_into_contact_with_french_artists",
      "and this brought him into touch", "French artists.",
      "Haskell says Tessin's 1728 purchases brought him into contact with a number of French artists.",
      "The artists are not named in this clause; do not assume that this group has the same membership as the leading artists he collected from later.",
      [E["tessin"],C["french_artists_1728"],E["paris"]],relation=True)
add_s("st-chp10-p293-tessin-ambassador",280,280,E["tessin"],C["ambassador_role"],
      "in_1739_tessin_became_ambassador_to_france_and_spent_three_years_in_paris",
      "In 1739 he became ambassador", "three years in Paris",
      "In 1739 Tessin became ambassador to France and spent three years in Paris.",
      "The three-year duration is explicit; do not infer exact start or end dates beyond the source.",
      [E["tessin"],C["ambassador_role"],E["france"],E["paris"]],relation=True)
add_s("st-chp10-p293-tessin-collection",280,280,E["tessin"],C["tessin_collection"],
      "tessin_assembled_a_superb_paris_collection_of_contemporary_art_by_leading_artists_especially_boucher",
      "he assembled a superb collection", "especially Boucher,",
      "During his three years in Paris Tessin assembled a collection of contemporary drawings and paintings by leading artists, especially Boucher.",
      "Haskell's praise 'superb' is retained as an authorial evaluation; the collection's type remains unresolved.",
      [E["tessin"],C["tessin_collection"],C["french_leading_artists"],E["boucher"]],relation=True)
add_s("st-chp10-p293-tessin-boucher-wife",280,280,E["tessin"],C["boucher_wife"],
      "haskell_says_tessin_apparently_became_bouchers_wifes_lover",
      "whose wife’s lover", "he apparently became",
      "Haskell says Tessin apparently became the lover of Boucher's wife.",
      "The claim is explicitly qualified as apparent and the woman is unnamed; do not convert it into a certain relationship.",
      [E["tessin"],E["boucher"],C["boucher_wife"]],layer="qualified authorial report",relation=True)
add_s("st-chp10-p293-tessin-boucher-picture",280,280,E["tessin"],C["boucher_picture"],
      "tessin_had_commissioned_a_picture_from_boucher_in_1737",
      "from whom he had already commissioned", "a picture in 1737.",
      "Haskell says Tessin had already commissioned a picture from Boucher in 1737.",
      "The picture is unidentified; preserve the year and do not infer its title or present location.",
      [E["tessin"],E["boucher"],C["boucher_picture"]],relation=True)
add_s("st-chp10-p293-tessin-search-stockholm-decorator",280,280,E["tessin"],E["royal_palace"],
      "a_year_before_1739_tessin_searched_venice_for_a_painter_for_the_stockholm_royal_palace",
      "The year before this he had been to Venice", "in Stockholm.",
      "The year before Tessin's 1739 ambassadorship, he went to Venice in search of a painter to decorate the Royal Palace in Stockholm.",
      "The date is expressed relatively in the source; no painter was selected in this sentence.",
      [E["tessin"],E["venice"],E["royal_palace"],E["stockholm"]],relation=True)
add_s("st-chp10-p293-tessin-venetian-school-assessment",280,280,E["tessin"],E["venetian_school"],
      "tessin_praised_the_venetian_school_but_found_little_for_his_immediate_requirements",
      "He was pleased with what he saw there", "immediate requirements.",
      "Tessin praised the Venetian school as flourishing and distinctive in Italy but found little that met his immediate requirements for the palace project.",
      "The French quotation is reported by Haskell; S0 OCR 'sur turtrès' and 'quelle' were checked against the scan and corrected only in S2 to 'sur un très' and 'qu'elle'.",
      [E["tessin"],E["venice"],E["venetian_school"],E["royal_palace"]],speaker="Tessin quoted by Haskell",layer="reported correspondence")
add_s("st-chp10-p293-tessin-tiepolo-letter-evaluation",280,280,E["tessin"],E["tessin_tiepolo"],
      "in_a_letter_tessin_compared_leading_artists_and_found_only_tiepolo_ideal_for_his_requirements",
      "In a well-known letter", "Tiepolo was ideal.1",
      "Haskell says Tessin enumerated the merits and drawbacks of leading artists in a well-known letter and found only Tiepolo ideal.",
      "This is a reported assessment for Tessin's immediate project, not a general ranking of all artists; note 1 remains linked to the consolidated notes.",
      [E["tessin"],C["tessin_painter_letter"],E["tessin_tiepolo"],E["royal_palace"]],speaker="Haskell reporting Tessin",layer="reported correspondence",footnote=1,relation=True)
add_s("st-chp10-p293-tessin-tiepolo-quoted-praise",280,280,E["tessin"],E["tessin_tiepolo"],
      "tessin_praised_tiepolo_for_spirit_flexible_manner_fire_color_and_speed",
      "‘Tout est dans ses Tableaux", "vitesse surprenante",
      "In the quoted letter, Tessin says Tiepolo's paintings show figures richly dressed even among beggars, then praises his spirit, accommodating manner, fire, brilliant colour, and speed.",
      "The source's question about fashion and all evaluative terms remain within Tessin's reported opinion; do not treat them as independent measurements.",
      [E["tessin"],C["tessin_painter_letter"],E["tessin_tiepolo"]],speaker="Tessin quoted by Haskell",layer="quoted correspondence",footnote=1)
add_s("st-chp10-p293-tiepolo-price-invitation",280,280,E["tessin_tiepolo"],C["swedish_buyers"],
      "tiepolo_prices_exceeded_swedish_offers_and_his_stockholm_invitation_received_no_response",
      "InfortunLtel Ite was also able", "met with no response.",
      "Haskell says Tiepolo commanded prices far beyond what the Swedes could offer and that the invitation to Stockholm received no response.",
      "The scan reads 'Unfortunately he'; the S0 OCR is preserved in original_quote and corrected only in S2. The source does not explain the lack of response.",
      [E["tessin_tiepolo"],C["swedish_buyers"],E["stockholm"]],speaker="Haskell",layer="authorial report",relation=True)
add_s("st-chp10-p293-tessin-personal-collecting",280,282,E["tessin"],C["tessin_collection"],
      "tessin_indulged_his_taste_for_colourful_pretty_works_in_his_personal_collection",
      "But\nTessin was able to indulge", "that attracted him.",
      "Tessin continued to indulge his taste for colourful and pretty works in his personal collection.",
      "This collection is distinct from works he bought for the King; the source does not say every item was acquired in one transaction.",
      [E["tessin"],C["tessin_collection"]],layer="authorial narrative")
add_s("st-chp10-p293-tessin-tiepolo-works",281,282,E["tessin"],E["tessin_tiepolo"],
      "tessin_bought_danae_and_a_modello_of_the_beheading_of_st_john_by_tiepolo_for_his_personal_collection",
      "He bought a\nDanaë", "for his personal collection,",
      "Tessin bought a Danaë and a modello of the Beheading of St John the Baptist by Tiepolo for his personal collection.",
      "The works are kept distinct as indexed; the passage supplies no further dates or locations.",
      [E["tessin"],E["tiepolo_danae"],E["tiepolo_modello"],E["tiepolo"]],relation=True)
add_s("st-chp10-p293-tessin-other-works",282,282,E["tessin"],C["tessin_collection"],
      "tessins_collection_included_views_portraits_fanciful_heads_drawings_and_other_works_by_named_venetian_artists",
      "as well as views by Canaletto", "other works that attracted him.",
      "Haskell lists views by Canaletto, Cimaroli and Richter; portraits and fanciful heads by Nazari and Nogari; drawings by Piazzetta and others; and further works that attracted Tessin.",
      "The source does not identify individual titles for these groups of works.",
      [E["tessin"],C["tessin_collection"],E["canaletto"],E["cimaroli"],E["richter"],E["nazari"],E["nogari"],E["piazzetta"]])
add_s("st-chp10-p293-tessin-gai-letter",283,285,E["tessin"],E["gai"],
      "after_failing_to_secure_royal_patronage_for_tiepolo_tessin_wrote_he_would_support_gai_despite_few_prospects",
      "Having failed to get royal patronage for Tiepolo", "à faire’.2",
      "After failing to obtain royal patronage for Tiepolo, Tessin wrote that he would do his best for the sculptor Gai, whom he particularly admired.",
      "The quotation continues that Tessin feared few prospects because French sculptors at court had undertaken the most urgent work; footnote 2 identifies the letter but remains pending migration.",
      [E["tessin"],E["tiepolo"],E["gai"],C["french_sculptors"],C["swedish_court"]],speaker="Tessin quoted by Haskell",layer="reported correspondence",relation=True,footnote=2)
add_s("st-chp10-p293-tessin-venetian-friends",285,285,E["tessin"],E["venice"],
      "tessin_kept_venetian_friendships_after_his_art_collecting_became_mostly_french",
      "Tessin had made many friends in Venice", "confined to the French.",
      "Haskell says Tessin made many friends in Venice and remained faithful to them long after his art collecting was almost entirely confined to French works.",
      "The unnamed friends and unnamed collection items remain unspecified; this does not imply that all his collecting became French.",
      [E["tessin"],E["venice"],C["tessin_collection"],C["french_leading_artists"]],layer="authorial report")
add_s("st-chp10-p293-berlin-opinion",287,288,C["berlin"],E["paris"],
      "an_unnamed_berlin_opinion_said_there_was_no_salvation_outside_paris_as_french_competition_increased",
      "Although French competition became increasingly serious", "opinion in Berlin3",
      "Haskell says French competition intensified and attributes the phrase 'hors de Paris point de salut' to opinion in Berlin.",
      "The speaker is unnamed and the phrase is a reported opinion, not Haskell's factual conclusion; note 3 remains pending migration.",
      [C["berlin"],E["paris"]],speaker="Opinion reported from Berlin by Haskell",layer="reported opinion",footnote=3)
add_s("st-chp10-p293-venetian-patronage-germany",288,289,C["venetian_artists_germany"],E["germany"],
      "venetian_artists_continued_to_find_enthusiastic_patronage_across_germany",
      "Venetian artists went on", "all over Germany.",
      "Haskell says Venetian artists continued to find enthusiastic patrons throughout Germany despite stronger French competition.",
      "The collective is not enumerated in this sentence; named examples follow in the next account.",
      [C["venetian_artists_germany"],E["germany"]],layer="authorial report",relation=True)
add_s("st-chp10-p293-duesseldorf-after-elector",289,290,E["johann_wilhelm"],C["dusseldorf"],
      "after_johann_wilhelms_death_in_1716_duesseldorf_lost_its_importance",
      "After the death of the Elector Johann", "lost its importance,",
      "Haskell says Düsseldorf lost importance after the Elector Johann Wilhelm died in 1716.",
      "The city's relative importance is Haskell's assessment; the scan corrects the OCR form 'Diisseldorf'.",
      [E["johann_wilhelm"],C["dusseldorf"]],layer="authorial interpretation")
add_s("st-chp10-p293-hapsburg-schoenborn-reception",290,290,E["hapsburgs"],E["pellegrini"],
      "hapsburgs_and_schoenborns_welcomed_pellegrini_ricci_and_carriera_partly_after_their_success_in_progressive_towns",
      "but the Hapsburgs and Schönborns", "London, Paris and Düsseldorf.4",
      "Haskell says the Hapsburgs and Schönborns, formerly attached to traditional late-Baroque artists, were now ready to welcome Pellegrini, Ricci and Rosalba Carriera, partly because of their success in London, Paris and Düsseldorf.",
      "The causal wording is explicitly partial. The scan reads 'Carriera' where S0 OCR has 'Camera'; 'Düsseldorf' is likewise retained as the printed form. Footnote 4 remains pending migration.",
      [E["hapsburgs"],E["schoenborn_family"],E["pellegrini"],E["ricci"],E["carriera"],E["london"],E["paris"],C["dusseldorf"]],layer="authorial interpretation",relation=True,footnote=4)

open_statement = next(row for row in statements if row["statement_id"] == "st-chp10-p292-tessin-political-importance-open")
if open_statement["segment_id"] != PREV or open_statement["qualifiers"]["source_line_end"] != 277:
    raise SystemExit("p.292 open Tessin statement changed")
open_statement["predicate"] = "tessin_later_achieved_great_political_importance_in_his_native_country"
open_statement["qualifiers"]["claim"] = "A few years later Tessin achieved great political importance in his native country, Sweden."
open_statement["qualifiers"]["qualification"] = "The phrase opens on p.292 and closes at p.293 L280; 'native country' refers to Sweden, identified immediately before as Tessin's nationality."
open_statement["qualifiers"]["cross_reference_segments"] = [SEG]
open_statement["qualifiers"]["cross_reference_printed_pages"] = [293]
open_statement["qualifiers"].pop("footnote_marker", None)
open_statement["qualifiers"].pop("footnote_text_pending", None)

cov[PREV].update({"migration_status":"complete", "source_line_ranges":"L268-277",
                  "note":"Printed p.292 body is complete; its final Tessin clause closes at p.293 L280, now linked from the statement. Footnotes 1-6 remain pending in the consolidated notes segment."})
cov[SEG].update({"disposition":"reviewed", "migration_status":"partial", "source_line_ranges":"L280-290",
                 "note":"Printed p.293 was checked against CHP-10.pdf physical page 22. Closed the p.292 Tessin sentence: his political importance was in his native country, Sweden. Recorded his 1728 office and purchases for the Swedish King; 1739 ambassadorship and Paris collection; qualified Boucher-wife claim and 1737 picture; Venice search for a Stockholm Palace decorator, the Tiepolo evaluation letter and attributed praise; price/invitation outcome; his personal acquisitions, Gai correspondence, and Venetian friendships; Haskell's Berlin opinion and German patronage account after Johann Wilhelm's 1716 death. Reused indexed Tiepolo works and artist candidates; preserved unnamed king, court groups, wife, collection type and unresolved names. S2 scan corrections include 'sur turtrès'/'quelle', 'InfortunLtel Ite', 'seared', 'Diisseldorf', and 'Camera'; source remains unchanged. Footnotes 1-4 are linked/pending note-source review; note 1 locator 'Siren, pp.103 ff.' is retained as a citation candidate. The final fragment 'And in-1725' continues on p.294, so this segment remains partial."})
cov[NEXT]["note"] = "Next source-order segment is printed p.294 at L292-302; it completes p.293 L290 'And in 1725' and continues the German patronage discussion. Footnotes 1-4 printed on p.293 remain to be reconciled with the consolidated notes source."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"segment_sha256":SEG_SHA,"new_candidates":len(newc),
                  "candidate_ids":[row["candidate_id"] for row in newc],"new_mentions":len(newm),
                  "new_statements":len(new_s),"coverage":{"p292":cov[PREV]["migration_status"],
                  "p293":cov[SEG]["migration_status"],"p294":cov[NEXT]["migration_status"]}},
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
    print("Applied p.293 S2 migration; p.293 remains partial pending p.294 and consolidated notes.")
