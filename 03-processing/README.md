# 摄入与处理层

阶段职责与交接以 `.agents/pipeline.md` 为准。处理阶段先完整语义阅读，再形成可追溯分析；不能以机器覆盖检查冒充语义接受。

每个来源/处理对象沿用固定包目录：

- process/stages.md：阶段 1 摄入的版本、范围、资产与缺失核对；阶段 2 处理的阅读、分析、取舍和过程决定，按阶段分节。
- results/stages.md：分别说明摄入可处理范围和当前处理结论、覆盖边界、候选及下一阶段条件；来源登记链接回 02-sources/source-registry.md。
- compact-v4 的 source-map.jsonl、semantic-units.jsonl、candidate-ledger.jsonl、manifest.json、summary.md：保留既有覆盖、指纹和写回接口；summary 是兼容摘要，不复制新的阶段结果。

未开始的阶段不生成空文档。已有包保留原工件和历史验收，只有继续处理时才在固定过程/结果文件记录变化；不能为新目录规则重写旧来源与验收。

状态区分未开始、处理中、已完成、部分完成、受阻和暂不开展。processing completed 只说明声明范围的处理状态，不等于知识元对齐、补足或关系完成。

必要机械校验：`python scripts/validate_processing_package.py <包目录>`。来源指纹、范围无缺口及语义验收边界遵守 ingest 契约。
