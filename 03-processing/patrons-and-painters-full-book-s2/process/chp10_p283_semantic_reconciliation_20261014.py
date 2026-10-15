"""Resolve p.283 gallery entities and classify the open S2 statements.

Dry-run by default. Apply only when source and table fingerprints match.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
PDF = ROOT / "02-sources/01-book/CHP-10.pdf"
TABLES = ROOT / "04-knowledge/tables"
SEGMENT = "chp-10:10_CHP-10_intro:l151-165"
NEW_CANDIDATES = {"picture_gallery": "cand-12109", "lower_gallery": "cand-12110", "casts": "cand-12111", "venetian_painting": "cand-12112"}
NEW_MENTIONS = {
    "this_gallery": "m-chp10-p283-this-gallery",
    "five_room_gallery": "m-chp10-p283-five-room-gallery",
    "lower_gallery": "m-chp10-p283-lower-gallery",
    "casts": "m-chp10-p283-lower-gallery-casts",
    "venetian_painting": "m-chp10-p283-venetian-painting",
}
NEW_STATEMENTS = [
    "st-chp10-p283-lower-gallery-sculptural-casts",
    "st-chp10-p283-pellegrini-colour-assessment",
    "st-chp10-p283-van-dyck-debt-to-venetian-painting",
    "st-chp10-p283-rubens-debt-to-venetian-painting",
    "st-chp10-p283-van-dyck-effect-on-pellegrini",
    "st-chp10-p283-rubens-effect-on-pellegrini",
]
BACKUP_SUFFIX = ".bak-s2-chp10-p283-semantic-reconciliation-20261014"
EXPECTED_SHA256 = {
    SOURCE: "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    PDF: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
    TABLES / "entity-candidates.csv": "b79f48b04dc12b4ebc6293f1db8cfb19ab0a260b254e4adf90067bf8b697c602",
    TABLES / "mentions.csv": "d96e9d3ce02b5f9b3904f5c873ff7394703f5de32dc9f1a82bc82508ce5f1244",
    TABLES / "book-statements.jsonl": "07f8d2d26094e9c0aafb6e4ebdad2231dfb83d78542a12512342d58ea6b64532",
    TABLES / "s2-coverage.csv": "d0f6e819a817dc8eabc678c6c8baa7d6bc915edf4061c247f4e717b4c4907c4d",
}
SEGMENT_SHA256 = "fe70838d7bc6f4712b673c0589cccd39b21644c66c43030ce002057fc126a7c6"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)

def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(handle.name)
    tmp.replace(path)

def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(handle.name)
    tmp.replace(path)

for path, expected in EXPECTED_SHA256.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if not source_lines[152].endswith("Johann Wilhelm’s gallery. But the real importance of this gallery lay elsewhere. For it Johann Wilhelm had ‘presque vuide toute la Flandre et la Hollande’. Seventeen paintings by Van Dyck and forty by Rubens, whose ‘bizarrerie et bravure’ made a special impact and which are now among the most splendid treasures of the Alte Pinakothek in Munich, prove that for once Rapparini’s claims were not excessively exaggerated. Despite the debt that both artists owed to"):
    raise SystemExit("p.283 gallery/influence source anchor changed")
if not source_lines[158].endswith("In all the rooms were displayed bronzes and cabinets of miniatures, and below them was another gallery containing casts of the main sculptures in Florence and Rome."):
    raise SystemExit("p.283 sculpture-gallery source anchor changed")
segment_rows = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segment_rows}
if segment_by_id.get(SEGMENT, {}).get("sha256") != SEGMENT_SHA256:
    raise SystemExit("p.283 source segment hash changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates) != 12108:
    raise SystemExit("candidate sequence changed")
if any(candidate_id in candidate_by_id for candidate_id in NEW_CANDIDATES.values()):
    raise SystemExit("one or more p.283 candidates already exist")
if any(mention_id in mention_by_id for mention_id in NEW_MENTIONS.values()):
    raise SystemExit("one or more p.283 mentions already exist")
if any(statement_id in statement_by_id for statement_id in NEW_STATEMENTS):
    raise SystemExit("one or more p.283 statements already exist")

CLASSIFICATIONS = {
    "st-chp10-p283-five-room-gallery": False,
    "st-chp10-p283-lankheit-citation-locator": False,
    "st-chp10-p283-sculpture-casts-in-gallery": False,
    "st-chp10-p283-pellegrini-gallery-influence-and-style": True,
    "st-chp10-p283-venetian-influence-on-pellegrini": False,
}
if not set(CLASSIFICATIONS) <= statement_by_id.keys():
    raise SystemExit("one or more p.283 statements are missing")
for statement_id in CLASSIFICATIONS:
    row = statement_by_id[statement_id]
    if row.get("segment_id") != SEGMENT or row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit(f"target statement changed or is already classified: {statement_id}")
old_gallery_mention = mention_by_id.get("m-chp10-p283-johann_gallery")
if not old_gallery_mention or old_gallery_mention["candidate_id"] != "cand-1325" or old_gallery_mention["surface_form"] != "Johann Wilhelm’s":
    raise SystemExit("expected p.283 Johann Wilhelm/gallery overlapping mention changed")

segment_text = "\n".join(source_lines[150:165])
def span(surface: str):
    start = segment_text.find(surface)
    if start < 0 or segment_text.find(surface, start + 1) >= 0:
        raise SystemExit(f"expected unique source span changed: {surface}")
    return start, start + len(surface)

old_gallery_span = span("Johann Wilhelm’s gallery")
old_gallery_mention.update({
    "candidate_id": NEW_CANDIDATES["picture_gallery"], "surface_form": "Johann Wilhelm’s gallery",
    "start_char": str(old_gallery_span[0]), "end_char": str(old_gallery_span[1]),
    "note": "Five-room picture-gallery place associated with Johann Wilhelm; the exact building/site is not identified in this passage.",
})

new_candidate_rows = [
    {"candidate_id": "cand-12109", "index_entry_id": "", "canonical_name": "Johann Wilhelm’s five-room picture gallery described by Haskell (site unresolved, p.283)", "index_page_range": "", "suggested_type": "place", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "Haskell describes a five-room gallery and its contents, then a lower gallery containing sculpture casts. The page does not identify the exact building or site; do not infer that it is the Bensburg castle named separately on the page.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L153"},
    {"candidate_id": "cand-12110", "index_entry_id": "", "canonical_name": "Lower gallery containing casts of sculptures from Florence and Rome (site unresolved, p.283)", "index_page_range": "", "suggested_type": "place", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "Haskell says another gallery below the five-room picture gallery contained casts of principal sculptures from Florence and Rome. Its exact building/site and the represented sculptures are not identified.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L159"},
    {"candidate_id": "cand-12111", "index_entry_id": "", "canonical_name": "Unidentified casts of principal sculptures from Florence and Rome described on p.283", "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "The source identifies a group of casts in a lower gallery but gives no individual cast or original sculpture identities and no casting material.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L159"},
    {"candidate_id": "cand-12112", "index_entry_id": "", "canonical_name": "Venetian painting tradition credited by Haskell as an influence on Van Dyck and Rubens (p.283)", "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "", "detail": "Art-historical tradition, not the city of Venice or a specific painting. Haskell's statement jointly attributes a debt to this tradition to Van Dyck and Rubens.", "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L154"},
]
mention_specs = [
    ("this_gallery", "this gallery", "cand-12109", "Anaphoric reference to Johann Wilhelm’s five-room picture-gallery place."),
    ("five_room_gallery", "The gallery", "cand-12109", "The five-room picture gallery whose rooms and contents Haskell describes."),
    ("lower_gallery", "another gallery", "cand-12110", "Separate lower gallery below the five-room picture gallery."),
    ("casts", "casts of the main sculptures", "cand-12111", "Unidentified work group held in the lower gallery; no individual sculptures are identified."),
    ("venetian_painting", "Venetian painting", "cand-12112", "Artistic tradition named as the source of Van Dyck and Rubens’s debt."),
]
new_mention_rows = []
for key, surface, candidate_id, note in mention_specs:
    start, end = span(surface)
    new_mention_rows.append({"mention_id": NEW_MENTIONS[key], "segment_id": SEGMENT, "candidate_id": candidate_id, "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})

gallery_row = statement_by_id["st-chp10-p283-five-room-gallery"]
gallery_row["subject_candidate_id"] = "cand-12109"
gallery_row["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(gallery_row["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-12109", "cand-1325"]))
casts_row = statement_by_id["st-chp10-p283-sculpture-casts-in-gallery"]
casts_row["subject_candidate_id"], casts_row["object_candidate_id"] = "cand-12109", None
casts_row["predicate"] = "elector_gallery_rooms_displayed_bronzes_and_miniature_cabinets"
casts_row["qualifiers"].update({"source_line_start": 159, "source_line_end": 159, "claim": "Haskell says bronzes and cabinets of miniatures were displayed in all the rooms of the five-room picture gallery.", "qualification": "This statement covers the five-room gallery only; the lower gallery and its sculpture casts are recorded separately.", "mentioned_candidate_ids": ["cand-12109"], "relation_candidate": False})
casts_row["original_quote"] = "In all the rooms were displayed bronzes and cabinets of miniatures,"

gallery_influence = statement_by_id["st-chp10-p283-pellegrini-gallery-influence-and-style"]
gallery_influence["subject_candidate_id"], gallery_influence["object_candidate_id"] = "cand-12109", "cand-8954"
gallery_influence["predicate"] = "elector_picture_gallery_may_have_influenced_composition_and_style_of_pellegrini_canvas_series"
gallery_influence["qualifiers"].update({"claim": "Haskell says awkward composition and stylistic mixture in some canvases may reflect the impact of the Elector's varied picture gallery, especially its Flemish artists.", "qualification": "Preserve 'some' and 'may reflect' as Haskell's qualified interpretation; this does not establish the gallery as the sole cause. The colour assessment is recorded separately.", "mentioned_candidate_ids": ["cand-1325", "cand-1862", "cand-12109", "cand-8954"], "relation_candidate": True})
gallery_influence["original_quote"] = "There is a certain awkwardness about the composition of some of these and a confusion of styles that may reflect the impact on Pellegrini of the\nElector’s widely varied picture gallery and especially of the Flemish artists in it."

venetian_row = statement_by_id["st-chp10-p283-venetian-influence-on-pellegrini"]
venetian_row["subject_candidate_id"], venetian_row["object_candidate_id"] = None, "cand-3401"
venetian_row["predicate"] = "van_dyck_and_rubens_were_little_known_in_venice"
venetian_row["qualifiers"].update({"source_line_start": 154, "source_line_end": 154, "claim": "Haskell says Van Dyck and Rubens were little known in Venice.", "qualification": "The source's 'that city' refers to Venice. Their debt to Venetian painting and their effect on Pellegrini are recorded as separate relations.", "mentioned_candidate_ids": ["cand-0958", "cand-2293", "cand-3401"], "relation_candidate": False})
venetian_row["original_quote"] = "they were little known in that city"

new_statements = [
    {"statement_id": NEW_STATEMENTS[0], "segment_id": SEGMENT, "subject_candidate_id": "cand-12111", "object_candidate_id": "cand-12110", "predicate": "casts_of_principal_sculptures_from_florence_and_rome_held_in_lower_gallery", "qualifiers": {"source_line_start": 159, "source_line_end": 159, "printed_page": 283, "pdf_physical_page": 12, "claim": "Haskell says the lower gallery contained casts of the principal sculptures in Florence and Rome.", "speaker": "Haskell", "text_layer": "authorial narrative", "qualification": "The source identifies no individual casts, original sculptures, or casting material.", "mentioned_candidate_ids": ["cand-12111", "cand-12110", "cand-3397", "cand-4490"], "relation_candidate": True}, "original_quote": "below them was another gallery containing casts of the main sculptures in Florence and Rome.", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "origin": "book"},
    {"statement_id": NEW_STATEMENTS[1], "segment_id": SEGMENT, "subject_candidate_id": "cand-8954", "object_candidate_id": None, "predicate": "pellegrinis_allegorical_series_praised_for_freshness_buoyancy_and_delicate_colour", "qualifiers": {"source_line_start": 163, "source_line_end": 163, "printed_page": 283, "pdf_physical_page": 12, "claim": "Haskell praises the canvases' freshness, buoyancy, and lighthearted delicacy of colour as unmatched in Venice at that date.", "speaker": "Haskell", "text_layer": "authorial narrative", "qualification": "This remains Haskell's aesthetic comparison; it is not a claim that no similar work existed elsewhere.", "mentioned_candidate_ids": ["cand-8954", "cand-3401"], "relation_candidate": False}, "original_quote": "But they are painted with a freshness, buoyancy and lighthearted delicacy of colour that have no parallel in Venice itself at this date.", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "origin": "book"},
]
for artist_id, artist_slug, artist_name in [("cand-0958", "van-dyck", "Van Dyck"), ("cand-2293", "rubens", "Rubens")]:
    new_statements.append({"statement_id": f"st-chp10-p283-{artist_slug}-debt-to-venetian-painting", "segment_id": SEGMENT, "subject_candidate_id": artist_id, "object_candidate_id": "cand-12112", "predicate": f"{artist_slug}_owed_a_debt_to_venetian_painting", "qualifiers": {"source_line_start": 153, "source_line_end": 154, "printed_page": 283, "pdf_physical_page": 12, "claim": f"Haskell says {artist_name} owed a debt to Venetian painting.", "speaker": "Haskell", "text_layer": "authorial narrative", "qualification": "The book states that both Van Dyck and Rubens owed this debt; separate rows preserve the named artists while retaining the joint source attribution.", "mentioned_candidate_ids": ["cand-0958", "cand-2293", "cand-12112"], "relation_candidate": True}, "original_quote": "Despite the debt that both artists owed to\nVenetian painting", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "origin": "book"})
    new_statements.append({"statement_id": f"st-chp10-p283-{artist_slug}-effect-on-pellegrini", "segment_id": SEGMENT, "subject_candidate_id": artist_id, "object_candidate_id": "cand-1862", "predicate": f"{artist_slug}_had_considerable_effect_on_receptive_pellegrini", "qualifiers": {"source_line_start": 154, "source_line_end": 155, "printed_page": 283, "pdf_physical_page": 12, "claim": f"Haskell says {artist_name} had a considerable effect on the receptive Pellegrini.", "speaker": "Haskell", "text_layer": "authorial narrative", "qualification": "The source attributes the effect jointly to Van Dyck and Rubens; separate rows do not imply a relative measure for either artist.", "mentioned_candidate_ids": ["cand-0958", "cand-2293", "cand-1862"], "relation_candidate": True}, "original_quote": "their effect on the receptive\nPellegrini was considerable.", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "origin": "book"})

for statement_id, value in CLASSIFICATIONS.items():
    statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = value
all_candidate_ids = set(candidate_by_id) | set(NEW_CANDIDATES.values())
for row in [gallery_row, casts_row, gallery_influence, venetian_row, *new_statements]:
    refs = {row.get("subject_candidate_id"), row.get("object_candidate_id"), *row.get("qualifiers", {}).get("mentioned_candidate_ids", [])} - {None, ""}
    if not refs <= all_candidate_ids:
        raise SystemExit(f"unresolved candidate references in {row['statement_id']}: {sorted(refs - all_candidate_ids)}")

coverage_row = coverage_by_id.get(SEGMENT)
if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.283 coverage state changed")
coverage_row["note"] += " 2026-10-14 semantic reconciliation added separate candidates for the five-room picture gallery, the lower cast gallery, the cast work group, and the Venetian painting tradition. Corrected the gallery-place subject; split the room display from lower-gallery casts, separated the qualified gallery-influence claim from the colour judgment, and recorded the Van Dyck/Rubens relations separately while preserving Haskell's joint wording."

print(json.dumps({"source": "p.283, CHP-10.pdf physical page 12", "page_scan_sha256": EXPECTED_SHA256[PDF], "existing_statements_classified": len(CLASSIFICATIONS), "new_candidates": list(NEW_CANDIDATES.values()), "new_mentions": len(new_mention_rows), "new_statements": [row["statement_id"] for row in new_statements], "planned_totals": {"candidates": len(candidates) + len(new_candidate_rows), "mentions": len(mentions) + len(new_mention_rows), "statements": len(statements) + len(new_statements), "p283_true": sum(CLASSIFICATIONS.values()) + sum(row["qualifiers"]["relation_candidate"] for row in new_statements), "p283_false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values()) + sum(not row["qualifiers"]["relation_candidate"] for row in new_statements), "p283_unset": 0}}, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("recovery backup already exists; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    try:
        write_csv(candidate_path, candidate_fields, candidates + new_candidate_rows)
        write_csv(mention_path, mention_fields, mentions + new_mention_rows)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, coverage)
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; backups=" + ", ".join(str(path.relative_to(ROOT)) for path in backups))
