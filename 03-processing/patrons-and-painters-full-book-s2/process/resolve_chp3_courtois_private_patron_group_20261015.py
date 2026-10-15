from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l26-33"
TARGET = "st-chp3-seciv-l26-33-private-patron-painting"
SUFFIX = "bak-s2-chp3-courtois-private-patron-group-20261015"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, fieldnames=fields, lineterminator=newline, extrasaction="raise").writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline.encode("ascii")
    return raw + stream.getvalue().encode("utf-8")


def open_count(raw: bytes) -> int:
    return sum(
        1 for line in raw.decode("utf-8").splitlines()
        if (lambda x: (x.get("qualifiers") or {}).get("relation_candidate") is True
        and (not x.get("subject_candidate_id") or not x.get("object_candidate_id")))(json.loads(line))
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidate_rows = read_csv(CANDIDATES)
    mention_raw, mention_fields, mention_rows = read_csv(MENTIONS)
    max_cid = max(int(re.fullmatch(r"cand-(\d+)", row["candidate_id"]).group(1)) for row in candidate_rows)
    segment_mentions = [row for row in mention_rows if row["segment_id"] == SEGMENT_ID]
    max_mid = max(int(m.group(1)) for row in segment_mentions if (m := re.fullmatch(r"m-chp3-seciv-l26-33-(\d+)", row["mention_id"])))
    if max_cid != 12318 or max_mid != 61:
        raise ValueError(f"Sequences changed: candidate={max_cid}, mention={max_mid}")
    if any(row["candidate_id"] == "cand-12319" for row in candidate_rows):
        raise ValueError("Planned candidate ID already exists")
    if any(row["mention_id"] == "m-chp3-seciv-l26-33-0062" for row in mention_rows):
        raise ValueError("Planned mention ID already exists")

    segment = next(json.loads(line) for line in SEGMENTS.open(encoding="utf-8") if json.loads(line).get("segment_id") == SEGMENT_ID)
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    phrase = "private patrons"
    start = text.find(phrase)
    if start < 0 or text.find(phrase, start + 1) >= 0:
        raise ValueError("Source phrase missing or repeated")

    candidate = {
        "candidate_id": "cand-12319", "index_entry_id": "",
        "canonical_name": "Unidentified private patrons for whom Courtois was encouraged to continue painting",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell identifies private patrons as the intended beneficiaries of Courtois's continued painting but names no individual or bounded membership. This passage does not identify the encourager or establish any specific completed commission.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L27",
    }
    mention = {
        "mention_id": "m-chp3-seciv-l26-33-0062", "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12319", "surface_form": phrase,
        "start_char": str(start), "end_char": str(start + len(phrase)),
        "note": "Source-defined but unnamed patron group; no membership or specific commission is supplied.",
    }

    statement_raw = STATEMENTS.read_bytes()
    statement_lines = statement_raw.decode("utf-8").splitlines(keepends=True)
    found = False
    for i, line in enumerate(statement_lines):
        row = json.loads(line)
        if row.get("statement_id") != TARGET:
            continue
        if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != "cand-0399" or row.get("object_candidate_id") is not None:
            raise ValueError("Target statement state changed")
        q = row.setdefault("qualifiers", {})
        if q.get("relation_candidate") is not True:
            raise ValueError("Target is no longer a relation candidate")
        row["object_candidate_id"] = "cand-12319"
        q["claim"] = "Haskell says Courtois was encouraged to continue painting for unnamed private patrons and to hand his earnings to the Jesuit Society; the encourager and any specific commission are not identified."
        q["qualification"] = "The passage reports encouragement and an intended patron group, not a named commission or confirmation that a particular work was completed for them."
        q["relation_candidate_note"] = "The source explicitly names 'private patrons' as the intended beneficiaries of Courtois's continued painting. Map the unnamed group as an open candidate; do not infer the encourager or individual commissions."
        q.pop("open_endpoint_reason", None)
        statement_lines[i] = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        found = True
        break
    if not found:
        raise ValueError(f"Missing target statement {TARGET}")

    candidate_after = append_csv(candidate_raw, candidate_fields, [candidate])
    mention_after = append_csv(mention_raw, mention_fields, [mention])
    statement_after = "".join(statement_lines).encode("utf-8")
    paths = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    backups = {path: path.with_name(f"{path.name}.{SUFFIX}") for path in paths}
    print(f"candidate_rows={len(candidate_rows)}->{len(candidate_rows)+1}")
    print(f"mention_rows={len(mention_rows)}->{len(mention_rows)+1}")
    print(f"statement_rows={len(statement_lines)} unchanged")
    print(f"open_endpoints={open_count(statement_raw)}->{open_count(statement_after)}")
    for path, after in paths.items():
        print(f"{path.relative_to(ROOT)} {digest(path.read_bytes())}->{digest(after)}")
    if args.preview:
        return 0
    if any(path.exists() for path in backups.values()):
        raise FileExistsError("A recovery copy already exists; refusing to overwrite it")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    temps: dict[Path, Path] = {}
    try:
        for path, data in paths.items():
            temp = path.with_name(f"{path.name}.tmp-{SUFFIX}")
            if temp.exists():
                raise FileExistsError(f"Temporary file already exists: {temp}")
            temp.write_bytes(data)
            temps[path] = temp
        for path, temp in temps.items():
            temp.replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        raise
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
