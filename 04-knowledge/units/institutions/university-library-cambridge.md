---
title: 剑桥大学图书馆（Cambridge University Library）
name_en: Cambridge University Library
type: institution
evidence_status: source_backed
sources:
- citation: Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this printing 2006).
  location: 章前：图片来源；印刷页xvi；OCR L172–172
  sentence_summary: 本书图片来源列明的供片者。
  original_quotes:
  - source_span: lines 172–172
    text: '18a; University Library, Cambridge: 9, 57a; Villani, Bologna: 28a; Eberhard Zwicker, Wiirzburg: 50.'
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_05_List_of_Plates.md
    source_span: lines 172–172; 章前：图片来源；印刷页xvi
- citation: Cambridge University Library, A Journey Around the World Mind (2005), ISBN 0-902205-60-9. https://api.repository.cam.ac.uk/server/api/core/bitstreams/678848c7-a7b2-4a76-a937-ea1bbd5ba59c/content. Accessed 2026-09-14.
  location: 题名页PDF2、馆长导言PDF3／印刷1；年表和出版项PDF38／印刷36，年表页图像已查看
  sentence_summary: 剑桥大学图书馆名称、研究服务与材料收藏；1416是最早明确提及图书馆的记录年，1424为首份目录年，1934迁馆；2005出版项列West Road地址。
created: '2026-09-14'
updated: '2026-09-15'
process_ref: 03-processing/patrons-and-painters-front-matter/process/knowledge.md#机构沿革出版责任与研究支持定稿
relations:
- relation_type: part_of
  target: institutions/university-of-cambridge.md
  evidence_ref:
    doc_id: institutions-university-library-cambridge
    source_file: https://api.repository.cam.ac.uk/server/api/core/bitstreams/678848c7-a7b2-4a76-a937-ea1bbd5ba59c/content
    source_span: 2005馆长导言PDF3／印刷1及PDF38／印刷36年表
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  scope: 大学所属研究图书馆，不与大学合并为同一KU
  role: 所属图书馆
- relation_type: located_at
  target: places/cambridge.md
  evidence_ref:
    doc_id: institutions-university-library-cambridge
    source_file: https://api.repository.cam.ac.uk/server/api/core/bitstreams/678848c7-a7b2-4a76-a937-ea1bbd5ba59c/content
    source_span: PDF38／印刷36出版项
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  scope: 2005年出版项所列West Road城市；不倒填1416年的精确地址
  role: 出版项所列馆址
  time: 2005年记录
---


## 内容

### 描述

**中文：** 剑桥大学的研究图书馆，最早明确文献记录见于1416年；本书列其为图版9和57a的供片者。

**English:** The research library of the University of Cambridge, first explicitly documented in 1416; it is credited as the photographic supplier for plates 9 and 57a in the book.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 原文名称 | University Library, Cambridge | S1 |
| 中文名性质 | 项目工作译名 | 项目命名 |
| 机构全称 | Cambridge University Library | S2 |

### 来源所载信息

| 字段 | 值 | 证据 |
|---|---|---|
| 所供图版 | 9、57a | S1 |
| 供片对应对象 | [《巴贝里尼宫》卷首图](../works/guido-abbatini-frontispiece-of-aedes-barberinae-ad-quirinalem.md)；图版9复制图像 | S1 |
| 供片对应对象 | [《耶路撒冷解放》插图末页](../works/piazzetta-final-plate-of-illustrations-to-gerusalemme-liberata.md)；图版57a复制图像 | S1 |

### 机构与沿革

| 字段 | 值 | 证据 |
|---|---|---|
| 所属大学 | [剑桥大学](university-of-cambridge.md) | S2，馆长导言及年表 |
| 所在地 | [剑桥](../places/cambridge.md) | S1、S2 |
| 最早明确文献记录 | 1416 | S2，印刷36 |
| 首份馆藏目录 | 1424 | S2，印刷36 |
| 迁入新馆年 | 1934 | S2，印刷36 |
| 2005年出版项所列地址 | West Road, Cambridge, CB3 9DR, England | S2，印刷36 |
| 服务 | 收藏、保存并提供研究材料／Collecting, preserving and providing access to research materials | S2，印刷1 |

## 关系与证据

### 身份与外部链接

[馆方2005年出版物](https://api.repository.cam.ac.uk/server/api/core/bitstreams/678848c7-a7b2-4a76-a937-ea1bbd5ba59c/content)（S2，ISBN 0-902205-60-9）。

### 关系记录
| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 组成部分（`part_of`） | [剑桥大学（University of Cambridge）](university-of-cambridge.md) | 角色：所属图书馆；范围：大学所属研究图书馆，不与大学合并为同一KU；证据：[来源](https://api.repository.cam.ac.uk/server/api/core/bitstreams/678848c7-a7b2-4a76-a937-ea1bbd5ba59c/content)；src-7a4785dfb96dd6b8；2005馆长导言PDF3／印刷1及PDF38／印刷36年表 |
| → 位于（`located_at`） | [剑桥（Cambridge）](../places/cambridge.md) | 时间：2005年记录；角色：出版项所列馆址；范围：2005年出版项所列West Road城市；不倒填1416年的精确地址；证据：[来源](https://api.repository.cam.ac.uk/server/api/core/bitstreams/678848c7-a7b2-4a76-a937-ea1bbd5ba59c/content)；src-7a4785dfb96dd6b8；PDF38／印刷36出版项 |
| ← 供应者（`supplier_of`，反向投影） | [《巴贝里尼宫》卷首图（Frontispiece of Aedes Barberinae ad Quirinalem）](../works/guido-abbatini-frontispiece-of-aedes-barberinae-ad-quirinalem.md) | 角色：本书复制图像供片者；范围：《赞助人与画家》图版9的复制图像；不表示作品创作者、所有者或保管者；原断言与证据见发出端卡片“《巴贝里尼宫》卷首图（Frontispiece of Aedes Barberinae ad Quirinalem）”：[来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；haskell-1980-rev-ed；lines 172–172; 章前：图片来源；印刷页xvi |
| ← 供应者（`supplier_of`，反向投影） | [《耶路撒冷解放》插图末页（Final plate of Illustrations to Gerusalemme Liberata）](../works/piazzetta-final-plate-of-illustrations-to-gerusalemme-liberata.md) | 角色：本书复制图像供片者；范围：《赞助人与画家》图版57a的复制图像；不表示作品创作者、所有者或保管者；原断言与证据见发出端卡片“《耶路撒冷解放》插图末页（Final plate of Illustrations to Gerusalemme Liberata）”：[来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；haskell-1980-rev-ed；lines 172–172; 章前：图片来源；印刷页xvi |

### 关系候选入口

[章前原文关系候选与端点映射](../../../03-processing/patrons-and-painters-front-matter/process/knowledge.md#候选登记映射)

[英国供片机构候选与裁决](../../../03-processing/patrons-and-painters-front-matter/process/knowledge.md#英国供片机构与大学图书馆)
