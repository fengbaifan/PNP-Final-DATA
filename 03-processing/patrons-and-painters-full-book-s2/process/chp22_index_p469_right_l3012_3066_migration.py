#!/usr/bin/env python3
"""Classify p.469 right-column index seeds and close its S2 segment."""

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
S_INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "S.csv"
SEGMENT_ID = "chp-22:22_CHP-22Index:l3012-3066"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p469-right-l3012-3066-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/S.csv": "a73a199a0d4e2c01dfe12fd77e562e30298edb2357c54b341da887bad306393f",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    "02-sources/02-Markdown/09_CHP-9_sec_ii.md": "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    "02-sources/02-Markdown/19_CHP-19Appendix.md": "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "a8c07b18d7e987d1b1567bce2c74d7ee717a9231f8e43db64f5d4b3e5d5cac2d",
    "04-knowledge/tables/s2-coverage.csv": "73021f48baedf2bdafa7601a922ddfe570b5a016ec7b4fc6cbd2c9edaa0393c7",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}
SEGMENT_SHA256 = "b133adf261d17a48bb7305d644605c03b35faa495e9539471c61124ccb74666b"

TYPE_BY_ENTRY = {
    **{f"S.csv#{i}": "person" for i in (
        127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138,
        143, 144, 145, 148, 152, 163, 168,
    )},
    **{f"S.csv#{i}": "event" for i in (
        142, 149, 150, 154, 155, 156, 157, 158, 159, 160, 161, 162, 164,
    )},
    **{f"S.csv#{i}": "archive" for i in (139, 140, 141, 147, 165)},
    "S.csv#146": "place",
    "S.csv#153": "place",
    "S.csv#166": "term",
    "S.csv#167": "family",
}
EXPECTED_PRETYPES = {
    "S.csv#136": "person",
    "S.csv#160": "person",
    "S.csv#165": "person",
}
UNRESOLVED_ENTRY = "S.csv#151"
EXPECTED_CORRECTIONS = {
    "S.csv#129": {
        "candidate_id": "cand-2440",
        "field": "index_page_range",
        "before": "236n, 252, 264, 266, 290n, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 318, 320, 322, 328, 335, 341, 343n, 346, 352, 355, 357, 361, 364, 369, 406, 407",
        "after": "236n, 252, 264, 266, 290n, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 318, 320, 322, 328, 335, 341, 343n, 346, 352, 355, 357, 361, 364, 369, 406, 407",
    },
    "S.csv#139": {
        "candidate_id": "cand-2450",
        "field": "index_page_range",
        "before": "212, 394",
        "after": "310, 394",
    },
    "S.csv#141": {
        "candidate_id": "cand-2452",
        "field": "sub_entry",
        "before": "Catalogus di Libri Raccolti dal fu Signor Giuseppe Smith",
        "after": "Catalogo di Libri Raccolti dal fu Signor Giuseppe Smith",
    },
    "S.csv#160": {
        "candidate_id": "cand-2471",
        "field": "index_page_range",
        "before": "300, 303n, 309, 361, 391, 392, 393, 394",
        "after": "300, 303, 309, 361, 391, 392, 393, 394",
    },
    "S.csv#161": {
        "candidate_id": "cand-2472",
        "field": "index_page_range",
        "before": "307n, 317",
        "after": "307, 310",
    },
    "S.csv#163": {
        "candidate_id": "cand-2474",
        "field": "index_page_range",
        "before": "299, 306, 337",
        "after": "299, 301, 306, 337",
    },
}
EXPECTED_ROWS = {f"S.csv#{i}" for i in range(127, 169)}
RELATED_CANDIDATES = {
    "cand-1848": ("archive", "Dactylografia Smithiana"),
    "cand-9274": ("archive", "Bibliotheca Smithiana (Joseph Smith's 1755 book inventory)"),
    "cand-10832": ("archive", "Catalogo di Libri Raccolti dal fu Signor Giuseppe Smith e pulitamente legati (Venice, 1771; Correr I. 5911)"),
    "cand-10833": ("archive", "Bibliotheca Smithiana, pars altera (catalogue of the remaining Joseph Smith library, advertised 1773)"),
    "cand-8651": ("archive", "Joseph Smith's will as published by Parker, 1948, p.60 (citation locator)"),
    "cand-9556": ("", "Joseph Smith's medal cabinet"),
}
RELATED_STATEMENTS = {
    "st-chp10-p299-pasquali-firm-launched",
    "st-chp10-p301-smith-pasquali-publication-activity",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write reviewed index types and S2 coverage")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    if sha256(ROOT / relative) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[3011:3066])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA256:
    raise SystemExit("p.469 right-column source segment changed")
if not all(token in segment_text for token in (
    "Skippon, Philip", "Smith, Joseph", "Dactylograjia Smithiana", "publication of controversial works", "Soldani, Massimiliano",
)):
    raise SystemExit("p.469 right-column content boundary check failed")
if "[Page 470]" in segment_text or "Sole," in segment_text:
    raise SystemExit("next-page content leaked into the p.469 right-column scope")

s_fields, s_rows = read_csv(S_INDEX)
if len(s_rows) <= 168 or (s_rows[127]["Main Entry"], s_rows[168]["Main Entry"]) != (
    "Skippon, Philip", "Soldani, Massimiliano",
):
    raise SystemExit("S.csv#127-168 boundary check failed")

manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
row = manifest.get(SEGMENT_ID)
if not row or (
    row.get("source_file"), row.get("line_start"), row.get("line_end"), row.get("sha256"),
    row.get("asset_sha256"), row.get("release_excluded"),
) != (SOURCE_FILE, 3012, 3066, SEGMENT_SHA256, EXPECTED_HASHES[SOURCE_FILE], True):
    raise SystemExit("p.469 right-column manifest mismatch")

candidate_path = TABLES / "entity-candidates.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
if len(candidates) != 11436 or len(coverage) != 832:
    raise SystemExit("unexpected S2 table dimensions")

candidate_by_entry = {}
candidate_by_id = {candidate["candidate_id"]: candidate for candidate in candidates}
for candidate in candidates:
    entry_id = candidate.get("index_entry_id", "")
    if entry_id in EXPECTED_ROWS:
        if entry_id in candidate_by_entry:
            raise SystemExit(f"duplicate candidate mapping: {entry_id}")
        candidate_by_entry[entry_id] = candidate
if set(candidate_by_entry) != EXPECTED_ROWS or len(candidate_by_entry) != 42:
    raise SystemExit("p.469 right-column candidate mapping is incomplete")
if len(TYPE_BY_ENTRY) != 41 or Counter(TYPE_BY_ENTRY.values()) != Counter({
    "person": 19, "event": 13, "archive": 5, "place": 2, "term": 1, "family": 1,
}):
    raise SystemExit("p.469 right-column type map is incomplete")

for entry_id, candidate in candidate_by_entry.items():
    expected_id = f"cand-{2311 + int(entry_id.split('#')[1]):04d}"
    if candidate["candidate_id"] != expected_id or candidate["status"] != "open":
        raise SystemExit(f"unexpected candidate identity or status: {entry_id}")
    expected_type = EXPECTED_PRETYPES.get(entry_id, "")
    if candidate["suggested_type"] != expected_type:
        raise SystemExit(f"unexpected candidate type pre-state: {entry_id}")

for entry_id, correction in EXPECTED_CORRECTIONS.items():
    candidate = candidate_by_entry[entry_id]
    if candidate["candidate_id"] != correction["candidate_id"]:
        raise SystemExit(f"unexpected candidate ID for correction: {entry_id}")
    if candidate[correction["field"]] != correction["before"]:
        raise SystemExit(f"unexpected candidate correction pre-state: {entry_id}")
    candidate[correction["field"]] = correction["after"]

for candidate_id, (expected_type, expected_text) in RELATED_CANDIDATES.items():
    candidate = candidate_by_id.get(candidate_id)
    if not candidate or candidate["suggested_type"] != expected_type or expected_text not in (
        candidate["canonical_name"], candidate["sub_entry"], candidate["detail"],
    ):
        raise SystemExit(f"related candidate changed: {candidate_id}")
statements = {
    json.loads(line)["statement_id"]
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
}
if not RELATED_STATEMENTS.issubset(statements):
    raise SystemExit("existing Smith-Pasquali statement anchors are missing")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
if candidate_by_entry[UNRESOLVED_ENTRY]["suggested_type"]:
    raise SystemExit("medal-cabinet index candidate must remain type-unresolved")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
coverage_row = coverage_by_segment.get(SEGMENT_ID)
if not coverage_row or (
    coverage_row["disposition"], coverage_row["migration_status"],
    coverage_row["source_line_ranges"], coverage_row["note"],
) != ("queued", "pending", "", ""):
    raise SystemExit("p.469 right-column coverage is not queued/pending")
coverage_row.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L3012-3066",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.27 prints p.469; the physical right column contains "
        "S.csv#127-168 (42 entries), from Skippon, Philip through Soldani, Massimiliano. Types: 19 person, 13 event, 5 archive, 2 place, "
        "1 term and 1 family; #151 medal cabinet remains type-unresolved. The named books/catalogues are archive; Mogliano country house and "
        "Palazzo Balbi are places; Smith's marriages, commissions, purchases, resumed consulship and sales are event seeds. Person subentries "
        "and index wording do not create formal relations. Printed p.469 corrects cand-2440 by removing 311, cand-2450 from 212 to 310, "
        "cand-2452 Catalogus to Catalogo, cand-2471 303n to 303, cand-2472 from 307n/317 to 307/310, and adds 301 to cand-2474. "
        "The Dactylografia/Dactylografa title variant and repeated catalogue/will candidates remain for S3 alignment; cand-9556 remains unresolved. "
        "Existing Smith-Pasquali relation candidates are in st-chp10-p299-pasquali-firm-launched and st-chp10-p301-smith-pasquali-publication-activity; "
        "the index adds no mentions, book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segment_id": SEGMENT_ID,
    "index_rows": len(EXPECTED_ROWS),
    "classified_types": len(TYPE_BY_ENTRY),
    "unresolved_entries": [UNRESOLVED_ENTRY],
    "preserved_pretypes": EXPECTED_PRETYPES,
    "candidate_corrections": [
        {"entry_id": entry_id, "candidate_id": change["candidate_id"], "field": change["field"],
         "before": change["before"], "after": change["after"]}
        for entry_id, change in sorted(EXPECTED_CORRECTIONS.items())
    ],
    "final_type_counts": dict(sorted(counts.items())),
    "pending_s3_candidates": sorted(RELATED_CANDIDATES),
    "mentions_or_statements_changed": False,
    "apply": args.apply,
}

if args.apply:
    backups = [
        candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX),
        coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX),
    ]
    if any(path.exists() for path in backups):
        raise SystemExit("a backup with this task suffix already exists")
    for original, backup in zip((candidate_path, coverage_path), backups):
        shutil.copy2(original, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    summary["backups"] = [str(path.relative_to(ROOT)) for path in backups]

print(json.dumps(summary, ensure_ascii=False, indent=2))
