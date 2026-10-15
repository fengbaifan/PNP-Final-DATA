from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
SEGMENTS = TABLE_DIR / "segments.jsonl"
COVERAGE = TABLE_DIR / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "00_05_List_of_Plates.md"
TASK_PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"

STATEMENT_ID = "st-fm-2ed-l190-196-09-selected-artists"
SEGMENT_ID = "front-matter:00_05_List_of_Plates:l190-196"
GROUP_CANDIDATE_ID = "cand-12262"
GROUP_MENTION_ID = "m-fm-2ed-l190-196-025"
EVENT_CANDIDATE_ID = "cand-3613"
MEMBER_CANDIDATE_IDS = [
    "cand-3881",
    "cand-3869",
    "cand-3054",
    "cand-3863",
    "cand-3891",
    "cand-3789",
    "cand-3780",
]
SURFACE = "those chosen"
START, END = 908, 920

EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "287cb3b73ce8d113e6d82d1fb28fc9630145b1277ce010858b731d16c1e1f8f2",
    MENTIONS: "389c4878660c1f6d3a530bc986eec11e968b8cc9a1a1397087a2960dd5563edf",
    STATEMENTS: "b1c540ab56932e9acbcb2791dba14a347a2e09afd2638c714e415a4a5466864a",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    COVERAGE: "1352b756f0f0310c00d21bfc3bfe194b5a347d291b699db78b5c85fa6e636a4d",
    SOURCE: "96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83",
}
BACKUPS = {
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-fm-selected-artists-group-20261015"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-fm-selected-artists-group-20261015"),
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-fm-selected-artists-group-20261015"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def serialize_csv_row(headers: list[str], row: dict[str, str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n", extrasaction="ignore")
    writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def append_bytes(current: bytes, addition: bytes) -> bytes:
    separator = b"" if current.endswith((b"\n", b"\r")) else b"\n"
    return current + separator + addition


