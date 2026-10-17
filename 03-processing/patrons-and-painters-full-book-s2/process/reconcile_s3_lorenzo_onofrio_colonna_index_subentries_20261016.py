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
EXISTING_CARD = ROOT / "04-knowledge" / "units" / "persons" / "lorenzo-onofrio-colonna.md"
GROUP = "new-person:colonna-lorenzo-onofrio-c75ad3fea2"
MAIN = "cand-0811"
TARGETS = {"cand-0812", "cand-0813"}
PROCESS_REF = "S3-Lorenzo-Onofrio-Colonna-subentry-evidence-2026-10-16"


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
    parser = argparse.ArgumentParser(description="Resolve two evidence-anchored Lorenzo Onofrio Colonna index subentries")
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

    assert len(manifest) == 1140
    before = Counter(row["decision"] for row in decisions)
    assert before == Counter({"same": 1696, "new": 4985, "undecided": 5618, "excluded": 97, "conflict": 7}), before
    same_groups = grouped_ids(decisions, "same")
    new_groups = grouped_ids(decisions, "new")
    assert len(same_groups) == 1019 and sum(len(ids) > 1 for ids in same_groups.values()) == 276
    assert len(new_groups) == 4819 and sum(len(ids) > 1 for ids in new_groups.values()) == 131
    assert new_groups[GROUP] == {MAIN}
    assert {r["candidate_id"] for r in decisions if r["decision"] == "new" and r.get("ku_id")}.__len__() == 150
    assert {r["candidate_id"] for r in decisions if r["decision"] == "new" and r.get("ku_id") and get_group(r["resolution_note"]) == GROUP} == set()

    main = decision_by_id[MAIN]
    assert main["decision"] == "new" and not main.get("ku_id") and get_group(main["resolution_note"]) == GROUP
    expected = {
        "cand-0812": ("C.csv#342", "employment of Claude", "m-chp6-p156-003", "st-chp6-p156-claude-employment-taste", "his employment of Claude, ranging over a period of nearly twenty years"),
        "cand-0813": ("C.csv#343", "liking for mythological fables and landscapes", "m-chp6-p155-038", "st-chp6-p155-lorenzo-genre-preferences", "his greatest passion seems to have been for mythological fables and landscapes"),
    }
    for cid, (entry, subentry, mention_id, statement_id, phrase) in expected.items():
        candidate = candidate_by_id[cid]
        row = decision_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "Colonna, Lorenzo Onofrio"
        assert candidate["index_entry_id"] == entry and candidate["sub_entry"] == subentry
        assert row["decision"] == "undecided" and not row.get("ku_id")
        assert "s2_mentions=none" in row["resolution_note"]
        assert mention_id in main["resolution_note"]

    source_path = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md"
    source_text = source_path.read_text(encoding="utf-8-sig")
    assert "But the most interesting and influential patron of the family was Lorenzo Onofrio" in source_text
    assert "his employment of Claude, ranging over a period of nearly twenty years" in source_text
    assert "his greatest passion seems to have been for mythological fables and landscapes" in source_text
    assert "he subsequently commissioned from him a series of eight mythological scenes" in source_text

    statement_by_id = {}
    with STATEMENTS.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            statement_by_id[statement["statement_id"]] = statement
    for _, _, _, statement_id, _ in expected.values():
        statement = statement_by_id[statement_id]
        assert MAIN in {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}
        assert statement.get("qualifiers", {}).get("relation_candidate") is True

    # This tracked pre-existing draft is outside both accepted.yml and the manifest; S4 will update it in place.
    assert EXISTING_CARD.exists()
    draft_text = EXISTING_CARD.read_text(encoding="utf-8-sig")
    assert "title: 洛伦佐·奥诺弗里奥·科隆纳（Lorenzo Onofrio Colonna）" in draft_text
    assert not any(row["card_path"] == "04-knowledge/units/persons/lorenzo-onofrio-colonna.md" for row in manifest)

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}
    for cid, (entry, subentry, mention_id, statement_id, _) in expected.items():
        row = planned_by_id[cid]
        old_note = row["resolution_note"]
        row["decision"] = "new"
        row["ku_id"] = ""
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"source_ref=candidate={cid};index_entry={entry};index_page={candidate_by_id[cid]['index_page_range']};"
            f"sub_entry={subentry};s2_mentions={mention_id}@02-sources/02-Markdown/06_CHP-6_sec_i.md;"
            f"s2_statement={statement_id};group={GROUP}; New: this index subentry repeats the exact canonical person name "
            "'Colonna, Lorenzo Onofrio' used by the main entry cand-0811. Its page-specific subject matches the S2 body: "
            "the narrative names Lorenzo Onofrio on p. 155 and the p. 155-156 passage explicitly describes this same person's "
            f"{subentry} ({phrase}); the cited statement is already anchored to cand-0811. This direct body-to-subentry match "
            "supports a single source-defined person group rather than surname-only merging. No external source was accessed. "
            f"prior_decision=undecided; prior_resolution_note={old_note}"
        )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    same_after = grouped_ids(after_rows, "same")
    new_after = grouped_ids(after_rows, "new")
    assert after == Counter({"same": 1696, "new": 4987, "undecided": 5616, "excluded": 97, "conflict": 7}), after
    assert len(same_after) == 1019 and sum(len(ids) > 1 for ids in same_after.values()) == 276
    assert len(new_after) == 4819 and sum(len(ids) > 1 for ids in new_after.values()) == 132
    assert new_after[GROUP] == {MAIN} | TARGETS
    registered = defaultdict(set)
    for row in after_rows:
        if row["decision"] == "new" and row.get("ku_id"):
            registered[get_group(row["resolution_note"])].add(row["candidate_id"])
    assert (len(registered), sum(map(len, registered.values()))) == (121, 150)
    assert (len(new_after) - len(registered), sum(len(ids) for ids in new_after.values()) - sum(map(len, registered.values()))) == (4698, 4837)

    if args.dry_run:
        print(
            "dry-run passed: cand-0812/cand-0813 undecided->new in Lorenzo Onofrio group; "
            f"same={before['same']}->{after['same']} new={before['new']}->{after['new']} "
            f"undecided={before['undecided']}->{after['undecided']} groups={len(new_groups)} "
            f"multi_candidate_groups={sum(len(ids)>1 for ids in new_groups.values())}->132 "
            "existing registrations=121/150; pending groups=4698 candidates=4837; existing draft and manifest unchanged"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-0812/cand-0813 -> new-person:colonna-lorenzo-onofrio-c75ad3fea2; "
        f"new={after['new']} undecided={after['undecided']} groups={len(new_after)}; S4 not yet applied"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
