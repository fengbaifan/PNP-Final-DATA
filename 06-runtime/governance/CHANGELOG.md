# 规则变更日志

> 治理日志已冻结归档：`user-revisions.md` 与 `system-upgrade-log.md` 自 2026-09-25 起只读，不再追加。
> 此后的规则与系统变更只记在这里，按时间倒序；`current-requirements.md` 仍索引有效要求。

## 2026-09-25

- 冻结 `user-revisions.md`、`system-upgrade-log.md`，普通问答不再逐条记 REV，结果文件只保留当前状态。
- 新增 S0–S7 阶段产出规范（`01-domain/stage-artifact-schema.md`）与关系域值域矩阵（`01-domain/relation-domain-range.yml`）。
- 新增 `scripts/export_s0s7.py`（一次性转换产出 v0.1）与 `scripts/build_entity_candidates.py`（原书索引 → 全书候选）。
- 修正 `gianfranco-torcellan.md` 的 `authored_by` 反向边。
- 框架修订：`pipeline.md` 改为 S0–S7 并切断回环（backlog 替代「回知识元」），8 个 skill 与 `AGENTS.md` 对齐新阶段与产物。
- 派生文件约定：`relation-index.yml` 等派生文件只在 S7 发布或按需生成，不逐批重建、不当事实源（见 `scripts/README.md`）。

