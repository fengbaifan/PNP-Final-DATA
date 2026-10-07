#!/usr/bin/env python3
"""Classify p.470 right-column index seeds and preserve linked S2 relation candidates."""

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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
S_INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "S.csv"
T_INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "T.csv"
SEGMENT_ID = "chp-22:22_CHP-22Index:l3126-3179"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p470-rcol-l3126-3179-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/S.csv": "a73a199a0d4e2c01dfe12fd77e562e30298edb2357c54b341da887bad306393f",
    "02-sources/03-Index/03-2-Index-CSV/T.csv": "0bb8f044307aa705fdbef065e4c4353c3f46cf598d5ae888772db227de41266a",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/03_CHP-3_sec_iv.md": "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    "02-sources/02-Markdown/04_CHP-4_sec_ii.md": "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    "02-sources/02-Markdown/06_CHP-6_sec_v.md": "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
    "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    "02-sources/02-Markdown/07_CHP-7_sec_iv.md": "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    "02-sources/02-Markdown/14_CHP-14_intro.md": "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7",
    "02-sources/02-Markdown/19_CHP-19Appendix.md": "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    "02-sources/02-Markdown/20_CHP-20Postscript.md": "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "a20b1f9e24700baeba9225ad56fc09a1867f6b7daca9b1f50822548a6ab75602",
    "04-knowledge/tables/s2-coverage.csv": "618088f68114a017b7120a4e05633daf6543009036684e77789db6bba895a202",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
    "04-knowledge/tables/relations.csv": "ea6174c55fec8a2515dc56d581789af210731dcd6e48acfc7becb84e4e107ff2",
}

SEGMENT_SHA256 = "980508bf015ac3e9a1f91843a77796d136c490b38ec0ebfb95762f1c2159abba"

TYPE_BY_ENTRY = {
    "S.csv#219": "work",
    **{f"S.csv#{i}": "person" for i in (220, 221, 223, 224, 225)},
    "S.csv#222": "term",
    **{f"T.csv#{i}": "person" for i in (
        0, 1, 2, 3, 4, 5, 6, 7, 9,
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
        23, 24, 29, 31, 32, 33, 35, 36,
    )},
    **{f"T.csv#{i}": "archive" for i in (8, 10, 22)},
    **{f"T.csv#{i}": "institution" for i in (25, 27, 28)},
    "T.csv#26": "place",
    **{f"T.csv#{i}": "work" for i in (30, 34, 37)},
}

EXPECTED_STATEMENTS = {
    "st-chp7-p195-strudel-tarquin": (
        "cand-7195", "cand-2529", "painted_by_as_reported_in_liechtenstein_letter",
    ),
    "st-chp7-p195-strudel-joseph": (
        "cand-7196", "cand-2529", "painted_by_as_reported_in_liechtenstein_letter",
    ),
    "st-chp7-p197-isham-acquired-paintings-with-advice": (
        "cand-1315", "cand-2539", "acquired_paintings_advised_by",
    ),
    "st-chp4-sec-ii-p110-testa-print-dedicated-flight": (
        "cand-2557", "cand-5859", "reports_testa_dedicated_unique_flight_into_egypt_print_to_cassiano",
    ),
    "st-chp4-sec-ii-p112-treatise": (
        "cand-2557", "cand-5911", "wrote_treatise_with_observational_and_secondhand_material",
    ),
    "st-chp4-sec-ii-p113-archbishop-letter-velasquez": (
        "cand-5925", "cand-2036", "wrote_in_1646_to_announce_velasquez_visit",
    ),
    "st-chp3-seciv-l165-177-theodon-group-chosen-to-show-no-style-preference": (
        "cand-3403", "cand-5434", "chose_faith_crushing_idolatry_group_as_contrast_to_legros_style",
    ),
    "st-chp7-p186-i06": (
        "cand-1588", "cand-2564", "mazarin_summoned_theatine_branch_to_paris_in_1644_and_it_settled_by_seine",
    ),
    "st-chp7-p186-i07": (
        "cand-6873", "cand-6875", "mazarin_will_left_sum_to_rebuild_st_anne_la_royale",
    ),
    "st-chp7-p186-i09": (
        "cand-2564", "cand-6876", "theatines_summoned_guarino_guarini_for_st_anne_project_in_1662",
    ),
    "st-chp7-p193-barelli-theatine-church": (
        "cand-0243", "cand-7159", "built_for_theatines_based_on_prototype",
    ),
}

TALBOT_DETAIL = (
    "S2 print and chapter 7 p.197 read Buno; T.csv#2 transcribes Bruno. "
    "Candidate spelling follows the book; preserve the index-data variant for S3."
)

