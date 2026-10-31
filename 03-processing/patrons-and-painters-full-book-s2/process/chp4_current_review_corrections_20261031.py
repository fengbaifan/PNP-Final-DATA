"""Apply corrections confirmed by independent review of current Chapter 4 rows."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
RELATIONS = ROOT / "04-knowledge" / "tables" / "relations.csv"
ALIGNMENTS = ROOT / "04-knowledge" / "tables" / "alignment.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
STATEMENT_BACKUP = STATEMENTS.with_name(
    "book-statements.jsonl.bak-independent-review-ch4-20261031"
)
RELATION_BACKUP = RELATIONS.with_name(
    "relations.csv.bak-independent-review-ch4-20261031"
)

S2_CORRECTIONS = {
    "st-chp4-sec-ii-p102-footnote4-cigoli-galilei": "cand-5712",
    "st-chp4-sec-ii-p117-french-protested-violently": "cand-4591",
}


def read_relations() -> tuple[bytes, list[str], list[dict[str, str]], str, bool]:
    raw = RELATIONS.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    fields = list(rows[0]) if rows else []
    expected = {
        "relation_id", "subject_ku_id", "object_ku_id", "predicate", "time",
        "role", "scope", "origin", "status", "source_id", "source_span",
        "source_file", "note",
    }
    if set(fields) != expected:
        raise SystemExit("unexpected relations.csv schema")
    return raw, fields, rows, eol, has_bom


def append_relation(
    raw: bytes, fields: list[str], row: dict[str, str], eol: str, has_bom: bool
) -> bytes:
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

    statement_lines = STATEMENTS.read_text(encoding="utf-8").splitlines(keepends=True)
    statement_rows: dict[str, dict] = {}
    replacement_lines = list(statement_lines)
    for index, line in enumerate(statement_lines):
        record = json.loads(line)
        statement_id = record.get("statement_id")
        if statement_id in S2_CORRECTIONS:
            if statement_id in statement_rows:
                raise SystemExit(f"duplicate statement ID: {statement_id}")
            statement_rows[statement_id] = record
            ids = record.get("qualifiers", {}).get("mentioned_candidate_ids", [])
            stale_id = S2_CORRECTIONS[statement_id]
            if ids.count(stale_id) != 1:
                raise SystemExit(f"expected one {stale_id} in {statement_id}")
            record["qualifiers"]["mentioned_candidate_ids"] = [
                candidate_id for candidate_id in ids if candidate_id != stale_id
            ]
            newline = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            replacement_lines[index] = json.dumps(record, ensure_ascii=False) + newline
    if set(statement_rows) != set(S2_CORRECTIONS):
        raise SystemExit("one or more expected current statements are missing")

    training_id = "st-chp4-sec-ii-p117-lessons-from-poussin"
    citation_id = "st-chp4-sec-ii-p115-fn2-sources"
    all_statements = {
        record["statement_id"]: record
        for record in (json.loads(line) for line in statement_lines)
    }
    for statement_id in (training_id, citation_id):
        statement = all_statements.get(statement_id)
        if not statement or statement.get("qualifiers", {}).get("relation_candidate") is not True:
            raise SystemExit(f"missing relation candidate: {statement_id}")

    source = SOURCE.read_text(encoding="utf-8-sig")
    for phrase in (
        "Naturally enough the French, who were everywhere taking the initiative in Europe",
        "See Cigoli-Galilei Carteggio edited by A. Matteoli.",
        "For Camillo Massimi see Litta, Moroni and the Abbate Michele Giustiniani",
        "probably took lessons",
    ):
        if phrase not in source:
            raise SystemExit(f"source precondition failed: {phrase}")

    with ALIGNMENTS.open(encoding="utf-8-sig", newline="") as stream:
        aligned = {
            row["candidate_id"]: row["ku_id"]
            for row in csv.DictReader(stream)
            if row["decision"] in {"same", "new"}
        }
    if (aligned.get("cand-1564"), aligned.get("cand-1984")) != (
        "units/persons/camillo-massimi", "units/persons/nicolas-poussin"
    ):
        raise SystemExit("trained_by endpoint alignment precondition failed")
    if aligned.get("cand-4842") != "units/archives/famiglie-celebri-italiane-litta-1819-1881":
        raise SystemExit("cites endpoint alignment precondition failed")

    raw, fields, rows, eol, has_bom = read_relations()
    expected_relations = [
        {
            "subject_ku_id": "units/persons/camillo-massimi",
            "object_ku_id": "units/persons/nicolas-poussin",
            "predicate": "trained_by",
            "source_span": f"Chapter 4, printed p.117, lines 215-216; statement={training_id}",
            "role": "学生（推测）",
            "scope": "Haskell says Massimi probably took lessons from Poussin. The qualified report does not establish an unqualified training relationship; footnote 5's cited inscription was not independently inspected.",
            "note": "Pending S6: preserve 'probably'; do not assert an established teacher-student relationship.",
        },
        {
            "subject_ku_id": "units/archives/patrons-and-painters",
            "object_ku_id": aligned["cand-4842"],
            "predicate": "cites",
            "source_span": f"Chapter 4, printed p.115, note 2, line 293; statement={citation_id}",
            "role": "引文目标待识别",
            "scope": "Haskell's note lists Litta, Moroni and Abbate Michele Giustiniani together with 'III, p. 319'; the locator cannot be uniquely assigned to the Famiglie celebri italiane candidate.",
            "note": "Pending S6: retain the citation candidate, but do not formalize until the title-to-locator match is resolved.",
        },
    ]
    for proposed in expected_relations:
        if any(
            row["subject_ku_id"] == proposed["subject_ku_id"]
            and row["object_ku_id"] == proposed["object_ku_id"]
            and row["predicate"] == proposed["predicate"]
            for row in rows
        ):
            raise SystemExit(f"duplicate relation natural key: {proposed['predicate']}")

    max_id = max(
        int(match.group(1))
        for row in rows
        if (match := re.fullmatch(r"rel-(\d+)", row["relation_id"]))
    )
    relation_rows = []
    for offset, proposed in enumerate(expected_relations, start=1):
        relation_rows.append(
            {
                **{field: "" for field in fields},
                **proposed,
                "relation_id": f"rel-{max_id + offset:04d}",
                "time": "",
                "origin": "book",
                "status": "pending",
                "source_id": "haskell-1980-rev-ed",
                "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            }
        )

    proposed_relation_bytes = raw
    for row in relation_rows:
        proposed_relation_bytes = append_relation(
            proposed_relation_bytes, fields, row, eol, has_bom
        )
    proposed_statement_bytes = "".join(replacement_lines).encode("utf-8")

    print("S2 corrections:")
    for statement_id, candidate_id in S2_CORRECTIONS.items():
        print(f"  {statement_id}: remove unrelated candidate {candidate_id}")
    print("S6 pending decisions:")
    for row in relation_rows:
        print(f"  {row['relation_id']} {row['predicate']} pending; {row['source_span']}")
    if not args.apply:
        print("DRY RUN: no files written")
        return 0

    for backup in (STATEMENT_BACKUP, RELATION_BACKUP):
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(STATEMENTS, STATEMENT_BACKUP)
    shutil.copy2(RELATIONS, RELATION_BACKUP)
    statement_temp = STATEMENTS.with_suffix(STATEMENTS.suffix + ".tmp")
    relation_temp = RELATIONS.with_suffix(RELATIONS.suffix + ".tmp")
    statement_temp.write_bytes(proposed_statement_bytes)
    relation_temp.write_bytes(proposed_relation_bytes)
    statement_temp.replace(STATEMENTS)
    relation_temp.replace(RELATIONS)
    print(f"updated={STATEMENTS}")
    print(f"updated={RELATIONS}")
    print(f"backups={STATEMENT_BACKUP};{RELATION_BACKUP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
