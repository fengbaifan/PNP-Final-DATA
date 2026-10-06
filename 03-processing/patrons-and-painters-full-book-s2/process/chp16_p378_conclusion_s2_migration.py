"""Controlled S2 migration for chapter 16 p.378's concluding paragraph."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-16.pdf"
SOURCE_SHA = "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff"
PDF_SHA = "6bfb3e331f0ac2421d31279f97b08b17486f0e2c32451a10a6798cf31424af5f"
SEGMENT = "chp-16:16_CHP-16_intro:l66-67"
PREVIOUS_STATEMENT = "st-chp16-p377-haskell-generalizes-dealers-collections-and-patronage"
BACKUP_SUFFIX = ".bak-s2-chp16-p378-conclusion-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 16 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-16 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = {
    66: "[Page 378]",
    67: "They earned their livings by pandering to the international demand for old masters",
}
for line_number, fragment in required.items():
    if fragment.casefold() not in source_lines[line_number - 1].casefold():
        raise SystemExit(f"required source text changed at L{line_number}: {fragment}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

if SEGMENT not in coverage_by_id or coverage_by_id[SEGMENT]["disposition"] != "queued" or coverage_by_id[SEGMENT]["migration_status"] != "pending":
    raise SystemExit("p.378 S2 coverage preconditions changed")
if any(row["segment_id"] == SEGMENT for row in mentions):
    raise SystemExit("p.378 segment already has mention rows")
if any(row.get("statement_id", "").startswith("st-chp16-p378-") for row in statements):
    raise SystemExit("p.378 statements already exist")
if any(cid not in candidate_by_id for cid in ("cand-0126", "cand-2367", "cand-1387", "cand-2764", "cand-2643", "cand-2534", "cand-0622", "cand-3462", "cand-4288", "cand-8013")):
    raise SystemExit("one or more chapter-16 referent/term candidates are missing")
if "cand-10673" in candidate_by_id:
    raise SystemExit("p.378 Venetian-tradition candidate ID already exists")
previous = statement_by_id.get(PREVIOUS_STATEMENT)
if not previous or previous["segment_id"] != "chp-16:16_CHP-16_intro:l48-64":
    raise SystemExit("p.377 group-level synthesis statement is missing")
previous_q = previous["qualifiers"]
if previous_q.get("source_line_start") != 59 or "group-level interpretation" not in previous_q.get("qualification", ""):
    raise SystemExit("p.377 statement no longer matches the expected group-level claim")
if previous_q.get("cross_reference_statement_ids") or previous_q.get("cross_reference_segments"):
    raise SystemExit("p.377 statement already has cross-reference fields; review before updating")

line_start, line_end = 66, 67
segment_lines = {number: source_lines[number - 1] for number in range(line_start, line_end + 1)}
segment_text = "\n".join(segment_lines.values())
line_offsets = {66: 0, 67: len(source_lines[65]) + 1}

planned_mentions = []
mention_counter = 0


def add_mention(candidate_id, surface, occurrence, note):
    global mention_counter
    positions = []
    search_from = 0
    while True:
        position = segment_text.find(surface, search_from)
        if position < 0:
            break
        positions.append(position)
        search_from = position + 1
    if occurrence >= len(positions):
        raise SystemExit(f"source surface not found: {surface!r}, occurrence {occurrence + 1}")
    start = positions[occurrence]
    end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions if row["segment_id"] == SEGMENT]
    if any(start < other_end and other_start < end for other_start, other_end in occupied):
        raise SystemExit(f"duplicate or overlapping mention span: {surface!r}")
    mention_counter += 1
    planned_mentions.append({
        "mention_id": f"m-chp16-p378-conclusion-{mention_counter:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })


group_note = (
    "Collective anaphor to the men synthesized in p.377 L59: Sasso, della Lena, Vianello, "
    "Toninotto, Swajer, and Celotti. The page-378 Art dealers index candidate is used as a "
    "category locator, not as a claim that every referent held the same dealer role."
)
venetian_tradition = {
    "candidate_id": "cand-10673", "index_entry_id": "",
    "canonical_name": "Venetian tradition as invoked in Haskell's p.378 conclusion",
    "index_page_range": "", "suggested_type": "term", "status": "open",
    "index_source_file": "", "sub_entry": "",
    "detail": "Haskell's retrospective concept of the Venetian tradition; kept separate from the chapter-8 Venetian tradition candidate so S3 can assess cross-context identity.",
    "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT}#L67",
}
candidates.append(venetian_tradition)
candidate_by_id["cand-10673"] = venetian_tradition
add_mention("cand-0126", "They", 0, group_note)
add_mention("cand-0126", "they", 0, group_note)
add_mention("cand-0126", "they", 1, group_note)
add_mention("cand-3462", "Europe", 0, "Geographic span in Haskell's account of the change in taste.")
add_mention("cand-4288", "old masters", 0, "Broad art-historical category; reuses the existing term candidate.")
add_mention("cand-10673", "Venetian tradition", 0, "Aesthetic-historical concept in the p.378 retrospective; kept separate from the chapter-8 candidate for S3 identity review.")

group_members = ["cand-2367", "cand-1387", "cand-2764", "cand-2643", "cand-2534", "cand-0622"]
group_context = {
    "referent_statement_ids": [PREVIOUS_STATEMENT],
    "referent_candidate_ids": group_members,
    "coreference_note": "The plural pronouns continue Haskell's 'all these men' synthesis at p.377 L59. They are retained as a group-level authorial generalization; individual biographies or collections are not inferred from the pronoun alone.",
}
quote = source_lines[66]
statements.extend([
    {
        "statement_id": "st-chp16-p378-group-livelihood-and-old-masters-demand",
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": None,
        "predicate": "group_earned_livings_by_pandering_to_international_demand_for_old_masters",
        "qualifiers": {
            "source_line_start": 67, "source_line_end": 67,
            "printed_page": 378, "pdf_physical_page": 6,
            "claim": "Haskell says the men discussed collectively earned their living by pandering to international demand for old masters.",
            "speaker": "Haskell", "text_layer": "authorial synthesis",
            "qualification": "The source's evaluative verb 'pandering' is retained; no named market, buyer, or individual transaction is supplied.",
            "mentioned_candidate_ids": group_members + ["cand-0126", "cand-4288"],
            **group_context,
        },
        "original_quote": quote, "origin": "book",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
    },
    {
        "statement_id": "st-chp16-p378-group-collected-artists-affected-by-taste-change",
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": None,
        "predicate": "group_assembled_pictures_by_artists_affected_by_european_change_in_taste",
        "qualifiers": {
            "source_line_start": 67, "source_line_end": 67,
            "printed_page": 378, "pdf_physical_page": 6,
            "claim": "Haskell says the men themselves assembled pictures by artists who were victims of a change in taste across Europe during the second half of the eighteenth century.",
            "speaker": "Haskell", "text_layer": "authorial synthesis",
            "qualification": "The passage does not name these artists or identify individual works; 'victims' records Haskell's characterization.",
            "mentioned_candidate_ids": group_members + ["cand-0126", "cand-3462"],
            **group_context,
        },
        "original_quote": quote, "origin": "book",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
    },
    {
        "statement_id": "st-chp16-p378-group-retrospective-venetian-tradition",
        "segment_id": SEGMENT,
        "subject_candidate_id": None,
        "object_candidate_id": "cand-10673",
        "predicate": "retrospectively_seen_as_guardians_of_venetian_tradition_after_change_in_taste",
        "qualifiers": {
            "source_line_start": 67, "source_line_end": 67,
            "printed_page": 378, "pdf_physical_page": 6,
            "claim": "Haskell says that time effected a remarkable revolution and that the men now appear to readers as the true guardians of the Venetian tradition.",
            "speaker": "Haskell", "text_layer": "authorial synthesis",
            "qualification": "'Guardians' is Haskell's retrospective evaluative metaphor, not an institutional role or a verified collective identity.",
            "mentioned_candidate_ids": group_members + ["cand-0126", "cand-10673"],
            **group_context,
        },
        "original_quote": quote, "origin": "book",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
    },
])

previous_q["cross_reference_segments"] = [SEGMENT]
previous_q["cross_reference_statement_ids"] = [
    "st-chp16-p378-group-livelihood-and-old-masters-demand",
    "st-chp16-p378-group-collected-artists-affected-by-taste-change",
    "st-chp16-p378-group-retrospective-venetian-tradition",
]
previous_q["cross_reference_text"] = "P.378 L67 continues the group-level synthesis about the same men, their trade and collecting, and Haskell's retrospective assessment."
coverage_by_id = {row["segment_id"]: row for row in coverage}
coverage_by_id[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L66-67",
    "note": "P.378's concluding paragraph is migrated; plural anaphora is linked to the p.377 group-level synthesis and its named antecedents.",
})

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp16-p378-")]
if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": 1,
        "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
        "completed_segments": [SEGMENT],
        "updated_statement": PREVIOUS_STATEMENT,
        "referent_candidate_ids": group_members,
        "mention_spans": [{"candidate_id": row["candidate_id"], "surface_form": row["surface_form"], "start_char": row["start_char"], "end_char": row["end_char"]} for row in planned_mentions],
        "new_statement_ids": new_statement_ids,
        "new_candidate_ids": ["cand-10673"],
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
mentions.extend(planned_mentions)
write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps({
    "mode": "applied", "new_candidates": 1,
    "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
    "completed_segments": [SEGMENT],
    "updated_statement": PREVIOUS_STATEMENT,
    "backups": [path.name + BACKUP_SUFFIX for path in (candidate_path, mention_path, statement_path, coverage_path)],
}, ensure_ascii=False))
