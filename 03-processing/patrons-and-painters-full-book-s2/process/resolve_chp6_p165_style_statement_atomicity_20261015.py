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
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_v.md"
SEGMENT_ID = "chp-6:06_CHP-6_sec_v:l35-40"
SUFFIX = "bak-s2-ch6-p165-style-statement-atomicity-20261015"

CANDIDATES_TO_ADD = [
    {
        "candidate_id": "cand-12331",
        "canonical_name": "True Baroque as a stylistic comparator in Haskell's account of Ottoboni's style (p. 165)",
        "suggested_type": "term",
        "detail": "Haskell contrasts the vigour of the true Baroque with the style attributed to Ottoboni's influence. Keep this comparator distinct from the broader Baroque cultural category used elsewhere.",
        "line": 37,
    },
    {
        "candidate_id": "cand-12332",
        "canonical_name": "Later eighteenth-century painting as a stylistic comparator in Haskell's p. 165 account",
        "suggested_type": "term",
        "detail": "Haskell contrasts the severity of later eighteenth-century painting with the style attributed to Ottoboni's influence. This is an artistic-period category, not a claim about individual paintings; S0 OCR joins the line-break hyphen.",
        "line": 38,
    },
    {
        "candidate_id": "cand-12333",
        "canonical_name": "Master-pupil and court-to-court channels of style transmission in Haskell's p. 165 account",
        "suggested_type": "term",
        "detail": "Haskell generalizes that the style passed from master to pupil and from court to court. The term records these source-named channels without identifying individual teachers, pupils, courts, or transmission events.",
        "line": 37,
    },
    {
        "candidate_id": "cand-12334",
        "canonical_name": "Princes and general public as audiences for Ottoboni-associated style (p. 165)",
        "suggested_type": "term",
        "detail": "Haskell says the style was readily appreciated by princes and the general public. Individual members of either audience are not identified.",
        "line": 37,
    },
]

NEW_MENTIONS = [
    {
        "mention_id": "m-chp6-p165-style-later-painting-comparator",
        "candidate_id": "cand-12332",
        "surface_form": "later eighteenthcentury painting",
        "note": "Haskell's third stylistic comparator; S0 OCR joins 'eighteenth-century', while the scan prints a line-break hyphen.",
    },
    {
        "mention_id": "m-chp6-p165-style-master-pupil-court-transmission",
        "candidate_id": "cand-12333",
        "surface_form": "from master to pupil, from court to court",
        "note": "Generalized transmission channels named by Haskell; no individual teachers, pupils, or courts are identified.",
    },
    {
        "mention_id": "m-chp6-p165-style-prince-public-audience",
        "candidate_id": "cand-12334",
        "surface_form": "easily appreciated by princes and general public alike",
        "note": "Generalized audience classes named by Haskell; individual members are not identified.",
    },
]

