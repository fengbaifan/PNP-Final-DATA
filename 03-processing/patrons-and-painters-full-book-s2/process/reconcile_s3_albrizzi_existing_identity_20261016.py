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
EXISTING_KU = "units/persons/albrizzi"
EXISTING_GROUP = "sg3-ku-units-persons-albrizzi"
EXISTING_CANDIDATE = "cand-3711"
OLD_NEW_GROUP = "new-person:albrizzi-giambattista-bd0a26b9de"
TARGETS = ("cand-0025", "cand-0027", "cand-0029")
PROCESS_REF = "S3-Albrizzi-cross-chapter-reconciliation-2026-10-16"


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


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def grouped_ids(rows, decision):
    groups = defaultdict(set)
    for row in rows:
        if row["decision"] == decision:
            group = get_group(row.get("resolution_note", ""))
            assert group, f"{decision} candidate lacks group: {row['candidate_id']}"
            groups[group].add(row["candidate_id"])
    return groups


def main():
    parser = argparse.ArgumentParser(description="Map the Chapter 13 Giambattista Albrizzi candidates to the existing Albrizzi person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT)
    _, candidates = read_csv(CANDIDATES)
    _, manifest = read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = decision_rows(alignments)
    decision_by_id = {row["candidate_id"]: row for row in decisions}
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert len(manifest) == 1128, f"unexpected manifest count: {len(manifest)}"
    assert manifest_by_id[EXISTING_KU]["type"] == "person"
    assert manifest_by_id[EXISTING_KU]["card_path"] == "04-knowledge/units/persons/albrizzi.md"
    existing_card = (ROOT / "04-knowledge" / "units" / "persons" / "albrizzi.md").read_text(encoding="utf-8-sig")
    assert "Giovanni Battista Albrizzi" in existing_card
    assert "Giambatista Albrizzi" in existing_card
    assert "Giambattista Albrizzi" not in existing_card

    for cid in TARGETS:
        candidate = candidate_by_id[cid]
        row = decision_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "Albrizzi, Giambattista"
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == OLD_NEW_GROUP
    assert {row["candidate_id"] for row in decisions if row["decision"] == "new" and get_group(row.get("resolution_note", "")) == OLD_NEW_GROUP} == set(TARGETS)
    assert decision_by_id[EXISTING_CANDIDATE]["decision"] == "same"
    assert decision_by_id[EXISTING_CANDIDATE]["ku_id"] == EXISTING_KU
    assert get_group(decision_by_id[EXISTING_CANDIDATE]["resolution_note"]) == EXISTING_GROUP
    assert {row["candidate_id"] for row in decisions if row["decision"] == "same" and get_group(row.get("resolution_note", "")) == EXISTING_GROUP} == {EXISTING_CANDIDATE}

    chapter13 = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
    chapter13_text = chapter13.read_text(encoding="utf-8-sig")
    assert "Three publishers stand out above all the others for the enterprise and quality of their patronage—Giambattista Albrizzi" in chapter13_text
    assert "Albrizzi was a notable collector of contemporary pictures" in chapter13_text
    assert "Thereafter the two men were so intimately linked in friendship as well as in business partnership" in chapter13_text
    assert "the Gerusalemme Liberata which he brought out in 1745" in chapter13_text
    assert "Albrizzi was keen to build up a private collection for himself" in chapter13_text
    front_matter = ROOT / "02-sources" / "02-Markdown" / "00_05_List_of_Plates.md"
    assert "published by Albrizzi 1745, with portraits of Piazzetta and Albrizzi" in front_matter.read_text(encoding="utf-8-sig")

    before = Counter(row["decision"] for row in decisions)
    same_before = grouped_ids(decisions, "same")
    new_before = grouped_ids(decisions, "new")
    assert before == Counter({"same": 1678, "new": 5003, "undecided": 5618, "excluded": 97, "conflict": 7}), before
    assert len(same_before) == 1019 and sum(len(ids) > 1 for ids in same_before.values()) == 269
    assert len(new_before) == 4828 and sum(len(ids) > 1 for ids in new_before.values()) == 135

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}
    for cid in TARGETS:
        row = planned_by_id[cid]
        previous_note = row["resolution_note"]
        source_prefix, old_tail = previous_note.split("; group=", 1)
        row["decision"] = "same"
        row["ku_id"] = EXISTING_KU
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"{source_prefix}; matched_manifest={EXISTING_KU}; matched_candidate_ids={EXISTING_CANDIDATE}; "
            f"group={EXISTING_GROUP}; Same: Chapter 13 p. 334 names Giambattista Albrizzi among Venice's "
            "leading publishers and describes the same publisher's commercial, intellectual, and collecting "
            "activity through pp. 335–345. The existing person KU records Giovanni Battista Albrizzi and the "
            "publication signature Giambatista Albrizzi; its front-matter plate evidence identifies Albrizzi "
            "as publisher of the 1745 Piazzetta edition of Gerusalemme Liberata, matching the Chapter 13 "
            "account. Reuse that existing identity. Haskell's approximate birth year 1699 differs from the "
            "existing card's externally sourced exact date 1698-12-29; retain this as a source-level date "
            "discrepancy for later fact review, not as evidence of a second person. No external source was "
            f"accessed. Historical new-group and rationale retained: group={old_tail}"
        )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    same_after = grouped_ids(after_rows, "same")
    new_after = grouped_ids(after_rows, "new")
    assert after == Counter({"same": 1681, "new": 5000, "undecided": 5618, "excluded": 97, "conflict": 7}), after
    assert len(same_after) == 1019 and sum(len(ids) > 1 for ids in same_after.values()) == 270
    assert len(new_after) == 4827 and sum(len(ids) > 1 for ids in new_after.values()) == 134
    assert same_after[EXISTING_GROUP] == {EXISTING_CANDIDATE, *TARGETS}

    if args.dry_run:
        print(
            "dry-run passed: cand-0025,cand-0027,cand-0029 new->same existing Albrizzi KU; "
            f"same={before['same']}->{after['same']} new={before['new']}->{after['new']} "
            f"new_groups={len(new_before)}->{len(new_after)} multi_same=269->{sum(len(ids)>1 for ids in same_after.values())}; "
            f"manifest={len(manifest)}; birth-date discrepancy retained for later fact review"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-0025,cand-0027,cand-0029 -> units/persons/albrizzi; "
        f"S3 same={after['same']} new={after['new']} new_groups={len(new_after)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
