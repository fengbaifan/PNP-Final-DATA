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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l45-52"
SEGMENT_SHA256 = "8cde8f28190a93455f5efa9d6dd2c56c37633da7f376e805fcdb2bd660dd0fe5"
STATEMENTS_SHA256 = "946ddf08a1e67c8775ae3c3d8f1d943ce136c8c9348adc75bd861f6c08637788"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l45-52-20261010")

DECISIONS = {
    "st-chp2-seciv-l45-52-barberini-new-palace-plan": (
        True,
        "Haskell reports the Barberini family's intention to build a larger palace and a proposal to incorporate part of the existing Sforza structure. This is a plan, not completed construction; keep the palace identities distinct pending alignment.",
    ),
    "st-chp2-seciv-l45-52-bernini-restored-s-bibiana": (
        True,
        "The parenthetical says Bernini had by then only restored S. Bibiana. Preserve the limited restoration claim and its temporal scope.",
    ),
    "st-chp2-seciv-l45-52-della-rovere-prior-prefecture": (
        True,
        "Haskell says the Prefect of Rome office had belonged to the Della Rovere until the family's extinction and identifies them collectively as dukes of Urbino. No individual duke is identified.",
    ),
    "st-chp2-seciv-l45-52-francesco-transfer-sforza-palace-in-1626": (
        True,
        "Haskell explicitly dates Francesco's transfer of the Sforza palace to Taddeo to 1626. This is distinct from the 1625 purchase described earlier.",
    ),
    "st-chp2-seciv-l45-52-maderno-or-collaborator-design-fragment": (
        True,
        "Haskell attributes the architectural departure tentatively to Maderno or, more likely, an unidentified collaborator or adviser. Preserve the uncertainty and the continuation into L54–63.",
    ),
    "st-chp2-seciv-l45-52-papal-pardon-and-character-deterioration": (
        True,
        "The source says a broadly worded papal pardon settled the events just described, while Taddeo's character continued to deteriorate. The pardon is not reproduced and the account remains Haskell's.",
    ),
    "st-chp2-seciv-l45-52-precedence-claims-resisted": (
        True,
        "Haskell reports ceremonial precedence claims being pressed and resisted and foreign embassies resenting perceived humiliations. Preserve the passage's collective framing and unspecified actors and incidents.",
    ),
    "st-chp2-seciv-l45-52-sforza-family-sale-at-valmontone": (
        True,
        "Haskell says the Sforza family was compelled a few years later to sell its Valmontone property to the same purchaser, Francesco Barberini. Keep the relative date and source-level identity reference.",
    ),
    "st-chp2-seciv-l45-52-taddeo-age-and-election-context": (
        False,
        "This is Taddeo's age at the time of Urban VIII's election. Urban supplies the temporal event context, not a direct relation between the two people; retain the age assertion without treating it as a graph relation.",
    ),
    "st-chp2-seciv-l45-52-taddeo-approached-maderno": (
        True,
        "Haskell says Taddeo approached Carlo Maderno for the palace project. 'Leading architect' and prior service to the Pope are the author's contextual descriptions.",
    ),
    "st-chp2-seciv-l45-52-taddeo-dynastic-role": (
        True,
        "Haskell frames fathering a Barberini dynasty as Taddeo's role. Preserve this as the author's account of an expected dynastic role, not a claim that the outcome was achieved by this act.",
    ),
    "st-chp2-seciv-l45-52-taddeo-income-ranking": (
        False,
        "This is a comparative attribute of Taddeo's annual income. Italy supplies the comparison scope, not a direct relation endpoint; retain the source-backed attribute outside the relation graph.",
    ),
    "st-chp2-seciv-l45-52-taddeo-lieutenant-general": (
        True,
        "Haskell says Taddeo was appointed lieutenant-general of the papal armies at about the time of his 1627 marriage. Preserve the approximate timing and the father's supreme-command role.",
    ),
    "st-chp2-seciv-l45-52-taddeo-marriage": (
        True,
        "Haskell says Taddeo was made to marry an unnamed daughter of the Colonna in 1627. Do not infer her personal identity.",
    ),
    "st-chp2-seciv-l45-52-taddeo-palestrina-purchase": (
        True,
        "Haskell links Taddeo's purchase of the Principality of Palestrina with his nobility being assured two years after the preceding appointment context. Preserve relative timing and the author's causal framing.",
    ),
    "st-chp2-seciv-l45-52-taddeo-prefect-title": (
        True,
        "Haskell says Taddeo was given the archaic title Prefect of Rome in 1631. Preserve the office and date as reported.",
    ),
    "st-chp2-seciv-l45-52-taddeo-succeeds-father-command": (
        True,
        "Haskell says Taddeo succeeded his father in the supreme command of the papal armies. The father and timing are not identified in this passage.",
    ),
    "st-chp2-seciv-l45-52-taddeo-surrounding-land-purchases": (
        True,
        "Haskell says Taddeo continued buying surrounding land for the palace project. Individual parcels and dates are unspecified.",
    ),
    "st-chp2-seciv-l45-52-urban-viii-intended-assertion-of-rights": (
        True,
        "Haskell says Urban VIII was determined that Taddeo assert his rights vigorously. Preserve the stated intention and do not treat it as proof that every subsequent claim was made by Urban personally.",
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
