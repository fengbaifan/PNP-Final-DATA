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
COLLECTIONS_ID = "st-chp8-sec-ii-intro-collections_in_nonlocal_centres"
LOCAL_ARTISTS_ID = "st-chp8-sec-ii-intro-local-artists-backbone"
LOCAL_CENTRES_ID = "st-chp8-sec-ii-intro-local-centres"
OUTSIDE_COMMISSIONING_ID = "st-chp8-sec-ii-intro-outside-commissioning"
YOUNGER_PAINTERS_ID = "st-chp8-sec-ii-intro-younger-painters"
BACKUP_SUFFIX = "bak-s2-chp8-p214-section-ii-source-groups-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "1da825ed2a2ea250acda495cf125f05d076f4888e87836c3079007f8723504a4",
    "mentions.csv": "4f263981d16af337ee937ab41b4d0a457b161cbb550936faf9e4a9c4ef236a41",
    "book-statements.jsonl": "2848c6a145557a76490cf1aae8e768b6878ce7dedbcb7e2fef17e77af17cee58",
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


def candidate(
    candidate_id: str,
    name: str,
    suggested_type: str,
    detail: str,
    source_line: int,
) -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": suggested_type,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{source_line}",
    }


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

    group_specs = [
        (
            "cand-12352",
            "Italian art collections in cities with undistinguished native painters (Haskell's p.214 overview)",
            "",
            "Source-defined group of Italian art collections in cities Haskell characterizes as having undistinguished native painters. No individual collection or exhaustive city list is supplied; collection has no dedicated type in the current taxonomy.",
            5,
            "some of the most interesting collections of Italian art",
            "m-chp8-p214-sec-ii-nonlocal-collections",
        ),
        (
            "cand-12353",
            "Cities with undistinguished native painters in Haskell's p.214 overview",
            "place",
            "Source-defined group of cities characterized as lacking distinguished native painters. Bergamo, Ferrara, Macerata, and Lucca are given as examples in the next sentence, not as an exhaustive list.",
            5,
            "cities quite undistinguished for their native painters",
            "m-chp8-p214-sec-ii-undistinguished-cities",
        ),
        (
            "cand-12354",
            "Previously discussed patrons other than Don Antonio Ruffo (Haskell's p.214 overview)",
            "",
            "The source-defined group expressed as 'all of them' except Don Antonio Ruffo. The source OCR reads Russo, corrected to Ruffo from the printed page; individual patrons are not enumerated in this sentence. Type remains unset because the taxonomy has no person-group type.",
            3,
            "all of them",
            "m-chp8-p214-sec-ii-patrons-ex-ruffo",
        ),
        (
            "cand-12355",
            "Centres with flourishing local painting schools in Haskell's p.214 overview",
            "place",
            "Source-defined group of centres characterized by great artistic traditions and flourishing local painting schools. This statement does not assign each previously discussed patron to a specific centre.",
            3,
            "centres of great artistic traditions and achievement characterised by flourishing local schools of painting",
            "m-chp8-p214-sec-ii-flourishing-centres",
        ),
        (
            "cand-12356",
            "Local artists providing the backbone of patrons' collections in Haskell's p.214 overview",
            "",
            "Source-defined group of local artists whom Haskell says provided the backbone of collections in most cases. The artists and their individual schools are not named; type remains unset because the taxonomy has no person-group type.",
            4,
            "these local artists",
            "m-chp8-p214-sec-ii-local-artists",
        ),
        (
            "cand-12357",
            "Collectors in cities without a local artistic tradition or painting school (Haskell's p.214 overview)",
            "",
            "Source-defined collector group for the general case described by Haskell. No individual collectors or cities are assigned; type remains unset because the taxonomy has no person-group type.",
            4,
            "a collector living in a city with no such tradition or local school",
            "m-chp8-p214-sec-ii-collectors-without-local-school",
        ),
        (
            "cand-12358",
            "Works commissioned from outside collectors' provinces in Haskell's p.214 overview",
            "work",
            "Source-described group of works of art commissioned by collectors outside their own provinces. The claim is qualified as 'almost exclusively'; no individual commissions or works are named.",
            5,
            "commission works of art almost exclusively from outside his province",
            "m-chp8-p214-sec-ii-external-commissions",
        ),
    ]
    candidate_ids = {row["candidate_id"] for row in candidates}
    candidate_names = {row["canonical_name"] for row in candidates}
    new_candidates: list[dict[str, str]] = []
    new_mentions: list[dict[str, str]] = []
    for cid, name, suggested_type, detail, line, surface, mention_id in group_specs:
        if cid in candidate_ids or name in candidate_names:
            raise ValueError(f"Candidate ID or name already exists: {cid} / {name}")
        start = text.find(surface)
        if start < 0 or text.find(surface, start + 1) >= 0:
            raise ValueError(f"Source phrase missing or repeated: {surface}")
        new_candidates.append(candidate(cid, name, suggested_type, detail, line))
        new_mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": cid,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(start + len(surface)),
                "note": detail,
            }
        )
        candidate_ids.add(cid)
        candidate_names.add(name)
    if {row["mention_id"] for row in new_mentions} & {row["mention_id"] for row in mentions}:
        raise ValueError("A planned mention ID already exists")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    statement_index = {row["statement_id"]: row for row in rows}
    targets = {
        COLLECTIONS_ID: statement_index.get(COLLECTIONS_ID),
        LOCAL_ARTISTS_ID: statement_index.get(LOCAL_ARTISTS_ID),
        LOCAL_CENTRES_ID: statement_index.get(LOCAL_CENTRES_ID),
        OUTSIDE_COMMISSIONING_ID: statement_index.get(OUTSIDE_COMMISSIONING_ID),
        YOUNGER_PAINTERS_ID: statement_index.get(YOUNGER_PAINTERS_ID),
    }
    if any(row is None for row in targets.values()):
        raise ValueError("One or more target statements are missing")
    expected_state = {
        COLLECTIONS_ID: (None, None),
        LOCAL_ARTISTS_ID: (None, "cand-12351"),
        LOCAL_CENTRES_ID: (None, None),
        OUTSIDE_COMMISSIONING_ID: (None, None),
        YOUNGER_PAINTERS_ID: (None, None),
    }
    for sid, row in targets.items():
        if (
            row.get("segment_id") != SEGMENT_ID
            or (row.get("subject_candidate_id"), row.get("object_candidate_id")) != expected_state[sid]
            or not is_open_relation(row)
        ):
            raise ValueError(f"Target statement changed: {sid}")
    if endpoint_counts(rows) != (453, 278, 64, 111):
        raise ValueError(f"Unexpected pre-update endpoint counts: {endpoint_counts(rows)}")

    additions = {
        COLLECTIONS_ID: ("cand-12352", "cand-12353"),
        LOCAL_ARTISTS_ID: ("cand-12356",),
        LOCAL_CENTRES_ID: ("cand-12354", "cand-12355"),
        OUTSIDE_COMMISSIONING_ID: ("cand-12357", "cand-12358"),
    }
    for sid, row in targets.items():
        if sid == YOUNGER_PAINTERS_ID:
            continue
        q = row.get("qualifiers") or {}
        q["mentioned_candidate_ids"] = list(
            dict.fromkeys((q.get("mentioned_candidate_ids") or []) + list(additions[sid]))
        )
        q.pop("open_endpoint_reason", None)
        row["qualifiers"] = q

    targets[COLLECTIONS_ID]["subject_candidate_id"] = "cand-12352"
    targets[COLLECTIONS_ID]["object_candidate_id"] = "cand-12353"
    targets[COLLECTIONS_ID]["qualifiers"]["relation_candidate_note"] = (
        "The endpoints are source-defined groups: the collections Haskell calls especially "
        "interesting and the cities he characterizes as having undistinguished native painters. "
        "The following examples are not treated as an exhaustive list or as named collections."
    )

    targets[LOCAL_ARTISTS_ID]["subject_candidate_id"] = "cand-12356"
    targets[LOCAL_ARTISTS_ID]["object_candidate_id"] = "cand-12351"
    targets[LOCAL_ARTISTS_ID]["qualifiers"]["relation_candidate_note"] = (
        "The source-defined local-artist group is linked to the distinct collections of patrons "
        "discussed earlier. Preserve 'in most cases' and 'usually'; no artist or collection is "
        "assigned individually."
    )

    targets[LOCAL_CENTRES_ID]["subject_candidate_id"] = "cand-12354"
    targets[LOCAL_CENTRES_ID]["object_candidate_id"] = "cand-12355"
    targets[LOCAL_CENTRES_ID]["qualifiers"]["relation_candidate_note"] = (
        "The endpoints are the previously discussed patrons as a source-defined group excluding "
        "Don Antonio Ruffo, and the group of centres with flourishing local schools. No patron "
        "is assigned to an individual city."
    )

    targets[OUTSIDE_COMMISSIONING_ID]["subject_candidate_id"] = "cand-12357"
    targets[OUTSIDE_COMMISSIONING_ID]["object_candidate_id"] = "cand-12358"
    targets[OUTSIDE_COMMISSIONING_ID]["qualifiers"]["relation_candidate_note"] = (
        "The endpoints are source-defined groups of collectors in cities without local schools "
        "and works commissioned beyond their provinces. Preserve 'almost exclusively' and the "
        "comparison with Bologna, Genoa, and Naples."
    )

    targets[YOUNGER_PAINTERS_ID]["qualifiers"]["open_endpoint_reason"] = (
        "This is a modal travel scenario ('might have found'), not a report of identified works "
        "actually present in the listed cities. Keep the individual painter and city mentions; "
        "do not invent a traveller or a settled group of works."
    )

    candidate_after = append_csv(candidate_raw, candidate_fields, new_candidates)
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
    if after_counts != (449, 278, 63, 108) or segment_open != [YOUNGER_PAINTERS_ID]:
        raise ValueError(f"Unexpected post-update state: {after_counts}, {segment_open}")

    print(f"candidate_rows={len(candidates)}->{len(candidates) + len(new_candidates)}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + len(new_mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    for row in new_candidates:
        print(f"planned_candidate={row['candidate_id']}|{row['suggested_type'] or 'type unresolved'}|{row['canonical_name']}")
    for row in new_mentions:
        print(
            f"planned_mention={row['mention_id']}|[{row['start_char']},{row['end_char']})|"
            f"{row['surface_form']}"
        )
    print(f"resolved_statements={COLLECTIONS_ID},{LOCAL_ARTISTS_ID},{LOCAL_CENTRES_ID},{OUTSIDE_COMMISSIONING_ID}")
    print(f"preserved_open_statement={YOUNGER_PAINTERS_ID}")
    print(f"open_endpoints={(453, 278, 64, 111)}->{after_counts}")
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
