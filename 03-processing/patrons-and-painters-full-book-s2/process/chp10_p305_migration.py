"""Controlled S2 migration for printed p.305; dry-run unless --apply."""
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
P304 = "chp-10:10_CHP-10_intro:l411-421"
P305 = "chp-10:10_CHP-10_intro:l423-433"
P306 = "chp-10:10_CHP-10_intro:l435-443"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = "80631bd09f439079d273b40a48c4078bad34ee98d2db2c0aaf80784fb5df92fb"
BACKUP = ".bak-s2-chp10-p305-20261002"


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
first, last, PAGE, PHYSICAL = 423, 433, 305, 34
body = "\n".join(src[first - 1:last])
digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
if digest != EXPECTED_SEGMENT_SHA or src[422].strip() != "[Page 305]" or "six views of S. Marco" not in body:
    raise SystemExit(f"p.305 source segment mismatch: {digest}")
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
if maximum != 9213:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((P304, ("reviewed", "partial")), (P305, ("queued", "pending")),
                      (P306, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] == P305 for row in mentions) or any(row["segment_id"] == P305 for row in statements):
    raise SystemExit("p.305 already has mention or statement rows")

E = {
    "smith": "cand-2440", "canaletto": "cand-0514", "canaletto_sanmarco": "cand-0521",
    "canaletto_grand_canal": "cand-0517", "canaletto_bedford": "cand-0509",
    "canaletto_carlisle": "cand-0510", "canaletto_hervey": "cand-0511",
    "bedford": "cand-0267", "carlisle": "cand-0559", "hervey": "cand-1297",
    "visentini": "cand-2784", "tessin": "cand-2552", "grand_canal": "cand-8178",
    "venice": "cand-3401", "england": "cand-8983",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("smith_first_sanmarco_views", "Six early Canaletto views of S. Marco and its surroundings for Joseph Smith", "work",
     "Haskell calls these Smith’s first Canalettos; the passage does not resolve whether they are included in the later fourteen-picture series.", 425),
    ("smith_fourteen_picture_series", "Fourteen Canaletto pictures painted for Joseph Smith between 1730 and 1735", "work",
     "A series described as having a documentary purpose; the text identifies twelve small Venetian views and two large regatta exceptions.", 427),
    ("grand_canal_twelve_views", "Twelve small Canaletto views of Venice documenting the Grand Canal", "work",
     "The twelve views form the core of Smith’s fourteen-picture group; individual titles are not enumerated here.", 428),
    ("smith_regatta_pair", "Two large Canaletto regatta pictures in Joseph Smith’s fourteen-picture series", "work",
     "The two pictures are described as exceptions to the twelve small Grand Canal views; their titles and subjects beyond regattas are not given.", 428),
    ("visentini_engraving_series", "Antonio Visentini’s published engravings of Canaletto’s series for Joseph Smith", "work",
     "A published engraved series dated 1735, giving tourists access to Canaletto’s pictures; the publication title and edition details remain for the notes/bibliography.", 428),
    ("bedford_twenty_views", "Twenty Venetian views painted by Canaletto for the Duke of Bedford in the late 1730s", "work",
     "A group of twenty views mentioned by Haskell; individual titles are not supplied in this passage.", 431),
    ("hervey_twenty_views", "Twenty Venetian views painted by Canaletto for Sir Robert Hervey in the late 1730s", "work",
     "A group of twenty views mentioned by Haskell; individual titles are not supplied in this passage.", 432),
    ("carlisle_seventeen_views", "Seventeen Venetian views painted by Canaletto for the Earl of Carlisle in the late 1730s", "work",
     "A group of seventeen views mentioned by Haskell; individual titles are not supplied in this passage.", 432),
    ("san_marco_area", "S. Marco and its immediate surroundings in Venice", "place",
     "Locator for Canaletto’s first six views for Smith; retain the exact scope ‘S. Marco and its immediate surroundings’ pending identity alignment.", 425),
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
                 "candidate_source_ref": f"{P305}#L{line}"})

newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p305-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    line_start = line_offsets[line]
    line_end = line_start + len(src[line - 1])
    positions, at = [], line_start
    while True:
        at = body.find(surface, at)
        if at < 0 or at + len(surface) > line_end:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": P305, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    ("smith-commissioned-for-others", 424, "Smith", E["smith"], "Closes p.304’s sentence about commissions for other customers."),
    ("tessin-observation", 424, "Tessin’s observation", E["tessin"]),
    ("smith-first-canalettos", 425, "Smith’s first", E["smith"]),
    ("canalettos", 425, "Canalettos", E["canaletto_sanmarco"], "Page-index subentry for Canaletto’s S. Marco views."),
    ("six-views", 425, "six views", C["smith_first_sanmarco_views"]),
    ("san-marco", 425, "S. Marco", C["san_marco_area"]),
    ("first-views-impressionistic", 425, "impressionistic", C["smith_first_sanmarco_views"], "Footnote 1 cites Constable 1976; full note remains in the consolidated source."),
    ("first-group-they", 426, "They", C["smith_first_sanmarco_views"], "Corefers to the six views just named."),
    ("canaletto-finest-works", 426, "his finest works", C["smith_first_sanmarco_views"], "Corefers to Canaletto’s first six views."),
    ("consul", 426, "the Consul", E["smith"], "Smith’s role as Consul."),
    ("english-patrons", 426, "English patrons", E["england"], "Collective patron group; individual patrons are not named in this phrase."),
    ("fourteen-pictures", 427, "fourteen pictures", C["smith_fourteen_picture_series"]),
    ("canaletto-painted", 427, "he painted", E["canaletto"], "Canaletto is the artist in the continuing context."),
    ("smith-fourteen", 427, "for him", E["smith"], "Corefers to Joseph Smith."),
    ("smith-series-change", 428, "the series", C["smith_fourteen_picture_series"], "The fourteen-picture Smith series."),
    ("two-large-exceptions", 428, "two large exceptions", C["smith_regatta_pair"]),
    ("regattas", 428, "regattas", C["smith_regatta_pair"]),
    ("twelve-views", 428, "twelve small views", C["grand_canal_twelve_views"]),
    ("venice-views", 428, "Venice", E["venice"]),
    ("grand-canal", 428, "Grand Canal", E["grand_canal"]),
    ("painter-systematically", 428, "the painter", E["canaletto"]),
    ("canal-perspective", 428, "the Canal", E["grand_canal"], "Corefers to the Grand Canal."),
    ("canaletto-abilities", 428, "Canaletto’s abilities", E["canaletto"]),
    ("visentini", 428, "Visentini", E["visentini"], "Antonio Visentini; the publication and note remain pending."),
    ("published-engraving-series", 428, "engravings of the series", C["visentini_engraving_series"]),
    ("tessin-year-later", 428, "Tessin", E["tessin"]),
    ("exclusive-engagement", 428, "Canaletto", E["canaletto"], "In the reported four-year engagement.", 1),
    ("smith-four-years", 428, "Smith", E["smith"]),
    ("canaletto-virtually-stopped", 428, "Canaletto had virtually ceased working for Smith", E["canaletto"], "The claim concerns this moment, despite Tessin’s reported engagement."),
    ("no-paintings-canaletto", 429, "Canaletto", E["canaletto"]),
    ("consul-collection", 429, "the Consul’s collection", E["smith"]),
    ("visentini-series-reference", 429, "the series engraved by Visentini", C["visentini_engraving_series"]),
    ("english-visitors", 429, "English visitors", E["england"]),
    ("series-advertisement", 430, "the Visentini series", C["visentini_engraving_series"]),
    ("scheme", 430, "the scheme", C["smith_fourteen_picture_series"], "Haskell’s conditional advertising hypothesis about the series and its engravings."),
    ("canaletto-bedford", 431, "Canaletto", E["canaletto_bedford"]),
    ("bedford-views", 431, "twenty views", C["bedford_twenty_views"]),
    ("duke-bedford", 432, "Duke of Bedford", E["bedford"]),
    ("hervey-views", 432, "another series of twenty", C["hervey_twenty_views"]),
    ("sir-robert-hervey", 432, "Sir Robert Hervey", E["hervey"]),
    ("carlisle-views", 432, "seventeen", C["carlisle_seventeen_views"]),
    ("earl-carlisle", 433, "Earl of Carlisle", E["carlisle"]),
    ("artist-in-these-groups", 433, "the artist", E["canaletto"]),
    ("smith-work-comparison", 433, "working for Smith", E["smith"]),
    ("style-evaluation", 433, "mannerisms, the harshness, the signs of studio assistance", E["canaletto"], "The evaluation continues on p.306.")
]
for row in M:
    add_m(*row)

new_s = []


def add_s(local, lo, hi, subject, obj, predicate, claim, qualification, relation=False,
          footnote=None, cross=None, layer="authorial narrative", speaker="Haskell"):
    sid = f"st-chp10-p305-{local}"
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    mentioned = []
    for mention in newm:
        start = int(mention["start_char"])
        line_no = max((n for n, off in line_offsets.items() if off <= start), default=first)
        if lo <= line_no <= hi and mention["candidate_id"] not in mentioned:
            mentioned.append(mention["candidate_id"])
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": PAGE,
                  "pdf_physical_page": PHYSICAL, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        page_map = {P304: 304, P306: 306}
        pages = [page_map[item] for item in cross if item in page_map]
        if pages:
            qualifiers["cross_reference_printed_pages"] = pages
    new_s.append({"statement_id": sid, "segment_id": P305, "subject_candidate_id": subject,
                  "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": "\n".join(src[lo - 1:hi]), "source_file": SOURCE_FILE, "origin": "book"})


