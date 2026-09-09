# Mainline-Only Git Governance

本仓库采用单主线 Git 工作流。该约束同时适用于 Codex、VS Code、命令行和其他客户端。

## 规则

1. 唯一允许的本地分支和远端分支是 `main`。
2. 禁止创建功能分支、临时分支、IDE 自动分支、Codex 分支和额外 worktree。
3. 所有治理修订在同步后的 `main` 上执行；提交前必须先运行受控检查，推送前必须重新确认远端状态。
4. `origin` 必须指向正式仓库，fetch refspec 必须只跟踪 `refs/heads/main`。
5. 发布完成后必须确认：
   - 当前分支为 `main`；
   - 本地仅有 `refs/heads/main`；
   - 跟踪引用仅有 `refs/remotes/origin/main` 和可选的 `refs/remotes/origin/HEAD`；
   - 仅有主工作树；
   - `origin/main...main = 0/0`。

## 取舍

单主线工作流降低了分支隔离和 PR 审查能力。作为补偿：

- 修改必须保持小批次；
- 中间 checkpoint 运行按变化集合路由的 `python scripts/run_sync_closure.py`；
- 工作包最终提交前运行 `python scripts/run_sync_closure.py --full` 和 `python scripts/pre_commit_check.py`；
- 推送前运行 `git fetch origin main` 并检查 ahead/behind；
- 推送后再次检查远端同步状态。

## 客户端边界

仓库内规则无法可靠禁用 VS Code 或其他客户端的“创建分支”按钮。防线是确定性治理检查：一旦出现额外分支或 worktree，`audit_rule_drift.py` 和 pre-commit 必须失败，直到清理完成。
