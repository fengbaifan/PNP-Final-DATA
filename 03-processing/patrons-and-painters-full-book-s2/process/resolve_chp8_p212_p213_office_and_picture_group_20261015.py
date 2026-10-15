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
SOURCE = ROOT / "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l126-157"
OFFICE_STATEMENT_ID = "st-chp8-p212-n5-panciatichi-office"
PICTURES_STATEMENT_ID = "st-chp8-p213-n1-more-del-rosso-pictures"
LETTER_STATEMENT_ID = "st-chp8-p212-n5-archivio-letter-content"
OFFICE_CANDIDATE_ID = "cand-12349"
PICTURE_GROUP_CANDIDATE_ID = "cand-12350"
OFFICE_MENTION_ID = "m-chp8-p212-primo-segretario-office"
PICTURE_GROUP_MENTION_ID = "m-chp8-p213-del-rosso-picture-group"
OFFICE_SURFACE = "Primo Segretario"
PICTURE_GROUP_SURFACE = "pictures by Ribera, Preti and Paceco de Rosa"
BACKUP_SUFFIX = "bak-s2-chp8-p212-p213-open-endpoints-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "bf6ac1f8a45a04995907a614d875e5ff2e1611941fc46e332091a7cf086bb81d",
    "mentions.csv": "4f8edd898bf3261bf112f8ad9c580f81c3683dfb034e15b8e091094e37b43029",
    "book-statements.jsonl": "6c8c17a6cf2eb1b175f35ab77a086183d50b459c72e4dd5921f13395b252c257",
}
EXPECTED_SEGMENT_HASH = "0ecf16986f97d6044129c91ccafde31ac1ebe6dadef71c79a6d4691c10d90b4c"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=fields, lineterminator=newline.decode("ascii"), extrasaction="raise"
    )
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open_relation(row: dict[str, object]) -> bool:
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [row for row in rows if is_open_relation(row)]
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
    actual = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(actual[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    segment = next(
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Source segment hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(
        source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])]
    )
    offsets: dict[str, tuple[int, int]] = {}
    for surface in (OFFICE_SURFACE, PICTURE_GROUP_SURFACE):
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise ValueError(f"Source phrase missing or repeated: {surface}")
        offsets[surface] = (start, start + len(surface))

    candidate_ids = {row["candidate_id"] for row in candidates}
    if OFFICE_CANDIDATE_ID in candidate_ids or PICTURE_GROUP_CANDIDATE_ID in candidate_ids:
        raise ValueError("Planned candidate ID already exists")
    names = {row["canonical_name"] for row in candidates}
    office_name = "Primo Segretario (Florentine government office)"
    picture_group_name = (
        "Unidentified pictures by Ribera, Preti and Paceco de Rosa in the Del Rosso collection"
    )
    if office_name in names or picture_group_name in names:
        raise ValueError("An equivalent candidate name already exists")
    mention_ids = {row["mention_id"] for row in mentions}
    if {OFFICE_MENTION_ID, PICTURE_GROUP_MENTION_ID} & mention_ids:
        raise ValueError("A planned mention ID already exists")

    new_candidates = [
        {
            "candidate_id": OFFICE_CANDIDATE_ID,
            "index_entry_id": "",
            "canonical_name": office_name,
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": (
                "Haskell says Senator Francesco Panciatichi held this named office from 1682. "
                "The note supplies no end date or independent account of the office."
            ),
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L153",
        },
        {
            "candidate_id": PICTURE_GROUP_CANDIDATE_ID,
            "index_entry_id": "",
            "canonical_name": picture_group_name,
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": (
                "Haskell reports these pictures in the Del Rosso holdings but gives no titles "
                "or count. Preserve the source spelling Paceco de Rosa; artist and work "
                "identity alignment remains for S3."
            ),
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L154",
        },
    ]
    candidate_after = append_csv(candidate_raw, candidate_fields, new_candidates)

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    statement_index = {row["statement_id"]: row for row in rows}
    for statement_id in (OFFICE_STATEMENT_ID, PICTURES_STATEMENT_ID, LETTER_STATEMENT_ID):
        if statement_id not in statement_index:
            raise ValueError(f"Expected statement is missing: {statement_id}")
    office = statement_index[OFFICE_STATEMENT_ID]
    pictures = statement_index[PICTURES_STATEMENT_ID]
    letter = statement_index[LETTER_STATEMENT_ID]
    if (
        office.get("segment_id") != SEGMENT_ID
        or office.get("subject_candidate_id") != "cand-1825"
        or office.get("object_candidate_id") is not None
        or not is_open_relation(office)
        or pictures.get("segment_id") != SEGMENT_ID
        or pictures.get("subject_candidate_id") != "cand-7489"
        or pictures.get("object_candidate_id") is not None
        or not is_open_relation(pictures)
        or letter.get("segment_id") != SEGMENT_ID
        or letter.get("subject_candidate_id") is not None
        or letter.get("object_candidate_id") != "cand-7613"
        or not is_open_relation(letter)
    ):
        raise ValueError("One or more target relation endpoints changed")
    if endpoint_counts(rows) != (456, 280, 63, 113):
        raise ValueError(f"Unexpected pre-update endpoint counts: {endpoint_counts(rows)}")
    before_open = endpoint_counts(rows)
    if sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in rows) != 10389:
        raise ValueError("Unexpected relation-candidate total")

    office_start, office_end = offsets[OFFICE_SURFACE]
    office["object_candidate_id"] = OFFICE_CANDIDATE_ID
    office_q = office.get("qualifiers") or {}
    office_q["mentioned_candidate_ids"] = list(
        dict.fromkeys((office_q.get("mentioned_candidate_ids") or []) + [OFFICE_CANDIDATE_ID])
    )
    office_q["qualification"] = (
        "Haskell reports the office and a starting point in 1682; no end date or independent "
        "verification is supplied."
    )
    office_q["relation_candidate_note"] = (
        "The object is the source-named office Primo Segretario, represented as a term; it is "
        "not a person or a separately identified institution."
    )
    office_q.pop("open_endpoint_reason", None)
    office["qualifiers"] = office_q

    picture_start, picture_end = offsets[PICTURE_GROUP_SURFACE]
    pictures["object_candidate_id"] = PICTURE_GROUP_CANDIDATE_ID
    pictures_q = pictures.get("qualifiers") or {}
    pictures_q["mentioned_candidate_ids"] = list(
        dict.fromkeys(
            (pictures_q.get("mentioned_candidate_ids") or []) + [PICTURE_GROUP_CANDIDATE_ID]
        )
    )
    pictures_q["qualification"] = (
        "The source supplies no titles or count for this group. Preserve the spelling Paceco de Rosa; "
        "the cited Longhi publication is recorded separately and does not identify every work."
    )
    pictures_q["relation_candidate_note"] = (
        "The object is a source-described group of pictures by the three named artists in the "
        "Del Rosso holdings; individual titles and count are not supplied."
    )
    pictures_q.pop("open_endpoint_reason", None)
    pictures["qualifiers"] = pictures_q

    new_mentions = [
        {
            "mention_id": OFFICE_MENTION_ID,
            "segment_id": SEGMENT_ID,
            "candidate_id": OFFICE_CANDIDATE_ID,
            "surface_form": OFFICE_SURFACE,
            "start_char": str(office_start),
            "end_char": str(office_end),
            "note": "The post held by Panciatichi from 1682, as stated in Haskell's footnote.",
        },
        {
            "mention_id": PICTURE_GROUP_MENTION_ID,
            "segment_id": SEGMENT_ID,
            "candidate_id": PICTURE_GROUP_CANDIDATE_ID,
            "surface_form": PICTURE_GROUP_SURFACE,
            "start_char": str(picture_start),
            "end_char": str(picture_end),
            "note": (
                "A source-described group of Del Rosso pictures; the existing artist mentions "
                "remain nested within this group mention."
            ),
        },
    ]
    mention_after = append_csv(mention_raw, mention_fields, new_mentions)
    statement_after = (
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    ).encode("utf-8")
    after_rows = [
        json.loads(line) for line in statement_after.decode("utf-8").splitlines() if line.strip()
    ]
    after_open = endpoint_counts(after_rows)
    segment_open = [
        row["statement_id"]
        for row in after_rows
        if row.get("segment_id") == SEGMENT_ID and is_open_relation(row)
    ]
    if after_open != (454, 278, 63, 113) or segment_open != [LETTER_STATEMENT_ID]:
        raise ValueError(f"Unexpected post-update endpoint state: {after_open}, {segment_open}")

    print(f"candidate_rows={len(candidates)}->{len(candidates) + len(new_candidates)}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + len(new_mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    print(
        f"planned_candidate={OFFICE_CANDIDATE_ID}|term|{office_name}; "
        f"mention=[{office_start},{office_end}) {OFFICE_SURFACE}"
    )
    print(
        f"planned_candidate={PICTURE_GROUP_CANDIDATE_ID}|work|{picture_group_name}; "
        f"mention=[{picture_start},{picture_end}) {PICTURE_GROUP_SURFACE}"
    )
    print(f"resolved_endpoint={OFFICE_STATEMENT_ID}|None->{OFFICE_CANDIDATE_ID}")
    print(f"resolved_endpoint={PICTURES_STATEMENT_ID}|None->{PICTURE_GROUP_CANDIDATE_ID}")
    print(f"preserved_open_endpoint={LETTER_STATEMENT_ID}|subject remains unidentified")
    print(f"open_endpoints={before_open}->{after_open}")
    print(f"segment_open={segment_open}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    paths = (
        (CANDIDATES, candidate_after),
        (MENTIONS, mention_after),
        (STATEMENTS, statement_after),
    )
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in paths:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temp, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temp, data in pairs:
            temp.write_bytes(data)
        for path, backup, temp, _ in pairs:
            temp.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temp, _ in pairs:
            if temp.exists():
                temp.unlink()
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
