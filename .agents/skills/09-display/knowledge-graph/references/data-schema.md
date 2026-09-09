# 知识图谱数据格式规范

## JSON结构

```json
{
  "nodes": [{
    "id": "string",
    "title": "中文标题",
    "name_en": "English Name",
    "type": "person|institution|place|work|publication|term|procedure|event",
    "type_zh": "人物|机构|地点|作品|出版物|术语|程序|事件",
    "color": "#HEX",
    "tags": ["标签1", "标签2"],
    "confidence": "high|medium|low",
    "consensus": "confirmed|tentative|debated",
    "sub_type": "子类型",
    "source_count": "来源数量",
    "evidence_status": "验证状态",
    "primary_domain": "领域代码",
    "secondary_domains": ["次级领域代码"],
    "primary_dimension": "维度代码",
    "primary_theme": "Theme 稳定代码",
    "secondary_themes": ["次级 Theme 代码"],
    "role_in_theme": "Theme 内角色",
    "topic_memberships": [{"topic": "Topic 代码", "theme": "父 Theme", "role": "成员角色"}],
    "hierarchy_scope_note": "层级适用范围说明",
    "description": "简短描述",
    "path": "相对路径"
  }],
  "links": [{
    "source": "node_id",
    "target": "node_id",
    "relation_type": "权威 relation vocabulary 中的关系类型",
    "relation_source": "explicit|inferred_by_rule|migrated_from_related",
    "review_status": "关系审查状态",
    "confidence": "high|medium|low",
    "evidence_ref": {}
  }],
  "structure": {
    "domains": [{"id": "information-visualization-history-and-theory", "code": "information-visualization-history-and-theory", "title": "..."}],
    "dimensions": [{"id": "B-visual-encoding-techniques", "code": "B", "title": "..."}],
    "themes": [{"id": "b4-cartography-and-isoline-techniques", "code": "B.4", "title": "..."}],
    "topics": [{"id": "maps-and-power", "code": "maps-and-power", "parent_theme": "D.4", "title": "..."}]
  },
  "stats": {
    "total_nodes": 1637,
    "total_links": 2225,
    "relation_index_total": 3466,
    "skipped_non_unit_relations": 1241,
    "by_type": {"person": 430, "institution": 90, "place": 19, "work": 620, "publication": 74, "term": 284, "procedure": 91, "event": 29},
    "hierarchy": {
      "domain_assigned": 340,
      "dimension_assigned": 340,
      "theme_assigned": 340,
      "topic_assigned": 0
    },
    "structure_nodes": {"domains": 1, "dimensions": 5, "themes": 33, "topics": 22}
  }
}
```

## 数据生成器

`scripts/build_knowledge_graph_data.py` — 从 `04-knowledge/units/` 提取全部知识元，
读取 `04-knowledge/structure/` 的正式层级，以 `04-knowledge/quality/relation-index.yml` 为唯一关系来源，并只生成：

- `05-outputs/knowledge-graph-data.json`：机器可读 JSON。
- `05-outputs/knowledge-graph-data.js`：供 `file://` 直接打开 HTML 时读取的同内容脚本。

## 展示实现与依赖

- `05-outputs/vendor/d3.v7.9.0.min.js`：固定版本的本地 D3 运行时；页面不得依赖远程脚本或字体。
- `05-outputs/knowledge-graph.html`：当前 D3 二维主入口，读取 `knowledge-graph-data.*`。
- `05-outputs/knowledge-graph-2d.html`：冻结的 D3 二维归档，读取独立的 `knowledge-graph-2d-data.*`。
- `05-outputs/knowledge-graph-2d-manifest.json`：冻结二维归档的入口、数据、D3 依赖与 SHA-256 边界。

`knowledge-graph-2d-manifest.json` 是用户输出完整性清单，不是 runtime R2 provenance manifest。它只约束冻结二维归档；`hash_mode: sha256-lf-normalized-v1` 要求计算前把 CRLF 规范化为 LF，以保证 Windows 与 Linux 检出一致。当前主入口的数据由生成器和 closure 管理。

层级字段只呈现仓库中已正式写入的挂载。缺失 `primary_theme` 的知识元进入“待组织空间”；缺失 `topic_memberships` 时不得根据相似度或画面需要虚构 Topic。

`structure.*[].id` 是结构文件的稳定 slug，显示与布局匹配必须优先使用 `code`。例如 Theme 文件 `b4-cartography-and-isoline-techniques.md` 的 `id` 为文件名 slug，而正式层级键是 `code: B.4`。
