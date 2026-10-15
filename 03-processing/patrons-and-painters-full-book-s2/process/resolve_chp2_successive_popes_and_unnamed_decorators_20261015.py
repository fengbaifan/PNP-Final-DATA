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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "0dff1faa4568c502c36727f0e9d86372f31f5a652bdf6d707c57aa0abd7b2e13",
    MENTIONS: "de9d289c1b2c29d26ae32b6882e737856c3be5f6746ce89b75511f9a4a956906",
    STATEMENTS: "5d28a183eb2a386f7ed34cf17eec6309e7e286287d7d801854e88a25b53eefa6",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l65-77"
PAPAL_STATEMENT_ID = "st-chp2-seciv-l65-77-bentivoglio-family-papal-art-patronage"
DECORATION_STATEMENT_ID = "st-chp2-seciv-l65-77-borghese-palace-decoration-by-unnamed-artists"
POPES_CANDIDATE_ID = "cand-12304"
ARTISTS_CANDIDATE_ID = "cand-12305"
MENTION_IDS = {
    POPES_CANDIDATE_ID: "m-chp2-seciv-l65-77-successive-popes",
    ARTISTS_CANDIDATE_ID: "m-chp2-seciv-l65-77-borghese-palace-other-decorators",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-successive-popes-decorators-20261015")
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
    statement_rows = [json.loads(line) for line in statement_bytes.splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    if len(statement_by_id) != len(statement_rows):
        raise SystemExit("duplicate statement IDs")
    before_open = open_endpoint_counts(statement_rows)

    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if candidate_ids.intersection({POPES_CANDIDATE_ID, ARTISTS_CANDIDATE_ID}):
        raise SystemExit("planned candidate ID already exists")
    if mention_ids.intersection(MENTION_IDS.values()):
        raise SystemExit("planned mention ID already exists")
    max_candidate = max(
        int(row["candidate_id"].split("-")[1])
        for row in candidate_rows
        if row["candidate_id"].startswith("cand-")
    )
    if max_candidate != 12303:
        raise SystemExit(f"candidate sequence changed: {max_candidate}")
    for existing in candidate_rows:
        name = existing.get("canonical_name", "").casefold()
        if "succeeding popes" in name or "other decorators of the borghese palace" in name:
            raise SystemExit(f"possible duplicate group candidate: {existing['candidate_id']}")

    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 segment or source asset mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment text hash mismatch")

    surfaces = {"succeeding popes": POPES_CANDIDATE_ID, "others": ARTISTS_CANDIDATE_ID}
    spans: dict[str, tuple[int, int]] = {}
    for surface in surfaces:
        anchor = "and others" if surface == "others" else surface
        if text.count(anchor) != 1:
            raise SystemExit(f"source phrase changed or is not unique: {surface}")
        start = text.index(anchor) + len(anchor) - len(surface)
        end = start + len(surface)
        spans[surface] = (start, end)
        for row in mention_rows:
            if (
                row["segment_id"] == SEGMENT_ID
                and start < int(row["end_char"])
                and end > int(row["start_char"])
            ):
                raise SystemExit(f"source span overlaps existing mention: {row['mention_id']}")

    papal = statement_by_id.get(PAPAL_STATEMENT_ID)
    decoration = statement_by_id.get(DECORATION_STATEMENT_ID)
    if (
        not papal
        or papal.get("segment_id") != SEGMENT_ID
        or papal.get("subject_candidate_id") != "cand-4651"
        or papal.get("object_candidate_id") not in (None, "")
        or papal.get("qualifiers", {}).get("relation_candidate") is not True
        or "succeeding popes" not in papal.get("original_quote", "")
    ):
        raise SystemExit("Bentivoglio papal-art statement state changed")
    if (
        not decoration
        or decoration.get("segment_id") != SEGMENT_ID
        or decoration.get("subject_candidate_id") != "cand-0398"
        or decoration.get("object_candidate_id") not in (None, "")
        or decoration.get("qualifiers", {}).get("relation_candidate") is not True
        or "and others" not in decoration.get("original_quote", "")
    ):
        raise SystemExit("Borghese decoration statement state changed")

    candidate_rows.extend(
        [
            {
                "candidate_id": POPES_CANDIDATE_ID,
                "index_entry_id": "",
                "canonical_name": "Unnamed succeeding popes assisted by the Bentivoglio brothers in art patronage",
                "index_page_range": "",
                "suggested_type": "",
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": "Haskell refers collectively to succeeding popes whom the Bentivoglio brothers helped with art purchases and artist employment. No individual patrons, transactions, or complete membership are identified; do not reduce the group to adjacent examples Gregory XV and Urban VIII.",
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": f"{SEGMENT_ID}#L73",
            },
            {
                "candidate_id": ARTISTS_CANDIDATE_ID,
                "index_entry_id": "",
                "canonical_name": "Additional unnamed decorators of the Borghese palace",
                "index_page_range": "",
                "suggested_type": "",
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": "Haskell names Guido Reni, Tassi, and Gentileschi, then adds 'others' as further decorators. Their identities and membership are unspecified; keep this source-defined group separate from the three named decorators.",
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": f"{SEGMENT_ID}#L67",
            },
        ]
    )
    for surface, candidate_id in surfaces.items():
        start, end = spans[surface]
        mention_rows.append(
            {
                "mention_id": MENTION_IDS[candidate_id],
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(end),
                "note": "Explicit source-defined group mention; group membership and individual identities remain unspecified.",
            }
        )

    papal["object_candidate_id"] = POPES_CANDIDATE_ID
    papal_q = papal.setdefault("qualifiers", {})
    papal_q["relation_candidate_note"] = "Map the explicit collective phrase 'succeeding popes' to an open group candidate; the passage identifies no individual members or transactions."
    papal_q["mentioned_candidate_ids"] = list(
        dict.fromkeys([*(papal_q.get("mentioned_candidate_ids") or []), POPES_CANDIDATE_ID])
    )
    papal_q.pop("open_endpoint_reason", None)

    decoration["object_candidate_id"] = ARTISTS_CANDIDATE_ID
    decoration_q = decoration.setdefault("qualifiers", {})
    decoration_q["relation_candidate_note"] = "Map 'and others' to an open source-defined group of additional palace decorators, separate from the three named painters; membership remains unknown."
    decoration_q["mentioned_candidate_ids"] = list(
        dict.fromkeys([*(decoration_q.get("mentioned_candidate_ids") or []), ARTISTS_CANDIDATE_ID])
    )
    decoration_q.pop("open_endpoint_reason", None)

    after_open = open_endpoint_counts(statement_rows)
    if before_open != (511, 334, 64, 113):
        raise SystemExit(f"unexpected open-endpoint baseline: {before_open}")
    if after_open != (509, 332, 64, 113):
        raise SystemExit(f"unexpected projected open-endpoint counts: {after_open}")
    if (len(candidate_rows), len(mention_rows), len(statement_rows)) != (12283, 26474, 15116):
        raise SystemExit("unexpected projected table counts")

    updated_candidates = write_csv(candidate_bytes, candidate_headers, candidate_rows)
    updated_mentions = write_csv(mention_bytes, mention_headers, mention_rows)
    line_ending = "\r\n" if b"\r\n" in statement_bytes else "\n"
    updated_statements = line_ending.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statement_rows
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
    print("New open group candidates: cand-12304 (succeeding popes), cand-12305 (additional Borghese palace decorators).")
    print("Both source-defined group endpoints are explicit; identities and memberships remain open.")
    print("Spans: " + ", ".join(f"{surface} [{start},{end})" for surface, (start, end) in spans.items()))
    print("Open endpoints: 511 -> 509; projected counts: 12,283 candidates, 26,474 mentions, 15,116 statements.")
    if args.apply:
        apply(updates)
        print("Applied with recovery backups.")


if __name__ == "__main__":
    main()
