#!/usr/bin/env python3
"""Classify the remaining p.336 S2 statements; dry-run unless --apply is passed."""

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
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l41-50"
SEGMENT_SHA256 = "575ec0ac309dcec132ec190a56e047e1d634a0407f4a40453f06764329833fde"
PRE_HASHES = {
    STATEMENTS.name: "a91ad69f059749d542abd5f5a0b6eee617ad665403d23a5c37a565d9d290a908",
    CANDIDATES.name: "a3aa675b332c6c1b17f387eb477d121fee4014906574d54ab2a9abc69f1c4fa3",
    MENTIONS.name: "56207317fc2f80761b4f541123d09f90384b7638bc6705e5b71850e3e2554f20",
}
BACKUP_SUFFIX = ".bak-s2-ch13-p336-semantic-review-20261014"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_atomic(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes after all preflight checks")
    args = parser.parse_args()
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = digest(path)
        expected = PRE_HASHES[path.name]
        if actual != expected:
            raise SystemExit(f"preflight failed: {path.name} SHA-256 {actual} != {expected}")
    segment = next((r for r in read_jsonl(TABLES / "segments.jsonl") if r.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.336 segment identity/hash changed")

    statements = read_jsonl(STATEMENTS)
    by_id = {r["statement_id"]: r for r in statements}
    if len(by_id) != len(statements):
        raise SystemExit("preflight failed: duplicate statement_id")
    local = [r for r in statements if r.get("segment_id") == SEGMENT_ID]
    unset = {r["statement_id"] for r in local if r.get("qualifiers", {}).get("relation_candidate") is None}
    decisions = {
        "st-chp13-p336-albrizzi-admired-carriera": True,
        "st-chp13-p336-albrizzi-attempted-to-help-zais": True,
        "st-chp13-p336-albrizzi-died-in-1777-aged-85": False,
        "st-chp13-p336-albrizzi-felt-debt-to-piazzetta": True,
        "st-chp13-p336-albrizzi-influential-patron-evaluation": False,
        "st-chp13-p336-albrizzi-kept-piazzetta-memory-alive": True,
        "st-chp13-p336-albrizzi-shop-flourishing-artistic-centre": True,
        "st-chp13-p336-gherardi-characterisation-of-publishers-open": False,
        "st-chp13-p336-orlando-subscription-project-failed": False,
        "st-chp13-p336-pasquali-independent-and-vigorous": False,
        "st-chp13-p336-pasquali-outlook-differed-from-albrizzi": True,
        "st-chp13-p336-pasquali-produced-luxurious-books": True,
        "st-chp13-p336-piazzetta-died-in-1754": False,
        "st-chp13-p336-piazzetta-french-sophistication": False,
    }
    if unset != set(decisions):
        raise SystemExit(f"preflight failed: unexpected unset IDs: {sorted(unset ^ set(decisions))}")
    for statement_id, value in decisions.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = value

    # The index headword candidate is Piazzetta as a person; the source's actual illustration group is cand-9991.
    plagiarised = by_id["st-chp13-p336-guardi-brothers-plagiarised-gerusalemme-illustrations"]
    if plagiarised.get("subject_candidate_id") != "cand-9999" or plagiarised.get("object_candidate_id") != "cand-9998":
        raise SystemExit("preflight failed: Guardi illustration endpoint changed")
    plagiarised["qualifiers"]["mentioned_candidate_ids"] = ["cand-9999", "cand-1242", "cand-1250", "cand-9998", "cand-9991", "cand-9990", "cand-2545"]
    plagiarised["qualifiers"]["qualification"] = "Haskell's accusation of plagiarism is preserved as his source claim; 'his illustrations' resolves to the approximately seventy Gerusalemme drawings (cand-9991), not the Piazzetta person index row. The series of Guardi canvases remains the statement's object."

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        candidate_reader = csv.DictReader(stream)
        candidate_fields = candidate_reader.fieldnames
        candidates = list(candidate_reader)
    candidate_ids = {r["candidate_id"] for r in candidates}
    if "cand-12142" in candidate_ids:
        raise SystemExit("preflight failed: cand-12142 already exists")
    candidate = {
        "candidate_id": "cand-12142", "index_entry_id": "", "canonical_name": "Fine and luxurious books produced by Giambattista Pasquali (unnamed group)",
        "index_page_range": "", "suggested_type": "archive", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Source-bounded aggregate of books attributed to Pasquali; Haskell calls them fine and luxurious. No individual titles or count are specified.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L49",
    }

    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        mention_reader = csv.DictReader(stream)
        mention_fields = mention_reader.fieldnames
        mentions = list(mention_reader)
    if any(r["mention_id"] == "m-s2-ch13-p336-049" for r in mentions):
        raise SystemExit("preflight failed: m-s2-ch13-p336-049 already exists")
    if any(r["candidate_id"] == "cand-12142" for r in mentions):
        raise SystemExit("preflight failed: an existing mention already uses cand-12142")
    segment_text = "\n".join(SOURCE.read_text(encoding="utf-8").splitlines()[40:50])
    surface = "many fine and luxurious books"
    start = segment_text.find(surface)
    if start < 0 or segment_text.find(surface, start + 1) >= 0:
        raise SystemExit("preflight failed: Pasquali book-group mention is not unique in p.336 segment")
    mention = {
        "mention_id": "m-s2-ch13-p336-049", "segment_id": SEGMENT_ID, "candidate_id": "cand-12142",
        "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)),
        "note": "Source-bounded aggregate of Pasquali publications; no individual title is named.",
    }
    pasquali_books = by_id["st-chp13-p336-pasquali-produced-luxurious-books"]
    if pasquali_books.get("object_candidate_id") is not None:
        raise SystemExit("preflight failed: Pasquali books statement already has an object endpoint")
    pasquali_books["object_candidate_id"] = "cand-12142"
    pasquali_books["qualifiers"]["mentioned_candidate_ids"] = ["cand-1844", "cand-12142"]
    pasquali_books["qualifiers"]["qualification"] = "The source identifies an aggregate publication group but names no individual book; 'fine and luxurious' remains Haskell's characterization."
    for row in mentions:
        if row["mention_id"] == "m-s2-ch13-p336-013":
            if row["candidate_id"] != "cand-1913":
                raise SystemExit("preflight failed: expected illustration mention mapping changed")
            row["candidate_id"] = "cand-9991"
            break
    else:
        raise SystemExit("preflight failed: m-s2-ch13-p336-013 not found")
    mentions.append(mention)
    candidates.append(candidate)

    print(f"segment={SEGMENT_ID}; SHA-256={SEGMENT_SHA256}; statements={len(local)}; unset classified={len(decisions)}")
    for statement_id, value in decisions.items():
        print(f"  {statement_id}: {value}")
    print("mention repair: Guardi plagiarism claim reference cand-1913 -> cand-9991 (Gerusalemme drawing group); canvas-series endpoint cand-9998 retained")
    print("new candidate: cand-12142 (Pasquali's unnamed fine and luxurious books)")
    print(f"new mention: m-s2-ch13-p336-049 [{start},{start + len(surface)}): {surface!r}")
    print("mention repair: m-s2-ch13-p336-013 cand-1913 -> cand-9991")
    if not args.apply:
        print("DRY RUN only; no files written. Pass --apply to write after review.")
        return

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False) for row in statements) + "\n").encode("utf-8")
    def csv_bytes(fields: list[str], rows: list[dict]) -> bytes:
        with tempfile.SpooledTemporaryFile(mode="w+", encoding="utf-8-sig", newline="", max_size=8 * 1024 * 1024) as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows); stream.seek(0)
            return stream.read().encode("utf-8-sig")
    write_atomic(STATEMENTS, statement_bytes)
    write_atomic(CANDIDATES, csv_bytes(candidate_fields, candidates))
    write_atomic(MENTIONS, csv_bytes(mention_fields, mentions))
    print("APPLIED. Backups saved for statements, candidates, and mentions.")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"  {path.name}: {digest(path)}")


if __name__ == "__main__":
    main()
