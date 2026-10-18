from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp7-p185-citation-mapping-20261019")

FIXES = {
    "st-chp7-p185-n2-cite-hautecoeur": {
        "object": "cand-7097",
        "source_line": 358,
        "original_quote": "1 de Cosnac, pp. 169 ff. 2 Hautecoeur, pp. 39-49.",
        "old_locator": "Hautecœur, Rome et la Renaissance de la peinture française (1943), pp. 39–49",
        "locator": "Hautecoeur, pp. 39-49",
        "claim": "The p.185 footnote text records 'Hautecoeur, pp. 39-49.' It gives author and pages only. The publication endpoint is mapped by cross-reference to the sole Hautecoeur entry in the book bibliography, L’Histoire des Châteaux du Louvre et des Tuileries (Paris, 1927); the cited pages were not independently read.",
        "qualification": "The footnote gives author and page locator only. The work is mapped by cross-reference to the unique matching bibliography entry; the cited pages were not independently read.",
    },
    "st-chp7-p185-n3-cite-hautecoeur": {
        "object": "cand-7097",
        "source_line": 359,
        "original_quote": "3 ibid., pp. 84-9. 4 Alazard, pp. 18-28 and 55-86.",
        "old_locator": "Hautecœur, Rome et la Renaissance de la peinture française (1943), pp. 84–89 (ibid. to footnote 2)",
        "locator": "ibid., pp. 84-9 (resolves to footnote 2)",
        "claim": "The p.185 footnote text records 'ibid., pp. 84-9,' referring to note 2. The publication endpoint follows that ibid. reference and is mapped to the sole Hautecoeur entry in the book bibliography, L’Histoire des Châteaux du Louvre et des Tuileries (Paris, 1927); the cited pages were not independently read.",
        "qualification": "Ibid. resolves to footnote 2. The work is mapped by cross-reference to the unique matching bibliography entry; the cited pages were not independently read.",
    },
    "st-chp7-p185-n4-cite-alazard": {
        "object": "cand-7099",
        "source_line": 359,
        "original_quote": "3 ibid., pp. 84-9. 4 Alazard, pp. 18-28 and 55-86.",
        "old_locator": "Alazard, La Vie artistique au temps de Mazarin (1931), pp. 18–28 and 55–86",
        "locator": "Alazard, pp. 18-28 and 55-86",
        "claim": "The p.185 footnote text records 'Alazard, pp. 18-28 and 55-86.' It gives author and pages only. The publication endpoint is mapped by cross-reference to the sole Alazard entry in the book bibliography, L’Abbé Luigi Strozzi correspondant artistique de Mazarin, de Colbert, de Louvois et de La Teulière (Paris, 1924); the cited pages were not independently read.",
        "qualification": "The footnote gives author and page locator only. The work is mapped by cross-reference to the unique matching bibliography entry; the cited pages were not independently read.",
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Correct p.185 footnote locators without changing citation endpoints.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes and retain a recovery backup")
    args = parser.parse_args()

    before = TABLE.read_bytes()
    bom = b"\xef\xbb\xbf" if before.startswith(b"\xef\xbb\xbf") else b""
    raw_lines = (before[len(bom) :]).splitlines(keepends=True)
    rows = []
    line_by_id = {}
    row_by_id = {}
    for index, raw_line in enumerate(raw_lines):
        line_body = raw_line.rstrip(b"\r\n")
        if not line_body.strip():
            continue
        row = json.loads(line_body.decode("utf-8"))
        rows.append(row)
        line_by_id[row["statement_id"]] = index
        row_by_id[row["statement_id"]] = row
    if len(line_by_id) != len(rows):
        raise SystemExit("statement IDs are not unique")

    changed = []
    replacement_by_line = {}
    for statement_id, fix in FIXES.items():
        line_index = line_by_id.get(statement_id)
        if line_index is None:
            raise SystemExit(f"missing statement: {statement_id}")
        row = row_by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        citations = qualifiers.get("citations") or []
        if (
            row.get("object_candidate_id") != fix["object"]
            or row.get("predicate") != "cites"
            or row.get("original_quote") != fix["original_quote"]
            or qualifiers.get("source_line_start") != fix["source_line"]
            or qualifiers.get("citation_locator") != fix["old_locator"]
            or len(citations) != 1
            or citations[0].get("publication_candidate_id") != fix["object"]
            or citations[0].get("locator") != fix["old_locator"]
        ):
            raise SystemExit(f"evidence guard failed: {statement_id}")

        q = dict(qualifiers)
        q.update(
            {
                "claim": fix["claim"],
                "qualification": fix["qualification"],
                "citation_locator": fix["locator"],
                "citations": [
                    {
                        **citations[0],
                        "locator": fix["locator"],
                    }
                ],
                "relation_candidate_note": "S2 citation lead only: the footnote supplies the author and locator; the work endpoint is mapped by cross-reference to the unique matching bibliography entry. The cited pages were not independently read, and no S6 edge is created.",
            }
        )
        row["qualifiers"] = q
        ending = b"\r\n" if raw_lines[line_index].endswith(b"\r\n") else b"\n"
        replacement_by_line[line_index] = json.dumps(row, ensure_ascii=False).encode("utf-8") + ending
        changed.append(
            {
                "statement_id": statement_id,
                "object_candidate_id": row["object_candidate_id"],
                "locator_before": fix["old_locator"],
                "locator_after": fix["locator"],
            }
        )

    output = bom + b"".join(replacement_by_line.get(i, line) for i, line in enumerate(raw_lines))
    report = {
        "mode": "apply" if args.apply else "dry_run",
        "statements_changed": changed,
        "statement_count": len(rows),
        "before_sha256": digest(before),
        "after_sha256": digest(output),
        "backup": str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return
    if BACKUP.exists() and BACKUP.read_bytes() != before:
        raise SystemExit(f"refusing to overwrite a different recovery backup: {BACKUP.name}")
    if TABLE.read_bytes() != before:
        raise SystemExit("statement table changed after preflight")
    if not BACKUP.exists():
        shutil.copy2(TABLE, BACKUP)
    atomic_write(TABLE, output)
    if digest(TABLE.read_bytes()) != report["after_sha256"]:
        shutil.copy2(BACKUP, TABLE)
        raise SystemExit("post-write hash mismatch; original restored from recovery backup")
    print("applied; recovery backup retained; statement hash verified")


if __name__ == "__main__":
    main()
