---
title: 大都会艺术博物馆（Metropolitan Museum of Art）
name_en: Metropolitan Museum of Art
type: institution
created: '2026-09-13'
updated: 2026-09-14
evidence_status: source_backed
relations: []
sources:
- citation: Wikipedia (en), Caravaggio, revision 1372526492. https://en.wikipedia.org/wiki/Caravaggio. Accessed 2026-09-11.
  location: 与本端点有关的作品、人物或关系段；全文已保存于REV-052
  sentence_summary: 本轮只连接其直接保管的卡拉瓦乔作品。
- citation: Wikipedia (en), Metropolitan Museum of Art. https://en.wikipedia.org/wiki/Metropolitan_Museum_of_Art. Accessed 2026-09-13.
  location: 正文全文已保存于REV-068；本轮定向读取身份、类型及当前作品链字段
  sentence_summary: 核对Metropolitan Museum of Art的身份、类型及本轮关系角色。
- citation: Wikidata, Q160236. https://www.wikidata.org/wiki/Q160236. Accessed 2026-09-13.
  location: labels、descriptions、P31及适用标识／sitelink；不机械采纳全部声明
  sentence_summary: 用于Metropolitan Museum of Art的同粒度身份核对；QID不验证本卡全部事实。
- citation: Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this
    printing 2006).
  location: 章前：图版目录；印刷页xiv；OCR L96–96
  sentence_summary: 图版34目录将其记为书中收藏／保管者。
  original_quotes:
  - source_span: lines 96–96
    text: '34 Velasquez: Juan de Pareja (Metropolitan Museum, New York)'
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_05_List_of_Plates.md
    source_span: lines 96–96; 章前：图版目录；印刷页xiv
- citation: Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this
    printing 2006).
  location: 章前：图版目录；印刷页xiv；OCR L97–99
  sentence_summary: 图版35a目录将其记为书中收藏／保管者。
  original_quotes:
  - source_span: lines 97–99
    text: '35 a Rembrandt: Aristotle contemplating the bust of Homer

      (Metropolitan Museum of Art, New York. Purchase, various funds

      and donors, 1961)'
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_05_List_of_Plates.md
    source_span: lines 97–99; 章前：图版目录；印刷页xiv
process_ref: 03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-072-institutions-metropolitan-museum-of-art
---

## 内容

### 描述

**中文：** 大都会艺术博物馆是艺术博物馆。收藏卡拉瓦乔作品。

**English:** The Metropolitan Museum of Art is an art museum connected here only to the Caravaggio works it directly holds.

### 名称与机构信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 规范名 | 大都会艺术博物馆／Metropolitan Museum of Art | S1–S3（如有） |
| 机构性质 | 艺术博物馆 | S2–S3；无独立页面时据S1限定 |
| 所在地／服务范围 | 纽约，美国 | S2–S3 |
| 本轮职能 | 收藏卡拉瓦乔作品。 | S1 |

### 收藏、管理与使用边界

作品的所有权、保管、展陈建筑和实际安置分别建模。本卡只接受作品来源明确支持的机构角色，不从机构通史递归扩张全部藏品、分馆或负责人。


### 章前材料中的记录

| 字段 | 值 | 证据 |
|---|---|---|
| 图版34角色 | 书中收藏／保管者 | S4 |
| 图版34相关对象 | [胡安·德·帕雷哈肖像](../works/velasquez-juan-de-pareja.md)；书中收藏／保管者 | S4 |
| 图版35a角色 | 书中收藏／保管者 | S5 |
| 图版35a相关对象 | [凝视荷马像的亚里士多德](../works/rembrandt-aristotle-contemplating-the-bust-of-homer.md)；书中收藏／保管者 | S5 |

## 关系与证据

### 关系记录
| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← 保管对象（`holder_of`，反向投影） | [《圣彼得不认主》（The Denial of Saint Peter）](../works/caravaggio-denial-saint-peter.md) | 当前对象记录将The Denial of Saint Peter列由该机构保管；保管不自动等于产权；时间：本轮来源访问时；角色：保管机构；范围：现存；原断言与证据见发出端卡片“《圣彼得不认主》（The Denial of Saint Peter）”：[来源](https://en.wikipedia.org/wiki/The_Denial_of_Saint_Peter_(Caravaggio))；held-by-institutions-metropolitan-museum-of-art-md；本卡S2；有S4时并参对象字段 |
| ← 保管对象（`holder_of`，反向投影） | [《音乐家们》（The Musicians）](../works/caravaggio-musicians.md) | 当前对象记录将The Musicians列由该机构保管；保管不自动等于产权；时间：本轮来源访问时；角色：保管机构；范围：现存；原断言与证据见发出端卡片“《音乐家们》（The Musicians）”：[来源](https://en.wikipedia.org/wiki/The_Musicians_(Caravaggio))；held-by-institutions-metropolitan-museum-of-art-md；本卡S2；有S4时并参对象字段 |

### 身份与外部链接

- [Wikipedia：Metropolitan Museum of Art](https://en.wikipedia.org/wiki/Metropolitan_Museum_of_Art)
- [Wikidata Q160236](https://www.wikidata.org/wiki/Q160236)