def validate_and_build() -> tuple[dict[Path, bytes], dict[str, str]]:
    import subprocess

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit(f"HEAD changed: expected {EXPECTED_HEAD}, got {head}")
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"{path.relative_to(ROOT)} hash changed: expected {expected}, got {actual}")

    candidate_bytes = CANDIDATES.read_bytes()
    mention_bytes = MENTIONS.read_bytes()
    statement_bytes = STATEMENTS.read_bytes()
    candidate_headers, candidates = parse_csv(candidate_bytes)
    mention_headers, mentions = parse_csv(mention_bytes)
    if not candidate_headers or not mention_headers:
        raise SystemExit("candidate or mention table has no header")
    if len(candidates) != 12_239 or len(mentions) != 26_427:
        raise SystemExit("unexpected candidate or mention row count")
    candidate_ids = [row["candidate_id"] for row in candidates]
    mention_ids = [row["mention_id"] for row in mentions]
    if len(candidate_ids) != len(set(candidate_ids)) or len(mention_ids) != len(set(mention_ids)):
        raise SystemExit("candidate or mention IDs are duplicated")
    if GROUP_CANDIDATE_ID in set(candidate_ids) or GROUP_MENTION_ID in set(mention_ids):
        raise SystemExit("new candidate or mention ID already exists")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if candidate_by_id.get(EVENT_CANDIDATE_ID, {}).get("suggested_type") != "event":
        raise SystemExit("the San Clemente redecoration event candidate changed")
    for candidate_id in MEMBER_CANDIDATE_IDS:
        member = candidate_by_id.get(candidate_id)
        if not member or member.get("suggested_type") != "person":
            raise SystemExit(f"named participant candidate is missing or not a person: {candidate_id}")

    segment_map = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    segment = segment_map.get(SEGMENT_ID)
    if not segment:
        raise SystemExit(f"source segment is missing: {SEGMENT_ID}")
    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != EXPECTED_HASHES[SOURCE] or sha256(source_bytes) != segment.get("asset_sha256"):
        raise SystemExit("S0 source asset hash mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha256(segment_text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    if segment_text[START:END] != SURFACE:
        raise SystemExit("group mention span does not match S0 text")

    coverage = {
        row["segment_id"]: row
        for row in csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline=""))
    }.get(SEGMENT_ID)
    if not coverage or coverage.get("disposition") != "reviewed" or coverage.get("migration_status") != "complete":
        raise SystemExit("S2 coverage is not reviewed/complete for the selected source segment")

    mention_rows_by_id = {row["mention_id"]: row for row in mentions}
    existing_members = {
        row["candidate_id"]
        for row in mentions
        if row["segment_id"] == SEGMENT_ID and row["candidate_id"] in MEMBER_CANDIDATE_IDS
    }
    if existing_members != set(MEMBER_CANDIDATE_IDS):
        raise SystemExit("one or more named participant mentions are absent from the source segment")
    for row in mentions:
        if row["segment_id"] != SEGMENT_ID:
            continue
        start, end = int(row["start_char"]), int(row["end_char"])
        if START < end and END > start:
            raise SystemExit(f"group mention span overlaps existing mention {row['mention_id']}")

    statement_lines = statement_bytes.splitlines(keepends=True)
    target_index = None
    target_statement = None
    for index, raw_line in enumerate(statement_lines):
        if not raw_line.strip():
            continue
        row = json.loads(raw_line)
        if row.get("statement_id") == STATEMENT_ID:
            target_index, target_statement = index, row
            break
    if target_statement is None:
        raise SystemExit(f"statement is missing: {STATEMENT_ID}")
    if target_statement.get("segment_id") != SEGMENT_ID or target_statement.get("object_candidate_id") != EVENT_CANDIDATE_ID:
        raise SystemExit("statement source or event endpoint changed")
    if target_statement.get("subject_candidate_id") is not None:
        raise SystemExit("statement subject endpoint is no longer open")
    qualifiers = target_statement.get("qualifiers", {})
    if (
        qualifiers.get("relation_candidate") is not True
        or qualifiers.get("participant_candidate_ids") != MEMBER_CANDIDATE_IDS
        or qualifiers.get("source_line_start") != 193
    ):
        raise SystemExit("statement participant list or source anchor changed")

    new_candidate = {
        "candidate_id": GROUP_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Seven artists selected for the S. Clemente redecoration (source-defined group)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Source-defined cohort of the seven artists named in Haskell's indicative list of those chosen "
            "for Pope Clement XI's second-decade eighteenth-century redecoration of S. Clemente. "
            "The listed members are mapped separately in participant_candidate_ids; the list may not be exhaustive, "
            "and no individual paintings are allocated. Type remains unset because the current taxonomy has no "
            "person-group type and the source gives no organizational identity."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L193",
    }
    new_mention = {
        "mention_id": GROUP_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": GROUP_CANDIDATE_ID,
        "surface_form": SURFACE,
        "start_char": str(START),
        "end_char": str(END),
        "note": "Anaphoric group reference to the seven named artists that follow; Haskell calls the list indicative, so it may not be exhaustive.",
    }

    candidate_after = append_bytes(candidate_bytes, serialize_csv_row(candidate_headers, new_candidate))
    mention_after = append_bytes(mention_bytes, serialize_csv_row(mention_headers, new_mention))
    updated_statement = dict(target_statement)
    updated_statement["subject_candidate_id"] = GROUP_CANDIDATE_ID
    updated_qualifiers = dict(qualifiers)
    updated_qualifiers.pop("open_endpoint_reason", None)
    updated_qualifiers["relation_candidate_note"] = (
        "The phrase 'those chosen' is mapped to a source-defined group of seven named artists; "
        "participant_candidate_ids retains the individually mapped names. The list is indicative and may not be exhaustive; "
        "no individual paintings are allocated. The group's type remains unset pending taxonomy-compatible treatment."
    )
    updated_statement["qualifiers"] = updated_qualifiers
    original_line = statement_lines[target_index]
    line_ending = b"\r\n" if original_line.endswith(b"\r\n") else b"\n" if original_line.endswith(b"\n") else b""
    replacement = json.dumps(updated_statement, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + line_ending
    statement_lines[target_index] = replacement
    statement_after = b"".join(statement_lines)

    candidate_after_headers, candidate_after_rows = parse_csv(candidate_after)
    mention_after_headers, mention_after_rows = parse_csv(mention_after)
    if candidate_after_headers != candidate_headers or mention_after_headers != mention_headers:
        raise SystemExit("appended table rows failed header validation")
    if len(candidate_after_rows) != len(candidates) + 1 or len(mention_after_rows) != len(mentions) + 1:
        raise SystemExit("appended table row counts are incorrect")
    if len({row["candidate_id"] for row in candidate_after_rows}) != len(candidate_after_rows):
        raise SystemExit("candidate ID validation failed after preview")
    if len({row["mention_id"] for row in mention_after_rows}) != len(mention_after_rows):
        raise SystemExit("mention ID validation failed after preview")
    updated_decoded = [json.loads(line) for line in statement_after.splitlines() if line.strip()]
    if len(updated_decoded) != 15_109:
        raise SystemExit("statement count changed unexpectedly")
    updated_target = next(row for row in updated_decoded if row.get("statement_id") == STATEMENT_ID)
    if updated_target.get("subject_candidate_id") != GROUP_CANDIDATE_ID:
        raise SystemExit("statement endpoint did not update in the preview")

    return {
        CANDIDATES: candidate_after,
        MENTIONS: mention_after,
        STATEMENTS: statement_after,
    }, {
        "candidate_count": str(len(candidate_after_rows)),
        "mention_count": str(len(mention_after_rows)),
        "statement_count": str(len(updated_decoded)),
        "group_span": f"{START}:{END}",
        "group_candidate_id": GROUP_CANDIDATE_ID,
    }


def apply_transaction(updates: dict[Path, bytes]) -> None:
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("one or more recovery backups already exist")
    for path, expected in EXPECTED_HASHES.items():
        if sha256(path.read_bytes()) != expected:
            raise SystemExit(f"{path.relative_to(ROOT)} changed after preview")

    for source, backup in BACKUPS.items():
        shutil.copy2(source, backup)

    temps: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for target, data in updates.items():
            with tempfile.NamedTemporaryFile("wb", dir=target.parent, delete=False) as stream:
                temp_path = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            temps[target] = temp_path
        for target, temp_path in temps.items():
            os.replace(temp_path, target)
            replaced.append(target)
    except Exception:
        for target in reversed(replaced):
            shutil.copy2(BACKUPS[target], target)
        raise
    finally:
        for temp_path in temps.values():
            if temp_path.exists():
                temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Map the seven named artists as a source-defined group endpoint in S2.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    updates, summary = validate_and_build()
    print(f"statement={STATEMENT_ID} subject_candidate_id {None} -> {summary['group_candidate_id']}")
    print(f"new_group_mention={GROUP_MENTION_ID} span={summary['group_span']} surface={SURFACE!r}")
    print(f"candidate_count={summary['candidate_count']} mention_count={summary['mention_count']} statement_count={summary['statement_count']}")
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(data)}")
    if args.preview:
        print("preview only; no files or backups written")
        return

    apply_transaction(updates)
    print("backups:")
    for backup in BACKUPS.values():
        print(backup)
    print("applied")


if __name__ == "__main__":
    main()
