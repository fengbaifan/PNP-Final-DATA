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
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_iv.md"
SEGMENT_ID = "chp-6:06_CHP-6_sec_iv:l12-26"
SUFFIX = "bak-s2-ch6-p158-marucelli-open-groups-20261015"

TARGETS = [
    {
        "statement_id": "st-chp6-p158-marucelli-commissioned-writer-busts",
        "subject": "cand-1554",
        "candidate_id": "cand-12328",
        "mention_id": "m-chp6-p158-marucelli-writer-bust-group",
        "surface_form": "busts in stucco, wood, marble and paint of the great writers",
        "line": 15,
        "candidate": {
            "canonical_name": "Marucelli-commissioned busts of great writers in four media (p. 158)",
            "suggested_type": "work",
            "detail": "Haskell says Marucelli commissioned busts in stucco, wood, marble, and paint representing unnamed great writers. Treat this as a source-bounded work group; individual busts, sitters, makers, and count are not supplied.",
        },
        "note": "The source defines a group of busts by medium and generic sitters. Close the object with a source-bounded work-group candidate without inferring individual titles, makers, sitters, or count.",
    },
    {
        "statement_id": "st-chp6-p158-marucelli-friends-with-painters",
        "subject": "cand-1554",
        "candidate_id": "cand-12329",
        "mention_id": "m-chp6-p158-marucelli-painter-friends-group",
        "surface_form": "some of the principal painters, many of whom were his friends",
        "line": 13,
        "candidate": {
            "canonical_name": "Principal painters whose lives Marucelli wrote and who were his friends (unnamed group, p. 158)",
            "suggested_type": "term",
            "detail": "Haskell says Marucelli wrote the lives of some principal painters and that many of those painters were his friends. This source-bounded group preserves the stated overlap without supplying names or treating it as the complete set of painters whose lives he wrote.",
        },
        "note": "The object is the source-bounded subset of principal painters whose lives Marucelli wrote and who were his friends. Their names are not supplied in this passage.",
    },
    {
        "statement_id": "st-chp6-p158-writers-books-in-library",
        "subject": "cand-1555",
        "candidate_id": "cand-12330",
        "mention_id": "m-chp6-p158-marucelli-library-works-group",
        "surface_form": "works fdled his excellent library",
        "line": 15,
        "candidate": {
            "canonical_name": "Unidentified works by the great writers in Marucelli's library (p. 158)",
            "suggested_type": "work",
            "detail": "Haskell says works by unnamed great writers filled Marucelli's library. Individual authors, titles, editions, and count are not given. Keep this work group distinct from the busts of writers commissioned in the same sentence. The source OCR reads 'fdled'; the scan reads 'filled'.",
        },
        "note": "The source defines a group of works in Marucelli's library but supplies no authors, titles, or count. The OCR surface reads 'fdled'; the scan correction is 'filled'. Keep these works distinct from the commissioned busts.",
    },
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"), extrasaction="raise").writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidate_rows = read_csv(CANDIDATES)
    mention_raw, mention_fields, mention_rows = read_csv(MENTIONS)
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    next_id = max(int(re.fullmatch(r"cand-(\d+)", value).group(1)) for value in candidate_ids) + 1
    if next_id != 12328:
        raise ValueError(f"Candidate sequence changed: expected 12328, got {next_id}")

    segment = next(json.loads(line) for line in SEGMENTS.open(encoding="utf-8") if json.loads(line).get("segment_id") == SEGMENT_ID)
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    added_candidates: list[dict[str, str]] = []
    added_mentions: list[dict[str, str]] = []
    statement_raw = STATEMENTS.read_bytes()
    statement_lines = statement_raw.decode("utf-8").splitlines(keepends=True)
    statement_index = {json.loads(line)["statement_id"]: i for i, line in enumerate(statement_lines)}

    for target in TARGETS:
        cid = target["candidate_id"]
        mid = target["mention_id"]
        if cid in candidate_ids or mid in mention_ids:
            raise ValueError(f"Planned identifier already exists: {cid} / {mid}")
        phrase = target["surface_form"]
        start = text.find(phrase)
        if start < 0 or text.find(phrase, start + 1) >= 0:
            raise ValueError(f"Source phrase missing or repeated for {mid}")
        index = statement_index.get(target["statement_id"])
        if index is None:
            raise ValueError(f"Missing target statement {target['statement_id']}")
        row = json.loads(statement_lines[index])
        q = row.get("qualifiers") or {}
        if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != target["subject"]:
            raise ValueError(f"Target identity changed: {target['statement_id']}")
        if row.get("object_candidate_id") is not None or q.get("relation_candidate") is not True or not q.get("open_endpoint_reason"):
            raise ValueError(f"Target endpoint state changed: {target['statement_id']}")

        detail = target["candidate"]
        added_candidates.append({
            "candidate_id": cid, "index_entry_id": "",
            "canonical_name": detail["canonical_name"],
            "index_page_range": "", "suggested_type": detail["suggested_type"],
            "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": detail["detail"], "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{target['line']}",
        })
        added_mentions.append({
            "mention_id": mid, "segment_id": SEGMENT_ID,
            "candidate_id": cid, "surface_form": phrase,
            "start_char": str(start), "end_char": str(start + len(phrase)),
            "note": target["note"],
        })
        row["object_candidate_id"] = cid
        q["mentioned_candidate_ids"] = list(dict.fromkeys([*(q.get("mentioned_candidate_ids") or []), cid]))
        q["relation_candidate_note"] = target["note"]
        q.pop("open_endpoint_reason", None)
        row["qualifiers"] = q
        statement_lines[index] = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"

    candidate_after = append_csv(candidate_raw, candidate_fields, added_candidates)
    mention_after = append_csv(mention_raw, mention_fields, added_mentions)
    statement_after = "".join(statement_lines).encode("utf-8")
    paths = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    backups = {path: path.with_name(f"{path.name}.{SUFFIX}") for path in paths}
    before_open = sum(1 for line in statement_raw.decode("utf-8").splitlines() if (lambda x: (x.get("qualifiers") or {}).get("relation_candidate") is True and (not x.get("subject_candidate_id") or not x.get("object_candidate_id")))(json.loads(line)))
    after_open = sum(1 for line in statement_after.decode("utf-8").splitlines() if (lambda x: (x.get("qualifiers") or {}).get("relation_candidate") is True and (not x.get("subject_candidate_id") or not x.get("object_candidate_id")))(json.loads(line)))
    print(f"candidate_rows={len(candidate_rows)}->{len(candidate_rows) + len(added_candidates)}")
    print(f"mention_rows={len(mention_rows)}->{len(mention_rows) + len(added_mentions)}")
    print(f"statement_rows={len(statement_lines)} unchanged")
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
