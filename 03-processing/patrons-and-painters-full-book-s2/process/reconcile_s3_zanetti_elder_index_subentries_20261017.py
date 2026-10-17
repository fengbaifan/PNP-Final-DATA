from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ALIGNMENT = ROOT / "04-knowledge" / "tables" / "alignment.csv"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MANIFEST = ROOT / "04-knowledge" / "tables" / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
KU_ID = "units/persons/a-m-zanetti-the-elder"
GROUP = "sg3-ku-units-persons-a-m-zanetti-the-elder"
PROCESS_REF = "S3-Zanetti-the-Elder-person-index-subentries-2026-10-17"
EXISTING_MEMBERS = {"cand-2838", "cand-3707"}
TARGETS = {
    "cand-2839": ("UVWXYZ.csv#176", "and Crozat", "341", "L91-93", "When Crozat came to Venice in 1716, he formed a close friendship with Zanetti."),
    "cand-2840": ("UVWXYZ.csv#177", "and Joseph Smith", "341", "L95", "In Venice itself Zanetti was in touch with Joseph Smith and Schulenburg."),
    "cand-2841": ("UVWXYZ.csv#178", "and Marshal Schulenburg", "341", "L95", "In Venice itself Zanetti was in touch with Joseph Smith and Schulenburg."),
    "cand-2842": ("UVWXYZ.csv#179", "and Regent de France", "341", "L93", "he was introduced to the Regent, who entrusted him with the purchase of pictures for his gallery."),
    "cand-2843": ("UVWXYZ.csv#180", "and Sebastiano and Marco Ricci", "341, 342", "L91", "Early in the eighteenth century he was already in contact with most of the leading artists, above all Sebastiano and Marco Ricci."),
    "cand-2844": ("UVWXYZ.csv#181", "as intermediary between Venice and rest of Europe", "342", "L102", "Zanetti frequently acted as an intermediary between Venice and the rest of Europe."),
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


def group_members(rows):
    return {
        row["candidate_id"]
        for row in rows
        if row.get("decision") == "same" and row.get("ku_id") == KU_ID and get_group(row.get("resolution_note", "")) == GROUP
    }


def main():
    parser = argparse.ArgumentParser(description="Reuse the accepted A. M. Zanetti the Elder person KU for six index subentries")
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
    assert manifest_row["card_path"] == "04-knowledge/units/persons/a-m-zanetti-the-elder.md"
    assert manifest_row["card_path"] in ACCEPTED.read_text(encoding="utf-8-sig")
    card_text = (ROOT / manifest_row["card_path"]).read_text(encoding="utf-8-sig")
    assert "Anton Maria Zanetti the Elder" in card_text

    for cid, (entry, subentry, pages, _, _) in TARGETS.items():
        candidate = candidate_by_id[cid]
        row = decision_by_id[cid]
        assert candidate["suggested_type"] == "person", cid
        assert candidate["canonical_name"] == "Zanetti, A. M., the Elder", cid
        assert candidate["index_entry_id"] == entry, cid
        assert candidate["sub_entry"] == subentry, cid
        assert candidate["index_page_range"] == pages, cid
        assert row["decision"] == "undecided" and not row.get("ku_id"), cid
        assert "; Undecided:" in row["resolution_note"], cid

    body_path = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
    body = re.sub(r"\s+", " ", body_path.read_text(encoding="utf-8-sig"))
    assert "Antonio Maria Zanetti the Elder (Plate 58a)" in body
    for cid, (_, _, _, _, evidence) in TARGETS.items():
        check = evidence.rstrip(".")
        assert check in body, (cid, check)

    decisions = decision_rows(alignments)
    before = Counter(row["decision"] for row in decisions)
    assert group_members(decisions) == EXISTING_MEMBERS
    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}

    for cid, (entry, subentry, pages, lines, evidence) in TARGETS.items():
        row = planned_by_id[cid]
        prefix, separator, old_reason = row["resolution_note"].partition("; Undecided:")
        assert separator and old_reason
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"{prefix}; matched_manifest={KU_ID}; matched_candidate_ids={','.join(sorted(EXISTING_MEMBERS))}; "
            f"group={GROUP}; Same: Candidate type is person. The index subentry {subentry!r} is nested under "
            "'Zanetti, A. M., the Elder'; chapter 13 p.341 gives the full name 'Antonio Maria Zanetti the Elder' "
            "before describing the indexed person and continues the same subject through p.342. "
            f"Body anchor=02-sources/02-Markdown/13_CHP-13_intro.md#{lines} (print p.{pages}): {evidence} "
            "This identifies the person only; it does not assert any relationship implied by the subentry. "
            "Reuse the accepted person KU; no external identity source was accessed. "
            f"Historical undecided rationale retained: Undecided:{old_reason}"
        )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    assert after["same"] == before["same"] + len(TARGETS)
    assert after["undecided"] == before["undecided"] - len(TARGETS)
    assert {"cand-2838", "cand-3707"} | set(TARGETS) == group_members(after_rows)
    assert len({row["ku_id"] for row in after_rows if row["decision"] == "same" and row.get("ku_id")}) == 1030

    if args.dry_run:
        print(
            "dry-run passed: 6 Zanetti the Elder person index candidates undecided->same; "
            f"same={before['same']}->{after['same']} (unique same KUs remain 1030), "
            f"undecided={before['undecided']}->{after['undecided']}, "
            f"Zanetti person group={len(EXISTING_MEMBERS)}->{len(group_members(after_rows))}; card/manifest unchanged"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    print(
        "applied: cand-2839/2840/2841/2842/2843/2844 -> units/persons/a-m-zanetti-the-elder; "
        f"same={after['same']}, undecided={after['undecided']}; card/manifest unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
