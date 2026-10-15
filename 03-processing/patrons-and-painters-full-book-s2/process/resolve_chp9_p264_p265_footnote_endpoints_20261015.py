from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
NOTES_SEGMENT = "chp-9:09_CHP-9_intro:l323-445"
BODY_SEGMENT = "chp-9:09_CHP-9_intro:l291-301"
P264_STATEMENT = "st-chp9-p263264-direct-acquisition-limit-partial"
P265_N6_STATEMENT = "st-chp9-p265-note6-crespi-works-identified"
BACKUP_SUFFIX = "bak-s2-chp9-p264-p265-footnote-endpoints-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "607366432d9d465bd126ad479a412b64538ef285567d94cdb4f67dc0dea36bc3",
    "mentions.csv": "9fb2073f2c4b47038001030f9880450c53d8570e7490668f8b42e3b9969e21e2",
    "book-statements.jsonl": "315f8244ed46707f65dd986ee8119451a1be37dd6e867edc742a8580d729285f",
}
EXPECTED_SEGMENT_HASHES = {
    NOTES_SEGMENT: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
    BODY_SEGMENT: "3820d49b66ee86388bfe238d2257d81f282963238c24fbf01a771e396f41cc83",
}
NEW_CANDIDATE = {
    "candidate_id": "cand-12387",
    "canonical_name": "Unidentified 1685-1729 inventory pictures Haskell treats as directly acquired by Zaccaria Sagredo",
    "suggested_type": "work",
    "detail": "A source-defined group of pictures listed in eighteenth-century inventories and dated by Haskell to 1685-1729, the range he treats as safe for direct acquisition by Zaccaria Sagredo. Individual works, full membership and dates are not supplied; the underlying inventories were not independently consulted.",
}
GROUP_SURFACE = "the few pictures listed in the various eighteenth-century inventories"
GROUP_MENTION_ID = "m-chp9-p264-acquired-picture-set"
MISSION_STATEMENT_ID = "st-chp9-p265-note6-mission-work-identified"


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
    for name, data in (
        ("entity-candidates.csv", candidate_raw), ("mentions.csv", mention_raw), ("book-statements.jsonl", statement_raw)
    ):
        if digest(data) != EXPECTED_HASHES[name]:
            raise ValueError(f"Input table changed since this batch was reviewed: {name}")

    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    segment_index = {row["segment_id"]: row for row in segments}
    for segment_id, expected in EXPECTED_SEGMENT_HASHES.items():
        if segment_index[segment_id].get("sha256") != expected:
            raise ValueError(f"Source segment changed: {segment_id}")
    note_segment = segment_index[NOTES_SEGMENT]
    source_lines = (ROOT / note_segment["source_file"]).read_text(encoding="utf-8").splitlines()
    p264_line = source_lines[426]
    if p264_line.count(GROUP_SURFACE) != 1:
        raise ValueError("Expected p.264 note 8 picture-group phrase not found uniquely")

    if NEW_CANDIDATE["candidate_id"] in {row["candidate_id"] for row in candidates}:
        raise ValueError("New picture-group candidate ID already exists")
    if GROUP_MENTION_ID in {row["mention_id"] for row in mentions}:
        raise ValueError("New p.264 group mention ID already exists")
    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    before_counts = endpoint_counts(rows)
    if before_counts != (419, 262, 53, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {before_counts}")
    index = {row["statement_id"]: row for row in rows}
    p264 = index.get(P264_STATEMENT)
    p265 = index.get(P265_N6_STATEMENT)
    if p264 is None or not is_open(p264) or p264.get("subject_candidate_id") != "cand-2329":
        raise ValueError("Expected open p.264 note 8 statement is absent or changed")
    if p265 is None or not is_open(p265) or p265.get("subject_candidate_id") != "cand-8591":
        raise ValueError("Expected open p.265 note 6 statement is absent or changed")
    if p265.get("object_candidate_id") is not None:
        raise ValueError("p.265 note 6 already has an object endpoint")
    if MISSION_STATEMENT_ID in index:
        raise ValueError("The atomic Mission statement already exists")

    start = sum(len(text) + 1 for text in source_lines[int(note_segment["line_start"]) - 1 : 426]) + p264_line.index(GROUP_SURFACE)
    new_mention = {
        "mention_id": GROUP_MENTION_ID, "segment_id": NOTES_SEGMENT, "candidate_id": NEW_CANDIDATE["candidate_id"],
        "surface_form": GROUP_SURFACE, "start_char": str(start), "end_char": str(start + len(GROUP_SURFACE)),
        "note": "Source-defined picture group in Haskell's p.264 note 8; its p.265 continuation names Loth canvases and Cassana portraits but does not enumerate the complete set.",
    }
    p264["object_candidate_id"] = NEW_CANDIDATE["candidate_id"]
    p264["predicate"] = "zaccaria_directly_acquired_haskell_1685_1729_inventory_picture_group"
    q264 = p264["qualifiers"]
    q264["claim"] = "Haskell says the few inventory pictures dated 1685-1729 are the only works safe to assume Zaccaria Sagredo acquired directly."
    q264["mentioned_candidate_ids"] = list(dict.fromkeys((q264.get("mentioned_candidate_ids") or []) + [NEW_CANDIDATE["candidate_id"]]))
    q264["relation_candidate_note"] = "The p.264 sentence defines a source-bounded group of inventory pictures; p.265 note 8 continues the same claim with Loth canvases and Cassana portraits as named members, without giving a complete list."
    q264.pop("open_endpoint_reason", None)

    original_note6_quote = p265["original_quote"]
    p265["object_candidate_id"] = "cand-8645"
    p265["predicate"] = "crespi_work_group_includes_unidentified_nativity"
    q265 = p265["qualifiers"]
    q265["claim"] = "Haskell identifies one of the two religious works attributed to Giuseppe Maria Crespi for Zaccaria Sagredo as an unidentified Nativity."
    q265["mentioned_candidate_ids"] = ["cand-0871", "cand-2339", "cand-8591", "cand-8645", "cand-7716", "cand-8644"]
    q265["qualification"] = "The Nativity has no full title, date or current location in this note. The short-form L. Crespi p.215 citation was not independently consulted."
    q265["relation_candidate_note"] = "The footnote enumerates two components of the previously recorded Crespi picture group. This row records the Nativity; the Mission is represented separately, and neither is assigned a full title or external identity."
    q265.pop("open_endpoint_reason", None)

    mission = deepcopy(p265)
    mission["statement_id"] = MISSION_STATEMENT_ID
    mission["object_candidate_id"] = "cand-8646"
    mission["predicate"] = "crespi_work_group_includes_unidentified_mission"
    mission["qualifiers"]["claim"] = "Haskell identifies the other religious work attributed to Giuseppe Maria Crespi for Zaccaria Sagredo as an unidentified Mission."
    mission["qualifiers"]["mentioned_candidate_ids"] = ["cand-0871", "cand-2339", "cand-8591", "cand-8646", "cand-7716", "cand-8644"]
    mission["qualifiers"]["qualification"] = "The Mission has no full title or date in this note. Haskell says it may be the work described as a 'Jesuit Mission' now in Chicago; that identification remains expressly tentative. The short-form L. Crespi p.215 citation was not independently consulted."
    mission["qualifiers"]["relation_candidate_note"] = "The footnote enumerates the Mission as the second component of the previously recorded Crespi picture group. Haskell's possible Chicago identification is retained as tentative and is not treated as an identity match."
    mission["original_quote"] = original_note6_quote
    rows.append(mission)
    after_counts = endpoint_counts(rows)
    if after_counts != (417, 260, 53, 104):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")

    candidate_row = {
        "candidate_id": NEW_CANDIDATE["candidate_id"], "index_entry_id": "",
        "canonical_name": NEW_CANDIDATE["canonical_name"], "index_page_range": "",
        "suggested_type": NEW_CANDIDATE["suggested_type"], "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": NEW_CANDIDATE["detail"], "exclude_reason": "",
        "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTES_SEGMENT}#L427",
    }
    candidate_after = append_rows(candidate_raw, candidate_fields, [candidate_row])
    mention_after = append_rows(mention_raw, mention_fields, [new_mention])
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")
    print("resolved=p.264 note 8 direct-acquisition picture group; p.265 note 6 Nativity and Mission as separate works")
    print("retained_uncertainty=complete membership and individual identities of the inventory group; full titles/dates/locations of the Crespi works; possible Chicago match remains tentative")
    print(f"candidates={len(candidates)}->{len(candidates) + 1}; mentions={len(mentions)}->{len(mentions) + 1}; statements={len(rows) - 1}->{len(rows)}")
    print(f"open_endpoints={before_counts}->{after_counts}")
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
