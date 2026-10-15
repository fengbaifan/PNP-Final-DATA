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
SOURCE = ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"

SOURCE_SHA256 = "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3"
SEGMENT_ID = "chp-7:07_CHP-7_sec_i:l293-389"
SEGMENT_SHA256 = "ad9ae34a8e0247ade77cf812cd0d5943582c3fd615590da5064cef79c38ae28b"
DESTROYED_ID = "st-chp7-p174-n2-monument-destroyed"
NONEXECUTED_ID = "st-chp7-p174-n2-statue-not-executed"
BODY_REFERENT_ID = "st-chp7-p174-i18"
CANDIDATE_ID = "cand-12413"
MENTION_ID = "m-chp7-p174-fn2-destruction-event"
PHRASE = "was destroyed in 1792"
EXPECTED_SPAN = (1970, 1991)

EXPECTED_INPUT_HASHES = {
    "statements": "afe33f1c47e0294f595f1b5f91a42ad9b31f0ba27d916576da4594029cb75890",
    "mentions": "59f53ef5947d89b19f89c9db48543a74df12462c1c570c735a7703fbac15b38c",
    "candidates": "9c6f9c45d247336ee0d3205d3e579e1f9b816e8d7c98d18b6dbceb6621c1bc60",
}

BACKUP_SUFFIX = ".bak-s2-chp7-p174-n2-event-claims-20261015"
TEMP_SUFFIX = ".tmp-s2-chp7-p174-n2-event-claims-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def decode_csv(raw: bytes) -> tuple[bool, list[str], list[dict[str, str]]]:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return has_bom, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], row: dict[str, str]) -> bytes:
    has_bom, current_fields, _ = decode_csv(raw)
    if fields != current_fields:
        raise ValueError("CSV schema changed.")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=fields, lineterminator=newline).writerow(row)
    text = raw.decode("utf-8-sig")
    if not text.endswith(("\n", "\r")):
        text += newline
    text += buffer.getvalue()
    return (("\ufeff" if has_bom else "") + text).encode("utf-8")


def statement_rows(raw: bytes) -> list[dict]:
    return [
        json.loads(line)
        for line in raw.decode("utf-8-sig").splitlines()
        if line.strip()
    ]


