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
EXISTING_KU = "units/persons/caravaggio"
EXISTING_GROUP = "sg3-ku-units-persons-caravaggio"
EXISTING_CANDIDATES = {"cand-3010", "cand-7513"}
TARGETS = {"cand-0544", "cand-0545", "cand-0547", "cand-0549"}
OLD_NEW_GROUP = "new-person:caravaggio-da-michelangelo-ed41ab7f56"
PROCESS_REF = "S3-Caravaggio-cross-chapter-identity-reconciliation-2026-10-16"


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
    parser = argparse.ArgumentParser(description="Reuse the accepted Caravaggio person KU for four cross-chapter index candidates")
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
    assert manifest_row["card_path"] == "04-knowledge/units/persons/caravaggio.md"
    card_path = ROOT / manifest_row["card_path"]
    card_text = card_path.read_text(encoding="utf-8-sig")
    assert "title: 卡拉瓦乔（Caravaggio）" in card_text
    assert manifest_row["card_path"] in ACCEPTED.read_text(encoding="utf-8-sig")

    existing_rows = [row for row in decisions if row["candidate_id"] in EXISTING_CANDIDATES]
    assert {row["candidate_id"] for row in existing_rows} == EXISTING_CANDIDATES
    assert all(row["decision"] == "same" and row["ku_id"] == EXISTING_KU for row in existing_rows)
    same_before = grouped_ids(decisions, "same")
    assert same_before[EXISTING_GROUP] == EXISTING_CANDIDATES

    targets = [row for row in decisions if row["candidate_id"] in TARGETS]
    assert {row["candidate_id"] for row in targets} == TARGETS
    assert len(targets) == len(TARGETS)
    for target in targets:
        cid = target["candidate_id"]
        candidate = candidate_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "Caravaggio, Michelangelo da"
        assert target["decision"] == "new" and not target.get("ku_id"), cid
        assert get_group(target["resolution_note"]) == OLD_NEW_GROUP, cid
    expected_index = {
        "cand-0544": "C.csv#68",
        "cand-0545": "C.csv#69",
        "cand-0547": "C.csv#71",
        "cand-0549": "C.csv#73",
    }
    for cid, entry in expected_index.items():
        assert candidate_by_id[cid]["index_entry_id"] == entry

    chapter2 = (ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md").read_text(encoding="utf-8-sig")
    chapter3 = (ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md").read_text(encoding="utf-8-sig")
    chapter5 = (ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_i.md").read_text(encoding="utf-8-sig")
    assert "Michelangelo da Caravaggio" in chapter2
    assert "Caravaggio’s Death of the Virgin" in chapter5
    assert "Caravaggio of The Entombment" in chapter3
    assert "Caravaggio" in (ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_i.md").read_text(encoding="utf-8-sig")

    endpoint_count = Counter()
    relation_count = Counter()
    endpoint_statements = defaultdict(set)
    with STATEMENTS.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            for cid in TARGETS & {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_count[cid] += 1
                endpoint_statements[cid].add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_count[cid] += 1
    assert endpoint_count["cand-0544"] > 0 and endpoint_count["cand-0545"] > 0
    assert endpoint_count["cand-0549"] > 0 and endpoint_count["cand-0547"] == 0
    assert "m-chp5-p125-0013" in decision_by_id["cand-0547"]["resolution_note"]

    before = Counter(row["decision"] for row in decisions)
    new_before = grouped_ids(decisions, "new")
    assert before == Counter({"same": 1692, "new": 4989, "undecided": 5618, "excluded": 97, "conflict": 7}), before
    assert len(new_before) == 4820 and new_before[OLD_NEW_GROUP] == TARGETS

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}
    for cid in sorted(TARGETS):
        target = planned_by_id[cid]
        source_prefix, old_tail = target["resolution_note"].split("; group=", 1)
        target["decision"] = "same"
        target["ku_id"] = EXISTING_KU
        target["process_ref"] = PROCESS_REF
        target["resolution_note"] = (
            f"{source_prefix}; matched_manifest={EXISTING_KU}; "
            f"matched_candidate_ids={','.join(sorted(EXISTING_CANDIDATES))}; group={EXISTING_GROUP}; Same: "
            "The four full-book C-index entries name the person as 'Caravaggio, Michelangelo da'; their subentries "
            "and indexed pages are anchored in chapters 1-5 and the postscript. The accepted person KU at "
            "04-knowledge/units/persons/caravaggio.md is already in accepted.yml and the manifest. Its chapter-2 "
            "source anchor names Michelangelo da Caravaggio, and existing full-book candidate cand-3010 maps that "
            "full-name anchor to this KU; candidate cand-7513 independently reuses it from chapter 8. The chapter-3 "
            "and chapter-5 passages explicitly identify the Entombment and Death of the Virgin as works by "
            "Caravaggio, supporting the corresponding index subentries without creating separate person identities. "
            "Reuse the existing KU; no external source was accessed. Historical new-group decision and rationale "
            f"retained: group={old_tail}"
        )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    same_after = grouped_ids(after_rows, "same")
    new_after = grouped_ids(after_rows, "new")
    assert after == Counter({"same": 1696, "new": 4985, "undecided": 5618, "excluded": 97, "conflict": 7}), after
    assert len(same_after) == 1019 and same_after[EXISTING_GROUP] == EXISTING_CANDIDATES | TARGETS
    assert len(new_after) == 4819 and OLD_NEW_GROUP not in new_after

    registered = defaultdict(list)
    for row in after_rows:
        if row["decision"] == "new" and row.get("ku_id"):
            registered[get_group(row["resolution_note"])].append(row)
    assert (len(registered), sum(map(len, registered.values()))) == (120, 149)
    assert len(new_after) - len(registered) == 4699
    assert sum(len(ids) for ids in new_after.values()) - 149 == 4836

    if args.dry_run:
        print(
            "dry-run passed: four Caravaggio index candidates new->same existing accepted person KU; "
            f"statement_endpoints={sum(len(endpoint_statements[cid]) for cid in TARGETS)} "
            f"relation_candidate_mentions={sum(relation_count.values())} "
            f"same={before['same']}->{after['same']} new={before['new']}->{after['new']} "
            f"new_groups={len(new_before)}->{len(new_after)} registered_new_groups=120 mapped_new_candidates=149 "
            "pending_groups=4699 pending_candidates=4836; manifest/card unchanged"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-0544/0545/0547/0549 -> units/persons/caravaggio; "
        f"S3 same={after['same']} new={after['new']} pending_groups=4699 pending_candidates=4836; manifest/card unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
