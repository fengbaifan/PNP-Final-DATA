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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "611770a414b9e9c0e56ac6e8423d1337103160ba27d0a5d010ecfeffd4ce4a6e",
    MENTIONS: "4a38e79980716b992a209ceab145b8827db12cbb07ea3aa1775393df5031445b",
    STATEMENTS: "fbdf5900f515227d21b21f42a3a2835acf7dd568b4cc6755eb2697e411ca2bd6",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-l82-93-open-endpoints-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l82-93"

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12282",
        "index_entry_id": "",
        "canonical_name": "Haskell’s unspecified new era associated with Scipione’s way of life and carefree patronage",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Scipione’s way of life and carefree patronage helped bring about a new era. The preceding account describes broad changes in the arts during Paul V’s pontificate, but this phrase supplies no formal period name or exact boundaries. Keep distinct from the brief classical reaction candidate cand-4301.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L83",
    },
    {
        "candidate_id": "cand-12283",
        "index_entry_id": "",
        "canonical_name": "Cardinals, artists, retainers, and sycophants who deserted Scipione after the papal succession",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell groups the cardinals who attended Scipione’s banquets and the artists, retainers, and sycophants who thronged his halls as deserting him after the succession. Individual identities, group membership, number, and organizational identity are not supplied.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L85",
    },
    {
        "candidate_id": "cand-12284",
        "index_entry_id": "",
        "canonical_name": "Unnamed definite policy replacing the cheerful chaos of Borghese patronage",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says a definite policy replaced the cheerful chaos of Borghese patronage. The policy is not named, its content is not specified in this sentence, and no single agent is assigned; do not identify it with Agucchi, Gregory XV, or Ludovico without further evidence.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L87",
    },
    {
        "candidate_id": "cand-12285",
        "index_entry_id": "",
        "canonical_name": "Wide-tolerance period preceding Haskell’s brief classical reaction",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell describes the period preceding the brief classical reaction as one of wide tolerance lasting about twenty years. Exact calendar boundaries and the complete scope of the period are not supplied; keep distinct from the reaction candidate cand-4301.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L89",
    },
    {
        "candidate_id": "cand-12286",
        "index_entry_id": "",
        "canonical_name": "Other patrons besides the Popes and their nephews active in Rome",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell distinguishes other active and influential patrons in Rome from Popes and their nephews. The collective is not enumerated or identified as an organization; Cardinal del Monte is introduced as a named example in the following sentence, not the whole group.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L91",
    },
]

MENTION_SPECS = [
    ("m-chp2-seci-l82-93-new-era", "cand-12282", "a new era", "Haskell’s unnamed new-era phrase for the artistic change associated with Scipione’s patronage; formal period boundaries are not supplied."),
    ("m-chp2-seci-l82-93-deserting-courtiers", "cand-12283", "The cardinals who had flocked to\nScipione’s sumptuous banquets, the artists, retainers and sycophants who had thronged his halls", "The collective actors Haskell says deserted Scipione after the succession; membership remains unresolved."),
    ("m-chp2-seci-l82-93-definite-policy", "cand-12284", "a definite policy", "The unnamed policy Haskell says replaced the cheerful chaos of Borghese patronage; no single agent is inferred."),
    ("m-chp2-seci-l82-93-wide-tolerance", "cand-12285", "wide tolerance", "The source’s description of the preceding period, later characterized as about twenty years; exact boundaries remain unspecified."),
    ("m-chp2-seci-l82-93-other-patrons", "cand-12286", "Other patrons besides the Popes and their nephews", "The unnamed patron collective Haskell distinguishes from Popes and their nephews; members are not enumerated."),
]

