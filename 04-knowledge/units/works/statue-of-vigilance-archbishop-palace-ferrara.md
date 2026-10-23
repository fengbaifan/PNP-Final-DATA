---
title: "警醒雕像（Statue of Vigilance, Archbishop’s Palace, Ferrara）"
name_en: "Statue of Vigilance, Archbishop’s Palace, Ferrara"
type: work
evidence_status: source_backed
sources:
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 8, p. 221.'
    location: 第8章，印刷页221；PDF物理页23；Markdown L124
    sentence_summary: Haskell称一尊Vigilance雕像由Cardinal Tommaso Ruffo委托雕塑家Andrea Ferrerio制作，位于费拉拉大主教宫楼梯栏杆中段。
    original_quotes:
      - source_span: line 124; print p. 221; PDF physical p. 23
        text: "At the halfway mark on the balustrade stands a statue of Vigilance"
      - source_span: line 124; print p. 221; PDF physical p. 23
        text: "a statue of Vigilance commissioned by Ruffo from the sculptor Andrea Ferrerio,"
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/08_CHP-8_sec_ii.md
      source_span: line 124; print p. 221; PDF physical p. 23
created: '2026-10-23'
updated: '2026-10-23'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch8-p221-vigilance-stucco-endpoints-20261023
---

## 内容

### 描述

**中文：** 本卡记录Haskell在费拉拉大主教宫楼梯叙述中的一尊Vigilance雕像。原书称Cardinal Tommaso Ruffo委托雕塑家Andrea Ferrerio制作，并称雕像立于楼梯栏杆中段。这里保留来源所报的作品、委托与作者归属，不据此识别现存雕像、推定创作日期或断言其现况。[第8章 p.221](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L124）

**English:** This card records the statue of Vigilance in Haskell’s account of the Archbishop’s Palace staircase in Ferrara. Haskell says Cardinal Tommaso Ruffo commissioned it from the sculptor Andrea Ferrerio and places it at the midpoint of the stairway’s balustrade. The work, commission, and sculptor attribution remain at the level reported by the source; this card does not identify a surviving statue, infer a date, or claim its present condition. [Chapter 8, p. 221](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md) (L124)

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 对象类型 | 雕像／statue | S1；第8章 p.221，L124 |
| 来源所报题材名称 | Vigilance | S1；第8章 p.221，L124 |
| 来源所报位置 | 楼梯栏杆中段 | S1；第8章 p.221，L124 |

## 关系与证据

对象与楼梯空间及栏杆构件分别登记。正式关系由 `relations.csv` 投影；来源所报委托人与雕塑家归属均保留在关系及证据记录中。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 由其委托（`commissioned_by`） | [托马索·鲁福（Tommaso Ruffo）](../persons/tommaso-ruffo.md) | S6裁决：formal。work→person的commissioned_by符合受控域值域；雕像身份与归属限于Haskell书内表述；角色：委托人（Haskell所述）；范围：仅记录Haskell称Cardinal Tommaso Ruffo为该书内雕像的委托人；不据此识别现存雕像或推定委托日期。；证据：[来源](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)；haskell-1980-rev-ed；Chapter 8, printed p. 221, L124; PDF physical p. 23; S2 statement: st-chp8-p221-vigilance-statue-commissioned-by-ruffo |
| → 创作者（`created_by`） | [安德烈亚·费雷里奥（Andrea Ferrerio）](../persons/andrea-ferrerio.md) | S6裁决：formal。work→person的created_by表达原书明确的雕塑家归属；不将其与委托关系混同；角色：雕塑家（Haskell所述）；范围：仅记录Haskell将Andrea Ferrerio称为该雕像的雕塑家；不表示已核验现存作品或外部归属。；证据：[来源](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)；haskell-1980-rev-ed；Chapter 8, printed p. 221, L124; PDF physical p. 23; S2 statement: st-chp8-p221-ferrerio-sculptor-of-vigilance |

### 尚待证关系

`st-chp8-p221-vigilance-statue-on-balustrade` 保留为 pending：两端KU已登记，但受控谓词不能准确表达作品位于建筑构件之上的位置关系。
