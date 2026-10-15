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
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_iv.md"
SEGMENT_ID = "chp-5:05_CHP-5_sec_iv:l23-31"
TARGET = "st-chp5-p144-de-rossi-obtained-smaller-rosa-pictures"
SUFFIX = "bak-s2-chp5-derossi-small-pictures-group-20261015"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidate_rows = read_csv(CANDIDATES)
    mention_raw, mention_fields, mention_rows = read_csv(MENTIONS)
    max_cid = max(int(re.fullmatch(r"cand-(\d+)", row["candidate_id"]).group(1)) for row in candidate_rows)
    if max_cid != 12322:
        raise ValueError(f"Candidate sequence changed: expected 12322, got {max_cid}")
    if any(row["candidate_id"] == "cand-12323" for row in candidate_rows):
        raise ValueError("Planned candidate ID already exists")
    mention_id = "m-chp5-p144-derossi-small-pictures"
    if any(row["mention_id"] == mention_id for row in mention_rows):
        raise ValueError("Planned mention ID already exists")

    segment = next(json.loads(line) for line in SEGMENTS.open(encoding="utf-8") if json.loads(line).get("segment_id") == SEGMENT_ID)
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    phrase = "quantities of the smaller pictures"
    start = text.find(phrase)
    if start < 0 or text.find(phrase, start + 1) >= 0:
        raise ValueError("Source phrase missing or repeated")

    candidate = {
        "candidate_id": "cand-12323", "index_entry_id": "",
        "canonical_name": "Unnamed smaller pictures by Salvator Rosa acquired by Carlo de' Rossi (p. 144)",
        "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says De' Rossi obtained quantities of Rosa's smaller pictures, including battles, sea pieces, landscapes, and weird scenes of witchcraft. Individual titles and count are not supplied. Keep distinct from De' Rossi's private-museum collection and the altarpieces Rosa painted for the family chapel.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L26",
    }
    mention = {
        "mention_id": mention_id, "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12323", "surface_form": phrase,
        "start_char": str(start), "end_char": str(start + len(phrase)),
        "note": "Source-bounded group of smaller pictures; the following genre list names types, not individual works.",
    }

    statement_raw = STATEMENTS.read_bytes()
    statement_lines = statement_raw.decode("utf-8").splitlines(keepends=True)
    found = False
    for i, line in enumerate(statement_lines):
        row = json.loads(line)
        if row.get("statement_id") != TARGET:
            continue
        if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != "cand-2269" or row.get("object_candidate_id") is not None:
            raise ValueError("Target statement state changed")
        q = row.setdefault("qualifiers", {})
        if q.get("relation_candidate") is not True:
            raise ValueError("Target is no longer a relation candidate")
        row["object_candidate_id"] = "cand-12323"
        q["claim"] = "Haskell says Carlo de' Rossi obtained an unnamed group of Salvator Rosa's smaller pictures, including battles, sea pieces, landscapes, and witchcraft scenes."
        q["qualification"] = "The group is explicit, but no individual titles or exact count are given; keep it distinct from the private-museum collection and chapel altarpieces."
        q["relation_candidate_note"] = "Use an open work-group candidate for the explicit 'quantities of the smaller pictures'; genre labels do not identify individual works."
        q["mentioned_candidate_ids"] = list(dict.fromkeys([*(q.get("mentioned_candidate_ids") or []), "cand-12323"]))
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
    before_open = sum(1 for line in statement_raw.decode("utf-8").splitlines() if (lambda x: (x.get("qualifiers") or {}).get("relation_candidate") is True and (not x.get("subject_candidate_id") or not x.get("object_candidate_id")))(json.loads(line)))
    after_open = sum(1 for line in statement_after.decode("utf-8").splitlines() if (lambda x: (x.get("qualifiers") or {}).get("relation_candidate") is True and (not x.get("subject_candidate_id") or not x.get("object_candidate_id")))(json.loads(line)))
    print(f"open_endpoints={before_open}->{after_open}")
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
