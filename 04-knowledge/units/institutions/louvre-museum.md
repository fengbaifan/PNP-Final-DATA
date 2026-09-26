---
title: 卢浮宫博物馆（Louvre Museum）
name_en: Louvre Museum
type: institution
created: '2026-09-13'
updated: 2026-09-14
evidence_status: source_backed
relations: []
sources:
- citation: Wikipedia (en), Caravaggio, revision 1372526492. https://en.wikipedia.org/wiki/Caravaggio. Accessed 2026-09-11.
  location: 与本端点有关的作品、人物或关系段；全文已保存于REV-052
  sentence_summary: 当前保管关系与历史法国王室所有权不混同。
- citation: Wikipedia (en), Louvre. https://en.wikipedia.org/wiki/Louvre. Accessed 2026-09-13.
  location: 正文全文已保存于REV-068；本轮定向读取身份、类型及当前作品链字段
  sentence_summary: 核对Louvre Museum的身份、类型及本轮关系角色。
- citation: Wikidata, Q19675. https://www.wikidata.org/wiki/Q19675. Accessed 2026-09-13.
  location: labels、descriptions、P31及适用标识／sitelink；不机械采纳全部声明
  sentence_summary: 用于Louvre Museum的同粒度身份核对；QID不验证本卡全部事实。
- citation: Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this
    printing 2006).
  location: 章前：图版目录；印刷页xiii；OCR L72–72
  sentence_summary: 图版19a目录将其记为书中收藏／保管者。
  original_quotes:
  - source_span: lines 72–72
    text: '19 a Poussin: Moses trampling on Pharaoh’s crown (Louvre) b Claude: View of Delphi with a Procession
      (Art Institute of Chicago Robert A. Waller Fund)'
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_05_List_of_Plates.md
    source_span: lines 72–72; 章前：图版目录；印刷页xiii
- citation: Francis Haskell, Patrons and Painters, revised and enlarged edition (Yale University Press, 1980; this
    printing 2006).
  location: 章前：图版目录；印刷页xiii；OCR L78–78
  sentence_summary: 图版25目录将其记为书中收藏／保管者。
  original_quotes:
  - source_span: lines 78–78
    text: '25 Orazio Gentileschi: Public Felicity triumphant over Dangers (Louvre) 184'
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/00_05_List_of_Plates.md
    source_span: lines 78–78; 章前：图版目录；印刷页xiii
process_ref: 03-processing/patrons-and-painters-chp-1/process/knowledge.md#rev-072-institutions-louvre-museum
---

## 内容

### 描述

**中文：** 卢浮宫博物馆是法国国家博物馆。当前保管关系与历史法国王室所有权不混同。

**English:** The Louvre Museum is a French national museum; its present custodial role is distinguished from historical ownership by the French Crown.

### 名称与机构信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 规范名 | 卢浮宫博物馆／Louvre Museum | S1–S3（如有） |
| 机构性质 | 法国国家博物馆 | S2–S3；无独立页面时据S1限定 |
| 所在地／服务范围 | 巴黎，法国 | S2–S3 |
| 本轮职能 | 当前保管关系与历史法国王室所有权不混同。 | S1 |

### 收藏、管理与使用边界

作品的所有权、保管、展陈建筑和实际安置分别建模。本卡只接受作品来源明确支持的机构角色，不从机构通史递归扩张全部藏品、分馆或负责人。


### 章前材料中的记录

| 字段 | 值 | 证据 |
|---|---|---|
| 图版19a角色 | 书中收藏／保管者 | S4 |
| 图版19a相关对象 | [摩西践踏法老王冠](../works/poussin-moses-trampling-on-pharaoh-s-crown.md)；书中收藏／保管者 | S4 |
| 图版25角色 | 书中收藏／保管者 | S5 |
| 图版25相关对象 | [公共幸福战胜危难](../works/orazio-gentileschi-public-felicity-triumphant-over-dangers.md)；书中收藏／保管者 | S5 |

## 关系与证据

### 关系记录
| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| ← 雇主（`employer_of`，反向投影） | [皮埃尔·罗森贝格（Pierre Rosenberg）](../persons/pierre-rosenberg.md) | 时间：1962–2001-04-13；角色：助理、策展负责人；后任院长；范围：1962进入绘画部；1994-10至2001-04-13任院长，不将院长头衔倒推至1962；原断言与证据见发出端卡片“皮埃尔·罗森贝格（Pierre Rosenberg）”：[来源](https://www.academie-francaise.fr/les-immortels/pierre-rosenberg)；src-66832422578152de；Biographie前两段 |
| ← 保管对象（`holder_of`，反向投影） | [《圣母之死》（Death of the Virgin）](../works/caravaggio-death-virgin.md) | 当前对象记录将Death of the Virgin列由该机构保管；保管不自动等于产权；时间：本轮来源访问时；角色：保管机构；范围：现存；原断言与证据见发出端卡片“《圣母之死》（Death of the Virgin）”：[来源](https://en.wikipedia.org/wiki/Death_of_the_Virgin_(Caravaggio))；src-9656281414931357；本卡S2；有S4时并参对象字段 |
| ← 保管对象（`holder_of`，反向投影） | [《算命者》（卢浮宫第二版）（The Fortune Teller (Louvre second version)）](../works/caravaggio-fortune-teller-louvre.md) | 当前对象记录将The Fortune Teller (Louvre second version)列由该机构保管；保管不自动等于产权；时间：本轮来源访问时；角色：保管机构；范围：现存；原断言与证据见发出端卡片“《算命者》（卢浮宫第二版）（The Fortune Teller (Louvre second version)）”：[来源](https://collections.louvre.fr/ark:/53355/cl010062329)；src-87aee525cbc6142c；本卡S2；有S4时并参对象字段 |
| ← 保管对象（`holder_of`，反向投影） | [《阿洛夫·德·维尼亚库尔与侍从肖像》（Portrait of Alof de Wignacourt and his Page）](../works/caravaggio-portrait-wignacourt.md) | 当前对象记录将Portrait of Alof de Wignacourt and his Page列由该机构保管；保管不自动等于产权；时间：本轮来源访问时；角色：保管机构；范围：现存；原断言与证据见发出端卡片“《阿洛夫·德·维尼亚库尔与侍从肖像》（Portrait of Alof de Wignacourt and his Page）”：[来源](https://collections.louvre.fr/ark:/53355/cl010062328)；src-247621ddd635cc91；本卡S2；有S4时并参对象字段 |
| ← 保管对象（`holder_of`，反向投影） | [公共幸福战胜危难（Public Felicity triumphant over Dangers）](../works/orazio-gentileschi-public-felicity-triumphant-over-dangers.md) | 时间：本书所述时点；角色：书中保管机构；范围：图版25；原断言与证据见发出端卡片“公共幸福战胜危难（Public Felicity triumphant over Dangers）”：[来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；haskell-1980-rev-ed；lines 78–78; 章前：图版目录；印刷页xiii |
| ← 保管对象（`holder_of`，反向投影） | [摩西践踏法老王冠（Moses trampling on Pharaoh's crown）](../works/poussin-moses-trampling-on-pharaoh-s-crown.md) | 时间：本书所述时点；角色：书中保管机构；范围：图版19a；原断言与证据见发出端卡片“摩西践踏法老王冠（Moses trampling on Pharaoh's crown）”：[来源](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)；haskell-1980-rev-ed；lines 72–72; 章前：图版目录；印刷页xiii |

### 身份与外部链接

- [Wikipedia：Louvre](https://en.wikipedia.org/wiki/Louvre)
- [Wikidata Q19675](https://www.wikidata.org/wiki/Q19675)
