---
title: 狄安娜狩猎（Hunt of Diana）
name_en: Hunt of Diana
type: work
evidence_status: source_backed
sources:
- citation: Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this
    printing 2006).
  location: 章前：图版目录；印刷页xii；OCR L47–47
  sentence_summary: 《赞助人与画家》图版07目录所记的《狄安娜狩猎》艺术对象。
  original_quotes:
  - source_span: lines 47–47
    text: '7 Domenichino: Hunt of Diana {Villa Borghese, Rome)'
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_05_List_of_Plates.md
    source_span: lines 47–47; 章前：图版目录；印刷页xii
- citation: Galleria Borghese, The hunting of Diana, https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana. Accessed 2026-09-25.
  location: Object details; Catalogue entry, paragraphs 1, 2, 12, and 14
  sentence_summary: Identifies the painting as 1616–17, oil on canvas, 225×320 cm, inventory 053; commissioned by Pietro Aldobrandini for the Frascati villa, taken for Scipione Borghese in 1617, and purchased by the Italian State in 1902. The 150 scudi payment covered this work and the Cumaean Sibyl together. Catalogue entry also names the later Venturini engraving and Giacomo Rospigliosi dedication.
- citation: Galleria Borghese, Room 19 – Helen and Paris Room, https://galleriaborghese.cultura.gov.it/en/il-museo/la-villa/sala-19-sala-di-elena-e-paride/. Accessed 2026-09-25.
  location: Room description and works displayed
  sentence_summary: Identifies Room 19 as the Helen and Paris Room and lists The Hunting of Diana by Domenichino among displayed paintings.
- citation: Regione Lazio, Ville tuscolane, residenze d’arte e natura, Villa Aldobrandini. https://www.regione.lazio.it/sites/default/files/2021-04/descrizione-ville-tuscolane.pdf. Accessed 2026-09-25.
  location: Villa Aldobrandini subsection
  sentence_summary: Identifies Villa Aldobrandini as the Frascati villa and records it was given to Cardinal Pietro Aldobrandini; used with the Galleria's Frascati-villa statement to resolve the intended site.
created: '2026-09-14'
updated: '2026-09-25'
process_ref: 03-processing/patrons-and-painters-front-matter/process/knowledge.md#狄安娜狩猎委托版画与陈列关系补足
relations:
- relation_type: created_by
  target: persons/domenichino.md
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_05_List_of_Plates.md
    source_span: lines 47–47; 章前：图版目录；印刷页xii
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 原书署名作者
  scope: 图版07所列作品；建筑位置不自动转为博物馆产权或创作地点
- relation_type: located_at
  target: places/villa-borghese.md
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_05_List_of_Plates.md
    source_span: lines 47–47; 章前：图版目录；印刷页xii
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 书中建筑位置
  scope: 图版07所列作品；建筑位置不自动转为博物馆产权或创作地点
  time: 本书所述时点
- relation_type: commissioned_by
  target: persons/pietro-aldobrandini.md
  evidence_ref:
    doc_id: galleria-borghese-hunting-of-diana
    source_file: https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana
    source_span: Catalogue entry, paragraphs 1–2
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 委托人
  scope: 博尔盖塞美术馆称作品原为其委托；区分其与后来的取得者Scipione Borghese
- relation_type: intended_for
  target: places/villa-aldobrandini-frascati.md
  evidence_ref:
    doc_id: galleria-borghese-hunting-of-diana
    source_file: https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana
    source_span: Catalogue entry, paragraphs 1–2; intended destination named as the villa at Frascati
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 原定安置地
  scope: 原定用途不等于实际安置；Frascati villa与Villa Aldobrandini的地点识别另由地区官方资料支持
- relation_type: acquired_by
  target: persons/cardinal-borghese-ch1.md
  evidence_ref:
    doc_id: galleria-borghese-hunting-of-diana
    source_file: https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana
    source_span: Object details, Provenance; Catalogue entry, paragraphs 1–2
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 取得者；馆方叙述为强行取走后付款
  scope: 1617年取得；150 scudi是《狄安娜狩猎》与《库迈女先知》两件作品合计，争议的其他付款记载不归并为单件确定价款
  time: '1617'
