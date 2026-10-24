#!/usr/bin/env python3
"""Guarded S2/S3/S4/S6 table and card write for the Poussin/Louvre endpoint batch."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
RECOVERY = ROOT / "06-runtime" / "recovery" / "poussin-arcadian-louvre-s4-s6-20261025" / "original"

EXPECTED = {
    "entity-candidates.csv": "f77200fd64a3054c32addd39d6c5150a516ca6962247dcf411516195168e56da",
    "alignment.csv": "8cd964da75fb52e570cbfa7342aa3bfa4047e8d03db17e574f94bbf963c886cc",
    "mentions.csv": "29b1a0f660aff2daab1032f67805b809ec174f65c2b7c6f3cbe488deb843a22c",
    "book-statements.jsonl": "9ca8bebecd491758de4226067ff6ff65da1c78ec480c6483b1a3690c2aeeaac4",
    "ku-manifest.csv": "66bb2fa4a17b7ae88bcf3ce90a3b900394a3225ac26a3fc731c8b8dae214e15a",
    "accepted.yml": "bf7f922ede5f8df80dd039e1287daa1df3bed048e093544a1b73158345ea54a4",
    "relations.csv": "7f969032a9a4c073d4549eccb77ee51fe4d28aadbac7984efb4bbd363b5d0433",
}

KU_ROWS = [
    ("cand-1994", "units/works/arcadian-shepherds-first-version-poussin", "work", "《阿卡迪亚牧人》（第一版）", "The Arcadian Shepherds, first version", "04-knowledge/units/works/arcadian-shepherds-first-version-poussin.md", "sg3-work-arcadian-shepherds-first-version-poussin"),
    ("cand-1995", "units/works/arcadian-shepherds-louvre-second-version-poussin", "work", "《死亡前的幸福》（《阿卡迪亚牧人》第二版）", "Happiness subject to Death / The Arcadian Shepherds, second version", "04-knowledge/units/works/arcadian-shepherds-louvre-second-version-poussin.md", "sg3-work-arcadian-shepherds-louvre-second-version-poussin"),
    ("cand-2009", "units/works/king-midas-washing-face-pactolus-poussin", "work", "《迈达斯王在帕克托洛斯河中洗脸》", "King Midas washing his Face in the River Pactolus", "04-knowledge/units/works/king-midas-washing-face-pactolus-poussin.md", "sg3-work-king-midas-washing-face-pactolus-poussin"),
    ("cand-11667", "units/works/poussin-early-work-pair-massimi-passage", "work", "普桑早期两件作品组", "Pair of early works by Nicolas Poussin", "04-knowledge/units/works/poussin-early-work-pair-massimi-passage.md", "sg3-work-poussin-early-pair-massimi-passage"),
    ("cand-1450", "units/places/louvre-historical-site", "place", "卢浮宫历史地点", "Historical Louvre site", "04-knowledge/units/places/louvre-historical-site.md", "sg3-place-cand-1450"),
]

CARDS = {
    "units/works/arcadian-shepherds-first-version-poussin": """---
title: 《阿卡迪亚牧人》（第一版）（The Arcadian Shepherds, first version）
name_en: The Arcadian Shepherds, first version
type: work
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 4, p. 117.'
  location: 第4章，印刷页117，来源转录L212–213
  sentence_summary: Haskell 将第一版《阿卡迪亚牧人》列为普桑早期两件作品组的一员；本记录不把它与第2章注释中所述卢浮宫版本合并。
  original_quotes:
  - source_span: lines 212–213; print p. 117
    text: the first version of the Arcadian Shepherds
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/04_CHP-4_sec_ii.md
    source_span: lines 212–213; print p. 117
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 2, p. 57 n. 3.'
  location: 第2章，印刷页57注3，来源转录L242；PDF物理页46
  sentence_summary: Haskell脚注称《阿卡迪亚牧人》在卢浮宫，并转述Mahon提出的断代意见；本卡将该作品与第4章明确称为第一版的作品区分。
  original_quotes:
  - source_span: line 242; print p. 57 n. 3
    text: The Arcadian Shepherds in the Louvre
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/02_CHP-2_sec_iv.md
    source_span: line 242; print p. 57 n. 3