NEW_STATEMENTS = [
    {
        "statement_id": "st-chp6-p165-v1-11-audience-reception",
        "subject_candidate_id": "cand-6554",
        "object_candidate_id": "cand-12334",
        "predicate": "appreciated_by_princes_and_general_public",
        "source_line_start": 37,
        "source_line_end": 37,
        "claim": "Haskell says the style was easily appreciated by princes and the general public.",
        "quote": "easily appreciated by princes and general public alike",
        "mention_ids": ["cand-6554", "cand-12334"],
        "qualification": "This is a broad authorial generalization; no individual audience members are specified.",
        "note": "The source names princes and the general public as audience classes. Preserve the generalized claim without inferring individuals.",
    },
    {
        "statement_id": "st-chp6-p165-v1-12-french-rococo",
        "subject_candidate_id": "cand-6554",
        "object_candidate_id": "cand-6555",
        "predicate": "lacked_intricate_fantasy_of_french_rococo",
        "source_line_start": 37,
        "source_line_end": 38,
        "claim": "Haskell says the style lacked the intricate fantasy of contemporary French rococo.",
        "quote": "the intricate fantasy of\nFrench rococo, with which it was contemporary",
        "mention_ids": ["cand-6554", "cand-6555"],
        "qualification": "This is Haskell's evaluative comparison of style categories, not a claim about a particular work.",
        "note": "Keep the French rococo comparison distinct from the other two style comparisons; the wording remains attributed to Haskell.",
    },
    {
        "statement_id": "st-chp6-p165-v1-12-later-painting",
        "subject_candidate_id": "cand-6554",
        "object_candidate_id": "cand-12332",
        "predicate": "lacked_severity_of_later_eighteenth_century_painting",
        "source_line_start": 38,
        "source_line_end": 38,
        "claim": "Haskell says the style lacked the severity of later eighteenth-century painting.",
        "quote": "the severity of later eighteenthcentury painting",
        "mention_ids": ["cand-6554", "cand-12332"],
        "qualification": "This is Haskell's evaluative comparison of style categories, not a claim about a particular work. S0 OCR joins the line-break hyphen.",
        "note": "Record the later-period painting category as named by Haskell; do not invent individual works.",
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


def rewrite_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return bom + stream.getvalue().encode("utf-8")


def relation_statement(item: dict[str, object]) -> dict[str, object]:
    return {
        "statement_id": item["statement_id"],
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": item["subject_candidate_id"],
        "object_candidate_id": item["object_candidate_id"],
        "predicate": item["predicate"],
        "qualifiers": {
            "speaker": "Haskell",
            "printed_page": "165",
            "source_line_start": item["source_line_start"],
            "source_line_end": item["source_line_end"],
            "claim": item["claim"],
            "text_layer": "authorial historical account",
            "qualification": item["qualification"],
            "mentioned_candidate_ids": item["mention_ids"],
            "relation_candidate": True,
            "relation_candidate_note": item["note"],
        },
        "original_quote": item["quote"],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
    }


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
    if next_id != 12331:
        raise ValueError(f"Candidate sequence changed: expected 12331, got {next_id}")
    if {item["candidate_id"] for item in CANDIDATES_TO_ADD} & candidate_ids:
        raise ValueError("A planned candidate ID already exists")
    if {item["mention_id"] for item in NEW_MENTIONS} & mention_ids:
        raise ValueError("A planned mention ID already exists")

    segment = next(json.loads(line) for line in SEGMENTS.open(encoding="utf-8") if json.loads(line).get("segment_id") == SEGMENT_ID)
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    added_mentions: list[dict[str, str]] = []
    for mention in NEW_MENTIONS:
        phrase = mention["surface_form"]
        start = text.find(phrase)
        if start < 0 or text.find(phrase, start + 1) >= 0:
            raise ValueError(f"Source phrase missing or repeated for {mention['mention_id']}")
        added_mentions.append({
            "mention_id": mention["mention_id"], "segment_id": SEGMENT_ID,
            "candidate_id": mention["candidate_id"], "surface_form": phrase,
            "start_char": str(start), "end_char": str(start + len(phrase)),
            "note": mention["note"],
        })

    statement_raw = STATEMENTS.read_bytes()
    statement_lines = statement_raw.decode("utf-8").splitlines(keepends=True)
    rows = [json.loads(line) for line in statement_lines]
    open_before = sum(1 for row in rows if (row.get("qualifiers") or {}).get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")))
    statement_index = {row["statement_id"]: i for i, row in enumerate(rows)}
    target_ids = {"st-chp6-p165-v1-11", "st-chp6-p165-v1-12"}
    if not target_ids <= statement_index.keys():
        raise ValueError("An existing target statement is missing")
    if any(item["statement_id"] in statement_index for item in NEW_STATEMENTS):
        raise ValueError("A planned statement ID already exists")

    for statement_id, object_id, predicate, claim, quote, statement_mentions, qualification, note in [
        (
            "st-chp6-p165-v1-11", "cand-12333",
            "transmitted_from_master_to_pupil_and_court_to_court",
            "Haskell says the style was easily transmitted from master to pupil and from court to court.",
            "easily transmitted from master to pupil, from court to court",
            ["cand-6554", "cand-12333"],
            "This is a broad authorial generalization; no individual teachers, pupils, or courts are specified.",
            "The source names master-to-pupil and court-to-court channels. Record this generalized transmission without inferring individuals or specific transmission events.",
        ),
        (
            "st-chp6-p165-v1-12", "cand-12331",
            "lacked_vigour_of_true_baroque",
            "Haskell says the style lacked the vigour of the true Baroque.",
            "It lacked the vigour of the true Baroque",
            ["cand-6554", "cand-12331"],
            "This is Haskell's evaluative comparison of style categories, not a claim about a particular work.",
            "Keep the true Baroque comparator distinct from the broader Baroque cultural category; the evaluation remains attributed to Haskell.",
        ),
    ]:
        idx = statement_index[statement_id]
        row = rows[idx]
        q = row.get("qualifiers") or {}
        if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != "cand-6554" or row.get("object_candidate_id") is not None or q.get("relation_candidate") is not True or not q.get("open_endpoint_reason"):
            raise ValueError(f"Target statement state changed: {statement_id}")
        row["object_candidate_id"] = object_id
        row["predicate"] = predicate
        q["claim"] = claim
        q["source_line_start"] = 37
        q["source_line_end"] = 37
        q["mentioned_candidate_ids"] = statement_mentions
        q["qualification"] = qualification
        q["relation_candidate_note"] = note
        q.pop("open_endpoint_reason", None)
        row["qualifiers"] = q
        row["original_quote"] = quote

    baroque_mention = next((m for m in mention_rows if m["mention_id"] == "m-chp6-p165-v-025"), None)
    if not baroque_mention or baroque_mention["candidate_id"] != "cand-4500" or baroque_mention["surface_form"] != "the true Baroque":
        raise ValueError("Existing Baroque mention state changed")
    baroque_mention["candidate_id"] = "cand-12331"
    baroque_mention["note"] = "Specific stylistic comparator; separate from the broader Baroque cultural-category candidate cand-4500."

    rococo_mention = next((m for m in mention_rows if m["mention_id"] == "m-chp6-p165-v-026"), None)
    if not rococo_mention or rococo_mention["candidate_id"] != "cand-6555" or rococo_mention["surface_form"] != "French rococo":
        raise ValueError("Existing French rococo mention state changed")

    new_rows = [relation_statement(item) for item in NEW_STATEMENTS]
    statement_after = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        for row in rows
    ) + "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in new_rows)
    candidates_after = [
        {
            "candidate_id": item["candidate_id"], "index_entry_id": "",
            "canonical_name": item["canonical_name"], "index_page_range": "",
            "suggested_type": item["suggested_type"], "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": item["detail"],
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{item['line']}",
        }
        for item in CANDIDATES_TO_ADD
    ]
    candidate_after = append_csv(candidate_raw, candidate_fields, candidates_after)
    mention_rows.extend(added_mentions)
    mention_after = rewrite_csv(mention_raw, mention_fields, mention_rows)
    paths = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after.encode("utf-8")}
    backups = {path: path.with_name(f"{path.name}.{SUFFIX}") for path in paths}
    after_open = sum(1 for line in paths[STATEMENTS].decode("utf-8").splitlines() if (lambda row: (row.get("qualifiers") or {}).get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")))(json.loads(line)))
    print(f"candidate_rows={len(candidate_rows)}->{len(candidate_rows) + len(candidates_after)}")
    print(f"mention_rows={len(mention_ids)}->{len(mention_ids) + len(added_mentions)} (one existing mention remapped)")
    print(f"statement_rows={len(rows)}->{len(rows) + len(new_rows)}")
    print(f"open_endpoints={open_before}->{after_open}")
    for path, data in paths.items():
        print(f"{path.relative_to(ROOT)} {digest(path.read_bytes())}->{digest(data)}")
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
