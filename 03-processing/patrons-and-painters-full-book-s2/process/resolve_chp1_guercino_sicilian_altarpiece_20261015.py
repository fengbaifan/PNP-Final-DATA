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
SEGMENT_ID = "chp-1:01_CHP-1_sec_ii:l28-38"
STATEMENT_ID = "st-chp1-secii-l28-38-02"
CANDIDATE_ID = "cand-12275"
MENTION_ID = "m-chp1-secii-guercino-sicilian-altarpiece"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "6a408ce997a3e2bba4eb307d1048ced34fabd57e98df47038114e9578d7213dd",
    MENTIONS: "154e044abc3530eaf51f0f10b03bb8599a3d370847738423d9c47d7c6c927a9b",
    STATEMENTS: "c9dc60fceadb1f7d06c9b3ac2cbad07ccdc9a48c80484abe5a14ca4fa9eb8658",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp1-guercino-altarpiece-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def append_csv(data: bytes, headers: list[str], row: dict[str, str]) -> bytes:
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n").writerow(row)
    ending = b"\r\n" if b"\r\n" in data else b"\n"
    separator = b"" if data.endswith((b"\n", b"\r")) else ending
    return data + separator + buffer.getvalue().encode("utf-8")


def build() -> dict[Path, bytes]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, digest in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != digest:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    candidate_bytes = CANDIDATES.read_bytes()
    mention_bytes = MENTIONS.read_bytes()
    statement_bytes = STATEMENTS.read_bytes()
    candidate_headers, candidate_rows = read_csv(candidate_bytes)
    mention_headers, mention_rows = read_csv(mention_bytes)
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if CANDIDATE_ID in candidate_ids or MENTION_ID in mention_ids:
        raise SystemExit("new candidate or mention ID already exists")

    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 asset/segment mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(source_text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    surface = "altarpiece"
    if source_text.count(surface) != 1:
        raise SystemExit("expected one exact work mention in the S0 segment")
    start = source_text.index(surface)
    end = start + len(surface)
    if any(
        row["segment_id"] == SEGMENT_ID
        and start < int(row["end_char"])
        and end > int(row["start_char"])
        for row in mention_rows
    ):
        raise SystemExit("new work mention overlaps an existing mention")

    lines = statement_bytes.splitlines(keepends=True)
    target_index = None
    target = None
    for index, line in enumerate(lines):
        if line.strip():
            row = json.loads(line)
            if row.get("statement_id") == STATEMENT_ID:
                target_index, target = index, row
                break
    if target is None or target.get("segment_id") != SEGMENT_ID:
        raise SystemExit("target statement/source mapping changed")
    if target.get("subject_candidate_id") != "cand-1258" or target.get("object_candidate_id") not in (None, ""):
        raise SystemExit("target endpoint state changed")
    qualifiers = dict(target.get("qualifiers", {}))
    if qualifiers.get("relation_candidate") is not True or qualifiers.get("source_line_start") != 295:
        raise SystemExit("target statement classification/source line changed")
    if "monastery" not in qualifiers.get("claim", "") or "1665" not in qualifiers.get("claim", ""):
        raise SystemExit("target claim is not the expected 1665 commission")

    candidate = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Unidentified altarpiece Guercino was required to paint for a monastery in Sicily (1665)",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "A specific altarpiece described in Haskell’s account of a 1665 assignment for Guercino. "
            "The brief specifies figures and composition, but the commissioner, monastery, formal title, "
            "and subsequent completion are not identified. Haskell reports the episode through quoted correspondence."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L295",
    }
    mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": "The specific altarpiece in Haskell’s 1665 Guercino account; its title, commissioner, monastery, and completion status are unknown.",
    }
    updated = dict(target)
    updated["object_candidate_id"] = CANDIDATE_ID
    qualifiers.pop("open_endpoint_reason", None)
    qualifiers["relation_candidate_note"] = (
        "Haskell reports that in 1665 Guercino was required to paint this specific altarpiece and asked follow-up "
        "questions about its brief. The work is represented as an open candidate; its commissioner, monastery, "
        "formal title, and completion status remain unknown."
    )
    mentioned = list(qualifiers.get("mentioned_candidate_ids", []))
    if CANDIDATE_ID not in mentioned:
        mentioned.append(CANDIDATE_ID)
    qualifiers["mentioned_candidate_ids"] = mentioned
    updated["qualifiers"] = qualifiers
    ending = b"\r\n" if lines[target_index].endswith(b"\r\n") else b"\n"
    lines[target_index] = json.dumps(updated, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending
    updated_statement_bytes = b"".join(lines)

    if len(candidate_rows) != 12252 or len(mention_rows) != 26440:
        raise SystemExit("input table counts changed")
    out = {
        CANDIDATES: append_csv(candidate_bytes, candidate_headers, candidate),
        MENTIONS: append_csv(mention_bytes, mention_headers, mention),
        STATEMENTS: updated_statement_bytes,
    }
    new_counts = {path: len(read_csv(data)[1]) for path, data in out.items() if path in (CANDIDATES, MENTIONS)}
    if new_counts != {CANDIDATES: 12253, MENTIONS: 26441}:
        raise SystemExit(f"projected table counts mismatch: {new_counts}")
    return out


def apply(updates: dict[Path, bytes]) -> None:
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("recovery backup already exists")
    for path, digest in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != digest:
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
    updates = build()
    print(f"{STATEMENT_ID}: object -> {CANDIDATE_ID} (open work candidate)")
    print(f"candidate: {CANDIDATE_ID} | work | specific 1665 altarpiece; title and completion status unknown")
    print(f"mention: {MENTION_ID} | exact surface 'altarpiece' | chars {updates[MENTIONS].decode('utf-8-sig').splitlines()[-1]}")
    print(f"projected candidates=12253 mentions=26441 statements=15111")
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {EXPECTED_HASHES[path]} -> {sha(data)}")
    if args.preview:
        print("preview only; no files or backups written")
        return
    apply(updates)
    print(f"applied with recovery backups ({next(iter(BACKUPS.values())).name} suffix)")


if __name__ == "__main__":
    main()
