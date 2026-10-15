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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "ccc14395839635318fa8187bf9901267ced19aaea52c6615a9190c8824e650e9",
    MENTIONS: "13700bee9acb8aa67dc37f63f0121cd679d0cfe34527c21410a82d51e0695fd1",
    STATEMENTS: "85902b3e4bb26dc00d2e53568299505154ccff730e537d952a521e18a4e6f53a",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l127-139"
STATEMENT_ID = "st-chp2-secii-l127-139-peretti-similar-plans"
CANDIDATE_ID = "cand-12297"
MENTION_ID = "m-chp2-secii-l127-139-peretti-plan"
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-peretti-plan-20261015")
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
    return subject_missing + object_missing - both_missing, object_missing - both_missing, subject_missing - both_missing, both_missing


def build() -> tuple[dict[Path, bytes], tuple[int, int]]:
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
    if any(row["candidate_id"] == CANDIDATE_ID for row in candidate_rows):
        raise SystemExit("candidate ID already exists")
    if any(row["mention_id"] == MENTION_ID for row in mention_rows):
        raise SystemExit("mention ID already exists")
    max_candidate = max(
        int(row["candidate_id"].split("-")[1])
        for row in candidate_rows
        if row["candidate_id"].startswith("cand-")
    )
    if max_candidate != 12296:
        raise SystemExit(f"candidate sequence changed: {max_candidate}")

    segments = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 segment or source asset mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment text hash mismatch")
    surface = "similar plans"
    if text.count(surface) != 1:
        raise SystemExit("source phrase changed or is not unique")
    start = text.index(surface)
    end = start + len(surface)
    for row in mention_rows:
        if row["segment_id"] == SEGMENT_ID and start < int(row["end_char"]) and end > int(row["start_char"]):
            raise SystemExit(f"source span overlaps existing mention: {row['mention_id']}")

    candidate_rows.append(
        {
            "candidate_id": CANDIDATE_ID,
            "index_entry_id": "",
            "canonical_name": "Prince Peretti's unspecified plan in the S. Maria della Concezione context",
            "index_page_range": "",
            "suggested_type": "event",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": (
                "Haskell says Prince Peretti had 'similar plans' after describing the Emperor's proposed "
                "Felice chapel and Magalotti's St Lawrence chapel and materials. The passage does not specify "
                "Peretti's exact proposal, dedication, ornamentation, or whether the plan was carried out; do "
                "not transfer either preceding example's details."
            ),
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L136",
        }
    )
    mention_rows.append(
        {
            "mention_id": MENTION_ID,
            "segment_id": SEGMENT_ID,
            "candidate_id": CANDIDATE_ID,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": "Open event candidate for Peretti's source-described plan; its exact content is not supplied.",
        }
    )

    output: list[bytes] = []
    found = False
    original_statement_rows: list[dict] = []
    for raw in STATEMENTS.read_bytes().splitlines(keepends=True):
        if not raw.strip():
            output.append(raw)
            continue
        row = json.loads(raw)
        original_statement_rows.append(copy.deepcopy(row))
        if row.get("statement_id") == STATEMENT_ID:
            q = dict(row.get("qualifiers", {}))
            if (
                row.get("segment_id") != SEGMENT_ID
                or row.get("subject_candidate_id") != "cand-1875"
                or row.get("object_candidate_id") not in (None, "")
                or q.get("relation_candidate") is not True
                or row.get("original_quote") != "Prince Peretti had similar plans."
            ):
                raise SystemExit("target statement state changed")
            row["object_candidate_id"] = CANDIDATE_ID
            q["qualification"] = (
                "Haskell says Prince Peretti had 'similar plans' in the S. Maria della Concezione context, "
                "after describing chapel initiatives by the Emperor and Magalotti. The passage does not "
                "identify Peretti's exact proposal, dedication, ornamentation, or whether it was carried out."
            )
            q["relation_candidate_note"] = (
                "Map 'similar plans' to a source-bounded open event candidate. Do not transfer the Emperor's "
                "chapel dedication or Magalotti's materials to Peretti."
            )
            q["mentioned_candidate_ids"] = list(
                dict.fromkeys([*(q.get("mentioned_candidate_ids", [])), "cand-1875", CANDIDATE_ID])
            )
            row["qualifiers"] = q
            found = True
            ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            output.append(raw)
    if not found:
        raise SystemExit("target statement not found")

    before = open_endpoint_counts(original_statement_rows)
    updated_statements = b"".join(output)
    after_rows = [json.loads(line) for line in updated_statements.decode("utf-8-sig").splitlines() if line.strip()]
    after = open_endpoint_counts(after_rows)
    if before != (517, 339, 65, 113) or after != (516, 338, 65, 113):
        raise SystemExit(f"unexpected open-endpoint counts: {before} -> {after}")
    if (len(candidate_rows), len(mention_rows), len(after_rows)) != (12275, 26467, 15114):
        raise SystemExit("unexpected projected table counts")

    updated_candidates = write_csv(candidate_bytes, candidate_headers, candidate_rows)
    updated_mentions = write_csv(mention_bytes, mention_headers, mention_rows)
    return {CANDIDATES: updated_candidates, MENTIONS: updated_mentions, STATEMENTS: updated_statements}, (start, end)


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
    updates, (start, end) = build()
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {sha(path.read_bytes())} -> {sha(data)}")
    print(
        f"Add {CANDIDATE_ID} (event) and mention {MENTION_ID} [{start},{end}); "
        f"link {STATEMENT_ID} object endpoint. Open endpoints: 517 -> 516."
    )
    print("Projected counts: 12,275 candidates, 26,467 mentions, 15,114 statements.")
    if args.apply:
        apply(updates)
        print("Applied with recovery backups.")


if __name__ == "__main__":
    main()
