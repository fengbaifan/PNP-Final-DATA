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
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l11-19"
SEGMENT_SHA256 = "131cfa5f062c6baf0c97e31844b950a27f45817e5442687f1935a2e38b153a00"
SEGMENT_ASSET_SHA256 = "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6"
PDF_SHA256 = "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3"
LOCAL_ID = "st-chp8-p215-local-capacity-and-foreign-commission"
INFLUENCE_ID = "st-chp8-p215-one-collection-influential"
COMMISSION_ID = "st-chp8-p215-commission-requires-foreigner"
COMMISSION_CANDIDATE_ID = "cand-12416"
FOREIGNER_CANDIDATE_ID = "cand-12417"
COMMISSION_MENTION_ID = "m-chp8-p215-planned-commission"
FOREIGNER_MENTION_ID = "m-chp8-p215-unnamed-foreigner"
EXPECTED_HASHES = {
    "statements": "f437006da1420668d801984398f7636fdba9f60bf0d24d1e08e5647fdb3f27a5",
    "mentions": "4c3bfe1d788e7d17fd32846b088a2f46462ea51cd7236aef010a5d836379c39c",
    "candidates": "d52f63301fcd5d3a59482823465b57623ab177a6737aede1d64566da7f8af674",
}
BACKUP_SUFFIX = ".bak-s2-chp8-p215-open-claims-20261015"
TEMP_SUFFIX = ".tmp-s2-chp8-p215-open-claims-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def read_csv(raw: bytes) -> tuple[bool, list[str], list[dict[str, str]]]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return bom, list(reader.fieldnames or []), list(reader)


