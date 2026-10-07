#!/usr/bin/env python3
"""Classify p.470 S-index seeds and close the page marker and left-column S2 segments."""

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
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_IDS = (
    "chp-22:22_CHP-22Index:l3068-3068",
    "chp-22:22_CHP-22Index:l3070-3124",
)
BACKUP_SUFFIX = ".bak-s2-chp22-index-p470-l3068-3124-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/S.csv": "a73a199a0d4e2c01dfe12fd77e562e30298edb2357c54b341da887bad306393f",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/05_CHP-5_sec_iii.md": "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a",
    "02-sources/02-Markdown/08_CHP-8_sec_i.md": "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
    "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    "02-sources/02-Markdown/16_CHP-16_intro.md": "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff",
    "02-sources/02-Markdown/19_CHP-19Appendix.md": "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "49d0ef1729d30d0b11acd4af4cd834e56835f8a2db6931211f15b77127c4b3c4",
    "04-knowledge/tables/s2-coverage.csv": "f97ae9c0593e31151f9ad5321d657273744121c91d5bda5c2b2522c3e9b7bd49",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
    "04-knowledge/tables/relations.csv": "ea6174c55fec8a2515dc56d581789af210731dcd6e48acfc7becb84e4e107ff2",
}

SEGMENT_SHA256 = {
    "chp-22:22_CHP-22Index:l3068-3068": "7a44ec5cec2b8c71058eab0f869c2fc33b679d7947d6b4223d7e580c8ece960a",
    "chp-22:22_CHP-22Index:l3070-3124": "7ac56b7e40d485a9b01399fde19cd9a7b1a385bb3a7157213a8fd5560ff97aba",
}

TYPE_BY_ENTRY = {
    **{f"S.csv#{i}": "person" for i in (
        169, 173, 181, 182, 183, 184, 193, 194, 195, 197, 198,
        200, 201, 203, 205, 206, 208, 209, 216, 217, 218,
    )},
    **{f"S.csv#{i}": "work" for i in (
        170, 171, 172, 174, 175, 176, 177, 178, 179, 180, 185,
        186, 187, 202, 210, 212, 213, 214, 215,
    )},
    **{f"S.csv#{i}": "event" for i in (191, 207, 211)},
    **{f"S.csv#{i}": "archive" for i in (192, 204)},
    **{f"S.csv#{i}": "term" for i in (188, 189, 190, 196, 199)},
}

EXPECTED_CORRECTIONS = {
    "S.csv#174": {
        "candidate_id": "cand-2485",
        "field": "sub_entry",
        "before": "Deborah and Barak",
        "after": "Deborah and Barach",
    },
    "S.csv#182": {
        "candidate_id": "cand-2493",
        "field": "index_page_range",
        "before": "75n, 139",
        "after": "75, 139",
    },
    "S.csv#184": {
        "candidate_id": "cand-2495",
        "field": "index_page_range",
        "before": "139n, 204n",
        "after": "139, 204n",
    },
}

DISCREPANCY_DETAIL = (
    "S2 attribution discrepancy: the printed index places this work under Micco Spadaro; "
    "chapter 5 p.139 and Plate 22b identify a work with this title by Michelangelo Cerquozzi. "
    "Possible index misattribution or a distinct work; do not assign the artist or merge with "
    "body candidate cand-4060 until identity is resolved."
)