def is_open_relation(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def open_counts(rows: list[dict]) -> tuple[int, int]:
    opened = [row for row in rows if is_open_relation(row)]
    no_reason = sum(
        not (row.get("qualifiers") or {}).get("open_endpoint_reason")
        for row in opened
    )
    return len(opened), no_reason


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record the statue's destruction event and classify non-execution as a work claim."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("Chapter 7 source asset changed.")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[292:389])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("Reviewed p.174 footnote segment changed.")
    if segment_text.count(PHRASE) != 1:
        raise ValueError("Expected the destruction phrase exactly once.")
    start = segment_text.index(PHRASE)
    end = start + len(PHRASE)
    if (start, end) != EXPECTED_SPAN:
        raise ValueError(f"Source span changed: found [{start},{end}).")
    if "this was never executed" not in segment_text:
        raise ValueError("The reviewed non-execution clause is missing.")

    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment_matches = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment_matches) != 1 or (
        segment_matches[0].get("sha256") != SEGMENT_SHA256
        or segment_matches[0].get("asset_sha256") != SOURCE_SHA256
    ):
        raise ValueError("Segment manifest no longer matches the reviewed source.")

    statement_raw = STATEMENTS.read_bytes()
    mention_raw = MENTIONS.read_bytes()
    candidate_raw = CANDIDATES.read_bytes()
    input_hashes = {
        "statements": sha(statement_raw),
        "mentions": sha(mention_raw),
        "candidates": sha(candidate_raw),
    }
    if input_hashes != EXPECTED_INPUT_HASHES:
        raise ValueError(f"Protected table snapshot changed: {input_hashes}")

    statements = statement_rows(statement_raw)
    by_id = {row.get("statement_id"): row for row in statements}
    if len(by_id) != len(statements):
        raise ValueError("Duplicate statement IDs in input.")
    destruction = by_id.get(DESTROYED_ID)
    nonexecution = by_id.get(NONEXECUTED_ID)
    if not destruction or (
        destruction.get("segment_id") != SEGMENT_ID
        or destruction.get("subject_candidate_id") != "cand-6676"
        or destruction.get("object_candidate_id") is not None
        or destruction.get("predicate") != "destroyed_in_1792"
        or destruction.get("qualifiers", {}).get("source_line_start") != 310
        or destruction.get("qualifiers", {}).get("relation_candidate") is not True
        or destruction.get("qualifiers", {}).get("open_endpoint_reason")
    ):
        raise ValueError("The destruction statement changed from its reviewed precondition.")
    if not nonexecution or (
        nonexecution.get("segment_id") != SEGMENT_ID
        or nonexecution.get("subject_candidate_id") != "cand-7037"
        or nonexecution.get("object_candidate_id") is not None
        or nonexecution.get("predicate") != "commission_was_never_executed"
        or nonexecution.get("qualifiers", {}).get("source_line_start") != 310
        or nonexecution.get("qualifiers", {}).get("relation_candidate") is not True
        or nonexecution.get("qualifiers", {}).get("open_endpoint_reason")
    ):
        raise ValueError("The non-execution statement changed from its reviewed precondition.")
    if BODY_REFERENT_ID not in by_id:
        raise ValueError("The linked Henri IV body statement is missing.")
    if len(statements) != 15151 or open_counts(statements) != (370, 49):
        raise ValueError(f"Unexpected statement state: rows={len(statements)}, open={open_counts(statements)}.")

    mention_bom, mention_fields, mention_rows = decode_csv(mention_raw)
    candidate_bom, candidate_fields, candidate_rows = decode_csv(candidate_raw)
    if mention_bom != candidate_bom:
        raise ValueError("CSV BOM state differs.")
    if any(row.get("mention_id") == MENTION_ID for row in mention_rows):
        raise ValueError(f"{MENTION_ID} already exists.")
    if any(row.get("candidate_id") == CANDIDATE_ID for row in candidate_rows):
        raise ValueError(f"{CANDIDATE_ID} already exists.")
    if len(candidate_rows) != 12390 or len(mention_rows) != 26600:
        raise ValueError("Unexpected candidate or mention row counts.")

    event_candidate = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Destruction of the equestrian statue of Henri IV (1792; Haskell, p.174 n.2)",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell's note reports the statue's destruction in 1792. The person or agency "
            "responsible and the location of the destruction are not stated."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L310",
    }
    event_mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": PHRASE,
        "start_char": str(start),
        "end_char": str(end),
        "note": (
            "Explicit destruction event and date; the passive sentence names no agent "
            "or location."
        ),
    }

    updated_destruction = json.loads(json.dumps(destruction, ensure_ascii=False))
    updated_destruction["object_candidate_id"] = CANDIDATE_ID
    updated_destruction["original_quote"] = "The monument was destroyed in 1792."
    q = updated_destruction.setdefault("qualifiers", {})
    q["mentioned_candidate_ids"] = list(
        dict.fromkeys((q.get("mentioned_candidate_ids") or []) + [CANDIDATE_ID])
    )
    q["referent_statement_ids"] = [BODY_REFERENT_ID]
    q["referent_note"] = (
        "'The monument' refers to the Henri IV equestrian statue described in the linked "
        "body passage."
    )
    q["relation_candidate_note"] = (
        "Haskell's note reports the specific destruction of the previously discussed Henri IV "
        "statue. The event candidate records the occurrence and date; no agent or location is stated."
    )

    updated_nonexecution = json.loads(json.dumps(nonexecution, ensure_ascii=False))
    updated_nonexecution["original_quote"] = (
        "In 1559 Catherine de’ Medici had commissioned an equestrian statue of Henri ll "
        "from Michelangelo, but this was never executed."
    )
    nq = updated_nonexecution.setdefault("qualifiers", {})
    nq["relation_candidate"] = False
    nq["relation_candidate_note"] = (
        "The note states a negative realization status for the proposed statue. No execution "
        "event occurred, so preserve this as a claim about the work rather than an entity relation."
    )

    has_bom = statement_raw.startswith(b"\xef\xbb\xbf")
    lines = statement_raw.decode("utf-8-sig").splitlines(keepends=True)
    output_lines: list[str] = []
    replacements = {DESTROYED_ID: updated_destruction, NONEXECUTED_ID: updated_nonexecution}
    found: set[str] = set()
    for line in lines:
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        statement_id = row.get("statement_id")
        if statement_id in replacements:
            output_lines.append(
                json.dumps(replacements[statement_id], ensure_ascii=False, separators=(",", ":")) + ending
            )
            found.add(statement_id)
        else:
            output_lines.append(line)
    if found != set(replacements):
        raise ValueError(f"Unexpected replacement set: {found}")
    statement_output = (("\ufeff" if has_bom else "") + "".join(output_lines)).encode("utf-8")
    mention_output = append_csv(mention_raw, mention_fields, event_mention)
    candidate_output = append_csv(candidate_raw, candidate_fields, event_candidate)

    after_statements = statement_rows(statement_output)
    after_mentions = decode_csv(mention_output)[2]
    after_candidates = decode_csv(candidate_output)[2]
    if open_counts(after_statements) != (368, 47):
        raise ValueError(f"Unexpected post-edit open state: {open_counts(after_statements)}.")
    if (
        len(after_statements) != len(statements)
        or len(after_mentions) != len(mention_rows) + 1
        or len(after_candidates) != len(candidate_rows) + 1
    ):
        raise ValueError("Unexpected post-edit row counts.")

    outputs = {
        STATEMENTS: statement_output,
        MENTIONS: mention_output,
        CANDIDATES: candidate_output,
    }
    print("reviewed=p.174 n.2: work destruction event plus non-execution status claim")
    print("change=one event candidate and exact mention; event linked to Henri IV statue")
    print("change=non-execution kept as a work claim; no non-event entity created")
    print("open_endpoints=370->368; no_reason_open=49->47")
    for path, data in outputs.items():
        print(f"{path.name} sha256 {sha(path.read_bytes())}->{sha(data)}")

    if args.preview:
        return 0

    expected = {
        "statements": args.expected_statements_sha256,
        "mentions": args.expected_mentions_sha256,
        "candidates": args.expected_candidates_sha256,
    }
    if expected != input_hashes:
        raise ValueError("Apply requires the three input hashes printed by this preview.")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    temps = {path: path.with_name(path.name + TEMP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise FileExistsError("A recovery copy already exists; refusing to overwrite it.")
    if any(path.exists() for path in temps.values()):
        raise FileExistsError("A temporary file already exists; refusing to overwrite it.")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, data in outputs.items():
            temps[path].write_bytes(data)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in backups.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise

    print("applied=yes")
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.name}:{sha(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
