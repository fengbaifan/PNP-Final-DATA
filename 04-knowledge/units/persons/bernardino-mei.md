---
title: 贝尔纳迪诺·梅伊（Bernardino Mei）
name_en: Bernardino Mei
type: person
evidence_status: source_backed
sources:
- citation: Francis Haskell, *Patrons and Painters*, index.
  location: 全书索引 M.csv#173
  sentence_summary: 索引以“Mei, Bernardino”列出此人，页码指向本卡所据正文。
  original_quotes:
  - source_span: M.csv#173
    text: Mei, Bernardino
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/03-Index/03-2-Index-CSV/M.csv
    source_span: M.csv#173
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)'
  location: 第6章；印刷页154
  sentence_summary: Haskell称Flavio Chigi委托Bernardino Mei绘制天花板壁画，并在列举的Chigi宫殿寓意画中提到《正义与和平》及《从维纳斯的欢愉中救出的青年》。
  original_quotes:
  - source_span: lines 95-97; print p.154
    text: Bernardino Mei
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/06_CHP-6_sec_i.md
    source_span: lines 95-97; print p.154
created: '2026-10-17'
updated: '2026-10-17'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-gloucester-farsetti-monconys-mei-newcastle-20261017
---

## 内容

### 描述

**中文：** 本卡按全书索引中的完整姓名及第6章对应正文称谓登记该人物。本轮未查验外部人物规范记录；卡片只保留书内身份锚点，不扩展未经本书支持的履历。

**English:** This card registers the person named in the book index and matched to the corresponding chapter form in the text. No external authority record was consulted in this batch; the card preserves the book-based identity anchor without adding unsupported biography.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 索引名 | Mei, Bernardino | S1（索引 M.csv#173） |
| 正文称谓 | Bernardino Mei | S2（第6章；印刷页154） |

### 本书语境

**中文：** Haskell称Flavio Chigi委托Bernardino Mei绘制天顶壁画，并在列举的Chigi宫殿寓意画中提到《正义与和平》及《从维纳斯的欢愉中救出的青年》。第6章 p.154 的委托与《受美德节制的命运》壁画创作者归属已分别登记为正式关系；其他寓意画仍按各自对象边界审查。

**English:** Haskell says Flavio Chigi commissioned Bernardino Mei to paint a ceiling fresco and lists Justice and Peace and Youth rescued from the Pleasures of Venus among Mei’s allegories in the Chigi palace. The Chapter 6 p.154 commission and creator-attribution statements for the Fortune ceiling fresco are now formal relations; the other allegories remain separate objects for review.

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← 所创作对象（`creator_of`，反向投影） | [受美德节制的命运天顶壁画（Ceiling fresco of Fortune under the Control of Virtue）](../works/fortune-under-control-of-virtue-ceiling-fresco.md) | S2 statement st-chp6-p154-mei-paints-fortune-fresco; direction follows controlled created_by schema; decision is limited to Haskell’s reported passage.；角色：来源记载的创作者；范围：Haskell lists Fortune under the control of Virtue among Mei’s allegories; this is the book’s attribution, with no external catalogue check or surviving version identification.；原断言与证据见发出端卡片“受美德节制的命运天顶壁画（Ceiling fresco of Fortune under the Control of Virtue）”：[来源](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)；haskell-1980-rev-ed；Chapter 6, printed p.154, lines 95–97; PDF physical p.9; statement=st-chp6-p154-mei-paints-fortune-fresco |

正式关系由 `relations.csv` 维护；本卡展示由该表定向生成。

**中文：** `st-chp6-p154-mei-paints-fortune-fresco` 已裁为 `created_by` 正式关系；Flavio Chigi 的委托关系另见对应工作卡。`st-chp6-p154-mei-allegories` 与 `st-chp6-p154-mei-youth-rescued-allegory` 仍待 S6 逐项裁决，涉及的作品保持独立。

**English:** `st-chp6-p154-mei-paints-fortune-fresco` is now a formal `created_by` relation; the related commission edge is shown on the corresponding work card. `st-chp6-p154-mei-allegories` and `st-chp6-p154-mei-youth-rescued-allegory` remain for individual S6 review and concern separate works.
