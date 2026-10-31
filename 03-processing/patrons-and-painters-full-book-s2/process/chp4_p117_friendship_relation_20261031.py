"""Register the single supported friendship edge from two p.117 statements."""

from __future__ import annotations

import argparse
import csv
import io
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RELATIONS = ROOT / "04-knowledge" / "tables" / "relations.csv"
ALIGNMENTS = ROOT / "04-knowledge" / "tables" / "alignment.csv"
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
BACKUP = RELATIONS.with_name("relations.csv.bak-s6-chp4-p117-friendship-20261031")

SUBJECT = "units/persons/camillo-massimi"
OBJECT = "units/persons/nicolas-poussin"
STATEMENT_IDS = (
    "st-chp4-sec-ii-p117-poussin-relationship",
    "st-chp4-sec-ii-p117-poussin-massimi-friendship",
)


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]], str, bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return raw, reader.fieldnames or [], list(reader), eol, has_bom


def append_row(raw: bytes, fields: list[str], row: dict[str, str], eol: str, has_bom: bool) -> bytes:
    prefix = b"\xef\xbb\xbf" if has_bom else b""
    body = raw[len(prefix):] if has_bom else raw
    if body and not body.endswith((b"\n", b"\r")):
        body += eol.encode("ascii")
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=fields, lineterminator=eol).writerow(row)
    return prefix + body + buffer.getvalue().encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, _, alignments, _, _ = read_csv(ALIGNMENTS)
    aligned = {row["candidate_id"]: row["ku_id"] for row in alignments if row["decision"] == "same" or row["decision"] == "new"}
    if (aligned.get("cand-1564"), aligned.get("cand-1984")) != (SUBJECT, OBJECT):
        raise SystemExit("person endpoint alignment precondition failed")

    statement_rows = {}
    for line in STATEMENTS.read_text(encoding="utf-8").splitlines():
        import json

        record = json.loads(line)
        if record.get("statement_id") in STATEMENT_IDS:
            statement_rows[record["statement_id"]] = record
    if set(statement_rows) != set(STATEMENT_IDS):
        raise SystemExit("missing friendship statement")
    if any(row["qualifiers"].get("relation_candidate") is not True for row in statement_rows.values()):
        raise SystemExit("friendship statements are not both relation candidates")
    if any(
        (row["subject_candidate_id"], row["object_candidate_id"])
        != ("cand-1564", "cand-1984")
        for row in statement_rows.values()
    ):
        raise SystemExit("friendship statement endpoint precondition failed")

    source = SOURCE.read_text(encoding="utf-8-sig")
    if "and above all he too enjoyed the closest relationship possible with Poussin" not in source:
        raise SystemExit("missing p.117 relationship source phrase")
    if "Certainly the two men established a very close friendship." not in source:
        raise SystemExit("missing p.117 friendship source phrase")

    raw, fields, rows, eol, has_bom = read_csv(RELATIONS)
    if not fields or set(fields) != {
        "relation_id", "subject_ku_id", "object_ku_id", "predicate", "time", "role",
        "scope", "origin", "status", "source_id", "source_span", "source_file", "note",
    }:
        raise SystemExit("unexpected relations.csv schema")
    if any(
        row["predicate"] == "friend_of"
        and {row["subject_ku_id"], row["object_ku_id"]} == {SUBJECT, OBJECT}
        for row in rows
    ):
        raise SystemExit("friendship edge already exists")
    max_id = max(int(match.group(1)) for row in rows if (match := re.fullmatch(r"rel-(\d+)", row["relation_id"])))
    relation_id = f"rel-{max_id + 1:04d}"
    row = {
        "relation_id": relation_id,
        "subject_ku_id": SUBJECT,
        "object_ku_id": OBJECT,
        "predicate": "friend_of",
        "time": "",
        "role": "朋友",
        "scope": "Haskell says Massimi enjoyed the closest possible relationship with Poussin and that the two men established a very close friendship; these are two reports of one relationship, not separate phases.",
        "origin": "book",
        "status": "formal",
        "source_id": "haskell-1980-rev-ed",
        "source_span": "Chapter 4, printed p.117, lines 211 and 215; statements=" + ";".join(STATEMENT_IDS),
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "note": "Consolidates two Haskell statements into one supported friend_of edge; no distinct friendship phases inferred.",
    }
    print(f"proposed={relation_id} {SUBJECT} friend_of {OBJECT} formal")
    print(f"source_statements={';'.join(STATEMENT_IDS)}")
    print("domain_range=person->person; predicate is symmetric and controlled")
    if not args.apply:
        print("DRY RUN: no files written")
        return 0
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP}")
    shutil.copy2(RELATIONS, BACKUP)
    temp = RELATIONS.with_suffix(RELATIONS.suffix + ".tmp")
    temp.write_bytes(append_row(raw, fields, row, eol, has_bom))
    temp.replace(RELATIONS)
    print(f"backup={BACKUP}")
    print(f"updated={RELATIONS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
