# 《赞助人与画家》知识系统

项目初始化版本：0.1.0。第一章作为知识元与知识图谱样例，进度见[第一章当前结果](04-knowledge/results/patrons-and-painters-chp-1.md)；章前材料已完成摄入、处理并进行知识元登记，见[章前当前结果](04-knowledge/results/patrons-and-painters-front-matter.md)。第六章后置，知识涌现与页面暂停；未接收内容不计作有效成果。

[AGENTS.md](AGENTS.md) 是 Codex 唯一总入口；[pipeline](.agents/pipeline.md) 定义交接，八个 Skill 在 `.agents/skills/`。当前规则和文档不再各自累计大版本号。

采用渐进式读取与分布记录：总入口定位任务和 Skill，按需读其直接参考；过程在 03 的任务包分阶段记录，04 保存当前成果与结果，06 保存用户原话和系统治理。结果原位更新，历史判断保留，入口不复制整套报告。详细读取与记录规则只在 AGENTS 维护。

```mermaid
flowchart LR
  subgraph P1[第一部分：知识元与知识图谱]
    S[01 材料范围与约定] --> A[摄入] --> B[处理：完整语义阅读]
    B --> C[知识元：对象与端点]
    C --> D[初步对齐：身份与版本]
    D --> E[补足：书内与外部分源]
    E --> F[关系：正式／待决／否决]
    B -.同步记录.-> R[关系候选：提及·指代·证据跨度]
    R -.端点映射.-> C
    R -.逐项裁决.-> F
    E -.外部关系事实.-> F
  end
  subgraph P2[第二部分：知识发现与知识呈现]
    G[Topic] --> H[Theme] --> I[Dimension] --> J[Domain]
    J --> K[成果组织与页面]
  end
  F -.用户启动第二部分.-> G
```

六阶段仍按摄入、处理、知识元、对齐、补足、关系依次交付。关系候选在处理原文时同步记录，随后更新端点映射并在关系阶段裁决；候选不是正式边，外部补足也不覆盖原书表达。结构从知识元及正式关系中逐级涌现，不预设 Topic、Theme、Dimension、Domain 或层级归属；可在实际形成的层次停止，未开展不是缺陷。

| 目录 | 职责 |
|---|---|
| 01-domain | 材料范围、表达与命名约定 |
| 02-sources | 来源资产与登记 |
| 03-processing | 摄入至关系及后续发现的过程记录；摄入处理结果与覆盖依据 |
| 04-knowledge | 知识元、关系、证据、涌现结构及当前结果说明 |
| 05-outputs | 呈现过程、定稿与页面 |
| 06-runtime | 用户记录、治理与必要运行状态 |
| [07-paper](07-paper/README.md) | 论文定位、写作与实验建议、投稿期刊及分区依据；不新增研究阶段 |

[有效成果登记](04-knowledge/accepted.yml) 汇集第一章与章前材料已接收的来源支持成果；各范围的完成状态以对应任务结果为准。知识元登记不表示全部对齐、补足或关系已完成。
[页面](05-outputs/knowledge-graph.html) 保留视觉样式，本次按用户要求暂停刷新，因此尚未呈现第一章新成果。

日常直接分析、写作并核对受影响内容；外部核验、批量预检、恢复状态和测试按需启用。只用 main，Git 提交/推送须有明确授权。

用户原话见 [user-revisions.md](06-runtime/governance/user-revisions.md)，有效要求见 [current-requirements.md](06-runtime/governance/current-requirements.md)，系统过程与结果见 [system-upgrade-log.md](06-runtime/governance/system-upgrade-log.md)。
