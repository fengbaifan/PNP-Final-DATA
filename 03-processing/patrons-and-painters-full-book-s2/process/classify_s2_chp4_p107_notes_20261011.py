#!/usr/bin/env python3
"""Classify and atomize the p.107 footnotes after scan review.

Default mode is a guarded dry-run. --apply writes only book-statements.jsonl
and mentions.csv, with byte-for-byte recovery copies and atomic replacement.
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
PAGE_IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p107_body_notes_page_review_20261011.png"
SEGMENTS = TABLES / "segments.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
NOTES_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
PDF_SHA256 = "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303"
PAGE_IMAGE_SHA256 = "3467380e8ebfdcfa5fe7d6ac86d7f624461aa413ae024bf83e32d71031af6a78"
NOTES_SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
TABLE_SHA256 = {
    "book-statements.jsonl": "7f5485a6be1f77ad0b49bdeea7792c81aead0d095379fff55ed4750efbe51eb4",
    "mentions.csv": "056f1ec87a9271eaadf34bdf31cbed181455dafa8c6896f833d3a84dd1ff4020",
    "entity-candidates.csv": "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    "s2-coverage.csv": "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
BACKUP_SUFFIX = "bak-s2-chp4-p107-notes-20261011"

TARGETS = {
    "st-chp4-sec-ii-notes-l260-264-fn260-blunt",
    "st-chp4-sec-ii-notes-l260-264-fn261-pintard",
    "st-chp4-sec-ii-notes-l260-264-fn262-naudaeana",
    "st-chp4-sec-ii-notes-l260-264-fn263-haskell-interpretation",
    "st-chp4-sec-ii-notes-l260-264-fn263-peiresc-letter-report",
    "st-chp4-sec-ii-notes-l260-264-fn264-lumbroso",
}
NEW_IDS = {
    "st-chp4-sec-ii-p107-fn263-cites-peiresc-edition",
    "st-chp4-sec-ii-p107-fn263-cassiano-wished-to-own-work",
    "st-chp4-sec-ii-p107-fn263-haskell-thanks-pintard",
    "st-chp4-sec-ii-p107-fn264-lumbroso-quote",
}
NEW_MENTION_ID = "m-chp4-sec-ii-p107-fn263-haskell-first-person"


def sha256(path: Path) -> str:
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


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)).encode("utf-8")


def csv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    import io

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def merge_ids(*groups: list[str | None]) -> list[str]:
    return list(dict.fromkeys(value for group in groups for value in group if value))


def add_relation_flag(row: dict, value: bool, note: str, *, open_reason: str | None = None) -> None:
    q = row.setdefault("qualifiers", {})
    q["relation_candidate"] = value
    q["relation_candidate_note"] = note
    if open_reason:
        q["open_endpoint_reason"] = open_reason
    else:
        q.pop("open_endpoint_reason", None)


def citation_statement(
    *, statement_id: str, line: int, marker: int, publication_id: str,
    author_id: str | None, locator: str, claim: str, original_quote: str,
    mentioned: list[str],
) -> dict:
    citation = {"publication_candidate_id": publication_id, "locator": locator}
    if author_id:
        citation["source_candidate_id"] = author_id
    q = {
        "source_line_start": line,
        "source_line_end": line,
        "pdf_physical_page": 18,
        "printed_page_locator": "p.107",
        "footnote_marker": marker,
        "claim": claim,
        "speaker": "Haskell's footnote",
        "text_layer": "bibliographic citation to publication",
        "mentioned_candidate_ids": mentioned,
        "citation_publication_candidate_id": publication_id,
        "citation_locator": locator,
        "citations": [citation],
        "cited_material_not_independently_consulted": True,
        "qualification": "This records Haskell's citation only; the cited material was not independently consulted.",
        "relation_candidate": True,
        "relation_candidate_note": "The footnote explicitly cites this publication; citation is not independent verification of adjacent claims.",
    }
    if author_id:
        q["citation_candidate_id"] = author_id
    return {
        "statement_id": statement_id,
        "segment_id": NOTES_ID,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": publication_id,
        "predicate": "cites",
        "qualifiers": q,
        "original_quote": original_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after guarded preflight")
    args = parser.parse_args()

    for path, expected in ((SOURCE, SOURCE_SHA256), (PDF, PDF_SHA256), (PAGE_IMAGE, PAGE_IMAGE_SHA256)):
        if sha256(path) != expected:
            raise SystemExit(f"preflight failed: evidence asset changed: {path.relative_to(ROOT)}")
    table_paths = {name: TABLES / name for name in TABLE_SHA256}
    for name, expected in TABLE_SHA256.items():
        if sha256(table_paths[name]) != expected:
            raise SystemExit(f"preflight failed: table changed: {name}")

    segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
    segment = segments.get(NOTES_ID)
    if not segment or segment.get("sha256") != NOTES_SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("preflight failed: p.107 notes segment or source hash changed")
    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = {row["segment_id"]: row for row in csv.DictReader(handle)}
    if coverage.get(NOTES_ID, {}).get("disposition") != "reviewed" or coverage.get(NOTES_ID, {}).get("migration_status") != "complete":
        raise SystemExit("preflight failed: p.107 source segment coverage state changed")

    statements_path = table_paths["book-statements.jsonl"]
    statements = read_jsonl(statements_path)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements) or len(statements) != 13141:
        raise SystemExit("preflight failed: statement identifiers or table total changed")
    targets = {sid: by_id.get(sid) for sid in TARGETS}
    if any(row is None for row in targets.values()):
        raise SystemExit("preflight failed: a p.107 target statement is missing")
    if any("relation_candidate" in row.get("qualifiers", {}) for row in targets.values()):
        raise SystemExit("preflight failed: a p.107 target has already been classified")
    if any(sid in by_id for sid in NEW_IDS):
        raise SystemExit("preflight failed: a planned p.107 statement ID already exists")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    note_text = "\n".join(source_lines[259:264])
    for sid, row in targets.items():
        if row.get("segment_id") != NOTES_ID or row.get("original_quote") not in note_text:
            raise SystemExit(f"preflight failed: statement source anchor changed: {sid}")
    anchors = {
        "ambiguous": "Unfortunately, it is not clear whether the ‘paroles assez libertines’ are attributed to Bacon or to Cassiano.",
        "cassiano_work": "it is still interesting to note that Cassiano was so keen to own the work and prepared, therefore, to risk the displeasure of the papal customs and police in getting it.",
        "haskell_thanks": "I am most grateful to Professor Pintard for helping me to unravel the syntax and meaning of this quotation.",
        "lumbroso_quote": "tanto è poco il rispetto, che da questa sorte di gente aile chiese si porta.",
        "peiresc_locator": "III, p. 252",
    }
    if any(anchor not in note_text for anchor in anchors.values()):
        raise SystemExit("preflight failed: one or more reviewed p.107 source quotations changed")

    candidates = {}
    with table_paths["entity-candidates.csv"].open(encoding="utf-8-sig", newline="") as handle:
        candidates = {row["candidate_id"]: row for row in csv.DictReader(handle)}
    expected_types = {
        "cand-2962": "archive", "cand-0379": "person", "cand-5812": "archive",
        "cand-5789": "work", "cand-4547": "archive", "cand-5818": "person",
        "cand-5650": "archive", "cand-2036": "person", "cand-5813": "archive",
        "cand-1861": "person", "cand-5814": "archive", "cand-5815": "person",
        "cand-5816": "archive", "cand-5817": "archive", "cand-5626": "person",
        "cand-3770": "person",
    }
    for candidate_id, expected_type in expected_types.items():
        row = candidates.get(candidate_id)
        if not row or row.get("suggested_type") != expected_type:
            raise SystemExit(f"preflight failed: candidate endpoint changed: {candidate_id}")

    mentions_path = table_paths["mentions.csv"]
    with mentions_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        mention_fields = reader.fieldnames or []
        mentions = list(reader)
    if NEW_MENTION_ID in {row["mention_id"] for row in mentions}:
        raise SystemExit("preflight failed: planned first-person mention ID already exists")
    block = "\n".join(source_lines[231:308])
    first_person_at = block.find("I am most grateful")
    if first_person_at < 0 or block.find("Professor Pintard") != 6733:
        raise SystemExit("preflight failed: source-local first-person offsets changed")
    new_mention = {
        "mention_id": NEW_MENTION_ID,
        "segment_id": NOTES_ID,
        "candidate_id": "cand-3770",
        "surface_form": "I",
        "start_char": first_person_at,
        "end_char": first_person_at + 1,
        "note": "First-person authorial speaker Francis Haskell; reused the book-author candidate already present in the front matter.",
    }
    if not all(field in mention_fields for field in new_mention):
        raise SystemExit("preflight failed: mention table schema changed")

    # Normalize the three page references to Haskell-book -> cited publication.
    def normalize_citation(sid: str, publication_id: str, author_id: str | None,
                           locator: str, claim: str, mentioned: list[str], original_quote: str) -> None:
        row = by_id[sid]
        row["subject_candidate_id"] = "cand-2962"
        row["object_candidate_id"] = publication_id
        row["predicate"] = "cites"
        q = row["qualifiers"]
        q.update({
            "claim": claim,
            "speaker": "Haskell's footnote",
            "text_layer": "bibliographic citation to publication",
            "mentioned_candidate_ids": mentioned,
            "citation_publication_candidate_id": publication_id,
            "citation_locator": locator,
            "citations": [{"publication_candidate_id": publication_id, "locator": locator,
                           **({"source_candidate_id": author_id} if author_id else {})}],
            "cited_material_not_independently_consulted": True,
            "qualification": "This records Haskell's citation only; the cited material was not independently consulted.",
        })
        if author_id:
            q["citation_candidate_id"] = author_id
        else:
            q.pop("citation_candidate_id", None)
        row["original_quote"] = original_quote
        add_relation_flag(row, True,
                          "The footnote explicitly cites this publication; citation is not independent verification of adjacent claims.")

    normalize_citation(
        "st-chp4-sec-ii-notes-l260-264-fn260-blunt", "cand-5812", "cand-0379",
        "Anthony Blunt, 1967, pp. 177–207",
        "Haskell's book cites Anthony Blunt's 1967 discussion, pages 177–207, for the analysis of the Seven Sacraments.",
        ["cand-2962", "cand-0379", "cand-5812", "cand-5789"],
        "1 Blunt, 1967, pp. 177-207.",
    )
    normalize_citation(
        "st-chp4-sec-ii-notes-l260-264-fn261-pintard", "cand-4547", "cand-5818",
        "R. Pintard, chapter 2, ‘Les déniaisés d’Italie’",
        "Haskell directs readers to chapter 2, ‘Les déniaisés d’Italie’, in Pintard's book on the subject.",
        ["cand-2962", "cand-5818", "cand-4547", "cand-2036"],
        "2 See especially Chapter 2—‘Les “déniaisés” d’Italie’—in Pintard’s marvellous book on the subject.",
    )
    normalize_citation(
        "st-chp4-sec-ii-notes-l260-264-fn262-naudaeana", "cand-5650", None,
        "Naudaeana, p. 8",
        "Haskell's footnote cites page 8 of Naudaeana et Patiniana.",
        ["cand-2962", "cand-5650"],
        "3 Naudaeana, p. 8.",
    )

    # Keep the source's ambiguity and conditional gloss separate from the
    # inferred Cassiano-to-document relation recorded below.
    row = by_id["st-chp4-sec-ii-notes-l260-264-fn263-haskell-interpretation"]
    row["subject_candidate_id"] = "cand-2036"
    row["object_candidate_id"] = None
    row["predicate"] = "haskell_interprets_ambiguous_libertine_phrases"
    row["original_quote"] = anchors["ambiguous"]
    q = row["qualifiers"]
    q.update({
        "claim": "Haskell says the ‘paroles assez libertines’ cannot be confidently attributed to Bacon or Cassiano and offers only a broad, conditional gloss of ‘libertines’ as possibly meaning politically suspect.",
        "speaker": "Haskell",
        "text_layer": "authorial interpretation of a secondary quotation",
        "mentioned_candidate_ids": ["cand-2036", "cand-0155", "cand-5813"],
        "qualification": "The phrase's attribution remains expressly unresolved; this scalar interpretive statement is distinct from Haskell's separate inference that Cassiano sought to own the referenced work.",
    })
    add_relation_flag(row, False,
                      "This records uncertainty about the attribution and Haskell's conditional interpretation of a word; the distinct Cassiano-to-work inference is recorded separately.")

    # The letter's addressee is explicit; its contents remain mediated through Haskell.
    row = by_id["st-chp4-sec-ii-notes-l260-264-fn263-peiresc-letter-report"]
    q = row["qualifiers"]
    q.update({
        "claim": "Haskell quotes a letter from Peiresc to Monsieur de Saint-Saulveur dated 9 January 1635. The quoted passage concerns Cassiano dal Pozzo's memoranda for Bacon's works, a requested copy, and ‘paroles libertines’ in the text.",
        "speaker": "Peiresc as quoted by Haskell",
        "qualification": "The addressee is explicit in Haskell's secondary quotation. The original letter, edition, Bacon reference, and quoted wording have not been independently verified; the attribution of the libertine phrases remains unclear.",
        "mentioned_candidate_ids": ["cand-5813", "cand-1861", "cand-5815", "cand-5814", "cand-2036", "cand-5816", "cand-0155", "cand-5818"],
    })
    add_relation_flag(row, True,
                      "The letter is explicitly addressed to Monsieur de Saint-Saulveur; the quoted contents remain source-attributed and partly ambiguous.")

    # Split the distinct edition citation from the cited letter's addressee relation.
    edition_cite = citation_statement(
        statement_id="st-chp4-sec-ii-p107-fn263-cites-peiresc-edition",
        line=263, marker=4, publication_id="cand-5814", author_id="cand-1861",
        locator="Peiresc source, vol. III, p. 252",
        claim="Haskell cites the Peiresc source at volume III, page 252, for the 9 January 1635 letter.",
        original_quote=anchors["peiresc_locator"],
        mentioned=["cand-2962", "cand-1861", "cand-5814", "cand-5813"],
    )

    cassiano_work = {
        "statement_id": "st-chp4-sec-ii-p107-fn263-cassiano-wished-to-own-work",
        "segment_id": NOTES_ID,
        "subject_candidate_id": "cand-2036",
        "object_candidate_id": "cand-5816",
        "predicate": "wished_to_own",
        "qualifiers": {
            "source_line_start": 263, "source_line_end": 263,
            "pdf_physical_page": 18, "printed_page_locator": "p.107", "footnote_marker": 4,
            "claim": "Haskell infers from the letter that Cassiano was keen to own the referenced work and prepared to risk displeasing papal customs and police to obtain it.",
            "speaker": "Haskell",
            "text_layer": "authorial interpretation of a secondary quotation",
            "mentioned_candidate_ids": ["cand-2036", "cand-5816", "cand-2962"],
            "qualification": "This is Haskell's inference, not an independently established act or completed acquisition. The exact document and edition remain unresolved; the attribution of ‘paroles assez libertines’ to Bacon or Cassiano remains ambiguous.",
            "relation_candidate": True,
            "relation_candidate_note": "The sentence explicitly relates Cassiano's interpreted wish to possess the referenced memoranda/work; keep it as an attributed S2 candidate, not a formal relation.",
        },
        "original_quote": anchors["cassiano_work"],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }

    haskell_thanks = {
        "statement_id": "st-chp4-sec-ii-p107-fn263-haskell-thanks-pintard",
        "segment_id": NOTES_ID,
        "subject_candidate_id": "cand-3770",
        "object_candidate_id": "cand-5818",
        "predicate": "acknowledged_assistance_from",
        "qualifiers": {
            "source_line_start": 263, "source_line_end": 263,
            "pdf_physical_page": 18, "printed_page_locator": "p.107", "footnote_marker": 4,
            "claim": "Francis Haskell thanks Professor Pintard for helping him interpret the syntax and meaning of the quoted passage.",
            "speaker": "Haskell",
            "text_layer": "authorial acknowledgement",
            "mentioned_candidate_ids": ["cand-3770", "cand-5818"],
            "qualification": "This records the author's explicit acknowledgement of interpretive assistance; it does not infer co-authorship or a broader personal relationship.",
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly records Pintard's assistance to Haskell in interpreting the quotation; preserve the narrow scope of that assistance.",
        },
        "original_quote": anchors["haskell_thanks"],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }

    # The final footnote contains a citation and a separate attributed judgement.
    normalize_citation(
        "st-chp4-sec-ii-notes-l260-264-fn264-lumbroso", "cand-5817", "cand-5626",
        "G. Lumbroso, p. 207",
        "Haskell's footnote cites G. Lumbroso, page 207.",
        ["cand-2962", "cand-5626", "cand-5817"],
        "5 Lumbroso, p. 207.",
    )
    by_id["st-chp4-sec-ii-notes-l260-264-fn264-lumbroso"]["qualifiers"].pop("ocr_corrections", None)
    lumbroso_quote = {
        "statement_id": "st-chp4-sec-ii-p107-fn264-lumbroso-quote",
        "segment_id": NOTES_ID,
        "subject_candidate_id": None,
        "object_candidate_id": None,
        "predicate": "shows_little_respect_for_churches",
        "qualifiers": {
            "source_line_start": 264, "source_line_end": 264,
            "pdf_physical_page": 18, "printed_page_locator": "p.107", "footnote_marker": 5,
            "claim": "Haskell quotes Lumbroso as saying that ‘this sort of people’ show little respect for churches.",
            "speaker": "G. Lumbroso as quoted by Haskell",
            "text_layer": "secondary quotation in a bibliographic note",
            "mentioned_candidate_ids": ["cand-5626", "cand-5817"],
            "qualification": "The quoted judgement is mediated through Haskell. ‘This sort of people’ is not safely identified with the nearby French libertins or Bouchard, and the churches are generic; neither endpoint is assigned.",
            "relation_candidate": True,
            "relation_candidate_note": "The quotation expresses a people-to-churches relation, but both referents remain generic and open.",
            "open_endpoint_reason": "The referent of ‘questa sorte di gente’ and the churches are not identified in this note; no nearby group or religious-order church candidate is substituted.",
            "ocr_corrections": [{"source_line": 264, "source_form": "aile chiese", "print_form": "alle chiese"}],
        },
        "original_quote": anchors["lumbroso_quote"],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }

    additions = [edition_cite, cassiano_work, haskell_thanks, lumbroso_quote]
    statements_out = statements + additions
    mentions_out = mentions + [new_mention]

    # Confirm every planned row remains a source-grounded S2 statement.
    for row in additions:
        if row["original_quote"] not in note_text or row["segment_id"] != NOTES_ID:
            raise SystemExit(f"preflight failed: new statement anchor is not in p.107 source: {row['statement_id']}")
    if len({row["statement_id"] for row in statements_out}) != len(statements_out):
        raise SystemExit("preflight failed: output statement IDs are not unique")
    if len({row["mention_id"] for row in mentions_out}) != len(mentions_out):
        raise SystemExit("preflight failed: output mention IDs are not unique")

    counts = {"statements": len(statements_out), "mentions": len(mentions_out),
              "p107_statement_rows": sum(1 for row in statements_out
                  if row.get("segment_id") == NOTES_ID and row.get("qualifiers", {}).get("printed_page_locator") == "p.107"
                  and row.get("qualifiers", {}).get("source_line_start") in range(260, 265))}
    print("DRY-RUN" if not args.apply else "APPLY PREFLIGHT PASSED")
    print(json.dumps({"targets": sorted(TARGETS), "new_statements": [
        {"statement_id": row["statement_id"], "subject": row["subject_candidate_id"],
         "object": row["object_candidate_id"], "predicate": row["predicate"],
         "relation_candidate": row["qualifiers"].get("relation_candidate"),
         "claim": row["qualifiers"].get("claim")} for row in additions],
        "new_mention": new_mention, "output_counts": counts}, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = {path: path.with_name(path.name + "." + BACKUP_SUFFIX) for path in (statements_path, mentions_path)}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("apply refused: a recovery copy with this suffix already exists")
    payloads = {statements_path: jsonl_bytes(statements_out), mentions_path: csv_bytes(mention_fields, mentions_out)}
    for path, backup in backups.items():
        shutil.copyfile(path, backup)
    try:
        for path, payload in payloads.items():
            atomic_write(path, payload)
    except Exception:
        for path, backup in backups.items():
            atomic_write(path, backup.read_bytes())
        raise
    print("APPLIED")
    for path in payloads:
        print(f"{path.relative_to(ROOT)} sha256={sha256(path)}")
    print(f"recovery copies: {', '.join(p.relative_to(ROOT).as_posix() for p in backups.values())}")


if __name__ == "__main__":
    main()
