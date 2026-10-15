from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp3-sec-i-l35-43-relations-20261010"
SEGMENT_ID = "chp-3:03_CHP-3_sec_i:l35-43"

EXPECTED_HASHES = {
    STATEMENTS: "1ad47d220b9502852c7932db26e857722a740e2080521d7dfd45529ce65d6583",
    CANDIDATES: "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    MENTIONS: "fb2d4512ace8ebd177abf3279b0a10ad0610aab8038fe03c8b3de33eb6097dba",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "a18f48c7b8bf5b161fa13a7ce26ed2935e72d9a14d555f82dfc1d85f84314255",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

DECISIONS = {
    "st-chp3-seci-l35-43-cozzi-qualified-rejection": (
        True,
        "Haskell reports Cozzi's forceful but qualified rejection of the preceding opinion, with Friedlaender cited in that discussion. Keep 'this opinion' at the printed scope; do not upgrade the disagreement into independently verified scholarship.",
    ),
    "st-chp3-seci-l35-43-pecchiai-history-reference": (
        True,
        "The printed note directs readers to Pecchiai (1952) for a documented history of the Gesu. This records Haskell's bibliographic recommendation; the cited book was not independently consulted.",
    ),
    "st-chp3-seci-l35-43-redig-de-campos-citation": (
        True,
        "The printed note explicitly adds Redig de Campos (1936) alongside the 1923 canonisation volume. Record the citation in connection with the canonisation and paintings account; do not assert that the article independently verifies it.",
    ),
    "st-chp3-seci-l35-43-sacchi-picture-repository": (
        True,
        "Haskell's note reports the Sacchi picture as then being in the Galleria Nazionale di Arte Antica, Rome. Preserve the historical 'now' relative to the book's publication; do not present it as current custody.",
    ),
    "st-chp3-seci-l35-43-trattato-cortona-bracket-identification": (
        True,
        "The printed bracket identifies Britio Prenetteri with Pietro da Cortona as a named author of the cited Trattato. This is the note's identification, not an independent authorship verification.",
    ),
    "st-chp3-seci-l35-43-trattato-ottonelli-bracket-identification": (
        True,
        "The printed bracket identifies Odomenigio Lelonotti da Fanano with Gio. Dom. Ottonelli as a named author of the cited Trattato. This is the note's identification; the full title and edition remain unresolved.",
    ),
}

EXPECTED_TARGETS = {
    "st-chp3-seci-l35-43-cozzi-qualified-rejection": (36, "cand-4991", "cand-4375", "G. Cozzi"),
    "st-chp3-seci-l35-43-redig-de-campos-citation": (38, "cand-4993", "cand-4980", "Redig de Campos"),
    "st-chp3-seci-l35-43-sacchi-picture-repository": (39, "cand-4982", "cand-4142", "Galleria Nazionale"),
    "st-chp3-seci-l35-43-trattato-cortona-bracket-identification": (40, "cand-4979", "cand-0342", "Pietro da Cortona"),
    "st-chp3-seci-l35-43-trattato-ottonelli-bracket-identification": (40, "cand-4979", "cand-1800", "Ottonelli"),
    "st-chp3-seci-l35-43-pecchiai-history-reference": (43, "cand-3112", "cand-4996", "Pecchiai"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qualifiers(row: dict) -> dict:
    value = row.get("qualifiers") or {}
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict):
        raise SystemExit(f"invalid qualifiers for {row.get('statement_id')}")
    return value


def has_endpoint(value: object) -> bool:
    return value is not None and str(value).strip() != ""


def stats(rows: list[dict]) -> dict:
    bilateral = [
        row for row in rows
        if has_endpoint(row.get("subject_candidate_id")) and has_endpoint(row.get("object_candidate_id"))
    ]
    candidates = [row for row in rows if qualifiers(row).get("relation_candidate") is True]
    categories = Counter(
        "true" if qualifiers(row).get("relation_candidate") is True
        else "false" if qualifiers(row).get("relation_candidate") is False
        else "pending"
        for row in bilateral
    )
    open_candidates = sum(
        not (has_endpoint(row.get("subject_candidate_id")) and has_endpoint(row.get("object_candidate_id")))
        for row in candidates
    )
    return {
        "bilateral": len(bilateral),
        "bilateral_true": categories["true"],
        "bilateral_false": categories["false"],
        "bilateral_pending": categories["pending"],
        "relation_candidates_total": len(candidates),
        "relation_candidates_open": open_candidates,
    }


def read_jsonl_lines(raw: bytes) -> list[tuple[dict, bytes, bytes]]:
    result = []
    for line in raw.splitlines(keepends=True):
        body = line.rstrip(b"\r\n")
        ending = line[len(body):]
        row = json.loads(body.decode("utf-8-sig"))
        result.append((row, ending, body))
    return result


def project(raw: bytes, lines: list[tuple[dict, bytes, bytes]]) -> tuple[bytes, dict[str, dict]]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    output = bytearray()
    changed = {}
    for index, (row, ending, original_body) in enumerate(lines):
        statement_id = row.get("statement_id")
        if statement_id in DECISIONS:
            q = qualifiers(row)
            flag, note = DECISIONS[statement_id]
            if "relation_candidate" in q:
                raise SystemExit(f"target already classified: {statement_id}")
            q["relation_candidate"] = flag
            q["relation_candidate_note"] = note
            row["qualifiers"] = q
            changed[statement_id] = q
            encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            if index == 0 and bom:
                encoded = b"\xef\xbb\xbf" + encoded
            output.extend(encoded)
        else:
            output.extend(original_body)
        output.extend(ending)
    return bytes(output), changed


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"SHA mismatch for {path.relative_to(ROOT)}: {actual}")
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage_rows = [row for row in csv.DictReader(handle) if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit(f"unexpected coverage matches: {len(coverage_rows)}")
    coverage = coverage_rows[0]
    if (coverage["disposition"], coverage["migration_status"], coverage["source_line_ranges"]) != (
        "reviewed", "complete", "L36-43"
    ):
        raise SystemExit(f"unexpected S2 coverage row: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    raw = STATEMENTS.read_bytes()
    lines = read_jsonl_lines(raw)
    all_rows = [row for row, _, _ in lines]
    segment_rows = [row for row in all_rows if row.get("segment_id") == SEGMENT_ID]
    targets = {row["statement_id"]: row for row in segment_rows if row.get("statement_id") in DECISIONS}
    if set(targets) != set(DECISIONS) or len(segment_rows) != 12:
        raise SystemExit(f"unexpected segment targets/size: targets={sorted(targets)} rows={len(segment_rows)}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for statement_id, (line_number, subject, obj, quote_part) in EXPECTED_TARGETS.items():
        row = targets[statement_id]
        q = qualifiers(row)
        if "relation_candidate" in q:
            raise SystemExit(f"target already classified: {statement_id}")
        if q.get("source_line_start") != line_number or q.get("source_line_end") != line_number:
            raise SystemExit(f"source locator changed for {statement_id}: {q}")
        if row.get("subject_candidate_id") != subject or row.get("object_candidate_id") != obj:
            raise SystemExit(f"endpoint changed for {statement_id}: {row}")
        if quote_part not in row.get("original_quote", ""):
            raise SystemExit(f"quotation anchor changed for {statement_id}")
        if quote_part not in source_lines[line_number - 1]:
            raise SystemExit(f"source line no longer contains {quote_part!r} at L{line_number}")
        if subject not in candidate_ids or obj not in candidate_ids:
            raise SystemExit(f"unresolved candidate endpoint in {statement_id}")

    before = stats(all_rows)
    expected_before = {
        "bilateral": 8499,
        "bilateral_true": 4530,
        "bilateral_false": 460,
        "bilateral_pending": 3509,
        "relation_candidates_total": 4564,
        "relation_candidates_open": 34,
    }
    if before != expected_before:
        raise SystemExit(f"unexpected pre-write counts: {before}")

    projected, changed = project(raw, lines)
    projected_rows = [row for row, _, _ in read_jsonl_lines(projected)]
    after = stats(projected_rows)
    expected_after = {
        "bilateral": 8499,
        "bilateral_true": 4536,
        "bilateral_false": 460,
        "bilateral_pending": 3503,
        "relation_candidates_total": 4570,
        "relation_candidates_open": 34,
    }
    if len(changed) != len(DECISIONS) or after != expected_after:
        raise SystemExit(f"unexpected projected result: changed={len(changed)} counts={after}")

    print(json.dumps({
        "mode": "dry-run" if args.dry_run else "apply",
        "segment_id": SEGMENT_ID,
        "printed_pages": "64-65; PDF physical pages 2-3",
        "relation_candidates": len(DECISIONS),
        "before": before,
        "after": after,
        "changed_ids": sorted(changed),
        "backup": str(BACKUP.relative_to(ROOT)) if args.apply else None,
    }, ensure_ascii=False, indent=2))
    if args.dry_run:
        return

    shutil.copy2(STATEMENTS, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix="book-statements.s2-l35-43.", suffix=".tmp", dir=TABLES)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(projected)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, STATEMENTS)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise

    written_rows = [row for row, _, _ in read_jsonl_lines(STATEMENTS.read_bytes())]
    written_targets = {row["statement_id"]: row for row in written_rows if row.get("statement_id") in DECISIONS}
    if set(written_targets) != set(DECISIONS):
        raise SystemExit("post-write target set changed; recovery backup retained")
    for statement_id, (flag, note) in DECISIONS.items():
        q = qualifiers(written_targets[statement_id])
        if q.get("relation_candidate") is not flag or q.get("relation_candidate_note") != note:
            raise SystemExit(f"post-write classification mismatch: {statement_id}; recovery backup retained")
    verified = stats(written_rows)
    if verified != expected_after:
        raise SystemExit(f"post-write counts mismatch: {verified}; recovery backup retained")
    print(f"post_write_sha256={sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
