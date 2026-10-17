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
PAOLO_II_GROUP = "new-person:bracciano-giordona-ii-of-orsini-paolo-502da19f7d"
MULIER_KU = "units/persons/duke-bracciano-mulier"
PROCESS_REF = "S3-Bracciano-Paolo-Giordano-II-reconciliation-2026-10-16"
TARGET = "cand-0428"
GROUP_MEMBER = "cand-0434"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def normalized_text(path):
    return " ".join(path.read_text(encoding="utf-8-sig").split())


def main():
    parser = argparse.ArgumentParser(description="Separate Paolo Giordano II from the unresolved Mulier patron identity")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, alignments = read_csv(ALIGNMENT)
    _, candidates = read_csv(CANDIDATES)
    _, manifest = read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    assert len(manifest) == 1123
    assert manifest_by_id[MULIER_KU]["type"] == "person"
    assert manifest_by_id["units/persons/paolo-giordano-orsini"]["type"] == "person"
    assert candidate_by_id[TARGET]["suggested_type"] == "person"
    assert candidate_by_id[GROUP_MEMBER]["suggested_type"] == "person"
    assert candidate_by_id[TARGET]["canonical_name"] == candidate_by_id[GROUP_MEMBER]["canonical_name"]

    row = alignment_by_id[TARGET]
    other = alignment_by_id[GROUP_MEMBER]
    assert row["decision"] == "same" and row.get("ku_id") == MULIER_KU
    assert get_group(row["resolution_note"]) == "sg3-ku-units-persons-duke-bracciano-mulier"
    assert other["decision"] == "new" and not other.get("ku_id")
    assert get_group(other["resolution_note"]) == PAOLO_II_GROUP
    assert candidate_by_id[GROUP_MEMBER]["index_entry_id"] == "B.csv#281"

    ch4 = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_i.md"
    appendix = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md"
    postscript = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
    mulier_card = ROOT / "04-knowledge" / "units" / "persons" / "duke-bracciano-mulier.md"
    paolo_card = ROOT / "04-knowledge" / "units" / "persons" / "paolo-giordano-orsini.md"
    assert "Paolo Giordano II Orsini, Duke of Bracciano" in normalized_text(ch4)
    assert "Documents relating to commissions from Paolo Giordano Orsini, duke of Bracciano, to" in normalized_text(appendix)
    assert "bust of Paolo Giordano II Orsini, Duke of Bracciano" in normalized_text(postscript)
    assert "Two generations of Orsini dukes remain unresolved candidates." in mulier_card.read_text(encoding="utf-8-sig")
    assert "Paolo Giordano I Orsini" in paolo_card.read_text(encoding="utf-8-sig")

    current = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    current_counts = Counter(row["decision"] for row in current)
    assert current_counts == Counter({"same": 1675, "new": 5006, "undecided": 5618, "excluded": 97, "conflict": 7})
    new_rows = [row for row in current if row["decision"] == "new"]
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    for item in new_rows:
        group = get_group(item["resolution_note"])
        assert group
        new_groups[group].append(item)
        if item.get("ku_id"):
            registered[group].append(item)
    assert len(new_groups) == 4830
    assert set(r["candidate_id"] for r in new_groups[PAOLO_II_GROUP]) == {GROUP_MEMBER}
    assert (len([g for g, rs in registered.items() if rs]), sum(map(len, registered.values()))) == (104, 110)

    planned = [dict(item) for item in alignments]
    planned_by_id = {
        item["candidate_id"]: item for item in planned
        if item.get("candidate_id") and not item.get("external_source")
    }
    old_note = planned_by_id[TARGET]["resolution_note"]
    source_prefix = old_note.split("matched_manifest=", 1)[0].rstrip("; ")
    planned_by_id[TARGET]["decision"] = "new"
    planned_by_id[TARGET]["ku_id"] = ""
    planned_by_id[TARGET]["process_ref"] = PROCESS_REF
    planned_by_id[TARGET]["resolution_note"] = (
        f"{source_prefix}; cross_chapter_identity=Paolo Giordano II Orsini, Duke of Bracciano; "
        f"group={PAOLO_II_GROUP}; New: Chapter 4 and the Chapter 19 appendix name Paolo Giordano II Orsini "
        "in connection with the Duke of Bracciano; Chapter 20 again names Paolo Giordano II. This is the same "
        "full person as cand-0434 (B.csv#281), not the unnamed Duke of Bracciano who patronised Mulier: the "
        "existing Mulier card explicitly leaves that person unresolved between other Orsini candidates. Keep "
        "this person separate from the existing Paolo Giordano I Orsini KU. No external identity source was used. "
        f"Historical prior resolution note retained in full: {old_note}"
    )

    planned_current = [item for item in planned if item.get("candidate_id") and not item.get("external_source")]
    planned_counts = Counter(item["decision"] for item in planned_current)
    assert planned_counts == Counter({"same": 1674, "new": 5007, "undecided": 5618, "excluded": 97, "conflict": 7})
    planned_new = [item for item in planned_current if item["decision"] == "new"]
    planned_groups = defaultdict(list)
    for item in planned_new:
        planned_groups[get_group(item["resolution_note"])].append(item)
    assert len(planned_groups) == 4830
    assert set(item["candidate_id"] for item in planned_groups[PAOLO_II_GROUP]) == {TARGET, GROUP_MEMBER}
    assert (len([g for g, rs in planned_groups.items() if any(x.get("ku_id") for x in rs)]), sum(
        1 for item in planned_new if item.get("ku_id")
    )) == (104, 110)

    if args.dry_run:
        print("dry-run passed: cand-0428 same->new, grouped with cand-0434; same=1674 new=5007 groups=4830 manifest=1123")
        return 0

    write_csv(ALIGNMENT, fields, planned)
    print("applied: cand-0428,cand-0434 -> one Paolo Giordano II new group; existing Mulier patron KU kept distinct")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
