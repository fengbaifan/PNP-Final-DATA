"""Controlled semantic repair for printed p.251 in full-book S2.

Default invocation is a read-only preflight. Source OCR is never modified.
The script restores pinned p.251 mentions, records exact footnote mentions,
reviews endpoints/classifications, and separates compound page claims.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l106-114"
NOTES_SEGMENT_ID = "chp-9:09_CHP-9_intro:l323-445"
NEXT_SEGMENT_ID = "chp-9:09_CHP-9_intro:l116-122"
BASELINE_REV = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_SEGMENT_HASH = "8d3a506cd567873e58c704496c286086bb86b701fcc0b32bc9e5fdd2b2547eae"
EXPECTED_NOTES_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p251-semantic-review-20261014"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.251 S2 repair")
parser.add_argument("--resume-partial-apply", action="store_true", help="finish coverage write after a partial apply")
args = parser.parse_args()
if args.apply and args.resume_partial_apply:
    raise SystemExit("choose either --apply or --resume-partial-apply")


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
segment = segment_by_id.get(SEGMENT_ID)
notes_segment = segment_by_id.get(NOTES_SEGMENT_ID)
if not segment or not notes_segment or NEXT_SEGMENT_ID not in segment_by_id:
    raise SystemExit("p.251, notes, or next-page segment metadata is missing")
if segment["sha256"] != EXPECTED_SEGMENT_HASH or notes_segment["sha256"] != EXPECTED_NOTES_HASH:
    raise SystemExit("p.251 or notes segment hash changed; inspect before repair")
if segment["asset_sha256"] != EXPECTED_ASSET_HASH or notes_segment["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash in segment metadata changed")
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()


def segment_text_and_offsets(meta):
    selected = source_lines[meta["line_start"] - 1:meta["line_end"]]
    text = "\n".join(selected)
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash mismatch: {meta['segment_id']}")
    offsets, offset = {}, 0
    for line_number, line in zip(range(meta["line_start"], meta["line_end"] + 1), selected):
        offsets[line_number] = offset
        offset += len(line) + 1
    return text, offsets


segment_text, line_offsets = segment_text_and_offsets(segment)
notes_text, notes_line_offsets = segment_text_and_offsets(notes_segment)
candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
_, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
statement_rows = read_jsonl(statement_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}
statement_by_id = {row["statement_id"]: row for row in statement_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
coverage = coverage_by_id.get(SEGMENT_ID)
notes_coverage = coverage_by_id.get(NOTES_SEGMENT_ID)

if args.resume_partial_apply:
    backup_paths = {path: path.with_name(path.name + BACKUP_SUFFIX)
                    for path in (mention_path, statement_path, coverage_path)}
    if any(not backup.exists() for backup in backup_paths.values()):
        raise SystemExit("partial-apply backups are incomplete; refusing to resume")
    if hashlib.sha256(coverage_path.read_bytes()).hexdigest() != hashlib.sha256(backup_paths[coverage_path].read_bytes()).hexdigest():
        raise SystemExit("coverage table changed since partial apply; inspect before resuming")
    baseline_rows = list(csv.DictReader(io.StringIO(subprocess.check_output(
        ["git", "show", f"{BASELINE_REV}:04-knowledge/tables/mentions.csv"],
        cwd=ROOT, text=True, encoding="utf-8",
    ))))
    expected_page_ids = {row["mention_id"] for row in baseline_rows if row["segment_id"] == SEGMENT_ID}
    current_page_rows = [row for row in mention_rows if row["segment_id"] == SEGMENT_ID]
    expected_note_ids = {
        "m-chp9-notes-p251-florio-poet", "m-chp9-notes-p251-florio-work",
        "m-chp9-notes-p251-florio-venice", "m-chp9-notes-p251-correspondence-letter",
        "m-chp9-notes-p251-correspondence-recipient", "m-chp9-notes-p251-correspondence-palace",
        "m-chp9-notes-p251-periodical",
    }
    current_note_ids = {row["mention_id"] for row in mention_rows if row["mention_id"] in expected_note_ids}
    target_statements = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    if {row["mention_id"] for row in current_page_rows} != expected_page_ids or len(current_page_rows) != 57:
        raise SystemExit("partial-apply page mentions do not match the pinned 57-row baseline")
    if current_note_ids != expected_note_ids:
        raise SystemExit("partial-apply note mentions are incomplete")
    if len(target_statements) != 34 or any(row.get("qualifiers", {}).get("relation_candidate") is None for row in target_statements):
        raise SystemExit("partial-apply statement table does not match the planned 34 classified p.251 statements")
    for row in target_statements:
        q = row.get("qualifiers", {})
        for candidate_id in [row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])]:
            if candidate_id is not None and candidate_id not in candidate_ids:
                raise SystemExit(f"partial-apply statement has missing candidate: {row['statement_id']} {candidate_id}")
    if not coverage or (coverage["disposition"], coverage["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit("p.251 coverage changed since partial apply")
    coverage["note"] = (
        "Printed p.251 reviewed against CHP-9.pdf physical p.13. Restored and span-checked 57 baseline page mentions; "
        "added seven exact mentions to notes L350-351, including the identified Florio title and the cited 1708 letter/publication. "
        "Reviewed 14 existing statements, classified every claim, corrected attribution/endpoints, and separated the gallery, "
        "employment, style-location, and family-display claims. L114's Ricci continuation is linked to p.252 L117. "
        "The page image supports the correction 'Le Crazie' to printed 'Le Grazie'; S0 remains unchanged."
    )
    write_csv_atomic(coverage_path, coverage_fields, coverage_rows)
    print("Resumed partial apply: coverage record written; mention and statement tables were verified and left untouched.")
    raise SystemExit(0)

if not coverage or (coverage["disposition"], coverage["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit(f"unexpected p.251 coverage: {coverage}")
if not notes_coverage or (notes_coverage["disposition"], notes_coverage["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit(f"unexpected notes coverage: {notes_coverage}")

expected_existing_ids = {
    "st-chp9-p251-1708-palace-description", "st-chp9-p251-artists-seventeenth-century-taste",
    "st-chp9-p251-avant-painters-outside-venice", "st-chp9-p251-cignani-and-mazza",
    "st-chp9-p251-consistent-taste-and-team", "st-chp9-p251-florio-country-house-verse",
    "st-chp9-p251-gallery-works", "st-chp9-p251-lodovico-last-doge", "st-chp9-p251-manin-style-sites",
    "st-chp9-p251-manin-venice-patronage", "st-chp9-p251-mirror-fashion-origin",
    "st-chp9-p251-old-new-shared-display", "st-chp9-p251-palace-hangings-tapestries",
    "st-chp9-p251-passeriano-wings",
}
target_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
if {row["statement_id"] for row in target_rows} != expected_existing_ids:
    raise SystemExit("p.251 statement inventory changed; inspect before repair")
unset_ids = {"st-chp9-p251-mirror-fashion-origin", "st-chp9-p251-palace-hangings-tapestries"}
if any(statement_by_id[sid].get("qualifiers", {}).get("relation_candidate") is not None for sid in unset_ids):
    raise SystemExit("p.251 classification pre-state changed; inspect before repair")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("p.251 already has current mentions; inspect instead of duplicating")

baseline_text = subprocess.check_output(
    ["git", "show", f"{BASELINE_REV}:04-knowledge/tables/mentions.csv"],
    cwd=ROOT, text=True, encoding="utf-8",
)
baseline_mentions = list(csv.DictReader(io.StringIO(baseline_text)))
restored_mentions = [row.copy() for row in baseline_mentions if row["segment_id"] == SEGMENT_ID]
if len(restored_mentions) != 57:
    raise SystemExit(f"pinned baseline has {len(restored_mentions)} p.251 mentions, expected 57")
for row in restored_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"restored mention has missing candidate: {row['mention_id']}")
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"restored mention span differs from S0: {row['mention_id']}")
    if row["mention_id"] in mention_ids:
        raise SystemExit(f"mention ID already exists: {row['mention_id']}")

new_note_mentions = []
note_span_set = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mention_rows}


def add_note_mention(mention_id: str, line_number: int, surface: str, candidate_id: str, note: str,
                     occurrence: int = 0):
    if mention_id in mention_ids or any(r["mention_id"] == mention_id for r in new_note_mentions):
        raise SystemExit(f"note mention ID already exists: {mention_id}")
    line = source_lines[line_number - 1]
    pos = -1
    cursor = 0
    for _ in range(occurrence + 1):
        pos = line.find(surface, cursor)
        if pos < 0:
            raise SystemExit(f"note mention span not found at L{line_number}: {surface!r}")
        cursor = pos + len(surface)
    start = notes_line_offsets[line_number] + pos
    end = start + len(surface)
    span = (NOTES_SEGMENT_ID, str(start), str(end))
    if span in note_span_set:
        raise SystemExit(f"note mention span already exists: {mention_id}")
    if candidate_id not in candidate_ids or notes_text[start:end] != surface:
        raise SystemExit(f"invalid candidate or note span: {mention_id}")
    note_span_set.add(span)
    new_note_mentions.append({
        "mention_id": mention_id, "segment_id": NOTES_SEGMENT_ID, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_note_mention("m-chp9-notes-p251-florio-poet", 350, "Daniele Florio", "cand-8228",
                 "Poet named in the p.251 note; not independently identified beyond the cited source.")
add_note_mention("m-chp9-notes-p251-florio-work", 350, "Le Crazie", "cand-8229",
                 "S0 OCR reads 'Le Crazie'; page image reads the cited title Le Grazie.")
add_note_mention("m-chp9-notes-p251-florio-venice", 350, "Venezia", "cand-2719",
                 "Publication place named for the cited Florio work.")
add_note_mention("m-chp9-notes-p251-correspondence-letter", 351,
                 "Lettera del Co: di N.N. A Madama la Marchesa di N.N. a Parigi", "cand-8230",
                 "Letter/account title cited for the 1708 Palazzo Manin wedding festivities; original not consulted.")
add_note_mention("m-chp9-notes-p251-correspondence-recipient", 351,
                 "Madama la Marchesa di N.N.", "cand-8233",
                 "Recipient remains unnamed in the title's N.N. placeholder.")
add_note_mention("m-chp9-notes-p251-correspondence-palace", 351,
                 "Palazzo di S.E. il Signor Co: Manin", "cand-1520",
                 "Palazzo Manin named in the cited letter title.")
add_note_mention("m-chp9-notes-p251-periodical", 351, "La Galleria di Minerva, VI", "cand-8231",
                 "Volume cited as the publication venue for the letter/account.")


def quote_lines(first: int, last: int | None = None):
    last = first if last is None else last
    return "\n".join(source_lines[first - 1:last])


def update(statement_id: str, *, subject: str | None, object_: str | None, predicate: str,
           claim: str, qualification: str, mentioned: list[str], relation: bool,
           first: int, last: int | None = None, speaker: str = "Haskell",
           layer: str | None = None, extras: dict | None = None):
    row = statement_by_id[statement_id]
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers.update({
        "source_line_start": first,
        "source_line_end": first if last is None else last,
        "printed_page": 251,
        "pdf_physical_page": 13,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer or ("footnote" if first >= 349 else "body"),
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "semantic_review": "2026-10-14 source-order review; page image, spans, endpoints, and speaker attribution checked",
    })
    if extras:
        qualifiers.update(extras)
    row["original_quote"] = quote_lines(first, last)


def new_statement(statement_id: str, *, first: int, subject: str | None, object_: str | None,
                  predicate: str, claim: str, qualification: str, mentioned: list[str],
                  relation: bool, speaker: str = "Haskell", last: int | None = None,
                  layer: str | None = None, extras: dict | None = None):
    if statement_id in statement_ids:
        raise SystemExit(f"new statement ID already exists: {statement_id}")
    for candidate_id in [subject, object_, *mentioned]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"new statement has missing candidate: {statement_id} {candidate_id}")
    qualifiers = {
        "source_line_start": first,
        "source_line_end": first if last is None else last,
        "printed_page": 251,
        "pdf_physical_page": 13,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer or ("footnote" if first >= 349 else "body"),
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "semantic_review": "2026-10-14 source-order review; atomic statement",
    }
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": statement_id, "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject, "object_candidate_id": object_, "predicate": predicate,
        "qualifiers": qualifiers, "original_quote": quote_lines(first, last),
        "origin": "book", "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    }


correspondent = "Unidentified correspondent (quoted/reported by Haskell)"
note3 = {"footnote_marker": 3, "cross_reference_segments": [{
    "segment_id": NOTES_SEGMENT_ID, "source_line_start": 351, "source_line_end": 351,
}]}

update("st-chp9-p251-1708-palace-description", subject="cand-1520", object_="cand-8227",
    predicate="palazzo_manin_compared_with_adjoining_rialto_marvel",
    claim="The unidentified correspondent writing in 1708 described the Palazzo Manin as majestic and said it lost nothing in grandeur when compared with an adjoining marvel of the Rialto.",
    qualification="This is the correspondent's comparison, not an independently measured ranking. The exact Rialto landmark remains unresolved.",
    mentioned=["cand-8232", "cand-1520", "cand-8178", "cand-8227", "cand-8230"], relation=False,
    first=108, speaker=correspondent, extras=note3)
update("st-chp9-p251-artists-seventeenth-century-taste", subject="cand-8238", object_="cand-8240",
    predicate="successful_artists_linked_to_seventeenth_century_taste",
    claim="Haskell says the artists he considered most successful were chiefly those most closely linked to seventeenth-century taste, and their prestige lasted after more adventurous painters struck out in new directions.",
    qualification="The named successful group remains open ('and others'); this is Haskell's comparative historical characterization, not a formal connection between the term and each artist.",
    mentioned=["cand-8238", "cand-2834", "cand-1368", "cand-0168", "cand-0944", "cand-0171", "cand-8240", "cand-8239"],
    relation=False, first=114)
update("st-chp9-p251-avant-painters-outside-venice", subject="cand-8239", object_="cand-2719",
    predicate="three_adventurous_painters_scarcely_employed_in_great_venetian_palaces",
    claim="Haskell says Pellegrini, Amigoni and Sebastiano Ricci, all adults in the early eighteenth century, were scarcely employed in the decoration of great palaces and became better known outside Venice.",
    qualification="Retain 'scarcely' and the comparative claim. The following sentence about Ricci continues at p.252 L117 and is handled in that segment.",
    mentioned=["cand-8239", "cand-1862", "cand-0094", "cand-2154", "cand-2719"], relation=False, first=114,
    extras={"continuation_to_segment_id": NEXT_SEGMENT_ID, "continuation_to_source_line": 117})
update("st-chp9-p251-cignani-and-mazza", subject="cand-1520", object_="cand-8225",
    predicate="palazzo_manin_held_two_pictures_by_carlo_cignani",
    claim="The Manin turned to Bologna for contemporary art, including two pictures by Carlo Cignani.",
    qualification="Haskell calls Cignani the most expensive artist in Italy; that separate authorial superlative is recorded separately.",
    mentioned=["cand-1519", "cand-1520", "cand-3398", "cand-8225", "cand-0748", "cand-3461"], relation=True,
    first=110)
update("st-chp9-p251-consistent-taste-and-team", subject="cand-1519", object_=None,
    predicate="haskell_characterized_manin_taste_as_consistent_and_extravagant",
    claim="Haskell says the Manin family's taste was more consistent and more extravagant than that of other families.",
    qualification="This evaluative comparison is separate from the family's repeated employment of named professionals.",
    mentioned=["cand-1519"], relation=False, first=111)
update("st-chp9-p251-florio-country-house-verse", subject="cand-1518", object_="cand-8234",
    predicate="florio_described_manin_country_house_rooms_with_coloured_marble",
    claim="Daniele Florio's verse describes the Manin country-house rooms as adorned with smooth, shiny marbles of fine colours rather than gold friezes.",
    qualification="The speaker is identified by p.251 note 4. S0 OCR reads 'Le Crazie' in note 2; the page image reads Le Grazie. This records the quoted description, not a verified building survey.",
    mentioned=["cand-8228", "cand-1518", "cand-8234"], relation=False, first=111, speaker="Daniele Florio (identified in note 4; quoted by Haskell)",
    extras={"footnote_marker": 4, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 352, "source_line_end": 352}],
            "ocr_corrections": [{"source_line": 350, "ocr": "Le Crazie", "print": "Le Grazie", "basis": "CHP-9.pdf physical page 13"}]})
update("st-chp9-p251-gallery-works", subject="cand-8221", object_="cand-1520",
    predicate="giambologna_bronzes_reported_in_palazzo_manin_gallery",
    claim="The 1708 correspondent's account lists unidentified bronzes by Giambologna in the Palazzo Manin gallery.",
    qualification="No subjects or individual object identities are supplied; the report does not independently establish current location.",
    mentioned=["cand-8232", "cand-1520", "cand-8221", "cand-1160", "cand-8230"], relation=True,
    first=108, speaker=correspondent, extras=note3)
update("st-chp9-p251-lodovico-last-doge", subject="cand-1519", object_="cand-1517",
    predicate="haskell_linked_manin_expenditure_to_lodovico_election_as_last_doge",
    claim="Haskell links the Manin family's expenditure of money to the eventual election of the 'futile Lodovico' as the last of the Doges.",
    qualification="Preserve the author's causal interpretation and evaluative word 'futile'; this is not evidence that expenditure itself was a formal political appointment relation.",
    mentioned=["cand-1519", "cand-1517"], relation=False, first=107)
update("st-chp9-p251-manin-style-sites", subject="cand-8234", object_=None,
    predicate="manin_style_defined_by_coloured_marble_or_stucco_drapery_finish",
    claim="Haskell calls coloured marble or stucco, often cut to imitate hanging draperies, the hallmark of the Manin style.",
    qualification="The style description is separated from the buildings where Haskell says it can be found.",
    mentioned=["cand-8234"], relation=False, first=111, last=112)
update("st-chp9-p251-manin-venice-patronage", subject="cand-1519", object_="cand-2719",
    predicate="manin_family_decorated_palaces_country_houses_and_churches_in_venice_region",
    claim="Haskell says the Manin from Friuli were untiring in decorating palaces, country houses and churches in and around Venice.",
    qualification="The statement gives a broad regional activity, not named commission endpoints. Haskell's account of the family's reputation and display is separated below.",
    mentioned=["cand-1519", "cand-8237", "cand-2719", "cand-1518", "cand-1520"], relation=False, first=107,
    extras={"footnote_marker": 1, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 349, "source_line_end": 349}]})
update("st-chp9-p251-mirror-fashion-origin", subject="cand-8220", object_="cand-5317",
    predicate="mirror_fashion_reported_as_introduced_from_france_and_rooted_in_persia",
    claim="Haskell's account presents the small-room mirrors as a new fashion recently introduced from France and ultimately springing from Persia.",
    qualification="This is the source's account of a fashion's diffusion and reported origin, not independently verified provenance.",
    mentioned=["cand-8232", "cand-8220", "cand-5317", "cand-8236"], relation=False, first=108, speaker=correspondent,
    extras=note3)
update("st-chp9-p251-old-new-shared-display", subject="cand-8176", object_=None,
    predicate="old_and_new_families_shared_splendour_and_love_of_display",
    claim="Haskell says unparalleled splendour and a love of display were shared by old and new families alike.",
    qualification="The accompanying aphorism by the correspondent and Haskell's observation about reluctance to break with the past are separate claims.",
    mentioned=["cand-8176"], relation=False, first=113)
update("st-chp9-p251-palace-hangings-tapestries", subject="cand-1520", object_="cand-8219",
    predicate="palazzo_manin_walls_covered_with_hangings_and_tapestries",
    claim="The 1708 correspondent's account says the Palazzo Manin walls were covered with rich hangings and tapestries.",
    qualification="The work group represents the unspecified tapestries; the Raphael source and Old Testament subject are separate claims. No individual designs are identified.",
    mentioned=["cand-8232", "cand-1520", "cand-8219", "cand-8230"], relation=True, first=108,
    speaker=correspondent, extras=note3)
update("st-chp9-p251-passeriano-wings", subject="cand-1518", object_="cand-8218",
    predicate="passeriano_country_house_wings_adapted_from_bernini_porticos",
    claim="The approach to the Manin country house at Passeriano ran through two colonnaded wings adapted from Bernini's porticos for St Peter's.",
    qualification="The source does not identify a specific Bernini design or surviving feature. The page image confirms St Peter's as the stated model.",
    mentioned=["cand-1518", "cand-8217", "cand-8218", "cand-6960"], relation=True, first=107, last=108,
    extras={"footnote_marker": 2, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 350, "source_line_end": 350}]})

new_statements = [
    new_statement("st-chp9-p251-palace-decoration-exceeded-expectations", first=108,
        subject="cand-1520", object_=None, predicate="correspondent_said_palace_decoration_surpassed_expectations",
        claim="The correspondent said the value and splendour of the Palazzo Manin's decoration surpassed all expectations.",
        qualification="Attributed to the unidentified correspondent writing in 1708; this is a reported evaluation.",
        mentioned=["cand-8232", "cand-1520", "cand-8230"], relation=False, speaker=correspondent, extras=note3),
    new_statement("st-chp9-p251-gallery-sansovino-bronzes", first=108,
        subject="cand-8222", object_="cand-1520", predicate="sansovino_bronzes_reported_in_palazzo_manin_gallery",
        claim="The correspondent's 1708 account lists unidentified bronzes by Jacopo Sansovino in the Palazzo Manin gallery.",
        qualification="No subjects or individual object identities are supplied.",
        mentioned=["cand-8232", "cand-1520", "cand-8222", "cand-2354", "cand-8230"], relation=True,
        speaker=correspondent, extras=note3),
    new_statement("st-chp9-p251-gallery-giovanni-da-udine-pictures", first=108,
        subject="cand-8223", object_="cand-1520", predicate="giovanni_da_udine_pictures_reported_in_palazzo_manin_gallery",
        claim="The correspondent's 1708 account lists pictures by Giovanni da Udine in the Palazzo Manin gallery.",
        qualification="No titles or individual picture identities are supplied.",
        mentioned=["cand-8232", "cand-1520", "cand-8223", "cand-2667", "cand-8230"], relation=True,
        speaker=correspondent, extras=note3),
    new_statement("st-chp9-p251-gallery-andrea-del-sarto-pictures", first=108,
        subject="cand-8224", object_="cand-1520", predicate="andrea_del_sarto_pictures_reported_in_palazzo_manin_gallery",
        claim="The correspondent's 1708 account lists pictures by Andrea del Sarto in the Palazzo Manin gallery.",
        qualification="No titles or individual picture identities are supplied.",
        mentioned=["cand-8232", "cand-1520", "cand-8224", "cand-2361", "cand-8230"], relation=True,
        speaker=correspondent, extras=note3),
    new_statement("st-chp9-p251-cignani-expensive-artist", first=110,
        subject="cand-0748", object_="cand-3461", predicate="haskell_called_cignani_italys_most_expensive_artist",
        claim="Haskell calls Carlo Cignani the most expensive artist in Italy.",
        qualification="This is Haskell's comparative description, not an independently established price ranking.",
        mentioned=["cand-0748", "cand-3461"], relation=False),
    new_statement("st-chp9-p251-mazza-marble-venus", first=110,
        subject="cand-8226", object_="cand-1520", predicate="marble_venus_by_mazza_in_palazzo_manin",
        claim="The Manin palace had a marble Venus by Giuseppe Mazza, called 'the Phidias of Bologna'.",
        qualification="No date, exact title, or further object identification is supplied; preserve the quoted sobriquet as such.",
        mentioned=["cand-1520", "cand-8226", "cand-1602", "cand-3398"], relation=True),
    new_statement("st-chp9-p251-manin-employed-rossi", first=111,
        subject="cand-1519", object_="cand-2270", predicate="manin_family_employed_architect_domenico_rossi",
        claim="The Manin employed architect Domenico Rossi on many of their enterprises as part of a recurring team.",
        qualification="The source identifies his role as architect and does not enumerate the enterprises.",
        mentioned=["cand-1519", "cand-2270", "cand-0944"], relation=True),
    new_statement("st-chp9-p251-manin-employed-dorigny", first=111,
        subject="cand-1519", object_="cand-0944", predicate="manin_family_employed_painter_luigi_dorigny",
        claim="The Manin employed painter Luigi Dorigny on many of their enterprises as part of a recurring team.",
        qualification="The source identifies his role as painter and does not enumerate the enterprises.",
        mentioned=["cand-1519", "cand-2270", "cand-0944"], relation=True),
    new_statement("st-chp9-p251-manin-origin-friuli", first=107,
        subject="cand-1519", object_="cand-8237", predicate="manin_family_from_friuli",
        claim="Haskell describes the Manin as being from Friuli.",
        qualification="The source gives no more precise place of origin.", mentioned=["cand-1519", "cand-8237"], relation=False),
    new_statement("st-chp9-p251-manin-reputation-through-expenditure", first=107,
        subject="cand-1519", object_=None, predicate="manin_expenditure_won_reputation_for_nobility_of_soul",
        claim="Haskell says the Manin won a reputation for nobility of soul through expenditure of money.",
        qualification="This is Haskell's account of reputation and expenditure, not an independent moral assessment.",
        mentioned=["cand-1519"], relation=False),
    new_statement("st-chp9-p251-manin-megalomaniac-display", first=107,
        subject="cand-1519", object_=None, predicate="manin_indulged_in_megalomaniac_display",
        claim="Haskell says the Manin indulged in megalomaniac display more than any of the other 'new' families.",
        qualification="Retain the author's evaluative term and comparative scope; the comparison group is not expanded into named families.",
        mentioned=["cand-1519"], relation=False),
    new_statement("st-chp9-p251-palace-mirrors", first=108,
        subject="cand-1520", object_="cand-8220", predicate="palazzo_manin_smaller_rooms_shone_with_mirrors",
        claim="The correspondent's account says the smaller rooms of the Palazzo Manin shone with glistening mirrors.",
        qualification="The sea-in-the-Apocalypse comparison belongs to the reported description; the fashion's claimed origin is stated separately.",
        mentioned=["cand-8232", "cand-1520", "cand-8220", "cand-8230"], relation=True,
        speaker=correspondent, extras=note3),
    new_statement("st-chp9-p251-tapestries-derived-from-raphael", first=108,
        subject="cand-8219", object_="cand-2098", predicate="manin_tapestries_derived_from_raphael",
        claim="The tapestries in the Palazzo Manin were described as derived from Raphael.",
        qualification="The source identifies no specific Raphael work or tapestry design; retain this as the correspondent's reported description.",
        mentioned=["cand-8232", "cand-1520", "cand-8219", "cand-2098", "cand-8230"], relation=True,
        speaker=correspondent, extras=note3),
    new_statement("st-chp9-p251-tapestries-old-testament-subject", first=108,
        subject="cand-8219", object_="cand-7677", predicate="manin_tapestries_show_old_testament_scenes",
        claim="The tapestries were described as showing scenes from the Old Testament.",
        qualification="No individual scenes are identified; the claim is attributed to the correspondent's 1708 account.",
        mentioned=["cand-8232", "cand-1520", "cand-8219", "cand-7677", "cand-8230"], relation=True,
        speaker=correspondent, extras=note3),
    new_statement("st-chp9-p251-correspondent-richness-and-nobility", first=113,
        subject="cand-8232", object_="cand-8176", predicate="correspondent_defined_richness_as_body_of_nobility",
        claim="The same correspondent said richness was the body of nobility, whose soul was ancient lineage and virtue.",
        qualification="This is the correspondent's aphoristic judgement as quoted by Haskell, not a general definition adopted by the project.",
        mentioned=["cand-8232", "cand-8176", "cand-1520", "cand-8230"], relation=False,
        speaker=correspondent, extras=note3),
    new_statement("st-chp9-p251-reluctance-to-break-with-past", first=113,
        subject="cand-8176", object_=None, predicate="families_showed_reluctance_to_break_with_the_past",
        claim="Haskell says there was a certain reluctance to break with the past.",
        qualification="Broad authorial interpretation; the passage does not assign this attitude to a specific family.",
        mentioned=["cand-8176"], relation=False),
    new_statement("st-chp9-p251-manin-style-at-udine-cathedral", first=112,
        subject="cand-8234", object_="cand-8235", predicate="manin_style_exemplified_in_udine_cathedral_choir",
        claim="Haskell says the Manin-style finish can be found in the choir of Udine Cathedral.",
        qualification="The style is said to occur in the choir; no specific surviving surface or date is identified.",
        mentioned=["cand-8234", "cand-8235", "cand-2666"], relation=True),
    new_statement("st-chp9-p251-manin-style-at-jesuit-church", first=112,
        subject="cand-8234", object_="cand-0734", predicate="manin_style_exemplified_in_venice_jesuit_church",
        claim="Haskell says the Manin-style finish can be found in the Jesuit church in Venice.",
        qualification="The source does not specify which exact surfaces in the church carry the finish.",
        mentioned=["cand-8234", "cand-0734", "cand-2719"], relation=True),
    new_statement("st-chp9-p251-manin-style-at-palace", first=112,
        subject="cand-8234", object_="cand-1520", predicate="manin_style_exemplified_in_manin_palace",
        claim="Haskell says the Manin-style finish can be found in the family's palace.",
        qualification="The source does not identify the exact rooms or surfaces.", mentioned=["cand-8234", "cand-1520"], relation=True),
    new_statement("st-chp9-p251-manin-style-at-country-house", first=112,
        subject="cand-8234", object_="cand-1518", predicate="manin_style_exemplified_in_manin_country_house",
        claim="Haskell says the Manin-style finish can be found in the family's country house.",
        qualification="The source does not identify the exact rooms or surfaces.", mentioned=["cand-8234", "cand-1518"], relation=True),
]

for row in new_statements:
    if row["statement_id"] in statement_ids:
        raise SystemExit(f"new statement ID already exists: {row['statement_id']}")
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"new statement has missing candidate: {row['statement_id']} {candidate_id}")
    if row["original_quote"] not in "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]]):
        raise SystemExit(f"new statement quote is not reproduced by source: {row['statement_id']}")

mention_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
for row in restored_mentions:
    span = (row["segment_id"], row["start_char"], row["end_char"])
    if span in mention_spans:
        raise SystemExit(f"p.251 mention span already exists: {row['mention_id']}")
    mention_spans.add(span)
mention_rows.extend(restored_mentions)
mention_rows.extend(new_note_mentions)
statement_rows.extend(new_statements)

coverage["note"] = (
    "Printed p.251 reviewed against CHP-9.pdf physical p.13. Restored and span-checked 57 baseline page mentions; "
    "added seven exact mentions to notes L350-351, including the identified Florio title and the cited 1708 letter/publication. "
    "Reviewed 14 existing statements, classified every claim, corrected attribution/endpoints, and separated the gallery, "
    "employment, style-location, and family-display claims. L114's Ricci continuation is linked to p.252 L117. "
    "The page image supports the correction 'Le Crazie' to printed 'Le Grazie'; S0 remains unchanged."
)

final_target = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
if len(final_target) != 34 or any(row.get("qualifiers", {}).get("relation_candidate") is None for row in final_target):
    raise SystemExit(f"post-plan p.251 statement/classification check failed ({len(final_target)} rows)")
for row in final_target:
    q = row["qualifiers"]
    for candidate_id in [row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"final statement references missing candidate: {row['statement_id']} {candidate_id}")

summary = {
    "segment_id": SEGMENT_ID,
    "baseline_revision": BASELINE_REV,
    "source_segment_sha256": segment["sha256"],
    "restored_p251_mentions": len(restored_mentions),
    "added_note_mentions": len(new_note_mentions),
    "existing_statements_reviewed": len(expected_existing_ids),
    "new_atomic_statements": len(new_statements),
    "final_p251_statements": len(final_target),
    "classifications_complete": all(row["qualifiers"]["relation_candidate"] is not None for row in final_target),
    "apply": args.apply,
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
if not args.apply:
    print("Dry run only; no table files were written.")
    raise SystemExit(0)

paths = [mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, statement_rows)
write_csv_atomic(coverage_path, coverage_fields, coverage_rows)
print("Applied. Backups saved with suffix " + BACKUP_SUFFIX)
