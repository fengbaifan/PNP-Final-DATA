# 知识元关系契约

> 受控类型与 inverse 映射的唯一机器事实源是同目录的 `relation-types.yml`。本文件只定义语义边界和字段契约，不复制完整枚举。

## 一、权威与投影

- 已批准的 KU `relations` 是当前关系断言输入。
- `04-knowledge/quality/relation-index.yml` 是由输入生成的 R2 投影，不是独立关系事实源。
- `related` 仅为历史兼容字段；`weak_associations` 对其具有排除优先级。
- 生成器、审计器和 batch prescreen 必须共同加载 `relation-types.yml`，不得各自维护类型集合或 inverse map。
- REV-019、020 的正文“关系与证据”部分解释并指向这些记录，不复制另一套正式边。内容表中的亲缘、创作者、设计师、所有者等项目须有各自依据；正式建边仍检查有效端点、受控类型、方向及具体证据，不能由字段/链接存在自动生成。历史角色与时间限定不得在建边时丢失。

## 二、字段

```yaml
relations:
  - relation_type: authored_by
    target: ../persons/example.md
    target_type: person
    note: "关系语义说明"
    evidence_ref: source-or-claim-reference
    confidence: medium
    relation_source: explicit
    review_status: evidence_backed_relation
```

最低要求：

- `relation_type` 必须属于受控 schema；历史 generic 类型只能按 baseline 读取，禁止新增。
- source/target 必须存在并满足方向语义。
- 要求 inverse 的类型使用 schema 中的映射；自动补全只生成派生 backlink，不构成第二次语义裁决。
- `evidence_ref`、`claim_id` 或明确的 `needs_evidence` 状态至少存在一个。
- 不得仅凭共享标签、年代、同章或正文链接提升为正式关系。

## 三、来源与审查状态

`relation_source`：

- `explicit`：Agent 已在 KU 中声明；
- `inferred_by_model` / `inferred_by_rule`：仅为候选信号；
- `migrated_from_related`：历史兼容记录，不自动成为正式关系。

`review_status`：

- `evidence_backed_relation`：证据和语义已审查；
- `needs_evidence`：语义可能成立但证据不足；
- `weak_inference`：仅保留候选信号；
- `conflict`：存在方向、对象或证据冲突。

## 四、弱关联

```yaml
weak_associations:
  - target: ../terms/example.md
    reason: co_occurrence_in_same_topic
    confidence: low
    evidence_gap: no_direct_evidence
```

weak association 不进入正式 relation index；重新运行生成器不得复活已排除信号。

## 五、变更流程

新增或修改关系类型时，先修改 `relation-types.yml`，再运行 schema 测试、relation index 重建与关系一致性审计。类型、方向和强度仍由 Agent 裁决，脚本只校验受控值、端点和 inverse。
