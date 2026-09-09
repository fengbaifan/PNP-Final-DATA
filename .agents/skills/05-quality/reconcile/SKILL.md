---
name: reconcile
kind: leaf
triggers:
  - reconcile
  - 冲突裁决
description: >
  知识库冲突裁决技能。对同一对象、断言或关系中的矛盾证据执行来源复核、边界裁决和受控写回。
  触发词：reconcile、冲突裁决、冲突解决。
---

# Reconcile 技能 v2.1

> 冲突是 assertion/evidence 层的治理状态，不是 knowledge unit 类型。证据不足时保留 unresolved，不得折中平均或伪装成已裁决。

## 输入

- 用户明确指出的冲突；或
- `06-runtime/automation/` 中带来源定位的冲突候选；或
- KU、claim、relation 之间可复现的事实/身份/边界矛盾。

无冲突信号不是本 Skill 的输入。摄入和发现流程只做重复/冲突筛查，不为每个候选固定运行本流程。

## 流程

1. 读取冲突两侧对象、现有来源、claim/relation 记录和直接证据片段。
2. 将来源事实与解释性判断分开，明确冲突类型：对象同一性、事实、年代、定义、关系、解释或类型边界。
3. 按 `verify` 的 `collect -> evidence JSONL -> dry-run -> apply` 两阶段流程补充证据；collect 不得写库。
4. 形成 decision artifact，结论只能是 `resolved`、`parallel_interpretations`、`deferred` 或 `rejected`。
5. 涉及 merge、alias、same_as 或对象迁移时，除术语同一性证据外还必须取得明确授权。
6. 仅在 dry-run 与授权门槛通过后，使用对应受控 apply 入口写回 KU/claim/relation；不得直接编辑验证状态伪造闭环。

## 产物

复用当前 work package 的 candidate envelope，不另建第二套冲突状态机。只保留实际发生的工件：

- 冲突候选与 decision 记录在 `candidate-ledger.jsonl`；
- 发生补证时生成 `evidence.jsonl`；
- 发生正式写回时生成 `apply-plan.jsonl`；
- `summary.md` 记录裁决、延期和未解决项。

没有补证、延期或写回时不得制造空文件。

## 冲突记录

冲突记录属于当前 work package 的 assertion/evidence 治理产物，不是 KU、structure node 或新的 `type`：

```yaml
conflict_id:
conflict_type: identity | fact | chronology | definition | relation | interpretation | type_boundary
objects: []
source_sides: []
evidence_refs: []
decision: unresolved | resolved | parallel_interpretations | deferred | rejected
decision_rationale:
apply_authorized: false
```

- 对象同一性先于字段合并；无法证明同一对象时保持并列。
- 事实冲突依赖可定位的一手或权威来源，不按来源数量投票。
- 解释冲突允许并列，不用平均化表述掩盖分歧。
- relation、merge、alias 和类型迁移分别遵守各自门槛；正式写回一律先 dry-run。

## 禁止事项

- 不创建 `type: conflict` 或 `04-knowledge/quality/conflicts/` 作为新的知识类型体系。
- 不按来源数量简单投票，不把解释冲突强行合并为单一结论。
- 不因名称相同自动 merge/alias。
- 不绕过 verify/relation 的 dry-run 与 apply 边界。

## 参考

- `../../03-verification/verify/SKILL.md`
- `../lint/references/claim-evidence-governance.md`
