#!/usr/bin/env python3
"""Classify eight Rosa footnote citations and register six source-bounded letters.

Default mode is a read-only dry run. --apply requires the exact reviewed table
hashes, verifies source segment hashes and anchors, creates recoverable backups,
then atomically replaces the three S2 tables.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCES = ROOT / "02-sources" / "02-Markdown"
BACKUP_SUFFIX = ".bak-s2-handoff-rosa-letter-citations-20261010"

EXPECTED_HASHES = {
    "entity-candidates.csv": "22fde23647c189c636b314427fab097f60ec54d75ead8eaf8b3b041ad2d7ce61",
    "mentions.csv": "54bb4aec6a410db284dd95b0179fcb16dd3031093d9fd7309b8accf394e0ba25",
    "book-statements.jsonl": "9ea1b452173df2c26b070d84bdbe41f40a27f54b633704c49876b7232378f2dd",
}

APPLIED_HASHES = {
    "entity-candidates.csv": "b4ac5c42748249c553bf133ab9267acb9fbb85422d1198208b19b7e8b8c250de",
    "mentions.csv": "c95782736e9cfc5b4dad1cbae2afa04f0694548f29dd7f46a2d7beffdf1de897",
    "book-statements.jsonl": "e79f8ca2a01ab5e032e51bd3c92e242a1ddd6edbc89d0ead4d61736b8098ca12",
}

SPECS = [
    {
        "statement_id": "st-chp5-notes-l163-rosa-ricciardi-letter",
        "candidate_id": "cand-11571",
        "date": "1660-04-02",
        "name": "Letter from Salvator Rosa to G. B. Ricciardi, 2 April 1660",
        "segment_id": "chp-5:05_CHP-5_sec_iii:l126-165",
        "source_file": "05_CHP-5_sec_iii.md",
        "line": 163,
        "surface": "Letter from Salvator Rosa to G. B. Ricciardi dated 2 April 1660",
        "author": "cand-2236",
        "recipient": "cand-2187",
        "publication": "cand-6205",
        "page": 109,
        "linked": ["st-chp5-p142-rosa-bought-vanlaer-copy-for-ricciardi"],
        "detail": "Haskell identifies a letter from Salvator Rosa to G. B. Ricciardi dated 2 April 1660 and cites de Rinaldis (1939), p. 109. The letter and cited edition have not been independently examined; the source obscures part of the surname.",
        "citation_role": "letter",
    },
    {
        "statement_id": "st-chp5-seciv-note-l40-p143-marker1",
        "candidate_id": "cand-11572",
        "date": "1666-10-09",
        "name": "Letter from Salvator Rosa to G. B. Ricciardi, 9 October 1666",
        "segment_id": "chp-5:05_CHP-5_sec_iv:l39-54",
        "source_file": "05_CHP-5_sec_iv.md",
        "line": 40,
        "surface": "Letter to Ricciardi of 9 October 1666",
        "author": "cand-2236",
        "recipient": "cand-2187",
        "publication": "cand-6239",
        "page": 138,
        "linked": ["st-chp5-p143-rosa-stoic-roast-meat-letter"],
        "detail": "Haskell identifies a letter to Ricciardi dated 9 October 1666 and cites Limentani (1950), p. 138. Rosa is identified as author by the linked body passage. The letter itself has not been independently examined.",
        "citation_role": "letter",
    },
    {
        "statement_id": "st-chp5-seciv-note-l45-p143-marker6",
        "candidate_id": None,
        "segment_id": "chp-5:05_CHP-5_sec_iv:l39-54",
        "source_file": "05_CHP-5_sec_iv.md",
        "line": 45,
        "surface": None,
        "publication": "cand-6239",
        "page": 139,
        "linked": ["st-chp5-p143-carlo-de-rossi-greatest-roman-patron"],
        "citation_role": "publication",
    },
    {
        "statement_id": "st-chp5-seciv-note-l46-p144-marker1",
        "candidate_id": None,
        "segment_id": "chp-5:05_CHP-5_sec_iv:l39-54",
        "source_file": "05_CHP-5_sec_iv.md",
        "line": 46,
        "surface": None,
        "publication": "cand-6205",
        "page": 199,
        "linked": ["st-chp5-p143-rosa-and-de-rossi-quarrel-in-1667"],
        "citation_role": "publication",
    },
    {
        "statement_id": "st-chp5-seciv-note-l48-p144-marker4",
        "candidate_id": "cand-11573",
        "date": "1651-04-24",
        "name": "Letter from Salvator Rosa to G. B. Ricciardi, 24 April 1651",
        "segment_id": "chp-5:05_CHP-5_sec_iv:l39-54",
        "source_file": "05_CHP-5_sec_iv.md",
        "line": 48,
        "surface": "Letter of 24 April 1651",
        "author": "cand-2236",
        "recipient": "cand-2187",
        "publication": "cand-6205",
        "page": 17,
        "linked": ["st-chp5-p144-rosa-painted-for-ricciardi-and-sought-advice", "st-chp5-p144-rosa-requested-lively-story-for-picture"],
        "detail": "Haskell cites de Rinaldis (1939), p. 17, for a letter dated 24 April 1651. Rosa and Ricciardi are identified by the linked body passage. The letter itself has not been independently examined.",
        "citation_role": "letter",
    },
    {
        "statement_id": "st-chp5-seciv-note-l49-p144-marker5",
        "candidate_id": "cand-11574",
        "date": "1651-05-12",
        "name": "Letter from Salvator Rosa to G. B. Ricciardi, 12 May 1651",
        "segment_id": "chp-5:05_CHP-5_sec_iv:l39-54",
        "source_file": "05_CHP-5_sec_iv.md",
        "line": 49,
        "surface": "Letter of 12 May 1Ó51",
        "author": "cand-2236",
        "recipient": "cand-2187",
        "publication": "cand-6205",
        "page": 19,
        "linked": ["st-chp5-p144-rosa-proposed-georgics-subject-of-justice", "st-chp5-p144-rosa-claimed-rome-heard-of-his-originality"],
        "detail": "Haskell cites de Rinaldis (1939), p. 19, for a letter dated 12 May 1651; the printed year is read as 1651 although the OCR has 1Ó51. Rosa and Ricciardi are identified by the linked body passage. The letter itself has not been independently examined.",
        "citation_role": "letter",
    },
    {
        "statement_id": "st-chp5-seciv-note-l50-p144-marker6",
        "candidate_id": "cand-11575",
        "date": "1662-05-13",
        "name": "Letter from Salvator Rosa to G. B. Ricciardi, 13 May 1662",
        "segment_id": "chp-5:05_CHP-5_sec_iv:l39-54",
        "source_file": "05_CHP-5_sec_iv.md",
        "line": 50,
        "surface": "Letter of 13 May 1662",
        "author": "cand-2236",
        "recipient": "cand-2187",
        "publication": "cand-4830",
        "page": 450,
        "linked": ["st-chp5-p144-rosa-letter-described-landscape-contrast"],
        "detail": "Haskell cites Bottari, vol. I, p. 450, for Rosa's letter dated 13 May 1662. Rosa and Ricciardi are identified by the linked body passage. The letter itself has not been independently examined.",
        "citation_role": "letter",
    },
    {
        "statement_id": "st-chp5-seciv-note-l51-p145-marker1",
        "candidate_id": "cand-11576",
        "date": "1664-05-21",
        "name": "Letter from Salvator Rosa to G. B. Ricciardi, 21 May 1664",
        "segment_id": "chp-5:05_CHP-5_sec_iv:l39-54",
        "source_file": "05_CHP-5_sec_iv.md",
        "line": 51,
        "surface": "Letter ofZI May 1664",
        "author": "cand-2236",
        "recipient": "cand-2187",
        "publication": "cand-6205",
        "page": 164,
        "linked": ["st-chp5-p145-rosa-letter-disagreed-about-little-picture"],
        "detail": "Haskell cites de Rinaldis (1939), p. 164, for a letter dated 21 May 1664; the printed page reads 21 where OCR has ZI. Rosa and Ricciardi are identified by the linked body passage; the recipient is contextual and is not named in this note. The letter itself has not been independently examined.",
        "citation_role": "letter",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def repair_applied_claims() -> None:
    for name, expected in APPLIED_HASHES.items():
        actual = sha256(TABLES / name)
        if actual != expected:
            raise SystemExit(f"repair precondition failed: {name} SHA-256 {actual} != {expected}")
    path = TABLES / "book-statements.jsonl"
    rows = read_jsonl(path)
    by_id = {row["statement_id"]: row for row in rows}
    changed = []
    for spec in SPECS:
        if not spec["candidate_id"]:
            continue
        for role, predicate in (("authored-by", "authored_by"), ("addressed-to", "addressed_to")):
            statement_id = f"st-chp5-l{spec['line']}-letter-{role}"
            row = by_id.get(statement_id)
            if row is None or row["predicate"] != predicate or row["qualifiers"].get("date") != spec["date"]:
                raise ValueError(f"unexpected applied relation state: {statement_id}")
            if role == "authored-by":
                expected_claim = "Haskell identifies Salvator Rosa as the letter's author."
                claim = f"Haskell identifies the letter dated {spec['date']} as authored by Salvator Rosa."
            else:
                expected_claim = "Haskell's text identifies G. B. Ricciardi as the letter's recipient."
                claim = f"Haskell's text identifies the letter dated {spec['date']} as addressed to G. B. Ricciardi."
            if row["qualifiers"].get("claim") != expected_claim:
                raise ValueError(f"unexpected prior claim: {statement_id}")
            row["qualifiers"]["claim"] = claim
            changed.append(statement_id)
    if len(changed) != 12:
        raise ValueError(f"expected 12 statements to repair, found {len(changed)}")
    content = write_jsonl(rows)
    backup = path.with_name(path.name + ".bak-s2-handoff-rosa-letter-claim-fix-20261010")
    if backup.exists():
        raise SystemExit(f"repair backup already exists: {backup.name}")
    original = path.read_bytes()
    backup.write_bytes(original)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
        stream.write(content)
        temp_path = Path(stream.name)
    try:
        os.replace(temp_path, path)
    except Exception:
        path.write_bytes(original)
        raise
    finally:
        if temp_path.exists():
            temp_path.unlink()
    print(json.dumps({"mode": "repair-applied-claims", "updated_statements": changed, "backup": backup.name, "output_sha256": sha256(path)}, ensure_ascii=True, indent=2))


def source_segment(spec: dict, segment_rows: dict[str, dict]) -> tuple[list[str], str]:
    row = segment_rows[spec["segment_id"]]
    path = SOURCES / spec["source_file"]
    lines = path.read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines[row["line_start"] - 1 : row["line_end"]])
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if digest != row["sha256"]:
        raise ValueError(f"source segment hash mismatch: {spec['segment_id']}")
    if not (row["line_start"] <= spec["line"] <= row["line_end"]):
        raise ValueError(f"source line outside segment: {spec['statement_id']}")
    return lines, text


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="write the reviewed changes")
    mode.add_argument("--repair-applied-claims", action="store_true", help="repair duplicate claims in an already applied batch")
    args = parser.parse_args()

    if args.repair_applied_claims:
        repair_applied_claims()
        return

    for name, expected in EXPECTED_HASHES.items():
        actual = sha256(TABLES / name)
        if actual != expected:
            raise SystemExit(f"precondition failed: {name} SHA-256 {actual} != {expected}")

    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    statement_path = TABLES / "book-statements.jsonl"
    candidate_fields, candidates = read_csv(candidate_path)
    mention_fields, mentions = read_csv(mention_path)
    statements = read_jsonl(statement_path)
    segment_rows = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}

    if candidates[-1]["candidate_id"] != "cand-11570":
        raise ValueError("unexpected candidate-table tail")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    statement_by_id = {row["statement_id"]: row for row in statements}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(candidate_by_id) != len(candidates) or len(statement_by_id) != len(statements) or len(mention_by_id) != len(mentions):
        raise ValueError("duplicate natural key in an input table")

    planned_candidates: list[dict[str, str]] = []
    planned_mentions: list[dict[str, str]] = []
    planned_relations: list[dict] = []
    updated_citations: list[dict] = []
    relation_statements: list[dict] = []
    citation_ids = {spec["statement_id"] for spec in SPECS}

    for spec in SPECS:
        old = statement_by_id.get(spec["statement_id"])
        if old is None or old["predicate"] != "footnote_citation_to_letter":
            raise ValueError(f"statement state changed: {spec['statement_id']}")
        if old["subject_candidate_id"] != "cand-2236" or old["object_candidate_id"] not in candidate_by_id:
            raise ValueError(f"unexpected citation endpoints: {spec['statement_id']}")
        if old["qualifiers"].get("relation_candidate") is True:
            raise ValueError(f"statement already classified: {spec['statement_id']}")

        source_lines, segment_text = source_segment(spec, segment_rows)
        line_quote = source_lines[spec["line"] - 1]
        if spec["surface"]:
            start = segment_text.find(spec["surface"])
            if start < 0 or segment_text.find(spec["surface"], start + 1) >= 0:
                raise ValueError(f"source surface missing or ambiguous: {spec['statement_id']}")
            end = start + len(spec["surface"])
        else:
            start = end = None
        q = old["qualifiers"]
        if q.get("source_line_start") != spec["line"] or q.get("source_line_end") != spec["line"]:
            raise ValueError(f"source line qualifier changed: {spec['statement_id']}")
        if not all(linked_id in statement_by_id for linked_id in spec["linked"]):
            raise ValueError(f"missing linked body statement: {spec['statement_id']}")
        if spec["candidate_id"]:
            if spec["candidate_id"] in candidate_by_id:
                raise ValueError(f"candidate id already exists: {spec['candidate_id']}")
            mention_id = {
                "cand-11571": "m-chp5-letter-16600402-01",
                "cand-11572": "m-chp5-letter-16661009-01",
                "cand-11573": "m-chp5-letter-16510424-01",
                "cand-11574": "m-chp5-letter-16510512-01",
                "cand-11575": "m-chp5-letter-16620513-01",
                "cand-11576": "m-chp5-letter-16640521-01",
            }[spec["candidate_id"]]
            if mention_id in mention_by_id:
                raise ValueError(f"mention id already exists: {mention_id}")
            ref = f"{spec['segment_id']}#L{spec['line']}"
            planned_candidates.append({
                "candidate_id": spec["candidate_id"],
                "index_entry_id": "",
                "canonical_name": spec["name"],
                "index_page_range": "",
                "suggested_type": "archive",
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": spec["detail"],
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": ref,
            })
            planned_mentions.append({
                "mention_id": mention_id,
                "segment_id": spec["segment_id"],
                "candidate_id": spec["candidate_id"],
                "surface_form": spec["surface"],
                "start_char": str(start),
                "end_char": str(end),
                "note": "A specific letter identified by Haskell; retain the printed/OCR surface and keep the publication locator separate.",
            })

            for role, obj in (("authored-by", spec["author"]), ("addressed-to", spec["recipient"])):
                relation_id = f"st-chp5-l{spec['line']}-letter-{role}"
                if relation_id in statement_by_id:
                    raise ValueError(f"statement id already exists: {relation_id}")
                if obj not in candidate_by_id:
                    raise ValueError(f"missing relation endpoint: {obj}")
                relation_predicate = "authored_by" if role == "authored-by" else "addressed_to"
                role_claim = (
                    f"Haskell identifies the letter dated {spec['date']} as authored by Salvator Rosa."
                    if role == "authored-by"
                    else f"Haskell's text identifies the letter dated {spec['date']} as addressed to G. B. Ricciardi."
                )
                context_note = " The author/recipient is supplied by the linked body passage where not explicit in the note."
                relation_statements.append({
                    "statement_id": relation_id,
                    "segment_id": spec["segment_id"],
                    "subject_candidate_id": spec["candidate_id"],
                    "object_candidate_id": obj,
                    "predicate": relation_predicate,
                    "qualifiers": {
                        "source_line_start": spec["line"],
                        "source_line_end": spec["line"],
                        "claim": role_claim,
                        "speaker": "Haskell, footnote and linked body context",
                        "text_layer": "reported correspondence",
                        "qualification": "The underlying letter and cited edition were not independently examined." + context_note,
                        "relation_candidate": True,
                        "linked_body_statement_ids": spec["linked"],
                        "cited_material_not_independently_consulted": True,
                        "publication_candidate_id": spec["publication"],
                        "page": spec["page"],
                        "date": spec["date"],
                    },
                    "original_quote": line_quote,
                    "origin": "book",
                    "source_file": f"02-sources/02-Markdown/{spec['source_file']}",
                })

        citation = dict(old)
        citation_q = dict(q)
        citation["predicate"] = "footnote_citation"
        citation["subject_candidate_id"] = "cand-2962"
        citation["object_candidate_id"] = spec["candidate_id"] or spec["publication"]
        citation_q["relation_candidate"] = True
        citation_q.pop("citation_candidate_id", None)
        if spec["candidate_id"]:
            citation_q["publication_candidate_id"] = spec["publication"]
            citation_q["author_candidate_id"] = spec["author"]
            citation_q["recipient_candidate_id"] = spec["recipient"]
            citation_q["date"] = spec["date"]
            citation_q.pop("letter_date", None)
        else:
            citation_q.pop("publication_candidate_id", None)
        citation["qualifiers"] = citation_q
        updated_citations.append(citation)
        planned_relations.append({
            "statement_id": spec["statement_id"],
            "target": citation["object_candidate_id"],
            "role": spec["citation_role"],
            "source_line": spec["line"],
            "mention_span": [start, end] if start is not None else None,
        })

    # Preserve row order for existing natural keys, append only the new rows.
    updated_statement_map = {row["statement_id"]: row for row in updated_citations}
    new_statements = [updated_statement_map.get(row["statement_id"], row) for row in statements]
    new_statements.extend(relation_statements)
    new_candidates = candidates + planned_candidates
    new_mentions = mentions + planned_mentions

    outputs = {
        candidate_path: write_csv(candidate_path, candidate_fields, new_candidates),
        mention_path: write_csv(mention_path, mention_fields, new_mentions),
        statement_path: write_jsonl(new_statements),
    }
    report = {
        "mode": "apply" if args.apply else "dry-run",
        "new_candidates": [row["candidate_id"] for row in planned_candidates],
        "new_mentions": [
            {"id": row["mention_id"], "surface": row["surface_form"], "span": [int(row["start_char"]), int(row["end_char"])]}
            for row in planned_mentions
        ],
        "updated_citations": planned_relations,
        "new_relation_candidates": [row["statement_id"] for row in relation_statements],
        "counts_after": {
            "candidates": len(new_candidates),
            "mentions": len(new_mentions),
            "statements": len(new_statements),
            "explicit_relation_candidates": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in new_statements),
            "two_endpoint_explicit_candidates": sum(
                int(
                    row.get("qualifiers", {}).get("relation_candidate") is True
                    and bool(row.get("subject_candidate_id"))
                    and bool(row.get("object_candidate_id"))
                )
                for row in new_statements
            ),
        },
    }

    if args.apply:
        backups: dict[Path, bytes] = {}
        temp_paths: list[tuple[Path, Path]] = []
        try:
            for path, content in outputs.items():
                backup = path.with_name(path.name + BACKUP_SUFFIX)
                if backup.exists():
                    raise ValueError(f"backup already exists: {backup.name}")
                backups[path] = path.read_bytes()
                backup.write_bytes(backups[path])
                with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
                    stream.write(content)
                    temp_paths.append((path, Path(stream.name)))
            for path, temp_path in temp_paths:
                os.replace(temp_path, path)
            report["backups"] = {path.name: path.name + BACKUP_SUFFIX for path in outputs}
            report["output_sha256"] = {path.name: sha256(path) for path in outputs}
        except Exception:
            for path, original in backups.items():
                path.write_bytes(original)
            raise
        finally:
            for _, temp_path in temp_paths:
                if temp_path.exists():
                    temp_path.unlink()

    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
