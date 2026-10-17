from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
PROCESS_PATH = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
GROUP = "new-person:crozat-pierre-793a5b5d2e"
PROCESS_REF = "S3-full-book-2026-10-16"
NEW_NOTE = (
    "source_ref=candidate=cand-0895;index_entry=C.csv#429;index_parent=C.csv#428;"
    "index_pages=284, 285;sub_entry=patronage of Venetian artists;"
    "s2_statements=st-chp10-p284-crozat-patronage-carriera-contact,"
    "st-chp10-p284-crozat-patronage-zanetti-contact,"
    "st-chp10-p285-crozat-welcomed-and-hosted-carriera;"
    f"group={GROUP}; The named index subentry points to Crozat's patronage of Venetian artists, "
    "and the indexed pages explicitly identify Pierre Crozat in the same continuing account. "
    "Grouped with cand-0894 by shared parent name, subentry scope, and page-anchored S2 statements; "
    "one person identity, not a second patron or a formal relationship ruling. "
)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_of(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description="Resolve the Pierre Crozat index subentry into its source-backed S3 group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(CANDIDATE_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_rows = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in candidate_rows}
    counts = Counter(row["decision"] for row in candidate_rows)
    assert counts == Counter({"same": 1697, "new": 4988, "undecided": 5615, "excluded": 97, "conflict": 7}), counts

    target = candidate_by_id["cand-0895"]
    parent = candidate_by_id["cand-0894"]
    target_alignment = alignment_by_id["cand-0895"]
    parent_alignment = alignment_by_id["cand-0894"]
    assert target["canonical_name"] == parent["canonical_name"] == "Crozat, Pierre"
    assert target["suggested_type"] == parent["suggested_type"] == "person"
    assert (target["index_entry_id"], target["sub_entry"], target["index_page_range"]) == (
        "C.csv#429", "patronage of Venetian artists", "284, 285"
    )
    assert target_alignment["decision"] == "undecided" and not target_alignment.get("ku_id")
    assert "no mapped S2 mention/body source_ref" in target_alignment["resolution_note"]
    assert parent_alignment["decision"] == "new" and group_of(parent_alignment["resolution_note"]) == GROUP

    source_10 = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    assert "through the patronage of Crozat" in source_10
    assert "She was welcomed by Crozat, who lodged" in source_10
    statements_path = TABLES / "book-statements.jsonl"
    expected_statement_ids = {
        "st-chp10-p284-crozat-patronage-carriera-contact",
        "st-chp10-p284-crozat-patronage-zanetti-contact",
        "st-chp10-p285-crozat-welcomed-and-hosted-carriera",
    }
    found = set()
    with statements_path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("statement_id") in expected_statement_ids:
                found.add(row["statement_id"])
                assert "cand-0894" in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    assert found == expected_statement_ids, found

    planned = [dict(row) for row in alignments]
    planned_target = next(row for row in planned if row.get("candidate_id") == "cand-0895" and not row.get("external_source"))
    planned_target["decision"] = "new"
    planned_target["ku_id"] = ""
    planned_target["accessed_date"] = ""
    planned_target["process_ref"] = PROCESS_REF
    planned_target["resolution_note"] = NEW_NOTE + "Previous S3 decision and rationale retained: " + target_alignment["resolution_note"]
    planned_rows = [row for row in planned if row.get("candidate_id") and not row.get("external_source")]
    planned_counts = Counter(row["decision"] for row in planned_rows)
    assert planned_counts == Counter({"same": 1697, "new": 4989, "undecided": 5614, "excluded": 97, "conflict": 7})
    groups = defaultdict(list)
    for row in planned_rows:
        if row["decision"] == "new":
            group = group_of(row["resolution_note"])
            assert group
            groups[group].append(row)
    assert len(groups) == 4819 and len(groups[GROUP]) == 2

    if args.dry_run:
        print(
            "dry-run passed: cand-0895 undecided->new; both Crozat index candidates share "
            f"{GROUP}; S3 new=4989 undecided=5614 groups=4819; "
            "three page-anchored S2 statements verified; no KU or formal relation written"
        )
        return 0

    write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    print(
        "applied: cand-0895 now joins the source-backed Pierre Crozat identity group; "
        "prior undecided decision preserved in resolution_note"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
