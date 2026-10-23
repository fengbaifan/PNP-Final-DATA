---
title: "罗马奇博宫（Palazzo Cibo）"
name_en: "Palazzo Cibo"
type: place
sub_type: building
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 8, pp. 221, 223.'
  location: 第8章，印刷页221、223；PDF物理页23、25；OCR L120–121、145
  sentence_summary: p.221记述Ruffo晚年居住并购置的罗马宫殿及其相对位置；p.223称Ruffo的画廊位于Palazzo Cibo。
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/08_CHP-8_sec_ii.md
    source_span: lines 120–121, 145; print pp. 221, 223; PDF physical pp. 23, 25
  original_quotes:
  - source_span: lines 120–121
    text: |-
      As an old man he then lived in Rome in a palace opposite the Trevi
      Fountain which he bought from the Cibo family. He died there, aged 90,
      in 1753.
  - source_span: line 145
    text: his gallery in the Palazzo Cibo must have retained its exotic and delicate flavour until his death.
created: '2026-10-23'
updated: '2026-10-23'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp8-p221-cibo-palace-trevi-fountain-20261023
---

## 内容

### 描述

**中文：** 第8章将鲁福晚年居住并购置的罗马宫殿称为 “Palazzo Cibo”。本卡依据 p.221 的宫殿叙述及 p.223 的画廊称谓记录这一来源内对象；不补写精确地址、建造年代、现存状态或未记载的产权区间。

**English:** Chapter 8 calls the Roman palace where Ruffo lived in old age and which he bought “Palazzo Cibo.” This card records the source-internal place identified by the palace account on p. 221 and the gallery reference on p. 223. It adds no exact address, construction date, survival status, or unreported period of ownership.

### 名称与基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 原文名称 | Palazzo Cibo | S1，第8章，印刷页223 |
| 建筑类型 | 宫殿／palace | S1，第8章，印刷页221 |
| 地理位置 | 罗马／Rome | S1，第8章，印刷页221 |
| 相对位置 | 与 Trevi Fountain 相对／opposite the Trevi Fountain | S1，第8章，印刷页221 |

### 本书相关内容

第8章 p.221 称 Cardinal Tommaso Ruffo 晚年住在罗马一座与 Trevi Fountain 相对的宫殿，并称他从 Cibo 家族购得该宫殿，1753年在那里去世。p.223 在同一人物的画廊叙述中使用 “Palazzo Cibo”。购置日期和宫殿当前状况未载。

In Chapter 8, p. 221, Haskell says Cardinal Tommaso Ruffo lived in old age in a Rome palace opposite the Trevi Fountain, bought it from the Cibo family, and died there in 1753. On p. 223, the account of the same person's gallery calls the place “Palazzo Cibo.” No purchase date or present condition is given.

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← 所在地（`location_of`，反向投影） | [托马索·鲁福（Tommaso Ruffo）](../persons/tommaso-ruffo.md) | S6裁决：formal。仅记录原书所述晚年居所；不补造起始年份、精确地址或现状；角色：晚年居所；范围：Haskell称Ruffo晚年居住于该罗马宫殿；起始年份未载，不表示连续居住或今日住址。；原断言与证据见发出端卡片“托马索·鲁福（Tommaso Ruffo）”：[来源](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)；haskell-1980-rev-ed；Chapter 8, printed p. 221, L120; PDF physical p. 23; S2 statement: st-chp8-p221-ruffo-lives-in-rome-palace |
| ← 所在地（`location_of`，反向投影） | [托马索·鲁福（Tommaso Ruffo）](../persons/tommaso-ruffo.md) | S6裁决：formal。只记录书内所述去世地点，不外推宫殿当前状态；时间：1753；角色：去世地点；范围：Haskell称Ruffo于1753年在该宫殿去世，享年90岁；年龄与日期均限于原书报告。；原断言与证据见发出端卡片“托马索·鲁福（Tommaso Ruffo）”：[来源](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)；haskell-1980-rev-ed；Chapter 8, printed p. 221, L121; PDF physical p. 23; S2 statement: st-chp8-p221-ruffo-dies-in-palace |
| → 位于（`located_at`） | [特雷维喷泉（Trevi Fountain）](trevi-fountain-rome.md) | S6裁决：formal。place→place的located_at仅表达书内相对位置；scope保留opposite，不作part_of；角色：相对地标；范围：Haskell称宫殿与Trevi Fountain相对；范围是书内报告的位置关系，不表示宫殿位于喷泉内部、属于喷泉或与其同址。；证据：[来源](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)；haskell-1980-rev-ed；Chapter 8, printed p. 221, L120–121; PDF physical p. 23; S2 statement: st-chp8-p221-rome-palace-opposite-trevi-fountain |
| → 由其收藏／拥有（`owned_by`） | [托马索·鲁福（Tommaso Ruffo）](../persons/tommaso-ruffo.md) | S6裁决：formal。以place→person的owned_by表达原书所述购置结果；Cibo家族作为卖方保留在证据语境，购置日期与完整产权链未载；角色：购置后的所有人；范围：Haskell称Ruffo从Cibo家族购得该宫殿；购置日期未载。本边记录原书明确购置所支持的历史所有关系，不表示连续或现时产权，也不将Cibo家族另判为登记所有人。；证据：[来源](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)；haskell-1980-rev-ed；Chapter 8, printed p. 221, L120–121; PDF physical p. 23; S2 statement: st-chp8-p221-ruffo-buys-palace-from-cibo-family |
