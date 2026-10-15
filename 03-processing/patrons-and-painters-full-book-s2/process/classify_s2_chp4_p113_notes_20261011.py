from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-4.pdf"
PAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p113_body_notes_page_review_20261011.png"

EXPECTED = {
    SOURCE: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    PDF: "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303",
    PAGE: "3935113f75d7898b0f6f1f130b47c4580422d1eee8dbe9e9502230e4e53f4294",
    STATEMENTS: "276fece27ca3e4b0b28cedb1d50e082ae85334daef4cb76433b3980c3c15ea32",
    CANDIDATES: "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    MENTIONS: "01b0dbe6ab585430923576913ca45d81185ef5f8cad8c744e979d67a0c87fb4e",
    COVERAGE: "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}

SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
SOURCE_LINES = {
    287: "1 As stated in note 2, p. in, Mr Mahon believes that the ex-Leon landscapes date from before Poussin’s visit to Paris.",
    288: "2 See p. 106, note 2.",
    289: "3 Lumbroso, p. 314, and Haskell and Rinehart, i960...",
    290: "4 For the eventual fate of the Museum Chartaceum see Vermeule, and Fleming, 1958, p. 164. The collection of paintings probably began to be dispersed not very long after Carlo Antonio’s death in 1689— see Haskell and Rinehart, i960. Only a small fraction of it can now be identified.",
}

FN1 = "st-chp4-sec-ii-notes-p113-fn1-mahon-landscapes"
FN2 = "st-chp4-sec-ii-notes-p113-fn2-cross-reference"
FN3 = "st-chp4-sec-ii-notes-p113-fn3-lumbroso-rinehart"
FN4_MUSEUM = "st-chp4-sec-ii-notes-p113-fn4-chartaceum-fate"
FN4_COLLECTION = "st-chp4-sec-ii-notes-p113-fn4-painting-collection"
NEW_IDS = {
    "fn3_rinehart": "st-chp4-sec-ii-notes-p113-fn3-rinehart-citation",
    "fn4_rinehart": "st-chp4-sec-ii-notes-p113-fn4-rinehart-citation",
    "fn4_identification": "st-chp4-sec-ii-notes-p113-fn4-collection-identification-limit",
}
BACKUP_SUFFIX = ".bak-s2-chp4-p113-notes-20261011"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_atomic(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and atomize the p.113 footnote statements.")
    parser.add_argument("--apply", action="store_true", help="write only after every source and table guard passes")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f"guard failed: {path.relative_to(ROOT)} SHA-256 {actual} != {expected}")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for line_no, expected in SOURCE_LINES.items():
        if lines[line_no - 1] != expected:
            raise SystemExit(f"guard failed: source line {line_no} changed")
    source_segment = next((r for r in read_jsonl(SEGMENTS) if r.get("segment_id") == SEGMENT_ID), None)
    if not source_segment or source_segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("guard failed: normalized segment identity or hash changed")

    page_text = "\n".join(lines[231:308])
    mention_expectations = {
        "m-chp4-sec-ii-notes-p113-0029": ("cand-5905", "note 2, p. in", 9200, 9213),
        "m-chp4-sec-ii-notes-p113-0028": ("cand-1494", "Mahon", 9218, 9223),
        "m-chp4-sec-ii-notes-p113-0027": ("cand-5899", "ex-Leon landscapes", 9242, 9260),
        "m-chp4-sec-ii-notes-p113-0030": ("cand-5778", "p. 106, note 2", 9310, 9324),
        "m-chp4-sec-ii-notes-p113-0031": ("cand-5626", "Lumbroso", 9328, 9336),
        "m-chp4-sec-ii-notes-p113-0032": ("cand-5683", "p. 314", 9338, 9344),
        "m-chp4-sec-ii-notes-p113-0033": ("cand-5658", "Haskell and Rinehart, i960", 9350, 9376),
        "m-chp4-sec-ii-notes-p113-0034": ("cand-5920", "Museum Chartaceum", 9411, 9428),
        "m-chp4-sec-ii-notes-p113-0035": ("cand-5689", "Vermeule", 9433, 9441),
        "m-chp4-sec-ii-notes-p113-0037": ("cand-5928", "Vermeule, and Fleming, 1958, p. 164", 9433, 9468),
        "m-chp4-sec-ii-notes-p113-0036": ("cand-5929", "Fleming", 9447, 9454),
        "m-chp4-sec-ii-notes-p113-0038": ("cand-5921", "collection of paintings", 9474, 9497),
        "m-chp4-sec-ii-notes-p113-0039": ("cand-2035", "Carlo Antonio", 9549, 9562),
        "m-chp4-sec-ii-notes-p113-0040": ("cand-5927", "Carlo Antonio’s death in 1689", 9549, 9578),
        "m-chp4-sec-ii-notes-p113-0041": ("cand-5658", "Haskell and Rinehart, i960", 9584, 9610),
        "m-chp4-sec-ii-notes-p113-0042": ("cand-5921", "Only a small fraction of it", 9612, 9639),
    }
    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        mentions = list(csv.DictReader(stream))
    actual_mentions = {r["mention_id"]: r for r in mentions if r.get("mention_id") in mention_expectations}
    if set(actual_mentions) != set(mention_expectations):
        raise SystemExit("guard failed: expected p.113 source mentions changed")
    for mention_id, (candidate_id, surface, start, end) in mention_expectations.items():
        row = actual_mentions[mention_id]
        if (row.get("segment_id") != SEGMENT_ID or row.get("candidate_id") != candidate_id
                or row.get("surface_form") != surface or int(row["start_char"]) != start
                or int(row["end_char"]) != end or page_text[start:end] != surface):
            raise SystemExit(f"guard failed: p.113 mention mismatch: {mention_id}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        candidates = {r["candidate_id"]: r for r in csv.DictReader(stream)}
    required_types = {
        "cand-2962": "archive",
        "cand-5683": "archive",
        "cand-5658": "archive",
        "cand-5928": "archive",
        "cand-1494": "person",
        "cand-5899": "work",
        "cand-2035": "person",
        "cand-5927": "event",
    }
    for candidate_id, expected_type in required_types.items():
        if candidates.get(candidate_id, {}).get("suggested_type") != expected_type:
            raise SystemExit(f"guard failed: candidate type changed for {candidate_id}")

    before = read_jsonl(STATEMENTS)
    by_id = {r["statement_id"]: r for r in before}
    if len(by_id) != len(before):
        raise SystemExit("guard failed: duplicate statement IDs exist")
    for new_id in NEW_IDS.values():
        if new_id in by_id:
            raise SystemExit(f"guard failed: new statement already exists: {new_id}")

    expected_old = {
        FN1: ("cand-1494", "cand-5899", "citation_and_reported_dating_opinion"),
        FN2: ("cand-1984", "cand-1390", "cross_reference_to_p106_note2"),
        FN3: ("cand-5626", "cand-5658", "citation_sources_for_portrait_discussion"),
        FN4_MUSEUM: ("cand-5920", "cand-5928", "cites_study_on_paper_museum_fate"),
        FN4_COLLECTION: ("cand-5921", "cand-5927", "painting_collection_began_dispersing_after_1689"),
    }
    for statement_id, (subject, obj, predicate) in expected_old.items():
        row = by_id.get(statement_id)
        if not row or row.get("segment_id") != SEGMENT_ID:
            raise SystemExit(f"guard failed: missing target statement {statement_id}")
        if (row.get("subject_candidate_id") != subject or row.get("object_candidate_id") != obj
                or row.get("predicate") != predicate or (row.get("qualifiers") or {}).get("relation_candidate") is not None):
            raise SystemExit(f"guard failed: target statement changed before classification: {statement_id}")

    after = json.loads(json.dumps(before))
    out = {r["statement_id"]: r for r in after}

    q = out[FN1]["qualifiers"]
    q["relation_candidate"] = True
    q["relation_candidate_note"] = "Haskell explicitly attributes the dating view to Mahon. The landscapes and the opinion remain source-attributed; the cited article was not independently consulted."

    r = out[FN2]
    r["subject_candidate_id"] = None
    r["object_candidate_id"] = None
    q = r["qualifiers"]
    q["mentioned_candidate_ids"] = ["cand-5778"]
    q["relation_candidate"] = False
    q["relation_candidate_note"] = "This is an internal page-and-footnote pointer only. Poussin and Leonardo belong to the referenced discussion and are not asserted as endpoints by this note."

    r = out[FN3]
    r["subject_candidate_id"] = "cand-2962"
    r["object_candidate_id"] = "cand-5683"
    r["predicate"] = "cites"
    q = r["qualifiers"]
    q.update({
        "claim": "Haskell’s book cites G. Lumbroso’s Notizie sulla vita di Cassiano dal Pozzo, p. 314, in connection with the unfinished-portrait report.",
        "mentioned_candidate_ids": ["cand-5626", "cand-5683"],
        "relation_candidate": True,
        "relation_candidate_note": "This records Haskell’s bibliographic pointer to Lumbroso’s publication; the cited page was not independently consulted.",
        "citation_candidate_id": "cand-5626",
        "citation_publication_candidate_id": "cand-5683",
        "citation_locator": "Lumbroso, p. 314",
        "cited_material_not_independently_consulted": True,
        "ocr_corrections": [{"source_line": 289, "source_form": "i960...", "print_form": "1960."}],
    })

    fn3_rinehart = {
        "statement_id": NEW_IDS["fn3_rinehart"],
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-5658",
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 289,
            "source_line_end": 289,
            "pdf_physical_page": 24,
            "printed_page_locator": "p.113 footnote 3",
            "claim": "Haskell’s footnote also cites the 1960 Haskell and Rinehart article following the unfinished-portrait report.",
            "speaker": "Haskell",
            "text_layer": "bibliographic attribution",
            "mentioned_candidate_ids": ["cand-5658"],
            "relation_candidate": True,
            "relation_candidate_note": "This records a citation pointer only; the cited article was not independently consulted.",
            "citation_publication_candidate_id": "cand-5658",
            "citation_locator": "Haskell and Rinehart, 1960",
            "cited_material_not_independently_consulted": True,
            "ocr_corrections": [{"source_line": 289, "source_form": "i960...", "print_form": "1960."}],
        },
        "original_quote": SOURCE_LINES[289],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }

    r = out[FN4_MUSEUM]
    r["subject_candidate_id"] = "cand-2962"
    r["predicate"] = "cites"
    q = r["qualifiers"]
    q.update({
        "claim": "Haskell’s footnote cites a Vermeule and Fleming publication (1958, p. 164) for the eventual fate of the Museum Chartaceum.",
        "mentioned_candidate_ids": ["cand-5920", "cand-5689", "cand-5929", "cand-5928"],
        "relation_candidate": True,
        "relation_candidate_note": "This is a bibliographic pointer only; the cited publication’s title and edition are not identified and it was not independently consulted.",
        "citation_context_candidate_id": "cand-5920",
        "citation_author_candidate_ids": ["cand-5689", "cand-5929"],
        "citation_publication_candidate_id": "cand-5928",
        "citation_locator": "Vermeule and Fleming, 1958, p. 164",
        "cited_material_not_independently_consulted": True,
    })

    r = out[FN4_COLLECTION]
    r["object_candidate_id"] = "cand-5927"
    r["original_quote"] = "The collection of paintings probably began to be dispersed not very long after Carlo Antonio’s death in 1689"
    q = r["qualifiers"]
    q.update({
        "claim": "Haskell says Cassiano’s painting collection probably began to be dispersed not very long after Carlo Antonio’s death in 1689.",
        "mentioned_candidate_ids": ["cand-5921", "cand-2035", "cand-5927"],
        "qualification": "‘Probably’ and ‘not very long after’ remain qualified. This concerns the painting collection, distinct from the Museum Chartaceum; Haskell reports the chronology, which was not independently verified.",
        "relation_candidate": True,
        "relation_candidate_note": "This is Haskell’s qualified historical claim about the collection’s dispersal in relation to Carlo Antonio’s death, not an independently verified event.",
        "ocr_corrections": [],
    })

    fn4_rinehart = {
        "statement_id": NEW_IDS["fn4_rinehart"],
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-5658",
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 290,
            "source_line_end": 290,
            "pdf_physical_page": 24,
            "printed_page_locator": "p.113 footnote 4",
            "claim": "Haskell’s footnote cites the 1960 Haskell and Rinehart article in connection with the reported dispersal of Cassiano’s painting collection.",
            "speaker": "Haskell",
            "text_layer": "bibliographic attribution",
            "mentioned_candidate_ids": ["cand-5921", "cand-5658"],
            "relation_candidate": True,
            "relation_candidate_note": "This records a citation pointer only; the cited article was not independently consulted.",
            "citation_context_candidate_id": "cand-5921",
            "citation_publication_candidate_id": "cand-5658",
            "citation_locator": "Haskell and Rinehart, 1960",
            "cited_material_not_independently_consulted": True,
            "ocr_corrections": [{"source_line": 290, "source_form": "i960", "print_form": "1960"}],
        },
        "original_quote": "see Haskell and Rinehart, i960",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }

    fn4_identification = {
        "statement_id": NEW_IDS["fn4_identification"],
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-5921",
        "object_candidate_id": None,
        "predicate": "only_small_fraction_identifiable_today",
        "qualifiers": {
            "source_line_start": 290,
            "source_line_end": 290,
            "pdf_physical_page": 24,
            "printed_page_locator": "p.113 footnote 4",
            "claim": "Haskell says that only a small fraction of Cassiano’s painting collection can now be identified.",
            "speaker": "Haskell",
            "text_layer": "authorial bibliographic note",
            "mentioned_candidate_ids": ["cand-5921"],
            "qualification": "‘It’ refers to the painting collection in the preceding sentence, not the Museum Chartaceum. This identification limit is Haskell’s report, not independently audited.",
            "relation_candidate": False,
            "relation_candidate_note": "This is a scalar claim about the surviving identification of a collection, not a relation between entities.",
            "footnote_marker": 4,
        },
        "original_quote": "Only a small fraction of it can now be identified.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }

    after.extend([fn3_rinehart, fn4_rinehart, fn4_identification])
    if len({r.get("statement_id") for r in after}) != len(after):
        raise SystemExit("guard failed: output would contain duplicate statement IDs")

    output = ("\n".join(json.dumps(row, ensure_ascii=False) for row in after) + "\n").encode("utf-8")
    preview = {
        "mode": "APPLY PREFLIGHT" if args.apply else "DRY-RUN",
        "updates": [
            {"statement_id": FN1, "relation_candidate": True, "predicate": out[FN1]["predicate"]},
            {"statement_id": FN2, "relation_candidate": False, "subject": None, "object": None},
            {"statement_id": FN3, "relation_candidate": True, "subject": "cand-2962", "object": "cand-5683", "predicate": "cites"},
            {"statement_id": NEW_IDS["fn3_rinehart"], "relation_candidate": True, "subject": "cand-2962", "object": "cand-5658", "predicate": "cites"},
            {"statement_id": FN4_MUSEUM, "relation_candidate": True, "subject": "cand-2962", "object": "cand-5928", "predicate": "cites"},
            {"statement_id": FN4_COLLECTION, "relation_candidate": True, "subject": "cand-5921", "object": "cand-5927", "predicate": out[FN4_COLLECTION]["predicate"]},
            {"statement_id": NEW_IDS["fn4_rinehart"], "relation_candidate": True, "subject": "cand-2962", "object": "cand-5658", "predicate": "cites"},
            {"statement_id": NEW_IDS["fn4_identification"], "relation_candidate": False, "subject": "cand-5921", "object": None},
        ],
        "statements_before": len(before),
        "statements_after": len(after),
        "mentions_unchanged": len(mentions),
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return 0

    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"guard failed: recovery copy already exists: {backup.name}")
    backup.write_bytes(STATEMENTS.read_bytes())
    write_atomic(STATEMENTS, output)
    print(f"APPLIED {STATEMENTS.relative_to(ROOT)} sha256={digest(STATEMENTS)}")
    print(f"recovery copy {backup.relative_to(ROOT)} sha256={digest(backup)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
