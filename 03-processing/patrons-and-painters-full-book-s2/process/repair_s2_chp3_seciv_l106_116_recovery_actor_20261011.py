from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
BACKUP = TABLE.with_name(
    "book-statements.jsonl.bak-s2-chp3-seciv-l106-116-recovery-actor-20261011"
)
EXPECTED_PRE_SHA256 = "bf8632a6f1588c47298326d9bc233193cdeb0837bc98b0f29ec2ead45bd87bfe"
OLD_ID = "st-chp3-seciv-l106-116-novitiate-intended-recovery-from-prince"
NEW_ID = "st-chp3-seciv-l106-116-scara-intended-recovery-from-prince"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Correct the actor attributed an intention in the p.87 archival quotation."
    )
    parser.add_argument(
        "--apply", action="store_true", help="write the reviewed one-statement repair"
    )
    args = parser.parse_args()

    before = TABLE.read_bytes()
    current_sha = sha256(before)
    if current_sha != EXPECTED_PRE_SHA256:
        raise SystemExit(
            f"refusing unexpected table state: {current_sha} != {EXPECTED_PRE_SHA256}"
        )

    lines = before.decode("utf-8").splitlines(keepends=True)
    matches: list[tuple[int, dict]] = []
    ids: set[str] = set()
    for i, raw in enumerate(lines):
        if not raw.strip():
            continue
        row = json.loads(raw)
        sid = row.get("statement_id")
        if sid in ids:
            raise SystemExit(f"duplicate statement id: {sid}")
        ids.add(sid)
        if sid == OLD_ID:
            matches.append((i, row))
    if len(matches) != 1:
        raise SystemExit(f"expected one target statement, found {len(matches)}")
    if NEW_ID in ids:
        raise SystemExit(f"new statement id already exists: {NEW_ID}")

    i, row = matches[0]
    if row.get("segment_id") != "chp-3:03_CHP-3_sec_iv:l106-116":
        raise SystemExit("target statement is outside the expected S2 segment")
    if row.get("subject_candidate_id") != "cand-11617":
        raise SystemExit("unexpected current subject endpoint")
    if row.get("object_candidate_id") != "cand-5327":
        raise SystemExit("unexpected current object endpoint")
    q = row.get("qualifiers", {})
    if q.get("intermediary_candidate_id") != "cand-5339":
        raise SystemExit("unexpected current Scaramuccia qualifier")
    if q.get("relation_candidate") is not True:
        raise SystemExit("target is not marked as an S2 relation candidate")

    row["statement_id"] = NEW_ID
    row["subject_candidate_id"] = "cand-5339"
    row["object_candidate_id"] = "cand-5327"
    q.pop("intermediary_candidate_id", None)
    q["funding_source_candidate_id"] = "cand-11617"
    q["claim"] = (
        "Haskell's quoted archival report attributes to Father Francesco Scaramuccia "
        "an intention to recover from Prince Pamfili the sum he said he had paid "
        "from the Novitiate's own funds."
    )
    q["speaker"] = (
        "Haskell quoting a cited archival entry; the stated intention is attributed "
        "to Father Francesco Scaramuccia"
    )
    q["qualification"] = (
        "The cited archival item has not been independently consulted. The intention "
        "is attributed to Scaramuccia, who reportedly paid Gaulli using Novitiate "
        "funds; the passage does not report completed recovery. The Prince is not "
        "identified as Camillo."
    )
    q["relation_candidate_note"] = (
        "The cited entry attributes the intended recovery to Scaramuccia, who said "
        "he paid from Novitiate funds; the Prince is the intended reimbursement "
        "source, not a reported completed recovery."
    )
    lines[i] = json.dumps(row, ensure_ascii=False) + ("\n" if lines[i].endswith("\n") else "")
    after = "".join(lines).encode("utf-8")

    changed_rows = [
        json.loads(line)
        for line in after.decode("utf-8").splitlines()
        if line.strip()
    ]
    repaired = [x for x in changed_rows if x.get("statement_id") == NEW_ID]
    if len(repaired) != 1:
        raise SystemExit("post-render target validation failed")
    repaired = repaired[0]
    if (
        repaired["subject_candidate_id"] != "cand-5339"
        or repaired["object_candidate_id"] != "cand-5327"
        or repaired["qualifiers"].get("funding_source_candidate_id") != "cand-11617"
        or "intermediary_candidate_id" in repaired["qualifiers"]
    ):
        raise SystemExit("post-render endpoint validation failed")

    print(f"pre_sha256={current_sha}")
    print(f"post_sha256={sha256(after)}")
    print(f"repair={OLD_ID} -> {NEW_ID}")
    print("endpoints=cand-5339 -> cand-5327; funding_source_candidate_id=cand-11617")
    if not args.apply:
        print("DRY-RUN PASS; no files written")
        return 0

    if BACKUP.exists():
        raise SystemExit(f"refusing to overwrite recovery copy: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    TABLE.write_bytes(after)
    written_sha = sha256(TABLE.read_bytes())
    if written_sha != sha256(after):
        TABLE.write_bytes(before)
        raise SystemExit("write verification failed; original bytes restored")
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"APPLY PASS post_sha256={written_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
