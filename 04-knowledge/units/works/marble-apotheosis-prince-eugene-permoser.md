---
title: "欧根亲王的《神化》大理石作品（Apotheosis of Prince Eugene of Savoy）"
name_en: "Apotheosis of Prince Eugene of Savoy"
type: work
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
  location: 第7章，印刷页201，L47–48；PDF物理页43
  sentence_summary: Haskell称这是一件由Permoser创作、由欧根亲王亲自设计的大理石《神化》作品，并称其仍存世。
  original_quotes:
  - source_span: Chapter 7, printed p. 201, L47–48; PDF physical p. 43
    text: the marble Apotheosis by Permoser which he himself designed survives
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/07_CHP-7_sec_v.md
    source_span: lines 47–48; print p. 201
- citation: Belvedere Museum, “Apotheosis of Prince Eugene of Savoy,” Sammlung Online, object 3013, inventory no. 4219. https://sammlung.belvedere.at/objects/3013/apotheose-des-prinzen-eugen-von-savoyen. Accessed 2026-10-24.
  location: Object 3013; title, artist, date, object type, medium, dimensions, inventory number, and locations fields
  sentence_summary: The Belvedere collection identifies the sculpture as the Apotheosis of Prince Eugene of Savoy by Balthasar Permoser, c. 1718/1721, in marble, inventory no. 4219, and lists the Lower Belvedere as a location.
  evidence_ref:
    doc_id: belvedere-object-3013
    source_file: https://sammlung.belvedere.at/objects/3013/apotheose-des-prinzen-eugen-von-savoyen
    source_span: Object 3013, title and collection-data fields
created: '2026-10-24'
updated: '2026-10-24'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp7-p201-apotheosis-endpoints-20261024
---

## 内容

### 描述

**中文：** Belvedere馆藏记录将该作品著录为欧根亲王《神化》，作者为Balthasar Permoser，日期约1718/1721，媒材为大理石。Haskell第7章p.201也称有一件Permoser创作、由欧根亲王亲自设计的大理石《神化》作品；材质、创作者和语境与馆藏对象相合，故将书中指称与馆藏对象归入同一作品KU。馆方记录列出的尺寸、馆藏号与地点只按该目录状态记录，不据此推定现展厅位置。

**English:** The Belvedere collection catalogues the work as the Apotheosis of Prince Eugene of Savoy by Balthasar Permoser, dated c. 1718/1721 and made of marble. Haskell’s Chapter 7, p. 201 also describes a marble Apotheosis by Permoser, designed by Prince Eugene; the material, maker, and context match the catalogued object, so the book reference and museum object are grouped as one work KU. Dimensions, inventory number, and location are recorded as catalog data and do not establish a specific current gallery display.

### 作品信息

| 字段 | 值 | 依据 |
|---|---|---|
| 馆方目录题名 | Apotheosis of Prince Eugene of Savoy；Haskell未提供正式题名 | S2 |
| 作品类型 | 雕塑（sculpture） | S2 |
| 材质 | 大理石（marble） | S2 |
| 目录日期 | 约1718/1721；保留馆方记法 | S2 |
| 尺寸 | 234 × 124 × 100 cm；馆方页面未在所列尺寸旁标注各轴对应 | S2 |
| 馆藏编号 | 4219 | S2 |
| 馆方目录所列地点 | Lower Belvedere；未标具体房间或当前展出位置，地点端点待登记 | S2 |
| 原书记载状态 | Haskell称作品仍存世；此处保留书内说法，不单独推断存世起止时间 | S1 |

## 关系与证据

### 身份入口

- [Belvedere馆藏记录：Apotheosis of Prince Eugene of Savoy，object 3013，inventory no. 4219](https://sammlung.belvedere.at/objects/3013/apotheose-des-prinzen-eugen-von-savoyen)。目录记录用于作品身份与字段对照；不把馆方所列Lower Belvedere映射到“两座Belvedere”集合端点。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → designed_by（`designed_by`） | [萨伏依的欧根亲王（Prince Eugene of Savoy）](../persons/prince-eugene-of-savoy.md) | 仅记录Haskell书内所述设计角色；S2 attribution candidate；角色：设计者；范围：Haskell称欧根亲王亲自设计这件大理石《神化》作品；仅记录其设计者角色，与Permoser的制作归属分别表达，不推及建筑设计。；证据：[来源](../../../02-sources/02-Markdown/07_CHP-7_sec_v.md)；haskell-1980-rev-ed；Chapter 7, printed p. 201, L48; PDF physical p. 43; statement=st-chp7-p201-v-apotheosis-designed-by-eugene |
| → 创作者（`created_by`） | [巴尔塔萨·佩尔莫泽（Balthasar Permoser）](../persons/balthasar-permoser.md) | Belvedere Museum object 3013 provides independent catalogue corroboration; relation evidence remains anchored to the Haskell S2 statement.；角色：雕塑制作人；范围：Haskell将大理石《神化》归于Permoser；Belvedere object 3013也将Balthasar Permoser列为作者。此边记录来源支持的制作人归属，不代表本项目已独立审查作品归属。；证据：[来源](../../../02-sources/02-Markdown/07_CHP-7_sec_v.md)；haskell-1980-rev-ed；Chapter 7, printed p. 201, L47–48; PDF physical p. 43; statement=st-chp7-p201-v-apotheosis-executed-by-permoser |
| → 所涉对象（`has_subject`） | [萨伏依的欧根亲王（Prince Eugene of Savoy）](../persons/prince-eugene-of-savoy.md) | External catalogue subject relation for the sculpture; distinct from Haskell’s designed_by relation.；角色：描绘人物；范围：Belvedere object 3013的作品说明将欧根亲王描述为作品所表现的人物（“second Hercules”）；不据此推断委托关系。；证据：[来源](https://sammlung.belvedere.at/objects/3013/apotheose-des-prinzen-eugen-von-savoyen)；src-fafe74be6f3ca959；Object 3013 description, represented figure; collection title and description |
