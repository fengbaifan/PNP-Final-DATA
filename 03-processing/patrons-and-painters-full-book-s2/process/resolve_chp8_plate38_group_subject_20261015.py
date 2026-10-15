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
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii_plates_p232_visual-transcription:l1-1"
SEGMENT_SHA256 = "2ebff9a49e58b2aa8dbc19fd44e152bb67f5c19cc444f561fa441a0e44a5b4be"
SEGMENT_ASSET_SHA256 = "8ad8a26c7b8086289177728145cb9fa42a71e19c29278fbf241a743fa1b52405"
PDF_SHA256 = "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3"
STATEMENT_ID = "st-chp8-pl38-group-attribution"
GROUP_CANDIDATE_ID = "cand-12418"
GROUP_MENTION_ID = "m-chp8-pl38-frescoes-group"
ARTIST_MENTION_ID = "m-chp8-pl38-ricci-heading"
EXPECTED_HASHES = {
    "statements": "8b7ce737d0be8f209faf70fe70a3707b8a493c047e75d95e25483c60ec7605ea",
    "mentions": "f011fb50c45c9860995a051ab89f2f7c007021b435a4702605c95d68892612e1",
    "candidates": "f747ae5276606ece4408a284609a4bbc5cd2e968ef2142e27a6e999197cc7c98",
}
BACKUP_SUFFIX = ".bak-s2-chp8-pl38-group-subject-20261015"
TEMP_SUFFIX = ".tmp-s2-chp8-pl38-group-subject-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def csv_rows(raw: bytes) -> tuple[bool, list[str], list[dict[str, str]]]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return bom, list(reader.fieldnames or []), list(reader)


