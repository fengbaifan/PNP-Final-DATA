---
title: "圣乌巴尔多圣殿（Basilica of Sant'Ubaldo）"
name_en: "Basilica of Sant'Ubaldo"
type: place
created: 2026-09-25
updated: 2026-09-25
evidence_status: source_backed
sources:
- citation: "Paolo Salciarini, with Anna Radicchi, Guida alla Basilica: Santuario di Sant'Ubaldo, 4th reprint (February 2015). https://www.eugubininelmondo.com/public/GuidaBasilica2015.pdf Accessed 2026-09-25."
  location: "PDF pp.1, 6–14, 20–21"
  sentence_summary: "圣殿自称Basilica di Sant'Ubaldo；指南记载其在Gubbio的Ingino山、1919年获小宗座圣殿地位，并记作品与堂内历史。"
  evidence_ref:
    doc_id: santubaldo-basilica-guide-2015
    source_file: https://www.eugubininelmondo.com/public/GuidaBasilica2015.pdf
    source_span: "PDF pp.1, 6–14, 20–21"
  original_quotes:
  - source_span: "PDF p.1, cover"
    text: "Basilica di S. Ubaldo"
- citation: "Wikipedia (en), 'Basilica of Sant'Ubaldo, Gubbio,' revision 1324716422. https://en.wikipedia.org/wiki/Basilica_of_Sant'Ubaldo,_Gubbio Accessed 2026-09-25."
  location: "lead; history and artworks sections read"
  sentence_summary: "确认这是位于Gubbio城外Ingino山上的天主教教堂；导言身份段用于页面配对，不作为整卡事实来源。"
  evidence_ref:
    doc_id: enwiki-basilica-of-santubaldo-rev-1324716422
    source_file: https://en.wikipedia.org/wiki/Basilica_of_Sant'Ubaldo,_Gubbio
    source_span: "lead, revision 1324716422"
  original_quotes:
  - source_span: "lead, revision 1324716422"
    text: "The Basilica of Sant'Ubaldo is a Roman Catholic church atop Mount Ingino"
- citation: "Wikipedia (it), 'Basilica di Sant'Ubaldo,' revision 150331520. https://it.wikipedia.org/wiki/Basilica_di_Sant'Ubaldo Accessed 2026-09-25."
  location: "lead; history and church description read"
  sentence_summary: "与英文页面、Wikidata名称、类型和地点相符；双向配对只确认端点身份。"
  evidence_ref:
    doc_id: itwiki-basilica-di-santubaldo-rev-150331520
    source_file: https://it.wikipedia.org/wiki/Basilica_di_Sant'Ubaldo
    source_span: "lead, revision 150331520"
  original_quotes:
  - source_span: "lead, revision 150331520"
    text: "La basilica di Sant'Ubaldo è un luogo di culto cattolico situato a Gubbio"
- citation: "Wikidata, Q3635744, revision 2159739749. https://www.wikidata.org/wiki/Q3635744 Accessed 2026-09-25."
  location: "labels, descriptions, instance-of, location and enwiki/itwiki sitelinks"
  sentence_summary: "英语和意大利语Wikipedia页面均以该QID为页面项目，Wikidata同时列出两条对应sitelink；用于实体身份配对。"
  evidence_ref:
    doc_id: wikidata-Q3635744-rev-2159739749
    source_file: https://www.wikidata.org/wiki/Q3635744
    source_span: "identity fields and enwiki/itwiki sitelinks"
process_ref: 03-processing/patrons-and-painters-chp-1/process/knowledge.md#salvio-savini-pala-del-voto及圣乌巴尔多圣殿端点补足2026-09-25
relations:
- relation_type: located_at
  target: places/gubbio.md
  evidence_ref:
    doc_id: itwiki-basilica-di-santubaldo-rev-150331520
    source_file: https://it.wikipedia.org/wiki/Basilica_di_Sant'Ubaldo
    source_span: "lead: located at Gubbio, on Monte Ingino"
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  role: "basilica location"
  scope: "The basilica is located at Gubbio; this does not assert historical jurisdiction or ownership."
---

## 内容

### 描述

**中文：**圣乌巴尔多圣殿（Basilica di Sant'Ubaldo）是位于翁布里亚大区古比奥城外、Ingino山上的天主教圣所；1919年获小宗座圣殿地位。2015年指南记载，现存建筑工程始于1513年，约1527年完成。（S1–S3）

**English:** The Basilica of Sant'Ubaldo (Basilica di Sant'Ubaldo) is a Catholic sanctuary on Mount Ingino outside Gubbio in Umbria. It was raised to the dignity of a minor basilica in 1919. The 2015 guide dates the present building campaign to 1513–c.1527. (S1–S3)

### 地点字段

| 字段 | 内容 | 依据 |
|---|---|---|
| 名称 | Basilica di Sant'Ubaldo；Basilica of Sant'Ubaldo | S1–S4 |
| 对象类型 | 教堂／圣所；建筑空间归入place | S1–S3 |
| 所在地 | Ingino山，古比奥，翁布里亚，意大利 | S1–S3 |
| 宗教属性 | 罗马天主教 | S2–S3 |
| 地位 | 1919年获小宗座圣殿地位 | S1 |
| 建筑时间 | 现存建筑工程1513年开始，约1527年完成 | S1；按指南表述 |
| 相关作品 | [《还愿祭坛画》（Pala del Voto）](../works/salvio-savini-pala-del-voto.md)，2022年指南列于还愿小堂 | S1–S2 |

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 位于（`located_at`） | [古比奥（Gubbio）](gubbio.md) | 地点关系；意大利语页面导言及Q3635744身份配对确认对应对象；不延伸为历史管辖或所有权；S3–S4 |
| ← 安置于此（`location_of`，反向投影） | [《还愿祭坛画》（Pala del Voto）](../works/salvio-savini-pala-del-voto.md) | 2022年圣殿指南明列其在还愿小堂；关系的原断言及位置范围见作品卡；不推定首次安置时间 |

### 身份与外部链接

- [Wikidata Q3635744](https://www.wikidata.org/wiki/Q3635744)
- [Wikipedia（en）](https://en.wikipedia.org/wiki/Basilica_of_Sant'Ubaldo,_Gubbio)
- [Wikipedia（it）](https://it.wikipedia.org/wiki/Basilica_di_Sant'Ubaldo)
