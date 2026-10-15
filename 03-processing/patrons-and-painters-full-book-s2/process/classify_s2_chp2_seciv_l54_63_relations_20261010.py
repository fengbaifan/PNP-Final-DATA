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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l54-63"
SEGMENT_SHA256 = "a045f0601ca2ce9cd4099916aa0cb20b60a811eafd3996f3849b2d7a422389e7"
STATEMENTS_SHA256 = "8fd627f21a4d2627d1a9714622cb021b26157c45a48ffc91abc87510e4ba4747"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l54-63-20261010")

DECISIONS = {
    "st-chp2-seciv-l54-63-barberini-palace-largest-private-palace": (
        False,
        "This is a comparative size attribute of the palace. Rome supplies the comparison scope, not a direct palace-to-city relation; preserve the source-backed superlative outside the relation graph.",
    ),
    "st-chp2-seciv-l54-63-barberini-supremacy-symbolized": (
        True,
        "Haskell interprets the palace as symbolizing the Barberini family's confidence and supremacy over rivals, based on money rather than arms. Preserve this as the author's symbolic interpretation.",
    ),
    "st-chp2-seciv-l54-63-bentivoglio-family-advises-taddeo": (
        True,
        "Haskell says the Bentivoglio family was ready to advise Taddeo and had a long special relationship with seventeenth-century popes. Preserve the group's unspecified boundaries and the author's framing.",
    ),
    "st-chp2-seciv-l54-63-bentivoglio-family-origin-and-standing": (
        True,
        "The text associates the Bentivoglio with Ferrara and distinguishes the family's historical standing there. Footnote 1 says the family originated in Bologna while an important branch had long been settled in Ferrara; preserve that distinction rather than flattening it into a single origin claim.",
    ),
    "st-chp2-seciv-l54-63-bernini-succeeds-maderno-with-borromini": (
        True,
        "Haskell says Bernini replaced Maderno after Maderno's death in 1629 and, with Francesco Borromini's help, made limited modifications while retaining the main plan. Preserve each architect's role and sequence.",
    ),
    "st-chp2-seciv-l54-63-enzo-benefits-from-papal-appeasement": (
        True,
        "Haskell says Enzo reaped benefits from a Pope anxious to appease local nobility. The Pope is unnamed and the causal account remains the author's.",
    ),
    "st-chp2-seciv-l54-63-enzo-ferrara-rome-ambassador": (
        True,
        "Haskell says Enzo served for a time as an 'ambassador' from Ferrara to Rome. Preserve the quotation marks, limited duration, and the explanation that the post was created to satisfy local sensibilities.",
    ),
    "st-chp2-seciv-l54-63-enzo-rallies-to-church-cause": (
        True,
        "Haskell says Enzo rallied to the Church's cause after Ferrara devolved to the Papacy in 1598. Preserve the author's causal sequence.",
    ),
    "st-chp2-seciv-l54-63-enzo-younger-brother-of-ippolito": (
        True,
        "Haskell explicitly identifies Enzo as Ippolito's younger brother.",
    ),
    "st-chp2-seciv-l54-63-facade-precedents-around-rome": (
        True,
        "Haskell says façades of this kind had precedents almost only in villas scattered around Rome. Preserve the comparison and its near-exclusive qualifier; do not infer a named model.",
    ),
    "st-chp2-seciv-l54-63-ferrara-devolves-to-papacy-1598": (
        True,
        "Haskell reports that Ferrara devolved to the Papacy in 1598. Preserve the date and source wording without adding a more specific legal mechanism.",
    ),
    "st-chp2-seciv-l54-63-guido-benefits-from-papal-appeasement": (
        True,
        "Haskell says Guido reaped benefits from an unnamed Pope anxious to appease local nobility. Preserve the attribution and unspecified Pope.",
    ),
    "st-chp2-seciv-l54-63-guido-career-in-church": (
        True,
        "Haskell describes Guido's career in the Church as exceedingly successful. This is an authorial evaluation of an ecclesiastical career.",
    ),
    "st-chp2-seciv-l54-63-guido-rallies-to-church-cause": (
        True,
        "Haskell says Guido rallied to the Church's cause after Ferrara devolved to the Papacy in 1598. Preserve the author's causal sequence.",
    ),
    "st-chp2-seciv-l54-63-guido-younger-brother-of-ippolito": (
        True,
        "Haskell explicitly identifies Guido as Ippolito's younger brother.",
    ),
    "st-chp2-seciv-l54-63-haskell-characterizes-guido-portrait": (
        True,
        "The statement concerns the portrait's rendering of Guido's features and Haskell's interpretation of the figure. Preserve the work-to-sitter anchor and attribute the evaluative comparison to Haskell.",
    ),
    "st-chp2-seciv-l54-63-ippolito-supports-cesare-deste-succession-claim": (
        True,
        "Haskell says Ippolito supported Cesare d'Este's succession claim in a final attempt to maintain Ferrara's independence. Preserve 'rather dubious' as Haskell's characterization of the claim.",
    ),
    "st-chp2-seciv-l54-63-van-dyck-paints-guido-portrait-1623": (
        True,
        "Haskell says Guido had his portrait painted by Van Dyck early in 1623. Preserve the printed footnote and plate references as source pointers.",
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

    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    require(segment is not None and segment.get("sha256") == SEGMENT_SHA256, "segment metadata mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    require(digest(source_text.encode("utf-8")) == SEGMENT_SHA256, "source segment content changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    require(len(by_id) == len(rows), "duplicate statement IDs in table")
    pending_ids = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT_ID
        and row.get("subject_candidate_id")
        and row.get("object_candidate_id")
        and "relation_candidate" not in (row.get("qualifiers") or {})
    }
    require(pending_ids == set(DECISIONS), f"pending bilateral set changed: {sorted(pending_ids)}")
    for statement_id, (decision, note) in DECISIONS.items():
        row = by_id.get(statement_id)
        require(row is not None, f"missing statement: {statement_id}")
        require(row.get("segment_id") == SEGMENT_ID, f"unexpected segment: {statement_id}")
        require(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")), f"not bilateral: {statement_id}")
        require(row["original_quote"] in source_text, f"source quote mismatch: {statement_id}")
        qualifiers = row.get("qualifiers") or {}
        require("relation_candidate" not in qualifiers, f"already classified: {statement_id}")
        qualifiers["relation_candidate"] = decision
        qualifiers["relation_candidate_note"] = note

    output = (b"\xef\xbb\xbf" if bom else b"") + newline.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") for row in rows
    ) + newline
    bilateral = [row for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    classified_true = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral)
    classified_false = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral)
    unclassified = sum("relation_candidate" not in (row.get("qualifiers") or {}) for row in bilateral)
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "classified_true": [key for key, (decision, _) in DECISIONS.items() if decision],
        "classified_false": [key for key, (decision, _) in DECISIONS.items() if not decision],
        "after_bilateral": {"relation_true": classified_true, "relation_false": classified_false, "unclassified": unclassified},
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
