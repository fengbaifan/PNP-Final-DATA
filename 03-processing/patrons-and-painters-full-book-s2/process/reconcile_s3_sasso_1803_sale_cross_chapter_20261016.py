from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ALIGNMENT = ROOT / "04-knowledge" / "tables" / "alignment.csv"
PROCESS_REF = "S3-sasso-1803-sale-cross-chapter-2026-10-16"
EXISTING_CANDIDATE = "cand-10715"
PENDING_CANDIDATE = "cand-11549"
GROUP = "sg3-event-cand-10715"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Join the second source anchor to the existing Sasso-sale event group.")
    args = parser.parse_args()

    fields, rows = read_csv(ALIGNMENT)
    by_id = {row["candidate_id"]: row for row in rows if row.get("candidate_id") and not row.get("external_source")}
    _, candidates = read_csv(ROOT / "04-knowledge" / "tables" / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert EXISTING_CANDIDATE in by_id and PENDING_CANDIDATE in by_id
    assert candidate_by_id[EXISTING_CANDIDATE]["suggested_type"] == candidate_by_id[PENDING_CANDIDATE]["suggested_type"] == "event"
    current = by_id[EXISTING_CANDIDATE]
    pending = by_id[PENDING_CANDIDATE]
    assert current["decision"] == "new" and pending["decision"] == "undecided"
    assert re.search(rf"group={re.escape(GROUP)}(?:;|\|)", current["resolution_note"])
    assert not pending["ku_id"]

    prior = pending["resolution_note"]
    pending["decision"] = "new"
    pending["ku_id"] = ""
    pending["process_ref"] = PROCESS_REF
    pending["resolution_note"] = (
        f"group={GROUP}; source_ref=chp-16:16_CHP-16_intro:l16-22#L22; "
        "S3 cross-chapter review 2026-10-16: undecided -> new, joined to cand-10715. "
        "Ch. 16 says Sasso's collection was auctioned after his death in 1803 and cites the collection catalogue. "
        "Ch. 17, p.382, says Correr almost certainly bought Zocchi's double portrait at the Sasso sale in 1803. "
        "The shared sale and year establish one event group; the catalogue remains cited by Haskell and was not independently consulted. "
        f"Prior rationale retained as history: {prior}"
    )

    print("S3 Sasso sale cross-chapter dry-run passed")
    print("candidate group:", GROUP)
    print("members:", EXISTING_CANDIDATE, PENDING_CANDIDATE)
    if args.apply:
        write_csv(ALIGNMENT, fields, rows)
        print("applied: cand-11549 joined the existing new event group")
    else:
        print("dry-run only; pass --apply to write")


if __name__ == "__main__":
    main()
