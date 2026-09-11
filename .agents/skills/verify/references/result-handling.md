# 验证结果处理

本文件以当前两阶段验证模型为准，替代旧的单阶段 Wikipedia 结果写法。

本参考约束调用验证状态接口的写回；常规语义正文及过程记录按AGENTS与verify执行。脚本允许的状态上限不证明实体身份、版本或Wikipedia—Wikidata配对通过。当前collector/apply未自动执行语义判断，Agent须按verify记录实际采用的类型来源及核对结论。没有Wiki配对时仍可由其他权威记录支持身份或事实，但须分别说明来源能力与限制。

## 一、结果处理与状态裁决原则

1. 使用验证状态接口的外部证据先进入 evidence JSONL。
2. collect 阶段不直接写知识元。
3. apply 阶段由 `verify_apply_evidence.py` 统一写回；整批预检不通过时不得修改任何 KU 或 verification log。
4. 写回前必须支持 `--dry-run`。
5. 只有成功提交的 apply/no_delta 记录进入 `verification-log.md`；blocked/failed 留在 work package 状态与 summary。
6. `confidence`、`consensus`、`evidence_status` 与 `verification_level` 的变化必须针对明确的 assertion scope 进行语义裁决。
7. 来源数量、QID 命中、时间经过或脚本分数都不能自动触发状态晋升或降级。
8. 本文件从属于 AGENTS 与 verify，集中说明 confidence/consensus 接口处理；其他 Skill 引用，不另建阈值表。

## 二、推荐变更字段

当前 apply 阶段重点处理以下字段：

- `evidence_status`
- `verification_level`
- `confidence`
- `consensus`
- `last_verified`
- `updated`
- 正文第三部分 `## 关系与证据` 下的 `### 验证状态`

## 三、阻断规则

以下情况应阻断或降级：

- 单一 evidence 不得把 `confidence` 升为 `high`
- 多条 evidence 也不得仅因数量达到阈值而自动升为 `high`；必须确认来源独立性、支持范围和未解决冲突
- `entity_identity_only` 不得单独把 `consensus` 升为 `confirmed`
- `entity_identity_only` / `term_existence` / `event_identity_only` / `bibliographic_hint` 单源 evidence 不得推荐 `externally_verified`
- `source_count` 不得自动递增
- `last_verified` 或 `review_due` 到期只产生复核信号，不自动降低 `confidence`
- `L7` 不能充当外证；只有实际来源支持时才保留 `source_backed`，仅模型知识为 `model_supported`
- 消歧义页、弱标题匹配、关键字段冲突必须阻断或进入二次验证

## 三点五、claim_scope 写回上限

| claim_scope | 单源写回上限 |
|---|---|
| `entity_identity_only` | `partially_verified` |
| `term_existence` | `partially_verified` |
| `event_identity_only` | `partially_verified` |
| `bibliographic_hint` | `partially_verified` |
| `basic_fact` | `externally_verified` |
| `bibliographic_fact` | `externally_verified` |
| `source_claim` | `source_backed` / `externally_verified` |
| `domain_relevance` | `source_backed` / `externally_verified` |
| `historiographic_claim` | `source_backed` / `externally_verified` |

`externally_verified` 需要满足以下任一条件：

1. evidence 自身的 `claim_scope` 已达到 `basic_fact` 或更高；
2. evidence 明确记录 `second_source_confirmed: true`，且第二来源的独立性和支持范围已经审查；
3. apply 阶段检测到多条 `source_independence_group` 不同的 evidence 支持同一知识元的同一 claim，并且不存在影响该 claim 的未解决冲突。`source_type` 不同不等于来源独立。

满足上述条件只说明该 claim 具备进入语义审核的证据基础，不自动授权 `confidence: high` 或 `consensus: confirmed`。

## 四、正文写入格式

工具将验证段写入第三部分“关系与证据”下，保留相邻关系、证据和待补内容；旧顶层验证段在实际写回时归并，不另造第四部分。出现重复且无法确定目标的段落则阻断，避免覆盖不明内容。未有 version 字段的普通 KU 不新增版本计数，既有接口版本继续兼容；不因此全库重写或执行外部采集。

```markdown
## 关系与证据

### 验证状态

- **证据状态**: source_backed / partially_verified / externally_verified / model_supported / unverified
- **验证层级**: L1-L7
- **验证平台**: <平台名称>
- **匹配质量**: strong / medium / weak / N/A
- **验证日期**: YYYY-MM-DD
- **证据范围**: entity_identity_only / source_claim / ...
- **来源URL**: <URL，可选>
- **说明**: <补充说明，可选>
```

## 五、运行记录与恢复

- apply 结果写入 `verification-log.md`，阻断和失败同时进入命令结果或工作包 summary。
- 仓库级全局 runtime state 已退役；默认 dry-run/apply 不写状态文件。
- 只有需要恢复的长任务才显式传入 `--state-file <work-package>/runner-state.json`。
- `--resume` 必须与同一批次的 `--state-file` 一起使用，并核对 evidence 的规范化 SHA-256；输入变化时直接拒绝恢复。
- apply 使用同目录临时文件和原子替换；任一提交失败时恢复本批已替换的原文件，不生成持久 `.bak`。
