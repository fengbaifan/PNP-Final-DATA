from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-4.pdf"
PAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p109_body_notes_page_review_20261011.png"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"

EXPECTED = {
    SOURCE: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    PDF: "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303",
    PAGE: "f1ad93fa61324cba7aff7cac4a21fcea631d252d44a3262116680adf07498926",
    STATEMENTS: "38439a0e0fae7edb81ee343aeb8e419c4532ead933a3dad5c6a81b995631a4e2",
    CANDIDATES: "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    MENTIONS: "0251842ac93313725448baf44c7878ef71f74f5dfd31cdad8df19a5f84e3dca9",
    COVERAGE: "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
HASKELL_BOOK = "cand-2962"

PLAN = {
    "st-chp4-sec-ii-notes-p109-fn1-epigrammata-citation": {
        "old_subject": "cand-5832", "old_object": "cand-5837",
        "old_predicate": "cites_1641_epigrammata_print_dedicated_in_cassiano_library",
        "line": 269, "source_candidate": "cand-5838", "publication": "cand-5837",
        "locator": "Epigrammata in virorum literarorum imagines (Rome, 1641)",
    },
    "st-chp4-sec-ii-notes-p109-fn2-gaudenzi-correspondence": {
        "old_subject": "cand-2036", "old_object": "cand-5839",
        "old_predicate": "cites_vatican_correspondence_between_cassiano_and_gaudenzi",
        "line": 270, "source_candidate": "cand-2036", "publication": "cand-5839",
        "locator": "Biblioteca Vaticana, Urb. Lat. 1626 and 1628, cited folios",
    },
    "st-chp4-sec-ii-notes-p109-fn3-pintard-citation": {
        "old_subject": "cand-5848", "old_object": "cand-1116",
        "old_predicate": "cites_pintard_pages_251_to_253_for_gaudenzi_description",
        "line": 271, "source_candidate": "cand-5818", "publication": "cand-5848",
        "locator": "Pintard, pp. 251-253",
    },
    "st-chp4-sec-ii-notes-p109-fn5-lumbroso-p165": {
        "old_subject": "cand-5626", "old_object": "cand-2036",
        "old_predicate": "cites_lumbroso_on_cassiano_interest_in_contemporary_ceremonial_occasions",
        "line": 273, "source_candidate": "cand-5626", "publication": "cand-5853",
        "locator": "Lumbroso, p. 165",
    },
    "st-chp4-sec-ii-notes-p109-fn6-lumbroso-p199": {
        "old_subject": "cand-5626", "old_object": "cand-5854",
        "old_predicate": "cites_lumbroso_page_199_for_cassiano_collecting_purpose_quote",
        "line": 274, "source_candidate": "cand-5626", "publication": "cand-5854",
        "locator": "Lumbroso, p. 199",
    },
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows() -> list[dict]:
    return [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and normalize the five p.109 footnote citation statements.")
    parser.add_argument("--apply", action="store_true", help="write after all source, table, and row guards pass")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f"guard failed: {path.relative_to(ROOT)} SHA-256 {actual} != {expected}")

    segment = next((json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
                    if line.strip() and json.loads(line).get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("guard failed: p.109 source segment hash mismatch")

    types = {}
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            types[row["candidate_id"]] = row["suggested_type"]

    before = load_rows()
    by_id = {row["statement_id"]: row for row in before}
    if len(by_id) != len(before):
        raise SystemExit("guard failed: duplicate statement IDs")
    if any(sid not in by_id for sid in PLAN):
        raise SystemExit("guard failed: target statement set changed")

    after = [dict(row) for row in before]
    after_by_id = {row["statement_id"]: row for row in after}
    for sid, item in PLAN.items():
        row = after_by_id[sid]
        q = row.get("qualifiers", {})
        if (row.get("segment_id") != SEGMENT_ID or q.get("source_line_start") != item["line"]
                or q.get("source_line_end") != item["line"]):
            raise SystemExit(f"guard failed: source anchor changed for {sid}")
        if (row.get("subject_candidate_id") != item["old_subject"]
                or row.get("object_candidate_id") != item["old_object"]
                or row.get("predicate") != item["old_predicate"]
                or q.get("relation_candidate") is not None):
            raise SystemExit(f"guard failed: existing classification changed for {sid}")
        for candidate_id in (HASKELL_BOOK, item["source_candidate"], item["publication"]):
            if candidate_id not in types:
                raise SystemExit(f"guard failed: missing candidate {candidate_id}")
        if types[HASKELL_BOOK] != "archive" or types[item["publication"]] != "archive":
            raise SystemExit(f"guard failed: expected book and cited item to be archives for {sid}")
        row["subject_candidate_id"] = HASKELL_BOOK
        row["object_candidate_id"] = item["publication"]
        row["predicate"] = "cites"
        q["relation_candidate"] = True
        q["relation_candidate_note"] = "Haskell's bibliographic or archival citation; the cited material has not been independently consulted."
        q["citation_candidate_id"] = item["source_candidate"]
        q["citation_publication_candidate_id"] = item["publication"]
        q["citation_locator"] = item["locator"]
        q["citations"] = [{
            "source_candidate_id": item["source_candidate"],
            "publication_candidate_id": item["publication"],
            "locator": item["locator"],
        }]
        q["cited_material_not_independently_consulted"] = True

    output = ("\n".join(json.dumps(row, ensure_ascii=False) for row in after) + "\n").encode("utf-8")
    preview = [{"statement_id": sid, "subject": HASKELL_BOOK, "object": item["publication"],
                "predicate": "cites", "relation_candidate": True, "locator": item["locator"]}
               for sid, item in PLAN.items()]
    print(json.dumps({"mode": "APPLY PREFLIGHT" if args.apply else "DRY-RUN",
                      "updates": preview, "statements": len(after)}, ensure_ascii=False, indent=2))
    if not args.apply:
        return 0

    backup = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp4-p109-notes-20261011")
    if backup.exists():
        raise SystemExit(f"guard failed: recovery copy already exists: {backup.name}")
    backup.write_bytes(STATEMENTS.read_bytes())
    write_atomic(STATEMENTS, output)
    print(f"APPLIED {STATEMENTS.relative_to(ROOT)} sha256={digest(STATEMENTS)}")
    print(f"recovery copy {backup.relative_to(ROOT)} sha256={digest(backup)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
