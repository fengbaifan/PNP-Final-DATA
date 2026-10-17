from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def source(location: str, summary: str, quote: str, source_file: str, span: str) -> dict:
    return {
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": span,
        },
    }


CH9 = "02-sources/02-Markdown/09_CHP-9_intro.md"
CH9_II = "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
CH10 = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
CH13 = "02-sources/02-Markdown/13_CHP-13_intro.md"

TARGETS = [
    {
        "group": "sg3-event-cand-8587",
        "candidates": ["cand-8587"],
        "ku": "units/events/s-rocco-annual-exhibition",
        "type": "event",
        "name_zh": "圣罗科年度展览系列",
        "name_en": "Annual S. Rocco exhibition series",
        "sources": [
            source("第9章；印刷页263；OCR L418（注5）", "Haskell's note says Sagredo bought Piazzetta's Angelo Custode at the S. Rocco exhibition; it gives no year.", "he bought Piazzetta’s Angelo Custode at the S. Rocco exhibition", CH9, "line 418; print p.263, note 5"),
            source("第9章；印刷页265；OCR L292", "Haskell places Sagredo's purchase at one of the annual exhibitions at S. Rocco.", "at one of the annual exhibitions at S. Rocco he bought Piazzetta’s Angelo Custode", CH9, "line 292; print p.265"),
            source("第10章；印刷页331；OCR L270", "Haskell describes more systematic exhibitions at the Scuola di S. Rocco and says a number of artists participated every year.", "far more systematic exhibitions at the Scuola di S. Rocco", CH10, "line 270; print p.331"),
        ],
        "body": """## 内容

### 描述

**中文：** 本卡记录哈斯克尔所述的圣罗科年度绘画展览系列。第10章称，圣罗科的展览较有组织，每年都有若干画家参加；作者认为它们可能从总督与元老院每年8月16日前往该教堂的巡行中非正式发展而来，此解释保留“可能”限定。第9章记载萨格雷多曾在某一年度展览中购入 Piazzetta 的《Angelo Custode》，未给出年份。展览系列不等同于某一已定年的场次。〔[第10章 p.331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L270）；[第9章 p.265](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L292）〕

**English:** This unit records the annual painting-exhibition series at S. Rocco described by Haskell. Chapter 10 calls the exhibitions more systematic and says that several artists took part each year. The author says they probably developed informally from the Doge and Senate's procession to the church on 16 August; the qualification “probably” is retained. Chapter 9 says that Sagredo bought Piazzetta's *Angelo Custode* at one annual exhibition but gives no year. The series is distinct in identity from any dated occurrence. ([Chapter 10, p. 331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (line 270); [Chapter 9, p. 265](../../../02-sources/02-Markdown/09_CHP-9_intro.md) (line 292).)

### 基本信息

- **事件性质：** 年度绘画展览系列；不是单一场次。
- **周期：** Haskell称每年举行；未给系列起始年、结束年或完整场次数。
- **书内场所称谓：** 第10章称 Scuola di S. Rocco。具体场所对象身份仍按现有对齐记录保留，不由本卡标准化为教堂建筑或机构。

## 关系与证据

目前没有登记为 S6 正式关系的记录；相关 S2 关系候选保留待 S6 审查。""",
    },
    {
        "group": "sg3-event-cand-9871",
        "candidates": ["cand-9871"],
        "ku": "units/events/doge-senate-procession-to-s-rocco-august-16",
        "type": "event",
        "name_zh": "威尼斯总督与元老院赴圣罗科堂巡行（8月16日）",
        "name_en": "Doge and Senate procession to S. Rocco (16 August)",
        "sources": [source("第10章；印刷页331；OCR L270", "Haskell says the Doge and Senate went in procession to the church each 16 August and describes this as the probable informal origin of the annual exhibitions.", "the processions which the Doge and Senate made to the church each 16 August", CH10, "line 270; print p.331")],
        "body": """## 内容

### 描述

**中文：** 哈斯克尔记述威尼斯总督与元老院每年8月16日赴圣罗科堂巡行。作者认为，圣罗科较有组织的展览“可能”非正式地从这些巡行发展而来；巡行与展览系列是不同事件，且起源解释并非确定事实。〔[第10章 p.331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L270）〕

**English:** Haskell describes an annual procession by the Doge and Senate of Venice to the church of S. Rocco on 16 August. He says the more systematic exhibitions there probably developed informally from these processions. The procession and exhibition series are distinct events, and the proposed origin remains uncertain. ([Chapter 10, p. 331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (line 270).)

### 基本信息

- **事件性质：** 年度公共巡行。
- **日期：** 每年8月16日；原文未提供其他起讫时间。
- **参与机构／职务：** 威尼斯总督职务与威尼斯元老院；本卡不将总督这一职务并入某一具体任职者。
- **目的地：** 原文称前往 S. Rocco 的教堂；不据此裁定该名称在本段中的建筑或机构边界。

## 关系与证据

目前没有登记为 S6 正式关系的记录；关于巡行与展览缘起的 S2 候选保留来源限定并待 S6 审查。""",
    },
    {
        "group": "sg3-event-cand-10005",
        "candidates": ["cand-10005"],
        "ku": "units/events/exhibition-of-16-august-1770-albrizzi-account",
        "type": "event",
        "name_zh": "1770年8月16日展览（Albrizzi 记述）",
        "name_en": "Exhibition of 16 August 1770 (Albrizzi account)",
        "sources": [source("第13章；印刷页336；OCR L49", "Haskell says that Albrizzi, while Guardiano in 1770, took two Zais pictures to an exhibition on 16 August; the clause does not specify the exact venue.", "he took two of that artist’s pictures to the exhibition on 16 August", CH13, "line 49; print p.336")],
        "body": """## 内容

### 描述

**中文：** 哈斯克尔称，Albrizzi 于1770年担任 Scuola di S. Rocco 的 Guardiano 时，将 Giuseppe Zais 的两幅画带到8月16日的展览。原句没有在该展览短语中明确场地；本卡只记录有据的日期和展览活动，不补定具体地点。该场次作为有日期的事件，与年度展览系列分开登记。〔[第13章 p.336](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L49）〕

**English:** Haskell says that, while Albrizzi was Guardiano of the Scuola di S. Rocco in 1770, he took two pictures by Giuseppe Zais to an exhibition on 16 August. The clause does not explicitly name the exhibition venue. This unit records the dated event without assigning a more specific location. The occurrence is registered separately from the recurring annual exhibition series. ([Chapter 13, p. 336](../../../02-sources/02-Markdown/13_CHP-13_intro.md) (line 49).)

### 基本信息

- **事件性质：** 一次展览场次。
- **时间：** 1770年8月16日。
- **参与者：** Haskell称 Albrizzi 带去两幅 Zais 作品；两幅作品尚未个别识别。
- **地点：** 该句未明确展览的具体场地。

## 关系与证据

目前没有登记为 S6 正式关系的记录。两幅画仍保持未决，不因本事件登记而新建作品知识元。""",
    },
    {
        "group": "workgrp-2db59a92c3c7c6",
        "candidates": ["cand-8569"],
        "ku": "units/works/piazzetta-angelo-custode-altarpiece",
        "type": "work",
        "name_zh": "《守护天使》",
        "name_en": "Guardian Angel (Angelo Custode)",
        "sources": [
            source("第9章；印刷页262；OCR L220", "Haskell says the large picture of the Angelo Custode was valued at about 100 zecchini.", "Piazzetta’s large picture of the Angelo Custode was valued at about 100 zecchini", CH9, "line 220; print p.262"),
            source("第9章；印刷页265；OCR L292", "Haskell identifies the picture as a huge altarpiece bought by Zaccaria Sagredo at an annual S. Rocco exhibition.", "Piazzetta’s Angelo Custode, a huge altarpiece", CH9, "line 292; print p.265"),
            source("第9章；印刷页265；OCR L297（注2）", "Haskell's note says part of the picture was then in the Detroit Institute of Arts; the nested references are not independently consulted.", "Part of the picture is now in the Detroit Institute of Arts.", CH9, "line 297; print p.265, note 2"),
        ],
        "body": """## 内容

### 描述

**中文：** 哈斯克尔称 Piazzetta 创作的《Angelo Custode》为一幅大型祭坛画。第262页记其估价约100 zecchini；这是估值，不是成交价。第265页称 Zaccaria Sagredo 在某一届圣罗科年度展览中购入该画，未给年份。注2称该画的“部分”在作者所述时间位于 Detroit Institute of Arts；该陈述不是对今日馆藏状态的独立核验。〔[第9章 p.262](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L220）；[第9章 p.265](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L292、L297）〕

**English:** Haskell describes Piazzetta's *Angelo Custode* (rendered here as *Guardian Angel*) as a large altarpiece. On page 262 he reports an approximate valuation of 100 zecchini; this is not a sale price. On page 265 he says Zaccaria Sagredo bought it at one annual S. Rocco exhibition, without giving the year. Note 2 says that “part” of the picture was then in the Detroit Institute of Arts. This reports Haskell's time-relative statement and does not independently verify a present-day holding. ([Chapter 9, p. 262](../../../02-sources/02-Markdown/09_CHP-9_intro.md) (line 220); [p. 265](../../../02-sources/02-Markdown/09_CHP-9_intro.md) (lines 292, 297).)

### 作品信息

- **书内称谓：** *Angelo Custode*；中文显示名《守护天使》是描述性译名。〔第9章 p.262（L220）〕
- **作品类型：** 大型祭坛画。〔第9章 p.265（L292）〕
- **创作者：** Giovanni Battista Piazzetta；按 Haskell 叙述。〔第9章 p.262、p.265（L220、L292）〕
- **估值：** 约100 zecchini；不是成交价。〔第9章 p.262（L220）〕
- **购藏：** Zaccaria Sagredo 在某一届 S. Rocco 年度展览购入；年份未载。〔第9章 p.265（L292）〕
- **存放记述：** Haskell 注称部分作品当时在 Detroit Institute of Arts；未据此断言今日完整作品所在地。〔第9章 p.265 注2（L297）〕

### 本章相关内容

Haskell 称画家此前未能在别处售出此画，并称 Piazzetta 与 Tiepolo 在编制收藏估价时都高度评价该画；“最重要的现代收藏”等评价保持为作者表述，不转成作品固有属性。〔[第9章 p.265](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L292）〕

## 关系与证据

相关 S2 关系候选待 S6 审查，目前没有新增正式关系。""",
    },
    {
        "group": "sg3-institution-cand-8129",
        "candidates": ["cand-8129"],
        "ku": "units/institutions/senate-of-venice",
        "type": "institution",
        "name_zh": "威尼斯元老院",
        "name_en": "Senate of Venice",
        "sources": [
            source("第9章；印刷页247；OCR L28", "Haskell says the Senate was compelled to admit more new families as State resources drained during the wars against the Turks.", "the Senate was, in fact, compelled to admit more and more new families", CH9, "line 28; print p.247"),
            source("第9章；印刷页272；OCR L56", "Haskell says the Pietà refuge came under the direct patronage of the Doge and Senate.", "it had soon come under the direct patronage of the Doge and Senate", CH9_II, "line 56; print p.272"),
            source("第10章；印刷页331；OCR L270", "Haskell says the Doge and Senate went in procession to S. Rocco each 16 August.", "the processions which the Doge and Senate made to the church each 16 August", CH10, "line 270; print p.331"),
        ],
        "body": """## 内容

### 描述

**中文：** 本卡记录 Haskell 所称的威尼斯元老院这一政治机构。第9章提到其在国家财政资源消耗时被迫接纳新贵族家族，并称其与总督共同庇护 Pietà 避难机构；第10章称元老院与总督每年8月16日前往圣罗科堂巡行。上述记载保留各自章节语境，不把 Senate 与威尼斯共和国、城市或其他行政机构等同。〔[第9章 p.247](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L28）；[第9章 p.272](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L56）；[第10章 p.331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L270）〕

**English:** This unit records the political institution called the Senate of Venice in Haskell's account. Chapter 9 says it was compelled to admit new noble families as State resources were depleted and that it shared patronage of the Pietà refuge with the Doge. Chapter 10 says the Senate and Doge processed to S. Rocco each 16 August. These statements retain their separate contexts; the Senate is not equated with the Republic of Venice, the city, or another administrative body. ([Chapter 9, p. 247](../../../02-sources/02-Markdown/09_CHP-9_intro.md) (line 28); [p. 272](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md) (line 56); [Chapter 10, p. 331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (line 270).)

## 关系与证据

当前没有登记为 S6 正式关系的记录。""",
    },
    {
        "group": "sg3-institution-cand-8728",
        "candidates": ["cand-8728"],
        "ku": "units/institutions/doge-of-venice-office",
        "type": "institution",
        "name_zh": "威尼斯总督职务",
        "name_en": "Office of the Doge of Venice",
        "sources": [
            source("第9章；印刷页272；OCR L56", "Haskell says the Pietà refuge came under the direct patronage of the Doge and Senate.", "it had soon come under the direct patronage of the Doge and Senate", CH9_II, "line 56; print p.272"),
            source("第10章；印刷页331；OCR L270", "Haskell refers to the Doge as a recurring officeholder in the annual procession to S. Rocco.", "the processions which the Doge and Senate made to the church each 16 August", CH10, "line 270; print p.331"),
        ],
        "body": """## 内容

### 描述

**中文：** 本卡记录 Haskell 在跨章叙述中以一般职务称谓提到的威尼斯总督。第9章称 Pietà 避难机构受到总督与元老院的直接庇护；第10章称总督与元老院每年8月16日赴圣罗科堂巡行。本卡表达的是制度性职务，不指向某一位总督，也不将职务与具体任职者合并。〔[第9章 p.272](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L56）；[第10章 p.331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L270）〕

**English:** This unit records the Doge of Venice as a general institutional office in Haskell's cross-chapter account. Chapter 9 says the Pietà refuge came under the direct patronage of the Doge and Senate; Chapter 10 says the Doge and Senate processed to S. Rocco each 16 August. The unit denotes the office, not a particular officeholder, and does not merge the office with any named person. ([Chapter 9, p. 272](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md) (line 56); [Chapter 10, p. 331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (line 270).)

## 关系与证据

当前没有登记为 S6 正式关系的记录。""",
    },
    {
        "group": "sg3-term-cand-9866",
        "candidates": ["cand-9866"],
        "ku": "units/terms/painters-in-s-rocco-exhibition-reports",
        "type": "term",
        "name_zh": "圣罗科展览报道中的画家群体",
        "name_en": "Painters mentioned in reports of the S. Rocco exhibitions",
        "sources": [
            source("第10章；印刷页330；OCR L265–267（注4）", "Haskell quotes reports naming painters of the present Venetian school and works by old and living painters.", "the painters of the present Venetian school exhibit their performances in the Scuola", CH10, "lines 265–267; print p.330, note 4"),
            source("第10章；印刷页331；OCR L270", "Haskell says a number of artists took part in the S. Rocco exhibitions each year.", "every year a number of artists took part", CH10, "line 270; print p.331"),
        ],
        "body": """## 内容

### 描述

**中文：** 本术语项归集 Haskell 所引圣罗科展览报道中对参展画家的概括性称谓：Thomas Martyn 的文字称“当时威尼斯画派的画家”在 Scuola 展示作品；1762年《Nuova Gazzetta Veneta》提及古代与在世画家的其他作品；正文另称每年有若干画家参加。这里记录的是来源中的群体称谓，不是有名册的组织或一个可还原成员名单的历史社团。不同报道中的画家不据此视为完全相同的一组人。〔[第10章 p.330 注4](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L265–267）；[p.331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L270）〕

**English:** This term groups the collective descriptions of exhibiting painters in reports cited by Haskell about S. Rocco. Thomas Martyn's text refers to “painters of the present Venetian school” showing their work at the Scuola; the 1762 *Nuova Gazzetta Veneta* mentions other works by old and living painters; the main text says that several artists took part each year. This is a source-defined collective label, not a named organization or a recoverable membership list. Painters in the different reports are not assumed to be exactly the same group. ([Chapter 10, p. 330, note 4](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (lines 265–267); p. 331 (line 270).)

### 概念边界

- **适用范围：** Haskell 所引报道及其本人对圣罗科年度展示的概括。
- **不适用边界：** 不指单一画家、完整参展名册或正式画家团体；不把各引文提及的全部画家合并为同一批成员。

## 关系与证据

当前没有登记为 S6 正式关系的记录。""",
    },
    {
        "group": "sg3-event-cand-9870",
        "candidates": ["cand-9870"],
        "ku": "units/events/salon-in-paris-exhibition-series",
        "type": "event",
        "name_zh": "巴黎沙龙展览（Haskell 所引比较对象）",
        "name_en": "Salon in Paris (exhibition series cited by Haskell)",
        "sources": [source("第10章；印刷页331；OCR L270", "Haskell reports Algarotti's comparison of the S. Rocco exhibition to the Paris Salon and says the S. Rocco showings were less complex and attracted less attention.", "like the Salon in Paris", CH10, "line 270; print p.331")],
        "body": """## 内容

### 描述

**中文：** 哈斯克尔在比较圣罗科展览时提到巴黎的 Salon：他转述 Algarotti 至迟在1751年将圣罗科展览称为“在某些方面”如同绘画的 tribunal，随后指出圣罗科展示在组织复杂程度和吸引关注方面都未达到 Salon 的程度。本卡只登记被明确点名的比较对象，不从这段文字补写巴黎展览的起讫时间、组织细节或历史沿革；二者不视为同一展览。〔[第10章 p.331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L270）〕

**English:** Haskell mentions the Salon in Paris while comparing it with the S. Rocco exhibitions. He reports that by 1751 Algarotti described the S. Rocco exhibition as, “in some ways,” the tribunal of Venetian painting, then says its organization and public attention never approached those of the Salon. This unit records the explicitly named comparison object without adding dates, organizational details, or a history of the Paris exhibition; the two exhibitions are not treated as identical. ([Chapter 10, p. 331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (line 270).)

## 关系与证据

相关 S2 比较候选留待 S6 审查，目前没有新增正式关系。""",
    },
    {
        "group": "archive-group-51421cc9cca5",
        "candidates": ["cand-9863"],
        "ku": "units/archives/papal-nuncio-report-1729-08-20",
        "type": "archive",
        "name_zh": "1729年8月20日教廷使节报告（Haskell 引用）",
        "name_en": "Papal Nuncio report of 20 August 1729 (as cited by Haskell)",
        "sources": [source("第10章；印刷页330；OCR L349（注4）", "Haskell cites a report from the papal Nunzio dated 20 August 1729, located in Archivio Vaticano—Venezia, no. 180, and reproduces a passage about paintings and a crowd.", "A report from the papal Nunzio of 20 August 1729 in the Archivio Vaticano—Venezia, n. 180", CH10, "line 349; print p.330, note 4(i)")],
        "body": """## 内容

### 描述

**中文：** 本卡记录 Haskell 在第10章注释中引用的一份教廷使节报告：日期为1729年8月20日，书内定位为 Archivio Vaticano—Venezia，第180号。哈斯克尔引述的意大利文称，当时展出了一些古代与现代画家的作品，并有大量民众聚集。报告引文本身没有指出展览场地；本档案项不据此关联圣罗科展览系列。〔[第10章 p.330 注4(i)](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L349）〕

**English:** This unit records a report from the papal Nunzio cited in Haskell's Chapter 10 footnote: dated 20 August 1729 and located there as Archivio Vaticano—Venezia, no. 180. The Italian passage reproduced by Haskell says that works by old and modern painters were displayed and that a large crowd gathered. The quoted report does not identify the venue; this archive item is therefore not attached to the S. Rocco exhibition series. ([Chapter 10, p. 330, note 4(i)](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (line 349).)

### 文献定位

- **文献类型：** Haskell 所引报告。
- **日期：** 1729年8月20日。
- **书内档案定位：** Archivio Vaticano—Venezia，n. 180；按原书引用记录，未独立核对馆藏目录或原件。

## 关系与证据

报告与展览场地之间的关系未成立；不新增正式关系。""",
    },
    {
        "group": "archive-group-e9b0dc02987a",
        "candidates": ["cand-9869"],
        "ku": "units/archives/algarotti-letter-to-mariette-s-rocco-by-1751",
        "type": "archive",
        "name_zh": "Algarotti 致 Mariette 谈圣罗科展览的书信（至迟1751年）",
        "name_en": "Algarotti's letter to Mariette on the S. Rocco exhibition (by 1751)",
        "sources": [source("第10章；印刷页331；OCR L270", "Haskell reports that by 1751 Algarotti could write to Mariette comparing the S. Rocco exhibition with the Paris Salon.", "By 1751 Francesco Algarotti could write to Mariette that the exhibition was ‘in some ways the tribunal of our painting like the Salon in Paris’.", CH10, "line 270; print p.331")],
        "body": """## 内容

### 描述

**中文：** 本卡记录 Haskell 所引 Francesco Algarotti 致 Pierre-Jean Mariette 书信中的展览比较。书中称，至迟在1751年，Algarotti 曾将圣罗科展览比作“在某些方面”如同绘画的 tribunal 的巴黎 Salon。此为 Haskell 对书信的转述和引文；书信原件未在本任务中独立查阅，不能据此指定更精确日期或档案馆藏。〔[第10章 p.331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L270）〕

**English:** This unit records the comparison in a letter from Francesco Algarotti to Pierre-Jean Mariette cited by Haskell. The book says that by 1751 Algarotti had described the S. Rocco exhibition as, “in some ways,” the tribunal of Venetian painting like the Paris Salon. This is Haskell's report and quotation; the letter itself was not independently consulted here, so no more precise date or repository is assigned. ([Chapter 10, p. 331](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (line 270).)

### 文献定位

- **文献类型：** 书信。
- **作者／收信人：** Francesco Algarotti 致 Pierre-Jean Mariette；按 Haskell 的表述。
- **时间：** Haskell 称“至迟在1751年”；不是已核定的确切写信日期。

## 关系与证据

书信中的比较断言留待 S6 审查；目前没有新增正式关系。""",
    },
    {
        "group": "archive-group-730f3cb1654d",
        "candidates": ["cand-8580"],
        "ku": "units/archives/cochin-volume-iii-sagredo-pictures-1758",
        "type": "archive",
        "name_zh": "Cochin 第三卷所记 Sagredo 宫绘画（1758）",
        "name_en": "Cochin, vol. III: account of paintings in the Sagredo palace (1758)",
        "sources": [
            source("第9章；印刷页263；OCR L237", "Haskell cites Cochin, vol. III, pp. 143–150, for pictures in Zaccaria Sagredo's collection.", "Cochin, III, pp. 143-50, discussed many of the pictures in the collection.", CH9, "line 237; print p.263"),
            source("第9章；印刷页265；OCR L297（注2）", "Haskell says Cochin wrote an account in 1758 of pictures then in the Sagredo palace and called the Angelo Custode a tableau fort beau.", "who in 1758 wrote an account of the pictures then in the Sagredo palace", CH9, "line 297; print p.265, note 2"),
        ],
        "body": """## 内容

### 描述

**中文：** 本卡按 Haskell 的引文定位记录 Cochin 第三卷中关于 Sagredo 宫绘画的记述。第9章 p.263 指向第三卷第143–150页；p.265 注2称 Cochin 于1758年记述当时位于 Sagredo 宫中的绘画，并称《Angelo Custode》为“tableau fort beau”。完整书名、版本及引文上下文在此处没有独立核验；本卡不将 Haskell 的引文定位扩展为已读原书。〔[第9章 p.263](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L237）；[p.265 注2](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L297）〕

**English:** This unit records the citation locator in Haskell for Cochin's third volume and its account of paintings in the Sagredo palace. Chapter 9, p. 263 points to volume III, pages 143–150; note 2 on p. 265 says Cochin wrote an account in 1758 of pictures then in the Sagredo palace and called the *Angelo Custode* “tableau fort beau.” The full title, edition, and cited context have not been independently verified here; Haskell's citation is not treated as evidence that the original volume was read. ([Chapter 9, p. 263](../../../02-sources/02-Markdown/09_CHP-9_intro.md) (line 237); [p. 265, note 2](../../../02-sources/02-Markdown/09_CHP-9_intro.md) (line 297).)

### 文献定位

- **文献类型：** Cochin 著作中的第三卷段落；此处按作者与卷页定位。
- **年代语境：** Haskell 称该记述作于1758年。
- **页码：** Haskell 引为第143–150页；注2另指第150页。

## 关系与证据

相关 S2 评价断言留待 S6 审查；未将引用定位写成已核原件或版本。""",
    },
    {
        "group": "new-person:charles-cochin-nicolas-9535855bb7",
        "candidates": ["cand-0793"],
        "ku": "units/persons/charles-nicolas-cochin",
        "type": "person",
        "name_zh": "夏尔-尼古拉·科尚",
        "name_en": "Charles-Nicolas Cochin",
        "sources": [
            source("第9章；印刷页263；OCR L237", "Haskell cites Cochin, vol. III, pp. 143–150, in discussing the Sagredo collection.", "Cochin, III, pp. 143-50", CH9, "line 237; print p.263"),
            source("第9章；印刷页265；OCR L297（注2）", "Haskell names Cochin as the author of a 1758 account of pictures then in the Sagredo palace.", "who in 1758 wrote an account", CH9, "line 297; print p.265, note 2"),
        ],
        "body": """## 内容

### 描述

**中文：** Haskell 在第9章引用 Cochin 第三卷，并称 Cochin 于1758年写过一份记录 Sagredo 宫当时绘画的记述。该书目语境支持此人物候选与 Cochin, III 的作者同一；本卡不据此扩写生平或其他身份。〔[第9章 p.263](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L237）；[p.265 注2](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L297）〕

**English:** Haskell cites Cochin's third volume in Chapter 9 and says that Cochin wrote an account in 1758 of pictures then in the Sagredo palace. This source context identifies the person candidate with the author of *Cochin*, volume III; no broader biography or additional identity claims are added. ([Chapter 9, p. 263](../../../02-sources/02-Markdown/09_CHP-9_intro.md) (line 237); [p. 265, note 2](../../../02-sources/02-Markdown/09_CHP-9_intro.md) (line 297).)

## 关系与证据

当前没有登记为 S6 正式关系的记录。""",
    },
]

