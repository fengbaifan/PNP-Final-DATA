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

SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l30-36"
STATUE_CANDIDATE_ID = "cand-11561"
STATUE_MENTION_ID = "m-chp15-p367-memmo-0066"
STATUE_MENTION = "one"
WALDSTEIN_ID = "st-chp15-p367-waldstein-might-fund-statue"
SKALA_ID = "st-chp15-p367-skala-possible-statue-subject"
VEITH_ID = "st-chp15-p367-veith-alternative-statue-subject"
FURTHER_STATUES_ID = "st-chp15-p367-further-statues-still-needed"


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
    if len(lines) < 36:
        raise SystemExit("The p.367 source sentence no longer matches the reviewed letter passage.")
    segment_text = "\n".join(lines[29:36])
    source_phrase = "pay for one—Giovanni Dubravio Skala, perhaps"
    if segment_text.count(source_phrase) != 1:
        raise SystemExit("The p.367 source sentence no longer matches the reviewed letter passage.")
    expected_start = segment_text.index("pay for one—") + len("pay for ")
    if segment_text[expected_start : expected_start + len(STATUE_MENTION)] != STATUE_MENTION:
        raise SystemExit("The singular statue pronoun no longer matches the reviewed source span.")
    if (expected_start, expected_start + len(STATUE_MENTION)) != (1175, 1178):
        raise SystemExit(f"Segment offsets changed: found [{expected_start},{expected_start + len(STATUE_MENTION)}).")
    return expected_start, expected_start + len(STATUE_MENTION), segment_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register the singular proposed Prà della Valle statue discussed in Memmo's Waldstein inquiry."
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
    by_id: dict[str, dict] = {}
    for statement_id in (WALDSTEIN_ID, SKALA_ID, VEITH_ID, FURTHER_STATUES_ID):
        matches = [row for row in statements if row.get("statement_id") == statement_id]
        if len(matches) != 1:
            raise SystemExit(f"Expected one statement {statement_id}; found {len(matches)}.")
        by_id[statement_id] = matches[0]

    for statement_id in (WALDSTEIN_ID, SKALA_ID, VEITH_ID):
        row = by_id[statement_id]
        if (
            row.get("segment_id") != SEGMENT_ID
            or row.get("object_candidate_id") is not None
            or row.get("qualifiers", {}).get("relation_candidate") is not True
            or not row.get("original_quote")
            or normalize(row["original_quote"]) not in normalize(segment_text)
        ):
            raise SystemExit(f"The target statement or source quote changed: {statement_id}.")
    if by_id[WALDSTEIN_ID].get("subject_candidate_id") != "cand-2797":
        raise SystemExit("The Waldstein candidate mapping changed.")
    if by_id[SKALA_ID].get("subject_candidate_id") != "cand-2436":
        raise SystemExit("The Skala candidate mapping changed.")
    if by_id[VEITH_ID].get("subject_candidate_id") != "cand-2708":
        raise SystemExit("The Veith candidate mapping changed.")

    candidate_raw_text, _, candidate_fields, candidate_rows = csv_parts(candidate_raw)
    candidate_ids = {row.get("candidate_id") for row in candidate_rows}
    highest = max(int(value.removeprefix("cand-")) for value in candidate_ids if value and value.startswith("cand-"))
    if STATUE_CANDIDATE_ID in candidate_ids or highest != 11560:
        raise SystemExit(f"Candidate sequence changed; found highest={highest}.")

    _, _, mention_fields, mention_rows = csv_parts(mention_raw)
    mention_ids = {row.get("mention_id") for row in mention_rows}
    if STATUE_MENTION_ID in mention_ids:
        raise SystemExit(f"Mention ID {STATUE_MENTION_ID} already exists.")
    if any(row.get("segment_id") == SEGMENT_ID and row.get("surface_form") == STATUE_MENTION for row in mention_rows):
        raise SystemExit("The singular statue pronoun already has a mention in this segment.")

    candidate = {
        "candidate_id": STATUE_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Unidentified Prà della Valle statue considered for possible Waldstein support",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell reports that Memmo asked Casanova whether Waldstein might pay for 'one' statue; Skala and Veith are "
            "alternative possible subjects. This candidate represents the proposed object only: no final subject, commission, "
            "payment, maker, title, or completion is established. Keep distinct from the earlier Statue of Antenor plan and "
            "from the later Canova-related statues."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L34",
    }
    if list(candidate) != candidate_fields:
        raise SystemExit(f"Candidate CSV schema changed: {candidate_fields}")

    mention = {
        "mention_id": STATUE_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": STATUE_CANDIDATE_ID,
        "surface_form": STATUE_MENTION,
        "start_char": str(start),
        "end_char": str(end),
        "note": "The singular pronoun refers to the possible statue Memmo asks Waldstein to fund; the following Skala and Veith clauses give alternative possible subjects, not a completed commission.",
    }
    if list(mention) != mention_fields:
        raise SystemExit(f"Mention CSV schema changed: {mention_fields}")

    statement_updates = {}
    qualifications = {
        WALDSTEIN_ID: (
            "The singular statue in Memmo's inquiry is represented by candidate cand-11561. This is only a question about "
            "possible support; no commitment, commission, payment, selected subject, or completed work is established."
        ),
        SKALA_ID: (
            "Skala is one tentative subject proposed for the singular statue represented by candidate cand-11561. The "
            "question mark and 'perhaps' remain; no subject is selected and no commission is established."
        ),
        VEITH_ID: (
            "Veith is offered as an alternative possible subject for the same statue represented by candidate cand-11561. "
            "No subject is selected and no commission is established."
        ),
    }
    relation_notes = {
        WALDSTEIN_ID: "The object is the one proposed statue represented by cand-11561; retain the conditional question and do not treat it as a pledge or payment.",
        SKALA_ID: "This is a tentative subject proposal for the statue candidate cand-11561, not an identified or commissioned work.",
        VEITH_ID: "This is an alternative tentative subject proposal for the same statue candidate cand-11561, not an identified or commissioned work.",
    }
    for statement_id in (WALDSTEIN_ID, SKALA_ID, VEITH_ID):
        updated = json.loads(json.dumps(by_id[statement_id]))
        updated["object_candidate_id"] = STATUE_CANDIDATE_ID
        qualifiers = updated.setdefault("qualifiers", {})
        existing = qualifiers.get("mentioned_candidate_ids", [])
        qualifiers["mentioned_candidate_ids"] = list(dict.fromkeys([*existing, STATUE_CANDIDATE_ID]))
        qualifiers["qualification"] = qualifications[statement_id]
        qualifiers["relation_candidate_note"] = relation_notes[statement_id]
        statement_updates[statement_id] = updated

    plural_updated = json.loads(json.dumps(by_id[FURTHER_STATUES_ID]))
    plural_q = plural_updated.setdefault("qualifiers", {})
    plural_q["qualification"] = (
        "The plural set of further statues is not enumerated. The following letter discussion isolates one possible statue, "
        "represented separately by cand-11561; that singular proposal does not define the full set or resolve its endpoint."
    )
    plural_q["relation_candidate_note"] = (
        "Keep the plural required-work set open. The following Waldstein inquiry concerns one possible statue represented by "
        "cand-11561, not an exhaustive endpoint for all further statues."
    )
    plural_q["related_statement_ids"] = list(dict.fromkeys([
        *plural_q.get("related_statement_ids", []), WALDSTEIN_ID
    ]))
    statement_updates[FURTHER_STATUES_ID] = plural_updated

    newline = "\r\n" if b"\r\n" in statement_raw else "\n"
    statement_after_lines = []
    replacements = {key: 0 for key in statement_updates}
    for line in statement_lines:
        if not line.strip():
            statement_after_lines.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in statement_updates:
            statement_after_lines.append(json.dumps(statement_updates[statement_id], ensure_ascii=False, separators=(",", ":")) + newline)
            replacements[statement_id] += 1
        else:
            statement_after_lines.append(line)
    if any(count != 1 for count in replacements.values()):
        raise SystemExit(f"Expected one write per statement; replacements={replacements}.")

    candidate_after = append_csv_row(candidate_raw, candidate)
    mention_after = append_csv_row(mention_raw, mention)
    has_statement_bom = statement_raw.startswith(b"\xef\xbb\xbf")
    statement_after = (b"\xef\xbb\xbf" if has_statement_bom else b"") + "".join(statement_after_lines).encode("utf-8")

    print(f"source_span={SEGMENT_ID}#L33-L35 [{start},{end}) surface={STATUE_MENTION!r}")
    print(f"candidate_add={STATUE_CANDIDATE_ID}: {candidate['canonical_name']} [work, open]")
    print(f"mention_add={STATUE_MENTION_ID}: {STATUE_MENTION} [{start},{end})")
    print(f"statement_object_updates={','.join((WALDSTEIN_ID, SKALA_ID, VEITH_ID))} -> {STATUE_CANDIDATE_ID}")
    print(f"statement_qualification_update={FURTHER_STATUES_ID}: plural endpoint remains open; singular proposal cross-linked")
    print("expected_counts_after_apply: candidates +1; mentions +1; statements unchanged; relation candidates unchanged; complete endpoints +3; open endpoints -3")
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
        (STATEMENTS, statement_raw, statement_after, "book-statements.jsonl.bak-s2-handoff-chp15-p367-proposed-statue-20261009"),
        (MENTIONS, mention_raw, mention_after, "mentions.csv.bak-s2-handoff-chp15-p367-proposed-statue-20261009"),
        (CANDIDATES, candidate_raw, candidate_after, "entity-candidates.csv.bak-s2-handoff-chp15-p367-proposed-statue-20261009"),
    ]
    backups = []
    temps = []
    for path, old, new, backup_name in changes:
        backup = path.with_name(backup_name)
        temp = path.with_name(path.name + ".tmp-s2-handoff-chp15-p367")
        if backup.exists():
            raise SystemExit(f"Refusing to overwrite recovery copy: {backup}")
        if temp.exists():
            raise SystemExit(f"Refusing to overwrite temporary file: {temp}")
        backups.append((path, old, backup))
    try:
        for path, old, backup in backups:
            shutil.copy2(path, backup)
        for path, _, new, _ in changes:
            temp = path.with_name(path.name + ".tmp-s2-handoff-chp15-p367")
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

    print("APPLIED: singular work candidate, mention, and three relation endpoints updated.")
    for path, old, backup in backups:
        print(f"recovery_copy={backup} sha256={sha256(backup.read_bytes())}")
        print(f"new_file={path} sha256={sha256(path.read_bytes())}")


if __name__ == "__main__":
    main()
