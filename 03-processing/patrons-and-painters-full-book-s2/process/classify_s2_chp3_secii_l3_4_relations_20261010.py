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
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp3-sec-ii-l3-4-relations-20261010"
SEGMENT_ID = "chp-3:03_CHP-3_sec_ii:l3-4"

EXPECTED_HASHES = {
    STATEMENTS: "f0b02dd06a0d97de459422d98238887ff1bbb7d511310590402eca4fdbc2410a",
    CANDIDATES: "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

DECISIONS = {
    "st-chp3-secii-l3-4-farnese-assumed-gesu-patronage": (
        True,
        "Haskell says Alessandro Farnese assumed patronage of the Gesu in 1568. Preserve the source's initial 'gift from Heaven' evaluation and unspecified later drawbacks; this is not an independent assessment of the patronage.",
    ),
    "st-chp3-secii-l3-4-farnese-cardinal-characterization": (
        False,
        "This is Haskell's comparative description of Farnese as the most powerful sixteenth-century cardinal, an attribute of one person rather than a relation between two bounded entities. Preserve it as a source-attributed characterization, not a relation candidate.",
    ),
    "st-chp3-secii-l3-4-farnese-employed-vignola-and-painters": (
        True,
        "Haskell says Farnese employed Vignola as his architect and also employed his own painters. The painters remain unnamed; do not infer separate works, contracts, or commissions.",
    ),
    "st-chp3-secii-l3-4-farnese-ignored-jesuit-wishes": (
        True,
        "This records Haskell's broad claim that Farnese paid no attention to the Jesuits' wishes. No particular decision or event is identified, and the claim is not independently verified here.",
    ),
    "st-chp3-secii-l3-4-gesu-built-by-farnese": (
        True,
        "Haskell says Farnese built the Gesu for the Jesuits. Keep the statement source-attributed and distinct from the separately stated assumption of patronage; the cited history was not independently consulted.",
    ),
    "st-chp3-secii-l3-4-gesu-treated-as-private-property": (
        True,
        "Haskell characterizes Farnese as treating the new church as private property. This is a reported treatment, not proof of legal ownership.",
    ),
    "st-chp3-secii-l3-4-reported-three-beautiful-objects-saying": (
        True,
        "Haskell reports an unspecified saying that Farnese owned Rome's three most beautiful objects, including the Gesu. Preserve the reported-speech layer; the family palace is unidentified and the saying does not establish legal ownership.",
    ),
}

EXPECTED_TARGETS = {
    "st-chp3-secii-l3-4-farnese-assumed-gesu-patronage": (3, 4, "cand-0995", "cand-3112", "assumption of its patronage"),
    "st-chp3-secii-l3-4-farnese-cardinal-characterization": (3, 3, "cand-0995", "", "most powerful of sixteenth-century Cardinals"),
    "st-chp3-secii-l3-4-farnese-employed-vignola-and-painters": (4, 4, "cand-0995", "cand-2775", "own architect Vignola"),
    "st-chp3-secii-l3-4-farnese-ignored-jesuit-wishes": (4, 4, "cand-0995", "cand-1321", "wishes of the Jesuits"),
    "st-chp3-secii-l3-4-gesu-built-by-farnese": (3, 3, "cand-3112", "cand-0995", "built for them by"),
    "st-chp3-secii-l3-4-gesu-treated-as-private-property": (4, 4, "cand-0995", "cand-3112", "treated the new church as his private property"),
    "st-chp3-secii-l3-4-reported-three-beautiful-objects-saying": (4, 4, "cand-0995", "cand-3112", "owned the three most beautiful objects"),
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
        "reviewed", "complete", "L3-4"
    ):
        raise SystemExit(f"unexpected S2 coverage row: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    raw = STATEMENTS.read_bytes()
    lines = read_jsonl_lines(raw)
    all_rows = [row for row, _, _ in lines]
    segment_rows = [row for row in all_rows if row.get("segment_id") == SEGMENT_ID]
    targets = {row["statement_id"]: row for row in segment_rows if row.get("statement_id") in DECISIONS}
    if set(targets) != set(DECISIONS) or len(segment_rows) != 7:
        raise SystemExit(f"unexpected segment targets/size: targets={sorted(targets)} rows={len(segment_rows)}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for statement_id, (line_start, line_end, subject, obj, quote_part) in EXPECTED_TARGETS.items():
        row = targets[statement_id]
        q = qualifiers(row)
        if "relation_candidate" in q:
            raise SystemExit(f"target already classified: {statement_id}")
        if (q.get("source_line_start"), q.get("source_line_end")) != (line_start, line_end):
            raise SystemExit(f"source locator changed for {statement_id}: {q}")
        if row.get("subject_candidate_id") != subject or row.get("object_candidate_id") != obj:
            raise SystemExit(f"endpoint changed for {statement_id}: {row}")
        if quote_part not in row.get("original_quote", ""):
            raise SystemExit(f"quotation anchor changed for {statement_id}")
        if quote_part not in " ".join(source_lines[line_start - 1:line_end]):
            raise SystemExit(f"source lines no longer contain {quote_part!r} for {statement_id}")
        if subject not in candidate_ids or (obj and obj not in candidate_ids):
            raise SystemExit(f"unresolved candidate endpoint in {statement_id}")

    before = stats(all_rows)
    expected_before = {
        "bilateral": 8499,
        "bilateral_true": 4536,
        "bilateral_false": 460,
        "bilateral_pending": 3503,
        "relation_candidates_total": 4570,
        "relation_candidates_open": 34,
    }
    if before != expected_before:
        raise SystemExit(f"unexpected pre-write counts: {before}")

    projected, changed = project(raw, lines)
    projected_rows = [row for row, _, _ in read_jsonl_lines(projected)]
    after = stats(projected_rows)
    expected_after = {
        "bilateral": 8499,
        "bilateral_true": 4542,
        "bilateral_false": 460,
        "bilateral_pending": 3497,
        "relation_candidates_total": 4576,
        "relation_candidates_open": 34,
    }
    if len(changed) != len(DECISIONS) or after != expected_after:
        raise SystemExit(f"unexpected projected result: changed={len(changed)} counts={after}")

    print(json.dumps({
        "mode": "dry-run" if args.dry_run else "apply",
        "segment_id": SEGMENT_ID,
        "printed_page": 65,
        "decisions": {
            "relation_candidates": sum(flag for flag, _ in DECISIONS.values()),
            "nonrelations": sum(not flag for flag, _ in DECISIONS.values()),
        },
        "before": before,
        "after": after,
        "changed_ids": sorted(changed),
        "backup": str(BACKUP.relative_to(ROOT)) if args.apply else None,
    }, ensure_ascii=False, indent=2))
    if args.dry_run:
        return

    shutil.copy2(STATEMENTS, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix="book-statements.s2-chp3-secii-l3-4.", suffix=".tmp", dir=TABLES)
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
