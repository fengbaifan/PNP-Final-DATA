"""Controlled S2 migration for printed page 248.

Default invocation is a read-only dry run. It leaves the source OCR untouched.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-9.pdf"
P247 = "chp-9:09_CHP-9_intro:l27-36"
P248 = "chp-9:09_CHP-9_intro:l38-46"
P249 = "chp-9:09_CHP-9_intro:l77-88"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_P248_HASH = "353c3cfd37cc305ef624b371deb6b4e2a7cabf9c6a58bafa8e0269316329ba46"
EXPECTED_P249_HASH = "73ab39a6a928011b2397ba2020cb978873200751bd57a8913d385d59ad081dce"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p248-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
for required in (P247, P248, P249, NOTES):
    if required not in segment_by_id:
        raise SystemExit(f"missing segment metadata: {required}")
if segment_by_id[P248]["sha256"] != EXPECTED_P248_HASH:
    raise SystemExit("p.248 segment hash changed; inspect before migration")
if segment_by_id[P249]["sha256"] != EXPECTED_P249_HASH:
    raise SystemExit("p.249 continuation segment hash changed; inspect before migration")
if segment_by_id[P248]["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed in segment metadata")
asset = ROOT / segment_by_id[P248]["source_file"]
if hashlib.sha256(asset.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
if not PDF.is_file() or not all((PROCESS / name).is_file() for name in (
    "p247_page_review_hi.png", "p248_page_review.png", "p249_page_review.png"
)):
    raise SystemExit("chapter PDF or reviewed page images are missing")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
page_meta = segment_by_id[P248]
selected = source_lines[page_meta["line_start"] - 1:page_meta["line_end"]]
if hashlib.sha256("\n".join(selected).encode("utf-8")).hexdigest() != EXPECTED_P248_HASH:
    raise SystemExit("p.248 segment content hash changed")
line_offsets = {}
offset = 0
for line_no, line in zip(range(page_meta["line_start"], page_meta["line_end"] + 1), selected):
    line_offsets[line_no] = offset
    offset += len(line) + 1

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
statement_rows = read_jsonl(statement_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
expected_coverage = {
    P247: ("reviewed", "partial", "L27-36"),
    P248: ("queued", "pending", ""),
    P249: ("queued", "pending", ""),
    NOTES: ("queued", "pending", ""),
}
for segment_id, state in expected_coverage.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")

new_candidates = [
    ("cand-8148", "Votive pictures showing noble patrons beside divine protectors", "term", 39,
     "Class of large votive pictures described as placing noble patrons almost on equal terms with divine protectors; no individual picture is named."),
    ("cand-8149", "Unnamed publishers and printsellers praising Venetian patrician patrons", "term", 39,
     "Collective publishers and printsellers whose praise of patrician patrons is described as obsequious; no individual is named."),
    ("cand-8150", "Unnamed Venetian governors portrayed in provincial church canvases", "term", 40,
     "Collective officeholders shown in Maffei's canvases; none is named in this passage."),
    ("cand-8151", "Maffei's series of canvases depicting Venetian governors in provincial churches", "work", 39,
     "Collective series attributed by surname only in the body; the index candidate for Francesco Maffei is reused, while this work group remains open."),
    ("cand-8152", "Palazzo Ducale paintings commemorating Venetian commanders after victories", "work", 41,
     "Collective palace paintings commemorating military commanders; the text singles out Lazzarini's triumphal arch as a climax."),
    ("cand-8153", "Façade of S. Maria del Giglio designed by Antonio Barbaro", "work", 42,
     "Specific architectural façade at the church; keep distinct from the church building and from the people represented on it."),
    ("cand-8154", "War of Candia", "event", 43,
     "War in which Antonio Barbaro had fought; no dates or campaign details are supplied in this passage."),
    ("cand-8155", "Candia", "place", 45,
     "Place named among the plans represented on the façade pedestals; distinguish it from the War of Candia event."),
    ("cand-8156", "Este", "place", 39,
     "City named among the provincial church locations; distinguish it from the Este dynasty and family."),
    ("cand-8157", "Rovigo", "place", 39,
     "City named among the provincial church locations."),
    ("cand-8158", "Other provincial locations of Maffei's governor canvases", "term", 39,
     "Collective reference to provincial church sites beyond Este and Rovigo; no other town or church is identified."),
    ("cand-8159", "Spalato", "place", 45,
     "Historical place name listed among plans on the façade pedestals; no modern-name normalization is imposed here."),
    ("cand-8160", "Zara", "place", 45,
     "Historical place name listed among plans on the façade pedestals; no modern-name normalization is imposed here."),
    ("cand-8161", "Barbaro family arms on the S. Maria del Giglio façade", "work", 44,
     "Heraldic element on the façade; the source says Barbaro arms without identifying a particular blazon."),
    ("cand-8162", "Figure of Glory on the S. Maria del Giglio façade", "work", 44,
     "Allegorical figure crowning the façade; represent as an architectural work element, not as a historical person."),
    ("cand-8163", "Antonio Barbaro's four unnamed brothers represented on the façade", "term", 45,
     "Collective group of four brothers; the source does not name them here."),
    ("cand-8164", "Statues of Honour and Virtue on the S. Maria del Giglio façade", "work", 44,
     "Pair of named allegorical statues flanking Antonio Barbaro's central figure."),
    ("cand-8165", "Figures of Fame and Wisdom at the base of the façade volutes", "work", 45,
     "Pair of allegorical architectural figures; represent them as components of the façade, not as historical people."),
    ("cand-8166", "Urn containing Antonio Barbaro's remains on the façade", "work", 44,
     "Architectural element described as containing Antonio Barbaro's mortal remains."),
    ("cand-8167", "Non-nobles in Haskell's comparison of Venetian patronage", "term", 39,
     "Unnamed social category contrasted with patricians who were praised as patrons."),
    ("cand-8168", "Divine protectors in Venetian votive pictures", "term", 39,
     "Religious figures described as protectors alongside whom noble patrons were shown; individual figures are not named."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
if len(candidate_ids) != len(candidate_rows):
    raise SystemExit("duplicate candidate IDs already exist")
if max(int(cid.split("-")[1]) for cid in candidate_ids) != 8147:
    raise SystemExit("candidate inventory changed since p.247; inspect before allocating IDs")
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows}
new_keys = set()
for candidate_id, name, kind, line_no, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P248}#L{line_no}",
    })
    candidate_ids.add(candidate_id)

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
new_mentions = []


def mention(line_no, suffix, candidate_id, surface, note="", occurrence=0):
    mention_id = f"m-chp9-p248-{suffix}"
    if mention_id in existing_mention_ids or any(r["mention_id"] == mention_id for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    line = source_lines[line_no - 1]
    position = -1
    search_at = 0
    for _ in range(occurrence + 1):
        position = line.find(surface, search_at)
        if position < 0:
            raise SystemExit(f"surface not found at L{line_no}: {surface!r} occurrence={occurrence}")
        search_at = position + len(surface)
    start = line_offsets[line_no] + position
    end = start + len(surface)
    span = (P248, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mention_id} {surface!r}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": P248, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


MENTION_SPECS = [
    (39, "rich-families", "cand-8134", "immensely rich families", "Families discussed in connection with reception into the nobility."),
    (39, "nobility-reception", "cand-8108", "nobility", "Social estate into which the rich families were received."),
    (39, "patricians", "cand-8109", "patricians", "Venetian patricians praised as patrons; footnote marker 1."),
    (39, "publishers-printsellers", "cand-8149", "publishers or printsellers", "Unnamed collective sources of praise."),
    (39, "non-nobles", "cand-8167", "non-nobles", "Social group contrasted with patricians."),
    (39, "veronese", "cand-2755", "Veronese’s", "Paolo Veronese."),
    (39, "tintoretto", "cand-2627", "Tintoretto’s", "Tintoretto."),
    (39, "venice", "cand-2719", "Venice", "City/polity glorified by the earlier paintings."),
    (39, "tiepolo", "cand-2569", "Tiepolo", "Giambattista Tiepolo."),
    (39, "individual-families", "cand-8124", "individual families", "Families exalted by Tiepolo."),
    (39, "patronage", "cand-2720", "Patronage in Venice", "Venetian art patronage as an aristocratic practice."),
    (39, "government", "cand-8105", "system of government", "Venetian political system described as aristocratic."),
    (39, "aristocracy-first", "cand-8108", "the aristocracy", "Social estate said to dominate political and artistic life.", 0),
    (39, "state", "cand-8105", "the State", "Venetian political entity."),
    (39, "votive-pictures", "cand-8148", "huge votive pictures", "Class of pictures that came to prominence in the second half of the sixteenth century."),
    (39, "noble-patrons", "cand-8108", "noble patrons", "Patrons shown near their divine protectors."),
    (39, "divine-protectors", "cand-8168", "divine protectors", "Religious figures in the votive imagery."),
    (39, "individual-glorification", "cand-2721", "Individual glorification", "Index topic for apotheoses and individual display."),
    (39, "maffei", "cand-1486", "Maffei", "Surname only in the body; mapped to the page-248 Francesco Maffei index candidate, identity remains open."),
    (39, "canvas-series", "cand-8151", "series of canvases", "Collective work group attributed to Maffei."),
    (39, "churches", "cand-8158", "churches", "Unspecified provincial church sites for Maffei's canvases."),
    (39, "este", "cand-8156", "Este", "Provincial city."),
    (39, "rovigo", "cand-8157", "Rovigo", "Provincial city."),
    (39, "other-provinces", "cand-8158", "other provinces", "Unspecified additional locations."),
    (40, "venetian-governors", "cand-8150", "Venetian governors", "Unnamed governors depicted in the allegorical canvases."),
    (40, "state-homage", "cand-8105", "the State", "Political entity honored alongside individuals."),
    (41, "palazzo-ducale", "cand-1806", "Palazzo Ducale", "Palace location of commander memorial paintings."),
    (41, "commanders", "cand-8152", "great commanders", "Collective subject of the palace paintings."),
    (41, "triumphal-arch", "cand-1373", "triumphal arch", "Lazzarini's work for Francesco Morosini."),
    (41, "lazzarini", "cand-1368", "Gregorio Lazzarini", "Named painter."),
    (41, "morosini", "cand-1705", "Francesco Morosini", "Named commander."),
    (41, "peloponnese", "cand-8117", "Peloponnese", "Region named for Morosini's short-lived successes."),
    (41, "state-individual-shift", "cand-8105", "the State", "One pole in the shift toward individual glorification.", 0),
    (42, "facade", "cand-8153", "façade", "Architectural work at S. Maria del Giglio."),
    (42, "church-place", "cand-0736", "S. Maria del Giglio", "Church building; distinct from its façade work."),
    (43, "antonio-barbaro", "cand-0185", "Antonio Barbaro", "Named Venetian patrician."),
    (43, "war-candia", "cand-8154", "war of Candia", "Named conflict."),
    (43, "his-brothers", "cand-8163", "his brothers", "Unnamed Barbaro brothers represented alongside Antonio."),
    (43, "sardi", "cand-2360", "Giuseppe Sardi", "Named builder of the façade."),
    (44, "glory-figure", "cand-8162", "figure of Glory", "Architectural sculptural element."),
    (44, "barbaro-arms", "cand-8161", "Barbaro arms", "Heraldic element on the façade."),
    (44, "cardinal-virtues", "cand-5174", "cardinal virtues", "Allegorical group represented on the façade."),
    (44, "antonio-central-figure", "cand-0185", "Antonio", "Coreference to Antonio Barbaro."),
    (44, "urn", "cand-8166", "urn containing his mortal remains", "Funerary element on the façade."),
    (44, "honour-virtue-statues", "cand-8164", "statues of Honour and", "The first of the two named statues; Virtue follows in the source."),
    (45, "virtue-statue", "cand-8164", "Virtue", "Second statue in the named pair."),
    (45, "fame-wisdom", "cand-8165", "Fame and Wisdom", "Pair of allegorical figures at the base of the façade volutes."),
    (45, "four-brothers", "cand-8163", "Antonio’s four brothers", "Unnamed family members shown on the lower storey."),
    (45, "candia-place", "cand-8155", "Candia", "Place represented in a pedestal plan, distinct from the War of Candia."),
    (45, "corfu", "cand-8118", "Corfu", "Place represented in a pedestal plan."),
    (45, "spalato", "cand-8159", "Spalato", "Historical place name represented in a pedestal plan."),
    (45, "zara", "cand-8160", "Zara", "Historical place name represented in a pedestal plan."),
    (45, "padua", "cand-1803", "Padua", "Place represented in a pedestal plan."),
    (45, "rome", "cand-4490", "Rome", "Place represented in a pedestal plan; also the stated ambassadorial post."),
    (46, "ambassadorial-service", "cand-0185", "Antonio had served as ambassador", "Source text associates Antonio's ambassadorial service with Rome."),
    (46, "barbaro-conception", "cand-0185", "Antonio' Barbaro’s conception", "OCR has an extra apostrophe after Antonio; correction is stored on the anchored statement."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(first, last):
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, first, last, subject, obj, predicate, claim, qualification,
                   mentioned, marker=None, note_line=None, extras=None):
    if first < page_meta["line_start"] or last > page_meta["line_end"]:
        raise SystemExit(f"statement lines outside p.248 segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 248,
        "pdf_physical_page": 6, "claim": claim, "speaker": "Haskell",
        "text_layer": "body", "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if marker is not None:
        qualifiers["footnote_marker"] = marker
    if note_line is not None:
        qualifiers["cross_reference_segments"] = [{
            "segment_id": NOTES, "source_line_start": note_line, "source_line_end": note_line,
        }]
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": P248,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote(first, last), "origin": "book",
            "source_file": page_meta["source_file"]}


new_statements = [
    make_statement("st-chp9-p248-patronage-not-appreciation", 39, 39, "cand-2720", None,
        "patronage_often_had_little_to_do_with_artistic_appreciation_or_understanding",
        "Completing p.247 L31, Haskell says aristocratic patronage could often have little to do with appreciation or understanding.",
        "The continuation closes the p.247 sentence; preserve it as a separate anchored statement linked back to that page.",
        ["cand-2720", "cand-8124"],
        extras={"continued_from_segment_id": P247, "continued_from_source_line": 31,
                "cross_reference_segments": [{"segment_id": P247, "source_line_start": 31, "source_line_end": 31}]}),
    make_statement("st-chp9-p248-collections-after-nobility", 39, 39, "cand-8134", "cand-8108",
        "rich_families_began_collecting_after_reception_into_nobility",
        "Haskell says immensely rich families began amassing collections only after their reception into the nobility.",
        "No family or collection is identified; this continues the discussion of newly admitted families without naming members.",
        ["cand-8134", "cand-8108"], marker=1, note_line=335, extras={"relation_candidate": True}),
    make_statement("st-chp9-p248-patricians-praised-as-patrons", 39, 39, "cand-8109", "cand-2720",
        "patricians_often_acclaimed_as_glorious_patrons_by_publishers",
        "Haskell says that few patricians escaped being acclaimed as glorious patrons by obsequious publishers or printsellers, a tribute rarely given to non-nobles.",
        "This is a general authorial comparison; no individual publisher, patrician, or commission is named.",
        ["cand-8109", "cand-8149", "cand-8167"], marker=1, note_line=335),
    make_statement("st-chp9-p248-veronese-tintoretto-venice", 39, 39, "cand-2755", "cand-2719",
        "familiar_paintings_of_veronese_and_tintoretto_glorified_venice",
        "Haskell contrasts paintings by Veronese and Tintoretto devoted to glorifying Venice with Tiepolo's later emphasis on individual families.",
        "The passage names no individual painting; preserve the broad art-historical comparison.",
        ["cand-2755", "cand-2627", "cand-2719", "cand-2569", "cand-8124"],
        extras={"relation_candidate": True}),
    make_statement("st-chp9-p248-aristocratic-patronage-state", 39, 39, "cand-2720", "cand-2734",
        "venetian_patronage_and_government_were_aristocratic_with_state_aristocracy_identification",
        "Haskell describes Venetian patronage and government as aristocratic and says the identification of aristocracy and State was absolute.",
        "This is Haskell's interpretive generalization, not a constitutional formula quoted from a statute.",
        ["cand-2720", "cand-8108", "cand-8105", "cand-2734"]),
    make_statement("st-chp9-p248-votive-pictures", 39, 39, "cand-8148", "cand-8168",
        "votive_pictures_placed_noble_patrons_almost_equal_to_divine_protectors",
        "Haskell says large votive pictures that became prominent in the second half of the sixteenth century showed noble patrons on almost equal terms with their divine protectors.",
        "The class of pictures is not an individual work; preserve the author's approximate chronology and comparison.",
        ["cand-8148", "cand-8108", "cand-8168"]),
    make_statement("st-chp9-p248-maffei-governor-canvases", 39, 40, "cand-1486", "cand-8150",
        "maffei_canvases_portrayed_venetian_governors_in_provincial_churches",
        "Haskell says individual glorification advanced in the early seventeenth century through Maffei's series of canvases in churches in Este, Rovigo, and other provinces, portraying Venetian governors in complex allegorical trappings.",
        "The body gives Maffei's surname only; the Francesco Maffei index candidate is reused because it indexes p.248, but S3 must confirm identity. Note 2 is a separate source locator.",
        ["cand-1486", "cand-8151", "cand-8150", "cand-8156", "cand-8157", "cand-8158"],
        marker=2, note_line=336, extras={"relation_candidate": True}),
    make_statement("st-chp9-p248-canvas-homage", 40, 40, "cand-8151", "cand-8105",
        "governor_canvases_honored_state_as_well_as_depicted_individuals",
        "Haskell says the canvases paid homage both to the State and to the individual governors depicted.",
        "The claim is about the represented subject and political meaning of the work group.",
        ["cand-8151", "cand-8105", "cand-8150"], extras={"relation_candidate": True}),
    make_statement("st-chp9-p248-palace-commemorations", 41, 41, "cand-8152", "cand-1705",
        "palace_paintings_commemorated_commanders_with_lazzarini_arch_honoring_morosini",
        "Haskell says Palazzo Ducale paintings commemorated commanders after victories, with Gregorio Lazzarini's triumphal arch honouring Francesco Morosini's short-lived successes in the Peloponnese as a climax.",
        "The passage names no other commander or campaign; Morosini's success is explicitly described as short-lived.",
        ["cand-8152", "cand-1806", "cand-1373", "cand-1368", "cand-1705", "cand-8117"],
        marker=3, note_line=337, extras={"relation_candidate": True}),
    make_statement("st-chp9-p248-shift-to-individual", 41, 41, "cand-2721", "cand-8105",
        "seventeenth_century_attention_shifted_toward_individual_at_state_or_gods_expense",
        "Haskell describes a seventeenth-century shift of attention toward the individual at the expense of the State or God.",
        "This is a broad interpretive periodization rather than a single dated commission.",
        ["cand-2721", "cand-8105", "cand-8108"]),
    make_statement("st-chp9-p248-facade-design-and-building", 42, 43, "cand-8153", "cand-0185",
        "antonio_barbaro_designed_facade_as_family_apotheosis_and_sardi_erected_it",
        "Haskell says Antonio Barbaro designed the S. Maria del Giglio façade as an apotheosis of himself and his brothers, after fighting in the War of Candia, and Giuseppe Sardi erected it between 1675 and 1683.",
        "Retain the source's account of Barbaro's role and the stated construction span; note 4 points to Barbaro's will but does not itself prove the design attribution.",
        ["cand-8153", "cand-0736", "cand-0185", "cand-8154", "cand-8163", "cand-2360"],
        marker=4, note_line=338, extras={"relation_candidate": True}),
    make_statement("st-chp9-p248-facade-iconographic-program", 44, 45, "cand-8153", None,
        "facade_program_combined_barbaro_heraldry_portrait_family_and_allegories",
        "The façade program included Glory, Barbaro arms and cardinal virtues; a central armoured Antonio with an urn of his remains; statues of Honour and Virtue; Fame and Wisdom; and his four brothers on the lower storey.",
        "This records the source's description of architectural elements and allegorical imagery; individual components are not assigned independent historical personhood.",
        ["cand-8153", "cand-8162", "cand-8161", "cand-5174", "cand-0185", "cand-8166", "cand-8164", "cand-8165", "cand-8163"],
        extras={"continuation_to_segment_id": P249, "continuation_to_source_line": 78,
                "ocr_corrections": [{"source_line": 46, "ocr": "Antonio' Barbaro’s", "print": "Antonio Barbaro’s", "basis": "CHP-9.pdf physical page 6"}]}),
    make_statement("st-chp9-p248-facade-place-plans-and-ambassador", 45, 45, "cand-8153", "cand-0185",
        "pedestals_displayed_plans_of_named_places_where_antonio_served_as_ambassador_in_rome",
        "Haskell says the pedestals beneath the brothers displayed plans of Candia, Corfu, Spalato, Zara, Padua and Rome, where Antonio had served as ambassador.",
        "The grammar links the ambassadorial service specifically to Rome; it does not say he served as ambassador in every place whose plan appears.",
        ["cand-8153", "cand-8163", "cand-8155", "cand-8118", "cand-8159", "cand-8160", "cand-1803", "cand-4490", "cand-0185"],
        extras={"relation_candidate": True}),
]
statement_ids = {row["statement_id"] for row in statement_rows}
new_statement_ids = {row["statement_id"] for row in new_statements}
if len(statement_ids) != len(statement_rows) or len(new_statement_ids) != len(new_statements) or statement_ids & new_statement_ids:
    raise SystemExit("duplicate statement ID")

# The prior page's clause is now closed by p.248 L39.
coverage_by_id[P247].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L27-36",
    "note": "Printed p.247 (CHP-9.pdf physical p.5) reviewed against the page image. Its L31 sentence ending 'and may' is closed by p.248 L39 and cross-linked in book-statements. L32-34 continue p.246 note 4 and link to consolidated notes L331; L35-36 remain an unnumbered note-like passage quoting Paolo Renier, with marker uncertainty preserved. Numbered notes 1-3 remain in the separate notes segment L332-334."
})
coverage_by_id[P248].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L38-46",
    "note": "Printed p.248 (CHP-9.pdf physical p.6) reviewed against the page image. Body claims and footnote markers 1-4 are anchored separately; note pointers link to consolidated notes L335-338. The p.247 L31 sentence is closed at p.248 L39. L46 ends 'devoid' and continues at p.249 L78 ('of a single religious symbol'); retain this segment as reviewed/partial until that continuation is migrated. The intervening Plate 41-44 OCR segments are separate visual material and are not merged into this body segment."
})

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
print(json.dumps({
    "segments": [P247, P248], "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage": {
        P247: [coverage_by_id[P247]["disposition"], coverage_by_id[P247]["migration_status"]],
        P248: [coverage_by_id[P248]["disposition"], coverage_by_id[P248]["migration_status"]],
    },
    "cross_page_continuations": [
        f"{P247} L31 -> {P248} L39",
        f"{P248} L46 -> {P249} L78",
    ],
    "footnote_links": [
        f"{P248} marker 1 -> {NOTES} L335",
        f"{P248} marker 2 -> {NOTES} L336",
        f"{P248} marker 3 -> {NOTES} L337",
        f"{P248} marker 4 -> {NOTES} L338",
    ],
}, ensure_ascii=False))
if not args.apply:
    print("DRY RUN: no files changed")
else:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
    write_csv_atomic(mention_path, mention_fields, mention_rows + new_mentions)
    write_jsonl_atomic(statement_path, statement_rows + new_statements)
    write_csv_atomic(coverage_path, coverage_fields, coverage_rows)
    print("applied; backups=" + ", ".join(backup.name for _, backup in backups))
