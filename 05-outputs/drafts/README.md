# 历史蒸馏报告边界

> 本目录中的既有文件是摄入历史快照，不再生成新的固定九段式蒸馏报告。
> 当前知识元事实状态以 `04-knowledge/units/` frontmatter 与
> `06-runtime/state/current-health.json` 为准。

## 关键规则

### 快照边界

- 报告可记录当时的验证判断
- 报告不能替代当前知识元 frontmatter
- 若当前状态变化，不回写这些报告；当前事实以知识库和 runtime state 为准。

### 单文件原则

- 不创建 `-v2`、`-final`、`-new` 等平行版本。
- 新摄入只生成 compact-v4 五类处理工件；面向使用者的内容由 `compose` 按需生成。

### 禁止中间文件

不得新增以下独立文件：

- `semantic_analysis_ch*.md`
- `knowledge_units_ch*.md`
- `ingest_audit_report.md`

这些内容不再并入固定报告；语义覆盖、候选和验收状态只写入 compact-v4 对应工件。