add_s("tessin-observation-close", 424, 424, E["tessin"], E["canaletto"],
      "qualified_account_of_smiths_four_year_exclusive_engagement",
      "Haskell says that, if Smith’s commissions for other customers are counted, there is no reason to doubt the substantial truth of Tessin’s observation.",
      "This closes the p.304 continuation; ‘substantial truth’ is qualified, and the exact scope of exclusive work remains Haskell’s interpretation.",
      relation=True, cross=[P304], layer="authorial interpretation")
add_s("smith-first-six-views", 425, 425, E["canaletto_sanmarco"], C["smith_first_sanmarco_views"],
      "painted_six_first_views_of_s_marco_for_smith",
      "Canaletto’s first pictures for Smith were six views of S. Marco and its surroundings, larger than his earlier works and described as bold, free and almost impressionistic.",
      "‘First’ is Haskell’s ordering; S. Marco’s precise spatial scope remains open, and footnote 1 is pending.", relation=True, footnote=1)
add_s("first-views-evaluation", 426, 426, E["canaletto"], C["smith_first_sanmarco_views"],
      "among_finest_works_and_antithetical_to_later_style",
      "Haskell calls the first views among Canaletto’s finest works and an antithesis of his later characteristic style for the Consul and other English patrons.",
      "This is Haskell’s aesthetic evaluation, not an objective ranking.", layer="authorial interpretation")
add_s("smith-fourteen-series-style", 427, 428, E["canaletto"], C["smith_fourteen_picture_series"],
      "painted_fourteen_pictures_for_smith_1730_1735_in_sober_style",
      "Canaletto painted fourteen pictures for Smith between 1730 and 1735; their treatment was less dramatic and more sober than before.",
      "The change is described for this series and should not be generalized to all of Canaletto’s work.", relation=True)
add_s("fourteen-series-composition", 428, 428, C["smith_fourteen_picture_series"], C["grand_canal_twelve_views"],
      "comprised_twelve_small_grand_canal_views_and_two_regatta_exceptions",
      "With two large regatta pictures as exceptions, the fourteen-picture group consisted of twelve small Venetian views chosen to document the whole Grand Canal systematically.",
      "Haskell says the choice was not based on the interest, importance or beauty of the subjects; retain the two groups as distinct components.", relation=True)
add_s("documentary-canal-series", 428, 428, C["grand_canal_twelve_views"], E["grand_canal"],
      "systematically_documented_the_canal_and_its_buildings",
      "The views traced the Grand Canal systematically; palaces and churches often appear in steep perspective without inviting admiration of them as objects in themselves.",
      "Haskell characterizes this as a documentary memorial and a prosaic, business-like approach.", relation=True, layer="authorial interpretation")
add_s("new-approach-contrast", 428, 428, C["smith_fourteen_picture_series"], None,
      "omitted_the_picturesque_and_associative_elements_of_earlier_patronage",
      "Haskell calls this approach new, contrasting it with earlier patron commissions that recorded contemporary events, associated buildings and landscapes, picturesque back streets and ruins, or notable architecture.",
      "This is Haskell’s comparative art-historical interpretation.", layer="authorial interpretation")
add_s("visual-catalogue-hypothesis", 428, 428, E["smith"], C["smith_fourteen_picture_series"],
      "possibly_intended_as_visual_catalogue_of_canalettos_abilities",
      "Haskell suggests the series may have functioned like a prospectus or visual catalogue of Canaletto’s abilities and asks whether this was the real motive.",
      "Explicit hypothesis; do not record as a proven commission purpose.", relation=True, layer="authorial hypothesis")
add_s("visentini-tourist-access", 428, 428, E["visentini"], C["visentini_engraving_series"],
      "published_engraved_series_in_1735_for_tourist_access",
      "Visentini’s engravings of the series were published in 1735, giving tourists an easy opportunity to become familiar with it.",
      "The publication and possible footnote marker require reconciliation with the consolidated notes and bibliography.", relation=True, footnote=2)
add_s("tessin-and-working-pause", 428, 428, E["tessin"], E["canaletto"],
      "reported_exclusive_engagement_while_canaletto_had_virtually_stopped_working_for_smith",
      "A year after the 1735 publication, Tessin reported Canaletto’s four-year exclusive engagement to Smith; Haskell adds that at this very time Canaletto seems virtually to have stopped working for Smith.",
      "Reported engagement and apparent cessation create a tension that must be retained, not reconciled by inference.", relation=True, footnote=2, layer="authorial comparison")
