---
name: ingest
kind: leaf
phase: current
triggers:
  - ingest
  - 摄入来源
  - 语义处理
  - 知识元成稿
description: 负责 S0 来源、S1 全书候选、S2 语义处理、S4 KU 登记；对应产物 `segments.jsonl`、`entity-candidates.csv`、`mentions.csv`、`book-statements.jsonl`、`ku-manifest.csv`。原书陈述标 `origin=book`。不自动启动发现。
---

# ingest

负责 S0 来源、S1 全书候选、S2 语义处理、S4 KU 登记；对应产物 `segments.jsonl`、`entity-candidates.csv`、`mentions.csv`、`book-statements.jsonl`、`ku-manifest.csv`。原书陈述标 `origin=book`。不自动启动发现。

## 输入与工作

1. 摄入：读取用户任务、01-domain 的材料约定、来源版本和具体范围；核对可读性、章节/页码及缺失材料，登记来源。空库无历史对象是正常起点。
2. 处理：完整阅读声明范围内正文、注释与必要图像，理解论述、语境、对象和断言；按pipeline共同格式同步记录原文关系候选、提及、指代、证据跨度及语气／发言者限定。候选只保存原文实际表达，不用外部补足倒推原义，也不提前写成正式边。
3. 成稿：检索现有对象并判断同一性、类型和边界，将候选提及映射到新建或已有KU；端点不明时保留待决，不由关系猜造实体。形成有来源的KU正文及必要claim；claim是待证/有据断言，证据另指来源。

标题与描述按 REV-018 使用中英文：title 采用“中文名（English name）”，name_en 保存对应英文名称，正文描述包含语义等值的中文与英文。名称待定和推测性表述在两种语言中都保留限定；具体写法见字段契约与正文参考。检查语言对应关系，不以英文存在就判定翻译合格。
按 REV-019、020 分开共用元数据、类型内容、关系与证据。按 REV-041、042 使用正文参考中对应类型的分组字段：单值独立成行，多值分条，履历／沿革按时间逐项；保留本章语境。按REV-072，原书摘录随sources保存；卡内只保留事实、必要限定、身份和关系入口及逐条证据，阅读、核验、裁决和待补说明另存03过程。人物规范名以经核对的全名为主。适用但缺证的项目列入过程待补，不用空字段制造完整性，也不漏掉用户明确要求的项目。

类型边界以 `01-domain/taxonomy-registry.md` 为准，按原文指称的对象判断，不能按名字或文件后缀机械归类。未具正式题名但可定位的通信、合同、收据等仍应逐项判断 archive 成稿；不得以“脚注”“仅为引文”或“无全名”为由整批略去。有独立意义而现有类型暂不能表达的对象须保存为类型待决项，不自动丢弃。

## 产出与交接

摄入、处理的过程和结果分别在 03-processing/<task-id>/process/stages.md、results/stages.md。KU 成稿过程在同包 process/knowledge.md，知识结果在 04-knowledge/results/<task-id>.md，正文原位维护；实际成稿后在 accepted.yml 登记引用，既有试填不得批量接收。

按 pipeline 的阶段收口规则，摄入与处理定稿应包含可追溯的逐行语义分析、来源章页、句意摘要、校正、关系候选／指代／证据跨度和未决项，不能只留“已完成”的短报告。候选使用稳定锚点，成稿时记录提及到KU的映射；收口后过程只留必要裁决，消除与定稿重复的正文。

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
