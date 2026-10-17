from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

ITEMS = (
    {
        "candidate": "cand-8556",
        "group": "sg3-institution-cand-8556",
        "ku_id": "units/institutions/biblioteca-governativa-cremona",
        "card_rel": "04-knowledge/units/institutions/biblioteca-governativa-cremona.md",
        "canonical_name": "克雷莫纳 Biblioteca Governativa",
        "name_en": "Biblioteca Governativa, Cremona",
        "anchor": "s4-institution-biblioteca-governativa-cremona-20261017",
        "sources": (
            {
                "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "lines": [229],
                "location": "第9章注6，印刷页262；OCR L229",
                "span": "OCR line 229; printed page 262, note 6",
                "quote": "Biblioteca Governativa, Cremona, MSS. aa.I.4.1",
                "summary": "哈斯克尔将Biffi往来材料定位于克雷莫纳的Biblioteca Governativa，MSS. aa.I.4.1，并称曾使用Venturi制作的缩微胶片。",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "lines": [341],
                "location": "第10章注5，印刷页328；OCR L341",
                "span": "OCR line 341; printed page 328, note 5",
                "quote": "In an unpublished letter to Signor Vacchelli in 1773 in the Biblioteca Govcrnativa, Cremona, MSS. aa.I.4.,",
                "summary": "哈斯克尔以该馆藏号定位Biffi致Signor Vacchelli的1773年未刊信；OCR拼作Govcrnativa，书页图像读作Governativa。",
            },
        ),
        "description_cn": "哈斯克尔在第9章与第10章将Biblioteca Governativa, Cremona列为Biffi书信及往来材料的保存处，并给出MSS. aa.I.4.1与aa.I.4.定位。书页读作Governativa，OCR一处作Govcrnativa；本卡仅记录书内具名机构及地名，不声称独立核查手稿、馆藏目录或机构现行状态。",
        "description_en": "Haskell identifies Biblioteca Governativa, Cremona as the repository for Biffi correspondence and an unpublished 1773 letter, giving the locators MSS. aa.I.4.1 and aa.I.4. The printed reading is Governativa; one OCR transcription has Govcrnativa. This card records the institution and locality named in the book, without claiming independent inspection of the manuscripts, catalogue, or current institutional status.",
        "statement_ids": (
            "st-chp9-p262-note6-biffi-manuscript-locator",
            "st-chp10-p328-n05-letter-held-by-cremona-library",
        ),
    },
    {
        "candidate": "cand-9493",
        "group": "sg3-institution-cand-9493",
        "ku_id": "units/institutions/biblioteca-marucelliana",
        "card_rel": "04-knowledge/units/institutions/biblioteca-marucelliana.md",
        "canonical_name": "马鲁切利亚纳图书馆（佛罗伦萨）",
        "name_en": "Biblioteca Marucelliana, Florence",
        "anchor": "s4-institution-biblioteca-marucelliana-20261017",
        "sources": (
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "lines": [581],
                "location": "第10章注4，印刷页299；OCR L581",
                "span": "OCR line 581; printed page 299, note 4",
                "quote": "See letters from Joseph Smith to A. F. Gori in Biblioteca Marucelliana, Florence:",
                "summary": "哈斯克尔以该馆藏定位Joseph Smith致A. F. Gori的信件，并回引至第299页注4。",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "lines": [613, 615, 616],
                "location": "第10章注3、注5、注6，印刷页306–307；OCR L613、L615–616",
                "span": "OCR lines 613, 615–616; printed pages 306–307",
                "quote": "Biblioteca Marucelliana, Florence",
                "summary": "相邻注释将A. F. Gori、Girolamo Zanetti及Joseph Smith相关信件定位于佛罗伦萨Biblioteca Marucelliana。",
            },
            {
                "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "lines": [339],
                "location": "第10章注2，印刷页328；OCR L339",
                "span": "OCR line 339; printed page 328, note 2",
                "quote": "Letter from A. M. Zanetti to A. F. Gori of 23 August 1738 in Biblioteca Marucelliana, Florence",
                "summary": "哈斯克尔将1738年8月23日Zanetti致Gori的信定位于该馆MSS. B. VIII, 13。",
            },
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "lines": [233],
                "location": "第13章注6，印刷页342；OCR L233",
                "span": "OCR line 233; printed page 342, note 6",
                "quote": "Biblioteca Marucelliana, Florence—MSS. B. VIII, 13, p. 400:",
                "summary": "第13章另以同一机构及馆藏号定位一封1752年致A. F. Gori的信。",
            },
        ),
        "description_cn": "哈斯克尔在第10章和第13章多处将佛罗伦萨Biblioteca Marucelliana作为Joseph Smith、A. F. Gori及Girolamo Zanetti相关书信的保存处，并列出MSS. B. VIII, 13等定位。该馆藏记录未在本任务中独立查阅；本卡仅登记书内明确命名的机构身份与地点。",
        "description_en": "Haskell repeatedly names the Biblioteca Marucelliana in Florence as the repository for letters involving Joseph Smith, A. F. Gori, and Girolamo Zanetti, including references to MSS. B. VIII, 13. The manuscripts and repository catalogue were not independently consulted for this task; this card records only the institution and locality explicitly named in the book.",
        "statement_ids": (
            "st-chp10-p306-note3-gori-letter",
            "st-chp10-p306-note5-zanetti-letter-citation",
            "st-chp10-p306-note6-smith-gori-letter",
            "st-chp10-p328-n02-letter-held-by-marucelliana",
            "st-chp13-p342-notes-note6-letter-located-in-marucelliana",
        ),
    },
)


