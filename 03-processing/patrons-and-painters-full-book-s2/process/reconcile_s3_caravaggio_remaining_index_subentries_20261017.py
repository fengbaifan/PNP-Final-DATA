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
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
KU_ID = "units/persons/caravaggio"
GROUP = "sg3-ku-units-persons-caravaggio"
PROCESS_REF = "S3-Caravaggio-index-subentries-identity-reconciliation-2026-10-17"
TARGETS = {
    "cand-0546": {
        "index": "C.csv#70",
        "subentry": "Conversion of St Paul",
        "pages": "11",
        "anchor": "02-sources/02-Markdown/01_CHP-1.md#L397-401 (print p.11)",
        "evidence": "The p.11 passage names Caravaggio as the artist who agreed with his patron before executing The Conversion of St Paul.",
    },
    "cand-0548": {
        "index": "C.csv#72",
        "subentry": "Earthly Love",
        "pages": "127",
        "anchor": "02-sources/02-Markdown/05_CHP-5_sec_i.md#L80 (print p.127)",
        "evidence": "The p.127 passage names 'Michelangelo da Caravaggio's Earthly Love'.",
    },
    "cand-0550": {
        "index": "C.csv#74",
        "subentry": "Martyrdom of St Peter",
        "pages": "11",
        "anchor": "02-sources/02-Markdown/01_CHP-1.md#L397-401 (print p.11)",
        "evidence": "The p.11 passage names Caravaggio as the artist who agreed with his patron before executing The Martyrdom of St Peter.",
    },
    "cand-0551": {
        "index": "C.csv#75",
        "subentry": "portrait of Maffeo Barberini",
        "pages": "25",
        "anchor": "02-sources/02-Markdown/02_CHP-2_sec_i.md#L45-46 (print p.25)",
        "evidence": "The p.25 passage gives the artist's full name, Michelangelo da Caravaggio, and identifies him as the painter of Maffeo Barberini's portrait.",
    },
    "cand-0552": {
        "index": "C.csv#76",
        "subentry": "Sacrifice of Abraham",
        "pages": "25",
        "anchor": "02-sources/02-Markdown/02_CHP-2_sec_i.md#L46-47 (print p.25)",
        "evidence": "The p.25 passage says Maffeo Barberini commissioned a subject from the same artist, Michelangelo da Caravaggio, and names it The Sacrifice of Abraham.",
    },
}
EXISTING_GROUP_MEMBERS = {
    "cand-3010", "cand-7513", "cand-0544", "cand-0545", "cand-0547", "cand-0549"
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


def same_group_members(rows, group):
    return {
        row["candidate_id"]
        for row in rows
        if row.get("decision") == "same" and get_group(row.get("resolution_note", "")) == group
    }


def main():
    parser = argparse.ArgumentParser(
        description="Reuse the accepted Caravaggio person KU for five remaining index-subentry candidates"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT)
    _, candidates = read_csv(CANDIDATES)
    _, manifest = read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {row["candidate_id"]: row for row in decision_rows(alignments)}
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    manifest_row = manifest_by_id[KU_ID]
    assert manifest_row["type"] == "person"
    assert manifest_row["card_path"] == "04-knowledge/units/persons/caravaggio.md"
    assert manifest_row["card_path"] in ACCEPTED.read_text(encoding="utf-8-sig")
    card_text = (ROOT / manifest_row["card_path"]).read_text(encoding="utf-8-sig")
    assert "title: 卡拉瓦乔（Caravaggio）" in card_text

    for cid, expected in TARGETS.items():
        candidate = candidate_by_id[cid]
        row = decision_by_id[cid]
        assert candidate["suggested_type"] == "person", cid
        assert candidate["canonical_name"] == "Caravaggio, Michelangelo da", cid
        assert candidate["index_entry_id"] == expected["index"], cid
        assert candidate["sub_entry"] == expected["subentry"], cid
        assert candidate["index_page_range"] == expected["pages"], cid
        assert row["decision"] == "undecided" and not row.get("ku_id"), cid
        assert "; Undecided:" in row["resolution_note"], cid

    source_texts = {
        "chp1": (ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md").read_text(encoding="utf-8-sig"),
        "chp2": (ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md").read_text(encoding="utf-8-sig"),
        "chp5": (ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_i.md").read_text(encoding="utf-8-sig"),
    }
    assert "before executing his\naltarpieces of The Conversion of St Paul and The Martyrdom of St Peter" in source_texts["chp1"]
    assert "Michelangelo da Caravaggio’s Earthly Love" in source_texts["chp5"]
    assert "Michelangelo da Caravaggio" in source_texts["chp2"]
    assert "The Sacrifice os Abraham" in source_texts["chp2"]

    decisions = decision_rows(alignments)
    before = Counter(row["decision"] for row in decisions)
    assert same_group_members(decisions, GROUP) == EXISTING_GROUP_MEMBERS
    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}

    for cid, expected in TARGETS.items():
        row = planned_by_id[cid]
        prefix, separator, old_reason = row["resolution_note"].partition("; Undecided:")
        assert separator and old_reason
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"{prefix}; matched_manifest={KU_ID}; "
            f"matched_candidate_ids={','.join(sorted(EXISTING_GROUP_MEMBERS))}; group={GROUP}; Same: "
            f"Candidate type is person; the index subentry {expected['subentry']!r} is nested under the "
            "main entry 'Caravaggio, Michelangelo da' and supplies a page locator, not a separate work candidate. "
            f"Body anchor {expected['anchor']} confirms the person identification: {expected['evidence']} "
            "Reuse the accepted person KU; no external identity source was accessed. "
            f"Historical undecided rationale retained: Undecided:{old_reason}"
        )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    assert after == Counter({**before, "same": before["same"] + len(TARGETS), "undecided": before["undecided"] - len(TARGETS)})
    assert same_group_members(after_rows, GROUP) == EXISTING_GROUP_MEMBERS | set(TARGETS)
    assert len({row["ku_id"] for row in after_rows if row["decision"] == "same" and row.get("ku_id")}) == 1030

    if args.dry_run:
        print(
            "dry-run passed: 5 Caravaggio person index candidates undecided->same; "
            f"same={before['same']}->{after['same']} (unique same KUs remain 1030), "
            f"undecided={before['undecided']}->{after['undecided']}, new={after['new']}, "
            f"conflict={after['conflict']}, excluded={after['excluded']}; accepted KU/card unchanged"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-0546/0548/0550/0551/0552 -> units/persons/caravaggio; "
        f"same={after['same']}, undecided={after['undecided']}; accepted KU/card unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
