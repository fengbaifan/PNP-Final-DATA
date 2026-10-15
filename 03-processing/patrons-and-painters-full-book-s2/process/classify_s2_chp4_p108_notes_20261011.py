#!/usr/bin/env python3
"""Classify the p.108 footnote statements after checking the printed page.

Default mode is a hash-guarded dry-run. --apply changes only book-statements.jsonl.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-4.pdf"
PAGE_IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p108_body_notes_page_review_20261011.png"
NOTES_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
PDF_SHA256 = "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303"
PAGE_IMAGE_SHA256 = "46466b40804e8cf1940e15380f1842cf69c05b9dd8e80845142d1415267f365b"
NOTES_SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
TABLE_SHA256 = {
    "book-statements.jsonl": "145a3565682666a327bccf34a44b7606bea1faaf82af4196f542c6f5250d662d",
    "mentions.csv": "0251842ac93313725448baf44c7878ef71f74f5dfd31cdad8df19a5f84e3dca9",
    "entity-candidates.csv": "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    "s2-coverage.csv": "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
BACKUP_SUFFIX = "bak-s2-chp4-p108-notes-20261011"

TARGETS = {
    "st-chp4-sec-ii-notes-l265-268-fn265-dupuy-report",
    "st-chp4-sec-ii-notes-l265-268-fn265-haskell-inference",
    "st-chp4-sec-ii-notes-l265-268-fn265-manuscript-books",
    "st-chp4-sec-ii-notes-l265-268-fn265-private-transfer-inference",
    "st-chp4-sec-ii-notes-l265-268-fn265-publication",
    "st-chp4-sec-ii-notes-l265-268-fn265-will-cassiano-legacies",
    "st-chp4-sec-ii-notes-l265-268-fn266-pintard-citation",
    "st-chp4-sec-ii-notes-l265-268-fn267-galilei-citation",
    "st-chp4-sec-ii-notes-l265-268-fn268-dati-citation",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def atomic_write(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def merge_ids(*groups: list[str | None]) -> list[str]:
    return list(dict.fromkeys(value for group in groups for value in group if value))


def mark(row: dict, note: str) -> None:
    q = row.setdefault("qualifiers", {})
    q["relation_candidate"] = True
    q["relation_candidate_note"] = note
    q.pop("open_endpoint_reason", None)


def set_citation(row: dict, publication: str, author: str, locator: str,
                 claim: str, mentioned: list[str]) -> None:
    row["subject_candidate_id"] = "cand-2962"
    row["object_candidate_id"] = publication
    row["predicate"] = "cites"
    q = row["qualifiers"]
    q.update({
        "claim": claim,
        "speaker": "Haskell's footnote",
        "text_layer": "bibliographic citation to publication",
        "mentioned_candidate_ids": mentioned,
        "citation_candidate_id": author,
        "citation_publication_candidate_id": publication,
        "citation_locator": locator,
        "citations": [{"source_candidate_id": author,
                       "publication_candidate_id": publication,
                       "locator": locator}],
        "cited_material_not_independently_consulted": True,
        "qualification": "This records Haskell's citation only; the cited material was not independently consulted.",
    })
    mark(row, "The footnote explicitly cites this source; citation is not independent verification of adjacent claims.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after guarded preflight")
    args = parser.parse_args()

    for path, expected in ((SOURCE, SOURCE_SHA256), (PDF, PDF_SHA256), (PAGE_IMAGE, PAGE_IMAGE_SHA256)):
        if sha(path) != expected:
            raise SystemExit(f"preflight failed: evidence asset changed: {path.relative_to(ROOT)}")
    paths = {name: TABLES / name for name in TABLE_SHA256}
    for name, expected in TABLE_SHA256.items():
        if sha(paths[name]) != expected:
            raise SystemExit(f"preflight failed: table changed: {name}")

    segments = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    segment = segments.get(NOTES_ID)
    if not segment or segment.get("sha256") != NOTES_SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("preflight failed: p.108 notes segment or source hash changed")
    with paths["s2-coverage.csv"].open(encoding="utf-8-sig", newline="") as handle:
        coverage = {row["segment_id"]: row for row in csv.DictReader(handle)}
    state = coverage.get(NOTES_ID, {})
    if state.get("disposition") != "reviewed" or state.get("migration_status") != "complete":
        raise SystemExit("preflight failed: source coverage state changed")

    statement_path = paths["book-statements.jsonl"]
    statements = read_jsonl(statement_path)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements) or len(statements) != 13145:
        raise SystemExit("preflight failed: statement IDs or table total changed")
    targets = {sid: by_id.get(sid) for sid in TARGETS}
    if any(row is None for row in targets.values()):
        raise SystemExit("preflight failed: p.108 target statement missing")
    if any("relation_candidate" in row.get("qualifiers", {}) for row in targets.values()):
        raise SystemExit("preflight failed: p.108 target already classified")
    if any(row.get("segment_id") != NOTES_ID for row in targets.values()):
        raise SystemExit("preflight failed: p.108 statement segment changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    notes_text = "\n".join(source_lines[264:268])
    for sid, row in targets.items():
        q = row.get("qualifiers") or {}
        if q.get("source_line_start") not in range(265, 269) or row.get("original_quote") not in notes_text:
            raise SystemExit(f"preflight failed: statement source anchor changed: {sid}")

    expected_types = {
        "cand-2962": "archive", "cand-0419": "person", "cand-0951": "person",
        "cand-2036": "person", "cand-0199": "person", "cand-5811": "archive",
        "cand-5832": "archive", "cand-5833": "person", "cand-5834": "archive",
        "cand-4547": "archive", "cand-5818": "person", "cand-5835": "archive",
        "cand-1105": "person", "cand-0905": "person", "cand-5657": "archive",
        "cand-5827": "archive", "cand-5828": "work",
    }
    with paths["entity-candidates.csv"].open(encoding="utf-8-sig", newline="") as handle:
        candidates = {row["candidate_id"]: row for row in csv.DictReader(handle)}
    for candidate_id, expected in expected_types.items():
        candidate = candidates.get(candidate_id)
        if not candidate or candidate.get("suggested_type") != expected:
            raise SystemExit(f"preflight failed: candidate endpoint changed: {candidate_id}")

    # Keep the three distinct reports about Bouchard's writings and estate apart.
    row = by_id["st-chp4-sec-ii-notes-l265-268-fn265-dupuy-report"]
    row["subject_candidate_id"], row["object_candidate_id"] = "cand-0419", "cand-2036"
    row["predicate"] = "reported_left_writings_to"
    row["qualifiers"].update({
        "claim": "Haskell reports, through Pintard, Christophe Dupuy's statement that Jean-Jacques Bouchard left all his writings to Cassiano.",
        "mentioned_candidate_ids": ["cand-0419", "cand-2036", "cand-0951", "cand-4547"],
        "qualification": "This is Dupuy's statement as quoted by Pintard and reported by Haskell; it differs in scope from Haskell's account of the will and is not independently checked.",
    })
    mark(row, "The reported statement explicitly links Bouchard's writings to Cassiano; retain the Dupuy-through-Pintard attribution.")

    row = by_id["st-chp4-sec-ii-notes-l265-268-fn265-haskell-inference"]
    row["qualifiers"].update({
        "claim": "Haskell infers that Bouchard must have excepted the dangerous private papers from the bequest and argues that he could not have intended them to be read by an unlikely sympathizer.",
        "qualification": "This is Haskell's inference and value judgment, not wording from the will; the papers' identity and intended reader remain unresolved.",
    })
    mark(row, "Haskell makes a source-attributed claim about Bouchard's treatment of the dangerous papers; do not promote the inferred exception or intended audience to verified fact.")

    row = by_id["st-chp4-sec-ii-notes-l265-268-fn265-manuscript-books"]
    row["qualifiers"]["qualification"] = "Haskell reports the testamentary wording; the will has not been independently consulted."
    mark(row, "The report explicitly names Bouchard's manuscript books and Cardinal Francesco Barberini as bequest endpoints.")

    row = by_id["st-chp4-sec-ii-notes-l265-268-fn265-private-transfer-inference"]
    row["subject_candidate_id"], row["object_candidate_id"] = "cand-0419", "cand-2036"
    row["predicate"] = "may_have_transferred_private_papers_to"
    row["qualifiers"].update({
        "claim": "Haskell suggests that Bouchard may have given his private papers to Cassiano before his death, which Haskell says would be still more compromising.",
        "mentioned_candidate_ids": ["cand-0419", "cand-2036", "cand-5811"],
        "qualification": "Explicitly presented as Haskell's suggestion, not a documented transfer. The papers are represented by the open archive candidate cand-5811.",
    })
    mark(row, "This is an explicit but tentative Bouchard-to-Cassiano transfer claim; preserve Haskell's ‘may’ and retain the papers as context.")

    row = by_id["st-chp4-sec-ii-notes-l265-268-fn265-publication"]
    row["subject_candidate_id"], row["object_candidate_id"] = "cand-5832", "cand-5833"
    row["predicate"] = "will_published_by"
    row["qualifiers"].update({
        "claim": "Haskell reports that Bouchard's will was published by P. Tamizey de Laroque in 1886.",
        "mentioned_candidate_ids": ["cand-5832", "cand-5833", "cand-5834", "cand-0419"],
        "qualification": "The will and publisher are reported by Haskell. The bibliography offers a possible 1886 article match (cand-5834), but the mapping and publication have not been independently checked.",
    })
    mark(row, "The source reports a will publication relationship; the possible article match remains a candidate, not a settled identity.")

    row = by_id["st-chp4-sec-ii-notes-l265-268-fn265-will-cassiano-legacies"]
    row["qualifiers"]["qualification"] = "This is Haskell's report of the will's listed legacies; the testament has not been independently consulted. The list does not include the private papers in this account."
    mark(row, "The reported will explicitly describes legacies from Bouchard to Cassiano; preserve the distinction between listed legacies and the hypothesized private-paper transfer.")

    set_citation(
        by_id["st-chp4-sec-ii-notes-l265-268-fn266-pintard-citation"],
        "cand-4547", "cand-5818", "R. Pintard, p. 238",
        "Haskell cites Pintard, page 238, for the preceding report attributed to Dupuy.",
        ["cand-2962", "cand-5818", "cand-4547", "cand-0951", "cand-2036"],
    )
    set_citation(
        by_id["st-chp4-sec-ii-notes-l265-268-fn267-galilei-citation"],
        "cand-5835", "cand-1105", "Galilei, volume XVIII, pages 290 and 296",
        "Haskell cites Galileo's collected works, volume XVIII, pages 290 and 296, for the preceding letter and portrait account.",
        ["cand-2962", "cand-1105", "cand-5835", "cand-5827", "cand-5828", "cand-2036"],
    )
    set_citation(
        by_id["st-chp4-sec-ii-notes-l265-268-fn268-dati-citation"],
        "cand-5657", "cand-0905", "Carlo Dati (title and page not stated)",
        "Haskell identifies Carlo Dati's writing on Cassiano's religious orthodoxy and alchemy as a source for the preceding discussion.",
        ["cand-2962", "cand-0905", "cand-5657", "cand-2036"],
    )

    print("DRY-RUN" if not args.apply else "APPLY PREFLIGHT PASSED")
    print(json.dumps({"classified": [{
        "statement_id": sid,
        "subject": by_id[sid].get("subject_candidate_id"),
        "object": by_id[sid].get("object_candidate_id"),
        "predicate": by_id[sid].get("predicate"),
        "relation_candidate": by_id[sid].get("qualifiers", {}).get("relation_candidate"),
        "claim": by_id[sid].get("qualifiers", {}).get("claim"),
    } for sid in sorted(TARGETS)], "statements": len(statements)}, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backup = statement_path.with_name(statement_path.name + "." + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit("apply refused: recovery copy with this suffix already exists")
    backup.write_bytes(statement_path.read_bytes())
    payload = ("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in statements)).encode("utf-8")
    atomic_write(statement_path, payload)
    print("APPLIED", statement_path.relative_to(ROOT), "sha256=" + sha(statement_path))
    print("recovery copy", backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
