from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"
EXPECTED_SHA256 = "93d20c41325d4918b5fff54f3207a3880a783d5a6dd874277eb15e9db3374fcd"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp6-p154-notes2-4-20261010")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    original = TABLE.read_bytes()
    current_sha = sha256(original)
    if current_sha != EXPECTED_SHA256:
        raise SystemExit(f"input SHA mismatch: expected {EXPECTED_SHA256}, got {current_sha}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = {r["candidate_id"]: r for r in csv.DictReader(f)}
    expected_types = {
        "cand-2962": "archive",
        "cand-6196": "archive",
        "cand-4836": "archive",
        "cand-6379": "archive",
    }
    for cid, kind in expected_types.items():
        if cid not in candidates or candidates[cid].get("suggested_type") != kind:
            raise SystemExit(f"candidate preflight failed: {cid} must exist as {kind}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    anchors = {
        148: "2 Golzio, 1939, p. 14.",
        149: "3 Pastor, XIV, p. 329.",
        150: "4 Apart from Golzio, 1939, see also for Flavio’s collecting Incisa della Rocchetta, 1925, pp. 539-44.",
    }
    for line_no, phrase in anchors.items():
        if phrase not in source_lines[line_no - 1]:
            raise SystemExit(f"source anchor mismatch at line {line_no}")

    transformations = {
        "st-chp6-notes-l148-p154-n2": {
            "subject": "cand-2962", "object": "cand-6196", "claim": "Footnote 2 cites Golzio (1939), page 14.",
            "mention_ids": ["cand-3501", "cand-6196"], "locator": "p. 14",
        },
        "st-chp6-notes-l149-p154-n3": {
            "subject": "cand-2962", "object": "cand-4836", "claim": "Footnote 3 cites Pastor, volume XIV, page 329.",
            "mention_ids": ["cand-4836"], "locator": "vol. XIV, p. 329",
        },
        "st-chp6-notes-l150-p154-n4": {
            "subject": "cand-2962", "object": "cand-6196", "claim": "The note cites Golzio (1939) for its discussion of Flavio Chigi’s collecting, alongside a further Incisa della Rocchetta reference.",
            "mention_ids": ["cand-3501", "cand-6196"], "locator": "1939; page not specified in this note",
        },
    }
    new_id = "st-chp6-notes-l150-p154-n4-incisa-citation"
    relation_note = "The footnote explicitly directs readers to this identified archive; this is a bibliographic candidate and does not verify the cited content."
    seen: set[str] = set()
    output_lines: list[str] = []
    shown: dict[str, tuple[dict, dict]] = {}
    for line in original.decode("utf-8").splitlines():
        if not line.strip():
            output_lines.append(line)
            continue
        row = json.loads(line)
        sid = row.get("statement_id")
        spec = transformations.get(sid)
        if spec is None:
            output_lines.append(line)
            continue
        if sid in seen:
            raise SystemExit(f"duplicate statement ID: {sid}")
        seen.add(sid)
        q = row.get("qualifiers", {})
        page = "154"
        marker = {"st-chp6-notes-l148-p154-n2": 2, "st-chp6-notes-l149-p154-n3": 3, "st-chp6-notes-l150-p154-n4": 4}[sid]
        line_no = {"st-chp6-notes-l148-p154-n2": 148, "st-chp6-notes-l149-p154-n3": 149, "st-chp6-notes-l150-p154-n4": 150}[sid]
        if (row.get("origin") != "book" or row.get("source_file") != "02-sources/02-Markdown/06_CHP-6_sec_i.md"
                or q.get("source_line_start") != line_no or q.get("source_line_end") != line_no
                or q.get("printed_page") != page or q.get("footnote_marker") != marker
                or row.get("predicate") != "footnote_citation" or q.get("relation_candidate") is not None):
            raise SystemExit(f"statement provenance/classification preflight failed: {sid}")
        if not set(spec["mention_ids"]).issubset(set(q.get("mentioned_candidate_ids", []))):
            raise SystemExit(f"mention set does not cover citation endpoints: {sid}")
        before = deepcopy(row)
        row["subject_candidate_id"] = spec["subject"]
        row["object_candidate_id"] = spec["object"]
        row["predicate"] = "cites"
        q["claim"] = spec["claim"]
        q["citation_locator"] = spec["locator"]
        q["mentioned_candidate_ids"] = spec["mention_ids"]
        q["relation_candidate"] = True
        q["relation_candidate_note"] = relation_note
        row["qualifiers"] = q
        shown[sid] = (before, row)
        output_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))

        if sid == "st-chp6-notes-l150-p154-n4":
            split = deepcopy(row)
            split["statement_id"] = new_id
            split["object_candidate_id"] = "cand-6379"
            split_q = split["qualifiers"]
            split_q["claim"] = "The note also cites G. Incisa della Rocchetta (1925), pages 539–544, for Flavio Chigi’s collecting."
            split_q["citation_locator"] = "pp. 539–544"
            split_q["mentioned_candidate_ids"] = ["cand-3498", "cand-6379"]
            split_q["relation_candidate_note"] = relation_note
            split["qualifiers"] = split_q
            split["original_quote"] = row["original_quote"]
            shown[new_id] = ({}, split)
            output_lines.append(json.dumps(split, ensure_ascii=False, separators=(",", ":")))

    if seen != set(transformations):
        raise SystemExit(f"statement coverage mismatch: found {sorted(seen)}")
    if any(r.get("statement_id") == new_id for r in map(json.loads, original.decode("utf-8").splitlines()) if r):
        raise SystemExit(f"new statement ID already exists: {new_id}")

    output = ("\n".join(output_lines) + "\n").encode("utf-8")
    print(f"preflight passed: updated={len(seen)} split_added=1 input_sha256={current_sha}")
    for sid, (before, after) in shown.items():
        print(sid, "=>", after["predicate"], after["subject_candidate_id"], after["object_candidate_id"], after["qualifiers"]["claim"])
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