REUSED = {
    "candidate_id": "cand-7072",
    "ku_id": "units/institutions/detroit-institute-of-arts",
    "path": "04-knowledge/units/institutions/detroit-institute-of-arts.md",
}


CONTENT_LINKS = {
    "sg3-event-cand-8587": [
        ("总督与元老院", "[威尼斯总督职务](../institutions/doge-of-venice-office.md)与[威尼斯元老院](../institutions/senate-of-venice.md)"),
        ("每年8月16日前往该教堂的巡行", "每年8月16日前往该教堂的[巡行](../events/doge-senate-procession-to-s-rocco-august-16.md)"),
        ("萨格雷多", "[萨格雷多](../persons/zaccaria-sagredo.md)"),
        ("Piazzetta 的《Angelo Custode》", "Piazzetta 的[《守护天使》](../works/piazzetta-angelo-custode-altarpiece.md)"),
        ("the Doge and Senate's procession", "the procession by the [Doge](../institutions/doge-of-venice-office.md) and [Senate](../institutions/senate-of-venice.md)"),
        ("Sagredo bought Piazzetta's *Angelo Custode*", "[Sagredo](../persons/zaccaria-sagredo.md) bought Piazzetta's [*Angelo Custode*](../works/piazzetta-angelo-custode-altarpiece.md)"),
    ],
    "sg3-event-cand-9871": [
        ("威尼斯总督与元老院", "[威尼斯总督职务](../institutions/doge-of-venice-office.md)与[威尼斯元老院](../institutions/senate-of-venice.md)"),
        ("展览系列", "[展览系列](../events/s-rocco-annual-exhibition.md)"),
        ("the Doge and Senate of Venice", "the [Doge of Venice](../institutions/doge-of-venice-office.md) and [Senate](../institutions/senate-of-venice.md)"),
        ("exhibition series", "[exhibition series](../events/s-rocco-annual-exhibition.md)"),
    ],
    "sg3-event-cand-10005": [
        ("Albrizzi", "[Albrizzi](../persons/albrizzi.md)"),
        ("Giuseppe Zais", "[Giuseppe Zais](../persons/giuseppe-zais.md)"),
    ],
    "workgrp-2db59a92c3c7c6": [
        ("Piazzetta", "[Piazzetta](../persons/piazzetta.md)"),
        ("Zaccaria Sagredo", "[Zaccaria Sagredo](../persons/zaccaria-sagredo.md)"),
        ("Detroit Institute of Arts", "[Detroit Institute of Arts](../institutions/detroit-institute-of-arts.md)"),
        ("one annual S. Rocco exhibition", "one [annual S. Rocco exhibition](../events/s-rocco-annual-exhibition.md)"),
        ("Tiepolo", "[Tiepolo](../persons/giambattista-tiepolo.md)"),
    ],
    "sg3-institution-cand-8129": [
        ("总督", "[总督职务](../institutions/doge-of-venice-office.md)"),
        ("每年8月16日前往圣罗科堂巡行", "每年8月16日前往圣罗科堂[巡行](../events/doge-senate-procession-to-s-rocco-august-16.md)"),
        ("the Doge", "the [Doge](../institutions/doge-of-venice-office.md)"),
        ("processed to S. Rocco each 16 August", "took part in the [procession to S. Rocco each 16 August](../events/doge-senate-procession-to-s-rocco-august-16.md)"),
    ],
    "sg3-institution-cand-8728": [
        ("元老院", "[元老院](../institutions/senate-of-venice.md)"),
        ("每年8月16日赴圣罗科堂巡行", "每年8月16日赴圣罗科堂[巡行](../events/doge-senate-procession-to-s-rocco-august-16.md)"),
        ("the Doge and Senate processed to S. Rocco each 16 August", "the Doge and [Senate](../institutions/senate-of-venice.md) took part in the [procession to S. Rocco each 16 August](../events/doge-senate-procession-to-s-rocco-august-16.md)"),
    ],
    "sg3-term-cand-9866": [
        ("圣罗科年度展示", "[圣罗科年度展示](../events/s-rocco-annual-exhibition.md)"),
        ("S. Rocco", "[S. Rocco](../events/s-rocco-annual-exhibition.md)"),
    ],
    "sg3-event-cand-9870": [
        ("圣罗科展览", "[圣罗科展览](../events/s-rocco-annual-exhibition.md)"),
        ("the S. Rocco exhibitions", "the [S. Rocco exhibitions](../events/s-rocco-annual-exhibition.md)"),
    ],
    "archive-group-e9b0dc02987a": [
        ("Francesco Algarotti", "[Francesco Algarotti](../persons/francesco-algarotti.md)"),
        ("Pierre-Jean Mariette", "[Pierre-Jean Mariette](../persons/pierre-jean-mariette.md)"),
        ("圣罗科展览", "[圣罗科展览](../events/s-rocco-annual-exhibition.md)"),
        ("巴黎 Salon", "巴黎 [Salon](../events/salon-in-paris-exhibition-series.md)"),
        ("the S. Rocco exhibition", "the [S. Rocco exhibition](../events/s-rocco-annual-exhibition.md)"),
        ("the Paris Salon", "the [Paris Salon](../events/salon-in-paris-exhibition-series.md)"),
    ],
    "archive-group-730f3cb1654d": [
        ("Cochin 第三卷", "[Cochin](../persons/charles-nicolas-cochin.md) 第三卷"),
        ("Cochin's third volume", "[Cochin](../persons/charles-nicolas-cochin.md)'s third volume"),
        ("《Angelo Custode》", "[《Angelo Custode》](../works/piazzetta-angelo-custode-altarpiece.md)"),
        ("the *Angelo Custode*", "the [*Angelo Custode*](../works/piazzetta-angelo-custode-altarpiece.md)"),
    ],
    "new-person:charles-cochin-nicolas-9535855bb7": [
        ("Cochin 第三卷", "[Cochin 第三卷](../archives/cochin-volume-iii-sagredo-pictures-1758.md)"),
        ("*Cochin*, volume III", "[*Cochin*, volume III](../archives/cochin-volume-iii-sagredo-pictures-1758.md)"),
    ],
}


