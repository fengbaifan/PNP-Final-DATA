from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/13_CHP-13_intro.md"
PDF = ROOT / "02-sources/01-book/CHP-13.pdf"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l116-122"
SEGMENT_SHA = "2eee99ac3f4b0588c8491bc9a2987eb8817d8e07774747df9d898967e4fcc16b"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-ch13-p344-zompini-atomization-20261014")
EXPECTED = {
    SOURCE: "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    PDF: "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc",
    STATEMENTS: "6080e97f3c86d36bb343e9c4a314a34735e5047a5b56c4ea144b1c33cd30f358",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    for path, expected in EXPECTED.items():
        if digest(path) != expected:
            raise SystemExit(f"precheck failed: {path.relative_to(ROOT)} changed")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()]
    matches = [row for row in segments if row.get("segment_id") == SEGMENT_ID]
    if len(matches) != 1 or matches[0].get("sha256") != SEGMENT_SHA:
        raise SystemExit("precheck failed: p344 segment hash changed")

    raw = STATEMENTS.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    final_newline = raw.endswith(("\n", "\r"))
    lines = raw.splitlines()
    rows = [json.loads(line) for line in lines]
    by_id = {row["statement_id"]: row for row in rows}
    local = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    target_id = "st-chp13-p344-zanetti-employed_zompini"
    if len(local) != 29 or target_id not in by_id:
        raise SystemExit(f"precheck failed: expected 29 p344 statements and the Zompini claim; got {len(local)}")
    if by_id[target_id].get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("precheck failed: Zompini statement is not the expected accepted relation candidate")

    row = by_id[target_id]
    q = row["qualifiers"]
    row["predicate"] = "employed_zompini"
    row["original_quote"] = "his employment of Gaetano Zompini"
    q["claim"] = "Haskell says Zanetti employed Gaetano Zompini."
    q["qualification"] = "Haskell identifies employment as the chief basis for Zanetti's significance as a patron; housing and allowance are separate claims."

    def new_row(statement_id: str, predicate: str, claim: str, quote: str, qualification: str) -> dict:
        result = json.loads(json.dumps(row, ensure_ascii=False))
        result["statement_id"] = statement_id
        result["predicate"] = predicate
        result["original_quote"] = quote
        result["qualifiers"].update({
            "claim": claim,
            "qualification": qualification,
            "mentioned_candidate_ids": ["cand-2838", "cand-2877"],
            "relation_candidate": True,
            "source_line_start": 119,
            "source_line_end": 119,
        })
        return result

    additions = [
        new_row(
            "st-chp13-p344-zanetti-housed_zompini",
            "took_zompini_into_household",
            "Haskell says Zanetti took Gaetano Zompini into his house.",
            "whom he took into his house",
            "This records the stated household arrangement separately from employment and financial support.",
        ),
        new_row(
            "st-chp13-p344-zanetti-allowance_zompini",
            "provided_regular_allowance_to_zompini",
            "Haskell says Zanetti provided Gaetano Zompini with a regular allowance.",
            "provided with a regular allowance",
            "The source gives no amount or period for the allowance.",
        ),
    ]
    if any(addition["statement_id"] in by_id for addition in additions):
        raise SystemExit("precheck failed: planned statement ID already exists")
    rows.extend(additions)
    text = "\n".join(SOURCE.read_text(encoding="utf-8").splitlines()[115:122])
    for addition in [row, *additions]:
        if addition["original_quote"] not in text:
            raise SystemExit(f"precheck failed: source quote mismatch for {addition['statement_id']}")
    final_local = [item for item in rows if item.get("segment_id") == SEGMENT_ID]
    if len(final_local) != 31 or sum(item["qualifiers"]["relation_candidate"] is True for item in final_local) != 22:
        raise SystemExit("precheck failed: unexpected p344 totals after atomization")

    print("p344 existing employment/housing/allowance statement split into 3 supported relation candidates")
    print("final segment statements=31; true=22; false=9; unset=0")
    if not args.apply:
        print("dry-run: no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"refusing to overwrite recovery copy: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    output = newline.join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in rows)
    if final_newline:
        output += newline
    fd, temp_name = tempfile.mkstemp(prefix=STATEMENTS.name + ".", suffix=".tmp", dir=STATEMENTS.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(output.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, STATEMENTS)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    print(f"applied; backup={BACKUP.name}; statements_sha256={digest(STATEMENTS)}")


if __name__ == "__main__":
    main()
