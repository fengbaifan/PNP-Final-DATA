from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
BACKUP_STATEMENTS = TABLES / "book-statements.jsonl.bak-s2-chp1-sec-ii-l155-239-20261010"
BACKUP_MENTIONS = TABLES / "mentions.csv.bak-s2-chp1-sec-ii-l155-239-20261010"
SOURCE_FILE = "02-sources/02-Markdown/01_CHP-1.md"
SEGMENT_FILE = "02-sources/02-Markdown/01_CHP-1_sec_ii.md"
SEGMENT_ID_FOR_NOTES = "chp-1:01_CHP-1_sec_ii:l168-239"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "fdf806da9f62574b6a377c299342de23e7b1444478b61942eb746d547eec19d2",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SEGMENT_FILE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    SOURCE_FILE: "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
}

DECISIONS = {
    "st-chp1-secii-l927-943-03": (
        True,
        "Haskell reports Rosa's refusal of advance deposits and quotes the identified 1 April 1666 letter. "
        "The source supports a relation candidate between Rosa and the letter; the claim remains attributed, "
        "and the letter's archival identity is not independently verified here.",
    ),
    "st-chp1-secii-l959-970-05": (
        False,
        "Baldinucci's quoted appraisal concerns Rosa, while Haskell separately says Rosa had no real followers. "
        "The person endpoints are the evaluator and subject, not a controlled historical relation; preserve the "
        "attribution and connect the citation to the volume-level archive candidate separately.",
    ),
    "st-chp1-secii-l971-973-06": (
        False,
        "The note records one De Rosis letter to Ruffo and a separate Baldinucci citation. Its person-to-person "
        "endpoints do not establish an ongoing corresponded_with relation. The letter's author/addressee roles "
        "and both book citations are represented by separate source-attributed statements below.",
    ),
    "st-chp1-secii-l974-980-07": (
        False,
        "Haskell presents Ferri and Luti as qualified parallels to Rosa; the Ferri/Ruffo endpoints belong to one "
        "cited letter, not an established long-term corresponded_with relation. Preserve the comparison and "
        "record the letter's author/addressee and cited publications separately.",
    ),
}

