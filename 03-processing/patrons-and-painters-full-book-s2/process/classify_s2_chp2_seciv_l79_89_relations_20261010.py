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
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l79-89"
SEGMENT_SHA256 = "7f8e4442443bc927ff276280e0d182a1e751cb542f9d0ad3e652f2cf523fb53b"
SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
STATEMENTS_SHA256 = "83b586e42f3904aa5ed2c3f11c32c73bae8386ee4b93295b126a17f1efe56c58"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l79-89-20261010")

DECISIONS = {
    "st-chp2-seciv-l79-89-advisers-transform-wisdom-into-princely-exaltation": (
        True,
        "Connects the unnamed advisers' reported interpretation to the fresco and Barberini princes; retain Haskell's qualification 'to a large extent'.",
    ),
    "st-chp2-seciv-l79-89-apollo-identified-with-poet-pope": (
        True,
        "An explicit iconographic identification in Haskell's reading; retain the contextual, rather than named, identification with Urban VIII.",
    ),
    "st-chp2-seciv-l79-89-bentivoglio-recommends-camassei-to-barberini": (
        True,
        "Records the family's recommendation of Camassei to the Barberini; preserve the source's sequence and 'accordingly'.",
    ),
    "st-chp2-seciv-l79-89-camassei-begins-working-for-sacchetti": (
        True,
        "Records Camassei's work for the Sacchetti; retain the approximate timing and do not infer a precise start date.",
    ),
    "st-chp2-seciv-l79-89-camassei-decorates-borghese-room-with-cupid-psyche-scenes": (
        True,
        "Connects Camassei to the reported room decoration; no formal title, scene count, or medium is supplied.",
    ),
    "st-chp2-seciv-l79-89-camassei-described-as-umbrian-follower-of-domenichino": (
        True,
        "Records Haskell's artistic influence characterization; 'follower' does not establish formal apprenticeship.",
    ),
    "st-chp2-seciv-l79-89-camassei-employed-and-resident-in-borghese-palace": (
        True,
        "Records the Bentivoglio employment of Camassei; preserve the palace residence as a separate location qualifier.",
    ),
    "st-chp2-seciv-l79-89-camassei-frescoes-style-and-admiration": (
        False,
        "The two frescoes share reported style and reception attributes; the passage does not assert a relation between the two works.",
    ),
    "st-chp2-seciv-l79-89-camassei-given-god-creating-angels-fresco": (
        True,
        "Records Camassei's assignment to the fresco; the commissioning agent is not identified.",
    ),
    "st-chp2-seciv-l79-89-camassei-given-parnassus-fresco": (
        True,
        "Records Camassei's assignment to the fresco; retain the named subject group and small-room context.",
    ),
    "st-chp2-seciv-l79-89-divine-wisdom-artwork-personifies-concept": (
        True,
        "Records the artwork's representation of Wisdom as a theological concept, distinct from the source text.",
    ),
    "st-chp2-seciv-l79-89-divine-wisdom-central-figure-description-continues": (
        True,
        "The continued description identifies the Wisdom figure depicted in the fresco; retain the passage as an iconographic relation.",
    ),
    "st-chp2-seciv-l79-89-divine-wisdom-compared-with-raphael-stanze-frescoes": (
        True,
        "An explicit comparison between Sacchi's project and Raphael's fresco group; no individual Raphael work is identified.",
    ),
    "st-chp2-seciv-l79-89-divine-wisdom-fresco-derived-from-wisdom-of-solomon": (
        True,
        "Records the reported source relationship between the fresco subject and the Wisdom of Solomon text.",
    ),
    "st-chp2-seciv-l79-89-divine-wisdom-theme-selectors-unidentified": (
        True,
        "Records the reported theme-selection relation while preserving that the individual Roman theologians are unidentified.",
    ),
    "st-chp2-seciv-l79-89-filippo-recommends-camassei-to-unidentified-marchese": (
        True,
        "Records Filippo Napoletano's recommendation of Camassei to an unnamed Marchese; keep all three roles distinct.",
    ),
    "st-chp2-seciv-l79-89-francesco-barberini-presses-sacchi-claims-at-st-peters": (
        True,
        "Records Cardinal Francesco Barberini's advocacy for Sacchi at St Peter's; the precise commission remains unspecified.",
    ),
    "st-chp2-seciv-l79-89-haskell-doubts-sacchi-devised-far-fetched-theme": (
        True,
        "Records Haskell's qualified authorship judgment linking Sacchi to the theme; do not convert 'almost inconceivable' into certainty.",
    ),
    "st-chp2-seciv-l79-89-parnassus-heroes-interpreted-as-pope-ancestors": (
        True,
        "Records the reported interpretation of the Heroes as the poet-Pope's ancestors; neither group is individually named.",
    ),
    "st-chp2-seciv-l79-89-parnassus-references-barberini-as-cultural-protectors": (
        True,
        "Records Haskell's iconographic reading of the Parnassus as referring to the Barberini; retain the comparative wording.",
    ),
    "st-chp2-seciv-l79-89-sacchi-receives-first-large-scale-work": (
        True,
        "Records Sacchi's first large-scale assignment and its room setting; the commissioning agent is not identified.",
    ),
    "st-chp2-seciv-l79-89-unidentified-explanation-frames-barberini-rule-as-divinely-chosen": (
        True,
        "Records an unidentified explanation reported by Haskell; preserve its attribution and do not state it as verified doctrine.",
    ),
    "st-chp2-seciv-l79-89-wisdom-of-solomon-calls-princes-to-honour-wisdom": (
        True,
        "Records the reported scriptural exhortation concerning Wisdom; the source gives no chapter or verse.",
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
    source_raw = SOURCE.read_bytes()
    require(digest(source_raw) == SOURCE_SHA256, "source file changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    require(digest(source_text.encode("utf-8")) == SEGMENT_SHA256, "source segment content changed")
    require(source_lines[78] == "[Page 50]", "print page anchor changed")
    require("There is no indication as to which of the Roman" in source_lines[86], "theme-selector passage changed")

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

    for statement_id, (decision, note) in DECISIONS.items():
        row = by_id[statement_id]
        require(row.get("segment_id") == SEGMENT_ID, f"unexpected segment: {statement_id}")
        require(row.get("subject_candidate_id") and row.get("object_candidate_id"), f"not bilateral: {statement_id}")
        require(row.get("qualifiers", {}).get("relation_candidate") not in (True, False), f"already classified: {statement_id}")
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
        "classified_true": sum(decision for decision, _ in DECISIONS.values()),
        "classified_false": sum(not decision for decision, _ in DECISIONS.values()),
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
