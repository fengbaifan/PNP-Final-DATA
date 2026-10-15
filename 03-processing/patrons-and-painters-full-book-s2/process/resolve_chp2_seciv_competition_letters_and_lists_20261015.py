from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "95fb5b87e725ea8e0ebc5ab10b59ffb4168a44757b7b912a7d59bc2a33605cb1",
    MENTIONS: "6d81c7dd0c09eaade001aabab5aeed9fa48085f86b22b52a02a614ecf837bb4f",
    STATEMENTS: "41469184668b2d3389626b15451f0b8ad83ea4b0788c870887d6084cd4bf0f21",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l6-17"
NEXT_SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l19-29"
COMPETITION_ID = "st-chp2-seciv-l6-17-competition-and-committee-fragment"
COMMITTEE_ID = "st-chp2-seciv-l6-17-committee-correspondence-and-list-preparation"
LISTS_CONTINUATION_ID = "st-chp2-seciv-l19-29-committee-lists-amended"
NEW_LIST_STATEMENT_ID = "st-chp2-seciv-l6-17-committee-selection-lists-drawn"
ARTISTS_CANDIDATE_ID = "cand-12298"
LETTERS_CANDIDATE_ID = "cand-12299"
LISTS_CANDIDATE_ID = "cand-12300"
NEW_MENTION_IDS = {
    ARTISTS_CANDIDATE_ID: "m-chp2-seciv-l6-17-competing-artists-group",
    LETTERS_CANDIDATE_ID: "m-chp2-seciv-l6-17-committee-letters",
    LISTS_CANDIDATE_ID: "m-chp2-seciv-l6-17-committee-lists",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-competition-letters-lists-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def write_csv(data: bytes, headers: list[str], rows: list[dict[str, str]]) -> bytes:
    line_ending = "\r\n" if b"\r\n" in data else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    return bom + buffer.getvalue().encode("utf-8")


def open_endpoint_counts(rows: list[dict]) -> tuple[int, int, int, int]:
    relation_rows = [row for row in rows if row.get("qualifiers", {}).get("relation_candidate") is True]
    subject_missing = sum(not row.get("subject_candidate_id") for row in relation_rows)
    object_missing = sum(not row.get("object_candidate_id") for row in relation_rows)
    both_missing = sum(
        not row.get("subject_candidate_id") and not row.get("object_candidate_id")
        for row in relation_rows
    )
    return (
        subject_missing + object_missing - both_missing,
        object_missing - both_missing,
        subject_missing - both_missing,
        both_missing,
    )


def segment_text(segment_id: str, segments: list[dict], source_lines: list[str]) -> tuple[str, dict]:
    segment = next((row for row in segments if row.get("segment_id") == segment_id), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit(f"S0 segment or source asset mismatch: {segment_id}")
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit(f"S0 segment text hash mismatch: {segment_id}")
    return text, segment


def new_candidate(candidate_id: str, name: str, entity_type: str, detail: str) -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": entity_type,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L17",
    }


def build() -> tuple[dict[Path, bytes], dict[str, tuple[int, int]]]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    candidate_bytes = CANDIDATES.read_bytes()
    candidate_headers, candidate_rows = read_csv(candidate_bytes)
    mention_bytes = MENTIONS.read_bytes()
    mention_headers, mention_rows = read_csv(mention_bytes)
    statement_bytes = STATEMENTS.read_bytes()
    original_rows: list[dict] = []
    statement_by_id: dict[str, dict] = {}
    for raw in statement_bytes.splitlines(keepends=False):
        if raw.strip():
            row = json.loads(raw)
            original_rows.append(row)
            statement_by_id[row["statement_id"]] = row
    if len(statement_by_id) != len(original_rows):
        raise SystemExit("duplicate statement IDs")
    before_rows = copy.deepcopy(original_rows)

    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if any(cid in candidate_ids for cid in (ARTISTS_CANDIDATE_ID, LETTERS_CANDIDATE_ID, LISTS_CANDIDATE_ID)):
        raise SystemExit("planned candidate ID already exists")
    if any(mid in mention_ids for mid in NEW_MENTION_IDS.values()):
        raise SystemExit("planned mention ID already exists")
    if NEW_LIST_STATEMENT_ID in statement_by_id:
        raise SystemExit("planned statement ID already exists")
    max_candidate = max(
        int(row["candidate_id"].split("-")[1])
        for row in candidate_rows
        if row["candidate_id"].startswith("cand-")
    )
    if max_candidate != 12297:
        raise SystemExit(f"candidate sequence changed: {max_candidate}")

    segments = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text, _ = segment_text(SEGMENT_ID, segments, source_lines)
    _, next_segment = segment_text(NEXT_SEGMENT_ID, segments, source_lines)
    if int(next_segment.get("line_start", 0)) > int(next_segment.get("line_end", 0)):
        raise SystemExit("invalid continuation segment bounds")

    surfaces = {
        "artists and their protectors": ARTISTS_CANDIDATE_ID,
        "letters": LETTERS_CANDIDATE_ID,
        "lists": LISTS_CANDIDATE_ID,
    }
    spans: dict[str, tuple[int, int]] = {}
    for surface in surfaces:
        if text.count(surface) != 1:
            raise SystemExit(f"source phrase changed or is not unique: {surface}")
        start = text.index(surface)
        end = start + len(surface)
        spans[surface] = (start, end)
        for row in mention_rows:
            if (
                row["segment_id"] == SEGMENT_ID
                and start < int(row["end_char"])
                and end > int(row["start_char"])
            ):
                raise SystemExit(f"source span overlaps existing mention: {row['mention_id']}")

    expected_open = {
        COMPETITION_ID: (None, "cand-4605"),
        COMMITTEE_ID: ("cand-4306", None),
        LISTS_CONTINUATION_ID: ("cand-4306", None),
    }
    for statement_id, (subject, obj) in expected_open.items():
        row = statement_by_id.get(statement_id)
        if (
            not row
            or row.get("subject_candidate_id") != subject
            or row.get("object_candidate_id") != obj
            or row.get("qualifiers", {}).get("relation_candidate") is not True
        ):
            raise SystemExit(f"target statement state changed: {statement_id}")

    candidate_rows.extend(
        [
            new_candidate(
                ARTISTS_CANDIDATE_ID,
                "Artists and their protectors competing for new St Peter's altarpiece opportunities (source-defined group)",
                "",
                "Haskell describes artists and their protectors across Italy, especially Florence and Rome, competing for the opportunities opened by the new St Peter's altarpiece commissions. The group is defined by this competition; no individuals or complete roster are named. Type remains unset because the taxonomy has no person-group type.",
            ),
            new_candidate(
                LETTERS_CANDIDATE_ID,
                "Letters sent to the St Peter's altarpiece committee during its selection process (unnamed group)",
                "archive",
                "The plural correspondence that Haskell says inundated the St Peter's decoration committee during the altarpiece selection process. Individual letters, authors, count, and contents are not identified.",
            ),
            new_candidate(
                LISTS_CANDIDATE_ID,
                "Working lists drawn up and amended in the St Peter's altarpiece selection process",
                "archive",
                "The working lists that Haskell says were being drawn up and amended in the St Peter's committee process. Individual list documents, entries, and completeness are not identified.",
            ),
        ]
    )
    for surface, candidate_id in surfaces.items():
        start, end = spans[surface]
        mention_rows.append(
            {
                "mention_id": NEW_MENTION_IDS[candidate_id],
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(end),
                "note": "Source-bounded collective or document group; individual members, records, or complete contents are unspecified.",
            }
        )

    competition = statement_by_id[COMPETITION_ID]
    competition["subject_candidate_id"] = ARTISTS_CANDIDATE_ID
    competition_q = competition.setdefault("qualifiers", {})
    competition_q["qualification"] = (
        "The source defines the participants collectively as artists and their protectors competing for the St Peter's "
        "altarpiece opportunities. It names no individuals or complete membership list."
    )
    competition_q["relation_candidate_note"] = (
        "Map the explicit phrase 'artists and their protectors' to a type-undetermined, source-bounded group; do not infer members."
    )
    competition_q.pop("open_endpoint_reason", None)
    competition_q["mentioned_candidate_ids"] = list(
        dict.fromkeys([*(competition_q.get("mentioned_candidate_ids") or []), ARTISTS_CANDIDATE_ID, "cand-4605"])
    )

    committee = statement_by_id[COMMITTEE_ID]
    committee["object_candidate_id"] = LETTERS_CANDIDATE_ID
    committee["predicate"] = "received_correspondence_reported"
    committee["original_quote"] = "The committee was being bombarded with letters;"
    committee_q = committee.setdefault("qualifiers", {})
    committee_q["claim"] = "Haskell says the St Peter's decoration committee was being inundated with letters during the altarpiece selection process."
    committee_q["qualification"] = (
        "The source identifies a plural body of incoming correspondence but gives no individual letters, authors, count, or contents."
    )
    committee_q["relation_candidate_note"] = (
        "Use an open archive-group candidate for the explicitly mentioned letters received in this committee context; do not infer senders or contents."
    )
    committee_q.pop("open_endpoint_reason", None)
    committee_q["mentioned_candidate_ids"] = ["cand-4306", LETTERS_CANDIDATE_ID]
    prior_related = list(committee_q.get("related_statement_ids") or [])
    if LISTS_CONTINUATION_ID not in prior_related:
        raise SystemExit("expected list continuation link on the original composite statement")
    list_related = list(dict.fromkeys(prior_related))
    committee_related = [item for item in prior_related if item != LISTS_CONTINUATION_ID]
    if committee_related:
        committee_q["related_statement_ids"] = committee_related
    else:
        committee_q.pop("related_statement_ids", None)

    list_statement = copy.deepcopy(committee)
    list_statement["statement_id"] = NEW_LIST_STATEMENT_ID
    list_statement["object_candidate_id"] = LISTS_CANDIDATE_ID
    list_statement["predicate"] = "selection_lists_drawn_up_reported"
    list_statement["original_quote"] = "lists were being drawn"
    list_q = list_statement["qualifiers"]
    list_q["claim"] = "Haskell says working lists were being drawn up in the St Peter's altarpiece selection process."
    list_q["qualification"] = (
        "The phrase continues at L20 as 'up and amended'. The individual list documents and their entries are not identified."
    )
    list_q["relation_candidate_note"] = (
        "Link the source-named working-list group; its title, entries, and completeness remain unknown."
    )
    list_q["mentioned_candidate_ids"] = ["cand-4306", LISTS_CANDIDATE_ID]
    list_q["related_statement_ids"] = list_related
    list_q.pop("linked_statement_ids", None)

    continuation = statement_by_id[LISTS_CONTINUATION_ID]
    continuation["object_candidate_id"] = LISTS_CANDIDATE_ID
    continuation["predicate"] = "selection_lists_amended_reported"
    continuation_q = continuation.setdefault("qualifiers", {})
    continuation_q["claim"] = "Haskell says the working lists in the St Peter's altarpiece selection process were amended."
    continuation_q["qualification"] = (
        "This page-turn fragment continues the lists described as being drawn up at L17; the list documents and entries remain unspecified."
    )
    continuation_q["relation_candidate_note"] = (
        "Reuse the same open working-list group introduced at L17; the continuation supplies no additional list identity or entries."
    )
    continuation_q.pop("open_endpoint_reason", None)
    continuation_q["mentioned_candidate_ids"] = ["cand-4306", LISTS_CANDIDATE_ID]
    if continuation_q.get("continuation_of_statement_id") != COMMITTEE_ID:
        raise SystemExit("unexpected prior continuation target")
    continuation_q["continuation_of_statement_id"] = NEW_LIST_STATEMENT_ID
    old_related = list(continuation_q.get("related_statement_ids") or [])
    if COMMITTEE_ID not in old_related:
        raise SystemExit("expected prior statement link on the list continuation")
    continuation_q["related_statement_ids"] = list(
        dict.fromkeys(NEW_LIST_STATEMENT_ID if item == COMMITTEE_ID else item for item in old_related)
    )

    updated_rows: list[dict] = []
    for row in original_rows:
        updated_rows.append(row)
        if row.get("statement_id") == COMMITTEE_ID:
            updated_rows.append(list_statement)
    if len({row["statement_id"] for row in updated_rows}) != len(updated_rows):
        raise SystemExit("statement IDs not unique after prepared update")

    before_open = open_endpoint_counts(before_rows)
    after_open = open_endpoint_counts(updated_rows)
    true_before = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in before_rows)
    true_after = sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in updated_rows)
    if before_open != (516, 338, 65, 113) or after_open != (513, 336, 64, 113):
        raise SystemExit(f"unexpected open-endpoint counts: {before_open} -> {after_open}")
    if true_before != 10378 or true_after != 10379:
        raise SystemExit(f"unexpected relation-candidate counts: {true_before} -> {true_after}")
    if (len(candidate_rows), len(mention_rows), len(updated_rows)) != (12278, 26470, 15115):
        raise SystemExit("unexpected projected table counts")

    updated_candidates = write_csv(candidate_bytes, candidate_headers, candidate_rows)
    updated_mentions = write_csv(mention_bytes, mention_headers, mention_rows)
    line_ending = "\r\n" if b"\r\n" in statement_bytes else "\n"
    updated_statements = line_ending.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated_rows
    ).encode("utf-8") + line_ending.encode("ascii")
    return {
        CANDIDATES: updated_candidates,
        MENTIONS: updated_mentions,
        STATEMENTS: updated_statements,
    }, spans


def apply(updates: dict[Path, bytes]) -> None:
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("recovery backup already exists")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"file changed after preview: {path.relative_to(ROOT)}")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    temporary: dict[Path, Path] = {}
    written: list[Path] = []
    try:
        for path, data in updates.items():
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
                temp_path = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            temporary[path] = temp_path
        for path, temp_path in temporary.items():
            os.replace(temp_path, path)
            written.append(path)
    except Exception:
        for path in reversed(written):
            shutil.copy2(BACKUPS[path], path)
        raise
    finally:
        for temp_path in temporary.values():
            if temp_path.exists():
                temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updates, spans = build()
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {sha(path.read_bytes())} -> {sha(data)}")
    print("New candidates: cand-12298 (untyped participant group), cand-12299 (archive letters), cand-12300 (archive working lists).")
    print("Updated 3 open relations and split the combined letters/lists statement into separate claims.")
    print("Spans: " + ", ".join(f"{surface} [{a},{b})" for surface, (a, b) in spans.items()))
    print("Open endpoints: 516 -> 513; projected counts: 12,278 candidates, 26,470 mentions, 15,115 statements.")
    if args.apply:
        apply(updates)
        print("Applied with recovery backups.")


if __name__ == "__main__":
    main()
