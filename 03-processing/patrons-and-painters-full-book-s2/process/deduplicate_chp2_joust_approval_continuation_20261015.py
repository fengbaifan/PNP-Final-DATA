from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_TABLE_HASH = "29dc055869aa83f71076f97c4d634984b606fe8e317795196c209e27cf2c2580"
EXPECTED_SOURCE_HASH = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
FRAGMENT_ID = "st-chp2-seciv-l127-137-joust-pastiche-approval-fragment"
COMPLETE_ID = "st-chp2-seciv-l139-152-joust-pastiche-receives-delighted-approval"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-joust-approval-continuation-20261015")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def open_counts(rows: list[dict]) -> tuple[int, int, int, int]:
    relations = [r for r in rows if r.get("qualifiers", {}).get("relation_candidate") is True]
    sm = sum(not r.get("subject_candidate_id") for r in relations)
    om = sum(not r.get("object_candidate_id") for r in relations)
    both = sum(not r.get("subject_candidate_id") and not r.get("object_candidate_id") for r in relations)
    return sm + om - both, om - both, sm - both, both


def build() -> tuple[bytes, list[dict], list[dict]]:
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    raw = TABLE.read_bytes()
    if sha(raw) != EXPECTED_TABLE_HASH:
        raise SystemExit("statement table hash changed")
    if sha(SOURCE.read_bytes()) != EXPECTED_SOURCE_HASH:
        raise SystemExit("source asset changed")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    for sid in ("chp-2:02_CHP-2_sec_iv:l127-137", "chp-2:02_CHP-2_sec_iv:l139-152"):
        if not any(s.get("segment_id") == sid for s in segments):
            raise SystemExit(f"missing continuation segment: {sid}")

    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    fragment = by_id.get(FRAGMENT_ID)
    complete = by_id.get(COMPLETE_ID)
    if (
        not fragment
        or fragment.get("subject_candidate_id") != "cand-4767"
        or fragment.get("object_candidate_id") not in (None, "")
        or fragment.get("qualifiers", {}).get("continuation_to_statement_id") != COMPLETE_ID
        or fragment.get("qualifiers", {}).get("relation_candidate") is not True
        or fragment.get("original_quote") != "None the less this elaborate pastiche of feudal practices met"
    ):
        raise SystemExit("joust fragment state changed")
    if (
        not complete
        or complete.get("subject_candidate_id") != "cand-4767"
        or complete.get("object_candidate_id") not in (None, "")
        or complete.get("qualifiers", {}).get("resolved_from_statement_id") != FRAGMENT_ID
        or complete.get("qualifiers", {}).get("relation_candidate") is not True
        or complete.get("original_quote") != "with delighted approval"
    ):
        raise SystemExit("joust continuation state changed")
    before = open_counts(rows)
    true_before = sum(r.get("qualifiers", {}).get("relation_candidate") is True for r in rows)
    if before != (508, 331, 64, 113) or true_before != 10381:
        raise SystemExit(f"unexpected baseline counts: open={before}, true={true_before}")

    fq = fragment["qualifiers"]
    fq["relation_candidate"] = False
    fq["claim"] = "Opening fragment of the joust-reception sentence; its completed claim is recorded in the linked continuation statement."
    fq["qualification"] = "The source sentence continues at L140. This fragment is retained as a segment anchor, not as an independent relation candidate."
    fq["relation_candidate_note"] = "The complete relation is represented by the linked continuation statement, avoiding a duplicate open audience endpoint."
    fq.pop("open_endpoint_reason", None)

    cq = complete["qualifiers"]
    cq["relation_candidate_note"] = "Haskell says the joust's feudal pastiche met with delighted approval. The earlier aim to revive chivalry among young men of Rome does not identify who expressed this approval."
    cq["open_endpoint_reason"] = "The source does not name or bound the approving audience; do not infer that it was the young men mentioned as the joust's intended audience."

    after = open_counts(rows)
    true_after = sum(r.get("qualifiers", {}).get("relation_candidate") is True for r in rows)
    if after != (507, 330, 64, 113) or true_after != 10380:
        raise SystemExit(f"unexpected projected counts: open={after}, true={true_after}")
    line_ending = b"\r\n" if b"\r\n" in raw else b"\n"
    output = line_ending.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") for row in rows
    ) + line_ending
    return output, [fragment, complete], [copy_row(by_id[FRAGMENT_ID]), copy_row(by_id[COMPLETE_ID])]


def copy_row(row: dict) -> dict:
    return json.loads(json.dumps(row, ensure_ascii=False))


def apply(output: bytes) -> None:
    if BACKUP.exists():
        raise SystemExit("recovery backup already exists")
    if sha(TABLE.read_bytes()) != EXPECTED_TABLE_HASH:
        raise SystemExit("statement table changed after preview")
    shutil.copy2(TABLE, BACKUP)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=TABLE.parent, delete=False) as handle:
            temp_path = Path(handle.name)
            handle.write(output)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, TABLE)
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    output, changed_rows, _ = build()
    print(f"{TABLE.relative_to(ROOT)}: {EXPECTED_TABLE_HASH} -> {sha(output)}")
    print("The L137 fragment becomes a non-independent continuation anchor; L140 remains one open relation.")
    for row in changed_rows:
        print(f"{row['statement_id']}: relation_candidate={row['qualifiers'].get('relation_candidate')}, open_reason={row['qualifiers'].get('open_endpoint_reason')}")
    print("Open endpoints: 508 -> 507; true relation candidates: 10,381 -> 10,380.")
    if args.apply:
        apply(output)
        print(f"Applied with recovery backup {BACKUP.name}.")


if __name__ == "__main__":
    main()
