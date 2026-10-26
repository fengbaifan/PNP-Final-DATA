---
title: 卡莱尔伯爵（Earl of Carlisle）
name_en: Earl of Carlisle
type: person
evidence_status: source_backed
sources:
- citation: Francis Haskell, *Patrons and Painters*, index.
  location: 全书索引 C.csv#83；所列页码279, 305
  sentence_summary: 索引主项为“Carlisle, Earl of”，页码指向279, 305。
  original_quotes:
  - source_span: C.csv#83
    text: Carlisle, Earl of
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/03-Index/03-2-Index-CSV/C.csv
    source_span: C.csv#83
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)'
  location: 第10章导论 p.279；OCR L44
  sentence_summary: Haskell称Vanbrugh在Yorkshire为年轻的Lord Carlisle营建乡间住宅，并接着说“他”也大量雇用了两位从Castle Howard转往Narford Hall的威尼斯艺术家；S2将两位艺术家分别映射至Marco Ricci与Pellegrini，但原句没有分别说明各自工作内容。
  original_quotes:
  - source_span: line 44; print p.279
    text: for Lord Carlisle, a young man who had already embarked on a career to be more noted for its dazzling social prestige than for any real political achievement. He, too, extensively employed the two Venetian artists who from Castle Howard then moved to Narford Hall in
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/10_CHP-10_intro.md
    source_span: line 44; print p.279
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)'
  location: 第10章导论 p.305；OCR L433
  sentence_summary: 同章 p.305 的索引对应正文称谓为“Earl of Carlisle”；与p.279的“Lord Carlisle”及C.csv#83构成书内名称锚点。
  original_quotes:
  - source_span: line 433; print p.305
    text: Earl of Carlisle.
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/10_CHP-10_intro.md
    source_span: line 433; print p.305
created: '2026-10-17'
updated: '2026-10-17'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoints-caprara-carlisle-cavazza-caylus-cesi-20261017
---

## 内容

### 描述

**中文：** 本卡登记索引主项“Carlisle, Earl of”。第10章 p.279称其为年轻的Lord Carlisle，并说他也大量雇用了两位从Castle Howard转往Narford Hall的威尼斯艺术家；S2将艺术家端点映射到Marco Ricci和Pellegrini，但原句没有分别说明两人的具体工作。p.305出现“Earl of Carlisle”称谓。索引和正文均未在此提供个人名字。 [C.csv#83](../../../02-sources/03-Index/03-2-Index-CSV/C.csv) [第10章导论 p.279；OCR L44](../../../02-sources/02-Markdown/10_CHP-10_intro.md) [第10章导论 p.305；OCR L433](../../../02-sources/02-Markdown/10_CHP-10_intro.md)

**English:** This card records the person indexed as “Carlisle, Earl of.” Chapter 10, p.279, calls him the young Lord Carlisle and says he too extensively employed two Venetian artists who moved from Castle Howard to Narford Hall; S2 maps those artist endpoints to Marco Ricci and Pellegrini, while the sentence does not specify each artist’s individual work. Page 305 uses “Earl of Carlisle.” The index and these passages do not supply his personal name. [C.csv#83](../../../02-sources/03-Index/03-2-Index-CSV/C.csv) [第10章导论 p.279；OCR L44](../../../02-sources/02-Markdown/10_CHP-10_intro.md) [第10章导论 p.305；OCR L433](../../../02-sources/02-Markdown/10_CHP-10_intro.md)

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 索引名 | Carlisle, Earl of | S1（索引 C.csv#83） |

### 本书相关内容

**中文：** Haskell第10章 p.279称 Carlisle 大量雇用了两位威尼斯画家；两条关系现以 `employed_by` 记录到 Marco Ricci 与 Pellegrini。原文未给具体委托、作品、个人分工或雇佣年份，本卡不补写这些信息。 [C.csv#83](../../../02-sources/03-Index/03-2-Index-CSV/C.csv) [第10章导论 p.279；OCR L44](../../../02-sources/02-Markdown/10_CHP-10_intro.md) [第10章导论 p.305；OCR L433](../../../02-sources/02-Markdown/10_CHP-10_intro.md)

**English:** Haskell says in chapter 10, p.279, that Carlisle extensively employed the two Venetian artists; the two `employed_by` relations are now recorded for Marco Ricci and Pellegrini. The book supplies no specific commission, work, individual assignment, or employment year, and none is added here. [C.csv#83](../../../02-sources/03-Index/03-2-Index-CSV/C.csv) [第10章导论 p.279；OCR L44](../../../02-sources/02-Markdown/10_CHP-10_intro.md) [第10章导论 p.305；OCR L433](../../../02-sources/02-Markdown/10_CHP-10_intro.md)

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← 雇主（`employer_of`，反向投影） | [马尔科·里奇（Marco Ricci）](marco-ricci.md) | S2 statement=st-chp10-p279-carlisle-employs-marco-ricci；时间：时间未载；角色：artist；范围：Haskell says Lord Carlisle extensively employed Marco Ricci. Specific commissions, works, and dates are not supplied and are not inferred.；原断言与证据见发出端卡片“马尔科·里奇（Marco Ricci）”：[来源](../../../02-sources/02-Markdown/10_CHP-10_intro.md)；haskell-1980-rev-ed；p.279, OCR L44; PDF physical p.4 |
| ← 雇主（`employer_of`，反向投影） | [乔瓦尼·安东尼奥·佩莱格里尼（Giovanni Antonio Pellegrini）](pellegrini.md) | S2 statement=st-chp10-p279-carlisle-employs-pellegrini；时间：时间未载；角色：artist；范围：Haskell says Lord Carlisle extensively employed Pellegrini. Specific commissions, works, and dates are not supplied and are not inferred.；原断言与证据见发出端卡片“乔瓦尼·安东尼奥·佩莱格里尼（Giovanni Antonio Pellegrini）”：[来源](../../../02-sources/02-Markdown/10_CHP-10_intro.md)；haskell-1980-rev-ed；p.279, OCR L44; PDF physical p.4 |


第10章 p.279 的两条一般雇佣关系已按 Haskell 的直接表述写入 `relations.csv`；具体作品、委托和年份仍未载。
