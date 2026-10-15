from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
MENTIONS = TABLE_DIR / "mentions.csv"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/15_CHP-15_sec_ii.md"

SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l61-67"
STATEMENT_ID = "st-chp15-p370-querini-swiss-friendships-open"
CANDIDATE_ID = "cand-11560"
MENTION_ID = "m-chp15-p370-alticchiero-0049"
SURFACE = "those formed in Switzerland"
CANONICAL_NAME = "Unnamed people in Querini's Swiss friendships commemorated by the garden altars"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def csv_parts(raw: bytes) -> tuple[str, bool, list[str], list[dict[str, str]]]:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return text, has_bom, list(reader.fieldnames or []), list(reader)


def append_csv_row(raw: bytes, values: dict[str, str]) -> bytes:
    text, has_bom, fields, _ = csv_parts(raw)
    if set(values) != set(fields):
        raise SystemExit(f"CSV fields changed; expected {fields}, got {list(values)}")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=fields, lineterminator=newline).writerow(values)
    if not text.endswith(("\n", "\r")):
        text += newline
    text += buffer.getvalue()
    return (("\ufeff" if has_bom else "") + text).encode("utf-8")


def validate_source() -> tuple[int, int, str]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if len(lines) < 67 or SURFACE not in lines[64]:
        raise SystemExit("The p.370 source line no longer contains the reviewed phrase.")
    segment_text = "\n".join(lines[60:67])
    starts = [i for i in range(len(segment_text)) if segment_text.startswith(SURFACE, i)]
    if starts != [2218]:
        raise SystemExit(f"Expected one exact source span at [2218,2245); found {starts}.")
    return starts[0], starts[0] + len(SURFACE), segment_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register the source-defined unnamed group in Querini's Swiss friendships at p.370."
    )
    parser.add_argument("--apply", action="store_true", help="Apply only with all three exact dry-run hashes.")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    start, end, segment_text = validate_source()
    statement_raw = STATEMENTS.read_bytes()
    mention_raw = MENTIONS.read_bytes()
    candidate_raw = CANDIDATES.read_bytes()

    statement_text = statement_raw.decode("utf-8-sig")
    statement_lines = statement_text.splitlines(keepends=True)
    statements = [json.loads(line) for line in statement_lines if line.strip()]
    matches = [row for row in statements if row.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected one target statement; found {len(matches)}.")
    statement = matches[0]
    if (
        statement.get("segment_id") != SEGMENT_ID
        or statement.get("subject_candidate_id") != "cand-2075"
        or statement.get("object_candidate_id") is not None
        or statement.get("qualifiers", {}).get("relation_candidate") is not True
        or not statement.get("original_quote")
        or normalize(statement["original_quote"]) not in normalize(segment_text)
    ):
        raise SystemExit("The target statement or source quote has changed; review before writing.")

    _, _, candidate_fields, candidate_rows = csv_parts(candidate_raw)
    candidate_ids = {row.get("candidate_id") for row in candidate_rows}
    highest = max(int(value.removeprefix("cand-")) for value in candidate_ids if value and value.startswith("cand-"))
    if CANDIDATE_ID in candidate_ids or highest != 11559:
        raise SystemExit(f"Candidate sequence changed; found highest={highest}, target_exists={CANDIDATE_ID in candidate_ids}.")

    _, _, mention_fields, mention_rows = csv_parts(mention_raw)
    mention_ids = {row.get("mention_id") for row in mention_rows}
    if MENTION_ID in mention_ids:
        raise SystemExit(f"Mention ID {MENTION_ID} already exists.")
    if any(row.get("segment_id") == SEGMENT_ID and row.get("surface_form") == SURFACE for row in mention_rows):
        raise SystemExit("The exact p.370 phrase already has a mention in this source segment.")

    candidate = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": CANONICAL_NAME,
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Source-defined collective represented by the friendships that the garden altars are said to commemorate, "
            "including those formed in Switzerland. The source supplies no names, count, or roster. Do not identify Voltaire, "
            "Festari, Girolamo Giustiniani, or Mme Rosenberg as members without an explicit link; the candidate remains untyped and open."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L65",
    }
    if list(candidate) != candidate_fields:
        raise SystemExit(f"Candidate CSV schema changed: {candidate_fields}")

    mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": SURFACE,
        "start_char": str(start),
        "end_char": str(end),
        "note": "Anaphoric phrase for the unnamed friendship group commemorated by other garden altars; do not map individual members from nearby travel or friendship statements.",
    }
    if list(mention) != mention_fields:
        raise SystemExit(f"Mention CSV schema changed: {mention_fields}")

    statement_new = json.loads(json.dumps(statement))
    statement_new["object_candidate_id"] = CANDIDATE_ID
    qualifiers = statement_new.setdefault("qualifiers", {})
    existing = qualifiers.get("mentioned_candidate_ids", [])
    qualifiers["mentioned_candidate_ids"] = list(dict.fromkeys([*existing, CANDIDATE_ID]))
    qualifiers["qualification"] = (
        "The phrase 'those formed in Switzerland' identifies a source-defined collective of unnamed people represented by "
        "friendships commemorated by other garden altars. No members, group size, or roster are given. Do not infer that "
        "Voltaire, Festari, Girolamo Giustiniani, or Mme Rosenberg belongs to this group; membership and type remain open."
    )
    qualifiers["relation_candidate_note"] = (
        "The object endpoint represents only the unnamed collective associated with the Swiss friendships; no individual member "
        "or connection to nearby named friends is established."
    )

    newline = "\r\n" if b"\r\n" in statement_raw else "\n"
    statement_after_lines = []
    replaced = 0
    for line in statement_lines:
        if not line.strip():
            statement_after_lines.append(line)
            continue
        row = json.loads(line)
        if row.get("statement_id") == STATEMENT_ID:
            statement_after_lines.append(json.dumps(statement_new, ensure_ascii=False, separators=(",", ":")) + newline)
            replaced += 1
        else:
            statement_after_lines.append(line)
    if replaced != 1:
        raise SystemExit(f"Expected to replace exactly one statement; replaced={replaced}.")

    candidate_after = append_csv_row(candidate_raw, candidate)
    mention_after = append_csv_row(mention_raw, mention)
    has_statement_bom = statement_raw.startswith(b"\xef\xbb\xbf")
    statement_after = ((b"\xef\xbb\xbf" if has_statement_bom else b"") + "".join(statement_after_lines).encode("utf-8"))

    print(f"source_span={SEGMENT_ID}#L65 [{start},{end}) surface={SURFACE!r}")
    print(f"candidate_add={CANDIDATE_ID}: {CANONICAL_NAME} [untyped, open]")
    print(f"mention_add={MENTION_ID}: {CANDIDATE_ID} [{start},{end})")
    print(f"statement_update={STATEMENT_ID}: object null -> {CANDIDATE_ID}")
    print("expected_counts_after_apply: candidates +1; mentions +1; statements unchanged; relation candidates unchanged; complete endpoints +1; open endpoints -1")
    print(f"statements_sha256={sha256(statement_raw)}")
    print(f"mentions_sha256={sha256(mention_raw)}")
    print(f"candidates_sha256={sha256(candidate_raw)}")
    if not args.apply:
        print("DRY-RUN: no files changed.")
        return

    expected = (args.expected_statements_sha256, args.expected_mentions_sha256, args.expected_candidates_sha256)
    actual = (sha256(statement_raw), sha256(mention_raw), sha256(candidate_raw))
    if None in expected or expected != actual:
        raise SystemExit("--apply requires all three hashes from this exact dry run.")

    changes = [
        (STATEMENTS, statement_raw, statement_after, "book-statements.jsonl.bak-s2-handoff-chp15-p370-swiss-friends-20261009"),
        (MENTIONS, mention_raw, mention_after, "mentions.csv.bak-s2-handoff-chp15-p370-swiss-friends-20261009"),
        (CANDIDATES, candidate_raw, candidate_after, "entity-candidates.csv.bak-s2-handoff-chp15-p370-swiss-friends-20261009"),
    ]
    backups = []
    temps = []
    for path, old, new, backup_name in changes:
        backup = path.with_name(backup_name)
        temp = path.with_name(path.name + ".tmp-s2-handoff-chp15-p370")
        if backup.exists():
            raise SystemExit(f"Refusing to overwrite recovery copy: {backup}")
        if temp.exists():
            raise SystemExit(f"Refusing to overwrite temporary file: {temp}")
        backups.append((path, old, backup))
    try:
        for path, old, backup in backups:
            shutil.copy2(path, backup)
        for path, _, new, _ in changes:
            temp = path.with_name(path.name + ".tmp-s2-handoff-chp15-p370")
            temp.write_bytes(new)
            temps.append((temp, path))
        for temp, path in temps:
            os.replace(temp, path)
    except Exception:
        for temp, path in temps:
            if temp.exists():
                temp.unlink()
            original = next((old for target, old, _ in backups if target == path), None)
            if original is not None and path.exists() and path.read_bytes() != original:
                path.write_bytes(original)
        raise

    print("APPLIED: candidate, mention, and relation endpoint written to the three S2 tables.")
    for path, old, backup in backups:
        print(f"recovery_copy={backup} sha256={sha256(backup.read_bytes())}")
        print(f"new_file={path} sha256={sha256(path.read_bytes())}")


if __name__ == "__main__":
    main()
