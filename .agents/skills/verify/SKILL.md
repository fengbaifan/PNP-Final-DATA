---
name: verify
kind: leaf
phase: current
triggers:
  - verify
  - 知识元对齐
  - 验证知识元
  - 冲突裁决
description: 负责第四阶段对齐及各阶段必要的事实验证，包含原 reconcile 的冲突裁决职责。
---

# verify

负责第四阶段对齐及各阶段必要的事实验证，包含原 reconcile 的冲突裁决职责。

## 输入

已有知识元、来源依据和明确待核问题。先读取知识元成稿结果；必要时做局部补证，不默认遍历所有网站或运行全部 collector。

## 对齐与冲突

1. 语义比较库内名称、别名、身份、年代、作品/出版物版本；同名不等于同一对象。
2. 需要外部锚点时，直接读取权威来源正文；API 只辅助定位。优先已有证据和问题最匹配的来源，不固定 Wikipedia 优先级。
3. 记录命中与未命中、冲突两侧事实、来源独立性及裁决依据；身份锚点只能支持身份，不能验证整篇条目。
4. 存在可复现冲突时判定 resolved、parallel_interpretations、deferred 或 rejected；无冲突不制造冲突流程。无法证明同一对象时不合并；合并授权按当前任务实际范围判断。

## 证据与写回

collect → evidence JSONL → Agent 判断 → scripts/verify_apply_evidence.py --dry-run → --apply。
collect 不改事实；只有受控 apply 更新验证状态、日期及正文验证区块。先整批预检，再原子写知识与成功日志；失败不记 completed，恢复前核对 evidence 指纹。
source_independence_group 必须填写；同一来源的转引不能伪装独立证据，source_count 不自动累加。
身份证据、QID、链接、来源数量或模型知识不能自动把 confidence/consensus/verification 提升至完全确认。证据不足保留不确定状态。
L1–L7 是现有验证字段代码，不是本项目阶段编号；适用范围见 result-handling。

## 过程、结果与交接

在 04-knowledge/process/<id>.md 记录逐对象比较、证据和判断；在 results/<id>.md 记录已对齐、待消歧、冲突及具体改动。需要的 JSONL 证据仍留在同一工作包，通过引用关联，不复制第二套。
仅成功写回进入 quality/verification-log.md。对齐通过对象交给 enrich；无缺口对象也需明确说明后进入关系阶段。Theme/Topic 挂载不属于对齐。

## 按需直接参考

- `references/api-verification.md`
- `references/cascade.md`
- `references/no-data-and-browser-research.md`
- `references/result-handling.md`
- `references/type-verification.md`

- `.agents/skills/system-upgrade/references/work-package-contract.md`
