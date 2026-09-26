"""Lossless-enough parsing helpers for structured Markdown tables in KU cards.

The parser keeps every cell and source marker. It does not decide whether a row
is a true historical claim; that remains a semantic review decision.
"""
from __future__ import annotations

import re


RELATION_HEADERS = {
    ("方向与关系", "关联知识元", "语境与证据"),
}


def split_row(line: str) -> list[str]:
    """Split a simple pipe table row, respecting escaped pipes."""
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in value:
        if char == "|" and not escaped:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
    cells.append("".join(current).strip())
    return cells


def is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\|?[\s:|\-]+\|?", line.strip()))


def parse_table_blocks(body: str) -> list[dict]:
    """Return table blocks with original cell values and stable local ordinals."""
    lines = body.splitlines()
    blocks: list[dict] = []
    section = ""
    heading_stack: dict[int, str] = {}
    i = 0
    while i < len(lines):
        heading = re.match(r"^(#{2,6})\s+(.+?)\s*#*\s*$", lines[i])
        if heading:
            level = len(heading.group(1))
            heading_stack[level] = heading.group(2).strip()
            heading_stack = {k: v for k, v in heading_stack.items() if k <= level}
            section = " / ".join(heading_stack[k] for k in sorted(heading_stack))
        if not lines[i].strip().startswith("|"):
            i += 1
            continue
        start_line = i
        raw_rows: list[str] = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            raw_rows.append(lines[i].strip())
            i += 1
        if len(raw_rows) < 2:
            continue
        has_header = len(raw_rows) > 1 and is_separator(raw_rows[1])
        header = split_row(raw_rows[0]) if has_header else []
        data_source_rows = raw_rows[2:] if has_header else raw_rows
        data_rows = [split_row(row) for row in data_source_rows if not is_separator(row)]
        if (has_header and not header) or not data_rows:
            continue
        if tuple(header) in RELATION_HEADERS or section.split(" / ")[-1] in {"关系记录", "关系"}:
            continue
        blocks.append({
            "section": section,
            "table_index": len([b for b in blocks if b["section"] == section]) + 1,
            "start_line": start_line,
            "end_line": i,
            "has_header": has_header,
            "header": header,
            "header_line": raw_rows[0] if has_header else "",
            "separator": raw_rows[1] if has_header else "",
            "rows": data_rows,
        })
    return blocks


def source_refs(text: str) -> list[int]:
    """Expand references such as S2–S4 while preserving order and uniqueness."""
    refs: list[int] = []
    pattern = re.compile(r"(?i)(?<![A-Za-z0-9])S\s*(\d+)\s*(?:[–—-]\s*S?\s*(\d+))?(?!\d)")
    for match in pattern.finditer(text):
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if end < start or end - start > 100:
            continue
        for ref in range(start, end + 1):
            if ref not in refs:
                refs.append(ref)
    return refs
