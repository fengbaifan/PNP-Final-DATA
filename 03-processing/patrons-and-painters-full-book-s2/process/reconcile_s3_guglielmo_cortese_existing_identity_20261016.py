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
EXISTING_KU = "units/persons/guglielmo-cortese"
EXISTING_GROUP = "sg3-ku-units-persons-guglielmo-cortese"
EXISTING_CANDIDATES = {"cand-3063", "cand-3480"}
OLD_NEW_GROUP = "new-person:borgognone-guglielmo-courtois-guillaume-d85d80e219"
TARGETS = ("cand-0401", "cand-0402")
PROCESS_REF = "S3-Guglielmo-Cortese-cross-chapter-reconciliation-2026-10-16"


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
        description="Map the Guglielmo Borgognone candidates to the existing Guglielmo Cortese person KU"
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
    manifest_row = manifest_by_id[EXISTING_KU]
    assert manifest_row["type"] == "person"
    assert manifest_row["card_path"] == "04-knowledge/units/persons/guglielmo-cortese.md"
    existing_card = (ROOT / manifest_row["card_path"]).read_text(encoding="utf-8-sig")
    assert "Guglielmo Cortese" in existing_card and "Jacques Courtois" in existing_card
    assert "兄弟" in existing_card

    for cid in TARGETS:
        candidate = candidate_by_id[cid]
        row = decision_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "Borgognone, Guglielmo (Guillaume Courtois)"
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == OLD_NEW_GROUP
    assert {
        row["candidate_id"]
        for row in decisions
        if row["decision"] == "new" and get_group(row.get("resolution_note", "")) == OLD_NEW_GROUP
    } == set(TARGETS)

    for cid in EXISTING_CANDIDATES:
        row = decision_by_id[cid]
        assert row["decision"] == "same" and row["ku_id"] == EXISTING_KU
        assert get_group(row["resolution_note"]) == EXISTING_GROUP
    jacques = decision_by_id["cand-0399"]
    assert jacques["decision"] == "new"
    assert get_group(jacques["resolution_note"]) == "new-person:borgognone-giacomo-courtois-jacques-e79bfdac5a"
    assert decision_by_id["cand-0400"]["decision"] == "undecided"

    chapter3 = (ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md").read_text(encoding="utf-8-sig")
    for quote in (
        "In 1657 a French painter, Jacques Courtois, had entered the Society.",
        "Courtois—or Giacomo Borgognone as the Italians called him—",
        "He and his brother Guglielmo painted much for Oliva",
        "Guglielmo\nBorgognone who was commissioned in 1668 to paint The Martyrdom of St. Andrew",
        "his Jesuit brother",
        "[Page 88]",
        "Giacomo. Gaulli was an equally obvious choice.",
    ):
        assert quote in chapter3, quote

    endpoints = Counter()
    with STATEMENTS.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            for cid in TARGETS:
                if cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                    endpoints[cid] += 1
    assert endpoints == Counter({"cand-0401": 1, "cand-0402": 3}), endpoints

    before = Counter(row["decision"] for row in decisions)
    same_before = grouped_ids(decisions, "same")
    new_before = grouped_ids(decisions, "new")
    assert before == Counter({"same": 1686, "new": 4995, "undecided": 5618, "excluded": 97, "conflict": 7}), before
    assert len(same_before) == 1019 and sum(len(ids) > 1 for ids in same_before.values()) == 272
    assert len(new_before) == 4825 and sum(len(ids) > 1 for ids in new_before.values()) == 133
    assert same_before[EXISTING_GROUP] == EXISTING_CANDIDATES

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}
    for cid in TARGETS:
        target = planned_by_id[cid]
        source_prefix, old_tail = target["resolution_note"].split("; group=", 1)
        target["decision"] = "same"
        target["ku_id"] = EXISTING_KU
        target["process_ref"] = PROCESS_REF
        target["resolution_note"] = (
            f"{source_prefix}; matched_manifest={EXISTING_KU}; "
            f"matched_candidate_ids={','.join(sorted(EXISTING_CANDIDATES))}; group={EXISTING_GROUP}; Same: "
            "Chapter 3 p. 79 explicitly names Guglielmo as Jacques Courtois/Giacomo Borgognone's brother "
            "and says they painted for Oliva; pp. 87 and 106 identify Guglielmo Borgognone and his Jesuit "
            "brother Giacomo. Existing Guglielmo Cortese KU is already supported by the same-source "
            "Guglielmo Cortese candidate cand-3480 and records Jacques Courtois as his brother. Reuse that "
            "person KU for Guglielmo; keep Jacques/Giacomo as a separate person. No new external source "
            f"was accessed. Historical new-group decision and rationale retained: group={old_tail}"
        )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    same_after = grouped_ids(after_rows, "same")
    new_after = grouped_ids(after_rows, "new")
    assert after == Counter({"same": 1688, "new": 4993, "undecided": 5618, "excluded": 97, "conflict": 7}), after
    assert len(same_after) == 1019 and sum(len(ids) > 1 for ids in same_after.values()) == 272
    assert len(new_after) == 4824 and sum(len(ids) > 1 for ids in new_after.values()) == 132
    assert same_after[EXISTING_GROUP] == EXISTING_CANDIDATES | set(TARGETS)

    registered = defaultdict(list)
    for row in after_rows:
        if row["decision"] == "new" and row.get("ku_id"):
            registered[get_group(row["resolution_note"])].append(row)
    assert (len(registered), sum(map(len, registered.values()))) == (112, 127)
    assert len(new_after) - len(registered) == 4712
    assert sum(len(ids) for ids in new_after.values()) - 127 == 4866

    if args.dry_run:
        print(
            "dry-run passed: cand-0401/cand-0402 new->same existing Guglielmo Cortese KU; "
            f"statement_endpoints={sum(endpoints.values())} same={before['same']}->{after['same']} "
            f"new={before['new']}->{after['new']} new_groups={len(new_before)}->{len(new_after)} "
            "registered_new_groups=112 mapped_new_candidates=127 pending_groups=4712 pending_candidates=4866; "
            "Jacques/Giacomo Courtois remains a separate person group; cand-0400 remains undecided"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-0401/cand-0402 -> units/persons/guglielmo-cortese; "
        f"S3 same={after['same']} new={after['new']} new_groups={len(new_after)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
