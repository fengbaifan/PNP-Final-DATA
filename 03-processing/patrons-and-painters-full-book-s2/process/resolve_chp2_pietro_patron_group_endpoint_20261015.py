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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "cb1d79b826880eebf011c794be16bdbe1582efcd2bcb079a9a2be4cb6df7c575",
    MENTIONS: "b14166712644ad370c3f19afa35ee8e98653b66deaa76c07ee19ac8159841f9d",
    STATEMENTS: "22db2b8ae11c9578d29eb39c8ba0ba0757e8f29c9a2ace3b8bd825c23bd6f0ec",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l80-89"
STATEMENT_ID = "st-chp2-secii-l80-89-pietro-requested-subjects"
CANDIDATE_ID = "cand-12295"
MENTION_ID = "m-chp2-secii-l80-89-pietro-patrons"
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-pietro-patron-group-20261015")
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


def source_segment() -> str:
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 segment or source asset mismatch")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    return text


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
    if any(row["candidate_id"] == CANDIDATE_ID for row in candidate_rows) or any(row["mention_id"] == MENTION_ID for row in mention_rows):
        raise SystemExit("new candidate or mention ID already exists")
    max_id = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row["candidate_id"].startswith("cand-"))
    if max_id != 12294:
        raise SystemExit(f"candidate sequence changed: {max_id}")

    text = source_segment()
    surface = "his patrons"
    if text.count(surface) != 1:
        raise SystemExit("source phrase changed")
    start = text.index(surface)
    end = start + len(surface)
    if "would always ask his patrons for subjects" not in text[max(0, start - 50):end + 30]:
        raise SystemExit("patron-search context changed")
    if any(row["segment_id"] == SEGMENT_ID and start < int(row["end_char"]) and end > int(row["start_char"]) for row in mention_rows):
        raise SystemExit("patrons mention overlaps an existing mention")

    candidate_rows.append({
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Pietro da Cortona’s unnamed patrons from whom he requested subjects",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Pietro habitually asked his patrons for subjects. The passage does not identify or enumerate these patrons; keep this source-defined group distinct from the specifically discussed Marcello Sacchetti unless a source explicitly assigns membership.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L81",
    })
    mention_rows.append({
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": "Unnamed plural patron group from whom Haskell says Pietro asked for subjects; members are not enumerated.",
    })

    output: list[bytes] = []
    found = False
    for raw in STATEMENTS.read_bytes().splitlines(keepends=True):
        if not raw.strip():
            output.append(raw)
            continue
        row = json.loads(raw)
        if row.get("statement_id") == STATEMENT_ID:
            q = dict(row.get("qualifiers", {}))
            if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != "cand-0356" or row.get("object_candidate_id") not in (None, "") or q.get("relation_candidate") is not True:
                raise SystemExit("target statement state changed")
            row["object_candidate_id"] = CANDIDATE_ID
            q.pop("open_endpoint_reason", None)
            q["qualification"] = "Haskell describes a habitual request to an unnamed plural set of patrons; their identities, individual subjects, and exact periods are not supplied."
            q["relation_candidate_note"] = "The source explicitly names Pietro’s patrons as the group from whom he habitually requested subjects. The open group preserves the plural role without identifying members or asserting that Marcello was its only member."
            q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), CANDIDATE_ID]))
            row["qualifiers"] = q
            found = True
            ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            output.append(raw)
    if not found:
        raise SystemExit("target statement not found")

    updated_candidates = write_csv(candidate_bytes, candidate_headers, candidate_rows)
    updated_mentions = write_csv(mention_bytes, mention_headers, mention_rows)
    updated_statements = b"".join(output)
    counts = (len(candidate_rows), len(mention_rows), sum(bool(line.strip()) for line in updated_statements.splitlines()))
    if counts != (12273, 26465, 15114):
        raise SystemExit(f"projected counts changed: {counts}")
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
    print(f"Added open patron-group candidate {CANDIDATE_ID}, mention [{start},{end}), linked to {STATEMENT_ID}.")
    print("Projected counts: 12,273 candidates, 26,465 mentions, 15,114 statements; open endpoints 519 -> 518.")
    if args.apply:
        apply(updates)
        print("Applied with recovery backups.")


if __name__ == "__main__":
    main()
