---
title: 田园场景（Pastoral Scene）
name_en: Pastoral Scene
type: work
evidence_status: source_backed
sources:
- citation: Art Institute of Chicago, Pastoral Scene, artwork 23333, reference 1937.68. https://api.artic.edu/api/v1/artworks/23333. Accessed 2026-09-14.
  location: 馆方API的作品字段、完整description、provenance_text、publication_history及exhibition_history
  sentence_summary: Giovanni Battista Piazzetta，1740年布面油画，191.8×143厘米；Schulenburg委托，1743年清单已载，1937年芝加哥艺术博物馆购入。题材寓意保留解释的不确定性。
- citation: Regione Lombardia / Gabinetto dei Disegni, Testa femminile di profilo, SIRBeC 4y010-09084. https://www.lombardiabeniculturali.it/opere-arte/schede-complete/4y010-09084/. Accessed 2026-09-14.
  location: 完整10页PDF；PDF3–5作品对应、技术与解释；PDF6取得与保管
  sentence_summary: 米兰素描4884/8 C 526/1，241×186毫米；目录将其与科隆Idillio 2806及Cleveland另一素描联系。评论提出科隆画中少女头部的准备稿解释，称科隆画与芝加哥Scena pastorale为Schulenburg所作配对作品，科隆画不晚于1745年。
created: '2026-09-15'
updated: '2026-09-15'
process_ref: 03-processing/patrons-and-painters-front-matter/process/knowledge.md#德国馆藏版本与创作委托关系
relations:
- relation_type: created_by
  target: persons/piazzetta.md
  evidence_ref:
    doc_id: aic-23333
    source_file: https://api.artic.edu/api/v1/artworks/23333
    source_span: artist_display、date_display
  relation_source: explicit
  review_status: evidence_backed_relation
  bidirectional_required: false
  scope: '1937.68'
  role: 画家
  time: '1740'
- relation_type: commissioned_by
  target: persons/marshal-schulenburg.md
  evidence_ref:
    doc_id: aic-23333
    source_file: https://api.artic.edu/api/v1/artworks/23333
    source_span: description、provenance_text首句
  relation_source: explicit
  review_status: evidence_backed_relation
  bidirectional_required: false
  scope: 1937.68；1743年清单已有记录
  role: 委托人
  time: 不晚于1743
- relation_type: acquired_by
  target: institutions/art-institute-of-chicago.md
  evidence_ref:
    doc_id: aic-23333
    source_file: https://api.artic.edu/api/v1/artworks/23333
    source_span: provenance_text末句：purchased by Art Institute, 1937
  relation_source: explicit
  review_status: evidence_backed_relation
  bidirectional_required: false
  scope: '1937.68'
  role: 购买方
  time: '1937'
- relation_type: held_by
  target: institutions/art-institute-of-chicago.md
  evidence_ref:
    doc_id: aic-23333
    source_file: https://api.artic.edu/api/v1/artworks/23333
    source_span: 馆方对象记录、main_reference_number
  relation_source: explicit
  review_status: evidence_backed_relation
  bidirectional_required: false
  scope: 馆藏1937.68
---

## 内容

### 描述

**中文：** 皮亚泽塔为舒伦堡创作的1740年布面油画，芝加哥艺术博物馆于1937年购入，馆号1937.68。

**English:** An oil painting made by Piazzetta for Schulenburg in 1740, acquired by the Art Institute of Chicago in 1937 and catalogued as 1937.68.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 馆方题名 | Pastoral Scene | S1 |
| 意大利语对应名 | Scena pastorale | S2，PDF5 |
| 中文名性质 | 项目工作译名 | 项目命名 |

### 作品信息

| 字段 | 值 | 证据 |
|---|---|---|
| 创作者 | [乔万尼·巴蒂斯塔·皮亚泽塔](../persons/piazzetta.md) | S1 |
| 创作年 | 1740 | S1 |
| 媒介 | 布面油画／Oil on canvas | S1 |
| 尺寸（高×宽） | 191.8 × 143 cm | S1 |
| 馆藏号 | 1937.68 | S1 |
| API对象标识 | 23333 | S1 |

### 委托与收藏

| 字段 | 值 | 证据 |
|---|---|---|
| 委托人 | [舒伦堡元帅](../persons/marshal-schulenburg.md) | S1–S2 |
| 1743年收藏记录 | 已列入舒伦堡清单 | S1，provenance_text |
| 1937年购入 | [芝加哥艺术博物馆](../institutions/art-institute-of-chicago.md) | S1，provenance_text |
| 配对作品 | [科隆《田园》](piazzetta-idyll.md) | S2，PDF5 |

## 关系与证据

### 身份与外部链接

[馆方作品23333](https://www.artic.edu/artworks/23333/pastoral-scene)；[馆方API完整元数据](https://api.artic.edu/api/v1/artworks/23333)（S1）；[SIRBeC配对依据](https://www.lombardiabeniculturali.it/opere-arte/schede-complete/4y010-09084/)（S2）。

### 关系记录
| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← 配对作品（`pendant_of`，反向投影） | [田园（Idyll）](piazzetta-idyll.md) | 角色：配对画作；范围：科隆2806与芝加哥1937.68；后者身份由馆方23333记录核对；原断言与证据见发出端卡片“田园（Idyll）”：[来源](https://www.lombardiabeniculturali.it/opere-arte/schede-complete/4y010-09084/)；src-cf9bfd6d8b0a4249；PDF5：Idillio与Scena pastorale配对说明 |
| → 创作者（`created_by`） | [乔万尼·巴蒂斯塔·皮亚泽塔（Giovanni Battista Piazzetta）](../persons/piazzetta.md) | 时间：1740；角色：画家；范围：1937.68；证据：[来源](https://api.artic.edu/api/v1/artworks/23333)；src-634c16f565e32123；artist_display、date_display |
| → 由其委托（`commissioned_by`） | [约翰·马蒂亚斯·冯·德尔·舒伦堡（Johann Matthias von der Schulenburg）](../persons/marshal-schulenburg.md) | 时间：不晚于1743；角色：委托人；范围：1937.68；1743年清单已有记录；证据：[来源](https://api.artic.edu/api/v1/artworks/23333)；src-634c16f565e32123；description、provenance_text首句 |
| → 由其取得（`acquired_by`） | [芝加哥艺术博物馆（Art Institute of Chicago）](../institutions/art-institute-of-chicago.md) | 时间：1937；角色：购买方；范围：1937.68；证据：[来源](https://api.artic.edu/api/v1/artworks/23333)；src-634c16f565e32123；provenance_text末句：purchased by Art Institute, 1937 |
| → 由其保管（`held_by`） | [芝加哥艺术博物馆（Art Institute of Chicago）](../institutions/art-institute-of-chicago.md) | 范围：馆藏1937.68；证据：[来源](https://api.artic.edu/api/v1/artworks/23333)；src-634c16f565e32123；馆方对象记录、main_reference_number |

### 关系候选入口

[章前原文关系候选与端点映射](../../../03-processing/patrons-and-painters-front-matter/process/knowledge.md#候选登记映射)
