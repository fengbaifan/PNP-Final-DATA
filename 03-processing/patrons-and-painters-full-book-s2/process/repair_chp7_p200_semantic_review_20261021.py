from __future__ import annotations

import argparse
import csv
import io
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
MENTIONS_PATH = TABLES / "mentions.csv"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
SEGMENT_ID = "chp-7:07_CHP-7_sec_v:l9-18"
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_v.md"

def statement(statement_id: str, subject: str | None, object_: str | None,
              predicate: str, claim: str, quote: str, qualification: str,
              mentioned: list[str], note: str, related: list[str]) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 14 if "canvases" in statement_id else 13,
            "source_line_end": 14 if "canvases" in statement_id else 13,
            "printed_page": 200,
            "pdf_physical_page": 38,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "body",
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": True,
            "relation_candidate_note": note,
            "related_statement_ids": related,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


NEW_STATEMENTS = [
    statement(
        "st-chp7-p200-v-daun-rivalled-spanish-predecessors-patronage",
        "cand-0906", "cand-7295", "rivalled_predecessors_in_patronage_of_italian_art",
        "Haskell says Daun rivalled his Spanish predecessors in the patronage of Italian art.",
        "rivalled his Spanish predecessors in the patronage of Italian art",
        "The predecessors are unnamed; retain this as Haskell's comparative characterization rather than a measured ranking.",
        ["cand-0906", "cand-7295", "cand-4131"],
        "This separates the comparative patronage claim from Daun's viceroyal appointment; the unnamed predecessor group remains unresolved.",
        ["st-chp7-p200-v-daun-first-viceroy-and-patronage"],
    ),
    statement(
        "st-chp7-p200-v-paolo-works-for-daun-after-capture",
        "cand-1581", "cand-0906", "worked_for_after_conquest",
        "Haskell says Paolo de Matteis found himself working for Count Daun after the capture of Naples.",
        "and the Austrian commander Count Daun",
        "The source reports employment or patronage after the capture; it does not say whether each work was a formal commission.",
        ["cand-1581", "cand-0906", "cand-7293"],
        "This isolates Daun as one of the reported patrons; it does not infer a formal commission.",
        ["st-chp7-p200-v-paolo-works-for-binchs-and-daun"],
    ),
    statement(
        "st-chp7-p200-v-del-po-canvases-for-daun-palace",
        "cand-7296", "cand-7300", "produced_canvases_for_palace",
        "Haskell says Giacomo del Po produced canvases to decorate Count Daun's palace in Vienna.",
        "Solimena, Giacomo del Po and Paolo de Matteis all produced canvases to decorate his palace in Vienna",
        "The coordinated sentence attributes canvas production to each named painter, but supplies no titles or artist-to-canvas assignments; the group of canvases is unidentified.",
        ["cand-7296", "cand-7300", "cand-0906", "cand-7299", "cand-2772"],
        "This isolates del Po's contribution from the coordinated list; the canvas group remains unidentified and no title is inferred.",
        ["st-chp7-p200-v-painters-make-canvases-for-daun-palace"],
    ),
    statement(
        "st-chp7-p200-v-paolo-canvases-for-daun-palace",
        "cand-1581", "cand-7300", "produced_canvases_for_palace",
        "Haskell says Paolo de Matteis produced canvases to decorate Count Daun's palace in Vienna.",
        "Solimena, Giacomo del Po and Paolo de Matteis all produced canvases to decorate his palace in Vienna",
        "The coordinated sentence attributes canvas production to each named painter, but supplies no titles or artist-to-canvas assignments; the group of canvases is unidentified.",
        ["cand-1581", "cand-7300", "cand-0906", "cand-7299", "cand-2772"],
        "This isolates de Matteis's contribution from the coordinated list; the canvas group remains unidentified and no title is inferred.",
        ["st-chp7-p200-v-painters-make-canvases-for-daun-palace"],
    ),
]

NEW_STATEMENTS[0]["qualifiers"].update({
    "footnote_marker": 6,
    "footnote_statement_ids": [
        "st-chp7-p200-v-note6-cite-de-dominici",
        "st-chp7-p200-v-note6-cite-pascoli",
        "st-chp7-p200-v-note6-cite-tassi",
        "st-chp7-p200-v-note6-cite-zanotti",
        "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait",
    ],
    "footnote_refs": [{
        "marker": 6,
        "segment_id": SEGMENT_ID,
        "source_line": 18,
        "statement_ids": ["st-chp7-p200-v-daun-rivalled-spanish-predecessors-patronage"],
    }],
    "footnote_body_link_status": "linked",
})


