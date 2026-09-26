# 辅助脚本入口

本目录提供定位、索引、校验、候选采集和受控写回。语义阅读、身份核对及关系判断由 Agent 按相应 Skill 完成；脚本成功不等于语义验收。脚本不是另一套工作流或权限表，按 AGENTS 的授权和实际任务选用。

## 常用检查

- `python scripts/audit_rule_drift.py`：核对现行入口、规则和明确路径。
- `python scripts/skill_registry.py`：检查唯一 Skill 根、名称、触发词、直接参考及派生注册表；Skill 变更后用 `--export` 更新导航。
- `python -m pytest tests/<相关测试文件>.py`：检验受影响的代码行为；需要全套回归时才使用 `python -m pytest tests`。
- `audit_repo.py`、`audit_relation_consistency.py`、`audit_content_quality.py`：按问题选择只读检查，结构/编码检查不替代语义判断。
- `audit_tables.py --strict-stage --summary`：检查必需列、ID 与自然键、跨表 FK、状态前置条件、关系域值域、enrichment 证据字段、卡片表格独立重扫、S0 哈希/覆盖及 S2 offsets/引文/空段理由。结构错误返回非零；S2 语义召回和准确率仍须按处理记录独立判断。
- `audit_s2_candidate_surfaces.py --chapter chp-1`：只读提示已登记、有类型候选名称在已迁移 S2 段中的未覆盖跨度；不自动写提及、不发现候选清单以外对象，也不证明召回率。
- `validate_processing_package.py`：仅用于既有 compact-v4 机器接口；不强制普通语义任务生成该包。

## 按需工具

| 工作 | 工具与边界 |
|---|---|
| 外部候选采集 | verify_collect_*.py 只产生候选证据；Wikipedia/Wikidata collector 目前未自动完成双向 QID 配对，须按 verify 直接阅读与核对。Open Library 等书目来源只覆盖 archive 的适用子集 |
| 验证状态写回 | `verify_apply_evidence.py --dry-run` 可检查旧格式计划；`--apply/--resume` 与 `evidence_batch_runner.py --apply-low-risk` 已停用，因其写卡片 frontmatter 而 enrichment 正迁至表。runner 的候选路由不自行批准知识 |
| 未决事项定位 | audit_unverified_queue.py、plan_verification_batch.py、plan_relation_candidates.py 输出候选或计划；工具中的批量默认值不是日常研究固定配额 |
| 关系与名称投影 | `relations.csv` 是关系输入，`enrichment.jsonl` 是字段表行输入；`build_cards.py --preview --ku <ku_id>` 依据卡片保留的小节与表头重建单卡表格行并输出差异，拒绝缺行或未知布局；`--check` 核对全库且不写卡；`--render` 全量预检通过后批量写回全部卡片，必须有明确用户授权。`build_relation_views.py --apply` 的旧 frontmatter 写入路径已禁用。`build_translation_index.py` 按需生成名称索引 |
| 关系批量写回 | `apply_relation_plan.py` 的 frontmatter `--apply` 已停用。经语义裁决的边写入 `relations.csv` 并运行表检查；卡片展示先用 `build_cards.py --preview --ku <ku_id>` 审阅 |
| 后续结构 | build_discovery_index.py、hierarchy_stress_test.py 仅在相应任务已启动时使用，不因空层级自动执行 |
| 运行与生成记录 | build_runtime_index.py、build_generated_projection_manifest.py 记录实际运行/输入输出，不证明研究完成；不为普通编辑刷新全部快照 |
| 表迁移与数据包 | `build_source_segments.py`、`build_entity_candidates.py`、`build_field_facts.py` 默认预览；需写表时显式用 `--apply`。`build_entity_candidates.py` 逐项保留索引决策、为第一章已接收 KU 补来源映射，并稳定保留有定位的 `body-mention` 候选。`build_tables.py` 已退役，执行只返回错误码、不写文件。`export_dataset.py` 默认预览，可创建或刷新 `release/v0.2-draft/`；该包不表示许可或质量验收通过 |

## 收尾与历史入口

`run_sync_closure.py` 是可选的检查组合器，默认依据变化选择检查；`--full` 扩大审计和测试，`--refresh-generated` 改写研究与运行派生文件，`--check-generated` 比较 HEAD。页面数据独立受控：只有同时给出`--refresh-page`才重建`knowledge-graph-data.json/js`并纳入派生差异检查。仅在任务需要并允许相关写入时使用，不是每阶段固定动作；当前页面暂停，不传`--refresh-page`。

CI 在提交/推送触发的独立环境中依 `.github/workflows/quality.yml` 验证，不构成每次本地语义编辑的审批链。本地检查通过不等于远端 CI 已通过，提交/推送仍依据用户明确授权。

workflow-copy-manifest.json 是最初导入的历史清单，其中路径和数量不代表当前系统。portable/verify_copy.py 仅校验原始导出包或未修改的副本，不用于判断已迭代项目是否正确。当前测试直接使用 pytest；旧 portable/run_tests.py 所依赖的导入路径已经退役，不保留第二套测试入口。

## 派生文件约定

以下文件是**派生**的，不是事实源；日常批次不手动重建、不逐批提交，只在 S7 发布或按需时由对应脚本生成：

- 04-knowledge/quality/translation-index.yml、relation-candidates.yml
- 06-runtime/state/current-health.json、skill-registry.json、generated-projections-manifest.json、candidate-index.jsonl、discovery-manifest.json
- 06-runtime/automation/index.md、06-runtime/governance/governance-backlog.md
- 05-outputs/index/* 和页面数据 knowledge-graph-data.json/js：只在用户明确下指令时生成，S7 不生成。

事实源迁移状态以[管线说明](../.agents/pipeline.md)和[第一章结果](../04-knowledge/results/patrons-and-painters-chp-1.md)为准；本文件只说明工具入口与边界。`release/v0.2-draft/` 是内部可移植性审阅包，不是冻结或公开版本；机械审计与 provenance diagnostics 不代替语义质量判断。

不默认新增工作包、机器状态、全量收尾或固定审核轮数。每项实际任务的过程与结果按 pipeline 分布存储；系统调整只记 CHANGELOG.md。