NEW_MENTIONS = [
    {
        "mention_id": "m-chp1-secii-p23-n2-baldinucci-vol6-p579",
        "segment_id": SEGMENT_ID_FOR_NOTES,
        "candidate_id": "cand-4846",
        "surface_form": "VI, 1728, p. 579.",
        "start_char": 9521,
        "end_char": 9538,
        "note": "Volume VI (1728), page 579 locator following the existing Baldinucci person mention; the cited passage was not independently consulted.",
    },
    {
        "mention_id": "m-chp1-secii-p23-n3-pascoli-vol1-p233",
        "segment_id": SEGMENT_ID_FOR_NOTES,
        "candidate_id": "cand-4834",
        "surface_form": "I, p. 233",
        "start_char": 10039,
        "end_char": 10048,
        "note": "Volume I, page 233 locator after the Pascoli person mention; the cited passage was not independently consulted.",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def flag(row: dict):
    return row.get("qualifiers", {}).get("relation_candidate")


def bilateral(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def counts(rows: list[dict]) -> dict[str, int]:
    return {
        "statements": len(rows),
        "relation_true": sum(flag(row) is True for row in rows),
        "relation_false": sum(flag(row) is False for row in rows),
        "true_bilateral": sum(flag(row) is True and bilateral(row) for row in rows),
        "true_open": sum(flag(row) is True and not bilateral(row) for row in rows),
        "false_bilateral": sum(flag(row) is False and bilateral(row) for row in rows),
        "unclassified_bilateral": sum(bilateral(row) and flag(row) is None for row in rows),
        "cites": sum(row.get("predicate") == "cites" for row in rows),
    }


def citation_statement(
    statement_id: str,
    object_id: str,
    start: int,
    end: int,
    claim: str,
    locator: str,
    citation_candidate_id: str,
    publication_candidate_id: str,
    mentioned_candidate_ids: list[str],
    quote: str,
    marker: int,
) -> dict:
    citation = {
        "source_candidate_id": citation_candidate_id,
        "publication_candidate_id": publication_candidate_id,
        "locator": locator,
    }
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID_FOR_NOTES,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": object_id,
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": start,
            "source_line_end": end,
            "claim": claim,
            "speaker": f"Haskell footnote {marker}",
            "text_layer": "bibliographic citation to publication",
            "footnote_marker": marker,
            "citation_candidate_id": citation_candidate_id,
            "citation_publication_candidate_id": publication_candidate_id,
            "citation_locator": locator,
            "citations": [citation],
            "mentioned_candidate_ids": mentioned_candidate_ids,
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
            "relation_candidate_note": "The footnote explicitly points to this cited publication/source at the stated locator. This records a citation pointer only; the cited material was not independently consulted.",
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def role_statement(
    statement_id: str,
    archive_id: str,
    person_id: str,
    relation_type: str,
    start: int,
    end: int,
    claim: str,
    quote: str,
    note: str,
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID_FOR_NOTES,
        "subject_candidate_id": archive_id,
        "object_candidate_id": person_id,
        "predicate": relation_type,
        "qualifiers": {
            "source_line_start": start,
            "source_line_end": end,
            "claim": claim,
            "speaker": "Haskell footnote",
            "text_layer": "bibliographic note reporting document roles",
            "qualification": "A single dated letter is represented through its archive/document candidate; no ongoing correspondence is inferred.",
            "relation_candidate": True,
            "relation_candidate_note": note,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def preflight() -> tuple[list[dict], list[dict], dict, list[dict], list[str]]:
    for relative, expected_hash in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.is_file(), f"missing input: {relative}")
        require(sha256(path) == expected_hash, f"input hash changed: {relative}")

    statement_rows = load_jsonl(STATEMENTS)
    by_id = {row.get("statement_id"): row for row in statement_rows}
    require(len(by_id) == len(statement_rows), "statement IDs are not unique")
    require(set(DECISIONS) <= set(by_id), "one or more target statements are missing")

    targets = {
        "st-chp1-secii-l927-943-03": ("chp-1:01_CHP-1_sec_ii:l155-159", "cand-3099", "cand-2965", "rosa_asserted_artistic_independence_and_inspiration", 927, 943, "I do not paint to enrich myself"),
        "st-chp1-secii-l959-970-05": ("chp-1:01_CHP-1_sec_ii:l161-166", "cand-3099", "cand-3031", "rosa_integrity_legacy_and_patronage_independence", 959, 970, "Baldinucci made the point clearly enough"),
        "st-chp1-secii-l971-973-06": (SEGMENT_ID_FOR_NOTES, "cand-3058", "cand-3002", "de_rosis_letter_and_baldinucci_citation", 971, 973, "Letter from Giuseppe de Rosis"),
        "st-chp1-secii-l974-980-07": (SEGMENT_ID_FOR_NOTES, "cand-3021", "cand-3002", "ferri_and_luti_as_partial_patronage_parallels", 974, 980, "Ciro Ferri wrote to Don Antonio Ruffo"),
    }
    for statement_id, (segment_id, subject, object_id, predicate, start, end, quote_anchor) in targets.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers", {})
        require(row.get("segment_id") == segment_id, f"segment changed for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_id,
                f"endpoint changed for {statement_id}")
        require(row.get("predicate") == predicate, f"predicate changed for {statement_id}")
        require(qualifiers.get("source_line_start") == start and qualifiers.get("source_line_end") == end,
                f"source line anchor changed for {statement_id}")
        require(flag(row) is None, f"already classified: {statement_id}")
        require(quote_anchor in row.get("original_quote", ""), f"quote anchor changed for {statement_id}")

    coverage = list(csv.DictReader((TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="")))
    required_segments = {value[0] for value in targets.values()}
    for segment_id in required_segments:
        matches = [row for row in coverage if row.get("segment_id") == segment_id]
        require(len(matches) == 1 and matches[0].get("disposition") == "reviewed"
                and matches[0].get("migration_status") == "complete", f"coverage incomplete for {segment_id}")

    candidates = list(csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="")))
    by_candidate = {row.get("candidate_id"): row for row in candidates}
    required_candidate_types = {
        "cand-2962": "archive", "cand-3552": "archive", "cand-3555": "archive",
        "cand-4846": "archive", "cand-3560": "archive", "cand-4834": "archive",
        "cand-3058": "person", "cand-3002": "person", "cand-3021": "person",
    }
    for candidate_id, expected_type in required_candidate_types.items():
        require(candidate_id in by_candidate, f"missing candidate {candidate_id}")
        require(by_candidate[candidate_id].get("suggested_type") == expected_type,
                f"candidate type mismatch for {candidate_id}")

    mentions_text = MENTIONS.read_text(encoding="utf-8-sig")
    mention_has_bom = MENTIONS.read_bytes().startswith(b"\xef\xbb\xbf")
    mention_reader = csv.DictReader(io.StringIO(mentions_text, newline=""))
    mention_fieldnames = mention_reader.fieldnames
    require(mention_fieldnames == ["mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note"],
            "mention table schema changed")
    mention_rows = list(mention_reader)
    mention_ids = {row.get("mention_id") for row in mention_rows}
    require(len(mention_ids) == len(mention_rows), "mention IDs are not unique")
    require(not any(row["mention_id"] in mention_ids for row in NEW_MENTIONS), "new mention ID already exists")

    section_lines = (ROOT / SEGMENT_FILE).read_text(encoding="utf-8").splitlines(keepends=True)
    segment_text = "".join(section_lines[167:239])
    for mention in NEW_MENTIONS:
        start, end = mention["start_char"], mention["end_char"]
        require(segment_text[start:end] == mention["surface_form"],
                f"mention span mismatch for {mention['mention_id']}")
        require(mention["candidate_id"] in by_candidate, f"mention candidate missing for {mention['mention_id']}")
        require(mention["segment_id"] == SEGMENT_ID_FOR_NOTES, f"mention segment mismatch for {mention['mention_id']}")

    source_lines = (ROOT / SOURCE_FILE).read_text(encoding="utf-8").splitlines()
    anchors = {
        927: "But Salvator Rosa was engaged in a yet more serious battle.",
        963: "conduct. When summing up his career, Baldinucci made the point clearly enough:",
        971: "1 Letter from Giuseppe de Rosis to Don. Antonio Ruffo",
        973: "2 Baldinucci, VI, 1728, p. 579.",
        974: "3 Two other artists show some signs ofhaving rebelled",
        979: "mai protezioni de' Grandi, e siccome egli andava poco da loro, essi di rado givan da lui.",
    }
    for line_number, phrase in anchors.items():
        require(phrase in source_lines[line_number - 1], f"source anchor changed at L{line_number}")

    schema = (ROOT / ".agents/skills/ingest/references/relation-types.yml").read_text(encoding="utf-8")
    for relation_type in ("cites", "authored_by", "addressed_to"):
        require(f"  - {relation_type}\n" in schema, f"relation type not in controlled schema: {relation_type}")

    before = counts(statement_rows)
    require(before == {
        "statements": 12692,
        "relation_true": 3882,
        "relation_false": 1801,
        "true_bilateral": 3855,
        "true_open": 27,
        "false_bilateral": 436,
        "unclassified_bilateral": 4198,
        "cites": 135,
    }, "current statement totals changed")
    return statement_rows, mention_rows, before, mention_fieldnames, mention_has_bom


def build_new_statements(source_lines: list[str]) -> list[dict]:
    quote_971_972 = "\n".join(source_lines[970:972])
    quote_973 = source_lines[972]
    quote_974_978 = "\n".join(source_lines[973:978])
    quote_978_980 = "\n".join(source_lines[977:980])
    return [
        citation_statement(
            "st-chp1-secii-l971-n1-cites-ruffo-correspondence-p172", "cand-3555", 971, 972,
            "Haskell's footnote cites the published 22 September 1663 letter from Giuseppe de Rosis to Don Antonio Ruffo, at page 172.",
            "V. Ruffo, p. 172", "cand-3552", "cand-3555",
            ["cand-3058", "cand-3002", "cand-3552", "cand-3555"], quote_971_972, 1,
        ),
        citation_statement(
            "st-chp1-secii-l973-n2-cites-baldinucci-vol6-p579", "cand-4846", 973, 973,
            "Haskell's footnote cites Baldinucci, volume VI (1728), page 579, for the quoted appraisal of Rosa.",
            "Baldinucci, VI, 1728, p. 579", "cand-4846", "cand-4846",
            ["cand-3031", "cand-4846"], quote_973, 2,
        ),
        citation_statement(
            "st-chp1-secii-l974-n3-cites-ruffo-correspondence-p298", "cand-3555", 974, 978,
            "Haskell's footnote cites Ciro Ferri's 19 September 1672 letter to Don Antonio Ruffo through the cited correspondence publication, page 298.",
            "Ruffo, p. 298", "cand-3560", "cand-3555",
            ["cand-3021", "cand-3002", "cand-3560", "cand-3555"], quote_974_978, 3,
        ),
        citation_statement(
            "st-chp1-secii-l978-980-n3-cites-pascoli-vol1-p233", "cand-4834", 978, 980,
            "Haskell's footnote cites Pascoli, volume I, page 233, for the reported view attributed to Benedetto Luti.",
            "Pascoli, I, p. 233", "cand-4834", "cand-4834",
            ["cand-1842", "cand-3004", "cand-4834"], quote_978_980, 3,
        ),
        role_statement(
            "st-chp1-secii-l971-n1-derosis-letter-authored-by", "cand-3552", "cand-3058", "authored_by", 971, 972,
            "The cited 22 September 1663 letter is identified as written by Giuseppe de Rosis.", quote_971_972,
            "The note explicitly names the letter's author; preserve Haskell's citation chain and do not infer additional correspondence.",
        ),
        role_statement(
            "st-chp1-secii-l971-n1-derosis-letter-addressed-to", "cand-3552", "cand-3002", "addressed_to", 971, 972,
            "The cited 22 September 1663 letter is addressed to Don Antonio Ruffo.", quote_971_972,
            "The note explicitly names the addressee; this is a document role, not evidence of an ongoing person-to-person correspondence.",
        ),
        role_statement(
            "st-chp1-secii-l974-n3-ferri-letter-authored-by", "cand-3560", "cand-3021", "authored_by", 974, 978,
            "The cited letter of 19 September 1672 is identified as written by Ciro Ferri.", quote_974_978,
            "The note explicitly names Ferri as letter author; preserve the quoted Italian and Haskell's qualification of the comparison.",
        ),
        role_statement(
            "st-chp1-secii-l974-n3-ferri-letter-addressed-to", "cand-3560", "cand-3002", "addressed_to", 974, 978,
            "The cited letter of 19 September 1672 is addressed to Don Antonio Ruffo.", quote_974_978,
            "The note explicitly names the addressee; this is a document role, not evidence of an ongoing person-to-person correspondence.",
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify chapter 1 section ii L155-239 and normalize its cited-letter roles.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted statement and mention updates")
    args = parser.parse_args()

    rows, mention_rows, before, mention_fieldnames, mention_has_bom = preflight()
    updated = [dict(row) for row in rows]
    by_id = {row["statement_id"]: row for row in updated}
    for statement_id, (value, note) in DECISIONS.items():
        row = by_id[statement_id]
        row["qualifiers"] = dict(row.get("qualifiers", {}))
        row["qualifiers"]["relation_candidate"] = value
        row["qualifiers"]["relation_candidate_note"] = note

    source_lines = (ROOT / SOURCE_FILE).read_text(encoding="utf-8").splitlines()
    additions = build_new_statements(source_lines)
    existing_ids = {row["statement_id"] for row in updated}
    addition_ids = [row["statement_id"] for row in additions]
    require(len(addition_ids) == len(set(addition_ids)), "new statement IDs are not unique")
    require(not (set(addition_ids) & existing_ids), "a new statement ID already exists")
    updated.extend(additions)

    updated_mentions = [dict(row) for row in mention_rows] + [dict(row) for row in NEW_MENTIONS]
    after = counts(updated)
    print("PREVIEW: chapter 1 section ii L155-239")
    for statement_id, (value, _) in DECISIONS.items():
        print(f"  {statement_id}: relation_candidate={value}")
    print(f"  add {len(additions)} citation/document-role statements and {len(NEW_MENTIONS)} precise archive mentions")
    print("  counts before:", json.dumps(before, sort_keys=True))
    print("  counts after: ", json.dumps(after, sort_keys=True))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the reviewed changes.")
        return

    require(not BACKUP_STATEMENTS.exists(), f"backup already exists: {BACKUP_STATEMENTS.relative_to(ROOT)}")
    require(not BACKUP_MENTIONS.exists(), f"backup already exists: {BACKUP_MENTIONS.relative_to(ROOT)}")
    shutil.copy2(STATEMENTS, BACKUP_STATEMENTS)
    shutil.copy2(MENTIONS, BACKUP_MENTIONS)

    statement_payload = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated) + "\n"
    mention_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(mention_buffer, fieldnames=mention_fieldnames, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(updated_mentions)
    mention_payload = mention_buffer.getvalue().encode("utf-8-sig" if mention_has_bom else "utf-8")

    temporary_paths: list[Path] = []
    try:
        for target_path, payload in ((STATEMENTS, statement_payload.encode("utf-8")), (MENTIONS, mention_payload)):
            with tempfile.NamedTemporaryFile("wb", dir=target_path.parent, delete=False) as handle:
                temp_path = Path(handle.name)
                temporary_paths.append(temp_path)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        os.replace(temporary_paths[0], STATEMENTS)
        os.replace(temporary_paths[1], MENTIONS)
    finally:
        for path in temporary_paths:
            if path.exists():
                path.unlink()

    print(f"APPLIED; statement backup: {BACKUP_STATEMENTS.relative_to(ROOT)}")
    print(f"APPLIED; mention backup: {BACKUP_MENTIONS.relative_to(ROOT)}")
    print(f"new statement SHA-256: {sha256(STATEMENTS)}")
    print(f"new mention SHA-256: {sha256(MENTIONS)}")


if __name__ == "__main__":
    main()
