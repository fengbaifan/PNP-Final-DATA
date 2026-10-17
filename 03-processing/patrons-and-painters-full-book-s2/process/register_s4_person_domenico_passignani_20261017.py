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
GROUP = "new-person:domenico-passignani-0029da3d84"
MEMBERS = ("cand-1857",)
KU_ID = "units/persons/domenico-passignani"
CARD_REL = "04-knowledge/units/persons/domenico-passignani.md"
NAME_ZH = "多梅尼科·帕西尼亚尼"
NAME_EN = "Domenico Passignani"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/P.csv"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"
ANCHOR = "s3-s4-person-domenico-passignani-20261017"
RELATION_IDS = (
    "st-chp2-seci-l55-69-cupola-fresco-commission",
    "st-chp2-seci-l55-69-cupola-proposal",
    "st-chp2-seci-l55-69-lunette-scenes",
    "st-chp2-seci-l55-69-passignani-selected",
)

SOURCES = (
    {
        "file": INDEX_FILE,
        "location": "全书索引 P.csv#57；列印刷页26、30、94",
        "span": "P.csv#57",
        "quote": "Passignani, Domenico",
        "summary": "索引以倒置全名列出Domenico Passignani，并提供第2章相关页码26、30、94。",
    },
    {
        "file": SOURCE_FILE,
        "location": "第2章，印刷页26；L58–61；PDF物理页7",
        "span": "lines 58–61; print p. 26; PDF physical p. 7",
        "quote": "Instead he turned to his compatriot, Domenico Passignani, at the time one of the most fashionable painters in Rome. Passignani proposed that the cupola should be adorned with coloured mosaic and gilt stucco ribs, and he suggested a number of artists who would be suitable.3 Eventually, however, he himself was commissioned to cover it with frescoes of the Virtues with angels and in the spandrels Moses, David, Solomon and Isaiah. He also painted the canvases and frescoes in the lunettes with Scenes from the Life of the Virgin",
        "summary": "Haskell以全名介绍Passignani，叙述Maffeo转而选用他；随后分别记录其穹顶装饰方案、被委托绘制穹顶壁画及 lunettes 中圣母生平场景。委托方未在被动句中指明；“most fashionable”“masterpieces”是作者评价，方案不等于已执行。",
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
    index_ref = "[全书索引 P.csv#57](../../../02-sources/03-Index/03-2-Index-CSV/P.csv)"
    source_ref = "[第2章 p.26](../../../02-sources/02-Markdown/02_CHP-2_sec_i.md)（L58–61）"
    relation_list = "\n".join(f"- `{relation_id}`" for relation_id in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡对应全书索引中的 Domenico Passignani。第2章称Maffeo在Barocci年长后转而选用同乡Passignani，并叙述其提出穹顶装饰方案、后来受委托绘制穹顶壁画，以及绘制 lunettes 中的《圣母生平》场景。以上均保留为Haskell的书内叙述；本卡不补定被动句中未说明的委托方，也不把建议方案视为已实施。{index_ref} {source_ref}

**English:** This unit corresponds to Domenico Passignani in the index. Chapter 2 says that Maffeo turned to his compatriot Passignani after Barocci was considered too old, and recounts his proposal for the cupola, his later commission to paint its frescoes, and his paintings and frescoes of Scenes from the Life of the Virgin in the lunettes. These remain Haskell’s book statements. The card does not identify the unnamed agent in the passive commission clause or treat the proposal as executed. {index_ref} {source_ref}

### 姓名与身份范围

- **索引形式：** `Passignani, Domenico`；索引定位第2章印刷页26、30、94。{index_ref}
- **书内全名：** 第2章印刷页26写作 `Domenico Passignani`；中文显示名“多梅尼科·帕西尼亚尼”为项目工作音译。{source_ref}
- **类型边界：** 本卡登记人物；Barberini chapel 穹顶、穹顶壁画和 lunette 场景各保持独立 place/work 候选，不并入人物卡。

## 关系与证据

当前没有正式关系记录。以下4条直接S2关系候选留待S6，继续保留“方案”“被动委托”“作者评价”等限定：

{relation_list}

穹顶地点候选`cand-4258`为S3 `new`、待S4登记；穹顶壁画与lunette作品候选`cand-4259`、`cand-4260`仍为S3 `undecided`。委托方没有被原句指名，本卡不补造关系端点。"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Domenico Passignani's S4 person identity group")
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
    assert all(cid in candidate_by_id and candidate_by_id[cid].get("suggested_type") == "person" for cid in MEMBERS)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    card_path = ROOT / CARD_REL
    registered = [r for r in manifest if r.get("ku_id") == KU_ID and r.get("card_path") == CARD_REL]
    if registered and card_path.exists() and CARD_REL in accepted and all(decisions[cid].get("ku_id") == KU_ID for cid in MEMBERS):
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 4 relation candidates remain non-formal.")
        return 0
    for cid in MEMBERS:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)

    for item in SOURCES:
        text = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in text, (item["file"], item["quote"])
    assert "Domenico Passignani" in (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [row for row in statements if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert {row.get("statement_id") for row in relations} == set(RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; source-local full-name anchor, no external identity claim."
    planned_manifest = list(manifest)
    planned_manifest.append({"ku_id": KU_ID, "type": "person", "canonical_name": NAME_ZH, "name_en": NAME_EN, "source_task": TASK, "card_path": CARD_REL})
    card = make_card()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated person card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Domenico Passignani直接关系端点登记（{DATE}）\n\n"
        f"- `{MEMBERS[0]}`（`{GROUP}`）登记至[{NAME_EN}人物卡](../../../{CARD_REL})。索引P.csv#57列全名和pp.26、30、94；第2章p.26正文明确写作`Domenico Passignani`，支持该书内人物身份。未补外部生平。\n"
        "- 4条直接S2关系候选待S6：Maffeo转而选用Passignani、穹顶装饰方案、被动句中的壁画委托、lunette场景绘制。提案不等于执行；Haskell的“most fashionable”“masterpieces”不升级为核实事实。cupola地点`cand-4258`待S4，cupola fresco和lunette work候选`cand-4259`、`cand-4260`仍S3 undecided；未指名委托方保持未决。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = process_text + process_append
    next_result += (
        f"\n\n### person：Domenico Passignani直接关系端点 S4 登记（{DATE}）\n\n"
        f"`{MEMBERS[0]}`登记至[人物卡](../units/persons/domenico-passignani.md)。索引全名与第2章p.26正文锚点相合；4条关系候选留待S6。杯形穹顶地点候选待S4，壁画作品端点仍S3 undecided。\n\n"
        f"S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )

    if args.dry_run:
        print(f"dry-run passed: {GROUP} -> {KU_ID}; sources={len(SOURCES)}; relation_candidates_pending={len(relations)}")
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
    print(f"applied: {GROUP} -> {KU_ID}; relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
