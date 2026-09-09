# 关系治理契约

## 权威与投影

```text
KU frontmatter.relations / claim bindings  正式关系断言
relation-types.yml                         唯一受控词表与 inverse 映射
relation-index.yml                         可重建 R2 投影
related / weak_associations                召回或排除信号，不是正式关系
```

正式关系必须包含受控 `relation_type`、有效 target，以及能支持该具体关系的
`evidence_ref` 或 `claim_id`。反向边可以由索引生成，但不得反向改写知识事实。

## 状态边界

| 状态 | 含义 | 动作 |
|---|---|---|
| `legacy_related` | 旧相关性记录 | 仅作召回，不自动转正 |
| `weak_inference` | 共现、相似或模型推断 | 保留在弱关联层 |
| `needs_evidence` | 类型可能成立但证据不足 | 路由 verify / source review |
| `evidence_backed_relation` | 类型、方向、端点和证据均已审查 | 可进入正式关系图 |
| `conflict` | 证据或端点互相矛盾 | 路由 reconcile |

## 类型化写回

```text
relation candidate
-> Agent 审查端点、方向、relation_type 与证据范围
-> approved exact apply plan
-> dry-run diff
-> map-driven relation apply
-> relation consistency + index rebuild
-> applied / no_delta / blocked
```

- 批量大小由语义连贯性、写回文件交集和 dry-run 可审阅性动态决定，不设固定5–10条窗口。
- 同一文件串行写回；互不相交的 evidence collect 可以并发。
- 每个 applied relation 必须反查 candidate、decision、evidence 和 apply result。
- 批次内一次性 Python writer 不是现行入口；稳定机械行为应进入受控执行器，历史代码由 Git 保存。

## 禁止

- 不从 `related`、正文链接、共享 tag、同章共现或 Cluster 自动生成正式关系。
- `weak_associations` 是排除信号，索引 fallback 不得重新升级。
- 不用脚本选择关系语义、方向、强度或作者责任。
- 不以关系数量、节点度数或健康分数提升 confidence / consensus。
- Domain、Dimension、Theme、Topic 与 KU 的组织归属使用 hierarchy membership；不得伪装成普通 relation，也不存在 Cluster membership 正式关系。

## 机械验收

- relation type 与 inverse 来自 `relation-types.yml`。
- target 存在，类型兼容，证据引用可解析。
- 显式关系可由 inverse/backlink 找回；派生边不覆盖权威输入。
- `relation-index.yml` 重建幂等，provenance manifest 与输出哈希一致。
