#!/usr/bin/env python3
"""Extract card table rows into reviewable enrichment records.

Default mode is a read-only preview. Use --apply only after reviewing counts.
Every source table row, its full cells, header, section and source markers are
preserved so that a renderer can rebuild the same table without paraphrasing.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

import yaml

try:
    from scripts._card_tables import parse_table_blocks, source_refs
except ModuleNotFoundError:
    from _card_tables import parse_table_blocks, source_refs

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
TABLES = BASE / "04-knowledge" / "tables"
ENRICHMENT = TABLES / "enrichment.jsonl"
SOURCES = TABLES / "sources.csv"
SOURCE_COLUMNS = ["source_id", "kind", "label", "version", "accessed_date", "citation", "url"]
URL_START_RE = re.compile(r"https?://")


def normalize_url(value: str) -> str:
    url = value.rstrip(".,;:")
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def citation_urls(citation: str) -> list[str]:
    """Extract citation URLs without terminal prose punctuation.

    Keep balanced parentheses used in Wikipedia/Treccani paths, while
    dropping a closing parenthesis that belongs to surrounding punctuation.
    """
    urls: list[str] = []
    for match in URL_START_RE.finditer(citation):
        start = match.start()
        index = match.end()
        parentheses = 0
        while index < len(citation):
            character = citation[index]
            if character.isspace() or character in '<>"“”[]|':
                break
            if character == "(":
                parentheses += 1
            elif character == ")":
                if parentheses == 0:
                    break
                parentheses -= 1
            index += 1
        url = normalize_url(citation[start:index])
        if url and url not in urls:
            urls.append(url)
    return urls


def read_frontmatter(text: str) -> dict:
    match = re.match(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise ValueError("KU card has no valid frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("KU card frontmatter must be a mapping")
    return data


def citation_identity(citation: str) -> tuple[str, str]:
    normalized = " ".join(citation.split())
    if not normalized:
        return "", ""
    low = normalized.lower()
    if "haskell" in low or "patrons and painters" in low:
        return "haskell-1980-rev-ed", "book"
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"src-{digest}", "external"


def load_existing_ids(path: Path) -> tuple[dict[str, deque[str]], dict[tuple[str, str, str, str], deque[str]], int]:
    by_occurrence: dict[str, deque[str]] = defaultdict(deque)
    by_natural_key: dict[tuple[str, str, str, str], deque[str]] = defaultdict(deque)
    max_id = 0
    if not path.exists():
        return by_occurrence, by_natural_key, max_id
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        old_id = str(record.get("enrichment_id", ""))
        match = re.fullmatch(r"enr-(\d+)", old_id)
        if match:
            max_id = max(max_id, int(match.group(1)))
        key = (record.get("ku_id", ""), record.get("field", ""), record.get("value", ""), record.get("source_id", ""))
        if old_id:
            if record.get("occurrence_id"):
                by_occurrence[str(record["occurrence_id"])].append(old_id)
            by_natural_key[key].append(old_id)
    return by_occurrence, by_natural_key, max_id


def collect_source_rows(unit_sources: list[dict], citation_registry: dict[str, dict]) -> list[dict]:
    indexed: list[dict] = []
    for index, source in enumerate(unit_sources, 1):
        if not isinstance(source, dict):
            continue
        citation = str(source.get("citation", "") or "").strip()
        source_id, kind = citation_identity(citation)
        if source_id:
            citation_url_candidates = citation_urls(citation)
            explicit_url = str(source.get("url", "") or "").strip()
            url = normalize_url(explicit_url or (citation_url_candidates[0] if citation_url_candidates else ""))
            indexed.append({"index": index, "citation": citation, "source_id": source_id, "kind": kind, "url": url})
            row = citation_registry.setdefault(source_id, {
                "source_id": source_id,
                "kind": kind,
                "label": citation,
                "version": "",
                "accessed_date": str(source.get("accessed_date", source.get("access_date", "")) or ""),
                "citation": citation,
                "url": url,
            })
            if url and not row["url"]:
                row["url"] = url
            if not row["accessed_date"]:
                row["accessed_date"] = str(source.get("accessed_date", source.get("access_date", "")) or "")
    return indexed


def value_fields(header: list[str], cells: list[str], section: str) -> tuple[str, str, str]:
    if not header:
        return section or "结构化表格", "｜".join(cells), ""
    width = max(len(header), len(cells))
    normalized_header = (header + [""] * width)[:width]
    normalized_cells = (cells + [""] * width)[:width]
    citation_col = bool(normalized_header[-1] and re.search(r"证据|依据|出处|引用|evidence|citation", normalized_header[-1], re.I))
    data_cells = normalized_cells[:-1] if citation_col else normalized_cells
    data_headers = normalized_header[:-1] if citation_col else normalized_header
    if len(data_cells) >= 2 and data_headers and data_headers[0] in {"字段", "项目", "名称", "类别", "类型", "时间", "时期", "身份", "角色", "作品", "文献类型", "主体", "环节", "来源", "阶段", "标签", "数据"}:
        field = data_cells[0]
        value = "｜".join(data_cells[1:])
    elif len(data_cells) >= 2:
        field = f"{section}｜{data_headers[0]}" if section else data_headers[0]
        value = "｜".join(data_cells)
    else:
        field = section or (data_headers[0] if data_headers else "")
        value = "｜".join(data_cells)
    evidence = normalized_cells[-1] if citation_col else ""
    return field, value, evidence


def extract_records(ku_rows: list[dict]) -> tuple[list[dict], dict[str, dict], list[str], int]:
    records: list[dict] = []
    source_registry: dict[str, dict] = {}
    warnings: list[str] = []
    cards_with_tables = 0
    for ku in ku_rows:
        card = BASE / ku["card_path"]
        if not card.is_file():
            warnings.append(f"missing card: {ku['card_path']}")
            continue
        text = card.read_text(encoding="utf-8-sig")
        fm = read_frontmatter(text)
        parts = re.split(r"\A(?:\ufeff)?---\r?\n.*?\r?\n---\r?\n", text, maxsplit=1, flags=re.DOTALL)
        body = parts[1] if len(parts) == 2 else ""
        card_sources = fm.get("sources") if isinstance(fm.get("sources"), list) else []
        indexed_sources = collect_source_rows(card_sources, source_registry)
        blocks = parse_table_blocks(body)
        if blocks:
            cards_with_tables += 1
        for block in blocks:
            table_key = f"{ku['ku_id']}|{block['section']}|{block['table_index']}|{'|'.join(block['header'])}"
            table_id = "tbl-" + hashlib.sha256(table_key.encode("utf-8")).hexdigest()[:16]
            for row_index, original_cells in enumerate(block["rows"], 1):
                cells = original_cells + [""] * max(0, len(block["header"]) - len(original_cells))
                if block["has_header"] and len(original_cells) != len(block["header"]):
                    warnings.append(f"column count mismatch {ku['ku_id']} {table_id} row {row_index}: header {len(block['header'])}, row {len(original_cells)}")
                if not any(cell.strip() for cell in cells):
                    continue
                field, value, evidence = value_fields(block["header"], cells, block["section"])
                all_text = "\n".join(cells)
                refs = source_refs(all_text)
                mapped = [src for src in indexed_sources if src["index"] in refs]
                urls = citation_urls(all_text)
                # If an inline URL matches a card citation, it is a better locator
                # than a stale/misaligned S-number. Keep the original marker too.
                if urls:
                    mapped_ids = {src["source_id"] for src in mapped}
                    for src in indexed_sources:
                        if any(url in citation_urls(src["citation"]) for url in urls) and src["source_id"] not in mapped_ids:
                            mapped.append(src)
                            mapped_ids.add(src["source_id"])
                source_ids = list(dict.fromkeys(src["source_id"] for src in mapped))
                kinds = list(dict.fromkeys(src["kind"] for src in mapped))
                origin = kinds[0] if len(kinds) == 1 else ""
                citations = list(dict.fromkeys(src["citation"] for src in mapped))
                urls = list(dict.fromkeys(urls + [src["url"] for src in mapped if src["url"]]))
                source_ref = "、".join(f"S{ref}" for ref in refs)
                # The original evidence text and all cells remain available for review/rendering.
                raw_evidence = evidence or ("｜".join(cells) if refs else "")
                status = "source_backed" if mapped and raw_evidence else "unverified"
                occurrence_key = f"{ku['ku_id']}|{table_id}|{row_index}"
                occurrence_id = "occ-" + hashlib.sha256(occurrence_key.encode("utf-8")).hexdigest()[:16]
                records.append({
                    "enrichment_id": "",
                    "ku_id": ku["ku_id"],
                    "field": field,
                    "value": value,
                    "origin": origin,
                    "source_id": source_ids[0] if len(source_ids) == 1 else "",
                    "source_ids": source_ids,
                    "source_ref": source_ref,
                    "source_citations": citations,
                    "source_urls": urls,
                    "evidence": raw_evidence,
                    "evidence_status": status,
                    "dispute": None,
                    "accessed_date": "",
                    "occurrence_id": occurrence_id,
                    "table_id": table_id,
                    "table_section": block["section"],
                    "has_header": block["has_header"],
                    "table_header": block["header"],
                    "row_index": row_index,
                    "cells": cells,
                    "unit_evidence_status": str(fm.get("evidence_status", "") or ""),
                })
    return records, source_registry, warnings, cards_with_tables


def assign_ids(records: list[dict], existing_path: Path) -> None:
    by_occurrence, previous, max_id = load_existing_ids(existing_path)
    for record in records:
        occurrence_id = record.get("occurrence_id", "")
        if occurrence_id and by_occurrence[occurrence_id]:
            record["enrichment_id"] = by_occurrence[occurrence_id].popleft()
            continue
        legacy_key = (record["ku_id"], record["field"], record["value"], record["source_id"])
        if previous[legacy_key]:
            record["enrichment_id"] = previous[legacy_key].popleft()
        else:
            max_id += 1
            record["enrichment_id"] = f"enr-{max_id:05d}"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    temp.replace(path)


def write_sources(path: Path, old_rows: list[dict], registry: dict[str, dict]) -> None:
    rows_by_id = {str(row.get("source_id", "")): row for row in old_rows if row.get("source_id")}
    original_by_id = {source_id: dict(row) for source_id, row in rows_by_id.items()}
    for source_id, row in registry.items():
        old = rows_by_id.get(source_id, {})
        rows_by_id[source_id] = {**old, **row}
    if rows_by_id == original_by_id:
        return
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SOURCE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in sorted(rows_by_id.values(), key=lambda item: item["source_id"]):
            writer.writerow(row)
    temp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write enrichment and merge source registry")
    args = parser.parse_args()
    ku_path = TABLES / "ku-manifest.csv"
    with ku_path.open(encoding="utf-8-sig", newline="") as handle:
        ku_rows = list(csv.DictReader(handle))
    if not ku_rows:
        raise SystemExit("ku-manifest.csv is empty; refusing to write")
    records, source_registry, warnings, cards_with_tables = extract_records(ku_rows)
    assign_ids(records, ENRICHMENT)
    existing_records = [
        json.loads(line) for line in ENRICHMENT.read_text(encoding="utf-8-sig").splitlines() if line.strip()
    ] if ENRICHMENT.exists() else []
    existing_by_id = {row.get("enrichment_id", ""): row for row in existing_records}
    generated_by_id = {row.get("enrichment_id", ""): row for row in records}
    changed_ids = sorted(
        key for key in existing_by_id.keys() & generated_by_id.keys()
        if existing_by_id[key] != generated_by_id[key]
    )
    new_ids = generated_by_id.keys() - existing_by_id.keys()
    removed_ids = existing_by_id.keys() - generated_by_id.keys()
    old_source_rows = list(csv.DictReader(SOURCES.open(encoding="utf-8-sig", newline=""))) if SOURCES.exists() else []
    old_sources_by_id = {row.get("source_id", ""): row for row in old_source_rows if row.get("source_id")}
    merged_sources = dict(old_sources_by_id)
    for source_id, row in source_registry.items():
        merged_sources[source_id] = {**old_sources_by_id.get(source_id, {}), **row}
    source_changes = sum(merged_sources.get(source_id) != row for source_id, row in old_sources_by_id.items())
    source_changes += len(merged_sources.keys() - old_sources_by_id.keys())
    natural_keys = [(r["ku_id"], r["field"], r["value"], r["source_id"], r["occurrence_id"]) for r in records]
    duplicates = len(natural_keys) - len(set(natural_keys))
    print(f"cards={len(ku_rows)} cards_with_tables={cards_with_tables} rows={len(records)} unique_sources={len(source_registry)}")
    print(f"records_with_source={sum(bool(r['source_ids']) for r in records)} unverified={sum(r['evidence_status']=='unverified' for r in records)} duplicate_occurrences={duplicates}")
    print(f"record_changes={len(changed_ids)} new_ids={len(new_ids)} removed_ids={len(removed_ids)} source_registry_changes={source_changes}")
    for enrichment_id in changed_ids:
        before, after = existing_by_id[enrichment_id], generated_by_id[enrichment_id]
        changed_fields = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
        print(f"UPDATE {enrichment_id}: {', '.join(changed_fields)}")
    print(f"warnings={len(warnings)}")
    for warning in warnings[:30]:
        print(f"WARNING: {warning}")
    if warnings:
        print("Review warnings before applying; no data was written.")
        return 2
    if args.apply:
        write_jsonl(ENRICHMENT, records)
        write_sources(SOURCES, old_source_rows, source_registry)
        print(f"applied enrichment={ENRICHMENT.relative_to(BASE)} sources={SOURCES.relative_to(BASE)}")
    else:
        print("preview only; pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
