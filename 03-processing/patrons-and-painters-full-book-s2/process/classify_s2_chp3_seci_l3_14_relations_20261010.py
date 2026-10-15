from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
SEGMENT_ID = "chp-3:03_CHP-3_sec_i:l3-14"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp3-sec-i-l3-14-20261010"
EXPECTED_HASHES = {
    "table": "b53a1875e5df3950f699ecf64aefb942801cc4cba3d09b9d38983db9a1714151",
    "candidates": "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    "coverage": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "source": "a18f48c7b8bf5b161fa13a7ce26ed2935e72d9a14d555f82dfc1d85f84314255",
    "pdf": "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}
TARGET_IDS = {
    "st-chp3-seci-l3-14-early-order-origins",
    "st-chp3-seci-l3-14-grey-quoted-jesuit-description",
    "st-chp3-seci-l3-14-mother-churches-baroque-inference",
    "st-chp3-seci-l3-14-orders-rise-and-works",
}
NOTES = {
    "st-chp3-seci-l3-14-early-order-origins": (
        "This is Haskell's broad historical account of early religious Orders resisting "
        "worldly members of the papal court and, at times, popes. The Orders, individual "
        "courtiers, popes, saints, and natural leaders remain unspecified; preserve the "
        "continuation to the next source segment."
    ),
    "st-chp3-seci-l3-14-grey-quoted-jesuit-description": (
        "This records Grey Brydges' attributed description of Jesuit churches as quoted "
        "by Haskell. The principal church is unnamed, and the note's Horae Subsecivae "
        "citation versus the prose title Discourse of Rome remains unresolved; do not "
        "treat the quoted account as independently verified."
    ),
    "st-chp3-seci-l3-14-mother-churches-baroque-inference": (
        "The source relates the Orders' mother churches to Baroque taste as an apparent "
        "embodiment; deliberate use as propaganda is explicitly an inference. Preserve "
        "that qualification and do not assert an established intention."
    ),
    "st-chp3-seci-l3-14-orders-rise-and-works": (
        "The source explicitly associates the religious Orders with 'their churches' "
        "and describes those churches' extension, rebuilding, decoration, and copying. "
        "This is a broad group-level account, not proof of legal ownership or of which "
        "agents carried out the work; the artists remain unnamed."
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def read_jsonl(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    decoded = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in decoded else "\n"
    rows = [json.loads(line) for line in decoded.splitlines() if line.strip()]
    return rows, bom, newline


def write_jsonl(path: Path, rows, bom: bool, newline: str) -> None:
    text = newline.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows
    ) + newline
    data = (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")
    temp = path.with_suffix(path.suffix + ".s2tmp")
    if temp.exists():
        raise SystemExit(f"temporary output already exists: {temp}")
    temp.write_bytes(data)
    temp.replace(path)


def counts(rows):
    bilateral = [
        row for row in rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
    ]
    true_bilateral = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        for row in bilateral
    )
    false_bilateral = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is False
        for row in bilateral
    )
    pending = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is None
        for row in bilateral
    )
    true_total = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        for row in rows
    )
    open_true = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
        for row in rows
    )
    return {
        "bilateral": len(bilateral),
        "classified_relation": true_bilateral,
        "classified_nonrelation": false_bilateral,
        "pending": pending,
        "relation_candidates_total": true_total,
        "relation_candidates_open": open_true,
    }


def preflight():
    paths = {
        "table": STATEMENTS,
        "candidates": CANDIDATES,
        "coverage": COVERAGE,
        "source": SOURCE,
        "pdf": PDF,
    }
    actual = {name: sha256(path) for name, path in paths.items()}
    if actual != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: expected={EXPECTED_HASHES}; actual={actual}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = [
            row for row in csv.DictReader(handle)
            if row.get("segment_id") == SEGMENT_ID
        ]
    if (
        len(coverage) != 1
        or coverage[0].get("disposition") != "reviewed"
        or coverage[0].get("migration_status") != "complete"
    ):
        raise SystemExit(f"coverage preflight failed: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    rows, bom, newline = read_jsonl(STATEMENTS)
    selected = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    by_id = {row.get("statement_id"): row for row in selected}
    pending = {
        row["statement_id"]
        for row in selected
        if row.get("subject_candidate_id")
        and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if pending != TARGET_IDS:
        raise SystemExit(
            f"pending statement scope changed: missing={TARGET_IDS-pending}; unexpected={pending-TARGET_IDS}"
        )
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for statement_id in sorted(TARGET_IDS):
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        start, end = qualifiers.get("source_line_start"), qualifiers.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
            raise SystemExit(f"invalid source line anchor: {statement_id}")
        anchor = normalize("\n".join(source_lines[start - 1:end]))
        if normalize(row.get("original_quote", "")) not in anchor:
            raise SystemExit(f"source quote does not match line anchor: {statement_id}")
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint not in candidate_ids:
                raise SystemExit(f"candidate endpoint missing: {statement_id}: {endpoint}")

    before = counts(rows)
    expected_before = {
        "bilateral": 8500,
        "classified_relation": 4487,
        "classified_nonrelation": 459,
        "pending": 3554,
        "relation_candidates_total": 4517,
        "relation_candidates_open": 30,
    }
    if before != expected_before:
        raise SystemExit(f"unexpected relation counts before write: {before}")

    projected = []
    for row in rows:
        if row.get("statement_id") in TARGET_IDS:
            row = dict(row)
            qualifiers = dict(row.get("qualifiers") or {})
            qualifiers["relation_candidate"] = True
            qualifiers["relation_candidate_note"] = NOTES[row["statement_id"]]
            row["qualifiers"] = qualifiers
        projected.append(row)
    after = counts(projected)
    expected_after = {
        "bilateral": 8500,
        "classified_relation": 4491,
        "classified_nonrelation": 459,
        "pending": 3550,
        "relation_candidates_total": 4521,
        "relation_candidates_open": 30,
    }
    if after != expected_after:
        raise SystemExit(f"unexpected projected relation counts: {after}")
    return rows, projected, bom, newline, actual, before, after


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows, projected, bom, newline, hashes, before, after = preflight()
    preview = [
        {
            "statement_id": statement_id,
            "predicate": next(row["predicate"] for row in rows if row.get("statement_id") == statement_id),
            "subject_candidate_id": next(row["subject_candidate_id"] for row in rows if row.get("statement_id") == statement_id),
            "object_candidate_id": next(row["object_candidate_id"] for row in rows if row.get("statement_id") == statement_id),
            "relation_candidate": True,
            "relation_candidate_note": NOTES[statement_id],
        }
        for statement_id in sorted(TARGET_IDS)
    ]
    if args.dry_run:
        print(json.dumps({
            "preflight": "passed",
            "hashes": hashes,
            "changes": preview,
            "counts_before": before,
            "counts_after": after,
        }, ensure_ascii=False, indent=2))
        return

    shutil.copy2(STATEMENTS, BACKUP)
    write_jsonl(STATEMENTS, projected, bom, newline)
    written, _, _ = read_jsonl(STATEMENTS)
    verified = counts(written)
    if verified != after:
        raise SystemExit(f"post-write count verification failed: {verified}; backup preserved")
    print(json.dumps({
        "applied": len(TARGET_IDS),
        "backup": str(BACKUP.relative_to(ROOT)),
        "before_sha256": hashes["table"],
        "after_sha256": sha256(STATEMENTS),
        "verified_counts": verified,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