def make_sources(item: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "citation": BOOK_CITATION,
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["span"], "text": source["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source["file"],
                "source_span": source["span"],
            },
        }
        for source in item["sources"]
    ]


def card_text(item: dict[str, object]) -> str:
    fm = {
        "title": f"{item['canonical_name']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": "institution",
        "evidence_status": "source_backed",
        "sources": make_sources(item),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}",
    }
    frontmatter = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    links = "；".join(
        f"[来源{index}](../../../{source['file']}#L{source['lines'][0]})"
        for index, source in enumerate(item["sources"], start=1)
    )
    relation_list = "、".join(f"`{sid}`" for sid in item["statement_ids"])
    body = f"""## 内容

### 描述

**中文：** {item['description_cn']} {links}

**English:** {item['description_en']} {links}

### 身份范围

- 本卡只记录Haskell书内明确命名的机构身份和地点；不据此补充机构沿革、现行名称、组织隶属或未被来源支持的馆藏范围。
- 相关书信的保存/馆藏说法仍保留为S2关系候选，不在本次身份登记中转为正式关系。

## 关系与证据

当前没有本任务新增的正式关系。直接S2关系候选{relation_list}留待S6复核；书内馆藏定位不等于本项目已独立查阅原件或馆藏目录。
"""
    return f"---\n{frontmatter}---\n\n{body}"


