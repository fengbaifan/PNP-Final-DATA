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
EXISTING_KU = "units/persons/giovanni-pietro-bellori"
EXISTING_GROUP = "sg3-ku-units-persons-giovanni-pietro-bellori"
OLD_NEW_GROUP = "new-person:bellori-gian-pietro-7d6292ead5"
MATCHED_EXISTING_CANDIDATE = "cand-3056"
TARGETS = ("cand-0272", "cand-0274", "cand-0277")
PROCESS_REF = "S3-Bellori-cross-chapter-reconciliation-2026-10-16"


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


def grouped_ids(rows, decision):
    groups = defaultdict(set)
    for row in rows:
        if row["decision"] == decision:
            group = get_group(row.get("resolution_note", ""))
            assert group, f"{decision} candidate lacks group: {row['candidate_id']}"
            groups[group].add(row["candidate_id"])
    return groups


def main():
    parser = argparse.ArgumentParser(description="Map the cross-chapter Gian Pietro Bellori candidates to the existing Bellori person KU")
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

    assert len(manifest) == 1126, f"unexpected manifest count: {len(manifest)}"
    assert manifest_by_id[EXISTING_KU]["type"] == "person"
    assert manifest_by_id[EXISTING_KU]["card_path"] == "04-knowledge/units/persons/giovanni-pietro-bellori.md"
    existing_card = (ROOT / "04-knowledge" / "units" / "persons" / "giovanni-pietro-bellori.md").read_text(encoding="utf-8-sig")
    assert "Giovanni Pietro Bellori" in existing_card
    assert "Giovanni／Giovan Pietro Bellori" in existing_card
    assert "Wikidata, Q714400" in existing_card

    for cid in TARGETS:
        candidate = candidate_by_id[cid]
        row = decision_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "Bellori, Gian Pietro"
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == OLD_NEW_GROUP
    assert {row["candidate_id"] for row in decision_rows if row["decision"] == "new" and get_group(row.get("resolution_note", "")) == OLD_NEW_GROUP} == set(TARGETS)
    assert decision_by_id[MATCHED_EXISTING_CANDIDATE]["decision"] == "same"
    assert decision_by_id[MATCHED_EXISTING_CANDIDATE]["ku_id"] == EXISTING_KU
    assert get_group(decision_by_id[MATCHED_EXISTING_CANDIDATE]["resolution_note"]) == EXISTING_GROUP

    chapter4 = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
    chapter6 = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_iv.md"
    chapter7 = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
    postscript = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
    assert "Both the Italian critic Bellori and the French historian Felibien codified their enthusiasm for Poussin into a dogma." in chapter4.read_text(encoding="utf-8-sig")
    ch6_text = chapter6.read_text(encoding="utf-8-sig")
    assert "was Gian Pietro Bellori." in ch6_text
    assert "Bellori’s Descrizione delle Immagini dipinte da" in ch6_text
    assert "when he published" in ch6_text and "these in 1672" in ch6_text
    assert "Bellori, 1976" in postscript.read_text(encoding="utf-8-sig")
    assert "Bellori" in chapter7.read_text(encoding="utf-8-sig")

    before_counts = Counter(row["decision"] for row in decision_rows)
    same_groups_before = grouped_ids(decision_rows, "same")
    new_groups_before = grouped_ids(decision_rows, "new")
    assert before_counts == Counter(
        {"same": 1675, "new": 5006, "undecided": 5618, "excluded": 97, "conflict": 7}
    ), f"unexpected decision counts before: {before_counts}"
    assert len(same_groups_before) == 1019 and sum(len(ids) > 1 for ids in same_groups_before.values()) == 268
    assert len(new_groups_before) == 4829 and sum(len(ids) > 1 for ids in new_groups_before.values()) == 136

    planned = [dict(row) for row in alignments]
    planned_decision_by_id = {
        row["candidate_id"]: row for row in candidate_decision_rows(planned)
    }
    for cid in TARGETS:
        row = planned_decision_by_id[cid]
        previous_note = row["resolution_note"]
        source_prefix, old_decision_tail = previous_note.split("; group=", 1)
        row["decision"] = "same"
        row["ku_id"] = EXISTING_KU
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"{source_prefix}; matched_manifest={EXISTING_KU}; "
            f"matched_candidate_ids={MATCHED_EXISTING_CANDIDATE}; group={EXISTING_GROUP}; "
            "Same: Chapter 6 p. 159 explicitly names Gian Pietro Bellori and identifies him as the author "
            "of the 1672 Lives and the Descrizione delle Immagini dipinte da Raffaello d’Urbino. "
            "The cross-chapter Bellori references in Chapters 4, 6, 7, and the Chapter 20 postscript "
            "match the existing Giovanni Pietro Bellori KU; its prior S3 mapping and Q714400 identity "
            f"evidence are already recorded for {MATCHED_EXISTING_CANDIDATE}. The Giovanni/Gian Pietro "
            "name variation is retained. Reuse the existing identity; no new external source was accessed. "
            f"Historical new-group and rationale retained: group={old_decision_tail}"
        )

    planned_decisions = candidate_decision_rows(planned)
    after_counts = Counter(row["decision"] for row in planned_decisions)
    same_groups_after = grouped_ids(planned_decisions, "same")
    new_groups_after = grouped_ids(planned_decisions, "new")
    assert after_counts == Counter(
        {"same": 1678, "new": 5003, "undecided": 5618, "excluded": 97, "conflict": 7}
    ), f"unexpected decision counts after: {after_counts}"
    assert len(same_groups_after) == 1019 and sum(len(ids) > 1 for ids in same_groups_after.values()) == 269
    assert len(new_groups_after) == 4828 and sum(len(ids) > 1 for ids in new_groups_after.values()) == 135
    for cid in TARGETS:
        assert planned_decision_by_id[cid]["decision"] == "same"
        assert planned_decision_by_id[cid]["ku_id"] == EXISTING_KU

    if args.dry_run:
        print(
            "dry-run passed: cand-0272,cand-0274,cand-0277 new->same existing Bellori KU; "
            f"same={before_counts['same']}->{after_counts['same']} "
            f"new={before_counts['new']}->{after_counts['new']} "
            f"new_groups={len(new_groups_before)}->{len(new_groups_after)} "
            f"multi_same_groups=268->{sum(len(ids) > 1 for ids in same_groups_after.values())}; "
            f"manifest={len(manifest)}"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-0272,cand-0274,cand-0277 -> units/persons/giovanni-pietro-bellori; "
        f"S3 same={after_counts['same']} new={after_counts['new']} new_groups={len(new_groups_after)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
