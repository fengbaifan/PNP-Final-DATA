#!/usr/bin/env python3
"""Controlled migration of printed p.410 footnotes 1-5; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP = ".bak-s2-chp20-notes-p410-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
ARGS = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered PDF changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)
if (len(candidates), len(mentions), len(statements), len(coverage)) != (11190, 25911, 11223, 832):
    raise SystemExit("unexpected S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if NOTES not in coverage_by_id:
    raise SystemExit("postscript note segment missing")
note_coverage = coverage_by_id[NOTES]
if (note_coverage["disposition"], note_coverage["migration_status"], note_coverage["source_line_ranges"]) != (
    "reviewed", "partial", "L212-275"
):
    raise SystemExit(f"unexpected annotation coverage: {note_coverage}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
note_text = "\n".join(source_lines[210:280])
offsets = {}
offset = 0
for line_number in range(211, 281):
    offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

candidate_specs = [
    (
        "cand-11212",
        "Previtali 1964, pp. 153-158 (p.410 note 1; title pending bibliography reconciliation)",
        "archive",
        276,
        "The citation identifies a 1964 work and pages 153-158, but its title is not stated. Keep distinct from the unresolved p.301 short citation until bibliography reconciliation.",
    ),
    (
        "cand-11213",
        "Haskell 1967 (p.410 note 4; title pending bibliography reconciliation)",
        "archive",
        279,
        "Short-form citation to a Haskell 1967 work. The title is not stated, and more than one bibliography match may exist; defer identity alignment.",
    ),
]
natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
    for row in candidates
}
new_candidates = []
for candidate_id, name, kind, line_number, detail in candidate_specs:
    key = (name.strip().casefold(), kind.casefold())
    if candidate_id in candidate_by_id or key in natural_keys:
        raise SystemExit(f"candidate collision: {candidate_id} {name}")
    row = {field: "" for field in candidate_fields}
    row.update(
        candidate_id=candidate_id,
        canonical_name=name,
        suggested_type=kind,
        status="open",
        detail=detail,
        candidate_origin="body-mention",
        candidate_source_ref=f"{NOTES}#L{line_number}",
    )
    new_candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

body_links = {
    1: ["st-chp20-p410-sasso-scholarly-associations"],
    2: ["st-chp20-p410-lloyd-venezia-pittrice-project"],
    3: ["st-chp20-p410-olivato-sasso-article"],
    4: [
        "st-chp20-p410-della-lena-treatise-authorship",
        "st-chp20-p410-della-lena-treatise-content",
        "st-chp20-p410-della-lena-painter-appreciations",
    ],
    5: ["st-chp20-p410-fontana-manfrin-tobacco-article"],
}

note_specs = [
    (
        "st-chp20-p410-n01-citation", 1, 276, "Previtali, 1964, pp. 153-8.", "cand-11212",
        ["cand-9508"],
        "Cites Previtali's 1964 publication at pages 153-158; the work title is not given.",
        [],
    ),
    (
        "st-chp20-p410-n02-citation", 2, 277, "Art and its images, pp. 75-6.", "cand-11150",
        [],
        "Cites Art and its Images at pages 75-76.",
        [],
    ),
    (
        "st-chp20-p410-n03-citation", 3, 278, "Olivato, 1974.", "cand-11151",
        ["cand-11118"],
        "Cites Loredana Olivato's 1974 article on Giuseppe Maria Sasso; its title remains unidentified.",
        [],
    ),
    (
        "st-chp20-p410-n04-citation", 4, 279, "Haskell, 1967.", "cand-11213",
        ["cand-9423"],
        "Cites an unidentified Haskell publication from 1967; exact bibliography match is deferred.",
        [],
    ),
    (
        "st-chp20-p410-n05-citation", 5, 280, "Fontana.", "cand-11155",
        ["cand-11154"],
        "Cites Vincenzo Fontana's article on Manfrin's tobacco manufacture; its title is not stated.",
        [{"source_line": 280, "ocr": "6 Fontana", "print": "5 Fontana", "basis": "CHP-20Postscript.pdf physical page 19 image"}],
    ),
]

new_mentions = []
new_statements = []
existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}


def add_mention(line_number, surface, candidate_id, marker, role, within=None):
    line = source_lines[line_number - 1]
    container = line
    base = 0
    if within is not None:
        base = line.find(within)
        if base < 0 or line.find(within, base + 1) >= 0:
            raise SystemExit(f"ambiguous mention container L{line_number}: {within}")
        container = within
    index = container.find(surface)
    if index < 0 or container.find(surface, index + 1) >= 0:
        raise SystemExit(f"missing/ambiguous mention L{line_number}: {surface}")
    start = offsets[line_number] + base + index
    end = start + len(surface)
    if note_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch L{line_number}: {surface}")
    key = (NOTES, candidate_id, str(start), str(end))
    if key in existing_mention_keys or any(
        (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"])) == key
        for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention L{line_number}: {surface}")
    row = {field: "" for field in mention_fields}
    row.update(
        mention_id=f"m-s2-chp20-notes-p410-{len(new_mentions) + 1:03d}",
        segment_id=NOTES,
        candidate_id=candidate_id,
        surface_form=surface,
        start_char=start,
        end_char=end,
        note=f"Printed p.410 footnote {marker} {role}; cited work not independently consulted.",
    )
    new_mentions.append(row)


for spec in [
    (276, "Previtali, 1964, pp. 153-8", "cand-11212", 1, "publication citation and locator", None),
    (276, "Previtali", "cand-9508", 1, "surname-only author mention", "Previtali, 1964, pp. 153-8"),
    (277, "Art and its images", "cand-11150", 2, "publication citation", None),
    (278, "Olivato, 1974", "cand-11151", 3, "publication citation", None),
    (278, "Olivato", "cand-11118", 3, "surname-only author mention", "Olivato, 1974"),
    (279, "Haskell, 1967", "cand-11213", 4, "publication citation", None),
    (279, "Haskell", "cand-9423", 4, "surname-only author mention", "Haskell, 1967"),
    (280, "Fontana", "cand-11155", 5, "surname-only publication citation", None),
]:
    add_mention(*spec)

for statement_id, marker, line_number, quote, archive_id, related_ids, claim, corrections in note_specs:
    if statement_id in statement_by_id:
        raise SystemExit(f"statement exists: {statement_id}")
    if quote not in source_lines[line_number - 1]:
        raise SystemExit(f"source quote mismatch L{line_number}: {quote}")
    if archive_id not in candidate_by_id or candidate_by_id[archive_id]["suggested_type"] != "archive":
        raise SystemExit(f"archive candidate missing: {archive_id}")
    for candidate_id in related_ids:
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"related candidate missing: {candidate_id}")
    for body_id in body_links[marker]:
        body = statement_by_id.get(body_id)
        if body is None:
            raise SystemExit(f"body statement missing: {body_id}")
        qualifiers = body.get("qualifiers", {})
        refs = [
            ref for ref in qualifiers.get("footnote_refs", [])
            if isinstance(ref, dict) and ref.get("marker") == marker and ref.get("segment_id") == NOTES
        ]
        if len(refs) != 1 or refs[0].get("source_line") != line_number or qualifiers.get("footnote_text_pending") is not True:
            raise SystemExit(f"body link changed marker {marker}: {body_id}")
    mentioned_ids = list(dict.fromkeys([archive_id, *related_ids]))
    qualifiers = {
        "source_line_start": line_number,
        "source_line_end": line_number,
        "printed_page": 410,
        "pdf_physical_page": 19,
        "footnote_marker": marker,
        "claim": claim,
        "speaker": "Haskell's footnote apparatus",
        "text_layer": "bibliographic citation",
        "qualification": "Short citations only; titles are not inferred, and cited works were not independently consulted.",
        "mentioned_candidate_ids": mentioned_ids,
        "relation_candidate": False,
        "cited_material_not_independently_consulted": True,
    }
    if corrections:
        qualifiers["ocr_corrections"] = corrections
    statement = {
        "statement_id": statement_id,
        "segment_id": NOTES,
        "subject_candidate_id": None,
        "object_candidate_id": archive_id,
        "predicate": "footnote_cites_publication",
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
    }
    new_statements.append(statement)
    statement_by_id[statement_id] = statement

for marker, body_ids in body_links.items():
    citation_ids = [spec[0] for spec in note_specs if spec[1] == marker]
    for body_id in body_ids:
        qualifiers = statement_by_id[body_id]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        linked_ids = qualifiers.setdefault("footnote_statement_ids", [])
        for citation_id in citation_ids:
            if citation_id not in linked_ids:
                linked_ids.append(citation_id)

old_tail = "P.410 onward L276-280 remains queued."
if note_coverage["note"].count(old_tail) != 1:
    raise SystemExit("unexpected coverage note tail")
note_coverage["source_line_ranges"] = "L212-280"
note_coverage["migration_status"] = "complete"
note_coverage["note"] = note_coverage["note"].replace(
    old_tail,
    "P.410 notes 1-5 (L276-280) are reviewed, transcribed, and linked to body statements. Printed note 5 is Fontana; S0 OCR read 6, and the correction is recorded in its citation statement without changing S0.",
)

page_spans = sorted(
    (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
    for row in [*mentions, *new_mentions]
    if row["segment_id"] == NOTES
)
for index, left in enumerate(page_spans):
    for right in page_spans[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"overlapping note mentions: {left[2]} / {right[2]}")

paths = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP) for path in paths]
if ARGS.apply:
    present = [path.exists() for path in backups]
    if any(present) and not all(present):
        raise SystemExit("incomplete recovery backup set exists")
    if all(present):
        if any(hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(backup.read_bytes()).digest() for path, backup in zip(paths, backups)):
            raise SystemExit("existing backups differ from current pre-state")
    else:
        for path, backup in zip(paths, backups):
            shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, [*candidates, *new_candidates])
    write_csv(mention_path, mention_fields, [*mentions, *new_mentions])
    write_jsonl(statement_path, [*statements, *new_statements])
    write_csv(coverage_path, coverage_fields, coverage)
    print(
        f"applied p.410 notes 1-5: candidates +{len(new_candidates)}, mentions +{len(new_mentions)}, "
        f"citation statements +{len(new_statements)}; body statements linked {sum(map(len, body_links.values()))}"
    )
    print(f"recovery suffix {BACKUP}")
else:
    print(json.dumps({
        "mode": "dry-run",
        "page": 410,
        "notes": "1-5; printed note 5 OCR-corrected from 6",
        "candidates_added": len(new_candidates),
        "mentions_added": len(new_mentions),
        "citation_statements_added": len(new_statements),
        "body_statements_linked": sum(map(len, body_links.values())),
        "coverage_after": "reviewed/complete through L280",
        "unresolved_bibliographic_matches": ["Previtali 1964", "Haskell 1967"],
    }, ensure_ascii=False, indent=2))
