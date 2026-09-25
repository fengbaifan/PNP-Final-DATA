#!/usr/bin/env python3
"""
build_field_facts.py — 字段级深解析（第 7 步）

把卡片正文的表格抽成 enrichment.jsonl 的 field→value→source 记录：
- 三列「字段|值|证据」：field=第一列，value=第二列。
- 四列及以上的重复条目表（履历/亲缘/作品/所有权）：field=所属 ### 小节名，value=非证据列用「｜」连接。
origin 由 S# 对应的来源 citation 判定：含 Haskell / Patrons and Painters → book，否则 external。
无 S# 证据的字段标 origin=inferred（项目命名、待证等）。
"""
from __future__ import annotations

import csv
import json
import re
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


def origin_of(srefs: list[int], sources: list[dict]) -> str:
    for s in srefs:
        idx = s - 1
        if 0 <= idx < len(sources):
            if any(h in str(sources[idx].get("citation", "")).lower() for h in BOOK_HINT):
                return "book"
    return "external"


def citation_of(srefs: list[int], sources: list[dict]) -> str:
    for s in srefs:
        idx = s - 1
        if 0 <= idx < len(sources):
            return str(sources[idx].get("citation", ""))
    return ""


def main() -> None:
    ku_rows = list(csv.DictReader(open(TABLES / "ku-manifest.csv", encoding="utf-8")))
    records: list[dict] = []
    for ku in ku_rows:
        card = BASE / ku["card_path"]
        if not card.exists():
            continue
        text = card.read_text(encoding="utf-8")
        sources = frontmatter_sources(text)
        body = text.split("---", 2)[2] if text.count("---") >= 2 else ""
        ku_id = ku["ku_id"]

        section = ""
        lines = body.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            # 追踪 ### 小节
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
                    # 三列表：字段|值|证据
                    if len(header) == 3 and header[0] == "字段":
                        for cells in rows:
                            if len(cells) < 3 or not cells[0] or not cells[1]:
                                continue
                            field, value, evidence = cells[0], cells[1], cells[2]
                            srefs = [int(x) for x in re.findall(r"S(\d+)", evidence)]
                            origin = origin_of(srefs, sources) if srefs else "inferred"
                            records.append({
                                "ku_id": ku_id, "field": field, "value": value,
                                "origin": origin,
                                "source_ref": "、".join(f"S{s}" for s in srefs),
                                "source_citation": citation_of(srefs, sources)[:200],
                            })
                    # 四列及以上重复条目：字段=小节，值=非证据列
                    elif len(header) >= 4:
                        for cells in rows:
                            if len(cells) < 2:
                                continue
                            evidence = cells[-1]
                            content_cells = cells[:-1]
                            if not any(content_cells):
                                continue
                            srefs = [int(x) for x in re.findall(r"S(\d+)", evidence)]
                            origin = origin_of(srefs, sources) if srefs else "inferred"
                            records.append({
                                "ku_id": ku_id, "field": section or "｜".join(header[:-1]),
                                "value": "｜".join(content_cells),
                                "origin": origin,
                                "source_ref": "、".join(f"S{s}" for s in srefs),
                                "source_citation": citation_of(srefs, sources)[:200],
                            })
            else:
                i += 1

    with open(TABLES / "enrichment.jsonl", "w", encoding="utf-8") as f:
        for i, r in enumerate(records, 1):
            rec = {
                "enrichment_id": f"enr-{i:05d}",
                "ku_id": r["ku_id"],
                "field": r["field"],
                "value": r["value"],
                "origin": r["origin"],
                "source_id": "haskell-1980-rev-ed" if r["origin"] == "book" else "",
                "source_ref": r["source_ref"],
                "source_citation": r["source_citation"],
                "evidence_status": "source_backed",
                "dispute": False,
                "accessed_date": "",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    from collections import Counter
    print(f"cards: {len(ku_rows)}")
    print(f"field records: {len(records)}")
    print(f"origin: {dict(Counter(r['origin'] for r in records))}")


if __name__ == "__main__":
    main()
