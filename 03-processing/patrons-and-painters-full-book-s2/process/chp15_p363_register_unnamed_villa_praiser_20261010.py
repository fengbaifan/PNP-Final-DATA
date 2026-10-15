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
SEGMENT_ID = "chp-15:15_CHP-15_sec_i:l27-36"
STATEMENT_ID = "st-chp15-p363-contemporary-praised-villa"
CANDIDATE_ID = "cand-11564"
MENTION_ID = "m-chp15-p363-0089"
PHRASE = "one of them"
BACKUP_SUFFIX = ".bak-s2-handoff-chp15-p363-unnamed-villa-praiser-20261010"


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
        description="Register the source-identified but unnamed contemporary who praised Farsetti's villa."
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[26:36])
    if segment_text.count(PHRASE) != 1:
        raise SystemExit("Expected the exact speaker phrase once in p.363 segment L27-L36.")
    start = segment_text.index(PHRASE)
    end = start + len(PHRASE)
    if (start, end) != (465, 476):
        raise SystemExit(f"Source span changed: expected [465,476), found [{start},{end}).")

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
        or original.get("subject_candidate_id") is not None
        or original.get("object_candidate_id") != "cand-10432"
        or original.get("predicate") != "villa_praised_by_unnamed_contemporary"
        or original.get("qualifiers", {}).get("source_line_start") != 28
        or original.get("qualifiers", {}).get("source_line_end") != 28
        or PHRASE not in original.get("original_quote", "")
        or original.get("qualifiers", {}).get("relation_candidate") is not True
    ):
        raise SystemExit("The p.363 villa-praise statement changed from its reviewed precondition.")

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
        raise SystemExit("The exact speaker phrase already has a mention in this segment.")
    highest = max(
        int(match.group(1))
        for row in candidate_rows
        if (match := re.fullmatch(r"cand-(\d+)", row.get("candidate_id", "")))
    )
    if highest != 11563:
        raise SystemExit(f"Candidate sequence changed; highest ID is {highest}.")

    candidate = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Unnamed contemporary who praised Filippo Farsetti's villa",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell says one of Farsetti's contemporaries wrote the quoted praise of the villa. The passage does not "
            "name the writer. Note 2 cites a Boscovich letter, but that letter and its wording were not independently "
            "consulted; do not identify this person as Boscovich from the footnote alone."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L28",
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
            "Refers to the one unnamed contemporary who wrote the quoted villa praise; identity is not supplied. "
            "Do not infer Boscovich from note 2 without consulting the cited letter."
        ),
    }
    if list(mention) != mention_fields:
        raise SystemExit(f"Mention CSV columns changed: {mention_fields}")

    updated = json.loads(json.dumps(original))
    updated["subject_candidate_id"] = CANDIDATE_ID
    qualifiers = updated.setdefault("qualifiers", {})
    qualifiers["mentioned_candidate_ids"] = list(
        dict.fromkeys([*qualifiers.get("mentioned_candidate_ids", []), CANDIDATE_ID])
    )
    qualifiers["qualification"] = (
        "The quoted speaker is the source-bounded unnamed contemporary candidate cand-11564, described as one of "
        "Farsetti's contemporaries. Note 2 cites a Boscovich letter, but the letter and its wording were not "
        "independently consulted; do not identify the speaker as Boscovich from that reference alone."
    )
    qualifiers["relation_candidate_note"] = (
        "The subject is the source-bounded unnamed contemporary cand-11564 who wrote the quoted praise. Keep the "
        "person's identity unresolved; note 2 is a citation locator, not independent proof of Boscovich's authorship."
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
            {"candidate": candidate, "mention": mention, "statement_subject": CANDIDATE_ID,
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
