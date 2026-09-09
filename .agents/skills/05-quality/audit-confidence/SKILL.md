---
name: audit-confidence
kind: leaf
triggers:
  - audit-confidence
  - 置信度审计
description: >
  置信度与证据状态的只读审计技能。报告低置信、单来源、逾期和状态冲突对象，
  生成待验证队列，但不自动 enrich、晋升状态或写回知识元。
---

# audit-confidence

## 输入

- 当前 KU、claim、relation 和 evidence 状态。
- `current-health.json` 中未计分的知识成熟度分布。
- verify 的结果处理与 confidence/consensus 权威规则。

## 执行

1. 扫描 `confidence`、`consensus`、`evidence_status`、`verification_level`、`source_count` 和验证日期。
   - 全库审计或指定批次范围统一调用 `scripts/audit_unverified_queue.py --output <work-package>/confidence-priority.jsonl`；指定结果集时附加 `--input-result <result.json>`，需要人读摘要时再加 `--summary-output <work-package>/confidence-summary.md`。
2. 分别识别低置信、单来源、逾期、孤立以及字段组合冲突。
3. 区分系统缺陷、研究债务与候选机会，不设置人为达标比例。
4. 生成带对象、原因、证据缺口和建议下一跳的待验证队列。
5. 需要补证或多来源交叉验证的对象交给 `verify`；需要补写语义的对象只作为 `enrich` 建议，不自动调用。

## 输出

- 置信度与证据状态分布；
- 待验证、待补证和待冲突裁决队列；
- 已审查范围、未审查范围和剩余不确定性。

## 边界

- 来源数量、验证日期或 QID 命中不能自动改变状态。
- 不自动调用其他 Skill，不直接写回知识元。
- 不把结构 health 分数或置信度比例解释为知识成熟或发布就绪。
- 状态变化统一遵循 verify 的结果处理规则。

## 参考

- `../../03-verification/verify/references/result-handling.md`
- `../lint/references/claim-evidence-governance.md`
