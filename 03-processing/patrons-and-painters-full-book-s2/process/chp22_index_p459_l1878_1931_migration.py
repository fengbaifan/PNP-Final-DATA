#!/usr/bin/env python3
"""Classify p.459 right-column index entries without changing source transcription."""

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
INDEX_M = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "M.csv"
SEGMENT_ID = "chp-22:22_CHP-22Index:l1878-1931"
SEGMENT_SHA = "e956d3456f161edf144338ae415f82a2a537ff8269e0d2944dda50f9ab35cade"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p459-right-l1878-1931-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_M: "4443a44bdbbce2e0ad3b758e8853b026e79edfba4d06b742ddd3043c0e215b4c",
    ROOT / "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    ROOT / "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    ROOT / "02-sources/02-Markdown/02_CHP-2_sec_vii.md": "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c",
    ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md": "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md": "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md": "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee",
    ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md": "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    ROOT / "02-sources/02-Markdown/06_CHP-6_sec_v.md": "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
    ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    ROOT / "02-sources/02-Markdown/07_CHP-7_sec_iv.md": "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
    ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md": "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    ROOT / "02-sources/02-Markdown/17_CHP-17_sec_i.md": "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4",
    ROOT / "02-sources/02-Markdown/19_CHP-19Appendix.md": "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    ROOT / "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "8319fe691fc0c33b17fe73c5599e3cc779256991c25bcea401b0aa704cb0c59a",
    TABLES / "s2-coverage.csv": "7a63d2d93772109c025ca5dd31314821770aac8637af9f7a7f570401bca3a9a0",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}
