# 多层级验证级联（Cascade Verification）

> 核心理念：验证的目标不是判断“某个来源可靠吗”，而是判断“该 evidence 最多能支持什么结论”。

本文件以 `collect -> evidence JSONL -> apply` 两阶段流程为准。所有层级都只能先生成 evidence；知识元写回必须由 `verify_apply_evidence.py` 统一执行。

## 一、证据层级模型

### Level A：身份存在 / 术语存在

回答：

```text
实体或术语是否存在？
英文名、标准标题、别名或重定向是否匹配？
是否为消歧义页？
```

适用来源：

```text
Wikipedia REST Summary
Wikipedia Action Search
Wikidata search
```

写回上限：

```text
claim_scope: entity_identity_only / term_existence
evidence_status: partially_verified
confidence: 不得升 high
consensus: 不得升 confirmed
```

### Level B：基础事实

回答：

```text
人物生卒年、职业、国籍是否匹配？
作品作者、年份、馆藏或出版背景是否匹配？
出版物 DOI、ISBN、出版年、出版社是否匹配？
地点坐标、历史名称、机构属性是否匹配？
```

适用来源：

```text
Wikidata EntityData
Wikipedia 页面正文 / infobox
CrossRef
Google Books
WorldCat
archive.org
馆藏记录
```

写回上限：

```text
claim_scope: basic_fact / bibliographic_fact / place_identity
evidence_status: externally_verified
confidence: medium
consensus: tentative
```

只有多个独立来源一致，才允许进一步考虑 `confidence: high` 或 `consensus: confirmed`。

### Level C：知识体系关系

回答：

```text
它为什么属于巴洛克时期意大利艺术与社会（赞助、委托、艺术市场或视觉文化）？
它在本系统层级体系中承担什么角色？
贡献、方法、观念、谱系关系是否有文献支撑？
```

适用来源：

```text
原始摄入文献
学术论文
专著
展览目录
档案记录
权威数据库
```

写回上限：

```text
claim_scope: source_claim / domain_relevance / historiographic_claim
evidence_status: source_backed / externally_verified
confidence: medium/high，取决于多源一致性
consensus: tentative/confirmed，取决于证据数量与冲突情况
```

## 二、验证级联流程

```text
验证流程（级联）：

  L1: Wikipedia REST API
      ├─ 命中 strong + 非消歧义页
      │    -> 生成 entity_identity_only / term_existence evidence
      │    -> 单源最高 partially_verified
      ├─ 命中 weak / 消歧义页
      │    -> blocked，进入候选复核
      └─ 无页面
           -> continue cascade，不得判定“不存在”

  L2: Wikidata API
      ├─ QID + label/description/关键字段匹配
      │    -> 可生成 basic_fact 或 entity_identity_only evidence
      ├─ 仅 QID 命中
      │    -> entity_identity_only，最高 partially_verified
      └─ 字段冲突
           -> disputed / blocked，触发 reconcile 或二次验证

  L3: 浏览器与开放网页核验
      -> 核对页面正文、infobox、重定向、消歧义和上下文

  L4: Google Search / Perplexity
      -> 只作为候选发现或二次确认，需记录来源类型

  L5: Google Scholar / CrossRef
      -> Publication、学术人物、论文和书目信息优先层

  L6: archive.org / Google Books / 馆藏和档案站点
      -> Work、Publication、历史案例和原始图像出处优先层

  L7: 模型内部知识兜底
      -> 只能生成 model_supported 或 source_backed
      -> 不等于 external verification

  全部失败:
      -> evidence_status: unverified
      -> confidence 保持不变或降级
      -> review_due 延后
      -> 记录失败平台、候选和 blocking_reason
```

## 三、状态转换矩阵

| 证据情况 | 写回状态 |
|---|---|
| Wikipedia 无页面 | `unverified` 或无推荐变更；不得判定“不存在” |
| Wikipedia 页面存在但标题弱匹配 | `blocked`，进入候选复核 |
| Wikipedia 标题强匹配，非消歧义页，单源 | `partially_verified` |
| Wikipedia + Wikidata QID 对齐 | `partially_verified`；两者常共享同一知识生态，QID 只作身份锚点 |
| Wikipedia / Wikidata 与独立书目、论文或档案支持同一 claim | 进入 `externally_verified` 语义审核；不得据来源数量自动升 confidence |
| 原始文献支持领域关系，但外部数据库无页面 | `source_backed` |
| 只有 L7 支持 | `model_supported` |
| 多来源严重冲突 | `disputed`，触发 reconcile |

## 四、平台优先级

| 层级 | 平台 | 适用类型 | 输出上限 |
|---|---|---|---|
| L1 | Wikipedia REST API | 人物、地点、术语、事件候选 | identity / term evidence |
| L2 | Wikidata API | 人物、地点、作品、出版物 | identity / basic_fact evidence |
| L3 | 浏览器核验 provider | 全部 | 页面上下文二次确认 |
| L4 | Google Search / Perplexity | 候选发现、补充来源 | source-backed hint |
| L5 | Google Scholar / CrossRef | Publication、学术人物、论文 | bibliographic / scholarly evidence |
| L6 | archive.org / books / 馆藏 | Work、Publication、历史案例 | archival / bibliographic evidence |
| L7 | 模型内部知识 | 未解决的语义候选兜底 | model_supported |

## 五、硬性阻断

1. API 成功不得直接等于 VERIFIED。
2. Wikipedia 单源命中不得推荐 `confidence: high` 或 `consensus: confirmed`。
3. `entity_identity_only` 或 `term_existence` 单源 evidence 不得推荐 `externally_verified`。
4. QID 是身份锚点，不是独立语义来源；命中仍必须检查 label、description、instance of 与适用关键字段。
5. L7 通过只能形成 `model_supported` 或 `source_backed`，不得写成 external verification。
