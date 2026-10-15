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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l6-17"
SEGMENT_SHA256 = "438d479ced460d329f80c12d875c4bee2672944f6017cdc0e7c78b19820af78c"
STATEMENTS_SHA256 = "d14c8f52aaf055a39cfec6baa6cea9e82047625ad1b7074265aea71703dc9bb9"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l6-17-20261010")

DECISIONS = {
    "st-chp2-seciv-l6-17-altarpiece-opportunity": "Haskell connects Francesco's first serious opportunity with the series of St Peter's altarpiece commissions. This does not say he issued every commission or identify individual paintings.",
    "st-chp2-seciv-l6-17-capture-title-names-place-and-titus": "The picture title names the capture of Jerusalem. Preserve this as title/subject wording; it does not independently establish the historical event.",
    "st-chp2-seciv-l6-17-capture-title-names-titus": "The picture title names Emperor Titus in connection with the capture. Do not treat the title wording as independent historical verification.",
    "st-chp2-seciv-l6-17-fontainebleau-visit": "Haskell says Francesco's party visited Fontainebleau to examine art treasures. The exact site or collection boundary is not specified.",
    "st-chp2-seciv-l6-17-francesco-accepted-tapestries": "Haskell reports Francesco later accepted the tapestries after initially refusing them. No exact date for the change is supplied.",
    "st-chp2-seciv-l6-17-louvre-visit": "Haskell says Francesco's party visited the Louvre to examine art treasures. Retain the historical Louvre candidate and do not substitute the later museum entity.",
    "st-chp2-seciv-l6-17-francesco-court-cultural-center": "Haskell describes Francesco's court as a centre of Rome's artistic and intellectual life. Preserve the author's assessment and unspecified court boundaries.",
    "st-chp2-seciv-l6-17-francesco-friendship-sacchetti": "The passage explicitly calls Marcello Sacchetti Francesco's friend. It does not specify the relationship's nature or duration.",
    "st-chp2-seciv-l6-17-francesco-impact-new-reign": "This is Haskell's interpretation of Francesco's impact on achievements marking Urban VIII's new reign. The achievements and Francesco's specific contributions are not enumerated.",
    "st-chp2-seciv-l6-17-francesco-initially-refused-tapestries": "Haskell reports an initial refusal under his uncle's instructions; the following sentence reports later acceptance. Preserve the sequence without inventing a date.",
    "st-chp2-seciv-l6-17-french-culture-comparison": "Preserve Haskell's comparison of Francesco's response with Urban VIII's and the author's claim about French culture's change over twenty years; neither is independently verified here.",
    "st-chp2-seciv-l6-17-louis-xiii-tapestry-gift": "Haskell says Louis XIII sent a gift to Francesco's party; the adjacent sentence identifies seven tapestries already hanging in their apartments. Retain that immediate-sequence identification as source-level inference, not a new installation or ownership claim.",
    "st-chp2-seciv-l6-17-madrid-mission": "The second diplomatic mission is associated with Francesco by the surrounding paragraph. 'Almost immediately' is relative and supplies no precise date.",
    "st-chp2-seciv-l6-17-marino-introduced-poussin-to-sacchetti": "Haskell reports a three-person introduction: Marino introduced Poussin to Sacchetti. Preserve the introducer, introduced person, and recipient roles recorded in the qualifiers.",
    "st-chp2-seciv-l6-17-no-concessions-to-huguenots": "This records an instruction's stated diplomatic objective, not its outcome. The issuer is not named in this passive clause.",
    "st-chp2-seciv-l6-17-paris-mission-outcome": "Haskell calls the Paris mission a disastrous failure and says it proved consequential for Francesco. The nature of the consequence is not specified here.",
    "st-chp2-seciv-l6-17-paris-retinue-included-cassiano": "Haskell says Cassiano dal Pozzo was included in Francesco's Paris retinue. Other members remain unnamed and 'brilliant' is the author's characterization.",
    "st-chp2-seciv-l6-17-political-rebuffs-not-diminish-sympathy": "The anaphor 'these feelings' refers to Francesco's reported response to French culture. Preserve the author's claim that political rebuffs did not diminish it.",
    "st-chp2-seciv-l6-17-poussin-arrived-from-paris": "Haskell gives Paris as Poussin's point of departure eighteen months earlier; the destination on arrival is not stated in this clause.",
    "st-chp2-seciv-l6-17-purchased-capture-from-poussin": "Haskell says Francesco bought the picture from Poussin. The wording identifies Poussin as seller, not as the picture's painter; note 4 reports the work lost and a possible later recipient.",
    "st-chp2-seciv-l6-17-return-rome-december-1625": "Haskell dates Francesco's return to Rome to December 1625 after nine months abroad. Do not infer an exact departure date.",
    "st-chp2-seciv-l6-17-return-rome-october-1626": "Haskell dates Francesco's return to Rome to October 1626 and narrates that he was to remain there. No later residence endpoint is supplied.",
    "st-chp2-seciv-l6-17-tapestries-and-rubens-cartoons": "Haskell reports that the tapestries were woven from cartoons by Rubens. This does not identify Rubens as tapestry weaver or establish ownership.",
    "st-chp2-seciv-l6-17-threatened-war-involves-italy": "The continuation completes a conditional phrase: the threatened war would have involved Italy and opened a crisis. It does not assert that war occurred or Italy entered it.",
    "st-chp2-seciv-l6-17-urban-instruction-not-to-accept-gifts": "Haskell says Francesco's uncle instructed him not to accept gifts; the uncle is identified as Urban VIII by the explicit kinship in L3 and preceding context.",
    "st-chp2-seciv-l6-17-welcomed-french-intellectuals": "Haskell says French writers, scientists, artists, and thinkers were welcomed by Francesco and corresponded with him. The collective is unnamed and the temporal scope is the author's wording.",
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
    for statement_id, note in DECISIONS.items():
        row = by_id.get(statement_id)
        require(row is not None, f"missing statement: {statement_id}")
        require(row.get("segment_id") == SEGMENT_ID, f"unexpected segment: {statement_id}")
        require(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")), f"not bilateral: {statement_id}")
        require(row["original_quote"] in source_text, f"source quote mismatch: {statement_id}")
        q = row.get("qualifiers") or {}
        require("relation_candidate" not in q, f"already classified: {statement_id}")
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note

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
        "classified_true": sorted(DECISIONS),
        "classified_false": [],
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
