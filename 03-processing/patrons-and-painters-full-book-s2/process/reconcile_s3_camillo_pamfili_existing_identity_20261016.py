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
EXISTING_KU = "units/persons/camillo-pamfili"
EXISTING_GROUP = "sg3-ku-units-persons-camillo-pamfili"
OLD_NEW_GROUP = "new-person:camillo-pamfili-b8a79487fa"
TARGET = "cand-1814"
MATCHED_EXISTING_CANDIDATE = "cand-3009"
UNDECIDED_INDEX_CANDIDATE = "cand-1815"
PROCESS_REF = "S3-Camillo-Pamfili-cross-chapter-reconciliation-2026-10-16"


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
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def new_group_count(rows):
    groups = defaultdict(list)
    for row in rows:
        if row["decision"] == "new":
            group = get_group(row.get("resolution_note", ""))
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            groups[group].append(row["candidate_id"])
    return len(groups), groups


def main():
    parser = argparse.ArgumentParser(
        description="Map the cross-chapter Prince Camillo Pamfili candidate to its existing person KU"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT)
    _, candidates = read_csv(CANDIDATES)
    _, manifest = read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_rows = candidate_decision_rows(alignments)
    decision_by_id = {row["candidate_id"]: row for row in decision_rows}
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert len(manifest) == 1124, f"unexpected manifest count: {len(manifest)}"
    assert manifest_by_id[EXISTING_KU]["type"] == "person"
    assert manifest_by_id[EXISTING_KU]["card_path"] == "04-knowledge/units/persons/camillo-pamfili.md"
    assert candidate_by_id[TARGET]["suggested_type"] == "person"
    assert candidate_by_id[TARGET]["canonical_name"] == "Pamfili, Prince Camillo (nephew to Pope Innocent X)"
    assert decision_by_id[TARGET]["decision"] == "new"
    assert not decision_by_id[TARGET].get("ku_id")
    assert get_group(decision_by_id[TARGET]["resolution_note"]) == OLD_NEW_GROUP
    assert candidate_by_id[MATCHED_EXISTING_CANDIDATE]["suggested_type"] == "person"
    assert decision_by_id[MATCHED_EXISTING_CANDIDATE]["decision"] == "same"
    assert decision_by_id[MATCHED_EXISTING_CANDIDATE]["ku_id"] == EXISTING_KU
    assert get_group(decision_by_id[MATCHED_EXISTING_CANDIDATE]["resolution_note"]) == EXISTING_GROUP
    assert decision_by_id[UNDECIDED_INDEX_CANDIDATE]["decision"] == "undecided"
    assert "s2_mentions=none" in decision_by_id[UNDECIDED_INDEX_CANDIDATE]["resolution_note"]
    assert set(
        row["candidate_id"] for row in decision_rows
        if row["decision"] == "new" and get_group(row.get("resolution_note", "")) == OLD_NEW_GROUP
    ) == {TARGET}

    chapter1 = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
    chapter3 = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
    chapter6 = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md"
    existing_card = ROOT / "04-knowledge" / "units" / "persons" / "camillo-pamfili.md"
    ch1_text = chapter1.read_text(encoding="utf-8-sig")
    ch3_text = chapter3.read_text(encoding="utf-8-sig")
    ch6_text = chapter6.read_text(encoding="utf-8-sig")
    card_text = existing_card.read_text(encoding="utf-8-sig")
    assert "to Camillo Pamfili with suggestions for the decoration of his villa at Valmontone" in ch1_text
    assert "By far the largest sum was given by Prince Camillo Pamfili, nephew of Pope Innocent" in ch3_text
    assert "For Camillo Pamfili see later, Chapter 6" in ch3_text
    assert "authentic Prince" in ch6_text and "Pamfili" in ch6_text and "Camillo Astalli" in ch6_text
    assert "Camillo Francesco Maria Pamphili" in card_text
    assert "existing_KU_card=04-knowledge/units/persons/camillo-pamfili.md" in " ".join(
        row["resolution_note"] for row in decision_rows if row["candidate_id"] == MATCHED_EXISTING_CANDIDATE
    )

    before_counts = Counter(row["decision"] for row in decision_rows)
    before_groups, _ = new_group_count(decision_rows)
    assert before_counts == Counter(
        {"same": 1674, "new": 5007, "undecided": 5618, "excluded": 97, "conflict": 7}
    ), f"unexpected decision counts before: {before_counts}"
    assert before_groups == 4830, f"unexpected new groups before: {before_groups}"

    previous_note = decision_by_id[TARGET]["resolution_note"]
    source_prefix, old_decision_tail = previous_note.split("; group=", 1)
    planned = [dict(row) for row in alignments]
    planned_decision_by_id = {
        row["candidate_id"]: row for row in candidate_decision_rows(planned)
    }
    target = planned_decision_by_id[TARGET]
    target["decision"] = "same"
    target["ku_id"] = EXISTING_KU
    target["process_ref"] = PROCESS_REF
    target["resolution_note"] = (
        f"{source_prefix}; matched_manifest={EXISTING_KU}; "
        f"matched_candidate_ids={MATCHED_EXISTING_CANDIDATE}; group={EXISTING_GROUP}; "
        "Same: Chapter 1 pp. 7–9 identifies Prince Pamfili/Camillo Pamfili in the Valmontone "
        "employment and correspondence context; Chapter 3 p. 106 names Prince Camillo Pamfili "
        "as Innocent X's nephew and points forward to Chapter 6; Chapter 6 pp. 147–150 "
        "distinguishes the authentic Prince Camillo from Camillo Astalli. These internal anchors "
        "match the existing Camillo Francesco Maria Pamphili person KU and the previously mapped "
        f"candidate {MATCHED_EXISTING_CANDIDATE}. Reuse the existing identity; no new KU or "
        "external identity check was made. The separate index-only {UNDECIDED_INDEX_CANDIDATE} "
        "remains undecided because it has no mapped S2 mention. Historical new-group and rationale "
        f"retained: group={old_decision_tail}"
    )

    planned_decisions = candidate_decision_rows(planned)
    after_counts = Counter(row["decision"] for row in planned_decisions)
    after_groups, _ = new_group_count(planned_decisions)
    assert after_counts == Counter(
        {"same": 1675, "new": 5006, "undecided": 5618, "excluded": 97, "conflict": 7}
    ), f"unexpected decision counts after: {after_counts}"
    assert after_groups == 4829, f"unexpected new groups after: {after_groups}"
    assert planned_decision_by_id[TARGET]["ku_id"] == EXISTING_KU
    assert planned_decision_by_id[UNDECIDED_INDEX_CANDIDATE]["decision"] == "undecided"

    if args.dry_run:
        print(
            "dry-run passed: cand-1814 new->same existing Camillo KU; "
            f"same={before_counts['same']}->{after_counts['same']} "
            f"new={before_counts['new']}->{after_counts['new']} "
            f"new_groups={before_groups}->{after_groups}; manifest={len(manifest)}; "
            "cand-1815 remains undecided"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-1814 -> units/persons/camillo-pamfili; "
        f"S3 same={after_counts['same']} new={after_counts['new']} new_groups={after_groups}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
