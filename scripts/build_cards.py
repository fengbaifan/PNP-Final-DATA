#!/usr/bin/env python3
"""Preview card table rendering from enrichment and relations; preview never writes."""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from collections import defaultdict
from pathlib import Path

import yaml

try:
    from scripts._card_tables import parse_table_blocks
    from scripts._relation_tables import load_relations
    from scripts.build_relation_views import (
        INVERSE_MAP, _context, _normalize_target, _relative_link, _row,
        relation_view_layout, replace_relation_view,
    )
except ModuleNotFoundError:
    from _card_tables import parse_table_blocks
    from _relation_tables import load_relations
    from build_relation_views import (
        INVERSE_MAP, _context, _normalize_target, _relative_link, _row,
        relation_view_layout, replace_relation_view,
    )

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
TABLES = BASE / "04-knowledge" / "tables"
RELATION_VIEW_HEADING = re.compile(r"^### (?:当前)?关系记录(?:（[^\n]+）)?[ \t]*$", re.MULTILINE)


def relation_view_block(text: str) -> str:
    heading = RELATION_VIEW_HEADING.search(text)
    if not heading:
        return ""
    remainder = text[heading.end():]
    next_heading = re.search(r"^###\s+", remainder, re.MULTILINE)
    end = heading.end() + (next_heading.start() if next_heading else len(remainder))
    return text[heading.start():end]


def table_id(ku_id: str, section: str, index: int, header: list[str]) -> str:
    value = f"{ku_id}|{section}|{index}|{'|'.join(header)}"
    return "tbl-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def card_key(card_path: str) -> str:
    return Path(card_path).relative_to("04-knowledge/units").as_posix()


