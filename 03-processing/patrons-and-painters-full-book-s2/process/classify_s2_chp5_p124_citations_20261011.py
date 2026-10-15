from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md"
PDF = ROOT / "02-sources/01-book/CHP-5.pdf"
PAGE_IMAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p124_page_review_20261011.png"
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE_SHA256 = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA256 = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
PAGE_IMAGE_SHA256 = "f2c6cbc1ac4c334af4e37528b44c6582e94d6545e35ebfaab99a998058caeb30"
TABLE_SHA256 = "0e0cb51c776cf027f5adb373aa8b863dce550e084c5081a531e3858b5aa066eb"
NOTES_SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l125-147"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp5-p124-citations-20261011")
RELATION_NOTE = "S2 source-attributed citation relation candidate only; this classification does not create a formal S6 edge."


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Record the two citations in p.124 note 1 as book-to-source relations; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the validated statement-table update")
    args = parser.parse_args()

    for path, expected, label in (
        (SOURCE, SOURCE_SHA256, "canonical source"),
        (PDF, PDF_SHA256, "chapter PDF"),
        (PAGE_IMAGE, PAGE_IMAGE_SHA256, "p.124 page image"),
        (STATEMENTS, TABLE_SHA256, "statement table"),
    ):
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"STOP: {label} changed: {path} ({actual})")

    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    notes = "\n".join(lines[124:147])
    if "See Monconys’ Journal des Voyages, 2eme partie, p. 439" not in notes or "Bellori’s Nota dei Musei" not in notes:
        raise SystemExit("STOP: the p.124 note 1 citation text changed")

    raw = STATEMENTS.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("STOP: duplicate statement IDs")
    target_id = "st-chp5-note-p124-n1-monconys-1664"
    if target_id not in by_id:
        raise SystemExit("STOP: Monconys note statement is missing")
    q = by_id[target_id].get("qualifiers", {})
    if q.get("relation_candidate") is not False or by_id[target_id].get("object_candidate_id") is not None:
        raise SystemExit("STOP: Monconys citation statement no longer matches the expected pre-correction state")
    new_id = "st-chp5-note-p124-n1-cites-bellori-nota"
    if new_id in by_id:
        raise SystemExit("STOP: Bellori citation statement already exists")

    revised = dict(by_id[target_id])
    revised["subject_candidate_id"] = "cand-2962"
    revised["object_candidate_id"] = "cand-11403"
    revised["predicate"] = "cites"
    rq = dict(q)
    rq.update({
        "claim": "Haskell cites Monconys's Journal des Voyages, part 2, page 439, for Simonelli's contacts with artists in 1664.",
        "qualification": "The statement records Haskell's citation locator; the cited page was not independently consulted.",
        "mentioned_candidate_ids": ["cand-2962", "cand-11403", "cand-2434"],
        "relation_candidate": True,
        "relation_candidate_note": RELATION_NOTE,
        "footnote_marker": 1,
        "footnote_segment": NOTES_SEGMENT_ID,
        "printed_page_locator": "p.124n1",
        "pdf_physical_page": 5,
        "text_layer": "authorial footnote citation",
    })
    rq.pop("footnote_links", None)
    rq.pop("footnote_link_status", None)
    revised["qualifiers"] = rq
    revised["original_quote"] = "See Monconys’ Journal des Voyages, 2eme partie, p. 439, for Simonelli’s contacts with artists in 1664."
    by_id[target_id] = revised

    bellori = {
        "statement_id": new_id,
        "segment_id": NOTES_SEGMENT_ID,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-4805",
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 142,
            "source_line_end": 142,
            "pdf_physical_page": 5,
            "printed_page_locator": "p.124n1",
            "claim": "Haskell cites Bellori's Nota dei Musei as a source for information about Simonelli's collecting.",
            "speaker": "Haskell",
            "text_layer": "authorial footnote citation",
            "qualification": "The citation is recorded as given by Haskell; Bellori's inventory was not independently consulted.",
            "mentioned_candidate_ids": ["cand-2962", "cand-4805", "cand-2434"],
            "footnote_marker": 1,
            "footnote_segment": NOTES_SEGMENT_ID,
            "relation_candidate": True,
            "relation_candidate_note": RELATION_NOTE,
            "linked_body_statement_ids": [
                "st-chp5-p124-simonelli-collection",
                "st-chp5-p124-simonelli-collection-contents",
                "st-chp5-p124-simonelli-favorite-annibale",
            ],
        },
        "original_quote": "Some information about his own collecting is given in Bellori’s Nota dei Musei",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
    }

    if not {"cand-2962", "cand-11403", "cand-4805"}.issubset({
        candidate for row in (revised, bellori)
        for candidate in [row.get("subject_candidate_id"), row.get("object_candidate_id")]
    }):
        raise SystemExit("STOP: citation endpoints are incomplete")

    newline = "\r\n" if "\r\n" in text else "\n"
    output = []
    for raw_line in text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if line.strip():
            original = json.loads(line)
            if original["statement_id"] == target_id:
                line = json.dumps(revised, ensure_ascii=False)
                ending = ending or newline
        output.append(line + ending)
    if output and not output[-1].endswith(("\n", "\r")):
        output[-1] += newline
    output.append(json.dumps(bellori, ensure_ascii=False) + newline)
    out = (b"\xef\xbb\xbf" if bom else b"") + "".join(output).encode("utf-8")
    print("p.124 note 1 source/PDF/page image/table hashes verified")
    print("citation relations planned: book cand-2962 -> Journal des Voyages cand-11403; book cand-2962 -> Nota dei Musei cand-4805")
    print(f"statement rows: {len(rows)} -> {len(rows)+1}; sha256={sha(out)}")
    if not args.apply:
        print("dry-run only; no file written")
        return 0
    if BACKUP.exists():
        raise SystemExit(f"STOP: recovery copy already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    temp = STATEMENTS.with_name(STATEMENTS.name + ".tmp-s2-chp5-p124-citations")
    temp.write_bytes(out)
    temp.replace(STATEMENTS)
    print(f"written; recovery copy={BACKUP.name}; sha256={sha(STATEMENTS.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
