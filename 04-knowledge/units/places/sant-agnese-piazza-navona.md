---
title: "纳沃纳广场圣阿涅塞堂（S. Agnese in Piazza Navona）"
name_en: "S. Agnese in Piazza Navona"
type: place
created: 2026-09-09
updated: 2026-09-12
evidence_status: source_backed
relations:
  - {"relation_type":"located_at","target":"places/piazza-navona.md","note":"教堂定位为 Piazza Navona。","evidence_ref":{"doc_id":"patrons-and-painters","source_file":"02-sources/02-Markdown/01_CHP-1.md","source_span":"lines 437–439; print pp. 12"},"review_status":"evidence_backed_relation","relation_source":"explicit","bidirectional_required":false}
sources:
- citation: 'Francis Haskell, Patrons and Painters, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 1, pp. 12.'
  location: 第一章；印刷页 12；OCR L438–453
  sentence_summary: Ciro Ferri 1670 年穹顶彩稿及四年工期的教堂；不同城市同名教堂不合并。
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/01_CHP-1.md
    source_span: lines 438–453; print pp. 12
- citation: "Wikipedia (en), Sant'Agnese in Agone, revision 1362791584. https://en.wikipedia.org/wiki/Sant'Agnese_in_Agone. Accessed 2026-09-10."
  location: "导言身份段；REV-034 初步对齐，非全文补足"
  sentence_summary: "Sant’Agnese in Agone 与 Sant’Agnese in Piazza Navona 同指，地名和建筑类型相符。"
- citation: "Wikidata, Q1192577, revision 2519963951. https://www.wikidata.org/wiki/Q1192577. Accessed 2026-09-10."
  location: "labels／descriptions／P31／适用身份字段及 enwiki sitelink；判断范围见正文"
  sentence_summary: "Sant’Agnese in Agone 与 Sant’Agnese in Piazza Navona 同指，地名和建筑类型相符。"
- citation: "Wikipedia (en), Sant'Agnese in Agone, revision 1362791584. https://en.wikipedia.org/wiki/Sant'Agnese_in_Agone Accessed 2026-09-11."
  location: "全文8851字符；章节：History、Interior、Origin of name and legends、Cardinal-Deacons、Gallery、See also、References、External links"
  sentence_summary: "完成身份复核与全文语义阅读；只把与本卡类型和第一章语境相关的内容写入结构字段。"
- citation: "Wikidata, Q1192577, revision 2519963951. https://www.wikidata.org/wiki/Q1192577. Accessed 2026-09-11."
  location: "实体完整抓取；含rank、qualifiers、references及enwiki sitelink"
  sentence_summary: "与Wikipedia双向身份一致；结构字段保留参考状态，未机械接收全部声明。"
---

## 内容

### 描述

**中文：** Ciro Ferri 1670 年穹顶彩稿及四年工期的教堂；不同城市同名教堂不合并。

**English:** The church is associated with Ciro Ferri's coloured dome modello of 1670 and a four-year deadline. Churches with the same name in other cities are not merged.

### 已有信息

| 项目 | 内容 | 依据 |
|---|---|---|
| 名称／对应英文 | S. Agnese in Piazza Navona | S1；标题中的语境说明为登记用语 |
| 工程定位 | Ciro Ferri；1670 彩稿与四年工期 | S1，支持范围见各条句意摘要 |

规范显示沿用已能确认的名称；尚未外核的中文音译及说明性译名为本项目暂译，不声称官方命名。


### 本轮结构化补足（REV-055，2026-09-11）

| 字段 | 当前值 | 依据／状态 |
|---|---|---|
| Wikipedia全文 | Sant'Agnese in Agone（en）；revision 1362791584；8851字符 | 全文覆盖：History、Interior、Origin of name and legends、Cardinal-Deacons、Gallery、See also、References、External links |
| Wikidata身份 | [Q1192577](https://www.wikidata.org/wiki/Q1192577)；与enwiki标题双向一致 | revision 2519963951；只采用下列适用字段 |
| 对象类型 | 教堂 | Wikidata P31；有参考 |
| 国家／历史政治归属 | 意大利 | Wikidata P17；有参考 |
| 行政位置 | 罗马 | Wikidata P131；有参考 |
| 成立／建造时间 | 1650 | Wikidata P571；有参考 |

### 初步对齐（REV-034，2026-09-10）

**身份配对通过。** Sant’Agnese in Agone 与 Sant’Agnese in Piazza Navona 同指，地名和建筑类型相符。

[Wikipedia（en）](https://en.wikipedia.org/wiki/Sant'Agnese_in_Agone) 的 wikibase_item 与 [Wikidata Q1192577](https://www.wikidata.org/wiki/Q1192577) 的 enwiki sitelink 双向一致；已比较上列身份特征。仅确认该对象身份，不据此接收整页史实、全部 WD 属性或新增关系。

[身份对齐证据与检索记录](../../../03-processing/patrons-and-painters-chp-1/process/alignment-evidence.jsonl)按本卡稳定键定位。整卡 evidence_status 仍为 source_backed；关系定稿见本卡上表，外部事实继续按各条证据范围解释。

## 关系与证据

### 关系记录
| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 位于（`located_at`） | [纳沃纳广场（Piazza Navona）](piazza-navona.md) | 教堂定位为 Piazza Navona；证据：[来源](../../../02-sources/02-Markdown/01_CHP-1.md)；patrons-and-painters；lines 437–439; print pp. 12 |
| ← 所在地（`location_of`，反向投影） | [费里《圣阿涅塞被引入天堂荣耀》穹顶壁画（Ferri’s Saint Agnes Introduced to the Glory of Paradise）](../works/ferri-sant-agnese-cupola.md) | 工程位于 Piazza Navona 的 S. Agnese；原断言与证据见发出端卡片“费里《圣阿涅塞被引入天堂荣耀》穹顶壁画（Ferri’s Saint Agnes Introduced to the Glory of Paradise）”：[来源](../../../02-sources/02-Markdown/01_CHP-1.md)；patrons-and-painters；lines 437–450; print pp. 12 |

S1：第一章；印刷页 12；OCR L438–453。编号按文件头 sources 顺序对应。句意摘要是转述；具体条目支持范围以该条的章页／行号为准，不能把一个出处视为整卡全部内容的证明。

文件头保留 1 条既有正式关系及各自 note、evidence_ref。本轮未新增或改写这些关系；内容中的角色或提及不自动成为新边。

**本轮补足结论（REV-055）：** 已完成Wikipedia全文阅读、Wikidata完整实体提取及双向身份复核；按类型写入结构字段并标注Wikidata声明的参考状态。未列字段表示本轮来源不足，不表示对象没有该属性；具体关系仍须由直接证据支持。