- relation_type: acquired_by
  target: institutions/kingdom-of-italy.md
  evidence_ref:
    doc_id: galleria-borghese-hunting-of-diana
    source_file: https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana
    source_span: "Object details, Provenance: purchased by Italian State, 1902"
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 取得者；馆方原称意大利国家
  scope: 1902年“意大利国家”记录按当时存续的意大利王国定位；不表示当前产权
  time: '1902'
- relation_type: held_by
  target: institutions/galleria-borghese.md
  evidence_ref:
    doc_id: galleria-borghese-hunting-of-diana
    source_file: https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana
    source_span: Object details, Inventory 053 and Location, current catalogue record
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 馆藏保管机构
  scope: 依据馆方当前对象目录；不等同法律所有权
  time: 2026-09-25访问时
- relation_type: located_at
  target: places/room-19-helen-and-paris.md
  evidence_ref:
    doc_id: galleria-borghese-hunting-of-diana
    source_file: https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana
    source_span: Object details, Location; confirmed by Galleria Borghese Room 19 page
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 当前陈列展厅
  scope: 当前馆方目录所列位置；区别于原定Frascati安置地
  time: 2026-09-25访问时
- relation_type: located_at
  target: places/rome.md
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_05_List_of_Plates.md
    source_span: lines 47–47; 章前：图版目录；印刷页xii
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: 书中所在城市
  scope: 图版07所列作品；建筑位置不自动转为博物馆产权或创作地点
  time: 本书所述时点
---

## 内容

### 描述

**中文：** 多梅尼基诺于1616–17年创作的布面油画，现藏博尔盖塞美术馆；原为枢机皮耶特罗·阿尔多布兰迪尼委托，原定用于弗拉斯卡蒂别墅，后于1617年被枢机斯奇皮奥内·博尔盖塞取得。

**English:** An oil painting on canvas by Domenichino, dated 1616–17 and held by the Galleria Borghese; commissioned by Cardinal Pietro Aldobrandini for a villa at Frascati and acquired by Cardinal Scipione Borghese in 1617.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 原文名称 | Hunt of Diana | S1 |
| 中文名性质 | 项目工作译名 | 项目命名 |

### 来源所载信息

| 字段 | 值 | 证据 |
|---|---|---|
| 图版编号 | 07 | S1 |
| 创作者 | [多梅尼基诺](../persons/domenichino.md) | S1 |
| 创作年代 | 1616–17 | S2 |
| 媒材 | 布面油画 | S2 |
| 尺寸 | 225 × 320 cm | S2 |
| 馆藏号 | 053 | S2 |
| 委托人 | [皮耶特罗·阿尔多布兰迪尼](../persons/pietro-aldobrandini.md) | S2 |
| 原定安置地 | [弗拉斯卡蒂的阿尔多布兰迪尼别墅](../places/villa-aldobrandini-frascati.md) | S2、S4 |
| 1617年取得者 | [斯奇皮奥内·博尔盖塞](../persons/cardinal-borghese-ch1.md) | S2 |
| 1902年取得者 | [意大利王国](../institutions/kingdom-of-italy.md)（馆方称意大利国家） | S2 |
| 当前保管机构 | [博尔盖塞美术馆](../institutions/galleria-borghese.md) | S2 |
| 当前陈列 | [海伦与帕里斯厅，19号厅](../places/room-19-helen-and-paris.md) | S2–S3 |
| 书中位置 | [博尔盖塞别墅](../places/villa-borghese.md) | S1 |
| 书中位置 | [罗马](../places/rome.md) | S1 |

### 取得与安置沿革