EXPECTED_POST_APPLY_HASHES = {
    TABLES / "entity-candidates.csv": "11c04337cf5e11eaf130353d2afc19fad64d0b7cf58c770bc3ab12cc7438e9e9",
    TABLES / "s2-coverage.csv": "1f6b0440bcb0b420f81ade257bd960d2dd54ac5d5bad608bdf57869f476873c5",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ENTRY = {
    **{f"M.csv#{i}": "person" for i in (33, 36, 37, 38, 40, 41, 43, 44, 46, 47, 48, 49, 54, 58, 59, 60, 61, 62, 63, 70, 76, 77, 78, 79, 80, 81)},
    **{f"M.csv#{i}": "place" for i in (42, 55, 57, 64)},
    **{f"M.csv#{i}": "work" for i in (34, 35, 65, 66, 67, 68, 71, 72, 73)},
    **{f"M.csv#{i}": "archive" for i in (39, 45, 52, 69)},
    **{f"M.csv#{i}": "term" for i in (53, 75)},
    "M.csv#56": "family",
    "M.csv#51": "procedure",
}
PREEXISTING_TYPES = {"M.csv#78": "person"}

PAGE_RANGE_CORRECTIONS = {
    "M.csv#33": ("78, 147, 150, 122", "78, 147, 150, 153"),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the reviewed candidate types and coverage")
parser.add_argument("--fix-coverage-rationale", action="store_true", help="repair the audit-required no_semantic_content prefix after apply")
ARGS = parser.parse_args()

if ARGS.fix_coverage_rationale:
    for path, expected in EXPECTED_POST_APPLY_HASHES.items():
        if sha256(path) != expected:
            raise SystemExit(f"post-apply state changed: {path.relative_to(ROOT)}")
    candidate_path = TABLES / "entity-candidates.csv"
    coverage_path = TABLES / "s2-coverage.csv"
    _candidate_fields, _candidates = read_csv(candidate_path)
    coverage_fields, coverage = read_csv(coverage_path)
    target = next((row for row in coverage if row["segment_id"] == SEGMENT_ID), None)
    if not target or (target["disposition"], target["migration_status"], target["source_line_ranges"]) != (
        "reviewed", "complete", "L1878-1931"
    ):
        raise SystemExit("p.459 right-column coverage state changed")
    if not target["note"].startswith("index-seed classification only:") or "no_semantic_content:" in target["note"]:
        raise SystemExit("coverage rationale is not the expected pre-repair note")
    target["note"] = "no_semantic_content: " + target["note"]
    result = {"mode": "apply" if ARGS.apply else "dry-run", "source_segment": SEGMENT_ID,
              "coverage_note_prefix": "no_semantic_content:", "coverage_complete": 649,
              "coverage_queued": 44, "coverage_excluded": 139}
    if ARGS.apply:
        backup_path = coverage_path.with_name(coverage_path.name + ".bak-s2-chp22-index-p459-right-rationale-20261007")
        if backup_path.exists():
            raise SystemExit(f"migration backup already exists; refusing to overwrite: {backup_path.name}")
        shutil.copy2(coverage_path, backup_path)
        write_csv(coverage_path, coverage_fields, coverage)
        result["backup"] = str(backup_path.relative_to(ROOT))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1877:1931])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 p.459 right-column segment changed")

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
    segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
    segment.get("sha256"), segment.get("asset_sha256"), segment.get("release_excluded"),
) != (SOURCE_FILE, 1878, 1931, SEGMENT_SHA, ASSET_SHA, True):
    raise SystemExit("S0 p.459 right-column manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_fields, coverage = read_csv(coverage_path)
m_fields, m_rows = read_csv(INDEX_M)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(candidates), len(coverage), len(m_rows), len(mentions), len(statements)) != (11436, 832, 262, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

expected_entries = {f"M.csv#{i}" for i in range(33, 82)}
excluded_entry = "M.csv#74"
untyped_entry = "M.csv#50"
classified_entries = expected_entries - {excluded_entry, untyped_entry}
if len(expected_entries) != 49 or set(TYPE_BY_INDEX_ENTRY) != classified_entries or len(TYPE_BY_INDEX_ENTRY) != 47:
    raise SystemExit("type map does not cover exactly the 47 classifiable p.459 right-column entries")
if set(PREEXISTING_TYPES) != {"M.csv#78"} or any(TYPE_BY_INDEX_ENTRY.get(entry) != entity_type for entry, entity_type in PREEXISTING_TYPES.items()):
    raise SystemExit("unexpected pre-existing classification")
if set(PAGE_RANGE_CORRECTIONS) != {"M.csv#33"}:
    raise SystemExit("unexpected candidate-only page-range correction")

all_by_entry = {}
for row in candidates:
    if row["index_entry_id"]:
        all_by_entry.setdefault(row["index_entry_id"], []).append(row)
if any(len(all_by_entry.get(entry, [])) != 1 for entry in expected_entries):
    raise SystemExit("p.459 right-column candidate mapping is incomplete or duplicated")
by_entry = {entry: all_by_entry[entry][0] for entry in expected_entries}
expected_ids = {f"M.csv#{i}": f"cand-{1463 + i}" for i in range(33, 74)}
expected_ids.update({f"M.csv#{i}": f"cand-{1462 + i}" for i in range(75, 82)})
expected_ids[excluded_entry] = "cand-2916"

for entry, candidate in by_entry.items():
    row_number = int(entry.split("#")[1])
    index_row = m_rows[row_number]
    if candidate["candidate_id"] != expected_ids[entry] or candidate["index_source_file"] != "M.csv":
        raise SystemExit(f"unexpected candidate identity for {entry}: {candidate['candidate_id']}")
    for candidate_field, index_field in (("canonical_name", "Main Entry"), ("sub_entry", "Sub-entry"), ("detail", "Detail")):
        if candidate[candidate_field] != index_row[index_field]:
            raise SystemExit(f"candidate/index transcription mismatch for {entry}: {candidate_field}")
    expected_pages = PAGE_RANGE_CORRECTIONS[entry][0] if entry in PAGE_RANGE_CORRECTIONS else index_row["Page Numbers"]
    if candidate["index_page_range"] != expected_pages:
        raise SystemExit(f"candidate page-range pre-state changed for {entry}: {candidate['index_page_range']!r}")
    if entry == excluded_entry:
        if candidate["status"] != "excluded" or candidate["exclude_reason"] != "索引交叉引用：see under Richmond, Duke of":
            raise SystemExit("M.csv#74 alias exclusion changed")
    elif candidate["status"] != "open":
        raise SystemExit(f"candidate is not open: {entry}")
    elif entry in PREEXISTING_TYPES:
        if candidate["suggested_type"] != PREEXISTING_TYPES[entry]:
            raise SystemExit(f"pre-existing classification changed: {entry}")
    elif candidate["suggested_type"]:
        raise SystemExit(f"candidate unexpectedly has a type: {entry}")

if (m_rows[33]["Main Entry"], m_rows[33]["Page Numbers"]) != ("Maidalchini, Donna Olimpia", "78, 147, 150, 122"):
    raise SystemExit("unexpected original M.csv row for Donna Olimpia Maidalchini")

for entry, entity_type in TYPE_BY_INDEX_ENTRY.items():
    by_entry[entry]["suggested_type"] = entity_type
for entry, (_old, new) in PAGE_RANGE_CORRECTIONS.items():
    by_entry[entry]["index_page_range"] = new

typed_counts = Counter(by_entry[entry]["suggested_type"] for entry in TYPE_BY_INDEX_ENTRY)
expected_types = Counter({"person": 26, "place": 4, "work": 9, "archive": 4, "term": 2, "family": 1, "procedure": 1})
if typed_counts != expected_types:
    raise SystemExit(f"unexpected p.459 right-column type counts: {typed_counts}")

coverage_by_id = {row["segment_id"]: row for row in coverage}
target = coverage_by_id.get(SEGMENT_ID)
previous_left = coverage_by_id.get("chp-22:22_CHP-22Index:l1822-1876")
next_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1933-1933")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.459 right-column segment is not queued")
if not previous_left or previous_left["migration_status"] != "complete":
    raise SystemExit("preceding p.459 left-column segment is not complete")
