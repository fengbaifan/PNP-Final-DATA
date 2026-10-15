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
SEGMENT_ID = "chp-7:07_CHP-7_sec_i:l21-29"
SEGMENT_SHA256 = "fd941cd7830cc92c1a9b548342d32bb71fd24d036072b6b22986b4c12bb7c201"
STATEMENT_ID = "st-chp7-p171-i09"
REFERENT_STATEMENT_ID = "st-chp7-p171-i08"
CANDIDATE_ID = "cand-12412"
MENTION_ID = "m-chp7-p171-b-059"
PHRASE = "the subjects whom he later ruled"
EXPECTED_SPAN = (1047, 1079)

EXPECTED_INPUT_HASHES = {
    "statements": "78c0943074cb5df49fb364e60674ed522f5e3bf9cf9e73eca5b922c146830a2a",
    "mentions": "7b97632beda7b843fa22142e3f9b486421f6de52710313abeb6c528b247f991c",
    "candidates": "39ad1c0cce7d9c844356c6d6395ffee902e9d935aaf5c591c5e3ecb9a0c2f78d",
}

BACKUP_SUFFIX = ".bak-s2-chp7-p171-unnamed-subjects-20261015"


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
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def open_counts(rows: list[dict]) -> tuple[int, int]:
    opened = [row for row in rows if is_open_relation(row)]
    no_reason = sum(
        not (row.get("qualifiers") or {}).get("open_endpoint_reason")
        for row in opened
    )
    return len(opened), no_reason


