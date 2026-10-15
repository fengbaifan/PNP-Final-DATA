from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l323-445"
STATEMENT_ID = "st-chp9-p259-note3-visconti-letter-citation"
BACKUP_SUFFIX = "bak-s2-chp9-p259-note3-publication-endpoint-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "ef66e4641ba258dd12bd3d4c405d18dff497f15d176b75d6ef14539398a542fa",
    "mentions.csv": "ffe9a58e9394e5911b9b79081268f5e06c03bb1b837976ecd6672b1cb5320b4e",
    "book-statements.jsonl": "5b95502ed9bebd1af1fa24a13c9897f6b8d259852ce6e210cedabc88579ff0f7",
}
EXPECTED_SEGMENT_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
NEW_CANDIDATE = {
    "candidate_id": "cand-12386",
    "canonical_name": "Unidentified Arslan publication containing the Visconti-Ligari letter (1952, p. 63)",
    "suggested_type": "archive",
    "detail": "The p.259 note locates Pietro Visconti's letter to Gian Pietro Ligari in a publication attributed to Arslan (1952), p.63. The note does not provide the publication title, Arslan's full name or role, or the full publication details; neither the letter nor publication was independently consulted.",
}
NEW_MENTION_ID = "m-chp9-p259-arslan-1952-publication"
MENTION_SURFACE = "published by Arslan, 1952, p. 63"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open(row: dict[str, object]) -> bool:
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [row for row in rows if is_open(row)]
    object_only = sum(bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id") for row in opens)
    subject_only = sum(not row.get("subject_candidate_id") and bool(row.get("object_candidate_id")) for row in opens)
    both = sum(not row.get("subject_candidate_id") and not row.get("object_candidate_id") for row in opens)
    return len(opens), object_only, subject_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    current_hashes = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if expected.startswith("PLACEHOLDER") or digest(current_hashes[name]) != expected:
            raise ValueError(f"Input table changed since this batch was prepared: {name}")

    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    segment = next(row for row in segments if row["segment_id"] == SEGMENT_ID)
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("p.259 footnote source segment changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source_line = source_lines[390]
    if source_line.count(MENTION_SURFACE) != 1:
        raise ValueError("Expected unique cited-publication phrase is absent from p.259 note 3")

    candidate_ids = {row["candidate_id"] for row in candidates}
    if NEW_CANDIDATE["candidate_id"] in candidate_ids or any(row["canonical_name"] == NEW_CANDIDATE["canonical_name"] for row in candidates):
        raise ValueError("Publication candidate ID or name already exists")
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if NEW_MENTION_ID in mention_by_id:
        raise ValueError("Publication mention already exists")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    if endpoint_counts(rows) != (420, 263, 53, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {endpoint_counts(rows)}")
    index = {row["statement_id"]: row for row in rows}
    statement = index.get(STATEMENT_ID)
    if statement is None or not is_open(statement) or statement.get("subject_candidate_id") != "cand-8466":
        raise ValueError("Expected open Visconti-letter citation statement is absent or changed")

    line_no = 391
    segment_start = int(segment["line_start"])
    line_base = sum(len(text) + 1 for text in source_lines[segment_start - 1 : line_no - 1])
    mention_start = line_base + source_line.index(MENTION_SURFACE)
    new_mention = {
        "mention_id": NEW_MENTION_ID, "segment_id": SEGMENT_ID, "candidate_id": NEW_CANDIDATE["candidate_id"],
        "surface_form": MENTION_SURFACE, "start_char": str(mention_start),
        "end_char": str(mention_start + len(MENTION_SURFACE)),
        "note": "Bibliographic locator for the cited 1952 publication containing the Visconti-Ligari letter; title and Arslan's role remain unspecified.",
    }

    statement["object_candidate_id"] = NEW_CANDIDATE["candidate_id"]
    statement["predicate"] = "letter_located_in_publication_cited_as_arslan_1952_page_63"
    qualifiers = statement["qualifiers"]
    qualifiers["claim"] = "Haskell's note identifies Pietro Visconti's letter to Gian Pietro Ligari as published by Arslan in 1952, page 63."
    qualifiers["mentioned_candidate_ids"] = list(dict.fromkeys((qualifiers.get("mentioned_candidate_ids") or []) + [NEW_CANDIDATE["candidate_id"]]))
    qualifiers["relation_candidate_note"] = "The citation names the letter and supplies a publication locator, but not the publication title or Arslan's full identity or role. The source-defined publication candidate preserves the citation without adding bibliographic details."
    qualifiers.pop("open_endpoint_reason", None)

    after_counts = endpoint_counts(rows)
    if after_counts != (419, 262, 53, 104):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")
    candidate_row = {
        "candidate_id": NEW_CANDIDATE["candidate_id"], "index_entry_id": "",
        "canonical_name": NEW_CANDIDATE["canonical_name"], "index_page_range": "",
        "suggested_type": NEW_CANDIDATE["suggested_type"], "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": NEW_CANDIDATE["detail"], "exclude_reason": "",
        "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L391",
    }
    candidate_after = append_rows(candidate_raw, candidate_fields, [candidate_row])
    mention_after = append_rows(mention_raw, mention_fields, [new_mention])
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")

    print("closed=Visconti letter -> source-defined Arslan 1952 publication locator")
    print("retained_uncertainty=publication title and Arslan's full identity/role")
    print(f"candidates={len(candidates)}->{len(candidates) + 1}; mentions={len(mentions)}->{len(mentions) + 1}; statements={len(rows)}")
    print(f"open_endpoints={endpoint_counts([json.loads(line) for line in statement_raw.decode('utf-8').splitlines() if line.strip()])}->{after_counts}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} sha256 {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = ((CANDIDATES, candidate_after), (MENTIONS, mention_after), (STATEMENTS, statement_after))
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temporary = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temporary.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temporary, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temporary, data in pairs:
            temporary.write_bytes(data)
        for path, backup, temporary, _ in pairs:
            temporary.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temporary, _ in pairs:
            if temporary.exists():
                temporary.unlink()
        for path, backup in replaced:
            shutil.copy2(backup, path)
        raise
    for path, backup, _, _ in pairs:
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