COVERAGE_NOTE = (
    "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.28 prints p.470; "
    "the segment contains S.csv#219-225 and T.csv#0-37 (45 entries), from Strudel's Tarquin and Lucretia "
    "subentry through Tiepolo's unfinished portrait of Algarotti. Types: 33 person, 4 work, 3 archive, "
    "3 institution, 1 place and 1 term. T.csv#1 remains person because the headword names Tacca; the "
    "document group is separately represented by archive candidate cand-5606 and the p.387 Appendix 2 "
    "statement. Gerusalemme Liberata is Tasso's literary text, distinct from the 1745 illustrated edition "
    "and the later canvas group. The Munich church is a place; Theatines in Paris and Rome are institution "
    "contexts. Printed p.470 corrects Talbot to Buno and Tiepolo's locators 383n/405n to 384/405. "
    "Explicit body relations at the indexed references are marked for S6 review in their existing statements; "
    "no formal relation edge or new statement is created by the index pass."
)


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


def write_statements_preserving_other_lines(path: Path, changed_statements):
    original = path.read_bytes()
    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    lines = original.decode("utf-8-sig").splitlines(keepends=True)
    found = set()
    output = []
    for line in lines:
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        content = line[:-len(ending)] if ending else line
        row = json.loads(content)
        statement_id = row.get("statement_id")
        if statement_id in changed_statements:
            row["qualifiers"]["relation_candidate"] = True
            content = json.dumps(row, ensure_ascii=False, separators=(",", ":"))
            found.add(statement_id)
        output.append(content + ending)
    if found != set(changed_statements):
        raise SystemExit(f"statement rows missing: {sorted(set(changed_statements) - found)}")
    new_bytes = bom + "".join(output).encode("utf-8")
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(new_bytes)
        temporary = Path(handle.name)
    temporary.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write reviewed candidate types, S2 coverage, and relation-candidate flags")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    if sha256(ROOT / relative) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[3125:3179])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA256:
    raise SystemExit("p.470 right-column source segment changed")
normalized = " ".join(segment_text.split())
if not all(token in normalized for token in (
    "Tarquin and Lucretia", "documents relating to commissions from", "Talbot, Buno",
    "church in Munich", "Faith crushing", "unfinished portrait of Algarotti",
)) or "Scuola del Carmine" in normalized:
    raise SystemExit("p.470 right-column content boundary check failed")

s_fields, s_rows = read_csv(S_INDEX)
t_fields, t_rows = read_csv(T_INDEX)
if len(s_rows) <= 225 or len(t_rows) <= 37 or (
    s_rows[219]["Main Entry"], s_rows[219]["Sub-entry"],
    s_rows[225]["Main Entry"], t_rows[0]["Main Entry"],
    t_rows[37]["Sub-entry"], t_rows[37]["Detail"], t_rows[38]["Sub-entry"],
) != (
    "Strudel, Peter", "Tarquin and Lucretia", "Sweerts, Michael",
    "Tacca, Pietro", "and F. Algarotti", "unfinished portrait of Algarotti", "and Scuola del Carmine",
):
    raise SystemExit("S/T index boundary check failed")

manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
manifest_row = manifest.get(SEGMENT_ID)
if not manifest_row or (
    manifest_row.get("source_file"), manifest_row.get("line_start"), manifest_row.get("line_end"),
    manifest_row.get("sha256"), manifest_row.get("asset_sha256"), manifest_row.get("release_excluded"),
) != (
    "02-sources/02-Markdown/22_CHP-22Index.md", 3126, 3179,
    SEGMENT_SHA256, EXPECTED_HASHES["02-sources/02-Markdown/22_CHP-22Index.md"], True,
):
    raise SystemExit("p.470 right-column manifest mismatch")

candidate_path = TABLES / "entity-candidates.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
statement_path = TABLES / "book-statements.jsonl"
if len(candidates) != 11436 or len(coverage) != 832:
    raise SystemExit("unexpected S2 table dimensions")

candidate_by_entry = {}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
for candidate in candidates:
    entry_id = candidate.get("index_entry_id", "")
    if entry_id in TYPE_BY_ENTRY:
        if entry_id in candidate_by_entry:
            raise SystemExit(f"duplicate candidate mapping: {entry_id}")
        candidate_by_entry[entry_id] = candidate
if set(candidate_by_entry) != set(TYPE_BY_ENTRY) or len(candidate_by_entry) != 45:
    raise SystemExit("p.470 right-column candidate mapping is incomplete")