def insert_accepted(text: str, card_rel: str) -> str:
    lines = text.splitlines()
    assert f"- {card_rel}" not in lines
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two source-named library endpoints as separate S4 institution KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id)
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    cards: list[tuple[dict[str, object], str, Path]] = []
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    for item in ITEMS:
        cid = str(item["candidate"])
        row = decisions[cid]
        assert candidate_by_id[cid].get("suggested_type") == "institution"
        assert row.get("decision") == "new" and not row.get("ku_id"), (cid, row)
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        group_members = {
            other["candidate_id"] for other in alignments
            if other.get("candidate_id") and not other.get("external_source")
            and other.get("decision") == "new"
            and sync.get_group(other.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        card_path = ROOT / str(item["card_rel"])
        assert not card_path.exists() and str(item["card_rel"]) not in accepted
        assert not any(entry.get("ku_id") == item["ku_id"] or entry.get("card_path") == item["card_rel"] for entry in manifest)
        assert not any(
            entry.get("type") == "institution"
            and entry.get("name_en", "").casefold() == str(item["name_en"]).casefold()
            for entry in manifest
        ), item["name_en"]

        for source in item["sources"]:
            source_text = " ".join((ROOT / str(source["file"])).read_text(encoding="utf-8-sig").split())
            assert " ".join(str(source["quote"]).split()) in source_text, (cid, source)

        direct = [
            statement for statement in statements
            if statement.get("subject_candidate_id") == cid or statement.get("object_candidate_id") == cid
        ]
        relation_ids = {
            statement["statement_id"] for statement in direct
            if (statement.get("qualifiers") or {}).get("relation_candidate") is True
        }
        assert relation_ids == set(item["statement_ids"]), (cid, relation_ids, item["statement_ids"])

        planned_by_id[cid]["ku_id"] = item["ku_id"]
        planned_by_id[cid]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}"
        planned_by_id[cid]["resolution_note"] += (
            f" S4 registration (2026-10-17): {item['group']} maps to {item['ku_id']}; "
            "source-named repository identity only; no independent catalogue inspection or formal S6 relation is implied."
        )
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "institution",
            "canonical_name": item["canonical_name"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })
        card = card_text(item)
        fm = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert fm and isinstance(yaml.safe_load(fm.group(1)), dict)
        cards.append((item, card, card_path))

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_append = f"""

### S4 institution：Biblioteca Governativa, Cremona 与 Biblioteca Marucelliana（{DATE}）

直接S2关系端点`cand-8556`和`cand-9493`分别登记为[克雷莫纳 Biblioteca Governativa](../units/institutions/biblioteca-governativa-cremona.md)与[佛罗伦萨 Biblioteca Marucelliana](../units/institutions/biblioteca-marucelliana.md)。第9、10章书内书信注释提供馆名与所在地，Marucelliana另见第13章引文定位。两张卡只记录书内具名机构身份；7条相关S2关系候选仍待S6，未新增正式边。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-institution-biblioteca-direct-endpoints-20261017"></a>

### S4 institution：两项书内具名图书馆端点（{DATE}）

- `cand-8556`（`sg3-institution-cand-8556`）登记至[克雷莫纳 Biblioteca Governativa](../../../04-knowledge/units/institutions/biblioteca-governativa-cremona.md)。第9章p.262注6给出MSS. aa.I.4.1，第10章p.328注5定位Biffi致Signor Vacchelli的1773年未刊信；第10章书页读作Governativa，OCR作Govcrnativa。该卡只记录Haskell书内名称和地点。
- `cand-9493`（`sg3-institution-cand-9493`）登记至[佛罗伦萨 Biblioteca Marucelliana](../../../04-knowledge/units/institutions/biblioteca-marucelliana.md)。第10章p.299及pp.306–307、p.328多条信件注释和第13章p.342注6均以该馆为保存处；原件与馆藏目录未独立查阅。
- 两组各登记一张institution KU。直接S2关系候选分别为{len(ITEMS[0]['statement_ids'])}条和{len(ITEMS[1]['statement_ids'])}条，合计7条，全部留待S6；本次不新增正式关系或S5补足。

`cand-8556` and `cand-9493` are registered as separate institution KUs based on Haskell's named repository references. The book supplies localities and manuscript locators; no manuscripts or repository catalogues were independently consulted. All seven direct S2 relation candidates remain pending S6, and no formal relation or S5 enrichment was added.

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = PROCESS.read_text(encoding="utf-8-sig").rstrip() + process_append
    accepted_next = accepted
    for item, _, _ in cards:
        accepted_next = insert_accepted(accepted_next, str(item["card_rel"]))

    if args.dry_run:
        print("dry-run passed: " + "; ".join(f"{item['candidate']} -> {item['ku_id']}" for item in ITEMS))
        print(
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        print("verified_direct_relation_candidates=7; no S5 enrichment or S6 formal relation rows will be written; no files changed")
        return 0

    for _, card, card_path in cards:
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_next, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
