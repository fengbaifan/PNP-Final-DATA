---
title: 洛雷丹别墅（Villa Loredan, Paese）
name_en: Villa Loredan, Paese
type: place
evidence_status: source_backed
sources:
- citation: National Gallery, “Villa del Timpano Arcuato at Paese,” inventory L1005. https://www.nationalgallery.org.uk/paintings/francesco-guardi-villa-del-timpano-arcuato-at-paese. Accessed 2026-09-25.
  location: About the work全文；“About the work”第3–4段
  sentence_summary: 三幅瓜尔迪景观画表现Villa Loredan；National Gallery称其为John Strange在Paese的乡间住宅。
- citation: The Metropolitan Museum of Art, “The Villa Loredan, Paese,” object 2019.141.14. https://www.metmuseum.org/art/collection/search/438116. Accessed 2026-09-25.
  location: 对象说明及Object Information
  sentence_summary: 独立馆藏作品以Villa Loredan, Paese为题，并称其描绘John Strange的乡间住宅；不据此断定为本书图版64的具体实物。
created: '2026-09-25'
updated: '2026-09-25'
process_ref: 03-processing/patrons-and-painters-front-matter/process/knowledge.md#章前实体身份对齐与地点作品关系补足约翰斯特兰奇2026-09-25
relations:
- relation_type: owned_by
  target: persons/john-strange.md
  evidence_ref:
    doc_id: national-gallery-villa-del-timpano-arcuato
    source_file: https://www.nationalgallery.org.uk/paintings/francesco-guardi-villa-del-timpano-arcuato-at-paese
    source_span: lines 104–105
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  scope: National Gallery所记Strange在Paese的乡间住宅；未给产权取得、转移或终止日期
  role: 历史所有人
- relation_type: located_at
  target: places/paese.md
  evidence_ref:
    doc_id: national-gallery-villa-del-timpano-arcuato
    source_file: https://www.nationalgallery.org.uk/paintings/francesco-guardi-villa-del-timpano-arcuato-at-paese
    source_span: lines 104–105
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  scope: Paese镇内的乡间别墅
  role: 建筑所在地
---

## 内容

### 描述

**中文：** 位于意大利威尼托大区Paese的乡间别墅；国家美术馆称其为约翰·斯特兰奇的住宅，并记载瓜尔迪曾为该处创作景观画。

**English:** A country house in Paese, Veneto, Italy, identified by the National Gallery as John Strange's residence and the subject of views painted by Francesco Guardi.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 英文名称 | Villa Loredan, Paese | S1–S2 |
| 建筑类别 | 别墅／乡间住宅 | S1 |

### 建筑信息

| 字段 | 值 | 证据 |
|---|---|---|
| 所在地 | [Paese](paese.md)，威尼托大区 | S1 |
| 历史所有人 | [John Strange](../persons/john-strange.md) | S1；该记录未给产权起止或转移日期 |
| 被描绘于 | [约翰·斯特兰奇别墅景观](../works/francesco-guardi-view-of-john-strange-s-villa-at-paese-near-treviso.md) | S1、S2；图版64与某一馆藏画作的版本对应未确认 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 所有人（`owned_by`） | [约翰·斯特兰奇（John Strange）](../persons/john-strange.md) | 角色：历史所有人；范围：National Gallery所记其Paese乡间住宅；产权时间未由来源注明；证据：[国家美术馆](https://www.nationalgallery.org.uk/paintings/francesco-guardi-villa-del-timpano-arcuato-at-paese)，About the work第3–4段 |
| → 位于（`located_at`） | [帕埃塞（Paese）](paese.md) | 角色：建筑所在地；证据：[国家美术馆](https://www.nationalgallery.org.uk/paintings/francesco-guardi-villa-del-timpano-arcuato-at-paese)，About the work第3–4段 |
| ← 描绘地点（`has_subject`，反向投影） | [约翰·斯特兰奇别墅景观（View of John Strange's villa at Paese near Treviso）](../works/francesco-guardi-view-of-john-strange-s-villa-at-paese-near-treviso.md) | 书中图版64题名与国家美术馆对别墅身份的说明相合；不配对某一具体馆藏画作；原断言与来源见发出端作品卡（S1） |

### 关系候选入口

[章前原文关系候选与端点映射](../../../03-processing/patrons-and-painters-front-matter/process/knowledge.md#候选登记映射)
