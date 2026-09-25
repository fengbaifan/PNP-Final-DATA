#!/usr/bin/env python3
"""
build_cards.py — 卡片渲染器（卡片 = tables 的视图）

check 模式（默认，只读）：用与 build_field_facts.py 相同的解析逻辑重新抽卡片字段，
与 tables/enrichment.jsonl 比对，报告「渲染会丢多少字段」，不写任何卡片。
render 模式（后续）：从 tables 重建卡片结构化表，散文原位保留。
"""
from __future__ import annotations

import csv
import json
import re
import sys
import yaml
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
TABLES = BASE / "04-knowledge" / "tables"

BOOK_HINT = ("haskell", "patrons and painters")


def frontmatter_sources(text: str) -> list[dict]:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not m:
        return []
    try:
        data = yaml.safe_load(m.group(1))
        srcs = data.get("sources") if isinstance(data, dict) else None
        return srcs if isinstance(srcs, list) else []
    except Exception:
        return []


def split_row(row: str) -> list[str]:
    return [c.strip() for c in row.strip("|").split("|")]


def parse_card_fields(text: str, ku_id: str) -> list[tuple[str, str, str]]:
    """返回 [(field, value, origin), ...]，与 build_field_facts.py 的解析一致。"""
    sources = frontmatter_sources(text)
    body = text.split("---", 2)[2] if text.count("---") >= 2 else ""
    out: list[tuple[str, str, str]] = []
    section = ""
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("###"):
            section = line.lstrip("#").strip()
            i += 1
            continue
        if line.strip().startswith("|") and "|" in line.strip():
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            if len(block) >= 3:
                header = split_row(block[0])
                rows = []
                for r in block[1:]:
                    if re.match(r"^\|?[\s:|-]+\|?$", r):
                        continue
                    cells = split_row(r)
                    if any(cells):
                        rows.append(cells)
                if len(header) == 3 and header[0] == "字段":
                    for cells in rows:
                        if len(cells) < 3 or not cells[0] or not cells[1]:
                            continue
                        srefs = [int(x) for x in re.findall(r"S(\d+)", cells[2])]
                        origin = "inferred" if not srefs else (
                            "book" if any("haskell" in str(sources[s-1].get("citation", "")).lower()
                                          or "patrons and painters" in str(sources[s-1].get("citation", "")).lower()
                                          for s in srefs if 0 <= s-1 < len(sources)) else "external")
                        out.append((cells[0], cells[1], origin))
                elif len(header) >= 4:
                    for cells in rows:
                        if len(cells) < 2:
                            continue
                        content = cells[:-1]
                        if not any(content):
                            continue
                        srefs = [int(x) for x in re.findall(r"S(\d+)", cells[-1])]
                        origin = "inferred" if not srefs else (
                            "book" if any("haskell" in str(sources[s-1].get("citation", "")).lower()
                                          or "patrons and painters" in str(sources[s-1].get("citation", "")).lower()
                                          for s in srefs if 0 <= s-1 < len(sources)) else "external")
                        out.append((section or "｜".join(header[:-1]), "｜".join(content), origin))
        else:
            i += 1
    return out


def check() -> int:
    ku_rows = list(csv.DictReader(open(TABLES / "ku-manifest.csv", encoding="utf-8")))
    # enrichment.jsonl 现有记录 → set[(ku_id, field, value)]
    enrich = set()
    for line in open(TABLES / "enrichment.jsonl", encoding="utf-8"):
        r = json.loads(line)
        enrich.add((r["ku_id"], r["field"], r["value"]))

    card_fields = set()
    missed = []
    for ku in ku_rows:
        card = BASE / ku["card_path"]
        if not card.exists():
            continue
        text = card.read_text(encoding="utf-8")
        for field, value, origin in parse_card_fields(text, ku["ku_id"]):
            card_fields.add((ku["ku_id"], field, value))
            if (ku["ku_id"], field, value) not in enrich:
                missed.append((ku["ku_id"], field, value))

    matched = len(card_fields) - len(missed)
    print(f"卡片字段总数: {len(card_fields)}")
    print(f"enrichment 记录数: {len(enrich)}")
    print(f"往返命中: {matched} ({100.0*matched/len(card_fields):.1f}%)" if card_fields else "0")
    print(f"会丢失字段: {len(missed)} ({100.0*len(missed)/len(card_fields):.1f}%)" if card_fields else "0")
    print()
    print("=== 会丢失字段样例（前 20）===")
    for ku_id, field, value in missed[:20]:
        print(f"  {ku_id} | {field} | {value[:50]}")
    return 0


def main() -> int:
    if "--render" in sys.argv:
        print("render 模式尚未实现（先跑通 check 往返校验）")
        return 1
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
