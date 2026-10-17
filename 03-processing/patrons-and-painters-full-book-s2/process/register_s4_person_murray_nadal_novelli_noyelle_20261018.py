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
ANCHOR = "s4-person-murray-nadal-novelli-noyelle-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

TARGETS = [
    {
        "candidate": "cand-1719", "group": "new-person:john-murray-587d09c515",
        "ku": "units/persons/john-murray-resident", "card": "04-knowledge/units/persons/john-murray-resident.md",
        "name_zh": "约翰·默里", "name_en": "John Murray",
        "index_file": "M.csv", "index_entry": "M.csv#260", "index_name": "Murray, John", "page": "302",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "location": "第10章，印刷页302；OCR L391–393",
        "span": "lines 391–393; print p. 302", "quote": "John Murray, the Resident",
        "summary": "Haskell称John Murray为Resident，并提及他是Smith第二任妻子的兄弟；书后索引以“Murray, John”指向第302页。",
        "description_zh": "本卡登记哈斯克尔第10章第302页所称John Murray。正文称他为Resident，并在叙述Thomas Smith的第二次婚姻时提及其为Smith妻子的兄弟；书后索引以“Murray, John”指向该页。本卡保留书内称名与语境，不补充其姓名之外的身份资料。中文显示名为项目工作音译。",
        "description_en": "This card records the John Murray named on page 302 of Chapter 10. The passage calls him the Resident and mentions him as the brother of Thomas Smith's second wife; the index lists “Murray, John” at that page. The card preserves the book's name and context without adding other identity details. The Chinese display name is a working transliteration.",
        "context_zh": "本次仅登记书内人物身份。没有把称谓或婚姻叙述转换为正式关系。",
        "context_en": "This registration records the person named in the book. It does not turn the title or marriage account into a formal relation.",
        "name_rows": [("索引名", "Murray, John", "S1"), ("正文姓名", "John Murray", "S2")],
    },
    {
        "candidate": "cand-1721", "group": "new-person:jerome-nadal-c9c2d78438",
        "ku": "units/persons/jerome-nadal", "card": "04-knowledge/units/persons/jerome-nadal.md",
        "name_zh": "杰罗姆·纳达尔", "name_en": "Jerome Nadal",
        "index_file": "N.csv", "index_entry": "N.csv#0", "index_name": "Nadal, Jerome", "page": "399",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "location": "Postscript，印刷页399；OCR L40–41",
        "span": "lines 40–41; print p. 399", "quote": "the Jesuit Jerome Nadal",
        "summary": "Haskell提及耶稣会士Jerome Nadal及其福音默想书；书后索引以“Nadal, Jerome”指向第399页。",
        "description_zh": "本卡登记哈斯克尔Postscript第399页所称耶稣会士Jerome Nadal。该段提及他的福音默想书，并称该书由St Ignatius委托；书后索引以“Nadal, Jerome”指向该页。本卡不把书内转述扩展为额外生平事实。中文显示名为项目工作音译。",
        "description_en": "This card records the Jesuit Jerome Nadal named on page 399 of the Postscript. The passage mentions his book of gospel meditations and says it was commissioned by St Ignatius; the index lists “Nadal, Jerome” at that page. The card does not extend this reported account into additional biography. The Chinese display name is a working transliteration.",
        "context_zh": "书内叙述将人物与一本福音默想书相联系；本次没有创建作品或委托关系记录。",
        "context_en": "The book associates the person with a book of gospel meditations; this registration creates no work or commission relation.",
        "name_rows": [("索引名", "Nadal, Jerome", "S1"), ("正文姓名", "Jerome Nadal", "S2")],
    },
    {
        "candidate": "cand-1757", "group": "new-person:il-monrealese-novelli-pietro-c49178815b",
        "ku": "units/persons/pietro-novelli-il-monrealese", "card": "04-knowledge/units/persons/pietro-novelli-il-monrealese.md",
        "name_zh": "彼得罗·诺韦利（il Monrealese）", "name_en": "Pietro Novelli (il Monrealese)",
        "index_file": "N.csv", "index_entry": "N.csv#37", "index_name": "Novelli, Pietro ('il Monrealese')", "page": "210",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "location": "第8章第I节，印刷页210；OCR L75",
        "span": "line 75; print p. 210", "quote": "seven pictures by Novelli",
        "summary": "Haskell称Russo收藏中有七幅Novelli作品；索引以“Novelli, Pietro ('il Monrealese')”定位第210页。",
        "description_zh": "本卡登记第8章第210页所称Novelli，索引将该条写作“Novelli, Pietro ('il Monrealese')”。正文只称其姓氏，并把其作品置于Russo收藏的那不勒斯及南意大利绘画语境中。本卡保留索引别称，不仅凭Novelli姓氏并入既有Pietro Antonio Novelli卡；两组历史身份是否相同未由本书此处证明。中文显示名保留原文别称。",
        "description_en": "This card records the Novelli named on page 210 of Chapter 8, whose index entry reads “Novelli, Pietro ('il Monrealese')”. The passage uses only the surname and places his pictures in the context of Russo's Neapolitan and southern Italian collection. The indexed epithet is preserved; the record is not merged with the existing Pietro Antonio Novelli card on surname alone. This passage does not establish whether the two source identities are historically identical.",
        "context_zh": "索引全名与正文姓氏共同支持这一书内身份组；与既有Pietro Antonio Novelli的身份关系仍未由本批外部核查。",
        "context_en": "The index form and body surname support this source-local identity group; this batch makes no external determination about its identity relation to the existing Pietro Antonio Novelli record.",
        "name_rows": [("索引姓名与别称", "Novelli, Pietro ('il Monrealese')", "S1"), ("正文称名", "Novelli", "S2")],
    },
    {
        "candidate": "cand-1763", "group": "new-person:charles-de-noyelle-54b3847378",
        "ku": "units/persons/charles-de-noyelle", "card": "04-knowledge/units/persons/charles-de-noyelle.md",
        "name_zh": "夏尔·德·努瓦耶尔", "name_en": "Charles de Noyelle",
        "index_file": "N.csv", "index_entry": "N.csv#43", "index_name": "Noyelle, Charles de", "page": "91",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md", "location": "第3章第IV节，印刷页91；OCR L162–163",
        "span": "lines 162–163; print p. 91", "quote": "Charles de Noy elle",
        "summary": "Haskell称Charles de Noyelle为Oliva之后的耶稣会总会长继任者；书后索引以“Noyelle, Charles de”指向第91页。",
        "description_zh": "本卡登记哈斯克尔第3章第IV节第91页所称Charles de Noyelle。正文称他为Oliva之后的比利时籍耶稣会总会长继任者，并说其四年任期不足以推进许多事项；OCR将姓氏断作“Noy elle”，同页书后索引写作“Noyelle, Charles de”。本卡保留姓名校正依据，不补充其他生平信息。中文显示名为项目工作音译。",
        "description_en": "This card records Charles de Noyelle named on page 91 of Chapter 3, section IV. The passage calls him Oliva's Belgian successor as Jesuit Superior General and says his four-year generalship was too short for much to be done; OCR splits the surname as “Noy elle”, while the index gives “Noyelle, Charles de”. The card preserves the basis for the normalized name without adding other biography. The Chinese display name is a working transliteration.",
        "context_zh": "原文语境记录其任耶稣会总会长的四年任期；该S2陈述未标记为关系候选，本次不建立正式关系。",
        "context_en": "The source reports his four-year term as Jesuit Superior General; the S2 statement is not marked as a relation candidate, and this registration creates no formal relation.",
        "name_rows": [("索引姓名", "Noyelle, Charles de", "S1"), ("正文姓名（校正OCR断行）", "Charles de Noyelle", "S2")],
    },
]


