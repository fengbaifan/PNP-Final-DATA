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
    CANDIDATES: "ba3c6aa1a17a3b1bb81ffabfc2e6c2ae4a1039245810c0d7205979912b34e8d7",
    MENTIONS: "0107f6a835b98687ebef2b53fb87cfaedf44939972e118be8cb4747ac7b818f7",
    STATEMENTS: "dbeb70ac3c4dab5b462cc85317ab2c5fe55f73c596ae744f2ddad94d12fa4340",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp1-secii-footnote-endpoints-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}
SEGMENT_ID = "chp-1:01_CHP-1_sec_ii:l168-239"
ALBANI_STATEMENT = "st-chp1-secii-p13-n1-albani-1639-advance"
SACCHI_STATEMENT = "st-chp1-secii-p12-n1-sacchi-specific-modelo-for-altarpiece"
CAPARRA_CANDIDATE = "cand-3155"
SACCHI_TARGET_CANDIDATE = "cand-12280"
ALBANI_MENTION = "m-chp1-secii-albani-caparra-1639"
SACCHI_TARGET_MENTION = "m-chp1-secii-sacchi-intended-altarpiece"


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


def load_segment() -> tuple[dict, str]:
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
    mention_headers, mention_rows = read_csv(MENTIONS.read_bytes())
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if SACCHI_TARGET_CANDIDATE in candidate_by_id or {ALBANI_MENTION, SACCHI_TARGET_MENTION} & mention_ids:
        raise SystemExit("new candidate/mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row["candidate_id"].startswith("cand-")) != 12279:
        raise SystemExit("candidate ID sequence changed")
    caparra = candidate_by_id.get(CAPARRA_CANDIDATE)
    if not caparra or caparra.get("candidate_origin") != "accepted-ku" or caparra.get("candidate_source_ref") != "04-knowledge/units/terms/caparra.md":
        raise SystemExit("accepted caparra term mapping changed")
    if not (ROOT / caparra["candidate_source_ref"]).is_file():
        raise SystemExit("accepted caparra card missing")

    _, text = load_segment()
    targets = {
        ALBANI_MENTION: ("caparra", "The deposit paid to Francesco Albani in 1639; mapped to the existing accepted caparra term."),
        SACCHI_TARGET_MENTION: ("an altarpiece", "The unnamed altarpiece for which Haskell says one Sacchi modello was made; exact title and Capuchin church remain unresolved."),
    }
    spans: dict[str, tuple[int, int]] = {}
    for mention_id, (surface, _) in targets.items():
        occurrences = [i for i in range(len(text)) if text.startswith(surface, i)]
        if mention_id == ALBANI_MENTION:
            # Two caparra mentions occur in this note; use Albani's, before Mola and Ferri.
            if len(occurrences) != 2:
                raise SystemExit("caparra source phrase count changed")
            start = occurrences[0]
            if text.rfind("Francesco Albani", 0, start) < 0 or text.find("Pier Francesco Mola", start) < 0:
                raise SystemExit("Albani caparra occurrence no longer matches its context")
        else:
            if len(occurrences) != 2:
                raise SystemExit("altarpiece source phrase count changed")
            start = occurrences[0]
            if "One of these, for " + surface not in text[max(0, start - 20):start + len(surface)]:
                raise SystemExit("Sacchi altarpiece phrase no longer matches its context")
        spans[mention_id] = (start, start + len(surface))

    for mention_id, (start, end) in spans.items():
        if any(row["segment_id"] == SEGMENT_ID and start < int(row["end_char"]) and end > int(row["start_char"]) for row in mention_rows):
            raise SystemExit(f"new mention overlaps an existing mention: {mention_id}")

    sacchi_candidate = {
        "candidate_id": SACCHI_TARGET_CANDIDATE,
        "index_entry_id": "",
        "canonical_name": "Unidentified altarpiece intended for an Andrea Sacchi modello in a Roman Capuchin church",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell identifies one of Andrea Sacchi’s recorded modelli as made for an altarpiece in a Capuchin church in Rome. The altarpiece title, exact church, patron, date, and execution are not given; keep this target distinct from the modello candidate cand-11874.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L467",
    }
    new_mentions = [
        {
            "mention_id": ALBANI_MENTION,
            "segment_id": SEGMENT_ID,
            "candidate_id": CAPARRA_CANDIDATE,
            "surface_form": targets[ALBANI_MENTION][0],
            "start_char": str(spans[ALBANI_MENTION][0]),
            "end_char": str(spans[ALBANI_MENTION][1]),
            "note": targets[ALBANI_MENTION][1],
        },
        {
            "mention_id": SACCHI_TARGET_MENTION,
            "segment_id": SEGMENT_ID,
            "candidate_id": SACCHI_TARGET_CANDIDATE,
            "surface_form": targets[SACCHI_TARGET_MENTION][0],
            "start_char": str(spans[SACCHI_TARGET_MENTION][0]),
            "end_char": str(spans[SACCHI_TARGET_MENTION][1]),
            "note": targets[SACCHI_TARGET_MENTION][1],
        },
    ]

    lines = STATEMENTS.read_bytes().splitlines(keepends=True)
    out: list[bytes] = []
    seen: set[str] = set()
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in {ALBANI_STATEMENT, SACCHI_STATEMENT}:
            if row.get("segment_id") != SEGMENT_ID or row.get("object_candidate_id") not in (None, ""):
                raise SystemExit(f"statement endpoint state changed: {statement_id}")
            q = dict(row.get("qualifiers", {}))
            if q.get("relation_candidate") is not True:
                raise SystemExit(f"statement classification changed: {statement_id}")
            if statement_id == ALBANI_STATEMENT:
                if row.get("subject_candidate_id") != "cand-0021" or q.get("source_line_start") != 503:
                    raise SystemExit("Albani statement anchor changed")
                q["qualification"] = "The deposit is identified as caparra and amounts to 450 of a total 1,000 lire; the commission itself remains unnamed."
                q["relation_candidate_note"] = "Haskell says Albani received an advance under the caparra form in 1639; the specific commission is unnamed. The endpoint records the cited deposit term, not an inferred work."
                q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), CAPARRA_CANDIDATE]))
                row["object_candidate_id"] = CAPARRA_CANDIDATE
            else:
                if row.get("subject_candidate_id") != "cand-11874" or q.get("source_line_start") != 467:
                    raise SystemExit("Sacchi modello statement anchor changed")
                q["qualification"] = "The target is a source-defined unnamed altarpiece; its title and exact Capuchin church are unresolved, and it remains distinct from the modello."
                q["relation_candidate_note"] = "Haskell explicitly says one Sacchi modello was for an altarpiece in a Capuchin church in Rome. The altarpiece is recorded as an open work candidate; no title, completion, or exact church is inferred."
                q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), SACCHI_TARGET_CANDIDATE]))
                row["object_candidate_id"] = SACCHI_TARGET_CANDIDATE
            q.pop("open_endpoint_reason", None)
            row["qualifiers"] = q
            seen.add(statement_id)
            ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
            out.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            out.append(line)
    if seen != {ALBANI_STATEMENT, SACCHI_STATEMENT}:
        raise SystemExit(f"target statement set mismatch: {seen}")

    mention_rows.extend(new_mentions)
    updated_mentions = write_csv(MENTIONS.read_bytes(), mention_headers, mention_rows)
    updated_candidates = append_csv(candidate_bytes, candidate_headers, sacchi_candidate)
    updated_statements = b"".join(out)
    counts = (
        len(read_csv(updated_candidates)[1]),
        len(read_csv(updated_mentions)[1]),
        sum(bool(line.strip()) for line in updated_statements.splitlines()),
    )
    if counts != (12258, 26450, 15113):
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
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {sha(path.read_bytes())} -> {sha(data)}")
    print("Albani 1639 advance: object -> cand-3155 (accepted caparra term); mention [4050,4057)")
    print("Sacchi modello: object -> cand-12280 (unidentified altarpiece work); mention [3582,3595)")
    print(f"projected counts: {counts}; open endpoints 536 -> 534; Chapter 1 73 -> 71")
    if args.apply:
        apply(updates)
        print("applied with recovery backups")
    else:
        print("preview only; no files or backups written")


if __name__ == "__main__":
    main()
