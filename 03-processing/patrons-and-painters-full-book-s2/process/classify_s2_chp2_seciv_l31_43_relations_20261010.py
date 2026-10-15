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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l31-43"
SEGMENT_SHA256 = "24c57f448578597f0570312dc6bca4744243c4f02872a4f4fba78dc979529abe"
STATEMENTS_SHA256 = "4051bfa6b8adb90ea42bee15ae5bfff71b832e8f565ac5a65ab284a77f814b7f"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l31-43-20261010")

DECISIONS = {
    "st-chp2-seciv-l31-43-barberini-circle-caravaggio-influence": "Haskell offers a broad causal interpretation: adoption of Vouet and Valentin by the Barberini circle effectively ended Caravaggio's direct influence on Roman art. Preserve 'effectively' and the author's scope.",
    "st-chp2-seciv-l31-43-blunt-four-evangelists-hypothesis": "The proposed series and interruption are explicitly attributed to Anthony Blunt's suggestion. Preserve the two landscape references and the fall of the Barberini as a hypothesis, not an established series.",
    "st-chp2-seciv-l31-43-francesco-buys-sforza-palace": "Haskell says Francesco bought Alessandro Sforza's Quirinal palace in 1625 between the Paris and Madrid embassies. The building's identity with the Barberini palace remains for later alignment.",
    "st-chp2-seciv-l31-43-francesco-gifts-palace-to-taddeo": "Haskell says Francesco gave the palace to his younger brother Taddeo before leaving for Spain. Preserve transfer rather than sale and do not supply an exact date.",
    "st-chp2-seciv-l31-43-francesco-less-attention-sacchi": "Haskell contrasts Francesco's lesser attention to Andrea Sacchi with his patronage of Vouet and Valentin. No commission count or specific action toward Sacchi is stated.",
    "st-chp2-seciv-l31-43-francesco-preferred-showy-taste": "Haskell contrasts Francesco's preference for a lush, showy manner with Cassiano dal Pozzo's severity. This is the author's characterization of taste, not verified psychology.",
    "st-chp2-seciv-l31-43-history-painting-demand": "Haskell says the two artists were then required to produce grandiose history paintings suited to the style he describes. The party imposing the requirement is unspecified.",
    "st-chp2-seciv-l31-43-letter-possibly-related-windsor-drawing": "Haskell says the Windsor drawing may be related to Poussin's letter and describes it as apparently from Poussin's studio. Preserve both qualifications and the cited publication context.",
    "st-chp2-seciv-l31-43-matthew-landscape-from-palace": "The note says the Landscape with St Matthew came from the Barberini palace. 'The former' refers to the first of the two named landscapes; no date or transfer path is supplied.",
    "st-chp2-seciv-l31-43-patronage-encouraged-barque-style": "Haskell says patronage by Francesco and his friends encouraged Vouet and Valentin to adopt a florid, lighter Baroque style. The unnamed 'others' and patronal-group boundaries remain unspecified.",
    "st-chp2-seciv-l31-43-poussin-landscapes-associated-barberini": "Haskell says two Poussin landscapes can be associated with the Barberini family. The note does not map Berlin and Chicago individually to each title.",
    "st-chp2-seciv-l31-43-poussin-letter-thanks-dal-pozzo": "Haskell reports Poussin's 27 June 1642 letter from Paris thanking Cassiano for the opportunity to serve Cardinal Barberini with a Scipio design and asking Cassiano to convey further thanks. The wording is cited through Correspondance.",
    "st-chp2-seciv-l31-43-sacchi-turns-to-raphael-and-classicism": "Haskell describes Sacchi as increasingly turning to Raphael and Roman classicism for inspiration after an early Baroque manner. Preserve this as the author's account of stylistic development.",
    "st-chp2-seciv-l31-43-second-capture-given-away": "Haskell says Francesco almost immediately gave the second Capture of Jerusalem to an unnamed foreign dignitary. Preserve the unknown recipient and relative timing; the footnote does not identify the dignitary.",
    "st-chp2-seciv-l31-43-valentin-allegory-assessment": "Haskell describes Valentin's Allegory of Rome as an awkward attempt to use a Caravaggesque manner on an unsuitable theme. Keep the assessment attributed to Haskell and retain the Plate 1 pointer.",
    "st-chp2-seciv-l31-43-virgin-spoleto-possible-francesco-commission": "The note says the Virgin protecting Spoleto at Dulwich may have been painted for Francesco, who was bishop of the city. Preserve 'may' and do not turn it into a confirmed commission.",
    "st-chp2-seciv-l31-43-vouet-foreshadows-grand-manner": "Haskell characterizes Vouet's talent as decorative and says he was foreshadowing the grand manner by 1627, later introducing it into France. Preserve the chronology and author's characterization.",
    "st-chp2-seciv-l31-43-vouet-valentin-career-backing": "Haskell says both artists had successful careers through Francesco's backing, culminating in altarpieces for St Peter's. The individual altarpieces and each artist's contribution are not identified.",
    "st-chp2-seciv-l31-43-vouet-valentin-influenced-by-caravaggio": "Haskell says both Simon Vouet and Valentin came strongly under Caravaggio's influence. No particular work or mechanism is specified.",
    "st-chp2-seciv-l31-43-vouet-valentin-restraint-comparison": "Haskell compares Vouet and Valentin with the fine restraint Poussin later developed. Preserve this as comparative aesthetic judgment, not a measured quality.",
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
        qualifiers = row.get("qualifiers") or {}
        require("relation_candidate" not in qualifiers, f"already classified: {statement_id}")
        qualifiers["relation_candidate"] = True
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
