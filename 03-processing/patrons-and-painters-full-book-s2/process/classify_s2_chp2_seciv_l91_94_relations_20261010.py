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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l91-94"
SEGMENT_SHA256 = "9d24f560848d29aca7437cce39e501eba7b6b5352e2ddce942c713418d352fe1"
SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
STATEMENTS_SHA256 = "1f9a6b483d30f0d2f2cecec8d5255c1292ec544e8b86c2a79f636c065bfc0472"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l91-94-20261010")

DECISIONS = {
    "st-chp2-seciv-l91-94-antonio-only-barberini-family-champion": (
        True,
        "Records Antonio's reported advocacy for the Divine Wisdom fresco; retain Haskell's scope that he was its only outright champion within the family.",
    ),
    "st-chp2-seciv-l91-94-bees-feature-in-surrounding-friezes": (
        True,
        "Records the bees as a motif in the painted and stucco friezes surrounding the fresco.",
    ),
    "st-chp2-seciv-l91-94-bracciolini-accompanies-maffeo-travel-continuation": (
        True,
        "Records Bracciolini's service and travel with Maffeo; the destination continues into the following segment.",
    ),
    "st-chp2-seciv-l91-94-bracciolini-called-in-to-devise-family-programme": (
        True,
        "Records Bracciolini's role in devising the programme for Barberini family glory.",
    ),
    "st-chp2-seciv-l91-94-bracciolini-has-reason-to-flatter-barberini": (
        True,
        "Records Haskell's attributed account of Bracciolini's flattery toward the Barberini; preserve it as an authorial characterization of motive.",
    ),
    "st-chp2-seciv-l91-94-bracciolini-programme-executed-by-cortona-for-family-glory": (
        True,
        "Connects the programme's author, execution by Cortona, and stated purpose of Barberini glorification; preserve Haskell's evaluative language.",
    ),
    "st-chp2-seciv-l91-94-bracciolini-serves-maffeo-as-secretary": (
        True,
        "Records Bracciolini's reported service as Maffeo Barberini's secretary; no exact dates are supplied.",
    ),
    "st-chp2-seciv-l91-94-camassei-small-room-work-judged-insufficient-for-great-hall": (
        True,
        "Records Haskell's assessment of Camassei's suitability for the planned great-hall commission, not a settled judgment about his ability in general.",
    ),
    "st-chp2-seciv-l91-94-cardinal-francesco-backs-cortona": (
        True,
        "Records Cardinal Francesco's reported support for Cortona.",
    ),
    "st-chp2-seciv-l91-94-cortona-already-engaged-on-chapel-frescoes": (
        True,
        "Records Cortona's prior engagement on the chapel frescoes; the chapel remains unnamed here.",
    ),
    "st-chp2-seciv-l91-94-cortona-starts-great-ceiling-end-1632": (
        True,
        "Connects Cortona to the great ceiling and preserves the approximate start and six-or-seven-year duration reported by Haskell.",
    ),
    "st-chp2-seciv-l91-94-divine-wisdom-fresco-admired-in-rome": (
        True,
        "Records the reported reception of the fresco among certain circles in Rome; the audience is not further identified.",
    ),
    "st-chp2-seciv-l91-94-great-ceiling-designed-as-secular-record-of-ambitions": (
        True,
        "Records the ceiling's stated commemorative purpose in relation to Barberini ambitions.",
    ),
    "st-chp2-seciv-l91-94-great-room-originally-planned-for-camassei": (
        True,
        "Records the original plan to assign the principal reception-room to Camassei; retain that this was a plan later displaced.",
    ),
    "st-chp2-seciv-l91-94-jesuit-advisers-back-cortona": (
        True,
        "Records the reported support for Cortona by unnamed Jesuit advisers of the Pope; do not infer their identities.",
    ),
    "st-chp2-seciv-l91-94-laurel-features-in-surrounding-friezes": (
        True,
        "Records the laurel emblem as a motif in the painted and stucco friezes surrounding the fresco.",
    ),
    "st-chp2-seciv-l91-94-love-and-fear-control-lust-and-wrath": (
        True,
        "Records the allegorical actions among personified figures in the fresco; do not infer a one-to-one pairing beyond the text.",
    ),
    "st-chp2-seciv-l91-94-sacchi-painting-technique-and-colour-described": (
        True,
        "Connects Sacchi's described execution and composition to the fresco; retain this as Haskell's formal assessment.",
    ),
    "st-chp2-seciv-l91-94-sacchi-treats-cosmic-conceit-with-severity": (
        True,
        "Records Sacchi's treatment of the fresco's conceit as characterized by Haskell; preserve the author's comparison and evaluation.",
    ),
    "st-chp2-seciv-l91-94-sacchi-work-judged-to-lack-urgency-and-sublimity": (
        True,
        "Records Haskell's aesthetic evaluation of Sacchi's subject and work; do not recast it as an objective property or settled consensus.",
    ),
    "st-chp2-seciv-l91-94-sun-conventional-emblem-for-wisdom": (
        True,
        "Records the reported symbolic relation between the Sun and Wisdom, including the source's statement that it was conventional.",
    ),
    "st-chp2-seciv-l91-94-taddeo-described-as-camassei-protector": (
        True,
        "Records Taddeo's reported patron-protege relation with Camassei; retain the temporal qualification 'newly acquired'.",
    ),
    "st-chp2-seciv-l91-94-wisdom-attributes-personified-as-maidens": (
        True,
        "Records the fresco's allegorical representation of Wisdom's attributes or manifestations; the list is explicitly non-exhaustive.",
    ),
    "st-chp2-seciv-l91-94-wisdom-figure-emits-sun": (
        True,
        "Completes the cross-page iconographic description by linking the Sun to the enthroned Wisdom figure in the fresco.",
    ),
}

ALREADY_CLASSIFIED = {
    "st-chp2-seciv-l91-94-bees-are-barberini-family-insignia",
    "st-chp2-seciv-l91-94-laurel-is-barberini-family-insignia",
    "st-chp2-seciv-l91-94-sun-is-barberini-family-insignia",
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
    source_raw = SOURCE.read_bytes()
    require(digest(source_raw) == SOURCE_SHA256, "source file changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    require(digest(source_text.encode("utf-8")) == SEGMENT_SHA256, "source segment content changed")
    require(source_lines[90] == "[Page 51]", "print page anchor changed")
    require("This Sun serves a double, punning purpose" in source_lines[91], "iconographic passage changed")

    coverage_rows = list(csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline="")))
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
    already = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT_ID
        and row.get("subject_candidate_id")
        and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") in (True, False)
    }
    require(pending == set(DECISIONS), f"pending bilateral set changed: {sorted(pending)}")
    require(already == ALREADY_CLASSIFIED, f"preclassified bilateral set changed: {sorted(already)}")
    for statement_id, (decision, note) in DECISIONS.items():
        row = by_id[statement_id]
        require(row.get("original_quote") in source_text, f"source quote mismatch: {statement_id}")
        row["qualifiers"]["relation_candidate"] = decision
        row["qualifiers"]["relation_candidate_note"] = note

    output = (b"\xef\xbb\xbf" if bom else b"") + newline.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        for row in rows
    ) + newline
    bilateral = [
        row for row in rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
    ]
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
        "already_classified_true": len(ALREADY_CLASSIFIED),
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
