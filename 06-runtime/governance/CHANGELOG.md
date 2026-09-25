# 规则变更日志

> 治理日志已冻结归档：`user-revisions.md` 与 `system-upgrade-log.md` 自 2026-09-25 起只读，不再追加。
> 此后的规则与系统变更只记在这里，按时间倒序；`current-requirements.md` 仍索引有效要求。

## 2026-09-25

- 冻结 `user-revisions.md`、`system-upgrade-log.md`，普通问答不再逐条记 REV，结果文件只保留当前状态。
- 新增 S0–S7 阶段产出规范（`01-domain/stage-artifact-schema.md`）与关系域值域矩阵（`01-domain/relation-domain-range.yml`）。
- 新增 `scripts/export_s0s7.py`（一次性转换产出 v0.1）与 `scripts/build_entity_candidates.py`（原书索引 → 全书候选）。
- 修正 `gianfranco-torcellan.md` 的 `authored_by` 反向边。