| 时间 | 事件 | 证据 |
|---|---|---|
| 原定 | 皮耶特罗·阿尔多布兰迪尼委托；原定用于弗拉斯卡蒂别墅 | S2 |
| 1617 | 斯奇皮奥内·博尔盖塞取得；馆方记录画家获150斯库多，但该款对应本画与《库迈女先知》两件作品 | S2 |
| 1902 | 意大利国家购入 | S2 |
| 现状 | 博尔盖塞美术馆目录列藏于馆内19号海伦与帕里斯厅 | S2–S3 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 创作者（`created_by`） | [多梅尼科·赞皮耶里（Domenico Zampieri）](../persons/domenichino.md) | 角色：原书署名作者；范围：图版07所列作品；建筑位置不自动转为博物馆产权或创作地点；证据：[来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；haskell-1980-rev-ed；lines 47–47; 章前：图版目录；印刷页xii |
| → 位于（`located_at`） | [博尔盖塞别墅（Villa Borghese）](../places/villa-borghese.md) | 时间：本书所述时点；角色：书中建筑位置；范围：图版07所列作品；建筑位置不自动转为博物馆产权或创作地点；证据：[来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；haskell-1980-rev-ed；lines 47–47; 章前：图版目录；印刷页xii |
| → 由其委托（`commissioned_by`） | [皮埃特罗·阿尔多布兰迪尼（Pietro Aldobrandini）](../persons/pietro-aldobrandini.md) | 角色：委托人；范围：博尔盖塞美术馆称作品原为其委托；区分其与后来的取得者Scipione Borghese；证据：[来源](https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana)；Catalogue entry, paragraphs 1–2 |
| → 拟用于（`intended_for`） | [阿尔多布兰迪尼别墅（Villa Aldobrandini, Frascati）](../places/villa-aldobrandini-frascati.md) | 角色：原定安置地；范围：原定用途不等于实际安置；Frascati villa与Villa Aldobrandini的地点识别另由地区官方资料支持；证据：[来源](https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana)；Catalogue entry, paragraphs 1–2; intended destination named as the villa at Frascati |
| → 由其取得（`acquired_by`） | [希皮奥内·博尔盖塞枢机（Cardinal Scipione Borghese）](../persons/cardinal-borghese-ch1.md) | 时间：1617；角色：取得者；馆方叙述为强行取走后付款；范围：1617年取得；150 scudi是《狄安娜狩猎》与《库迈女先知》两件作品合计，争议的其他付款记载不归并为单件确定价款；证据：[来源](https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana)；Object details, Provenance; Catalogue entry, paragraphs 1–2 |
| → 由其取得（`acquired_by`） | [意大利王国（Kingdom of Italy）](../institutions/kingdom-of-italy.md) | 时间：1902；角色：取得者；馆方原称意大利国家；范围：1902年“意大利国家”记录按当时存续的意大利王国定位；不表示当前产权；证据：[来源](https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana)；Object details, Provenance: purchased by Italian State, 1902 |
| → 由其保管（`held_by`） | [博尔盖塞美术馆（Galleria Borghese）](../institutions/galleria-borghese.md) | 时间：2026-09-25访问时；角色：馆藏保管机构；范围：依据馆方当前对象目录；不等同法律所有权；证据：[来源](https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana)；Object details, Inventory 053 and Location, current catalogue record |
| → 位于（`located_at`） | [海伦与帕里斯厅（Room 19, Helen and Paris Room）](../places/room-19-helen-and-paris.md) | 时间：2026-09-25访问时；角色：当前陈列展厅；范围：当前馆方目录所列位置；区别于原定Frascati安置地；证据：[来源](https://www.collezionegalleriaborghese.it/en/opere/the-hunting-of-diana)；Object details, Location; confirmed by Galleria Borghese Room 19 page |
| → 位于（`located_at`） | [罗马（Rome）](../places/rome.md) | 时间：本书所述时点；角色：书中所在城市；范围：图版07所列作品；建筑位置不自动转为博物馆产权或创作地点；证据：[来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；haskell-1980-rev-ed；lines 47–47; 章前：图版目录；印刷页xii |
| ← 来源（`source_of`，反向投影） | [狄安娜与仙女的射箭比赛版画（Diana and Her Nymphs at an Archery Contest）](venturini-diana-hunting-print.md) | 角色：原画图像来源；版画与油画为不同作品对象；原断言与证据见发出端卡片“狄安娜与仙女的射箭比赛版画（Diana and Her Nymphs at an Archery Contest）”：[来源](https://id.rijksmuseum.nl/200266316)；src-9d0a3066d1a95c3a；Creation: after painting by Domenichino |

### 关系候选入口

[章前原文关系候选与端点映射](../../../03-processing/patrons-and-painters-front-matter/process/knowledge.md#候选登记映射)