def patch_statements(apply: bool) -> tuple[bytes, list[str]]:
    raw = STATEMENTS_PATH.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    updates = {
        "st-chp7-p200-v-treaties-confirm-changes-and-patronage-counterpart": {
            "subject_candidate_id": None,
            "predicate": "political_changes_had_counterparts_in_patronage",
            "qualifiers.claim": "Haskell says political changes following the War of the Spanish Succession were confirmed by the Treaties of Utrecht and Rastatt and had counterparts in the patronage of Italian art.",
            "qualifiers.qualification": "Preserve the correspondence as Haskell's interpretation; the treaties are not said to cause a particular commission.",
            "qualifiers.relation_candidate_note": "This records Haskell's interpretation of political changes and their patronage counterpart; the changes have no single bound candidate in this segment, and the treaties are not treated as causes of individual commissions.",
            "qualifiers.related_statement_ids": [
                "st-chp7-p200-v-victor-amadeus-breaks-from-louis-xiv",
                "st-chp7-p200-v-austrians-conquer-lombardy",
                "st-chp7-p200-v-austrians-seize-naples-from-spaniards",
            ],
        },
        "st-chp7-p200-v-contemporary-painting-interest-at-versailles": {
            "subject_candidate_id": None,
            "qualifiers.claim": "Haskell says this occasion stimulated interest in contemporary Italian painting among some younger art lovers who were tiring of the official style at Versailles.",
            "qualifiers.qualification": "The occasion is the preceding introduction of de Matteis to influential nobles and bankers; retain 'some' and Haskell's quoted 'official' characterization.",
            "qualifiers.relation_candidate_note": "This preserves Haskell's attributed claim about the effect of the preceding introduction; the occasion is not represented as a candidate endpoint.",
            "qualifiers.related_statement_ids": ["st-chp7-p200-v-destrees-introduces-paolo-to-nobles-bankers"],
        },
        "st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles": {
            "object_candidate_id": "cand-1021",
        },
        "st-chp7-p200-v-destrees-introduces-paolo-to-nobles-bankers": {
            "object_candidate_id": "cand-1581",
            "qualifiers.qualification": "The source names Paolo as the painter introduced; the nobles and bankers are unnamed, and no resulting commission is asserted.",
            "qualifiers.relation_candidate_note": "This records d'Estrées introducing de Matteis to an unnamed group; preserve the source's three participants and do not infer a commission.",
        },
        "st-chp7-p200-v-destrees-visits-naples-with-philip-v": {
            "object_candidate_id": "cand-7286",
            "qualifiers.qualification": "Naples is the setting; Philip V is the companion in the visit claim. Preserve Haskell's political description without independently resolving the succession claim.",
        },
        "st-chp7-p200-v-daun-first-viceroy-and-patronage": {
            "predicate": "became_first_viceroy_of",
            "qualifiers.claim": "Haskell says Daun became the first viceroy of the new regime in 1707.",
            "qualifiers.qualification": "The regime is unnamed; Daun's comparative patronage claim is recorded separately.",
            "qualifiers.relation_candidate_note": "This records only Daun's 1707 appointment as first viceroy of the unnamed new regime.",
            "qualifiers.related_statement_ids": ["st-chp7-p200-v-daun-rivalled-spanish-predecessors-patronage"],
            "original_quote": "Daun, who in 1707 was made the first viceroy of the new regime",
        },
        "st-chp7-p200-v-paolo-works-for-binchs-and-daun": {
            "qualifiers.claim": "Haskell says Paolo de Matteis found himself working for the English Admiral 'Binchs' after the capture of Naples.",
            "qualifiers.qualification": "The source separately names Count Daun as another patron; this statement isolates the source-form Admiral, and does not infer a formal commission.",
            "qualifiers.relation_candidate_note": "This preserves Haskell's report that de Matteis worked for the English Admiral 'Binchs' after the capture; the Count Daun clause is recorded separately.",
            "qualifiers.related_statement_ids": ["st-chp7-p200-v-paolo-works-for-daun-after-capture"],
        },
        "st-chp7-p200-v-painters-make-canvases-for-daun-palace": {
            "qualifiers.claim": "Haskell says Solimena produced canvases to decorate Count Daun's palace in Vienna.",
            "qualifiers.qualification": "The coordinated sentence attributes canvas production to each named painter; no title or individual artist-to-canvas assignment is supplied, and the other painters are split into linked statements.",
            "qualifiers.relation_candidate_note": "This isolates Solimena's contribution from the coordinated list; the canvas group remains unidentified and no title is inferred.",
            "qualifiers.related_statement_ids": [
                "st-chp7-p200-v-del-po-canvases-for-daun-palace",
                "st-chp7-p200-v-paolo-canvases-for-daun-palace",
            ],
        },
        "st-chp7-p200-v-victor-amadeus-breaks-from-louis-xiv": {
            "qualifiers.ocr_corrections": [{
                "source_line": 9,
                "ocr": "tortuous' manoeuvres",
                "print": "tortuous manoeuvres",
                "basis": "CHP-7.pdf physical page 38.",
            }],
        },
    }
    note6_body_links = [
        "st-chp7-p200-v-daun-first-viceroy-and-patronage",
        "st-chp7-p200-v-daun-rivalled-spanish-predecessors-patronage",
        "st-chp7-p200-v-note6-daun-commissioned-ghislandi-portrait",
    ]
    note6_refs = [{
        "marker": 6,
        "segment_id": SEGMENT_ID,
        "source_line": 18,
        "statement_ids": [
            "st-chp7-p200-v-daun-first-viceroy-and-patronage",
            "st-chp7-p200-v-daun-rivalled-spanish-predecessors-patronage",
        ],
    }]
    for cite_id in [
        "st-chp7-p200-v-note6-cite-de-dominici",
        "st-chp7-p200-v-note6-cite-pascoli",
        "st-chp7-p200-v-note6-cite-tassi",
        "st-chp7-p200-v-note6-cite-zanotti",
    ]:
        updates[cite_id] = {
            "qualifiers.related_body_statement_ids": note6_body_links,
            "qualifiers.linked_body_statement_ids": note6_body_links,
            "qualifiers.footnote_refs": note6_refs,
        }
    found: dict[str, dict] = {}
    rendered: list[str] = []
    existing_ids = {json.loads(line.lstrip("\ufeff"))["statement_id"] for line in lines}
    new_by_id = {r["statement_id"]: r for r in NEW_STATEMENTS}
    for statement_id in new_by_id:
        if statement_id in existing_ids:
            raise ValueError(f"new statement already exists: {statement_id}")
    insert_after = {
        "st-chp7-p200-v-daun-first-viceroy-and-patronage": [
            "st-chp7-p200-v-daun-rivalled-spanish-predecessors-patronage"
        ],
        "st-chp7-p200-v-paolo-works-for-binchs-and-daun": [
            "st-chp7-p200-v-paolo-works-for-daun-after-capture"
        ],
        "st-chp7-p200-v-painters-make-canvases-for-daun-palace": [
            "st-chp7-p200-v-del-po-canvases-for-daun-palace",
            "st-chp7-p200-v-paolo-canvases-for-daun-palace",
        ],
    }
    inserted: set[str] = set()
    for line in lines:
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        body = line[:-len(ending)] if ending else line
        record = json.loads(body)
        statement_id = record.get("statement_id")
        if statement_id in updates:
            if statement_id in found:
                raise ValueError(f"duplicate statement_id: {statement_id}")
            found[statement_id] = record
            for key, value in updates[statement_id].items():
                if "." in key:
                    parent, child = key.split(".", 1)
                    record[parent][child] = value
                else:
                    record[key] = value
            rendered.append(json.dumps(record, ensure_ascii=False) + ending)
        else:
            rendered.append(line)
        if statement_id in insert_after:
            for new_id in insert_after[statement_id]:
                rendered.append(json.dumps(new_by_id[new_id], ensure_ascii=False) + ending)
                inserted.add(new_id)
    if set(found) != set(updates):
        raise ValueError(f"statement precondition failed; missing={sorted(set(updates)-set(found))}")
    if inserted != set(new_by_id):
        raise ValueError(f"statement insertion anchor missing: {sorted(set(new_by_id)-inserted)}")
    output = ("\ufeff" if bom else "") + "".join(rendered)
    return output.encode("utf-8"), sorted(set(updates) | {r["statement_id"] for r in NEW_STATEMENTS})


