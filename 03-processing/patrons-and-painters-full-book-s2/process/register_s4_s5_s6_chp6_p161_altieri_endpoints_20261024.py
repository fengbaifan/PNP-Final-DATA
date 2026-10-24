from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROC = ROOT / "03-processing" / TASK / "process"
TABLES = ROOT / "04-knowledge" / "tables"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PROC))
DATE = "2026-10-24"
ANCHOR = "s3-s4-s5-s6-chp6-p161-altieri-endpoints-20261024"
BOOK = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
SRC6 = "02-sources/02-Markdown/06_CHP-6_sec_v.md"
SRC6I = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
SRC6IV = "02-sources/02-Markdown/06_CHP-6_sec_iv.md"
SRC4 = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SRC1 = "02-sources/02-Markdown/01_CHP-1_sec_i.md"
SRC2 = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SRC2VIII = "02-sources/02-Markdown/02_CHP-2_sec_viii.md"


def source(file, location, span, summary, quotes):
    return {"file": file, "location": location, "span": span, "summary": summary, "quotes": quotes}


ITEMS = [
    {
        "cid": "cand-0090", "group": "sg3-place-cand-0090", "ku": "units/places/altieri-palace",
        "path": "04-knowledge/units/places/altieri-palace.md", "type": "place",
        "zh": "阿尔蒂耶里宫", "en": "Altieri Palace",
        "identity": "将第4章装饰委托、第6章 p.156 的宫邸叙述与 p.161 的新家族宫殿视为同一宫殿候选；描述性名称，不声称已识别具体现存建筑。",
        "zhdesc": "记录哈斯克尔在第4章和第6章所称的 Altieri 家族新宫殿。第4章提到 Massimi 受托监督其装饰；第6章称宫殿正在建造，并叙述主厅壁画及未完成的装饰计划。来源没有给出可核实的现存建筑身份或正式建筑名。",
        "endesc": "This unit records the new Altieri family palace described by Haskell in Chapters 4 and 6. Chapter 4 says Massimi was asked to supervise its decoration; Chapter 6 describes the palace under construction, the principal-hall fresco, and an unfinished decorative programme. These passages do not establish the identity or formal name of a surviving building.",
        "sources": [
            source(SRC4, "第4章，印刷页118，来源行221。", "line 221; print p. 118", "哈斯克尔称 Altieri 委托 Massimi 监督新宫殿装饰。", ["their new palace"]),
            source(SRC6I, "第6章，印刷页156，来源行112–118。", "lines 112–118; print p. 156", "第6章继续提及 Altieri palace；该索引／正文锚点与第4章及 p.161 的宫殿叙述对齐。", ["Altieri palace"]),
            source(SRC6, "第6章，印刷页161，来源行5、10。", "lines 5, 10; print p. 161", "哈斯克尔称新家族宫殿正在建造，并记述主厅与未完成装饰计划。", ["the new family palace", "the decoration planned for the palace"]),
        ],
        "fields": [
            ("建筑类型", "宫殿（原文称 family palace）", "S1；第6章 p.161，L5"),
            ("建造状态", "哈斯克尔称克雷芒十世时期仍在建造；未从“the work dragged on”推定具体建造年限", "S1；第6章 p.161，L5、L10"),
            ("装饰情况", "主厅天顶于1673年准备装饰；宫殿装饰计划后来未完成", "S1；第6章 p.161，L5、L10"),
        ],
        "section": "基本信息", "statements": ["st-chp6-p161-v1-06", "st-chp6-p161-v1-07", "st-chp6-p161-v1-09", "st-chp6-p161-v1-19", "st-chp6-p161-v1-19-intended-for-palace"],
    },
    {
        "cid": "cand-6462", "group": "sg3-place-cand-6462", "ku": "units/places/altieri-palace-principal-hall",
        "path": "04-knowledge/units/places/altieri-palace-principal-hall.md", "type": "place",
        "zh": "阿尔蒂耶里宫主厅", "en": "Principal Hall of the Altieri Palace",
        "identity": "独立于宫殿整体的内部空间；S3 按 place 登记，不把天顶或壁画并入空间对象。",
        "zhdesc": "记录哈斯克尔所称 Altieri 宫殿主厅。原书称主厅天顶到1673年已准备装饰；该日期不表示整座宫殿或装饰计划已经完工。",
        "endesc": "This unit records the principal hall of the Altieri palace. Haskell says its ceiling was ready for decoration by 1673; this does not mean that the palace or its decorative programme was complete.",
        "sources": [source(SRC6, "第6章，印刷页161，来源行5。", "line 5; print p. 161", "哈斯克尔称主厅天顶到1673年准备装饰。", ["by 1673 the ceiling of the principal hall was ready for decoration"])],
        "fields": [("空间性质", "宫殿主厅；与宫殿整体及主厅天顶壁画分别登记", "S1；第6章 p.161，L5"), ("装饰准备状态", "主厅天顶于1673年准备装饰；不等于装饰完成", "S1；第6章 p.161，L5")],
        "section": "基本信息", "statements": ["st-chp6-p161-v1-09", "st-chp6-p161-principal-hall-part-of-palace"],
    },
    {
        "cid": "cand-6464", "group": "workgrp-429898c8edfe6c", "ku": "units/works/bernini-angels-symbols-passion-ponte-sant-angelo",
        "path": "04-knowledge/units/works/bernini-angels-symbols-passion-ponte-sant-angelo.md", "type": "work",
        "zh": "贝尔尼尼《持受难象征的天使群》", "en": "Bernini’s Angels Carrying the Symbols of the Passion",
        "identity": "对应第6章 p.161 所述的一组雕塑；与 Cortona 的《持受难器具的天使》壁画候选 cand-5108 分开。Haskell 记为委托及拟安置，不证明已经安装或存世。",
        "zhdesc": "记录哈斯克尔所述由克雷芒九世委托贝尔尼尼制作、原拟安置于 Ponte S. Angelo 的受难象征天使群。原书没有在此确认安装、完成状态、现存版本或单件数量。中文题名为描述性译名。",
        "endesc": "This unit records the group of angels carrying the Symbols of the Passion that Haskell says Clement IX commissioned from Bernini for intended placement on Ponte S. Angelo. The passage does not confirm installation, completion, surviving versions, or the number of individual figures. The Chinese title is descriptive.",
        "sources": [source(SRC6, "第6章，印刷页161，来源行4–5。", "lines 4–5; print p. 161", "哈斯克尔称克雷芒九世委托贝尔尼尼创作天使群，原拟置于 Ponte S. Angelo。", ["figures of the Angels carrying the Symbols of the Passion from Bernini to be placed on the Ponte S. Angelo"])],
        "fields": [("作品类型", "雕塑群（原文为 figures；不推断具体数量）", "S1；第6章 p.161，L4–5"), ("书内委托者", "克雷芒九世；依哈斯克尔叙述", "S1；第6章 p.161，L3–5"), ("原定安置地点", "Ponte S. Angelo；原文为“to be placed”，不表示已经安装", "S1；第6章 p.161，L4–5")],
        "section": "基本信息", "statements": ["st-chp6-p161-v1-04", "st-chp6-p161-v1-04-intended-placement"],
    },
    {
        "cid": "cand-6465", "group": "sg3-place-cand-6465", "ku": "units/places/ponte-sant-angelo",
        "path": "04-knowledge/units/places/ponte-sant-angelo.md", "type": "place",
        "zh": "圣天使桥", "en": "Ponte S. Angelo",
        "identity": "书中以 Ponte S. Angelo 指称的桥；本卡不补充现代桥梁身份史或现存构件信息。",
        "zhdesc": "记录哈斯克尔提及的 Ponte S. Angelo。第6章 p.161 将其作为贝尔尼尼受难象征天使群的拟安置地点；本卡不据此主张作品曾经安装。",
        "endesc": "This unit records the Ponte S. Angelo named by Haskell on p.161 of Chapter 6 as the intended placement for Bernini’s Passion-symbol angels. The citation does not establish that the works were installed there.",
        "sources": [source(SRC6, "第6章，印刷页161，来源行5。", "line 5; print p. 161", "哈斯克尔称天使群原拟安置于 Ponte S. Angelo。", ["to be placed on the Ponte S. Angelo"])],
        "fields": [("地点性质", "桥梁（由名称与原文语境识别）", "S1；第6章 p.161，L5"), ("书内关联", "被称为贝尔尼尼天使群的原定安置地点；不表示已安装", "S1；第6章 p.161，L4–5")],
        "section": "基本信息", "statements": ["st-chp6-p161-v1-04-intended-placement"],
    },
    {
        "cid": "cand-6467", "group": "workgrp-e9e8a3bdf4d15e", "ku": "units/works/altieri-palace-planned-decoration-programme",
        "path": "04-knowledge/units/works/altieri-palace-planned-decoration-programme.md", "type": "work",
        "zh": "阿尔蒂耶里宫装饰计划", "en": "Planned Decorative Programme for the Altieri Palace",
        "identity": "保持为整座宫殿的计划性装饰作品组；与主厅具体天顶壁画 cand-6466 及宫殿建造活动 cand-6483 区分。",
        "zhdesc": "记录哈斯克尔所述由 Carlo Maratta 及其学生为 Altieri 宫殿规划、但从未完成的装饰计划。原书将未完成归因于与 Don Gasparo Altieri 之间未具体说明的分歧；此卡不把含混的“the work dragged on”年限归给该计划。",
        "endesc": "This unit records the decorative programme that Haskell says Carlo Maratta and his pupils planned for the Altieri palace but never completed. Haskell attributes its non-completion to unspecified differences with Don Gasparo Altieri. The ambiguous statement that “the work dragged on” is not assigned a duration for this programme.",
        "sources": [source(SRC6, "第6章，印刷页161，来源行5、10–11。", "lines 5, 10–11; print p. 161", "哈斯克尔提到主厅准备装饰，并另称 Maratta 与学生计划的宫殿装饰最终未完成。", ["the ceiling of the principal hall was ready for decoration", "the decoration planned for the palace by Carlo Maratta and his pupils was never completed"])],
        "fields": [("作品类型", "计划性宫殿装饰项目；不等于某一具体壁画", "S1；第6章 p.161，L10"), ("计划者", "Carlo Maratta 及其学生（依 Haskell 归述；学生未具名）", "S1；第6章 p.161，L10"), ("计划对象", "Altieri 宫殿；具体覆盖空间未逐一说明", "S1；第6章 p.161，L10"), ("完成状态", "原书称计划从未完成；所述分歧未具体说明", "S1；第6章 p.161，L10")],
        "section": "基本信息", "statements": ["st-chp6-p161-v1-09", "st-chp6-p161-v1-19", "st-chp6-p161-v1-19-intended-for-palace"],
    },
    {
        "cid": "cand-6468", "group": "sg3-term-cand-6468", "ku": "units/terms/clemency-personification-altieri-fresco",
        "path": "04-knowledge/units/terms/clemency-personification-altieri-fresco.md", "type": "term",
        "zh": "阿尔蒂耶里宫壁画中的仁慈寓意", "en": "Clemency Personification in the Altieri Palace Fresco",
        "identity": "仅记录该壁画中的具体寓意形象，不将此用例扩展成一般概念史或独立人物实体。",
        "zhdesc": "记录哈斯克尔所述阿尔蒂耶里宫壁画中的女性仁慈寓意形象。作者称其为壁画高潮，并说明其与教皇名号有关的双关及金色光照；这些均按作者的图像解读保留。",
        "endesc": "This unit records the female personification of Clemency in the Altieri palace fresco. Haskell calls it the fresco’s climax and notes a pun on the pope’s name and its golden light. These details remain the author’s iconographic reading.",
        "sources": [source(SRC6, "第6章，印刷页161，来源行7。", "line 7; print p. 161", "哈斯克尔描述壁画高潮为女性仁慈形象，并提及教皇名号双关和金色光照。", ["the climax of the fresco is a female figure, Clemency", "bathed in golden light"])],
        "fields": [("书内用例", "壁画高潮中的女性仁慈寓意形象", "S1；第6章 p.161，L7"), ("图像解读", "Haskell 将形象称为与教皇名号相关的双关；不外推为一般词义", "S1；第6章 p.161，L7"), ("视觉描述", "沐浴于金色光照；依作者描述", "S1；第6章 p.161，L7")],
        "section": "书内用法", "statements": ["st-chp6-p161-v1-12"],
    },
    {
        "cid": "cand-6469", "group": "sg3-term-cand-6469", "ku": "units/terms/public-happiness-personification-altieri-fresco",
        "path": "04-knowledge/units/terms/public-happiness-personification-altieri-fresco.md", "type": "term",
        "zh": "阿尔蒂耶里宫壁画中的公众幸福寓意", "en": "Public Happiness Personification in the Altieri Palace Fresco",
        "identity": "保留为壁画中的寓意形象；“三项主要美德”中的其他形象未具名，未作展开。",
        "zhdesc": "记录哈斯克尔称为 Public Happiness 的壁画寓意形象。作者称其持有一面象征 Don Gasparo Altieri 的旗帜；此处仅保留来源中的象征解释。",
        "endesc": "This unit records the allegorical figure that Haskell calls Public Happiness. He says it holds a standard symbolizing Don Gasparo Altieri; the symbolism is retained as the source’s interpretation.",
        "sources": [source(SRC6, "第6章，印刷页161，来源行8–9。", "lines 8–9; print p. 161", "哈斯克尔称 Public Happiness 是壁画中与三项主要美德并列的形象，并持有象征 Don Gasparo 的旗帜。", ["one of the figures standing with the three cardinal virtues is Public Happiness holding a standard to symbolise Don Gasparo Altieri"])],
        "fields": [("书内用例", "Altieri 宫壁画中的寓意形象；与三项主要美德并列", "S1；第6章 p.161，L8–9"), ("图像属性", "手持一面旗帜；原书未给出旗帜的独立对象身份", "S1；第6章 p.161，L8–9"), ("象征指涉", "Haskell 称旗帜象征 Don Gasparo Altieri；不作外部图像学核验", "S1；第6章 p.161，L8–9")],
        "section": "书内用法", "statements": ["st-chp6-p161-v1-14", "st-chp6-p161-v1-14-symbolizes-gasparo"],
    },
    {
        "cid": "cand-6475", "group": "sg3-term-cand-6475", "ku": "units/terms/official-artistic-patronage-after-alexander-vii",
        "path": "04-knowledge/units/terms/official-artistic-patronage-after-alexander-vii.md", "type": "term",
        "zh": "亚历山大七世去世后的官方艺术赞助", "en": "Official Artistic Patronage after Alexander VII",
        "identity": "限定于 Haskell 对 Alexander VII 去世后艺术赞助变化的历史表述；与既有“罗马艺术赞助衰退”卡的跨时期概述不合并。",
        "zhdesc": "记录哈斯克尔关于亚历山大七世去世后官方艺术赞助急剧下降的特定历史表述。下降与去世的先后关系按原文保留，不据此建立因果边或独立分期。",
        "endesc": "This unit records Haskell’s specific statement that official artistic patronage declined sharply after Alexander VII’s death. The source’s chronology is retained without turning it into a causal edge or an independently established periodization.",
        "sources": [source(SRC6, "第6章，印刷页161，来源行3。", "line 3; print p. 161", "哈斯克尔称亚历山大七世去世后官方艺术赞助 precipitously declined。", ["After the death of Pope Alexander VII official patronage of the arts declined precipitously"])],
        "fields": [("书内用法", "Haskell 称 Alexander VII 去世后官方艺术赞助急剧下降；仅作原书归述", "S1；第6章 p.161，L3")],
        "section": "书内用法", "statements": ["st-chp6-p161-v1-01"],
    },
    {
        "cid": "cand-6443", "group": "sg3-term-cand-6443", "ku": "units/terms/high-baroque-haskell-cortona-gaulli-comparison",
        "path": "04-knowledge/units/terms/high-baroque-haskell-cortona-gaulli-comparison.md", "type": "term",
        "zh": "哈斯克尔科尔托纳与高利比较中的盛期巴洛克", "en": "High Baroque in Haskell’s Cortona–Gaulli Comparison",
        "identity": "限于 Haskell 在第6章 p.160 的比较性用语；与其在 p.161 对 Altieri 壁画使用一般 Baroque 的表述相关，但不预设为同一概念或外部时期边界。",
        "zhdesc": "记录哈斯克尔比较 Pietro da Cortona 与 Gaulli 时使用的“high Baroque”表达。该词在此是作者的比较性艺术史语言，不提供精确定年边界；第6章 p.161 对壁画正式语言的“Baroque”评价另保留其本地语境。",
        "endesc": "This unit records Haskell’s comparative use of “high Baroque” when discussing Pietro da Cortona and Gaulli. The phrase is the author’s comparative art-historical language and supplies no precise date boundary. His p.161 use of “Baroque” for the fresco’s formal language remains in its own passage context.",
        "sources": [source(SRC6IV, "第6章，印刷页160，来源行43。", "line 43; print p. 160", "哈斯克尔以 high Baroque 比较 Pietro da Cortona 与 Gaulli。", ["when compared to the high Baroque of Pietro da Cortona or Gaulli"]), source(SRC6, "第6章，印刷页161，来源行9。", "line 9; print p. 161", "哈斯克尔称壁画的形式语言属于 Baroque；此处一般风格用语与 p.160 比较性 high Baroque 保持语境区分。", ["The formal language is that of the Baroque"])],
        "fields": [("书内用法", "第6章 p.160 的比较性艺术史标签；未定义时期边界", "S1；第6章 p.160，L43"), ("比较对象", "Pietro da Cortona 与 Gaulli；不把比较等同于二者身份或作品关系", "S1；第6章 p.160，L43")],
        "section": "书内用法", "statements": ["st-chp6-p160-016", "st-chp6-p161-v1-17"],
    },
    {
        "cid": "cand-1734", "group": "sg3-term-cand-1734", "ku": "units/terms/nepotism-in-rome-haskell-context",
        "path": "04-knowledge/units/terms/nepotism-in-rome-haskell-context.md", "type": "term",
        "zh": "哈斯克尔所述罗马教皇亲族任用", "en": "Papal Nepotism in Rome in Haskell’s Account",
        "identity": "沿用既有跨章 S3 新术语组；与既有一般 Nepotism 概念卡分开，保持罗马教皇职位、亲族与赞助语境，不推定单一通用定义。",
        "zhdesc": "记录 Haskell 在第1、2、6章讨论的罗马教皇亲族任用语境：教皇亲属及依附者的职位、收入和赞助机会与政治更替相关；第6章又提及克雷芒十世试图减少过度的 nepotism。不同章节为作者的历史叙述，不合并成一条具体任命关系。",
        "endesc": "This unit records Haskell’s Roman papal context for nepotism across Chapters 1, 2, and 6: offices, income, and patronage opportunities for papal relatives and clients are connected to political succession, and Chapter 6 notes Clement X’s attempt to reduce excessive nepotism. These passages remain the author’s historical account and are not merged into a specific appointment relation.",
        "sources": [
            source(SRC1, "第1章，印刷页4，来源行17–19。", "lines 17–19; print p. 4", "Haskell 将教皇更替、亲属职位与 patronage patterns 联系起来，并使用 nepotism 一词。", ["patterns of art patronage", "for nepotism no longer took the form of private empires"]),
            source(SRC2, "第2章，印刷页约53，来源行6–7。", "lines 6–7; print p. 53", "Haskell 将 nepotism 说成教皇制度的一个公认特征。", ["Nepotism was a recognised feature of the papal system"]),
            source(SRC2VIII, "第2章，印刷页62，来源行14。", "line 14; print p. 62", "Haskell 将 Urban VIII 的 nepotism 与 Barberini 家族的差异化艺术支持并述。", ["thanks to Urban’s nepotism"]),
            source(SRC6, "第6章，印刷页161，来源行11。", "line 11; print p. 161", "Haskell 称 Clement X 试图减少过度的 nepotism。", ["attempt to reduce excessive nepotism"]),
        ],
        "fields": [("书内用法", "Haskell 将其用于罗马教皇制度中的亲族任用语境", "S1；第1章 p.4、 第2章 p.53、p.62"), ("涉及范围", "亲属职位、收入、赞助机会与教皇更替；各项事实不互相替代", "S1；第1章 p.4，L17–19；第2章 p.53，L6–7"), ("后续表述", "第6章称 Clement X 试图减少过度 nepotism；该评价仍归于 Haskell", "S1；第6章 p.161，L11")],
        "section": "书内用法", "statements": ["st-chp6-p161-v1-21"],
    },
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def write_csv_bytes(path, fields, rows):
    import io
    out = io.StringIO(newline="")
    w = csv.DictWriter(out, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    raw = path.read_bytes()
    return (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + out.getvalue().encode("utf-8")


def card_text(item):
    sources = []
    for s in item["sources"]:
        sources.append({"citation": BOOK, "location": s["location"], "sentence_summary": s["summary"],
            "original_quotes": [{"source_span": s["span"], "text": q} for q in s["quotes"]],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": s["file"], "source_span": s["span"]}})
    fm = yaml.safe_dump({"title": f"{item['zh']}（{item['en']}）", "name_en": item["en"], "type": item["type"],
        "evidence_status": "source_backed", "sources": sources, "created": DATE, "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"}, allow_unicode=True, sort_keys=False, width=1000)
    rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in item["fields"])
    evidence_table = f"| 字段 | 值 | 证据 |\n|---|---|---|\n{rows}"
    links = "；".join(f"[来源{i}](../../../{s['file']})" for i, s in enumerate(item["sources"], 1))
    ids = "、".join(f"`{sid}`" for sid in item["statements"])
    body = f"""## 内容

### 描述

**中文：** {item['zhdesc']}

**English:** {item['endesc']}

### 名称与身份边界

- S3 候选 `{item['cid']}` 保持身份组 `{item['group']}`，登记为 `{item['ku']}`。
- {item['identity']}
- 来源入口：{links}。

### {item['section']}

{evidence_table}

## 关系与证据

### 关系记录

正式关系由 `relations.csv` 定向渲染；未登记为正式边的裁决与理由见[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。

### 关系候选入口

{ids}
"""
    return f"---\n{fm}---\n\n{body}"


def add_statement(statements, spec):
    assert not any(x["statement_id"] == spec["statement_id"] for x in statements)
    statements.append(spec)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true"); g.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    paths = {"candidates": TABLES/"entity-candidates.csv", "alignment": TABLES/"alignment.csv", "manifest": TABLES/"ku-manifest.csv",
        "relations": TABLES/"relations.csv", "statements": TABLES/"book-statements.jsonl", "enrichment": TABLES/"enrichment.jsonl",
        "accepted": ROOT/"04-knowledge/accepted.yml", "process": PROC/"knowledge.md", "result": ROOT/"04-knowledge/results/patrons-and-painters-full-book-s2.md"}
    _, candidates = read_csv(paths["candidates"]); af, align = read_csv(paths["alignment"]); mf, manifest = read_csv(paths["manifest"]); rf, relations = read_csv(paths["relations"])
    candidate_by_id = {r["candidate_id"]:r for r in candidates}
    primary = {r["candidate_id"]:r for r in align if r.get("candidate_id") and not r.get("external_source")}
    accepted = paths["accepted"].read_text(encoding="utf-8-sig")
    process = paths["process"].read_text(encoding="utf-8-sig")
    result = paths["result"].read_text(encoding="utf-8-sig")
    statements = [json.loads(x) for x in paths["statements"].read_text(encoding="utf-8-sig").splitlines() if x.strip()]
    bysid = {s["statement_id"]:s for s in statements}
    assert ANCHOR not in process and ANCHOR not in result
    ferney_rationale = "判为 `new` 的 place 组，空间范围限于原文命名"
    assert process.count(ferney_rationale) == 1
    process = process.replace(ferney_rationale, "判为 `new` 的 place 组 `sg3-place-cand-10581`，空间范围限于原文命名", 1)
    assert len({x["cid"] for x in ITEMS}) == len(ITEMS)
    for item in ITEMS:
        c, a = candidate_by_id[item["cid"]], primary[item["cid"]]
        assert c["suggested_type"] == item["type"] and a["decision"] == "new" and not a.get("ku_id"), item["cid"]
        assert f"group={item['group']}" in a["resolution_note"], item["cid"]
        members = [r["candidate_id"] for r in align if r.get("candidate_id") and not r.get("external_source") and r["decision"] == "new" and f"group={item['group']}" in r.get("resolution_note", "")]
        assert members == [item["cid"]], (item["cid"], members)
        assert not (ROOT/item["path"]).exists() and item["path"] not in accepted
        assert not any(r["ku_id"] == item["ku"] or r["card_path"] == item["path"] for r in manifest)
        assert not any(r["name_en"].casefold() == item["en"].casefold() and r["type"] == item["type"] for r in manifest)
        for s in item["sources"]:
            text = (ROOT/s["file"]).read_text(encoding="utf-8-sig")
            norm = " ".join(text.split())
            for q in s["quotes"]: assert " ".join(q.split()) in norm, (item["cid"], q)

    # Repair statement granularity and direction before S6. S0 transcriptions remain unchanged.
    mutations = {
      "st-chp6-p161-note2-avviso": {"subject_candidate_id":"cand-2962", "predicate":"cites"},
      "st-chp6-p161-note3-bellori": {"subject_candidate_id":"cand-2962", "predicate":"cites"},
      "st-chp6-p161-note3-clark": {"subject_candidate_id":"cand-2962", "predicate":"cites"},
      "st-chp6-p161-note4-pascoli": {"subject_candidate_id":"cand-2962", "predicate":"cites"},
      "st-chp6-p161-v1-04": {"subject_candidate_id":"cand-6464", "object_candidate_id":"cand-2263", "predicate":"commissioned_by"},
      "st-chp6-p161-v1-10": {"subject_candidate_id":"cand-1564", "object_candidate_id":"cand-1526", "predicate":"advised", "qualifier_claim":"Haskell says Carlo Maratta was selected on Camillo Massimi’s advice."},
      "st-chp6-p161-v1-14": {"subject_candidate_id":"cand-6466", "object_candidate_id":"cand-6469", "predicate":"has_subject", "qualifier_claim":"Haskell identifies Public Happiness as a figure in the Altieri fresco, holding a standard said to symbolize Don Gasparo Altieri."},
      "st-chp6-p161-v1-15": {"predicate":"kin_of", "qualifier_claim":"Haskell identifies Don Gasparo as Clement X’s adopted nephew."},
      "st-chp6-p161-v1-19": {"predicate":"planned_palace_decoration_unfinished", "qualifier_claim":"Haskell says the planned palace decoration was never completed owing to unspecified differences with Don Gasparo Altieri."},
    }
    for sid, change in mutations.items():
        s = bysid[sid]
        for k,v in change.items():
            if k == "qualifier_claim": s.setdefault("qualifiers", {})["claim"] = v
            else: s[k] = v
    bysid["st-chp6-p161-v1-10"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-1564", "cand-1526"]
    bysid["st-chp6-p161-v1-14"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-6466", "cand-6469", "cand-0089"]
    bysid["st-chp6-p161-v1-15"]["qualifiers"]["claim"] = "Haskell identifies Don Gasparo as Clement X’s adopted nephew."
    bysid["st-chp6-p161-v1-15"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-0089", "cand-0087"]
    bysid["st-chp6-p161-v1-15"]["original_quote"] = "Altieri, the Pope’s adopted nephew"
    bysid["st-chp6-p161-v1-19"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-6467", "cand-1526", "cand-6481", "cand-0089"]
    bysid["st-chp6-p161-v1-02"]["qualifiers"]["ocr_corrections"] = [{"ocr":"Clement IXin", "printed_reading":"Clement IX in", "evidence":"CHP-6.pdf physical p.16 (printed p.161) scan; the source transcription is retained."}]
    bysid["st-chp6-p161-v1-22"]["qualifiers"]["ocr_corrections"] = [{"ocr":"osa Barberini", "printed_reading":"a Barberini", "evidence":"CHP-6.pdf physical p.16 (printed p.161) scan; continuation ‘or a Chigi’ is on printed p.162."}]
    # Keep temporal succession, visual description, and office as claims, but do not turn them into unsupported edges.
    bysid["st-chp6-p161-v1-01"]["qualifiers"]["relation_candidate_note"] = "Chronological sequence only; it does not assert that Alexander VII’s death caused the decline. Rejected as a formal entity-relation edge."
    bysid["st-chp6-p161-v1-13"]["qualifiers"]["relation_candidate_note"] = "Physical description of the fresco; the frame is not separately identified as an endpoint. Rejected as a formal graph edge."
    bysid["st-chp6-p161-v1-06"]["qualifiers"]["relation_candidate_note"] = "Reports a family concern and anticipated completion, not a discrete relation between the family and the palace. Rejected as a formal graph edge."
    bysid["st-chp6-p161-note3-bellori"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-2962", "cand-6338", "cand-6466"]
    bysid["st-chp6-p161-note3-clark"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-2962", "cand-6479", "cand-6480"]
    bysid["st-chp6-p161-note4-pascoli"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-2962", "cand-4834", "cand-6467"]

    add_statement(statements, {"statement_id":"st-chp6-p161-v1-04-intended-placement", "segment_id":"chp-6:06_CHP-6_sec_v:l3-12", "subject_candidate_id":"cand-6464", "object_candidate_id":"cand-6465", "predicate":"intended_for", "qualifiers":{"speaker":"Haskell", "printed_page":"161", "source_line_start":4, "source_line_end":5, "claim":"Haskell says Bernini’s Angels carrying the Symbols of the Passion were to be placed on Ponte S. Angelo.", "text_layer":"authorial historical account", "qualification":"This records intended placement only; the passage does not establish installation.", "mentioned_candidate_ids":["cand-6464", "cand-6465"], "relation_candidate":True, "relation_candidate_note":"Records the intended placement of the commissioned sculpture group, not completed installation."}, "original_quote":"figures of the Angels carrying the Symbols of the Passion from Bernini to be placed on the Ponte S. Angelo", "origin":"book", "source_file":SRC6})
    add_statement(statements, {"statement_id":"st-chp6-p161-v1-10-maratta-consults-bellori", "segment_id":"chp-6:06_CHP-6_sec_v:l3-12", "subject_candidate_id":"cand-1526", "object_candidate_id":"cand-0272", "predicate":"consulted", "qualifiers":{"speaker":"Haskell", "printed_page":"161", "source_line_start":5, "source_line_end":6, "claim":"Haskell says Carlo Maratta consulted Bellori about the iconography.", "text_layer":"authorial historical account", "qualification":"Consultation does not establish co-authorship.", "mentioned_candidate_ids":["cand-1526", "cand-0272"], "relation_candidate":True, "relation_candidate_note":"The source reports consultation, but the controlled relation list has no predicate that precisely encodes this act."}, "original_quote":"On the advice of Camillo Massimi, the artist chosen was Carlo Maratta and he in turn consulted Bellori as regards the iconography.", "origin":"book", "source_file":SRC6})
    add_statement(statements, {"statement_id":"st-chp6-p161-v1-14-symbolizes-gasparo", "segment_id":"chp-6:06_CHP-6_sec_v:l3-12", "subject_candidate_id":"cand-6469", "object_candidate_id":"cand-0089", "predicate":"symbolizes", "qualifiers":{"speaker":"Haskell", "printed_page":"161", "source_line_start":8, "source_line_end":9, "claim":"Haskell says the standard held by Public Happiness symbolizes Don Gasparo Altieri.", "text_layer":"authorial historical account", "qualification":"Symbolism is Haskell’s interpretation; no separate standard entity is created.", "mentioned_candidate_ids":["cand-6469", "cand-0089"], "relation_candidate":True, "relation_candidate_note":"The source supports the symbolic reference, but no controlled predicate precisely expresses this relation."}, "original_quote":"Public Happiness holding a standard to symbolise Don Gasparo Altieri", "origin":"book", "source_file":SRC6})
    add_statement(statements, {"statement_id":"st-chp6-p161-v1-15-office", "segment_id":"chp-6:06_CHP-6_sec_v:l3-12", "subject_candidate_id":"cand-0089", "object_candidate_id":None, "predicate":"office_held", "qualifiers":{"speaker":"Haskell", "printed_page":"161", "source_line_start":9, "source_line_end":9, "claim":"Haskell identifies Don Gasparo as Gonfaloniere of the Church.", "text_layer":"authorial historical account", "qualification":"Retained as a person attribute; the office is not a separately identified graph entity.", "mentioned_candidate_ids":["cand-0089"], "relation_candidate":False, "relation_candidate_note":"Office title is an attribute in this passage, not a relation to Clement X."}, "original_quote":"Gonfaloniere of the Church", "origin":"book", "source_file":SRC6})
    add_statement(statements, {"statement_id":"st-chp6-p161-v1-19-intended-for-palace", "segment_id":"chp-6:06_CHP-6_sec_v:l3-12", "subject_candidate_id":"cand-6467", "object_candidate_id":"cand-0090", "predicate":"intended_for", "qualifiers":{"speaker":"Haskell", "printed_page":"161", "source_line_start":10, "source_line_end":10, "claim":"Haskell says Maratta and his pupils planned the decoration for the Altieri palace.", "text_layer":"authorial historical account", "qualification":"This is the programme’s intended scope; the programme was not completed.", "mentioned_candidate_ids":["cand-6467", "cand-0090", "cand-1526", "cand-6481"], "relation_candidate":True, "relation_candidate_note":"The source explicitly identifies the palace as the object of the planned decorative programme."}, "original_quote":"the decoration planned for the palace by Carlo Maratta and his pupils", "origin":"book", "source_file":SRC6})
    bysid = {s["statement_id"]:s for s in statements}

    # New source-backed cards and targeted S5 preview.
    cards = {ROOT/i["path"]:card_text(i) for i in ITEMS}
    planned_align = [dict(r) for r in align]
    planned_primary = {r["candidate_id"]:r for r in planned_align if r.get("candidate_id") and not r.get("external_source")}
    planned_manifest = list(manifest)
    for item in ITEMS:
        a = planned_primary[item["cid"]]
        a["ku_id"] = item["ku"]
        a["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        a["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku']}; source-local identity only."
        planned_manifest.append({"ku_id":item["ku"], "type":item["type"], "canonical_name":item["zh"], "name_en":item["en"], "source_task":TASK, "card_path":item["path"]})
    # Preserve the existing Ferney S3 ruling while adding its missing singleton group marker.
    ferney = planned_primary["cand-10581"]
    assert ferney["decision"] == "new" and ferney["ku_id"] == "units/places/ferney"
    if not re.search(r"(?<![A-Za-z0-9_-])group=", ferney["resolution_note"], re.IGNORECASE):
        ferney["resolution_note"] += " group=sg3-place-cand-10581."
    import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
    stats = sync.summarize_by_type(candidates, planned_align)
    totals = {key:sum(v[key] for v in stats.values()) for key in next(iter(stats.values()))}
    result = sync.update_result(result, stats, totals, len(planned_manifest))

    accepted_lines = accepted.splitlines()
    for item in sorted(ITEMS, key=lambda x:x["path"]):
        insert_at = next((i for i,line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > item["path"]), next((i for i,line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)))
        accepted_lines.insert(insert_at, f"- {item['path']}")
    planned_accepted = "\n".join(accepted_lines)+"\n"

    # The formal relation batch follows the current relation ID sequence.
    next_rel = max(int(r["relation_id"].split("-")[1]) for r in relations)+1
    rel_specs = [
      ("units/archives/patrons-and-painters","units/archives/avviso-1672-04-09-roma-vol-xviii-p57","cites","cited avviso","Haskell p.161 note 2 cites the 9 April 1672 avviso as a locator; the notice itself was not independently inspected.","st-chp6-p161-note2-avviso"),
      ("units/archives/patrons-and-painters","units/archives/lione-pascoli-vite-dei-pittori-vol-i","cites","cited source","Haskell p.161 note 4 cites Pascoli, volume I, p.140; the cited page was not independently read.","st-chp6-p161-note4-pascoli"),
      ("units/events/giulio-rospigliosi-accession-clement-ix-1667","units/persons/cardinal-rospigliosi-gimignani","has_participant","pope at accession","Haskell reports Giulio Rospigliosi became Clement IX in 1667 and reigned for two years; no exact accession date beyond the year is added.","st-chp6-p161-v1-02"),
      ("units/works/bernini-angels-symbols-passion-ponte-sant-angelo","units/persons/cardinal-rospigliosi-gimignani","commissioned_by","commissioner","Haskell reports Clement IX commissioned Bernini’s sculpture group; commission does not imply completion.","st-chp6-p161-v1-04"),
      ("units/works/bernini-angels-symbols-passion-ponte-sant-angelo","units/places/ponte-sant-angelo","intended_for","intended placement","The source says the figures were to be placed on Ponte S. Angelo; installation is not established.","st-chp6-p161-v1-04-intended-placement"),
      ("units/persons/camillo-massimi","units/persons/carlo-maratta","advised","advice in artist selection","Haskell says Maratta was selected on Massimi’s advice; this edge does not imply a commission or co-authorship.","st-chp6-p161-v1-10"),
      ("units/works/altieri-clemency-fresco","units/terms/clemency-personification-altieri-fresco","has_subject","depicted allegorical figure","Haskell identifies Clemency as the fresco’s female climax; the pun and lighting remain source interpretation.","st-chp6-p161-v1-12"),
      ("units/works/altieri-clemency-fresco","units/terms/public-happiness-personification-altieri-fresco","has_subject","depicted allegorical figure","Haskell identifies Public Happiness as a figure in the fresco; the separate symbolic reference remains pending.","st-chp6-p161-v1-14"),
      ("units/persons/don-gasparo-altieri","units/persons/emilio-altieri-pope-clement-x","kin_of","adopted nephew","Haskell calls Don Gasparo Clement X’s adopted nephew; the separate Gonfaloniere title is retained as a person attribute.","st-chp6-p161-v1-15"),
      ("units/works/altieri-palace-planned-decoration-programme","units/places/altieri-palace","intended_for","planned palace decoration","Haskell explicitly describes the programme as planned for the palace; its non-completion is separately recorded.","st-chp6-p161-v1-19-intended-for-palace"),
    ]
    new_rel = []
    for i,(sub,obj,predicate,role,scope,sid) in enumerate(rel_specs):
        new_rel.append({"relation_id":f"rel-{next_rel+i:04d}","subject_ku_id":sub,"object_ku_id":obj,"predicate":predicate,"time":"1667" if sid=="st-chp6-p161-v1-02" else "","role":role,"scope":scope,"origin":"book","status":"formal","source_id":"haskell-1980-rev-ed","source_span":f"Chapter 6, printed p.161; S2 statement: {sid}","source_file":SRC6,"note":"Formal S6 decision in the p.161 Altieri endpoint batch; only the source-supported relation and stated role are encoded."})
    planned_rel = relations+new_rel
    keys=set()
    for r in planned_rel:
        key=(r["subject_ku_id"],r["predicate"],r["object_ku_id"],r["time"],r["role"],r["scope"])
        assert key not in keys,key
        keys.add(key)

    # Preview field-fact extraction against the generated cards without writing them.
    from scripts import build_field_facts as facts
    old_base=facts.BASE
    try:
        import tempfile
        with tempfile.TemporaryDirectory(prefix="pnp-p161-fields-") as td:
            facts.BASE=Path(td)
            for path,content in cards.items():
                dest=Path(td)/path.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(content,encoding="utf-8-sig")
            selected=[r for r in planned_manifest if r["ku_id"] in {i["ku"] for i in ITEMS}]
            fields,_,warnings,ncards=facts.extract_records(selected)
    finally:
        facts.BASE=old_base
    assert not warnings,warnings
    assert ncards==len(ITEMS) and fields and all(r["evidence_status"]=="source_backed" and r["source_ids"]==["haskell-1980-rev-ed"] for r in fields)
    facts.assign_ids(fields,paths["enrichment"])
    enr_raw=paths["enrichment"].read_bytes()
    enr_append=(b"" if enr_raw.endswith(b"\n") else b"\n")+b"".join(json.dumps(r,ensure_ascii=False,separators=(",",":")).encode("utf-8")+b"\n" for r in fields)

    # Record every pending or rejected relation candidate without creating proxy edges.
    decisions = [
      ("st-chp6-p161-note2-avviso","formal","rel-{0:04d} cites：只记录 Haskell 对 avviso 的书目引注，不表示原件已查阅。".format(next_rel)),
      ("st-chp6-p161-note3-bellori","pending","Bellori 1942 的题名／版本未由当前脚注定位确定，cand-6338 仍 undecided。"),
      ("st-chp6-p161-note3-clark","pending","A. Clark 1961 条目缺题名，且 Berrettoni 作品未识别；cand-6479、cand-6480 仍 undecided。"),
      ("st-chp6-p161-note4-pascoli","formal","rel-{0:04d} cites：只记录 Haskell 对 Pascoli I, p.140 的引注，不表示已读该页。".format(next_rel+1)),
      ("st-chp6-p161-v1-01","rejected","原句只给出死亡之后赞助下降的时间顺序，不主张因果或其他实体关系。"),
      ("st-chp6-p161-v1-02","formal","rel-{0:04d} has_participant：1667年克雷芒九世即位事件→本人；两年任期按原文保留在 S2。".format(next_rel+2)),
      ("st-chp6-p161-v1-03","pending","肖像题名与对象身份不明；cand-6463 保持 undecided。"),
      ("st-chp6-p161-v1-04","formal","rel-{0:04d} commissioned_by：天使群作品→克雷芒九世；不表示完成。".format(next_rel+3)),
      ("st-chp6-p161-v1-04-intended-placement","formal","rel-{0:04d} intended_for：仅表示原定安置于 Ponte S. Angelo。".format(next_rel+4)),
      ("st-chp6-p161-v1-06","rejected","家族的忧虑与预期不是当前图谱中的明确对象关系边。"),
      ("st-chp6-p161-v1-07","pending","施工活动身份 cand-6483 未定；Gesù 邻接与 Jesuit indignation 不能合并成一条受控关系。"),
      ("st-chp6-p161-v1-09","pending","准备装饰的状态不等同于可确认的 intended_for 或 part_of 关系；主厅与计划保持分别登记。"),
      ("st-chp6-p161-v1-10","formal","rel-{0:04d} advised：Massimi→Maratta；仅编码建议参与选人。".format(next_rel+5)),
      ("st-chp6-p161-v1-10-maratta-consults-bellori","pending","consulted 在受控关系类型中没有精确谓词；不以 advised_by 替代咨询。"),
      ("st-chp6-p161-v1-11","pending","Cortona ceiling 的具体作品身份 cand-6472 未决；不据泛称补建作品边。"),
      ("st-chp6-p161-v1-12","formal","rel-{0:04d} has_subject：壁画→仁慈寓意；双关和光照保留为来源解释。".format(next_rel+6)),
      ("st-chp6-p161-v1-13","rejected","这是壁画形制描述；灰泥框未单独识别为有边界的实体。"),
      ("st-chp6-p161-v1-14","formal","rel-{0:04d} has_subject：壁画→公众幸福寓意。".format(next_rel+7)),
      ("st-chp6-p161-v1-14-symbolizes-gasparo","pending","symbolizes 没有精确受控谓词；不把寓意错写成作品的直接人物题材或所有权。"),
      ("st-chp6-p161-v1-15","formal","rel-{0:04d} kin_of：只记录 Don Gasparo 为 Clement X 的 adopted nephew。".format(next_rel+8)),
      ("st-chp6-p161-v1-17","pending","high Baroque／Baroque 为来源风格评价；当前受控表无可准确编码作品风格的谓词。"),
      ("st-chp6-p161-v1-19","pending","未完成与 Don Gasparo 间的未具体说明分歧不等于 commissioned_by、disputed_with 或因果边。"),
      ("st-chp6-p161-v1-19-intended-for-palace","formal","rel-{0:04d} intended_for：计划性装饰项目→Altieri 宫；未完成状态另行保留。".format(next_rel+9)),
      ("st-chp6-p161-v1-21","pending","reduce nepotism 是作者所述行动，不是现有谓词可准确表达的关系；保留 source-local 概念。"),
      ("st-chp6-p161-v1-22","pending","比较对象含家族且主体为人物；受控 compared_with 的域／值域不支持该组合，故不强塞。"),
    ]
    assert len(decisions)==25
    assert sum(x[1]=="formal" for x in decisions)==10 and sum(x[1]=="pending" for x in decisions)==12 and sum(x[1]=="rejected" for x in decisions)==3
    assert all(d[0] in {s["statement_id"] for s in statements} for d in decisions)

    process_note = f"""

<a id="{ANCHOR}"></a>

### 跨章身份组／S4 登记／S5 字段／S6 逐项裁决：第6章 p.161 Altieri 宫殿与人物端点（{DATE}）

#### S3 身份组与 S4 登记

本批沿用既有 S3 `new` 决定，不重开身份判断。cand-0090 以第4章 p.118、第6章 p.156 与 p.161 的连续书内提及归入 `sg3-place-cand-0090`；Altieri 宫殿、内部主厅、主厅壁画与整座宫殿装饰计划分别登记。cand-6464 与 cand-5108（Cortona 壁画）保持不同作品身份。Ponte S. Angelo 已有独立 `new` 地点候选 cand-6465。cand-6443 与 cand-1734 沿用各自跨章术语身份组，不并入一般 Baroque 或既有 Nepotism KU。

| candidate_id | 既有 S3 身份组 | S4 KU | 对象范围 |
|---|---|---|---|
""" + "\n".join(f"| `{i['cid']}` | `{i['group']}` | `{i['ku']}` | {i['identity']} |" for i in ITEMS) + """

相关候选 cand-6473 Barberini family、cand-6484 Chigi family、cand-6466 Altieri fresco、cand-6461 Altieri family、cand-6482 accession event 已按既有 S3 决定映射；本批不重复登记。复用对象包括 Clement IX、Clement X、Massimi、Maratta、Bellori、Rome 与 Urban VIII。以下仍保留 S3 待证：cand-6463 未识别肖像、cand-6470 未具名美德组、cand-6472 Cortona 天顶画、cand-6480 Berrettoni 未指定作品、cand-6479 A. Clark 书目、cand-6338 Bellori 1942 书目，以及 cand-6483 宫殿施工活动。cand-6481 学生未具名且类型未定。该范围没有新增 conflict；上述对象均不以卡片补齐为由强制归并。

全书 S4 汇总预检另发现第15章 p.371 Ferney place 候选 cand-10581 已有 `new` 决定和 KU，但对齐说明漏写身份组标记。本批在原有 S3 说明中补记其单候选组 `sg3-place-cand-10581`，不改身份边界、决定或 KU；共用计数解析器同时接受历史 `Group=` 大小写写法。

#### S2 原子化与页图校读

将 `st-chp6-p161-v1-04` 收窄为 Clement IX 委托 Bernini 天使群，并新增 `st-chp6-p161-v1-04-intended-placement` 单独记录原定安置于桥上；不表示实际安装。将 `st-chp6-p161-v1-10` 收窄为 Massimi 建议选择 Maratta，新增咨询 Bellori 的断言；consultation 没有精确受控谓词，S6 pending。将 `st-chp6-p161-v1-14` 的壁画题材改为壁画→Public Happiness，并另存其旗帜象征 Don Gasparo 的来源解释。将 `st-chp6-p161-v1-15` 拆为 adopted nephew 关系和 Gonfaloniere 职衔属性，避免把 Clement X 误作职务端点。将 `st-chp6-p161-v1-19` 保留未完成及未说明分歧，并新增装饰计划 intended_for 宫殿的独立断言。新增5条 statement，其中4条为 S6 关系候选、1条职衔属性；未增 mention，均不计入 S2 独立语义复核分子。

对照 CHP-6.pdf 物理页16（印刷页161）图像校读：原OCR `Clement IXin` 读作 `Clement IX in`；`osa Barberini` 读作 `a Barberini`，并由第162页续句补全 `or a Chigi`。S0 转录保留原样，校读取证写入 statement qualifiers，不改写来源文本。

#### S5 来源字段

10张新卡共提取 {len(fields)} 条 Haskell 原书字段，均为 source_backed，未新增外部来源或独立身份核验。字段限定宫殿与主厅空间、雕塑委托和原定安置、计划性装饰的未完成状态、两项壁画寓意及三个跨章术语的书内用法；没有把模糊的“the work dragged on”时间范围分派给某一对象。

#### S6 逐项去向

本批25项关系候选均有当前决定：10 formal、12 pending、3 rejected。仅formal写入 `relations.csv`，pending 与 rejected 保留理由但不生成边。

| statement_id | 去向 | 裁决与边界 |
|---|---|---|
""" + "\n".join(f"| `{sid}` | {status}{(' `' + detail.split(' ')[0] + '`' if status=='formal' and detail.startswith('rel-') else '')} | {detail} |" for sid,status,detail in decisions) + """

note 1 的 Pascoli 引注属于相邻 Canini 讨论，不纳入本批 Altieri 关系裁决。未决的 Bellori、Clark 与 Berrettoni 身份继续阻断对应正式引注边；原书中“the work”的指代不确定、未命名 stucco frame、主厅 readiness、Baroque 风格评价和 nepotism 政策表述均不以弱谓词替代。除上述25项外，本批不处理同页其他艺术家关系。
"""
    process_new = process.rstrip() + process_note
    batch_result = (f"**第6章 p.161 Altieri 宫殿跨章端点批次（{DATE}）：** 沿用10个既有 S3 `new` 身份组，登记10个KU及10条S4映射；新增{len(fields)}条 Haskell 原书 S5 字段。S2 关系断言拆分后新增5条statement（4条关系候选、1条职衔属性），不增加mention或独立复核分子。25项S6逐项裁决为10 formal、12 pending、3 rejected，新增rel-{next_rel:04d}–rel-{next_rel+len(new_rel)-1:04d}。未识别肖像、Cortona作品、Bellori/Clark书目与不明施工活动保留待证；OCR校读只记入 qualifiers，不改S0转录。详见[跨章身份与逐项裁决](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。\n\n")
    marker = "### 本轮进度与后续工作（2026-10-24）\n"
    assert result.count(marker)==1
    result = result.replace(marker, marker+"\n"+batch_result, 1)
    result = re.sub(r"^\*\*当前状态：.*$", lambda m:m.group(0), result, count=1, flags=re.M)

    # Create the exact planned writes and a recovery snapshot before applying.
    stmt_bytes = b"\xef\xbb\xbf" + ("\n".join(json.dumps(s,ensure_ascii=False,separators=(",",":")) for s in statements)+"\n").encode("utf-8")
    enr_bytes = enr_raw + enr_append
    accepted_bytes = (b"\xef\xbb\xbf" if paths["accepted"].read_bytes().startswith(b"\xef\xbb\xbf") else b"") + planned_accepted.encode("utf-8")
    process_bytes = (b"\xef\xbb\xbf" if paths["process"].read_bytes().startswith(b"\xef\xbb\xbf") else b"") + process_new.encode("utf-8")
    result_bytes = (b"\xef\xbb\xbf" if paths["result"].read_bytes().startswith(b"\xef\xbb\xbf") else b"") + result.encode("utf-8")
    writes = {paths["alignment"]:write_csv_bytes(paths["alignment"],af,planned_align), paths["manifest"]:write_csv_bytes(paths["manifest"],mf,planned_manifest),
        paths["relations"]:write_csv_bytes(paths["relations"],rf,planned_rel), paths["statements"]:stmt_bytes, paths["enrichment"]:enr_bytes,
        paths["accepted"]:accepted_bytes, paths["process"]:process_bytes, paths["result"]:result_bytes}
    if args.dry_run:
        print(f"dry-run passed: {len(ITEMS)} S4 groups/cards; {len(fields)} source-backed S5 fields; {len(new_rel)} formal S6 relations")
        print("S6 dispositions: 25 total = 10 formal, 12 pending, 3 rejected; S2 +5 statements, +0 mentions")
        print(f"new relation IDs: rel-{next_rel:04d}–rel-{next_rel+len(new_rel)-1:04d}; no duplicate natural keys")
        return 0

    recovery = ROOT/"06-runtime"/"recovery"/"S4-S5-S6-chp6-p161-altieri-endpoints-20261024"
    recovery.mkdir(parents=True, exist_ok=False)
    backup = {}
    for path in list(writes)+list(cards):
        rel=path.relative_to(ROOT); original=path.read_bytes() if path.exists() else None
        if original is not None:
            dest=recovery/"original"/rel; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(original)
            backup[rel.as_posix()]=hashlib.sha256(original).hexdigest()
        else:
            backup[rel.as_posix()]=None
    (recovery/"backup-manifest.json").write_text(json.dumps(backup,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for path,content in cards.items(): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding="utf-8-sig",newline="\n")
    for path,data in writes.items(): path.write_bytes(data)
    print(f"applied: S4={len(ITEMS)}; S5={len(fields)}; S6 formal={len(new_rel)}, pending=12, rejected=3; recovery={recovery.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
