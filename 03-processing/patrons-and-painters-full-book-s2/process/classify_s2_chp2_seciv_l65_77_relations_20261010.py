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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l65-77"
SEGMENT_SHA256 = "69490f9d868a34da1b43ef70ed866733a906d4a10d1935155fa65fb8dd57a811"
STATEMENTS_SHA256 = "ab603c3569ea1acd90181d504eab7bdf64061ba5117a14091172ab7fb2f031d8"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l65-77-20261010")

DECISIONS = {
    "st-chp2-seciv-l65-77-bentivoglio-palace-sale-before-guido-death": (
        False,
        "This statement dates the family's sale relative to Guido's death; Guido is a temporal anchor, not a direct relation endpoint. Preserve the reported timing and the footnote's named buyer in the statement record.",
    ),
    "st-chp2-seciv-l65-77-bentivoglio-sells-palace-to-lante": (
        True,
        "The footnote says the Bentivoglio sold the palace to the Lante family, from whom Cardinal Mazarin later acquired it. The main text calls the sale forced; retain that source distinction.",
    ),
    "st-chp2-seciv-l65-77-claude-appeals-to-guido-taste": (
        True,
        "Haskell says Claude's treatment of the landscape themes appealed to Cardinal Guido Bentivoglio's love of colour and poetry. Preserve this as an authorial account of aesthetic affinity.",
    ),
    "st-chp2-seciv-l65-77-enzo-buys-borghese-palace-1619": (
        True,
        "The main text names Enzo as buyer in 1619; footnote 1 says the Bentivoglio bought the palace from the Altemps family in that year. Preserve both attributions without silently resolving the actor.",
    ),
    "st-chp2-seciv-l65-77-enzo-despoils-ferrara-for-scipione": (
        True,
        "Haskell says Enzo used deliberate trickery to help despoil his native Ferrara for Scipione Borghese's benefit. Preserve this charged authorial characterization and the stated beneficiary.",
    ),
    "st-chp2-seciv-l65-77-enzo-in-charge-of-ludovisi-palaces": (
        True,
        "Haskell says Enzo was put in charge of decorating the various Ludovisi palaces under Gregory XV. The buildings and exact scope are unspecified.",
    ),
    "st-chp2-seciv-l65-77-enzo-procures-dosso-works-1608": (
        True,
        "Haskell says Enzo procured some of the finest works by Dosso Dossi from the Ferrara Ducal collection for Scipione Borghese's gallery in 1608. Preserve the source's collective wording and provenance sequence.",
    ),
    "st-chp2-seciv-l65-77-enzo-sends-giovanni-to-decorate-palace": (
        True,
        "Haskell says Enzo sent Giovanni da San Giovanni to help decorate the Borghese palace. Preserve 'help' and the palace context.",
    ),
    "st-chp2-seciv-l65-77-giovanni-letter-describes-guido-tour": (
        True,
        "Haskell reports through Giovanni's letter that Guido took Giovanni around the ground-floor apartments and requested decorations for unfinished vaults. The direct endpoints are patron Guido and artist Giovanni; retain the letter as evidence and do not map the request directly onto the three named finished scenes.",
    ),
    "st-chp2-seciv-l65-77-guido-admires-claude-and-patronage": (
        True,
        "Haskell says Guido was among Claude's first admirers and that Claude's success was partly assured through Guido's patronage. Preserve 'partly' and the source's relative chronology.",
    ),
    "st-chp2-seciv-l65-77-guido-collection-includes-crucifixion": (
        True,
        "Haskell says Guido amassed a notable collection including a Van Dyck Crucifixion as well as his portrait. Preserve the collection inclusion without inferring later ownership or location.",
    ),
    "st-chp2-seciv-l65-77-guido-relative-austerity-explained": (
        True,
        "The sentence completes the previous segment and says Guido lived for a number of years in the Borghese palace on the Quirinal. Preserve the explanatory attribution and unspecified duration.",
    ),
    "st-chp2-seciv-l65-77-haskell-rejects-passeri-patron-attribution": (
        False,
        "This records Haskell's correction of Passeri's attribution, not a historical relation between Passeri and Guido. Footnote 1 dates the frescoes to 1611–12 while the palace belonged to Scipione Borghese; do not create a Guido patron edge from the disputed attribution.",
    ),
    "st-chp2-seciv-l65-77-mazarin-acquires-palace-from-lante": (
        True,
        "Footnote 1 says Cardinal Mazarin acquired the palace from the Lante family. The cross-reference supplies further location in chapter 7 but no date here.",
    ),
    "st-chp2-seciv-l65-77-taddeo-turns-to-enzo-under-urban": (
        True,
        "Haskell says the uncertain Taddeo turned to Enzo under Urban VIII. Preserve this advisory relation and the author's characterization of Taddeo.",
    ),
    "st-chp2-seciv-l65-77-tassi-gentileschi-frescoes-1611-1612": (
        True,
        "Footnote 1 says the Tassi and Gentileschi frescoes were painted in 1611 and 1612 while the palace still belonged to Scipione Borghese. Preserve the date and ownership context; it contradicts Passeri's later attribution to Bentivoglio.",
    ),
    "st-chp2-seciv-l65-77-urban-commissions-two-claude-pictures": (
        True,
        "Haskell says Urban VIII commissioned Claude two pictures of fanciful and genre scenes after Guido introduced him to the Pope. Preserve the sequence and the two-picture count.",
    ),
    "st-chp2-seciv-l65-77-urban-commissions-two-location-views": (
        True,
        "Haskell says Urban VIII then asked Claude for two further pictures connected with Santa Marinella fortifications and the country house at Castel Gandolfo. Preserve 'perhaps hoped' and do not assign individual themes to surviving works beyond the source.",
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

    letter_row = by_id["st-chp2-seciv-l65-77-giovanni-letter-describes-guido-tour"]
    require(letter_row.get("subject_candidate_id") == "cand-0291", "unexpected Guido endpoint")
    require(letter_row.get("object_candidate_id") == "cand-4664", "unexpected letter endpoint")
    require(letter_row.get("predicate") == "letter_reports_patron_tour_and_decoration_request", "unexpected letter predicate")
    require(letter_row["original_quote"] in source_text, "letter quote mismatch")
    letter_row["object_candidate_id"] = "cand-2350"
    letter_row["predicate"] = "palace_tour_and_decoration_request_to_artist_reported"
    letter_row["qualifiers"]["claim"] = "Haskell reports, through a letter from Giovanni da San Giovanni, that Cardinal Guido took Giovanni around the ground-floor apartments and asked him to paint sea monsters and sirens fighting in the water on unfinished vaults."
    letter_row["qualifiers"]["letter_candidate_id"] = "cand-4664"
    letter_row["qualifiers"]["qualification"] = "The endpoints are patron Guido and artist Giovanni; the letter is retained as evidence. Do not map the request directly onto the three finished scenes named in the following sentence."

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
        "endpoint_correction": {
            "statement_id": letter_row["statement_id"],
            "old_object": "cand-4664 (letter)",
            "new_object": "cand-2350 (Giovanni da San Giovanni)",
            "predicate": letter_row["predicate"],
        },
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
