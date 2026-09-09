# 输出产物层说明

本目录只承载**知识库与内容产出物**。

允许放在这里的内容：

- `drafts/`：蒸馏报告与摄入快照
- `retrospects/`：面向知识生产的回溯产物
- `exports/`：面向知识使用的导出物
- `index/`：面向知识浏览与检索的内容导航
- `output-registry.yml`：没有 bundle-local metadata 的输出元数据登记表
- `index/output-gallery.md`：file-back 状态总览（由 `build_output_gallery.py` 生成）

知识图谱只保留 D3.js 二维展示：

- `knowledge-graph.html`：当前二维主入口，读取现行 `knowledge-graph-data.*`。
- `knowledge-graph-2d.html`：早期二维快照，使用独立的 `knowledge-graph-2d-data.*`。
- `knowledge-graph-2d-manifest.json`：二维快照的入口、依赖与跨平台 LF 规范化 SHA-256 完整性边界。

不应再放在这里的内容：

- 系统状态
- 治理待办
- Hook 日志
- 系统升级日志
- 系统审查报告
- 脚本运行记录

这些内容统一放入 `06-runtime/`。