def patch_csv(path: Path, key_column: str, key_value: str,
              changes: dict[str, str] | None, append: dict[str, str] | None,
              apply: bool, base_bytes: bytes | None = None,
              after_key: str | None = None) -> tuple[bytes, str]:
    raw = base_bytes if base_bytes is not None else path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    physical_lines = text.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(text, newline=""))
    header = next(reader)
    if key_column not in header:
        raise ValueError(f"{path.name} lacks key column {key_column}")
    key_index = header.index(key_column)
    previous_line = reader.line_num
    changed = False
    insert_line: int | None = None
    terminator = "\r\n" if b"\r\n" in raw else "\n"
    for row in reader:
        start_line = previous_line
        end_line = reader.line_num
        previous_line = end_line
        if after_key is not None and len(row) > key_index and row[key_index] == after_key:
            insert_line = end_line
        if len(row) <= key_index or row[key_index] != key_value:
            continue
        if changes is None:
            raise ValueError(f"duplicate key already present: {key_value}")
        if changed:
            raise ValueError(f"duplicate key row: {key_value}")
        row_dict = dict(zip(header, row))
        for field, value in changes.items():
            if field not in row_dict:
                raise ValueError(f"{path.name} lacks field {field}")
            row_dict[field] = value
        buf = io.StringIO(newline="")
        csv.writer(buf, lineterminator=terminator).writerow([row_dict[h] for h in header])
        physical_lines[start_line:end_line] = buf.getvalue().splitlines(keepends=True)
        changed = True
        if append is None:
            break
    if changes is not None and not changed:
        raise ValueError(f"key row not found: {key_value}")
    if append is not None:
        if append.get(key_column) != key_value:
            raise ValueError("append key mismatch")
        buf = io.StringIO(newline="")
        csv.writer(buf, lineterminator=terminator).writerow([append.get(h, "") for h in header])
        new_lines = buf.getvalue().splitlines(keepends=True)
        if after_key is not None:
            if insert_line is None:
                raise ValueError(f"insertion anchor not found: {after_key}")
            physical_lines[insert_line:insert_line] = new_lines
        else:
            if not text.endswith(("\n", "\r")):
                physical_lines.append(terminator)
            physical_lines.extend(new_lines)
    output = ("\ufeff" if bom else "") + "".join(physical_lines)
    return output.encode("utf-8"), "updated" if changed else "appended"


