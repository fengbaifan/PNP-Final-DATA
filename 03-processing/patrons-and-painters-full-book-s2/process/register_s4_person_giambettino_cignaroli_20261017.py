from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "new-person:cignaroli-giambettino-1b6e1c2f7d"
MEMBERS = ("cand-0754", "cand-0755")
KU_ID = "units/persons/giambettino-cignaroli"
CARD_REL = "04-knowledge/units/persons/giambettino-cignaroli.md"
NAME_ZH = "吉安贝蒂诺·齐尼亚罗利"
NAME_EN = "Giambettino Cignaroli"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/C.csv"
CH9_INTRO = "02-sources/02-Markdown/09_CHP-9_intro.md"
CH9_SECII = "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
ANCHOR = "s3-s4-person-giambettino-cignaroli-20261017"
DIRECT_RELATIONS = (
    "st-chp9-p262-cignaroli-labia-employment",
    "st-chp9-p262-note5-cignaroli-ceiling-paintings",
    "st-chp9-p268-cignaroli-saints-claim",
)
AGGREGATE_CONTEXT = "st-chp9-p271-oratorian-fava-commissions"

SOURCES = (
    {
        "file": INDEX_FILE,
        "location": "全书索引 C.csv#278；列印刷页262、268、271",
        "span": "C.csv#278",
        "quote": '"Cignaroli, Giambettino",,,,"262, 268, 271"',
        "summary": "索引主项列全名Cignaroli, Giambettino，定位第9章印刷页262、268、271。",
    },
    {
        "file": INDEX_FILE,
        "location": "全书索引 C.csv#279；子目work for Labia；印刷页262注",
        "span": "C.csv#279",
        "quote": '"Cignaroli, Giambettino",,work for Labia,,262n',
        "summary": "第二个索引条目仍列同一全名，以“work for Labia”作页码子目；该子目指向人物相关语境，不另立为作品对象。",
    },
    {
        "file": CH9_INTRO,
        "location": "第9章，印刷页262；L223；PDF物理页24",
        "span": "line 223; print p. 262; PDF physical p. 24",
        "quote": "employed Cignaroli for a time",
        "summary": "Haskell称Labia曾雇用Cignaroli一段时间；句末脚注OCR标记6已由S2依印刷页校为注5。",
    },
    {
        "file": CH9_INTRO,
        "location": "第9章，印刷页262注5；L227；PDF物理页24",
        "span": "line 227; print p. 262, note 5; PDF physical p. 24",
        "quote": "He worked for the Labia for four years and some of the oil paintings which he inserted into ceilings in the palace are still in situ.",
        "summary": "Haskell注5称其为Labia工作四年，并称若干置于宫殿天花板中的油画当时仍在原位；清单与现状未独立核查。",
    },
    {
        "file": CH9_SECII,
        "location": "第9章，印刷页268；L9–10；PDF物理页34",
        "span": "lines 9–10; print p. 268; PDF physical p. 34",
        "quote": "Of Cignaroli in Verona it was claimed that like Barocci and Carlo Dolci (significant parallels) for years he painted almost nothing but saints",
        "summary": "Haskell转述对Cignaroli的说法，称其多年几乎只画圣徒；“it was claimed”保留为转述，后接关于私人虔敬图像的推断不作为已核事实。",
    },
    {
        "file": CH9_SECII,
        "location": "第9章，印刷页271；L47",
        "span": "line 47; print p. 271",
        "quote": "during the middle years of the century they employed other leading artists such as Balestra, Amigoni and Cignaroli.",
        "summary": "Haskell在Oratorian语境中将Cignaroli列入中世纪时期受雇的艺术家名单。现有S2语句端点落在Oratorian机构与合并的altarpiece作品候选；本卡记录该书内提及，不在S4把它拆成个人正式关系。",
    },
)


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx278 = "[全书索引 C.csv#278](../../../02-sources/03-Index/03-2-Index-CSV/C.csv)"
    idx279 = "[全书索引 C.csv#279](../../../02-sources/03-Index/03-2-Index-CSV/C.csv)"
    p262 = "[第9章 p.262](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L223、L227 注5）"
    p268 = "[第9章 p.268](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L9–10）"
    p271 = "[第9章 p.271](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L47）"
    relation_list = "\n".join(f"- `{relation_id}`" for relation_id in DIRECT_RELATIONS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡对应全书索引中两条同列全名“Cignaroli, Giambettino”的人物候选。主项列第9章p.262、268、271；第二条以“work for Labia”作p.262注释的索引子目。第9章正文以姓氏Cignaroli提及其在Labia工作的语境，并在Verona段落转述关于其绘画圣徒的说法。中文显示名为项目工作音译。{idx278} {idx279} {p262} {p268}

**English:** This unit corresponds to two index candidates that both give the full form “Cignaroli, Giambettino.” The main entry points to Chapter 9, pp. 262, 268, and 271; the second gives “work for Labia” as a subentry at p. 262, note. Chapter 9 refers to him by surname in the Labia context and reports a claim about his religious painting in Verona. The Chinese display name is a project working transliteration. {idx278} {idx279} {p262} {p268}

### 姓名与身份范围

- **索引全名：** `Cignaroli, Giambettino`；两个索引候选依S3同名组映射至本人物卡。{idx278} {idx279}
- **索引子目边界：** “work for Labia”是人物索引条目下的语境子目，不是单件作品题名；Labia家族与其宫殿作品仍分开记录。{idx279}
- **来源限定：** p.262称其为Labia工作一段时间，注5称四年；p.268明确写作“it was claimed”，不把相关说法或Haskell的私人虔敬图像推断提升为独立核验。{p262} {p268}
- **p.271名单：** Haskell还将Cignaroli列入Oratorian所雇艺术家名单。该段现有S2关系语句端点是Oratorian机构与合并的altarpiece作品候选`cand-8711`；本卡不据S4登记将其改写为个人正式边。{p271}

## 关系与证据

当前没有正式关系。以下3条直接S2候选继续留待S6，并保留来源限定：

{relation_list}

其中Labia雇用及油画仍在原位的陈述未独立核查；圣徒绘画说法是Haskell所转述的主张。p.271的Oratorian名单与`st-chp9-p271-oratorian-fava-commissions`现有集合式对象另行保留，不在本轮新增关系或改写statement端点。"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-index Giambettino Cignaroli person group in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    align_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(candidate_by_id[cid].get("suggested_type") == "person" for cid in MEMBERS)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    card_path = ROOT / CARD_REL
    registered = [r for r in manifest if r.get("ku_id") == KU_ID and r.get("card_path") == CARD_REL]
    if registered and card_path.exists() and CARD_REL in accepted and all(decisions[cid].get("ku_id") == KU_ID for cid in MEMBERS):
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 3 direct relation candidates remain non-formal.")
        return 0
    for cid in MEMBERS:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)

    for item in SOURCES:
        text = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in text, (item["file"], item["quote"])
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert '"Cignaroli, Giambettino",,,,"262, 268, 271"' in index_text
    assert '"Cignaroli, Giambettino",,work for Labia,,262n' in index_text

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [row for row in statements if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert {row.get("statement_id") for row in relations} == set(DIRECT_RELATIONS)
    p271 = next(row for row in statements if row.get("statement_id") == AGGREGATE_CONTEXT)
    assert p271.get("subject_candidate_id") == "cand-1783" and p271.get("object_candidate_id") == "cand-8711"
    assert not any(p271.get(key) in MEMBERS for key in ("subject_candidate_id", "object_candidate_id"))

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped S3 group {GROUP} to {KU_ID}; same indexed person identity, work-for-Labia remains a person subentry."
    planned_manifest = list(manifest)
    planned_manifest.append({"ku_id": KU_ID, "type": "person", "canonical_name": NAME_ZH, "name_en": NAME_EN, "source_task": TASK, "card_path": CARD_REL})
    card = make_card()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated person card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Giambettino Cignaroli跨索引身份组登记（{DATE}）\n\n"
        f"- `{MEMBERS[0]}`（C.csv#278，索引页262、268、271）与`{MEMBERS[1]}`（C.csv#279，子目`work for Labia`，p.262n）同列全名`Cignaroli, Giambettino`，按S3组`{GROUP}`登记至[{NAME_EN}人物卡](../../../{CARD_REL})。子目保留人物语境，不新建作品对象。\n"
        f"- 3条以该人物候选为端点的直接S2关系候选留待S6；p.262注5与p.268的限定及未核验状态保留。p.271还提及Cignaroli属于Oratorian所雇艺术家名单，但现有statement `{AGGREGATE_CONTEXT}`将关系端点记作机构与altarpiece作品候选`cand-8711`；本次不把该集合式陈述拆成个人关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = process_text + process_append
    next_result += (
        f"\n\n### person：Giambettino Cignaroli跨索引组 S4 登记（{DATE}）\n\n"
        f"`{MEMBERS[0]}`与`{MEMBERS[1]}`共同映射至[人物卡](../units/persons/giambettino-cignaroli.md)。同全名索引主项与`work for Labia`子项对应一个人；3条人物关系候选待S6，p.271集合式Oratorian陈述未拆为个人边。\n\n"
        f"S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )

    if args.dry_run:
        print(f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; sources={len(SOURCES)}; direct relation candidates={len(relations)}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}; no files changed")
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", align_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; direct relation candidates={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
