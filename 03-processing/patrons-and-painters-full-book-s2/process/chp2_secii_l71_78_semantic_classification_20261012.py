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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
SOURCE_SHA = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l71-78"
SEGMENT_SHA = "4553743974bb21f3bdf2c258c0c6d80807998e704df129b44061ac34ad97749f"
STATEMENT_ID = "st-chp2-secii-l71-78-section-wide-bibliography-pointer"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l71-78-20261012"
EXPECTED = {
    "book-statements.jsonl": "e30e0e8d49ef2196c240ef55947cc8340382220cf3cc3367e7ed6da0d7c66c07",
    "entity-candidates.csv": "168052abd79d9a7c72735690564aaa538fd8e048993aaac9971d77aee3f4baaf",
    "mentions.csv": "948ffdc32c6d07f5b84dbf0c695223eeec60da9f347464b6bd5c0a14d6dc4b87",
    "s2-coverage.csv": "73e4cdc2df45507f74048eaced170247a92c932fd5a20ad1b28978cf9ac514cf",
}


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
    parser = argparse.ArgumentParser()
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
        raise SystemExit("protected p.38 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_ids = {row["candidate_id"] for row in candidates}
    row = statement_by_id.get(STATEMENT_ID)
    if not row or row.get("segment_id") != SEGMENT_ID:
        raise SystemExit("expected p.38 bibliography statement is missing")
    if row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit("p.38 bibliography statement is no longer unset")
    if row.get("object_candidate_id") != "cand-4472" or row.get("qualifiers", {}).get("additional_archive_candidate_ids") != ["cand-4473"]:
        raise SystemExit("expected two archive endpoints changed; re-review before applying")
    if not {"cand-2962", "cand-4472", "cand-4473"} <= candidate_ids:
        raise SystemExit("book archive or cited archive candidates are missing")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[70:78])
    for mention in mentions:
        if mention["segment_id"] == SEGMENT_ID:
            start, end = int(mention["start_char"]), int(mention["end_char"])
            if source_text[start:end] != mention["surface_form"]:
                raise SystemExit(f"existing p.38 mention span changed or is invalid: {mention['mention_id']}")

    row["subject_candidate_id"] = "cand-2962"
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = False
    qualifiers["relation_candidate_note"] = (
        "This is a section-wide bibliographic locator, not a substantive relation claim. "
        "Keep the two cited archive candidates, precise mentions, OCR correction, and footnote linkage for citation traceability; do not export it as a formal entity relation."
    )
    qualifiers["mentioned_candidate_ids"] = ["cand-4472", "cand-4473"]

    coverage_rows = [item for item in coverage if item["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.38 coverage row")
    coverage_note = (
        " S2 follow-up classified the section-wide bibliography pointer as citation metadata rather than a substantive relation candidate. "
        "Both cited works remain mapped to their existing archive candidates and mention anchors; the printed p.38 scan confirms Briganti where S0 OCR reads Brigand."
    )
    if coverage_note.strip() not in coverage_rows[0]["note"]:
        coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + coverage_note

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2 printed p.38 / normalized S0 L71-78",
        "classified_statement": STATEMENT_ID,
        "relation_candidate": False,
        "subject_candidate_id": "cand-2962",
        "archive_endpoints": ["cand-4472", "cand-4473"],
        "remaining_unset_in_segment": [],
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(serialize(name, rows)).hexdigest() for name, rows in updated.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, rows in updated.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(serialize(name, rows))
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_row = next(item for item in written if item["statement_id"] == STATEMENT_ID)
        if written_row.get("qualifiers", {}).get("relation_candidate") is not False:
            raise SystemExit("p.38 non-relation classification was not persisted")
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
