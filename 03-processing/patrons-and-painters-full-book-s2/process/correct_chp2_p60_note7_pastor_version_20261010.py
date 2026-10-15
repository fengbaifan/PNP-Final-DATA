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
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
STATEMENTS_SHA = "e365f21672abb8ab72999882c03d8717ef90742347145bf18fe3d02bbad2768a"
CANDIDATES_SHA = "b4ac5c42748249c553bf133ab9267acb9fbb85422d1198208b19b7e8b8c250de"
TARGET_ID = "st-chp2-secvii-l38-54-fn-p60-7c-pastor-citation"
RELATED_BIBLIOGRAPHY_CANDIDATE_ID = "cand-11414"
BACKUP_SUFFIX = ".bak-s2-handoff-chp2-p60-note7-pastor-version-20261010"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows():
    raw = STATEMENTS.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.splitlines(keepends=True)
    rows = [json.loads(line.decode("utf-8-sig")) for line in lines if line.strip()]
    return rows, lines, bom


def counts(rows: list[dict]) -> dict:
    marked = [s for s in rows if (s.get("qualifiers") or {}).get("relation_candidate") is True]
    complete = sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) for s in marked)
    return {
        "statements": len(rows),
        "relations": len(marked),
        "complete_relations": complete,
        "open_relations": len(marked) - complete,
        "footnote_claims": sum(s.get("predicate") == "footnote-claim" for s in rows),
        "cites": sum(s.get("predicate") == "cites" and (s.get("qualifiers") or {}).get("relation_candidate") is True
                     for s in rows),
    }


def serialize(rows: list[dict], original_lines: list[bytes], bom: bool) -> bytes:
    newline = b"\r\n" if any(line.endswith(b"\r\n") for line in original_lines) else b"\n"
    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    return b"".join(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    require(sha(STATEMENTS) == STATEMENTS_SHA, "unexpected statement table SHA-256")
    require(sha(CANDIDATES) == CANDIDATES_SHA, "unexpected candidate table SHA-256")
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = {c["candidate_id"]: c for c in csv.DictReader(f)}
    version = candidates.get(RELATED_BIBLIOGRAPHY_CANDIDATE_ID)
    require(version is not None and version["suggested_type"] == "archive" and version["status"] == "open",
            "the possible Pastor bibliography candidate changed")
    rows, lines, bom = read_rows()
    before = counts(rows)
    expected = {
        "statements": 12676, "relations": 3653, "complete_relations": 3638,
        "open_relations": 15, "footnote_claims": 4, "cites": 114,
    }
    require(before == expected, f"current statement counts differ: {before}")
    target = next((s for s in rows if s["statement_id"] == TARGET_ID), None)
    require(target is not None and target["predicate"] == "cites"
            and target["object_candidate_id"] == "cand-4237", "Pastor citation target changed")
    q = target.get("qualifiers", {})
    require(q.get("volume") == "XIII" and q.get("page") == 969 and q.get("year") == 1943,
            "unexpected Pastor citation locator/year")
    require(q.get("possible_version_candidate_id") is None, "version correction already applied")

    updated = json.loads(json.dumps(rows))
    changed = next(s for s in updated if s["statement_id"] == TARGET_ID)
    cq = changed["qualifiers"]
    cq.pop("year")
    cq["possible_version_candidate_id"] = RELATED_BIBLIOGRAPHY_CANDIDATE_ID
    cq["version_qualification"] = (
        "The bibliography identifies a 1943 Italian edition of the Pastor series but gives no volume; "
        "that year is not assigned to this volume XIII citation."
    )
    after = counts(updated)
    require(after == before, f"counts changed unexpectedly: {after}")
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "statement": TARGET_ID,
        "before": {k: q.get(k) for k in ("year", "volume", "page", "possible_version_candidate_id")},
        "after": {k: cq.get(k) for k in ("year", "volume", "page", "possible_version_candidate_id", "version_qualification")},
        "counts_unchanged": after,
    }, ensure_ascii=True, indent=2))
    if not args.apply:
        return

    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    require(not backup.exists(), "recovery backup already exists")
    shutil.copy2(STATEMENTS, backup)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=STATEMENTS.parent, prefix=STATEMENTS.name + ".tmp-", delete=False) as f:
            f.write(serialize(updated, lines, bom))
            temp = Path(f.name)
        os.replace(temp, STATEMENTS)
        reread, _, _ = read_rows()
        checked = next(s for s in reread if s["statement_id"] == TARGET_ID)
        require("year" not in checked["qualifiers"] and checked["qualifiers"]["volume"] == "XIII"
                and checked["qualifiers"]["page"] == 969, "post-write Pastor citation check failed")
        print(json.dumps({"result": "applied", "statements_sha256": sha(STATEMENTS),
                          "backup": str(backup.relative_to(ROOT))}, ensure_ascii=True, indent=2))
    except Exception:
        shutil.copy2(backup, STATEMENTS)
        raise
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


if __name__ == "__main__":
    main()
