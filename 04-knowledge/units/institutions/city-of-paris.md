---
title: 巴黎市政当局（City of Paris）
name_en: City of Paris
type: institution
evidence_status: source_backed
sources:
- citation: Musée Cognacq-Jay, History of the museum. https://www.museecognacqjay.paris.fr/en/museum/history-museum. Accessed 2026-09-15.
  location: 完整正文及1929年图录序言的网页引文
  sentence_summary: Cognacq在1925年展示私人收藏；1928年去世后巴黎市作为遗赠受益主体推进博物馆，1929-06-04开馆，1990年迁入Hôtel Donon。
- citation: Paris Musées, The musée Cognacq-Jay. https://parismuseescollections.paris.fr/en/the-musee-cognacq-jay. Accessed 2026-09-15.
  location: 完整馆藏概述正文
  sentence_summary: 馆藏由Ernest Cognacq及妻Marie-Louise Jay共同形成，1928年遗赠给巴黎市；收藏以18世纪作品为主。
- citation: Paris Musées, Le Banquet de Cléopâtre, J 104. https://www.parismuseescollections.paris.fr/fr/musee-cognacq-jay/oeuvres/le-banquet-de-cleopatre. Accessed 2026-09-15.
  location: 完整对象字段、图像学、历史及取得信息；HTTP200读取
  sentence_summary: J 104为Tiepolo巴黎预备版本，取得方式为遗赠，遗赠者Cognacq, Ernest，取得年1928，保管机构Musée Cognacq-Jay。
created: '2026-09-15'
updated: '2026-09-15'
process_ref: 03-processing/patrons-and-painters-front-matter/process/knowledge.md#肖像配对与遗赠主体补齐
relations:
- relation_type: located_at
  target: places/paris.md
  evidence_ref:
    doc_id: institutions-city-of-paris
    source_file: https://parismuseescollections.paris.fr/en/the-musee-cognacq-jay
    source_span: 馆藏概述：City of Paris
  review_status: evidence_backed_relation
  relation_source: explicit
  bidirectional_required: false
  scope: 遗赠行政主体对应巴黎城市；不是两个同类地理实体
  role: 对应市政城市
---

## 内容

### 描述

**中文：** 作为市政主体的巴黎市，是科涅克1928年收藏遗赠的接收方；遗赠收藏随后由科涅克—杰博物馆保管。

**English:** The City of Paris, acting as a municipal authority, received Cognacq’s art bequest in 1928; the bequeathed collection was subsequently held by Musée Cognacq-Jay.

### 名称与边界

| 字段 | 值 | 证据 |
|---|---|---|
| 法文名称 | Ville de Paris | S1、S2 |
| 英文名称 | City of Paris | S1、S2 |
| 对象类型 | 市政行政主体 | S1，遗赠受益主体 |
| 对应城市 | [巴黎](../places/paris.md) | S1、S2 |
| 中文名性质 | 项目描述性译名 | 项目命名 |

### 收藏事务

| 字段 | 值 | 证据 |
|---|---|---|
| 1928年角色 | 科涅克收藏遗赠的受益主体 | S1、S2 |
| 遗赠人 | [泰奥多尔—埃内斯特·科涅克](../persons/ernest-cognacq.md) | S1 |
| 具体作品 | [提埃坡罗《克娄巴特拉的宴会》，J 104](../works/tiepolo-banquet-cognacq-jay.md) | S1–S3 |
| 保管馆 | [科涅克—杰博物馆](musee-cognacq-jay.md) | S1–S3 |

## 关系与证据

### 身份与外部链接

[馆方历史：遗赠受益主体](https://www.museecognacqjay.paris.fr/en/museum/history-museum)（S1）；[Paris Musées收藏概述](https://parismuseescollections.paris.fr/en/the-musee-cognacq-jay)（S2）。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| → 位于（`located_at`） | [巴黎（Paris）](../places/paris.md) | 角色：对应市政城市；范围：遗赠行政主体对应巴黎城市；不是两个同类地理实体；证据：[来源](https://parismuseescollections.paris.fr/en/the-musee-cognacq-jay)；institutions-city-of-paris；馆藏概述：City of Paris |
| ← 取得者（`acquirer_of`，反向投影） | [克娄巴特拉的宴会：科涅克—杰藏本（The Banquet of Cleopatra, Musée Cognacq-Jay version）](../works/tiepolo-banquet-cognacq-jay.md) | 时间：1928；角色：遗赠受益主体；范围：J 104随Cognacq收藏于1928年遗赠给巴黎市；Musée Cognacq-Jay为保管馆，1929年开馆；原断言与证据见发出端卡片“克娄巴特拉的宴会：科涅克—杰藏本（The Banquet of Cleopatra, Musée Cognacq-Jay version）”：[来源](https://www.museecognacqjay.paris.fr/en/museum/history-museum)；cognacq-jay-museum-history；The museum located Boulevard des Capucines：City of Paris为遗赠受益主体；具体J 104见本卡取得记录 |
