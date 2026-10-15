from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
EXPECTED_TABLE_SHA = "1ade5faf6b6aa1c7cabb9efc772e6610b072b3ab80dae7b2bf2cc3c7c97e9c7c"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp6-footnote-relations-20261010")
SEGMENT = "chp-6:06_CHP-6_sec_i:l120-157"

CLASSIFICATIONS = {
    "st-chp6-notes-l123-p148-n2": (
        "The note explicitly describes Bernini's commissions from Innocent X and names the Equestrian statue of Constantine. Preserve the claim's 'only important' scope as Haskell's wording; this is an S2 candidate, not independent verification or a formal edge."
    ),
    "st-chp6-notes-l128-p149-n6": (
        "The note explicitly says the poems contain a eulogistic account of Camillo Pamfili's patronage. This is a reported work-subject relation; the poems were not independently examined and no authorship by Pamfili is implied."
    ),
}

EXPECTED_ENDPOINTS = {
    "st-chp6-notes-l123-p148-n2": ("cand-0312", "cand-6353"),
    "st-chp6-notes-l128-p149-n6": ("cand-1814", "cand-6357"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def complete(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def counts(rows: list[dict]) -> dict[str, int]:
    flag = lambda row: (row.get("qualifiers") or {}).get("relation_candidate")
    true_rows = [row for row in rows if flag(row) is True]
    false_rows = [row for row in rows if flag(row) is False]
    return {
        "statements": len(rows),
        "relation_true": len(true_rows),
        "relation_true_with_two_endpoints": sum(complete(row) for row in true_rows),
        "relation_true_open": sum(not complete(row) for row in true_rows),
        "relation_false": len(false_rows),
        "double_endpoint_unclassified": sum(complete(row) and flag(row) not in (True, False) for row in rows),
    }


def write_atomic(path: Path, payload: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".tmp-", delete=False) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed S2 classifications; default is dry-run")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    require(sha256(TABLE) == EXPECTED_TABLE_SHA, "book-statements.jsonl changed since review")
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    require(set(CLASSIFICATIONS) <= set(by_id), "reviewed statement missing")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    source_text = "\n".join(source_lines)
    for path, label in [(CANDIDATES, "candidate table"), (COVERAGE, "coverage table")]:
        require(path.exists(), f"{label} missing")
    candidate_text = CANDIDATES.read_text(encoding="utf-8-sig")
    coverage_text = COVERAGE.read_text(encoding="utf-8-sig")
    require(SEGMENT in coverage_text, "reviewed segment missing from S2 coverage")

    for statement_id in CLASSIFICATIONS:
        row = by_id[statement_id]
        q = row.get("qualifiers") or {}
        require(row.get("predicate") == "footnote_claim", f"{statement_id} predicate changed")
        require(row.get("segment_id") == SEGMENT, f"{statement_id} segment changed")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == EXPECTED_ENDPOINTS[statement_id],
                f"{statement_id} endpoints changed")
        require(q.get("relation_candidate") not in (True, False), f"{statement_id} already classified")
        start, end = q.get("source_line_start"), q.get("source_line_end")
        require(isinstance(start, int) and start == end and 1 <= start <= len(source_lines),
                f"{statement_id} source anchor invalid")
        require(row.get("original_quote") in source_text, f"{statement_id} source quote no longer matches")
        require(all(candidate_id in candidate_text for candidate_id in EXPECTED_ENDPOINTS[statement_id]),
                f"{statement_id} endpoint candidate missing")

    before = counts(rows)
    require(before == {
        "statements": 12684,
        "relation_true": 3774,
        "relation_true_with_two_endpoints": 3758,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4317,
    }, f"unexpected statement counts: {before}")

    for statement_id, note in CLASSIFICATIONS.items():
        q = dict(by_id[statement_id].get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        by_id[statement_id]["qualifiers"] = q

    after = counts(rows)
    require(after == {
        "statements": 12684,
        "relation_true": 3776,
        "relation_true_with_two_endpoints": 3760,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4315,
    }, f"unexpected projected counts: {after}")

    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    payload = b"".join(output)

    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified": list(CLASSIFICATIONS),
        "before": before,
        "after": after,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    require(not BACKUP.exists(), "recovery backup already exists")
    shutil.copy2(TABLE, BACKUP)
    try:
        write_atomic(TABLE, payload)
        written = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        require(counts(written) == after, "post-write counts differ from preview")
        written_by_id = {row["statement_id"]: row for row in written}
        require(all((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is True
                    for sid in CLASSIFICATIONS), "classification not persisted")
        print(json.dumps({"result": "applied", "counts": counts(written), "sha256": sha256(TABLE),
                          "backup": str(BACKUP.relative_to(ROOT))}, ensure_ascii=False, indent=2))
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise


if __name__ == "__main__":
    main()
