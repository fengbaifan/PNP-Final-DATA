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
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l21-35"
BACKUP_SUFFIX = "bak-s2-chp8-p216-source-groups-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "4b5efa9e8b81f0570872586964f437bd8b5472c63e9a57403f8eda43e8aa2883",
    "mentions.csv": "6c2d791d991b4744e2ee79a5697636755de1a1e21a358afb1d331f57bbc02f6b",
    "book-statements.jsonl": "8b61e14a298b6b856c882ce3746c25d27255c9461b108606a51ce42da0b09829",
}
EXPECTED_SEGMENT_HASH = "4f5d502c755d5a791200895b453b3a196db68632297a0864a37c4995a91c1039"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def encode_csv_rows(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=fields, lineterminator=newline.decode("ascii"), extrasaction="raise"
    )
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open(row: dict[str, object]) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    open_rows = [row for row in rows if is_open(row)]
    object_only = sum(bool(r.get("subject_candidate_id")) and not r.get("object_candidate_id") for r in open_rows)
    subject_only = sum(not r.get("subject_candidate_id") and bool(r.get("object_candidate_id")) for r in open_rows)
    both = sum(not r.get("subject_candidate_id") and not r.get("object_candidate_id") for r in open_rows)
    return len(open_rows), object_only, subject_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    actual_hashes = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(actual_hashes[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row["segment_id"] == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError(f"Source segment changed: {SEGMENT_ID}")
    source_path = ROOT / segment["source_file"]
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    source_text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])

    candidate_specs = [
        (
            "cand-12366",
            "Leading families in Bergamo with whom Cristoforo Storer had close contacts",
            "",
            "Haskell identifies leading families in Bergamo as Storer's close contacts but names no family or member; this source-defined group does not assert membership or kinship details.",
            "leading families in Bergamo",
        ),
        (
            "cand-12367",
            "Milan-area artists commissioned for four Santa Maria Maggiore paintings (Haskell's p.216 account)",
            "",
            "Haskell refers collectively to other artists from Milan and its surroundings commissioned for four named subjects. The group is source-defined; no individual artist is assigned to a particular painting.",
            "other artists from Milan and its surroundings",
        ),
        (
            "cand-12368",
            "Completion of the first decoration stage at Santa Maria Maggiore in Bergamo by 1659",
            "event",
            "The first stage of the existing Santa Maria Maggiore decoration programme was complete by 1659. The source does not identify who completed it or give a more precise completion date.",
            "the first stage in the decoration",
        ),
    ]
    candidate_index = {row["candidate_id"]: row for row in candidates}
    names = {row["canonical_name"] for row in candidates}
    new_candidates: list[dict[str, str]] = []
    new_mentions: list[dict[str, str]] = []

    def add_candidate(cid: str, name: str, suggested_type: str, detail: str, surface: str) -> None:
        if cid in candidate_index or name in names:
            raise ValueError(f"Candidate ID or name already exists: {cid} / {name}")
        start = source_text.find(surface)
        if start < 0 or source_text.find(surface, start + 1) >= 0:
            raise ValueError(f"Source phrase missing or repeated: {surface}")
        line = int(segment["line_start"]) + source_text.count("\n", 0, start)
        row = {
            "candidate_id": cid,
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
            "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        }
        new_candidates.append(row)
        new_mentions.append(
            {
                "mention_id": f"m-chp8-{cid}-source-mention",
                "segment_id": SEGMENT_ID,
                "candidate_id": cid,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(start + len(surface)),
                "note": detail,
            }
        )
        candidate_index[cid] = row
        names.add(name)

    for spec in candidate_specs:
        add_candidate(*spec)

    existing_mention_ids = {row["mention_id"] for row in mentions}
    planned_mention_ids = {row["mention_id"] for row in new_mentions}
    if existing_mention_ids & planned_mention_ids:
        raise ValueError("A planned mention ID already exists")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    statement_index = {row["statement_id"]: row for row in rows}
    target_ids = [
        "st-chp8-p216-storer-close-contacts-bergamo-families",
        "st-chp8-p216-milan-artists-commissioned-killing-of-sisera",
        "st-chp8-p216-milan-artists-commissioned-sacrifice-of-isaac",
        "st-chp8-p216-milan-artists-commissioned-jacobs-ladder",
        "st-chp8-p216-milan-artists-commissioned-murder-of-cain",
        "st-chp8-p216-first-decoration-stage-complete-1659",
    ]
    for sid in target_ids:
        if sid not in statement_index or not is_open(statement_index[sid]):
            raise ValueError(f"Expected open statement missing or already resolved: {sid}")

    def resolve(sid: str, subject: str | None, object_id: str | None, note: str, extra: list[str]) -> None:
        row = statement_index[sid]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = object_id
        q = row.get("qualifiers") or {}
        q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + extra))
        q["relation_candidate_note"] = note
        q.pop("open_endpoint_reason", None)
        row["qualifiers"] = q

    resolve(
        target_ids[0],
        "cand-2512",
        "cand-12366",
        "The source explicitly identifies an unnamed group of leading Bergamo families as Storer's close contacts; no individual family or member is inferred.",
        ["cand-2512", "cand-12366"],
    )
    artist_statement_ids = target_ids[1:5]
    for sid in artist_statement_ids:
        row = statement_index[sid]
        existing_object = row.get("object_candidate_id")
        resolve(
            sid,
            "cand-12367",
            existing_object,
            "The plural source phrase identifies a source-defined group of Milan-area artists commissioned for the four works; no individual painter is mapped to a particular work.",
            ["cand-12367"],
        )
    resolve(
        target_ids[5],
        "cand-7639",
        "cand-12368",
        "The source dates completion of the first stage of the existing decoration programme to by 1659 without identifying the completing agents.",
        ["cand-7639", "cand-12368"],
    )

    after_counts = endpoint_counts(rows)
    if after_counts != (437, 275, 58, 104):
        raise ValueError(f"Unexpected post-update endpoint counts: {after_counts}")
    expected_open = "st-chp8-p216-governors-pleased-with-massacre"
    remaining_open = [
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT_ID and is_open(row)
    ]
    if remaining_open != [expected_open]:
        raise ValueError(f"Unexpected remaining p.216 open statements: {remaining_open}")

    candidate_after = encode_csv_rows(candidate_raw, candidate_fields, new_candidates)
    mention_after = encode_csv_rows(mention_raw, mention_fields, new_mentions)
    statement_after = (
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    ).encode("utf-8")
    print(f"candidate_rows={len(candidates)}->{len(candidates) + len(new_candidates)}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + len(new_mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    print(f"resolved_statements={','.join(target_ids)}")
    print(f"retained_open_statements={remaining_open}")
    print(f"open_endpoints={endpoint_counts([json.loads(x) for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{after_counts}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, candidate_after),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    outputs = ((CANDIDATES, candidate_after), (MENTIONS, mention_after), (STATEMENTS, statement_after))
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in outputs:
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
