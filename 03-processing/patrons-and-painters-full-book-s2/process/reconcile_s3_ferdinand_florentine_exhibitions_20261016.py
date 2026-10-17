from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ALIGNMENT = ROOT / "04-knowledge" / "tables" / "alignment.csv"
PROCESS_REF = "S3-ferdinand-florentine-exhibitions-2026-10-16"

DECISIONS = {
    "cand-1610": (
        "sg3-procedure-ferdinand-art-exhibition-guidance",
        "A.csv#129 pp.240-241; chp-8:08_CHP-8_sec_ii:l350-368#L357",
        "The index subentry points to Ferdinand's use of exhibitions to guide the direction of painting in Florence. Ch. 8 describes his regular public displays, his intended display of Cassana's painting, and the more ambitious 1706 exhibition. This is a source-defined patronage practice, distinct from the 1706 event itself and from the existing artist-self-promotion procedure.",
    ),
    "cand-11046": (
        "sg3-event-florentine-art-exhibition-1706",
        "chp-8:08_CHP-8_sec_ii:l350-368#L357; chp-20:20_CHP-20Postscript:l123-135#L131",
        "The ch. 8 account identifies the specific 1706 Florence exhibition, its St Luke's day venue in the Annunziata cloister, catalogue, lending, and Ferdinand's attendance. The postscript discusses the same 1706 exhibition while qualifying the extent of Ferdinand's role after discovery of a 1705 exhibition catalogue. Keep the 1706 event distinct from the 1705 exhibition and from later exhibitions; preserve the revised qualification about Ferdinand's role.",
    ),
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write the two reviewed S3 decisions.")
    args = parser.parse_args()

    fields, rows = read_csv(ALIGNMENT)
    by_id = {row["candidate_id"]: row for row in decision_rows(rows)}
    _, candidates = read_csv(ROOT / "04-knowledge" / "tables" / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert set(DECISIONS) <= set(by_id) and set(DECISIONS) <= set(candidate_by_id)
    assert all(by_id[cid]["decision"] == "undecided" and not by_id[cid]["ku_id"] for cid in DECISIONS)
    assert candidate_by_id["cand-1610"]["suggested_type"] == "procedure"
    assert candidate_by_id["cand-11046"]["suggested_type"] == "event"
    assert all(by_id[cid]["resolution_note"].find(group) < 0 for cid, (group, _, _) in DECISIONS.items())

    for cid, (group, source_ref, rationale) in DECISIONS.items():
        row = by_id[cid]
        prior = row["resolution_note"]
        row["decision"] = "new"
        row["ku_id"] = ""
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"group={group}; source_ref={source_ref}; S3 cross-chapter review 2026-10-16: undecided -> new. "
            f"{rationale} Prior rationale retained as history: {prior}"
        )

    new_rows = [row for row in decision_rows(rows) if row["decision"] == "new"]
    print("S3 Florence exhibition cross-chapter dry-run passed")
    print("new candidate rows after:", len(new_rows))
    print("new identity groups created:", 2)
    print("procedure/event identity groups kept separate:", DECISIONS["cand-1610"][0], DECISIONS["cand-11046"][0])
    if args.apply:
        write_csv(ALIGNMENT, fields, rows)
        print("applied: two S3 new decisions with prior rationales retained")
    else:
        print("dry-run only; pass --apply to write")


if __name__ == "__main__":
    main()
