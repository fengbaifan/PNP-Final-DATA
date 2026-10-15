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
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l19-29"
SEGMENT_SHA256 = "06b98701267f8db00f7dc1b9fa35e8ffcdc5d0951ba8c9c0a9e56347885e5fbd"
STATEMENTS_SHA256 = "aacd6a5b584448bf676e9e6074d5f5fb950248e13ffaa7e3365093ef3021c85b"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l19-29-20261010")

DECISIONS = {
    "st-chp2-seciv-l19-29-capuchin-introduction-forecast": "Haskell presents Francesco's introduction of Pietro da Cortona and Andrea Sacchi to the Capuchin church as a foregone conclusion. Preserve it as a forecast, not a completed introduction or commission; the church mapping is contextual.",
    "st-chp2-seciv-l19-29-committee-preferred-older-bolognese": "The source reports the committee's preference for paintings by the older generation, especially Bolognese artists. Individual artists and the group's membership are unspecified.",
    "st-chp2-seciv-l19-29-del-monte-sacchi-commission": "Haskell says Cardinal del Monte obtained a commission for Andrea Sacchi during 1624 and early 1625. The work and execution date are unspecified; 'virtually unknown' is the author's characterization.",
    "st-chp2-seciv-l19-29-del-monte-vouet-commission": "Haskell says Cardinal del Monte obtained commissions for Simon Vouet during 1624 and early 1625. No work titles or execution dates are supplied.",
    "st-chp2-seciv-l19-29-francesco-approached-poussin-second-capture": "The source reports Francesco approaching Poussin for a second version of the named picture. Preserve the title as title wording, the approximate interval from the first version, and the continuation into L31; do not infer a precise date.",
    "st-chp2-seciv-l19-29-francesco-bought-germanicus": "Haskell says Francesco bought The Death of Germanicus for his private collection as a Poussin work. Preserve the source's count ambiguity: it says 'one or two other works' and then names two.",
    "st-chp2-seciv-l19-29-francesco-bought-samson": "Haskell says Francesco bought a Samson picture for his private collection as a Poussin work. Preserve the source's count ambiguity and the reported disappearance; this is the painting, not the biblical figure.",
    "st-chp2-seciv-l19-29-francesco-joined-committee": "Haskell says Francesco joined the St Peter's committee on becoming a cardinal. The passage supplies no exact appointment date.",
    "st-chp2-seciv-l19-29-francesco-lanfranco-picture-proposal": "Before leaving for Paris, Francesco tentatively proposed ordering an important picture from Lanfranco. Preserve the proposal's tentative status and do not infer acceptance or execution.",
    "st-chp2-seciv-l19-29-francesco-main-picture-cortona-proposal": "After Reni's departure, Francesco proposed assigning the principal picture to Pietro da Cortona. The proposal was accepted, but completion and installation are not stated.",
    "st-chp2-seciv-l19-29-francesco-small-picture-poussin-proposal": "Francesco proposed assigning to Nicolas Poussin the smaller picture originally intended for Cortona. Preserve the contextual antecedent and proposal status; completion is not stated.",
    "st-chp2-seciv-l19-29-francesco-welcomed-reni": "Haskell explicitly says Cardinal Francesco Barberini welcomed Guido Reni warmly. The pronoun in the source refers to Reni.",
    "st-chp2-seciv-l19-29-germanicus-style-discouraged-francesco": "Haskell interprets the painting's stylistic tendency as probably discouraging Francesco. Preserve both the author's attribution and the explicit probability.",
    "st-chp2-seciv-l19-29-ginnasi-legate-reni": "Haskell says Ginnasi asked the unnamed legate in Bologna to approach Guido Reni. This records an instruction through an intermediary; it does not establish that Reni was approached.",
    "st-chp2-seciv-l19-29-ginnasi-main-picture-reni": "Haskell reports Ginnasi's intention that Guido Reni receive the principal picture. Preserve it as intention, not a completed assignment.",
    "st-chp2-seciv-l19-29-lanfranco-applied-for-picture": "Haskell says Lanfranco had written to Francesco applying for the proposed picture task. The letter, date, and outcome are not supplied.",
    "st-chp2-seciv-l19-29-reni-arrived-rome": "Haskell says Guido Reni came to Rome after months of negotiation and advance payments. The payers and amounts are not named.",
    "st-chp2-seciv-l19-29-reni-left-after-perceived-control": "Haskell says Reni left after a short stay, partly because he considered the committee's control humiliating. Preserve the account as Reni's perception and a partial cause.",
    "st-chp2-seciv-l19-29-second-capture-relative-interval": "The source says the second version was painted 'some dozen years or so' after the first. This is an approximate relative interval, not an absolute date.",
    "st-chp2-seciv-l19-29-smaller-picture-offered-cortona": "Haskell says Francesco had to content himself with an offer of a smaller picture to Pietro da Cortona. The offeror, picture subject, and completion are unspecified; retain Cortona as recipient.",
    "st-chp2-seciv-l19-29-three-artists-appear-st-peters": "Haskell says the three young artists made their first crucial appearances at St Peter's alongside an earlier generation. Their membership is inferred from nearby assignments; preserve 'neo-Venetian' and 'first crucial' as the author's characterization.",
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
