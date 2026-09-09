# Work Package、Candidate 与 Write-back Contract

适用范围：以下计划、机器账本及事务字段仅用于批量机器写回或既有接口的续接。普通语义编辑在现有过程记录中说明依据、原位更新并定向核对，不强制另建候选/计划/摘要。

## 一、工作包边界

一个用户目标原则上对应一个 work package。工作包可以包含多次 checkpoint，但不得因每次网络请求、每个文件或每个候选另建 batch。

批量大小由以下约束动态决定，不设人为固定小批次数：

- 外部 API 限流与失败恢复窗口。
- 上下文可承载的语义审查量。
- 写回对象是否互相独立。
- 单次 dry-run diff 是否仍可审阅。

## 二、最小 Candidate Envelope

不同发现入口共用以下字段；类型专有字段放入 `payload`，不得复制一套新状态机。

```yaml
candidate_id: stable-id
origin_type: source | knowledge | relation_graph | external | output
origin_ref: path-or-uri
candidate_type: unit | claim | relation | evidence | theme | topic | cluster | hierarchy_change
target_ref: optional-existing-target
payload: {}
evidence_refs: []
state: candidate
decision:
  status: pending
  reason: null
  decided_by: null
  decided_at: null
created_at: ISO-8601
updated_at: ISO-8601
```

正式状态：

```text
candidate -> needs_evidence -> ready_for_review -> approved -> applied
                                  |                |          -> no_delta
                                  |                -> deferred / rejected / blocked
                                  -> deferred / rejected / blocked
```

`deferred` 只有在 evidence、target 状态、规则版本或用户指令发生变化后才能重新入队。仅因重新运行脚本不得复活。

统一候选投影额外计算 `lifecycle_class`：`active`、`terminal`、`historical_non_replay`。它是派生调度字段，不回写历史 R1 账本。`applied/no_delta/rejected` 属于 terminal；只读迁移引用属于 historical_non_replay；backlog 和研究债务只统计 active。

### 追加式 Candidate 裁决

历史 `candidate-ledger.jsonl` 是 R1 证据，不得为更新状态而原地改写。后续语义裁决写入当前 work package 的 `candidate-decision-ledger.jsonl`，由统一候选投影按 work package 路径和行序确定性叠加。每条转换至少包含：

```json
{"candidate_id":"stable-id","expected_state":"needs_evidence","state":"deferred","decision":{"status":"deferred","reason":"...","decided_by":"Agent","decided_at":"2026-08-09"},"updated_at":"2026-08-09"}
```

- 可选字段仅限 `target_ref`、`payload_patch`、`evidence_refs_add`。
- `expected_state` 必须与当前投影一致；未知 candidate、状态不符、字段非法或转换后 schema 不合法时整条转换 fail closed。
- 多次转换必须形成连续状态链，不得跳过前一条转换的实际结果。
- 转换账本属于 R1，并必须进入 candidate projection 的输入指纹；`lifecycle_class` 仍只在投影中派生。

## 三、类型化写回

| candidate_type | 写回入口 | 机械执行边界 |
|---|---|---|
| evidence / verification | `verify_apply_evidence.py` | 已批准、existing-KU、dry-run 后 apply |
| unit create / merge | `ingest` 或 `verify` exact change-set | 模板和字段可机械写入，类型与合并裁决不可自动化 |
| claim | claim/evidence governance exact change-set | 不自动判断 claim_scope、consensus 或 truth |
| relation | relation governance exact change-set | 不自动选择 relation_type、方向或强度 |
| theme / topic | `synthesize` 的边界审查与结构写回 | 不自动宣布成熟或写入 hierarchy |
| cluster | `synthesize` boundary test | 只批准为发现信号；不得物化为 structure node，正式结果另建类型化候选 |
| hierarchy_change | `synthesize` 专项变更 | 必须记录 impact 与 unresolved items |

不得建立可对任意 candidate_type 自动写入任意知识文件的通用 writer。

## 四、事务与可恢复性

正式写回按以下最小事务执行：

```text
approved candidate set
-> exact apply plan
-> dry-run diff
-> apply
-> targeted validation
-> record applied / no_delta / blocked
```

- 同一文件的写回串行执行；互不相交的 collect 和只读审计可以并发。
- 长任务才需要 `runner-state.json`，并保存在当前工作包目录内。
- 全局 runtime state 仅保留为历史兼容入口，不得混合多个活跃批次的运行事实。
- 失败恢复从最后一个已验证 checkpoint 继续，不重跑已完成 collect。

## 五、Output File-back

`file_back_status` 只能使用：

```text
not_reviewed
reviewed_no_candidates
candidates_deferred
candidates_ready
applied
rejected
blocked
```

`reviewed_no_candidates` 表示已执行语义回溯但没有知识增量；`applied` 必须存在 candidate 与写回证据。旧值 `filed_back` 仅作历史兼容，不得用于新输出。

## 六、最小运行工件

按实际需要选择，禁止固定生成空工件：

```text
manifest.json              # 工作包边界
candidate-ledger.jsonl     # 存在候选时
candidate-decision-ledger.jsonl # 对历史候选作追加式裁决时
evidence.jsonl             # 存在证据收集时
apply-plan.jsonl           # 存在正式写回时
runner-state.json          # 长任务或需要恢复时
summary.md                 # 仅旧接口兼容；人工交接引用业务 results，不重复写报告
```
