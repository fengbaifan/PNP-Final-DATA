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
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-family-ch6-ch7-ch10"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def source(chapter, page, file, lines, quote, summary, location_note=""):
    return {
        "chapter": chapter,
        "page": page,
        "file": file,
        "lines": lines,
        "quote": quote,
        "summary": summary,
        "location_note": location_note,
    }


BATCH = [
    {
        "group": "sg3-family-cand-2400",
        "candidate": "cand-2400",
        "slug": "schonborn-family",
        "name_zh": "舍恩博恩家族",
        "name_en": "Schönborn family",
        "description_zh": "哈斯克尔称 Pommersfelden 的 Schönborn 家族委托多地意大利画家创作，并将该家族列为资助 Lateran 圣殿艺术的德意志赞助者。第10章后记段落回指其既述赞助，并称该主教区曾属 Schönborn 家族。OCR 拼写包括 `Schônborn` 和不带变音符号的 `Schonborn`。",
        "description_en": "Haskell says the Schönborn family of Pommersfelden commissioned Italian painters in several cities and lists the family among German patrons who paid for art at the Lateran basilica. A later Chapter 10 passage refers back to the family's previously discussed patronage and says the bishopric had belonged to the Schönborn family. OCR forms include `Schônborn` and `Schonborn` without the umlaut.",
        "context_zh": "第6章第163页与第7章第194页记载家族为 Lateran 圣殿及 Pommersfelden 委托艺术；第10章第293、296页回顾其赞助与主教区归属。",
        "context_en": "Chapter 6 (p. 163) and Chapter 7 (p. 194) describe the family's Lateran and Pommersfelden patronage; Chapter 10 (pp. 293, 296) revisits that patronage and the bishopric's association with the family.",
        "scope_zh": "此卡保留书中对家族的集体称谓及书内交叉指引，不据此推断完整支系或成员名单。",
        "scope_en": "This card preserves the book's collective family reference and internal cross-reference without inferring a complete branch structure or membership list.",
        "sources": [
            source("6", "163", "06_CHP-6_sec_v.md", "25", "including the Schönborn family of Pommersfelden in Franconia, had to pay for most of them.", "哈斯克尔称 Pommersfelden 的 Schönborn 家族等德意志赞助者为 Lateran 圣殿的大部分艺术品付费。"),
            source("7", "194", "07_CHP-7_sec_iv.md", "29–31", "At Pommersfelden in Franconia the Schônborn family commissioned pictures from Antonio\nBalestra and Gregorio Lazzarini in Venice; Carlo Maratta, Benedetto Luti and Francesco\nTrevisani in Rome; Luca Giordano and Francesco Solimena in Naples; Carlo Cignani in Bologna.", "哈斯克尔称 Pommersfelden 的 Schönborn 家族委托威尼斯、罗马、那不勒斯和博洛尼亚画家创作。"),
            source("10", "293", "10_CHP-10_intro.md", "290", "the Hapsburgs and Schönborns who had hitherto stuck to the more traditional late-Baroque artists were now ready to welcome Pellegrini, Ricci and Rosalba Camera", "哈斯克尔称 Hapsburg 与 Schönborn 家族开始接受 Pellegrini、Ricci 和 Rosalba Camera 等艺术家。"),
            source("10", "296", "10_CHP-10_intro.md", "320", "The bishopric had belonged to the Schonborn family, whose vast patronage has already been referred to", "哈斯克尔回指已述的 Schönborn 家族赞助，并称该主教区曾属该家族。"),
        ],
    },
    {
        "group": "sg3-family-cand-9568",
        "candidate": "cand-9568",
        "slug": "house-of-savoy",
        "name_zh": "萨伏依王室",
        "name_en": "House of Savoy",
        "description_zh": "哈斯克尔称 Johann Matthias Schulenburg 曾为 House of Savoy 作战。原书此处指王朝／家族，不指地理对象 Savoy；两类对象分别保留。",
        "description_en": "Haskell says Johann Matthias Schulenburg fought for the House of Savoy. The passage refers to the ruling house, not the geographic place Savoy; the two entity types remain separate.",
        "context_zh": "第10章第311页在叙述 Schulenburg 的军事经历时列出 House of Savoy。来源 OCR 页面标记异常读作 `1661`，候选过程定位为第311页；本卡保留该定位差异供后续原件核对。",
        "context_en": "Chapter 10 (p. 311) names the House of Savoy in its account of Schulenburg's military service. The OCR page marker reads `1661`, while the candidate process locates the passage at p. 311; this discrepancy is retained for later source-image review.",
        "scope_zh": "不把 House of Savoy 与地理候选 `cand-2379` Savoy 合并。",
        "scope_en": "Do not merge the House of Savoy with the geographic candidate `cand-2379` for Savoy.",
        "sources": [
            source("10", "311", "10_CHP-10_sec_ii.md", "10", "Hungarians and for the House of Savoy", "哈斯克尔称 Schulenburg 曾为匈牙利人和 House of Savoy 作战。", "候选过程定位页311；来源 OCR 页码标记 L7 读作1661。"),
        ],
    },
    {
        "group": "sg3-family-cand-9570",
        "candidate": "cand-9570",
        "slug": "hanoverian-dynasty",
        "name_zh": "汉诺威王朝",
        "name_en": "Hanoverian dynasty",
        "description_zh": "哈斯克尔称 Schulenburg 与 Hanoverian 王朝有密切亲属关系，但没有指明具体亲属或谱系。",
        "description_en": "Haskell says Schulenburg was closely related to the Hanoverian dynasty but identifies no particular relative or line of descent.",
        "context_zh": "第10章第311页在回顾 Schulenburg 退休后的社交关系时提及 Hanoverian 王朝。来源 OCR 页面标记异常读作 `1661`，候选过程定位为第311页；本卡保留该定位差异供后续原件核对。",
        "context_en": "Chapter 10 (p. 311) mentions the Hanoverian dynasty in its account of Schulenburg's retirement and social connections. The OCR page marker reads `1661`, while the candidate process locates the passage at p. 311; this discrepancy is retained for later source-image review.",
        "scope_zh": "不补写 Schulenburg 与王朝内任何具体人物的亲属关系。",
        "scope_en": "No kinship relation between Schulenburg and a specific member of the dynasty is added.",
        "sources": [
            source("10", "311", "10_CHP-10_sec_ii.md", "13", "He was closely related to the Hanoverian dynasty", "哈斯克尔称 Schulenburg 与 Hanoverian 王朝有密切亲属关系，但未点名具体亲属。", "候选过程定位页311；来源 OCR 页码标记 L7 读作1661。"),
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
                "location": f"第{item['chapter']}章，候选过程定位印刷页{item['page']}；OCR L{item['lines']} {item['location_note']}",
                "sentence_summary": item["summary"],
                "original_quotes": [
                    {"source_span": f"lines {item['lines']}", "text": item["quote"]}
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": f"02-sources/02-Markdown/{item['file']}",
                    "source_span": f"lines {item['lines']}; candidate print p. {item['page']}; {item['location_note']}",
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

中文显示名为{record['name_zh']}；英文名及原书所用名称为 {record['name_en']}。中文显示名为便于阅读所用的音译，不表示书中另有中文规范名。

The Chinese display name is a transliteration for readability. The English name and form used in the book are {record['name_en']}.

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
    parser = argparse.ArgumentParser(description="S4 registration for ch. 6–7 and 10 family groups")
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

    assert len(manifest) == 1103, f"unexpected manifest count: {len(manifest)}"
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
    assert len(registered) == 84 and sum(map(len, registered.values())) == 90
    assert len(family_groups) == 80 and sum(map(len, family_groups.values())) == 85
    family_registered = {
        group: rows for group, rows in registered.items()
        if candidate_by_id[rows[0]["candidate_id"]].get("suggested_type") == "family"
    }
    assert len(family_registered) == 60 and sum(map(len, family_registered.values())) == 65

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
    assert len(planned_registered) == 87
    assert sum(len(rows) for rows in planned_registered.values()) == 93

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
