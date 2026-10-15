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
SEGMENT_ID = "chp-9:09_CHP-9_intro:l124-132"
MASTERPIECES_ID = "st-chp9-p253-dionisio-saw-tiepolo-masterpieces"
SUMMONED_ID = "st-chp9-p253-tiepolo-summoned-outside-venice"
CANDIDATE_ID = "cand-12377"
CANDIDATE_NAME = "Tiepolo's first Udine masterpieces described in Haskell's p.253 passage (group)"
MENTION_ID = "m-chp9-p253-first-masterpieces-group"
BACKUP_SUFFIX = "bak-s2-chp9-p253-udine-masterpieces-endpoint-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "402c7dc6104c9c14e798f036d1e8a8d2416dd9b2068d168c0556c9025ec64f8c",
    "mentions.csv": "a707da62ada857bd0ef4238d18fd9d2fab82fcf929d82471ca6c6991aa90b658",
    "book-statements.jsonl": "8a92210a851305c41a38bf8c3f4599595f156b2876afd466fbd9996cb89dc4b4",
}
EXPECTED_SEGMENT_HASH = "bdcf1ec70bda8a3346f427787148673220496aeed2c647ad5260fcff41744e9a"
EXPECTED_AFTER = (427, 269, 54, 104)


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
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [r for r in rows if is_open(r)]
    object_only = sum(bool(r.get("subject_candidate_id")) and not r.get("object_candidate_id") for r in opens)
    subject_only = sum(not r.get("subject_candidate_id") and bool(r.get("object_candidate_id")) for r in opens)
    both = sum(not r.get("subject_candidate_id") and not r.get("object_candidate_id") for r in opens)
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
    raw_by_name = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(raw_by_name[name]) != expected:
            raise ValueError(f"Input table changed since review: {name}")
    if any(r["candidate_id"] == CANDIDATE_ID or r["canonical_name"] == CANDIDATE_NAME for r in candidates):
        raise ValueError("Candidate ID or name already exists")
    if any(r["mention_id"] == MENTION_ID for r in mentions):
        raise ValueError("Mention ID already exists")

    segment = next(
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Page 253 segment changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    line_no = 127
    line = source_lines[line_no - 1]
    surface = "first masterpieces"
    if line.count(surface) != 1:
        raise ValueError("Expected unique 'first masterpieces' phrase is missing or repeated")
    line_base = sum(len(text) + 1 for text in source_lines[int(segment["line_start"]) - 1 : line_no - 1])
    start = line.find(surface)
    mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": surface,
        "start_char": str(line_base + start),
        "end_char": str(line_base + start + len(surface)),
        "note": "Haskell's collective phrase is contextually bounded to the Abraham scenes and The Justice of Solomon, following the distinct earlier staircase start.",
    }

    rows = [json.loads(text) for text in statement_raw.decode("utf-8").splitlines() if text.strip()]
    if endpoint_counts(rows) != (428, 270, 54, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {endpoint_counts(rows)}")
    masterpieces = next((r for r in rows if r.get("statement_id") == MASTERPIECES_ID), None)
    summoned = next((r for r in rows if r.get("statement_id") == SUMMONED_ID), None)
    if masterpieces is None or not is_open(masterpieces) or masterpieces.get("subject_candidate_id") != "cand-0929" or masterpieces.get("object_candidate_id") is not None:
        raise ValueError("Expected open Dionisio statement not found")
    if summoned is None or not is_open(summoned) or summoned.get("subject_candidate_id") != "cand-2569" or summoned.get("object_candidate_id") is not None:
        raise ValueError("Expected open 'summoned outside Venice' statement not found")

    candidate = {
        "candidate_id": CANDIDATE_ID, "index_entry_id": "", "canonical_name": CANDIDATE_NAME,
        "index_page_range": "", "suggested_type": "work", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "A context-bounded group of the Abraham scenes in the palace gallery (cand-8282) and The Justice of Solomon in the tribunal hall (cand-8283), which immediately follow a separately described melodramatic start on the staircase ceiling (cand-8281). Haskell does not enumerate the Abraham scenes or explicitly define the group's membership.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
    }
    masterpieces["object_candidate_id"] = CANDIDATE_ID
    mq = masterpieces["qualifiers"]
    mq["claim"] = "Haskell says Dionisio Dolfin saw Tiepolo's first masterpieces shortly before dying; the surrounding passage points to the Abraham scenes and The Justice of Solomon at Udine."
    mq["qualification"] = "The endpoint is a context-bounded group of the Abraham scenes and The Justice of Solomon; the earlier staircase ceiling is separately described as a melodramatic start. Individual scenes and the exact viewing occasion are not specified."
    mq["mentioned_candidate_ids"] = list(dict.fromkeys((mq.get("mentioned_candidate_ids") or []) + [CANDIDATE_ID]))
    mq["relation_candidate_note"] = "Resolve the plural referent as a bounded work group from the two immediately described works that mark Tiepolo's stylistic change; do not include the separately characterized staircase start or invent individual scene identities."
    mq.pop("open_endpoint_reason", None)
    masterpieces["predicate"] = "dionisio_saw_tiepolo_first_udine_masterpieces_shortly_before_dying"

    sq = summoned["qualifiers"]
    sq["open_endpoint_reason"] = "The passage says Tiepolo was frequently summoned outside Venice but names no commissioner or destination. The adjacent Udine works do not establish that Udine was a destination of these early-1730s summons; keep the missing endpoint open."
    sq["relation_candidate_note"] = "This is a reviewed, source-supported general claim with no named commissioner or destination; do not infer Udine or other places from adjacent context."
    sq["semantic_review"] = "2026-10-15 source-order endpoint review: CHP-9.pdf physical page 15 checked; no specific destination or summoning party is identified, so the endpoint remains open."

    if endpoint_counts(rows) != EXPECTED_AFTER:
        raise ValueError(f"Unexpected post-update endpoint counts: {endpoint_counts(rows)}")
    candidate_after = append_rows(candidate_raw, candidate_fields, [candidate])
    mention_after = append_rows(mention_raw, mention_fields, [mention])
    statement_after = ("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)).encode("utf-8")
    print(f"candidates={len(candidates)}->{len(candidates) + 1}")
    print(f"mentions={len(mentions)}->{len(mentions) + 1}")
    print(f"statements={len([1 for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{len(rows)}")
    print(f"resolved_endpoint={MASTERPIECES_ID}|object->{CANDIDATE_ID}")
    print(f"retained_open={SUMMONED_ID}|reason=unidentified_commissioner_and_destination")
    print(f"open_endpoints={endpoint_counts([json.loads(x) for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{endpoint_counts(rows)}")
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
