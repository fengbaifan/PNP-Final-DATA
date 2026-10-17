from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-family-ch9"
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
        "group": "sg3-family-cornerfamily",
        "candidates": ["cand-0847", "cand-0848"],
        "slug": "corner-family",
        "name_zh": "科尔纳家族",
        "name_en": "Corner family",
        "description_zh": "哈斯克尔将 Corner 列为声称拥有罗马祖先的威尼斯家族之一，并称他们曾委托提埃波罗和拉扎里尼创作家族历史题材作品。这里保留原书的集体家族指称，不把未具名家族成员识别为具体人物。",
        "description_en": "Haskell lists the Corner among Venetian families claiming Roman ancestry and says they commissioned Tiepolo and Lazzarini to paint family-history subjects. This record preserves the book's collective family reference and does not identify an unnamed member as a specific person.",
        "context_zh": "第9章第252页称提埃波罗在1722年前曾为 Corner 工作；第255页称 Corner 于1700年委托拉扎里尼绘制一位曾在康布雷同盟战争时期建立功绩的家族成员。",
        "context_en": "Chapter 9 says Tiepolo had worked for the Corner before 1722 (p. 252), and that in 1700 the Corner commissioned Lazzarini to depict a family member distinguished during the War of the League of Cambrai (p. 255).",
        "scope_zh": "不据此确定 Corner 的完整谱系，也不把家族委托指派给某一位未具名成员。",
        "scope_en": "This account does not establish a complete Corner genealogy or assign the family commission to an unnamed individual member.",
        "sources": [
            source("9", "252", "09_CHP-9_intro.md", "118", "for many Venetian families claimed Roman ancestry—among them the Corner, for whom he is known to have worked before 1722.", "哈斯克尔称许多威尼斯家族声称具有罗马祖先，其中包括提埃波罗在1722年前曾为之工作的 Corner。"),
            source("9", "255", "09_CHP-9_intro.md", "153", "1700 the Corner commissioned Gregorio Lazzarini to paint a member of their family who had distinguished himself at the time of the League of Cambrai—Venice’s finest hour.", "哈斯克尔称 Corner 于1700年委托拉扎里尼绘制一位在康布雷同盟战争时期建立功绩的家族成员。"),
        ],
    },
    {
        "group": "sg3-family-cand-1197",
        "candidates": ["cand-1197"],
        "slug": "giustiniani-family",
        "name_zh": "朱斯蒂尼亚尼家族",
        "name_en": "Giustiniani family",
        "description_zh": "哈斯克尔称 Giustiniani 家族曾在其宫殿或乡间宅邸中设置家族神化题材的装饰画。该卡只登记原书明确提及的集体家族及其装饰语境。",
        "description_en": "Haskell says the Giustiniani had family-apotheosis paintings in their palaces or country houses. This card records only the collective family and decorative context explicitly named in the book.",
        "context_zh": "第9章第254页将 Giustiniani 与 Grassi、Widmann、Soderini 并列，称这些家族都曾在宫殿或乡间宅邸绘制家族神化题材。",
        "context_en": "On page 254, Chapter 9 names the Giustiniani alongside the Grassi, Widmann, and Soderini as families with apotheoses painted in their palaces or country houses.",
        "scope_zh": "不推断具体成员、支系、谱系或相关装饰的具体画家。",
        "scope_en": "No individual members, branches, genealogy, or specific painter for these decorations is inferred.",
        "sources": [
            source("9", "254", "09_CHP-9_intro.md", "142", "The Grassi,2 the Widmann, the Giustiniani3 and the Soderini all had apotheoses of their families painted in their palaces or country houses", "哈斯克尔将 Giustiniani 列入曾在宫殿或乡间宅邸绘制家族神化题材的威尼斯家族。"),
        ],
    },
    {
        "group": "sg3-family-cand-1228",
        "candidates": ["cand-1228"],
        "slug": "grassi-family-venice",
        "name_zh": "格拉西家族",
        "name_en": "Grassi family",
        "description_zh": "哈斯克尔称 Grassi 家族曾在宫殿或乡间宅邸设置家族神化题材装饰，并将其描述为1699年付费进入贵族阶层的新贵家族；他还称该家族在18世纪建立了贵族家族中少见的绘画收藏。",
        "description_en": "Haskell says the Grassi had family-apotheosis decoration in a palace or country house and describes them as a newly ennobled family that bought entry into the aristocracy in 1699; he also says they built a rare eighteenth-century picture collection among patrician families.",
        "context_zh": "第9章第254—255页将 Grassi 列为家族神化装饰的赞助者，并称这类历史题材超出 Widmann 或 Grassi 所能负担的范围。",
        "context_en": "Chapter 9 (pp. 254–255) includes the Grassi among patrons of family-apotheosis decoration and says historical subjects of this kind were beyond the means of a Widmann or a Grassi.",
        "scope_zh": "不把集体收藏或赞助陈述归给某一位 Grassi 成员，也不补写家族谱系。",
        "scope_en": "The collective collection and patronage statements are not assigned to an individual Grassi member, and no genealogy is supplied.",
        "sources": [
            source("9", "254", "09_CHP-9_intro.md", "142", "The Grassi,2 the Widmann, the Giustiniani3 and the Soderini all had apotheoses of their families painted in their palaces or country houses", "哈斯克尔称 Grassi 家族曾在宫殿或乡间宅邸绘制家族神化题材。"),
            source("9", "255", "09_CHP-9_intro.md", "153", "beyond the reach of a Widmann or a Grassi.", "哈斯克尔称回溯家族历史的绘画题材超出 Widmann 或 Grassi 的财力范围。"),
        ],
    },
    {
        "group": "sg3-family-cand-1349",
        "candidates": ["cand-1349"],
        "slug": "labia-family",
        "name_zh": "拉比亚家族",
        "name_en": "Labia family",
        "description_zh": "哈斯克尔将 Labia 描述为具有加泰罗尼亚渊源、财富丰厚的威尼斯商人家族，记载其兴建大型宫殿并以显赫装饰展示财富；第8章注释也将 Labia 列入拥有那不勒斯画家作品的家族。",
        "description_en": "Haskell describes the Labia as wealthy Venetian businessmen of Catalan origin who built a large palace and displayed their wealth through its decoration. A Chapter 8 note also lists the Labia among families who owned works by Neapolitan painters.",
        "context_zh": "第9章第250页记载 Labia 的宫殿建设、装饰与绘画收藏；第257页称该家族因奢华宴会而闻名。第8章第214页注释将 Labia 与其他威尼斯藏家并列。",
        "context_en": "Chapter 9 (p. 250) describes the Labia palace, its decoration, and picture holdings; page 257 says the family became legendary for lavish banquets. A Chapter 8 note on p. 214 lists the Labia with other Venetian picture owners.",
        "scope_zh": "书中另提家族成员 Maria Labia；本卡不据此扩展成员清单，也不将个人珠宝或身份自动归为家族财产。",
        "scope_en": "The book separately names the family member Maria Labia; this card does not expand a membership list or automatically treat her personal jewels or status as family property.",
        "sources": [
            source("9", "250", "09_CHP-9_intro.md", "95", "The Labia, rich businessmen of Catalan origin, had also set about building a gigantic palace which was completed in the early eighteenth century and were engaged in displaying their great wealth in as ostentatious a manner as possible.", "哈斯克尔称 Labia 是具有加泰罗尼亚渊源的富裕商人家族，兴建大型宫殿并以奢华方式展示财富。"),
            source("9", "257", "09_CHP-9_intro.md", "168", "the Labia, whose palace contained Tiepolo’s most magnificent version of the subject, became legendary for their extravagance.", "哈斯克尔称 Labia 因奢华宴会闻名，其宫殿收藏了提埃波罗对该题材最宏伟的表现。"),
            source("8", "214", "08_CHP-8_sec_i_notes_p214_visual-transcription.md", "4", "Besides the Labia, who are discussed separately in Chapter 9, the Procuratore Canale, Flaminio Corner, the Giovanelli and the Widmann all owned pictures by one or other of them", "第8章注释将 Labia 与 Canale、Corner、Giovanelli、Widmann 并列为拥有 Luca Giordano 或 Solimena 作品者。", "（视觉转录）"),
        ],
    },
    {
        "group": "sg3-family-cand-1519",
        "candidates": ["cand-1519"],
        "slug": "manin-family",
        "name_zh": "马宁家族",
        "name_en": "Manin family",
        "description_zh": "哈斯克尔称来自 Friuli 的 Manin 家族持续装饰威尼斯及周边的宫殿、乡间宅邸和教堂；他还记载该家族参与 Udine 主教座堂与威尼斯教堂的装饰工程。",
        "description_en": "Haskell says the Manin from Friuli repeatedly decorated palaces, country houses, and churches in and around Venice; he also records the family's involvement in decoration projects at Udine Cathedral and Venetian churches.",
        "context_zh": "第9章第251页概述 Manin 家族的装饰赞助；第268页与第271页进一步记载其教堂工程及其作为耶稣会教堂主要资源来源之一。",
        "context_en": "Chapter 9 (p. 251) outlines the Manin family's decorative patronage; pages 268 and 271 further describe its church projects and its role as a major source of resources for a Jesuit church.",
        "scope_zh": "本卡保留原书的 Manin 家族集体指称。相似拼写的 Manini brothers 候选 `cand-8780` 仍未决，不据姓名相近并入本卡。",
        "scope_en": "This card preserves the book's collective reference to the Manin family. The similarly spelled Manini brothers candidate `cand-8780` remains undecided and is not merged on the basis of name resemblance.",
        "sources": [
            source("9", "251", "09_CHP-9_intro.md", "107", "Perhaps most striking of all, the Manin from the Friuli were untiring in the decoration of palaces, country houses and churches in and around Venice", "哈斯克尔称来自 Friuli 的 Manin 持续装饰威尼斯及周边的宫殿、乡间宅邸和教堂。"),
            source("9", "268", "09_CHP-9_sec_ii.md", "14", "Manin offered in 1706 to decorate the choir, transept and High Altar of the Cathedral at Udine.", "哈斯克尔记载 Manin 于1706年提出装饰 Udine 主教座堂的唱诗席、耳堂和主祭坛。"),
            source("9", "271", "09_CHP-9_sec_ii.md", "51", "Their resources, like those of many other Orders, came mostly from the exceedingly rich, but only recently ennobled, Manin family.", "哈斯克尔称耶稣会教堂的资源主要来自富裕但较新近获贵族身份的 Manin 家族。"),
        ],
    },
    {
        "group": "sg3-family-cand-2478",
        "candidates": ["cand-2478"],
        "slug": "soderini-family",
        "name_zh": "索德里尼家族",
        "name_en": "Soderini family",
        "description_zh": "哈斯克尔称 Soderini 家族曾为其家族历史绘制提埃波罗的装饰画，并指出其具有悠久的佛罗伦萨渊源。原书此处 OCR 作 `Sodcrini`；候选索引记录作 `Soderini`，本卡保留这一文字差异，不把 OCR 读法称作扫描校勘结果。",
        "description_en": "Haskell says the Soderini commissioned Tiepolo to depict their family history and notes their long Florentine ancestry. The OCR reads `Sodcrini` at this passage, while the candidate index records `Soderini`; this card preserves the textual difference without presenting the OCR reading as a scan-based correction.",
        "context_zh": "第9章第254页将 Soderini 列为曾绘制家族神化题材的家族；第255页称其于1656年获封贵族，并拥有悠久而知名的佛罗伦萨祖先渊源。",
        "context_en": "Chapter 9 (p. 254) includes the Soderini among families with apotheosis paintings; page 255 says they were ennobled in 1656 and had a long and renowned Florentine ancestry.",
        "scope_zh": "名称采用候选索引中的 Soderini 形式；不据单处 OCR 文字差异推定支系或谱系。",
        "scope_en": "The name follows the candidate index form Soderini; the single OCR spelling difference is not used to infer a branch or genealogy.",
        "sources": [
            source("9", "254", "09_CHP-9_intro.md", "142", "The Grassi,2 the Widmann, the Giustiniani3 and the Soderini all had apotheoses of their families painted in their palaces or country houses", "哈斯克尔将 Soderini 列入曾在宫殿或乡间宅邸绘制家族神化题材的家族。"),
            source("9", "255", "09_CHP-9_intro.md", "153", "for the Sodcrini, ennobled as late as 1656, but they had a long and renowned Florentine ancestry", "OCR 在此处将 Soderini 记为 Sodcrini；同句称该家族于1656年获封贵族且具有悠久的佛罗伦萨渊源。"),
        ],
    },
    {
        "group": "sg3-family-cand-2812",
        "candidates": ["cand-2812"],
        "slug": "widmann-family",
        "name_zh": "维德曼家族",
        "name_en": "Widmann family",
        "description_zh": "哈斯克尔称 Widmann 家族源自 Carinthia，在威尼斯 S. Canciano 附近拥有宫殿，并装饰其乡间宅邸；他还将该家族列入拥有家族神化题材装饰的家族。第8章注释另记 Widmann 持有那不勒斯画家的作品。",
        "description_en": "Haskell says the Widmann originated in Carinthia, had a palace near S. Canciano in Venice, and decorated a country house; he also lists the family among those with apotheosis decoration. A Chapter 8 note separately records Widmann ownership of works by Neapolitan painters.",
        "context_zh": "第9章第250页叙述其来源地、宫殿及乡间宅邸；第254页提及家族神化装饰；第8章第214页注释将其列为作品持有人。",
        "context_en": "Chapter 9 (p. 250) describes the family's origin, palace, and country house; page 254 mentions its apotheosis decoration; a Chapter 8 note on p. 214 lists the family as a picture owner.",
        "scope_zh": "不由居所或作品持有事实推断完整产权链、家族成员或支系。",
        "scope_en": "The residence and picture-ownership references do not establish a complete title chain, membership list, or branch structure.",
        "sources": [
            source("9", "250", "09_CHP-9_intro.md", "94", "The Widmann, of Carinthian origin, had a splendid palace near S. Canciano which they too were lavishly decorating with a series of large canvases by Lazzarini showing scenes from the life of Scipio Africanus", "哈斯克尔称源自 Carinthia 的 Widmann 在 S. Canciano 附近有宫殿，并以拉扎里尼的大幅画作装饰。"),
            source("9", "254", "09_CHP-9_intro.md", "142", "The Grassi,2 the Widmann, the Giustiniani3 and the Soderini all had apotheoses of their families painted in their palaces or country houses", "哈斯克尔称 Widmann 与其他家族一样曾在宫殿或乡间宅邸绘制家族神化题材。"),
            source("8", "214", "08_CHP-8_sec_i_notes_p214_visual-transcription.md", "4", "the Giovanelli and the Widmann all owned pictures by one or other of them", "第8章注释称 Giovanelli 与 Widmann 都拥有 Luca Giordano 或 Solimena 的作品。", "（视觉转录）"),
        ],
    },
    {
        "group": "sg3-family-cand-2870",
        "candidates": ["cand-2870"],
        "slug": "zenobio-family",
        "name_zh": "泽诺比奥家族",
        "name_en": "Zenobio family",
        "description_zh": "哈斯克尔称 Zenobio 是威尼斯富裕家族之一，并记述 Carmini 宫殿的改建及其对美术的保护；第9章注释还提到 Carlevarijs 曾受雇于 Zenobio。后记再次回顾该家族的艺术赞助。",
        "description_en": "Haskell describes the Zenobio as a wealthy Venetian family, records the rebuilding of its palace at the Carmini and its protection of the arts, and notes that Carlevarijs worked for the family. The postscript revisits its artistic patronage.",
        "context_zh": "第9章第250页记载 Zenobio 宫殿及其艺术赞助；第260页注8提到 Carlevarijs 受雇于该家族；后记第405页再次讨论 Zenobio 的赞助。",
        "context_en": "Chapter 9 (p. 250) describes the Zenobio palace and artistic patronage; note 8 on p. 260 mentions Carlevarijs's employment by the family; the postscript on p. 405 revisits Zenobio patronage.",
        "scope_zh": "名称与描述限于书中的集体家族指称，不补写成员、支系或家族财产清单。",
        "scope_en": "The name and description are limited to the book's collective family reference; no members, branches, or family-property inventory are added.",
        "sources": [
            source("9", "250", "09_CHP-9_intro.md", "92", "The Zenobio were said to be the richest family in the city.", "哈斯克尔称 Zenobio 被认为是威尼斯最富裕的家族。"),
            source("9", "250", "09_CHP-9_intro.md", "93", "The young Tiepolo produced some of his earliest works for them.", "哈斯克尔称年轻的提埃波罗曾为 Zenobio 创作早期作品。"),
            source("9", "260 n. 8", "09_CHP-9_intro_notes_p260_visual-transcription.md", "1", "Such as the Zenobio employment of Carlevarijs (Mauroner, p. 15)", "第9章注8将 Carlevarijs 受雇于 Zenobio 作为相关例子。", "（视觉转录）"),
            source("postscript", "405", "20_CHP-20Postscript.md", "142", "the patronage of the Zenobio has been looked at in some detail", "后记回顾本书相关章节中对 Zenobio 艺术赞助的讨论。"),
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


def citation_label(record: dict) -> tuple[str, str]:
    chapter = record["chapter"]
    page = record["page"]
    if chapter == "postscript":
        return f"{BOOK_CITATION}, postscript, p. {page}.", f"后记，印刷页{page}"
    suffix = record.get("location_note", "")
    citation_suffix = f"p. {page}"
    location_suffix = f"印刷页{page}" if "n." not in page else f"印刷页{page.replace(' n. ', '注')}"
    return (
        f"{BOOK_CITATION}, ch. {chapter}, {citation_suffix}.",
        f"第{chapter}章，{location_suffix}{suffix}；OCR L{record['lines']}",
    )


def make_card(record: dict) -> str:
    sources = []
    for item in record["sources"]:
        citation, location = citation_label(item)
        print_location = f"print p. {item['page']}"
        sources.append(
            {
                "citation": citation,
                "location": location,
                "sentence_summary": item["summary"],
                "original_quotes": [
                    {"source_span": f"lines {item['lines']}", "text": item["quote"]}
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": f"02-sources/02-Markdown/{item['file']}",
                    "source_span": f"lines {item['lines']}; {print_location}",
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

中文显示名为{record['name_zh']}；英文名及原书所用姓氏形式为 {record['name_en'].removesuffix(' family')}。中文显示名为便于阅读所用的姓氏音译，不表示书中另有中文规范名。

The Chinese display name is a transliteration of the surname for readability. The English name and surname form used in the book are {record['name_en']}.

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
    parser = argparse.ArgumentParser(description="S4 registration for source-backed family groups in ch. 9")
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
    import json

    with statements_path.open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            candidate_endpoints.update(
                cid for cid in (
                    statement.get("subject_candidate_id"),
                    statement.get("object_candidate_id"),
                ) if cid
            )

    assert len(manifest) == 1082, f"unexpected manifest count: {len(manifest)}"
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
    assert len(registered) == 63 and sum(map(len, registered.values())) == 68
    assert len(family_groups) == 80 and sum(map(len, family_groups.values())) == 85
    family_registered = {
        group: rows for group, rows in registered.items()
        if candidate_by_id[rows[0]["candidate_id"]].get("suggested_type") == "family"
    }
    assert len(family_registered) == 39 and sum(map(len, family_registered.values())) == 43

    candidates_in_batch = [cid for record in BATCH for cid in record["candidates"]]
    assert len(BATCH) == 8 and len(candidates_in_batch) == len(set(candidates_in_batch)) == 9
    for record in BATCH:
        for candidate_id in record["candidates"]:
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
        ku_id = f"units/families/{record['slug']}"
        for candidate_id in record["candidates"]:
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
    assert len(planned_registered) == 71
    assert sum(len(rows) for rows in planned_registered.values()) == 77

    if args.dry_run:
        print(
            f"dry-run passed: family_groups={len(BATCH)} candidates={len(candidates_in_batch)} "
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
        f"applied {len(BATCH)} family groups and {len(candidates_in_batch)} candidate mappings; "
        f"manifest={len(manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
