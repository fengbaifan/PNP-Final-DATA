from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ALIGNMENT = ROOT / "04-knowledge" / "tables" / "alignment.csv"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MANIFEST = ROOT / "04-knowledge" / "tables" / "ku-manifest.csv"
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
EXISTING_KU = "units/persons/marchese-del-carpio"
EXISTING_GROUP = "sg3-ku-units-persons-marchese-del-carpio"
EXISTING_CANDIDATE = "cand-3076"
OLD_NEW_GROUP = "new-person:carpio-del-carpio-del-s-6b4329a11f"
TARGETS = ("cand-0569", "cand-0570", "cand-0571", "cand-0573")
PROCESS_REF = "S3-Del-Carpio-cross-chapter-reconciliation-2026-10-16"


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
    match = re.search(r"group=([^;| ]+)", note or "")
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
    parser = argparse.ArgumentParser(
        description="Map the cross-chapter Marchese del Carpio candidates to the existing person KU"
    )
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

    assert len(manifest) == 1130, f"unexpected manifest count: {len(manifest)}"
    assert manifest_by_id[EXISTING_KU]["type"] == "person"
    assert manifest_by_id[EXISTING_KU]["card_path"] == "04-knowledge/units/persons/marchese-del-carpio.md"
    existing_card = (ROOT / "04-knowledge" / "units" / "persons" / "marchese-del-carpio.md").read_text(
        encoding="utf-8-sig"
    )
    assert "Gaspar Méndez de Haro" in existing_card
    assert "7th Marquess of Carpio" in existing_card

    for candidate_id in TARGETS:
        candidate = candidate_by_id[candidate_id]
        row = decision_by_id[candidate_id]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "Carpio, Marchese Del"
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == OLD_NEW_GROUP
    assert {
        row["candidate_id"]
        for row in decisions
        if row["decision"] == "new" and get_group(row.get("resolution_note", "")) == OLD_NEW_GROUP
    } == set(TARGETS)

    existing_row = decision_by_id[EXISTING_CANDIDATE]
    assert existing_row["decision"] == "same" and existing_row["ku_id"] == EXISTING_KU
    assert get_group(existing_row["resolution_note"]) == EXISTING_GROUP

    chapter7 = (ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md").read_text(encoding="utf-8-sig")
    assert "Don Gasparo de Haro y Guzman, known in Italy as the Marchese del\nCarpio, was appointed ambassador in Rome in 1677" in chapter7
    assert "brief administration made the first serious attempt to tackle these evils" in chapter7

    target_endpoints = 0
    with STATEMENTS.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if set(TARGETS).intersection(
                {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}
            ):
                target_endpoints += 1
    assert target_endpoints == 45, f"unexpected S2 statement endpoints: {target_endpoints}"

    before = Counter(row["decision"] for row in decisions)
    same_before = grouped_ids(decisions, "same")
    new_before = grouped_ids(decisions, "new")
    assert before == Counter({"same": 1681, "new": 5000, "undecided": 5618, "excluded": 97, "conflict": 7}), before
    assert len(same_before) == 1019 and sum(len(ids) > 1 for ids in same_before.values()) == 270
    assert len(new_before) == 4827 and sum(len(ids) > 1 for ids in new_before.values()) == 134

    registered_before = defaultdict(list)
    for row in decisions:
        if row["decision"] == "new" and row.get("ku_id"):
            registered_before[get_group(row["resolution_note"])].append(row)
    assert (len(registered_before), sum(map(len, registered_before.values()))) == (111, 126)
    for group, members in registered_before.items():
        assert len(members) == len(new_before[group]) and len({row["ku_id"] for row in members}) == 1, group

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}
    for candidate_id in TARGETS:
        row = planned_by_id[candidate_id]
        source_prefix, old_tail = row["resolution_note"].split("; group=", 1)
        row["decision"] = "same"
        row["ku_id"] = EXISTING_KU
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"{source_prefix}; matched_manifest={EXISTING_KU}; matched_candidate_ids={EXISTING_CANDIDATE}; "
            f"group={EXISTING_GROUP}; Same: Chapter 7 p. 190 explicitly names Don Gasparo de Haro y Guzman "
            "as the Marchese del Carpio; pp. 191–192 continue the same ambassador and viceroy's Roman and "
            "Neapolitan patronage and administration. The existing person KU is titled Gaspar Méndez de Haro, "
            "7th Marquess of Carpio, and candidate cand-3076 already maps that card in the same S3 identity "
            "group. The book's full name and explicit title identification support reuse; no new external source "
            f"was accessed. Historical new-group and rationale retained: group={old_tail}"
        )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    same_after = grouped_ids(after_rows, "same")
    new_after = grouped_ids(after_rows, "new")
    assert after == Counter({"same": 1685, "new": 4996, "undecided": 5618, "excluded": 97, "conflict": 7}), after
    assert len(same_after) == 1019 and sum(len(ids) > 1 for ids in same_after.values()) == 271
    assert len(new_after) == 4826 and sum(len(ids) > 1 for ids in new_after.values()) == 133
    assert same_after[EXISTING_GROUP] == {EXISTING_CANDIDATE, *TARGETS}
    assert {row["candidate_id"] for row in after_rows if row["decision"] == "undecided"}.issuperset(
        {"cand-0572", "cand-0574"}
    )

    registered_after = defaultdict(list)
    for row in after_rows:
        if row["decision"] == "new" and row.get("ku_id"):
            registered_after[get_group(row["resolution_note"])].append(row)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (111, 126)
    assert len(new_after) - len(registered_after) == 4715
    assert sum(len(ids) for ids in new_after.values()) - 126 == 4870

    if args.dry_run:
        print(
            "dry-run passed: cand-0569,cand-0570,cand-0571,cand-0573 new->same existing Carpio KU; "
            f"statement_endpoints={target_endpoints} same={before['same']}->{after['same']} "
            f"new={before['new']}->{after['new']} new_groups={len(new_before)}->{len(new_after)} "
            "registered_new_groups=111 mapped_new_candidates=126 pending_groups=4715 pending_candidates=4870; "
            "index-only cand-0572,cand-0574 remain undecided"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-0569,cand-0570,cand-0571,cand-0573 -> units/persons/marchese-del-carpio; "
        f"S3 same={after['same']} new={after['new']} new_groups={len(new_after)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
