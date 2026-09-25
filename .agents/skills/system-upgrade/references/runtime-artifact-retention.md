# Runtime artifact retention policy

Historical files under `06-runtime/automation/` remain in place by default. Size, age and重复信号不是删除授权；但用户明确要求收敛现行体系时，可以删除由 Git 保存且会被误认为当前入口的批次脚本、重复规范和过时快照。

## Retention tiers

- `R1`: evidence, review/defer decisions, manifests, plans, apply reports, inventories, summaries, and other不可替代 provenance。保留数据与裁决；批次内可执行代码不是保留 R1 的必要条件。文件名包含 `inventory` 或 `summary` 不足以证明可重建。
- `R2`: mechanically rebuildable projections. A provenance manifest must record the generator identity/hash, invocation or parameters, effective inputs with digests, relevant KU-state digest, and output hashes；支持仓库现行 `outputs[]` 与兼容 `output_hashes` 表达，但只有 manifest 精确列出该输出且哈希匹配时才归 R2。字段缺失、未列出或哈希不符时只能保留为 R1，并在命中窄范围生成态信号时标记 `review_required`。
- `R3`: `.bak`, `.tmp`, `.temp`, `.pyc`, `__pycache__/`, `.DS_Store`, and `*.egg-info/`。任务结束前清理；需要暂存时必须留在受控临时目录。

Unknown artifacts default to R1。删除必须有明确路径范围；Git 历史可恢复性不能替代删除授权，但可作为已授权清理的恢复边界。

## Workflow

```text
read-only retention report
-> classify R1/R2/R3
-> verify R2 provenance
-> retain in place unless explicit path-level archive or deletion authority exists
```

Run `python scripts/build_runtime_index.py --retention-report`. The report must remain read-only and expose tier counts, R2 provenance gaps, duplicate capacity signals, and R3 residue.

Repository-level generated projections use 06-runtime/state/generated-projections-manifest.json. It is generated only after all projections have been refreshed.
