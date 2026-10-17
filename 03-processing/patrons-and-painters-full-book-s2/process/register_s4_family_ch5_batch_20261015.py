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
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-family-ch5"
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
        "group": "sg3-family-cand-0863",
        "candidate": "cand-0863",
        "slug": "corsini-family-florence",
        "name_zh": "科西尼家族",
        "name_en": "Corsini family",
        "description_zh": "哈斯克尔将 Corsini 与 Salviati 并列为佛罗伦萨 Cerquozzi 的热心欣赏者。另一处提到 Carmine 的 Corsini 礼拜堂，并仅称 del Rosso 兄弟可能促成 Luca Giordano 获得该委托；该段没有指出委托家族中的具体人物。",
        "description_en": "Haskell names the Corsini alongside the Salviati as keen admirers of Cerquozzi in Florence. Another passage mentions the Corsini chapel at the Carmine and says only that the del Rosso brothers may have helped secure Luca Giordano's commission; it does not identify a specific Corsini family member as the commissioner.",
        "context_zh": "第5章第142页将 Corsini 列为 Cerquozzi 的欣赏者；第8章第212页提及 Corsini 礼拜堂及 del Rosso 兄弟可能参与委托的说法。",
        "context_en": "Chapter 5 (p. 142) names the Corsini as admirers of Cerquozzi; Chapter 8 (p. 212) mentions the Corsini chapel and the possibility that the del Rosso brothers helped secure the commission.",
        "scope_zh": "保留原书的家族指称；不将礼拜堂名称当作独立家族成员，也不把可能的中介行为改写为已确认关系。",
        "scope_en": "This preserves the book's family reference; the chapel name is not treated as a family member, and the possible intermediary role is not rewritten as a confirmed relation.",
        "sources": [
            source("5", "142", "05_CHP-5_sec_iv.md", "7", "Cerquozzi’s keenest admirers, above all the Corsini and Salviati families.", "哈斯克尔称 Corsini 与 Salviati 是 Cerquozzi 的热心欣赏者。"),
            source("8", "212", "08_CHP-8_sec_i.md", "105", "it may well have been they who arranged for him to be given.the commission to paint the Corsini chapel in the Carmine", "哈斯克尔推测 del Rosso 兄弟可能安排 Luca Giordano 获得 Carmine 的 Corsini 礼拜堂委托。"),
        ],
    },
    {
        "group": "sg3-family-cand-2348",
        "candidate": "cand-2348",
        "slug": "salviati-family-florence",
        "name_zh": "萨尔维亚蒂家族",
        "name_en": "Salviati family",
        "description_zh": "哈斯克尔将 Salviati 与 Corsini 并列为佛罗伦萨 Cerquozzi 的热心欣赏者。原书此处没有点名具体家族成员，也没有把欣赏者表述为委托人。",
        "description_en": "Haskell names the Salviati alongside the Corsini as keen admirers of Cerquozzi in Florence. The passage names no individual family member and does not describe the admirers as commissioners.",
        "context_zh": "第5章第142页讨论 Cerquozzi 在佛罗伦萨的声望及其作品的欣赏者。",
        "context_en": "Chapter 5 (p. 142) discusses Cerquozzi's reputation in Florence and those who admired his work.",
        "scope_zh": "不从家族集体欣赏者身份推断赞助、委托或成员关系。",
        "scope_en": "The collective reference as admirers does not establish patronage, commissions, or individual membership relations.",
        "sources": [
            source("5", "142", "05_CHP-5_sec_iv.md", "7", "Cerquozzi’s keenest admirers, above all the Corsini and Salviati families.", "哈斯克尔称 Salviati 与 Corsini 是 Cerquozzi 的热心欣赏者。"),
        ],
    },
    {
        "group": "sg3-family-cand-6049",
        "candidate": "cand-6049",
        "slug": "rospigliosi-family",
        "name_zh": "罗丝皮廖西家族",
        "name_en": "Rospigliosi family",
        "description_zh": "哈斯克尔称 Rospigliosi 家族于1668年负责组织罗马圣若望斩首堂的年度展览，并以陈设的华丽程度超过此前主办者。文中接着说明教宗之弟 Camillo Rospigliosi 与其四子当时成为管理该堂的慈善团体的新成员。",
        "description_en": "Haskell says the Rospigliosi were responsible for the 1668 annual exhibition at San Giovanni Decollato and surpassed earlier organizers in the lavishness of the display. He adds that Camillo Rospigliosi, the Pope's brother, and his four sons had just become novices of the confraternity that administered the church.",
        "context_zh": "第5章第127页以 Rospigliosi 家族的展览组织和教会活动为例，讨论罗马家族对年度展览的支持。",
        "context_en": "Chapter 5 (p. 127) uses the Rospigliosi exhibition and church activity as an example of Roman family involvement in the annual event.",
        "scope_zh": "原文没有列出 Camillo 四子的姓名；本卡不据此补写家族成员清单，也不新增展览或慈善团体关系。",
        "scope_en": "The source does not name Camillo's four sons; this card does not add a membership list or create exhibition or confraternity relations.",
        "sources": [
            source("5", "127", "05_CHP-5_sec_i.md", "81", "Six years later the Rospigliosi were responsible and they challenged all previous patrons by the lavishness of the display they organised.", "哈斯克尔称六年后由 Rospigliosi 负责组织展览，其陈设之华丽超过此前主办者。"),
            source("5", "127", "05_CHP-5_sec_i.md", "81", "For Camillo Rospigliosi was the Pope’s brother, and he and his four sons had just been admitted as novices to the Compagnia della Misericordia which administered the church.", "哈斯克尔称 Camillo Rospigliosi 是教宗之弟，他与四子刚被接纳为管理该堂的慈善团体新成员。"),
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
    parser = argparse.ArgumentParser(description="S4 registration for ch. 5 family groups")
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

    assert len(manifest) == 1096, f"unexpected manifest count: {len(manifest)}"
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
    assert len(registered) == 77 and sum(map(len, registered.values())) == 83
    assert len(family_groups) == 80 and sum(map(len, family_groups.values())) == 85
    family_registered = {
        group: rows for group, rows in registered.items()
        if candidate_by_id[rows[0]["candidate_id"]].get("suggested_type") == "family"
    }
    assert len(family_registered) == 53 and sum(map(len, family_registered.values())) == 58

    batch_candidates = [record["candidate"] for record in BATCH]
    assert len(BATCH) == len(batch_candidates) == len(set(batch_candidates)) == 3
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
    assert len(planned_registered) == 80
    assert sum(len(rows) for rows in planned_registered.values()) == 86

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
