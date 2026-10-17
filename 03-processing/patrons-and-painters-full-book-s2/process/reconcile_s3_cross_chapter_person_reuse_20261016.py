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
PROCESS_REF = "S3-cross-chapter-person-reuse-2026-10-16"

RECONCILIATIONS = {
    "cand-1844": {
        "ku_id": "units/persons/pasquali",
        "existing_group": "sg3-ku-units-persons-pasquali",
        "existing_candidates": {"cand-3857"},
        "old_group": "new-person:giambattista-pasquali-d8a083f523",
        "canonical_name": "Pasquali, Giambattista",
        "card_path": "04-knowledge/units/persons/pasquali.md",
        "manifest_name_en": "Giovanni Battista Pasquali",
        "card_checks": ("Giovanni Battista Pasquali", "Giambattista Pasquali", "Treccani"),
        "source_checks": (
            ("10_CHP-10_intro.md", "launching the firm of a young man, G. B.\nPasquali."),
            ("10_CHP-10_intro.md", "his client Pasquali"),
            ("13_CHP-13_intro.md", "Giambattista Pasquali"),
        ),
        "endpoints": 33,
        "relation_candidates": 30,
        "reason": (
            "The Chapter 10 index form 'Pasquali, Giambattista' matches the existing KU's documented "
            "Giovanni Battista Pasquali and its Giambattista variant. Chapter 10 pp. 299–301 identifies "
            "G. B. Pasquali as the young publisher whose firm Joseph Smith launched and later calls him "
            "Smith's client; Chapter 13 pp. 334–338 continues the same Venetian publisher's activity. "
            "Reuse the existing person KU; the identity does not rest on surname similarity alone."
        ),
    },
    "cand-1325": {
        "ku_id": "units/persons/johann-wilhelm-elector-palatine",
        "existing_group": "sg3-ku-units-persons-johann-wilhelm-elector-palatine",
        "existing_candidates": {"cand-3812"},
        "old_group": "new-person:elector-johann-palatinate-wilhelm-b5477ca163",
        "canonical_name": "Johann Wilhelm, Elector Palatinate",
        "card_path": "04-knowledge/units/persons/johann-wilhelm-elector-palatine.md",
        "manifest_name_en": "Johann Wilhelm, Elector Palatine",
        "card_checks": ("Johann Wilhelm, Elector Palatine", "GND 118712411"),
        "source_checks": (
            ("10_CHP-10_intro.md", "ruled over by the Elector Johann Wilhelm"),
            ("10_CHP-10_intro.md", "Johann Wilhelm came to power in 1690"),
        ),
        "endpoints": 34,
        "relation_candidates": 29,
        "reason": (
            "Chapter 10 p. 281 explicitly names the Elector Johann Wilhelm and p. 282 continues with "
            "Johann Wilhelm's rule; the candidate's full personal name and title match the existing "
            "Johann Wilhelm, Elector Palatine KU, whose identity is supported by Deutsche Biographie "
            "GND 118712411. Reuse that person KU."
        ),
    },
    "cand-2426": {
        "ku_id": "units/persons/anthony-ashley-cooper-3rd-earl",
        "existing_group": "sg3-ku-units-persons-anthony-ashley-cooper-3rd-earl",
        "existing_candidates": {"cand-3378"},
        "old_group": "new-person:3rd-of-shaftesbury-82bbccfee5",
        "canonical_name": "Shaftesbury, 3rd Earl of",
        "card_path": "04-knowledge/units/persons/anthony-ashley-cooper-3rd-earl.md",
        "manifest_name_en": "Anthony Ashley-Cooper, 3rd Earl of Shaftesbury",
        "card_checks": ("Anthony Ashley-Cooper, 3rd Earl of Shaftesbury", "3rd Earl of Shaftesbury"),
        "source_checks": (
            ("07_CHP-7_sec_iv.md", "the 3rd Earl of Shaftesbury"),
            ("05_CHP-5_sec_iv.md", "Lord Shaftesbury"),
        ),
        "endpoints": 29,
        "relation_candidates": 27,
        "reason": (
            "Chapter 7 p. 198 identifies the theorist as the 3rd Earl of Shaftesbury, and Chapter 5 "
            "and other passages use Lord Shaftesbury in the same art-patronage context. The index title "
            "matches the existing Anthony Ashley-Cooper, 3rd Earl of Shaftesbury KU and its full name; "
            "reuse that person KU."
        ),
    },
}


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
        description="Reconcile three cross-chapter person candidates to existing person KUs"
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

    assert len(manifest) == 1134, f"unexpected manifest count: {len(manifest)}"
    before = Counter(row["decision"] for row in decisions)
    assert before == Counter({"same": 1688, "new": 4993, "undecided": 5618, "excluded": 97, "conflict": 7}), before
    same_before = grouped_ids(decisions, "same")
    new_before = grouped_ids(decisions, "new")
    assert len(same_before) == 1019 and sum(len(ids) > 1 for ids in same_before.values()) == 272
    assert len(new_before) == 4824 and sum(len(ids) > 1 for ids in new_before.values()) == 132

    registered_before = defaultdict(set)
    for row in decisions:
        if row["decision"] == "new" and row.get("ku_id"):
            registered_before[get_group(row["resolution_note"])].add(row["candidate_id"])
    assert (len(registered_before), sum(map(len, registered_before.values()))) == (115, 134)

    endpoint_counts = Counter()
    relation_counts = Counter()
    with STATEMENTS.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            for cid in RECONCILIATIONS:
                if cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                    endpoint_counts[cid] += 1
                    if statement.get("qualifiers", {}).get("relation_candidate") is True:
                        relation_counts[cid] += 1

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}
    for cid, spec in RECONCILIATIONS.items():
        candidate = candidate_by_id[cid]
        target = decision_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == spec["canonical_name"]
        assert target["decision"] == "new" and not target.get("ku_id")
        assert get_group(target["resolution_note"]) == spec["old_group"]
        assert new_before[spec["old_group"]] == {cid}, f"target group is not a singleton: {cid}"
        assert endpoint_counts[cid] == spec["endpoints"], (cid, endpoint_counts[cid])
        assert relation_counts[cid] == spec["relation_candidates"], (cid, relation_counts[cid])

        manifest_row = manifest_by_id[spec["ku_id"]]
        assert manifest_row["type"] == "person"
        assert manifest_row["card_path"] == spec["card_path"]
        assert manifest_row["name_en"] == spec["manifest_name_en"]
        card = (ROOT / spec["card_path"]).read_text(encoding="utf-8-sig")
        for marker in spec["card_checks"]:
            assert marker.casefold() in card.casefold(), (cid, marker)

        existing = set()
        for existing_cid in spec["existing_candidates"]:
            existing_row = decision_by_id[existing_cid]
            assert existing_row["decision"] == "same" and existing_row["ku_id"] == spec["ku_id"]
            assert get_group(existing_row["resolution_note"]) == spec["existing_group"]
            existing.add(existing_cid)
        assert same_before[spec["existing_group"]] == existing

        for filename, quote in spec["source_checks"]:
            source = ROOT / "02-sources" / "02-Markdown" / filename
            assert quote in source.read_text(encoding="utf-8-sig"), (cid, filename, quote)

        target_plan = planned_by_id[cid]
        source_prefix, old_tail = target_plan["resolution_note"].split("; group=", 1)
        target_plan["decision"] = "same"
        target_plan["ku_id"] = spec["ku_id"]
        target_plan["process_ref"] = PROCESS_REF
        target_plan["resolution_note"] = (
            f"{source_prefix}; matched_manifest={spec['ku_id']}; "
            f"matched_candidate_ids={','.join(sorted(spec['existing_candidates']))}; "
            f"group={spec['existing_group']}; Same: {spec['reason']} "
            "No new external source was accessed. Historical new-group decision and rationale retained: "
            f"group={old_tail}"
        )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    assert after == Counter({"same": 1691, "new": 4990, "undecided": 5618, "excluded": 97, "conflict": 7}), after
    same_after = grouped_ids(after_rows, "same")
    new_after = grouped_ids(after_rows, "new")
    assert len(same_after) == 1019 and sum(len(ids) > 1 for ids in same_after.values()) == 275
    assert len(new_after) == 4821 and sum(len(ids) > 1 for ids in new_after.values()) == 132
    for cid, spec in RECONCILIATIONS.items():
        assert same_after[spec["existing_group"]] == spec["existing_candidates"] | {cid}

    registered_after = defaultdict(set)
    for row in after_rows:
        if row["decision"] == "new" and row.get("ku_id"):
            registered_after[get_group(row["resolution_note"])].add(row["candidate_id"])
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (115, 134)
    pending_groups = len(new_after) - len(registered_after)
    pending_candidates = sum(map(len, new_after.values())) - sum(map(len, registered_after.values()))
    assert (pending_groups, pending_candidates) == (4706, 4856)

    if args.dry_run:
        for cid, spec in RECONCILIATIONS.items():
            print(
                f"dry-run passed: {cid} new->same {spec['ku_id']} "
                f"statement_endpoints={endpoint_counts[cid]} relation_candidates={relation_counts[cid]}"
            )
        print(
            f"S3 same={before['same']}->{after['same']} new={before['new']}->{after['new']} "
            f"new_groups={len(new_before)}->{len(new_after)} registered_groups=115 mapped_candidates=134 "
            f"pending_groups={pending_groups} pending_candidates={pending_candidates}; "
            "historical new-group rationales preserved"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        f"applied: {', '.join(RECONCILIATIONS)} -> existing person KUs; "
        f"S3 same={after['same']} new={after['new']} new_groups={len(new_after)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
