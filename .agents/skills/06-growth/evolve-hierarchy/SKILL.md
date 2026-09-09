---
name: evolve-hierarchy
kind: leaf
triggers:
  - evolve-hierarchy
  - 演化层级
description: >
  按增量信号重评既有领域—维度—主题—议题结构，必要时形成受证据约束的结构变更。
---

# evolve-hierarchy v4.0

## 触发条件

- 新增或变更 KU 无法进入现有 Topic；
- 已审查 Cluster 暴露稳定的 Topic、Theme、Dimension 或 Domain 边界；
- 现有 Domain、Dimension、Theme 或 Topic 出现可复现的重叠、空洞或边界冲突；
- 用户明确要求全量层级重评。

无变化信号时不运行全库重评。

## 流程

1. 读取当前 hierarchy 与变化集合，先尝试映射到现有 Level 4 Topic。
2. 不能容纳时先建立 topic 候选；多个 Topic 形成稳定问题群时建立 theme 候选，只有既有 Theme/Dimension 无法解释时才进入 dimension/domain 候选。
3. 新 Dimension 与 Domain 分别满足 `01-domain/dimension-registry.md` 和 `01-domain/domain-registry.md`，不得由数量阈值自动晋升。
4. 记录 evidence、boundary test、hierarchy impact、迁移映射与 unresolved items。
5. 审批后调用 `build-hierarchy` 更新；未通过则保留候选，不修改正式 hierarchy。

全量或大范围重评先运行 `python scripts/hierarchy_stress_test.py --queue-output <work-package>/hierarchy-review-queue.jsonl` 生成当前缺口队列。队列只记录缺失字段和现状，不提出归属。Agent 应按语义连贯的 Theme/Topic 窗口审查并形成 exact change-set；批量大小由上下文和 diff 可审阅性决定，不设固定100条窗口。

脚本可计算增量、链接和覆盖率，不得自动决定 Domain、Dimension、Theme、Topic 或 KU placement。`hierarchy_stress_test.py` 默认只输出 JSON 摘要，只有显式 `--queue-output` 才生成语义待审队列。

## 参考

- `../build-hierarchy/SKILL.md`
- `01-domain/dimension-registry.md`