def atomic_write(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Review and repair the p.200 body S2 statements and mention span.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    statements_bytes, changed_statement_ids = patch_statements(args.apply)
    mentions_bytes, _ = patch_csv(
        MENTIONS_PATH, "mention_id", "m-chp7-p200-v-040",
        {"note": "Haskell's p.200 n.5 identifies the source form 'Binchs' as Admiral Byng; S3 groups the two source forms as one source-local person, not as an external identity verification."},
        None,
        args.apply,
    )
    mentions_bytes, _ = patch_csv(
        MENTIONS_PATH, "mention_id", "m-chp7-p200-v-daun-portrait",
        None,
        {
            "mention_id": "m-chp7-p200-v-daun-portrait",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-7302",
            "surface_form": "his portrait",
            "start_char": "2625",
            "end_char": "2637",
            "note": "Anaphoric reference to the unidentified portrait Count Daun commissioned from Vittore Ghislandi in Haskell's p.200 n.6.",
        },
        args.apply,
        base_bytes=mentions_bytes,
        after_key="m-chp7-p200-v-070",
    )
    coverage_bytes, coverage_action = patch_csv(
        COVERAGE_PATH, "segment_id", SEGMENT_ID,
        {"note": "p.200 body and footnote 6 (the text present at L18) read against CHP-7.pdf physical p.38. Footnote 6 is cross-linked to the claims at L13; footnotes 1-5 and 7 in the later composite block L62-76 are now migrated. The L17 sentence ending 'furnishing' closes at p.201 L43. S2 corrections: printed 'tortuous manoeuvres' for OCR 'tortuous\u0027 manoeuvres'; printed 'further' for OCR 'Anther'; printed 'Pascoli, II' for OCR 'H'; printed 'Ghislandi' for OCR 'Gliislandi'. Source text unchanged."},
        None,
        args.apply,
    )

    print(f"mode={'apply' if args.apply else 'dry-run'}")
    print(f"statement rows changed/appended: {len(changed_statement_ids)}")
    print("statement IDs:")
    for statement_id in changed_statement_ids:
        print(f"  {statement_id}")
    print("mentions.csv: updated Admiral Byng cross-reference note; appended m-chp7-p200-v-daun-portrait")
    print(f"s2-coverage.csv: {coverage_action}; segment={SEGMENT_ID}")
    if args.apply:
        atomic_write(STATEMENTS_PATH, statements_bytes)
        atomic_write(MENTIONS_PATH, mentions_bytes)
        atomic_write(COVERAGE_PATH, coverage_bytes)
    else:
        print("No files written; rerun with --apply to write these preflighted changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
