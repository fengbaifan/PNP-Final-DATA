# Distillation System Contract v2.1

## 一、对象链

```text
Source Signal
-> Source Block
-> Semantic Unit
-> Candidate
-> Existing-knowledge screening
-> Typed Write-back
-> KU / Claim / Relation / Evidence / Structure
```

后续 growth、output 与 file-back 复用同一 candidate/write-back 边界，不再建立另一条流水线。

## 二、不可变原则

1. Agent 负责语义阅读、候选边界、类型、命名、claim、relation 和 hierarchy 判断。
2. 脚本负责校验、hash、索引、collect、dry-run 与已批准机械写回。
3. `02-sources/` 来源本体只追加；顶层登记文件可更新、不可删除。
4. 证据不足必须保留不确定状态。
5. A-E 五个 pilot 维度、8 类 KU 与 4 类 structure node 不因摄入工具变化而被改写；Theme/Topic 数与实时 KU 数以现行结构与 health 快照为准。

## 三、覆盖证明

- 每个 source block 必须被读取、合并或有理由排除。
- 每个可用 block 必须关联 semantic unit。
- 每个 block 必须关联候选，或有具体 `no_candidate_reason`。
- 每个候选必须筛查现有知识，区分新对象、既有目标、潜在重复、潜在冲突与无法判断。
- source block、semantic unit、candidate 与正式对象之间可以正反向追踪。

覆盖证明保存在 compact-v4 的三个 JSONL 和 manifest 中；历史 legacy processing 继续使用原有 chapter artifacts。

## 四、候选与写回

候选使用 work package contract 的统一 envelope；来源候选的 `payload.knowledge_match` 保存重复/冲突筛查。正式对象按类型路由：

| candidate | route |
|---|---|
| unit create/merge | ingest / reconcile exact change-set |
| claim | claim/evidence governance |
| relation | relation governance |
| evidence | verify collect/apply |
| theme/topic | synthesize boundary test 后交给 evolve-hierarchy |
| cluster | synthesize boundary test；只保留发现信号，不物化 structure node |
| hierarchy_change | evolve-hierarchy |

候选不是正式对象。`approved` 也不是 `applied`；无变化必须记录 `no_delta`。

## 五、禁止

- 用正则、切块器或 LLM 摘要声称替代完整语义阅读。
- 把 structure node 或 claim 建成 KU。
- 把 legacy `related` 或弱共现直接升格为正式 relation。
- 把 output 解释直接写回知识事实。
- 为满足文件清单制造空工件。

## 六、完成

processing 完成要求覆盖证明闭合；知识写回完成要求 candidate、decision、evidence、apply 与定向验证闭合。两者必须分别记录，不能用一个 completed 混写。
