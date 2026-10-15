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
    CANDIDATES: "2d7871e39b7a3039f52c2ca4a00c74fead6f77a58e014d9ae2644a04a2a6db32",
    MENTIONS: "95831ea69ca9453e9d115a9da498ecf4c0604fa9531c642aebeedd95dabd7754",
    STATEMENTS: "7a39bced1076d576ddfd6f8263983c79f1aebb2044d35e290e8d76266b5b26f0",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l3-8"
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-secii-l3-8-open-endpoints-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}
NEW_CANDIDATES = {
    "cand-12290": {
        "canonical_name": "Most of Urban VIII’s male relations just named as patrons (exact members unidentified)",
        "suggested_type": "",
        "detail": "Haskell attributes artistic patronage to ‘most’ of the men just named, without identifying the subset. Preserve this source-defined majority group without treating every named relation as a patron.",
        "line": 4,
    },
    "cand-12291": {
        "canonical_name": "Unnamed ambitious nephew of a papabile cardinal in Haskell’s reported 1635 witchcraft plot",
        "suggested_type": "person",
        "detail": "Haskell reports an ambitious nephew of an unnamed papabile cardinal in an alleged 1635 witchcraft plot against Urban VIII. The person’s name and identity are not supplied; preserve the account as reported.",
        "line": 6,
    },
    "cand-12292": {
        "canonical_name": "Unnamed papabile cardinal whose nephew is mentioned in Haskell’s 1635 plot account",
        "suggested_type": "person",
        "detail": "Haskell refers to one unnamed papabile cardinal as the uncle of the ambitious nephew in the reported 1635 plot. The cardinal’s identity is not supplied. The OCR joins ‘one papabile’; the page image confirms the spaced reading, while S0 remains unchanged.",
        "line": 6,
    },
    "cand-12293": {
        "canonical_name": "Urban VIII’s contemporaries and successors who held his enrichment to exceed reasonable limits",
        "suggested_type": "",
        "detail": "Haskell attributes this judgment to Urban VIII’s contemporaries and successors collectively. Their identities and the membership of each group are not supplied; ‘universally’ remains Haskell’s characterization.",
        "line": 6,
    },
}
NEW_MENTIONS = [
    ("m-chp2-secii-l3-8-patronage-majority", "cand-12290", "Most of these men", "Haskell’s majority wording defines a source-specific group; the exact patron subset is unidentified."),
    ("m-chp2-secii-l3-8-ambitious-nephew", "cand-12291", "ambitious nephew", "Unnamed individual described as the actor in Haskell’s reported plot account."),
    ("m-chp2-secii-l3-8-papabile-cardinal", "cand-12292", "onepapabile cardinal", "The S0 OCR joins ‘one papabile’; the page image confirms the spaced reading. Mention span follows S0; source asset is unchanged."),
    ("m-chp2-secii-l3-8-contemporaries-successors", "cand-12293", "his contemporaries and by his successors", "Collective audience to whom Haskell attributes the judgment; individual members are not identified."),
]
TARGET_SUBJECT_UPDATES = {
    "st-chp2-sec-ii-l3-8-family-art-patronage": ("cand-3126", "cand-12290"),
    "st-chp2-sec-ii-l3-8-urban-excess-reputation": ("cand-3104", "cand-12293"),
    "st-chp2-sec-ii-l3-8-witchcraft-plot": ("cand-3104", "cand-12291"),
}
NEW_STATEMENT_ID = "st-chp2-sec-ii-l3-8-nephew-kinship-cardinal"


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


def load_segment() -> str:
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit(f"S0 asset/segment mismatch: {SEGMENT_ID}")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit(f"S0 segment hash mismatch: {SEGMENT_ID}")
    return text


