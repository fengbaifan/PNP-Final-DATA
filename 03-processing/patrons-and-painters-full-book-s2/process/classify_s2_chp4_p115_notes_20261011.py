from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
PDF = ROOT / "02-sources/01-book/CHP-4.pdf"
PDF_SHA256 = "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303"
PAGE_IMAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p115_page_review_20261011.png"
PAGE_IMAGE_SHA256 = "cdf4944885bf3a1b8daab11777bef1adecbf25ec5dd2243c84a51570773b1c7b"
TABLES = {
    "statements": ROOT / "04-knowledge/tables/book-statements.jsonl",
    "candidates": ROOT / "04-knowledge/tables/entity-candidates.csv",
    "mentions": ROOT / "04-knowledge/tables/mentions.csv",
    "coverage": ROOT / "04-knowledge/tables/s2-coverage.csv",
}
EXPECTED_SHA256 = {
    "statements": "5846cabeb8f3eaa49ee923b5060aba54781b47cb794d60f2a676621660c284ea",
    "candidates": "adc8b7ddf5c576bd2749b977033db51f322d5fe18c785e392acc0658ebc22413",
    "mentions": "006171b24887e0e6534a66499eab4f745f4b91d81310ed0c92927d456577c26c",
    "coverage": "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
BACKUP_SUFFIX = ".bak-s2-chp4-p115-notes-20261011"
ORIGINAL_STATEMENTS = {
    "st-chp4-sec-ii-p115-fn2-inventory": (
        "cand-5959",
        "inventory_partly_published_by_orbaan",
        "cand-4373",
    ),
    "st-chp4-sec-ii-p115-fn2-moroni-correction": (
        "cand-5954",
        "misidentified_as_life_of_massimi_by_moroni",
        "cand-5956",
    ),
    "st-chp4-sec-ii-p115-fn2-patrignani": (
        "cand-1564",
        "footnote_points_to_other_massimi_references",
        "cand-5958",
    ),
    "st-chp4-sec-ii-p115-fn2-sources": (
        "cand-1564",
        "footnote_cites_massimi_references",
        None,
    ),
    "st-chp4-sec-ii-p115-fn3-blunt": (
        "cand-1564",
        "contact_with_poussin_before_1640_reported_by_blunt",
        "cand-1984",
    ),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    return raw, bom, text, list(csv.DictReader(io.StringIO(text, newline="")))


def emit_csv(headers, rows, bom: bool, original_text: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=headers,
        lineterminator="\r\n" if "\r\n" in original_text else "\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(rows)
    raw = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + raw


def new_statement(
    statement_id: str,
    subject: str | None,
    predicate: str,
    object_: str | None,
    *,
    line: int,
    marker: int,
    claim: str,
    quote: str,
    mentioned: list[str],
    qualification: str,
    extra: dict | None = None,
) -> dict:
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "pdf_physical_page": 26,
        "printed_page_locator": "p.115 footnote",
        "claim": claim,
        "speaker": "Haskell’s footnote",
        "text_layer": "bibliographic citation" if predicate == "cites" else "reported historical claim",
        "footnote_marker": marker,
        "mentioned_candidate_ids": mentioned,
        "qualification": qualification,
        "relation_candidate": True,
        "relation_candidate_note": (
            "S2 source-attributed candidate only; citation or claim is not an independent verification and no formal S6 edge is created."
        ),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }


def prepare():
    for path, expected in (
        (SOURCE, SOURCE_SHA256),
        (PDF, PDF_SHA256),
        (PAGE_IMAGE, PAGE_IMAGE_SHA256),
    ):
        actual = digest(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"STOP: source evidence changed: {path.name} {actual}")
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment = "\n".join(lines[231:308])
    if digest(segment.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("STOP: canonical source segment hash changed")
    note2, note3 = lines[292], lines[293]
    for required in (
        "For Camillo Massimi see Litta, Moroni and the Abbate Michele Giustiniani, III, p. 319.",
        "Moroni is mistaken in his reference to a life of Massimi by Luca Bartolotti published at Asti in 1677.",
        "a biography of Cardinal Bona dedicated to Massimi",
        "The inventory of Massimi’s collections was published in part by Orbaan, 1920, pp. 515-22.",
    ):
        if required not in note2:
            raise SystemExit(f"STOP: expected p.115 footnote 2 text missing: {required}")
    if "Blunt, 1945, p. 32" not in note3 or "ibid., p. 45" not in note3 or "before 1640" not in note3:
        raise SystemExit("STOP: expected p.115 footnote 3 text missing")
    if segment[10598:10605] != "Massimi":
        raise SystemExit("STOP: planned second Massimi mention span changed")

    raw = {name: path.read_bytes() for name, path in TABLES.items()}
    for name, data in raw.items():
        if digest(data) != EXPECTED_SHA256[name]:
            raise SystemExit(f"STOP: {name} table SHA changed: {digest(data)}")

    statements = [json.loads(row) for row in raw["statements"].decode("utf-8").splitlines()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise SystemExit("STOP: duplicate statement IDs")
    for statement_id, expected in ORIGINAL_STATEMENTS.items():
        row = statement_by_id.get(statement_id)
        if row is None:
            raise SystemExit(f"STOP: missing source statement {statement_id}")
        actual = (
            row.get("subject_candidate_id"),
            row.get("predicate"),
            row.get("object_candidate_id"),
        )
        if actual != expected or "relation_candidate" in row.get("qualifiers", {}):
            raise SystemExit(f"STOP: original statement no longer matches expected pre-review state: {statement_id} {actual}")
        if row.get("segment_id") != SEGMENT_ID:
            raise SystemExit(f"STOP: wrong source segment on {statement_id}")

    _, _, _, candidates = read_csv(TABLES["candidates"])
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(candidate_by_id) != len(candidates):
        raise SystemExit("STOP: duplicate candidate IDs")
    required_types = {
        "cand-2962": "archive",
        "cand-1564": "person",
        "cand-5959": "archive",
        "cand-4373": "archive",
        "cand-5954": "person",
        "cand-5955": "archive",
        "cand-5956": "archive",
        "cand-5951": "person",
        "cand-5952": "person",
        "cand-5953": "place",
        "cand-4842": "archive",
        "cand-5504": "archive",
        "cand-5957": "person",
        "cand-5958": "archive",
        "cand-1199": "person",
        "cand-5949": "work",
        "cand-0379": "person",
        "cand-4635": "archive",
        "cand-1984": "person",
    }
    for candidate_id, kind in required_types.items():
        if candidate_id not in candidate_by_id or candidate_by_id[candidate_id]["suggested_type"] != kind:
            raise SystemExit(f"STOP: candidate type mismatch: {candidate_id}")

    _, _, _, mentions = read_csv(TABLES["mentions"])
    mention_by_id = {row["mention_id"]: row for row in mentions}
    p115_mentions = [
        row for row in mentions
        if row["segment_id"] == SEGMENT_ID and row["mention_id"].startswith("m-chp4-sec-ii-p115note-")
    ]
    if len(p115_mentions) != 21:
        raise SystemExit(f"STOP: expected 21 existing p.115 footnote mentions, got {len(p115_mentions)}")
    for row in p115_mentions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment[start:end] != row["surface_form"]:
            raise SystemExit(f"STOP: mention span mismatch: {row['mention_id']}")

    new_ids = {
        "st-chp4-sec-ii-p115-fn2-sources-moroni",
        "st-chp4-sec-ii-p115-fn2-sources-giustiniani",
        "st-chp4-sec-ii-p115-fn2-inventory-cites-orbaan",
        "st-chp4-sec-ii-p115-fn2-moroni-bona-biography",
        "st-chp4-sec-ii-p115-fn2-moroni-book-dedication",
        "st-chp4-sec-ii-p115-fn3-cites-blunt",
    }
    if new_ids & statement_by_id.keys():
        raise SystemExit("STOP: planned statement ID already exists")
    mention_id = "m-chp4-sec-ii-p115note-0072"
    if mention_id in mention_by_id:
        raise SystemExit("STOP: planned mention ID already exists")

    for row in statements:
        sid = row["statement_id"]
        if sid == "st-chp4-sec-ii-p115-fn2-inventory":
            row["predicate"] = "partly_published_in"
            row["qualifiers"].update(
                {
                    "claim": "Haskell says part of the inventory of Massimi’s collections was published in Orbaan’s 1920 book, pp. 515-22.",
                    "text_layer": "reported publication history",
                    "mentioned_candidate_ids": ["cand-5959", "cand-1564", "cand-4373"],
                    "relation_candidate": True,
                    "relation_candidate_note": "Explicitly reported publication history; the archive and cited book were not independently examined, and no formal S6 edge is created.",
                    "citation_statement_id": "st-chp4-sec-ii-p115-fn2-inventory-cites-orbaan",
                    "citation_locator": "Orbaan, 1920, pp. 515-22",
                }
            )
        elif sid == "st-chp4-sec-ii-p115-fn2-moroni-correction":
            row["subject_candidate_id"] = "cand-5956"
            row["object_candidate_id"] = "cand-5954"
            row["predicate"] = "misidentified_as_life_of_massimi_by"
            row["qualifiers"].update(
                {
                    "claim": "Haskell says Moroni mistakenly referred to the same book as a life of Massimi by Luca Bartolotti, published at Asti in 1677.",
                    "text_layer": "reported bibliographic correction",
                    "mentioned_candidate_ids": ["cand-5954", "cand-5955", "cand-5956", "cand-5951", "cand-5953", "cand-1564"],
                    "moroni_publication_candidate_id": "cand-5955",
                    "misidentified_book_candidate_id": "cand-5956",
                    "relation_candidate": True,
                    "relation_candidate_note": "This preserves the mistaken description attributed to Moroni; it is not asserted as the book’s actual title or subject.",
                    "qualification": "Haskell explicitly says Moroni is mistaken; the same book is identified in the following source-limited claims as a Bona biography dedicated to Massimi.",
                }
            )
        elif sid == "st-chp4-sec-ii-p115-fn2-patrignani":
            row["subject_candidate_id"] = "cand-2962"
            row["predicate"] = "cites"
            row["qualifiers"].update(
                {
                    "claim": "Haskell’s book points to Patrignani’s 1948 article for further references concerning Massimi.",
                    "text_layer": "bibliographic citation",
                    "mentioned_candidate_ids": ["cand-1564", "cand-5957", "cand-5958"],
                    "citation_author_candidate_ids": ["cand-5957"],
                    "citation_publication_candidate_id": "cand-5958",
                    "citation_locator": "Patrignani, 1948",
                    "cited_material_not_independently_consulted": True,
                    "relation_candidate": True,
                    "relation_candidate_note": "Bibliographic pointer only; the article was not independently consulted, and no formal S6 edge is created.",
                }
            )
        elif sid == "st-chp4-sec-ii-p115-fn2-sources":
            row["subject_candidate_id"] = "cand-2962"
            row["object_candidate_id"] = "cand-4842"
            row["predicate"] = "cites"
            row["qualifiers"].update(
                {
                    "claim": "Haskell’s book cites the existing Litta publication candidate in the note directing readers to sources on Camillo Massimi.",
                    "text_layer": "bibliographic citation",
                    "mentioned_candidate_ids": ["cand-1564", "cand-4842"],
                    "citation_publication_candidate_id": "cand-4842",
                    "citation_locator": "Litta (title and page not supplied in this footnote)",
                    "cited_material_not_independently_consulted": True,
                    "relation_candidate": True,
                    "relation_candidate_note": "The footnote gives only the surname; this uses the existing Famiglie celebri italiane candidate provisionally. No formal S6 edge is created.",
                    "qualification": "The note supplies no title or page for Litta; exact publication-to-citation mapping remains provisional.",
                }
            )
        elif sid == "st-chp4-sec-ii-p115-fn3-blunt":
            row["qualifiers"].update(
                {
                    "claim": "Haskell attributes to Blunt the inference that Massimi must have been in contact with Poussin before 1640.",
                    "text_layer": "reported historical claim",
                    "mentioned_candidate_ids": ["cand-5949", "cand-0379", "cand-4635", "cand-1564", "cand-1984"],
                    "reporting_author_candidate_id": "cand-0379",
                    "source_publication_candidate_id": "cand-4635",
                    "source_locator": "Blunt, 1945, p. 45",
                    "citation_statement_id": "st-chp4-sec-ii-p115-fn3-cites-blunt",
                    "relation_candidate": True,
                    "relation_candidate_note": "Second-hand attribution; ‘must have been’ remains an inference reported by Haskell, not an independently verified contact.",
                    "qualification": "Neither Blunt passage was independently checked; the identity/title of the cited 1945 publication remains as recorded in its open candidate.",
                }
            )

    quote2, quote3 = note2, note3
    cite_note = "Bibliographic pointer only; the cited material was not independently consulted and no formal S6 edge is created."
    additions = [
        new_statement(
            "st-chp4-sec-ii-p115-fn2-sources-moroni",
            "cand-2962",
            "cites",
            "cand-5955",
            line=293,
            marker=2,
            claim="Haskell’s book cites an unidentified Moroni publication concerning Camillo Massimi.",
            quote=quote2,
            mentioned=["cand-1564", "cand-5954", "cand-5955"],
            qualification="The footnote gives surname only; the publication title and edition remain unresolved.",
            extra={
                "citation_author_candidate_ids": ["cand-5954"],
                "citation_publication_candidate_id": "cand-5955",
                "citation_locator": "Moroni (title and edition unspecified)",
                "cited_material_not_independently_consulted": True,
            },
        ),
        new_statement(
            "st-chp4-sec-ii-p115-fn2-sources-giustiniani",
            "cand-2962",
            "cites",
            "cand-5504",
            line=293,
            marker=2,
            claim="Haskell’s book cites Abbate Michele Giustiniani, volume III, p. 319, concerning Camillo Massimi.",
            quote=quote2,
            mentioned=["cand-1564", "cand-1199", "cand-5504"],
            qualification="The volume is identified, but its full title and edition remain unresolved; it was not independently consulted.",
            extra={
                "citation_author_candidate_ids": ["cand-1199"],
                "citation_publication_candidate_id": "cand-5504",
                "citation_locator": "Abbate Michele Giustiniani, III, p. 319",
                "cited_material_not_independently_consulted": True,
            },
        ),
        new_statement(
            "st-chp4-sec-ii-p115-fn2-inventory-cites-orbaan",
            "cand-2962",
            "cites",
            "cand-4373",
            line=293,
            marker=2,
            claim="Haskell’s book cites Orbaan, 1920, pp. 515-22, for the partial publication of Massimi’s collection inventory.",
            quote=quote2,
            mentioned=["cand-5959", "cand-1564", "cand-4373"],
            qualification=cite_note,
            extra={
                "citation_publication_candidate_id": "cand-4373",
                "citation_locator": "Orbaan, 1920, pp. 515-22",
                "cited_material_not_independently_consulted": True,
            },
        ),
        new_statement(
            "st-chp4-sec-ii-p115-fn2-moroni-bona-biography",
            "cand-5956",
            "biography_of",
            "cand-5952",
            line=293,
            marker=2,
            claim="Haskell identifies the same Bartolotti book as a biography of Cardinal Bona.",
            quote=quote2,
            mentioned=["cand-5956", "cand-5952", "cand-5951", "cand-5954"],
            qualification="Haskell’s bibliographic correction; the book and edition were not independently examined.",
            extra={"same_book_as_moroni_reference": True},
        ),
        new_statement(
            "st-chp4-sec-ii-p115-fn2-moroni-book-dedication",
            "cand-5956",
            "dedicated_to",
            "cand-1564",
            line=293,
            marker=2,
            claim="Haskell says the biography of Cardinal Bona is dedicated to Massimi.",
            quote=quote2,
            mentioned=["cand-5956", "cand-5952", "cand-1564"],
            qualification="Reported by Haskell in his correction of Moroni; dedication was not independently checked.",
            extra={"same_book_as_moroni_reference": True},
        ),
        new_statement(
            "st-chp4-sec-ii-p115-fn3-cites-blunt",
            "cand-2962",
            "cites",
            "cand-4635",
            line=294,
            marker=3,
            claim="Haskell’s book cites Blunt’s 1945 publication at pp. 32 and 45.",
            quote=quote3,
            mentioned=["cand-5949", "cand-0379", "cand-4635", "cand-1564", "cand-1984"],
            qualification="Page locators only; the cited publication was not independently consulted.",
            extra={
                "citation_author_candidate_ids": ["cand-0379"],
                "citation_publication_candidate_id": "cand-4635",
                "citation_locator": "Blunt, 1945, pp. 32, 45",
                "cited_material_not_independently_consulted": True,
                "ocr_corrections": [
                    {"source_line": 294, "source_form": "sec Blunt", "print_form": "see Blunt"}
                ],
            },
        ),
    ]
    statements.extend(additions)

    mention_raw, mention_bom, mention_text, mentions = read_csv(TABLES["mentions"])
    mentions.append(
        {
            "mention_id": "m-chp4-sec-ii-p115note-0072",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-1564",
            "surface_form": "Massimi",
            "start_char": "10598",
            "end_char": "10605",
            "note": "The named dedicatee of the biography in Haskell’s reported correction.",
        }
    )
    candidate_ids = {row["candidate_id"] for row in candidates}
    for row in statements:
        if row["statement_id"].startswith("st-chp4-sec-ii-p115-fn"):
            for candidate_id in row["qualifiers"].get("mentioned_candidate_ids", []):
                if candidate_id not in candidate_ids:
                    raise SystemExit(f"STOP: dangling candidate {candidate_id} in {row['statement_id']}")
            for field in ("subject_candidate_id", "object_candidate_id"):
                candidate_id = row.get(field)
                if candidate_id and candidate_id not in candidate_ids:
                    raise SystemExit(f"STOP: dangling {field} in {row['statement_id']}")
    if segment[10598:10605] != "Massimi":
        raise SystemExit("STOP: new mention does not match source")

    # Preserve the existing JSONL and CSV schemas/serialization while adding only rows.
    statement_bytes = "\n".join(json.dumps(row, ensure_ascii=False) for row in statements).encode("utf-8") + b"\n"
    mention_bytes = emit_csv(list(mentions[0]), mentions, mention_bom, mention_text)
    return statements, mentions, {"statements": statement_bytes, "mentions": mention_bytes}


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.115 footnotes under guarded S2 writeback.")
    parser.add_argument("--apply", action="store_true", help="write after all source and table guards pass")
    args = parser.parse_args()
    statements, mentions, planned = prepare()
    print("P.115 notes review plan")
    print("  5 existing statements become 11 source-attributed S2 relation candidates")
    print("  split 3 Litta/Moroni/Giustiniani citations, Patrignani and Orbaan citations, Moroni correction, and Blunt citation")
    print("  add one exact mention for the book's dedicatee; candidates and coverage unchanged")
    for name, data in planned.items():
        print(f"  planned {name} sha256={digest(data)} bytes={len(data)}")
    if not args.apply:
        print("DRY-RUN: no files written")
        return

    originals = {name: path.read_bytes() for name, path in TABLES.items()}
    for name, path in TABLES.items():
        if digest(originals[name]) != EXPECTED_SHA256[name]:
            raise SystemExit(f"STOP: {name} changed between dry-run and apply")
    backups = {name: TABLES[name].with_name(TABLES[name].name + BACKUP_SUFFIX) for name in planned}
    for backup in backups.values():
        if backup.exists():
            raise SystemExit(f"STOP: recovery backup already exists: {backup.name}")
    temp_paths: dict[str, Path] = {}
    for name, path in TABLES.items():
        if name in backups:
            shutil.copy2(path, backups[name])
    try:
        for name, data in planned.items():
            temp_path = TABLES[name].with_name(TABLES[name].name + ".tmp-s2-chp4-p115-notes-20261011")
            if temp_path.exists():
                raise SystemExit(f"STOP: temporary path already exists: {temp_path.name}")
            temp_path.write_bytes(data)
            temp_paths[name] = temp_path
        for name, path in temp_paths.items():
            path.replace(TABLES[name])
    except Exception:
        for name, backup in backups.items():
            target = TABLES[name]
            if backup.exists() and digest(target.read_bytes()) != digest(originals[name]):
                shutil.copy2(backup, target)
        raise
    finally:
        for path in temp_paths.values():
            if path.exists():
                path.unlink()
    print("APPLIED")
    for name, backup in backups.items():
        print(f"  {name}: sha256={digest(TABLES[name].read_bytes())} backup={backup.name}")
    print(f"  rows: statements={len(statements)} mentions={len(mentions)}")


if __name__ == "__main__":
    main()