def patch_csv(raw: bytes, key: str, updates: dict[str, dict[str, str]], additions: list[dict[str, str]]) -> bytes:
    bom, fields, parsed = read_csv(raw)
    ids = [row.get(key, "") for row in parsed]
    if not fields or len(ids) != len(set(ids)) or not set(updates).issubset(ids):
        raise ValueError(f"Invalid {key} inventory or update target.")
    if any(set(row) != set(fields) for row in additions):
        raise ValueError(f"New {key} rows do not match current CSV schema.")
    if any(row[key] in set(ids) for row in additions):
        raise ValueError(f"New {key} id already exists.")
    text = raw.decode("utf-8-sig")
    physical = text.splitlines(keepends=True)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != fields or reader.line_num != 1:
        raise ValueError("CSV header changed or spans multiple physical lines.")
    output = [physical[0]]
    previous_line = reader.line_num
    seen: set[str] = set()
    for row in reader:
        end_line = reader.line_num
        original = "".join(physical[previous_line:end_line])
        if not original:
            raise ValueError("Unable to map CSV record to source lines.")
        row_id = row.get(key, "")
        if row_id in updates:
            row.update(updates[row_id])
            stream = io.StringIO(newline="")
            csv.DictWriter(stream, fieldnames=fields, lineterminator=newline).writerow(row)
            output.append(stream.getvalue())
            seen.add(row_id)
        else:
            output.append(original)
        previous_line = end_line
    if seen != set(updates):
        raise ValueError(f"Not all {key} updates were applied.")
    for row in additions:
        stream = io.StringIO(newline="")
        csv.DictWriter(stream, fieldnames=fields, lineterminator=newline).writerow(row)
        output.append(stream.getvalue())
    return (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")


def patch_jsonl(raw: bytes, updates: dict[str, dict], additions: list[dict]) -> bytes:
    bom = raw.startswith(b"\xef\xbb\xbf")
    output: list[str] = []
    seen: set[str] = set()
    all_ids: set[str] = set()
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    for line in lines:
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        row_id = row.get("statement_id")
        if row_id in all_ids:
            raise ValueError("Duplicate statement ID in source table.")
        all_ids.add(row_id)
        if row_id in updates:
            output.append(json.dumps(updates[row_id], ensure_ascii=False, separators=(",", ":")) + ending)
            seen.add(row_id)
        else:
            output.append(line)
    if seen != set(updates) or any(row["statement_id"] in all_ids for row in additions):
        raise ValueError("Statement update/addition IDs failed uniqueness checks.")
    output.extend(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in additions)
    return (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")


def counts(rows: list[dict]) -> tuple[int, int, int, int, int]:
    opened = []
    flags = {True: 0, False: 0, None: 0}
    for row in rows:
        q = row.get("qualifiers") or {}
        flag = q.get("relation_candidate")
        flags[flag] = flags.get(flag, 0) + 1
        if flag is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")):
            opened.append(row)
    no_reason = sum(not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in opened)
    return len(opened), no_reason, flags[True], flags[False], flags[None]


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the reviewed Chapter 8 p.215 open statements.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    pdf = ROOT / "02-sources/01-book/CHP-8.pdf"
    if sha(pdf.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-8.pdf changed.")
    segment_rows = jsonl(SEGMENTS.read_bytes())
    matches = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    if len(matches) != 1:
        raise ValueError("Reviewed p.215 source segment is missing or duplicated.")
    segment = matches[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SEGMENT_ASSET_SHA256:
        raise ValueError("Reviewed p.215 segment metadata changed.")
    source_path = ROOT / segment["source_file"]
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    source_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(source_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("Reviewed p.215 source transcription changed.")
    phrases = [
        "It was clear that there were no longer any Bergamasque artists of the calibre required",
        "the commission would have to be given to a foreigner",
        "the commission",
        "a foreigner",
        "but in at least one case they were highly influential",
    ]
    if any(source_text.count(phrase) != 1 for phrase in phrases):
        raise ValueError("A reviewed p.215 phrase changed or became ambiguous.")

    raw = {"statements": STATEMENTS.read_bytes(), "mentions": MENTIONS.read_bytes(), "candidates": CANDIDATES.read_bytes()}
    actual = {name: sha(value) for name, value in raw.items()}
    if actual != EXPECTED_HASHES:
        raise ValueError(f"Protected table snapshot changed: {actual}")
    statements = jsonl(raw["statements"])
    by_id = {row["statement_id"]: row for row in statements}
    if len(statements) != 15157 or len(by_id) != len(statements) or counts(statements) != (363, 41, 10401, 4756, 0):
        raise ValueError(f"Unexpected statement inventory/state: rows={len(statements)}, counts={counts(statements)}")
    local = by_id.get(LOCAL_ID)
    influence = by_id.get(INFLUENCE_ID)
    if not local or not influence:
        raise ValueError("One of the two reviewed statements is missing.")
    for row in (local, influence):
        q = row.get("qualifiers") or {}
        if row.get("segment_id") != SEGMENT_ID or q.get("relation_candidate") is not True or q.get("open_endpoint_reason"):
            raise ValueError(f"Reviewed open statement precondition changed: {row['statement_id']}")
    if local.get("subject_candidate_id") or local.get("object_candidate_id"):
        raise ValueError("The p.215 commission statement endpoints changed.")
    if influence.get("subject_candidate_id") or influence.get("object_candidate_id"):
        raise ValueError("The p.215 influence statement endpoints changed.")

    _, mention_fields, mention_rows = read_csv(raw["mentions"])
    _, candidate_fields, candidate_rows = read_csv(raw["candidates"])
    mention_ids = {row["mention_id"] for row in mention_rows}
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    if {COMMISSION_MENTION_ID, FOREIGNER_MENTION_ID} & mention_ids:
        raise ValueError("A planned p.215 mention ID already exists.")
    if {COMMISSION_CANDIDATE_ID, FOREIGNER_CANDIDATE_ID} & candidate_ids:
        raise ValueError("A planned p.215 candidate ID already exists.")

    capacity = json.loads(json.dumps(local, ensure_ascii=False))
    capacity["original_quote"] = phrases[0]
    capacity_q = capacity["qualifiers"]
    capacity_q["claim"] = "Haskell states that no Bergamasque artists of the required calibre remained for this task."
    capacity_q["qualification"] = "Haskell's assessment of local capacity for the 1653 Santa Maria Maggiore painting programme, not a verified judgment of every local artist."
    capacity_q["relation_candidate"] = False
    capacity_q["relation_candidate_note"] = "This is an attributed assessment of local artistic capacity, not an explicit relation between two entities."
    capacity_q["mentioned_candidate_ids"] = ["cand-6208", "cand-7641"]
    capacity_q.pop("open_endpoint_reason", None)

    influence_row = json.loads(json.dumps(influence, ensure_ascii=False))
    influence_row["subject_candidate_id"] = "cand-12352"
    influence_q = influence_row["qualifiers"]
    influence_q["claim"] = "Haskell says at least one collection in the discussed group was highly influential."
    influence_q["qualification"] = "At least one; neither the individual collection nor a specific object or domain of influence is identified in this sentence."
    influence_q["relation_candidate"] = False
    influence_q["relation_candidate_note"] = "The source gives an evaluative description but does not identify what the collection influenced; retain it as a claim without inventing a relation target."
    influence_q["mentioned_candidate_ids"] = ["cand-12352"]
    influence_q.pop("open_endpoint_reason", None)

    start_commission = source_text.index("the commission")
    start_foreigner = source_text.index("a foreigner")
    commission_candidate = {
        "candidate_id": COMMISSION_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Anticipated foreign-artist commission under Santa Maria Maggiore's 1653 decoration programme (Haskell, p.215)",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says the painting commission would have to go to a foreigner. The intended work and whether this prospective commission maps to any later named award are not specified; keep distinct from the broader decoration programme and later recorded commissions.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L19",
    }
    foreigner_candidate = {
        "candidate_id": FOREIGNER_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Unidentified foreign painter contemplated for the Santa Maria Maggiore commission (p.215)",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The singular role is explicit in Haskell's account of the painting commission, but the individual's identity, place of origin, and actual receipt of a commission are not stated.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L19",
    }
    commission_mention = {
        "mention_id": COMMISSION_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": COMMISSION_CANDIDATE_ID,
        "surface_form": "the commission",
        "start_char": str(start_commission),
        "end_char": str(start_commission + len("the commission")),
        "note": "The singular prospective painting commission, distinct from the wider decoration programme.",
    }
    foreigner_mention = {
        "mention_id": FOREIGNER_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": FOREIGNER_CANDIDATE_ID,
        "surface_form": "a foreigner",
        "start_char": str(start_foreigner),
        "end_char": str(start_foreigner + len("a foreigner")),
        "note": "Anonymous singular artist role contemplated for the painting commission; no person is identified.",
    }
    commission_statement = json.loads(json.dumps(local, ensure_ascii=False))
    commission_statement.update({
        "statement_id": COMMISSION_ID,
        "subject_candidate_id": COMMISSION_CANDIDATE_ID,
        "object_candidate_id": FOREIGNER_CANDIDATE_ID,
        "predicate": "painting_commission_expected_to_be_awarded_to_foreign_artist",
        "original_quote": phrases[1],
    })
    commission_q = commission_statement["qualifiers"]
    commission_q["claim"] = "Haskell says the painting commission would have to be given to a foreigner."
    commission_q["qualification"] = "This is a modal projection in Haskell's account, not proof that this singular commission was actually awarded; no later named artist is identified here as its recipient."
    commission_q["relation_candidate"] = True
    commission_q["relation_candidate_note"] = "The sentence names a singular commission and an anonymous foreign recipient role, while leaving the identity and actual award unresolved."
    commission_q["mentioned_candidate_ids"] = [COMMISSION_CANDIDATE_ID, FOREIGNER_CANDIDATE_ID, "cand-7639", "cand-7641"]
    commission_q.pop("open_endpoint_reason", None)

    statement_output = patch_jsonl(raw["statements"], {
        LOCAL_ID: capacity,
        INFLUENCE_ID: influence_row,
    }, [commission_statement])
    mention_output = patch_csv(raw["mentions"], "mention_id", {}, [commission_mention, foreigner_mention])
    candidate_output = patch_csv(raw["candidates"], "candidate_id", {}, [commission_candidate, foreigner_candidate])
    after_statements = jsonl(statement_output)
    _, _, after_mentions = read_csv(mention_output)
    _, _, after_candidates = read_csv(candidate_output)
    if len(after_statements) != 15158 or counts(after_statements) != (361, 39, 10400, 4758, 0):
        raise ValueError(f"Unexpected post-edit statement inventory/state: {counts(after_statements)}")
    if len(after_mentions) != 26607 or len(after_candidates) != 12395:
        raise ValueError("Unexpected post-edit mention or candidate inventory.")
    for mention in [commission_mention, foreigner_mention]:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise ValueError(f"Mention span does not match source: {mention['mention_id']}")

    outputs = {STATEMENTS: statement_output, MENTIONS: mention_output, CANDIDATES: candidate_output}
    print("reviewed=CHP-8 printed p.215 / PDF physical page 13, source lines 11-19")
    print("change=separate source assessment from prospective commission; retain collection influence as non-relational attributed claim")
    print("new_candidates=2 (prospective commission event; unidentified foreign painter); new_mentions=2; new_statements=1")
    print("open_endpoints=363->361; no_reason_open=41->39")
    for path, data in outputs.items():
        print(f"{path.name} sha256 {sha(path.read_bytes())}->{sha(data)}")
    if args.preview:
        return 0
    requested = {
        "statements": args.expected_statements_sha256,
        "mentions": args.expected_mentions_sha256,
        "candidates": args.expected_candidates_sha256,
    }
    if requested != actual:
        raise ValueError("Apply requires the three input hashes printed by this preview.")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    temps = {path: path.with_name(path.name + TEMP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()) or any(path.exists() for path in temps.values()):
        raise FileExistsError("A recovery copy or temporary table already exists; refusing to overwrite it.")
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
