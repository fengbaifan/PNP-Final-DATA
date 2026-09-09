# Apply Gates v1.1

> 本文件定义 knowledge unit / claim / relation / evidence / automation 写回前的强制门禁。

## 一、KU 入库 Gate

写入 `04-knowledge/units/` 前必须满足：

1. processing manifest 明确声明 profile；新来源使用 `compact-v4`，历史包保留 legacy profile。
2. 当前 profile 要求的 source spans、reading coverage、candidate ledger 和 decision ledger 均存在且闭合；不得同时要求两套 profile 的重复工件。
3. source span 或 source citation 已绑定。
4. 类型在当前 8 类 KU 受控词表中。
5. 至少 1 个真实 source，且 `source_count` 与来源记录一致。
6. Agent 已完成语义阅读与类型裁决；机械覆盖检查不能替代该判断。

## 二、Claim 入库 Gate

写入 `claim-registry.yml` 前必须满足：

1. `statement_zh` 和 `statement_en` 均已填写。
2. `source.doc_id` 已绑定，或 `discussion_notes` 标注 `needs_evidence`。
3. `claim_type` 在受控词表中。
4. 不得将术语直接写成 claim。
5. 单一 source-backed claim 不得标记为 `confirmed`。

## 三、Relation 入库 Gate

写入 relation 前必须满足：

1. `relation_type` 在受控词表中。
2. source_type / target_type 符合类型约束。
3. 双向关系的 inverse_relation_type 正确。
4. `evidence_ref` 或 `claim_id` 已绑定，或 `review_status` 标注 `needs_evidence`。
5. 不得把 legacy `related` 自动提升为 `evidence_backed_relation`。

## 四、Evidence Apply Gate

交给 `verify_apply_evidence.py` 写回 evidence 前必须满足：

1. collect 阶段已完成，evidence JSONL 已生成。
2. Agent 已审核 evidence 质量，或自动化风险分级为 L1。
3. `match_quality` 不为 `none`。
4. 不因 Wikipedia 页面存在自动标记 verified。
5. 单一 limited-scope evidence 不得写成 `externally_verified` 或 `confirmed`。

## 五、可控自动化 Gate

使用 `scripts/evidence_batch_runner.py` 编排 evidence 队列时，必须遵守：

1. 只生成当前工作包实际需要的 manifest、candidate/evidence/apply ledger 和 summary；禁止固定生成空队列。
2. `--dry-run-apply` 只允许调用 `verify_apply_evidence.py --dry-run`。
3. `--apply-low-risk` 只允许处理 `.agents/guards/automation-risk-policy.md` 中定义的 L1 existing-KU evidence。
4. L2 项必须进入 Agent review，不得自动 apply。
5. L3 项必须进入 defer queue，不得自动创建 event KU、confirmed claim 或 externally_verified 状态。
6. 自动化批次结束后先跑最近邻门禁；仅在工作包发布时运行完整 closure。

详细风险分级见 `.agents/guards/automation-risk-policy.md`。
