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
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SEGMENTS = TABLE_DIR / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_v.md"
SEGMENT_ID = "chp-6:06_CHP-6_sec_v:l28-33"
SOURCE_SHA256 = "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15"
SEGMENT_SHA256 = "dc896ba93ce0a9f27592da3144a4c13503e29fa2008f5ba51920a63921492e67"
EXPECTED_HASHES = {
    STATEMENTS: "3cc019e9179a57c2fc3bc9af224977437f6f9d5587bfea1d44965cb22c7600e3",
    CANDIDATES: "030826c120263f2c4074106728201968678b01063b3444fb72e9c1dc0e6c16f3",
    MENTIONS: "371e3de5207f666c02a464cce6182883ac8a85255ff5d70202d9648fcfb32b2a",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp6-p164-ottoboni-cardinalate-20261015"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp6-p164-ottoboni-cardinalate-20261015"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp6-p164-ottoboni-cardinalate-20261015"),
}

NEW_CANDIDATE = {
    "candidate_id": "cand-12411",
    "index_entry_id": "",
    "canonical_name": "Pietro Ottoboni's creation as cardinal (1689; Haskell, p.164)",
    "index_page_range": "",
    "suggested_type": "event",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": "Haskell states that Pietro Ottoboni was made cardinal in 1689 at age 22. The source does not identify the appointing pope in this sentence; do not infer the office-granting actor from adjacent context.",
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT_ID}#L29",
}
NEW_MENTION = {
    "mention_id": "m-chp6-p164-ottoboni-cardinalate-creation",
    "segment_id": SEGMENT_ID,
    "candidate_id": "cand-12411",
    "surface_form": "was made cardinal in 1689",
    "start_char": "122",
    "end_char": "147",
    "note": "Appointment event named by the source; no appointing actor is stated in this clause.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def csv_bytes(rows: list[dict], fields: list[str], has_bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig" if has_bom else "utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if digest(raw[path]) != expected:
            raise ValueError(f"protected table changed: {path.name} ({digest(raw[path])})")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("chapter 6 source asset changed")
    segment_rows = {
        row["segment_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLE_DIR / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    segment = segment_rows.get(SEGMENT_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise ValueError("reviewed p.164 segment changed")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(lines[27:33])
    quote = "Pietro who was made cardinal in 1689 was then aged 22."
    if digest(segment_text.encode("utf-8")) != SEGMENT_SHA256 or quote not in segment_text:
        raise ValueError("p.164 appointment statement no longer matches the source")
    if segment_text[122:147] != NEW_MENTION["surface_form"]:
        raise ValueError("appointment mention span changed")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    row = by_id.get("st-chp6-p164-v1-02")
    if not row or row.get("subject_candidate_id") != "cand-6536" or row.get("object_candidate_id"):
        raise ValueError("reviewed Ottoboni cardinalate statement changed")
    if (row.get("qualifiers") or {}).get("relation_candidate") is not True:
        raise ValueError("Ottoboni cardinalate statement is no longer a relation candidate")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        candidate_fields = reader.fieldnames
        candidates = list(reader)
    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        mention_fields = reader.fieldnames
        mentions = list(reader)
    if any(c["candidate_id"] == NEW_CANDIDATE["candidate_id"] for c in candidates):
        raise ValueError("candidate ID already exists")
    if any(m["mention_id"] == NEW_MENTION["mention_id"] for m in mentions):
        raise ValueError("mention ID already exists")

    open_before = sum(is_open(r) for r in statements)
    no_reason_before = sum(is_open(r) and not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in statements)
    true_count = sum((r.get("qualifiers") or {}).get("relation_candidate") is True for r in statements)
    false_count = sum((r.get("qualifiers") or {}).get("relation_candidate") is False for r in statements)
    if (open_before, no_reason_before, true_count, false_count, len(statements)) != (373, 52, 10397, 4754, 15151):
        raise ValueError("unexpected pre-edit S2 statement counts")

    row["object_candidate_id"] = "cand-12411"
    row["original_quote"] = quote
    q = row["qualifiers"]
    q["pdf_physical_page"] = 19
    q["mentioned_candidate_ids"] = list(dict.fromkeys(q.get("mentioned_candidate_ids", []) + ["cand-12411"]))
    q["qualification"] = "Haskell directly states the appointment year and age. No birth date or appointing actor is independently inferred from adjacent context."
    q["relation_candidate_note"] = "The person is linked to a source-defined appointment event; the sentence does not identify who made the appointment."
    q.pop("open_endpoint_reason", None)
    candidates.append(NEW_CANDIDATE)
    mentions.append(NEW_MENTION)

    outputs = {
        STATEMENTS: "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in statements).encode("utf-8"),
        CANDIDATES: csv_bytes(candidates, candidate_fields, raw[CANDIDATES].startswith(b"\xef\xbb\xbf")),
        MENTIONS: csv_bytes(mentions, mention_fields, raw[MENTIONS].startswith(b"\xef\xbb\xbf")),
    }
    open_after = sum(is_open(r) for r in statements)
    no_reason_after = sum(is_open(r) and not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in statements)
    if (open_after, no_reason_after) != (372, 51):
        raise ValueError(f"unexpected resulting open state: {open_after}, {no_reason_after}")

    print("reviewed=chapter 6 p.164; mapped Ottoboni's 1689 cardinalate appointment as a distinct event")
    print("changes=1 source-bounded event candidate, 1 exact mention, 1 relation-candidate object completed")
    print(f"open_endpoints={open_before}->{open_after}; open_without_reason={no_reason_before}->{no_reason_after}")
    for path, output in outputs.items():
        print(f"{path.name} sha256 {digest(raw[path])}->{digest(output)}")
    if args.preview:
        return 0

    for backup in BACKUPS.values():
        if backup.exists():
            raise FileExistsError(f"recovery copy already exists: {backup.name}")
    temps = {path: path.with_name(path.name + ".tmp-s2-chp6-p164-ottoboni-cardinalate-20261015") for path in outputs}
    if any(path.exists() for path in temps.values()):
        raise FileExistsError("protected temporary output already exists")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, output in outputs.items():
            temps[path].write_bytes(output)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in BACKUPS.items():
            shutil.copy2(backup, path)
        raise
    print("backups=" + ", ".join(path.name for path in BACKUPS.values()))
    print("applied_hashes=" + ", ".join(f"{path.name}:{digest(path.read_bytes())}" for path in outputs))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
