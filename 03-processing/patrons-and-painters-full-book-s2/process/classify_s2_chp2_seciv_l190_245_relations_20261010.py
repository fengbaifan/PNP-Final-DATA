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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-2.pdf"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l190-245"
EXPECTED_HASHES = {
    "table": "6b876781f1d7f5a538167b50bb279b4b4b8a7123f1e02f1b5e7f1cc489b1f2bf",
    "candidates": "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    "coverage": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "source": "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
    "pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
}
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-iv-l190-245-20261010"
TARGET_IDS = {
    "st-chp2-seciv-l190-245-arcadian-shepherds-date-proposal",
    "st-chp2-seciv-l190-245-baldinucci-anecdote",
    "st-chp2-seciv-l190-245-barberini-ceiling-iconography-critique",
    "st-chp2-seciv-l190-245-bentivoglio-branch",
    "st-chp2-seciv-l190-245-cigoli-earlier-story-scenes",
    "st-chp2-seciv-l190-245-claude-will-and-pictures-in-collection",
    "st-chp2-seciv-l190-245-claude-works-locations",
    "st-chp2-seciv-l190-245-contarini-report",
    "st-chp2-seciv-l190-245-fresco-attribution-and-date",
    "st-chp2-seciv-l190-245-later-bernini-account",
    "st-chp2-seciv-l190-245-lost-capture",
    "st-chp2-seciv-l190-245-operatic-performance-date-dispute",
    "st-chp2-seciv-l190-245-palace-transfer-and-earlier-frescoes",
    "st-chp2-seciv-l190-245-panofsky-contact-claim-corrected",
    "st-chp2-seciv-l190-245-portrait-location-and-date",
    "st-chp2-seciv-l190-245-poussin-lost-and-current-locations",
    "st-chp2-seciv-l190-245-poussin-work-locations-and-dedications",
    "st-chp2-seciv-l190-245-rest-flight-owned-by-rospigliosi",
    "st-chp2-seciv-l190-245-taddeo-moral-claim-disputed",
    "st-chp2-seciv-l190-245-tavole-barberini-attribution",
    "st-chp2-seciv-l190-245-valentin-picture-location",
    "st-chp2-seciv-l190-245-venetian-reports-taddeo",
    "st-chp2-seciv-l190-245-vouet-election",
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
    temp.write_bytes(data)
    temp.replace(path)


def preflight():
    paths = {
        "table": STATEMENTS,
        "candidates": CANDIDATES,
        "coverage": COVERAGE,
        "source": SOURCE,
        "pdf": PDF,
    }
    actual_hashes = {name: sha256(path) for name, path in paths.items()}
    if actual_hashes != EXPECTED_HASHES:
        raise SystemExit(
            f"input hashes changed: expected={EXPECTED_HASHES}; actual={actual_hashes}"
        )

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
    pending_ids = {
        row["statement_id"]
        for row in selected
        if row.get("subject_candidate_id")
        and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if len(selected) != 108 or pending_ids != TARGET_IDS:
        raise SystemExit(
            f"segment scope mismatch: rows={len(selected)}, "
            f"pending={len(pending_ids)}, missing={TARGET_IDS-pending_ids}, "
            f"unexpected={pending_ids-TARGET_IDS}"
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
        if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
            raise SystemExit(f"bilateral endpoint missing: {statement_id}")
        if (
            row["subject_candidate_id"] not in candidate_ids
            or row["object_candidate_id"] not in candidate_ids
        ):
            raise SystemExit(f"candidate endpoint missing: {statement_id}")
        if qualifiers.get("relation_candidate") is not None:
            raise SystemExit(f"target is already classified: {statement_id}")
    return rows, by_id, bom, newline, actual_hashes


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows, by_id, bom, newline, hashes = preflight()
    preview = [
        {
            "statement_id": statement_id,
            "predicate": by_id[statement_id].get("predicate"),
            "subject_candidate_id": by_id[statement_id].get("subject_candidate_id"),
            "object_candidate_id": by_id[statement_id].get("object_candidate_id"),
            "relation_candidate": True,
        }
        for statement_id in sorted(TARGET_IDS)
    ]
    if args.dry_run:
        print(json.dumps({"preflight": "passed", "hashes": hashes, "changes": preview}, ensure_ascii=False, indent=2))
        return

    shutil.copy2(STATEMENTS, BACKUP)
    for row in rows:
        if row.get("statement_id") in TARGET_IDS:
            row.setdefault("qualifiers", {})["relation_candidate"] = True
    write_jsonl(STATEMENTS, rows, bom, newline)
    after = sha256(STATEMENTS)
    if after == hashes["table"]:
        raise SystemExit("write-back unexpectedly produced no table change")
    print(json.dumps({
        "applied": len(TARGET_IDS),
        "backup": str(BACKUP.relative_to(ROOT)),
        "before_sha256": hashes["table"],
        "after_sha256": after,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
