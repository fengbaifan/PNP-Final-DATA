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
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l141-145"
COMMISSION_ID = "st-chp2-secii-l141-145-barberini-altar-pictures-commission"
RENI_ID = "st-chp2-secii-l141-145-reni-archangel-picture-sent"
RENI_MENTION_ID = "m-chp2-secii-l141-145-0029"
GROUP_MENTION_ID = "m-chp2-secii-l141-145-0039"
GROUP_CANDIDATE_ID = "cand-11554"
PERSON_CANDIDATE_ID = "cand-2124"
INDEX_WORK_CANDIDATE_ID = "cand-2126"
NAMED_WORK_CANDIDATE_ID = "cand-4544"
OTHER_PAINTINGS_CANDIDATE_ID = "cand-4545"
GROUP_SURFACE = "altar pictures"
RENI_SURFACE = "Guido Reni"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_csv(raw: bytes) -> tuple[str, bool, list[str]]:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    header = next(csv.reader(io.StringIO(text, newline="")))
    return text, has_bom, header


def encode_csv(text: str, has_bom: bool) -> bytes:
    return (("\ufeff" if has_bom else "") + text).encode("utf-8")


def csv_line(values: list[str], newline: str) -> str:
    buffer = io.StringIO(newline="")
    csv.writer(buffer, lineterminator=newline).writerow(values)
    return buffer.getvalue()


def parse_csv_rows(raw: bytes) -> tuple[str, bool, list[str], list[dict[str, str]]]:
    text, has_bom, header = read_csv(raw)
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    return text, has_bom, header, rows


def validate_source() -> tuple[int, int]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(lines[140:145])
    if not lines[143].startswith("For the altar pictures the Pope and his brother commissioned works"):
        raise SystemExit("The p.43 source sentence no longer matches the reviewed commission passage.")
    start = segment_text.find(GROUP_SURFACE)
    if start != 1574 or segment_text.find(GROUP_SURFACE, start + 1) >= 0:
        raise SystemExit(f"Expected one altar-pictures span at [1574:1588); found start={start}.")
    if segment_text[1589:1597] != "the Pope" or segment_text[1716:1726] != RENI_SURFACE:
        raise SystemExit("Existing p.43 mention offsets no longer match this exact segment text.")
    return start, start + len(GROUP_SURFACE)


