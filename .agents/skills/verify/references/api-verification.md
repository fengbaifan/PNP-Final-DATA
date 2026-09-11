# API 验证流程

> API 验证只负责生成有限范围 evidence，不负责直接宣告知识元 VERIFIED。

身份、版本与粒度判断由 verify/SKILL.md 规定。下列API字段和写回上限只是现有接口能力，不能代替对实际来源对象的语义比较；Wikipedia—Wikidata双向核对仅在有适用对象时执行，脚本没有自动完成。官方记录可独立支持其范围内的身份或事实，无须等待Wiki配对，但不能扩大其支持范围。

## 一、通用原则

1. API 命中只说明找到候选页面、实体或元数据。
2. API collector 只能输出 evidence JSONL，不得直接写知识元。
3. `recommended_changes` 必须受 `claim_scope` 限制。
4. 单一 API evidence 不得推荐 `confidence: high`、`consensus: confirmed` 或 `source_count +1`。
5. 消歧义页、弱标题匹配、字段冲突必须写入 `blocking_reason`，不得静默覆盖。

## 二、Wikipedia API

### 默认 claim_scope

| 知识元类型 | 默认 claim_scope |
|---|---|
| person | `entity_identity_only` |
| family | `entity_identity_only` |
| institution | `entity_identity_only` |
| place | `entity_identity_only` |
| work | `entity_identity_only` |
| archive | `bibliographic_hint` |
| term | `term_existence` |
| procedure | `term_existence` |
| event | `event_identity_only` |

archive 包括未出版手稿、书信及档案，书目数据库只覆盖其中一部分。出版年、ISBN、出版商不是所有 archive 的必需属性；未找到出版物类型或书目匹配不证明文献不存在。API 原字段（如 publication_year）保持提供方名称。

> claim 不作为知识元类型，其验证通过 quality/claim-registry.yml 的证据层独立管理。

### 写回上限

```text
strong title match + 非消歧义页 + extract present
  -> evidence_status: partially_verified
  -> verification_level: L1
  -> confidence: medium
  -> consensus: tentative
```

除非 evidence 中明确记录 `second_source_confirmed: true`，否则 Wikipedia 单源不得推荐 `externally_verified`。

### 必须记录字段

```json
{
  "source_authority": "tertiary_reference",
  "claim_scope": "entity_identity_only",
  "claim_target": "name_en",
  "match_quality": "strong",
  "match_score": 0.86,
  "matched_fields": ["title", "description", "extract"],
  "conflicting_fields": [],
  "candidate_rank": 1,
  "candidate_count": 5,
  "is_disambiguation": false,
  "is_redirect": true,
  "redirect_from": "Original Query",
  "blocking_reason": null
}
```

## 三、Wikidata API

### QID 命中不等于确认

Wikidata collector 必须至少检查：

- label / aliases
- description
- instance of
- type-specific fields
- candidate rank
- conflicting fields

候选选择必须先比较语义质量、再比较匹配分数；质量、分数和对象类型相容性均相同时保留 API 返回的更早排名，不得由后排同分候选覆盖首位候选。后排同名候选只有在语义对象类型更相容时才可越过前排；字段更齐全本身不是身份消歧证据。

Term / Procedure 的任意 `instance of (P31)` 不能自动算作概念类型命中。软件、作品、姓氏、剧集等实体经常与术语同名；此时至少需要 `subclass of (P279)`、独立描述来源或 Agent 语义裁决，才能把同名候选当作术语证据。

### 类型字段

| 类型 | 关键字段 |
|---|---|
| person | P31、P569、P570、P106、P27、P800 |
| archive | P31、P50、P577、P123、DOI/ISBN 相关字段 |
| work | P31、P170、P571、P195、馆藏或创作者字段 |
| place | P31、P17、坐标、历史名称或机构属性 |
| term / procedure | P279、P31、P1343，仅作术语或程序候选 |

### 写回上限

- 仅 QID + label 命中：`entity_identity_only`，最高 `partially_verified`。
- QID + 多个关键字段匹配：可推荐 `basic_fact` / `externally_verified`。
- 字段冲突：写入 `conflicting_fields` 和 `blocking_reason`，不得推荐写回。

### 请求失败与恢复

- 同一 KU 的搜索候选使用一次 `wbgetentities` 批量取回，不按候选逐条放大请求。
- 429、可恢复的 5xx、超时与连接失败只做有界重试；最终失败统一保留 `blocking_reason: api_error`，并在 `collection_error` 记录阶段、类型、HTTP 状态、尝试次数和可重试性。
- `api_error` 是收集失败，不得改写为 `no_search_results`，也不得据此判定对象不存在。
- 恢复运行用 `--retry-from <evidence.jsonl>` 只选择历史 `api_error` 目标，输出新的 evidence ledger；历史 evidence 不原地改写。

## 四、禁止旧写法

以下表达不再作为有效规则：

```text
API 成功 -> 验证通过
L7 通过 -> VERIFIED
Wikipedia 已验证 -> consensus confirmed
QID 命中 -> externally_verified
```

应改为：

```text
API 命中 -> evidence
evidence -> claim_scope 判断
claim_scope + source_authority + source_count -> 状态转换
apply -> 统一写回或阻断
```
