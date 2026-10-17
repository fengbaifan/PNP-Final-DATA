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
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-family-ch7-ch8"
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
        "group": "sg3-family-cand-1406",
        "candidate": "cand-1406",
        "slug": "liechtenstein-family",
        "name_zh": "列支敦士登家族",
        "name_en": "Liechtenstein family",
        "description_zh": "哈斯克尔称，哈布斯堡领地内新教势力失败后发生的没收使列支敦士登家族大为富裕，并称该家族仅向博洛尼亚画家 Marcantonio Franceschini 订购了42幅画。",
        "description_en": "Haskell says confiscations following Protestant defeats in the Habsburg dominions greatly enriched the Liechtenstein family, which ordered forty-two paintings from the Bolognese painter Marcantonio Franceschini alone.",
        "context_zh": "第7章第194页将列支敦士登家族置于德意志诸侯委托意大利艺术家的赞助语境。",
        "context_en": "Chapter 7 (p. 194) places the Liechtenstein family in the context of German princely patronage of Italian artists.",
        "scope_zh": "保留 Haskell 对家族财富来源及委托数量的叙述，不据此展开支系、成员或所有权史。",
        "scope_en": "This preserves Haskell's account of the family's wealth and commission count without expanding its branches, membership, or property history.",
        "sources": [
            source("7", "194", "07_CHP-7_sec_iv.md", "29", "The Liechtenstein family, which had been greatly enriched by the expropriations that followed Protestant defeats in the Hapsburg dominions, ordered forty-two paintings from the Bolognese Marcantonio Franceschini alone.", "哈斯克尔将列支敦士登家族的财富与哈布斯堡领地的没收相联系，并称该家族单独向 Franceschini 订购42幅画。"),
        ],
    },
    {
        "group": "sg3-family-cand-6657",
        "candidate": "cand-6657",
        "slug": "crescenzi-family-rome",
        "name_zh": "克雷申齐家族",
        "name_en": "Crescenzi family",
        "description_zh": "哈斯克尔称 Giovanni Battista Crescenzi 出身罗马贵族家族，其兄为枢机；两人都是艺术赞助者与收藏者，并较早委托 Claude 创作宫殿壁画。该段未说明其兄的姓名。",
        "description_en": "Haskell says Giovanni Battista Crescenzi came from a noble Roman family and that his brother was a cardinal. The two were patrons and collectors who were among the early employers of Claude for frescoes in their palace; the passage does not name the brother.",
        "context_zh": "第7章第173页以 Giovanni Battista Crescenzi 及其兄弟的艺术赞助活动说明西班牙宫廷与意大利艺术家的联系。",
        "context_en": "Chapter 7 (p. 173) uses Giovanni Battista Crescenzi and his brother's patronage to discuss links between the Spanish court and Italian artists.",
        "scope_zh": "不补写兄长姓名、家族支系或未经该段直接支持的成员关系。",
        "scope_en": "No name for the brother, family branch, or membership relation beyond what this passage directly supports is added.",
        "sources": [
            source("7", "173", "07_CHP-7_sec_i.md", "38", "Giovanni Battista Crescenzi, who was born in 1577, came of a noble Roman family.", "哈斯克尔称 Giovanni Battista Crescenzi 于1577年出生，出身罗马贵族家族。"),
            source("7", "173", "07_CHP-7_sec_i.md", "38", "His brother was a cardinal and the two men were not only enthusiastic patrons and collectors but also among the very first to employ Claude, who painted frescoes in their palace.", "哈斯克尔称 Crescenzi 的兄弟为枢机，两人都是赞助者与收藏者，并较早雇用 Claude 为其宫殿绘制壁画。"),
        ],
    },
    {
        "group": "sg3-family-cand-6673",
        "candidate": "cand-6673",
        "slug": "gondi-family",
        "name_zh": "贡迪家族",
        "name_en": "Gondi family",
        "description_zh": "哈斯克尔称贡迪家族源自佛罗伦萨，约在其叙述所涉时期前50年迁居巴黎；Marie de Medici 抵达巴黎后曾短暂居于贡迪家族的宫殿。",
        "description_en": "Haskell describes the Gondi as a Florentine family that had settled in Paris about fifty years earlier; Marie de Medici stayed briefly in the family's palace after arriving in Paris.",
        "context_zh": "第7章第174页将贡迪宫殿、家族的佛罗伦萨渊源及其定居巴黎的记载联系起来。",
        "context_en": "Chapter 7 (p. 174) connects the Gondi palace with the family's Florentine origin and settlement in Paris.",
        "scope_zh": "家族与候选 `cand-1212` 所指的 Gondi 宫殿分属不同对象；不扩展完整迁徙史或成员清单。",
        "scope_en": "The family is distinct from the Gondi palace represented by candidate `cand-1212`; no complete migration history or membership list is added.",
        "sources": [
            source("7", "174", "07_CHP-7_sec_i.md", "48–49", "she stayed for a time in the splendid palace of the Gondi, a\nFlorentine family which had settled in Paris some fifty years earlier.", "哈斯克尔称 Marie de Medici 曾暂居贡迪宫殿，并说明该家族源自佛罗伦萨且约50年前迁居巴黎。"),
        ],
    },
    {
        "group": "sg3-family-cand-7154",
        "candidate": "cand-7154",
        "slug": "wittelsbach-dynasty",
        "name_zh": "维特尔斯巴赫王朝",
        "name_en": "Wittelsbach dynasty",
        "description_zh": "哈斯克尔称三十年战争后迅速恢复的王朝之一是慕尼黑的 Wittelsbach；1652年选帝侯 Ferdinand Maria 与 Savoy 的 Adelaide Enrichetta 结婚后，两家建立联姻关系。",
        "description_en": "Haskell names the Wittelsbach in Munich as a dynasty that recovered relatively quickly after the Thirty Years' War. In 1652, Elector Ferdinand Maria's marriage to Adelaide Enrichetta of Savoy allied the two ruling families.",
        "context_zh": "第7章第193页以 Wittelsbach 家族为慕尼黑艺术赞助与意大利艺术家活动的语境。",
        "context_en": "Chapter 7 (p. 193) places the Wittelsbach dynasty in the context of artistic patronage in Munich and Italian artists' activity there.",
        "scope_zh": "本卡保留书中对王朝的集体指称，不枚举成员、支系或继承序列。",
        "scope_en": "This card preserves the book's collective dynastic reference and does not enumerate members, branches, or succession.",
        "sources": [
            source("7", "193", "07_CHP-7_sec_iv.md", "14–15", "Another dynasty that recovered with some speed from the effects of the Thirty\nYears War was that of the Wittelsbachs in Munich.", "哈斯克尔称三十年战争后较快恢复的另一王朝是慕尼黑的 Wittelsbach。"),
            source("7", "193", "07_CHP-7_sec_iv.md", "15–16", "when, in 1652, the Elector Ferdinand Maria married\nAdelaide Enrichetta of Savoy they found themselves allied to the most astute ruling family in Europe.3", "哈斯克尔称 Ferdinand Maria 于1652年与 Savoy 的 Adelaide Enrichetta 结婚后，两家形成联姻联盟。"),
        ],
    },
    {
        "group": "sg3-family-cand-7699",
        "candidate": "cand-7699",
        "slug": "cibo-family",
        "name_zh": "奇博家族",
        "name_en": "Cibo family",
        "description_zh": "哈斯克尔称枢机 Tommaso Ruffo 晚年在罗马居住，并从 Cibo 家族购得 Trevi 喷泉对面的宫殿。书中未指出具体出售者或家族支系。",
        "description_en": "Haskell says Cardinal Tommaso Ruffo lived in Rome in old age and bought the palace opposite the Trevi Fountain from the Cibo family. The book does not identify an individual seller or family branch.",
        "context_zh": "第8章第221页将 Cibo 家族列为 Ruffo 购置罗马宫殿时的前持有方。",
        "context_en": "Chapter 8 (p. 221) names the Cibo family as the former holder from whom Ruffo acquired a Roman palace.",
        "scope_zh": "不从宫殿转手推断卖方个人、确切支系或完整产权链。",
        "scope_en": "The palace transfer does not establish an individual seller, exact branch, or complete chain of title.",
        "sources": [
            source("8", "221", "08_CHP-8_sec_ii.md", "121", "Fountain which he bought from the Cibo family.", "哈斯克尔称 Ruffo 购得 Trevi 喷泉对面的罗马宫殿，前持有方为 Cibo 家族。"),
        ],
    },
    {
        "group": "sg3-family-cand-7840",
        "candidate": "cand-7840",
        "slug": "bibbiena-family",
        "name_zh": "比比耶纳家族",
        "name_en": "Bibbiena family",
        "description_zh": "哈斯克尔称，Ferdinand 在 Pratolino 的剧院曾雇用领先的舞台设计师，其中包括 Bibbiena 家族成员。该段没有点名具体设计师。",
        "description_en": "Haskell says Ferdinand employed leading stage designers for his theatre at Pratolino, including members of the Bibbiena family. The passage does not name a specific designer.",
        "context_zh": "第8章第230页将 Bibbiena 家族成员置于 Ferdinand 剧院舞台设计工作的语境。",
        "context_en": "Chapter 8 (p. 230) places members of the Bibbiena family in the context of stage-design work for Ferdinand's theatre.",
        "scope_zh": "不根据家族集体称谓推定具体成员身份或设计项目清单。",
        "scope_en": "The collective family reference does not establish individual identities or a list of design projects.",
        "sources": [
            source("8", "230", "08_CHP-8_sec_ii.md", "229", "His theatre at Pratolino was famous throughout Italy and for it he employed leading stage designers such as members of the Bibbiena family.", "哈斯克尔称 Ferdinand 为 Pratolino 剧院雇用领先舞台设计师，其中包括 Bibbiena 家族成员。"),
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
    parser = argparse.ArgumentParser(description="S4 registration for ch. 7–8 family groups")
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

    assert len(manifest) == 1090, f"unexpected manifest count: {len(manifest)}"
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
    assert len(registered) == 71 and sum(map(len, registered.values())) == 77
    assert len(family_groups) == 80 and sum(map(len, family_groups.values())) == 85
    family_registered = {
        group: rows for group, rows in registered.items()
        if candidate_by_id[rows[0]["candidate_id"]].get("suggested_type") == "family"
    }
    assert len(family_registered) == 47 and sum(map(len, family_registered.values())) == 52

    batch_candidates = [record["candidate"] for record in BATCH]
    assert len(BATCH) == len(batch_candidates) == len(set(batch_candidates)) == 6
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
    assert len(planned_registered) == 77
    assert sum(len(rows) for rows in planned_registered.values()) == 83

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