def validate_candidates(candidate_rows: list[dict[str, str]]) -> None:
    by_id = {row.get("candidate_id"): row for row in candidate_rows}
    person = by_id.get(PERSON_CANDIDATE_ID)
    if not person or person.get("canonical_name") != "Reni, Guido" or person.get("suggested_type") != "person":
        raise SystemExit("The page-43 painter does not resolve to the expected person-level index candidate.")
    indexed_work = by_id.get(INDEX_WORK_CANDIDATE_ID)
    if (
        not indexed_work
        or indexed_work.get("canonical_name") != "Reni, Guido"
        or indexed_work.get("suggested_type") != "work"
        or indexed_work.get("sub_entry") != "Archangel Michael Trampling on the Devil"
    ):
        raise SystemExit("The distinct Reni index sub-entry for the painting has changed; review candidate boundaries.")
    if not by_id.get(NAMED_WORK_CANDIDATE_ID) or not by_id.get(OTHER_PAINTINGS_CANDIDATE_ID):
        raise SystemExit("Expected existing named-work and other-paintings candidates were not found.")
    if by_id[OTHER_PAINTINGS_CANDIDATE_ID].get("suggested_type") != "work":
        raise SystemExit("The existing group of other altar paintings is no longer typed as work.")
    if GROUP_CANDIDATE_ID in by_id:
        raise SystemExit(f"Planned group candidate {GROUP_CANDIDATE_ID} already exists.")
    highest = max(int(row["candidate_id"].removeprefix("cand-")) for row in candidate_rows)
    if highest != 11553 or int(GROUP_CANDIDATE_ID.removeprefix("cand-")) != highest + 1:
        raise SystemExit(f"Candidate sequence changed; current highest candidate ID is {highest}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve the p.43 collective altar-picture commission to a bounded S2 work-group candidate."
    )
    parser.add_argument("--apply", action="store_true", help="Apply only with all three exact dry-run hashes.")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    group_start, group_end = validate_source()
    statement_raw = STATEMENTS.read_bytes()
    mention_raw = MENTIONS.read_bytes()
    candidate_raw = CANDIDATES.read_bytes()

    statement_lines = statement_raw.decode("utf-8").splitlines(keepends=True)
    records = [json.loads(line) for line in statement_lines if line.strip()]
    commission_rows = [row for row in records if row.get("statement_id") == COMMISSION_ID]
    reni_rows = [row for row in records if row.get("statement_id") == RENI_ID]
    if len(commission_rows) != 1 or len(reni_rows) != 1:
        raise SystemExit("Expected exactly one commission statement and one Reni-work statement.")
    commission = commission_rows[0]
    reni_statement = reni_rows[0]
    if (
        commission.get("segment_id") != SEGMENT_ID
        or commission.get("object_candidate_id") is not None
        or commission.get("qualifiers", {}).get("relation_candidate") is not True
    ):
        raise SystemExit("The joint commission statement no longer has its expected open S2 endpoint.")
    if (
        reni_statement.get("segment_id") != SEGMENT_ID
        or reni_statement.get("subject_candidate_id") != INDEX_WORK_CANDIDATE_ID
        or reni_statement.get("object_candidate_id") != NAMED_WORK_CANDIDATE_ID
    ):
        raise SystemExit("The Reni statement endpoints changed; review before applying the person/work correction.")

    candidate_text, candidate_bom, candidate_header, candidate_rows = parse_csv_rows(candidate_raw)
    validate_candidates(candidate_rows)
    candidate_newline = "\r\n" if b"\r\n" in candidate_raw else "\n"
    candidate = {
        "candidate_id": GROUP_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Altar pictures commissioned by Urban VIII and Antonio Barberini for S. Maria della Concezione",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "A source-bounded group of altar pictures commissioned by Urban VIII and Antonio Barberini for the Capuchin church "
            "S. Maria della Concezione. Haskell names Guido Reni's The Archangel Michael and a separate group of other paintings. "
            "The total count, complete membership, and individual work assignments beyond the named Reni picture are not supplied. "
            "Keep this group distinct from the named painting cand-4544 and the other-paintings group cand-4545; do not treat it as one painting or infer survival at the church."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L144",
    }
    candidate_line = csv_line([candidate.get(col, "") for col in candidate_header], candidate_newline)
    candidate_after_text = candidate_text
    if candidate_after_text and not candidate_after_text.endswith(("\n", "\r")):
        candidate_after_text += candidate_newline
    candidate_after_text += candidate_line
    candidate_after = encode_csv(candidate_after_text, candidate_bom)

    mention_text, mention_bom, mention_header, mention_rows = parse_csv_rows(mention_raw)
    by_mention = {row.get("mention_id"): row for row in mention_rows}
    group_existing = [
        row for row in mention_rows
        if row.get("segment_id") == SEGMENT_ID and row.get("surface_form", "").casefold() == GROUP_SURFACE.casefold()
    ]
    if group_existing or GROUP_MENTION_ID in by_mention:
        raise SystemExit("The group phrase or planned mention ID already exists; inspect its current mapping.")
    reni_mention = by_mention.get(RENI_MENTION_ID)
    if (
        not reni_mention
        or reni_mention.get("segment_id") != SEGMENT_ID
        or reni_mention.get("candidate_id") != INDEX_WORK_CANDIDATE_ID
        or reni_mention.get("surface_form") != RENI_SURFACE
    ):
        raise SystemExit("The Guido Reni mention no longer has the reviewed person/work mismatch.")
    mention_newline = "\r\n" if b"\r\n" in mention_raw else "\n"
    mention_new = {
        "mention_id": GROUP_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": GROUP_CANDIDATE_ID,
        "surface_form": GROUP_SURFACE,
        "start_char": str(group_start),
        "end_char": str(group_end),
        "note": "The bounded group of altar pictures named in the joint commission statement; not an individual painting.",
    }
    mention_lines = mention_text.splitlines(keepends=True)
    mention_header_line = next(csv.reader(io.StringIO(mention_text, newline="")))
    start_marker = f"{RENI_MENTION_ID},"
    reni_line_positions = [i for i, line in enumerate(mention_lines) if line.startswith(start_marker)]
    if len(reni_line_positions) != 1:
        raise SystemExit("Could not uniquely locate the existing Guido Reni mention row.")
    reni_line_index = reni_line_positions[0]
    old_reni_line = mention_lines[reni_line_index]
    old_reni_ending = "\r\n" if old_reni_line.endswith("\r\n") else "\n" if old_reni_line.endswith("\n") else ""
    old_reni_values = next(csv.reader([old_reni_line.rstrip("\r\n")]))
    if len(old_reni_values) != len(mention_header_line):
        raise SystemExit("The Guido Reni CSV row is not a single standard record; refusing a broad rewrite.")
    reni_values = dict(zip(mention_header_line, old_reni_values, strict=True))
    reni_values["candidate_id"] = PERSON_CANDIDATE_ID
    reni_values["note"] = (
        "Guido Reni is the painter; use the person-level index candidate cand-2124. "
        "The separate index sub-entry cand-2126 identifies the Archangel Michael work."
    )
    mention_lines[reni_line_index] = csv_line([reni_values[col] for col in mention_header], old_reni_ending)
    pope_marker = "m-chp2-secii-l141-145-0027,"
    pope_positions = [i for i, line in enumerate(mention_lines) if line.startswith(pope_marker)]
    if len(pope_positions) != 1:
        raise SystemExit("Could not uniquely locate the p.43 Pope mention insertion point.")
    mention_lines.insert(
        pope_positions[0],
        csv_line([mention_new.get(col, "") for col in mention_header], mention_newline),
    )
    mention_after = encode_csv("".join(mention_lines), mention_bom)

    commission_new = json.loads(json.dumps(commission))
    commission_new["object_candidate_id"] = GROUP_CANDIDATE_ID
    qualifiers = commission_new["qualifiers"]
    qualifiers["artist_candidates"] = [
        PERSON_CANDIDATE_ID if candidate_id == INDEX_WORK_CANDIDATE_ID else candidate_id
        for candidate_id in qualifiers.get("artist_candidates", [])
    ]
    qualifiers.pop("open_endpoint_reason", None)
    qualifiers["mentioned_candidate_ids"] = [GROUP_CANDIDATE_ID]
    qualifiers["qualification"] = (
        "The commissioned objects are represented by bounded group candidate cand-11554, defined by the joint altar-picture "
        "commission at S. Maria della Concezione. Haskell names Reni's Archangel Michael and a further group of paintings; "
        "the total count, complete membership, and individual assignments beyond the named Reni work are not established. "
        "The following named contributors and works are recorded separately; the passage does not specify that every contributor "
        "belonged to exactly the same generation."
    )

    reni_new = json.loads(json.dumps(reni_statement))
    reni_new["subject_candidate_id"] = PERSON_CANDIDATE_ID
    reni_new["qualifiers"]["qualification"] = (
        "Guido Reni is mapped to person candidate cand-2124; the separate index work sub-entry cand-2126 remains distinct. "
        "The passive ‘was written to’ does not identify who wrote to Reni; the preceding sentence names Urban VIII and Antonio as commissioners."
    )

    statement_newline = "\r\n" if b"\r\n" in statement_raw else "\n"
    statement_after_lines = []
    replaced = {COMMISSION_ID: 0, RENI_ID: 0}
    for line in statement_lines:
        if not line.strip():
            statement_after_lines.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id == COMMISSION_ID:
            statement_after_lines.append(json.dumps(commission_new, ensure_ascii=False, separators=(",", ":")) + statement_newline)
            replaced[COMMISSION_ID] += 1
        elif statement_id == RENI_ID:
            statement_after_lines.append(json.dumps(reni_new, ensure_ascii=False, separators=(",", ":")) + statement_newline)
            replaced[RENI_ID] += 1
        else:
            statement_after_lines.append(line)
    if replaced != {COMMISSION_ID: 1, RENI_ID: 1}:
        raise SystemExit(f"Expected to update exactly two statements; replacements={replaced}.")
    statement_after = "".join(statement_after_lines).encode("utf-8")

    print(f"statements_sha256={sha256(statement_raw)}")
    print(f"mentions_sha256={sha256(mention_raw)}")
    print(f"candidates_sha256={sha256(candidate_raw)}")
    print(f"group_candidate_add={GROUP_CANDIDATE_ID}: {candidate['canonical_name']} [work]")
    print(f"mention_add={GROUP_MENTION_ID}: {GROUP_SURFACE} [{group_start}:{group_end})")
    print(f"mention_update={RENI_MENTION_ID}: {INDEX_WORK_CANDIDATE_ID} -> {PERSON_CANDIDATE_ID}")
    print(f"statement_update={COMMISSION_ID}: object null -> {GROUP_CANDIDATE_ID}; open scalar endpoint resolved")
    print(f"statement_update={RENI_ID}: subject {INDEX_WORK_CANDIDATE_ID} -> person {PERSON_CANDIDATE_ID}")
    print("expected_counts_after_apply: candidates +1; mentions +1; statements unchanged; relation_candidates unchanged; complete_endpoints +1; open_endpoints -1")
    if not args.apply:
        print("DRY-RUN: no files changed.")
        return

    expected = (args.expected_statements_sha256, args.expected_mentions_sha256, args.expected_candidates_sha256)
    actual = (sha256(statement_raw), sha256(mention_raw), sha256(candidate_raw))
    if None in expected or expected != actual:
        raise SystemExit("--apply requires all three hashes from this exact dry run.")

    changes = [
        (STATEMENTS, statement_raw, statement_after, "book-statements.jsonl.bak-s2-handoff-chp2-p43-altar-group-20261009"),
        (MENTIONS, mention_raw, mention_after, "mentions.csv.bak-s2-handoff-chp2-p43-altar-group-20261009"),
        (CANDIDATES, candidate_raw, candidate_after, "entity-candidates.csv.bak-s2-handoff-chp2-p43-altar-group-20261009"),
    ]
    backups = []
    temps = []
    for path, old, new, backup_name in changes:
        backup = path.with_name(backup_name)
        if backup.exists():
            raise SystemExit(f"Refusing to overwrite recovery copy: {backup}")
        backups.append((path, old, backup))
    try:
        for path, old, backup in backups:
            shutil.copy2(path, backup)
        for path, _, new, _ in changes:
            temp = path.with_name(path.name + ".tmp-s2-handoff-chp2-p43")
            if temp.exists():
                raise SystemExit(f"Refusing to overwrite temporary file: {temp}")
            temp.write_bytes(new)
            temps.append((temp, path))
        for temp, path in temps:
            os.replace(temp, path)
    except Exception:
        for temp, path in temps:
            if temp.exists():
                temp.unlink()
            matching = next((old for original, old, _ in backups if original == path), None)
            if matching is not None and path.exists() and path.read_bytes() != matching:
                path.write_bytes(matching)
        raise
    print("APPLIED: group endpoint and person/work distinction written to the three S2 tables.")
    for path, old, backup in backups:
        print(f"recovery_copy={backup} sha256={sha256(backup.read_bytes())}")
        print(f"new_file={path} sha256={sha256(path.read_bytes())}")


if __name__ == "__main__":
    main()
