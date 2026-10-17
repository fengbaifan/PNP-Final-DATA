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
EXISTING_KU = "units/persons/francesco-maria-del-monte"
EXISTING_GROUP = "sg3-ku-units-persons-francesco-maria-del-monte"
MATCHED_CANDIDATE = "cand-3271"
TARGET = "cand-1691"
OLD_GROUP = "new-person:del-francesco-monte-7e5c27fe05"
PROCESS_REF = "S3-del-monte-existing-person-reconciliation-2026-10-16"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def candidate_decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def group_rows(rows, decision):
    groups = defaultdict(list)
    for row in rows:
        if row["decision"] == decision:
            group = get_group(row.get("resolution_note", ""))
            assert group, f"{decision} candidate lacks group: {row['candidate_id']}"
            groups[group].append(row)
    return groups


def main():
    parser = argparse.ArgumentParser(description="Reuse the existing Francesco Maria del Monte person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT)
    _, candidates = read_csv(CANDIDATES)
    _, manifest = read_csv(MANIFEST)
    current = candidate_decision_rows(alignments)
    decision_by_id = {row["candidate_id"]: row for row in current}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert len(manifest) == 1159, f"unexpected manifest count: {len(manifest)}"
    assert manifest_by_id[EXISTING_KU]["type"] == "person"
    assert manifest_by_id[EXISTING_KU]["card_path"] == "04-knowledge/units/persons/francesco-maria-del-monte.md"
    card_path = ROOT / manifest_by_id[EXISTING_KU]["card_path"]
    card_text = card_path.read_text(encoding="utf-8-sig")
    assert "Francesco Maria del Monte" in card_text and "Wikidata, Q140106" in card_text

    matched = decision_by_id[MATCHED_CANDIDATE]
    assert matched["decision"] == "same" and matched["ku_id"] == EXISTING_KU
    assert get_group(matched["resolution_note"]) == EXISTING_GROUP
    candidate = candidate_by_id[TARGET]
    row = decision_by_id[TARGET]
    assert candidate["suggested_type"] == "person"
    assert candidate["canonical_name"] == "Monte, Cardinal Francesco del"
    assert candidate["index_entry_id"] == "M.csv#232"
    assert row["decision"] == "new" and not row["ku_id"]
    assert get_group(row["resolution_note"]) == OLD_GROUP
    assert {item["candidate_id"] for item in group_rows(current, "new")[OLD_GROUP]} == {TARGET}

    chapter2 = (ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md").read_text(encoding="utf-8-sig")
    chapter5 = (ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_i.md").read_text(encoding="utf-8-sig")
    postscript = (ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md").read_text(encoding="utf-8-sig")
    assert "Francesco del Monte" in chapter2
    assert "first serious patron he had been" in chapter2
    assert "Cardinal del Monte" in chapter5
    assert "Cardinal Del Monte" in postscript

    before_counts = Counter(item["decision"] for item in current)
    new_before = group_rows(current, "new")
    same_before = group_rows(current, "same")
    assert before_counts == Counter({"same": 1696, "new": 4989, "undecided": 5615, "excluded": 97, "conflict": 7}), before_counts
    assert len(new_before) == 4820 and sum(len(items) > 1 for items in new_before.values()) == 133
    assert len(same_before) == 1019

    planned = [dict(item) for item in alignments]
    planned_row = next(item for item in planned if item.get("candidate_id") == TARGET and not item.get("external_source"))
    old_note = planned_row["resolution_note"]
    planned_row["decision"] = "same"
    planned_row["ku_id"] = EXISTING_KU
    planned_row["process_ref"] = PROCESS_REF
    planned_row["resolution_note"] = (
        f"source_ref=candidate={TARGET}; matched_manifest={EXISTING_KU}; "
        f"matched_candidate_ids={MATCHED_CANDIDATE}; group={EXISTING_GROUP}; "
        "Same: Chapter 2 p. 44 names Francesco del Monte and the same passage identifies him as a cardinal; "
        "pp. 47–48 continue his patronage of Caravaggio, artists, and Andrea Sacchi. Chapter 5 p. 120 and "
        "the Chapter 20 postscript p. 397 continue the Cardinal del Monte account. The existing accepted KU "
        "is Francesco Maria del Monte, an Italian cardinal and Caravaggio's early patron; the full name, title, "
        "patronage context, and cross-chapter continuity identify the same person. Candidate cand-3271 already "
        "maps this accepted KU. Reuse it; no new external source was accessed. "
        f"Historical new-group decision and rationale retained verbatim: {old_note}"
    )

    planned_current = candidate_decision_rows(planned)
    after_counts = Counter(item["decision"] for item in planned_current)
    new_after = group_rows(planned_current, "new")
    same_after = group_rows(planned_current, "same")
    assert after_counts == Counter({"same": 1697, "new": 4988, "undecided": 5615, "excluded": 97, "conflict": 7}), after_counts
    assert len(new_after) == 4819 and sum(len(items) > 1 for items in new_after.values()) == 133
    assert len(same_after) == 1019
    assert {item["candidate_id"] for item in same_after[EXISTING_GROUP]} >= {MATCHED_CANDIDATE, TARGET}
    assert planned_row["decision"] == "same" and planned_row["ku_id"] == EXISTING_KU

    if args.dry_run:
        print(
            f"dry-run passed: {TARGET} new->{EXISTING_KU} same; "
            f"same={before_counts['same']}->{after_counts['same']} "
            f"new={before_counts['new']}->{after_counts['new']} "
            f"new_groups={len(new_before)}->{len(new_after)}; manifest={len(manifest)}"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        f"applied: {TARGET} -> {EXISTING_KU}; "
        f"same={after_counts['same']} new={after_counts['new']} new_groups={len(new_after)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