def make_card(target: dict) -> str:
    frontmatter = {
        "title": f"{target['name_zh']}（{target['name_en']}）",
        "name_en": target["name_en"],
        "type": target["type"],
        "evidence_status": "source_backed",
        "sources": target["sources"],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = target["body"].strip()
    for original, linked in CONTENT_LINKS.get(target["group"], []):
        assert original in body, f"missing content-link anchor {original!r} in {target['group']}"
        body = body.replace(original, linked)
    return f"---\n{fm}---\n\n{body}\n"


def validate_target(target: dict, candidate_by_id: dict, alignment_by_id: dict) -> None:
    assert target["type"] in {"archive", "event", "institution", "person", "term", "work"}
    assert len(target["candidates"]) == len(set(target["candidates"]))
    assert len(target["sources"]) > 0
    for cid in target["candidates"]:
        candidate = candidate_by_id[cid]
        decision = alignment_by_id[cid]
        assert candidate["suggested_type"] == target["type"], f"type mismatch: {cid}"
        assert decision["decision"] == "new", f"not an S3 new decision: {cid}"
        assert not decision.get("ku_id"), f"already mapped: {cid}"
        assert sync.get_group(decision.get("resolution_note", "")) == target["group"], f"group mismatch: {cid}"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignment if not row.get("external_source")}
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()

    assert len({target["ku"] for target in TARGETS}) == len(TARGETS), "duplicate planned KU"
    assert len({target["group"] for target in TARGETS}) == len(TARGETS), "duplicate planned identity group"
    assert len({cid for target in TARGETS for cid in target["candidates"]}) == sum(len(t["candidates"]) for t in TARGETS)
    planned_paths = {f"04-knowledge/{target['ku']}.md" for target in TARGETS}
    for target in TARGETS:
        assert target["ku"] not in manifest_by_id, f"KU already exists: {target['ku']}"
        assert not (ROOT / f"04-knowledge/{target['ku']}.md").exists(), f"card already exists: {target['ku']}"
        assert f"- 04-knowledge/{target['ku']}.md" not in accepted_lines
        validate_target(target, candidate_by_id, alignment_by_id)
        for item in target["sources"]:
            source_path = ROOT / item["evidence_ref"]["source_file"]
            assert source_path.exists(), f"missing source file: {source_path}"
            source_text = source_path.read_text(encoding="utf-8-sig")
            normalized_source = " ".join(source_text.split())
            normalized_quote = " ".join(item["original_quotes"][0]["text"].split())
            assert normalized_quote in normalized_source, f"quote not found: {item['original_quotes'][0]['text']}"

    # Correct the earlier S3 "new" decision: chapter 7's "Institute of Arts, Detroit"
    # and chapter 9's "Detroit Institute of Arts" are the same institution already
    # represented by the accepted, identity-verified DIA unit. The Poussin pair-to-site
    # mapping remains unresolved independently of the institution's identity.
    dia_decision = alignment_by_id[REUSED["candidate_id"]]
    assert dia_decision["decision"] == "new" and not dia_decision.get("ku_id")
    assert sync.get_group(dia_decision.get("resolution_note", "")) == "sg3-institution-cand-7072"
    assert REUSED["ku_id"] in manifest_by_id and (ROOT / REUSED["path"]).exists()
    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") == REUSED["candidate_id"] and not row.get("external_source"):
            row["decision"] = "same"
            row["ku_id"] = REUSED["ku_id"]
            row["resolution_note"] += (
                " S3 cross-chapter correction (2026-10-17): same as the already accepted "
                "Detroit Institute of Arts unit. Haskell's chapter 7 wording 'Institute of Arts, Detroit' "
                "and chapter 9 note 2 wording 'Detroit Institute of Arts' identify the same institution; "
                "the existing card's identity record is at 04-knowledge/units/institutions/detroit-institute-of-arts.md. "
                "The unresolved assignment of the two Poussin works to the Louvre and Detroit remains a separate question. "
                "The prior new-group rationale is retained as history; no duplicate institution KU is created."
            )

    planned_manifest = [dict(row) for row in manifest]
    for target in TARGETS:
        for row in planned_alignment:
            if row.get("candidate_id") in target["candidates"] and not row.get("external_source"):
                row["ku_id"] = target["ku"]
                row["resolution_note"] += f" S4 registration: mapped {target['group']} to {target['ku']}."
        planned_manifest.append({
            "ku_id": target["ku"],
            "type": target["type"],
            "canonical_name": target["name_zh"],
            "name_en": target["name_en"],
            "source_task": TASK,
            "card_path": f"04-knowledge/{target['ku']}.md",
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    anchor = "<a id=\"s3-srocco-cross-chapter-s4-registration-20261017\"></a>"
    assert anchor not in process_text
    process_text += (
        f"\n\n{anchor}\n\n### S3 机构复用修正与 S4 圣罗科跨章身份组登记（2026-10-17）\n\n"
        "复核跨章直接端点时，发现 `cand-7072`（第7章 p.180 注4，“Institute of Arts, Detroit”）与既有 "
        "`units/institutions/detroit-institute-of-arts` 重复。第9章 p.265 注2同页明确写出全名 “Detroit Institute of Arts”，" 
        "与现有机构卡的身份记录吻合；故将其 S3 决定从 `new` 更正为 `same` 并复用既有 KU。" 
        "第7章两幅 Poussin 画与两处馆藏的逐件配对仍未解决，不因机构同一性而选择任何一条边。\n\n"
        "S4 按 S3 当前身份组登记：`cand-8587` 圣罗科年度展览系列，`cand-9871` 总督与元老院8月16日巡行，"
        "`cand-10005` 1770年8月16日展览场次，`cand-8569` Piazzetta《Angelo Custode》，`cand-8129` 威尼斯元老院，"
        "`cand-8728` 威尼斯总督职务，`cand-9866` 圣罗科展览报道中的画家群体，`cand-9870` 巴黎 Salon 比较对象，"
        "`cand-9863` 1729年8月20日 Nunzio 报告，`cand-9869` Algarotti 致 Mariette 书信，`cand-8580` Cochin 第三卷引文定位，"
        "以及 `cand-0793` Charles-Nicolas Cochin。每组一个 KU；人名、年份、引文、身份层级和原文限定均按来源记录。\n\n"
        "保持待证：`cand-8588`（S. Rocco 场所身份边界）、`cand-10006`（两幅 Zais 画未个别识别）、"
        "`cand-1904`（“the painter”索引候选缺少可核 S2 body mention）、`cand-8621`（估价记录未识别）、"
        "`cand-8586`（d’Argenville 引文身份／粒度未定）。`cand-9863` 报告只报告绘画展示和人群，场地未定，" 
        "仍不关联圣罗科系列。已映射对象如 `cand-2329`、`cand-1901`、`cand-2569`、`cand-2830`、`cand-4056`、`cand-9874` 沿用原 S3 去向。\n\n"
        "本批相关 S2 关系候选仍留待 S6；未写入 `relations.csv`，未把“possibly/probably”改成确定因果，" 
        "未将年度系列与1770场次合并。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S3 机构复用修正与 S4 圣罗科跨章身份组登记（2026-10-17）\n\n"
        "`cand-7072`（Institute of Arts, Detroit）改为 `same`，复用既有[底特律艺术学院](../units/institutions/detroit-institute-of-arts.md)。"
        "第9章注2给出同一机构的完整名称；第7章两幅 Poussin 画与两处馆藏的逐件配对仍待证。\n\n"
        "新增登记："
        + "；".join(
            f"`{target['candidates'][0]}` → [{target['name_zh']}](../{target['ku']}.md)"
            for target in TARGETS
        )
        + "。年度展览系列、巡行和1770年场次保持分立；Nunzio 报告没有可据以关联圣罗科的场地信息。"
        "`cand-8588`、`cand-10006`、`cand-1904`、`cand-8621`、`cand-8586` 继续保留各自 S3 待证理由。"
        "相关 S2 关系候选留待 S6，本批未新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    planned_accepted = list(accepted_lines)
    for card in sorted(planned_paths):
        insert_at = next(
            (i for i, line in enumerate(planned_accepted)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card),
            next((i for i, line in enumerate(planned_accepted) if line == "claims:"), len(planned_accepted)),
        )
        planned_accepted.insert(insert_at, f"- {card}")
    assert len(planned_accepted) == len(accepted_lines) + len(TARGETS)

    if args.dry_run:
        print("S3 correction dry-run passed: cand-7072 -> same units/institutions/detroit-institute-of-arts")
        print(f"S4 dry-run passed: groups={len(TARGETS)}; candidates={sum(len(t['candidates']) for t in TARGETS)}")
        print("types=event,institution,work,term,archive,person; unresolved venue, works, painter, estimate, and citation kept pending")
        print("formal_relations_added=0; relations.csv unchanged; annual series and dated 1770 occurrence remain separate")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    for target in TARGETS:
        card_path = ROOT / f"04-knowledge/{target['ku']}.md"
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(make_card(target), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: s3_reuse=1; s4_groups={len(TARGETS)}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
