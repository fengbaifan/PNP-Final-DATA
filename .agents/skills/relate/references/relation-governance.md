# 关系治理契约

适用范围：以下计划、机器账本及事务字段仅用于批量机器写回或既有接口的续接。普通语义编辑在现有过程记录中说明依据、原位更新并定向核对，不强制另建候选/计划/摘要。

## 权威与投影

```text
KU frontmatter.relations / claim bindings  正式关系断言
relation-types.yml                         唯一受控词表与 inverse 映射
relation-index.yml                         可重建 R2 投影
related / weak_associations                召回或排除信号，不是正式关系
```

正式关系必须包含受控 `relation_type`、有效 target，以及能支持该具体关系的
`evidence_ref` 或 `claim_id`。反向边可以由索引生成，但不得反向改写知识事实。

关系事实还应按来源实际支持范围保留必要限定：`time` 记录有据日期、年份或区间，`role` 记录参与者在该关系中的具体职责，`scope` 记录作品版本、具体项目或地点作用。没有精确值时不补造字段。谓词本身先区分创作、委托、赞助、师承、合作、朋友、亲缘、成员／雇佣、所有权、保管、安置和一般位置；`note` 用于解释争议与边界，不代替可查询的核心角色。

`owned_by`通常用于work→所有人；当place明确表示建筑、宅邸或地产，且来源直接陈述其历史所有权时，也可由place指向所有人。应记录可支持的时期与权利范围；只有居住、管理、使用、委托或馆藏关系时不得改写成所有权。来源未给取得或转移日期时保留日期缺项，不推定连续产权。

`located_at`用于work指向其物理地点，也用于建筑／地点place指向其所在的更大地点place。它表示空间位置，不自动表达行政隶属、政治归属或产权。

关系完整性按已采纳内容反查，不以“现有 relations 全部可解析”代替。正文中出现具名、可独立识别且承担上述关系端点的对象而尚无 KU 时，相关关系保持待处理并回 ingest；不为补端点递归接收网页中所有背景链接。

## 状态边界

| 状态 | 含义 | 动作 |
|---|---|---|
| `legacy_related` | 旧相关性记录 | 仅作召回，不自动转正 |
| `weak_inference` | 共现、相似或模型推断 | 保留在弱关联层 |
| `needs_evidence` | 类型可能成立但证据不足 | 路由 verify / source review |
| `evidence_backed_relation` | 类型、方向、端点和证据均已审查 | 可进入正式关系图 |
| `conflict` | 证据或端点互相矛盾 | 路由 verify |

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
