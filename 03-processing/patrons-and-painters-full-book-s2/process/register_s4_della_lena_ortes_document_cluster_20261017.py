from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

GIACOMO_GROUP = "new-person:della-giacomo-lena-0fb3da9b14"
OLD_DELLA_LENA_GROUP = "new-person:della-lena-718aef6568"
ADDITIONAL_GROUP_MEMBERS = {
    "cand-11152": {
        "group": GIACOMO_GROUP,
        "ku_id": "units/persons/giacomo-della-lena",
    },
}

ITEMS = {
    "cand-1387": {
        "group": GIACOMO_GROUP,
        "ku_id": "units/persons/giacomo-della-lena",
        "card_rel": "04-knowledge/units/persons/giacomo-della-lena.md",
        "type": "person",
        "name_zh": "贾科莫·德拉莱纳（Abate Giacomo della Lena）",
        "name_en": "Abate Giacomo della Lena",
        "sub_type": None,
        "sources": [
            {
                "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "location": "第16章；印刷页375；OCR L30–35",
                "span": "lines 30–35; print p. 375",
                "summary": "Haskell 以全名介绍 Abate Giacomo della Lena，并转述其交游、威尼斯副领事任职、出生与死亡信息、兄弟关系、收藏及写给 Ortes 的信；其中部分说法仍属作者报告或转引。",
                "quotes": [
                    ("line 30", "The Abate Giacomo della Lena, for instance, was also on the fringes of scholarship."),
                    ("lines 30–31", "He was a close friend of the Abate G. A. Moschini, an antiquarian who saved many Venetian records from destruction, and he himself wrote an account of the ‘Spoliation of Pictures from Venice’.5"),
                    ("lines 31–32", "Della Lena had been born in Lucca in 1732, but he spent most of his life in Venice, where he acted as Spanish vice-consul and where he died in 1807."),
                    ("lines 31–32", "He probably owed the job to his brother Innocenzo, who was the\n-Spanish Ambassador’s doctor, while another brother, Eusebio, was a friend of Casanova."),
                    ("lines 33–34", "The enthusiasm that della Lena felt for this artist is rationalised in a letter that he wrote to the economist, Giuseppe Maria Ortes.6"),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "location": "第16章；印刷页376；OCR L39",
                "span": "line 39; print p. 376",
                "summary": "Haskell 将 Della Lena 与 Sasso 并列为可能属于同一收藏者圈子的参照人物；该句没有扩展身份或圈子成员范围。",
                "quotes": [
                    ("line 39", "Another collector who took the same line and who may well have belonged to the circle of Sasso and della Lena was a canon ofChioggia Cathedral, Dr GiovanniVianello.1"),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "location": "第二版后记；印刷页410；OCR L207",
                "span": "line 207; print p. 410",
                "summary": "Haskell 在讨论第16、17章相关研究时以 Abate Della Lena 指称同一人物，并再次提到题为 ‘Spoliation of Pictures from Venice’ 的 treatise。",
                "quotes": [
                    ("line 207", "Among these is the Abate Della Lena, whose treatise on the ‘Spoliation of Pictures from Venice’ I published after the appearance of this book.4"),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/22_CHP-22Index.md",
                "location": "书后索引；索引条目 L.csv#44",
                "span": "index entry Lena, Abate Giacomo della",
                "summary": "索引以全名形式汇集第375–376、410页；用于书内定位，不独立补写生平。",
                "quotes": [("index entry", "Lena, Abate Giacomo della, 375-6, 410")],
            },
        ],
        "body": """### 描述

**中文：** 本卡对应书后索引“Lena, Abate Giacomo della”（L.csv#44）及第16章 p.375–376、第二版后记 p.410 的相关提及。第375页以全名介绍这位 Abate；后记第410页用 “Abate Della Lena” 指称其 treatise《Spoliation of Pictures from Venice》的作者。两处所指由相同题名和作者语境互证，故与原仅按姓氏建组的候选合并。卡片保留 Haskell 的转述状态，不把未经原始文献核验的生平和交易细节提升为外部事实。[第16章 p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L30–35）；[第16章 p.376](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L39）；[第二版后记 p.410](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)（L207）；[书后索引](../../../02-sources/02-Markdown/22_CHP-22Index.md)（L1748）

**English:** This card represents the index entry “Lena, Abate Giacomo della” (L.csv#44) and the related references on pp.375–376 of Chapter 16 and p.410 of the postscript. Chapter 16 gives the full name; on p.410 the postscript calls “Abate Della Lena” the author of a treatise titled *Spoliation of Pictures from Venice*. The matching title and authorship context support merging the postscript candidate with the named person in Chapter 16. Reports in Haskell are retained as reports and are not independently verified biography or transaction facts. [Chapter 16, p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md) (L30–35); [Chapter 16, p.376](../../../02-sources/02-Markdown/16_CHP-16_intro.md) (L39); [Postscript, p.410](../../../02-sources/02-Markdown/20_CHP-20Postscript.md) (L207); [Index](../../../02-sources/02-Markdown/22_CHP-22Index.md) (L1748)

### 名称与身份边界

- 对应 `cand-1387`（索引 L.csv#44）与 `cand-11152`（后记 p.410 的 “Abate Della Lena”）；当前 S3 组为 `new-person:della-giacomo-lena-0fb3da9b14`。旧组 token `new-person:della-lena-718aef6568` 只作为被合并组的历史记录保留。
- 合并依据不是姓氏相同：第16章 p.375 明示全名与题名；第20章 p.410 再次给出同一题名并说明作者曾出版该文，形成跨章的作品与作者对应。
- 本卡记录书内身份，不作外部身份核验。副领事职务、生卒年、交易与交游均按 Haskell 的陈述保留其归属和限定。

### 关系与证据

10条直接 `relation_candidate` 留待 S6：

- `st-chp16-p375-della-lena-moschini-friendship-and-records`
- `st-chp16-p375-della-lena-spoliation-account`
- `st-chp16-p375-historian-della-lena-german-dealings`（转述一位未具名十九世纪历史学家的评论）
- `st-chp16-p375-della-lena-life-and-venice-office`
- `st-chp16-p375-della-lena-born-in-lucca`
- `st-chp16-p375-della-lena-brothers-and-casanova`
- `st-chp16-p375-della-lena-private-collection-and-guardi-paintings`
- `st-chp16-p375-della-lena-letter-to-ortes`
- `st-chp20-p410-della-lena-treatise-authorship`
- `st-chp20-p410-della-lena-painter-appreciations`

`st-chp16-p375-della-lena-dealers-and-scholarship` 与 `st-chp16-p375-della-lena-arts-and-sciences-theory` 是评价或观点陈述，保持非关系分类。未具名西班牙大使、32幅 Guardi 绘画集合及 Moschini 身份候选仍按各自 alignment 决定保留待证。本卡未新增正式关系。
""",
    },
    "cand-1389": {
        "group": "new-person:della-innocenzo-lena-7dbf7300d2",
        "ku_id": "units/persons/innocenzo-della-lena",
        "card_rel": "04-knowledge/units/persons/innocenzo-della-lena.md",
        "type": "person",
        "name_zh": "伊诺琴佐·德拉莱纳（Innocenzo della Lena）",
        "name_en": "Innocenzo della Lena",
        "sub_type": None,
        "sources": [
            {
                "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "location": "第16章；印刷页375；OCR L31–32",
                "span": "lines 31–32; print p. 375",
                "summary": "Haskell 称 Innocenzo 是 Giacomo della Lena 的兄弟，并称他担任西班牙大使的医生；大使姓名未给出。",
                "quotes": [
                    ("lines 31–32", "He probably owed the job to his brother Innocenzo, who was the\n-Spanish Ambassador’s doctor, while another brother, Eusebio, was a friend of Casanova."),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/22_CHP-22Index.md",
                "location": "书后索引；索引条目 L.csv#46",
                "span": "index entry Lena, Innocenzo della",
                "summary": "索引提供 Innocenzo 的姓氏形式并定位第375页；不据此补充其他生平。",
                "quotes": [("index entry", "Lena, Innocenzo della, 375")],
            },
        ],
        "body": """### 描述

**中文：** 本卡对应书后索引“Lena, Innocenzo della”（L.csv#46）及第16章 p.375 的 Innocenzo。正文称其为 Giacomo della Lena 的兄弟，并说他是西班牙大使的医生；大使没有具名，因此不将该角色端点扩展成一位已识别人物。除这一书内关系语境外，本卡不补充其他生平。[第16章 p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L31–32）；[书后索引](../../../02-sources/02-Markdown/22_CHP-22Index.md)（L1750）

**English:** This card represents “Lena, Innocenzo della” in the index (L.csv#46) and the reference on p.375 of Chapter 16. The passage calls him a brother of Giacomo della Lena and says he was the doctor of a Spanish Ambassador, whose name is not given. The role does not identify that officeholder. No further biography is added. [Chapter 16, p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md) (L31–32); [Index](../../../02-sources/02-Markdown/22_CHP-22Index.md) (L1750)

### 名称与身份边界

- 对应 S3 候选 `cand-1389`（L.csv#46），保持独立人物组 `new-person:della-innocenzo-lena-7dbf7300d2`。
- 姓氏以同页索引形式定位；不将其与兄弟 Giacomo 或 Eusebio 合并为同一人物。
- 未具名西班牙大使为 `cand-10627`，仍是单独的 `undecided` 人物候选。

### 关系与证据

`st-chp16-p375-della-lena-brothers-and-casanova` 与 `st-chp16-p375-innocenzo-spanish-ambassador-doctor` 均留待 S6；前者保留 Haskell 对 Giacomo 是否因兄弟 Innocenzo 而获任职的限定语气，后者的西班牙大使端点仍未具名。本卡未新增正式关系。
""",
    },
    "cand-1789": {
        "group": "new-person:giuseppe-maria-ortes-7b7bd7d035",
        "ku_id": "units/persons/giuseppe-maria-ortes",
        "card_rel": "04-knowledge/units/persons/giuseppe-maria-ortes.md",
        "type": "person",
        "name_zh": "朱塞佩·玛丽亚·奥尔特斯（Abate Giuseppe Maria Ortes）",
        "name_en": "Abate Giuseppe Maria Ortes",
        "sub_type": None,
        "sources": [
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "location": "第10章注释；印刷页321，注1；OCR L311",
                "span": "line 311; print p. 321, note 1",
                "summary": "Haskell 的注释以 “Abate Ortes” 引述一封1749年致 Francesco Algarotti 的信；此处是书内书目定位。",
                "quotes": [
                    ("line 311", "1 Letter from the Abate Ortes to Francesco Algarotti of 26 September 1749 in Algarotti, XIV, p. 315, and Temanza, p. 87."),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "location": "第16章；印刷页375；OCR L33–34",
                "span": "lines 33–34; print p. 375",
                "summary": "Haskell 以全名 Giuseppe Maria Ortes 称呼经济学家，并说 Giacomo della Lena 写信向他解释对 Guardi 的热忱。",
                "quotes": [
                    ("lines 33–34", "The enthusiasm that della Lena felt for this artist is rationalised in a letter that he wrote to the economist, Giuseppe Maria Ortes.6"),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/22_CHP-22Index.md",
                "location": "书后索引；索引条目 O.csv#24",
                "span": "index entry Ortes, Abate Giuseppe Maria",
                "summary": "索引列出 Abate Giuseppe Maria Ortes，并给出相关页码定位；原Markdown转录的首个定位为‘32m’，本卡保留转录形式，不另行校改页码。",
                "quotes": [("index entry", "Ortes, Abate Giuseppe Maria, 32m, 375")],
            },
        ],
        "body": """### 描述

**中文：** 本卡对应书后索引“O.csv#24”所列 Abate Giuseppe Maria Ortes。第10章注释称“Abate Ortes”，并引述其1749年致 Francesco Algarotti 的信；第16章 p.375 则明确写出经济学家 Giuseppe Maria Ortes。候选记录把这两处与索引条目连在同一书内身份组。索引Markdown将首个定位转录为“32m”；候选行的规范化定位为“321n”。页码转录差异暂保留，不影响 p.375 全名所支持的身份归组。[第10章 p.321 注1](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L311）；[第16章 p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L33–34）；[书后索引](../../../02-sources/02-Markdown/22_CHP-22Index.md)（L2232）

**English:** This card represents Abate Giuseppe Maria Ortes as indexed in O.csv#24. A Chapter 10 note refers to “Abate Ortes” and cites his letter to Francesco Algarotti dated 1749; Chapter 16, p.375, gives the full name Giuseppe Maria Ortes and identifies him as an economist. The candidate record links these references to the same book-local identity group. The index transcription reads “32m,” while the candidate row normalizes the locator as “321n”; the discrepancy is retained and does not affect the identity match supported by the full name on p.375. [Chapter 10, p.321, note 1](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (L311); [Chapter 16, p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md) (L33–34); [Index](../../../02-sources/02-Markdown/22_CHP-22Index.md) (L2232)

### 名称与身份边界

- 对应 S3 候选 `cand-1789`（O.csv#24），保持人物组 `new-person:giuseppe-maria-ortes-7b7bd7d035`。
- 合并书内称谓“Abate Ortes”与 p.375 的全名，依据是全名、职称和索引交叉定位；没有使用外部身份来源。
- 第10章注释的信件引文提供书目定位，不由本卡认定亲自查阅了信件原件或 Algarotti 卷册。

### 关系与证据

`st-chp16-p375-della-lena-letter-to-ortes` 是与 Giacomo della Lena 的一条直接关系候选，留待 S6。第10章注释记录的书目信息不另行写成正式关系。本卡未新增正式关系。
""",
    },
    "cand-10622": {
        "group": "archive-group-8b6fed618f62",
        "ku_id": "units/archives/della-lena-spoliation-of-pictures-from-venice",
        "card_rel": "04-knowledge/units/archives/della-lena-spoliation-of-pictures-from-venice.md",
        "type": "archive",
        "name_zh": "《威尼斯绘画劫掠记述》（The Spoliation of Pictures from Venice, as cited by Haskell）",
        "name_en": "The Spoliation of Pictures from Venice (as cited by Haskell)",
        "sub_type": "treatise",
        "sources": [
            {
                "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "location": "第16章；印刷页375；OCR L30–31",
                "span": "lines 30–31; print p. 375",
                "summary": "Haskell 称 Abate Giacomo della Lena 写有题为 ‘Spoliation of Pictures from Venice’ 的 account，并概述其涉及从威尼斯移走绘画的收藏者。",
                "quotes": [
                    ("line 30", "he himself wrote an account of the ‘Spoliation of Pictures from Venice’.5"),
                    ("lines 30–31", "This deals with the activities of various collectors who had removed pictures from the city, ranging from Cardinal Leopold de’ Medici to his own contemporaries."),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "location": "第二版后记；印刷页410；OCR L207、L279",
                "span": "line 207 and footnote at line 279; print p. 410",
                "summary": "后记称 Della Lena 的同题 treatise 曾由 Haskell 在本书初版之后出版；脚注4仅给出 Haskell, 1967 的简略引文。该文本及其完整出版信息未独立核验。",
                "quotes": [
                    ("line 207", "Among these is the Abate Della Lena, whose treatise on the ‘Spoliation of Pictures from Venice’ I published after the appearance of this book.4"),
                    ("line 279", "4 Haskell, 1967."),
                ],
            },
            {
                "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "location": "第16章注5；印刷页375；OCR L80",
                "span": "line 80; print p. 375, note 5",
                "summary": "同一注释报告 Biblioteca Correr 的 MSS. Raccolta Cicogna 3006/9 及其他版本，并提到 Haskell 1967；此定位未独立查验。",
                "quotes": [
                    ("line 80", "5 Biblioteca Correr, Venice—MSS. Raccolta Cicogna 3006/9 and other versions. See Haskell, 1967."),
                ],
            },
        ],
        "body": """### 描述

**中文：** 本卡记录 Haskell 在第16章 p.375 称作 “Spoliation of Pictures from Venice” 的 treatise/account。第20章后记 p.410 再次以相同题名提及该文本，并称 Haskell 在本书初版之后将其出版；脚注只写“Haskell, 1967”。第16章注5另报告 Biblioteca Correr 的 MSS. Raccolta Cicogna 3006/9 及其他版本。本文、手稿版本和简略引文均未在本轮独立查阅；英文题名按 Haskell 的书内形式保留，中文为项目工作译名。[第16章 p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L30–31、注5 L80）；[第二版后记 p.410](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)（L207、注4 L279）

**English:** This card records the treatise/account that Haskell calls “Spoliation of Pictures from Venice” on p.375 of Chapter 16. The postscript on p.410 refers to a treatise with the same title and says Haskell published it after the first appearance of the book; footnote 4 gives only “Haskell, 1967.” Note 5 in Chapter 16 separately reports Biblioteca Correr, MSS. Raccolta Cicogna 3006/9 and other versions. Neither the text, the manuscript witnesses, nor the abbreviated citation was independently consulted in this pass. The English title follows Haskell’s wording; the Chinese title is a project working translation. [Chapter 16, p.375](../../../02-sources/02-Markdown/16_CHP-16_intro.md) (L30–31, note 5 L80); [Postscript, p.410](../../../02-sources/02-Markdown/20_CHP-20Postscript.md) (L207, note 4 L279)

### 文献身份与范围

- 对应候选 `cand-10622`，保持 `archive-group-8b6fed618f62`；登记的是书内所指的 treatise/account，不是某个已核验的单件手稿或确定出版版本。
- 该标题由第16章正文和第20章后记两处相同题名支持。候选 `cand-10625` 单独记录注5所称的 Biblioteca Correr 手稿定位组；两卡分别表示文本与被报告的物质见证，不把其他版本逐一假定为已识别对象。
- 书内引述的内容、出版信息与手稿定位均未独立核验；不据此补写作者之外的书目字段、出版日期或完整版本关系。

### 关系与证据

3条直接 S2 `relation_candidate` 留待 S6：

- `st-chp16-p375-della-lena-spoliation-account`
- `st-chp20-p410-della-lena-treatise-authorship`
- `st-chp20-p410-della-lena-treatise-content`（保留为对文献内容的来源转述，不扩展未具名人物或作品端点）

本卡未新增正式关系。
""",
    },
    "cand-10625": {
        "group": "archive-group-cfe23b044720",
        "ku_id": "units/archives/correr-cicogna-3006-9-della-lena-account",
        "card_rel": "04-knowledge/units/archives/correr-cicogna-3006-9-della-lena-account.md",
        "type": "archive",
        "name_zh": "科雷尔图书馆 Cicogna 3006/9 等手稿版本（Biblioteca Correr MSS. Raccolta Cicogna 3006/9 and other versions）",
        "name_en": "Biblioteca Correr Manuscript References (MSS. Raccolta Cicogna 3006/9 and Other Versions)",
        "sub_type": "manuscript reference",
        "sources": [
            {
                "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
                "location": "第16章注5；印刷页375；OCR L80",
                "span": "line 80; print p. 375, note 5",
                "summary": "Haskell 的注5将 Biblioteca Correr、MSS. Raccolta Cicogna 3006/9 和 ‘other versions’ 列为 Della Lena account 的手稿定位，并引用 Haskell 1967；具体馆藏对象与层级未核验。",
                "quotes": [
                    ("line 80", "5 Biblioteca Correr, Venice—MSS. Raccolta Cicogna 3006/9 and other versions. See Haskell, 1967."),
                ],
            },
        ],
        "body": """### 描述

**中文：** 本卡仅记录 Haskell 第16章 p.375 注5 对 Della Lena account 手稿版本的定位：“Biblioteca Correr, Venice—MSS. Raccolta Cicogna 3006/9 and other versions.” 注释还引用“Haskell, 1967”。本轮未查阅 Correr 目录、馆藏层级、MSS. Raccolta Cicogna 3006/9 原件或其他版本；“other versions”没有逐项列出，不能据此声称已识别一组封闭文献清单。[第16章 p.375 注5](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L80）

**English:** This card records only the manuscript locator that Haskell gives in note 5 on p.375 of Chapter 16: “Biblioteca Correr, Venice—MSS. Raccolta Cicogna 3006/9 and other versions.” The note also cites “Haskell, 1967.” The Correr catalogue, archival hierarchy, manuscript, and other versions were not consulted in this pass. Since “other versions” are not itemized, the card does not claim a closed inventory of identified documents. [Chapter 16, p.375, note 5](../../../02-sources/02-Markdown/16_CHP-16_intro.md) (L80)

### 档案身份与范围

- 对应 S3 候选 `cand-10625`，保持 `archive-group-cfe23b044720`。此卡表示 Haskell 的一个书目/档案定位组，不表示已经核验的单一手稿实物。
- 与 `cand-10622` 的 treatise 文本分开登记：本卡保存注5所报的物质见证定位，另一卡记录正文与后记所指的文献文本。
- 保管机构端点 `cand-8262` 已复用 `units/institutions/correr-library`；本轮仅保持 S2 关系候选，不从引用自动生成正式关系。

### 关系与证据

`st-chp16-p375-note5-della-lena-account-manuscript` 是该书目/档案定位组与 Biblioteca Correr 之间的直接关系候选，留待 S6。未新增正式关系。
""",
    },
}

EXPECTED_STATEMENTS = {
    "cand-1387": {
        "st-chp16-p375-della-lena-moschini-friendship-and-records": True,
        "st-chp16-p375-della-lena-spoliation-account": True,
        "st-chp16-p375-historian-della-lena-german-dealings": True,
        "st-chp16-p375-della-lena-life-and-venice-office": True,
        "st-chp16-p375-della-lena-born-in-lucca": True,
        "st-chp16-p375-della-lena-brothers-and-casanova": True,
        "st-chp16-p375-della-lena-private-collection-and-guardi-paintings": True,
        "st-chp16-p375-della-lena-letter-to-ortes": True,
        "st-chp16-p375-della-lena-dealers-and-scholarship": False,
        "st-chp16-p375-della-lena-arts-and-sciences-theory": False,
    },
    "cand-11152": {
        "st-chp20-p410-della-lena-treatise-authorship": True,
        "st-chp20-p410-della-lena-painter-appreciations": True,
    },
    "cand-1389": {
        "st-chp16-p375-della-lena-brothers-and-casanova": True,
        "st-chp16-p375-innocenzo-spanish-ambassador-doctor": True,
    },
    "cand-1789": {"st-chp16-p375-della-lena-letter-to-ortes": True},
    "cand-10622": {
        "st-chp16-p375-della-lena-spoliation-account": True,
        "st-chp20-p410-della-lena-treatise-authorship": True,
        "st-chp20-p410-della-lena-treatise-content": True,
    },
    "cand-10625": {"st-chp16-p375-note5-della-lena-account-manuscript": True},
}


def group_from_note(note: str) -> str:
    return sync.get_group(note)


def make_card(item: dict) -> str:
    source_rows = []
    for source in item["sources"]:
        source_rows.append({
            "citation": BOOK,
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in source["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source["source_file"],
                "source_span": source["span"],
            },
        })
    frontmatter = {
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": item["type"],
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    if item["sub_type"]:
        frontmatter["sub_type"] = item["sub_type"]
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{fm}---\n\n## 内容\n\n{item['body']}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the cross-chapter Della Lena identity and register the associated S4 person/archive groups."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert set(ITEMS).issubset(candidate_by_id)
    assert set(ITEMS).issubset(decisions)
    assert candidate_by_id["cand-1387"]["suggested_type"] == "person"
    assert candidate_by_id["cand-11152"]["suggested_type"] == "person"
    assert candidate_by_id["cand-1389"]["suggested_type"] == "person"
    assert candidate_by_id["cand-1789"]["suggested_type"] == "person"
    assert candidate_by_id["cand-10622"]["suggested_type"] == "archive"
    assert candidate_by_id["cand-10625"]["suggested_type"] == "archive"

    # Verify the cross-chapter name/work link, source text, and original group history before planning any write.
    current = decisions["cand-1387"]
    moved = decisions["cand-11152"]
    assert current["decision"] == moved["decision"] == "new"
    assert not current.get("ku_id") and not moved.get("ku_id")
    assert group_from_note(current.get("resolution_note", "")) == GIACOMO_GROUP
    assert group_from_note(moved.get("resolution_note", "")) == OLD_DELLA_LENA_GROUP

    source_files = {
        "02-sources/02-Markdown/16_CHP-16_intro.md",
        "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "02-sources/02-Markdown/22_CHP-22Index.md",
    }
    source_texts = {
        rel: " ".join((ROOT / rel).read_text(encoding="utf-8-sig").split())
        for rel in source_files
    }
    for item in ITEMS.values():
        for source in item["sources"]:
            text = source_texts[source["source_file"]]
            for _, quote in source["quotes"]:
                assert " ".join(quote.split()) in text, (source["location"], quote)
    assert "The Abate Giacomo della Lena" in source_texts["02-sources/02-Markdown/16_CHP-16_intro.md"]
    assert "Spoliation of Pictures from Venice" in source_texts["02-sources/02-Markdown/20_CHP-20Postscript.md"]
    assert "Lena, Abate Giacomo della, 375-6, 410" in source_texts["02-sources/02-Markdown/22_CHP-22Index.md"]
    assert "Lena, Innocenzo della, 375" in source_texts["02-sources/02-Markdown/22_CHP-22Index.md"]

    statements = sync.load_statements()
    statement_by_id = {row["statement_id"]: row for row in statements}
    for candidate_id, expected in EXPECTED_STATEMENTS.items():
        direct = {
            row["statement_id"]: row
            for row in statements
            if candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        }
        assert set(direct) == set(expected), (candidate_id, sorted(set(direct) ^ set(expected)))
        for statement_id, relation_candidate in expected.items():
            qualifiers = direct[statement_id].get("qualifiers") or {}
            assert qualifiers.get("relation_candidate") is relation_candidate, statement_id
    for statement_id in (
        "st-chp16-p375-della-lena-spoliation-account",
        "st-chp20-p410-della-lena-treatise-authorship",
    ):
        assert statement_by_id[statement_id]["subject_candidate_id"] in {"cand-1387", "cand-11152"}
        assert statement_by_id[statement_id]["object_candidate_id"] == "cand-10622"

    # Keep the former standalone group token and its original reason as history, while moving the current group.
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    target = planned_by_id["cand-11152"]
    old_marker = f"group={OLD_DELLA_LENA_GROUP};"
    new_marker = f"prior_s3_group_token={OLD_DELLA_LENA_GROUP}; group={GIACOMO_GROUP};"
    assert old_marker in target["resolution_note"]
    target["resolution_note"] = target["resolution_note"].replace(old_marker, new_marker, 1)
    target["resolution_note"] += (
        " S3 cross-chapter identity correction 2026-10-17: merged with cand-1387 after source comparison. "
        "Chapter 16 p.375 names Abate Giacomo della Lena as author of an account titled ‘Spoliation of Pictures from Venice’; "
        "the postscript p.410 calls Abate Della Lena the author of a treatise with the same title and reports its later publication. "
        "The identical work title and authorship context establish the referent beyond surname similarity. "
        "The prior group and its original name-anchor reasoning are retained above as history, not current identity evidence."
    )
    planned_by_id["cand-1387"]["resolution_note"] += (
        " S3 cross-chapter group extension 2026-10-17: includes cand-11152 from the p.410 postscript; "
        "the matching ‘Spoliation of Pictures from Venice’ authorship context is recorded in cand-11152's history."
    )
    planned_by_id["cand-1789"]["resolution_note"] += (
        " S3 source check 2026-10-17: Chapter 10 note 1 uses ‘Abate Ortes’; Chapter 16 p.375 gives the full name Giuseppe Maria Ortes; "
        "the index Markdown transcribes the first locator as ‘32m’, while the candidate record normalizes it as ‘321n’. "
        "The locator discrepancy remains open; the full name and cross-reference support this source-local person group."
    )
    planned_by_id["cand-10622"]["resolution_note"] += (
        " S3 cross-chapter source check 2026-10-17: p.375 body and p.410 postscript report the same treatise title and Della Lena authorship. "
        "This group represents the cited textual work; cand-10625 separately represents the p.375 note's manuscript locator group. "
        "Neither the text nor the manuscript witnesses were independently consulted."
    )
    planned_by_id["cand-10625"]["resolution_note"] += (
        " S3 source check 2026-10-17: retained as the separately cited Biblioteca Correr manuscript-reference group ‘MSS. Raccolta Cicogna 3006/9 and other versions’; "
        "the individual witnesses and archival hierarchy remain unchecked. It is distinct from cand-10622's source-cited treatise text."
    )
    assert group_from_note(planned_by_id["cand-11152"]["resolution_note"]) == GIACOMO_GROUP
    assert group_from_note(planned_by_id["cand-1387"]["resolution_note"]) == GIACOMO_GROUP

    # Map every ready new group to one KU; unrelated undecided candidates and existing reuse targets stay untouched.
    for candidate_id, item in ITEMS.items():
        row = planned_by_id[candidate_id]
        assert row["decision"] == "new" and not row.get("ku_id"), candidate_id
        assert group_from_note(row.get("resolution_note", "")) == item["group"], candidate_id
    for candidate_id, item in ITEMS.items():
        members = [
            row for row in planned_alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and group_from_note(row.get("resolution_note", "")) == item["group"]
        ]
        assert members and all(not row.get("ku_id") for row in members), item["group"]
        planned_by_id[candidate_id]["ku_id"] = item["ku_id"]
        planned_by_id[candidate_id]["resolution_note"] += (
            f" S4 registration: mapped current group {item['group']} to {item['ku_id']}."
        )
    for candidate_id, mapping in ADDITIONAL_GROUP_MEMBERS.items():
        row = planned_by_id[candidate_id]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert group_from_note(row.get("resolution_note", "")) == mapping["group"]
        row["ku_id"] = mapping["ku_id"]
        row["resolution_note"] += (
            f" S4 registration: mapped current group {mapping['group']} to {mapping['ku_id']}."
        )
    giacomo_members = [
        row["candidate_id"] for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and group_from_note(row.get("resolution_note", "")) == GIACOMO_GROUP
    ]
    assert set(giacomo_members) == {"cand-1387", "cand-11152"}

    planned_manifest = list(manifest)
    existing_ids = {row.get("ku_id") for row in manifest}
    existing_cards = {row.get("card_path") for row in manifest}
    for item in ITEMS.values():
        assert item["ku_id"] not in existing_ids
        assert item["card_rel"] not in existing_cards
        assert not (ROOT / item["card_rel"]).exists()
        assert item["card_rel"] not in accepted
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": item["type"],
            "canonical_name": item["name_zh"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })
    assert len({item["ku_id"] for item in ITEMS.values()}) == len(ITEMS)

    accepted_lines = accepted.splitlines()
    for item in ITEMS.values():
        card_rel = item["card_rel"]
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card_rel}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3–S4：Della Lena 跨章人物组及相关文献端点（2026-10-17）\n\n"
        f"S3 将 `cand-11152`（后记 p.410 “Abate Della Lena”）并入 `cand-1387` 的 `{GIACOMO_GROUP}`。"
        "身份依据是第16章 p.375 的全名、题名与作者关系，以及后记 p.410 对同一题名 treatise 的再次指称；不是姓氏匹配。"
        f"原组 `{OLD_DELLA_LENA_GROUP}` 及其原始名称锚点理由保留在 `cand-11152` alignment 历史字段。"
        "另核对 Ortes：第10章注释中的 ‘Abate Ortes’ 与第16章 p.375 的 ‘Giuseppe Maria Ortes’ 由书后索引交叉定位；索引Markdown首个定位转录为 ‘32m’，候选记录为 ‘321n’，页码差异保留待核。"
        "S3 明确保留：`cand-10623`（32幅 Guardi 绘画集合）、`cand-10627`（未具名西班牙大使）与 `cand-1709`（Moschini 姓名形式不足）为 `undecided`；未知历史学家不另造人物候选。"
        "`cand-1454` Lucca、`cand-2719` Venice、`cand-1239` Francesco Guardi 与 `cand-8262` Biblioteca Correr 分别复用已有 KU。"
        "新登记5个 KU：人物 Giacomo della Lena（`cand-1387`、`cand-11152` 同组）、Innocenzo della Lena（`cand-1389`）、Giuseppe Maria Ortes（`cand-1789`）；archive 文献文本（`cand-10622`）与 Correr 手稿定位组（`cand-10625`）各自保留独立身份。"
        "所有直接关系候选及文献内容断言留待 S6；未改写 `relations.csv`。Giacomo 的两条评价/观点陈述维持非关系分类。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S3–S4 复核：Della Lena 与关联人物/文献端点（2026-10-17）\n\n"
        "`cand-11152` 已并入 `cand-1387` 的 Giacomo della Lena 人物组：第16章 p.375 与后记 p.410 对同一题名及作者的明确对应，排除了只凭姓氏合并。"
        "Ortes 由第10章注释称谓与第16章全名、索引交叉归为同一书内人物；原索引首个页码转录差异记入卡片和 alignment。"
        "Giacomo、Innocenzo、Ortes、同题 treatise 文本、Correr 手稿定位组均已映射到各自 KU；旧组和新身份判断均保留于 alignment。"
        "32幅 Guardi 作品集合、未具名西班牙大使和 Moschini 的身份候选继续为 `undecided`；Lucca、Venice、Francesco Guardi、Biblioteca Correr 复用既有 KU。"
        "本批关系候选仍待 S6，未新增正式关系。"
        f"S3 new 共{sync.fmt(totals['new_candidates'])}条候选/{sync.fmt(totals['new_groups'])}组；"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    if args.dry_run:
        print("Della Lena S3 group correction and S4 registration dry-run passed")
        print("cross-chapter authorship match verified: cand-1387 + cand-11152 -> one Giacomo person KU")
        print("Innocenzo, Ortes, cited treatise text, and Correr manuscript-reference group map to four additional KUs")
        print("5 KUs planned for 6 candidate mappings; all direct relationship candidates remain pending S6")
        print("undecided collection, unnamed ambassador, and Moschini identity remain unchanged")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}")
        print(f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; new alignment rows pending={sync.fmt(totals['pending_members'] + 15)}")
        print("no files changed")
        return 0

    for item in ITEMS.values():
        card_path = ROOT / item["card_rel"]
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(make_card(item), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: five KUs registered; manifest={len(planned_manifest)}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
