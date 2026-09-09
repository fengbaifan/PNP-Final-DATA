---
name: knowledge-graph
kind: leaf
description: >
  知识图谱可视化展示。将知识蒸馏系统的全部知识元渲染为交互式 D3.js 二维关系图；
  支持筛选、搜索、详情、缩放与视图控制。触发关键词：知识图谱、knowledge graph、
  可视化展示、展示页面。
triggers:
  - "knowledge-graph"
  - "知识图谱"
  - "knowledge graph"
  - "可视化展示"
  - "展示页面"
  - "knowledge map"
  - "知识元展示"
od:
  mode: prototype
  preview:
    type: html
  craft:
    requires: [typography, color, anti-ai-slop]
---

# 知识图谱展示技能

> 主入口使用本地 D3.js v7 二维关系图；显式二维入口保留早期快照，二者均可离线打开。

## 核心功能

1. **数据生成** — 运行 `scripts/build_knowledge_graph_data.py`，从 KU、正式层级和权威 relation index 提取图谱数据
2. **主图谱渲染** — `05-outputs/knowledge-graph.html` 使用本地 D3.js 和当前 `knowledge-graph-data.*`
3. **二维归档** — `knowledge-graph-2d.html` 使用独立冻结数据，不随当前数据刷新而覆盖
4. **交互操作** — 类型筛选、关键词搜索、节点详情、缩放、平移与视图复位

## 设计系统

本技能参照 Open Design 的 "Clean" 设计系统：
- 主色 `#3B82F6`，辅色 `#8B5CF6`
- 排版使用本地系统字体栈，不依赖远程字体服务
- 8pt 基线网格，12px 圆角
- 8 种节点颜色对应 8 种知识元类型

## 类型颜色映射

| 类型 | 颜色 |
|------|------|
| person / 人物 | `#3B82F6` (蓝) |
| institution / 机构 | `#8B5CF6` (紫) |
| term / 术语 | `#10B981` (绿) |
| work / 作品 | `#F59E0B` (琥珀) |
| event / 事件 | `#EF4444` (红) |
| procedure / 程序 | `#EC4899` (粉) |
| place / 地点 | `#06B6D4` (青) |
| publication / 出版物 | `#6366F1` (靛) |

## 执行流程

1. 运行 `python scripts/build_knowledge_graph_data.py` 生成 JSON 与 file-compatible JS
2. 直接打开 `05-outputs/knowledge-graph.html`；完整渲染不得依赖网络或 HTTP server
3. 修改页面或静态依赖后，用浏览器复测主入口与二维归档；不得用截图或文件存在替代 SVG 渲染、筛选、搜索、选择、详情和缩放验收
4. 若浏览器自身限制本地脚本，可运行 `python -m http.server 8080 -d 05-outputs` 后打开 `http://127.0.0.1:8080/knowledge-graph.html`

## 状态边界

- `knowledge-graph-2d-manifest.json` 是冻结二维快照的输出完整性清单，不是 R2 provenance manifest；其 SHA-256 按 `sha256-lf-normalized-v1` 规范化 CRLF/LF，避免检出平台制造假漂移。
- 缺失 Theme 或 Topic membership 的 KU 必须显示为待组织状态，不得为布局效果推断正式归属。
- 主入口读取当前数据；二维归档保持独立数据和独立哈希边界。

## 参考

- `references/data-schema.md`
