from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
TARGET = "st-chp3-seciv-l16-24-courtois-good-faith-test"
SUPPORT = "st-chp3-seciv-l16-24-nickel-oliva-roles"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-courtois-good-faith-authority-20261015")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    before = TABLE.read_bytes()
    rows = [json.loads(line) for line in before.decode("utf-8").splitlines()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows) or TARGET not in by_id or SUPPORT not in by_id:
        raise ValueError("Statement IDs are missing or duplicated")
    target = by_id[TARGET]
    support = by_id[SUPPORT]
    if target.get("segment_id") != "chp-3:03_CHP-3_sec_iv:l16-24":
        raise ValueError("Target moved to a different segment")
    if target.get("subject_candidate_id") != "cand-0399" or target.get("object_candidate_id") is not None:
        raise ValueError("Target endpoint state changed")
    if support.get("subject_candidate_id") != "cand-1740" or support.get("object_candidate_id") != "cand-3403":
        raise ValueError("Nickel support statement changed")
    q = target.setdefault("qualifiers", {})
    q["claim"] = "Haskell says Courtois was required in Rome to prove his good faith by an unusual use of his artistic skill; the passage identifies the authority as Goswin Nickel, the General of the Jesuits at that time."
    q["relation_candidate_note"] = "The preceding clause says Courtois was sent to 'the General in Rome'; the following sentence identifies the General at that time as Goswin Nickel. Link the authority to the existing Nickel candidate and the supporting office statement."
    q.pop("unresolved_endpoint", None)
    q.pop("open_endpoint_reason", None)
    related = q.setdefault("related_statement_ids", [])
    if SUPPORT not in related:
        related.append(SUPPORT)
    target["object_candidate_id"] = "cand-1740"

    after = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
    print(f"statements={len(rows)} unchanged")
    print(f"open_endpoints={sum(1 for row in rows if (row.get('qualifiers') or {}).get('relation_candidate') is True and (not row.get('subject_candidate_id') or not row.get('object_candidate_id')))}")
    print(f"sha256={digest(before)}->{digest(after)}")
    print(f"resolved: {TARGET} object=cand-1740; support={SUPPORT}")
    if args.preview:
        return 0
    if BACKUP.exists():
        raise FileExistsError(f"Recovery copy already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    temp = TABLE.with_name(TABLE.name + ".tmp-courtois-good-faith-authority-20261015")
    if temp.exists():
        raise FileExistsError(f"Temporary file already exists: {temp}")
    try:
        temp.write_bytes(after)
        temp.replace(TABLE)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={digest(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
