from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ALIGNMENT = ROOT / "04-knowledge" / "tables" / "alignment.csv"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MANIFEST = ROOT / "04-knowledge" / "tables" / "ku-manifest.csv"
EXISTING_KU = "units/persons/ferdinand-grand-prince-tuscany"
EXISTING_GROUP = "sg3-ku-units-persons-ferdinand-grand-prince-tuscany"
OLD_NEW_GROUP = "new-person:de-ferdinand-medici-f49b6a1e05"
TARGETS = ["cand-1609", "cand-1611"]
PROCESS_REF = "S3-Ferdinand-cross-chapter-reconciliation-2026-10-15"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def decision_counts(rows):
    return Counter(row["decision"] for row in rows)


def main():
    parser = argparse.ArgumentParser(description="Reconcile the cross-chapter identity of Grand Prince Ferdinand de' Medici")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT)
    _, candidates = read_csv(CANDIDATES)
    _, manifest = read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert len(manifest) == 1123, f"unexpected manifest count: {len(manifest)}"
    assert manifest_by_id[EXISTING_KU]["card_path"] == "04-knowledge/units/persons/ferdinand-grand-prince-tuscany.md"
    assert manifest_by_id[EXISTING_KU]["type"] == "person"
    assert candidate_by_id["cand-1617"]["suggested_type"] == "person"
    assert candidate_by_id["cand-3761"]["suggested_type"] == "person"
    for cid in TARGETS:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == OLD_NEW_GROUP
    assert set(
        row["candidate_id"] for row in alignment_by_id.values()
        if row["decision"] == "new" and get_group(row["resolution_note"]) == OLD_NEW_GROUP
    ) == set(TARGETS)
    for cid in ("cand-1617", "cand-3761"):
        row = alignment_by_id[cid]
        assert row["decision"] == "same" and row["ku_id"] == EXISTING_KU
        assert get_group(row["resolution_note"]) == EXISTING_GROUP

    preface = ROOT / "02-sources" / "02-Markdown" / "00_03_Preface_1st_Ed.md"
    plate_list = ROOT / "02-sources" / "02-Markdown" / "00_05_List_of_Plates.md"
    chapter8 = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
    postscript = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
    existing_card = ROOT / "04-knowledge" / "units" / "persons" / "ferdinand-grand-prince-tuscany.md"
    assert "Grand Prince Ferdinand of Tuscany" in preface.read_text(encoding="utf-8-sig")
    assert "36 a Francesco Petrucci: Grand Prince Ferdinand of Tuscany" in plate_list.read_text(encoding="utf-8-sig")
    assert "In the Grand Prince Ferdinand who was responsible for this short-lived but profoundly important revival" in chapter8.read_text(encoding="utf-8-sig")
    assert "Grand Prince Ferdinand de’ Medici" in postscript.read_text(encoding="utf-8-sig")
    assert existing_card.exists()

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    new_groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        new_groups[group].append(row)
    assert decision_counts([row for row in alignments if not row.get("external_source")]) == Counter(
        {"same": 1673, "new": 5008, "undecided": 5618, "excluded": 97, "conflict": 7}
    )
    assert len(new_groups) == 4831

    planned = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in TARGETS:
        row = planned_by_id[cid]
        previous_note = row["resolution_note"]
        source_prefix = previous_note.split("; group=", 1)[0]
        row["decision"] = "same"
        row["ku_id"] = EXISTING_KU
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"{source_prefix}; matched_manifest={EXISTING_KU}; matched_candidate_ids=cand-1617,cand-3761; "
            f"group={EXISTING_GROUP}; Same: the full name Grand Prince Ferdinand de’ Medici in Chapter 8, "
            "the Chapter 20 postscript, and the Chapter 8 Plate 36a reference align with the existing "
            "Grand Prince Ferdinand of Tuscany identity already mapped by cand-1617 and cand-3761. "
            "The Chapter 8 passage identifies the subject of Plate 36a as the Grand Prince Ferdinand; "
            "this is an internal source and card comparison, not a new external verification. "
            f"Historical prior resolution note retained in full: {previous_note}"
        )

    planned_non_external = [row for row in planned if row.get("candidate_id") and not row.get("external_source")]
    assert decision_counts(planned_non_external) == Counter(
        {"same": 1675, "new": 5006, "undecided": 5618, "excluded": 97, "conflict": 7}
    )
    planned_new = [row for row in planned_non_external if row["decision"] == "new"]
    planned_groups = {get_group(row["resolution_note"]) for row in planned_new}
    assert len(planned_groups) == 4830
    assert all(planned_by_id[cid]["ku_id"] == EXISTING_KU and planned_by_id[cid]["decision"] == "same" for cid in TARGETS)

    if args.dry_run:
        print("dry-run passed: candidates=2 same_before=1673 new_before=5008 new_groups_before=4831 same_after=1675 new_after=5006 new_groups_after=4830 manifest=1123")
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print("applied: cand-1609,cand-1611 -> existing Ferdinand of Tuscany KU; S3 same=1675 new=5006 new_groups=4830")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
