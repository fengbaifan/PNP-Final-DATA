from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def group_id(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(
        description="Reconcile source-supported family identity groups before S4 registration"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_fields, alignments = read_csv(ALIGNMENT)
    decisions = decision_rows(alignments)
    alignment_by_id = {row["candidate_id"]: row for row in decisions}

    counts = Counter(row["decision"] for row in decisions)
    assert counts == Counter(
        {"same": 1696, "new": 4988, "undecided": 5616, "excluded": 97, "conflict": 7}
    ), counts

    main_entry = candidate_by_id["cand-0930"]
    subentry = candidate_by_id["cand-0931"]
    main_alignment = alignment_by_id["cand-0930"]
    sub_alignment = alignment_by_id["cand-0931"]
    assert main_entry["suggested_type"] == subentry["suggested_type"] == "family"
    assert main_entry["canonical_name"] == subentry["canonical_name"] == "Dolfin family"
    assert main_entry["index_entry_id"] == "D.csv#32"
    assert subentry["index_entry_id"] == "D.csv#33"
    assert main_alignment["decision"] == "undecided" and not main_alignment["ku_id"]
    assert sub_alignment["decision"] == "new" and not sub_alignment["ku_id"]
    expected_group = "sg3-family-dolfinfamily"
    assert group_id(sub_alignment["resolution_note"]) == expected_group
    assert "Index locator only" in main_alignment["resolution_note"]

    # The indexed main heading and subentry must both exist under the same
    # family label; entry IDs remain the stable locators, not line numbers.
    with (ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "D.csv").open(
        encoding="utf-8-sig", newline=""
    ) as stream:
        index_rows = list(csv.reader(stream))
    family_rows = [row for row in index_rows[1:] if row and row[0] == "Dolfin family"]
    assert len(family_rows) == 2, family_rows
    assert not family_rows[0][2] and family_rows[0][1] == "Venice"
    assert family_rows[1][2] == "patronage of Tiepolo" and family_rows[1][1] == "Venice"
    body = (ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md").read_text(
        encoding="utf-8-sig"
    )
    assert "They were a tremendous family in the old style." in body
    assert "his greatest patrons of the 1720s" in body

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}

    main_alignment = planned_by_id["cand-0930"]
    previous_note = main_alignment["resolution_note"]
    main_alignment["decision"] = "new"
    main_alignment["resolution_note"] = (
        f"group={expected_group}; source_ref=D.csv#32; S3 decision update 2026-10-16: changed from "
        f"undecided after checking the exact index parent/subentry pair (D.csv#32/#33) against the "
        f"chapter 9 p. 252 family anchor mapped by cand-0931. The index main heading and its Tiepolo-patronage "
        f"subentry name the same Dolfin family; retain the earlier reason for traceability: {previous_note}"
    )
    planned_by_id["cand-0931"]["resolution_note"] += (
        " S3 cross-chapter identity clarification 2026-10-16: group with the adjacent index main heading "
        "cand-0930; the chapter 9 p. 252 family and Tiepolo-patronage anchor supports this family-level identity."
    )

    planned_by_id["cand-7617"]["resolution_note"] += (
        " S3 identity clarification 2026-10-16: the p. 214 footnote names a family-level owner group, and "
        "chapter 9 p. 262 independently calls the Giovanelli a family ennobled in 1668; this is a new family "
        "identity. Keep the distinct, untyped Giovanelli collection index candidate cand-1192 undecided; the "
        "family decision does not resolve or absorb that collection referent."
    )
    planned_by_id["cand-8571"]["resolution_note"] += (
        " S3 identity clarification 2026-10-16: pp. 263–264 establish a source-named collective Sagredo family, "
        "distinct from individually named Zaccaria and Niccolò Sagredo. The new decision resolves only the "
        "family-level identity; full genealogy and individual membership mapping remain unverified and are not "
        "being inferred here."
    )

    planned_decisions = decision_rows(planned)
    planned_counts = Counter(row["decision"] for row in planned_decisions)
    assert planned_counts == Counter(
        {"same": 1696, "new": 4989, "undecided": 5615, "excluded": 97, "conflict": 7}
    ), planned_counts
    groups = defaultdict(list)
    for row in planned_decisions:
        if row["decision"] == "new":
            group = group_id(row["resolution_note"])
            assert group, row["candidate_id"]
            groups[group].append(row)
    assert {row["candidate_id"] for row in groups[expected_group]} == {"cand-0930", "cand-0931"}
    assert len(groups) == 4820 and sum(map(len, groups.values())) == 4989

    if args.dry_run:
        print(
            "dry-run passed: Dolfin main heading cand-0930 undecided->new; "
            "group=sg3-family-dolfinfamily members=2; family identity clarifications=2; "
            "candidate_decisions new=4989 undecided=5615 groups=4820; no files written"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: Dolfin main heading cand-0930 changed to new in sg3-family-dolfinfamily; "
        "family identity notes clarified for cand-0931, cand-7617, cand-8571; "
        "candidate_decisions new=4989 undecided=5615 groups=4820"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
