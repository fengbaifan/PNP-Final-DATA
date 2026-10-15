from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
EXPECTED_TABLE_SHA256 = "aacc24e80abdcc26e7fb55a98f6d1a5873793ff6a855283d22f72e5f3235563d"
SOURCE_SHA256 = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEGMENT_ID = "chp-10:10_CHP-10_intro:l491-634"
SEGMENT_SHA256 = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp10-p276n1-colle-endpoint-20261015")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if digest(raw) != EXPECTED_TABLE_SHA256:
        raise ValueError(f"statement table changed: {digest(raw)}")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("chapter 10 source asset changed")
    segments = {
        row["segment_id"]: row
        for row in (
            json.loads(line)
            for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    segment = segments.get(SEGMENT_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise ValueError("reviewed p.276 note segment changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("duplicate statement IDs")
    row = by_id.get("st-chp10-notes-p276n1-biographical-attribution")
    if not row:
        raise ValueError("p.276 note statement is missing")
    q = row.get("qualifiers") or {}
    if (
        row.get("segment_id") != SEGMENT_ID
        or row.get("subject_candidate_id") is not None
        or row.get("object_candidate_id") is not None
        or row.get("predicate") != "haskell_reports_early_biographers_on_colle_and_pastel_advice"
        or q.get("relation_candidate") is not True
        or q.get("open_endpoint_reason")
        or "retain the attributed advice relation" not in q.get("qualification", "")
    ):
        raise ValueError("p.276 attribution statement no longer matches the reviewed state")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_by_id = {item["candidate_id"]: item for item in csv.DictReader(handle)}
    for candidate_id in ("cand-0801", "cand-0581"):
        if candidate_id not in candidate_by_id or candidate_by_id[candidate_id]["suggested_type"] != "person":
            raise ValueError(f"missing or wrong type for candidate: {candidate_id}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[490:634])
    exact_mentions = {
        "m-chp10-p276n1-cole-attribution": ("cand-0801", "Colle inglese", 68, 81),
        "m-chp10-p276n1-carriera": ("cand-0581", "Rosalba Carriera", 167, 183),
    }
    with (ROOT / "04-knowledge/tables/mentions.csv").open(encoding="utf-8-sig", newline="") as handle:
        mention_rows = {item["mention_id"]: item for item in csv.DictReader(handle)}
    for mention_id, (candidate_id, surface, start, end) in exact_mentions.items():
        mention = mention_rows.get(mention_id)
        if (
            not mention
            or mention.get("segment_id") != SEGMENT_ID
            or mention.get("candidate_id") != candidate_id
            or mention.get("surface_form") != surface
            or int(mention.get("start_char", -1)) != start
            or int(mention.get("end_char", -1)) != end
            or segment_text[start:end] != surface
        ):
            raise ValueError(f"attribution mention changed or span mismatch: {mention_id}")

    open_before = sum(is_open(item) for item in rows)
    missing_reason_before = sum(is_open(item) and not (item.get("qualifiers") or {}).get("open_endpoint_reason") for item in rows)
    if (open_before, missing_reason_before) != (382, 62):
        raise ValueError(f"unexpected full-table open state: {open_before}, {missing_reason_before}")

    row["subject_candidate_id"] = "cand-0801"
    row["object_candidate_id"] = "cand-0581"
    row["predicate"] = "is-reported-as-first-to-advise-carriera-to-use-pastels"
    q["relation_candidate_note"] = "Haskell reports that most early biographers identify the English signor Colle (candidate cand-0801) as the first to advise Rosalba Carriera (cand-0581) to turn to pastels. This remains a reported attribution; the cited biographies were not independently consulted."
    q.pop("open_endpoint_reason", None)
    row["qualifiers"] = q

    output = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in rows).encode("utf-8")
    open_after = sum(is_open(item) for item in rows)
    missing_reason_after = sum(is_open(item) and not (item.get("qualifiers") or {}).get("open_endpoint_reason") for item in rows)
    if (open_after, missing_reason_after) != (381, 61):
        raise ValueError(f"unexpected resulting open state: {open_after}, {missing_reason_after}")

    print("reviewed=Haskell footnote attribution on p.276 against the existing S2 decision, indexed candidates and exact mention spans")
    print("change=complete the reported Colle-to-Carriera advice relation; preserve its historiographical attribution and unverified citation status")
    print(f"open_endpoints={open_before}->{open_after}; open_without_reason={missing_reason_before}->{missing_reason_after}")
    print(f"book-statements.jsonl sha256 {digest(raw)}->{digest(output)}")
    if args.preview:
        return 0
    if BACKUP.exists():
        raise FileExistsError(f"recovery copy already exists: {BACKUP.name}")
    temp = TABLE.with_name("book-statements.jsonl.tmp-s2-chp10-p276n1-colle-endpoint-20261015")
    if temp.exists():
        raise FileExistsError(f"temporary file already exists: {temp.name}")
    shutil.copy2(TABLE, BACKUP)
    try:
        temp.write_bytes(output)
        temp.replace(TABLE)
    except Exception:
        if temp.exists():
            temp.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={digest(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
