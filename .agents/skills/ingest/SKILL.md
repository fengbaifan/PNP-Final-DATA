---
name: ingest
kind: leaf
phase: current
triggers:
  - ingest
  - 摄入来源
  - 语义处理
  - 知识元成稿
description: 负责摄入、处理、知识元成稿，三阶段分别保存结果；不自动启动发现。
---

# ingest

负责摄入、处理、知识元成稿，三阶段分别保存结果；不自动启动发现。

## 输入与工作

1. 摄入：读取用户任务、01-domain 的材料约定、来源版本和具体范围；核对可读性、章节/页码及缺失材料，登记来源。空库无历史对象是正常起点。
2. 处理：完整阅读声明范围内正文、注释与必要图像，理解论述、语境、对象和断言；保留来源定位、实际覆盖、歧义和遗漏。按语义划分，不用关键词或固定切块代替阅读。
3. 成稿：检索现有对象并判断同一性、类型和边界，形成有来源的 KU 正文及必要 claim；claim 是待证/有据断言，证据另指来源。不能判明的对象暂缓，不为补齐类型或结构制造对象。

标题与描述按 REV-018 使用中英文：title 采用“中文名（English name）”，name_en 保存对应英文名称，正文描述包含语义等值的中文与英文。名称待定和推测性表述在两种语言中都保留限定；具体写法见字段契约与正文参考。检查语言对应关系，不以英文存在就判定翻译合格。
按 REV-019、020 分开共用元数据、类型内容、关系与证据。按 REV-041、042 使用正文参考中对应类型的分组字段：单值独立成行，多值分条，履历／沿革按时间逐项；保留本章语境，内容栏不混入采集和审核过程。第三部分说明对应关系、证据和未决项。人物规范名以经核对的全名为主。适用但缺证的项目列入待补，不用空字段制造完整性，也不漏掉用户明确要求的项目。

类型边界以 `01-domain/taxonomy-registry.md` 为准，按原文指称的对象判断，不能按名字或文件后缀机械归类。未具正式题名但可定位的通信、合同、收据等仍应逐项判断 archive 成稿；不得以“脚注”“仅为引文”或“无全名”为由整批略去。有独立意义而现有类型暂不能表达的对象须保存为类型待决项，不自动丢弃。

## 产出与交接

摄入、处理的过程和结果分别在 03-processing/<task-id>/process/stages.md、results/stages.md。KU 成稿过程在同包 process/knowledge.md，知识结果在 04-knowledge/results/<task-id>.md，正文原位维护；实际成稿后在 accepted.yml 登记引用，既有试填不得批量接收。

按 pipeline 的阶段收口规则，摄入与处理定稿应包含可追溯的逐行语义分析、来源章页、句意摘要、校正和未决项，不能只留“已完成”的短报告。收口后过程只留必要裁决，消除与定稿重复的正文；知识元登记及以后阶段按顺序处理，已有下游内容不自动重新接收。

明确新增、更新、无变化和暂缓对象，逐个说明来源支持与缺口。上下文充分的成稿对象交 verify；依赖未读范围或关键歧义的对象不交接。第一次成稿不填写虚假的验证日期或任何预设层级。

## 必要检查与工具

直接核对范围覆盖、来源定位、对象重复和正文忠实性；自查不能称独立验收。普通任务不强制 JSONL/manifest/summary 五件套。既有 compact-v4 包及其机器校验按 model-semantic-processing 契约处理，来源指纹变化需重审受影响内容。
批量候选接口使用 payload.knowledge_match 和 candidate 状态；approved 后的实际写回才记 applied，无变化 no_delta，失败 blocked。机器完整性不代替 semantic_acceptance。

## 按需直接参考

- `references/body-template.md`：三部分、双语描述、九类实体的分组字段与条目格式；按对象类型读取。
- `references/knowledge-unit-field-contract.md`：创建或更新共同元数据。
- `references/taxonomy.md`：类型、名称及重复对象判断。
- `references/citation.md`：新增或整理出处。
- `references/distillation-system-contract.md`：来源/候选/成稿证据边界有疑问时。
- `references/relation-types.md`：正文包含关系、需要记录正式边时。
- `references/hierarchy-field.md`：后续结构实际启动后使用，初期不填。
- `references/model-semantic-processing.md`：仅 compact-v4 接口或相应历史包续接。
- `.agents/skills/system-upgrade/references/work-package-contract.md`：仅批量机器写回或旧接口续接。
