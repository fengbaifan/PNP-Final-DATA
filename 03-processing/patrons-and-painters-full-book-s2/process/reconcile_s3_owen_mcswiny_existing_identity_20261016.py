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
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
EXISTING_KU = "units/persons/owen-mcswiny"
EXISTING_GROUP = "sg3-ku-units-persons-owen-mcswiny"
EXISTING_CANDIDATES = {"cand-3853"}
OLD_NEW_GROUP = "new-person:mcswiny-owen-63fc610cd9"
TARGET = "cand-1466"
PROCESS_REF = "S3-Owen-McSwiny-cross-task-identity-reconciliation-2026-10-16"


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
        description="Map the full-book Owen McSwiny candidate to the existing accepted person KU"
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

    assert len(manifest) == 1139, f"unexpected manifest count: {len(manifest)}"
    manifest_row = manifest_by_id[EXISTING_KU]
    assert manifest_row["type"] == "person"
    assert manifest_row["card_path"] == "04-knowledge/units/persons/owen-mcswiny.md"
    card_path = ROOT / manifest_row["card_path"]
    assert "Owen MacSwinny" in card_path.read_text(encoding="utf-8-sig")
    assert "Portrait of Owen McSwiny" in card_path.read_text(encoding="utf-8-sig")
    assert "MacSwinny (or Swinny)" in card_path.read_text(encoding="utf-8-sig")
    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    assert manifest_row["card_path"] in accepted_text

    target = decision_by_id[TARGET]
    candidate = candidate_by_id[TARGET]
    assert candidate["suggested_type"] == "person"
    assert candidate["index_entry_id"] == "M.csv#3"
    assert candidate["canonical_name"] == "McSwiny, Owen"
    assert target["decision"] == "new" and not target.get("ku_id")
    assert get_group(target["resolution_note"]) == OLD_NEW_GROUP
    assert {
        row["candidate_id"] for row in decisions
        if row["decision"] == "new" and get_group(row.get("resolution_note", "")) == OLD_NEW_GROUP
    } == {TARGET}

    existing_rows = [row for row in decisions if row["candidate_id"] in EXISTING_CANDIDATES]
    assert len(existing_rows) == 1
    existing = existing_rows[0]
    assert existing["decision"] == "same" and existing["ku_id"] == EXISTING_KU
    assert get_group(existing["resolution_note"]) == EXISTING_GROUP

    # The adjacent index subentries keep their existing S3 decisions; the pamphlet is a distinct archive group.
    for cid in ("cand-1467", "cand-1468", "cand-1469", "cand-1470", "cand-1471", "cand-1472", "cand-1474"):
        assert decision_by_id[cid]["decision"] == "undecided" and not decision_by_id[cid].get("ku_id"), cid
    pamphlet_candidate = candidate_by_id["cand-1473"]
    pamphlet_alignment = decision_by_id["cand-1473"]
    assert pamphlet_candidate["suggested_type"] == "archive"
    assert pamphlet_alignment["decision"] == "new" and not pamphlet_alignment.get("ku_id")
    assert get_group(pamphlet_alignment["resolution_note"]) == "archive-group-mcswiny-ladies-gentlemen-pamphlet"

    chapter10 = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    plate_list = (ROOT / "02-sources" / "02-Markdown" / "00_05_List_of_Plates.md").read_text(encoding="utf-8-sig")
    plate_transcription = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro_plates_visual-transcription.md").read_text(encoding="utf-8-sig")
    assert "Owen McSwiny (Plate 52a) was an Irishman" in chapter10
    assert "McSwiny spelt his name in a great number of different ways" in chapter10
    assert "P. Van Bleek: Owen McSwiny" in plate_list
    assert "Owen McSwiney" in plate_transcription

    endpoints = Counter()
    relation_endpoints = Counter()
    with STATEMENTS.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if TARGET in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoints[TARGET] += 1
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_endpoints[TARGET] += 1
    assert endpoints[TARGET] == 28 and relation_endpoints[TARGET] == 16, (endpoints, relation_endpoints)

    before = Counter(row["decision"] for row in decisions)
    same_before = grouped_ids(decisions, "same")
    new_before = grouped_ids(decisions, "new")
    assert before == Counter({"same": 1691, "new": 4990, "undecided": 5618, "excluded": 97, "conflict": 7}), before
    assert len(same_before) == 1019 and sum(len(ids) > 1 for ids in same_before.values()) == 275
    assert len(new_before) == 4821 and sum(len(ids) > 1 for ids in new_before.values()) == 132
    assert same_before[EXISTING_GROUP] == EXISTING_CANDIDATES

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}
    target = planned_by_id[TARGET]
    source_prefix, old_tail = target["resolution_note"].split("; group=", 1)
    target["decision"] = "same"
    target["ku_id"] = EXISTING_KU
    target["process_ref"] = PROCESS_REF
    target["resolution_note"] = (
        f"{source_prefix}; matched_manifest={EXISTING_KU}; "
        f"matched_candidate_ids={','.join(sorted(EXISTING_CANDIDATES))}; group={EXISTING_GROUP}; Same: "
        "The full-book main-entry candidate M.csv#3 names Owen McSwiny and is explicitly anchored in Chapter 10, "
        "with the same person revisited in the Chapter 20 postscript. The accepted front-matter person KU at "
        "04-knowledge/units/persons/owen-mcswiny.md records Owen MacSwinny and is supported by the same Plate 52a "
        "portrait: the full-book plate list names Owen McSwiny, the plate transcription includes Owen McSwiney, "
        "and the existing card records MacSwinny (or Swinny). Haskell notes that McSwiny spelled his name in "
        "different ways; this supports reuse of the accepted portrait-sitter KU rather than a duplicate person. "
        "No new external source was accessed. Historical new-group decision and rationale retained: group="
        f"{old_tail}"
    )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    same_after = grouped_ids(after_rows, "same")
    new_after = grouped_ids(after_rows, "new")
    assert after == Counter({"same": 1692, "new": 4989, "undecided": 5618, "excluded": 97, "conflict": 7}), after
    assert len(same_after) == 1019 and sum(len(ids) > 1 for ids in same_after.values()) == 276
    assert len(new_after) == 4820 and sum(len(ids) > 1 for ids in new_after.values()) == 132
    assert same_after[EXISTING_GROUP] == EXISTING_CANDIDATES | {TARGET}

    registered = defaultdict(list)
    for row in after_rows:
        if row["decision"] == "new" and row.get("ku_id"):
            registered[get_group(row["resolution_note"])].append(row)
    assert (len(registered), sum(map(len, registered.values()))) == (120, 149)
    assert len(new_after) - len(registered) == 4700
    assert sum(len(ids) for ids in new_after.values()) - 149 == 4840

    if args.dry_run:
        print(
            "dry-run passed: cand-1466 new->same existing Owen MacSwinny KU; "
            f"statement_endpoints={endpoints[TARGET]} relation_candidates={relation_endpoints[TARGET]} "
            f"same={before['same']}->{after['same']} new={before['new']}->{after['new']} "
            f"new_groups={len(new_before)}->{len(new_after)} registered_new_groups=120 "
            "mapped_new_candidates=149 pending_groups=4700 pending_candidates=4840; "
            "adjacent undecided entries and separate archive group remain unchanged"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-1466 -> units/persons/owen-mcswiny; "
        f"S3 same={after['same']} new={after['new']} new_groups={len(new_after)}; manifest unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
