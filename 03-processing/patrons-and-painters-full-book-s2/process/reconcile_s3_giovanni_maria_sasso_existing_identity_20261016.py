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
EXISTING_KU = "units/persons/g-m-sasso"
EXISTING_GROUP = "sg3-ku-units-persons-g-m-sasso"
EXISTING_CANDIDATE = "cand-3776"
OLD_NEW_GROUP = "new-person:giuseppe-maria-sasso-53ab44c390"
TARGETS = ("cand-2364",)
PROCESS_REF = "S3-Sasso-cross-chapter-reconciliation-2026-10-16"


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
        description="Map the cross-chapter Sasso candidate to the existing Giovanni Maria Sasso person KU"
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

    assert len(manifest) == 1131, f"unexpected manifest count: {len(manifest)}"
    assert manifest_by_id[EXISTING_KU]["type"] == "person"
    assert manifest_by_id[EXISTING_KU]["card_path"] == "04-knowledge/units/persons/g-m-sasso.md"
    existing_card = (ROOT / "04-knowledge" / "units" / "persons" / "g-m-sasso.md").read_text(
        encoding="utf-8-sig"
    )
    assert "Giovanni Maria Sasso" in existing_card
    assert "G. M. Sasso" in existing_card
    assert "National Gallery Archive" in existing_card

    candidate = candidate_by_id[TARGETS[0]]
    row = decision_by_id[TARGETS[0]]
    assert candidate["suggested_type"] == "person"
    assert candidate["canonical_name"] == "Sasso, Giuseppe Maria"
    assert row["decision"] == "new" and not row.get("ku_id")
    assert get_group(row["resolution_note"]) == OLD_NEW_GROUP
    assert {
        item["candidate_id"]
        for item in decisions
        if item["decision"] == "new" and get_group(item.get("resolution_note", "")) == OLD_NEW_GROUP
    } == set(TARGETS)

    existing_row = decision_by_id[EXISTING_CANDIDATE]
    assert existing_row["decision"] == "same" and existing_row["ku_id"] == EXISTING_KU
    assert get_group(existing_row["resolution_note"]) == EXISTING_GROUP

    chapter16 = (ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md").read_text(encoding="utf-8-sig")
    chapter17 = (ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md").read_text(encoding="utf-8-sig")
    assert "In the very centre of this world was Giovan Maria Sasso (Plate 58), buying and selling" in chapter16
    assert "Giuseppe Maria Sasso" in chapter17
    assert "the painter and dealer G. A. Armarmi at once wrote to Giuseppe Maria Sasso" in chapter17
    assert "because he is almost the only man in" in chapter17

    endpoints = 0
    with STATEMENTS.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if TARGETS[0] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoints += 1
    assert endpoints == 40, f"unexpected S2 statement endpoints: {endpoints}"

    before = Counter(item["decision"] for item in decisions)
    same_before = grouped_ids(decisions, "same")
    new_before = grouped_ids(decisions, "new")
    assert before == Counter({"same": 1685, "new": 4996, "undecided": 5618, "excluded": 97, "conflict": 7}), before
    assert len(same_before) == 1019 and sum(len(ids) > 1 for ids in same_before.values()) == 271
    assert len(new_before) == 4826 and sum(len(ids) > 1 for ids in new_before.values()) == 133
    assert same_before[EXISTING_GROUP] == {EXISTING_CANDIDATE}

    planned = [dict(item) for item in alignments]
    planned_by_id = {item["candidate_id"]: item for item in decision_rows(planned)}
    target = planned_by_id[TARGETS[0]]
    source_prefix, old_tail = target["resolution_note"].split("; group=", 1)
    target["decision"] = "same"
    target["ku_id"] = EXISTING_KU
    target["process_ref"] = PROCESS_REF
    target["resolution_note"] = (
        f"{source_prefix}; matched_manifest={EXISTING_KU}; matched_candidate_ids={EXISTING_CANDIDATE}; "
        f"group={EXISTING_GROUP}; Same: Chapter 16 p. 373 names Giovan Maria Sasso as a Venetian dealer "
        "and collector; Chapter 17 p. 380 calls the correspondent Giuseppe Maria Sasso in the 1790 Manfrin "
        "context. Both page ranges occur under the single index entry S.csv#52, and the source describes a "
        "continuous Venetian art-dealing and collecting context. The existing person KU records Giovanni "
        "Maria Sasso from the G. M. Sasso portrait and already-mapped candidate cand-3776; its saved NGA "
        "archive descriptor concerns Sasso's 1787–1805 correspondence. Reuse the existing identity while "
        "preserving the source's Giovan/Giovanni/Giuseppe name variation; do not infer a corrected full name "
        f"or add biography from that variation. No new external source was accessed. Historical new-group "
        f"and rationale retained: group={old_tail}"
    )

    after_rows = decision_rows(planned)
    after = Counter(item["decision"] for item in after_rows)
    same_after = grouped_ids(after_rows, "same")
    new_after = grouped_ids(after_rows, "new")
    assert after == Counter({"same": 1686, "new": 4995, "undecided": 5618, "excluded": 97, "conflict": 7}), after
    assert len(same_after) == 1019 and sum(len(ids) > 1 for ids in same_after.values()) == 272
    assert len(new_after) == 4825 and sum(len(ids) > 1 for ids in new_after.values()) == 133
    assert same_after[EXISTING_GROUP] == {EXISTING_CANDIDATE, TARGETS[0]}

    registered = defaultdict(list)
    for item in after_rows:
        if item["decision"] == "new" and item.get("ku_id"):
            registered[get_group(item["resolution_note"])].append(item)
    assert (len(registered), sum(map(len, registered.values()))) == (112, 127)
    assert len(new_after) - len(registered) == 4713
    assert sum(len(ids) for ids in new_after.values()) - 127 == 4868

    if args.dry_run:
        print(
            "dry-run passed: cand-2364 new->same existing Giovanni Maria Sasso KU; "
            f"statement_endpoints={endpoints} same={before['same']}->{after['same']} "
            f"new={before['new']}->{after['new']} new_groups={len(new_before)}->{len(new_after)} "
            "registered_new_groups=112 mapped_new_candidates=127 pending_groups=4713 pending_candidates=4868; "
            "Giovan/Giovanni/Giuseppe source forms retained"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-2364 -> units/persons/g-m-sasso; "
        f"S3 same={after['same']} new={after['new']} new_groups={len(new_after)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
