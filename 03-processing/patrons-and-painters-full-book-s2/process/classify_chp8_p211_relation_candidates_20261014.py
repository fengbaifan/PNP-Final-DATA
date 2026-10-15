"""Classify p.211 S2 statements, split mixed claims, and repair source mappings."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE = ROOT / SOURCE_REL
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l84-96"
BACKUP_SUFFIX = ".bak-s2-chp8-p211-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "7344faaa5e491ace953556b1c5bf41f3d5d828590a275b44f1096a0ef86a035c",
    CANDIDATES: "a02431b737c70be448d1bb56aa839abf79cc5efdc205bde7669f1e5350719c8e",
    MENTIONS: "7bf6eb46012a12e3a19d0a612fafabf58bffa2e340f7e7d0ecb2eec77b8ab194",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
EXPECTED_SEGMENT_SHA = "c4febe69e396257dee157d52e90f34ab1fdcc4c09162e8f81db5b744d70901ff"
NEW_CANDIDATES = [
    ("cand-12049", "Giuseppe Ghezzi's notes on Andrea del Rosso's artistic activities", "archive",
     "Haskell identifies Ghezzi's notes as a source for Andrea's artistic activities in Rome; title, repository and date are not supplied in this passage.", 95),
    ("cand-12050", "Brief career accounts of Andrea and Ottavio del Rosso by Manini and Salvini", "archive",
     "Haskell attributes brief accounts of Andrea's and Ottavio's careers to Giuseppe Manini and Salvino Salvini; titles, editions and precise source locations are not supplied here.", 90),
]
NEW_STATEMENT_IDS = {
    "st-chp8-p211-andrea-artistic-activity-in-resta-letters",
    "st-chp8-p211-andrea-inventory-bought-durer-pictures-in-cologne",
    "st-chp8-p211-ottavio-entered-church",
    "st-chp8-p211-ottavio-lived-in-volterra",
    "st-chp8-p211-ottavio-quoted-reputation-for-goodness",
}
NEW_MENTION_IDS = {"m-chp8-p211-081", "m-chp8-p211-082", "m-chp8-p211-083"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preconditions and dry-run checks pass")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    hashes = {path: sha(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit("a table or source file changed since the p.211 review baseline")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES, MENTIONS)}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("a recovery copy already exists; inspect it before applying")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[83:96])
    if sha(segment_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.211 source segment changed since review")
    segments = read_jsonl(TABLES / "segments.jsonl")
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (segment.get("line_start"), segment.get("line_end")) != (84, 96):
        raise SystemExit("p.211 segment metadata changed")
    if segment.get("sha256") != EXPECTED_SEGMENT_SHA or segment.get("asset_sha256") != EXPECTED_HASHES[SOURCE]:
        raise SystemExit("p.211 segment/source fingerprints do not match")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(by_id) != len(statements) or len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise SystemExit("statement, candidate, or mention IDs are not unique")

    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    expected_unset = {
        "st-chp8-p211-andrea-artistic-activity-sources",
        "st-chp8-p211-caravaggio-bequest-description-and-dimensions",
        "st-chp8-p211-collection-records-indicate-brothers-travelled",
        "st-chp8-p211-del-rosso-inventory-reports-glass-and-durer-pairs",
        "st-chp8-p211-del-rosso-trade-patronage-connected",
        "st-chp8-p211-forebears-grandfather-open",
        "st-chp8-p211-manini-salvini-career-accounts",
        "st-chp8-p211-ottavio-bishop-volterra",
    }
    unset = {row["statement_id"] for row in page_rows if "relation_candidate" not in (row.get("qualifiers") or {})}
    if len(page_rows) != 32 or unset != expected_unset:
        raise SystemExit(f"unexpected p.211 inventory: rows={len(page_rows)}, unset_delta={sorted(unset ^ expected_unset)}")
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("a planned statement ID already exists")
    if {row[0] for row in NEW_CANDIDATES} & set(candidate_by_id):
        raise SystemExit("a planned candidate ID already exists")
    if NEW_MENTION_IDS & set(mention_by_id):
        raise SystemExit("a planned mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12048:
        raise SystemExit("candidate sequence changed since the reviewed baseline")

    expected_mentions = {
        "m-chp8-p211-013": ("cand-2286", "Bjshop"),
        "m-chp8-p211-019": ("cand-0954", "Albert Diirer"),
        "m-chp8-p211-021": ("cand-7494", "two ‘by Albert Diirer bought by me in Cologne’"),
    }
    for mention_id, expected in expected_mentions.items():
        row = mention_by_id.get(mention_id)
        if not row or (row["candidate_id"], row["surface_form"]) != expected:
            raise SystemExit(f"mention {mention_id} no longer matches its expected prestate")
    old_durer = candidate_by_id["cand-7494"]
    if old_durer["canonical_name"] != "Two pictures attributed to Albrecht Dürer in the del Rosso collection":
        raise SystemExit("the p.211 Dürer work candidate changed since review")

    new_candidates = []
    for candidate_id, name, kind, detail, line in NEW_CANDIDATES:
        new_candidates.append({
            "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
            "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
            "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        })
    candidates.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    def exact_mention(mention_id: str, candidate_id: str, surface: str, note: str) -> dict:
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"expected unique mention text is missing or repeated: {surface!r}")
        return {"mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
                "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note}

    new_mentions = [
        exact_mention("m-chp8-p211-081", "cand-12049", "notes", "The plural 'notes' refers to Giuseppe Ghezzi's source notes; no title or repository is supplied here."),
        exact_mention("m-chp8-p211-082", "cand-12050", "Very brief accounts of the careers of Andrea and Ottavio", "A source group attributed to Manini and Salvini; titles and editions remain unspecified."),
        exact_mention("m-chp8-p211-083", "cand-3400", "Church", "The capitalized institutional reference to the Catholic Church, not a church building."),
    ]
    mention_by_id["m-chp8-p211-019"]["note"] = "The OCR reads 'Albert Diirer'; the page image reads 'Albert Dürer'. Mapping to the indexed Albrecht Dürer candidate remains provisional for S3 identity review."
    mention_by_id["m-chp8-p211-021"]["note"] = "Andrea's inventory is quoted as naming 'Albert Dürer'; the two works remain unidentified and the name-to-index identity is provisional for S3."
    mentions.extend(new_mentions)
    mention_by_id = {row["mention_id"]: row for row in mentions}

    candidate_by_id["cand-7494"]["canonical_name"] = "Two pictures attributed to 'Albert Dürer' in the del Rosso collection"
    candidate_by_id["cand-7494"]["detail"] = "The printed inventory wording is 'Albert Dürer'; identity with the indexed Albrecht Dürer candidate remains undecided for S3. Individual titles are not supplied."

    def add_corrections(q: dict, corrections: list[dict]) -> None:
        old = list(q.get("ocr_corrections") or [])
        for correction in corrections:
            if correction not in old:
                old.append(correction)
        q["ocr_corrections"] = old

    def update(statement_id: str, relation: bool, note: str, **changes) -> None:
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        for key in ("predicate", "subject_candidate_id", "object_candidate_id", "original_quote"):
            if key in changes:
                value = changes.pop(key)
                row[key] = value
        corrections = changes.pop("ocr_corrections", None)
        if corrections:
            add_corrections(q, corrections)
        for key, value in changes.items():
            if key == "mentioned_candidate_ids":
                q[key] = list(dict.fromkeys(value))
            else:
                q[key] = value
        row["qualifiers"] = q

    def excerpt(start_line: int, end_line: int, first: str, last: str) -> str:
        source = "\n".join(source_lines[start_line - 1:end_line])
        start, end = source.find(first), source.rfind(last)
        if start < 0 or end < start:
            raise SystemExit(f"expected source phrase missing at L{start_line}-L{end_line}: {first!r} ... {last!r}")
        return source[start:end + len(last)]

    page9 = "CHP-8.pdf physical page 9."
    update(
        "st-chp8-p211-andrea-artistic-activity-sources", True,
        "Haskell identifies Ghezzi's notes as one source for Andrea's activities; the note is a source candidate whose title and repository are not supplied.",
        predicate="ghezzi_notes_refer_to_andreas_artistic_activities",
        subject_candidate_id="cand-12049", object_candidate_id="cand-2275",
        claim="Haskell says Andrea del Rosso's artistic activities in Rome are referred to in Giuseppe Ghezzi's notes.",
        qualification="The note's title, date and repository are not identified in this passage; no independent source inspection is claimed.",
        original_quote=excerpt(95, 95, "Andrea’s artistic activities", "Ghezzi’s notes"),
        mentioned_candidate_ids=["cand-12049", "cand-2275", "cand-4490", "cand-1157"],
    )
    update(
        "st-chp8-p211-caravaggio-bequest-description-and-dimensions", False,
        "This statement records the reported painting's subject description and approximate dimensions; it does not introduce a separate relation candidate.",
        subject_candidate_id="cand-7514", object_candidate_id=None,
        mentioned_candidate_ids=["cand-7514", "cand-7512", "cand-7513"],
    )
    update(
        "st-chp8-p211-collection-records-indicate-brothers-travelled", False,
        "Haskell infers extensive travel from the places associated with works in the collection; the records do not identify which brother travelled to each place.",
        subject_candidate_id="cand-7489", object_candidate_id=None,
        mentioned_candidate_ids=["cand-7489", "cand-7520", "cand-7490", "cand-7493", "cand-7494", "cand-6300", "cand-0954"],
    )
    update(
        "st-chp8-p211-del-rosso-inventory-reports-glass-and-durer-pairs", True,
        "This statement is narrowed to the two modern glass pictures recorded as coming from Mainz; the Dürer pair and its purchase in Cologne are recorded separately.",
        predicate="del_rosso_collection_record_lists_two_modern_glass_pictures_from_mainz",
        subject_candidate_id="cand-7520", object_candidate_id="cand-7493",
        claim="Haskell says the Del Rosso collection record lists two modern pictures on glass from Mainz.",
        qualification="The pictures are unidentified; the source does not name their makers.",
        original_quote=excerpt(88, 88, "‘two modern ones on glass’", "from Mainz"),
        mentioned_candidate_ids=["cand-7520", "cand-7493", "cand-7490"],
    )
    update(
        "st-chp8-p211-del-rosso-trade-patronage-connected", False,
        "This is Haskell's general characterization that trading and patronage were closely connected, with Roomer as comparison rather than a named business partner in this claim.",
        object_candidate_id=None,
        mentioned_candidate_ids=["cand-7489", "cand-2223"],
    )
    update(
        "st-chp8-p211-forebears-grandfather-open", True,
        "This p.211 fragment is completed by the p.212 statement identifying the grandfather Andrea and his chapel project; classify the two page fragments together.",
        claim="Haskell introduces the del Rosso brothers' grandfather in 1642, two years before his death; p.212 completes the account by saying he had a family chapel built.",
        qualification="The sentence crosses the page break and is not an independent second claim; its continuation is st-chp8-p212-grandfather-andrea-built-chapel.",
        mentioned_candidate_ids=["cand-7489", "cand-2279", "cand-7522"],
    )
    update(
        "st-chp8-p211-manini-salvini-career-accounts", True,
        "Haskell attributes brief career accounts to Manini and Salvini; the source group is represented as an open archive candidate because no titles or editions are given.",
        predicate="brief_career_accounts_by_manini_and_salvini",
        subject_candidate_id="cand-12050", object_candidate_id=None,
        mentioned_candidate_ids=["cand-12050", "cand-2275", "cand-2286", "cand-7505", "cand-7506"],
    )
    update(
        "st-chp8-p211-ottavio-bishop-volterra", True,
        "Haskell reports that Ottavio became Bishop of Volterra; Volterra is retained as the named place, with no appointing authority or separate ecclesiastical institution inferred.",
        predicate="ottavio_became_bishop_of_volterra",
        claim="Haskell says Ottavio del Rosso became Bishop of Volterra.",
        qualification="The source's OCR reads 'Bjshop'; the page image reads 'Bishop'. The passage does not identify who appointed him.",
        original_quote=excerpt(87, 87, "became Bjshop of Volterra", "became Bjshop of Volterra"),
        mentioned_candidate_ids=["cand-2286", "cand-7491"],
        ocr_corrections=[{"source_line": 87, "ocr": "Bjshop", "print": "Bishop", "basis": page9}],
    )

    update(
        "st-chp8-p211-del-rosso-inventory-reports-glass-and-durer-pairs", True,
        "This statement is narrowed to the two modern glass pictures recorded as coming from Mainz; the Dürer pair and its purchase in Cologne are recorded separately.",
        ocr_corrections=[{"source_line": 88, "ocr": "Albert Diirer", "print": "Albert Dürer", "basis": page9}],
    )
    update(
        "st-chp8-p211-andrea-artistic-activity-sources", True,
        "Haskell identifies Ghezzi's notes as one source for Andrea's activities; the note is a source candidate whose title and repository are not supplied.",
        ocr_corrections=[{"source_line": 95, "ocr": "and'ih two letters", "print": "and in two letters", "basis": page9}],
    )

    # The continuation row on p.212 already points back to this fragment; keep both directions explicit.
    continuation = by_id["st-chp8-p212-grandfather-andrea-built-chapel"]
    continuation_q = dict(continuation.get("qualifiers") or {})
    continuation_q["continues_statement_id"] = "st-chp8-p211-forebears-grandfather-open"
    continuation["qualifiers"] = continuation_q

    def make_statement(statement_id: str, predicate: str, subject: str | None, obj: str | None,
                       claim: str, quote: str, start_line: int, end_line: int, mentioned: list[str],
                       relation: bool, note: str, qualification: str, **extra) -> dict:
        q = {
            "source_line_start": start_line, "source_line_end": end_line, "printed_page": 211, "pdf_physical_page": 9,
            "claim": claim, "speaker": "Haskell", "text_layer": "body or footnote as marked by source position",
            "qualification": qualification, "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation, "relation_candidate_note": note,
        }
        q.update(extra)
        return {"statement_id": statement_id, "segment_id": SEGMENT_ID, "subject_candidate_id": subject,
                "object_candidate_id": obj, "predicate": predicate, "qualifiers": q,
                "original_quote": quote, "origin": "book", "source_file": SOURCE_REL}

    statements.extend([
        make_statement(
            "st-chp8-p211-andrea-artistic-activity-in-resta-letters",
            "resta_letters_to_gabburri_refer_to_andreas_artistic_activities", "cand-7515", "cand-2275",
            "Haskell cites two letters from Sebastiano Resta to Francesco Gabburri, published by Bottari, as sources for Andrea's artistic activities in Rome.",
            excerpt(95, 95, "two letters from Sebastiano Resta", "pp. 100 and 104"), 95, 95,
            ["cand-7515", "cand-2275", "cand-4490", "cand-2134", "cand-1097", "cand-7516"], True,
            "Haskell identifies the two letters and their publication pages as sources for Andrea's activities; the letters and cited pages were not independently consulted.",
            "The letters are already represented by an open archive candidate; Bottari volume II remains separately identified as their cited publication.",
            ocr_corrections=[{"source_line": 95, "ocr": "and'ih two letters", "print": "and in two letters", "basis": page9}]),
        make_statement(
            "st-chp8-p211-andrea-inventory-bought-durer-pictures-in-cologne",
            "andrea_inventory_records_purchase_of_two_pictures_named_albert_durer_in_cologne", "cand-2275", "cand-7494",
            "Haskell quotes Andrea's inventory as naming two pictures by 'Albert Dürer' and saying that the writer bought them in Cologne.",
            excerpt(88, 88, "and two ‘by Albert Diirer", "Cologne’"), 88, 88,
            ["cand-2275", "cand-7494", "cand-0954", "cand-6300"], True,
            "The purchase is directly reported in the first-person inventory quotation; mapping 'Albert Dürer' to the indexed Albrecht Dürer candidate remains for S3.",
            "The source does not identify the individual pictures; preserve its printed name form and do not treat the indexed identity match as verified.",
            ocr_corrections=[{"source_line": 88, "ocr": "Albert Diirer", "print": "Albert Dürer", "basis": page9}]),
        make_statement(
            "st-chp8-p211-ottavio-entered-church",
            "ottavio_entered_the_catholic_church", "cand-2286", "cand-3400",
            "Haskell says Ottavio entered the Church.", excerpt(86, 87, "Ottavio entered the", "Church"), 86, 87,
            ["cand-2286", "cand-3400"], True,
            "The capitalized Church is an institutional referent; the passage does not specify an order or appointment.",
            "This records only Haskell's statement that Ottavio entered the Church, without inferring a particular religious order."),
        make_statement(
            "st-chp8-p211-ottavio-lived-in-volterra",
            "ottavio_lived_in_volterra", "cand-2286", "cand-7491",
            "Haskell says Ottavio lived in Volterra.", excerpt(87, 87, "Volterra, where he lived", "Volterra, where he lived"), 87, 87,
            ["cand-2286", "cand-7491"], True,
            "The relative clause explicitly locates Ottavio in Volterra; it is kept separate from his episcopal office and the quoted characterization.",
            "The source gives no residence dates."),
        make_statement(
            "st-chp8-p211-ottavio-quoted-reputation-for-goodness",
            "haskell_quoted_italian_characterization_of_ottavio", "cand-2286", None,
            "Haskell quotes the Italian phrase 'concetto di straordinaria bontà' in characterizing Ottavio.",
            excerpt(87, 87, "‘concetto di straordinaria bontà’", "‘concetto di straordinaria bontà’"), 87, 87,
            ["cand-2286"], False,
            "This is an attributed qualitative characterization, not a separate relationship or office.",
            "The Italian quotation is preserved without imposing a stronger interpretation."),
    ])

    final_page = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(final_page) != 37 or any("relation_candidate" not in (row.get("qualifiers") or {}) for row in final_page):
        raise SystemExit("p.211 statements remain unclassified or the planned statement count changed")
    if len(statements) != 14246 or len(candidates) != 12028 or len(mentions) != 28077:
        raise SystemExit(f"unexpected output counts: statements={len(statements)}, candidates={len(candidates)}, mentions={len(mentions)}")

    outputs = {STATEMENTS: jsonl_bytes(statements), CANDIDATES: csv_bytes(candidate_fields, candidates),
               MENTIONS: csv_bytes(mention_fields, mentions)}
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    print("p.211 statements:", len(final_page),
          "true:", sum(row["qualifiers"]["relation_candidate"] is True for row in final_page),
          "false:", sum(row["qualifiers"]["relation_candidate"] is False for row in final_page))
    print("new statements:", ", ".join(sorted(NEW_STATEMENT_IDS)))
    print("new candidates:", ", ".join(row["candidate_id"] for row in new_candidates))
    print("new mentions:", ", ".join(row["mention_id"] for row in new_mentions))
    for path, data in outputs.items():
        print(f"{path.relative_to(ROOT)} sha256={sha(data)} bytes={len(data)}")
    if args.apply:
        for path, backup in backups.items():
            shutil.copy2(path, backup)
        try:
            for path, data in outputs.items():
                atomic_write(path, data)
        except Exception:
            for path, backup in backups.items():
                path.write_bytes(backup.read_bytes())
            raise
        print("recovery copies:", ", ".join(str(path.relative_to(ROOT)) for path in backups.values()))


if __name__ == "__main__":
    main()
