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
SOURCE = ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l3-9"
COLLECTION_GROUP_ID = "cand-12351"
ROMAN_VARIETY_ID = "st-chp8-sec-ii-intro-roman-variety"
LOCAL_ARTISTS_ID = "st-chp8-sec-ii-intro-local-artists-backbone"
ROMAN_PATRONAGE_ID = "cand-7186"
OWN_COLLECTIONS_MENTION_ID = "m-chp8-p214-sec-ii-own-collections"
COLLECTIONS_MENTION_ID = "m-chp8-p214-sec-ii-collections-backbone"
BACKUP_SUFFIX = "bak-s2-chp8-p214-section-ii-collection-group-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "9b07e72f5872ef39f1cc771b52f561fda701309183ea0bbc4638db2eba988d59",
    "mentions.csv": "95acb4352db8f695e46f763617c32e9dddd63bdadf04a9e064790cb4197355ff",
    "book-statements.jsonl": "4e7c39067b8371ee7c75d64cb31a21d905cf94608af9271ef5fb1187fc18b5dd",
}
EXPECTED_SEGMENT_HASH = "7f6b9c5db0dbec4681c52467cfb5f786815710aea929e957183cd6024fffb1ba"


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
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    phrases = {
        "their own collections": OWN_COLLECTIONS_MENTION_ID,
        "their collections": COLLECTIONS_MENTION_ID,
    }
    offsets: dict[str, tuple[int, int]] = {}
    for phrase in phrases:
        start = text.find(phrase)
        if start < 0 or text.find(phrase, start + 1) >= 0:
            raise ValueError(f"Source phrase missing or repeated: {phrase}")
        offsets[phrase] = (start, start + len(phrase))

    candidate_index = {row["candidate_id"]: row for row in candidates}
    if COLLECTION_GROUP_ID in candidate_index or ROMAN_PATRONAGE_ID not in candidate_index:
        raise ValueError("Candidate preconditions changed")
    roman_patronage = candidate_index[ROMAN_PATRONAGE_ID]
    if roman_patronage.get("suggested_type") != "term":
        raise ValueError("Roman patronage candidate is not a term")
    collection_group_name = "Collections of patrons discussed in Haskell's Chapter 8 overview"
    if collection_group_name in {row["canonical_name"] for row in candidates}:
        raise ValueError("Equivalent collection-group candidate already exists")
    planned_mention_ids = set(phrases.values())
    existing_mention_ids = {row["mention_id"] for row in mentions}
    if planned_mention_ids & existing_mention_ids:
        raise ValueError("A planned mention ID already exists")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    statement_index = {row["statement_id"]: row for row in rows}
    if ROMAN_VARIETY_ID not in statement_index or LOCAL_ARTISTS_ID not in statement_index:
        raise ValueError("One or more target statements are missing")
    roman_variety = statement_index[ROMAN_VARIETY_ID]
    local_artists = statement_index[LOCAL_ARTISTS_ID]
    if (
        roman_variety.get("segment_id") != SEGMENT_ID
        or roman_variety.get("subject_candidate_id") is not None
        or roman_variety.get("object_candidate_id") is not None
        or not is_open_relation(roman_variety)
        or local_artists.get("segment_id") != SEGMENT_ID
        or local_artists.get("subject_candidate_id") is not None
        or local_artists.get("object_candidate_id") is not None
        or not is_open_relation(local_artists)
        or endpoint_counts(rows) != (454, 278, 63, 113)
    ):
        raise ValueError("Target relation state or global open counts changed")

    new_candidate = {
        "candidate_id": COLLECTION_GROUP_ID,
        "index_entry_id": "",
        "canonical_name": collection_group_name,
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Collective referent for the patrons' own collections in this section's opening "
            "synthesis. It denotes multiple distinct collections, not one institution; the "
            "individual collections and full membership are not identified here. Collection "
            "has no dedicated type in the current taxonomy."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L3",
    }
    candidate_after = append_csv(candidate_raw, candidate_fields, [new_candidate])

    roman_variety["subject_candidate_id"] = COLLECTION_GROUP_ID
    roman_variety["object_candidate_id"] = ROMAN_PATRONAGE_ID
    roman_q = roman_variety.get("qualifiers") or {}
    roman_q["mentioned_candidate_ids"] = list(
        dict.fromkeys((roman_q.get("mentioned_candidate_ids") or []) + [COLLECTION_GROUP_ID])
    )
    roman_q["relation_candidate_note"] = (
        "The subject is the source-defined group of distinct collections owned by the patrons "
        "discussed earlier in the section; the object reuses the Roman patronage term. The "
        "individual collections and patrons are not enumerated here."
    )
    roman_q.pop("open_endpoint_reason", None)
    roman_variety["qualifiers"] = roman_q

    local_artists["object_candidate_id"] = COLLECTION_GROUP_ID
    local_q = local_artists.get("qualifiers") or {}
    local_q["mentioned_candidate_ids"] = list(
        dict.fromkeys((local_q.get("mentioned_candidate_ids") or []) + [COLLECTION_GROUP_ID])
    )
    local_q["relation_candidate_note"] = (
        "The object is the source-defined group of distinct collections discussed in the opening "
        "synthesis. The local artists are described collectively but are not identified or "
        "bounded here, so the subject remains open."
    )
    local_q["open_endpoint_reason"] = (
        "The text refers to local artists collectively and gives no member list; do not infer "
        "individual artists from the broad generalization."
    )
    local_artists["qualifiers"] = local_q

    new_mentions = []
    for surface, mention_id in phrases.items():
        start, end = offsets[surface]
        new_mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": COLLECTION_GROUP_ID,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(end),
                "note": (
                    "Collective reference to the distinct collections of the previously discussed "
                    "patrons; the source does not identify each collection."
                ),
            }
        )
    mention_after = append_csv(mention_raw, mention_fields, new_mentions)
    statement_after = (
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    ).encode("utf-8")
    after_rows = [
        json.loads(line) for line in statement_after.decode("utf-8").splitlines() if line.strip()
    ]
    after_counts = endpoint_counts(after_rows)
    segment_open = [
        row["statement_id"]
        for row in after_rows
        if row.get("segment_id") == SEGMENT_ID and is_open_relation(row)
    ]
    expected_segment_open = [
        "st-chp8-sec-ii-intro-collections_in_nonlocal_centres",
        "st-chp8-sec-ii-intro-local-artists-backbone",
        "st-chp8-sec-ii-intro-local-centres",
        "st-chp8-sec-ii-intro-outside-commissioning",
        "st-chp8-sec-ii-intro-younger-painters",
    ]
    if after_counts != (453, 278, 64, 111) or segment_open != expected_segment_open:
        raise ValueError(f"Unexpected post-update endpoint state: {after_counts}, {segment_open}")

    print(f"candidate_rows={len(candidates)}->{len(candidates) + 1}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + len(new_mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    print(
        f"planned_candidate={COLLECTION_GROUP_ID}|type=unresolved|{collection_group_name}"
    )
    for surface, mention_id in phrases.items():
        start, end = offsets[surface]
        print(f"planned_mention={mention_id}|[{start},{end})|{surface}")
    print(
        f"resolved={ROMAN_VARIETY_ID}|{COLLECTION_GROUP_ID}->{ROMAN_PATRONAGE_ID}"
    )
    print(f"partially_resolved={LOCAL_ARTISTS_ID}|object->{COLLECTION_GROUP_ID}; subject remains open")
    print(f"open_endpoints={(454, 278, 63, 113)}->{after_counts}")
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
