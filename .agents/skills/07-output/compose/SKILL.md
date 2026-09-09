---
name: compose
kind: leaf
triggers:
  - compose
  - 写作生成
  - draft-outline
  - 写作提纲
  - 规划写作
description: >
  知识生产写作技能。基于知识元、层级体系、涌现主题和验证边界规划提纲或生成结构化文本输出。
---

# compose 技能 v2.0

## 支持类型

| 类型 | 说明 |
|---|---|
| `research-report` | 研究报告 |
| `literature-review` | 文献综述 |
| `academic-section` | 学术段落 |
| `argument-outline` | 论证提纲 |
| `research-outline` | 研究提纲与覆盖规划 |
| `annotation` | 文献注释 |
| `concept-essay` | 概念解析 |
| `comparison` | 对比分析 |

## compose 流程

```text
1. 解析主题与输出类型
2. 按 query 的最小检索步骤召回相关知识元和结构文档；运行时支持多 Skill 组合时可同时加载 query，但不得把 Skill 当作确定性函数调用
3. 过滤或标注低置信 / disputed / L7-only 内容
4. 组织论证结构并生成文本
5. 如需落盘，写入 05-outputs/drafts/ 或 exports/，同时登记 output metadata，初始 `file_back_status: not_reviewed`
```

## 写作规则

- 事实陈述优先使用 externally verified 或至少 source_backed 的知识元
- 使用 L7 支持的内容时，必须说明其证据边界
- 若写作中发现结构空洞，可建议回流 `enrich`、`verify` 或 `build-hierarchy`
- 输出只是重组现有知识且没有新解释时，不固定运行 `retrospect`
- 输出形成新的可检验 claim、关系、主题或研究问题时，路由 `retrospect`；未经回溯不得写成 `reviewed_no_candidates` 或 `applied`

## 提纲模式

当触发词为 `draft-outline`、写作提纲或规划写作时，compose 只执行规划，不直接扩写正文：

1. 解析研究问题和所需证据类型。
2. 检索 Domain、Dimension、Theme、Topic、KU 与验证状态；运行时支持时可同时加载 `query`，否则直接执行本 Skill 的检索步骤。
3. 按章节标注可用知识、证据边界、覆盖缺口和需补证项，不用 High/Medium/Low 代替实际依据。
4. 生成可审查提纲；需要落盘时写入 `05-outputs/drafts/<问题>-outline-<日期>.md` 并登记 output metadata。
5. 只有用户继续要求撰写时才进入正文生成；提纲发现的新 claim 或 Topic 仍先路由 `retrospect`。

提纲没有独立状态机、写回入口或产物类型，因此并入 compose，而不是单独 Skill。
