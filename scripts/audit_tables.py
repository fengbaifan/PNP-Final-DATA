#!/usr/bin/env python3
"""Validate S0-S6 table keys, references, evidence and source anchors."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parents[1]
TABLES = BASE / "04-knowledge" / "tables"
UNIT_TYPES = {"persons": "person", "families": "family", "institutions": "institution", "places": "place",
              "works": "work", "archives": "archive", "terms": "term", "procedures": "procedure", "events": "event"}
EVIDENCE_STATES = {"unverified", "source_backed", "partially_verified", "externally_verified", "model_supported"}
ALIGNMENT_STATES = {"same", "new", "conflict", "excluded", "undecided"}
RELATION_STATES = {"formal", "pending", "rejected"}
MENTION_COLUMNS = {"mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char"}
COVERAGE_COLUMNS = {"chapter", "segment_id", "disposition", "migration_status", "source_line_ranges", "note"}
STATEMENT_FIELDS = {
    "statement_id", "segment_id", "subject_candidate_id", "object_candidate_id",
    "predicate", "qualifiers", "original_quote", "origin", "source_file",
}
CSV_REQUIRED_COLUMNS = {
    "sources.csv": {"source_id", "kind", "label", "citation"},
    "ku-manifest.csv": {"ku_id", "type", "canonical_name", "name_en", "card_path"},
    "entity-candidates.csv": {"candidate_id", "canonical_name", "status", "candidate_origin"},
    "alignment.csv": {"alignment_id", "candidate_id", "decision", "process_ref"},
    "relations.csv": {"relation_id", "subject_ku_id", "object_ku_id", "predicate", "origin", "status", "source_file", "source_span"},
}
KU_TYPES = {"person", "family", "institution", "place", "work", "archive", "term", "procedure", "event"}
ORIGINS = {"book", "external", "inferred"}
RELATION_ORIGINS = ORIGINS | {"explicit"}


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_columns(path: Path) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return set(next(csv.reader(handle), []))


def csv_row_shape_errors(filename: str, rows: list[dict]) -> list[str]:
    errors = []
    for line, row in enumerate(rows, 2):
        if None in row:
            errors.append(f"{filename}:{line}: row has {len(row[None])} extra CSV field(s)")
        missing = [key for key, value in row.items() if key is not None and value is None]
        if missing:
            errors.append(f"{filename}:{line}: row has missing field(s): {', '.join(missing)}")
    return errors


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(path)
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip():
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path.name}:{number}: each record must be an object")
            records.append(value)
    return records


def duplicates(values: list[str]) -> set[str]:
    counts = Counter(value for value in values if value)
    return {value for value, count in counts.items() if count > 1}


def independently_parse_card_tables(body: str, ku_id: str) -> dict[str, dict]:
    """Re-scan raw Markdown independently of the extractor/renderer helper."""
    lines = body.splitlines()
    heading_stack: dict[int, str] = {}
    section = ""
    ordinals: Counter[str] = Counter()
    tables: dict[str, dict] = {}
    i = 0

    def cells(line: str) -> list[str]:
        value = line.strip()
        if value.startswith("|"): value = value[1:]
        if value.endswith("|"): value = value[:-1]
        result, token, escaped = [], [], False
        for char in value:
            if char == "|" and not escaped:
                result.append("".join(token).strip())
                token = []
            else:
                token.append(char)
            if char == "\\" and not escaped: escaped = True
            else: escaped = False
        result.append("".join(token).strip())
        return result

    while i < len(lines):
        heading = re.match(r"^(#{2,6})\s+(.+?)\s*#*\s*$", lines[i])
        if heading:
            level = len(heading.group(1))
            heading_stack[level] = heading.group(2).strip()
            heading_stack = {key: value for key, value in heading_stack.items() if key <= level}
            section = " / ".join(heading_stack[key] for key in sorted(heading_stack))
        if not lines[i].strip().startswith("|"):
            i += 1
            continue
        raw = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            raw.append(lines[i].strip())
            i += 1
        if len(raw) < 2:
            continue
        has_header = bool(re.fullmatch(r"\|?[\s:|\-]+\|?", raw[1]))
        header = cells(raw[0]) if has_header else []
        if header == ["方向与关系", "关联知识元", "语境与证据"] or section.split(" / ")[-1] in {"关系", "关系记录"}:
            continue
        data = [cells(line) for line in raw[2:] if not re.fullmatch(r"\|?[\s:|\-]+\|?", line)] if has_header else [cells(line) for line in raw]
        if not data:
            continue
        ordinals[section] += 1
        table_key = f"{ku_id}|{section}|{ordinals[section]}|{'|'.join(header)}"
        table_id = "tbl-" + hashlib.sha256(table_key.encode("utf-8")).hexdigest()[:16]
        tables[table_id] = {"section": section, "header": header, "has_header": has_header, "rows": data}
    return tables


def audit_s2_artifacts(
    table_dir: Path,
    candidate_ids: set[str],
    segment_ids: set[str],
    strict_stage: bool = False,
    segment_texts: dict[str, str] | None = None,
    source_root: Path | None = None,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    missing = [name for name in ("s2-coverage.csv", "mentions.csv", "book-statements.jsonl") if not (table_dir / name).exists()]
    if missing:
        message = f"S2 artifacts not yet migrated: {', '.join(missing)}"
        warnings.append(message)
        if strict_stage:
            errors.append(f"S2 artifacts required for release: {', '.join(missing)}")

    coverage_rows: list[dict] = []
    coverage_path = table_dir / "s2-coverage.csv"
    if coverage_path.exists():
        try:
            coverage_rows = read_csv(coverage_path)
            with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
                columns = set(next(csv.reader(handle), []))
            absent = sorted(COVERAGE_COLUMNS - columns)
            if absent:
                errors.append(f"s2-coverage.csv: missing columns {', '.join(absent)}")
            keys = [f"{row.get('chapter', '')}|{row.get('segment_id', '')}" for row in coverage_rows]
            if any(key.startswith("|") or key.endswith("|") for key in keys) or duplicates(keys):
                errors.append("s2-coverage.csv has duplicate/missing chapter+segment key")
            for row in coverage_rows:
                chapter = row.get("chapter", "")
                segment_id = row.get("segment_id", "")
                disposition = row.get("disposition", "")
                migration_status = row.get("migration_status", "")
                if not segment_id or segment_id not in segment_ids:
                    errors.append(f"s2-coverage.csv: unknown or empty segment_id {segment_id!r}")
                if not segment_id.startswith(f"{chapter}:"):
                    errors.append(f"s2-coverage.csv: segment {segment_id!r} does not belong to chapter {chapter!r}")
                if disposition not in {"reviewed", "excluded"}:
                    errors.append(f"s2-coverage.csv: invalid disposition {disposition!r} for {segment_id}")
                if migration_status not in {"pending", "partial", "complete"}:
                    errors.append(f"s2-coverage.csv: invalid migration_status {migration_status!r} for {segment_id}")
                if disposition == "excluded" and migration_status != "complete":
                    errors.append(f"s2-coverage.csv: excluded segment must be migration_status=complete: {segment_id}")
                if strict_stage and disposition == "reviewed" and migration_status != "complete":
                    errors.append(f"s2-coverage.csv: {segment_id} migration is {migration_status or 'unset'}, expected complete")
                if disposition == "reviewed" and not row.get("source_line_ranges", "").strip():
                    errors.append(f"s2-coverage.csv: reviewed segment lacks source_line_ranges: {segment_id}")
                if disposition == "excluded" and not row.get("note", "").strip():
                    errors.append(f"s2-coverage.csv: excluded segment lacks note: {segment_id}")
            chapters = {row.get("chapter", "") for row in coverage_rows if row.get("chapter")}
            for chapter in chapters:
                expected = {sid for sid in segment_ids if sid.startswith(f"{chapter}:")}
                actual = {row.get("segment_id", "") for row in coverage_rows if row.get("chapter") == chapter}
                if expected != actual:
                    errors.append(f"s2-coverage.csv: {chapter} coverage incomplete ({len(actual & expected)}/{len(expected)} segments)")
        except (OSError, ValueError, csv.Error) as exc:
            errors.append(f"s2-coverage.csv: {exc}")

    mentions: list[dict] = []
    mention_intervals: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    mentions_path = table_dir / "mentions.csv"
    if mentions_path.exists():
        try:
            mentions = read_csv(mentions_path)
            with mentions_path.open(encoding="utf-8-sig", newline="") as handle:
                columns = set(next(csv.reader(handle), []))
            absent = sorted(MENTION_COLUMNS - columns)
            if absent:
                errors.append(f"mentions.csv: missing columns {', '.join(absent)}")
            if any(not row.get("mention_id", "").strip() for row in mentions) or duplicates([row.get("mention_id", "") for row in mentions]):
                errors.append("mentions.csv has duplicate/missing mention_id")
            for row in mentions:
                mention_id = row.get("mention_id", "") or "<missing id>"
                if not row.get("segment_id") or row["segment_id"] not in segment_ids:
                    errors.append(f"{mention_id}: unknown or empty segment_id")
                if not row.get("candidate_id") or row["candidate_id"] not in candidate_ids:
                    errors.append(f"{mention_id}: unknown or empty candidate_id")
                if not row.get("surface_form", "").strip():
                    errors.append(f"{mention_id}: empty surface_form")
                try:
                    start_char, end_char = int(row.get("start_char", "")), int(row.get("end_char", ""))
                    if start_char < 0 or end_char <= start_char:
                        raise ValueError
                    segment_text = (segment_texts or {}).get(row.get("segment_id", ""))
                    if segment_text is not None and segment_text[start_char:end_char] != row.get("surface_form"):
                        errors.append(f"{mention_id}: surface_form does not match segment character offsets")
                    elif segment_text is not None and end_char > len(segment_text):
                        errors.append(f"{mention_id}: character offsets exceed segment text length")
                    mention_intervals[row.get("segment_id", "")].append((start_char, end_char, mention_id))
                except (TypeError, ValueError):
                    errors.append(f"{mention_id}: invalid start_char/end_char")
            for segment_id, intervals in mention_intervals.items():
                intervals.sort()
                for index, left in enumerate(intervals):
                    for right in intervals[index + 1:]:
                        if right[0] >= left[1]:
                            break
                        exact_duplicate = left[:2] == right[:2]
                        strictly_nested = (
                            (left[0] <= right[0] and right[1] <= left[1])
                            or (right[0] <= left[0] and left[1] <= right[1])
                        )
                        if exact_duplicate or not strictly_nested:
                            errors.append(
                                f"mentions.csv: duplicate or crossing mention offsets in {segment_id}: "
                                f"{left[2]} and {right[2]}"
                            )
        except (OSError, ValueError, csv.Error) as exc:
            errors.append(f"mentions.csv: {exc}")

    statements: list[dict] = []
    statements_path = table_dir / "book-statements.jsonl"
    if statements_path.exists():
        try:
            statements = read_jsonl(statements_path)
            if any(not row.get("statement_id", "").strip() for row in statements) or duplicates([row.get("statement_id", "") for row in statements]):
                errors.append("book-statements.jsonl has duplicate/missing statement_id")
            for row in statements:
                statement_id = row.get("statement_id", "") or "<missing id>"
                absent = sorted(STATEMENT_FIELDS - set(row))
                if absent:
                    errors.append(f"{statement_id}: missing fields {', '.join(absent)}")
                    continue
                if not row.get("segment_id") or row["segment_id"] not in segment_ids:
                    errors.append(f"{statement_id}: unknown or empty segment_id")
                for endpoint in ("subject_candidate_id", "object_candidate_id"):
                    candidate_id = row.get(endpoint)
                    if candidate_id is not None and candidate_id != "" and candidate_id not in candidate_ids:
                        errors.append(f"{statement_id}: unknown {endpoint} {candidate_id}")
                qualifiers = row.get("qualifiers")
                if not isinstance(qualifiers, dict):
                    errors.append(f"{statement_id}: qualifiers must be an object")
                if not isinstance(row.get("original_quote"), str) or not row["original_quote"].strip():
                    errors.append(f"{statement_id}: original_quote is empty or not a string")
                if row.get("origin") != "book":
                    errors.append(f"{statement_id}: origin must be 'book'")
                if not isinstance(row.get("predicate"), str) or not row["predicate"].strip():
                    errors.append(f"{statement_id}: predicate is empty or not a string")
                source_file = row.get("source_file", "")
                source_root = source_root or BASE
                allowed_root = source_root if source_root != BASE else BASE / "02-sources"
                try:
                    if not isinstance(source_file, str) or not source_file.strip():
                        raise ValueError("empty source_file")
                    source_path = (source_root / source_file).resolve()
                    source_path.relative_to(allowed_root.resolve())
                except (OSError, TypeError, ValueError):
                    source_path = None
                if source_path is None or not source_path.is_file():
                    errors.append(f"{statement_id}: source_file is missing, unresolved, or outside 02-sources")
                if isinstance(qualifiers, dict):
                    try:
                        line_start = int(qualifiers["source_line_start"])
                        line_end = int(qualifiers["source_line_end"])
                        if line_start < 1 or line_end < line_start:
                            raise ValueError
                    except (KeyError, TypeError, ValueError):
                        errors.append(f"{statement_id}: invalid source_line_start/source_line_end")
                    else:
                        coverage = next((item for item in coverage_rows if item.get("segment_id") == row.get("segment_id")), {})
                        covered_ranges = sorted(
                            (int(start), int(end))
                            for start, end in re.findall(r"L(\d+)-(\d+)", coverage.get("source_line_ranges", ""))
                        )
                        cursor = line_start
                        for start, end in covered_ranges:
                            if start <= cursor <= end:
                                cursor = end + 1
                            if cursor > line_end:
                                break
                        if cursor <= line_end:
                            errors.append(f"{statement_id}: source lines are outside S2 coverage for segment")
                        if source_path is not None and source_path.is_file():
                            source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
                            if line_end > len(source_lines):
                                errors.append(f"{statement_id}: source line range exceeds source file")
                            elif isinstance(row.get("original_quote"), str) and row["original_quote"].strip():
                                cited_text = "\n".join(source_lines[line_start - 1:line_end])
                                normalize = lambda value: " ".join(value.split())
                                if normalize(row["original_quote"]) not in normalize(cited_text):
                                    errors.append(f"{statement_id}: original_quote does not match cited source lines")
            statement_keys = []
            for row in statements:
                qualifiers = row.get("qualifiers")
                if not isinstance(qualifiers, dict):
                    continue
                claim = qualifiers.get("claim") or qualifiers.get("attribution") or row.get("original_quote", "")
                normalized_claim = " ".join(str(claim).split()).casefold()
                if normalized_claim:
                    statement_keys.append(f"{row.get('segment_id', '')}|{normalized_claim}")
            if duplicates(statement_keys):
                errors.append("book-statements.jsonl has duplicate segment_id + normalized claim natural key")
        except (OSError, ValueError) as exc:
            errors.append(f"book-statements.jsonl: {exc}")

    if not missing:
        incomplete_migrations = sum(row.get("disposition") == "reviewed" and row.get("migration_status") != "complete" for row in coverage_rows)
        if incomplete_migrations:
            warnings.append(f"S2 coverage is present, but {incomplete_migrations} reviewed segments are not fully migrated to mentions/statements")
        else:
            warnings.append("S2 segment dispositions and migrations are mechanically complete; semantic review quality still requires checking the linked processing record")
    return {
        "errors": errors, "warnings": warnings, "missing": missing,
        "coverage_records": coverage_rows,
        "coverage_rows": len(coverage_rows),
        "coverage_complete_rows": sum(row.get("disposition") == "reviewed" and row.get("migration_status") == "complete" for row in coverage_rows),
        "coverage_excluded_rows": sum(row.get("disposition") == "excluded" for row in coverage_rows),
        "mentions": len(mentions), "book_statements": len(statements),
    }


def audit_tables(strict_stage: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    ku_rows = read_csv(TABLES / "ku-manifest.csv")
    candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    alignment_rows = read_csv(TABLES / "alignment.csv")
    relation_rows = read_csv(TABLES / "relations.csv")
    source_rows = read_csv(TABLES / "sources.csv")
    for filename, rows in (
        ("ku-manifest.csv", ku_rows), ("entity-candidates.csv", candidate_rows),
        ("alignment.csv", alignment_rows), ("relations.csv", relation_rows),
        ("sources.csv", source_rows),
    ):
        errors.extend(csv_row_shape_errors(filename, rows))
    segment_rows = read_jsonl(TABLES / "segments.jsonl")
    enrichment_rows = read_jsonl(TABLES / "enrichment.jsonl")
    for filename, required in CSV_REQUIRED_COLUMNS.items():
        path = TABLES / filename
        absent = sorted(required - csv_columns(path))
        if absent:
            errors.append(f"{filename}: missing required columns {', '.join(absent)}")
    ku_ids = {row.get("ku_id", "") for row in ku_rows}
    candidate_ids = {row.get("candidate_id", "") for row in candidate_rows}
    source_ids = {row.get("source_id", "") for row in source_rows}
    for filename, rows, key in (("sources.csv", source_rows, "source_id"), ("ku-manifest.csv", ku_rows, "ku_id"),
                                ("entity-candidates.csv", candidate_rows, "candidate_id"), ("alignment.csv", alignment_rows, "alignment_id"),
                                ("relations.csv", relation_rows, "relation_id")):
        if any(not row.get(key, "").strip() for row in rows) or duplicates([row.get(key, "") for row in rows]):
            errors.append(f"{filename} has duplicate/missing {key}")
    for filename, rows, key in (("enrichment.jsonl", enrichment_rows, "enrichment_id"), ("segments.jsonl", segment_rows, "segment_id")):
        if any(not row.get(key, "").strip() for row in rows) or duplicates([row.get(key, "") for row in rows]):
            errors.append(f"{filename} has duplicate/missing {key}")
    if duplicates([row.get("index_entry_id", "") for row in candidate_rows]): errors.append("entity-candidates.csv has duplicate index_entry_id")
    non_index_candidate_keys = [
        "|".join((row.get("canonical_name", "").strip().casefold(), row.get("suggested_type", "").strip().casefold()))
        for row in candidate_rows if not row.get("index_entry_id") and row.get("suggested_type")
    ]
    if duplicates(non_index_candidate_keys):
        errors.append("entity-candidates.csv has duplicate non-index canonical_name + suggested_type natural key")
    for row in source_rows:
        if row.get("kind") not in {"book", "external"}:
            errors.append(f"{row.get('source_id')}: invalid source kind {row.get('kind')!r}")
        if not row.get("label", "").strip() or not row.get("citation", "").strip():
            errors.append(f"{row.get('source_id')}: source label/citation is required")
    for row in ku_rows:
        if row.get("type") not in KU_TYPES:
            errors.append(f"{row.get('ku_id')}: invalid KU type {row.get('type')!r}")
        if not row.get("canonical_name", "").strip() or not row.get("name_en", "").strip():
            errors.append(f"{row.get('ku_id')}: bilingual canonical names are required")
    for row in candidate_rows:
        status = row.get("status", "")
        if not row.get("canonical_name", "").strip():
            errors.append(f"{row.get('candidate_id')}: canonical_name is required")
        if status not in {"open", "excluded"}:
            errors.append(f"{row.get('candidate_id')}: invalid candidate status {status!r}")
        if status == "excluded" and not row.get("exclude_reason"):
            errors.append(f"{row.get('candidate_id')}: excluded candidate lacks reason")
        if not row.get("index_entry_id") and row.get("candidate_origin") == "accepted-ku" and not row.get("candidate_source_ref"):
            errors.append(f"{row.get('candidate_id')}: non-index candidate lacks source reference")
        if row.get("suggested_type") and row["suggested_type"] not in KU_TYPES:
            errors.append(f"{row.get('candidate_id')}: invalid suggested_type {row['suggested_type']!r}")
    segment_ids = {row.get("segment_id", "") for row in segment_rows}
    for row in segment_rows:
        if row.get("source_id") not in source_ids:
            errors.append(f"{row.get('segment_id')}: unknown source_id {row.get('source_id')!r}")
        for field in ("chapter", "section", "source_file", "sha256", "asset_sha256"):
            if not row.get(field):
                errors.append(f"{row.get('segment_id')}: required segment field {field} is empty")
        if row.get("release_excluded") is not True:
            errors.append(f"{row.get('segment_id')}: source segment must be marked release_excluded")
    for row in alignment_rows:
        if not row.get("candidate_id"):
            errors.append(f"{row.get('alignment_id')}: candidate_id is required")
        if row.get("decision") not in ALIGNMENT_STATES:
            errors.append(f"{row.get('alignment_id')}: invalid alignment decision {row.get('decision')!r}")
        if row.get("candidate_id") and row["candidate_id"] not in candidate_ids:
            errors.append(f"{row.get('alignment_id')}: unknown candidate_id {row['candidate_id']}")
        if row.get("ku_id") and row["ku_id"] not in ku_ids:
            errors.append(f"{row.get('alignment_id')}: unknown ku_id {row['ku_id']}")
        decision = row.get("decision")
        if decision in {"same", "new"} and not row.get("ku_id"):
            errors.append(f"{row.get('alignment_id')}: {decision} requires ku_id")
        if decision == "same" and not (row.get("external_source") and row.get("external_id")):
            errors.append(f"{row.get('alignment_id')}: same requires external_source and external_id")
        if decision in {"undecided", "excluded", "conflict"} and not (row.get("process_ref") or row.get("resolution_note")):
            errors.append(f"{row.get('alignment_id')}: {decision} requires process_ref or resolution_note")
    alignment_keys = [f"{r.get('candidate_id','')}|{r.get('external_source','')}" for r in alignment_rows]
    if duplicates(alignment_keys): errors.append("alignment.csv has duplicate candidate_id + external_source natural key")
    if not candidate_rows:
        errors.append("entity-candidates.csv is empty")
    enrichment_keys = []
    table_rows: dict[str, list[int]] = defaultdict(list)
    for row in enrichment_rows:
        for field in ("enrichment_id", "ku_id", "field", "value", "table_id", "table_section", "occurrence_id"):
            if row.get(field) is None or (isinstance(row.get(field), str) and not row[field].strip()):
                errors.append(f"{row.get('enrichment_id') or '<missing id>'}: required field {field} is empty")
        for field in ("source_ids", "source_citations", "source_urls", "cells", "table_header"):
            if field in row and not isinstance(row[field], list):
                errors.append(f"{row.get('enrichment_id')}: {field} must be an array")
        if row.get("dispute") is not None and not isinstance(row.get("dispute"), bool):
            errors.append(f"{row.get('enrichment_id')}: dispute must be boolean or null")
        if row.get("origin") not in {"", *ORIGINS}:
            errors.append(f"{row.get('enrichment_id')}: invalid or ambiguous origin {row.get('origin')!r}")
        enrichment_keys.append("|".join(str(row.get(key, "")) for key in ("ku_id", "field", "value", "source_id")))
        try:
            row_index = int(row.get("row_index", 0))
            if row_index < 1: raise ValueError
            table_rows[row.get("table_id", "")].append(row_index)
        except (ValueError, TypeError):
            errors.append(f"{row.get('enrichment_id')}: invalid row_index")
        if row.get("ku_id") not in ku_ids:
            errors.append(f"{row.get('enrichment_id')}: unknown ku_id {row.get('ku_id')}")
        if row.get("source_id") and row["source_id"] not in source_ids:
            errors.append(f"{row.get('enrichment_id')}: unknown source_id {row['source_id']}")
        for source_id in row.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"{row.get('enrichment_id')}: unknown source_ids entry {source_id}")
        if row.get("evidence_status") not in EVIDENCE_STATES:
            errors.append(f"{row.get('enrichment_id')}: invalid evidence_status")
        if row.get("evidence_status") == "source_backed" and not (row.get("source_ids") or row.get("source_id")):
            errors.append(f"{row.get('enrichment_id')}: source_backed without mapped source")
        if row.get("evidence_status") == "source_backed" and not row.get("source_ref"):
            errors.append(f"{row.get('enrichment_id')}: source_backed without source_ref")
        if row.get("source_ref") and not row.get("source_ids"):
            warnings.append(f"{row.get('enrichment_id')}: source_ref cannot be resolved from this card's source list")
    if duplicates(enrichment_keys): errors.append("enrichment.jsonl has duplicate ku_id + field + value + source_id natural key")
    if duplicates([str(row.get("occurrence_id", "")) for row in enrichment_rows]):
        errors.append("enrichment.jsonl has duplicate occurrence_id")
    for table_id, indexes in table_rows.items():
        if sorted(indexes) != list(range(1, len(indexes) + 1)):
            errors.append(f"{table_id}: row_index must be unique and contiguous from 1")
    enrichment_by_table: dict[str, list[dict]] = defaultdict(list)
    for row in enrichment_rows:
        enrichment_by_table[row.get("table_id", "")].append(row)
    source_table_ids: set[str] = set()
    independently_parsed_table_count = 0
    independently_parsed_row_count = 0
    for ku in ku_rows:
        card_path = BASE / ku.get("card_path", "")
        if not card_path.is_file():
            errors.append(f"{ku.get('ku_id')}: manifest card_path missing during table round-trip audit")
            continue
        card_text = card_path.read_text(encoding="utf-8-sig")
        boundary = re.match(r"\A(?:\ufeff)?---\r?\n.*?\r?\n---(?:\r?\n|$)", card_text, re.DOTALL)
        if not boundary:
            errors.append(f"{ku.get('ku_id')}: invalid frontmatter boundary during table round-trip audit")
            continue
        parsed = independently_parse_card_tables(card_text[boundary.end():], ku["ku_id"])
        source_table_ids.update(parsed)
        independently_parsed_table_count += len(parsed)
        independently_parsed_row_count += sum(len(table["rows"]) for table in parsed.values())
        for table_id, table in parsed.items():
            records = sorted(enrichment_by_table.get(table_id, []), key=lambda row: int(row.get("row_index", 0)))
            if len(records) != len(table["rows"]):
                errors.append(f"{ku['ku_id']} {table_id}: independent card/table row count mismatch {len(table['rows'])}/{len(records)}")
                continue
            for index, (record, cells) in enumerate(zip(records, table["rows"], strict=True), 1):
                if record.get("row_index") != index or record.get("cells") != cells:
                    errors.append(f"{ku['ku_id']} {table_id} row {index}: independent raw cell mismatch")
                if (record.get("table_section") != table["section"] or record.get("table_header") != table["header"]
                        or record.get("has_header") != table["has_header"]):
                    errors.append(f"{ku['ku_id']} {table_id} row {index}: independent table metadata mismatch")
    for table_id in set(enrichment_by_table) - source_table_ids:
        errors.append(f"{table_id}: enrichment refers to a table absent from independent raw Markdown scan")
    unit_type = {row["ku_id"]: row.get("type", "") for row in ku_rows}
    matrix = yaml.safe_load((BASE / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))
    domain_range = matrix.get("domain_range", {})
    for row in relation_rows:
        if row.get("subject_ku_id") not in ku_ids or row.get("object_ku_id") not in ku_ids:
            errors.append(f"{row.get('relation_id')}: relation endpoint absent from ku-manifest")
        if row.get("status") not in RELATION_STATES:
            errors.append(f"{row.get('relation_id')}: invalid relation status {row.get('status')!r}")
        if row.get("status") == "formal" and not (row.get("source_file") and row.get("source_span")):
            errors.append(f"{row.get('relation_id')}: formal relation lacks source file/span")
        if row.get("source_id") and row["source_id"] not in source_ids:
            errors.append(f"{row.get('relation_id')}: unknown source_id {row['source_id']}")
        if row.get("origin") not in RELATION_ORIGINS:
            errors.append(f"{row.get('relation_id')}: invalid origin {row.get('origin')!r}")
        if row.get("status") == "pending" and not (row.get("source_id") or row.get("source_file")):
            errors.append(f"{row.get('relation_id')}: pending relation lacks source locator")
        if row.get("status") == "pending" and not (row.get("note") or row.get("source_span")):
            errors.append(f"{row.get('relation_id')}: pending relation lacks rationale")
        if not row.get("predicate", "").strip():
            errors.append(f"{row.get('relation_id')}: predicate is required")
        limits = domain_range.get(row.get("predicate"), {})
        if not limits:
            errors.append(f"{row.get('relation_id')}: predicate missing from domain/range matrix")
            continue
        source_type = unit_type.get(row.get("subject_ku_id"), "")
        target_type = unit_type.get(row.get("object_ku_id"), "")
        if source_type not in limits.get("domain", []) or target_type not in limits.get("range", []):
            errors.append(f"{row.get('relation_id')}: illegal {source_type} -{row.get('predicate')}-> {target_type}")
    relation_keys = ["|".join(row.get(key, "").strip() for key in
                               ("subject_ku_id", "predicate", "object_ku_id", "time", "role", "scope"))
                     for row in relation_rows]
    if duplicates(relation_keys):
        errors.append("relations.csv has duplicate endpoints + predicate + time/role/scope natural key")
    intervals: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    segment_texts: dict[str, str] = {}
    for row in segment_rows:
        source_file = row.get("source_file", "")
        path = BASE / source_file
        if not path.is_file():
            errors.append(f"{row.get('segment_id')}: source file missing: {source_file}")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != row.get("asset_sha256"):
            errors.append(f"{row.get('segment_id')}: source asset hash mismatch")
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        start, end = int(row.get("line_start", 0)), int(row.get("line_end", 0))
        if start < 1 or end < start or end > len(lines):
            errors.append(f"{row.get('segment_id')}: invalid physical line interval")
            continue
        segment_text = "\n".join(lines[start - 1:end])
        segment_texts[row.get("segment_id", "")] = segment_text
        sliced = segment_text.encode("utf-8")
        if hashlib.sha256(sliced).hexdigest() != row.get("sha256"):
            errors.append(f"{row.get('segment_id')}: physical line slice hash mismatch")
        if not row.get("asset_sha256") or not row.get("release_excluded"):
            errors.append(f"{row.get('segment_id')}: missing source asset hash or release exclusion")
        intervals[source_file].append((start, end, row.get("segment_id", "")))
    for source_file, items in intervals.items():
        items.sort()
        for left, right in zip(items, items[1:]):
            if right[0] <= left[1]:
                errors.append(f"segments overlap: {source_file} {left[2]} and {right[2]}")
        lines = (BASE / source_file).read_text(encoding="utf-8-sig").splitlines()
        expected = sum(bool(line.strip()) for line in lines)
        covered = sum(end - start + 1 for start, end, _ in items)
        if expected != covered:
            errors.append(f"segments coverage mismatch: {source_file} {covered}/{expected} nonblank lines")
    s2 = audit_s2_artifacts(TABLES, candidate_ids, segment_ids, strict_stage, segment_texts)
    errors.extend(s2["errors"])
    warnings.extend(s2["warnings"])
    missing_s2 = s2["missing"]
    coverage_by_segment = {row.get("segment_id", ""): row for row in s2["coverage_records"]}
    mention_segments = {row.get("segment_id") for row in read_csv(TABLES / "mentions.csv")} if (TABLES / "mentions.csv").exists() else set()
    statement_segments = {row.get("segment_id") for row in read_jsonl(TABLES / "book-statements.jsonl")} if (TABLES / "book-statements.jsonl").exists() else set()
    for row in s2["coverage_records"]:
        if (row.get("disposition") == "reviewed" and row.get("migration_status") == "complete"
                and row.get("segment_id") not in mention_segments | statement_segments
                and "no_semantic_content:" not in row.get("note", "")):
            errors.append(f"{row.get('segment_id')}: empty reviewed segment requires no_semantic_content rationale")
    for row in candidate_rows:
        origin = row.get("candidate_origin", "")
        ref = row.get("candidate_source_ref", "")
        candidate_id = row.get("candidate_id", "")
        if origin not in {"", "accepted-ku", "body-mention"}:
            errors.append(f"{candidate_id}: unsupported candidate_origin {origin!r}")
        elif origin == "accepted-ku":
            ku_ref = ref.removeprefix("04-knowledge/").removesuffix(".md")
            if not ref or ku_ref not in ku_ids:
                errors.append(f"{candidate_id}: accepted-ku candidate_source_ref does not resolve to ku-manifest")
        elif origin == "body-mention":
            match = re.fullmatch(r"(.+)#L(\d+)", ref)
            if not match or match.group(1) not in coverage_by_segment:
                errors.append(f"{candidate_id}: body-mention candidate source ref does not resolve")
            else:
                segment_id, source_line = match.group(1), int(match.group(2))
                coverage = coverage_by_segment[segment_id]
                ranges = [(int(start), int(end)) for start, end in re.findall(r"L(\d+)-(\d+)", coverage.get("source_line_ranges", ""))]
                if coverage.get("disposition") != "reviewed" or not any(start <= source_line <= end for start, end in ranges):
                    errors.append(f"{candidate_id}: body-mention source line is outside reviewed coverage")
    metrics = {
        "kus": len(ku_rows), "candidates": len(candidate_rows),
        "candidate_index_rows": sum(bool(row.get("index_entry_id")) for row in candidate_rows),
        "candidate_excluded": sum(row.get("status") == "excluded" for row in candidate_rows),
        "alignments": len(alignment_rows), "alignments_unlinked": sum(not row.get("candidate_id") for row in alignment_rows),
        "relations": len(relation_rows), "formal_relations": sum(row.get("status") == "formal" for row in relation_rows),
        "enrichment_rows": len(enrichment_rows), "enrichment_unverified": sum(row.get("evidence_status") == "unverified" for row in enrichment_rows),
        "independent_card_tables": independently_parsed_table_count,
        "independent_card_rows": independently_parsed_row_count,
        "sources": len(source_rows), "segments": len(segment_rows), "s2_missing": missing_s2,
        "s2_coverage_rows": s2["coverage_rows"], "s2_coverage_complete_rows": s2["coverage_complete_rows"],
        "s2_coverage_excluded_rows": s2["coverage_excluded_rows"],
        "mentions": s2["mentions"], "book_statements": s2["book_statements"],
        "errors": errors, "warnings": warnings,
    }
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict-stage", action="store_true", help="also fail if S2 handoff artifacts are absent")
    parser.add_argument("--summary", action="store_true", help="emit compact machine-readable JSON")
    args = parser.parse_args()
    try:
        result = audit_tables(strict_stage=args.strict_stage)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"TABLE AUDIT ERROR: {exc}")
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=None if args.summary else 2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
