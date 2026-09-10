# 页面数据契约

保留现有页面样式和适用交互，数据来自本项目 accepted.yml 登记的有效对象，未接收的遗留内容不进入展示。

```json
{
  "nodes": [],
  "links": [],
  "structure": {"topics": [], "themes": [], "dimensions": [], "domains": []},
  "stats": {
    "total_nodes": 0,
    "total_links": 0,
    "relation_index_total": 0,
    "by_type": {},
    "hierarchy": {"domain_assigned": 0, "dimension_assigned": 0, "theme_assigned": 0, "topic_assigned": 0},
    "structure_nodes": {"topics": 0, "themes": 0, "dimensions": 0, "domains": 0}
  }
}
```

nodes 含稳定 id、title、type、path 及实际存在的状态/来源信息；KU 类型为 person/family/institution/place/work/archive/term/procedure/event。consensus 如提供，使用 tentative/disputed/confirmed。
后续呈现须保留 KU 的双语标题/描述及元数据、内容、关系与证据三部分，结构化属性和历史变化来自实际正文，不为页面反填知识。当前仅明确消费规则，尚未完成全库双语/三部分内容迁移及页面适配；本轮不刷新网页。
links 只表示登记对象间已有证据的正式关系，含 source/target/relation_type 及实际 evidence_ref；端点不在本次数据范围的边不显示，不能把遗留全库关系数量当当前统计。
structure 各数组按实际节点生成，父层未形成合法。展示字段兼容 primary_*、topic_memberships 和 code，但不得预设 A–E 分组或填满所有层级。
统计、筛选和详情都从当前数据派生，不放旧项目示例规模；空数据有明确说明。

scripts/build_knowledge_graph_data.py 生成 knowledge-graph-data.json/js；knowledge-graph.html 是当前入口。本地 D3 资源与样式保留，历史 knowledge-graph-2d* 不改写或作为当前数据。检查数据切换、空状态、动态层级、节点关系和证据链接。
