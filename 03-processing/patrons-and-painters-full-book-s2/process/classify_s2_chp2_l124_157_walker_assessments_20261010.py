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
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_i.md"
SEGMENT = "chp-2:02_CHP-2_sec_i:l124-157"
EXPECTED_SHA = "08c146e353ae05454063f7cd33438fd5f0347a2606cf6e868b400df594036558"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-l124-157-walker-20261010")
SPECS = {
    "st-chp2-seci-l124-157-walker-view-andrians": (
        "cand-4356",
        "cand-4249",
        "John Walker is reported as considering it unlikely that Rubens copied The Andrians from the original during his visit to Rome.",
    ),
    "st-chp2-seci-l124-157-walker-view-worship": (
        "cand-4356",
        "cand-4248",
        "John Walker is reported as considering it unlikely that Rubens copied The Worship of Venus from the original during his visit to Rome.",
    ),
}
NOTE = (
    "The source attributes a qualified view by Walker to the named work. This candidate relation records "
    "Walker’s reported assessment, not a definitive negative copying or authorship fact about Rubens."
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the reviewed classifications")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    require(actual_sha == EXPECTED_SHA, f"statement table changed since review: {actual_sha}")
    require(not BACKUP.exists(), f"recovery backup already exists: {BACKUP.name}")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    require(len(lines) >= 129, "source note line is missing")
    source_line = lines[128]
    for phrase in ("John Walker suggests that it is unlikely that Rubens made copies of the Worship of Venus and The Andrians",
                   "His versions of these pictures"):
        require(phrase in source_line, f"source line 129 no longer matches {phrase!r}")

    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    require(set(SPECS) <= set(by_id), "one or more reviewed statements are absent")
    with (ROOT / "04-knowledge/tables/entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in __import__("csv").DictReader(handle)}
    for statement_id, (subject, obj, claim) in SPECS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        require(row.get("segment_id") == SEGMENT, f"{statement_id} is outside the reviewed segment")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == (subject, obj),
                f"{statement_id} endpoints changed")
        require(subject in candidate_ids and obj in candidate_ids, f"{statement_id} has a missing endpoint")
        require(qualifiers.get("relation_candidate") is None, f"{statement_id} is already classified")
        require(qualifiers.get("source_line_start") == 129 and qualifiers.get("source_line_end") == 129,
                f"{statement_id} source anchor changed")
        require(qualifiers.get("modality") == "unlikely", f"{statement_id} modality changed")
        require("cand-2293" in qualifiers.get("other_candidate_ids", []),
                f"{statement_id} no longer records Rubens as the disputed copier")
        require(claim == qualifiers.get("claim"), f"{statement_id} claim changed")
        require("John Walker suggests that it is unlikely" in row.get("original_quote", ""),
                f"{statement_id} quote no longer supports Walker attribution")
        row_qualifiers = dict(qualifiers)
        row_qualifiers["relation_candidate"] = True
        row_qualifiers["relation_candidate_note"] = NOTE
        row["qualifiers"] = row_qualifiers

    true_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                         and (row.get("qualifiers") or {}).get("relation_candidate") is True)
    false_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                          and (row.get("qualifiers") or {}).get("relation_candidate") is False)
    pending_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                            and (row.get("qualifiers") or {}).get("relation_candidate") is None)
    require((true_bilateral, false_bilateral, pending_bilateral) == (3983, 450, 4064),
            f"unexpected projected counts: {(true_bilateral, false_bilateral, pending_bilateral)}")
    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    payload = b"".join(output)
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified_true": list(SPECS),
        "classified_false": [],
        "before": {"relation_true_bilateral": 3981, "relation_false_bilateral": 450, "unclassified_bilateral": 4066},
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
        written_by_id = {row["statement_id"]: row for row in written}
        require(all((written_by_id[key].get("qualifiers") or {}).get("relation_candidate") is True for key in SPECS),
                "one or more classifications were not persisted")
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
