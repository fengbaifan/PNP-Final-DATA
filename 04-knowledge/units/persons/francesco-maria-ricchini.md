---
title: 弗朗切斯科·马里亚·里基尼（Francesco Maria Ricchini）
name_en: Francesco Maria Ricchini
type: person
evidence_status: source_backed
sources:
- citation: Francis Haskell, *Patrons and Painters*, index.
  location: 全书索引 Q-R.csv#73
  sentence_summary: 索引以“Ricchini, Francesco Maria”列出此人并定位至第215页。
  original_quotes:
  - source_span: Q-R.csv#73
    text: Ricchini, Francesco Maria
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/03-Index/03-2-Index-CSV/Q-R.csv
    source_span: Q-R.csv#73
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)'
  location: 第8章第II节；印刷页215
  sentence_summary: Haskell称贝加莫圣母玛利亚教堂的穹顶由米兰建筑师Francesco Maria Ricchini于1612年规划。
  original_quotes:
  - source_span: lines 13–14; print p.215
    text: the dome which was planned by the Milanese architect Francesco Maria Ricchini in 1612
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/08_CHP-8_sec_ii.md
    source_span: lines 13–14; print p.215
created: '2026-10-18'
updated: '2026-10-18'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-qr-middle-20261018
---

## 内容

### 描述

**中文：** 本卡按索引Q-R.csv#73登记建筑师Francesco Maria Ricchini。第8章p.215称他于1612年规划贝加莫圣母玛利亚教堂穹顶；规划与之后的灰泥覆盖及壁画装饰分开。

**English:** This card registers architect Francesco Maria Ricchini under index Q-R.csv#73. Chapter 8, p.215, says he planned the dome of Santa Maria Maggiore in Bergamo in 1612; planning is distinct from the later stucco covering and fresco decoration.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 索引名 | Ricchini, Francesco Maria | S1（索引Q-R.csv#73） |
| 正文姓名形式 | Francesco Maria Ricchini | S2（第8章第II节p.215） |

### 本书语境

**中文：** 正文和索引均给出全名；不将规划者与之后施工、装饰者混同。直接S2候选 `st-chp8-p215-ricchini-planned-dome-1612` 已裁为 Ricchini → 穹顶的 `designer_of`，时间限定为1612年规划；不表示施工、完工或之后的装饰角色（`rel-1828`）。

**English:** The body and index both give his full name; the planner is kept distinct from later builders and decorators. The direct S2 candidate `st-chp8-p215-ricchini-planned-dome-1612` is recorded as `designer_of` the dome, limited to the 1612 planning role; it does not assert construction, completion, or later decorative work (`rel-1828`).

## 关系与证据

### 身份与外部链接

本批未在卡内添加外部身份链接；书内名称依据见上表及索引/正文来源。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → designer_of（`designer_of`） | [贝加莫圣母大殿穹顶（Dome of Santa Maria Maggiore in Bergamo）](../works/dome-santa-maria-maggiore-bergamo.md) | S2 relation candidate st-chp8-p215-ricchini-planned-dome-1612. The source identifies Ricchini as architect and says he planned the dome in 1612.；时间：1612（规划）；角色：建筑师／规划者；范围：仅记录 Haskell 所述 Ricchini 于1612年规划穹顶；不表示实际施工或完工，也不推及灰泥与壁画装饰。；证据：[来源](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)；haskell-1980-rev-ed；Chapter 8, printed pp.215 L13–14; statement=st-chp8-p215-ricchini-planned-dome-1612 |

正式关系由 `relations.csv` 渲染；本卡与穹顶的设计关系及其来源限定见上文与关系记录。

**中文：** 直接S2候选已正式裁决：`st-chp8-p215-ricchini-planned-dome-1612` → `rel-1828`。

**English:** Direct S2 candidate adjudicated formal: `st-chp8-p215-ricchini-planned-dome-1612` → `rel-1828`.
