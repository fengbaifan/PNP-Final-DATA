from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-family-ch9-ch15-ch17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def source(chapter, page, file, lines, quote, summary):
    return {
        "chapter": chapter,
        "page": page,
        "file": file,
        "lines": lines,
        "quote": quote,
        "summary": summary,
    }


BATCH = [
    {
        "group": "sg3-family-cand-8313",
        "candidate": "cand-8313",
        "slug": "collalto-family",
        "name_zh": "科拉尔托家族",
        "name_en": "Collalto family",
        "description_zh": "哈斯克尔称，1794年 Pietro Novelli 记录了 Collalto 家族的伟大；他还称 Novelli 在回忆录中说明，记录该家族伟大是他自己选择的题材。",
        "description_en": "Haskell says that Pietro Novelli recorded the greatness of the Collalto family in 1794, and reports Novelli's own memoirs as saying that he chose the subject himself.",
        "context_zh": "第9章第254—255页将 Collalto 家族置于威尼斯家族史题材及画家选择题材的讨论中。",
        "context_en": "Chapter 9 (pp. 254–255) places the Collalto family in a discussion of Venetian family-history subjects and painters' choices of subject.",
        "scope_zh": "不据家族题材扩展成员名单、谱系或具体委托关系。",
        "scope_en": "The family-history subject does not establish a membership list, genealogy, or specific commission relation.",
        "sources": [
            source("9", "254", "09_CHP-9_intro.md", "142–143", "the artist Pietro Novelli recording the greatness of the\nCollalto.", "哈斯克尔称 Pietro Novelli 于共和国晚期记录 Collalto 家族的伟大。"),
            source("9", "255", "09_CHP-9_intro.md", "155", "Novelli specifically tells us in his Memoirs (p. 62) that it was he himself who chose to record the Greatness of the Collalto family.", "哈斯克尔转述 Novelli 回忆录称，记录 Collalto 家族的伟大是他自己选择的题材。"),
        ],
    },
    {
        "group": "sg3-family-cand-10431",
        "candidate": "cand-10431",
        "slug": "farsetti-family",
        "name_zh": "法尔塞蒂家族",
        "name_en": "Farsetti family",
        "description_zh": "哈斯克尔称 Filippo Farsetti 于1703年出生于一个极其富裕的家族，该家族到1664年才取得威尼斯贵族身份。本文候选索引页码为362，而对应的章节来源文件页眉标作302；卡片依实际引用的原文行及页眉定位，不把页码差异当作身份依据。",
        "description_en": "Haskell says Filippo Farsetti was born in 1703 into an exceedingly rich family that acquired Venetian patrician status only in 1664. The candidate index gives p. 362, while the linked chapter source marks the passage as p. 302; the card cites the source text and page marker without using the page discrepancy as identity evidence.",
        "context_zh": "第15章第302页在介绍 Filippo 的艺术赞助时，同时说明其出生家族的财富和取得贵族身份的年份。",
        "context_en": "Chapter 15 (p. 302), while introducing Filippo's artistic patronage, also states the wealth and ennoblement date of his birth family.",
        "scope_zh": "本卡登记 Filippo 的出生家族这一集体对象，不与 Filippo Farsetti 人物 KU 合并，也不补写完整家谱。",
        "scope_en": "This card registers Filippo's birth family as a collective entity, separate from the person KU for Filippo Farsetti, and does not supply a full genealogy.",
        "sources": [
            source("15", "302", "15_CHP-15_sec_i.md", "17", "He was born in 1703 of an exceedingly rich family that had only acquired patrician status in 1664", "哈斯克尔称 Filippo Farsetti 于1703年出生于一个极富裕、至1664年才取得贵族身份的家族。"),
        ],
    },
    {
        "group": "sg3-family-cand-10707",
        "candidate": "cand-10707",
        "slug": "molin-family",
        "name_zh": "莫林家族",
        "name_en": "Molin family",
        "description_zh": "哈斯克尔称，Teodoro Correr 的许多绘画来自包括 Molin 在内的威尼斯显贵商人家族。原文未指定具体家族成员或逐件作品来源。",
        "description_en": "Haskell says many of Teodoro Correr's pictures came from prominent patrician and trading families, including the Molin. The passage identifies neither individual family members nor the source of each work.",
        "context_zh": "第17章第382页将 Molin 与 Orsetti、Pellegrini 并列为 Correr 收藏的来源家族。",
        "context_en": "Chapter 17 (p. 382) names the Molin alongside the Orsetti and Pellegrini among sources of Correr's collection.",
        "scope_zh": "“来自该家族”只按原文宽泛来源语句保留，不改写为赠与、借展或确定的所有权链。",
        "scope_en": "The source's broad statement that pictures came from the family is preserved without recasting it as a gift, loan, or established chain of ownership.",
        "sources": [
            source("17", "382", "17_CHP-17_sec_ii.md", "10", "We know that he obtained many of his pictures from the great patrician and trading families—especially the Molin, the Orsetti and the Pellegrini", "哈斯克尔称 Correr 的许多绘画来自显贵商人家族，特别提到 Molin、Orsetti 和 Pellegrini。"),
        ],
    },
    {
        "group": "sg3-family-cand-10708",
        "candidate": "cand-10708",
        "slug": "orsetti-family",
        "name_zh": "奥尔塞蒂家族",
        "name_en": "Orsetti family",
        "description_zh": "哈斯克尔称，Teodoro Correr 的许多绘画来自包括 Orsetti 在内的威尼斯显贵商人家族。原文未指定具体家族成员或逐件作品来源。",
        "description_en": "Haskell says many of Teodoro Correr's pictures came from prominent patrician and trading families, including the Orsetti. The passage identifies neither individual family members nor the source of each work.",
        "context_zh": "第17章第382页将 Orsetti 与 Molin、Pellegrini 并列为 Correr 收藏的来源家族。",
        "context_en": "Chapter 17 (p. 382) names the Orsetti alongside the Molin and Pellegrini among sources of Correr's collection.",
        "scope_zh": "“来自该家族”只按原文宽泛来源语句保留，不改写为赠与、借展或确定的所有权链。",
        "scope_en": "The source's broad statement that pictures came from the family is preserved without recasting it as a gift, loan, or established chain of ownership.",
        "sources": [
            source("17", "382", "17_CHP-17_sec_ii.md", "10", "We know that he obtained many of his pictures from the great patrician and trading families—especially the Molin, the Orsetti and the Pellegrini", "哈斯克尔称 Correr 的许多绘画来自显贵商人家族，特别提到 Orsetti、Molin 和 Pellegrini。"),
        ],
    },
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note: str) -> str | None:
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def make_card(record: dict) -> str:
    sources = []
    for item in record["sources"]:
        sources.append(
            {
                "citation": f"{BOOK_CITATION}, ch. {item['chapter']}, p. {item['page']}.",
                "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}",
                "sentence_summary": item["summary"],
                "original_quotes": [
                    {"source_span": f"lines {item['lines']}", "text": item["quote"]}
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": f"02-sources/02-Markdown/{item['file']}",
                    "source_span": f"lines {item['lines']}; print p. {item['page']}",
                },
            }
        )
    frontmatter = {
        "title": f"{record['name_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": "family",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-15",
        "updated": "2026-10-15",
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {record['description_zh']}

**English:** {record['description_en']}

### 名称

中文显示名为{record['name_zh']}；英文名及原书所用家族名称为 {record['name_en']}。中文显示名为便于阅读所用的音译，不表示书中另有中文规范名。

The Chinese display name is a transliteration for readability. The English name and family form used in the book are {record['name_en']}.

### 本书语境

{record['context_zh']}

{record['context_en']}

### 身份边界

中文：{record['scope_zh']}

English: {record['scope_en']}

## 关系与证据

本轮完成身份登记；正文中的家族成员、收藏与赞助陈述仍须按各自来源和端点在 S6 审查。本卡未新增正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="S4 registration for ch. 9, 15, and 17 family groups")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.apply:
        parser.error("choose exactly one of --dry-run or --apply")

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    candidate_path = TABLES / "entity-candidates.csv"
    statements_path = TABLES / "book-statements.jsonl"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(candidate_path)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {
        r["candidate_id"]: r for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    candidate_endpoints = set()
    with statements_path.open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            candidate_endpoints.update(
                cid for cid in (
                    statement.get("subject_candidate_id"),
                    statement.get("object_candidate_id"),
                ) if cid
            )

    assert len(manifest) == 1099, f"unexpected manifest count: {len(manifest)}"
    new_rows = [r for r in alignments if not r.get("external_source") and r.get("decision") == "new"]
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    registered: dict[str, list[dict[str, str]]] = defaultdict(list)
    family_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
        if candidate_by_id[row["candidate_id"]].get("suggested_type") == "family":
            family_groups[group].append(row)
    assert len(new_rows) == 5007 and len(groups) == 4830
    assert len(registered) == 80 and sum(map(len, registered.values())) == 86
    assert len(family_groups) == 80 and sum(map(len, family_groups.values())) == 85
    family_registered = {
        group: rows for group, rows in registered.items()
        if candidate_by_id[rows[0]["candidate_id"]].get("suggested_type") == "family"
    }
    assert len(family_registered) == 56 and sum(map(len, family_registered.values())) == 61

    batch_candidates = [record["candidate"] for record in BATCH]
    assert len(BATCH) == len(batch_candidates) == len(set(batch_candidates)) == 4
    for record in BATCH:
        candidate_id = record["candidate"]
        candidate = candidate_by_id[candidate_id]
        alignment = alignment_by_id[candidate_id]
        assert candidate.get("suggested_type") == "family"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == record["group"]
        assert candidate_id in candidate_endpoints, f"not a direct S2 endpoint: {candidate_id}"
        path = UNITS / "families" / f"{record['slug']}.md"
        rel_path = f"04-knowledge/units/families/{record['slug']}.md"
        ku_id = f"units/families/{record['slug']}"
        assert not path.exists(), f"refusing to overwrite {path}"
        assert not any(r["ku_id"] == ku_id or r["card_path"] == rel_path for r in manifest)
        assert rel_path not in accepted_text
        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (
                record["slug"], item["quote"]
            )

    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {
        r["candidate_id"]: r for r in planned_alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    for record in BATCH:
        candidate_id = record["candidate"]
        ku_id = f"units/families/{record['slug']}"
        row = planned_by_id[candidate_id]
        row["ku_id"] = ku_id
        row["resolution_note"] += f" S4 registration: mapped {record['group']} to {ku_id}."

    planned_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in planned_alignments:
        if row.get("external_source") or row.get("decision") != "new":
            continue
        planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {
        group: rows for group, rows in planned_groups.items() if any(r.get("ku_id") for r in rows)
    }
    for group, rows in planned_registered.items():
        mapped = [r for r in rows if r.get("ku_id")]
        assert len(mapped) == len(rows) and len({r["ku_id"] for r in rows}) == 1, group
    assert len(planned_registered) == 84
    assert sum(len(rows) for rows in planned_registered.values()) == 90

    if args.dry_run:
        print(
            f"dry-run passed: family_groups={len(BATCH)} candidates={len(batch_candidates)} "
            f"registered_groups={len(planned_registered)} registered_candidates="
            f"{sum(len(rows) for rows in planned_registered.values())} "
            f"manifest_after={len(manifest) + len(BATCH)}"
        )
        return 0

    for record in BATCH:
        path = UNITS / "families" / f"{record['slug']}.md"
        path.write_text(make_card(record), encoding="utf-8-sig", newline="\n")
        manifest.append(
            {
                "ku_id": f"units/families/{record['slug']}",
                "type": "family",
                "canonical_name": record["name_zh"],
                "name_en": record["name_en"],
                "source_task": TASK,
                "card_path": f"04-knowledge/units/families/{record['slug']}.md",
            }
        )
    write_csv(manifest_path, manifest_fields, manifest)
    write_csv(alignment_path, alignment_fields, planned_alignments)
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/institutions/")),
        len(accepted_lines),
    )
    accepted_lines[insert_at:insert_at] = [
        f"- 04-knowledge/units/families/{record['slug']}.md" for record in BATCH
    ]
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(
        f"applied {len(BATCH)} family groups and {len(batch_candidates)} candidate mappings; "
        f"manifest={len(manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
