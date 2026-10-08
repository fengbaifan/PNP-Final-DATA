"""Close verified body-to-footnote links found during the S2 handoff audit.

Source and table hashes are locked. Dry-run is the default; apply only after
reviewing the printed link plan. The original statement table is backed up to
the system temporary directory before writeback.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE_ROOT = ROOT / "02-sources" / "02-Markdown"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "5f78c091bbf4911c7f476aea7005d8dd569bbdfed8b531b227912001ce27b0c8",
    "02-sources/02-Markdown/02_CHP-2_intro.md": "4e93f8f73b981ff35a8b95df2f379e787c55fce396fee21d971dd7831b192e74",
    "02-sources/02-Markdown/02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
    "02-sources/02-Markdown/02_CHP-2_sec_ii.md": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
    "02-sources/02-Markdown/03_CHP-3_sec_ii.md": "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    "02-sources/02-Markdown/03_CHP-3_sec_iv.md": "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    "02-sources/02-Markdown/06_CHP-6_sec_i.md": "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    "02-sources/02-Markdown/06_CHP-6_intro.md": "ea2413fc5e957515a60e7284a1e1410f27dbe4bffaa4edaf896ff8cc96db4678",
    "02-sources/02-Markdown/07_CHP-7_sec_v.md": "956054d03a849749a1f7a0dbf0eade81c5cb1252a284cc26d024a7f9f134b432",
    "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
}

# Body statement -> [(printed marker, note segment, note source line, note statement IDs)].
BODY_LINKS = {
    "st-chp2-seci-l3-7-family": [
        (1, "chp-2:02_CHP-2_intro:l6-7", 7, [
            "st-chp2-intro-l6-7-pastor-xiii-citation",
            "st-chp2-intro-l6-7-pecchiai-citation",
        ]),
    ],
    "st-chp2-sec-ii-l10-18-rome-self-supporting-description": [
        (2, "chp-2:02_CHP-2_sec_ii:l147-193", 149, [
            "st-chp2-secii-l147-193-cite-barozzi-p228",
        ]),
    ],
    "st-chp2-sec-ii-l30-40-bernini-birthplace-and-mother": [
        (2, "chp-2:02_CHP-2_sec_ii:l147-193", 157, [
            "st-chp2-secii-l147-193-cite-passeri-p169",
        ]),
    ],
    "st-chp3-secii-l137-142-site-solution-praise": [
        (1, "chp-3:03_CHP-3_sec_ii:l144-179", 178, [
            "st-chp3-secii-p76-note1-relatione",
        ]),
    ],
    "st-chp3-secii-l137-142-style-departure": [
        (2, "chp-3:03_CHP-3_sec_ii:l144-179", 178, [
            "st-chp3-secii-p76-note2-wittkower",
        ]),
    ],
    "st-chp3-seciv-l106-116-heirs-funded-artists": [
        (5, "chp-3:03_CHP-3_sec_iv:l106-116", 114, [
            "st-chp3-seciv-l106-116-gaulli-payment-note-865-13",
        ]),
    ],
    "st-chp3-seciv-l106-116-prince-pamfili-reported-dead-1667": [
        (5, "chp-3:03_CHP-3_sec_iv:l106-116", 114, [
            "st-chp3-seciv-l106-116-gaulli-payment-note-865-13",
        ]),
    ],
    "st-chp6-p146-poussin-letter": [
        (1, "chp-6:06_CHP-6_intro:l7-11", 8, ["st-chp6-p146-note1-correspondance"]),
    ],
    "st-chp6-p146-arts-election": [
        (2, "chp-6:06_CHP-6_intro:l7-11", 9, ["st-chp6-p146-note2-passeri-haskell"]),
    ],
    "st-chp6-p146-multifactor-list": [
        (2, "chp-6:06_CHP-6_intro:l7-11", 9, ["st-chp6-p146-note2-passeri-haskell"]),
    ],
    "st-chp6-p146-castro-location": [
        (3, "chp-6:06_CHP-6_intro:l7-11", 10, ["st-chp6-p146-note3-pastor"]),
    ],
    "st-chp6-p146-urban-death": [
        (4, "chp-6:06_CHP-6_intro:l7-11", 11, ["st-chp6-p146-note4-gigli"]),
    ],
    # The p.201 footnote 1 belongs to the Caprara sentence; footnotes 4 and 5
    # occur inside the separate gallery list.
    "st-chp7-p201-v-caprara-commissions-bologna-paintings": [
        (1, "chp-7:07_CHP-7_sec_v:l62-76", 70, [
            "st-chp7-p201-n1-cite-zanotti-i",
            "st-chp7-p201-n1-cite-zanotti-ii",
        ]),
    ],
    "st-chp7-p201-v-eugene-gallery-pictures": [
        (4, "chp-7:07_CHP-7_sec_v:l62-76", 73, ["st-chp7-p201-n4-cite-zanotti"]),
        (5, "chp-7:07_CHP-7_sec_v:l62-76", 74, ["st-chp7-p201-n5-cite-de-dominici"]),
    ],
    "st-chp8-p241-additional-loans": [
        (1, "chp-8:08_CHP-8_sec_ii:l372-461", 457, ["st-chp8-p241-note1-fogolari-letter116"]),
        (2, "chp-8:08_CHP-8_sec_ii:l372-461", 458, ["st-chp8-p241-note2-uncertain-landscape-lender"]),
    ],
}

# Fix reverse links that were absent or wider than the printed note anchors.
NOTE_LINKS = {
    "st-chp2-intro-l6-7-pastor-xiii-citation": (
        [], ["st-chp2-seci-l3-7-family"]),
    "st-chp2-intro-l6-7-pecchiai-citation": (
        [], ["st-chp2-seci-l3-7-family"]),
    "st-chp2-secii-l147-193-cite-barozzi-p228": (
        ["st-chp2-sec-ii-l10-18-venetian-income-estimate"],
        ["st-chp2-sec-ii-l10-18-venetian-income-estimate",
         "st-chp2-sec-ii-l10-18-rome-self-supporting-description"]),
    "st-chp2-secii-l147-193-cite-passeri-p169": (
        ["st-chp2-sec-ii-l30-40-bernini-father-origin"],
        ["st-chp2-sec-ii-l30-40-bernini-birthplace-and-mother",
         "st-chp2-sec-ii-l30-40-bernini-father-origin"]),
    "st-chp3-secii-p76-note1-relatione": (
        ["st-chp3-secii-l137-142-site-solution-praise",
         "st-chp3-secii-l137-142-style-departure"],
        ["st-chp3-secii-l137-142-site-solution-praise"]),
    "st-chp3-secii-p76-note2-wittkower": (
        ["st-chp3-secii-l137-142-site-solution-praise",
         "st-chp3-secii-l137-142-style-departure"],
        ["st-chp3-secii-l137-142-style-departure"]),
    "st-chp3-seciv-l106-116-gaulli-payment-note-865-13": (
        [], ["st-chp3-seciv-l106-116-heirs-funded-artists",
             "st-chp3-seciv-l106-116-prince-pamfili-reported-dead-1667"]),
    "st-chp7-p201-n1-cite-zanotti-i": (
        ["st-chp7-p201-v-caprara-commissions-bologna-paintings",
         "st-chp7-p201-v-eugene-gallery-pictures"],
        ["st-chp7-p201-v-caprara-commissions-bologna-paintings"]),
    "st-chp7-p201-n1-cite-zanotti-ii": (
        ["st-chp7-p201-v-caprara-commissions-bologna-paintings",
         "st-chp7-p201-v-eugene-gallery-pictures"],
        ["st-chp7-p201-v-caprara-commissions-bologna-paintings"]),
    "st-chp7-p201-n4-cite-zanotti": (
        ["st-chp7-p201-v-eugene-gallery-pictures",
         "st-chp7-p201-v-list-not-exhaustive"],
        ["st-chp7-p201-v-eugene-gallery-pictures"]),
    "st-chp7-p201-n5-cite-de-dominici": (
        ["st-chp7-p201-v-eugene-gallery-pictures",
         "st-chp7-p201-v-pictures-by-neapolitan-painters"],
        ["st-chp7-p201-v-eugene-gallery-pictures"]),
}

# These exact OCR fragments anchor the printed markers and note lines used above.
SOURCE_CHECKS = {
    "02_CHP-2_intro.md": {
        7: ("Pastor, XIII", "Pecchiai, 1959"),
    },
    "02_CHP-2_sec_i.md": {
        4: ("family of merchants.1",),
    },
    "02_CHP-2_sec_ii.md": {
        13: ("almost self-supporting", "esteemed’.2"),
        33: ("Neapolitan mother", "Florentine.2"),
        149: ("2 ibid., I, p. 228",),
        157: ("Passeri sarcastically", "p. 169"),
    },
    "03_CHP-3_sec_ii.md": {
        138: ("problems it posed.1", "seen in Rome.2"),
        178: ("1 See Relatione", "2 Wittkower, 1958"),
    },
    "03_CHP-3_sec_iv.md": {
        112: ("died in 1667.5",),
        114: ("ibid., Fondo di Gesù", "N. 865-13"),
    },
    "06_CHP-6_sec_i.md": {
        4: ("favour at court’.1", "changes of fashion.2"),
        6: ("papal territory.3",),
        8: ("subjects.4",),
    },
    "06_CHP-6_intro.md": {
        8: ("1 CorresponJance",),
        9: ("2 Passeri",),
        10: ("3 Pastor",),
        11: ("4 For the effects",),
    },
    "07_CHP-7_sec_v.md": {
        43: ("paintings in 'Bologna1",),
        50: ("Bolognese painters4",),
        51: ("Ghislandi from Bergamo.5",),
        70: ("Above all by Crespi and dal Sole",),
        73: ("ibid., I, p. 302, and II, p. 43",),
        74: ("De Dominici, IV, pp. 432-3, 439",),
    },
    "08_CHP-8_sec_ii.md": {
        363: ("freschissimo’),1", "landscapes by Marco Ricci.2"),
        457: ("Letter 116 of 17 October 1705",),
        458: ("The lender is not mentioned by name",),
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows() -> list[dict]:
    return [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def by_id(rows: list[dict]) -> dict[str, dict]:
    indexed = {row["statement_id"]: row for row in rows}
    if len(indexed) != len(rows):
        raise SystemExit("duplicate statement_id in book-statements.jsonl")
    return indexed


def write_rows(rows: list[dict]) -> None:
    original_lines = TABLE.read_text(encoding="utf-8-sig").splitlines()
    original_by_id = {
        json.loads(line)["statement_id"]: line
        for line in original_lines
        if line.strip()
    }
    with TABLE.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            statement_id = row["statement_id"]
            original = original_by_id.get(statement_id)
            if original is not None and json.loads(original) == row:
                handle.write(original + "\n")
            else:
                handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed S2 footnote reconciliation")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    path = ROOT / relative
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"hash lock failed for {relative}: {actual}")

for filename, checks in SOURCE_CHECKS.items():
    lines = (SOURCE_ROOT / filename).read_text(encoding="utf-8-sig").splitlines()
    for line_number, fragments in checks.items():
        if line_number > len(lines) or any(fragment not in lines[line_number - 1] for fragment in fragments):
            raise SystemExit(f"S0 source anchor changed: {filename}:L{line_number}")

rows = read_rows()
indexed = by_id(rows)
all_body_ids = set(BODY_LINKS)
all_note_ids = {note_id for links in BODY_LINKS.values() for _, _, _, ids in links for note_id in ids}
all_note_ids.update(NOTE_LINKS)
if not (all_body_ids | all_note_ids).issubset(indexed):
    raise SystemExit(f"missing statement IDs: {sorted((all_body_ids | all_note_ids) - indexed.keys())}")

for body_id, links in BODY_LINKS.items():
    q = indexed[body_id].get("qualifiers", {})
    expected_markers = [marker for marker, _, _, _ in links]
    actual_markers = q.get("footnote_markers")
    if actual_markers is None:
        actual_markers = [q["footnote_marker"]] if q.get("footnote_marker") is not None else []
    if actual_markers != expected_markers:
        raise SystemExit(f"printed marker mismatch on {body_id}: {actual_markers} != {expected_markers}")
    for marker, note_segment, source_line, note_ids in links:
        for note_id in note_ids:
            note = indexed[note_id]
            nq = note.get("qualifiers", {})
            if note.get("segment_id") != note_segment or nq.get("source_line_start") != source_line:
                raise SystemExit(f"note locator mismatch: {note_id}")
            note_marker = nq.get("footnote_marker")
            if note_marker is not None and note_marker != marker:
                raise SystemExit(f"note marker mismatch: {note_id}: {note_marker} != {marker}")

for note_id, (before, after) in NOTE_LINKS.items():
    actual = indexed[note_id].get("qualifiers", {}).get("linked_body_statement_ids") or []
    if actual != before:
        raise SystemExit(f"unexpected prior body links on {note_id}: {actual} != {before}")

updated = copy.deepcopy(rows)
work = by_id(updated)
for body_id, links in BODY_LINKS.items():
    q = work[body_id].setdefault("qualifiers", {})
    refs = [
        {"marker": marker, "segment_id": note_segment, "source_line": source_line}
        for marker, note_segment, source_line, _ in links
    ]
    statement_ids = list(dict.fromkeys(note_id for _, _, _, ids in links for note_id in ids))
    note_segments = {note_segment for _, note_segment, _, _ in links}
    source_lines = list(dict.fromkeys(source_line for _, _, source_line, _ in links))
    q.update({
        "footnote_marker": links[0][0],
        "footnote_segment": next(iter(note_segments)),
        "footnote_segment_id": next(iter(note_segments)),
        "footnote_source_line": source_lines[0],
        "footnote_source_lines": source_lines,
        "footnote_refs": refs,
        "footnote_statement_ids": statement_ids,
        "footnote_link_status": "resolved_source_migration",
        "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_pending": False,
    })

for note_id, (_, after) in NOTE_LINKS.items():
    work[note_id]["qualifiers"]["linked_body_statement_ids"] = after

changed_ids = {
    row["statement_id"]
    for old, row in zip(rows, updated)
    if old != row
}
expected_changed_ids = all_body_ids | set(NOTE_LINKS)
if changed_ids != expected_changed_ids:
    raise SystemExit(f"unexpected write scope: {sorted(changed_ids ^ expected_changed_ids)}")

print("verified printed footnote anchors against hash-locked S0 lines and existing note statements")
print(f"planned body links: {len(BODY_LINKS)} statements across chapter 2, 3, 6, 7, and 8")
print(f"planned reverse-link corrections: {len(NOTE_LINKS)} note statements; no new evidence or entity rows")
print("p.76 note 1/2 are split to their respective statements; p.201 note 1 is limited to Caprara and notes 4/5 to the gallery list")
print("p.87 note 5 maps to its actual page-87 payment note at S0 L114, not the separate page-88 note 5")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-s2-footnote-handoff-20261008-"))
shutil.copy2(TABLE, backup_dir / TABLE.name)
write_rows(updated)

written = by_id(read_rows())
if set(written) != set(indexed):
    raise SystemExit(f"post-write statement ID set changed; recovery copy: {backup_dir}")
for body_id, links in BODY_LINKS.items():
    q = written[body_id]["qualifiers"]
    expected_refs = [
        {"marker": marker, "segment_id": note_segment, "source_line": source_line}
        for marker, note_segment, source_line, _ in links
    ]
    expected_ids = list(dict.fromkeys(note_id for _, _, _, ids in links for note_id in ids))
    if q.get("footnote_refs") != expected_refs or q.get("footnote_statement_ids") != expected_ids:
        raise SystemExit(f"post-write body link failed for {body_id}; recovery copy: {backup_dir}")
    if q.get("footnote_body_link_status") != "linked" or q.get("footnote_pending") is not False:
        raise SystemExit(f"post-write status failed for {body_id}; recovery copy: {backup_dir}")
for note_id, (_, expected) in NOTE_LINKS.items():
    actual = written[note_id]["qualifiers"].get("linked_body_statement_ids")
    if actual != expected:
        raise SystemExit(f"post-write reverse link failed for {note_id}; recovery copy: {backup_dir}")
print(f"applied S2 footnote reconciliation; recovery copy: {backup_dir}")
