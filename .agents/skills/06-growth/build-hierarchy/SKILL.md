---
name: build-hierarchy
kind: leaf
triggers:
  - build-hierarchy
  - 构建层级
description: >
  构建或重建领域—维度—主题—议题—知识元五级组织；Cluster 只作跨层发现候选。
---

# build-hierarchy v4.1

> 层级是可演化的解释结构，不是自动分类结果。默认只审查变化集合；只有用户明确要求全量重建、现有覆盖证明异常或结构契约迁移时才扫描全部 KU。

## 权威结构

```text
Level 1 domain      可演化的总问题域
Level 2 dimension   可演化的分析轴
Level 3 theme       稳定问题群；A.1/B.2 等代码
Level 4 topic       可操作、可回答的研究问题
Level 5 KU          通过 topic_memberships 提供材料

cluster             可扫描任意层级的发现候选，不是结构节点
```

正式节点分别物化在 `04-knowledge/structure/domains/`、`dimensions/`、`themes/` 和 `topics/`。Level 4 只组织 8 类 KU；claim 保留在 assertion/evidence 层。

## 流程

1. 读取当前 hierarchy、domain、dimension、topic 与本次新增/变更 KU；默认不重复扫描未变化对象。
2. 检查变化对象能否进入现有 Topic；不能时形成 topic 候选。多个 Topic 出现稳定共同边界时形成 theme 候选，再评估 dimension/domain 候选。
3. 为通过语义审查的 KU 记录 `primary_domain`、`primary_dimension`、`primary_theme` 与一个或多个 `topic_memberships`；每个 membership 必须声明 role。
4. 每个 Topic 检查理论、实证/材料、文献三类支撑；缺口保留为研究债务，不制造占位 KU。
5. 仅在结构发生实际变化时更新 hierarchy 版本并归档旧版；纯 KU 挂载使用 checkpoint，不虚增结构版本。
6. 运行链接、node type、挂载覆盖和历史兼容检查。

批量写回必须先形成逐对象语义决定；需要机械执行时使用 `scripts/apply_topic_memberships.py` 消费带 Topic 哈希和 Git 基线的精确计划。该执行器不得生成或推荐 membership。增量批次必须显式声明 `existing_hierarchy_policy: merge`；执行器合并已审 membership、保留未被计划替换的既有关系并跳过无变化对象，禁止隐式覆盖整组 membership。

大批历史回填可先用 `scripts/hierarchy_stress_test.py --source-doc-id ... --queue-output ... --generation-manifest ...` 按同源、同类型和来源章节生成候选召回队列；需要把来源库存切成单一类型批次时，显式增加 `--unit-type person|institution|place|work|publication|term|procedure|event`。来源范围只接受 KU `sources[].evidence_ref` 中带 `source_file` 的直接证据；relation 的证据出处不能冒充 KU 来源。召回器只汇总正式 relation 邻居、已审 Topic membership、共享来源章节与文本重合信号；所有候选必须保持 `decision.status: pending`、`apply_permitted: false`，并由 Agent 逐对象复读后另行裁决。长批次的 checkpoint 只作为同一 work package内的恢复边界，不得拆成多个批次或提前写回部分 KU。

历史 KU 的 Topic membership 必须分批语义审查，不得按 tags、链接、文件名或 Cluster 自动裁决。已批准的旧 Topic code 迁移为 Theme code 不改变其原语义边界。

## 字段与检查点

- 新增或重构 KU 使用顶层 `primary_domain`、`primary_dimension`、`primary_theme` 和至少一个带 role 的 `topic_memberships`；历史回填不得机械裁决。
- hierarchy 顶部记录版本、日期与评估基线；当前库存只从 health 读取。
- node 所在目录必须与 `node_type` 一致，所有引用目标存在，Domain/Dimension/Theme/Topic/KU 不混写。
- 新增知识能否被现有维度解释必须显式评估；未完成 KU 字段回填时不得声称全量挂载完成。

## 参考

- `../../01-intake/ingest/references/hierarchy-field.md`
- `../../../../01-domain/dimension-registry.md`