STATEMENT_UPDATES = {
    "st-chp2-seci-l82-93-lifestyle-cultural-impact": {
        "expected_subject": "cand-0394", "expected_object": None,
        "subject": "cand-0394", "object": "cand-12282", "line": 83,
        "qualification": "The object is Haskell’s own unspecified ‘new era’ phrase; the preceding text describes broad artistic changes, but no formal period name or boundary is given.",
        "note": "Haskell interprets Scipione’s way of life and carefree patronage as helping bring about a new era. Record the source-defined periodizing phrase without treating it as a formally identified historical period.",
        "candidate": "cand-12282",
    },
    "st-chp2-seci-l82-93-court-desertion": {
        "expected_subject": None, "expected_object": "cand-0394",
        "subject": "cand-12283", "object": "cand-0394", "line": 85,
        "qualification": "The subject is Haskell’s unnamed collective of cardinals, artists, retainers, and sycophants; identities and membership remain open.",
        "note": "Haskell explicitly says the named-role collective who attended Scipione’s banquets and halls deserted him after the succession; this is a group-level claim, not individual relations.",
        "candidate": "cand-12283",
    },
    "st-chp2-seci-l82-93-borghese-policy-shift": {
        "expected_subject": "cand-4293", "expected_object": None,
        "subject": "cand-4293", "object": "cand-12284", "line": 87,
        "qualification": "The object is Haskell’s explicitly mentioned but unnamed policy; its content and responsible agent are not identified here.",
        "note": "Haskell says a definite policy replaced the cheerful chaos of Borghese patronage. The policy is retained as a source-defined open candidate; no person is assigned as its sole author or agent.",
        "candidate": "cand-12284",
    },
    "st-chp2-seci-l82-93-classic-reaction": {
        "expected_subject": None, "expected_object": "cand-4301",
        "subject": "cand-12285", "object": "cand-4301", "line": 89,
        "qualification": "The subject is Haskell’s preceding wide-tolerance period, described as lasting twenty years; its exact calendar boundaries remain unspecified.",
        "note": "Haskell places the brief classical reaction after the source-defined period of wide tolerance; preserve the sequence without inventing exact dates or membership.",
        "candidate": "cand-12285",
    },
    "st-chp2-seci-l82-93-other-patrons": {
        "expected_subject": None, "expected_object": "cand-3126",
        "subject": "cand-12286", "object": "cand-3126", "line": 91,
        "qualification": "The subject is the unnamed collective of patrons distinguished from Popes and their nephews; the following Cardinal del Monte example does not define the whole group.",
        "note": "Haskell states that other patrons besides Popes and their nephews were active and influential in Rome; preserve this source-defined group without inferring complete membership.",
        "candidate": "cand-12286",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def append_csv(data: bytes, headers: list[str], rows: list[dict[str, str]]) -> bytes:
    line_ending = "\r\n" if b"\r\n" in data else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=line_ending)
    writer.writerows(rows)
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


def load_segment() -> str:
    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit(f"S0 asset/segment mismatch: {SEGMENT_ID}")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit(f"S0 segment hash mismatch: {SEGMENT_ID}")
    return text


def build() -> tuple[dict[Path, bytes], dict[str, int], dict[str, tuple[int, int]]]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    candidate_bytes = CANDIDATES.read_bytes()
    candidate_headers, candidate_rows = read_csv(candidate_bytes)
    mention_headers, mention_rows = read_csv(MENTIONS.read_bytes())
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    new_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    new_mention_ids = {spec[0] for spec in MENTION_SPECS}
    if new_candidate_ids & candidate_by_id.keys() or new_mention_ids & mention_ids:
        raise SystemExit("new candidate/mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row["candidate_id"].startswith("cand-")) != 12281:
        raise SystemExit("candidate ID sequence changed")

    text = load_segment()
    spans: dict[str, tuple[int, int]] = {}
    for mention_id, _, surface, _ in MENTION_SPECS:
        occurrences = [i for i in range(len(text)) if text.startswith(surface, i)]
        if len(occurrences) != 1:
            raise SystemExit(f"source phrase is not unique: {mention_id}")
        start = occurrences[0]
        spans[mention_id] = (start, start + len(surface))

    # Permit only proper nesting for the known embedded Scipione mention; reject partial overlaps.
    for mention_id, (start, end) in spans.items():
        for row in mention_rows:
            if row["segment_id"] != SEGMENT_ID:
                continue
            a, b = int(row["start_char"]), int(row["end_char"])
            if start < b and end > a and not ((a <= start and end <= b) or (start <= a and b <= end)):
                raise SystemExit(f"partial mention overlap: {mention_id} with {row['mention_id']}")
    for i, (left_id, (a, b)) in enumerate(spans.items()):
        for right_id, (c, d) in list(spans.items())[i + 1:]:
            if a < d and b > c:
                raise SystemExit(f"new mentions overlap: {left_id} with {right_id}")

    new_mentions = []
    for mention_id, candidate_id, surface, note in MENTION_SPECS:
        start, end = spans[mention_id]
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    lines = STATEMENTS.read_bytes().splitlines(keepends=True)
    out: list[bytes] = []
    found: set[str] = set()
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in STATEMENT_UPDATES:
            update = STATEMENT_UPDATES[statement_id]
            q = dict(row.get("qualifiers", {}))
            if row.get("segment_id") != SEGMENT_ID or q.get("relation_candidate") is not True or q.get("source_line_start") != update["line"]:
                raise SystemExit(f"statement anchor/classification changed: {statement_id}")
            if row.get("subject_candidate_id") != update["expected_subject"] or row.get("object_candidate_id") != update["expected_object"]:
                raise SystemExit(f"statement endpoint state changed: {statement_id}")
            if update["subject"] not in candidate_by_id and update["subject"] not in new_candidate_ids:
                raise SystemExit(f"subject candidate missing: {statement_id}")
            if update["object"] not in candidate_by_id and update["object"] not in new_candidate_ids:
                raise SystemExit(f"object candidate missing: {statement_id}")
            row["subject_candidate_id"] = update["subject"]
            row["object_candidate_id"] = update["object"]
            q.pop("open_endpoint_reason", None)
            q["qualification"] = update["qualification"]
            q["relation_candidate_note"] = update["note"]
            q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), update["candidate"]]))
            row["qualifiers"] = q
            found.add(statement_id)
            ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
            out.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            out.append(line)
    if found != set(STATEMENT_UPDATES):
        raise SystemExit(f"target statement set mismatch: {found}")

    updated_candidates = append_csv(candidate_bytes, candidate_headers, NEW_CANDIDATES)
    mention_rows.extend(new_mentions)
    updated_mentions = write_csv(MENTIONS.read_bytes(), mention_headers, mention_rows)
    updated_statements = b"".join(out)
    counts = (
        len(read_csv(updated_candidates)[1]),
        len(read_csv(updated_mentions)[1]),
        sum(bool(line.strip()) for line in updated_statements.splitlines()),
    )
    if counts != (12264, 26456, 15113):
        raise SystemExit(f"projected counts changed: {counts}")
    return {CANDIDATES: updated_candidates, MENTIONS: updated_mentions, STATEMENTS: updated_statements}, {
        "candidates": counts[0], "mentions": counts[1], "statements": counts[2]
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
    updates, counts, spans = build()
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {sha(path.read_bytes())} -> {sha(data)}")
    for mention_id, (start, end) in spans.items():
        print(f"{mention_id}: [{start},{end})")
    print(f"linked 5 source-defined endpoints; projected counts {counts}; open endpoints 533 -> 528")
    if args.apply:
        apply(updates)
        print("applied with recovery backups")
    else:
        print("preview only; no files or backups written")


if __name__ == "__main__":
    main()