def build() -> tuple[dict[Path, bytes], dict[str, int], list[tuple[str, int, int]]]:
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
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    mentions = {row["mention_id"]: row for row in mention_rows}
    if set(NEW_CANDIDATES) & set(candidates) or any(row[0] in mentions for row in NEW_MENTIONS):
        raise SystemExit("new candidate or mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row["candidate_id"].startswith("cand-")) != 12289:
        raise SystemExit("candidate ID sequence changed")
    if any(row.get("statement_id") == NEW_STATEMENT_ID for row in (json.loads(x) for x in STATEMENTS.read_text(encoding="utf-8").splitlines() if x.strip())):
        raise SystemExit("new statement ID already exists")

    text = load_segment()
    found_spans: list[tuple[str, int, int]] = []
    for mention_id, candidate_id, surface, note in NEW_MENTIONS:
        count = text.count(surface)
        if count != 1:
            raise SystemExit(f"source phrase count for {mention_id}: {count}")
        start = text.index(surface)
        end = start + len(surface)
        if any(row["segment_id"] == SEGMENT_ID and start < int(row["end_char"]) and end > int(row["start_char"]) for row in mention_rows):
            raise SystemExit(f"mention overlaps existing span: {mention_id}")
        found_spans.append((mention_id, start, end))

    candidate_rows_new = []
    for candidate_id, spec in NEW_CANDIDATES.items():
        candidate_rows_new.append({
            "candidate_id": candidate_id,
            "index_entry_id": "",
            "canonical_name": spec["canonical_name"],
            "index_page_range": "",
            "suggested_type": spec["suggested_type"],
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": spec["detail"],
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{spec['line']}",
        })
    candidate_rows.extend(candidate_rows_new)

    span_map = {mention_id: (start, end) for mention_id, start, end in found_spans}
    for mention_id, candidate_id, surface, note in NEW_MENTIONS:
        start, end = span_map[mention_id]
        mention_rows.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    statement_lines = STATEMENTS.read_bytes().splitlines(keepends=True)
    output: list[bytes] = []
    found_statements: set[str] = set()
    for line in statement_lines:
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in TARGET_SUBJECT_UPDATES:
            expected_object, new_subject = TARGET_SUBJECT_UPDATES[statement_id]
            q = dict(row.get("qualifiers", {}))
            if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") not in (None, "") or row.get("object_candidate_id") != expected_object or q.get("relation_candidate") is not True:
                raise SystemExit(f"target statement state changed: {statement_id}")
            row["subject_candidate_id"] = new_subject
            q.pop("open_endpoint_reason", None)
            if statement_id == "st-chp2-sec-ii-l3-8-family-art-patronage":
                q["qualification"] = "The source refers to most, not necessarily all, of the male relations just named; it does not identify which individuals formed the patronage subset or name particular contributions."
                q["relation_candidate_note"] = "Haskell attributes some of Rome’s greatest achievements to a source-defined majority of the men just named. The open collective preserves the word ‘most’ without assigning patronage to every named relation."
            elif statement_id == "st-chp2-sec-ii-l3-8-urban-excess-reputation":
                q["qualification"] = "The judgment is attributed to Urban VIII’s contemporaries and successors collectively; their identities are not supplied. ‘Universally’ remains Haskell’s characterization, not an independently established measure."
                q["relation_candidate_note"] = "Haskell attributes the reported judgment to the collective groups of Urban VIII’s contemporaries and successors. Their membership remains unidentified; the candidate does not convert the author’s ‘universally’ into a verified consensus."
            else:
                q["qualification"] = "Haskell reports an alleged plot by an unnamed ambitious nephew of an unnamed papabile cardinal; preserve the account as reported, not independently verified."
                q["relation_candidate_note"] = "The source identifies the reported actor as an unnamed ambitious nephew and Urban VIII as the target. The actor’s identity remains open; the separate kinship statement preserves his relationship to the unnamed cardinal."
            q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), new_subject]))
            if statement_id == "st-chp2-sec-ii-l3-8-witchcraft-plot":
                q["mentioned_candidate_ids"] = list(dict.fromkeys([*q["mentioned_candidate_ids"], "cand-12292"]))
            row["qualifiers"] = q
            found_statements.add(statement_id)
            ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            output.append(line)
    if found_statements != set(TARGET_SUBJECT_UPDATES):
        raise SystemExit(f"target statement set mismatch: {found_statements}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    quote = source_lines[5]
    if "ambitious nephew of onepapabile cardinal" not in quote or "in 1635" not in quote:
        raise SystemExit("witchcraft source quotation changed")
    new_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-12291",
        "object_candidate_id": "cand-12292",
        "predicate": "kin_of",
        "qualifiers": {
            "source_line_start": 6,
            "source_line_end": 6,
            "claim": "Haskell describes the unnamed ambitious nephew in the reported 1635 plot as kin to an unnamed papabile cardinal, specifically as that cardinal’s nephew.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "The source gives the specific role ‘nephew of’; the controlled relation vocabulary has no nephew_of type, so kin_of is used with the role preserved. Both people remain unidentified, and the plot account remains attributed.",
            "print_page": 31,
            "role": "nephew of",
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly states the kinship. Use the controlled kin_of type and retain the more specific nephew role; neither person is identified by name.",
            "mentioned_candidate_ids": ["cand-12291", "cand-12292"],
        },
        "original_quote": "the ambitious nephew of onepapabile cardinal",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    }
    output.append(json.dumps(new_statement, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n")
    updated_statements = b"".join(output)

    updated_candidates = write_csv(candidate_bytes, candidate_headers, candidate_rows)
    updated_mentions = write_csv(mention_bytes, mention_headers, mention_rows)
    counts = (len(candidate_rows), len(mention_rows), sum(bool(line.strip()) for line in updated_statements.splitlines()))
    if counts != (12271, 26463, 15114):
        raise SystemExit(f"projected counts changed: {counts}")
    return {CANDIDATES: updated_candidates, MENTIONS: updated_mentions, STATEMENTS: updated_statements}, {
        "candidates": counts[0], "mentions": counts[1], "statements": counts[2]
    }, found_spans


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
    print("Added source-defined patronage/audience groups and two unnamed persons; linked three resolvable subjects.")
    print(f"Added exact mention spans: {spans}")
    print(f"Added kin_of statement {NEW_STATEMENT_ID}; political posts and great wealth remain open because the source does not name a grantor, office, or wealth source.")
    print(f"Projected counts: {counts}; open endpoints 524 -> 521")
    if args.apply:
        apply(updates)
        print("Applied with recovery backups.")


if __name__ == "__main__":
    main()