def patch_csv(raw: bytes, key: str, additions: list[dict[str, str]]) -> bytes:
    bom, fields, parsed = csv_rows(raw)
    ids = [row.get(key, "") for row in parsed]
    if not fields or len(ids) != len(set(ids)) or any(set(row) != set(fields) for row in additions):
        raise ValueError(f"Invalid {key} table schema or duplicate IDs.")
    if any(row[key] in set(ids) for row in additions):
        raise ValueError(f"A planned {key} ID already exists.")
    text = raw.decode("utf-8-sig")
    physical = text.splitlines(keepends=True)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != fields or reader.line_num != 1:
        raise ValueError("CSV header is changed or multiline.")
    previous_line = reader.line_num
    output = [physical[0]]
    for _row in reader:
        end_line = reader.line_num
        chunk = "".join(physical[previous_line:end_line])
        if not chunk:
            raise ValueError("Could not map CSV record to physical source lines.")
        output.append(chunk)
        previous_line = end_line
    for row in additions:
        stream = io.StringIO(newline="")
        csv.DictWriter(stream, fieldnames=fields, lineterminator=newline).writerow(row)
        output.append(stream.getvalue())
    return (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")


def rewrite_statement(raw: bytes, updated: dict) -> bytes:
    bom = raw.startswith(b"\xef\xbb\xbf")
    output: list[str] = []
    seen = 0
    for line in raw.decode("utf-8-sig").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        if row.get("statement_id") == STATEMENT_ID:
            output.append(json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + ending)
            seen += 1
        else:
            output.append(line)
    if seen != 1:
        raise ValueError("Target statement did not occur exactly once.")
    return (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the source-defined three-fresco group needed by the Plate 38-39 attribution.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    if sha((ROOT / "02-sources/01-book/CHP-8.pdf").read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-8.pdf changed.")
    segment_matches = [row for row in jsonl(SEGMENTS.read_bytes()) if row.get("segment_id") == SEGMENT_ID]
    if len(segment_matches) != 1:
        raise ValueError("Reviewed Plate 38 source segment is missing or duplicated.")
    segment = segment_matches[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SEGMENT_ASSET_SHA256:
        raise ValueError("Reviewed Plate 38 segment metadata changed.")
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != SEGMENT_SHA256 or text != "FRESCOES BY SEBASTIANO RICCI":
        raise ValueError("Reviewed plate heading changed.")

    raw = {"statements": STATEMENTS.read_bytes(), "mentions": MENTIONS.read_bytes(), "candidates": CANDIDATES.read_bytes()}
    actual = {name: sha(data) for name, data in raw.items()}
    if actual != EXPECTED_HASHES:
        raise ValueError(f"Protected table snapshot changed: {actual}")
    statements = jsonl(raw["statements"])
    statement_matches = [r for r in statements if r.get("statement_id") == STATEMENT_ID]
    if len(statements) != 15158 or len(statement_matches) != 1:
        raise ValueError("Unexpected statement inventory or target multiplicity.")
    updated = json.loads(json.dumps(statement_matches[0], ensure_ascii=False))
    q = updated.get("qualifiers") or {}
    if (
        updated.get("segment_id") != SEGMENT_ID
        or updated.get("subject_candidate_id")
        or updated.get("object_candidate_id") != "cand-3101"
        or q.get("relation_candidate") is not True
        or updated.get("original_quote") != text
    ):
        raise ValueError("Reviewed caption statement no longer matches its open state.")
    _, _, mention_rows = csv_rows(raw["mentions"])
    _, _, candidate_rows = csv_rows(raw["candidates"])
    if len(mention_rows) != 26607 or len(candidate_rows) != 12395:
        raise ValueError("Unexpected mention or candidate inventory.")
    if any(row["mention_id"] in {GROUP_MENTION_ID, ARTIST_MENTION_ID} for row in mention_rows):
        raise ValueError("A planned plate heading mention already exists.")
    if any(row["candidate_id"] == GROUP_CANDIDATE_ID for row in candidate_rows):
        raise ValueError("The planned artwork-group candidate already exists.")

    group_candidate = {
        "candidate_id": GROUP_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Sebastiano Ricci fresco group identified as Plates 38-39 (Rape of Europa; Pan and Syrinx; Venus and Adonis)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The printed Plate 38 heading says 'Frescoes by Sebastiano Ricci' and points to Plates 38 and 39. The List of Plates identifies three works across those plates: Rape of Europa, Pan and Syrinx, and Venus and Adonis. This group candidate records the shared caption scope; the three works remain separate candidates.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L1",
    }
    artist_start = text.index("SEBASTIANO RICCI")
    mentions = [
        {
            "mention_id": GROUP_MENTION_ID,
            "segment_id": SEGMENT_ID,
            "candidate_id": GROUP_CANDIDATE_ID,
            "surface_form": "FRESCOES",
            "start_char": "0",
            "end_char": "8",
            "note": "Plural heading for the three Ricci frescoes included under Plates 38-39.",
        },
        {
            "mention_id": ARTIST_MENTION_ID,
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-3101",
            "surface_form": "SEBASTIANO RICCI",
            "start_char": str(artist_start),
            "end_char": str(artist_start + len("SEBASTIANO RICCI")),
            "note": "Artist named in the printed group attribution heading.",
        },
    ]
    updated["subject_candidate_id"] = GROUP_CANDIDATE_ID
    q["claim"] = "The Plate 38-39 heading attributes the three listed frescoes to Sebastiano Ricci."
    q["qualification"] = "The heading's scope is resolved by its cross-reference to Plates 38 and 39 and the List of Plates; the three works remain individually represented."
    q["mentioned_candidate_ids"] = [GROUP_CANDIDATE_ID, "cand-3101", "cand-4097", "cand-4096", "cand-4098"]
    q["relation_candidate_note"] = "The printed group heading explicitly attributes its plural fresco group to Ricci; the referenced plates and List of Plates resolve the group to three separately identified works."
    updated["qualifiers"] = q

    statement_out = rewrite_statement(raw["statements"], updated)
    mention_out = patch_csv(raw["mentions"], "mention_id", mentions)
    candidate_out = patch_csv(raw["candidates"], "candidate_id", [group_candidate])
    after_statements = jsonl(statement_out)
    open_rows = [r for r in after_statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 359 or no_reason != 36:
        raise ValueError(f"Unexpected open endpoint state: {len(open_rows)}, no_reason={no_reason}")
    if len(csv_rows(mention_out)[2]) != 26609 or len(csv_rows(candidate_out)[2]) != 12396:
        raise ValueError("Unexpected post-edit mention or candidate inventory.")
    for row in mentions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if end - start != len(row["surface_form"]) or text[start:end] != row["surface_form"]:
            raise ValueError(f"Mention span mismatch: {row['mention_id']}")

    outputs = {STATEMENTS: statement_out, MENTIONS: mention_out, CANDIDATES: candidate_out}
    print("reviewed=CHP-8 printed Plate 38 / PDF physical page 36; cross-reference and List of Plates entries 38-39 checked")
    print("change=add source-defined three-fresco group as caption subject and register artist/group mentions")
    print("open_endpoints=360->359; no_reason_open=37->36; candidates=12395->12396; mentions=26607->26609")
    for path, data in outputs.items():
        print(f"{path.name} sha256 {sha(path.read_bytes())}->{sha(data)}")
    if args.preview:
        return 0
    requested = {
        "statements": args.expected_statements_sha256,
        "mentions": args.expected_mentions_sha256,
        "candidates": args.expected_candidates_sha256,
    }
    if requested != actual:
        raise ValueError("Apply requires the three input hashes printed by this preview.")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    temps = {path: path.with_name(path.name + TEMP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()) or any(path.exists() for path in temps.values()):
        raise FileExistsError("Recovery copy or temporary table already exists.")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, data in outputs.items():
            temps[path].write_bytes(data)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in backups.items():
            shutil.copy2(backup, path)
        raise
    print("applied=yes")
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.name}:{sha(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