def frontmatter_title(text: str, fallback: str) -> str:
    match = re.match(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise ValueError("card has no complete frontmatter")
    data = yaml.safe_load(match.group(1)) or {}
    if not isinstance(data, dict):
        raise ValueError("card frontmatter is not a mapping")
    return str(data.get("title") or fallback)


def render_cell(value: object) -> str:
    return str(value).replace("\n", "<br>")


def render_table_block(
    header: list[str], cells: list[list[str]], has_header: bool,
    header_line: str = "", separator: str = "",
) -> list[str]:
    rows = []
    if has_header:
        preserved_header = header_line or "| " + " | ".join(render_cell(value) for value in header) + " |"
        preserved_separator = separator or "|" + "|".join("---" for _ in header) + "|"
        rows.extend([preserved_header, preserved_separator])
    rows.extend("| " + " | ".join(render_cell(value) for value in row) + " |" for row in cells)
    return rows


def relation_rows(manifest_rows: list[dict], relation_table_rows: list[dict]) -> dict[str, list[str]]:
    units = {card_key(row["card_path"]): row for row in manifest_rows}
    titles: dict[str, str] = {}
    for key, row in units.items():
        text = (BASE / row["card_path"]).read_text(encoding="utf-8-sig")
        titles[key] = frontmatter_title(text, row.get("canonical_name", ""))
    ku_to_key = {row["ku_id"]: card_key(row["card_path"]) for row in manifest_rows}
    explicit_pairs = {
        (ku_to_key[row["subject_ku_id"]], ku_to_key[row["object_ku_id"]])
        for row in relation_table_rows if row.get("status") == "formal"
        and row.get("subject_ku_id") in ku_to_key and row.get("object_ku_id") in ku_to_key
    }
    adapted_by_id = {row.get("relation_id", ""): row for row in load_relations()}
    by_unit: dict[str, list[str]] = defaultdict(list)
    for raw in relation_table_rows:
        status = raw.get("status", "")
        if status not in {"formal", "pending"}:
            continue
        subject_id, object_id = raw.get("subject_ku_id", ""), raw.get("object_ku_id", "")
        if subject_id not in ku_to_key or object_id not in ku_to_key:
            raise ValueError(f"{raw.get('relation_id')}: relation endpoint has no card")
        source, target = ku_to_key[subject_id], ku_to_key[object_id]
        edge = adapted_by_id.get(raw.get("relation_id", ""))
        if edge is None:
            raise ValueError(f"{raw.get('relation_id')}: relation adapter failed to load this row")
        context = _context(source, edge)
        if status == "pending":
            context = "状态：待证；" + context
            text = _row("outgoing", raw["predicate"], titles[target], _relative_link(source, target), context)
            text = text.replace("→ ", "→ 待证：", 1)
            by_unit[source].append(text)
            continue
        by_unit[source].append(_row("outgoing", raw["predicate"], titles[target], _relative_link(source, target), context))
        inverse = INVERSE_MAP.get(raw["predicate"])
        if inverse and (target, source) not in explicit_pairs:
            by_unit[target].append(_row("incoming", inverse, titles[source], _relative_link(target, source), _context(source, edge, source_title=titles[source])))
    return by_unit


def render_card(text: str, ku_id: str, enrichment: list[dict], relation_markdown_rows: list[str]) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    text = text.replace("\r\n", "\n")
    frontmatter = re.match(r"\A(?:\ufeff)?---\r?\n.*?\r?\n---\r?\n", text, re.DOTALL)
    if not frontmatter:
        raise ValueError(f"{ku_id}: invalid YAML frontmatter boundary")
    body = text[frontmatter.end():]
    blocks = parse_table_blocks(body)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in enrichment:
        grouped[record.get("table_id", "")].append(record)
    body_lines = body.splitlines()
    seen: set[str] = set()
    for block in reversed(blocks):
        index = block["table_index"]
        block_id = table_id(ku_id, block["section"], index, block["header"])
        rows = sorted(grouped.get(block_id, []), key=lambda row: int(row["row_index"]))
        if not rows:
            raise ValueError(f"{ku_id} {block_id}: no table rows in enrichment; refusing to erase card content")
        rendered_cells = []
        for expected_index, record in enumerate(rows, 1):
            if int(record["row_index"]) != expected_index:
                raise ValueError(f"{ku_id} {block_id}: row_index sequence is not contiguous at {expected_index}")
            cells = record.get("cells")
            if not isinstance(cells, list) or not cells or not all(isinstance(value, str) for value in cells):
                raise ValueError(f"{ku_id} {block_id} row {expected_index}: cells must be a non-empty string array")
            if block["has_header"] and len(cells) != len(block["header"]):
                raise ValueError(f"{ku_id} {block_id} row {expected_index}: cell count does not match preserved header")
            if not block["has_header"] and len(cells) != len(rows[0].get("cells", [])):
                raise ValueError(f"{ku_id} {block_id} row {expected_index}: headerless table rows have inconsistent cell counts")
            rendered_cells.append(cells)
        replacement = render_table_block(
            block["header"], rendered_cells, block["has_header"],
            block.get("header_line", ""), block.get("separator", ""),
        )
        body_lines[block["start_line"]:block["end_line"]] = replacement
        seen.add(block_id)
    orphaned = set(grouped) - seen
    if orphaned:
        raise ValueError(f"{ku_id}: enrichment refers to absent card table(s): {sorted(orphaned)[:5]}")
    rendered = text[:frontmatter.end()] + "\n".join(body_lines) + ("\n" if body.endswith("\n") else "")
    relation_section = re.search(r"^##\s+关系与证据\s*$", rendered, re.MULTILINE)
    if relation_section and relation_markdown_rows and not re.search(
        r"^###\s+(?:当前)?关系记录(?:（[^\n]+）)?\s*$", rendered, re.MULTILINE
    ):
        next_heading = re.search(r"^#{1,6}\s+", rendered[relation_section.end():], re.MULTILINE)
        insertion = relation_section.end() + (next_heading.start() if next_heading else len(rendered[relation_section.end():]))
        # Put the missing subsection before the section's existing identity
        # table or prose, retaining all original content verbatim.
        rendered = rendered[:insertion].rstrip("\n") + "\n\n### 关系记录\n\n" + rendered[insertion:].lstrip("\n")
    if RELATION_VIEW_HEADING.search(rendered):
        rendered = replace_relation_view(rendered, relation_markdown_rows)
    return rendered.replace("\n", newline) if newline != "\n" else rendered


def load_inputs() -> tuple[list[dict], dict[str, list[dict]], dict[str, list[str]]]:
    with (TABLES / "ku-manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    enrichments: dict[str, list[dict]] = defaultdict(list)
    for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            row = json.loads(line)
            enrichments[row["ku_id"]].append(row)
    relation_table = list(csv.DictReader((TABLES / "relations.csv").open(encoding="utf-8-sig", newline="")))
    projected = relation_rows(manifest, relation_table)
    return manifest, enrichments, projected


def read_card(path: Path) -> str:
    """Read UTF-8 without newline translation so render can preserve BOM and EOLs."""
    return path.read_bytes().decode("utf-8")


def table_signature(items: list[dict]) -> list[tuple]:
    return [
        (
            block["section"], block["table_index"], block["header"], block["has_header"],
            block.get("header_line", ""), block.get("separator", ""), block["rows"],
        )
        for block in items
    ]


def build_render_plan(manifest, enrichments, projected):
    planned: dict[Path, str] = {}
    originals: dict[Path, bytes] = {}
    table_count = row_count = relation_count = relation_preview_change_count = 0
    for row in manifest:
        key = card_key(row["card_path"])
        path = BASE / row["card_path"]
        original_bytes = path.read_bytes()
        card = original_bytes.decode("utf-8")
        frontmatter = re.match(r"\A(?:\ufeff)?---\r?\n.*?\r?\n---\r?\n", card, re.DOTALL)
        if not frontmatter:
            raise ValueError(f"{row['ku_id']}: invalid YAML frontmatter boundary")
        blocks = parse_table_blocks(card[frontmatter.end():])
        ku_enrichment = enrichments.get(row["ku_id"], [])
        ku_relations = projected.get(key, [])
        rendered = render_card(card, row["ku_id"], ku_enrichment, ku_relations)
        if not rendered:
            raise ValueError(f"empty rendered card: {row['card_path']}")
        rendered_frontmatter = re.match(r"\A(?:\ufeff)?---\r?\n.*?\r?\n---\r?\n", rendered, re.DOTALL)
        assert rendered_frontmatter is not None
        rendered_blocks = parse_table_blocks(rendered[rendered_frontmatter.end():])
        if table_signature(blocks) != table_signature(rendered_blocks):
            raise ValueError(f"{row['ku_id']}: card table rows differ from enrichment; inspect --preview")
        before_heading, before_table = relation_view_layout(card)
        after_heading, after_table = relation_view_layout(rendered)
        if before_heading is not None and before_heading != after_heading:
            raise ValueError(f"{row['ku_id']}: relation subsection heading changed; inspect --preview")
        if before_table is not None and before_table != after_table:
            raise ValueError(f"{row['ku_id']}: existing relation table header changed; inspect --preview")
        if before_heading is None and bool(ku_relations) != (after_heading is not None):
            raise ValueError(f"{row['ku_id']}: relation subsection presence does not match projected rows")
        if before_table is None and bool(ku_relations) != (after_table is not None):
            raise ValueError(f"{row['ku_id']}: relation table presence does not match projected rows")
        if render_card(rendered, row["ku_id"], ku_enrichment, ku_relations) != rendered:
            raise ValueError(f"{row['ku_id']}: renderer is not idempotent")
        if relation_view_block(card) != relation_view_block(rendered):
            relation_preview_change_count += 1
        table_count += len(blocks)
        row_count += sum(len(block["rows"]) for block in blocks)
        relation_count += len(ku_relations)
        if rendered != card:
            planned[path] = rendered
            originals[path] = original_bytes
    return planned, originals, {
        "cards": len(manifest),
        "tables": table_count,
        "rows": row_count,
        "projected_relation_rows": relation_count,
        "cards_with_relation_changes": relation_preview_change_count,
    }


def apply_render_plan(planned: dict[Path, str], originals: dict[Path, bytes]) -> None:
    """Apply all rendered cards with a temporary backup and rollback on failure."""
    if not planned:
        return
    transaction_id = uuid.uuid4().hex
    recovery_root = Path(tempfile.mkdtemp(prefix=f"pnp-card-render-{transaction_id}-"))
    staged: dict[Path, Path] = {}
    replaced: list[Path] = []
    manifest = []
    try:
        for index, (path, rendered) in enumerate(planned.items()):
            relative = path.relative_to(BASE).as_posix()
            backup = recovery_root / "originals" / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(originals[path])
            content = rendered.encode("utf-8")
            manifest.append({
                "path": relative,
                "backup": backup.relative_to(recovery_root).as_posix(),
                "original_sha256": hashlib.sha256(originals[path]).hexdigest(),
                "rendered_sha256": hashlib.sha256(content).hexdigest(),
            })
            temporary = path.with_name(f".{path.name}.render-{transaction_id}-{index}.tmp")
            temporary.write_bytes(content)
            staged[path] = temporary
        (recovery_root / "manifest.json").write_text(
            json.dumps({"transaction_id": transaction_id, "files": manifest}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        for path, temporary in staged.items():
            if path.read_bytes() != originals[path]:
                raise RuntimeError(f"card changed after preflight: {path.relative_to(BASE).as_posix()}")
        print(f"transaction recovery snapshot: {recovery_root}")
        for path, temporary in staged.items():
            temporary.replace(path)
            replaced.append(path)
        for path, rendered in planned.items():
            if path.read_bytes() != rendered.encode("utf-8"):
                raise RuntimeError(f"post-write byte check failed: {path.relative_to(BASE).as_posix()}")
    except BaseException:
        rollback_errors = []
        for path in reversed(replaced):
            try:
                backup = recovery_root / "originals" / path.relative_to(BASE)
                restore = path.with_name(f".{path.name}.rollback-{transaction_id}.tmp")
                restore.write_bytes(backup.read_bytes())
                restore.replace(path)
            except OSError as error:
                rollback_errors.append(f"{path}: {error}")
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        if rollback_errors:
            raise RuntimeError(
                f"render failed; rollback incomplete. Recovery snapshot retained at {recovery_root}: "
                + "; ".join(rollback_errors)
            )
        shutil.rmtree(recovery_root, ignore_errors=True)
        raise
    else:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        shutil.rmtree(recovery_root)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="print a unified diff for one card; never writes")
    mode.add_argument("--check", action="store_true", help="preflight every card and report the exact render scope; never writes")
    mode.add_argument("--render", action="store_true", help="preflight and write the complete CSV-backed card projection")
    parser.add_argument("--ku", help="KU path, for example units/archives/arragona-mantua-letter-1621")
    args = parser.parse_args()
    manifest, enrichments, projected = load_inputs()
    if args.preview:
        if not args.ku:
            parser.error("--preview requires --ku")
        ku_id = args.ku.removesuffix(".md")
        if not ku_id.startswith("units/"):
            ku_id = "units/" + ku_id
        row = next((item for item in manifest if item["ku_id"] == ku_id), None)
        if row is None:
            parser.error(f"unknown ku_id: {ku_id}")
        path = BASE / row["card_path"]
        before = read_card(path)
        after = render_card(before, ku_id, enrichments.get(ku_id, []), projected.get(card_key(row["card_path"]), []))
        print(f"preview only: {row['card_path']} (no files written)")
        print("".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                            fromfile="card/current", tofile="card/rendered")))
        return 0
    if args.ku:
        parser.error("--ku is only valid with --preview")
    planned, originals, stats = build_render_plan(manifest, enrichments, projected)
    print(
        f"full render preflight passed: cards={stats['cards']} tables={stats['tables']} "
        f"rows={stats['rows']} projected_relation_rows={stats['projected_relation_rows']} "
        f"cards_with_relation_changes={stats['cards_with_relation_changes']} files_to_write={len(planned)}"
    )
    if args.render:
        apply_render_plan(planned, originals)
        # Re-read persisted outputs and verify idempotence against the source tables.
        for path, expected in planned.items():
            persisted = read_card(path)
            if persisted != expected:
                raise RuntimeError(f"persisted render differs from plan: {path.relative_to(BASE).as_posix()}")
        print(f"render complete: files_written={len(planned)}; post-write bytes verified; recovery snapshot cleaned")
    else:
        print("No card files were written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