if Counter(TYPE_BY_ENTRY.values()) != Counter({
    "person": 33, "work": 4, "archive": 3, "institution": 3, "place": 1, "term": 1,
}):
    raise SystemExit("p.470 right-column type map is incomplete")

for entry_id, candidate in candidate_by_entry.items():
    entry_number = int(entry_id.split("#")[1])
    expected_id = f"cand-{(2311 + entry_number) if entry_id.startswith('S.csv#') else (2537 + entry_number):04d}"
    if candidate["candidate_id"] != expected_id or candidate["status"] != "open":
        raise SystemExit(f"unexpected candidate identity or status: {entry_id}")
    expected_pre_type = "person" if entry_id == "T.csv#1" else ""
    if candidate["suggested_type"] != expected_pre_type:
        raise SystemExit(f"unexpected candidate type pre-state: {entry_id}")

talbot = candidate_by_entry["T.csv#2"]
if (talbot["candidate_id"], talbot["canonical_name"], talbot["detail"]) != (
    "cand-2539", "Talbot, Bruno", "",
):
    raise SystemExit("Talbot candidate pre-state changed")
talbot["canonical_name"] = "Talbot, Buno"
talbot["detail"] = TALBOT_DETAIL

tiepolo = candidate_by_entry["T.csv#32"]
old_tiepolo_range = (
    "xvii, 192, 214, 246, 248, 250, 252, 254, 255, 256, 262, 264, 265, 266, 267, 268, "
    "269n, 270, 271, 272, 276, 279, 293, 296, 297, 302, 309, 315, 322, 323, 332, 333, "
    "342, 343, 344, 345, 361, 374, 376, 377, 383n, 393, 405n, 406, 409"
)
new_tiepolo_range = old_tiepolo_range.replace("383n", "384").replace("405n", "405")
if tiepolo["candidate_id"] != "cand-2569" or tiepolo["index_page_range"] != old_tiepolo_range:
    raise SystemExit("Tiepolo candidate locator pre-state changed")
tiepolo["index_page_range"] = new_tiepolo_range

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type

statement_rows = [
    json.loads(line)
    for line in statement_path.read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
statement_by_id = {row["statement_id"]: row for row in statement_rows}
for statement_id, expected in EXPECTED_STATEMENTS.items():
    row = statement_by_id.get(statement_id)
    if not row or (
        row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate"),
    ) != expected:
        raise SystemExit(f"unexpected relation-candidate source statement: {statement_id}")
    if row.get("qualifiers", {}).get("relation_candidate") is True:
        raise SystemExit(f"relation candidate already marked: {statement_id}")

archive_locator = statement_by_id.get("st-chp19-p387-appendix2-archive-locator")
if not archive_locator or (
    archive_locator.get("object_candidate_id") != "cand-5606"
    or "cand-2538" not in archive_locator.get("qualifiers", {}).get("mentioned_candidate_ids", [])
):
    raise SystemExit("Tacca person and Fondo Orsini archive candidates are not distinguished")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
coverage_row = coverage_by_segment.get(SEGMENT_ID)
if not coverage_row or (
    coverage_row["disposition"], coverage_row["migration_status"],
    coverage_row["source_line_ranges"], coverage_row["note"],
) != ("queued", "pending", "", ""):
    raise SystemExit("p.470 right-column coverage is not queued/pending")
coverage_row.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L3126-3179",
    "note": COVERAGE_NOTE,
})

summary = {
    "segment_id": SEGMENT_ID,
    "index_rows": len(TYPE_BY_ENTRY),
    "classified_types": dict(sorted(Counter(TYPE_BY_ENTRY.values()).items())),
    "candidate_corrections": [
        {"candidate_id": "cand-2539", "field": "canonical_name", "before": "Talbot, Bruno", "after": "Talbot, Buno"},
        {"candidate_id": "cand-2569", "field": "index_page_range", "before": old_tiepolo_range, "after": new_tiepolo_range},
    ],
    "relation_candidate_statements_added": sorted(EXPECTED_STATEMENTS),
    "formal_relations_added": False,
    "mentions_or_statements_added": False,
    "apply": args.apply,
}

if args.apply:
    backup_paths = [
        candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX),
        coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX),
        statement_path.with_name(statement_path.name + BACKUP_SUFFIX),
    ]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("a backup with this task suffix already exists")
    for original, backup in zip((candidate_path, coverage_path, statement_path), backup_paths):
        shutil.copy2(original, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    write_statements_preserving_other_lines(statement_path, EXPECTED_STATEMENTS)
    summary["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

print(json.dumps(summary, ensure_ascii=False, indent=2))
