from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch16-p373-notes-classification-20261015")
EXPECTED_SHA256 = "47fd762726a7cc6f24feecd58929711a80cf44f515e00ca78e62e7049290e889"
SEGMENT = "chp-16:16_CHP-16_intro:l69-89"


DECISIONS = {
    "st-chp16-p373-note1-sasso-biography-citations": (
        False,
        "This is bibliographic guidance for a short biography, not a historical relation involving Sasso; the cited works remain evidence references.",
    ),
    "st-chp16-p373-note2-sasso-replies-mostly-missing": (
        False,
        "The note reports that most replies are missing; this is an archival condition claim, not a relation candidate.",
    ),
    "st-chp16-p373-note1-bollettino-portrait-citation": (
        False,
        "This is a locator to a portrait reference in a journal issue; the portrait-to-sitter and painter-to-portrait relations are recorded separately.",
    ),
    "st-chp16-p374-note1-guardi-patronage-reference": (
        False,
        "This directs readers to Haskell's fuller bibliography on Guardi patronage; it is a source locator, not an additional historical relation.",
    ),
    "st-chp16-p374-note2-strange-sasso-letter8": (
        False,
        "This identifies and dates a cited correspondence item; the Strange-Sasso correspondence relation is already stated separately in the body.",
    ),
    "st-chp16-p374-note3-armanni-sasso-letters-and-poore": (
        True,
        "The note locates the identified Armanni-Sasso letter volumes in a named archive; preserve the archival holding relation with the source attribution.",
    ),
    "st-chp16-p374-note3-poore-letter-locator": (
        True,
        "The note identifies a dated letter in which Mr Poore is discussed; the named person and source-level letter candidate are both retained.",
    ),
    "st-chp16-p374-note3-poore-auction-sales": (
        True,
        "The note reports two dated sales of prints and drawings belonging to Edward Poore; retain the sale/ownership claim without inferring any Tiepolo work.",
    ),
    "st-chp16-p374-note4-haskell-journal-276": (
        False,
        "This is a bibliographic page reference to Haskell's own publication, not a separate historical relation.",
    ),
    "st-chp16-p375-note1-sasso-sale-catalog": (
        True,
        "The note links Sasso's collection to its sale catalogue and reports two repository copies; retain the documentary relation and copy-location evidence as source-attributed.",
    ),
    "st-chp16-p375-note2-strange-sasso-letter57": (
        False,
        "This is a date and item locator for the correspondence already represented in the body; it supplies no additional correspondence partner or event claim.",
    ),
    "st-chp16-p375-note4-haskell-journal": (
        False,
        "This is a bibliographic page reference to Haskell's article; the cited article remains a source locator.",
    ),
    "st-chp16-p375-note5-della-lena-account-manuscript": (
        True,
        "The note locates the identified manuscript versions at Biblioteca Correr and cites a published discussion; keep the repository relation distinct from the citation.",
    ),
    "st-chp16-p375-note6-della-lena-ortes-letter": (
        True,
        "The note locates a dated letter in the Cicogna manuscript collection at Biblioteca Correr; preserve the archival holding relation.",
    ),
    "st-chp16-p377-note1-levi-celotti-date": (
        False,
        "This is a cited approximate death date for Celotti, a biographical attribute; Levi is recorded as the source rather than as a relation endpoint.",
    ),
    "st-chp16-p377-note2-celotti-advertisement": (
        False,
        "This gives a newspaper announcement as a locator; no separate sale or transaction is asserted in this note.",
    ),
    "st-chp16-p377-note3-christies-miniatures": (
        False,
        "This is a Christie’s sale locator; the separate statement that Ottley described the miniatures preserves the substantive attribution relation.",
    ),
    "st-chp16-p377-note4-celotti-1807-catalogue": (
        False,
        "This is a bibliographic locator for a 1807 catalogue, not a distinct sale or ownership relation.",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate() -> tuple[list[str], str]:
    current_hash = sha256(TABLE)
    if current_hash != EXPECTED_SHA256:
        raise SystemExit(f"table hash mismatch: expected {EXPECTED_SHA256}, got {current_hash}")
    lines = TABLE.read_text(encoding="utf-8").splitlines(keepends=True)
    selected = {}
    for line in lines:
        row = json.loads(line)
        if row["statement_id"] in DECISIONS:
            selected[row["statement_id"]] = row
    if set(selected) != set(DECISIONS):
        raise SystemExit(f"statement set mismatch: missing={sorted(set(DECISIONS)-set(selected))}")
    for statement_id, row in selected.items():
        if row["segment_id"] != SEGMENT:
            raise SystemExit(f"wrong segment for {statement_id}: {row['segment_id']}")
        if row["qualifiers"].get("relation_candidate") is not None:
            raise SystemExit(f"statement is no longer unset: {statement_id}")
    return lines, current_hash


def main() -> None:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    lines, before_hash = validate()
    counts = Counter(value for value, _ in DECISIONS.values())
    print(f"segment={SEGMENT} pending={len(DECISIONS)} classify_true={counts[True]} classify_false={counts[False]}")
    for statement_id, (value, note) in DECISIONS.items():
        print(f"{statement_id}: {str(value).lower()} | {note}")
    print(f"before_sha256={before_hash}")
    if args.preview:
        print("preview only; no table or backup written")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    changed_lines: list[str] = []
    seen: set[str] = set()
    for line in lines:
        row = json.loads(line)
        statement_id = row["statement_id"]
        if statement_id not in DECISIONS:
            changed_lines.append(line)
            continue
        value, note = DECISIONS[statement_id]
        row["qualifiers"]["relation_candidate"] = value
        row["qualifiers"]["relation_candidate_note"] = note
        changed_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        seen.add(statement_id)
    if seen != set(DECISIONS):
        raise SystemExit(f"write set mismatch: {sorted(set(DECISIONS)-seen)}")
    if sha256(TABLE) != before_hash:
        raise SystemExit("table changed after validation")

    shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
        temp_path = Path(stream.name)
        stream.writelines(changed_lines)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp_path, TABLE)
    print(f"backup={BACKUP}")
    print(f"after_sha256={sha256(TABLE)}")
    print("applied 18 classifications; unrelated statement lines preserved byte-for-byte")


if __name__ == "__main__":
    main()
