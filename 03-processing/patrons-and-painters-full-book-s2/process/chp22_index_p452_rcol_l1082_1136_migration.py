#!/usr/bin/env python3
"""Classify S1 index candidates in the right column of printed p.452."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INDEX_MD = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
INDEX_PDF = ROOT / "02-sources" / "01-book" / "CHP-22Index.pdf"
INDEX_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "C.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l1082-1136"
SEGMENT_SHA = "aa5a0600d15753ff77f7b3677a373d7e016297a65b8aa9bc2367129bb21c1641"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p452-rcol-l1082-1136-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_CSV: "7aa977632a7a7cdaff12ea4925a595a89b42cf168314bffde18e0b39c5b45696",
    TABLES / "entity-candidates.csv": "a5bdf14e016085ac4353af6a93da07a1f8b34634da5df60ff15de823fa9a43db",
    TABLES / "s2-coverage.csv": "9f2100067976b55c341defaa6f917a90454c7c69d0fed86d259ac6ef5ba8d008",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path, encoding="utf-8-sig"):
    with path.open(encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


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


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
segment = manifest.get(SEGMENT_ID)
if not segment or (
    segment.get("source_file"),
    segment.get("line_start"),
    segment.get("line_end"),
    segment.get("sha256"),
    segment.get("asset_sha256"),
) != (SOURCE_FILE, 1082, 1136, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")
segment_text = "\n".join(source_lines[1081:1136])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")
if "AND PAINTERS" not in source_lines[1081]:
    raise SystemExit("first source line no longer contains the p.452 running header")

candidate_path = TABLES / "entity-candidates.csv"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_fields, coverage = read_csv(coverage_path)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(candidates), len(coverage), len(mentions), len(statements)) != (11436, 832, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

coverage_by_id = {row["segment_id"]: row for row in coverage}
row = coverage_by_id.get(SEGMENT_ID)
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1024-1024")
previous_column = coverage_by_id.get("chp-22:22_CHP-22Index:l1026-1080")
if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.452 generated page marker is not complete")
if not previous_column or (previous_column["disposition"], previous_column["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.452 left column is not complete")

index_rows = read_csv(INDEX_CSV, encoding="cp1252")[1]
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}

# Subentries inherit the main headword unless the entry and S2 context identify a distinct object.
work_rows = {380, 381, 383, 384, 385, 390, *range(408, 421)}
family_rows = {377, 378, 393}
cross_references = {
    394: ("cand-2899", "Berrettini, Pietro"),
    397: ("cand-2900", "Borgognone, Giacomo and Guglielmo"),
    398: ("cand-2901", "Borgognone, Giacomo and Guglielmo"),
    401: ("cand-2902", "Bassi, Francesco"),
}
typed_before = {407: ("cand-0873", "person")}
type_pending = {
    388: (
        "cand-0858",
        "Correr's heterogeneous collections are an explicit S2 object, but the current taxonomy has no collection type.",
    )
}
name_overrides = {402: ("Crequi, Duc de", "Créqui, Duc de")}
candidate_updates = []
name_updates = []
type_counts = Counter()
retained = {}
unresolved = {}
excluded = {}

for index_row in range(372, 421):
    index_entry_id = f"C.csv#{index_row}"
    source_row = index_rows[index_row]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")

    old_name, new_name = name_overrides.get(index_row, (source_row["Main Entry"], source_row["Main Entry"]))
    if candidate["canonical_name"] != old_name:
        raise SystemExit(f"unexpected candidate name: {index_entry_id}: {candidate['canonical_name']}")
    if source_row["Main Entry"] != (old_name if index_row not in name_overrides else "Crequi, Duc de"):
        raise SystemExit(f"S1 source mapping changed: {index_entry_id}")

    if index_row in cross_references:
        expected_id, target = cross_references[index_row]
        if (
            candidate["candidate_id"] != expected_id
            or candidate["status"] != "excluded"
            or candidate["suggested_type"]
            or target not in candidate["exclude_reason"]
        ):
            raise SystemExit(f"existing see-under alias changed: {index_entry_id}")
        excluded[index_entry_id] = expected_id
        continue

    if candidate["status"] != "open":
        raise SystemExit(f"unexpected candidate status: {candidate['candidate_id']}")

    if index_row in typed_before:
        expected_id, expected_type = typed_before[index_row]
        if candidate["candidate_id"] != expected_id or candidate["suggested_type"] != expected_type:
            raise SystemExit(f"pre-existing candidate classification changed: {index_entry_id}")
        retained[index_entry_id] = {"candidate_id": expected_id, "suggested_type": expected_type}
        continue

    if index_row in type_pending:
        expected_id, _reason = type_pending[index_row]
        if candidate["candidate_id"] != expected_id or candidate["suggested_type"]:
            raise SystemExit(f"type-pending collection candidate changed: {index_entry_id}")
        unresolved[index_entry_id] = {"candidate_id": expected_id, "reason": _reason}
        continue

    if candidate["suggested_type"]:
        raise SystemExit(f"unexpected pre-existing type: {candidate['candidate_id']}")

    if index_row in name_overrides:
        candidate["canonical_name"] = new_name
        name_updates.append(
            {"index_entry_id": index_entry_id, "candidate_id": candidate["candidate_id"], "from": old_name, "to": new_name}
        )

    suggested_type = "work" if index_row in work_rows else "family" if index_row in family_rows else "person"
    candidate["suggested_type"] = suggested_type
    type_counts[suggested_type] += 1
    candidate_updates.append(
        {
            "index_entry_id": index_entry_id,
            "candidate_id": candidate["candidate_id"],
            "canonical_name": candidate["canonical_name"],
            "sub_entry": candidate["sub_entry"],
            "suggested_type": suggested_type,
        }
    )

expected_types = Counter({"person": 21, "work": 19, "family": 3})
if len(candidate_updates) != 43 or type_counts != expected_types:
    raise SystemExit(f"unexpected p.452 right-column type assignments: {type_counts}")
if len(name_updates) != 1 or name_updates[0]["to"] != "Créqui, Duc de":
    raise SystemExit(f"unexpected name corrections: {name_updates}")
if set(excluded) != {f"C.csv#{row}" for row in cross_references}:
    raise SystemExit("p.452 see-under exclusions do not match the expected rows")
if set(unresolved) != {"C.csv#388"} or set(retained) != {"C.csv#407"}:
    raise SystemExit("unexpected unresolved or pretyped candidate mapping")

row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1082-1136",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.10 visibly prints p.452; S0 L1082 is the "
        "running header and C.csv#372-420 covers 49 right-column rows on L1083-1136. Four existing see-under aliases "
        "C#394, C#397, C#398 and C#401 remain excluded; 43 open candidates are typed as 21 person, 19 work and 3 family, "
        "while existing C#407 cand-0873 remains person. Corradini's Schulenburg statue and Virginity, three Correggio "
        "paintings, the Longhi paintings/drawings topic (supported by existing S2 work groups cand-10712 and cand-10714), "
        "and thirteen titled Crespi works are typed work. Corner/Corsini family entries remain distinct from people. "
        "C#388 cand-0858 ('collections') remains type-pending: S2 identifies Correr's heterogeneous collection, but the "
        "taxonomy has no faithful collection type; it is not forced into person, place, institution or term. Crequi is "
        "corrected to printed 'Créqui' in the candidate only; source Markdown, PDF and C.csv remain unchanged. Index "
        "locators add no mentions, book statements or relations."
    ),
)

after = {
    "candidate_count": len(candidates),
    "mention_count": len(mentions),
    "statement_count": len(statements),
    "coverage_complete": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "complete"
        for item in coverage
    ),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "partial"
        for item in coverage
    ),
    "open_index_untyped": sum(
        bool(item["index_entry_id"])
        and item["status"] == "open"
        and not item["suggested_type"]
        for item in candidates
    ),
}
expected_after = {
    "candidate_count": 11436,
    "mention_count": 26829,
    "statement_count": 12102,
    "coverage_complete": 635,
    "coverage_queued": 65,
    "coverage_excluded": 132,
    "coverage_partial": 0,
    "open_index_untyped": 1973,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 452,
    "pdf_physical_page": 10,
    "index_rows_reviewed": 49,
    "candidate_type_changes": len(candidate_updates),
    "name_corrections": name_updates,
    "types": dict(type_counts),
    "pre-existing_types_retained": retained,
    "type_pending": unresolved,
    "see_under_exclusions_retained": excluded,
    "new_candidates": 0,
    "new_mentions": 0,
    "new_book_statements": 0,
    **after,
}
if ARGS.apply:
    table_paths = (candidate_path, coverage_path)
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in table_paths]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("a migration backup already exists; refusing to overwrite it")
    for path, backup in zip(table_paths, backup_paths):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

print(json.dumps(result, ensure_ascii=False, indent=2))
