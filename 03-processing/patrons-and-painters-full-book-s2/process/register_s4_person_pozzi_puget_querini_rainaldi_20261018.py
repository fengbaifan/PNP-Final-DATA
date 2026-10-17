from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_person_relation_endpoints_allegrini_bouchardon_20261018 as person_sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
DATE = "2026-10-18"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ANCHOR = "s4-person-pozzi-puget-querini-rainaldi-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

TARGETS = [
    {
        "candidate": "cand-2032", "group": "new-person:luigi-pozzi-99e955d500",
        "ku": "units/persons/luigi-pozzi", "card": "04-knowledge/units/persons/luigi-pozzi.md",
        "name_zh": "路易吉·波齐", "name_en": "Luigi Pozzi",
        "index_file": "P.csv", "index_entry": "P.csv#235", "index_name": "Pozzi, Luigi", "page": "362",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_i.md", "location": "第15章第I节，印刷页362；OCR L19",
        "span": "line 19; print p. 362", "quote": "the painter Luigi Pozzi to copy the principal works of Raphael and Annibale Carracci",
        "summary": "Haskell称Filippo Farsetti雇用画家Luigi Pozzi临摹Raphael与Annibale Carracci的主要作品；索引以“Pozzi, Luigi”指向第362页。",
        "description_zh": "本卡登记哈斯克尔第15章第I节第362页所称Luigi Pozzi。正文称Filippo Farsetti雇用画家Pozzi临摹Raphael与Annibale Carracci的主要作品；书后索引以“Pozzi, Luigi”指向该页。本卡保留书内叙述，不据此新增正式任职或委托关系。中文显示名为项目工作音译。",
        "description_en": "This card records Luigi Pozzi named on page 362 of Chapter 15, section I. The passage says Filippo Farsetti employed the painter Pozzi to copy principal works by Raphael and Annibale Carracci; the index lists “Pozzi, Luigi” at that page. The card preserves the account without creating a formal office or commission relation. The Chinese display name is a working transliteration.",
        "context_zh": "正文报告Farsetti安排的临摹工作；本次不将叙述迁移为正式关系。",
        "context_en": "The passage reports a copying task arranged by Farsetti; this registration does not migrate it into a formal relation.",
        "name_rows": [("索引姓名", "Pozzi, Luigi", "S1"), ("正文姓名", "Luigi Pozzi", "S2")],
    },
    {
        "candidate": "cand-2070", "group": "new-person:pierre-puget-c313de05b2",
        "ku": "units/persons/pierre-puget", "card": "04-knowledge/units/persons/pierre-puget.md",
        "name_zh": "皮埃尔·皮热", "name_en": "Pierre Puget",
        "index_file": "P.csv", "index_entry": "P.csv#273", "index_name": "Puget, Pierre", "page": "",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "location": "第10章第II节，印刷页312；OCR L22",
        "span": "line 22; print p. 312", "quote": "a bas-relief by Puget of the Assumption of the Virgin",
        "summary": "Haskell称Schulenburg收藏包括Puget创作的《圣母升天》浮雕，并称其价值颇高；索引列出“Puget, Pierre”，未标页码。",
        "description_zh": "本卡登记哈斯克尔第10章第II节第312页所称Pierre Puget。正文提及Schulenburg收藏中的《圣母升天》浮雕，称其为Puget所作且价值颇高；书后索引列出“Puget, Pierre”但未标页码。本卡只记录书内姓名与归属语境，不补充其他生平信息。中文显示名为项目工作音译。",
        "description_en": "This card records Pierre Puget named on page 312 of Chapter 10, section II. The passage mentions a relief of the Assumption of the Virgin in Schulenburg's collection, calls it by Puget, and says it was highly valued; the index lists “Puget, Pierre” without a page number. The card records only the book's name and attribution context without adding biography. The Chinese display name is a working transliteration.",
        "context_zh": "作品归属按Haskell的来源叙述保留；本次未创建正式作品关系。",
        "context_en": "The work attribution remains as reported by Haskell; this registration creates no formal work relation.",
        "name_rows": [("索引姓名", "Puget, Pierre", "S1"), ("正文称名", "Puget", "S2")],
    },
    {
        "candidate": "cand-2087", "group": "new-person:giacomo-querini-7687c88ca3",
        "ku": "units/persons/giacomo-querini", "card": "04-knowledge/units/persons/giacomo-querini.md",
        "name_zh": "贾科莫·奎里尼", "name_en": "Giacomo Querini",
        "index_file": "Q-R.csv", "index_entry": "Q-R.csv#14", "index_name": "Querini, Giacomo", "page": "152",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md", "location": "第6章第I节，印刷页152；OCR L72–74",
        "span": "lines 72–74; print p. 152", "quote": "Seven years later Sagredo’s heir, Giacomo Querini",
        "summary": "Haskell称Giacomo Querini为Sagredo的继承人，并转述他对Alexander VII时期教皇财政与圣彼得大教堂工程的批评；索引以“Querini, Giacomo”指向第152页。",
        "description_zh": "本卡登记哈斯克尔第6章第I节第152页所称Giacomo Querini。正文称其为Sagredo的继承人，并转述其对Alexander VII时期教皇财政和圣彼得大教堂柱廊工程的批评；书后索引以“Querini, Giacomo”指向该页。本卡保留来源称谓，不补充家族或生平细节。中文显示名为项目工作音译。",
        "description_en": "This card records Giacomo Querini named on page 152 of Chapter 6, section I. The passage calls him Sagredo's heir and reports his criticism of papal finances under Alexander VII and the portico at St Peter's; the index lists “Querini, Giacomo” at that page. The card preserves the source's designation without adding family or biographical details. The Chinese display name is a working transliteration.",
        "context_zh": "本次仅登记书内姓名与被归于他的文字；没有建立亲属或政治关系边。",
        "context_en": "This registration records the source name and the text attributed to him; it creates no kinship or political relation edge.",
        "name_rows": [("索引姓名", "Querini, Giacomo", "S1"), ("正文姓名", "Giacomo Querini", "S2")],
    },
    {
        "candidate": "cand-2092", "group": "new-person:carlo-rainaldi-7ecc91cf92",
        "ku": "units/persons/carlo-rainaldi", "card": "04-knowledge/units/persons/carlo-rainaldi.md",
        "name_zh": "卡洛·拉伊纳尔迪", "name_en": "Carlo Rainaldi",
        "index_file": "Q-R.csv", "index_entry": "Q-R.csv#19", "index_name": "Rainaldi, Carlo", "page": "187",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "location": "第7章第I节，印刷页187；OCR L230",
        "span": "line 230; print p. 187", "quote": "Carlo Rainaldi and the unknown Candiani",
        "summary": "Haskell列出Carlo Rainaldi为向法国宫廷提交方案的意大利建筑师之一，并转述对其设计的批评；索引以“Rainaldi, Carlo”指向第187页。",
        "description_zh": "本卡登记哈斯克尔第7章第I节第187页所称Carlo Rainaldi。正文将他列为向法国宫廷提交方案的建筑师之一，并转述法国方面对方案的批评；书后索引以“Rainaldi, Carlo”指向该页。本卡不推定其任职或正式机构归属。中文显示名为项目工作音译。",
        "description_en": "This card records Carlo Rainaldi named on page 187 of Chapter 7, section I. The passage lists him among the architects who submitted plans to the French court and reports criticism of those plans; the index lists “Rainaldi, Carlo” at that page. The card does not infer an office or formal institutional affiliation. The Chinese display name is a working transliteration.",
        "context_zh": "正文列举其提交方案及批评语境，不构造正式委托或任职关系。",
        "context_en": "The passage lists his submitted plan and the criticism it received; this registration does not infer a formal commission or office.",
        "name_rows": [("索引姓名", "Rainaldi, Carlo", "S1"), ("正文姓名", "Carlo Rainaldi", "S2")],
    },
]


