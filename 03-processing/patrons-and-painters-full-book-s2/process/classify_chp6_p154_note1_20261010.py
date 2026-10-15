from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"
EXPECTED_SHA256 = "862d6afed5b027c3b57238cc99b1b11b8354941a2fb0b9f1d290a10c79dbf09b"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp6-p154-note1-20261010")

EXPECTED = {
    "st-chp6-notes-l147-p154-n1-citation": {
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-4846",
        "predicate": "cites",
        "relation_candidate": True,
        "relation_candidate_note": (
            "Haskell's footnote explicitly cites the identified Baldinucci volume VI (1728) archive. "
            "This records the bibliographic link and does not verify the cited claim."
        ),
    },
    "st-chp6-notes-l147-p154-n1-location": {
        "subject_candidate_id": "cand-6224",
        "object_candidate_id": "cand-6378",
        "predicate": "owned_by",
        "relation_candidate": True,
        "relation_candidate_note": (
            "The footnote states that this painting was the institution's property at the time of Haskell's text. "
            "This is a source-attributed ownership candidate, not a current-location claim or formal S6 edge."
        ),
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_candidates() -> dict[str, dict[str, str]]:
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        return {row["candidate_id"]: row for row in csv.DictReader(f)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks pass")
    args = parser.parse_args()

    original = TABLE.read_bytes()
    current_sha = sha256(original)
    if current_sha != EXPECTED_SHA256:
        raise SystemExit(f"input SHA mismatch: expected {EXPECTED_SHA256}, got {current_sha}")

    candidates = load_candidates()
    for candidate_id, expected_type in {
        "cand-2962": "archive",
        "cand-4846": "archive",
        "cand-6224": "work",
        "cand-6378": "institution",
    }.items():
        candidate = candidates.get(candidate_id)
        if candidate is None or candidate.get("suggested_type") != expected_type:
            raise SystemExit(f"candidate preflight failed: {candidate_id} must exist as {expected_type}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if "Baldinucci, VI, 1728, pp. 558-9." not in source_lines[146]:
        raise SystemExit("source anchor mismatch at 06_CHP-6_sec_i.md L147")
    if "The picture is now the property of the Paul Getty Museum, Malibu." not in source_lines[146]:
        raise SystemExit("ownership anchor mismatch at 06_CHP-6_sec_i.md L147")

    lines = original.decode("utf-8").splitlines()
    changed = {}
    seen = set()
    output_lines = []
    for line in lines:
        if not line.strip():
            output_lines.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        expected = EXPECTED.get(statement_id)
        if expected is not None:
            if statement_id in seen:
                raise SystemExit(f"duplicate statement ID: {statement_id}")
            seen.add(statement_id)
            if row.get("origin") != "book" or row.get("source_file") != "02-sources/02-Markdown/06_CHP-6_sec_i.md":
                raise SystemExit(f"source provenance mismatch: {statement_id}")
            qualifiers = row.get("qualifiers", {})
            if qualifiers.get("source_line_start") != 147 or qualifiers.get("source_line_end") != 147:
                raise SystemExit(f"line anchor mismatch: {statement_id}")
            if qualifiers.get("printed_page") != "154" or qualifiers.get("footnote_marker") != 1:
                raise SystemExit(f"page/footnote mismatch: {statement_id}")
            if qualifiers.get("relation_candidate") is not None:
                raise SystemExit(f"already classified: {statement_id}")
            if not set(expected["object_candidate_id"] for _ in [0]).issubset(set(qualifiers.get("mentioned_candidate_ids", []))):
                raise SystemExit(f"object is not in the cited mention set: {statement_id}")
            before = dict(row)
            row["subject_candidate_id"] = expected["subject_candidate_id"]
            row["object_candidate_id"] = expected["object_candidate_id"]
            row["predicate"] = expected["predicate"]
            qualifiers["relation_candidate"] = expected["relation_candidate"]
            qualifiers["relation_candidate_note"] = expected["relation_candidate_note"]
            if statement_id.endswith("-location"):
                qualifiers["text_layer"] = "attributed ownership report in authorial footnote"
                qualifiers["qualification"] = (
                    "This records ownership as reported in Haskell's 1980 text; it is not a claim about present-day ownership or location."
                )
            row["qualifiers"] = qualifiers
            changed[statement_id] = (before, row)
            output_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
        else:
            output_lines.append(line)

    if seen != set(EXPECTED):
        raise SystemExit(f"statement coverage mismatch: found {sorted(seen)}, expected {sorted(EXPECTED)}")

    output = ("\n".join(output_lines) + "\n").encode("utf-8")
    print(f"preflight passed: rows={len(seen)}/{len(EXPECTED)} input_sha256={current_sha}")
    for statement_id, (before, after) in changed.items():
        print(f"{statement_id}")
        print("  before:", json.dumps({k: before.get(k) for k in ("subject_candidate_id", "object_candidate_id", "predicate")}, ensure_ascii=False))
        print("  after: ", json.dumps({k: after.get(k) for k in ("subject_candidate_id", "object_candidate_id", "predicate")}, ensure_ascii=False))
        print("  relation_candidate=true;", after["qualifiers"]["relation_candidate_note"])

    if not args.apply:
        print("dry-run only; table unchanged")
        return

    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(output)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    print(f"applied: backup={BACKUP.relative_to(ROOT)} output_sha256={sha256(output)}")


if __name__ == "__main__":
    main()
