from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l114-125"
NEW_STATEMENT_ID = "st-chp2-seciv-l114-125-francesco-antonio-sibling"
SIBLING_ID = "st-chp2-seciv-l114-125-antonio-nephew-and-brother"
SEGMENT_SHA256 = "9f19718c42f5753aa5b75f1317c40ad493602c9539fac022a1a681d37c2b4877"
SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
STATEMENTS_SHA256 = "f84022bc61b701e7cc218997db0f7ad402d6078c9c8b15be83c1b56b6fed0b81"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l114-125-20261010")

DECISIONS = {
    "st-chp2-seciv-l114-125-antonio-ambition-thwarted": "Records the reported obstruction of Antonio's ambitions by Francesco and Urban VIII; preserve Urban as the additional actor and the author's frequency claim.",
    "st-chp2-seciv-l114-125-antonio-family-enthusiasm": "Records Antonio's shared interest in learning and art in relation to the Barberini family; this does not assert a formal organization.",
    "st-chp2-seciv-l114-125-antonio-hopes-to-enrich-collection": "Records Antonio's reported intention to obtain pictures from Urbino; do not turn the comparison with earlier Ferrara collecting into an actual acquisition.",
    "st-chp2-seciv-l114-125-antonio-income-comparison": "Records a comparative income claim involving Antonio, the surname-only Borghese comparator, and Ludovisi; retain the unresolved identity and the author's doubt.",
    "st-chp2-seciv-l114-125-antonio-made-cardinal-1627": "Records the reported 1627 appointment event and Antonio as its recipient; preserve the age and footnote evidence link.",
    SIBLING_ID: "Records Antonio's reported nephew relationship to Urban VIII; the adjacent sibling relationship to Francesco is recorded separately.",
    "st-chp2-seciv-l114-125-antonio-opportunity-urbino": "Records the reported connection between the 1631 devolution of Urbino and Antonio's opportunity to assert himself in art; do not infer a specific acquisition here.",
    "st-chp2-seciv-l114-125-conclave-reacts-to-appointment": "Records the elder Conclave members' reported reaction to Antonio's appointment; preserve the collective and Haskell's attribution.",
    "st-chp2-seciv-l114-125-duke-death-and-possession-1631": "Records the succession sequence connecting the duke's death with steps to take possession of the State of Urbino; the agents are unnamed and the duke is not identified as the possessor.",
    "st-chp2-seciv-l114-125-francesco-favourite-cortona": "Records Francesco's reported preference for Pietro da Cortona; retain the stylistic description as Haskell's characterization.",
    "st-chp2-seciv-l114-125-francesco-favourite-romanelli": "Records Francesco's reported preference for Romanelli; retain 'follower' as the source's characterization.",
    NEW_STATEMENT_ID: "Records Antonio's reported sibling relationship to Francesco; do not infer birth order beyond the source's wording.",
    "st-chp2-seciv-l114-125-palace-built-by-federigo": "Records Federigo da Montefeltre's reported building of the unidentified Urbino palace and its described cultural significance.",
    "st-chp2-seciv-l114-125-pope-special-action-continuation": "Records the papal decree fragment continued at L128; preserve the decree's purpose and transfer terms from that continuation.",
    "st-chp2-seciv-l114-125-private-possession-inheritance": "Records the duke's reported transfer of private possessions to Vittoria; do not equate them with all public or ducal holdings.",
    "st-chp2-seciv-l114-125-sacchi-supported-by-antonio": "Records Sacchi's reported reliance on Antonio for support; preserve 'almost entirely' and do not specify the support beyond the source.",
    "st-chp2-seciv-l114-125-sacchi-temperament-and-raphael": "Records Haskell's developmental comparison between Sacchi and Raphael; retain the interpretation without treating it as a diagnosis or Sacchi's own statement.",
    "st-chp2-seciv-l114-125-studiolo-portraits-and-authorship": "Records the portraits' location in the Studiolo and the attributed painters and original owner listed in qualifiers; no individual portrait-to-painter pairing is inferred.",
    "st-chp2-seciv-l114-125-studiolo-portraits-sent-to-rome": "Records the reported movement of the portrait group from the Studiolo to Rome; the agents and any ownership change remain unspecified.",
    "st-chp2-seciv-l114-125-taddeo-inherits-prefect-title": "Records Taddeo's reported inheritance of the Prefect of Rome title; do not infer Della Rovere descent from the inherited title.",
    "st-chp2-seciv-l114-125-titian-raphael-pictures-to-florence": "Records the reported movement of unnamed Titian and Raphael pictures from Urbino to Florence; do not identify or count individual works.",
    "st-chp2-seciv-l114-125-urban-claims-urbino": "Records Urban VIII's political claims to the State of Urbino and the expected succession; this is not a claim that transfer had already occurred.",
    "st-chp2-seciv-l114-125-urban-transfers-effective-authority": "Records Urban's persuasion of the duke to transfer effective authority to an unnamed Rome-appointed governor; distinguish this from later possession.",
    "st-chp2-seciv-l114-125-urbino-collection-dispersal": "Records the reported despoiling of Urbino and dispersal of most of the picture collection; the bulk's destination and individual works remain unknown.",
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
    require(source_lines[113] == "[Page 54]", "print page anchor changed")
    require("Urban VIII had been pressing hard" in source_text, "political passage changed")
    require("those portraits of ancient and modern poets" in source_text, "Studiolo passage changed")
    brother_quote = "Francesco\u2019s second brother, the impetuous Antonio."
    nephew_quote = "Antonio was the youngest of the Pope\u2019s nephews"
    require(brother_quote in source_text and nephew_quote in source_text, "family-relation source wording changed")

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
    require(NEW_STATEMENT_ID not in by_id, "new sibling statement ID already exists")
    original = by_id.get(SIBLING_ID)
    require(original is not None, "combined nephew/brother statement missing")
    require(original.get("subject_candidate_id") == "cand-0187", "Antonio subject mapping changed")
    require(original.get("object_candidate_id") == "cand-0209", "Urban VIII object mapping changed")
    require(original.get("original_quote") in source_text, "original family-relation quote mismatch")

    pending = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT_ID
        and row.get("subject_candidate_id")
        and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") not in (True, False)
    }
    require(pending == (set(DECISIONS) - {NEW_STATEMENT_ID}), f"pending bilateral set changed: {sorted(pending)}")

    original["predicate"] = "nephew_of_reported"
    original["qualifiers"]["claim"] = "Haskell says Antonio was the youngest of Urban VIII's nephews."
    original["qualifiers"]["qualification"] = "The source states the nephew relationship; the adjacent sibling relation to Francesco is recorded separately."
    original["original_quote"] = nephew_quote

    sibling = deepcopy(original)
    sibling["statement_id"] = NEW_STATEMENT_ID
    sibling["subject_candidate_id"] = "cand-0187"
    sibling["object_candidate_id"] = "cand-0203"
    sibling["predicate"] = "sibling_relationship_reported"
    sibling["qualifiers"] = {
        "source_line_start": 117,
        "source_line_end": 117,
        "claim": "Haskell identifies Antonio as Francesco's brother, using the phrase 'Francesco's second brother'.",
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "print_page": 54,
        "pdf_physical_page": 39,
        "qualification": "The source explicitly states a sibling relationship; do not infer birth order beyond its wording.",
    }
    sibling["original_quote"] = brother_quote
    sibling["qualifiers"]["relation_candidate"] = True
    sibling["qualifiers"]["relation_candidate_note"] = DECISIONS[NEW_STATEMENT_ID]
    original_index = rows.index(original)
    rows.insert(original_index + 1, sibling)
    by_id[NEW_STATEMENT_ID] = sibling

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
        "statements": len(rows),
        "bilateral": len(bilateral),
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
        "split_statement": SIBLING_ID,
        "new_statement": NEW_STATEMENT_ID,
        "after": counts,
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
