from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SEGMENT = "chp-2:02_CHP-2_sec_ii:l3-8"
STATEMENT_ID = "st-chp2-sec-ii-l3-8-nepotism-rationale"
EXPECTED_SHA = "ea9d509a5e0a8b88a7ba7cd1c433686d3223bf90d7879edbc4cf1e47d887acf2"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-ii-l3-8-nepotism-20261010")
NOTE = (
    "This is Haskell’s explanatory evaluation of employing an unnamed close relative within a papal system "
    "marked by jealousies. It does not identify an adviser or assert that Urban VIII employed a specific person; "
    "the term and pope remain contextual referents rather than endpoints of a binary relation."
)
EXPECTED_QUOTE = "With jealousies so strong there was much to be said for the Pope employing a close relation as his most intimate adviser."


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the reviewed non-relation classification")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    require(actual_sha == EXPECTED_SHA, f"statement table changed since review: {actual_sha}")
    require(not BACKUP.exists(), f"recovery backup already exists: {BACKUP.name}")

    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    require(len(lines) >= 6 and EXPECTED_QUOTE in lines[5], "reviewed source line changed")
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    matches = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
    require(len(matches) == 1, "reviewed statement is missing or duplicated")
    row = matches[0]
    qualifiers = row.get("qualifiers") or {}
    require(row.get("segment_id") == SEGMENT, "statement belongs to another segment")
    require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == ("cand-1734", "cand-3104"),
            "statement endpoints changed")
    require((qualifiers.get("source_line_start"), qualifiers.get("source_line_end")) == (6, 6),
            "statement source anchor changed")
    require(row.get("original_quote") == EXPECTED_QUOTE, "statement quote changed")
    require(qualifiers.get("relation_candidate") is None, "statement is already classified")

    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    qualifiers = dict(qualifiers)
    qualifiers["relation_candidate"] = False
    qualifiers["relation_candidate_note"] = NOTE
    row["qualifiers"] = qualifiers
    output = []
    for index, item in enumerate(rows):
        line = json.dumps(item, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    payload = b"".join(output)

    true_bilateral = sum(1 for item in rows if item.get("subject_candidate_id") and item.get("object_candidate_id")
                         and (item.get("qualifiers") or {}).get("relation_candidate") is True)
    false_bilateral = sum(1 for item in rows if item.get("subject_candidate_id") and item.get("object_candidate_id")
                          and (item.get("qualifiers") or {}).get("relation_candidate") is False)
    pending_bilateral = sum(1 for item in rows if item.get("subject_candidate_id") and item.get("object_candidate_id")
                            and (item.get("qualifiers") or {}).get("relation_candidate") is None)
    require((true_bilateral, false_bilateral, pending_bilateral) == (3983, 451, 4063),
            f"unexpected projected counts: {(true_bilateral, false_bilateral, pending_bilateral)}")
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified_false": [STATEMENT_ID],
        "before": {"relation_true_bilateral": 3983, "relation_false_bilateral": 450, "unclassified_bilateral": 4064},
        "after": {"relation_true_bilateral": true_bilateral, "relation_false_bilateral": false_bilateral,
                  "unclassified_bilateral": pending_bilateral},
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    shutil.copy2(TABLE, BACKUP)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".s2tmp-", delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, TABLE)
        written = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        written_row = next(item for item in written if item.get("statement_id") == STATEMENT_ID)
        require((written_row.get("qualifiers") or {}).get("relation_candidate") is False,
                "non-relation classification was not persisted")
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print(json.dumps({
        "result": "applied",
        "statement_count": len(written),
        "sha256": hashlib.sha256(TABLE.read_bytes()).hexdigest(),
        "backup": BACKUP.name,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
