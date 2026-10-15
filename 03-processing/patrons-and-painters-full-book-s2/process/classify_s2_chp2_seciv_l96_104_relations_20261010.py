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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l96-104"
SEGMENT_SHA256 = "7f2a37d9ff4614cf577a2e70953139103c18b8f4e0698fa2c5c729a83031bf30"
SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
STATEMENTS_SHA256 = "e8f17c8c391e1f2998287ab4bd6abbd7a2021e341e639e0ce29a280d191c407b"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l96-104-20261010")

DECISIONS = {
    "st-chp2-seciv-l96-104-abundance-younger-antonio": (
        "Records the reported iconographic identification of Abundance with Cardinal Antonio and the accompanying granary interpretation; keep both attributed to interpreters.",
    ),
    "st-chp2-seciv-l96-104-antonio-bishop-sinigaglia": (
        "Records Antonio's reported appointment/status as Bishop of Sinigaglia from 1627.",
    ),
    "st-chp2-seciv-l96-104-antonio-capuchin": (
        "Records Antonio's membership in the Capuchin order; preserve the identification as Haskell's account.",
    ),
    "st-chp2-seciv-l96-104-appeal-letters-to-family": (
        "Records the reported dispatch of Bracciolini's letters to the Barberini family; retain the plural family scope and 1623 context.",
    ),
    "st-chp2-seciv-l96-104-appeal-to-urban": (
        "Records Bracciolini's quoted appeal to Urban; preserve it as a reported letter, not proof that the Pope accepted the appeal.",
    ),
    "st-chp2-seciv-l96-104-bee-emblem-ceiling-theme": (
        "Records the bees as an emblem made an essential theme in Cortona's ceiling; retain the comparison with Sacchi's earlier treatment.",
    ),
    "st-chp2-seciv-l96-104-bracciolini-complaint-letters": (
        "Records Bracciolini's reported complaints in letters while in Sinigaglia; retain Haskell's characterization of their tone.",
    ),
    "st-chp2-seciv-l96-104-bracciolini-cortona-plan-ceiling": (
        "Records Bracciolini and Cortona's joint planning of the ceiling decoration after Bracciolini's return to Rome.",
    ),
    "st-chp2-seciv-l96-104-bracciolini-departs-maffeo": (
        "Records Bracciolini's departure from Maffeo Barberini in 1605; preserve the political timing without inferring the Pope's motive.",
    ),
    "st-chp2-seciv-l96-104-bracciolini-regrets-departure": (
        "Records Bracciolini's reported regret about leaving Maffeo; retain the 1623 date and the author's account of his reaction.",
    ),
    "st-chp2-seciv-l96-104-bracciolini-return-to-rome": (
        "Records Bracciolini's return to Rome after permission was granted; the granting agent is not identified.",
    ),
    "st-chp2-seciv-l96-104-bracciolini-secretary-to-antonio": (
        "Records Bracciolini's appointment as secretary to Antonio by Urban VIII; retain the source's kinship and religious-order context.",
    ),
    "st-chp2-seciv-l96-104-bracciolini-stranded-sinigaglia": (
        "Records Bracciolini's reported location in Sinigaglia and the author's description of his situation; do not infer a cause for being stranded.",
    ),
    "st-chp2-seciv-l96-104-ceiling-baroque-characterization": (
        "Records Haskell's art-historical periodization linking Cortona's ceiling to a new chapter in Baroque decoration.",
    ),
    "st-chp2-seciv-l96-104-central-providence-composition": (
        "Records the ceiling's depicted allegorical figures and actions; preserve Haskell's description and the distinct roles of the personifications.",
    ),
    "st-chp2-seciv-l96-104-clement-death": (
        "Records the reported 1605 death event and its participant; this is an event-person relation, not merely a date anchor.",
    ),
    "st-chp2-seciv-l96-104-giants-conflict-continuation": (
        "Records the ceiling's reported conflict imagery and its interpretation as involving the visitor in the Pope's war against evil.",
    ),
    "st-chp2-seciv-l96-104-hercules-taddeo-allusion": (
        "Records the attributed iconographic reference from Hercules to Taddeo's administration of Rome; retain Haskell's reservation about its pertinence.",
    ),
    "st-chp2-seciv-l96-104-later-poem-series": (
        "Records Bracciolini's authorship of a later poem series and its dedications to Barberini family members.",
    ),
    "st-chp2-seciv-l96-104-laurel-emblem-ceiling-theme": (
        "Records the laurel as an emblem made an essential theme in Cortona's ceiling; retain the comparison with Sacchi's earlier treatment.",
    ),
    "st-chp2-seciv-l96-104-montagu-reports-four-ages": (
        "Records Montagu's report of one observer's possible Four Ages reading; preserve the nested attribution and uncertainty.",
    ),
    "st-chp2-seciv-l96-104-montagu-reports-rosichino-teti": (
        "Records Montagu's comparison of Rosichino's and Teti's reported readings; retain their different dates and interpretive claims.",
    ),
    "st-chp2-seciv-l96-104-poem-publication-and-honours": (
        "Records Bracciolini's work-publication context and the subsequent honours reported by Haskell; do not infer that publication alone caused them.",
    ),
    "st-chp2-seciv-l96-104-religion-rome-tribute": (
        "Records the allegorical tribute made by Religion and Rome to the reigning Barberini family.",
    ),
    "st-chp2-seciv-l96-104-series-subject-bulgaria": (
        "Records the later poem series' reported subject, the conversion of Bulgaria; the passage does not identify an individual poem.",
    ),
    "st-chp2-seciv-l96-104-series-subject-capture": (
        "Records the later poem series' reported subject, the capture of La Rochelle; the passage does not identify an individual poem.",
    ),
    "st-chp2-seciv-l96-104-subsidiary-themes-papal-government": (
        "Records the reported symbolic relation between subsidiary themes and the Pope's government; preserve the examples and their general framing.",
    ),
    "st-chp2-seciv-l96-104-urban-not-entirely-forgiving": (
        "Records Haskell's qualified account of Urban VIII's attitude toward Bracciolini; retain 'not entirely' and do not infer a specific sanction.",
    ),
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
    require(source_lines[95] == "[Page 52]", "print page anchor changed")
    require("Then, at the only critical moment" in source_lines[96], "Bracciolini passage changed")
    require("She refers to the interpretation" in source_lines[102], "footnote passage changed")

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
