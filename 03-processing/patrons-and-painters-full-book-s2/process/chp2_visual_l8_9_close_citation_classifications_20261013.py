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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii_visual-transcription.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii_visual-transcription:l8-9"
SEGMENT_SHA = "b39c4f81a1562544497b3e118913c379d95fc5cfedeefe5f7dbb264ad9cafd77"
SOURCE_SHA = "494aeb540e1ab40ae538f63377fd8bb18c469006690161969e0729cbc179835d"
BACKUP_SUFFIX = ".bak-s2-chp2-visual-l8-9-citations-20261013"
EXPECTED = {
    "book-statements.jsonl": "a9240b2ba04c97d09831bc0aafcbee744a51c6883bebeeb2d47f012e689656db",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "f926e9a17b40756fdb7f2c36fe445ed82d82b7fa9884fc185599df91c888bdc6",
}
STATEMENT_IDS = {
    "st-chp2-secii-visual-l8-9-cite-briganti-1962",
    "st-chp2-secii-visual-l8-9-cite-mostra-1956",
}
NOTE = (
    "This is a section-wide bibliographic pointer copied from the printed footnote into the visual-transcription source; "
    "the reference is already represented by the linked body citation statement and is not an additional entity relation."
)


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
    parser = argparse.ArgumentParser(description="Classify the printed p.38 visual footnote continuation as citation metadata.")
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected visual-transcription source asset changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.38 visual-transcription segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    coverage = read_csv(paths["s2-coverage.csv"])
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != STATEMENT_IDS:
        raise SystemExit(f"unexpected p.38 visual-transcription unset IDs: {sorted(unset)}")
    if any(by_id[sid].get("predicate") != "footnote_citation" for sid in STATEMENT_IDS):
        raise SystemExit("a protected p.38 row is not a citation statement")
    source_text = SOURCE.read_text(encoding="utf-8-sig")
    quote = "For this whole section see Mostra di Pietro da Cortona, 1956, and Briganti, 1962."
    if quote not in source_text or any(by_id[sid].get("original_quote") != quote for sid in STATEMENT_IDS):
        raise SystemExit("the p.38 continuation quote changed")
    if any(by_id[sid].get("qualifiers", {}).get("linked_body_statement_ids") != ["st-chp2-secii-l71-78-section-wide-bibliography-pointer"] for sid in STATEMENT_IDS):
        raise SystemExit("the citations are no longer linked to the section-wide body pointer")
    if len([row for row in coverage if row.get("segment_id") == SEGMENT_ID]) != 1:
        raise SystemExit("expected one visual-transcription coverage row")

    for sid in STATEMENT_IDS:
        row = by_id[sid]
        qualifiers = row.setdefault("qualifiers", {})
        qualifiers["relation_candidate"] = False
        qualifiers["relation_candidate_note"] = NOTE
        qualifiers["mentioned_candidate_ids"] = [row["object_candidate_id"]]

    coverage_row = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    coverage_note = (
        " S2 follow-up classifies the two printed p.38 footnote references (Mostra di Pietro da Cortona, 1956; Briganti, 1962) "
        "as citation metadata. Both remain linked to the section-wide bibliography statement at L78; the print correction 'Briganti' "
        "versus OCR 'Brigand' is retained in the existing qualifier. No additional entity relation or source rewrite was made."
    )
    if coverage_note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_note

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    payloads = {name: serialize(name, rows) for name, rows in updated.items()}
    print(json.dumps({
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "classified_unset_ids": sorted(STATEMENT_IDS),
        "classification": "false; citation metadata",
        "existing_body_pointer_preserved": True,
        "new_statements": 0,
        "new_candidates": 0,
        "new_mentions": 0,
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
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
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if any(written_by_id[sid]["qualifiers"].get("relation_candidate") is not False for sid in STATEMENT_IDS):
            raise SystemExit("a p.38 citation classification was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("visual-transcription source changed during write")
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
