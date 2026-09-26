---
title: 米涅瓦宫（Palazzo della Minerva）
name_en: Palazzo della Minerva
type: place
sub_type: building
evidence_status: source_backed
sources:
- citation: "Senato della Repubblica, Caravaggio – Ritratto di monsignor Maffeo Barberini, 2026 exhibition page. https://www.senato.it/CESUS/2026/caravaggio/. Accessed 2026-09-25."
  location: Exhibition venue and address
  sentence_summary: Names Palazzo della Minerva in Rome as the 2026 exhibition venue at Piazza della Minerva 38, with the portrait displayed in the Sala Capitolare.
- citation: "Senato della Repubblica, Palazzo della Minerva, institutional building brochure. https://www.senato.it/documenti/repository/relazioni/libreria/palazzi_del_Senato.pdf. Accessed 2026-09-25."
  location: Palazzo della Minerva section
  sentence_summary: Identifies the building as a Senate library site.
- citation: "Wikipédia (pt), Palazzo della Minerva, https://pt.wikipedia.org/wiki/Palazzo_della_Minerva. Accessed 2026-09-25."
  location: Lead and history
  sentence_summary: Identifies the specific building on the north side of Piazza della Minerva in Rome; used because no English or Italian Wikipedia article was found.
- citation: "Wikidata, Q58337859, https://www.wikidata.org/wiki/Q58337859. Accessed 2026-09-25."
  location: Label, place type, location and Portuguese Wikipedia sitelink
  sentence_summary: Q58337859 describes Palazzo della Minerva, gives the address Piazza della Minerva 38 and links to the Portuguese Wikipedia page.
created: '2026-09-25'
updated: '2026-09-25'
process_ref: 03-processing/patrons-and-painters-front-matter/process/knowledge.md#马费奥巴贝里尼肖像版本身份与购藏关系补足2026-09-25
relations:
- relation_type: located_at
  target: places/rome.md
  evidence_ref:
    doc_id: senato-maffeo-barberini-exhibition-2026
    source_file: https://www.senato.it/CESUS/2026/caravaggio/
    source_span: venue, address and “Roma” designation
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 建筑所在城市
  scope: Piazza della Minerva 38；与邻接教堂Santa Maria sopra Minerva分别处理
---

## 内容

### 描述

**中文：** 位于罗马Piazza della Minerva 38的建筑，现为意大利参议院图书馆所在地。2026年5月28日至6月21日，卡拉瓦乔《马费奥·巴贝里尼肖像》曾在该建筑内的Sala Capitolare展出。

**English:** A building at Piazza della Minerva 38 in Rome that houses the Library of the Senate. From 28 May to 21 June 2026, Caravaggio’s Portrait of Maffeo Barberini was exhibited in its Sala Capitolare.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 建筑名 | Palazzo della Minerva | S1、S3、S4 |
| 地址 | Piazza della Minerva 38, Rome | S1、S4 |
| 室内展览空间 | Sala Capitolare, Biblioteca del Senato | S1 |
| Wikidata | [Q58337859](https://www.wikidata.org/wiki/Q58337859) | S3、S4；葡萄牙语Wikipedia页面互链；无英语或意大利语条目 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 位于（`located_at`） | [罗马（Rome）](rome.md) | 角色：建筑所在城市；范围：Piazza della Minerva 38；与邻接教堂Santa Maria sopra Minerva分别处理；证据：[来源](https://www.senato.it/CESUS/2026/caravaggio/)；src-708610f012c3469e；venue, address and “Roma” designation |
| ← 所在地（`location_of`，反向投影） | [马费奥·巴贝里尼肖像（Maffeo Barberini）](../works/caravaggio-maffeo-barberini.md) | 时间：2026-05-28–2026-06-21；角色：收购后的临时展出地点；范围：展厅为Palazzo della Minerva内的Sala Capitolare；官网称后续拟移交至Palazzo Barberini，本关系不表示已完成该移交；原断言与证据见发出端卡片“马费奥·巴贝里尼肖像（Maffeo Barberini）”：[来源](https://www.senato.it/CESUS/2026/caravaggio/)；src-708610f012c3469e；exhibition dates and venue; Sala Capitolare, Biblioteca del Senato |
