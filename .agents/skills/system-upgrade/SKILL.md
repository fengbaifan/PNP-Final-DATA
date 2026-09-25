---
name: system-upgrade
kind: leaf
phase: support
triggers:
  - system-upgrade
  - 系统升级
  - 规则修订
description: 执行已授权的系统调整，保持规则、Skills 与实际工具一致。
---

# system-upgrade

执行已授权的系统调整，保持规则、Skills 与实际工具一致。

1. 记录用户原话，识别目标与范围；current-requirements 只索引有效要求。
2. 先改最近的权威规则及直接依赖。空项目只建立基本完备能力，不造研究内容或完成状态；历史材料不作当前结果。
3. 合并重复合同与记录，常规语义编辑直接进行；批量写回、外部核验、长任务恢复等按实际需要保留，不统一附加到每个阶段。
4. 删除/移动前核实路径、内容及调用者；来源和必要历史证据保留。Windows 联接不得递归进入目标。
5. 按改动运行必要检查；只有辅助代码/格式变化涉及广泛行为时运行相应回归。投影仅刷新受影响项，不要求未提交修改与 HEAD 相同，不为通过检查自动提交。
6. 过程、映射、结果和实际限制只记既有 CHANGELOG.md。普通文档不新增独立版本号，Git 与日志保留变化。

权限以当前用户要求和实际 Codex 环境为准。Git 提交/推送按明确授权执行，已授权时核验远端；不因 Skill 模板额外索取许可或默认发布。

## 按需直接参考

- `references/index-layering-contract.md`：入口、索引、记录位置及事实责任。
- `references/skill-registry-schema.md`：Skill 名称、路径、直接参考或注册变化。
- `references/upgrade-acceptance-gates.md`：按影响选择必要检查。
- `references/coding-execution-principles.md`、`references/script-governance.md`：实际调整辅助代码时。
- `references/mainline-only-git-governance.md`：已授权提交/推送或核查 Git 约束时。
- `references/runtime-artifact-retention.md`：需要移动、删除或判断机器工件保留范围时。
- `references/runtime-state-machine.md`：恢复状态接口变化时。
- `references/work-package-contract.md`：仅批量机器写回或旧接口续接。
