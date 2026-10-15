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
SEGMENT_ID = "chp-9:09_CHP-9_intro:l38-46"
STATEMENT_ID = "st-chp9-p248-facade-place-plans-and-ambassador"
CANDIDATE_ID = "cand-12376"
CANDIDATE_NAME = "Plans of Candia, Corfu, Spalato, Zara, Padua, and Rome shown on the S. Maria del Giglio facade pedestals"
MENTION_ID = "m-chp9-p248-facade-plan-group"
BACKUP_SUFFIX = "bak-s2-chp9-p248-facade-plan-group-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "6f35fdf045b7012efd60be46331f207bb3bd432949493cc76d5c79316da788a6",
    "mentions.csv": "c3b8e337d92ed66929ab70a93c79e48c79fdd54da5fff845b475d5f80b4dbf5c",
    "book-statements.jsonl": "e47b87fe789a440c79f6ae086d2a1dbe23c887fd5a773f20580018bcbffc9e46",
}
EXPECTED_SEGMENT_HASH = "353c3cfd37cc305ef624b371deb6b4e2a7cabf9c6a58bafa8e0269316329ba46"
EXPECTED_AFTER = (428, 270, 54, 104)


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
        raise ValueError("Page 248 segment changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    line_no = 45
    line = source_lines[line_no - 1]
    surface = "plans of Candia, Corfu, Spalato, Zara, Padua and Rome"
    if line.count(surface) != 1:
        raise ValueError("Expected unique plans phrase is missing or repeated")
    line_base = sum(len(text) + 1 for text in source_lines[int(segment["line_start"]) - 1 : line_no - 1])
    start = line.find(surface)
    mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": surface,
        "start_char": str(line_base + start),
        "end_char": str(line_base + start + len(surface)),
        "note": "The six plans are preserved as the source's collective work group; no individual plan or maker is identified.",
    }

    rows = [json.loads(text) for text in statement_raw.decode("utf-8").splitlines() if text.strip()]
    if endpoint_counts(rows) != (429, 271, 54, 104):
        raise ValueError(f"Unexpected pre-update endpoint counts: {endpoint_counts(rows)}")
    target = next((r for r in rows if r.get("statement_id") == STATEMENT_ID), None)
    if target is None or not is_open(target) or target.get("subject_candidate_id") != "cand-8153" or target.get("object_candidate_id") is not None:
        raise ValueError("Expected p.248 open façade-plan statement not found")
    q = target["qualifiers"]
    prior_ids = q.get("mentioned_candidate_ids") or []
    expected_places = {"cand-8155", "cand-8118", "cand-8159", "cand-8160", "cand-1803", "cand-4490"}
    if not expected_places.issubset(set(prior_ids)):
        raise ValueError("The six named plan subjects are not all linked in the source statement")
    candidate = {
        "candidate_id": CANDIDATE_ID, "index_entry_id": "", "canonical_name": CANDIDATE_NAME,
        "index_page_range": "", "suggested_type": "work", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "A source-level group of the six plans described on the S. Maria del Giglio façade pedestals. Individual plan objects, makers, and any one-to-one mapping to the four brothers are not supplied.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
    }
    target["object_candidate_id"] = CANDIDATE_ID
    q["mentioned_candidate_ids"] = list(dict.fromkeys(prior_ids + [CANDIDATE_ID]))
    q["relation_candidate_note"] = "The source treats the six plans collectively. No individual plan-maker or one-to-one correspondence to the four brothers is supplied; Antonio's Rome ambassadorship is separately recorded in st-chp9-p248-antonio-ambassador-in-rome."
    q.pop("open_endpoint_reason", None)
    q["claim"] = "Haskell says the pedestals beneath the four brothers displayed a group of plans of Candia, Corfu, Spalato, Zara, Padua, and Rome."
    target["predicate"] = "facade_pedestals_displayed_group_of_plans_of_six_named_places"

    if endpoint_counts(rows) != EXPECTED_AFTER:
        raise ValueError(f"Unexpected post-update endpoint counts: {endpoint_counts(rows)}")
    candidate_after = append_rows(candidate_raw, candidate_fields, [candidate])
    mention_after = append_rows(mention_raw, mention_fields, [mention])
    statement_after = ("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)).encode("utf-8")
    print(f"candidates={len(candidates)}->{len(candidates) + 1}")
    print(f"mentions={len(mentions)}->{len(mentions) + 1}")
    print(f"statements={len([1 for x in statement_raw.decode('utf-8').splitlines() if x.strip()])}->{len(rows)}")
    print(f"resolved_endpoint={STATEMENT_ID}|object->{CANDIDATE_ID}")
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