def make_index_source(t: dict) -> dict:
    return {
        "citation": f"Francis Haskell, *Patrons and Painters*, index, {t['index_file']}.",
        "location": f"书后索引，{t['index_entry']}" + (f"；指向印刷页{t['page']}" if t["page"] else "；未标页码"),
        "sentence_summary": f"索引以“{t['index_name']}”为主条" + (f"并指向印刷页{t['page']}。" if t["page"] else "，未标页码。"),
        "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}", "source_span": t["index_entry"]},
    }


def make_text_source(t: dict) -> dict:
    return {
        "citation": BOOK, "location": t["location"], "sentence_summary": t["summary"],
        "original_quotes": [{"source_span": t["span"], "text": t["quote"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["source_file"], "source_span": t["span"]},
    }


def make_card(t: dict) -> str:
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": [make_index_source(t), make_text_source(t)],
        "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    names = "\n".join(f"| {field} | {value} | {basis} |" for field, value, basis in t["name_rows"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']}

**English:** {t['description_en']}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
{names}

### 本书相关内容

**中文：** {t['context_zh']}

**English:** {t['context_en']}

## 关系与证据

### 关系记录

当前没有登记在 `relations.csv` 中的正式关系；本次S4身份登记不将来源叙述转换为正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four S3-new person groups from P/Q-R index entries.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = sync.load_statements()

    for t in TARGETS:
        cid = t["candidate"]
        candidate = candidate_by_id[cid]
        alignment = next(row for row in alignments if row.get("candidate_id") == cid and not row.get("external_source"))
        assert candidate.get("suggested_type") == "person"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        group_members = [row["candidate_id"] for row in alignments if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == t["group"]]
        assert group_members == [cid], (t["group"], group_members)
        assert candidate.get("index_entry_id") == t["index_entry"] and candidate.get("canonical_name") == t["index_name"] and candidate.get("index_page_range", "") == t["page"]
        index = person_sync.read_index_rows(t["index_file"])[int(t["index_entry"].split("#")[1])]
        assert index.get("Main Entry") == t["index_name"] and index.get("Page Numbers", "") == t["page"]
        assert t["quote"] in (ROOT / t["source_file"]).read_text(encoding="utf-8-sig"), (cid, t["quote"])
        assert t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not (ROOT / t["card"]).exists()
        assert not any(row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold() for row in manifest)
        direct = {row["statement_id"] for row in statements if (row.get("qualifiers") or {}).get("relation_candidate") is True and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))}
        assert direct == set(), (cid, direct)

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        row = next(row for row in planned_alignments if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        row["ku_id"], row["process_ref"] = t["ku"], PROCESS_REF
        row["resolution_note"] = row.get("resolution_note", "").rstrip() + f" S4登记（{DATE}）：身份组{t['group']}映射至{t['ku']}；新增一张书内来源支持的人物KU，未将来源叙述转换为正式关系。"
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = person_sync.insert_accepted(planned_accepted, t["card"])

    baseline = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == baseline["person"]["registered_groups"] + len(TARGETS)
    assert stats["person"]["registered_members"] == baseline["person"]["registered_members"] + len(TARGETS)
    assert stats["person"]["pending_groups"] == baseline["person"]["pending_groups"] - len(TARGETS)
    assert stats["person"]["pending_members"] == baseline["person"]["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    log_rows = [f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；依据索引{t['index_entry']}与正文{t['location']}登记。" for t in TARGETS]
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Pozzi、Puget、Querini与Rainaldi四组索引／正文登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四组均为单候选S3 new身份组。Pozzi临摹工作、Puget浮雕归属、Querini的Sagredo继承人称谓及Rainaldi方案语境均按来源原有范围记录；未新增外部来源或formal relation。\n\n"
        + f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        + f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        + f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物身份组登记：Pozzi、Puget、Querini与Rainaldi（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。四组均为S3 new，各登记一张KU；来源原有语境均予保留，未创建正式关系。"
    )

    if args.dry_run:
        print(f"dry-run passed: four singleton person groups; index/source/name checks passed; manifest={len(manifest)}->{len(planned_manifest)}; person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; KU={len(planned_manifest)}; external_sources_added=0; relation_rows_added=0; no files changed")
        return 0
    for path, card in cards.items():
        (ROOT / path).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: groups=4; candidate_mappings=4; KU={len(planned_manifest)}; person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; external_sources_added=0; relation_rows_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
