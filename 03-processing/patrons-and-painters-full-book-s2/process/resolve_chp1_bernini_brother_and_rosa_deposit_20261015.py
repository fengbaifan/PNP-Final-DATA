from __future__ import annotations

import argparse
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "317360dc58a1ff7ff952b209733ff093818c1c90a73d9de212406f2ef081bf18",
    MENTIONS: "67eec4d44273fc8dfa5fde7e842d2ff79fca95386bbe920f05a8529ecb4fa5a6",
    STATEMENTS: "b7300918d071593d4aeaec63cbe6c329174c2113fd4e66296ee5edb9aca0393b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp1-bernini-brother-rosa-deposit-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}
BERNINI_SEGMENT = "chp-1:01_CHP-1_sec_ii:l148-153"
ROSA_SEGMENT = "chp-1:01_CHP-1_sec_ii:l155-159"
BERNINI_STATEMENT = "st-chp1-secii-l148-153-02h"
ROSA_STATEMENT = "st-chp1-secii-l927-943-03c"
BROTHER_CANDIDATE = "cand-12279"
DEPOSIT_CANDIDATE = "cand-3155"
BROTHER_MENTION = "m-chp1-secii-bernini-fathers-brother-assistant"
DEPOSIT_MENTION = "m-chp1-secii-rosa-advance-deposit"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def append_csv(data: bytes, headers: list[str], row: dict[str, str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n")
    writer.writerow(row)
    ending = b"\r\n" if b"\r\n" in data else b"\n"
    separator = b"" if data.endswith((b"\n", b"\r")) else ending
    return data + separator + buffer.getvalue().encode("utf-8")


def write_csv(data: bytes, headers: list[str], rows: list[dict[str, str]]) -> bytes:
    line_ending = "\r\n" if b"\r\n" in data else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    return bom + buffer.getvalue().encode("utf-8")


def source_segment(segment_id: str, segment_rows: list[dict]) -> tuple[dict, str]:
    segment = next((row for row in segment_rows if row.get("segment_id") == segment_id), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit(f"S0 asset/segment mismatch: {segment_id}")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit(f"S0 segment hash mismatch: {segment_id}")
    return segment, text


def build() -> tuple[dict[Path, bytes], dict[str, int]]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    candidate_bytes = CANDIDATES.read_bytes()
    candidate_headers, candidate_rows = read_csv(candidate_bytes)
    _, mention_rows = read_csv(MENTIONS.read_bytes())
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if BROTHER_CANDIDATE in candidate_by_id or BROTHER_MENTION in mention_ids or DEPOSIT_MENTION in mention_ids:
        raise SystemExit("new candidate/mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row["candidate_id"].startswith("cand-")) != 12278:
        raise SystemExit("candidate ID sequence changed")
    deposit = candidate_by_id.get(DEPOSIT_CANDIDATE)
    if not deposit or deposit.get("candidate_origin") != "accepted-ku" or deposit.get("candidate_source_ref") != "04-knowledge/units/terms/caparra.md":
        raise SystemExit("accepted deposit/caparra term mapping changed")
    if not (ROOT / deposit["candidate_source_ref"]).is_file():
        raise SystemExit("accepted caparra card missing")

    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    bernini_segment, bernini_text = source_segment(BERNINI_SEGMENT, segment_rows)
    rosa_segment, rosa_text = source_segment(ROSA_SEGMENT, segment_rows)
    brother_surface = "his brother"
    deposit_surface = "deposit"
    if bernini_text.count(brother_surface) != 1 or "a famous sculptor who made some use of his brother as an assistant" not in bernini_text:
        raise SystemExit("Bernini-family source phrase changed")
    if rosa_text.count(deposit_surface) != 1 or "refuse to accept the deposit" not in rosa_text:
        raise SystemExit("Rosa deposit source phrase changed")
    brother_start = bernini_text.index(brother_surface)
    deposit_start = rosa_text.index(deposit_surface)
    brother_end = brother_start + len(brother_surface)
    deposit_end = deposit_start + len(deposit_surface)
    for segment_id, start, end in ((BERNINI_SEGMENT, brother_start, brother_end), (ROSA_SEGMENT, deposit_start, deposit_end)):
        if any(row["segment_id"] == segment_id and start < int(row["end_char"]) and end > int(row["start_char"]) for row in mention_rows):
            raise SystemExit(f"new mention overlaps an existing mention: {segment_id}")

    brother_candidate = {
        "candidate_id": BROTHER_CANDIDATE,
        "index_entry_id": "",
        "canonical_name": "Unidentified brother of the famous sculptor described as Bernini’s father",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says a famous sculptor, described as Bernini’s father, used his own brother as an assistant. The brother is unnamed; do not infer his personal identity.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BERNINI_SEGMENT}#L870",
    }
    brother_mention = {
        "mention_id": BROTHER_MENTION,
        "segment_id": BERNINI_SEGMENT,
        "candidate_id": BROTHER_CANDIDATE,
        "surface_form": brother_surface,
        "start_char": str(brother_start),
        "end_char": str(brother_end),
        "note": "The unnamed brother of the sculptor described as Bernini’s father; Haskell says he served as the sculptor’s assistant. Personal identity remains unknown.",
    }
    deposit_mention = {
        "mention_id": DEPOSIT_MENTION,
        "segment_id": ROSA_SEGMENT,
        "candidate_id": DEPOSIT_CANDIDATE,
        "surface_form": deposit_surface,
        "start_char": str(deposit_start),
        "end_char": str(deposit_end),
        "note": "The advance deposit Rosa refused for an unnamed commission; mapped to the existing accepted caparra term candidate.",
    }

    lines = STATEMENTS.read_bytes().splitlines(keepends=True)
    out: list[bytes] = []
    seen: set[str] = set()
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id == BERNINI_STATEMENT:
            if row.get("segment_id") != BERNINI_SEGMENT or row.get("subject_candidate_id") != "cand-11869" or row.get("object_candidate_id") not in (None, ""):
                raise SystemExit("Bernini-family endpoint state changed")
            q = dict(row.get("qualifiers", {}))
            if q.get("relation_candidate") is not True or q.get("source_line_start") != 870:
                raise SystemExit("Bernini-family relation/source anchor changed")
            q.pop("open_endpoint_reason", None)
            q["claim"] = "Haskell says the unnamed famous sculptor described as Bernini’s father used his own brother as an assistant."
            q["qualification"] = "The relative clause most naturally refers to the sculptor; his brother is represented as an unnamed person, and no personal identity is inferred."
            q["relation_candidate_note"] = "The statement connects the sculptor described as Bernini’s father to his unnamed brother in the assistant role; the brother’s identity remains unresolved."
            q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), BROTHER_CANDIDATE]))
            row["object_candidate_id"] = BROTHER_CANDIDATE
            row["qualifiers"] = q
            seen.add(statement_id)
        elif statement_id == ROSA_STATEMENT:
            if row.get("segment_id") != ROSA_SEGMENT or row.get("subject_candidate_id") != "cand-3099" or row.get("object_candidate_id") not in (None, ""):
                raise SystemExit("Rosa deposit endpoint state changed")
            q = dict(row.get("qualifiers", {}))
            if q.get("relation_candidate") is not True or q.get("source_line_start") != 932:
                raise SystemExit("Rosa deposit relation/source anchor changed")
            q.pop("open_endpoint_reason", None)
            q["qualification"] = "No particular commission or counterparty is named; the endpoint is the advance-deposit term, not a specific transaction."
            q["relation_candidate_note"] = "Rosa refused the advance deposit that Haskell describes as a usual guarantee for commissions; this links to the existing caparra term. No commission or counterparty is identified."
            q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), DEPOSIT_CANDIDATE]))
            row["object_candidate_id"] = DEPOSIT_CANDIDATE
            row["qualifiers"] = q
            seen.add(statement_id)
        ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
        out.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending if statement_id in {BERNINI_STATEMENT, ROSA_STATEMENT} else line)
    if seen != {BERNINI_STATEMENT, ROSA_STATEMENT}:
        raise SystemExit(f"target statement set mismatch: {seen}")

    mention_headers, _ = read_csv(MENTIONS.read_bytes())
    mention_rows.extend([brother_mention, deposit_mention])
    updated_mentions = write_csv(MENTIONS.read_bytes(), mention_headers, mention_rows)
    updated_candidates = append_csv(candidate_bytes, candidate_headers, brother_candidate)
    updated_statements = b"".join(out)
    counts = (len(read_csv(updated_candidates)[1]), len(read_csv(updated_mentions)[1]), sum(bool(line.strip()) for line in updated_statements.splitlines()))
    if counts != (12257, 26448, 15113):
        raise SystemExit(f"projected counts changed: {counts}")
    return {CANDIDATES: updated_candidates, MENTIONS: updated_mentions, STATEMENTS: updated_statements}, {
        "candidates": counts[0], "mentions": counts[1], "statements": counts[2]
    }


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
    updates, counts = build()
    print(f"Bernini-family relation: object -> {BROTHER_CANDIDATE}; mention {BROTHER_MENTION} [1013,1024)")
    print(f"Rosa refusal relation: object -> {DEPOSIT_CANDIDATE}; mention {DEPOSIT_MENTION} [2382,2389)")
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {EXPECTED_HASHES[path]} -> {sha(data)}")
    print(f"projected counts: {counts}; open endpoints 538 -> 536; Chapter 1 75 -> 73")
    if args.preview:
        print("preview only; no files or backups written")
        return
    apply(updates)
    print("applied with recovery backups")


if __name__ == "__main__":
    main()
