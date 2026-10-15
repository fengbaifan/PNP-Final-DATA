"""Repair two exact-source anchors found by the strict S2 table audit."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp8-p213-p214-anchor-repair-20261014"
EXPECTED = {
    STATEMENTS: "6f21a846fb26f2cb6896a573e408d01ea4bda05cec9c55cf085d908e497c5351",
    CANDIDATES: "9ff29918d6f3a6ae158a785738b9b55ac6326d43435bd4c8c73b683f2c4581d6",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
P213_SEGMENT_SHA = "ebbb5be59dbc67e1337d077618074f382126d0f7c97e61e385c00514897599f3"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_bytes(fields, rows) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def jsonl_bytes(rows) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = {path: path.read_bytes() for path in EXPECTED}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED:
        raise SystemExit("a table or source changed since the audit-anchor repair was reviewed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    p213_text = "\n".join(source_lines[107:118])
    if sha(p213_text.encode("utf-8")) != P213_SEGMENT_SHA:
        raise SystemExit("p.213 source segment changed since review")
    quote = "As an isolated phenomenon the del Rosso collection with its great emphasis on\nNaples and its total neglect of Rome is of outstanding interest"
    if quote not in "\n".join(source_lines[112:114]):
        raise SystemExit("p.213 quote does not match the cited source lines")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    target = statement_by_id.get("st-chp8-p213-collection-outstanding-interest")
    if not target or (target.get("original_quote"), target["qualifiers"].get("source_line_start"), target["qualifiers"].get("source_line_end")) != (quote, 114, 114):
        raise SystemExit("p.213 statement no longer matches the audit finding")
    target["qualifiers"]["source_line_start"] = 113
    target["qualifiers"]["source_line_end"] = 114

    reader = csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline=""))
    fields, candidates = reader.fieldnames, list(reader)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate = candidate_by_id.get("cand-7573")
    if not candidate or candidate["candidate_source_ref"] != "chp-8:08_CHP-8_sec_i:l120-124#L121-122":
        raise SystemExit("the Giordano canvas candidate no longer matches the audit finding")
    candidate["candidate_source_ref"] = "chp-8:08_CHP-8_sec_i:l120-124#L121"

    outputs = {STATEMENTS: jsonl_bytes(statements), CANDIDATES: csv_bytes(fields, candidates)}
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    print("statement source lines: 114-114 -> 113-114")
    print("cand-7573 source ref: #L121-122 -> #L121")
    for path, data in outputs.items():
        print(path.name, "sha256:", sha(data))
    if args.apply:
        backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
        if any(path.exists() for path in backups.values()):
            raise SystemExit("an anchor-repair recovery copy already exists; inspect it before applying")
        for path, backup in backups.items():
            shutil.copy2(path, backup)
        for path, data in outputs.items():
            atomic_write(path, data)
        print("recovery copies:", ", ".join(path.name for path in backups.values()))


if __name__ == "__main__":
    main()