def replace_statement(raw: bytes, updated: dict) -> bytes:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    matches = 0
    output: list[str] = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        if row.get("statement_id") == STATEMENT_ID:
            output.append(json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + ending)
            matches += 1
        else:
            output.append(line)
    if matches != 1:
        raise ValueError(f"Expected one target statement line; found {matches}.")
    return (("\ufeff" if has_bom else "") + "".join(output)).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register the unnamed comparison group in the p.171 taste statement."
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
    segment_text = "\n".join(SOURCE.read_text(encoding="utf-8").splitlines()[20:29])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("Reviewed p.171 source segment changed.")
    if segment_text.count(PHRASE) != 1:
        raise ValueError("Expected the exact comparison-group phrase once.")
    start = segment_text.index(PHRASE)
    end = start + len(PHRASE)
    if (start, end) != EXPECTED_SPAN:
        raise ValueError(f"Source span changed: found [{start},{end}).")
    if "this sometimes led" not in segment_text:
        raise ValueError("The reviewed antecedent phrase is missing.")

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
    target = by_id.get(STATEMENT_ID)
    if not target:
        raise ValueError(f"Missing {STATEMENT_ID}.")
    if (
        target.get("segment_id") != SEGMENT_ID
        or target.get("subject_candidate_id") != "cand-6624"
        or target.get("object_candidate_id") is not None
        or target.get("predicate") != "former_ambassadorship_sometimes_shaped_viceroy_taste"
        or target.get("qualifiers", {}).get("source_line_start") != 25
        or target.get("qualifiers", {}).get("source_line_end") != 25
        or target.get("qualifiers", {}).get("relation_candidate") is not True
        or PHRASE not in target.get("original_quote", "")
        or (target.get("qualifiers") or {}).get("open_endpoint_reason")
    ):
        raise ValueError("The p.171 statement changed from its reviewed precondition.")
    if REFERENT_STATEMENT_ID not in by_id or (
        by_id[REFERENT_STATEMENT_ID].get("segment_id") != SEGMENT_ID
        or by_id[REFERENT_STATEMENT_ID].get("predicate")
        != "former_rome_ambassadors_frequently_appointed_as_viceroys"
    ):
        raise ValueError("The immediate antecedent statement changed.")
    if open_counts(statements) != (372, 51):
        raise ValueError(f"Unexpected open-endpoint state: {open_counts(statements)}.")

    mention_bom, mention_fields, mention_rows = decode_csv(mention_raw)
    candidate_bom, candidate_fields, candidate_rows = decode_csv(candidate_raw)
    if mention_bom != candidate_bom:
        raise ValueError("CSV BOM state differs.")
    if any(row.get("mention_id") == MENTION_ID for row in mention_rows):
        raise ValueError(f"{MENTION_ID} already exists.")
    if any(row.get("candidate_id") == CANDIDATE_ID for row in candidate_rows):
        raise ValueError(f"{CANDIDATE_ID} already exists.")
    if len(candidate_rows) != 12389 or len(mention_rows) != 26599 or len(statements) != 15151:
        raise ValueError("Unexpected table row counts.")

    candidate = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "The subjects whom the viceroy ruled (unnamed group; p.171)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "The source identifies only an unnamed collective as the viceroy's subjects. "
            "Membership, jurisdiction, and individual identities are unspecified."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L25",
    }
    mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": PHRASE,
        "start_char": str(start),
        "end_char": str(end),
        "note": (
            "Unnamed comparison group; 'he' refers generically to a viceroy, "
            "not to a named individual."
        ),
    }

    updated = json.loads(json.dumps(target, ensure_ascii=False))
    updated["object_candidate_id"] = CANDIDATE_ID
    qualifiers = updated.setdefault("qualifiers", {})
    qualifiers["qualification"] = (
        "'Sometimes' is retained; the comparison concerns unnamed subjects of a "
        "generic viceroy, without identifying their membership or jurisdiction."
    )
    qualifiers["mentioned_candidate_ids"] = list(
        dict.fromkeys((qualifiers.get("mentioned_candidate_ids") or []) + [CANDIDATE_ID])
    )
    qualifiers["referent_statement_ids"] = [REFERENT_STATEMENT_ID]
    qualifiers["referent_note"] = (
        "'This sometimes led' refers to the preceding frequent practice of appointing "
        "a former Rome ambassador as viceroy, not to Monterey's later example."
    )
    qualifiers["relation_candidate_note"] = (
        "This preserves Haskell's qualified causal claim that prior Rome ambassadorship "
        "sometimes shaped a viceroy's taste in relation to his unnamed subjects; neither "
        "the individual viceroy nor the subjects are identified."
    )
    qualifiers.pop("open_endpoint_reason", None)

    statement_output = replace_statement(statement_raw, updated)
    mention_output = append_csv(mention_raw, mention_fields, mention)
    candidate_output = append_csv(candidate_raw, candidate_fields, candidate)
    after_statements = statement_rows(statement_output)
    after_mentions = decode_csv(mention_output)[2]
    after_candidates = decode_csv(candidate_output)[2]
    if open_counts(after_statements) != (371, 50):
        raise ValueError(f"Unexpected post-edit open-endpoint state: {open_counts(after_statements)}.")
    if (
        len(after_statements) != len(statements)
        or len(after_mentions) != len(mention_rows) + 1
        or len(after_candidates) != len(candidate_rows) + 1
    ):
        raise ValueError("Unexpected post-edit row counts.")

    output_bytes = {
        STATEMENTS: statement_output,
        MENTIONS: mention_output,
        CANDIDATES: candidate_output,
    }
    print("reviewed=unnamed subjects comparison group; generic 'this' linked to prior appointment-practice statement")
    print("scope=one candidate, one exact mention, one statement endpoint and qualifier update")
    print("candidate_type=unassigned; no identity, membership, or jurisdiction inferred")
    print("open_endpoints=372->371; no_reason_open=51->50")
    for path, raw in output_bytes.items():
        label = path.name
        print(f"{label} sha256 {sha(path.read_bytes())}->{sha(raw)}")

    if args.preview:
        return 0

    expected = {
        "statements": args.expected_statements_sha256,
        "mentions": args.expected_mentions_sha256,
        "candidates": args.expected_candidates_sha256,
    }
    if expected != input_hashes:
        raise ValueError("Apply requires all three expected hashes printed by the current preview.")

    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in output_bytes}
    temps = {path: path.with_name(path.name + ".tmp-s2-chp7-p171-unnamed-subjects-20261015") for path in output_bytes}
    if any(path.exists() for path in backups.values()):
        raise FileExistsError("A recovery copy already exists; refusing to overwrite it.")
    if any(path.exists() for path in temps.values()):
        raise FileExistsError("A temporary table file already exists; refusing to overwrite it.")

    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, raw in output_bytes.items():
            temps[path].write_bytes(raw)
        for path in output_bytes:
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
