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
SEGMENT_ID = "chp-5:05_CHP-5_sec_iv:l33-37"
SUFFIX = "bak-s2-chp5-p145-open-group-endpoints-20261015"

TARGETS = [
    {
        "statement_id": "st-chp5-p145-giordano-three-brushes-audience-metaphor",
        "subject": "cand-1172",
        "candidate_id": "cand-12324",
        "mention_id": "m-chp5-p145-giordano-audience-classes",
        "surface_form": "he used three brushes—one of gold to satisfy the nobility, one of silver for private citizens, and one of copper for the populace",
        "line": 37,
        "candidate": {
            "canonical_name": "Nobility, private citizens, and populace as the three audiences in De Dominici's Giordano account (p. 145)",
            "suggested_type": "term",
            "detail": "Haskell quotes De Dominici's account that Luca Giordano used three metaphorical brushes to satisfy the nobility, private citizens, and populace. This source-bounded term groups the three explicit audience classes; individual members are not identified. Haskell uses Giordano as an analogy for Rosa, so the quoted practice is not assigned to Rosa.",
            "line": 37,
        },
        "note": "The quotation names three audience classes together. Represent them as a source-bounded term; the quoted practice concerns Giordano in De Dominici's account as relayed by Haskell, not Rosa.",
    },
    {
        "statement_id": "st-chp5-p145-passeri-pictures-found-in-homes-of-different-status",
        "subject": "cand-11951",
        "candidate_id": "cand-12325",
        "mention_id": "m-chp5-p145-passeri-houses-social-status",
        "surface_form": "many houses belonging to gentlemen and princes but also in those owned by “persone di mediocre stato”",
        "line": 36,
        "candidate": {
            "canonical_name": "Unidentified houses in which Rosa's pictures were said to be seen (p. 145)",
            "suggested_type": "place",
            "detail": "Passeri, as quoted by Haskell, says Rosa's pictures could be seen in many houses owned by gentlemen and princes and in houses owned by people of mediocre status. The passage defines a source-bounded group of residences but gives no individual names or addresses.",
            "line": 36,
        },
        "note": "Passeri's quoted sentence defines the residence group by where Rosa's pictures could be seen and by the owners' social categories. Record a source-bounded place group without inferring addresses or owners.",
    },
    {
        "statement_id": "st-chp5-p145-rosa-launched-onslaught-to-impose-serious-artist-image",
        "subject": "cand-2236",
        "candidate_id": "cand-12326",
        "mention_id": "m-chp5-p145-rosa-conventional-patronage",
        "surface_form": "the onslaught on conventional patronage",
        "line": 36,
        "candidate": {
            "canonical_name": "Conventional patronage criticized by Salvator Rosa (p. 145)",
            "suggested_type": "term",
            "detail": "Haskell describes Rosa's attack on conventional patronage as a practice or system. The term records the source's abstract object of criticism; it does not identify a patron, institution, or specific commission.",
            "line": 36,
        },
        "note": "Conventional patronage is the abstract practice named in the source. Map the object to a term candidate without inferring a particular patron or institution.",
    },
    {
        "statement_id": "st-chp5-p145-rosa-looked-beyond-select-patronage-circles",
        "subject": "cand-2236",
        "candidate_id": "cand-12327",
        "mention_id": "m-chp5-p145-rosa-outer-patronage-circles",
        "surface_form": "the outer circles of contemporary patronage",
        "line": 36,
        "candidate": {
            "canonical_name": "Outer circles of contemporary patronage in Haskell's account of Rosa (p. 145)",
            "suggested_type": "term",
            "detail": "Haskell's phrase for the peripheral social field within contemporary patronage that Rosa was forced to look beyond. Membership is unspecified; this source-defined term is not equated with the select clientele of fastidious tastes mentioned immediately before it.",
            "line": 36,
        },
        "note": "The source explicitly names the outer circles of contemporary patronage as the object Rosa looked beyond. Record that source-defined social field as a term; its members remain unidentified and it stays distinct from the select clientele clause.",
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
    if next_id != 12324:
        raise ValueError(f"Candidate sequence changed: expected 12324, got {next_id}")

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

        candidate_detail = target["candidate"]
        added_candidates.append({
            "candidate_id": cid, "index_entry_id": "",
            "canonical_name": candidate_detail["canonical_name"],
            "index_page_range": "", "suggested_type": candidate_detail["suggested_type"],
            "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": candidate_detail["detail"], "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{candidate_detail['line']}",
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
