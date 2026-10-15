from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l69-76"
STATEMENT_ID = "st-chp8-p217-liberi-nudes-upset-bergamasque-susceptibilities"
BACKUP_SUFFIX = "bak-s2-chp8-p217-bergamasque-susceptibilities-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "1d75b32caa7b5491b9f8f191a9e406d263847c150983b2365f7cc058c7eeb0e5",
    "mentions.csv": "5d2dfcd72b8ac1f466c6f480eed8e3a792ebca541fb7b61748d5f3cd50910630",
    "book-statements.jsonl": "03909e32f7e4581bb585012cc2820698b5e21bc26affea0c266e94a20ee92afb",
}
EXPECTED_SEGMENT_HASH = "424e930247b9ca7b94a47d08addacc2514789fa1eaed04515ade100ac939b7d1"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open(row: dict[str, object]) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [row for row in rows if is_open(row)]
    object_only = sum(bool(r.get("subject_candidate_id")) and not r.get("object_candidate_id") for r in opens)
    subject_only = sum(not r.get("subject_candidate_id") and bool(r.get("object_candidate_id")) for r in opens)
    both = sum(not r.get("subject_candidate_id") and not r.get("object_candidate_id") for r in opens)
    return len(opens), object_only, subject_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    raw_by_name = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(raw_by_name[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    segment = next(
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Source segment changed")
    source_path = ROOT / segment["source_file"]
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    source = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    surface = "Bergamasque susceptibilities"
    start = source.find(surface)
    if start < 0 or source.find(surface, start + 1) >= 0:
        raise ValueError("Expected unique source mention was not found")

    candidate_id = "cand-12369"
    candidate_name = "Bergamasque susceptibilities in Haskell's probable explanation of Liberi's nudes"
    if any(row["candidate_id"] == candidate_id or row["canonical_name"] == candidate_name for row in candidates):
        raise ValueError("Candidate ID or name already exists")
    line_no = int(segment["line_start"]) + source.count("\n", 0, start)
    candidate = {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": candidate_name,
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "A cultural response concept that Haskell presents as the most probable explanation for the reception of Liberi's nudes. Preserve it as his attributed, uncertain interpretation, not a verified description of all Bergamasque viewers.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
    }
    mention_id = "m-chp8-cand-12369-source-mention"
    if any(row["mention_id"] == mention_id for row in mentions):
        raise ValueError("Mention ID already exists")
    mention = {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": candidate["detail"],
    }

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    statement = next((row for row in rows if row.get("statement_id") == STATEMENT_ID), None)
    if statement is None or not is_open(statement) or statement.get("subject_candidate_id") != "cand-1401":
        raise ValueError("Expected open Liberi statement not found")
    statement["object_candidate_id"] = candidate_id
    q = statement.get("qualifiers") or {}
    q["mentioned_candidate_ids"] = list(
        dict.fromkeys((q.get("mentioned_candidate_ids") or []) + [candidate_id])
    )
    q["relation_candidate_note"] = "Haskell names 'Bergamasque susceptibilities' as the object of his explicitly probable explanation; retain the attribution and uncertainty without treating it as a verified fact about every local viewer."
    q.pop("open_endpoint_reason", None)
    statement["qualifiers"] = q

    after_counts = endpoint_counts(rows)
    if after_counts != (436, 274, 58, 104):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")
    candidate_after = append_rows(candidate_raw, candidate_fields, [candidate])
    mention_after = append_rows(mention_raw, mention_fields, [mention])
    statement_after = (
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    ).encode("utf-8")
    print(f"candidate_rows={len(candidates)}->{len(candidates) + 1}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + 1}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    print(f"resolved_statement={STATEMENT_ID}|object->{candidate_id}")
    print(f"open_endpoints={endpoint_counts([json.loads(x) for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{after_counts}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = ((CANDIDATES, candidate_after), (MENTIONS, mention_after), (STATEMENTS, statement_after))
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temp, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temp, data in pairs:
            temp.write_bytes(data)
        for path, backup, temp, _ in pairs:
            temp.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temp, _ in pairs:
            if temp.exists():
                temp.unlink()
        for path, backup in replaced:
            shutil.copy2(backup, path)
        raise
    for path, backup, _, _ in pairs:
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
