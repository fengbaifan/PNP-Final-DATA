from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l31-43"
SEGMENT_SHA = "24c57f448578597f0570312dc6bca4744243c4f02872a4f4fba78dc979529abe"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
STATEMENT_ID = "st-chp2-seciv-l31-43-taddeo-characterization"
CONTINUATION_ID = "st-chp2-seciv-l45-52-taddeo-intellectual-resources"
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l31-43-characterization-20261013"
EXPECTED = {
    "book-statements.jsonl": "20da4338a32b53ca618161e7e0aa2cc44d9dd19e900ab9f272654f801f2052e0",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "a6f4514eabff8568f6327e32b0557130fd8a3e1592a0827ce4c67e9055fc6a54",
}
RAW_QUOTE = "- vTaddeo was at once the weakest and the most brutal of the Barberini."
BACKUP_MARK = ".bak-s2-chp2-seciv-l31-43-characterization-20261013"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Separate Taddeo's printed character assessment from the following cross-page fragment in CHP-2 section IV, L31-43."
    )
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected print-p.46 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    coverage = read_csv(paths["s2-coverage.csv"])
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    row = by_id.get(STATEMENT_ID)
    continuation = by_id.get(CONTINUATION_ID)
    if not row or row.get("segment_id") != SEGMENT_ID:
        raise SystemExit("protected Taddeo statement is missing or moved")
    if not continuation or continuation.get("segment_id") != "chp-2:02_CHP-2_sec_iv:l45-52":
        raise SystemExit("expected linked L45-52 intellectual-resources continuation")
    unset = {
        item["statement_id"] for item in statements
        if item.get("segment_id") == SEGMENT_ID and item.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != {STATEMENT_ID}:
        raise SystemExit(f"unexpected L31-43 unset statement set: {sorted(unset)}")
    if row.get("subject_candidate_id") != "cand-0239" or row.get("object_candidate_id") is not None:
        raise SystemExit("protected Taddeo characterization endpoints changed")
    if row.get("original_quote") != "- vTaddeo was at once the weakest and the most brutal of the Barberini. He lacked the":
        raise SystemExit("protected source transcription changed")
    source_text = SOURCE.read_text(encoding="utf-8-sig")
    if RAW_QUOTE not in source_text:
        raise SystemExit("the protected Taddeo characterization quote no longer matches S0")
    if len([item for item in coverage if item.get("segment_id") == SEGMENT_ID]) != 1:
        raise SystemExit("expected one print-p.46 L31-43 coverage row")

    row["original_quote"] = RAW_QUOTE
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["claim"] = "Haskell describes Taddeo as the weakest and most brutal of the Barberini."
    qualifiers["qualification"] = (
        "The printed page has a separate '- v -' section divider before 'Taddeo'; S0 OCR merged part of the divider into '- vTaddeo'. "
        "This statement covers only the first sentence. The following 'He lacked the' fragment continues in L45-52 as a separate claim."
    )
    qualifiers["relation_candidate"] = False
    qualifiers["relation_candidate_note"] = (
        "This is Haskell's evaluative characterization of Taddeo's relative character, not an entity relation."
    )
    qualifiers["mentioned_candidate_ids"] = ["cand-0239"]
    qualifiers["related_statement_ids"] = [CONTINUATION_ID]
    for key in ("continuation_segment_id", "continuation_source_line", "continuation_to_statement_id"):
        qualifiers.pop(key, None)

    coverage_row = next(item for item in coverage if item.get("segment_id") == SEGMENT_ID)
    coverage_note = (
        " 本轮将Taddeo“the weakest and the most brutal”独立为作者评价（非关系），并从本句剥离跨页残句“He lacked the”；"
        "该残句在l45–52另有对应断言。页图确认印刷p.46的“- v -”为章节分隔符，S0误并至Taddeo姓名；仅在S2记录，不改来源。"
    )
    if coverage_note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_note

    payloads = {
        "book-statements.jsonl": serialize("book-statements.jsonl", statements),
        "s2-coverage.csv": serialize("s2-coverage.csv", coverage),
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "classified_unset_ids": [STATEMENT_ID],
        "classification": False,
        "quote_scope": "first sentence only; cross-page clause linked separately",
        "linked_continuation_statement": CONTINUATION_ID,
        "source_asset_unchanged": True,
        "remaining_unset_in_segment": [],
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_MARK)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = next(item for item in read_jsonl(paths["book-statements.jsonl"]) if item["statement_id"] == STATEMENT_ID)
        if written.get("qualifiers", {}).get("relation_candidate") is not False:
            raise SystemExit("the Taddeo characterization classification was not persisted")
        if written.get("original_quote") != RAW_QUOTE:
            raise SystemExit("the Taddeo statement scope was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
