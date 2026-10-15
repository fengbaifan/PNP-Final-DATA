from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l106-112"
SEGMENT_SHA256 = "d409bac5a9e5c1caeaf2ed02cdfa8a1a4edc7dac8883ea2be458487bf1ebe001"
SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
STATEMENTS_SHA256 = "fcec9b8c1ff45120e23f9bb8941d3ca18b56ebfca85f4d0d530fd180a4c50b02"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l106-112-20261010")

DECISIONS = {
    "st-chp2-seciv-l106-112-borghese-ludovisi-subjects": "Records Haskell's comparison of the Borghese and Ludovisi subject choices with the more specific Barberini programme; retain the attributed preference.",
    "st-chp2-seciv-l106-112-ceiling-clarity-and-allusions": "Records the relation between Cortona's ceiling, its clear general meaning, and its learned allusions; preserve Haskell's account of visitor appeal.",
    "st-chp2-seciv-l106-112-ceilings-literary-interests": "Records Haskell's claim that Sacchi's and Cortona's ceilings reflect the new court's literary interests.",
    "st-chp2-seciv-l106-112-cortona-literary-display": "Records Cortona's combination of court literary interests with a sense of display; preserve the comparison with prior literary achievement.",
    "st-chp2-seciv-l106-112-court-humanist-comparison": "Records Haskell's comparison between the new court's literary interests and Renaissance humanist interests.",
    "st-chp2-seciv-l106-112-court-painters-adopt-synthesis": "Records the reported adoption of the artistic synthesis by court painters over more than a century.",
    "st-chp2-seciv-l106-112-domenichino-hears-ceiling-comparison": "Records Domenichino's reported comparison of the ceiling's suitability for a secular prince or pope; preserve the nested hearsay qualification.",
    "st-chp2-seciv-l106-112-francesco-controls-academy": "Records Haskell's claim that Cardinal Francesco controlled the Accademia di S. Luca at the time.",
    "st-chp2-seciv-l106-112-francesco-employs-romanelli": "Records Cardinal Francesco's employment of Romanelli for obligations he had undertaken; retain the source's scope.",
    "st-chp2-seciv-l106-112-francesco-funds-academy-church": "Records Cardinal Francesco's financial contribution to rebuilding the Academy church by Pietro da Cortona.",
    "st-chp2-seciv-l106-112-francesco-saw-rubens-cycle": "Records Haskell's qualified inference that Cardinal Francesco was encouraged by seeing Rubens's cycle in Paris; preserve 'very likely' and 'must certainly'.",
    "st-chp2-seciv-l106-112-papal-theme-novelty": "Records Haskell's contextual claim that the ceiling's theme was new in seventeenth-century papal patronage.",
    "st-chp2-seciv-l106-112-princely-flattery-comparison": "Records Haskell's comparative assessment of the princely flattery in the programme; preserve its geographic and evaluative limits.",
    "st-chp2-seciv-l106-112-romanelli-academy-prince-1638": "Records Romanelli's 1638 appointment as Principe of the Academy on Cardinal Francesco's orders.",
    "st-chp2-seciv-l106-112-romanelli-ambition-papal-service": "Records Romanelli's reported ambition to supplant Cortona in the Pope's service; retain the time qualification.",
    "st-chp2-seciv-l106-112-romanelli-church-paintings": "Records Romanelli's reported commissions in churches for which Cardinal Francesco had assumed responsibility.",
    "st-chp2-seciv-l106-112-romanelli-few-admirers": "Records Haskell's account of Romanelli's limited circle of admirers, including the Pope and his nephew.",
    "st-chp2-seciv-l106-112-romanelli-in-charge-tapestry-works": "Records Romanelli's appointment to oversee the Barberini tapestry works.",
    "st-chp2-seciv-l106-112-romanelli-style-assessment": "Records Haskell's comparative assessment of Romanelli's retained mannerisms and qualities in relation to Cortona; retain the evaluative attribution.",
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed S2 classifications")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    require(digest(raw) == STATEMENTS_SHA256, "statement table SHA-256 changed; re-review before writing")
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"

    segments = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    require(segment is not None, "segment metadata missing")
    require(segment.get("sha256") == SEGMENT_SHA256, "segment metadata hash changed")
    require(segment.get("asset_sha256") == SOURCE_SHA256, "source asset hash changed")
    require(digest(SOURCE.read_bytes()) == SOURCE_SHA256, "source file changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    require(digest(source_text.encode("utf-8")) == SEGMENT_SHA256, "source segment content changed")
    require(source_lines[105] == "[Page 53]", "print page anchor changed")
    require("the Borghese and the Ludovisi" in source_text, "opening passage changed")
    require("In 1638 he was made Principe" in source_text, "closing passage changed")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage_rows = list(csv.DictReader(handle))
    coverage = next((row for row in coverage_rows if row.get("segment_id") == SEGMENT_ID), None)
    require(
        coverage is not None
        and coverage.get("disposition") == "reviewed"
        and coverage.get("migration_status") == "complete",
        "segment coverage is not complete",
    )

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    require(len(by_id) == len(rows), "duplicate statement IDs in table")
    pending = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT_ID
        and row.get("subject_candidate_id")
        and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") not in (True, False)
    }
    require(pending == set(DECISIONS), f"pending bilateral set changed: {sorted(pending)}")

    for statement_id, note in DECISIONS.items():
        row = by_id[statement_id]
        require(row.get("original_quote") in source_text, f"source quote mismatch: {statement_id}")
        row["qualifiers"]["relation_candidate"] = True
        row["qualifiers"]["relation_candidate_note"] = note

    output = (b"\xef\xbb\xbf" if bom else b"") + newline.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        for row in rows
    ) + newline
    bilateral = [row for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    counts = {
        "relation_true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral),
        "relation_false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral),
        "unclassified": sum(
            (row.get("qualifiers") or {}).get("relation_candidate") not in (True, False)
            for row in bilateral
        ),
    }
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "classified_true": len(DECISIONS),
        "classified_false": 0,
        "bilateral_after": counts,
        "sha256_before": digest(raw),
        "sha256_after": digest(output),
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry-run only. Pass --apply to write.")
        return

    if BACKUP.exists():
        require(digest(BACKUP.read_bytes()) == STATEMENTS_SHA256, f"backup exists with unexpected contents: {BACKUP.name}")
    else:
        shutil.copy2(TABLE, BACKUP)
    handle = tempfile.NamedTemporaryFile(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent, delete=False)
    temp_path = Path(handle.name)
    try:
        with handle:
            handle.write(output)
        os.replace(temp_path, TABLE)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    require(digest(TABLE.read_bytes()) == digest(output), "post-write SHA-256 mismatch")
    print(json.dumps({"result": "applied", "backup": BACKUP.name, "sha256_after": digest(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
