# 03-processing 处理层规范 v4.0

> 处理层把只读来源转换为可审计的语义单元与候选。它证明阅读覆盖和候选召回，不直接宣布知识成立。

## 当前执行链

```text
source block
-> semantic unit
-> candidate
-> duplicate/conflict screening
-> typed write-back or defer
```

新来源默认使用 `compact-v4`，只保留五类工件：

```text
03-processing/<doc-id>/
  source-map.jsonl
  semantic-units.jsonl
  candidate-ledger.jsonl
  manifest.json
  summary.md
```

不得按章节固定生成 reading ledger、continuity map、stitch log、chunk、coverage matrix 等重复文件。跨页、跨段、正文—图注连续性直接记录在 source block 与 semantic unit 中；只有规模、并发审查或故障恢复确有需要时，才分片同一种 JSONL。

## 完成边界

- Agent 完整阅读正文、标题、图注、表格、脚注、参考文献和必要图片；脚本不得替代语义阅读。
- 每个 source block 必须关联 semantic unit，并关联候选或具体 `no_candidate_reason`。
- compact-v4 逐来源保存 CRLF/LF checkout 等价的 SHA-256；来源变化后有效状态自动重开。`source_assets` 负责版本指纹，`processing_scope.assets` 负责本包复读边界。
- `processing_scope` 中每个资产必须由 source-map 与 parallel spans 的并集逐行无缺口覆盖；块数不能代替全文覆盖。
- `semantic_artifact_integrity` 只检查文件、跨度和引用闭合；Agent 复读验收另记来源版本、遗漏数和边界。
- 每个候选必须检索现有 KU、claim、relation 与权威索引，记录 `novel`、`existing_target`、`potential_duplicate`、`potential_conflict` 或 `undetermined`。
- `potential_conflict` 才路由 `reconcile`；没有冲突信号时不得为形式完整性运行整套冲突裁决。
- processing 的 `completed` 只表示覆盖证明闭合，不表示候选已写入知识库。

机械校验：

```powershell
python scripts/validate_processing_package.py 03-processing/<doc-id>
```

详细契约见 `.agents/skills/01-intake/ingest/SKILL.md` 及其 `references/`。

## 历史边界

现有 `legacy-chapter` 目录是只读 provenance，不是现行处理 profile，不回填旧模板，也不作为新任务入口。现行摄入和补审只使用 compact-v4。
