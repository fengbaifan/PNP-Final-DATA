---
name: system-upgrade
kind: leaf
phase: support
triggers:
  - system-upgrade
  - 系统升级
  - 规则修订
description: 处理用户已授权的规则、阶段流程、Skills、辅助代码和目录重构。
---

# system-upgrade

处理用户已授权的规则、阶段流程、Skills、辅助代码和目录重构。

## 执行

1. 先把当前可见用户消息原话追加到 user-revisions.md，明确意图、对象与实际授权范围；current-requirements.md 只汇总有效要求。
2. 阅读 AGENTS.md、pipeline 和直接涉及的契约，检查真实依赖，区分当前文件、历史证据与客户端适配。
3. 直接修改最近的权威落点和依赖，不为同一规则新增副本。机械批量替换可以辅助，语义判断不交脚本。
4. 删除需核对范围与依赖；Windows 联接只删除链接本身，不能递归进入实际 Skill。来源和不可替代证据不删除。
5. 按变化运行必要测试和规则检查；系统改造收尾可运行 scripts/run_sync_closure.py --refresh-generated --full。未获提交授权时用文件哈希验证投影幂等，不能为满足 HEAD 检查而自行提交。
6. 在唯一 system-upgrade-log.md 分别记录实施过程、最终结果、删除/合并映射、验收与真实限制；不另外生成同用途升级报告。

## 完成与权限

入口、阶段职责、Skill、引用、代码和测试一致，历史状态没有伪装为当前验收。
流程和权限以当前用户要求及实际 Codex 环境为准；不维护其他客户端适配或虚构 Hook。
仅获明确授权后执行 Git 提交/推送并核验远端。没有新改动或实质疑点，不重复全套检查。
常规短规则在 Skill，长 schema、共享契约或条件分支放 direct reference；不因 reference 数量增加调用链。

## 按需直接参考

- `references/coding-execution-principles.md`
- `references/index-layering-contract.md`
- `references/mainline-only-git-governance.md`
- `references/runtime-artifact-retention.md`
- `references/runtime-state-machine.md`
- `references/script-governance.md`
- `references/skill-registry-schema.md`
- `references/upgrade-acceptance-gates.md`
- `references/work-package-contract.md`
