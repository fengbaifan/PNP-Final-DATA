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
SOURCE = ROOT / "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l120-124"
STATEMENT_ID = "st-chp8-p214-baglioni-family-publishers-and-nobility"
NOBILITY_CANDIDATE_ID = "cand-8108"
MENTION_ID = "m-chp8-p214-040"
SURFACE_FORM = "the nobility"
CONTAINING_MENTION_ID = "m-chp8-p214-025"
BACKUP_SUFFIX = "bak-s2-chp8-p214-venetian-nobility-endpoint-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "bf6ac1f8a45a04995907a614d875e5ff2e1611941fc46e332091a7cf086bb81d",
    "mentions.csv": "8aa6d919cc6ffdc9af1fed84e91548298976003494cadb0cd5636092ea4b9e9b",
    "book-statements.jsonl": "0687a82c9d71db923385472842a063a5f96094aa50e65d03ce2af16529b01ef9",
}
EXPECTED_SEGMENT_HASH = "021c88a32fcf270e3b3425913361730c08754daaaf5edaeddef950e5ef1d71c7"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"), extrasaction="raise")
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open_true(row: dict[str, object]) -> bool:
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, _, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    actual = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(actual[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    candidate_index = {row["candidate_id"]: row for row in candidates}
    if NOBILITY_CANDIDATE_ID not in candidate_index:
        raise ValueError("Existing Venetian nobility term candidate is missing")
    nobility = candidate_index[NOBILITY_CANDIDATE_ID]
    if nobility.get("suggested_type") != "term" or nobility.get("canonical_name") != "Venetian nobility as a social estate":
        raise ValueError("Existing candidate is not the expected Venetian nobility term")
    if MENTION_ID in {row["mention_id"] for row in mentions}:
        raise ValueError("Planned mention ID already exists")

    segment = next(
        json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Source segment hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    start = text.find(SURFACE_FORM)
    if start < 0 or text.find(SURFACE_FORM, start + 1) >= 0:
        raise ValueError("Source phrase missing or repeated")
    end = start + len(SURFACE_FORM)
    containing = next((row for row in mentions if row["mention_id"] == CONTAINING_MENTION_ID), None)
    if (
        containing is None
        or containing.get("segment_id") != SEGMENT_ID
        or containing.get("surface_form") != "bought their way into the nobility"
        or not (int(containing["start_char"]) <= start and end <= int(containing["end_char"]))
    ):
        raise ValueError("The expected family-level mention does not contain the specific nobility phrase")
    for old in mentions:
        if old["segment_id"] != SEGMENT_ID or old["mention_id"] == CONTAINING_MENTION_ID:
            continue
        old_start, old_end = int(old["start_char"]), int(old["end_char"])
        if start < old_end and old_start < end:
            raise ValueError(f"New mention unexpectedly overlaps {old['mention_id']}")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    index = {row["statement_id"]: pos for pos, row in enumerate(rows)}
    if STATEMENT_ID not in index:
        raise ValueError("Target statement is missing")
    row = rows[index[STATEMENT_ID]]
    qualifiers = row.get("qualifiers") or {}
    if (
        row.get("segment_id") != SEGMENT_ID
        or row.get("subject_candidate_id") != "cand-7575"
        or row.get("object_candidate_id") is not None
        or qualifiers.get("relation_candidate") is not True
        or NOBILITY_CANDIDATE_ID in (qualifiers.get("mentioned_candidate_ids") or [])
    ):
        raise ValueError("Target statement identity or open endpoint changed")
    before_open = sum(is_open_true(item) for item in rows)
    before_true = sum((item.get("qualifiers") or {}).get("relation_candidate") is True for item in rows)
    before_false = sum((item.get("qualifiers") or {}).get("relation_candidate") is False for item in rows)
    if (before_open, before_true, before_false) != (457, 10389, 4740):
        raise ValueError(f"Unexpected pre-update counts: {(before_open, before_true, before_false)}")

    row["object_candidate_id"] = NOBILITY_CANDIDATE_ID
    qualifiers["mentioned_candidate_ids"] = list(dict.fromkeys(
        (qualifiers.get("mentioned_candidate_ids") or []) + [NOBILITY_CANDIDATE_ID]
    ))
    qualifiers["qualification"] = "This is Haskell's characterization; no named family member, exact ennoblement date, or independent source is supplied. Keep this Venice family distinct from the Perugia Baglioni candidate cand-4279 pending S3 identity alignment."
    qualifiers["relation_candidate_note"] = "The object is the existing term candidate for the Venetian nobility as a social estate. Haskell's phrase 'bought their way' is retained as his characterization; no specific purchase transaction or exact date is inferred."
    qualifiers.pop("open_endpoint_reason", None)
    row["qualifiers"] = qualifiers
    row.pop("qualification", None)
    row.pop("mentioned_candidate_ids", None)

    new_mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": NOBILITY_CANDIDATE_ID,
        "surface_form": SURFACE_FORM,
        "start_char": str(start),
        "end_char": str(end),
        "note": "The social estate that the Venice Baglioni family is reported to have entered; Haskell's idiom is not treated as a specific purchase transaction.",
    }
    mention_after = append_csv(mention_raw, mention_fields, [new_mention])
    statement_after = ("".join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
        for item in rows
    )).encode("utf-8")
    after_rows = [json.loads(line) for line in statement_after.decode("utf-8").splitlines()]
    after_open = sum(is_open_true(item) for item in after_rows)
    after_true = sum((item.get("qualifiers") or {}).get("relation_candidate") is True for item in after_rows)
    segment_open = [
        item["statement_id"] for item in after_rows
        if item.get("segment_id") == SEGMENT_ID and is_open_true(item)
    ]
    if (after_open, after_true, segment_open) != (456, 10389, []):
        raise ValueError(f"Unexpected post-update state: {(after_open, after_true, segment_open)}")

    print(f"candidate_rows={len(candidates)}->{len(candidates)}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + 1}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    print(f"planned_mention={MENTION_ID}|{NOBILITY_CANDIDATE_ID}|[{start},{end}) {SURFACE_FORM}")
    print(f"planned_endpoint={STATEMENT_ID}|None->{NOBILITY_CANDIDATE_ID}")
    print(f"open_endpoints={before_open}->{after_open}; relation_candidate_true={after_true}")
    print(f"segment_open={segment_open}")
    print(f"{MENTIONS.relative_to(ROOT)} {digest(mention_raw)}->{digest(mention_after)}")
    print(f"{STATEMENTS.relative_to(ROOT)} {digest(statement_raw)}->{digest(statement_after)}")
    if args.preview:
        return 0

    paths = ((MENTIONS, mention_after), (STATEMENTS, statement_after))
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in paths:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temp, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    try:
        for _, _, temp, data in pairs:
            temp.write_bytes(data)
        for path, _, temp, _ in pairs:
            temp.replace(path)
    except Exception:
        for _, _, temp, _ in pairs:
            if temp.exists():
                temp.unlink()
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
