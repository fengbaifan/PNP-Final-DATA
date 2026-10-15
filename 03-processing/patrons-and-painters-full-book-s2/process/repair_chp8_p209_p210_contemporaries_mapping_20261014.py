"""Correct p.210 references inherited from the Ruffo index subentry."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
BACKUP_SUFFIX = ".bak-s2-chp8-p209-p210-contemporaries-link-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "06b8d22acd86f1e99fe123cc682e5784e65676a58d3b8336859477669a617e2f",
    MENTIONS: "8d351b5949c23a2cc2ce633420ac83afb11af57f3752abf7b976b9332378371d",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.apply:
        statement_backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
        mention_backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
        current_statement_hash = sha(STATEMENTS.read_bytes()) if STATEMENTS.exists() else None
        current_mention_hash = sha(MENTIONS.read_bytes()) if MENTIONS.exists() else None
        if (
            statement_backup.exists()
            and mention_backup.exists()
            and sha(statement_backup.read_bytes()) == EXPECTED_HASHES[STATEMENTS]
            and sha(mention_backup.read_bytes()) == EXPECTED_HASHES[MENTIONS]
            and current_statement_hash == "5190aef282907eb2879a558f55c50290c24ecd1a73436245419c21e053326d37"
            and current_mention_hash == EXPECTED_HASHES[MENTIONS]
        ):
            expected_mention_hash = "7890100a9cb7cd78f3fe163d19133fc353dfbecf7d239d71b396fd93ecabd095"
            temp_matches = [path for path in TABLES.glob("tmp*.tmp") if sha(path.read_bytes()) == expected_mention_hash]
            if len(temp_matches) != 1:
                raise SystemExit(f"partial-apply recovery expected one verified mention temp file, found {len(temp_matches)}")
            temporary = temp_matches[0]
            # The target allowed read/write access but denied atomic replacement. Its verified backup remains available.
            with MENTIONS.open("r+b") as target, temporary.open("rb") as source:
                target.seek(0)
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)
                target.truncate()
                target.flush()
                os.fsync(target.fileno())
            if sha(MENTIONS.read_bytes()) != expected_mention_hash:
                raise SystemExit("in-place recovery write did not match the verified mention payload")
            temporary.unlink()
            print("completed partial apply: mentions.csv now matches the verified payload")
            print("recovery copies retained:", statement_backup.name, mention_backup.name)
            print("book-statements.jsonl sha256:", current_statement_hash)
            print("mentions.csv sha256:", expected_mention_hash)
            return

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED_HASHES:
        raise SystemExit("statement or mention table changed since this correction was reviewed")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in EXPECTED_HASHES}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("a recovery copy already exists; inspect it before applying this correction")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8").splitlines() if line.strip()]
    mention_reader = csv.DictReader(io.StringIO(raw[MENTIONS].decode("utf-8-sig"), newline=""))
    mention_fields, mentions = mention_reader.fieldnames, list(mention_reader)
    by_statement = {row["statement_id"]: row for row in statements}
    by_mention = {row["mention_id"]: row for row in mentions}
    if len(by_statement) != len(statements) or len(by_mention) != len(mentions):
        raise SystemExit("statement or mention IDs are not unique")

    expected_ids = {
        "st-chp8-p209-ruffo-aimed-for-representative-collection-open",
        "st-chp8-p210-ruffo-collection-of-leading-contemporaries",
    }
    if not expected_ids.issubset(by_statement):
        raise SystemExit("one of the linked collecting-aim statements is missing")
    for statement_id in expected_ids:
        q = dict(by_statement[statement_id].get("qualifiers") or {})
        if q.get("mentioned_candidate_ids") != ["cand-2297", "cand-7468", "cand-2301"]:
            raise SystemExit(f"unexpected candidate references in {statement_id}")
        q["mentioned_candidate_ids"] = ["cand-2297", "cand-7468", "cand-12039"]
        by_statement[statement_id]["qualifiers"] = q

    contemporaries = by_mention.get("m-chp8-p210-001")
    if not contemporaries or (contemporaries.get("candidate_id"), contemporaries.get("surface_form")) != ("cand-2301", "contemporaries"):
        raise SystemExit("p.210 contemporaries mention no longer matches the reviewed prestate")
    contemporaries["candidate_id"] = "cand-12039"
    contemporaries["note"] = "Unspecified painter contemporaries; this completes the p.209 source phrase, and no members are named here."

    motive = by_mention.get("m-chp8-p210-005")
    if not motive or (motive.get("candidate_id"), motive.get("surface_form")) != ("cand-2301", "this motive"):
        raise SystemExit("p.210 motive mention no longer matches the reviewed prestate")
    mentions = [row for row in mentions if row["mention_id"] != motive["mention_id"]]

    if any("cand-2301" in (row.get("qualifiers") or {}).get("mentioned_candidate_ids", []) for row in statements):
        raise SystemExit("a statement still uses the Ruffo index subentry as a painter-group endpoint")
    if any(row["candidate_id"] == "cand-2301" for row in mentions):
        raise SystemExit("a mention still maps to the Ruffo index subentry instead of the referent")
    if len(statements) != 14238 or len(mentions) != 28072:
        raise SystemExit(f"unexpected post-correction counts: statements={len(statements)}, mentions={len(mentions)}")

    statement_data = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
    csv_stream = io.StringIO(newline="")
    writer = csv.DictWriter(csv_stream, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(mentions)
    mention_data = csv_stream.getvalue().encode("utf-8")
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    print("remapped:", "m-chp8-p210-001 cand-2301 -> cand-12039")
    print("removed non-entity anaphor:", "m-chp8-p210-005 'this motive'")
    print("linked statements:", ", ".join(sorted(expected_ids)))
    print("statements:", len(statements), "mentions:", len(mentions))
    print("book-statements.jsonl sha256:", sha(statement_data))
    print("mentions.csv sha256:", sha(mention_data))
    if args.apply:
        for path, backup in backups.items():
            backup.write_bytes(raw[path])
        for path, data in ((STATEMENTS, statement_data), (MENTIONS, mention_data)):
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
                handle.write(data)
                temp = Path(handle.name)
            temp.replace(path)
        print("recovery copies:", ", ".join(str(x.relative_to(ROOT)) for x in backups.values()))


if __name__ == "__main__":
    main()
