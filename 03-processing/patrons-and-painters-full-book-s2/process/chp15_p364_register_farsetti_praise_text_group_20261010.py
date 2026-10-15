from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
SOURCE = ROOT / "02-sources/02-Markdown/15_CHP-15_sec_i.md"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENT_ID = "chp-15:15_CHP-15_sec_i:l38-41"
STATEMENT_ID = "st-chp15-p364-farsetti-held-up-as-example"
CANDIDATE_ID = "cand-11565"
MENTION_ID = "m-chp15-p364-poems-speeches-group-0001"
PHRASE = "a flood of poems and speeches"
BACKUP_SUFFIX = ".bak-s2-handoff-chp15-p364-praise-text-group-20261010"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def decode_csv(raw: bytes) -> tuple[bool, list[str], list[dict[str, str]]]:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return has_bom, list(reader.fieldnames or []), list(reader)


def appended_csv(raw: bytes, fields: list[str], row: dict[str, str]) -> bytes:
    has_bom, current_fields, _ = decode_csv(raw)
    if fields != current_fields:
        raise SystemExit("Candidate or mention CSV schema changed.")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=fields, lineterminator=newline).writerow(row)
    text = raw.decode("utf-8-sig")
    if not text.endswith(("\n", "\r")):
        text += newline
    text += buffer.getvalue()
    return (("\ufeff" if has_bom else "") + text).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register the source-bounded unidentified poems and speeches about Farsetti."
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[37:41])
    if segment_text.count(PHRASE) != 1:
        raise SystemExit("Expected the exact phrase once in p.364 segment L38-L41.")
    start = segment_text.index(PHRASE)
    end = start + len(PHRASE)
    if (start, end) != (1180, 1209):
        raise SystemExit(f"Source span changed: expected [1180,1209), found [{start},{end}).")

    statement_raw = STATEMENTS.read_bytes()
    mention_raw = MENTIONS.read_bytes()
    candidate_raw = CANDIDATES.read_bytes()
    statement_text = statement_raw.decode("utf-8-sig")
    statement_lines = statement_text.splitlines(keepends=True)
    statement_rows = [json.loads(line) for line in statement_lines if line.strip()]
    matches = [row for row in statement_rows if row.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one {STATEMENT_ID}; found {len(matches)}.")
    original = matches[0]
    if (
        original.get("segment_id") != SEGMENT_ID
        or original.get("subject_candidate_id") != "cand-1002"
        or original.get("object_candidate_id") is not None
        or original.get("predicate") != "held_up_as_example_in_unidentified_poems_and_speeches"
        or original.get("qualifiers", {}).get("source_line_start") != 40
        or original.get("qualifiers", {}).get("source_line_end") != 40
        or PHRASE not in original.get("original_quote", "")
        or original.get("qualifiers", {}).get("relation_candidate") is not True
    ):
        raise SystemExit("The p.364 praise statement changed from its reviewed precondition.")

    mention_bom, mention_fields, mention_rows = decode_csv(mention_raw)
    candidate_bom, candidate_fields, candidate_rows = decode_csv(candidate_raw)
    if mention_bom != candidate_bom:
        raise SystemExit("CSV BOM state differs; refusing to alter encoding conventions.")
    if any(row.get("mention_id") == MENTION_ID for row in mention_rows):
        raise SystemExit(f"{MENTION_ID} already exists.")
    if any(row.get("candidate_id") == CANDIDATE_ID for row in candidate_rows):
        raise SystemExit(f"{CANDIDATE_ID} already exists.")
    if any(
        row.get("segment_id") == SEGMENT_ID
        and row.get("surface_form", "").casefold() == PHRASE.casefold()
        for row in mention_rows
    ):
        raise SystemExit("The exact source phrase already has a mention in this segment.")
    highest = max(
        int(match.group(1))
        for row in candidate_rows
        if (match := re.fullmatch(r"cand-(\d+)", row.get("candidate_id", "")))
    )
    if highest != 11564:
        raise SystemExit(f"Candidate sequence changed; highest ID is {highest}.")

    candidate = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Unnamed poems and speeches holding Filippo Farsetti up as an example",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Source-bounded group described by Haskell as a flood of poems and speeches in which Farsetti was held "
            "up as an example during a hoped-for cultural revival. No individual text, author, date, exact count, or "
            "group member is named. The source does not define a type that cleanly covers this mixed literary and "
            "oratorical group, so the candidate type remains unspecified."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L40",
    }
    if list(candidate) != candidate_fields:
        raise SystemExit(f"Candidate CSV columns changed: {candidate_fields}")
    mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": PHRASE,
        "start_char": str(start),
        "end_char": str(end),
        "note": (
            "The plural source phrase identifies a body of unnamed poems and speeches in which Farsetti was held up "
            "as an example; individual works and the group's exact extent are not supplied."
        ),
    }
    if list(mention) != mention_fields:
        raise SystemExit(f"Mention CSV columns changed: {mention_fields}")

    updated = json.loads(json.dumps(original))
    updated["object_candidate_id"] = CANDIDATE_ID
    qualifiers = updated.setdefault("qualifiers", {})
    qualifiers["mentioned_candidate_ids"] = list(
        dict.fromkeys([*qualifiers.get("mentioned_candidate_ids", []), CANDIDATE_ID])
    )
    qualifiers["qualification"] = (
        "The object is the source-bounded but unidentified group of poems and speeches in which Haskell says "
        "Farsetti was held up as an example. No individual text, author, date, or exact count is supplied; the "
        "candidate type remains unspecified because the taxonomy does not clearly classify this mixed group."
    )
    qualifiers["relation_candidate_note"] = (
        "The object endpoint cand-11565 represents the unnamed group of poems and speeches described in the source. "
        "Do not infer individual works, authors, dates, or a precise number from the rhetorical phrase 'a flood'."
    )

    newline = "\r\n" if b"\r\n" in statement_raw else "\n"
    replacements = 0
    output_lines: list[str] = []
    for line in statement_lines:
        if line.strip() and json.loads(line).get("statement_id") == STATEMENT_ID:
            output_lines.append(json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + newline)
            replacements += 1
        else:
            output_lines.append(line)
    if replacements != 1:
        raise SystemExit(f"Expected one statement replacement; found {replacements}.")
    statement_after = (
        ("\ufeff" if statement_raw.startswith(b"\xef\xbb\xbf") else "") + "".join(output_lines)
    ).encode("utf-8")
    mention_after = appended_csv(mention_raw, mention_fields, mention)
    candidate_after = appended_csv(candidate_raw, candidate_fields, candidate)

    before = {
        "statements": sha(statement_raw),
        "mentions": sha(mention_raw),
        "candidates": sha(candidate_raw),
    }
    after = {
        "statements": sha(statement_after),
        "mentions": sha(mention_after),
        "candidates": sha(candidate_after),
    }
    print(
        json.dumps(
            {"candidate": candidate, "mention": mention, "statement_object": CANDIDATE_ID,
             "before_sha256": before, "after_sha256": after},
            ensure_ascii=False,
            indent=2,
        )
    )

    if not args.apply:
        print("Dry-run only; tables unchanged.")
        return
    expected = {
        "statements": args.expected_statements_sha256,
        "mentions": args.expected_mentions_sha256,
        "candidates": args.expected_candidates_sha256,
    }
    if not all(expected.values()) or expected != before:
        raise SystemExit(f"Expected table hashes {expected}, current hashes {before}; no write performed.")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, MENTIONS, CANDIDATES)}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("A recovery backup already exists; refusing to overwrite it.")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    STATEMENTS.write_bytes(statement_after)
    MENTIONS.write_bytes(mention_after)
    CANDIDATES.write_bytes(candidate_after)
    print(
        json.dumps(
            {"applied": True, "backups": {str(k): str(v) for k, v in backups.items()}, "after_sha256": after},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
