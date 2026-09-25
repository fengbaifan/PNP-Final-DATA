#!/usr/bin/env python3
"""
build_entity_candidates.py — step 4：解析原书索引，生成全书实体候选（S1）

读取 02-sources/03-Index/03-2-Index-CSV/*.csv（原书人名/机构/地名索引，带页码），
生成全书级 entity-candidates.csv。这是以作者本人编制的索引为种子的一次性候选清单，
替代「Agent 逐章从零识别实体」；也是后续召回率对照的基准。
"""
import csv
import io
import re
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path(__file__).resolve().parents[1]
IDX = BASE / "02-sources" / "03-Index" / "03-2-Index-CSV"
OUT = BASE / "release" / "v0.1" / "entity-candidates.csv"


def infer_type(name):
    n = name.strip()
    if re.search(r"\b(Accademia|Academy|Académie)\b", n):
        return "institution"
    if re.search(r"\bcollection\b", n, re.I):
        return "institution"
    if re.search(r"\b(church|basilica|chapel|cappella|duomo|cathedral|monastery|convent)\b", n, re.I):
        return "place"
    if re.search(r"\b(palazzo|palace|villa)\b", n, re.I):
        return "place"
    if "," in n:  # "Last, First" 人名格式
        return "person"
    return "undetermined"


def main():
    rows, crossrefs = [], []
    for f in sorted(IDX.glob("*.csv")):
        data = f.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("gb18030")
        for i, r in enumerate(csv.DictReader(io.StringIO(text))):
                me = (r.get("Main Entry") or "").strip()
                if not me:
                    continue
                detail = (r.get("Detail") or "").strip()
                sub = (r.get("Sub-entry") or "").strip()
                if "see under" in (sub + " " + detail).lower():
                    m = re.search(r"see under\s+(.+)$", (sub + " " + detail), re.I)
                    crossrefs.append((me, m.group(1).strip() if m else ""))
                    continue
                rows.append({
                    "file": f.name, "row": i, "main": me,
                    "sub": (r.get("Sub-entry") or "").strip(),
                    "location": (r.get("Location") or "").strip(),
                    "pages": (r.get("Page Numbers") or "").strip(),
                })

    # 别名 -> 规范名（"see under" 交叉引用）
    alias_to_canon = {a: c for a, c in crossrefs if c}

    by_main = defaultdict(list)
    for r in rows:
        by_main[r["main"]].append(r)

    cand_rows, type_count = [], Counter()
    for n, (main, rlist) in enumerate(sorted(by_main.items())):
        pages = ",".join(sorted({r["pages"] for r in rlist if r["pages"]}))
        typ = infer_type(main)
        type_count[typ] += 1
        aliases = "; ".join(sorted(a for a, c in alias_to_canon.items() if c == main))
        cand_rows.append({
            "candidate_id": f"cand-{n:04d}",
            "index_entry_id": main,
            "canonical_name": main,
            "aliases": aliases,
            "suggested_type": typ,
            "index_page_range": pages,
            "index_source_file": rlist[0]["file"],
            "status": "open",
        })

    cols = ["candidate_id", "index_entry_id", "canonical_name", "aliases",
            "suggested_type", "index_page_range", "index_source_file", "status"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in cand_rows:
            w.writerow(r)

    print(f"index rows: {len(rows)}")
    print(f"cross-references (see under): {len(crossrefs)}")
    print(f"unique main entries -> candidates: {len(cand_rows)}")
    print(f"type distribution: {dict(type_count)}")
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
