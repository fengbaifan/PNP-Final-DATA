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
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-4.pdf"
PAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p112_body_notes_page_review_20261011.png"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"

EXPECTED = {
    SOURCE: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    PDF: "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303",
    PAGE: "47ab75b69c7b890158478ffbd3609bd428d3c1812732a7b562310f4a6d81bc7f",
    STATEMENTS: "e321d29b1d8b790f0400789bda f8c6d27d1aeb159d4cbb0a92918112ed3c14ff".replace(" ", ""),
    MENTIONS: "0251842ac93313725448ba f44c7878ef71f74f5dfd31cdad8df19a5f84e3dca9".replace(" ", ""),
    CANDIDATES: "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    COVERAGE: "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}

SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
SOURCE_LINE = "8 In records of payments which appear to be dated 1656 he is listed in Cardinal Barberini’ssamiglia— Biblioteca Vaticana, Barb..."
ORIGINAL_ID = "st-chp4-sec-ii-notes-p112-fn6-payment-records"
CITATION_ID = "st-chp4-sec-ii-notes-p112-fn6-citation"
MENTION_ID = "m-chp4-sec-ii-notes-p112-he-cassiano"
STATEMENT_BACKUP_SUFFIX = ".bak-s2-chp4-p112-fn6-20261011"
MENTION_BACKUP_SUFFIX = ".bak-s2-chp4-p112-fn6-20261011"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_atomic(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all source, table, mention, and row guards pass")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f"guard failed: {path.relative_to(ROOT)} sha256={actual}, expected={expected}")

    source_text = SOURCE.read_text(encoding="utf-8")
    lines = source_text.splitlines()
    if lines[284] != SOURCE_LINE:
        raise SystemExit("guard failed: source line 285 changed")
    segment_rows = read_jsonl(SEGMENTS)
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("guard failed: S2 source segment identity or hash changed")
    page_text = "\n".join(lines[231:308])
    if page_text[9090:9092] != "he":
        raise SystemExit("guard failed: expected Cassiano anaphor does not match the source segment")

    candidate_rows = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    expected_candidates = {
        "cand-2036": "person",
        "cand-2962": "archive",
        "cand-4380": "institution",
        "cand-5646": "institution",
        "cand-5915": "person",
        "cand-5917": "archive",
    }
    for candidate_id, candidate_type in expected_candidates.items():
        if candidates.get(candidate_id, {}).get("suggested_type") != candidate_type:
            raise SystemExit(f"guard failed: candidate type changed for {candidate_id}")

    before = read_jsonl(STATEMENTS)
    statement_ids = [row.get("statement_id") for row in before]
    if len(statement_ids) != len(set(statement_ids)):
        raise SystemExit("guard failed: duplicate statement IDs already exist")
    by_id = {row["statement_id"]: row for row in before}
    if CITATION_ID in by_id:
        raise SystemExit(f"guard failed: {CITATION_ID} already exists")
    old = by_id.get(ORIGINAL_ID)
    if not old:
        raise SystemExit(f"guard failed: missing {ORIGINAL_ID}")
    if (
        old.get("segment_id") != SEGMENT_ID
        or old.get("subject_candidate_id") != "cand-5917"
        or old.get("object_candidate_id") != "cand-4380"
        or old.get("predicate") != "archival_locator_for_payment_records"
        or old.get("original_quote") != SOURCE_LINE
        or (old.get("qualifiers") or {}).get("relation_candidate") is not None
    ):
        raise SystemExit("guard failed: existing p.112 footnote 6 statement changed")
    body = by_id.get("st-chp4-sec-ii-p112-cardinal-flight-return")
    if not body or (body.get("qualifiers") or {}).get("footnote_statement_id") != ORIGINAL_ID:
        raise SystemExit("guard failed: p.112 body-to-footnote link changed")

    mention_rows = list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
    mention_ids = [row.get("mention_id") for row in mention_rows]
    if len(mention_ids) != len(set(mention_ids)):
        raise SystemExit("guard failed: duplicate mention IDs already exist")
    if MENTION_ID in set(mention_ids):
        raise SystemExit(f"guard failed: {MENTION_ID} already exists")
    if any(
        row.get("segment_id") == SEGMENT_ID
        and row.get("candidate_id") == "cand-2036"
        and row.get("surface_form") == "he"
        and row.get("start_char") == "9090"
        for row in mention_rows
    ):
        raise SystemExit("guard failed: Cassiano anaphor mention already exists")

    updated = json.loads(json.dumps(old, ensure_ascii=False))
    updated["subject_candidate_id"] = "cand-2036"
    updated["object_candidate_id"] = "cand-5646"
    updated["predicate"] = "listed_as_member_of"
    q = updated.setdefault("qualifiers", {})
    q.update(
        {
            "claim": "Haskell reports that payment records apparently dated 1656 list Cassiano dal Pozzo as belonging to Cardinal Barberini’s famiglia (household).",
            "speaker": "Haskell",
            "text_layer": "footnote-reported archival record",
            "mentioned_candidate_ids": ["cand-2036", "cand-5646", "cand-5915", "cand-5917", "cand-4380"],
            "qualification": "The records only appear to be dated 1656 and were not independently consulted. The Cardinal remains unidentified. The printed famiglia is represented as the Barberini household; no specific office or employment status is inferred.",
            "relation_candidate": True,
            "relation_candidate_note": "This is Haskell’s explicit report that the records list Cassiano in the Barberini household. It does not identify the Cardinal or specify Cassiano’s office; no formal S6 edge is created.",
            "source_candidate_id": "cand-5917",
            "citation_statement_ids": [CITATION_ID],
            "printed_note_number": 6,
            "ocr_corrections": [
                {"source_line": 285, "source_form": "8", "print_form": "6"},
                {"source_line": 285, "source_form": "samiglia", "print_form": "famiglia"},
                {"source_line": 285, "source_form": "Barb...", "print_form": "Barb. Lat. 5635"},
            ],
        }
    )
    citation = {
        "statement_id": CITATION_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-5917",
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 285,
            "source_line_end": 285,
            "pdf_physical_page": 23,
            "printed_page_locator": "p.112 footnote 6",
            "claim": "Haskell’s book cites payment records identified by the locator Biblioteca Vaticana, Barb. Lat. 5635.",
            "speaker": "Haskell footnote",
            "text_layer": "archival bibliographic citation",
            "citation_locator": "Biblioteca Vaticana, Barb. Lat. 5635",
            "citation_context_candidate_id": "cand-2036",
            "cited_material_not_independently_consulted": True,
            "mentioned_candidate_ids": ["cand-5917", "cand-4380"],
            "relation_candidate": True,
            "relation_candidate_note": "This records the source’s citation pointer only; the payment records and the reported entry were not independently consulted.",
            "printed_note_number": 6,
        },
        "original_quote": SOURCE_LINE,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }
    after = [updated if row.get("statement_id") == ORIGINAL_ID else row for row in before]
    after.append(citation)
    if len({row.get("statement_id") for row in after}) != len(after):
        raise SystemExit("guard failed: output statement IDs would not be unique")
    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False) for row in after) + "\n").encode("utf-8")

    mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-2036",
        "surface_form": "he",
        "start_char": "9090",
        "end_char": "9092",
        "note": "Anaphor refers to Cassiano dal Pozzo in the preceding p.112 text; the printed page confirms footnote 6 follows the sentence about his reinstatement.",
    }
    mention_fields = list(mention_rows[0].keys())
    if set(mention) != set(mention_fields):
        raise SystemExit(f"guard failed: mention schema changed: {mention_fields}")
    new_mention_rows = mention_rows + [mention]
    from io import StringIO
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=mention_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(new_mention_rows)
    mention_bytes = buffer.getvalue().encode("utf-8")

    print(
        json.dumps(
            {
                "mode": "APPLY PREFLIGHT" if args.apply else "DRY-RUN",
                "updated_statement": {
                    "statement_id": ORIGINAL_ID,
                    "subject": updated["subject_candidate_id"],
                    "object": updated["object_candidate_id"],
                    "predicate": updated["predicate"],
                    "relation_candidate": True,
                },
                "added_citation_statement": {
                    "statement_id": CITATION_ID,
                    "subject": citation["subject_candidate_id"],
                    "object": citation["object_candidate_id"],
                    "predicate": citation["predicate"],
                },
                "added_mention": mention,
                "statements_before": len(before),
                "statements_after": len(after),
                "mentions_before": len(mention_rows),
                "mentions_after": len(new_mention_rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if not args.apply:
        return 0

    statement_backup = STATEMENTS.with_name(STATEMENTS.name + STATEMENT_BACKUP_SUFFIX)
    mention_backup = MENTIONS.with_name(MENTIONS.name + MENTION_BACKUP_SUFFIX)
    if statement_backup.exists() or mention_backup.exists():
        raise SystemExit("guard failed: one or more recovery backups already exist")
    statement_backup.write_bytes(STATEMENTS.read_bytes())
    mention_backup.write_bytes(MENTIONS.read_bytes())
    try:
        write_atomic(STATEMENTS, statement_bytes)
        write_atomic(MENTIONS, mention_bytes)
    except Exception:
        write_atomic(STATEMENTS, statement_backup.read_bytes())
        write_atomic(MENTIONS, mention_backup.read_bytes())
        raise
    print(f"APPLIED statements sha256={digest(STATEMENTS)}")
    print(f"recovery copy sha256={digest(statement_backup)}")
    print(f"APPLIED mentions sha256={digest(MENTIONS)}")
    print(f"recovery copy sha256={digest(mention_backup)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