RELATED_STATEMENT_IDS = {
    "st-chp5-p139-masaniello-painting",
    "st-chp8-p207-n1-pool-of-bethesda-passed-through-three-collections",
    "st-chp8-p207-n1-woman-taken-in-adultery-passed-through-three-collections",
    "st-chp10-p315-streit-bequests-of-acquired-pictures",
    "st-chp10-p316-streit-displayed-family-portraits",
    "st-chp16-p374-strange-employs-guardi",
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
marker_text = "\n".join(source_lines[3067:3068])
segment_text = "\n".join(source_lines[3069:3124])
if hashlib.sha256(marker_text.encode("utf-8")).hexdigest() != SEGMENT_SHA256[SEGMENT_IDS[0]]:
    raise SystemExit("p.470 page-marker source segment changed")
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA256[SEGMENT_IDS[1]]:
    raise SystemExit("p.470 left-column source segment changed")
if "[Page 470]" not in marker_text:
    raise SystemExit("p.470 page marker text mismatch")
normalized_segment = " ".join(segment_text.split())
if not all(token in normalized_segment for token in (
    "Sole, Giovan Gioseffo dal", "Deborah and Barach", "Spada, Cardinal Bernardino",
    "Revolt of Masaniello", "bequest of pictures to Gymnasium zum Grauen Kloster", "Strudel, Peter",
)) or "Tarquin and Lucretia" in normalized_segment:
    raise SystemExit("p.470 left-column content boundary check failed")

s_fields, s_rows = read_csv(S_INDEX)
if len(s_rows) <= 219 or (
    s_rows[169]["Main Entry"], s_rows[218]["Main Entry"],
    s_rows[219]["Main Entry"], s_rows[219]["Sub-entry"],
) != (
    "Sole, Giovan Gioseffo dal", "Strudel, Peter", "Strudel, Peter", "Tarquin and Lucretia",
):
    raise SystemExit("S.csv#169-219 boundary check failed")

manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
for segment_id, line_start, line_end in (
    (SEGMENT_IDS[0], 3068, 3068),
    (SEGMENT_IDS[1], 3070, 3124),
):
    row = manifest.get(segment_id)
    if not row or (
        row.get("source_file"), row.get("line_start"), row.get("line_end"), row.get("sha256"),
        row.get("asset_sha256"), row.get("release_excluded"),
    ) != (
        SOURCE_FILE, line_start, line_end, SEGMENT_SHA256[segment_id], EXPECTED_HASHES[SOURCE_FILE], True,
    ):
        raise SystemExit(f"p.470 manifest mismatch: {segment_id}")

candidate_path = TABLES / "entity-candidates.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
if len(candidates) != 11436 or len(coverage) != 832:
    raise SystemExit("unexpected S2 table dimensions")

expected_rows = {f"S.csv#{i}" for i in range(169, 219)}
candidate_by_entry = {}
candidate_by_id = {candidate["candidate_id"]: candidate for candidate in candidates}
for candidate in candidates:
    entry_id = candidate.get("index_entry_id", "")
    if entry_id in expected_rows:
        if entry_id in candidate_by_entry:
            raise SystemExit(f"duplicate candidate mapping: {entry_id}")
        candidate_by_entry[entry_id] = candidate
if set(candidate_by_entry) != expected_rows or len(candidate_by_entry) != 50:
    raise SystemExit("p.470 left-column candidate mapping is incomplete")
if len(TYPE_BY_ENTRY) != 50 or Counter(TYPE_BY_ENTRY.values()) != Counter({
    "person": 21, "work": 19, "event": 3, "archive": 2, "term": 5,
}):
    raise SystemExit("p.470 left-column type map is incomplete")

for entry_id, candidate in candidate_by_entry.items():
    expected_id = f"cand-{2311 + int(entry_id.split('#')[1]):04d}"
    if candidate["candidate_id"] != expected_id or candidate["status"] != "open":
        raise SystemExit(f"unexpected candidate identity or status: {entry_id}")
    if candidate["suggested_type"]:
        raise SystemExit(f"unexpected candidate type pre-state: {entry_id}")

for entry_id, correction in EXPECTED_CORRECTIONS.items():
    candidate = candidate_by_entry[entry_id]
    if candidate["candidate_id"] != correction["candidate_id"]:
        raise SystemExit(f"unexpected candidate ID for correction: {entry_id}")
    if candidate[correction["field"]] != correction["before"]:
        raise SystemExit(f"unexpected candidate correction pre-state: {entry_id}")
    candidate[correction["field"]] = correction["after"]

disputed = candidate_by_entry["S.csv#186"]
if disputed["candidate_id"] != "cand-2497" or disputed["detail"]:
    raise SystemExit("S.csv#186 discrepancy candidate pre-state changed")
disputed["detail"] = DISCREPANCY_DETAIL
for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type

statements = {
    json.loads(line)["statement_id"]: json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
}
if not RELATED_STATEMENT_IDS.issubset(statements):
    raise SystemExit("expected body statement anchors for p.470 index entries are missing")
if statements["st-chp16-p374-strange-employs-guardi"].get("qualifiers", {}).get("relation_candidate") is not True:
    raise SystemExit("existing Strange-Guardi relation candidate is not preserved")
if statements["st-chp10-p315-streit-bequests-of-acquired-pictures"].get("qualifiers", {}).get("relation_candidate") is not True:
    raise SystemExit("existing Streit bequest relation candidate is not preserved")
if statements["st-chp10-p316-streit-displayed-family-portraits"].get("qualifiers", {}).get("relation_candidate") is not True:
    raise SystemExit("existing Streit family-portrait relation candidate is not preserved")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
for segment_id in SEGMENT_IDS:
    row = coverage_by_segment.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"], row["note"]) != (
        "queued", "pending", "", "",
    ):
        raise SystemExit(f"S2 coverage is not queued/pending: {segment_id}")