add_s("canaletto-gap-and-english-commissions", 429, 429, E["canaletto"], E["smith"],
      "no_consul_collection_pictures_for_about_ten_years_while_english_commissions_increased",
      "Haskell says no Canaletto paintings appear in the Consul’s collection between the Visentini series and a group about ten years later, while Canaletto received important commissions from English visitors.",
      "The passage states a gap in paintings in Smith’s collection, not a gap in all work or in the relationship.", relation=True, layer="authorial narrative")
add_s("advertisement-success-hypothesis", 430, 430, C["smith_fourteen_picture_series"], C["visentini_engraving_series"],
      "if_intended_as_advertisement_the_engraving_scheme_was_successful",
      "Haskell says that if the series was intended as an advertisement and the pictures were painted with the engravings in mind, the scheme was remarkably successful.",
      "Both the intention and the causal connection are conditional.", relation=True, layer="authorial hypothesis")
add_s("bedford-views", 431, 432, E["canaletto_bedford"], C["bedford_twenty_views"],
      "painted_twenty_views_for_duke_of_bedford_in_late_1730s",
      "During the last half of the 1730s Canaletto painted twenty views for the Duke of Bedford.",
      "Individual titles and commission dates are not specified.", relation=True)
add_s("hervey-views", 432, 432, E["canaletto_hervey"], C["hervey_twenty_views"],
      "painted_twenty_views_for_sir_robert_hervey_in_late_1730s",
      "Canaletto painted another series of twenty views for Sir Robert Hervey.",
      "Individual titles and commission dates are not specified.", relation=True)
add_s("carlisle-views", 432, 433, E["canaletto_carlisle"], C["carlisle_seventeen_views"],
      "painted_seventeen_views_for_earl_of_carlisle_in_late_1730s",
      "Canaletto painted seventeen views for the Earl of Carlisle.",
      "Individual titles and commission dates are not specified.", relation=True)
add_s("later-groups-style-comparison", 433, 433, E["canaletto"], C["bedford_twenty_views"],
      "later_groups_more_accurately_delineated_specific_buildings_than_smith_series",
      "Haskell says these groups attend more to accurately delineating specific buildings than Canaletto’s work for Smith; he begins to identify mannerisms, harshness and studio assistance.",
      "The evaluation continues on p.306; the final clause must be read with that continuation.", relation=True,
      cross=[P306], layer="authorial interpretation")

all_ids = cids | {row["candidate_id"] for row in newc}
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < first or q["source_line_end"] > last:
        raise SystemExit(f"statement range outside p.305: {row['statement_id']}")
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"missing statement FK {row['statement_id']} -> {cid}")
    if not q["mentioned_candidate_ids"]:
        raise SystemExit(f"statement has no anchored mention: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

cov[P304]["note"] = cov[P304]["note"].replace(
    "L421’s sentence continues on p.305, so p.304 remains partial.",
    "p.305 closes L421’s cross-page sentence; footnotes 1–7 remain pending in the consolidated notes segment, so p.304 remains partial.")
cov[P305].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L424-433",
    "note": "Printed p.305 body checked against CHP-10.pdf physical page 34. Closed p.304’s Tessin comparison with the qualification that commissions for other customers are included. Recorded Canaletto’s first six S. Marco views and their evaluative description; the fourteen pictures for Smith between 1730–1735; twelve small views documenting the Grand Canal and two large regatta exceptions; the systematic documentary approach and Haskell’s contrast with prior patronage; the conditional prospectus/advertising hypothesis; Visentini’s 1735 engravings and tourist access; Tessin’s later report alongside Canaletto’s apparent pause in work for Smith; the gap in paintings at the Consul’s collection; English visitor commissions; and the Bedford/Hervey/Carlisle groups (20/20/17 views). The accuracy/style comparison opens at L433 and continues on p.306. Scan-only S2 corrections: OCR ‘contemporary Use’ and ‘slum Use’ read ‘contemporary life’ and ‘slum life’; the superscript after ‘know it’ is retained as a possible note marker pending the consolidated notes sequence. S0 unchanged. Footnote 1 and any p.305 note markers remain to be reconciled in the consolidated notes source; L433 continues on p.306, so p.305 remains partial."})

summary = {"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
           "segment": P305, "segment_sha256": digest, "new_candidates": len(newc),
           "candidate_ids": [row["candidate_id"] for row in newc],
           "new_mentions": len(newm), "new_statements": len(new_s),
           "coverage": {"p304": cov[P304]["migration_status"], "p305": cov[P305]["migration_status"],
                        "p306": cov[P306]["migration_status"]}}
print(json.dumps(summary, ensure_ascii=False, indent=2))
if sys.argv[-1:] == ["--apply"]:
    for path in (cp, mp, sp, vp):
        backup = Path(str(path) + BACKUP)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(cp, cf, candidates + newc)
    write_csv(mp, mf, mentions + newm)
    write_jsonl(sp, statements + new_s)
    write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
    print("Applied p.305 S2 body migration; p.305 footnotes remain pending.")
