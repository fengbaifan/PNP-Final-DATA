from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
GROUPS = {
    "cand-0815": {
        "group": "sg3-place-colonnapalace",
        "ku_id": "units/places/colonna-family-palace-rome",
        "card_rel": "04-knowledge/units/places/colonna-family-palace-rome.md",
        "card_path": ROOT / "04-knowledge" / "units" / "places" / "colonna-family-palace-rome.md",
        "name_zh": "罗马科隆纳家族宫殿",
        "name_en": "Colonna Family Palace, Rome",
    },
    "cand-0816": {
        "group": "sg3-place-chigi-palace-ss-apostoli",
        "ku_id": "units/places/flavio-chigi-palace-ss-apostoli",
        "card_rel": "04-knowledge/units/places/flavio-chigi-palace-ss-apostoli.md",
        "card_path": ROOT / "04-knowledge" / "units" / "places" / "flavio-chigi-palace-ss-apostoli.md",
        "name_zh": "罗马圣使徒广场弗拉维奥·基吉枢机宫殿",
        "name_en": "Flavio Chigi's Palace, Piazza SS. Apostoli, Rome",
    },
}
RELATION_IDS = {
    "cand-0815": {
        "st-chp6-p155-colonna-palace-decorated-by-girolamo",
        "st-chp6-p155-colonna-palace-rebuilt",
        "st-chp6-p155-grimaldi-landscape-decoration",
        "st-chp6-p155-maria-impression-of-palace",
    },
    "cand-0816": {
        "st-chp6-p155-bernin-reconstruction-delayed",
        "st-chp6-p154-chigi-palace-at-ss-apostoli",
        "st-chp6-p154-chigi-palace-has-canini-ceilings",
        "st-chp6-p154-chigi-palace-has-gaulli-paintings",
        "st-chp6-p154-chigi-palace-has-antique-statues",
    },
}
NON_RELATION_IDS = {
    "cand-0815": set(),
    "cand-0816": {
        "st-chp6-p154-collection-less-distinguished",
        "st-chp6-p154-palace-facade-interior-contrast",
        "st-chp6-p154-some-fine-pictures-in-collection",
    },
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_frontmatter(item, sources):
    return yaml.safe_dump(
        {
            "title": f"{item['name_zh']}（{item['name_en']}）",
            "name_en": item["name_en"],
            "type": "place",
            "evidence_status": "source_backed",
            "sources": sources,
            "created": "2026-10-17",
            "updated": "2026-10-17",
            "process_ref": f"03-processing/{TASK}/process/knowledge.md",
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )


def colonna_card() -> str:
    item = GROUPS["cand-0815"]
    sources = [
        {
            "citation": BOOK,
            "location": "第6章；印刷页155；OCR L102–110",
            "sentence_summary": "Haskell 将 Colonna 家族宫殿与售给 Chigi 的另一座宫殿区分开，称其位于后者附近，并记述 Filippo 与 Cardinal Girolamo Colonna 在本世纪上半叶重建和装饰了它。",
            "original_quotes": [
                {"source_span": "lines 102–110", "text": "Their palace, situated near the one sold to the Chigi"},
                {"source_span": "lines 102–110", "text": "had been largely rebuilt and decorated by Filippo and his son, Cardinal Girolamo"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "source_span": "lines 102–110; print p. 155",
            },
        },
    ]
    fm = make_frontmatter(item, sources)
    p155 = "[第6章 p.155](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L102–110）"
    body = f"""## 内容

### 描述

**中文：** 本卡指第6章 p.155 所称的科隆纳家族宫殿。Haskell 明确说它位于“卖给 Chigi 的那座宫殿”附近，并将其重建、装饰归于 Filippo Colonna 与其子 Cardinal Girolamo Colonna，时间为本世纪上半叶。原书未给出建筑正式名称，本卡使用描述性工作名。{p155}

**English:** This card identifies the Colonna family palace described on p.155 of Chapter 6. Haskell explicitly places it near “the one sold to the Chigi” and attributes its rebuilding and decoration during the first half of the century to Filippo Colonna and his son, Cardinal Girolamo Colonna. The book does not supply a formal building name; this card uses a descriptive working name. {p155}

### 身份边界

- 对应 S3 候选 `cand-0815`（C.csv#345；索引形式 `Colonna palace, Rome`）。
- 与位于 Piazza SS. Apostoli、1662年由 Colonna 家族一支售给 Flavio Chigi 的另一座宫殿 `cand-0816` 分开；p.155 明称两者相邻。
- 本卡仅记录来源内建筑身份与原书描述，不推定具体建筑的现存状态或未经来源给出的正式名称。

### 关系与证据

以下4条 S2 关系候选留待 S6；本卡未新增正式关系：

- `st-chp6-p155-colonna-palace-decorated-by-girolamo`
- `st-chp6-p155-colonna-palace-rebuilt`
- `st-chp6-p155-grimaldi-landscape-decoration`
- `st-chp6-p155-maria-impression-of-palace`
"""
    return f"---\n{fm}---\n\n{body}"


def chigi_card() -> str:
    item = GROUPS["cand-0816"]
    sources = [
        {
            "citation": BOOK,
            "location": "第6章；印刷页154；OCR L91–100",
            "sentence_summary": "Haskell 称 Cardinal Flavio Chigi 于1662年向 Colonna 家族一支购入位于 Piazza SS. Apostoli 的宫殿，并雇 Bernini 建造或重建；屋内包括 Mei、Canini、Gaulli 的装饰/作品及古代雕像。",
            "original_quotes": [
                {"source_span": "lines 91–100", "text": "the palace in piazza SS. Apostoli which he bought from a branch of the Colonna family in 1662"},
                {"source_span": "lines 91–100", "text": "a spectacular façade with colossal pilasters"},
                {"source_span": "lines 91–100", "text": "antique statues in plenty"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "source_span": "lines 91–100; print p. 154",
            },
        },
        {
            "citation": BOOK,
            "location": "第6章；印刷页155；OCR L102–110",
            "sentence_summary": "Haskell 说 Bernini 到 Alexander VII 在位近十年后才开始重建这座 Chigi 宫殿；同页随后把另一座 Colonna 家族宫殿称为位于售给 Chigi 的宫殿附近。",
            "original_quotes": [
                {"source_span": "lines 102–110", "text": "Bernini did not begin to reconstruct the palace until Alexander VII had been on the throne for nearly ten years"},
                {"source_span": "lines 102–110", "text": "Their palace, situated near the one sold to the Chigi"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "source_span": "lines 102–110; print p. 155",
            },
        },
        {
            "citation": "Francis Haskell, *Patrons and Painters*, index",
            "location": "书后索引 C.csv#346；印刷页140注、154",
            "sentence_summary": "索引以 Colonna palace, Rome 为主项，并以 sale to Cardinal Flavio Chigi 子项定位 p.140 注和 p.154；仅作书内定位。",
            "original_quotes": [{"source_span": "C.csv#346", "text": "Colonna palace, Rome — sale to Cardinal Flavio Chigi"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/22_CHP-22Index.md",
                "source_span": "lines 1053–1054",
            },
        },
    ]
    fm = make_frontmatter(item, sources)
    p154 = "[第6章 p.154](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L91–100）"
    p155 = "[第6章 p.155](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L102–110）"
    index = "[书后索引 C.csv#346](../../../02-sources/02-Markdown/22_CHP-22Index.md)（L1053–1054）"
    body = f"""## 内容

### 描述

**中文：** 本卡指第6章记述的 Cardinal Flavio Chigi 宫殿：Haskell 称它位于 Piazza SS. Apostoli，Flavio 于1662年向 Colonna 家族一支购入，并雇 Bernini 建造或重建。原书提到 Mei 的顶棚壁画、Canini 的其他顶棚、Gaulli 的神话画和肖像，以及大量古代雕像；p.155 说 Bernini 到 Alexander VII 在位近十年后才开始重建。名称为位置和人物限定的描述性工作名。{p154}；{p155}

**English:** This card identifies Cardinal Flavio Chigi's palace described in Chapter 6. Haskell locates it in Piazza SS. Apostoli, says Flavio bought it from a branch of the Colonna family in 1662, and says he employed Bernini to build or rebuild it. The book mentions ceiling paintings by Mei, other ceilings by Canini, mythological paintings and portraits by Gaulli, and numerous antique statues; p.155 says Bernini began rebuilding only after Alexander VII had been pope for nearly ten years. The name is a descriptive working label based on place and patron. {p154}; {p155}

### 身份边界

- 对应 S3 候选 `cand-0816`（C.csv#346；索引子项 `sale to Cardinal Flavio Chigi`）。索引提供定位；人物、地点和购买语境以正文为身份依据。{index}
- p.154 的 Chigi 宫殿与 p.155 所称 Colonna family palace 是两座相邻建筑：后者“situated near the one sold to the Chigi”。因此本卡不与[罗马科隆纳家族宫殿](colonna-family-palace-rome.md)合并。
- Haskell 将其购入、建造/重建和陈设逐项转述；原始产权记录、建筑档案和艺术品现状未独立查阅。

### 关系与证据

以下5条 S2 关系候选留待 S6；本卡未新增正式关系：

- `st-chp6-p155-bernin-reconstruction-delayed`
- `st-chp6-p154-chigi-palace-at-ss-apostoli`
- `st-chp6-p154-chigi-palace-has-canini-ceilings`
- `st-chp6-p154-chigi-palace-has-gaulli-paintings`
- `st-chp6-p154-chigi-palace-has-antique-statues`

有关收藏总体质量、立面与室内装饰反差、以及“有一些好画”的3条 statement 保持非关系陈述，不据此增加正式边。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the separated Colonna and Chigi palace place groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid, item in GROUPS.items():
        assert candidate_by_id[cid]["canonical_name"] == "Colonna palace"
        assert candidate_by_id[cid]["suggested_type"] == "place"
        assert alignment_by_id[cid]["decision"] == "new" and not alignment_by_id[cid].get("ku_id")
        assert sync.get_group(alignment_by_id[cid].get("resolution_note", "")) == item["group"]
        assert not item["card_path"].exists() and item["card_rel"] not in ACCEPTED_PATH.read_text(encoding="utf-8-sig")
        assert not any(row.get("ku_id") == item["ku_id"] or row.get("card_path") == item["card_rel"] for row in manifest)
        assert not any(row.get("type") == "place" and row.get("name_en", "").casefold() == item["name_en"].casefold() for row in manifest)
    assert alignment_by_id["cand-0815"]["resolution_note"].count("cand-0816") >= 1
    assert "prior_s3_group_token=sg3-place-colonnapalace" in alignment_by_id["cand-0816"]["resolution_note"]
    assert any(row.get("ku_id") == "units/persons/flavio-chigi" for row in manifest)

    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    for cid in GROUPS:
        direct = [
            row for row in statements
            if cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        ]
        direct_ids = {row["statement_id"] for row in direct}
        assert direct_ids == RELATION_IDS[cid] | NON_RELATION_IDS[cid]
        assert {
            row["statement_id"] for row in direct
            if row.get("qualifiers", {}).get("relation_candidate") is True
        } == RELATION_IDS[cid]

    source = (ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md").read_text(encoding="utf-8-sig")
    index = (ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md").read_text(encoding="utf-8-sig")
    assert "which he bought from a branch of the Colonna family in 1662" in source
    assert "Their palace, situated near the one sold to the Chigi" in source
    assert "had been largely rebuilt and decorated by Filippo and his son, Cardinal Girolamo" in source
    assert "Colonna palace" in index and "sale to Cardinal Flavio Chigi" in index

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    for cid, item in GROUPS.items():
        planned_by_id[cid]["ku_id"] = item["ku_id"]
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "place",
            "canonical_name": item["name_zh"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    audit_old = "4,589条待登记 `decision=new` alignment 行，含4,574条候选决定映射（4,498组）和15条外部身份记录。"
    audit_new = "4,587条待登记 `decision=new` alignment 行，含4,572条候选决定映射（4,496组）和15条外部身份记录。"
    assert audit_old in result_text
    result_text = result_text.replace(audit_old, audit_new, 1)
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S4 place：Colonna family palace 与 Flavio Chigi palace 分组登记（2026-10-17）\n\n"
        "按已更正的 S3 身份组，`cand-0815` 登记为[罗马科隆纳家族宫殿卡](../../../04-knowledge/units/places/colonna-family-palace-rome.md)，"
        "`cand-0816` 登记为[Flavio Chigi 圣使徒广场宫殿卡](../../../04-knowledge/units/places/flavio-chigi-palace-ss-apostoli.md)。两者都是 S3 `new` place，但代表两个相邻建筑，各自一个 KU。"
        "前者依据 p.155 的 Colonna 家族宫殿段落；后者依据 p.154 的 Chigi 购买/地点/装饰段落及 p.155 对两座建筑的明确区分。"
        "两卡分别保存4条与5条关系候选，均待 S6；Chigi 宫殿另外3条非关系 statement 保持原分类。本轮未写 `relations.csv`。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 place：Colonna / Chigi 两座宫殿分别登记（2026-10-17）\n\n"
        "`cand-0815` 与 `cand-0816` 分别映射到[Colonna 家族宫殿卡](../units/places/colonna-family-palace-rome.md)和"
        "[Flavio Chigi 宫殿卡](../units/places/flavio-chigi-palace-ss-apostoli.md)。S3 已根据 p.154–155 拆为两个相邻建筑组。"
        "分别有4条和5条关系候选待 S6；未新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    if args.dry_run:
        print("S4 palace registration dry-run passed: cand-0815 and cand-0816 map to separate place KUs")
        print("Colonna family palace: 4 relation candidates; Chigi palace: 5 relation candidates and 3 non-relations")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}")
        print(f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; audit pending new alignments=4,587")
        print("source distinctions, S3 group tokens, direct statement partitions, and unique destinations checked; no files changed")
        return 0

    card_builders = {"cand-0815": colonna_card, "cand-0816": chigi_card}
    for cid, item in GROUPS.items():
        item["card_path"].write_text(card_builders[cid](), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    for item in sorted(GROUPS.values(), key=lambda x: x["card_rel"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > item["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {item['card_rel']}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        "applied: cand-0815 and cand-0816 mapped to separate place KUs; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
