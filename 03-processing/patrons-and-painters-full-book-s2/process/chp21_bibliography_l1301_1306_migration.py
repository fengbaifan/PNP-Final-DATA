#!/usr/bin/env python3
"""Controlled S2 cross-link migration for the displaced bibliography OCR block."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-21Bibliography.pdf"
SOURCE_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
SEGMENT = "chp-21:21_CHP-21Bibliography:l1301-1306"
PREVIOUS_SEGMENT = "chp-21:21_CHP-21Bibliography:l1261-1299"
SEGMENT_SHA = "61c4adf622f6f3482eeca31e085be4d1d258c21f1dfb819470353486f18f4c57"
SOURCE_SHA = "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3"
PDF_SHA = "1c6131359d4641f6a0b6e05330a6687634a630c4aacac9c21aeacc4a1392a512"
BACKUP_SUFFIX = ".bak-s2-chp21-bibliography-l1301-1306-retry-20261007"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if sha256(SOURCE) != SOURCE_SHA or sha256(PDF) != PDF_SHA:
    raise SystemExit("bibliography Markdown or PDF changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1300:1306])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text/hash changed")

manifest = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
segment_row = manifest.get(SEGMENT)
if not segment_row or (
    segment_row.get("source_file"),
    segment_row.get("line_start"),
    segment_row.get("line_end"),
    segment_row.get("sha256"),
    segment_row.get("asset_sha256"),
) != (SOURCE_FILE, 1301, 1306, SEGMENT_SHA, SOURCE_SHA):
    raise SystemExit("source segment manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)

if (len(candidates), len(mentions), len(statements), len(coverage)) != (
    11436,
    26822,
    12095,
    832,
):
    raise SystemExit("unexpected bibliography S2 pre-state")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
mention_keys = {
    (row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"])
    for row in mentions
}
statement_by_id = {row["statement_id"]: row for row in statements}
statement_ids = set(statement_by_id)
coverage_by_id = {row["segment_id"]: row for row in coverage}
coverage_row = coverage_by_id.get(SEGMENT)
if not coverage_row or (
    coverage_row["disposition"], coverage_row["migration_status"]
) != ("queued", "pending"):
    raise SystemExit("bibliography segment is not queued")
previous_coverage = coverage_by_id.get(PREVIOUS_SEGMENT)
if not previous_coverage or (
    previous_coverage["disposition"], previous_coverage["migration_status"]
) != ("reviewed", "complete"):
    raise SystemExit("previous bibliography segment is not complete")

# Each span is displaced S0 OCR for an already-recorded page-image or bibliography
# statement. These are cross-links, not additional publication-listing assertions.
items = [
    {
        "candidate_id": "cand-11238",
        "line": 1302,
        "quote": "2 vols., 1877-8.",
        "target_statement_id": "st-chp21-bib-l87-127-entry-12",
        "kind": "bibliography_continuation",
        "printed_page": 413,
        "target_segment_id": "chp-21:21_CHP-21Bibliography:l87-127",
    },
    {
        "candidate_id": "cand-9439",
        "line": 1303,
        "quote": "2 vols., London 1834.",
        "target_statement_id": "st-chp21-bib-l129-163-entry-06",
        "kind": "bibliography_continuation",
        "printed_page": 414,
        "target_segment_id": "chp-21:21_CHP-21Bibliography:l129-163",
    },
    {
        "candidate_id": "cand-4805",
        "line": 1303,
        "quote": "- [Bellori, G. P.]: Nota delli Musei, Librerie, Gallerie e Ornamenti di statue e pitture ne’ palazzi, nelle case e ne’ giardini di Roma—appendice a Lunadoro: Relatione della corte di Roma, Roma e Venezia 1664.",
        "target_statement_id": "st-chp21-bib-l129-163-page-image-omission-01",
        "kind": "displaced_page_image_entry_transcription",
        "printed_page": 414,
        "target_segment_id": "chp-21:21_CHP-21Bibliography:l129-163",
    },
    {
        "candidate_id": "cand-11332",
        "line": 1304,
        "quote": "4 vols., Roma 1939-42.",
        "target_statement_id": "st-chp21-bib-l498-536-entry-04",
        "kind": "bibliography_continuation",
        "printed_page": 423,
        "target_segment_id": "chp-21:21_CHP-21Bibliography:l498-536",
    },
    {
        "candidate_id": "cand-11333",
        "line": 1304,
        "quote": "~ Gabrieli, Noemi: ‘Aggiunte a Sebastiano Ricci’ in Proporzioni, 1950, pp. 204-211.",
        "target_statement_id": "st-chp21-bib-l498-536-page-image-noemi-01",
        "kind": "displaced_page_image_entry_transcription",
        "printed_page": 423,
        "target_segment_id": "chp-21:21_CHP-21Bibliography:l498-536",
    },
    {
        "candidate_id": "cand-11347",
        "line": 1305,
        "quote": "3 vols., Londres 1764.",
        "target_statement_id": "st-chp21-bib-l538-575-entry-11",
        "kind": "bibliography_continuation",
        "printed_page": 424,
        "target_segment_id": "chp-21:21_CHP-21Bibliography:l538-575",
    },
    {
        "candidate_id": "cand-7696",
        "line": 1306,
        "quote": "109 vols., Venezia 1840-79.",
        "target_statement_id": "st-chp21-bib-l846-881-entry-01",
        "kind": "bibliography_continuation",
        "printed_page": 431,
        "target_segment_id": "chp-21:21_CHP-21Bibliography:l846-881",
    },
]

if len(items) != 7:
    raise SystemExit("unexpected displaced bibliography span count")

candidate_detail_replacements = {
    "cand-11238": (
        "S0 OCR omits the printed line ‘2 vols., 1877-8’",
        "S0 OCR places the printed continuation ‘2 vols., 1877-8’ at L1302; this span is now linked to the p.413 bibliography statement",
    ),
    "cand-9439": (
        "The print page supplies the continuation and corrects two OCR errors; cited contents were not independently consulted.",
        "The print page supplies the continuation and corrects two OCR errors; displaced S0 OCR at L1303 is now linked to the p.414 statement. Cited contents were not independently consulted.",
    ),
    "cand-4805": (
        "The entry is absent from S0 OCR; exact edition identity remains for S3 review.",
        "The p.414 OCR segment omits the entry, but its displaced S0 transcription at L1303 is now linked to the page-image addendum; exact edition identity remains for S3 review.",
    ),
    "cand-11332": (
        "its OCR text is displaced to L1304.",
        "its OCR text is displaced to L1304 and is now linked to the p.423 statement.",
    ),
    "cand-11333": (
        "where the separate queued segment will add the exact S0 mention.",
        "whose exact displaced S0 mention at L1304 is now linked to this page-image entry.",
    ),
    "cand-11347": (
        "When the queued L1301-1306 segment is reviewed, link that exact source span to this candidate without adding a second bibliography statement.",
        "The exact displaced S0 span at L1305 is now linked to this entry without adding a second bibliography statement.",
    ),
    "cand-7696": (
        "the OCR segment omits that continuation.",
        "the p.431 OCR segment omits it; the displaced S0 text at L1306 is now cross-linked.",
    ),
}

for candidate_id, (old_text, new_text) in candidate_detail_replacements.items():
    row = candidate_by_id.get(candidate_id)
    if not row:
        raise SystemExit(f"required candidate missing: {candidate_id}")
    if row["suggested_type"] != "archive":
        raise SystemExit(f"unexpected candidate type: {candidate_id}")
    if row["detail"].count(old_text) != 1 or new_text in row["detail"]:
        raise SystemExit(f"unexpected candidate detail pre-state: {candidate_id}")
    row["detail"] = row["detail"].replace(old_text, new_text, 1)

new_mentions = []
new_statements = []
new_spans = []
target_statement_updates = []
for index, item in enumerate(items, 1):
    candidate_id = item["candidate_id"]
    target = statement_by_id.get(item["target_statement_id"])
    if not target or (
        target.get("object_candidate_id"),
        target.get("segment_id"),
    ) != (candidate_id, item["target_segment_id"]):
        raise SystemExit(f"target bibliography statement mismatch: {item['target_statement_id']}")

    quote = item["quote"]
    if segment_text.count(quote) != 1:
        raise SystemExit(f"source span must occur exactly once: {candidate_id} L{item['line']}")
    source_line = source_lines[item["line"] - 1]
    if source_line.count(quote) != 1:
        raise SystemExit(f"source-line span must occur exactly once: {candidate_id} L{item['line']}")
    start_char = segment_text.index(quote)
    end_char = start_char + len(quote)
    mention_id = f"m-chp21-bib-l1301-1306-{index:03d}"
    statement_id = f"st-chp21-bib-l1301-1306-xref-{index:02d}"
    if mention_id in mention_ids or statement_id in statement_ids:
        raise SystemExit(f"duplicate migration ID: {mention_id} / {statement_id}")
    natural_key = (SEGMENT, candidate_id, str(start_char), str(end_char))
    if natural_key in mention_keys:
        raise SystemExit(f"duplicate mention natural key: {natural_key}")

    mention = {field: "" for field in mention_fields}
    mention.update(
        mention_id=mention_id,
        segment_id=SEGMENT,
        candidate_id=candidate_id,
        surface_form=quote,
        start_char=start_char,
        end_char=end_char,
        note="Exact displaced S0 bibliography OCR span linked to an existing bibliography statement; not an independently consulted publication.",
    )
    new_mentions.append(mention)
    mention_ids.add(mention_id)
    mention_keys.add(natural_key)
    new_spans.append((start_char, end_char))

    line_ref = f"{SEGMENT}#L{item['line']}"
    target_qualifiers = target.setdefault("qualifiers", {})
    previous_ref = target_qualifiers.get("displaced_s0_source_ref")
    if previous_ref and previous_ref != line_ref:
        raise SystemExit(f"conflicting displaced source reference: {item['target_statement_id']}")
    previous_xref = target_qualifiers.get("displaced_ocr_cross_reference_statement_id")
    if previous_xref:
        raise SystemExit(f"cross-reference already exists: {item['target_statement_id']}")
    target_qualifiers["displaced_s0_source_ref"] = line_ref
    target_qualifiers["displaced_ocr_cross_reference_statement_id"] = statement_id
    target_statement_updates.append(item["target_statement_id"])

    claim = (
        f"The displaced S0 OCR at L{item['line']} maps to existing bibliography "
        f"statement {item['target_statement_id']} for {candidate_id}."
    )
    new_statements.append(
        {
            "statement_id": statement_id,
            "segment_id": SEGMENT,
            "subject_candidate_id": None,
            "object_candidate_id": candidate_id,
            "predicate": "bibliography_displaced_ocr_cross_reference",
            "qualifiers": {
                "source_line_start": item["line"],
                "source_line_end": item["line"],
                "claim": claim,
                "speaker": "S0 OCR transcription",
                "text_layer": "displaced bibliography OCR cross-reference",
                "qualification": "This maps OCR text to an existing bibliography assertion and does not add a second publication-listing claim; the cited publication was not independently consulted.",
                "relation_candidate": False,
                "mentioned_candidate_ids": [candidate_id],
                "related_s2_statement_id": item["target_statement_id"],
                "displaced_ocr_kind": item["kind"],
                "printed_page": item["printed_page"],
                "displaced_from_segment_id": item["target_segment_id"],
            },
            "original_quote": quote,
            "origin": "book",
            "source_file": SOURCE_FILE,
        }
    )
    statement_ids.add(statement_id)

if len(new_mentions) != 7 or len(new_statements) != 7:
    raise SystemExit("unexpected mention or cross-reference statement count")
ordered_spans = sorted(new_spans)
if any(ordered_spans[i][1] > ordered_spans[i + 1][0] for i in range(len(ordered_spans) - 1)):
    raise SystemExit("displaced OCR mentions overlap")
if {item["line"] for item in items} != set(range(1302, 1307)):
    raise SystemExit("meaningful bibliography lines are not covered")

mentions.extend(new_mentions)
statements.extend(new_statements)
coverage_row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1302-1306",
    note="S0 Footnotes block contains seven displaced OCR spans for existing p.413–431 bibliography entries; exact mentions and cross-links added without duplicating publication assertions. L1301 is a structural header.",
)

after = {
    "candidate_count": len(candidates),
    "mention_count": len(mentions),
    "statement_count": len(statements),
    "coverage_complete": sum(row["disposition"] == "reviewed" and row["migration_status"] == "complete" for row in coverage),
    "coverage_queued": sum(row["disposition"] == "queued" for row in coverage),
    "coverage_excluded": sum(row["disposition"] == "excluded" for row in coverage),
    "coverage_partial": sum(row["disposition"] == "reviewed" and row["migration_status"] == "partial" for row in coverage),
}
expected_after = {
    "candidate_count": 11436,
    "mention_count": 26829,
    "statement_count": 12102,
    "coverage_complete": 617,
    "coverage_queued": 94,
    "coverage_excluded": 121,
    "coverage_partial": 0,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment_id": SEGMENT,
    "candidate_detail_updates": len(candidate_detail_replacements),
    "existing_statements_cross_linked": len(target_statement_updates),
    "new_publication_candidates": 0,
    "new_publication_assertions": 0,
    "new_mentions": len(new_mentions),
    "new_cross_reference_statements": len(new_statements),
    "cross_links": [
        {
            "line": item["line"],
            "candidate_id": item["candidate_id"],
            "target_statement_id": item["target_statement_id"],
            "mention_id": f"m-chp21-bib-l1301-1306-{index:03d}",
            "cross_reference_statement_id": f"st-chp21-bib-l1301-1306-xref-{index:02d}",
            "surface_form": item["quote"],
        }
        for index, item in enumerate(items, 1)
    ],
    **after,
}

if ARGS.apply:
    table_paths = (candidate_path, mention_path, statement_path, coverage_path)
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in table_paths]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("a migration backup already exists; refusing to overwrite it")
    for path, backup_path in zip(table_paths, backup_paths):
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

print(json.dumps(result, ensure_ascii=False, indent=2))
