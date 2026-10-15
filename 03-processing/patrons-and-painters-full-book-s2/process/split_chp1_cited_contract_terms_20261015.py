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
BIBLIOGRAPHY = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
SEGMENT_ID = "chp-1:01_CHP-1_sec_ii:l28-38"
OLD_STATEMENT_ID = "st-chp1-secii-notes-local-commissions-savini-minnitti"
NEW_STATEMENT_ID = "st-chp1-secii-notes-local-commissions-minnitti-1617"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "cafd97110d928177cbec0474eeae586e784f7208c3915ac73b199f3b918af315",
    MENTIONS: "0e28467974ae02ab8955fea35ab2189ac3cf81f058b07121515df413dce0a16d",
    STATEMENTS: "ad79caae41d5092007b23ff09ba3b7f6ca07cf13a32ef88174cac97e9e4edef7",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    BIBLIOGRAPHY: "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3",
}
NEW_CANDIDATES = {"cand-12276", "cand-12277", "cand-12278"}
NEW_MENTIONS = {
    "m-chp1-secii-gualandi-vol-iv",
    "m-chp1-secii-savini-1608-contract-terms",
    "m-chp1-secii-minnitti-1617-contract-terms",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp1-cited-contract-terms-corrected-20261015")
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


def statement_bytes(row: dict, line: bytes) -> bytes:
    ending = b"\r\n" if line.endswith(b"\r\n") else b"\n"
    return json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending


def source_span(text: str, phrase: str) -> tuple[int, int]:
    if text.count(phrase) != 1:
        raise SystemExit(f"source phrase count changed: {phrase}")
    start = text.index(phrase)
    return start, start + len(phrase)


def build() -> dict[Path, bytes]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, digest in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != digest:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    candidate_bytes = CANDIDATES.read_bytes()
    mention_bytes = MENTIONS.read_bytes()
    source_statement_bytes = STATEMENTS.read_bytes()
    candidate_headers, candidates = read_csv(candidate_bytes)
    mention_headers, mentions = read_csv(mention_bytes)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if NEW_CANDIDATES & set(candidate_by_id):
        raise SystemExit("new candidate ID already exists")
    if NEW_MENTIONS & {row["mention_id"] for row in mentions}:
        raise SystemExit("new mention ID already exists")
    if any("volume IV" in row["canonical_name"] and "Gualandi" in row["canonical_name"] for row in candidates):
        raise SystemExit("a Gualandi volume-IV citation candidate already exists")
    agnello_article = candidate_by_id.get("cand-11225", {})
    if agnello_article.get("suggested_type") != "archive" or "Un caravaggesco" not in agnello_article.get("canonical_name", ""):
        raise SystemExit("Agnello article archive candidate changed")
    gualandi_set = candidate_by_id.get("cand-11348", {})
    if gualandi_set.get("suggested_type") != "archive" or "Memorie originali" not in gualandi_set.get("canonical_name", ""):
        raise SystemExit("Gualandi bibliography-set candidate changed")

    segments = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 asset/segment mismatch")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")

    quote_savini = "1 See, for instance, the terms laid down for Saverio Savini in Gubbio in 1608 published by Gualandi,\nIV, p. 60;"
    quote_minnitti = "or for Mario Minnitti in Augusta (Sicily) in 1617, published by Giuseppe Agnello."
    for quote in (quote_savini, quote_minnitti):
        if " ".join(quote.split()) not in " ".join(text.split()):
            raise SystemExit("atomic quote no longer matches S0")

    spans = {
        "m-chp1-secii-gualandi-vol-iv": ("IV, p. 60", "cand-12276"),
        "m-chp1-secii-savini-1608-contract-terms": (
            "terms laid down for Saverio Savini in Gubbio in 1608", "cand-12277"
        ),
        "m-chp1-secii-minnitti-1617-contract-terms": (
            "or for Mario Minnitti in Augusta (Sicily) in 1617", "cand-12278"
        ),
    }
    new_mentions = []
    for mention_id, (surface, candidate_id) in spans.items():
        start, end = source_span(text, surface)
        overlaps = [
            row for row in mentions
            if row["segment_id"] == SEGMENT_ID
            and start < int(row["end_char"])
            and end > int(row["start_char"])
        ]
        if mention_id == "m-chp1-secii-gualandi-vol-iv" and overlaps:
            raise SystemExit("Gualandi volume locator unexpectedly overlaps an existing mention")
        if mention_id == "m-chp1-secii-savini-1608-contract-terms" and not any(r["candidate_id"] == "cand-2377" for r in overlaps):
            raise SystemExit("Savini name mention is missing under the archive span")
        if mention_id == "m-chp1-secii-minnitti-1617-contract-terms" and not any(r["candidate_id"] == "cand-1671" for r in overlaps):
            raise SystemExit("Minnitti name mention is missing under the archive span")
        note_by_id = {
            "m-chp1-secii-gualandi-vol-iv": "Specific Gualandi volume/page locator for the published Saverio Savini terms; the six-volume bibliography record is cand-11348.",
            "m-chp1-secii-savini-1608-contract-terms": "Source-defined published contract terms, nested around the Saverio Savini and Gubbio mentions; original record and holding are not independently identified.",
            "m-chp1-secii-minnitti-1617-contract-terms": "Source-defined published contract terms, nested around the Mario Minnitti and Augusta/Sicily mentions; preserve the source spelling Minnitti.",
        }
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note_by_id[mention_id],
        })

    new_candidates = [
        {
            "candidate_id": "cand-12276", "index_entry_id": "",
            "canonical_name": "[Gualandi], Memorie originali risguardanti le Belle Arti, volume IV (cited at p. 60)",
            "index_page_range": "", "suggested_type": "archive", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "Volume-level citation candidate for Haskell’s reference to Gualandi IV, p. 60. It belongs to the six-volume set candidate cand-11348; the cited page was not independently consulted.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L321",
        },
        {
            "candidate_id": "cand-12277", "index_entry_id": "",
            "canonical_name": "Published contract terms for Saverio Savini in Gubbio (1608; Gualandi IV, p. 60)",
            "index_page_range": "", "suggested_type": "archive", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "Haskell identifies published terms for Savini in Gubbio in 1608 and cites Gualandi IV, p. 60. This candidate denotes the cited documentary text of the terms, not an independently verified surviving original contract; commissioner, work, title, and holding are not supplied.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L321",
        },
        {
            "candidate_id": "cand-12278", "index_entry_id": "",
            "canonical_name": "Published contract terms for Mario Minnitti in Augusta, Sicily (1617; Giuseppe Agnello, 1941)",
            "index_page_range": "", "suggested_type": "archive", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "Haskell identifies published terms for Minnitti in Augusta in 1617 and cites Giuseppe Agnello; bibliography candidate cand-11225 identifies Agnello’s 1941 article. This candidate denotes the cited documentary text of the terms, not an independently verified surviving original contract; commissioner, work, exact article page, and holding are not supplied.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L321",
        },
    ]

    statement_lines = source_statement_bytes.splitlines(keepends=True)
    statement_rows = []
    target_index = None
    for line_index, line in enumerate(statement_lines):
        if line.strip():
            row = json.loads(line)
            statement_rows.append(row)
            if row.get("statement_id") == OLD_STATEMENT_ID:
                target_index = line_index
    if NEW_STATEMENT_ID in {row["statement_id"] for row in statement_rows}:
        raise SystemExit("new statement ID already exists")
    if target_index is None:
        raise SystemExit("original combined statement is missing")
    old_row = json.loads(statement_lines[target_index])
    if old_row.get("segment_id") != SEGMENT_ID or old_row.get("subject_candidate_id") not in (None, "") or old_row.get("object_candidate_id") not in (None, ""):
        raise SystemExit("original statement/source/endpoints changed")
    old_q = old_row.get("qualifiers", {})
    if old_q.get("relation_candidate") is not True or old_q.get("source_line_start") != 321 or old_q.get("source_line_end") != 322:
        raise SystemExit("original statement classification/source span changed")

    savini = dict(old_row)
    savini["subject_candidate_id"] = "cand-12277"
    savini["object_candidate_id"] = "cand-2377"
    savini["predicate"] = "has_subject"
    savini["original_quote"] = quote_savini
    savini_q = dict(old_q)
    savini_q["claim"] = "Haskell’s footnote cites published contract terms for Saverio Savini in Gubbio in 1608, published by Gualandi (vol. IV, p. 60)."
    savini_q["qualification"] = "The cited terms are mediated through Gualandi’s publication; the original document, commissioner, and commissioned work are not identified or independently verified."
    savini_q["relation_candidate_note"] = "The cited archive candidate represents the published contract terms and has Saverio Savini as its subject; it does not assert the identity of the commissioner or work."
    savini_q.pop("open_endpoint_reason", None)
    savini_q["mentioned_candidate_ids"] = ["cand-12276", "cand-12277", "cand-2377", "cand-3113", "cand-3477"]
    savini["qualifiers"] = savini_q

    minnitti = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-12278",
        "object_candidate_id": "cand-1671",
        "predicate": "has_subject",
        "qualifiers": {
            "source_line_start": 321,
            "source_line_end": 322,
            "claim": "Haskell’s footnote continues by citing published contract terms for Mario Minnitti in Augusta (Sicily) in 1617, published by Giuseppe Agnello.",
            "speaker": "Haskell’s footnotes",
            "qualification": "The bibliography identifies Agnello’s 1941 article, but the exact article page and identity or holding of any original contract are not supplied or independently verified.",
            "text_layer": "bibliographic note / evidence qualification",
            "relation_candidate": True,
            "relation_candidate_note": "The cited archive candidate represents the published contract terms and has Mario Minnitti as its subject; it does not assert the identity of the commissioner or work.",
            "mentioned_candidate_ids": ["cand-12278", "cand-1671", "cand-3107", "cand-3423", "cand-3478"],
        },
        "original_quote": quote_minnitti,
        "origin": "book",
        "source_file": old_row.get("source_file"),
    }
    statement_lines[target_index] = statement_bytes(savini, statement_lines[target_index])
    updated_statements = b"".join(statement_lines)
    ending = b"\r\n" if updated_statements.endswith(b"\r\n") else b"\n"
    separator = b"" if updated_statements.endswith((b"\n", b"\r")) else ending
    updated_statements += separator + statement_bytes(minnitti, ending)

    if len(candidates) != 12253 or len(mentions) != 26441 or len(statement_rows) != 15111:
        raise SystemExit("input table counts changed")
    result = {
        CANDIDATES: candidate_bytes,
        MENTIONS: mention_bytes,
        STATEMENTS: source_statement_bytes,
    }
    for candidate in new_candidates:
        result[CANDIDATES] = append_csv(result[CANDIDATES], candidate_headers, candidate)
    for mention in new_mentions:
        result[MENTIONS] = append_csv(result[MENTIONS], mention_headers, mention)
    result[STATEMENTS] = updated_statements
    new_candidate_count = len(read_csv(result[CANDIDATES])[1])
    new_mention_count = len(read_csv(result[MENTIONS])[1])
    new_statement_count = sum(1 for line in result[STATEMENTS].splitlines() if line.strip())
    if (new_candidate_count, new_mention_count, new_statement_count) != (12256, 26444, 15112):
        raise SystemExit("projected output counts mismatch")
    return result


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
    print("Split the combined footnote claim into Savini (1608) and Minnitti (1617) documentary-term records.")
    print("Added archive candidates cand-12276 (Gualandi IV citation), cand-12277 (Savini terms), cand-12278 (Minnitti terms).")
    print("Added three exact mentions; reused the existing Agnello article candidate cand-11225 from its bibliography entry without creating an overlapping footnote mention.")
    print("Both term-record candidates remain open and explicitly do not claim a verified original or holding.")
    print("projected candidates=12256 mentions=26444 statements=15112")
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {EXPECTED_HASHES[path]} -> {sha(data)}")
    if args.preview:
        print("preview only; no files or backups written")
        return
    apply(updates)
    print("applied with recovery backups")


if __name__ == "__main__":
    main()
