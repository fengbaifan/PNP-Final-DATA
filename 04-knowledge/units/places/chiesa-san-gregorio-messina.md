---
title: "墨西拿圣额我略堂（Church of San Gregorio, Messina）"
name_en: Church of San Gregorio, Messina
type: place
created: 2026-09-25
updated: 2026-09-25
evidence_status: source_backed
relations:
- relation_type: located_at
  target: places/messina.md
  note: 市级文化导览将圣额我略堂与相连修院列入墨西拿城市历史。
  evidence_ref:
    doc_id: metropolitan-city-messina-museum-history
    source_file: https://visitme.comune.messina.it/en/node/433
    source_span: 历史段；圣额我略堂与相连修院；1880年及1908年事件
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 所在城市
  scope: 历史建筑地点；不指代修院法人
sources:
- citation: "Wikipedia (it), Chiesa di San Gregorio (Messina), revision 150392543, https://it.wikipedia.org/wiki/Chiesa_di_San_Gregorio_(Messina). Accessed 2026-09-25."
  location: "全文；Storia、Interno及Monastero di San Gregorio，L65–197；本轮已读完整页面"
  sentence_summary: "识别该堂为Messina历史教堂；记1588年新堂、1908年震灾，以及1665年Guercino Madonna del Carmine画作位于堂内对应龛位。"
- citation: "Wikidata, Q3670706, https://www.wikidata.org/wiki/Q3670706. Accessed 2026-09-25."
  location: "英文标签和描述、实体类型及itwiki sitelink；通过API核对"
  sentence_summary: "标签San Gregorio、描述为意大利Messina教堂建筑；itwiki sitelink为Chiesa di San Gregorio (Messina)，未列enwiki。"
- citation: "Fondazione Federico Zeri, entry 57026, Barbieri Giovan Francesco, work 58737, https://catalogo.fondazionezeri.unibo.it/entry/work/58737/. Accessed 2026-09-25."
  location: "Locations；Last known：Chiesa di S. Gregorio, Messina"
  sentence_summary: "记录为圭尔奇诺1665年祭坛画的末知地点；该字段不说明委托法人或原定安置。"
- citation: "Metropolitan City of Messina, Il Museo Regionale di Messina, https://visitme.comune.messina.it/en/node/433. Accessed 2026-09-25."
  location: "San Gregorio教堂与修院历史段"
  sentence_summary: "记载1880年市立博物馆迁入San Gregorio教堂相连修院，1908年地震部分毁坏教堂。"
- citation: "Regione Siciliana, La città scomparsa: Chiesa e Monastero di San Gregorio, https://www.regione.sicilia.it/la-regione-informa/bbcc-messina-450deg-caravaggio-21-al-26-dicembre-si-entra-al-mume-2-euro. Accessed 2026-09-25."
  location: "San Gregorio教堂和修院历史说明"
  sentence_summary: "称墨西拿San Gregorio教堂与修院建于16世纪下半叶，修院曾为市立博物馆所在地。"
process_ref: 03-processing/patrons-and-painters-chp-1/process/knowledge.md#圣额我略堂末知地点与城市端点2026-09-25
---

## 内容

### 描述

**中文：** 墨西拿历史上的圣额我略堂，圭尔奇诺1665年祭坛画的末知地点。市级资料记载其相连修院自1880年用于市立博物馆，教堂于1908年地震中部分毁坏。

**English:** The historic Church of San Gregorio in Messina, recorded as the last-known location of Guercino’s 1665 altarpiece. Municipal records state that its attached monastery was used for the civic museum from 1880 and that the church was partly destroyed in the 1908 earthquake.

### 地点与建筑信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 地点性质 | 历史教堂建筑 | S1–S3 |
| 所在城市 | [墨西拿（Messina）](messina.md) | S1、S2 |
| 建筑沿革 | 现址新堂建于1588年；教堂与修院同属San Gregorio建筑组 | S1、S4 |
| 1908年状态 | 地震后严重受损，后颁布拆除令 | S1；市级来源概称部分毁坏 |
| 内部空间／作品 | [加尔默罗圣母小堂](chiesa-san-gregorio-cappella-madonna-carmine.md)位于右侧横翼北墙；龛位曾有Guercino 1665年画作 | S1；不由此确定委托法人 |
| 相关作品地点记录 | Zeri另将该画列为San Gregorio堂末知地点 | S3 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 位于（`located_at`） | [墨西拿（Messina）](messina.md) | 市级文化导览所载历史建筑地点；不指代修院法人；证据：[来源](https://visitme.comune.messina.it/en/node/433)；metropolitan-city-messina-museum-history；历史段；San Gregorio教堂与相连修院 |
| ← 内含（`location_of`，反向投影） | [圣额我略堂加尔默罗圣母小堂（Chapel of the Madonna del Carmine, Church of San Gregorio, Messina）](chiesa-san-gregorio-cappella-madonna-carmine.md) | 历史内部空间，右侧横翼北墙；原断言与证据见发出端卡片：[来源](https://it.wikipedia.org/wiki/Chiesa_di_San_Gregorio_(Messina))；chiesa-san-gregorio-messina-wikipedia-it；页面版本150392543；L169–170 |

### 作品地点入口

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← 末知地点（`located_at`，反向投影） | [圭尔奇诺《圣德肋撒从加尔默罗圣母领受会衣》（Guercino’s Saint Teresa Receiving the Habit from Our Lady of Mount Carmel）](../works/guercino-sicilian-altarpiece-1665.md) | Zeri记为末知地点；Wikipedia另定位至堂内Madonna del Carmine祭坛龛位。此地点不单独证明1665年委托法人或作品原定安置；原断言与证据见发出端卡片：[来源](https://catalogo.fondazionezeri.unibo.it/entry/work/58737/)；zeri-work-58737；Locations：Last known |

### 身份与外部链接

| 字段 | 值／链接 | 核对范围 |
|---|---|---|
| Wikipedia | [Chiesa di San Gregorio (Messina)](https://it.wikipedia.org/wiki/Chiesa_di_San_Gregorio_(Messina)) | 意大利语页面全文已读；无enwiki对应 |
| Wikidata | [Q3670706](https://www.wikidata.org/wiki/Q3670706) | Wikipedia入口指向该QID；条目反向itwiki sitelink标题完全匹配，类型描述为Messina教堂建筑 |
