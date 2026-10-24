---
title: 伏尔泰（Voltaire）
name_en: Voltaire
type: person
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press,
    1980; this printing 2006).'
  location: 第10章，印刷页318，L134–136及注1
  sentence_summary: Haskell将1766年Voltaire关于意大利思想复兴的评论与注释所引信件相连。
  original_quotes:
  - source_span: lines 134–136; printed p. 318
    text: When in 1766 Voltaire turned his attention southwards across the Alps and commented on the great intellectual revival
      that had taken place he suggested that it had been going on for about twenty years.
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/10_CHP-10_sec_ii.md
    source_span: lines 134–136; printed p. 318
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press,
    1980; this printing 2006).'
  location: 第14章，印刷页349，L24–25
  sentence_summary: Haskell叙述Algarotti在巴黎期间与Voltaire相识并曾住在Cirey。
  original_quotes:
  - source_span: lines 24–25; printed p. 349
    text: There he resided for some time, during which he met Pierre Crozat, Maupertuis and Voltaire, with whom he stayed
      at Cirey.
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/14_CHP-14_intro.md
    source_span: lines 24–25; printed p. 349
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press,
    1980; this printing 2006).'
  location: 第15章，印刷页369–370，L52、67
  sentence_summary: Haskell叙述Querini于1777年拜访Voltaire，并提到一幅Voltaire肖像版画。
  original_quotes:
  - source_span: lines 52 and 67; printed pp. 369–370
    text: In 1777 he went to Switzerland and visited Voltaire. He presented the philosopher with a medal he had had specially
      coined depicting Philosophy destroying Superstition surrounded by a text from Lucretius exaequat vincendo sidera cursus.
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/15_CHP-15_sec_ii.md
    source_span: lines 52 and 67; printed pp. 369–370
- citation: Voltaire, 1694–1778. Bibliothèque nationale de France, Catalogue général, notice de personne FRBNF11928669. https://catalogue.bnf.fr/ark:/12148/cb11928669t.public.
    Accessed 2026-10-18.
  url: https://catalogue.bnf.fr/ark:/12148/cb11928669t.public
  accessed_date: '2026-10-18'
  location: BnF人物规范记录：国际通行笔名、异名形式、人物类别及年代
  sentence_summary: BnF以Voltaire作为国际通行形式，列François-Marie Arouet为异名形式，并标注作者与哲学家身份及1694–1778年；支持人名对齐，不核实书中访问、肖像或思想影响叙述。
  original_quotes: []
created: '2026-10-18'
updated: '2026-10-18'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoint-batch-20261018
---

## 内容

### 描述

**中文：** 本卡以BnF规范记录所用的Voltaire为人物名，并保留François-Marie Arouet为关联姓名。Haskell在第10、14、15章提及此人，包括思想评论、交往及版画语境；这些仍是书内叙述。De Non 于 Ferney 刻制的肖像已作为独立作品登记，并有正式 `has_subject` 关系；其他关系候选仍按各自证据和端点逐项处理。 [S3身份记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoint-batch-20261018)

**English:** This card uses Voltaire, the form preferred by the BnF authority, and records François-Marie Arouet as an associated name. Haskell mentions him in Chapters 10, 14, and 15 in accounts of intellectual commentary, encounters, and prints; these remain source-bounded accounts. The portrait engraved by De Non at Ferney is registered as a separate work with a formal `has_subject` relation. Other relation candidates remain subject to their individual evidence and endpoint review. [S3 identity and S4 registration record](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoint-batch-20261018)

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范形式 | Voltaire | S4；BnF FRBNF11928669 |
| 关联姓名 | François-Marie Arouet（BnF异名形式） | S4；BnF FRBNF11928669 |
| 身份类别 | 作者；哲学家（writer; philosopher） | S4；BnF FRBNF11928669 |
| 生卒年 | 1694–1778 | S4；BnF FRBNF11928669 |

## 关系与证据

### 身份入口

- **S3身份组：** `new-person:voltaire-francois-marie-arouet-20261018`；候选映射：`cand-2791`。该候选映射至本人物KU；身份裁决见[S3/S4过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-endpoint-batch-20261018)。
- **外部身份记录：** [BnF人物规范记录 FRBNF11928669](https://catalogue.bnf.fr/ark:/12148/cb11928669t.public)。支持人物身份与规范名称；不验证书中所述访问、肖像或思想影响。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← 为其所涉对象（`subject_of`，反向投影） | [多角度伏尔泰头像版画（Huber’s Engraving of Voltaire’s Head from Multiple Angles）](../works/jean-huber-engraving-voltaire-head-multiple-angles.md) | S2 statement: st-chp15-p370-huber-engraving-depicts-voltaire. Source-limited relation; see the anchored S6 decision in the 2026-10-22 process record.；角色：图像主题；范围：版画表现伏尔泰头像的多个角度；本边不表示伏尔泰参与版画创作。；原断言与证据见发出端卡片“多角度伏尔泰头像版画（Huber’s Engraving of Voltaire’s Head from Multiple Angles）”：[来源](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)；haskell-1980-rev-ed；line 67; printed p. 370; PDF physical p. 10 |
| ← 为其所涉对象（`subject_of`，反向投影） | [伏尔泰肖像版画（多米尼克·德农于费尔内刻制）](../works/dominique-de-non-portrait-of-voltaire-at-ferney.md) | Records the person identified as the portrait subject.；角色：depicted person；范围：Haskell describes the engraving as a portrait of Voltaire; no more specific iconography is supplied.；原断言与证据见发出端卡片“伏尔泰肖像版画（多米尼克·德农于费尔内刻制）”：[来源](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)；haskell-1980-rev-ed；Chapter 15, printed p.371, L79; S2 statement: st-chp15-p371-voltaire-portrait-depicts-voltaire |


De Non 于 Ferney 刻制的肖像已登记为独立作品，并正式连接至本人物；其他 S2 关系候选仍按各自裁决状态处理，不由该作品关系替代。裁决依据见 `book-statements.jsonl` 与相应 S6 过程记录。
