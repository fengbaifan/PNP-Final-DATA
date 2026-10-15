from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"
IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p331_page_review_20261014.png"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l269-271"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp10-p331-semantics-20261014")

EXPECTED = {
    TABLE.name: "b772241016a76d91e111f91436e0791815e5742bebbcc6f1bf03ca1c4c21a295",
    SOURCE.name: "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    PDF.name: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
    IMAGE.name: "6f48bd6d684b38605c782b9f3b84c60e075c3d85655a28c9b872f49a860c46e1",
}
EXPECTED_IDS = {
    "st-chp10-p331-academy-borrowed-pictures",
    "st-chp10-p331-academy-exhibition-series-started-1777",
    "st-chp10-p331-academy-exhibitors-bore-cost",
    "st-chp10-p331-academy-shows-ended-1787",
    "st-chp10-p331-algarotti-letter-and-salon-comparison",
    "st-chp10-p331-exhibitions-as-public-forum",
    "st-chp10-p331-limited-surviving-criticism",
    "st-chp10-p331-piazza-display-completion",
    "st-chp10-p331-s-rocco-annual-participation",
    "st-chp10-p331-s-rocco-exhibition-origin",
    "st-chp10-p331-s-rocco-not-salon-in-scale",
    "st-chp10-p331-state-interference-evaluation",
}
TO_CLASSIFY = {
    "st-chp10-p331-academy-shows-ended-1787": False,
    "st-chp10-p331-limited-surviving-criticism": False,
    "st-chp10-p331-s-rocco-not-salon-in-scale": True,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and correct reviewed p.331 S2 statements")
    parser.add_argument("--apply", action="store_true", help="write after exact-hash, row-set, and quote preflight")
    args = parser.parse_args()

    actual = {p.name: sha(p) for p in (TABLE, SOURCE, PDF, IMAGE)}
    if actual != EXPECTED:
        raise SystemExit(f"preflight hash mismatch; no writes made: {actual}")

    rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement_id in table")
    target = [r for r in rows if r.get("segment_id") == SEGMENT]
    ids = {r["statement_id"] for r in target}
    if ids != EXPECTED_IDS:
        raise SystemExit(f"p.331 statement set mismatch: {sorted(ids ^ EXPECTED_IDS)}")
    unset = {r["statement_id"] for r in target if "relation_candidate" not in r.get("qualifiers", {})}
    if unset != set(TO_CLASSIFY):
        raise SystemExit(f"p.331 unset statement set changed: {sorted(unset ^ set(TO_CLASSIFY))}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if source_lines[268] != "[Page 331]":
        raise SystemExit("printed page marker changed")
    for row in target:
        q = row["qualifiers"]
        block = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
        if not row.get("original_quote") or row["original_quote"] not in block:
            raise SystemExit(f"source quote mismatch: {row['statement_id']}")

    # The two relationship predicates describe the painter group acting on an exhibition/event.
    direction = {
        "st-chp10-p331-academy-exhibitors-bore-cost": {
            "subject_candidate_id": "cand-9866",
            "object_candidate_id": "cand-9872",
            "predicate": "artists_bore_heavy_expenses_for_academy_exhibitions",
        },
        "st-chp10-p331-s-rocco-annual-participation": {
            "subject_candidate_id": "cand-9866",
            "object_candidate_id": "cand-8587",
            "predicate": "artists_participated_in_annual_s_rocco_exhibition",
        },
    }
    for sid, values in direction.items():
        q = by_id[sid]["qualifiers"]
        q["relation_candidate"] = True
        q["qualification"] = (
            "Haskell reports the painters' role in relation to the exhibition series. "
            + ("No cost amount or individual allocation is given." if "bore-cost" in sid else "No individual participants or exact annual count are named.")
        )
        by_id[sid]["subject_candidate_id"] = values["subject_candidate_id"]
        by_id[sid]["object_candidate_id"] = values["object_candidate_id"]
        by_id[sid]["predicate"] = values["predicate"]

    # Standalone terminal-state and evidence-limit statements are not binary entity relations.
    end_row = by_id["st-chp10-p331-academy-shows-ended-1787"]
    end_row["qualifiers"]["relation_candidate"] = False
    end_row["qualifiers"]["qualification"] = (
        "This records a terminal state and a terminus by 1787, not an exact closure date; "
        "no second entity endpoint is stated for a formal relation."
    )
    criticism = by_id["st-chp10-p331-limited-surviving-criticism"]
    criticism["qualifiers"]["relation_candidate"] = False
    criticism["qualifiers"]["qualification"] = (
        "This is an authorial statement about the limits of surviving written evidence and the difficulty of assessing contemporary reception; "
        "it names no specific criticism record or relation endpoint."
    )
    comparison = by_id["st-chp10-p331-s-rocco-not-salon-in-scale"]
    comparison["qualifiers"]["relation_candidate"] = True
    comparison["qualifiers"]["qualification"] = (
        "Explicit comparison of the S. Rocco showings with the Paris Salon in organizational complexity and attention; "
        "the comparison does not equate the two exhibition systems."
    )

    body = [r for r in rows if r.get("segment_id") == SEGMENT]
    counts = {
        "true": sum(r["qualifiers"].get("relation_candidate") is True for r in body),
        "false": sum(r["qualifiers"].get("relation_candidate") is False for r in body),
        "unset": sum("relation_candidate" not in r["qualifiers"] for r in body),
    }
    if counts != {"true": 10, "false": 2, "unset": 0}:
        raise SystemExit(f"unexpected p.331 classification counts: {counts}")

    output = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    print(f"p.331 rows: {len(body)}; relation_candidate true/false/unset: {counts['true']}/{counts['false']}/{counts['unset']}")
    print("Decisions: discontinued-by-1787 = false; limited surviving criticism = false; explicit S. Rocco/Salon comparison = true.")
    print("Direction corrections: exhibition costs and annual participation now run from painters to exhibition event.")
    print("Reviewed image:", IMAGE.name, actual[IMAGE.name])
    print("planned table hash:", hashlib.sha256(output).hexdigest())
    if not args.apply:
        print("preview only; no files written")
        return 0
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    TABLE.write_bytes(output)
    print("applied; backup:", BACKUP.name)
    print("written table hash:", sha(TABLE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