created: '2026-10-25'
updated: '2026-10-25'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025
---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第4章明确称为“第一版”的《阿卡迪亚牧人》。它是书中所说普桑早期两件作品组的一员；第2章注释另称卢浮宫中的《阿卡迪亚牧人》，并由索引区分为第二版。两者不合并。本卡只记录来源中的版本区分，不据此确认外部实物、现藏地点、共同原始赞助人或流传路径。[第4章 p.117](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L212–213）

**English:** This card records the *Arcadian Shepherds* that Haskell explicitly calls the “first version” in chapter 4. It is one member of the pair of early Poussin works discussed there. Chapter 2 separately mentions an *Arcadian Shepherds* at the Louvre, indexed as the second version; the two are not merged. This card preserves the book’s version distinction without identifying an external object, current location, common original patron, or provenance.[Chapter 4, p. 117](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md) (L212–213)

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性暂题 | 《阿卡迪亚牧人》（第一版） / The Arcadian Shepherds, first version | 第4章 p.117，L213；索引 P.csv#197；S1 |
| 版本性质 | 哈斯克尔明确称其为第一版 | 第4章 p.117，L213；S1 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 对象性质 | 来源可辨认的单件作品；不等同于第2章所述第二版 | 第2章 p.57 n.3；第4章 p.117；S1–S2 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|

### 关系候选入口

[普桑早期作品组、版本区分及逐项S2/S3/S4/S6裁决](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025)
""",
    "units/works/arcadian-shepherds-louvre-second-version-poussin": """---
title: 《死亡前的幸福》（《阿卡迪亚牧人》第二版）（Happiness subject to Death / The Arcadian Shepherds, second version）
name_en: Happiness subject to Death / The Arcadian Shepherds, second version
type: work
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 2, p. 57 n. 3.'
  location: 第2章，印刷页57正文L175–176及注3 L242；PDF物理页46
  sentence_summary: 正文以括号将“Happiness subject to Death”与“The Arcadian Shepherds”并列为同一题名表达；注3称《阿卡迪亚牧人》在卢浮宫，并报告Mahon提出约1640年的风格断代建议，而通常年代为1650–55。
  original_quotes:
  - source_span: lines 175–176; print p. 57
    text: Happiness subject to Death
  - source_span: line 242; print p. 57 n. 3
    text: The Arcadian Shepherds in the Louvre
  - source_span: line 242; print p. 57 n. 3
    text: on stylistic grounds The Arcadian Shepherds may be dated 1640 instead of 1650-5
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/02_CHP-2_sec_iv.md
    source_span: lines 175–176 and 242; print p. 57, n. 3
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 4, p. 117.'
  location: 第4章，印刷页117，来源转录L212–213
  sentence_summary: Haskell将第一版《阿卡迪亚牧人》列入普桑早期两件作品组；本卡对应索引区分的第2章p.57第二版。
  original_quotes:
  - source_span: lines 212–213; print p. 117
    text: the first version of the Arcadian Shepherds
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/04_CHP-4_sec_ii.md
    source_span: lines 212–213; print p. 117
created: '2026-10-25'
updated: '2026-10-25'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025
---

## 内容

### 描述

**中文：** 本卡对应第2章 p.57 的《阿卡迪亚牧人》版本：哈斯克尔将“Happiness subject to Death”列为括号中的另一题名，脚注称该作品在卢浮宫；普桑索引 P.csv#198 将此页所指作品标为第二版。第4章 p.117 的“第一版”保持为另一知识元。注3报告 Denis Mahon 的约1640年风格断代提议，并称通常年代为1650–55；这只是被转述的意见，不是已确定年代。来源所报卢浮宫位置不表示现今保管状态，也未作外部实物身份核验。[第2章 p.57](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L175–176，L242）

**English:** This card represents the version indexed at *Patrons and Painters* p. 57: Haskell gives “Happiness subject to Death” with “The Arcadian Shepherds” in parentheses, and the footnote reports the work at the Louvre. The Poussin index entry P.csv#198 identifies this page reference as the second version. The “first version” named in chapter 4 remains a separate unit. Note 3 reports Denis Mahon’s c. 1640 stylistic dating proposal against the usual 1650–55 dating; this remains an attributed proposal, not a settled date. The Louvre wording is a source report, not a verified present-day holding or external object identification.[Chapter 2, p. 57](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md) (L175–176, L242)

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性暂题 | 《死亡前的幸福》（《阿卡迪亚牧人》第二版） / Happiness subject to Death / The Arcadian Shepherds, second version | 第2章 p.57 L176；P.csv#198；S1 |
| 来源别题 | Happiness subject to Death；The Arcadian Shepherds | 第2章 p.57 L176，括号中的来源题名表达；S1 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 版本性质 | 索引将p.57所指版本标为第二版；与p.117第一版分开 | P.csv#198；第4章 p.117 L213；S1–S2 |
| 断代提议 | Haskell转述Mahon基于风格提出约1640年；同注称通常年代为1650–55。提议未定，不存作确定创作年代。 | 第2章 p.57 n.3 L242；S1；statement st-chp2-seciv-l190-245-arcadian-shepherds-date-proposal |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|

### 关系候选入口

[普桑早期作品组、版本区分及逐项S2/S3/S4/S6裁决](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025)
""",
    "units/works/king-midas-washing-face-pactolus-poussin": """---
title: 《迈达斯王在帕克托洛斯河中洗脸》（King Midas washing his Face in the River Pactolus）
name_en: King Midas washing his Face in the River Pactolus
type: work
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 4, p. 117.'
  location: 第4章，印刷页117，来源转录L212–213
  sentence_summary: Haskell在普桑早期两件作品组中点名此作；来源将其称为普桑的早期作品，但没有给出当前地点或明确年代。
  original_quotes:
  - source_span: lines 212–213; print p. 117
    text: the King Midas washing his Face in the River Pactolus
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/04_CHP-4_sec_ii.md
    source_span: lines 212–213; print p. 117
created: '2026-10-25'
updated: '2026-10-25'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025
---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第4章列入普桑早期两件作品组的《迈达斯王在帕克托洛斯河中洗脸》。这是依来源描述形成的中文暂题；不由题名推定媒介、年代、现存状况或当前馆藏，也不将它与一件已知实物强行等同。[第4章 p.117](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L212–213）

**English:** This card records *King Midas washing his Face in the River Pactolus*, which Haskell names as one of the pair of early Poussin works in chapter 4. The Chinese title is descriptive. The title does not establish medium, date, survival, present collection, or identity with a particular external object.[Chapter 4, p. 117](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md) (L212–213)

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性暂题 | 《迈达斯王在帕克托洛斯河中洗脸》 / King Midas washing his Face in the River Pactolus | 第4章 p.117 L212–213；P.csv#212；S1 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 对象性质 | 来源点名的单件作品；列入两件普桑早期作品组 | 第4章 p.117 L212–213；S1 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|

### 关系候选入口

[普桑早期作品组、版本区分及逐项S2/S3/S4/S6裁决](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025)
""",
    "units/works/poussin-early-work-pair-massimi-passage": """---
title: 普桑早期两件作品组（Pair of early works by Nicolas Poussin）
name_en: Pair of early works by Nicolas Poussin
type: work
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 4, p. 117.'
  location: 第4章，印刷页117，来源转录L211–214
  sentence_summary: Haskell称之为普桑早期两件作品的一组，列出《迈达斯王在帕克托洛斯河中洗脸》和第一版《阿卡迪亚牧人》。他只说Massimi“may well have”购得此组，并明确称继承人来源“there is no direct evidence”。
  original_quotes:
  - source_span: line 212; print p. 117
    text: a pair of that painter’s most beautiful early works
  - source_span: lines 212–213; print p. 117
    text: the King Midas washing his Face in the River Pactolus
  - source_span: line 213; print p. 117
    text: the first version of the Arcadian Shepherds
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/04_CHP-4_sec_ii.md
    source_span: lines 211–214; print p. 117
created: '2026-10-25'
updated: '2026-10-25'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025
---

## 内容

### 描述

**中文：** 本卡只表示第4章中被并称的一组作品：普桑《迈达斯王在帕克托洛斯河中洗脸》与第一版《阿卡迪亚牧人》。它是书内的组合对象，不是第三件绘画；并称不证明两画为pendants、同一原始赞助项目或具有可靠的共同流传史。哈斯克尔认为Massimi可能在此时购得这组作品，但仍保留“可能”语气；所谓Cassiano继承人来源被明确说明没有直接证据。[第4章 p.117](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L211–214）

**English:** This unit records only the pair discussed together in chapter 4: Poussin’s *King Midas washing his Face in the River Pactolus* and the first version of the *Arcadian Shepherds*. It is a source-defined group, not a third painting. Their pairing does not establish pendant status, a common original commission, or a secure shared provenance. Haskell says Massimi may have acquired the pair at this time; the possible source among Cassiano’s heirs is expressly said to lack direct evidence.[Chapter 4, p. 117](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md) (L211–214)

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性暂题 | 普桑早期两件作品组 / Pair of early works by Nicolas Poussin | 第4章 p.117 L212–213；来源未给此组正式题名；S1 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 对象性质 | 两件具名作品的来源界定组合，不是单件绘画 | 第4章 p.117 L212–213；S1 |
| 组合成员 | 《迈达斯王在帕克托洛斯河中洗脸》；第一版《阿卡迪亚牧人》 | 第4章 p.117 L212–213；S1 |
| 组内关系边界 | 并称不证明pendant关系、共同原始赞助人或可靠共同流传史 | 第4章 p.117 L211–214；S1；候选说明 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|

### 关系候选入口

[普桑早期作品组、版本区分及逐项S2/S3/S4/S6裁决](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025)
""",
    "units/places/louvre-historical-site": """---
title: 卢浮宫历史地点（Historical Louvre site）
name_en: Historical Louvre site
type: place
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 2, p. 44.'
  location: 第2章，印刷页44，来源转录L8–9
  sentence_summary: Haskell称1625年随Francesco Barberini出使巴黎的随员曾专程参观卢浮宫艺术珍藏。
  original_quotes:
  - source_span: line 9; print p. 44
    text: art treasures of the Louvre
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/02_CHP-2_sec_iv.md
    source_span: lines 8–9; print p. 44
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 2, p. 57 n. 3.'
  location: 第2章，印刷页57注3，来源转录L242
  sentence_summary: 脚注以卢浮宫作为《阿卡迪亚牧人》第二版的书内地点报告；本卡仅保留这项历史来源定位。
  original_quotes:
  - source_span: line 242; print p. 57 n. 3
    text: The Arcadian Shepherds in the Louvre
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/02_CHP-2_sec_iv.md
    source_span: line 242; print p. 57 n. 3
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 6, p. 153.'
  location: 第6章，印刷页153，来源转录L84
  sentence_summary: Haskell称Bernini等建筑师曾受邀为卢浮宫重建方案提供设计。
  original_quotes:
  - source_span: line 84; print p. 153
    text: designs for the rebuilding of the Louvre
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/06_CHP-6_sec_i.md
    source_span: line 84; print p. 153
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 7, p. 174.'
  location: 第7章，印刷页174，来源转录L47–49
  sentence_summary: Haskell叙述Marie de Medici于1601年抵达巴黎时对卢浮宫的居住环境不满；这是对同一历史地点的评价，不代表现代博物馆机构。
  original_quotes:
  - source_span: line 48; print p. 174
    text: she was horrified by the Louvre
  evidence_ref:
    doc_id: haskell-1980-rev-ed
    source_file: 02-sources/02-Markdown/07_CHP-7_sec_i.md
    source_span: lines 47–49; print p. 174
created: '2026-10-25'
updated: '2026-10-25'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025
---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔书中作为历史宫址、艺术珍藏地点及建筑改造对象出现的卢浮宫地点：1625年巴黎使团参观其艺术珍藏，1601年Marie de Medici评价其宫廷居住环境，第6章又叙述卢浮宫重建设计。第2章注3将《阿卡迪亚牧人》第二版定位于卢浮宫。这里表示来源中的历史物理地点，不等同于现代“卢浮宫博物馆”机构卡，也不声称任何作品的当前馆藏或现状。[第2章 p.44](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L8–9）；[第6章 p.153](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L84）；[第7章 p.174](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L47–49）

**English:** This card records the Louvre as a historical physical site in Haskell’s account: the Paris legation’s 1625 visit to its art treasures, Marie de Medici’s 1601 reaction to its palace setting, and the chapter 6 rebuilding designs. Chapter 2 note 3 also reports the second *Arcadian Shepherds* at the Louvre. This source-bounded place is distinct from the modern Louvre Museum institution KU and makes no claim about a work’s present holding or the site’s current condition.[Chapter 2, p. 44](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md) (L8–9); [Chapter 6, p. 153](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md) (L84); [Chapter 7, p. 174](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md) (L47–49)

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性暂题 | 卢浮宫历史地点 / Historical Louvre site | 第2、6、7章所引地点语境；非正式地名核验；S1–S4 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 对象性质 | 历史宫址／物理地点，按书内所指登记 | 第2章 p.44；第6章 p.153；第7章 p.174；S1、S3–S4 |
| 与机构区分 | 不等同于现代卢浮宫博物馆机构；本卡不记录其现行组织或保管职责 | 既有 institution/louvre-museum 卡；本卡所引历史地点语境；S1–S4 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|

### 关系候选入口

[普桑早期作品组、版本区分及逐项S2/S3/S4/S6裁决](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025)
""",
}


NEW_STATEMENTS = [
    {
        "statement_id": "st-chp4-sec-ii-p117-midas-created-by-poussin",
        "segment_id": "chp-4:04_CHP-4_sec_ii:l207-216",
        "subject_candidate_id": "cand-2009",
        "object_candidate_id": "cand-1984",
        "predicate": "created_by",
        "qualifiers": {
            "source_line_start": 212, "source_line_end": 213,
            "pdf_physical_page": 28, "printed_page_locator": "p.117",
            "claim": "Haskell identifies King Midas washing his Face in the River Pactolus as one of the pair of early works he attributes to Poussin.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "mentioned_candidate_ids": ["cand-2009", "cand-1984", "cand-11667"],
            "qualification": "The creator attribution is source-reported through the phrase 'that painter's works'; no external attribution, date, current location, or commission is inferred.",
            "relation_candidate": True,
            "relation_candidate_note": "The passage calls the named work one of the early works by Poussin; it is a creator relation, separate from pair membership.",
        },
        "original_quote": "the King\nMidas washing his Face in the River Pactolus",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    },
    {
        "statement_id": "st-chp4-sec-ii-p117-first-arcadian-created-by-poussin",
        "segment_id": "chp-4:04_CHP-4_sec_ii:l207-216",
        "subject_candidate_id": "cand-1994",
        "object_candidate_id": "cand-1984",
        "predicate": "created_by",
        "qualifiers": {
            "source_line_start": 212, "source_line_end": 213,
            "pdf_physical_page": 28, "printed_page_locator": "p.117",
            "claim": "Haskell identifies the first version of the Arcadian Shepherds as one of the pair of early works he attributes to Poussin.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "mentioned_candidate_ids": ["cand-1994", "cand-1984", "cand-11667"],
            "qualification": "The creator attribution is source-reported through the phrase 'that painter's works'; no external attribution, date, current location, or commission is inferred.",
            "relation_candidate": True,
            "relation_candidate_note": "The passage calls the named first version one of the early works by Poussin; it is a creator relation, separate from pair membership.",
        },
        "original_quote": "the first version of the Arcadian Shepherds",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    },
    {
        "statement_id": "st-chp2-seciv-l190-245-arcadian-shepherds-louvre-location",
        "segment_id": "chp-2:02_CHP-2_sec_iv:l190-245",
        "subject_candidate_id": "cand-1995",
        "object_candidate_id": "cand-1450",
        "predicate": "located_at",
        "qualifiers": {
            "source_line_start": 242, "source_line_end": 242,
            "pdf_physical_page": 46, "printed_page_locator": "p.57 n.3",
            "claim": "Haskell's footnote reports the Arcadian Shepherds at the Louvre.",
            "speaker": "Haskell", "text_layer": "substantive footnote",
            "mentioned_candidate_ids": ["cand-1995", "cand-1450"],
            "qualification": "This is a source-reported location in the book, not a verified present-day holding.",
            "relation_candidate": True,
            "relation_candidate_note": "The footnote explicitly places the indexed second version at the Louvre; the current holding is not asserted.",
        },
        "original_quote": "The Arcadian Shepherds in the Louvre",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
    },
]

RELATIONS = [
    {"relation_id":"rel-1990","subject_ku_id":"units/works/arcadian-shepherds-louvre-second-version-poussin","object_ku_id":"units/persons/nicolas-poussin","predicate":"created_by","time":"","role":"画家","scope":"Haskell names the work among the three paintings Poussin made; the statement does not settle whether all three were for Rospigliosi.","origin":"book","status":"formal","source_id":"haskell-1980-rev-ed","source_span":"Chapter 2, print p.57, lines 175–176; S2 statement st-chp2-seciv-l171-179-poussin-painted-happiness-subject-to-death","source_file":"02-sources/02-Markdown/02_CHP-2_sec_iv.md","note":"The S2 title candidate now maps to the indexed second version; no commission relation is inferred."},
    {"relation_id":"rel-1991","subject_ku_id":"units/works/arcadian-shepherds-louvre-second-version-poussin","object_ku_id":"units/places/louvre-historical-site","predicate":"located_at","time":"","role":"来源所报地点","scope":"Haskell's p.57 note reports this version at the Louvre; the relation records the book's location statement and does not assert present-day custody.","origin":"book","status":"formal","source_id":"haskell-1980-rev-ed","source_span":"Chapter 2, print p.57 n.3, line 242; S2 statement st-chp2-seciv-l190-245-arcadian-shepherds-louvre-location","source_file":"02-sources/02-Markdown/02_CHP-2_sec_iv.md","note":"The endpoint is the historical Louvre place candidate, distinct from the modern Louvre Museum institution KU."},
    {"relation_id":"rel-1992","subject_ku_id":"units/works/king-midas-washing-face-pactolus-poussin","object_ku_id":"units/persons/nicolas-poussin","predicate":"created_by","time":"","role":"画家","scope":"Haskell identifies the named work as one of the early works by Poussin in the source-defined pair; no external attribution is inferred.","origin":"book","status":"formal","source_id":"haskell-1980-rev-ed","source_span":"Chapter 4, print p.117, lines 212–213; S2 statement st-chp4-sec-ii-p117-midas-created-by-poussin","source_file":"02-sources/02-Markdown/04_CHP-4_sec_ii.md","note":"Creator attribution is distinct from membership in the source-defined pair."},
    {"relation_id":"rel-1993","subject_ku_id":"units/works/arcadian-shepherds-first-version-poussin","object_ku_id":"units/persons/nicolas-poussin","predicate":"created_by","time":"","role":"画家","scope":"Haskell identifies the first version as one of the early works by Poussin in the source-defined pair; no external attribution is inferred.","origin":"book","status":"formal","source_id":"haskell-1980-rev-ed","source_span":"Chapter 4, print p.117, lines 212–213; S2 statement st-chp4-sec-ii-p117-first-arcadian-created-by-poussin","source_file":"02-sources/02-Markdown/04_CHP-4_sec_ii.md","note":"Creator attribution is distinct from membership in the source-defined pair."},
    {"relation_id":"rel-1994","subject_ku_id":"units/works/king-midas-washing-face-pactolus-poussin","object_ku_id":"units/works/poussin-early-work-pair-massimi-passage","predicate":"part_of","time":"","role":"组内作品","scope":"The member identified by st-chp4-sec-ii-p117-named-poussin-pair; this records source-defined pair membership only, not pendant status or shared provenance.","origin":"book","status":"formal","source_id":"haskell-1980-rev-ed","source_span":"Chapter 4, print p.117, lines 212–213; S2 statement st-chp4-sec-ii-p117-named-poussin-pair","source_file":"02-sources/02-Markdown/04_CHP-4_sec_ii.md","note":"The S2 candidate predicate contains is represented by its controlled inverse part_of, whose work-to-work domain and range are defined."},
    {"relation_id":"rel-1995","subject_ku_id":"units/works/arcadian-shepherds-first-version-poussin","object_ku_id":"units/works/poussin-early-work-pair-massimi-passage","predicate":"part_of","time":"","role":"组内作品","scope":"The member explicitly called the first version in st-chp4-sec-ii-p117-pair-arcadian-member; this records source-defined pair membership only, not pendant status or shared provenance.","origin":"book","status":"formal","source_id":"haskell-1980-rev-ed","source_span":"Chapter 4, print p.117, line 213; S2 statement st-chp4-sec-ii-p117-pair-arcadian-member","source_file":"02-sources/02-Markdown/04_CHP-4_sec_ii.md","note":"The S2 candidate predicate contains is represented by its controlled inverse part_of, whose work-to-work domain and range are defined."},
    {"relation_id":"rel-1996","subject_ku_id":"units/works/poussin-early-work-pair-massimi-passage","object_ku_id":"units/persons/camillo-massimi","predicate":"acquired_by","time":"","role":"可能的收购人","scope":"Haskell's statement is tentative (""may well have been now""); no exact acquisition date is given and this must not be treated as established provenance.","origin":"book","status":"pending","source_id":"haskell-1980-rev-ed","source_span":"Chapter 4, print p.117, lines 211–213; S2 statement st-chp4-sec-ii-p117-possible-poussin-acquisition","source_file":"02-sources/02-Markdown/04_CHP-4_sec_ii.md","note":"Keep pending because the source itself hedges the acquisition; the possible heirs source is a separate unresolved S2 candidate."},
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_rows(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig" if bom else "utf-8")
    eol = "\r\n" if b"\r\n" in raw else "\n"
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    return raw, bom, eol, rows, list(rows[0].keys()) if rows else []


def encode_csv(rows, fields, bom: bool, eol: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=eol, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def replace_candidate(values: list[str], old: str, new: str) -> list[str]:
    return [new if value == old else value for value in values]


def build_changes() -> dict[Path, bytes]:
    for name, expected in EXPECTED.items():
        source_path = ROOT / "04-knowledge" / "accepted.yml" if name == "accepted.yml" else TABLES / name
        actual = sha(source_path.read_bytes())
        if actual != expected:
            raise SystemExit(f"stale input {name}: expected {expected}, got {actual}")

    changes: dict[Path, bytes] = {}

    path = TABLES / "entity-candidates.csv"
    raw, bom, eol, rows, fields = csv_rows(path)
    matches = [r for r in rows if r["candidate_id"] == "cand-4800"]
    if len(matches) != 1 or matches[0]["status"] != "open":
        raise SystemExit("cand-4800 candidate row is absent or has changed")
    matches[0]["status"] = "excluded"
    matches[0]["exclude_reason"] = (
        "This candidate conflated two source-distinct versions: the chapter 2 p.57 mentions map to the indexed second version cand-1995, "
        "while the chapter 4 p.117 mention explicitly identifies the first version cand-1994. The composite candidate does not denote a separate third work."
    )
    changes[path] = encode_csv(rows, fields, bom, eol)

    path = TABLES / "alignment.csv"
    raw, bom, eol, rows, fields = csv_rows(path)
    mapping = {"cand-1994": KU_ROWS[0], "cand-1995": KU_ROWS[1], "cand-2009": KU_ROWS[2], "cand-11667": KU_ROWS[3], "cand-1450": KU_ROWS[4]}
    resolution = {
        "cand-1994": "group=sg3-work-arcadian-shepherds-first-version-poussin; source_ref=entity-candidates.csv#cand-1994;index_entry=P.csv#197;index_pages=117;mention=m-chp4-sec-ii-p117-0032; S2 L213 explicitly says first version; distinct from the Louvre second version cand-1995. No external object identity is asserted.",
        "cand-1995": "group=sg3-work-arcadian-shepherds-louvre-second-version-poussin; source_ref=entity-candidates.csv#cand-1995;index_entry=P.csv#198;index_pages=57;mentions=m-chp2-seciv-l171-179-0033,m-chp2-seciv-l171-179-0034,m-chp2-seciv-l190-245-0126,m-s2-chp2-surface-d4864b3d59b8ab4b; S2 p.57 gives the alternate title and Louvre report; index marks this page reference second version. No present-day holding or external object identity is asserted.",
        "cand-2009": "group=sg3-work-king-midas-washing-face-pactolus-poussin; source_ref=entity-candidates.csv#cand-2009;index_entry=P.csv#212;index_pages=117;mention=m-chp4-sec-ii-p117-0031; direct title anchor in the source-defined pair. No date, current location, or external object identity is inferred.",
        "cand-11667": "group=sg3-work-poussin-early-pair-massimi-passage; source_ref=entity-candidates.csv#cand-11667;candidate_source_ref=chp-4:04_CHP-4_sec_ii:l207-216#L212;mention=m-chp4-sec-ii-p117-0034; the text names two works as a pair. This group does not establish pendant status, a common original patron, or secure provenance.",
        "cand-1450": "group=sg3-place-cand-1450; source_ref=entity-candidates.csv#cand-1450;index_entry=L.csv#108;mentions=m-chp2-seciv-l6-17-0011,m-s2-chp2-surface-6f8d05c487c242c2,m-chp7-p174-b-009; additional p.57 note directly reports the second Arcadian version at the historical Louvre place. Keep distinct from institution/louvre-museum and from other Louvre work/planning candidates.",
    }
    seen = set()
    for row in rows:
        cid = row["candidate_id"]
        if cid in mapping:
            if cid in seen or row["decision"] not in {"undecided", "new"} or row["ku_id"]:
                raise SystemExit(f"unexpected prior mapping/decision for {cid}")
            row["decision"] = "new"
            row["ku_id"] = mapping[cid][1]
            row["resolution_note"] = resolution[cid]
            seen.add(cid)
        elif cid == "cand-4800":
            if row["decision"] != "new" or row["ku_id"]:
                raise SystemExit("cand-4800 alignment changed")
            row["decision"] = "excluded"
            row["resolution_note"] = (
                "source_ref=entity-candidates.csv#cand-4800; former_group=workgrp-ebabbe4dded9fe; retired composite candidate. "
                "Its chapter 2 p.57 title/Louvre mentions now map to cand-1995 (second version); its chapter 4 p.117 first-version mention maps to cand-1994. "
                "No separate third work remains; see process/knowledge.md#s2-s3-s4-s5-s6-poussin-arcadian-pair-louvre-20261025."
            )
            seen.add(cid)
    if seen != set(mapping) | {"cand-4800"}:
        raise SystemExit(f"alignment rows missing: {(set(mapping) | {'cand-4800'}) - seen}")
    changes[path] = encode_csv(rows, fields, bom, eol)

    path = TABLES / "mentions.csv"
    raw, bom, eol, rows, fields = csv_rows(path)
    reassignment = {
        "m-chp2-seciv-l171-179-0033": "cand-1995",
        "m-chp2-seciv-l171-179-0034": "cand-1995",
        "m-chp2-seciv-l190-245-0126": "cand-1995",
        "m-chp4-sec-ii-p117-0032": "cand-1994",
    }
    seen_mentions = set()
    for row in rows:
        if row["mention_id"] in reassignment:
            row["candidate_id"] = reassignment[row["mention_id"]]
            if row["mention_id"] == "m-chp4-sec-ii-p117-0032":
                row["note"] = "Explicit first-version mention; maps to index candidate cand-1994, distinct from the chapter 2 Louvre second version."
            seen_mentions.add(row["mention_id"])
    if seen_mentions != set(reassignment):
        raise SystemExit(f"mention rows missing: {set(reassignment)-seen_mentions}")
    if any(r["mention_id"] in {"m-chp4-sec-ii-p117-0034", "m-chp4-sec-ii-p117-0035"} for r in rows):
        raise SystemExit("planned p.117 mention ID collision")
    added_mentions = [
        {"mention_id":"m-chp4-sec-ii-p117-0034","segment_id":"chp-4:04_CHP-4_sec_ii:l207-216","candidate_id":"cand-11667","surface_form":"a pair of that painter’s most beautiful early works","start_char":"2019","end_char":"2070","note":"Source-defined pair of works; no pendant status, common original patron, or provenance is inferred."},
        {"mention_id":"m-chp4-sec-ii-p117-0035","segment_id":"chp-4:04_CHP-4_sec_ii:l207-216","candidate_id":"cand-11668","surface_form":"heirs of\nCassiano","start_char":"1939","end_char":"1956","note":"Unidentified heirs are raised only as a possible source; Haskell expressly says there is no direct evidence."},
    ]
    last_p117 = max(i for i, r in enumerate(rows) if r["segment_id"] == "chp-4:04_CHP-4_sec_ii:l207-216")
    rows[last_p117 + 1:last_p117 + 1] = added_mentions
    changes[path] = encode_csv(rows, fields, bom, eol)

    path = TABLES / "book-statements.jsonl"
    original = path.read_bytes()
    if sha(original) != EXPECTED[path.name]:
        raise SystemExit("book-statements changed during preflight")
    lines = original.decode("utf-8").splitlines()
    replacements = {
        "st-chp2-seciv-l171-179-poussin-painted-happiness-subject-to-death": ("cand-4800", "cand-1995"),
        "st-chp2-seciv-l190-245-arcadian-shepherds-date-proposal": ("cand-4800", "cand-1995"),
        "st-chp4-sec-ii-p117-pair-arcadian-member": ("cand-4800", "cand-1994"),
    }
    found = set()
    updated_lines = []
    for line in lines:
        d = json.loads(line)
        sid = d.get("statement_id")
        if sid in replacements:
            old, new = replacements[sid]
            if d.get("object_candidate_id") != old:
                raise SystemExit(f"unexpected endpoint in {sid}")
            d["object_candidate_id"] = new
            q = d.setdefault("qualifiers", {})
            q["mentioned_candidate_ids"] = replace_candidate(q.get("mentioned_candidate_ids", []), old, new)
            if sid == "st-chp2-seciv-l190-245-arcadian-shepherds-date-proposal":
                if q.get("supporting_source_candidate_id") != "cand-4577":
                    raise SystemExit("unexpected Mahon supporting-source candidate")
                q["supporting_source_candidate_id"] = "cand-4867"
                if "cand-1450" not in q["mentioned_candidate_ids"]:
                    q["mentioned_candidate_ids"].append("cand-1450")
            found.add(sid)
        elif sid == "st-chp2-seciv-l190-245-poussin-work-locations-and-dedications":
            q = d.setdefault("qualifiers", {})
            q["work_candidate_ids"] = replace_candidate(q.get("work_candidate_ids", []), "cand-4800", "cand-1995")
            pairs = q.get("location_pairs", [])
            q["location_pairs"] = [
                ["cand-1995" if left == "cand-4800" else left,
                 "cand-1450" if left == "cand-4800" and right == "cand-4589" else right]
                for left, right in pairs
            ]
            found.add(sid)
        elif sid == "st-chp4-sec-ii-p117-possible-poussin-acquisition":
            q = d.setdefault("qualifiers", {})
            q["mentioned_candidate_ids"] = replace_candidate(q.get("mentioned_candidate_ids", []), "cand-4800", "cand-1994")
            found.add(sid)
        elif sid in {
            "st-chp4-sec-ii-p117-mood-and-moral-reading",
            "st-chp4-sec-ii-p117note-fn3-unknown-patron",
        }:
            q = d.setdefault("qualifiers", {})
            q["mentioned_candidate_ids"] = replace_candidate(q.get("mentioned_candidate_ids", []), "cand-4800", "cand-1994")
            found.add(sid)
        updated_lines.append(json.dumps(d, ensure_ascii=False))
    expected_replacements = set(replacements) | {"st-chp4-sec-ii-p117-possible-poussin-acquisition"}
    if not expected_replacements.issubset(found):
        raise SystemExit(f"statement rows missing/changed: {expected_replacements-found}")
    def has_retired_candidate_reference(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.endswith("candidate_id") and item == "cand-4800":
                    return True
                if key.endswith("candidate_ids") and isinstance(item, list) and "cand-4800" in item:
                    return True
                if has_retired_candidate_reference(item):
                    return True
        elif isinstance(value, list):
            return any(has_retired_candidate_reference(item) for item in value)
        return False
    stale_refs = [json.loads(line).get("statement_id") for line in updated_lines if has_retired_candidate_reference(json.loads(line))]
    if stale_refs:
        raise SystemExit(f"unexpected live structured reference to retired cand-4800: {stale_refs}")
    for statement in NEW_STATEMENTS:
        if any(json.loads(line).get("statement_id") == statement["statement_id"] for line in updated_lines):
            raise SystemExit(f"statement ID collision: {statement['statement_id']}")
        updated_lines.append(json.dumps(statement, ensure_ascii=False))
    changes[path] = ("\n".join(updated_lines) + "\n").encode("utf-8")

    path = TABLES / "ku-manifest.csv"
    raw, bom, eol, rows, fields = csv_rows(path)
    for _cid, ku_id, ku_type, name_zh, name_en, card_path, _group in KU_ROWS:
        if any(r["ku_id"] == ku_id or r["card_path"] == card_path for r in rows):
            raise SystemExit(f"manifest collision for {ku_id}")
        rows.append({"ku_id":ku_id,"type":ku_type,"canonical_name":f"{name_zh}（{name_en}）","name_en":name_en,"source_task":"patrons-and-painters-full-book-s2","card_path":card_path})
    changes[path] = encode_csv(rows, fields, bom, eol)

    path = ROOT / "04-knowledge" / "accepted.yml"
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    if "structure: []" not in text:
        raise SystemExit("accepted.yml structure marker missing")
    before, after = text.split("structure: []", 1)
    entries = [f"- {card_path}" for *_, card_path, _group in KU_ROWS]
    for entry in entries:
        if entry in before:
            raise SystemExit(f"accepted card already listed: {entry}")
    lines = before.splitlines()
    unit_lines = [line for line in lines if line.startswith("- 04-knowledge/units/")]
    if not unit_lines:
        raise SystemExit("accepted.yml units list not found")
    # Insert each path into its type block without reordering existing entries.
    for entry in entries:
        folder = entry.split("/")[2]
        same = [i for i, line in enumerate(lines) if line.startswith(f"- 04-knowledge/units/{folder}/")]
        if same:
            insertion = next((i for i in same if lines[i] > entry), same[-1] + 1)
        else:
            order = ["archives", "events", "families", "institutions", "persons", "places", "procedures", "terms", "works"]
            target_rank = order.index(folder)
            later = [i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and order.index(line.split("/")[2]) > target_rank]
            insertion = min(later) if later else len(lines)
        lines.insert(insertion, entry)
    new_text = "\n".join(lines) + "\nstructure: []" + after
    changes[path] = b"\xef\xbb\xbf" + new_text.encode("utf-8")

    path = TABLES / "relations.csv"
    raw, bom, eol, rows, fields = csv_rows(path)
    expected_next = f"rel-{len(rows)+1:04d}"
    if expected_next != "rel-1990":
        raise SystemExit(f"unexpected relation ID sequence: next is {expected_next}")
    for relation in RELATIONS:
        if any(r["relation_id"] == relation["relation_id"] for r in rows):
            raise SystemExit(f"relation ID collision: {relation['relation_id']}")
        rows.append(relation)
    changes[path] = encode_csv(rows, fields, bom, eol)

    for ku_id, content in CARDS.items():
        card_path = ROOT / "04-knowledge" / (ku_id + ".md")
        if card_path.exists():
            raise SystemExit(f"card path already exists: {card_path}")
        changes[card_path] = content.encode("utf-8")

    return changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview or apply the reviewed Poussin/Louvre endpoint batch.")
    parser.add_argument("--apply", action="store_true", help="write after the guarded dry-run plan has been reviewed")
    args = parser.parse_args()
    changes = build_changes()
    for path, content in changes.items():
        old = path.read_bytes() if path.exists() else b""
        print(f"{'WRITE' if args.apply else 'PREVIEW'} {path.relative_to(ROOT)} {len(old)} -> {len(content)} bytes sha256={sha(content)}")
    print("S2: 3 new relation statements; 2 mention additions; 4 existing work mentions reassigned; 1 misgrouped candidate excluded.")
    print("S3/S4: four work candidates and the existing new-place Louvre candidate map to five source-backed KUs.")
    print("S6: six formal rows and one pending row; all 12 affected S2 candidates receive formal/pending/rejected outcomes, with rejected and endpoint-less pending reasons in the batch process note.")
    if not args.apply:
        print("preview only; inspect the planned batch, then pass --apply")
        return
    RECOVERY.mkdir(parents=True, exist_ok=True)
    for path in changes:
        if path.exists():
            shutil.copy2(path, RECOVERY / path.name)
    for path, content in changes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"applied; originals preserved at {RECOVERY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
