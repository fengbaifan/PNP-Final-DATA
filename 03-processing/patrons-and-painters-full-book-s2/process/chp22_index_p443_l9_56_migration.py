#!/usr/bin/env python3
"""Controlled S2 review of S0 L9-56 on the unnumbered opening index leaf."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INDEX_MD = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
INDEX_PDF = ROOT / "02-sources" / "01-book" / "CHP-22Index.pdf"
INDEX_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "A.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENTS = {
    "header": "chp-22:22_CHP-22Index:l1-1",
    "page_marker": "chp-22:22_CHP-22Index:l3-3",
    "page_content": "chp-22:22_CHP-22Index:l9-56",
    "page_continuation": "chp-22:22_CHP-22Index:l64-109",
}
INDEX_MD_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
INDEX_PDF_SHA = "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5"
INDEX_CSV_SHA = "b44d3ac13df58464fab2aaa1d1fca0a819ab03b1abcc56f466a70d543c4a1133"
SEGMENT_HASHES = {
    SEGMENTS["header"]: "45492b6435dfca8b59bf2efd50dc25e63fc088c846b29d5aefeb8d94d3fc54a9",
    SEGMENTS["page_marker"]: "1140823e47965d344d7b8f12d028795097bb1e290cde7f9a0bca82bf317542aa",
    SEGMENTS["page_content"]: "93505ccd4c69f3eb008df01bdeafb5e0de00fcd3048bb1ef596b78ad3bb9018b",
    SEGMENTS["page_continuation"]: "63c4cdd642118aa4dfbe1bd9e67b0080fbec56373118aa58de9ef56975c4c09a",
}
BACKUP_SUFFIX = ".bak-s2-chp22-index-p443-20261007"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path, encoding="utf-8-sig"):
    with path.open(encoding=encoding, newline="") as handle:
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


if (
    sha256(INDEX_MD) != INDEX_MD_SHA
    or sha256(INDEX_PDF) != INDEX_PDF_SHA
    or sha256(INDEX_CSV) != INDEX_CSV_SHA
):
    raise SystemExit("index Markdown, PDF, or A.csv changed")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
manifest = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
for segment_id, expected_hash in SEGMENT_HASHES.items():
    row = manifest.get(segment_id)
    if not row or (
        row.get("source_file"),
        row.get("sha256"),
        row.get("asset_sha256"),
    ) != (SOURCE_FILE, expected_hash, INDEX_MD_SHA):
        raise SystemExit(f"index source segment manifest changed: {segment_id}")
    content = "\n".join(source_lines[row["line_start"] - 1 : row["line_end"]])
    if hashlib.sha256(content.encode("utf-8")).hexdigest() != expected_hash:
        raise SystemExit(f"index source segment text changed: {segment_id}")

candidate_path = TABLES / "entity-candidates.csv"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_fields, coverage = read_csv(coverage_path)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = read_jsonl(TABLES / "book-statements.jsonl")
if (
    len(candidates),
    len(mentions),
    len(statements),
    len(coverage),
) != (11436, 26829, 12102, 832):
    raise SystemExit("unexpected S2 pre-state")

coverage_by_id = {row["segment_id"]: row for row in coverage}
for segment_id in SEGMENTS.values():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
        raise SystemExit(f"index segment is not queued: {segment_id}")

index_fields, index_rows = read_csv(INDEX_CSV, encoding="cp1252")
if len(index_rows) <= 66:
    raise SystemExit("A.csv does not contain the expected p.24 entry rows")
candidate_by_index_id = {
    row["index_entry_id"]: row for row in candidates if row["index_entry_id"]
}
if len(candidate_by_index_id) != 2930:
    raise SystemExit("unexpected S1 index-candidate inventory")

type_by_row = {}
for i in range(0, 9):
    type_by_row[i] = "institution"
for i in range(9, 18):
    type_by_row[i] = "person"
type_by_row[18] = "event"
for i in range(19, 33):
    type_by_row[i] = "person"
for i in range(35, 67):
    type_by_row[i] = "person"
if len(type_by_row) != 65:
    raise SystemExit("unexpected p.24 entity type count")

candidate_updates = []
for row_number, expected_type in sorted(type_by_row.items()):
    index_entry_id = f"A.csv#{row_number}"
    index_row = index_rows[row_number]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"index row has no S1 candidate: {index_entry_id}")
    if candidate["status"] != "open" or candidate["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {candidate['candidate_id']}")
    if not index_row["Main Entry"] or candidate["index_source_file"] != "A.csv":
        raise SystemExit(f"index candidate mapping mismatch: {index_entry_id}")
    candidate["suggested_type"] = expected_type
    candidate_updates.append(
        {
            "index_entry_id": index_entry_id,
            "candidate_id": candidate["candidate_id"],
            "main_entry": candidate["canonical_name"],
            "sub_entry": candidate["sub_entry"],
            "suggested_type": expected_type,
        }
    )

alias_updates = {
    33: {
        "candidate_id": "cand-2889",
        "old_reason": "索引交叉引用：see under Chigi, Fabio",
        "new_reason": "索引交叉引用：see under Chigi, Fabio；目标为 C.csv#189 / cand-0665。此别名行不另建实体候选。",
        "target_index_entry_id": "C.csv#189",
        "target_candidate_id": "cand-0665",
    },
    34: {
        "candidate_id": "cand-2890",
        "old_reason": "索引交叉引用：see under Ottoboni, Pietro",
        "new_reason": "索引交叉引用：see under Ottoboni, Pietro；目标为 O.csv#29 / cand-1794。此别名行不另建实体候选。",
        "target_index_entry_id": "O.csv#29",
        "target_candidate_id": "cand-1794",
    },
}
alias_candidate_updates = []
for row_number, update in alias_updates.items():
    index_entry_id = f"A.csv#{row_number}"
    candidate = candidate_by_index_id.get(index_entry_id)
    target = candidate_by_index_id.get(update["target_index_entry_id"])
    if not candidate or candidate["candidate_id"] != update["candidate_id"]:
        raise SystemExit(f"index cross-reference candidate mismatch: {index_entry_id}")
    if candidate["status"] != "excluded" or candidate["exclude_reason"] != update["old_reason"]:
        raise SystemExit(f"index alias exclusion changed: {candidate['candidate_id']}")
    if not target or target["candidate_id"] != update["target_candidate_id"]:
        raise SystemExit(f"index cross-reference target missing: {update['target_index_entry_id']}")
    candidate["exclude_reason"] = update["new_reason"]
    alias_candidate_updates.append(
        {
            "index_entry_id": index_entry_id,
            "candidate_id": candidate["candidate_id"],
            "excluded_alias": candidate["canonical_name"],
            "target_index_entry_id": update["target_index_entry_id"],
            "target_candidate_id": update["target_candidate_id"],
        }
    )

coverage_by_id[SEGMENTS["header"]].update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L1-1",
    note="Generated Markdown filename heading only; not printed index content and contains no index entry.",
)
coverage_by_id[SEGMENTS["page_marker"]].update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L3-3",
    note="OCR/source marker [Page 24] only; it is not printed in CHP-22Index.pdf physical p.1 and conflicts with the following visible p.444 folio. Treat as a source locator, not an index entry or factual claim.",
)
coverage_by_id[SEGMENTS["page_content"]].update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L9-56",
    note="no_semantic_content: Unnumbered opening index leaf checked against CHP-22Index.pdf physical p.1; its folio is not visible and is inferred as p.443 from the following visible p.444. The full two-column page and S1 A.csv rows 0-66 were compared across S0 L9-56 and L64-109. Classified 65 open main-entry candidates (9 institutions, 55 people, 1 event); two see-under aliases remain excluded and point to their target candidates. This row covers the first OCR segment; index locators are not book-fact claims and no mentions or statements were added.",
)

after = {
    "candidate_count": len(candidates),
    "mention_count": len(mentions),
    "statement_count": len(statements),
    "coverage_complete": sum(
        row["disposition"] == "reviewed" and row["migration_status"] == "complete"
        for row in coverage
    ),
    "coverage_queued": sum(row["disposition"] == "queued" for row in coverage),
    "coverage_excluded": sum(row["disposition"] == "excluded" for row in coverage),
    "coverage_partial": sum(
        row["disposition"] == "reviewed" and row["migration_status"] == "partial"
        for row in coverage
    ),
}
expected_after = {
    "candidate_count": 11436,
    "mention_count": 26829,
    "statement_count": 12102,
    "coverage_complete": 618,
    "coverage_queued": 91,
    "coverage_excluded": 123,
    "coverage_partial": 0,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "index_page_inferred": 443,
    "index_page_folio_visible": False,
    "s0_segments": SEGMENTS,
    "typed_index_candidates": len(candidate_updates),
    "types": {
        kind: sum(update["suggested_type"] == kind for update in candidate_updates)
        for kind in sorted({u["suggested_type"] for u in candidate_updates})
    },
    "cross_reference_aliases_enriched": len(alias_candidate_updates),
    "new_candidates": 0,
    "new_mentions": 0,
    "new_book_statements": 0,
    "candidate_updates": candidate_updates,
    "alias_targets": alias_candidate_updates,
    **after,
}
if ARGS.apply:
    table_paths = (candidate_path, coverage_path)
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in table_paths]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("a migration backup already exists; refusing to overwrite it")
    for path, backup_path in zip(table_paths, backup_paths):
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

print(json.dumps(result, ensure_ascii=False, indent=2))
