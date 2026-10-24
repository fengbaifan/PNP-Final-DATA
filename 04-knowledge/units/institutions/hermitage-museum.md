---
title: 艾尔米塔什博物馆（Hermitage Museum）
name_en: Hermitage Museum
type: institution
created: '2026-09-13'
updated: 2026-09-14
evidence_status: source_backed
relations: []
sources:
- citation: Wikipedia (en), Caravaggio, revision 1372526492. https://en.wikipedia.org/wiki/Caravaggio. Accessed 2026-09-11.
  location: 与本端点有关的作品、人物或关系段；全文已保存于REV-052
  sentence_summary: 保管《鲁特琴演奏者》艾尔米塔什版本。
- citation: Wikipedia (en), Hermitage Museum. https://en.wikipedia.org/wiki/Hermitage_Museum. Accessed 2026-09-13.
  location: 正文全文已保存于REV-068；本轮定向读取身份、类型及当前作品链字段
  sentence_summary: 核对Hermitage Museum的身份、类型及本轮关系角色。
- citation: Wikidata, Q132783. https://www.wikidata.org/wiki/Q132783. Accessed 2026-09-13.
  location: labels、descriptions、P31及适用标识／sitelink；不机械采纳全部声明
  sentence_summary: 用于Hermitage Museum的同粒度身份核对；QID不验证本卡全部事实。
process_ref: 03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-072-institutions-hermitage-museum
---

## 内容

### 描述

**中文：** 艾尔米塔什博物馆是艺术博物馆。保管《鲁特琴演奏者》艾尔米塔什版本。

**English:** The State Hermitage Museum is an art museum that holds the Hermitage version of The Lute Player.

### 名称与机构信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 规范名 | 艾尔米塔什博物馆／Hermitage Museum | S1–S3（如有） |
| 机构性质 | 艺术博物馆 | S2–S3；无独立页面时据S1限定 |
| 所在地／服务范围 | 圣彼得堡，俄罗斯 | S2–S3 |
| 本轮职能 | 保管《鲁特琴演奏者》艾尔米塔什版本。 | S1 |

### 收藏、管理与使用边界

作品的所有权、保管、展陈建筑和实际安置分别建模。本卡只接受作品来源明确支持的机构角色，不从机构通史递归扩张全部藏品、分馆或负责人。

## 关系与证据

### 关系记录
| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← 雇主（`employer_of`，反向投影） | [拉里萨·萨尔米娜（Larissa Salmina）](../persons/larissa-dedicatee.md) | 时间：1962年时点；角色：威尼斯素描策展人；范围：1962年相识时职务；不推定完整任期；原断言与证据见发出端卡片“拉里萨·萨尔米娜（Larissa Salmina）”：[来源](https://www.thebritishacademy.ac.uk/documents/366/115p227.pdf)；src-82db5ffb1f42b5b4；印刷p.232 |
| ← 保管对象（`holder_of`，反向投影） | [《鲁特琴演奏者》（艾尔米塔什版本）（The Lute Player (Hermitage version)）](../works/caravaggio-lute-player-hermitage.md) | 当前对象记录将The Lute Player (Hermitage version)列由该机构保管；保管不自动等于产权；时间：本轮来源访问时；角色：保管机构；范围：现存；原断言与证据见发出端卡片“《鲁特琴演奏者》（艾尔米塔什版本）（The Lute Player (Hermitage version)）”：[来源](https://support.hermitagemuseum.org/en/projects/caravaggio)；src-438329609128d711；本卡S2；有S4时并参对象字段 |
| ← 所在地（`location_of`，反向投影） | [Canaletto《德·热尔吉伯爵入城图》（Entry of the Comte de Gergy）](../works/canaletto-entry-comte-de-gergy-1725.md) | 时间：Haskell 1956, p. 298 as cited in Haskell 1980, p. 277 n. 5；角色：来源所载作品位置；范围：Haskell 1980 note 5 cites Haskell 1956, p. 298, for “now in the Hermitage”. The cited page was not independently consulted; this is a source-reported location in that publication context, not a verified present-day location.；原断言与证据见发出端卡片“Canaletto《德·热尔吉伯爵入城图》（Entry of the Comte de Gergy）”：[来源](../../../02-sources/02-Markdown/10_CHP-10_intro.md)；haskell-1980-rev-ed；Chapter 10, printed p. 277 n. 5; S2 statement: st-chp10-notes-p277n5-gergy-location |
| ← 所在地（`location_of`，反向投影） | [Canaletto《博拉尼奥伯爵入城图》（Entry of the Count of Bolagno）](../works/canaletto-entry-count-bolagno-1729.md) | 仅记录Haskell注5所报位置；不据被引的Moschini页扩写事实，不声称当前馆藏状态已核验；时间：V. Moschini 1954, p. 29, as cited in Haskell 1980, ch. 10, p. 277 n. 5；角色：来源所报作品位置；范围：Haskell注5称“now in the Hermitage”并引V. Moschini 1954年页29；被引页未独立查阅。时间措辞限于Haskell来源语境，不表示现址已核验。；原断言与证据见发出端卡片“Canaletto《博拉尼奥伯爵入城图》（Entry of the Count of Bolagno）”：[来源](../../../02-sources/02-Markdown/10_CHP-10_intro.md)；haskell-1980-rev-ed；Chapter 10, printed p. 277 n. 5 (L499; PDF physical p. 2); S2 statement: st-chp10-notes-p277n5-bolagno-location |
| ← 所在地（`location_of`，反向投影） | [交予尚特卢的《绘画论》文本与普桑绘图（Set of the Trattato and Poussin Drawings Given to Chantelou）](../archives/chantelou-trattato-and-poussin-drawings-set.md) | Repository statement is Haskell-reported, not independently checked.；角色：reported repository for Chantelou publication version；范围：Haskell reports that the version given to Chantelou for publication is in the Hermitage, Leningrad. The cited copy/version is scoped explicitly.；原断言与证据见发出端卡片“交予尚特卢的《绘画论》文本与普桑绘图（Set of the Trattato and Poussin Drawings Given to Chantelou）”：[来源](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)；haskell-1980-rev-ed；Chapter 4, printed p.106, footnote 2, line 259; S2 statement: st-chp4-sec-ii-notes-l255-259-fn259-chantelou-copy-location |

### 身份与外部链接

- [Wikipedia：Hermitage Museum](https://en.wikipedia.org/wiki/Hermitage_Museum)
- [Wikidata Q132783](https://www.wikidata.org/wiki/Q132783)
