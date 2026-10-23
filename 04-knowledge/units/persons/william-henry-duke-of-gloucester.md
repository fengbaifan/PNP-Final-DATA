---
title: 威廉·亨利（第一代格洛斯特公爵）（William Henry, 1st Duke of Gloucester）
name_en: William Henry, 1st Duke of Gloucester
type: person
evidence_status: source_backed
sources:
- citation: Francis Haskell, *Patrons and Painters*, index.
  location: 全书索引 G.csv#111
  sentence_summary: 索引以“Gloucester, William Henry, 1st Duke of”列出此人，页码指向本卡所据正文。
  original_quotes:
  - source_span: G.csv#111
    text: Gloucester, William Henry, 1st Duke of
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/03-Index/03-2-Index-CSV/G.csv
    source_span: G.csv#111
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)'
  location: 第15章；印刷页366及注1
  sentence_summary: Haskell称途经帕多瓦的格洛斯特公爵竖立了Azzo d’Este雕像；注1记其1775年9月和1777年5月在帕多瓦期间患病，并称Memmo首次访问时与他有联系、劝其订制雕像的日期不确定。
  original_quotes:
  - source_span: lines 17-18 and 25-27; print p.366
    text: Duke of Gloucester
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/15_CHP-15_sec_ii.md
    source_span: lines 17-18 and 25-27; print p.366
created: '2026-10-17'
updated: '2026-10-17'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-gloucester-farsetti-monconys-mei-newcastle-20261017
---

## 内容

### 描述

**中文：** 本卡按全书索引中的完整姓名及第15章对应正文称谓登记该人物。本轮未查验外部人物规范记录；卡片只保留书内身份锚点，不扩展未经本书支持的履历。

**English:** This card registers the person named in the book index and matched to the corresponding chapter form in the text. No external authority record was consulted in this batch; the card preserves the book-based identity anchor without adding unsupported biography.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 索引名 | Gloucester, William Henry, 1st Duke of | S1（索引 G.csv#111） |
| 正文称谓 | Duke of Gloucester | S2（第15章；印刷页366及注1） |

### 本书语境

**中文：** Haskell称途经帕多瓦的格洛斯特公爵竖立了Azzo d’Este雕像；注1记其1775年9月和1777年5月在帕多瓦期间患病，并称Memmo首次访问时与他有联系、劝其订制雕像的日期不确定。S6已将竖立雕像裁为正式关系 `erected_by`（`rel-1702`）；注1的公爵到访及Memmo接触候选仍待证。

**English:** Haskell says the Duke of Gloucester erected a statue of Azzo d’Este while passing through Padua. Note 1 reports illness during visits in September 1775 and May 1777, and says Memmo was in touch with him on the first visit while the date of persuading him to order the statue remains uncertain. S6 adjudicated the statue erection as a formal `erected_by` relation (`rel-1702`); the visit and Memmo-contact candidates in note 1 remain pending.

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← erector_of（`erector_of`，反向投影） | [阿佐·德埃斯特侯爵纪念像（Statue of Azzo, Marchese d’Este）](../works/statue-of-azzo-marchese-deste-pra-della-valle.md) | Haskell says the Duke erected the statue; note 1 reports it had been erected by October 1777. The cited letter was not independently consulted; no exact installation date or present survival is inferred.；时间：by October 1777；角色：erector；范围：Haskell’s source-local Azzo statue at Prà della Valle；原断言与证据见发出端卡片“阿佐·德埃斯特侯爵纪念像（Statue of Azzo, Marchese d’Este）”：[来源](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)；haskell-1980-rev-ed；Chapter 15, printed p.366, L18 and note 1 L27; statements=st-chp15-p366-duke-gloucester-azzo-statue,st-chp15-p366-note1-azzo-statue-erected-by-1777 |


**中文：** 正式关系：`st-chp15-p366-duke-gloucester-azzo-statue` → `rel-1702`。待证候选：`st-chp15-p366-note1-duke-visits`、`st-chp15-p366-note1-memmo-contact-and-order-date`。

**English:** Formal relation: `st-chp15-p366-duke-gloucester-azzo-statue` → `rel-1702`. Pending candidates: `st-chp15-p366-note1-duke-visits` and `st-chp15-p366-note1-memmo-contact-and-order-date`.
