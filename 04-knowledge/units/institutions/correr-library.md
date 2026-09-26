---
title: 科雷尔图书馆（Correr Library）
name_en: Correr Library
type: institution
evidence_status: source_backed
sources:
- citation: Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this printing 2006).
  location: 章前：第一版序言；印刷页ix；PDF 7；OCR L23–23
  sentence_summary: 哈斯克尔在威尼斯进行研究所使用的图书馆。
  original_quotes:
  - source_span: lines 23–23
    text: I have benefited from conversations with so many people that it is impossible to thank them all and I apologise to all who have been inadvertently omitted. In Italy I would like to single out especially Dr Terisio Pignatti, who has given me such marvellous facilities for working in the Correr Library in Venice, Dr Alessandro Bettagno,
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_03_Preface_1st_Ed.md
    source_span: lines 23–23; 章前：第一版序言；印刷页ix；PDF 7
- citation: Museo Correr / Fondazione Musei Civici di Venezia, Library. https://correr.visitmuve.it/en/library/. Accessed 2026-09-14.
  location: The Library正文及Services；未读所链接目录、馆藏原件
  sentence_summary: 科雷尔博物馆及图书馆于1830年因威尼斯贵族Teodoro Correr遗赠而成立；馆内图书馆保存手稿、档案和印本文献，服务威尼斯艺术与历史研究。
created: '2026-09-14'
updated: '2026-09-15'
process_ref: 03-processing/patrons-and-painters-front-matter/process/knowledge.md#机构沿革出版责任与研究支持定稿
relations:
- relation_type: part_of
  target: institutions/museo-correr.md
  evidence_ref:
    doc_id: institutions-correr-library
    source_file: https://correr.visitmuve.it/en/library/
    source_span: The Library：The Correr Museum incorporates the Library
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  scope: 博物馆包含其威尼斯艺术与历史图书馆
  role: 所属图书馆
- relation_type: located_at
  target: places/venice.md
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_03_Preface_1st_Ed.md
    source_span: lines 23–23; 章前：第一版序言；印刷页ix；PDF 7
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  scope: 第一版序言所述研究场所所在地
- relation_type: supported_by
  target: persons/teodoro-correr.md
  evidence_ref:
    doc_id: institutions-correr-library
    source_file: https://correr.visitmuve.it/en/library/
    source_span: The Library首句：museum and library founded through bequest
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  scope: 遗赠促成图书馆1830年创立；与博物馆端点分别记录
  role: 创立遗赠者
  time: '1830'
---


## 内容

### 描述

**中文：** 科雷尔博物馆所属的威尼斯艺术与历史研究图书馆，1830年因泰奥多罗·科雷尔的遗赠而成立。

**English:** A library for research on Venetian art and history within the Museo Correr, established in 1830 through Teodoro Correr’s bequest.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 原文名称 | Correr Library | S1 |
| 中文名性质 | 项目工作译名 | 项目命名 |
| 机构归属名称 | Museo Correr Library | S2 |

### 来源所载信息

| 字段 | 值 | 证据 |
|---|---|---|
| 章前记载 | 哈斯克尔在威尼斯进行研究所使用的图书馆。 | S1 |

### 图书馆信息

| 字段 | 值 | 证据 |
|---|---|---|
| 所在地 | [威尼斯](../places/venice.md) | S1、S2 |
| 所属机构 | [科雷尔博物馆](museo-correr.md) | S2 |
| 成立年 | 1830 | S2 |
| 创立遗赠者 | [泰奥多罗·科雷尔](../persons/teodoro-correr.md) | S2 |
| 研究服务范围 | 威尼斯艺术与历史 | S2 |
| 收藏类型 | 手稿与档案 | S2 |
| 收藏类型 | 印本文献 | S2 |

### 本书研究支持

| 字段 | 值 | 证据 |
|---|---|---|
| 研究使用者 | [弗朗西斯·哈斯克尔](../persons/francis-haskell.md) | S1 |
| 提供研究便利者 | [泰里西奥·皮尼亚蒂](../persons/terisio-pignatti.md) | S1 |

## 关系与证据

### 身份与外部链接

[科雷尔图书馆官方介绍](https://correr.visitmuve.it/en/library/)（S2）。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 组成部分（`part_of`） | [科雷尔博物馆（Museo Correr）](museo-correr.md) | 角色：所属图书馆；范围：博物馆包含其威尼斯艺术与历史图书馆；证据：[来源](https://correr.visitmuve.it/en/library/)；src-a96f36b75b4b162a；The Library：The Correr Museum incorporates the Library |
| → 位于（`located_at`） | [威尼斯（Venice）](../places/venice.md) | 范围：第一版序言所述研究场所所在地；证据：[来源](../../../02-sources/02-Markdown/00_03_Preface_1st_Ed.md)；haskell-1980-rev-ed；lines 23–23; 章前：第一版序言；印刷页ix；PDF 7 |
| → supported_by（`supported_by`） | [泰奥多罗·科雷尔（Teodoro Correr）](../persons/teodoro-correr.md) | 时间：1830；角色：创立遗赠者；范围：遗赠促成图书馆1830年创立；与博物馆端点分别记录；证据：[来源](https://correr.visitmuve.it/en/library/)；src-a96f36b75b4b162a；The Library首句：museum and library founded through bequest |

### 关系候选入口

[章前原文关系候选与端点映射](../../../03-processing/patrons-and-painters-front-matter/process/knowledge.md#候选登记映射)
