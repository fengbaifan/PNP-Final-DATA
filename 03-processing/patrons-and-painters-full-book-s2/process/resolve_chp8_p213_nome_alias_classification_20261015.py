from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
TARGET_ID = "st-chp8-p213-nome-alias-and-inventory-description"
INVENTORY_ID = "st-chp8-p213-nome-inventory-described-as-lorenese"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l108-118"
BACKUP_SUFFIX = "bak-s2-chp8-p213-nome-alias-classification-20261015"
EXPECTED_STATEMENT_HASH = "068af80309912a77859f3e16e0194719f3e3e41c6a25fda8d8f318f5f6f80d2b"
EXPECTED_SEGMENT_HASH = "ebbb5be59dbc67e1337d077618074f382126d0f7c97e61e385c00514897599f3"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open_true(row: dict[str, object]) -> bool:
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = STATEMENTS.read_bytes()
    if digest(raw) != EXPECTED_STATEMENT_HASH:
        raise ValueError("Statement table changed since preview")
    segment = next(
        json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Source segment hash changed")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    index = {row["statement_id"]: pos for pos, row in enumerate(rows)}
    if TARGET_ID not in index or INVENTORY_ID not in index:
        raise ValueError("Alias or separate inventory statement is missing")
    row = rows[index[TARGET_ID]]
    inventory = rows[index[INVENTORY_ID]]
    if (
        row.get("segment_id") != SEGMENT_ID
        or row.get("subject_candidate_id") != "cand-1749"
        or row.get("object_candidate_id") is not None
        or (row.get("qualifiers") or {}).get("relation_candidate") is not True
        or inventory.get("segment_id") != SEGMENT_ID
        or inventory.get("subject_candidate_id") != "cand-7500"
        or inventory.get("object_candidate_id") != "cand-1749"
        or (inventory.get("qualifiers") or {}).get("relation_candidate") is not True
    ):
        raise ValueError("The alias or separate inventory statement changed")
    before_open = sum(is_open_true(item) for item in rows)
    before_true = sum((item.get("qualifiers") or {}).get("relation_candidate") is True for item in rows)
    before_false = sum((item.get("qualifiers") or {}).get("relation_candidate") is False for item in rows)
    if (before_open, before_true, before_false) != (458, 10390, 4739):
        raise ValueError(f"Unexpected pre-update counts: {(before_open, before_true, before_false)}")

    qualifiers = row.get("qualifiers") or {}
    qualifiers["claim"] = "Haskell says François Nomé was generally known as Monsù Desiderio."
    qualifiers["qualification"] = "This is a reported name form for the same person candidate. The separate inventory description 'Lorenese' is recorded in the linked statement; no separate person or global identity conclusion is inferred."
    qualifiers["mentioned_candidate_ids"] = ["cand-1749"]
    qualifiers["relation_candidate"] = False
    qualifiers["relation_candidate_note"] = "This is a name and identity assertion for the same person candidate, not a relation between distinct entities; preserve it as source evidence for identity and name alignment."
    qualifiers["related_statement_ids"] = [INVENTORY_ID]
    row["qualifiers"] = qualifiers
    for extra_key in ("claim", "qualification", "mentioned_candidate_ids"):
        row.pop(extra_key, None)

    inventory_q = inventory.get("qualifiers") or {}
    inventory_q["related_statement_ids"] = [TARGET_ID]
    inventory["qualifiers"] = inventory_q

    updated = ("".join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
        for item in rows
    )).encode("utf-8")
    after_rows = [json.loads(line) for line in updated.decode("utf-8").splitlines()]
    after_open = sum(is_open_true(item) for item in after_rows)
    after_true = sum((item.get("qualifiers") or {}).get("relation_candidate") is True for item in after_rows)
    after_false = sum((item.get("qualifiers") or {}).get("relation_candidate") is False for item in after_rows)
    segment_open = [
        item["statement_id"] for item in after_rows
        if item.get("segment_id") == SEGMENT_ID and is_open_true(item)
    ]
    if (after_open, after_true, after_false, segment_open) != (457, 10389, 4740, []):
        raise ValueError(f"Unexpected post-update counts: {(after_open, after_true, after_false, segment_open)}")

    print(f"statement_rows={len(rows)}->{len(after_rows)}")
    print(f"relation_candidate_true={before_true}->{after_true}")
    print(f"relation_candidate_false={before_false}->{after_false}")
    print(f"open_endpoints={before_open}->{after_open}")
    print(f"segment_open={segment_open}")
    print(f"classified_as_nonrelation={TARGET_ID}; alias remains on candidate cand-1749")
    print(f"linked_inventory_statement={INVENTORY_ID}")
    print(f"{STATEMENTS.relative_to(ROOT)} {digest(raw)}->{digest(updated)}")
    if args.preview:
        return 0

    backup = STATEMENTS.with_name(f"{STATEMENTS.name}.{BACKUP_SUFFIX}")
    temp = STATEMENTS.with_name(f"{STATEMENTS.name}.tmp-{BACKUP_SUFFIX}")
    if backup.exists() or temp.exists():
        raise FileExistsError("Recovery or temporary file already exists")
    shutil.copy2(STATEMENTS, backup)
    try:
        temp.write_bytes(updated)
        temp.replace(STATEMENTS)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise
    print(f"backup={backup.relative_to(ROOT)}")
    print(f"applied_sha256={digest(STATEMENTS.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
