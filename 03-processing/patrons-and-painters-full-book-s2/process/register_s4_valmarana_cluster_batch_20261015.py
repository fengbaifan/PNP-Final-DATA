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
TYPE_DIRS = {"family": "families", "person": "persons", "place": "places", "work": "works"}
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
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


BATCHES = {
    "family": [
        {
            "candidate": "cand-6461", "group": "sg3-family-cand-6461",
            "slug": "altieri-family-clement-x", "name_zh": "阿尔蒂耶里家族",
            "name_en": "Altieri family",
            "description_zh": "哈斯克尔称克勉十世的家族为 Altieri，并说其最紧迫的顾虑之一是在教皇去世前完成新家族宫邸。此卡保留家族集体指称，不把家族等同于宫邸或 Don Gasparo Altieri。",
            "description_en": "Haskell identifies Clement X's family as the Altieri and says one of its pressing concerns was completing a new family palace before the pope died. This card preserves the collective family reference and keeps the family distinct from the palace and Don Gasparo Altieri.",
            "context_zh": "第6章第161页将家族建造宫邸的顾虑置于克勉十世年迈、宫邸工程持续进行的叙述中。",
            "context_en": "Chapter 6 (p. 161) places the family's concern about completing its palace within the account of Clement X's advanced age and the ongoing building work.",
            "boundary_zh": "只登记本书明确称为 Altieri 的家族集体；不据姓氏或宫邸活动推定全部成员、支系或个人关系。",
            "boundary_en": "Register only the collective family Haskell calls the Altieri; do not infer all members, branches, or individual relationships from the surname or palace activity.",
            "sources": [source("6", "161", "06_CHP-6_sec_v.md", "5", "the great and natural preoccupation of his family, the Altieri, was that he would die before they had time to complete the new family palace", "哈斯克尔称克勉十世的 Altieri 家族担心无法在其去世前完成新家族宫邸。")],
        },
        {
            "candidate": "cand-10485", "group": "sg3-family-cand-10485",
            "slug": "brunswick-house-family", "name_zh": "不伦瑞克王室",
            "name_en": "House of Brunswick",
            "description_zh": "哈斯克尔称帕多瓦公民 Azzo, Marchese d’Este 为 Brunswick 家族的创始者。该表述仅作为本书关于该家族的来源性说法登记，未作外部核验。",
            "description_en": "Haskell describes the Paduan citizen Azzo, Marchese d’Este, as the originator of the House of Brunswick. This is recorded as the book's source-bounded account and has not been externally verified.",
            "context_zh": "第15章印刷页366在 Prato della Valle 雕像计划的叙述中提及该家族；OCR 页标 L14 仅显示 `[Page 66]`，处理记录据页序和相邻标记定位为印刷页366。",
            "context_en": "Chapter 15 (printed p. 366) names the house in the account of the Prato della Valle statue scheme. The OCR page marker at L14 reads only `[Page 66]`; the processing record locates it at printed p. 366 from page sequence and adjacent markers.",
            "boundary_zh": "不以本书的起源说补写王朝谱系、成员或后续分支；OCR 页标差异保留待原件核对。",
            "boundary_en": "Do not expand the book's origin statement into a genealogy, membership list, or later branches; retain the OCR page-marker discrepancy for source-image review.",
            "sources": [source("15", "366", "15_CHP-15_sec_ii.md", "18", "Azzo, Marchese d’Este, a Paduan citizen who had been the originator of the house of Brunswick", "哈斯克尔称 Azzo, Marchese d’Este 是帕多瓦公民及 Brunswick 家族的创始者。", "S2 处理记录定位印刷页366；来源 OCR 页标 L14 仅读作[Page 66]。")],
        },
        {
            "candidate": "cand-6669", "group": "sg3-review-gonzaga-family-redirect",
            "slug": "gonzaga-family-mantua", "name_zh": "曼图亚贡扎加家族",
            "name_en": "Gonzaga family in Mantua",
            "description_zh": "哈斯克尔称 Mantua 的 Gonzaga 家族是 Marie de’ Medici 可利用的家族联姻联系之一，并以她的姐妹嫁给 Vincenzo 公爵说明该联系。",
            "description_en": "Haskell names the Gonzaga in Mantua as one of Marie de’ Medici's useful family marriage connections and explains the link by noting that her sister married Duke Vincenzo.",
            "context_zh": "第7章第174页仅提供 Mantua 的集体家族称谓及婚姻联系语境。",
            "context_en": "Chapter 7 (p. 174) gives only the collective family reference in Mantua and its marriage-connection context.",
            "boundary_zh": "保持 Mantua 语境的一般 Gonzaga 家族身份，不推定具体支系。索引交叉引用 cand-2906 已按 S1 排除，本卡不复活或映射该索引项。",
            "boundary_en": "Keep the general Gonzaga family identity in its Mantua context without inferring a particular branch. Index redirect cand-2906 remains excluded under S1 and is neither reopened nor mapped by this card.",
            "sources": [source("7", "174", "07_CHP-7_sec_i.md", "46–47", "and the Gonzaga in Mantua (her sister married Duke\nVincenzo)", "哈斯克尔以 Marie de’ Medici 的姐妹嫁给 Vincenzo 公爵说明其与 Mantua Gonzaga 家族的联姻联系。")],
        },
        {
            "candidate": "cand-2688", "group": "sg3-family-cand-2688",
            "slug": "valmarana-family-vicenza", "name_zh": "瓦尔马拉纳家族",
            "name_en": "Valmarana family",
            "description_zh": "哈斯克尔第9章称 Tiepolo 为维琴察的 Valmarana 家族绘制一组壁画；第20章后记转述 Puppi 的研究，明确更正此前的委托归属，称委托者是 Conte Giustino Valmarana，而非 Leonardo Valmarana。",
            "description_en": "In Chapter 9, Haskell says Tiepolo painted a fresco cycle for the Valmarana family in Vicenza. The Chapter 20 postscript reports Puppi's research and explicitly corrects the earlier commission attribution: the commissioner was Conte Giustino Valmarana, not Leonardo Valmarana.",
            "context_zh": "第9章 p.258 将壁画与家族相连，并谨慎称 Leonardo 似在1757年为家族首领；第20章 p.405 回指同一组作品并将委托归于 Giustino。",
            "context_en": "Chapter 9 (p. 258) connects the frescoes with the family and cautiously says Leonardo seems to have headed it in 1757; Chapter 20 (p. 405) refers back to the same works and attributes the commission to Giustino.",
            "boundary_zh": "家族身份、Leonardo 的来源限定头衔与 Giustino 的委托角色分开。p.405 是 Haskell 转述 Puppi；该文章未独立查阅。",
            "boundary_en": "Keep the family identity, the qualified report of Leonardo's family role, and Giustino's commissioning role distinct. The p. 405 account is Haskell reporting Puppi; the article was not independently consulted.",
            "sources": [
                source("9", "258", "09_CHP-9_intro.md", "182–184", "which he painted for the\nValmarana family in Vicenza", "第9章称 Tiepolo 为维琴察的 Valmarana 家族绘制壁画组，并另述 Leonardo 似为家族首领。"),
                source("20", "405", "20_CHP-20Postscript.md", "142–143", "Puppi has demonstrated beyond the shadow of a doubt that I was quite wrong in attributing to the sweet-tempered and humble Leonardo Valmarana the commissioning of Tiepolo’s frescoes in the family\nVilla near Vicenza illustrating scenes from Homer, Virgil, Ariosto and Tasso. These beautiful works, so different in seeling from those generally produced by Tiepolo for the local nobility, were in fact commissioned by Conte Giustino Valmarana", "后记回指 Valmarana 家族别墅及同组壁画，转述 Puppi 对委托者的更正；来源 OCR `seeling` 的印本读法已在 S2 页图校读中记为 `feeling`。", "Haskell 对 Puppi 研究的报告；该文未独立查阅。")
            ],
        },
        {
            "candidate": "cand-2832", "group": "sg3-family-cand-2832",
            "slug": "zambelli-family-pittoni", "name_zh": "赞贝利家族",
            "name_en": "Zambelli family",
            "description_zh": "哈斯克尔脚注以“the Zambelli of Pittoni”列举一个家族集体称谓，并引 Moschini 1806。脚注未提供成员姓名或进一步的家族沿革。",
            "description_en": "Haskell's footnote uses the collective expression “the Zambelli of Pittoni” and cites Moschini 1806. It gives no member names or further family history.",
            "context_zh": "第9章 p.260 注8将该称谓与 Zenobio、Miani of Camerata、Baglione of Polazzo 并列为例。",
            "context_en": "Chapter 9 (p. 260 n. 8) lists the expression alongside the Zenobio, Miani of Camerata, and Baglione of Polazzo as examples.",
            "boundary_zh": "保留脚注中的姓氏集体及 Pittoni 语境；不把它与人物 Dottoressa Paola Zambelli 合并，也不据单条引文补写支系或具体成员。",
            "boundary_en": "Preserve the surname collective and its Pittoni context; do not merge it with Dottoressa Paola Zambelli or infer a branch or individual members from this single citation.",
            "sources": [source("9", "260 n. 8", "09_CHP-9_intro_notes_p260_visual-transcription.md", "1", "and the Zambelli of Pittoni at the end of his life (G. A. Moschini, 1806, III, p. 70)", "脚注将 Zambelli of Pittoni 列为一个例子，并引 Moschini 1806 第三卷第70页。", "派生视觉转录行；保留书内引证，不声称独立查阅 Moschini。")],
        },
    ],
    "person": [
        {
            "candidate": "cand-2689", "group": "new-person:co-leonardo-valmarana-leonardo-valmarana-4c7a74fe27",
            "slug": "leonardo-valmarana", "name_zh": "莱昂纳多·瓦尔马拉纳",
            "name_en": "Leonardo Valmarana",
            "description_zh": "哈斯克尔称 Leonardo Valmarana 似在1757年为家族首领；第20章后记更正壁画委托者是 Conte Giustino Valmarana，并未否定第9章对 Leonardo 家族身份的这一谨慎说法。其人格描述来自葬礼演说，哈斯克尔明确提示该来源不适合做公正的人格评估。",
            "description_en": "Haskell says Leonardo Valmarana seems to have headed the family in 1757. The Chapter 20 postscript corrects the fresco commission to Conte Giustino Valmarana but does not retract the qualified statement about Leonardo's family role. Haskell attributes the character portrait to a funeral oration and warns that it is not an impartial source for character.",
            "context_zh": "第9章 p.258 的“似为家族首领”是嵌套转述；第20章 p.405 更正的是委托人身份，两者不是同一事实。",
            "context_en": "The Chapter 9 (p. 258) statement that he “seems” to have headed the family is nested reporting; the Chapter 20 (p. 405) correction concerns the commissioner, a separate fact.",
            "boundary_zh": "不登记未经来源支持的出生、死亡、任职或完整谱系；不把家族首领身份改写为委托人身份。",
            "boundary_en": "Do not add unsupported birth, death, office, or genealogy; do not convert the family-head report into a commissioning role.",
            "sources": [
                source("9", "258", "09_CHP-9_intro.md", "183–184", "we are told of Leonardo Valmarana, who seems to have been the head of the family when the frescoes were painted in 1757", "哈斯克尔转述 Leonardo 似在壁画绘制时为家族首领，并保留不确定措辞。"),
                source("20", "405", "20_CHP-20Postscript.md", "142–143", "I was quite wrong in attributing to the sweet-tempered and humble Leonardo Valmarana the commissioning of Tiepolo’s frescoes", "后记更正 Leonardo 并非这组壁画的委托者；这不否定前文谨慎报告的家族首领身份。")
            ],
            "type_notes_zh": "姓名：原书写作 Leonardo Valmarana；家族身份只按第9章的限定陈述保留。",
            "type_notes_en": "Name: the book writes Leonardo Valmarana; family status is retained only as the qualified Chapter 9 report.",
        },
        {
            "candidate": "cand-11067", "group": "new-person:conte-giustino-valmarana-d74cf068d7",
            "slug": "giustino-valmarana", "name_zh": "朱斯蒂诺·瓦尔马拉纳伯爵",
            "name_en": "Giustino Valmarana",
            "description_zh": "第20章后记称 Conte Giustino Valmarana 于1757年去世，并转述 Puppi 的研究，称他委托了 Tiepolo 为 Valmarana 家族别墅绘制的壁画。其余身世仅限哈斯克尔在该段中的简短描述。",
            "description_en": "The Chapter 20 postscript says Conte Giustino Valmarana died in 1757 and reports Puppi's research that he commissioned Tiepolo's frescoes for the Valmarana family villa. Further biography is limited to Haskell's brief account in that passage.",
            "context_zh": "第20章 p.405 将其称为富有、办事有效且低调的地产所有者；该评价与委托信息均为 Haskell 转述 Puppi，论文未独立查阅。",
            "context_en": "Chapter 20 (p. 405) describes him as a very rich, efficient, and retiring landowner; both the evaluation and commission account are Haskell reporting Puppi, whose article was not independently consulted.",
            "boundary_zh": "原书称谓 Conte 保留在名称语境中，不据此扩展爵位沿革或亲属关系。",
            "boundary_en": "Retain the source form Conte in context; do not expand it into a title history or kinship claims.",
            "sources": [source("20", "405", "20_CHP-20Postscript.md", "143", "were in fact commissioned by Conte Giustino Valmarana (who died in 1757)", "Haskell 转述 Puppi 的结论，称实际委托者是 Giustino Valmarana 伯爵，并报告其卒于1757年。", "Haskell 对 Puppi 研究的报告；该文未独立查阅。")],
            "type_notes_zh": "姓名：原书称 Conte Giustino Valmarana；伯爵称谓与人名分开理解，除此不补写头衔或家系。",
            "type_notes_en": "Name: the source form is Conte Giustino Valmarana; the title is kept distinct from the personal name, with no further title or genealogy inferred.",
        },
    ],
    "place": [
        {
            "candidate": "cand-8444", "group": "sg3-place-cand-8444",
            "slug": "villa-valmarana-vicenza-haskell-reference", "name_zh": "瓦尔马拉纳别墅（维琴察）",
            "name_en": "Villa Valmarana at Vicenza",
            "description_zh": "哈斯克尔在第9章称 Villa Valmarana，并将壁画组置于维琴察的 Valmarana 家族语境；第20章后记再次称该家族别墅位于维琴察附近。",
            "description_en": "Haskell names the Villa Valmarana in Chapter 9 and places the fresco cycle in the context of the Valmarana family in Vicenza; the Chapter 20 postscript again refers to the family villa near Vicenza.",
            "context_zh": "p.258 与 p.405 的交叉提及支持书内同一 Villa Valmarana 指称；S3 说明不推定具体建筑群或房间。",
            "context_en": "The cross-chapter references at pp. 258 and 405 support the same Villa Valmarana reference in the book; S3 does not infer a more precise architectural complex or room.",
            "boundary_zh": "仅登记书内可辨认的别墅地点称谓；不补坐标、建筑沿革、所有权或别墅内部具体建筑身份。",
            "boundary_en": "Register only the villa place-name identifiable in the book; do not add coordinates, architectural history, ownership, or a more specific building identity.",
            "sources": [
                source("9", "258", "09_CHP-9_intro.md", "184", "at the Villa Valmarana", "哈斯克尔以 Villa Valmarana 指称壁画语境中的别墅地点。"),
                source("20", "405", "20_CHP-20Postscript.md", "143", "Villa near Vicenza", "后记回指同组壁画所在的家族别墅，并称其位于维琴察附近。")
            ],
        },
        {
            "candidate": "cand-2769", "group": "sg3-place-cand-2769",
            "slug": "vicenza", "name_zh": "维琴察", "name_en": "Vicenza",
            "description_zh": "哈斯克尔在多章中以 Vicenza 指称一座城市：第9章将其与 Valmarana 家族别墅和 Cordellina 宅邸相连，第14章记 Algarotti 曾旅行至此，第20章称 Valmarana 别墅在其附近。",
            "description_en": "Across several chapters Haskell uses Vicenza as a city: Chapter 9 associates it with the Valmarana family villa and a Cordellina house, Chapter 14 says Algarotti travelled there, and Chapter 20 places the Valmarana villa nearby.",
            "context_zh": "跨章同一性由第9章 p.258、第14章 p.348 與第20章 p.405 的城市用例支持；本卡仅记录书中地点指称。",
            "context_en": "Cross-chapter identity is supported by the city references in Chapter 9 (p. 258), Chapter 14 (p. 348), and Chapter 20 (p. 405); this card records only the place reference in the book.",
            "boundary_zh": "不补现代行政边界、坐标或人口；城市与 Villa Valmarana、Cordellina 宅邸分别登记。",
            "boundary_en": "Do not add modern administrative boundaries, coordinates, or population; keep the city distinct from Villa Valmarana and the Cordellina house.",
            "sources": [
                source("9", "258", "09_CHP-9_intro.md", "183", "Valmarana family in Vicenza", "家族壁画叙述将 Valmarana 家族置于 Vicenza。"),
                source("14", "348", "14_CHP-14_intro.md", "16–17", "He travelled between Venice, Padua, Vicenza and Verona", "哈斯克尔记 Algarotti 曾在 Veneto 城市之间旅行，其中包括 Vicenza。"),
                source("20", "405", "20_CHP-20Postscript.md", "143", "Villa near Vicenza", "后记称 Valmarana 家族别墅位于 Vicenza 附近。")
            ],
        },
    ],
    "work": [
        {
            "candidate": "cand-2594", "group": "sg3-work-valmarana-fresco-cycle",
            "slug": "tiepolo-valmarana-fresco-cycle",
            "name_zh": "提埃坡罗的瓦尔马拉纳别墅壁画组",
            "name_en": "Tiepolo’s Valmarana villa fresco cycle",
            "description_zh": "哈斯克尔称 Tiepolo 为维琴察的 Valmarana 家族别墅绘制了一组表现 Homer、Virgil、Tasso 与 Ariosto 浪漫场景的壁画。第20章后记转述 Puppi 的研究，明确更正委托者为 Conte Giustino Valmarana，而非 Leonardo。",
            "description_en": "Haskell says Tiepolo painted a cycle of frescoes for the Valmarana family villa in Vicenza, illustrating romantic scenes from Homer, Virgil, Tasso, and Ariosto. The Chapter 20 postscript reports Puppi's research and corrects the commissioner to Conte Giustino Valmarana rather than Leonardo.",
            "context_zh": "第9章 p.258 记作品类型、题材范围及家族语境；第20章 p.405 回指同组作品，报告 Puppi 对委托人的更正。",
            "context_en": "Chapter 9 (p. 258) gives the work type, subject range, and family context; Chapter 20 (p. 405) refers back to the same cycle and reports Puppi's correction of the commissioner.",
            "boundary_zh": "中文和英文题名均为便于识别所拟的描述性暂题，并非原作题名。未拆分具体壁画、未命名单幅作品、复制版本或现存状态；委托关系仍待 S6 正式审查。Puppi 文章未独立查阅。",
            "boundary_en": "The Chinese and English titles are descriptive working titles, not original titles. No individual fresco, unnamed single work, copy, or survival status is inferred; the commission relation remains for formal S6 review. Puppi's article was not independently consulted.",
            "sources": [
                source("9", "258", "09_CHP-9_intro.md", "182–183", "beautiful series of frescoes illustrating romantic scenes from Homer, Virgil, Tasso and Ariosto which he painted for the\nValmarana family in Vicenza", "哈斯克尔称 Tiepolo 为 Valmarana 家族在 Vicenza 绘制一组取材于四位诗人作品的浪漫场景壁画。"),
                source("20", "405", "20_CHP-20Postscript.md", "142–143", "were in fact commissioned by Conte Giustino Valmarana (who died in 1757)", "后记回指该组作品，并转述 Puppi 的结论称委托者为 Conte Giustino Valmarana。", "Haskell 对 Puppi 研究的报告；该文未独立查阅。")
            ],
            "type_notes_zh": "作品类型：壁画组；创作者：原书称 Giambattista Tiepolo。委托者按后记的研究转述记录为 Giustino，不将第9章所称家族首领 Leonardo 等同于委托人。原书未给具体画名、技法或现存状况。",
            "type_notes_en": "Work type: fresco cycle; creator: named by the book as Giambattista Tiepolo. The postscript's reported research identifies Giustino as commissioner; the Chapter 9 family-head report about Leonardo is not treated as a commission. The book gives no individual titles, technique, or survival status.",
        },
    ],
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def make_card(record, kind):
    source_rows = []
    for item in record["sources"]:
        loc_note = item["location_note"]
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}" + (f"；{loc_note}" if loc_note else ""),
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}" + (f"; {loc_note}" if loc_note else ""),
            },
        })
    frontmatter = {
        "title": f"{record['name_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": kind,
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-15",
        "updated": "2026-10-15",
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    type_notes = ""
    if record.get("type_notes_zh"):
        type_notes = f"\n### 类型记录\n\n中文：{record['type_notes_zh']}\n\nEnglish: {record['type_notes_en']}\n"
    body = f"""## 内容

### 描述

**中文：** {record['description_zh']}

**English:** {record['description_en']}

### 名称

中文显示名及英文显示名见卡片标题；中文名为便于识别所用音译或描述性暂译，原书用词按来源引文保留。

The bilingual display names appear in the card title. The Chinese name is a transliteration or descriptive rendering for readability; the book's wording is preserved in the source quotations.

### 本书语境

{record['context_zh']}

{record['context_en']}
{type_notes}
### 身份边界

中文：{record['boundary_zh']}

English: {record['boundary_en']}

## 关系与证据

本轮完成身份登记；S2 中涉及的创作、委托、地点、家族和人物陈述仍须按正式端点及证据在 S6 审查。本卡未新增正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def type_dir(kind):
    return TYPE_DIRS[kind]


def main():
    parser = argparse.ArgumentParser(description="Register S4 cards for the cross-chapter Valmarana identity cluster")
    parser.add_argument("--type", choices=sorted(BATCHES), required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    kind = args.type
    batch = BATCHES[kind]

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_alignment = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    expected_manifest = {"family": 1106, "work": 1111, "person": 1112, "place": 1114}
    expected_registered = {"family": (87, 93), "work": (92, 98), "person": (93, 99), "place": (95, 101)}
    assert len(manifest) == expected_manifest[kind], f"unexpected manifest count: {len(manifest)}"
    new_rows = [row for row in alignments if not row.get("external_source") and row.get("decision") == "new"]
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        new_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
    assert len(new_rows) == 5008 and len(new_groups) == 4831
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(registered_groups), sum(len(rows) for rows in registered_groups.values())) == expected_registered[kind]
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    candidate_endpoints = set()
    candidate_mentions = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            candidate_endpoints.update(cid for cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) if cid)
            candidate_mentions.update(statement.get("qualifiers", {}).get("mentioned_candidate_ids", []))
    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as f:
        mention_rows = list(csv.DictReader(f))
    s2_mention_candidates = {row["candidate_id"] for row in mention_rows if row.get("candidate_id")}
    all_source_files = {}
    for record in batch:
        cid = record["candidate"]
        candidate = candidate_by_id[cid]
        alignment = candidate_alignment[cid]
        assert candidate["suggested_type"] == kind
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == record["group"]
        assert cid in candidate_endpoints or cid in candidate_mentions or cid in s2_mention_candidates, cid
        group_rows = new_groups[record["group"]]
        assert [row["candidate_id"] for row in group_rows] == [cid], record["group"]
        if cid == "cand-6669":
            excluded = candidate_alignment["cand-2906"]
            assert excluded["decision"] == "excluded" and not excluded.get("ku_id")
        card_path = UNITS / type_dir(kind) / f"{record['slug']}.md"
        rel_path = f"04-knowledge/units/{type_dir(kind)}/{record['slug']}.md"
        ku_id = f"units/{type_dir(kind)}/{record['slug']}"
        assert not card_path.exists(), card_path
        assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
        assert rel_path not in accepted_text
        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            all_source_files[item["file"]] = source_path
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (cid, item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    new_paths = []
    for record in batch:
        cid = record["candidate"]
        ku_id = f"units/{type_dir(kind)}/{record['slug']}"
        rel_path = f"04-knowledge/units/{type_dir(kind)}/{record['slug']}.md"
        planned_by_id[cid]["ku_id"] = ku_id
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {record['group']} to {ku_id}."
        planned_manifest.append({
            "ku_id": ku_id,
            "type": kind,
            "canonical_name": record["name_zh"],
            "name_en": record["name_en"],
            "source_task": TASK,
            "card_path": rel_path,
        })
        new_paths.append(rel_path)

    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if row.get("external_source") or row.get("decision") != "new":
            continue
        planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    expected_after = {"family": (92, 98), "work": (93, 99), "person": (95, 101), "place": (97, 103)}
    assert (len(planned_registered), sum(len(rows) for rows in planned_registered.values())) == expected_after[kind]

    if args.dry_run:
        print(
            f"dry-run passed: type={kind} groups={len(batch)} candidates={len(batch)} "
            f"registered_groups_after={len(planned_registered)} mapped_candidates_after="
            f"{sum(len(rows) for rows in planned_registered.values())} manifest_after={len(planned_manifest)}"
        )
        return 0

    for record in batch:
        target = UNITS / type_dir(kind) / f"{record['slug']}.md"
        target.write_text(make_card(record, kind), encoding="utf-8-sig", newline="\n")
    write_csv(manifest_path, manifest_fields, planned_manifest)
    write_csv(alignment_path, alignment_fields, planned_alignment)

    accepted_lines = accepted_text.splitlines()
    for rel_path in sorted(new_paths):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {rel_path}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(f"applied: type={kind} groups={len(batch)} candidates={len(batch)} manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
