from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_iv.md"
SEGMENT = "chp-6:06_CHP-6_sec_iv:l55-72"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp6-seciv-notes-l55-72-relation-classification-20261013"

EXPECTED = {
    STATEMENTS: "69d5676632c2083172184d6ce1f86ec0d76a0979d5012dbe3364f4e9fda0b3fd",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
}

TRUE_NOTES = {
    "st-chp6-p157-armida-danae-placement": "This records Haskell's explicit placement of Armida next to Danae; the compared works remain separate candidates.",
    "st-chp6-p157-armida-judgement-placement": "This records the reported placement of Armida next to The Judgement of Paris; it does not merge either work with Danae.",
    "st-chp6-p157-catalogue-continuation": "This completes the p.156 claim by linking Antonio's knowledge of taste to the catalogue he compiled himself.",
    "st-chp6-p157-effetti-literary-interest": "This records Antonio's reported intellectual response to The Table; the historical attribution of the dialogue is treated separately.",
    "st-chp6-p157-employed-artists-theme": "This records Antonio's employment of artists and the reported subject he required them to depict; the artists remain an unnamed group.",
    "st-chp6-p157-gallery-reproduction": "This records Antonio's having a version of the dialogue's allegorical picture reproduced at his gallery entrance.",
    "st-chp6-p157-marino-comparison": "This preserves Haskell's explicit comparison between Antonio's treatment of wealth and seventeenth-century poets, especially Marino.",
    "st-chp6-p157-mascardi-professorship": "This records Mascardi's professorship at Rome University under Urban VIII as reported by Haskell.",
    "st-chp6-p157-midas-cleopatra-placement": "This records the reported hanging of King Midas near The Feast of Cleopatra; no shared authorship or room is inferred.",
    "st-chp6-p157-note1-source": "This records Haskell's footnote citation to Spon and Wheler as a bibliographic relation only; the cited page was not independently consulted.",
    "st-chp6-p157-ownership-and-collector-status": "This preserves Haskell's qualified relation between Antonio and the pictures in his catalogue, including the reported uncertainty over ownership.",
    "st-chp6-p157-picture-programme": "This records Haskell's claim that most pictures Antonio owned were designed to illustrate the dialogue's lessons.",
    "st-chp6-p157-renaissance-ekphrasis": "This records the reported use of antique picture descriptions and their appeal to Antonio; the source's broad historical framing is retained.",
    "st-chp6-p157-studiolo-description": "This records the relation between the travel account and its description of Antonio's Studiolo; the passage is a reported appearance, not a complete inventory.",
    "st-chp6-p157-table-attribution-correction": "This records the footnote's correction of the dialogue's attribution and date; the alternative author remains unidentified.",
    "st-chp6-p157-table-content": "This records the relation between The Table and the allegorical picture it purports to describe; the picture is not individually identified.",
    "st-chp6-p157-table-vogue-mascardi": "This records Mascardi's reported role in The Table's vogue and translation, while Shaftesbury's later interest remains separately attributed.",
    "st-chp6-p161-note1-pascoli-canini": "This records the footnote's bibliographic pointer to Pascoli for the Canini passage; it does not independently verify those pages.",
    "st-chp6-p161-note3-bellori": "This records the footnote's citation to Bellori for the Altieri fresco discussion; it is a locator, not independent verification.",
    "st-chp6-p161-note3-clark": "This records the footnote's citation to Clark concerning the unnamed Berrettoni work in the palace; it is a locator only.",
    "st-chp6-p161-note4-pascoli": "This records the footnote's citation to Pascoli for the unfinished palace decoration; it is a locator only.",
}

FALSE_NOTES = {
    "st-chp6-p157-effetti-wealth-interpretation": "This is Haskell's interpretive characterization of Antonio's attitude toward wealth, without a specific entity-to-entity claim.",
    "st-chp6-p157-iconographic-source-fields": "This is a broad account of possible literary and historical sources for imagery, without a specific artwork or source-to-work relation.",
    "st-chp6-p157-pinax-wealth-maxim": "This is a quoted moral maxim from the dialogue, not a relation between identified entities.",
    "st-chp6-p157-table-originality-evaluation": "This is Haskell's general evaluation of the dialogue's originality, not a specific entity relation.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.157-166 composite note-segment S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write the guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    if "Footnotes:" not in source_lines[54] or not any("2016" in source_lines[n - 1] or "1670" in source_lines[n - 1] for n in range(56, 73)):
        raise SystemExit("composite note-segment source guard failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    targets = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES) | set(FALSE_NOTES)
    if targets != expected_targets or len(targets) != 25:
        raise SystemExit(f"composite note-segment target set changed: {sorted(targets ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(targets):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 56 or end > 72 or start > end:
            raise SystemExit(f"invalid composite-note source anchor: {sid} {start}-{end}")
        ids = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing = sorted({cid for cid in ids if cid and cid not in candidate_ids})
        if missing:
            raise SystemExit(f"candidate endpoint missing for {sid}: {missing}")

    for sid, note in TRUE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
    for sid, note in FALSE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
    by_id["st-chp6-p157-employed-artists-theme"]["qualifiers"]["open_endpoint_reason"] = (
        "Haskell refers to artists employed by Antonio as a broad unnamed group; no individual artists are identified in this passage."
    )
    by_id["st-chp6-p157-table-content"]["qualifiers"]["open_endpoint_reason"] = (
        "The passage describes an allegorical picture within the dialogue but does not identify a separate work candidate for that picture."
    )
    by_id["st-chp6-p157-table-attribution-correction"]["qualifiers"]["open_endpoint_reason"] = (
        "The footnote says the Pinax has a different author but does not identify that author."
    )

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "segment": SEGMENT, "classified": len(targets), "relation_candidate_true": len(TRUE_NOTES), "relation_candidate_false": len(FALSE_NOTES), "unset_in_segment": 0, "before_sha256": digest(raw[STATEMENTS]), "after_sha256": digest(result)}, ensure_ascii=False))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
