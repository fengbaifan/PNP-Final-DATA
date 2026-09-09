---
name: synthesize
kind: leaf
triggers:
  - synthesize
  - 综合发现
description: >
  从知识库增量、关系图、外部研究和 output file-back 信号中发现跨来源模式，形成可追踪候选；不直接宣布主题成熟。
---

# synthesize

## 输入事件

- 新增或改变的 KU / claim / relation。
- output 回溯产生的候选。
- 外部研究出现的新对象或反复模式。
- 明确要求的全库综合发现。

默认只扫描自上次 discovery manifest 之后变化的输入；首次建基线或用户明确要求时才全量扫描。不按“每 N 次 ingest”固定触发。

## 执行

1. 读取变化集及相邻的 KU、claim、relation、source。
2. 识别可能解释多个对象的模式、断裂链、冲突或开放问题。
3. 按统一 candidate envelope 写入当前 work package 的 `candidate-ledger.jsonl`。
4. 绑定 supporting evidence，执行 boundary test 与 hierarchy impact check。
5. 标记 `ready_for_review`、`needs_evidence`、`deferred` 或 `rejected`。
6. Cluster 审批只确认“该分组值得保留为发现信号”，不得直接写入 structure。需要正式变化时，另建可追踪的 theme、topic、claim、relation 或 hierarchy_change 候选并交给对应写回入口。

## 候选与成熟边界

所有来源、知识、关系图、外部研究和 output 发现共用 work-package candidate envelope，类型为 `unit`、`claim`、`relation`、`evidence`、`theme`、`topic`、`cluster` 或 `hierarchy_change`。`scripts/build_discovery_index.py` 将活跃账本确定性投影为 `06-runtime/state/candidate-index.jsonl` 和 `discovery-manifest.json`；重复 ID 冲突必须 fail closed。

```text
candidate -> needs_evidence -> ready_for_review -> approved -> applied | no_delta
                                        \-> deferred | rejected | blocked
```

共享 tag、日期、名称、相似度、频次和中心性只能提供召回信号。Theme/Topic 候选必须说明 supporting units、claims、relations、sources、独立边界、跨来源独立性、反例、hierarchy impact 与未解决问题。

Cluster payload 至少包含：

```yaml
target_level: ku | topic | theme | dimension | domain | claim | relation
scope: within_topic | within_theme | within_dimension | cross_dimension | cross_domain
basis: semantic | relation | temporal | spatial | source | manual
input_snapshot: path-or-digest
members: []
boundary: ""
counterexamples: []
stability_across_runs: null
```

Cluster 只能经显式语义边界审查成为发现信号，不生成 `structure/clusters/`。零候选是合法结果，不创建空账本。

## 禁止

- 仅凭共享 tag、同一时期或图距离自动晋升主题。
- 把 output 解释当成独立证据。
- 把重复运行脚本当作 `deferred` 候选重新入队的理由。
- 直接修改 Domain、Dimension、Theme、Topic 主骨架。

## 参考

- `.agents/skills/00-coordination/system-upgrade/references/work-package-contract.md`
