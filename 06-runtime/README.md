# 系统运行层

本目录只保存当前派生状态、可追溯 work package 与评测用例，不定义知识蒸馏流程。
权威顺序是 `AGENTS.md -> Skill -> direct reference`。

## 当前目录

```text
06-runtime/
├── state/
│   ├── current-health.json
│   ├── skill-registry.json
│   ├── candidate-index.jsonl
│   ├── discovery-manifest.json
│   └── generated-projections-manifest.json
├── governance/
│   ├── governance-backlog.md
│   ├── system-upgrade-log.md
│   ├── relation-generic-explicit-baseline.jsonl
│   └── taxonomy-migration-map.json
├── automation/
│   ├── index.md
│   └── <work-package>/
└── eval/
    └── query-eval-set.jsonl
```

## 边界

1. `state/` 是可重建投影；health、backlog 和 candidate index 不是语义裁决。
2. 长任务状态只位于当前 work package 的 `runner-state.json`，不存在仓库级全局 runtime state。
3. `automation/` 保留 evidence、decision、plan、manifest、result 和 summary。批次内一次性 writer 不作为现行执行器保留；稳定执行器只位于 `scripts/`。
4. candidate index 同时保存完整 inventory 和 `lifecycle_class`；backlog 只统计 `active`，不把 terminal 或 historical non-replay 计作债务。
5. 生成式 R2 投影必须由 provenance manifest 明确列出且输出哈希匹配；inventory/summary 默认是 R1。工作包最终只刷新一次并执行 `--check-generated`。
6. audit 报告默认输出到终端或当前 work package，不在根运行层堆积日期版本快照。
7. 系统升级影响、删除边界与验收证据只写入 `system-upgrade-log.md`，不再维护逐次 upgrade-impact 副本。

## 入口

- `python scripts/build_runtime_index.py`：刷新 work package 索引。
- `python scripts/build_runtime_index.py --retention-report`：只读检查 R1/R2/R3 和残留。
- `python scripts/hierarchy_stress_test.py`：只读输出五级层级缺口；显式 `--queue-output` 才写待审队列。
- `python scripts/run_sync_closure.py --refresh-generated --full --check-generated`：最终发布门禁。
