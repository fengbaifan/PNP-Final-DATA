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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l127-137"
SEGMENT_SHA256 = "0e76625484b78cacdcbbe376367af73ff261938fbe4b749de9ac7dff7ce27da7"
SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
STATEMENTS_SHA256 = "e832e317ebd1b00d86d9c03924bab10b85826d32c9505c67da9c02ef8818c150"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l127-137-20261010")

DECISIONS = {
    "st-chp2-seciv-l127-137-antonio-1639-jesuit-centenary-reception": "Records Antonio's organization of the 1639 Ges\u00f9 reception for the centenary of the Jesuit statutes' approval; preserve the event and institutional context.",
    "st-chp2-seciv-l127-137-antonio-consistent-employment": "Records Antonio's reported consistent employment of Sacchi and the author's claim that he was the only Barberini to provide it.",
    "st-chp2-seciv-l127-137-antonio-continues-joust-to-revive-chivalry": "Records Antonio's decision to continue the joust after the planned visit was cancelled and his stated wish to revive chivalry among Roman youths.",
    "st-chp2-seciv-l127-137-antonio-helps-secure-sacchi-commissions": "Records Antonio's role in helping Sacchi obtain commissions in the Capuchin church and family palace; retain the degree of agency stated.",
    "st-chp2-seciv-l127-137-antonio-keeps-sacchi-modelli": "Records Antonio's reported keeping of the modelli for Sacchi's Lateran Baptistery canvases in his private collection.",
    "st-chp2-seciv-l127-137-antonio-organizes-mediaeval-joust": "Records Antonio's organization of the 1634 joust in Piazza Navona; preserve the date and place.",
    "st-chp2-seciv-l127-137-antonio-responsible-for-palace-decoration": "Records Antonio's reported responsibility for the palace decoration and his residence there; do not infer a more specific ownership status.",
    "st-chp2-seciv-l127-137-antonio-salary-and-retinue": "Records Antonio's payment of Sacchi's monthly salary and enrollment of him in the official retinue before 1637; preserve the approximate date.",
    "st-chp2-seciv-l127-137-antonio-supports-sacchi-passeri-testimony": "Records Antonio's reported patronal support for Sacchi and the nested Passeri testimony; retain the attribution rather than presenting Passeri's counterfactual as verified.",
    "st-chp2-seciv-l127-137-author-irony-at-clerical-society": "Records Haskell's interpretation of the clerical audience's relation to the joust's challenges; retain the author's irony and do not infer group membership.",
    "st-chp2-seciv-l127-137-bentivoglio-arranges-joust": "Records Haskell's claim that the Bentivoglio family was in charge of arrangements for the joust.",
    "st-chp2-seciv-l127-137-cortona-sacchi-divergence": "Records the reported divergence between Cortona and Sacchi becoming apparent in the early 1630s; keep Antonio's patronage as the author's contextual interpretation.",
    "st-chp2-seciv-l127-137-decree-grants-portraits-to-antonio": "Records the decree's transfer of the Studiolo portraits to Antonio and his heirs in perpetuity; preserve the source attribution and footnote.",
    "st-chp2-seciv-l127-137-joust-planned-for-prince-visit-cancelled": "Records the joust's initial plan as an entertainment for an unnamed Polish prince and the cancellation of his visit.",
    "st-chp2-seciv-l127-137-papal-decree-justifies-antonio-action": "Records Urban VIII's reported issuance of the decree to justify Antonio's action; retain its link to the continuation at L125 and the cited note.",
    "st-chp2-seciv-l127-137-sacchi-and-genre-painter-record-roman-scenes": "Records Antonio's employment of Sacchi and an unnamed genre painter to depict contemporary Roman scenes involving Antonio or his family; preserve the unnamed artist and broad subject scope.",
    "st-chp2-seciv-l127-137-sacchi-church-output-for-antonio": "Records the reported patronal relation between Sacchi's church canvases and Antonio; preserve the unspecified share and named Lateran Baptistery example.",
    "st-chp2-seciv-l127-137-sacchi-disapproves-cortona-style": "Records Sacchi's reported disapproval of Cortona's exuberance and complexity in debate and in their works.",
    "st-chp2-seciv-l127-137-sacchi-praises-simplicity-and-raphael": "Records Sacchi's reported praise of simplicity and his looking to Raphael as a special inspiration.",
    "st-chp2-seciv-l127-137-sacchi-records-reception-in-picture": "Records Sacchi's reported depiction of the 1639 reception in a special picture; the work remains unidentified.",
    "st-chp2-seciv-l127-137-sacchi-temporary-decoration-and-tapestries": "Records Sacchi's design of temporary church decoration and the hanging of tapestries for the Ges\u00f9 reception; preserve the separate tapestry reference.",
    "st-chp2-seciv-l127-137-sacchi-travels-and-advises-antonio": "Records Sacchi's travel with Antonio and his role as general artistic adviser on the palace decoration.",
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
    require(source_lines[126] == "[Page 55]", "print page anchor changed")
    require("most important contribution to artistic patronage" in source_text, "patronage passage changed")
    require("The Bentivoglio were in charge of the arrangements" in source_text, "joust passage changed")
    require("Sacelli was also an excessively slow worker" in source_text, "OCR source reading changed")

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
        "ocr_correction_note": "S0 'Sacelli' reads 'Sacchi' on print p.55; S0 remains unchanged.",
        "bilateral_after": counts,
        "sha256_before": digest(raw),
        "sha256_after": digest(output),
    }, ensure_ascii=True, indent=2))
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
    print(json.dumps({"result": "applied", "backup": BACKUP.name, "sha256_after": digest(output)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
