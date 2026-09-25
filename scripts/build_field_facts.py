#!/usr/bin/env python3
"""
build_field_facts.py — 字段级深解析（第 7 步）

把卡片正文的「字段 | 值 | 证据」三列表抽成 enrichment.jsonl 的 field→value→source 记录。
origin 由 S# 对应的来源 citation 判定：含 Haskell / Patrons and Painters → book，否则 external。
仅解析三列「字段|值|证据」表；四列的履历/亲缘/作品等重复条目表留作后续。
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
    fm = m.group(1)
    try:
        data = yaml.safe_load(fm)
        if isinstance(data, dict):
            srcs = data.get("sources")
            return srcs if isinstance(srcs, list) else []
    except Exception:
        pass
    return []


def parse_3col_tables(body: str) -> list[tuple[list[str], list[list[str]]]]:
    """解析「字段|值|证据」三列表。返回 [(header, rows), ...]。"""
    out: list[tuple[list[str], list[list[str]]]] = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and "|" in line.strip():
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            if len(block) >= 3:
                header = [c.strip() for c in block[0].strip("|").split("|")]
                # 三列「字段|值|证据」
                if len(header) == 3 and header[0] == "字段":
                    rows = []
                    for r in block[1:]:
                        if re.match(r"^\|?[\s:|-]+\|?$", r):
                            continue
                        cells = [c.strip() for c in r.strip("|").split("|")]
                        if len(cells) == 3 and cells[0] and cells[1]:
                            rows.append(cells)
                    out.append((header, rows))
        else:
            i += 1
    return out


def origin_of(srefs: list[int], sources: list[dict]) -> str:
    for s in srefs:
        idx = s - 1
        if 0 <= idx < len(sources):
            citation = str(sources[idx].get("citation", "")).lower()
            if any(h in citation for h in BOOK_HINT):
                return "book"
    return "external"


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
        for header, rows in parse_3col_tables(body):
            for field, value, evidence in rows:
                srefs = [int(x) for x in re.findall(r"S(\d+)", evidence)]
                if not srefs:
                    continue  # 无 S# 证据的字段（项目命名、待证等）跳过
                origin = origin_of(srefs, sources)
                citation = ""
                for s in srefs:
                    idx = s - 1
                    if 0 <= idx < len(sources):
                        citation = str(sources[idx].get("citation", ""))
                        break
                records.append({
                    "ku_id": ku_id,
                    "field": field,
                    "value": value,
                    "origin": origin,
                    "source_ref": "、".join(f"S{s}" for s in srefs),
                    "source_citation": citation[:200],
                })

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

    print(f"cards: {len(ku_rows)}")
    print(f"field records: {len(records)}")
    from collections import Counter
    print(f"origin: {dict(Counter(r['origin'] for r in records))}")


if __name__ == "__main__":
    main()
