from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
STATEMENT_ID = "st-chp7-p199-v-collectors-alternative-centres"
RELATED_STATEMENT_ID = "st-chp7-p199-v-papal-power-and-provincial-centres"
SEGMENT_ID = "chp-7:07_CHP-7_sec_v:l3-7"
BACKUP_SUFFIX = "bak-s2-chp7-p199-v-collectors-endpoint-20261015"
EXPECTED_HASH = "2fca2077ea16775c003e69242d57669ca8283113da7d8f734619f4c49c4215f0"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def open_count(rows: list[dict[str, object]]) -> int:
    return sum(
        1 for row in rows
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if digest(raw) != EXPECTED_HASH:
        raise ValueError("Statement table changed since preview")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    index = {row["statement_id"]: i for i, row in enumerate(rows)}
    if STATEMENT_ID not in index or RELATED_STATEMENT_ID not in index:
        raise ValueError("Target or contextual statement is missing")
    row = rows[index[STATEMENT_ID]]
    if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != "cand-7275" or row.get("object_candidate_id") is not None:
        raise ValueError("Target statement identity or endpoint changed")
    q = row.get("qualifiers") or {}
    if q.get("relation_candidate") is not True or open_count(rows) != 467:
        raise ValueError("Target classification or open-endpoint count changed")

    row["object_candidate_id"] = "cand-2066"
    q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + ["cand-2066"]))
    q["relation_candidate_note"] = "Bologna, Venice and Naples are the alternative city group named immediately after the active provincial centres in this paragraph; no individual collector-to-city assignment is inferred."
    q["related_statement_ids"] = [RELATED_STATEMENT_ID]
    q.pop("open_endpoint_reason", None)
    row["qualifiers"] = q

    updated = ("".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in rows)).encode("utf-8")
    after_rows = [json.loads(line) for line in updated.decode("utf-8").splitlines()]
    after_open = open_count(after_rows)
    if after_open != 466:
        raise ValueError(f"Unexpected post-update open count: {after_open}")
    print(f"statement_rows={len(rows)}->{len(after_rows)}")
    print(f"open_endpoints=467->{after_open}")
    print(f"segment_open={[r['statement_id'] for r in after_rows if r.get('segment_id') == SEGMENT_ID and (r.get('qualifiers') or {}).get('relation_candidate') is True and (not r.get('subject_candidate_id') or not r.get('object_candidate_id'))]}")
    print(f"{TABLE.relative_to(ROOT)} {digest(raw)}->{digest(updated)}")
    if args.preview:
        return 0

    backup = TABLE.with_name(f"{TABLE.name}.{BACKUP_SUFFIX}")
    temp = TABLE.with_name(f"{TABLE.name}.tmp-{BACKUP_SUFFIX}")
    if backup.exists() or temp.exists():
        raise FileExistsError("Recovery or temporary file already exists")
    shutil.copy2(TABLE, backup)
    try:
        temp.write_bytes(updated)
        temp.replace(TABLE)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise
    print(f"backup={backup.relative_to(ROOT)}")
    print(f"applied_sha256={digest(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