if not next_marker or (next_marker["disposition"], next_marker["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next p.459 page marker is not queued")

target.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1878-1931",
    note=(
        "no_semantic_content: index-seed classification only: 49 M.csv rows, 48 open candidates and one pre-excluded see-under alias. "
        "Types for 47 classifiable entries: 26 person, 4 place, 9 work, 4 archive, 2 term, 1 family, 1 procedure; "
        "Manfrin's collection candidate remains open/type-pending because collection is absent from taxonomy; "
        "his recurring painter competitions are a procedure, not a single dated event. Named portraits, busts, "
        "paintings and the Stanislas altarpiece are works; the Felsina Pittrice and Considerazioni sulla Pittura, "
        "Manfrin-Edwards letter and S. Andrea document group are archives. Manin family remains family; named "
        "mansions, country house, Manin palace and Altieri palace are places. Maratta's generic payment and "
        "Marchesini's work-for-Conti subentry remain person context; preserve the existing person type on M.csv#78. "
        "Candidate-only correction: M.csv#33 page "
        "122 -> 153 per CHP-22Index.pdf physical p.17; preserve S0 and original M.csv. M.csv#74 remains an "
        "excluded see-under alias. Index navigation adds no mentions, book statements or relations."
    ),
)

after = {
    "coverage_complete": sum(item["disposition"] == "reviewed" and item["migration_status"] == "complete" for item in coverage),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(item["disposition"] == "reviewed" and item["migration_status"] == "partial" for item in coverage),
    "index_open_untyped": sum(bool(item["index_entry_id"]) and item["status"] == "open" and not item["suggested_type"] for item in candidates),
}
expected_after = {
    "coverage_complete": 649,
    "coverage_queued": 44,
    "coverage_excluded": 139,
    "coverage_partial": 0,
    "index_open_untyped": 1334,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 459,
    "pdf_physical_page": 17,
    "classified_candidates": len(TYPE_BY_INDEX_ENTRY),
    "newly_classified_candidates": len(TYPE_BY_INDEX_ENTRY) - len(PREEXISTING_TYPES),
    "type_counts": dict(typed_counts),
    "preserved_existing_types": PREEXISTING_TYPES,
    "untyped_collection_entry": {"candidate_id": by_entry[untyped_entry]["candidate_id"], "index_entry_id": untyped_entry},
    "excluded_alias": {"candidate_id": by_entry[excluded_entry]["candidate_id"], "index_entry_id": excluded_entry},
    "candidate_only_corrections": {
        entry: {"from": old, "to": new} for entry, (old, new) in PAGE_RANGE_CORRECTIONS.items()
    },
    **after,
}
if ARGS.apply:
    backups = []
    for path in (candidate_path, coverage_path):
        backup_path = path.with_name(path.name + BACKUP_SUFFIX)
        if backup_path.exists():
            raise SystemExit(f"migration backup already exists; refusing to overwrite: {backup_path.name}")
        backups.append((path, backup_path))
    for path, backup_path in backups:
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for _source, path in backups]

print(json.dumps(result, ensure_ascii=False, indent=2))