coverage_by_segment[SEGMENT_IDS[0]].update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L3068-3068",
    "note": (
        "no_semantic_content: S0 L3068 [Page 470] is a generated navigation marker, confirmed on "
        "CHP-22Index.pdf physical p.28; it is not an indexed object or factual claim."
    ),
})
coverage_by_segment[SEGMENT_IDS[1]].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L3070-3124",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.28 prints p.470; "
        "the segment contains S.csv#169-218 (50 entries), Sole, Giovan Gioseffo dal through Strudel, Peter. "
        "Types: 21 person, 19 work, 3 event, 2 archive, 5 term. The next segment starts the Strudel subentry "
        "Tarquin and Lucretia and is not included here. Printed p.470 corrects cand-2485 Deborah and Barak to "
        "Deborah and Barach, cand-2493 Spada locator 75n to 75, and cand-2495 Spadaro locator 139n to 139. "
        "The printed index spells Rebecca and Eliezar; the body text and S.csv spell Eliezer, retained as the "
        "candidate name with the source variation recorded. S#186 is indexed under Micco Spadaro, while "
        "chapter 5 p.139 and Plate 22b identify a same-titled work by Cerquozzi; attribution or distinct-work "
        "status remains unresolved, so cand-2497 is not merged with body candidate cand-4060. The index "
        "subentries for employment, bequest, and family portraits do not create relations: existing book "
        "statement candidates remain st-chp16-p374-strange-employs-guardi, "
        "st-chp10-p315-streit-bequests-of-acquired-pictures, and "
        "st-chp10-p316-streit-displayed-family-portraits. No S0, S.csv, mentions, book statements, or relations changed."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segment_ids": list(SEGMENT_IDS),
    "index_rows": len(expected_rows),
    "classified_types": len(TYPE_BY_ENTRY),
    "excluded_marker": SEGMENT_IDS[0],
    "candidate_corrections": [
        {"entry_id": entry_id, "candidate_id": change["candidate_id"], "field": change["field"],
         "before": change["before"], "after": change["after"]}
        for entry_id, change in sorted(EXPECTED_CORRECTIONS.items())
    ],
    "candidate_detail_flagged": "cand-2497",
    "final_type_counts": dict(sorted(counts.items())),
    "related_statement_ids_checked": sorted(RELATED_STATEMENT_IDS),
    "mentions_statements_relations_changed": False,
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
