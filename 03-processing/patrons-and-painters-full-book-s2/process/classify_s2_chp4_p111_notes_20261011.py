from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-4.pdf"
PAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p111_body_notes_page_review_20261011.png"
SEGMENTS = TABLES / "segments.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"

EXPECTED = {
    SOURCE: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    PDF: "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303",
    PAGE: "a06212b8a1403fbb25a335d431e1bc28e47e88f9c7e93a8dd6759fc097b031d5",
    STATEMENTS: "12dab9fad1438eec8331a931352b271a035d45045dfa7d51ec5b6e981fd1ac8b",
    CANDIDATES: "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    MENTIONS: "0251842ac93313725448baf44c7878ef71f74f5dfd31cdad8df19a5f84e3dca9",
    COVERAGE: "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
HASKELL_BOOK = "cand-2962"

EXISTING = {
    "st-chp4-sec-ii-notes-p111-fn1-marabottini": {
        "old_subject": "cand-5898", "old_object": "cand-2557",
        "old_predicate": "footnote_cites_marabottini_1954_for_testa_biography",
        "line": 277, "quote": "1 Marabottini, 1954.",
    },
    "st-chp4-sec-ii-notes-p111-fn2-blunt-mahon": {
        "old_subject": "cand-5899", "old_object": "cand-5905",
        "old_predicate": "footnote_reports_blunt_publication_and_mahon_alternative_dating",
        "line": 278,
        "quote": "2 Such as, for instance, the two landscapes formerly in Sir George Leon’s collection published by Blunt in Burlington Magazine, 1945, p. 186. Contrary to Sir Anthony Blunt’s opinion Denis Mahon suggests co ivincing reasons for believing that these were painted in 1638-9 before the artist’s visit to France— 1961, p. 120.",
    },
    "st-chp4-sec-ii-notes-p111-fn3-testa-prison-letters": {
        "old_subject": "cand-5906", "old_object": "cand-4830",
        "old_predicate": "footnote_locates_testa_prison_letters_in_bottari",
        "line": 279,
        "quote": "3 See Testa’s letters from prison in September 1637 published by Bottari, I, pp. 358-61.",
    },
}

ADDITIONS = [
    {
        "statement_id": "st-chp4-sec-ii-notes-p111-fn2-blunt-citation",
        "line": 278, "subject": HASKELL_BOOK, "object": "cand-5904",
        "predicate": "cites", "author": "cand-5902", "locator": "Burlington Magazine, 1945, p. 186",
        "claim": "Haskell cites Anthony Blunt’s article on the two landscapes, published in Burlington Magazine in 1945, page 186.",
        "quote": "the two landscapes formerly in Sir George Leon’s collection published by Blunt in Burlington Magazine, 1945, p. 186.",
        "mentions": ["cand-5899", "cand-5902", "cand-5903", "cand-5904"],
        "text_layer": "bibliographic citation",
        "qualification": "Article title is not supplied in the note; publication has not been independently consulted.",
    },
    {
        "statement_id": "st-chp4-sec-ii-notes-p111-fn2-mahon-citation",
        "line": 278, "subject": HASKELL_BOOK, "object": "cand-5905",
        "predicate": "cites", "author": "cand-1494", "locator": "Art de France, 1961, p. 120",
        "claim": "Haskell cites Denis Mahon’s 1961 article, page 120, for the alternative dating discussion.",
        "quote": "Denis Mahon suggests co ivincing reasons for believing that these were painted in 1638-9 before the artist’s visit to France— 1961, p. 120.",
        "mentions": ["cand-1494", "cand-5905"],
        "text_layer": "bibliographic citation",
        "qualification": "The title and venue follow the book bibliography; the cited article has not been independently consulted.",
        "ocr_corrections": [{"source_line": 278, "source_form": "co ivincing", "print_form": "convincing"}],
    },
    {
        "statement_id": "st-chp4-sec-ii-notes-p111-fn2-landscape-dating",
        "line": 278, "subject": "cand-5899", "object": "cand-1984",
        "predicate": "reported_painted_by_before_artist_visit_to_france",
        "claim": "Haskell reports Mahon’s view that the two landscapes were painted in 1638–39 before Poussin’s visit to France.",
        "quote": "these were painted in 1638-9 before the artist’s visit to France",
        "mentions": ["cand-5899", "cand-1494", "cand-1984", "cand-5905"],
        "text_layer": "reported art-historical dating",
        "qualification": "This is Mahon’s reported opinion, not an adopted or independently verified date. The artist resolves to Poussin from the preceding sentence on the same printed page; individual landscape titles remain unspecified.",
        "epistemic_status": "reported_opinion",
        "reported_date_range": "1638-1639",
        "attributed_to_candidate_id": "cand-1494",
    },
    {
        "statement_id": "st-chp4-sec-ii-notes-p111-fn3-letters-published-by-bottari",
        "line": 279, "subject": "cand-5906", "object": "cand-3507",
        "predicate": "published_by",
        "claim": "Haskell states that Pietro Testa’s prison letters from September 1637 were published by Bottari.",
        "quote": "Testa’s letters from prison in September 1637 published by Bottari",
        "mentions": ["cand-2557", "cand-5906", "cand-3507"],
        "text_layer": "reported publication relation",
        "qualification": "The letters and publication history have not been independently checked; the volume locator remains recorded in the separate citation statement.",
    },
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_atomic(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def citation_fields(row: dict, author: str, publication: str, locator: str, claim: str,
                    quote: str, mentions: list[str], qualification: str,
                    text_layer: str, line: int, correction: list[dict] | None = None) -> None:
    row["subject_candidate_id"] = HASKELL_BOOK
    row["object_candidate_id"] = publication
    row["predicate"] = "cites"
    row["original_quote"] = quote
    q = row["qualifiers"]
    q.pop("continuation_commentary", None)
    q["source_line_start"] = line
    q["source_line_end"] = line
    q["claim"] = claim
    q["speaker"] = "Haskell’s footnote"
    q["text_layer"] = text_layer
    q["qualification"] = qualification
    q["mentioned_candidate_ids"] = mentions
    q["relation_candidate"] = True
    q["relation_candidate_note"] = "Haskell’s citation to a named source; the cited material has not been independently consulted."
    q["citation_candidate_id"] = author
    q["citation_publication_candidate_id"] = publication
    q["citation_locator"] = locator
    q["citations"] = [{"source_candidate_id": author,
                        "publication_candidate_id": publication,
                        "locator": locator}]
    q["cited_material_not_independently_consulted"] = True
    if correction:
        q["ocr_corrections"] = correction
    else:
        q.pop("ocr_corrections", None)


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and atomize citations and claims in Chapter 4 p.111 notes.")
    parser.add_argument("--apply", action="store_true", help="write after all source, table, and row guards pass")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f"guard failed: {path.relative_to(ROOT)} SHA-256 {actual} != {expected}")
    segment = next((json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
                    if line.strip() and json.loads(line).get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("guard failed: p.111 source segment hash mismatch")

    types = {}
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            types[row["candidate_id"]] = row["suggested_type"]
    mention_candidates = set()
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["segment_id"] == SEGMENT_ID:
                mention_candidates.add(row["candidate_id"])

    before = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in before}
    if len(by_id) != len(before) or any(sid not in by_id for sid in EXISTING):
        raise SystemExit("guard failed: duplicate or missing target statement IDs")
    if any(item["statement_id"] in by_id for item in ADDITIONS):
        raise SystemExit("guard failed: added statement ID already exists")

    for cid in {HASKELL_BOOK, "cand-5897", "cand-5898", "cand-5899", "cand-5900", "cand-5901",
                "cand-5902", "cand-5903", "cand-5904", "cand-5905", "cand-1494", "cand-1984",
                "cand-5906", "cand-3507", "cand-4830"}:
        if cid not in types:
            raise SystemExit(f"guard failed: candidate {cid} is missing")
    if types[HASKELL_BOOK] != "archive" or types["cand-5898"] != "archive" or types["cand-5904"] != "archive" or types["cand-5905"] != "archive" or types["cand-4830"] != "archive":
        raise SystemExit("guard failed: Haskell book or cited publication type changed")
    for cid in {"cand-5897", "cand-5902", "cand-1494", "cand-3507", "cand-1984", "cand-5900"}:
        if types[cid] != "person":
            raise SystemExit(f"guard failed: expected person candidate {cid}")
    for cid in {"cand-5898", "cand-5897", "cand-5899", "cand-5900", "cand-5901", "cand-5902",
                "cand-5903", "cand-5904", "cand-5905", "cand-1494", "cand-1984", "cand-5906",
                "cand-3507", "cand-4830"}:
        if cid not in mention_candidates:
            raise SystemExit(f"guard failed: candidate mention {cid} is missing from the reviewed segment")

    after = copy.deepcopy(before)
    after_by_id = {row["statement_id"]: row for row in after}
    old_fn1 = after_by_id["st-chp4-sec-ii-notes-p111-fn1-marabottini"]
    old_fn2 = after_by_id["st-chp4-sec-ii-notes-p111-fn2-blunt-mahon"]
    old_fn3 = after_by_id["st-chp4-sec-ii-notes-p111-fn3-testa-prison-letters"]
    for sid, item in EXISTING.items():
        row = after_by_id[sid]
        q = row.get("qualifiers", {})
        if (row.get("segment_id") != SEGMENT_ID or q.get("source_line_start") != item["line"]
                or q.get("source_line_end") != item["line"]
                or row.get("subject_candidate_id") != item["old_subject"]
                or row.get("object_candidate_id") != item["old_object"]
                or row.get("predicate") != item["old_predicate"]
                or q.get("relation_candidate") is not None
                or row.get("original_quote") != item["quote"]):
            raise SystemExit(f"guard failed: existing source record changed for {sid}")

    citation_fields(old_fn1, "cand-5897", "cand-5898", "Marabottini, 1954",
                    "Haskell cites Marabottini (1954) in the biographical passage about Testa.",
                    "1 Marabottini, 1954.", ["cand-5897", "cand-5898"],
                    "Citation only; the cited publication has not been independently consulted.",
                    "bibliographic citation", 277)

    # Keep the original p.111 note-2 ID for its explicit former-collection claim.
    old_fn2["subject_candidate_id"] = "cand-5899"
    old_fn2["object_candidate_id"] = "cand-5901"
    old_fn2["predicate"] = "formerly_in_collection_of"
    old_fn2["original_quote"] = "the two landscapes formerly in Sir George Leon’s collection"
    q2 = old_fn2["qualifiers"]
    q2.pop("ocr_corrections", None)
    q2["claim"] = "Haskell identifies the two landscapes as formerly belonging to Sir George Leon’s collection."
    q2["speaker"] = "Haskell’s footnote"
    q2["text_layer"] = "reported provenance"
    q2["qualification"] = "The collection’s type and the dates of ownership are unresolved; the individual landscape titles are not supplied here."
    q2["mentioned_candidate_ids"] = ["cand-5899", "cand-5900", "cand-5901"]
    q2["relation_candidate"] = True
    q2["relation_candidate_note"] = "Explicit former-collection claim in Haskell’s note; keep the collection endpoint’s type unresolved."

    additions = []
    for item in ADDITIONS:
        row = copy.deepcopy(old_fn2 if item["line"] == 278 else old_fn3)
        row["statement_id"] = item["statement_id"]
        q = row["qualifiers"]
        q.pop("continuation_commentary", None)
        q.pop("ocr_corrections", None)
        q["source_line_start"] = item["line"]
        q["source_line_end"] = item["line"]
        q["pdf_physical_page"] = 22
        q["printed_page_locator"] = "p.111"
        q["claim"] = item["claim"]
        q["speaker"] = "Haskell’s footnote"
        q["text_layer"] = item["text_layer"]
        q["qualification"] = item["qualification"]
        q["mentioned_candidate_ids"] = item["mentions"]
        q["relation_candidate"] = True
        q["relation_candidate_note"] = "Source-explicit relation or citation; report the attributed claim without independent verification."
        row["subject_candidate_id"] = item["subject"]
        row["object_candidate_id"] = item["object"]
        row["predicate"] = item["predicate"]
        row["original_quote"] = item["quote"]
        if item.get("ocr_corrections"):
            q["ocr_corrections"] = item["ocr_corrections"]
        if item.get("author"):
            q["citation_candidate_id"] = item["author"]
            q["citation_publication_candidate_id"] = item["object"]
            q["citation_locator"] = item["locator"]
            q["citations"] = [{"source_candidate_id": item["author"],
                                "publication_candidate_id": item["object"],
                                "locator": item["locator"]}]
            q["cited_material_not_independently_consulted"] = True
        for key in ("epistemic_status", "reported_date_range", "attributed_to_candidate_id"):
            if key in item:
                q[key] = item[key]
        additions.append(row)

    citation_fields(old_fn2, "cand-1494", "cand-5905", "Art de France, 1961, p. 120",
                    "Haskell cites Denis Mahon’s 1961 article, page 120, for the alternative dating discussion.",
                    "Denis Mahon suggests co ivincing reasons for believing that these were painted in 1638-9 before the artist’s visit to France— 1961, p. 120.",
                    ["cand-1494", "cand-5905"],
                    "The title and venue follow the book bibliography; the cited article has not been independently consulted.",
                    "bibliographic citation", 278,
                    [{"source_line": 278, "source_form": "co ivincing", "print_form": "convincing"}])
    # Restore the ownership row after using the same original ID for the Mahon citation.
    old_fn2 = after_by_id["st-chp4-sec-ii-notes-p111-fn2-blunt-mahon"]
    old_fn2["subject_candidate_id"] = "cand-5899"
    old_fn2["object_candidate_id"] = "cand-5901"
    old_fn2["predicate"] = "formerly_in_collection_of"
    old_fn2["original_quote"] = "the two landscapes formerly in Sir George Leon’s collection"
    old_fn2["qualifiers"].pop("citation_candidate_id", None)
    old_fn2["qualifiers"].pop("citation_publication_candidate_id", None)
    old_fn2["qualifiers"].pop("citation_locator", None)
    old_fn2["qualifiers"].pop("citations", None)
    old_fn2["qualifiers"].pop("cited_material_not_independently_consulted", None)
    old_fn2["qualifiers"].pop("ocr_corrections", None)
    old_fn2["qualifiers"]["claim"] = "Haskell identifies the two landscapes as formerly belonging to Sir George Leon’s collection."
    old_fn2["qualifiers"]["speaker"] = "Haskell’s footnote"
    old_fn2["qualifiers"]["text_layer"] = "reported provenance"
    old_fn2["qualifiers"]["qualification"] = "The collection’s type and the dates of ownership are unresolved; the individual landscape titles are not supplied here."
    old_fn2["qualifiers"]["mentioned_candidate_ids"] = ["cand-5899", "cand-5900", "cand-5901"]
    old_fn2["qualifiers"]["relation_candidate"] = True
    old_fn2["qualifiers"]["relation_candidate_note"] = "Explicit former-collection claim in Haskell’s note; keep the collection endpoint’s type unresolved."
    old_fn2["qualifiers"]["continuation_commentary"] = EXISTING["st-chp4-sec-ii-notes-p111-fn2-blunt-mahon"].get("continuation_commentary", {})
    # The exact existing continuation note is part of the source context; preserve it from the pre-edit row.
    old_fn2["qualifiers"]["continuation_commentary"] = next(r for r in before if r["statement_id"] == "st-chp4-sec-ii-notes-p111-fn2-blunt-mahon")["qualifiers"].get("continuation_commentary")

    # The original p.111 note-3 row is the Haskell-to-Bottari citation.
    citation_fields(old_fn3, "cand-3507", "cand-4830", "Bottari, volume I, pp. 358-361",
                    "Haskell directs readers to Pietro Testa’s September 1637 prison letters in Bottari, volume I, pages 358-361.",
                    "3 See Testa’s letters from prison in September 1637 published by Bottari, I, pp. 358-61.",
                    ["cand-2557", "cand-5906", "cand-3507", "cand-4830"],
                    "Citation locator only; the letters and Bottari edition have not been independently consulted.",
                    "bibliographic citation", 279)

    # Replace the initially built addition list with the four normalized rows after endpoint assignment.
    additions = [r for r in additions if r["statement_id"] != "st-chp4-sec-ii-notes-p111-fn2-mahon-citation"]
    additions.append(copy.deepcopy(old_fn2)) if False else None
    # Rebuild the three p.111 note-2 additions and the letters-to-publisher relation from their definitions.
    for item in ADDITIONS:
        if item["statement_id"] == "st-chp4-sec-ii-notes-p111-fn2-mahon-citation":
            row = copy.deepcopy(old_fn2)
            # old_fn2 is intentionally restored as provenance above; create this citation from a fresh source template.
            row = copy.deepcopy(next(r for r in before if r["statement_id"] == "st-chp4-sec-ii-notes-p111-fn2-blunt-mahon"))
            row["statement_id"] = item["statement_id"]
            citation_fields(row, item["author"], item["object"], item["locator"], item["claim"], item["quote"], item["mentions"], item["qualification"], item["text_layer"], item["line"], item.get("ocr_corrections"))
            additions.append(row)
        elif item["statement_id"] not in {r["statement_id"] for r in additions}:
            additions.append(row for row in [])

    # Ensure all four additions are present with their declared endpoints and source anchors.
    add_by_id = {r["statement_id"]: r for r in additions}
    normalized_additions = []
    for item in ADDITIONS:
        row = add_by_id.get(item["statement_id"])
        if row is None:
            # The first, third, and fourth rows are created from an existing statement template.
            template_id = ("st-chp4-sec-ii-notes-p111-fn3-testa-prison-letters" if item["line"] == 279
                           else "st-chp4-sec-ii-notes-p111-fn2-blunt-mahon")
            row = copy.deepcopy(next(r for r in before if r["statement_id"] == template_id))
            row["statement_id"] = item["statement_id"]
            q = row["qualifiers"]
            q.pop("continuation_commentary", None)
            q.pop("ocr_corrections", None)
            q["source_line_start"] = item["line"]
            q["source_line_end"] = item["line"]
            q["pdf_physical_page"] = 22
            q["printed_page_locator"] = "p.111"
            q["claim"] = item["claim"]
            q["speaker"] = "Haskell’s footnote"
            q["text_layer"] = item["text_layer"]
            q["qualification"] = item["qualification"]
            q["mentioned_candidate_ids"] = item["mentions"]
            q["relation_candidate"] = True
            q["relation_candidate_note"] = "Source-explicit relation or citation; report the attributed claim without independent verification."
            row["subject_candidate_id"] = item["subject"]
            row["object_candidate_id"] = item["object"]
            row["predicate"] = item["predicate"]
            row["original_quote"] = item["quote"]
            if item.get("ocr_corrections"):
                q["ocr_corrections"] = item["ocr_corrections"]
            if item.get("author"):
                q["citation_candidate_id"] = item["author"]
                q["citation_publication_candidate_id"] = item["object"]
                q["citation_locator"] = item["locator"]
                q["citations"] = [{"source_candidate_id": item["author"], "publication_candidate_id": item["object"], "locator": item["locator"]}]
                q["cited_material_not_independently_consulted"] = True
            for key in ("epistemic_status", "reported_date_range", "attributed_to_candidate_id"):
                if key in item:
                    q[key] = item[key]
        normalized_additions.append(row)
    additions = normalized_additions

    # The date claim uses the exact image-confirmed Poussin context; keep the OCR correction on the Mahon citation only.
    after.extend(additions)
    output = ("\n".join(json.dumps(row, ensure_ascii=False) for row in after) + "\n").encode("utf-8")
    preview = [{"statement_id": sid, "subject": after_by_id[sid]["subject_candidate_id"],
                "object": after_by_id[sid]["object_candidate_id"], "predicate": after_by_id[sid]["predicate"],
                "relation_candidate": after_by_id[sid]["qualifiers"].get("relation_candidate")}
               for sid in EXISTING]
    preview.extend({"statement_id": item["statement_id"], "subject": item["subject"],
                    "object": item["object"], "predicate": item["predicate"], "relation_candidate": True}
                   for item in ADDITIONS)
    print(json.dumps({"mode": "APPLY PREFLIGHT" if args.apply else "DRY-RUN",
                      "updates": preview, "statements_before": len(before),
                      "statements_after": len(after)}, ensure_ascii=False, indent=2))
    if not args.apply:
        return 0

    backup = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp4-p111-notes-20261011")
    if backup.exists():
        raise SystemExit(f"guard failed: recovery copy already exists: {backup.name}")
    backup.write_bytes(STATEMENTS.read_bytes())
    write_atomic(STATEMENTS, output)
    print(f"APPLIED {STATEMENTS.relative_to(ROOT)} sha256={digest(STATEMENTS)}")
    print(f"recovery copy {backup.relative_to(ROOT)} sha256={digest(backup)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
