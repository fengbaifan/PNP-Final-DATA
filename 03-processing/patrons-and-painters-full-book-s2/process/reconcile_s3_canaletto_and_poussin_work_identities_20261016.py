from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
INDEX_DIR = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"
INDEX_MD_DIR = ROOT / "02-sources" / "03-Index" / "03-1-Index-MD"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_REF = "S3-cross-chapter-canaletto-poussin-2026-10-16"

CANALLETTO_PERSON_IDS = [
    f"cand-{number:04d}"
    for number in range(498, 529)
    if number not in {504, 505}
]
SAME_TARGETS = {
    **{candidate_id: "units/persons/canaletto" for candidate_id in CANALLETTO_PERSON_IDS},
    "cand-2016": "units/works/poussin-massacre-innocents",
    "cand-2018": "units/works/poussin-moses-trampling-on-pharaoh-s-crown",
    "cand-2019": "units/works/plague-at-ashdod-1631",
}
NEW_GROUPS = {
    "cand-0504": "sg3-work-canaletto-entry-comte-de-gergy-1725",
    "cand-0505": "sg3-work-canaletto-entry-count-bolagno-1729",
}
WORK_DETAILS = {
    "cand-0504": (
        "C.csv#28; Haskell, ch. 10 p. 277 n. 5; statement "
        "st-chp10-notes-p277n5-gergy-entry; Canaletto's Entry of the Comte de Gergy, 1725"
    ),
    "cand-0505": (
        "C.csv#29; Haskell, ch. 10 p. 277 n. 5; statement "
        "st-chp10-notes-p277n5-bolagno-entry; Canaletto's entry of the Count of Bolagno, 1729"
    ),
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def rows_by_candidate(path: Path):
    _, rows = read_csv(path)
    return rows


def index_row(path: Path, row_number: int):
    _, rows = read_csv(path)
    if row_number < 0 or row_number >= len(rows):
        raise AssertionError(f"index row out of range: {path.name}#{row_number}")
    return rows[row_number]


def get_group(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def check_source_index(candidates):
    for candidate_id in CANALLETTO_PERSON_IDS:
        candidate = candidates[candidate_id]
        assert candidate["canonical_name"] == "Canaletto"
        assert candidate["suggested_type"] == "person"
        assert candidate["index_entry_id"].startswith("C.csv#")
        row_number = int(candidate["index_entry_id"].split("#")[1])
        source_row = index_row(INDEX_DIR / "C.csv", row_number)
        assert source_row["Main Entry"] == "Canaletto", (candidate_id, source_row)
        assert candidate["sub_entry"] == source_row["Sub-entry"]
        assert candidate["detail"] == source_row["Detail"]

    for candidate_id, expected_title, row_number in [
        ("cand-0504", "Entry of the Comte de Gergy", 28),
        ("cand-0505", "Entry of the Count of Bolagno", 29),
        ("cand-2016", "Massacre of the Innocents", 219),
        ("cand-2018", "Moses trampling on Pharaoh's Crown", 221),
        ("cand-2019", "Plague at Ashdod", 222),
    ]:
        candidate = candidates[candidate_id]
        index_name = "C.csv" if candidate_id in NEW_GROUPS else "P.csv"
        assert candidate["suggested_type"] == "work"
        assert candidate["index_entry_id"] == f"{index_name}#{row_number}"
        source_row = index_row(INDEX_DIR / index_name, row_number)
        assert source_row["Main Entry"] in {"Canaletto", "Poussin, Nicolas"}
        assert source_row["Sub-entry"] == expected_title


def verify_existing_targets(manifest):
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    expected_types = {
        "units/persons/canaletto": "person",
        "units/works/poussin-massacre-innocents": "work",
        "units/works/poussin-moses-trampling-on-pharaoh-s-crown": "work",
        "units/works/plague-at-ashdod-1631": "work",
    }
    for ku_id, expected_type in expected_types.items():
        assert ku_id in manifest_by_id
        assert manifest_by_id[ku_id]["type"] == expected_type
        card_path = ROOT / manifest_by_id[ku_id]["card_path"]
        assert card_path.is_file(), card_path

    assert "Canaletto" in (ROOT / manifest_by_id["units/persons/canaletto"]["card_path"]).read_text(encoding="utf-8-sig")
    assert "Massacre of the Innocents" in (ROOT / manifest_by_id["units/works/poussin-massacre-innocents"]["card_path"]).read_text(encoding="utf-8-sig")
    assert "Moses trampling on Pharaoh's crown" in (ROOT / manifest_by_id["units/works/poussin-moses-trampling-on-pharaoh-s-crown"]["card_path"]).read_text(encoding="utf-8-sig")
    assert "The Plague at Ashdod" in (ROOT / manifest_by_id["units/works/plague-at-ashdod-1631"]["card_path"]).read_text(encoding="utf-8-sig")


def verify_statements():
    wanted = {
        "st-chp10-notes-p277n5-gergy-entry": "Canaletto painted the Entry of the Comte de Gergy",
        "st-chp10-notes-p277n5-bolagno-entry": "that of the Count of Bolagno",
        "st-chp4-sec-i-l6-18-massacre-note": "Massacre of the Innocents at Chantilly",
    }
    found = {}
    with STATEMENTS_PATH.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in wanted:
                found[statement["statement_id"]] = statement
    assert set(found) == set(wanted)
    for statement_id, quote_part in wanted.items():
        statement = found[statement_id]
        assert quote_part in statement.get("original_quote", "")
        assert statement.get("origin") == "book"
    assert found["st-chp10-notes-p277n5-gergy-entry"]["object_candidate_id"] == "cand-0504"
    assert found["st-chp10-notes-p277n5-bolagno-entry"]["object_candidate_id"] == "cand-0505"
    assert found["st-chp4-sec-i-l6-18-massacre-note"]["subject_candidate_id"] == "cand-2016"


def main():
    parser = argparse.ArgumentParser(description="Reconcile cross-chapter Canaletto person candidates and Poussin work identities")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(CANDIDATE_PATH)
    _, manifest = read_csv(MANIFEST_PATH)
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    candidate_alignments = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(candidate_alignments) == 12404
    assert set(SAME_TARGETS).issubset(candidates)
    assert set(NEW_GROUPS).issubset(candidates)
    assert len(CANALLETTO_PERSON_IDS) == 29

    check_source_index(candidates)
    verify_existing_targets(manifest)
    verify_statements()

    manifest_by_id = {row["ku_id"]: row for row in manifest}
    for candidate_id, target in SAME_TARGETS.items():
        candidate = candidates[candidate_id]
        assert candidate["suggested_type"] == manifest_by_id[target]["type"]
        current = candidate_alignments[candidate_id]
        assert (current["decision"], current.get("ku_id", "")) in {
            ("undecided", ""),
            ("same", target),
        }, (candidate_id, current["decision"], current.get("ku_id"))

    for candidate_id, group in NEW_GROUPS.items():
        candidate = candidates[candidate_id]
        assert candidate["suggested_type"] == "work"
        current = candidate_alignments[candidate_id]
        assert (current["decision"], current.get("ku_id", ""), get_group(current.get("resolution_note", ""))) in {
            ("undecided", "", None),
            ("new", "", group),
        }, (candidate_id, current["decision"], current.get("ku_id"), get_group(current.get("resolution_note", "")))

    existing_groups = {}
    for current_candidate_id, row in candidate_alignments.items():
        if row["decision"] == "new":
            group = get_group(row.get("resolution_note", ""))
            if group:
                existing_groups.setdefault(group, set()).add(current_candidate_id)
    for candidate_id, group in NEW_GROUPS.items():
        assert not (existing_groups.get(group, set()) - {candidate_id}), (
            group,
            existing_groups.get(group, set()),
        )
    assert "units/works/canaletto-entry-comte-de-gergy-1725" not in manifest_by_id
    assert "units/works/canaletto-entry-count-bolagno-1729" not in manifest_by_id

    print(f"Canaletto person candidates to reuse: {len(CANALLETTO_PERSON_IDS)} -> units/persons/canaletto")
    print("Poussin work candidates to reuse: cand-2016, cand-2018, cand-2019 -> existing work KUs")
    print("Canaletto work candidates to create: cand-0504 and cand-0505 as separate groups")
    if args.dry_run:
        print("DRY-RUN OK; alignment.csv unchanged")
        return 0

    for candidate_id, target in SAME_TARGETS.items():
        row = candidate_alignments[candidate_id]
        group = f"sg3-ku-{target.replace('/', '-')}"
        if (
            row["decision"] == "same"
            and row.get("ku_id") == target
            and f"group={group}" in row.get("resolution_note", "")
            and row.get("process_ref") == PROCESS_REF
        ):
            continue
        old_note = row.get("resolution_note", "")
        candidate = candidates[candidate_id]
        evidence = (
            f"source_ref=entity-candidates.csv#{candidate_id};index_entry={candidate['index_entry_id']}; "
            f"matched_manifest={target}; group={group}; "
        )
        if candidate_id in CANALLETTO_PERSON_IDS:
            rationale = (
                "the book index has one Canaletto main entry with the listed person subentries; "
                "the accepted Canaletto person KU identifies this same in-book person as Giovanni Antonio Canal. "
                "This is an internal identity mapping; no external identifier or new biographical fact is added."
            )
        elif candidate_id == "cand-2016":
            rationale = (
                "P.csv#219 indexes the same Poussin work at pp.10n and 95; the ch.4 p.95 footnote identifies "
                "the Chantilly painting, while the existing KU retains the ch.1 reference and its version ambiguity. "
                "Map the book-index work identity without asserting an additional physical version or merging Reni's work."
            )
        elif candidate_id == "cand-2018":
            rationale = (
                "P.csv#221 names Poussin's Moses trampling on Pharaoh's Crown; the accepted front-matter work KU "
                "uses the same specific title and plate 19a source. Exact in-book title identity supports reuse."
            )
        else:
            rationale = (
                "P.csv#222 names Poussin's Plague at Ashdod at p.15; the existing work KU is the same titled "
                "Poussin painting and preserves the ch.1 source scope."
            )
        row["ku_id"] = target
        row["decision"] = "same"
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = evidence + rationale + f" | prior_decision=undecided; prior_resolution_note={old_note}"

    for candidate_id, group in NEW_GROUPS.items():
        row = candidate_alignments[candidate_id]
        if row["decision"] == "new" and get_group(row.get("resolution_note", "")) == group:
            continue
        old_note = row.get("resolution_note", "")
        row["ku_id"] = ""
        row["decision"] = "new"
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"source_ref=entity-candidates.csv#{candidate_id}; group={group}; {WORK_DETAILS[candidate_id]}; "
            "S2 directly identifies a distinct Canaletto painting; no exact existing work KU matches this title. "
            "The Gergy and Bolagno works remain separate by title, sitter label, and reported year; "
            "the personal identities of the named counts remain unresolved and are not inferred here. "
            "Authorship, location, and other statements remain S6 relation candidates, not formal relations. "
            f"| prior_decision=undecided; prior_resolution_note={old_note}"
        )

    decisions = Counter(row["decision"] for row in candidate_alignments.values())
    assert decisions == Counter({"same": 1751, "new": 5007, "undecided": 5541, "excluded": 98, "conflict": 7}), decisions
    for candidate_id, target in SAME_TARGETS.items():
        assert candidate_alignments[candidate_id]["decision"] == "same"
        assert candidate_alignments[candidate_id]["ku_id"] == target
    for candidate_id, group in NEW_GROUPS.items():
        row = candidate_alignments[candidate_id]
        assert row["decision"] == "new" and not row["ku_id"] and get_group(row["resolution_note"]) == group

    write_csv(ALIGNMENT_PATH, alignment_fields, alignments)
    print(f"APPLIED; current S3 decisions: {dict(decisions)}; process_ref={PROCESS_REF}")
    print("No KU, accepted.yml, external identifier, enrichment, or relation record was changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