def make_source(t: dict, index: bool) -> dict:
    if index:
        return {
            "citation": f"Francis Haskell, *Patrons and Painters*, index, {t['index_file']}.",
            "location": f"书后索引，{t['index_entry']}；指向印刷页{t['page']}",
            "sentence_summary": f"索引以“{t['index_name']}”为主条并指向印刷页{t['page']}。",
            "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}", "source_span": t["index_entry"]},
        }
    return {
        "citation": BOOK, "location": t["location"], "sentence_summary": t["summary"],
        "original_quotes": [{"source_span": t["span"], "text": t["quote"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["source_file"], "source_span": t["span"]},
    }


def make_card(t: dict) -> str:
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": [make_source(t, True), make_source(t, False)],
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
    parser = argparse.ArgumentParser(description="Register four S3-new person identity groups from M/N index passages.")
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
        assert candidate.get("index_entry_id") == t["index_entry"] and candidate.get("canonical_name") == t["index_name"] and candidate.get("index_page_range") == t["page"]
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
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Murray、Nadal、Novelli与Noyelle四组索引人物登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四组均为单候选S3 new身份组；均依据书后索引与正文姓名登记，不新增外部来源或正式关系。Pietro Novelli的索引别称保留，并未仅凭姓氏并入既有Pietro Antonio Novelli卡；两组的历史身份关系未由本批外部核验。"
        + " `cand-1748`（Abbé Nollet）本批暂缓S4登记：索引与正文仅给出尊称加姓氏，没有足以唯一登记的完整姓名依据；S3决定保留，待获得进一步身份依据后再回到S4。\n\n"
        + f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        + f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        + f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物身份组登记：Murray、Nadal、Novelli与Noyelle（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。四组均为S3 new，各登记一张KU；Pietro Novelli索引别称照录，未凭姓氏与既有Pietro Antonio Novelli合并，历史身份关系待核。`cand-1748` Abbé Nollet因称名不足暂缓S4，不改动其S3决定。"
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
