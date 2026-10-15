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
EXPECTED_SHA = "66985c0d28adc747f98ed4f30dfdda50323bcac7f3fb2c3c687fc37fc8e17697"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-explicit-relations-20261010")

SPECS = {
    "st-chp4-sec-ii-p102-footnote2-vouet-letters-addressed-to": (
        "letters from Vouet to Cassiano of 1621",
        "The footnote explicitly identifies 1621 letters from Vouet to Cassiano. This is a source-attributed archive-to-addressee candidate; the cited letters were not independently consulted.",
    ),
    "st-chp4-sec-ii-p103-footnote2-pietro-letters-addressed-to": (
        "Pietro’s letters to him",
        "The note identifies Pietro da Cortona's letters to 'him'; the preceding prose identifies Cassiano as the recipient. This remains a source-attributed candidate, and the cited letters were not independently consulted.",
    ),
    "st-chp6-p165-n3-friend": (
        "Among these friends was the great violinist Arcangelo CoreUi",
        "The footnote explicitly names Corelli as one of Ottoboni's friends. No collaboration or formal affiliation is inferred.",
    ),
    "st-chp7-p190-i21": (
        "Salvator Rosa’s friend Carlo de Rossi",
        "The passage explicitly describes Carlo de Rossi as Salvator Rosa's friend; no additional patronage or collaboration is inferred.",
    ),
    "st-chp2-seci-l3-7-birth": (
        "was born in Florence in 1568",
        "The text explicitly states Maffeo Barberini was born in Florence in 1568. The claim remains attributed to the book and is not externally verified here.",
    ),
    "st-chp3-seciv-l118-128-pozzo-born-in-trent": (
        "Pozzo, who was born in Trent",
        "The text explicitly states Andrea Pozzo was born in Trent. The claim remains attributed to the book and is not externally verified here.",
    ),
    "st-chp1-l139-141-montalto-quote": (
        "carried on with",
        "The quoted biography explicitly reports Peretti-Montalto continuing the project at S. Andrea della Valle; attribution remains with Haskell's quotation of that source.",
    ),
    "st-chp1-l147-montalto-plan-continuation": (
        "his plans to the glory of God",
        "This source continuation completes the same person-to-project claim with the stated purpose. It remains a source-anchored S2 candidate, not a second formal S6 edge.",
    ),
    "st-chp1-l26-27-gregory-precedent": (
        "XV (1621-1623), had set a pattern",
        "Haskell explicitly says Gregory XV set a pattern Urban VIII followed, with the relative qualification 'to a lesser extent' retained.",
    ),
    "st-chp1-l26-27-paul-precedent": (
        "Paul V (1605-1621)",
        "Haskell explicitly says Paul V set a pattern Urban VIII followed. This is a source-specific historical relation candidate, not a formal S6 edge.",
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows():
    raw = TABLE.read_bytes()
    require(sha256(TABLE) == EXPECTED_SHA, "book-statements.jsonl changed since review")
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()]
    require(len({r["statement_id"] for r in rows}) == len(rows), "duplicate statement_id")
    by_id = {r["statement_id"]: r for r in rows}
    require(set(SPECS) <= set(by_id), "one or more reviewed statement IDs are absent")

    for statement_id, (expected_text, _) in SPECS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        require("relation_candidate" not in qualifiers, f"{statement_id} already classified")
        require(row.get("subject_candidate_id") and row.get("object_candidate_id"),
                f"{statement_id} lacks a candidate endpoint")
        start = qualifiers.get("source_line_start")
        end = qualifiers.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int) and start <= end,
                f"{statement_id} has no valid source line anchor")
        source = ROOT / row["source_file"]
        lines = source.read_text(encoding="utf-8").splitlines()
        require(end <= len(lines) and any(expected_text in lines[n - 1] for n in range(start, end + 1)),
                f"{statement_id} source text no longer matches the reviewed evidence")

    return rows, bom, newline


def counts(rows: list[dict]) -> dict[str, int]:
    def flag(row):
        return (row.get("qualifiers") or {}).get("relation_candidate")

    true_rows = [r for r in rows if flag(r) is True]
    false_rows = [r for r in rows if flag(r) is False]
    complete = lambda r: bool(r.get("subject_candidate_id") and r.get("object_candidate_id"))
    unclassified_double = sum(
        complete(r) and flag(r) not in (True, False) for r in rows
    )
    return {
        "statements": len(rows),
        "relation_true": len(true_rows),
        "relation_true_with_two_endpoints": sum(complete(r) for r in true_rows),
        "relation_true_open": sum(not complete(r) for r in true_rows),
        "relation_false": len(false_rows),
        "double_endpoint_unclassified": unclassified_double,
    }


def serialize(rows: list[dict], bom: bool, newline: bytes) -> bytes:
    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    return b"".join(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write reviewed S2 classifications; default is dry-run")
    args = parser.parse_args()
    rows, bom, newline = read_rows()
    before = counts(rows)
    require(before == {
        "statements": 12682,
        "relation_true": 3682,
        "relation_true_with_two_endpoints": 3666,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4407,
    }, f"unexpected before counts: {before}")

    by_id = {r["statement_id"]: r for r in rows}
    for statement_id, (_, note) in SPECS.items():
        qualifiers = dict(by_id[statement_id].get("qualifiers") or {})
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note
        by_id[statement_id]["qualifiers"] = qualifiers

    after = counts(rows)
    require(after == {
        "statements": 12682,
        "relation_true": 3692,
        "relation_true_with_two_endpoints": 3676,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4397,
    }, f"unexpected projected counts: {after}")
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "reviewed_statement_count": len(SPECS),
        "statement_ids": list(SPECS),
        "before": before,
        "after": after,
        "source_anchors_checked": len(SPECS),
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    require(not BACKUP.exists(), f"recovery backup already exists: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    temp_path = None
    try:
        payload = serialize(rows, bom, newline)
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".tmp-", delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, TABLE)
        written = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        require(counts(written) == after, "post-write counts do not match preview")
        written_by_id = {r["statement_id"]: r for r in written}
        require(all((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is True for sid in SPECS),
                "one or more classifications were not persisted")
        print(json.dumps({
            "result": "applied",
            "counts": counts(written),
            "sha256": sha256(TABLE),
            "backup": str(BACKUP.relative_to(ROOT)),
        }, ensure_ascii=False, indent=2))
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    main()
