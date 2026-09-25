# 辅助脚本入口

本目录提供定位、索引、校验、候选采集和受控写回。语义阅读、身份核对及关系判断由 Agent 按相应 Skill 完成；脚本成功不等于语义验收。脚本不是另一套工作流或权限表，按 AGENTS 的授权和实际任务选用。

## 常用检查

- `python scripts/audit_rule_drift.py`：核对现行入口、规则和明确路径。
- `python scripts/skill_registry.py`：检查唯一 Skill 根、名称、触发词、直接参考及派生注册表；Skill 变更后用 `--export` 更新导航。
- `python -m pytest tests/<相关测试文件>.py`：检验受影响的代码行为；需要全套回归时才使用 `python -m pytest tests`。
- `audit_repo.py`、`audit_relation_consistency.py`、`audit_content_quality.py`：按问题选择只读检查，结构/编码检查不替代语义判断。
- `validate_processing_package.py`：仅用于既有 compact-v4 机器接口；不强制普通语义任务生成该包。

## 按需工具

| 工作 | 工具与边界 |
|---|---|
| 外部候选采集 | verify_collect_*.py 只产生候选证据；Wikipedia/Wikidata collector 目前未自动完成双向 QID 配对，须按 verify 直接阅读与核对。Open Library 等书目来源只覆盖 archive 的适用子集 |
| 验证状态写回 | verify_apply_evidence.py 使用证据、语义裁决、dry-run 和显式 apply；evidence_batch_runner.py 只路由已有证据，不自行批准知识 |
| 未决事项定位 | audit_unverified_queue.py、plan_verification_batch.py、plan_relation_candidates.py 输出候选或计划；工具中的批量默认值不是日常研究固定配额 |
| 关系与名称投影 | build_relation_index.py 生成关系索引，build_relation_views.py 将正式边及反向导航投影到卡片可读表格，build_translation_index.py 生成名称索引；正式事实仍在 KU frontmatter，当前成果范围由 accepted.yml 指定 |
| 关系批量写回 | apply_relation_plan.py 只执行已审查 JSONL 的精确替换，默认 dry-run、整批预检、正式 apply 原子写回；语义类型与限定词须先写入计划 |
| 后续结构 | build_discovery_index.py、hierarchy_stress_test.py、apply_topic_memberships.py 仅在相应任务已启动时使用，不因空层级自动执行 |
| 运行与生成记录 | build_runtime_index.py、build_generated_projection_manifest.py 记录实际运行/输入输出，不证明研究完成；不为普通编辑刷新全部快照 |

## 收尾与历史入口

`run_sync_closure.py` 是可选的检查组合器，默认依据变化选择检查；`--full` 扩大审计和测试，`--refresh-generated` 改写研究与运行派生文件，`--check-generated` 比较 HEAD。页面数据独立受控：只有同时给出`--refresh-page`才重建`knowledge-graph-data.json/js`并纳入派生差异检查。仅在任务需要并允许相关写入时使用，不是每阶段固定动作；当前页面暂停，不传`--refresh-page`。

CI 在提交/推送触发的独立环境中依 `.github/workflows/quality.yml` 验证，不构成每次本地语义编辑的审批链。本地检查通过不等于远端 CI 已通过，提交/推送仍依据用户明确授权。

workflow-copy-manifest.json 是最初导入的历史清单，其中路径和数量不代表当前系统。portable/verify_copy.py 仅校验原始导出包或未修改的副本，不用于判断已迭代项目是否正确。当前测试直接使用 pytest；旧 portable/run_tests.py 所依赖的导入路径已经退役，不保留第二套测试入口。

## 派生文件约定

以下文件是**派生**的，不是事实源；日常批次不手动重建、不逐批提交，只在 S7 发布或按需时由对应脚本生成：

- `04-knowledge/quality/relation-index.yml`、`translation-index.yml`、`relation-candidates.yml`
- `06-runtime/state/current-health.json`、`skill-registry.json`、`generated-projections-manifest.json`、`candidate-index.jsonl`、`discovery-manifest.json`
- `06-runtime/automation/index.md`、`06-runtime/governance/governance-backlog.md`
- `05-outputs/index/*`（页面数据 `knowledge-graph-data.json/js` 暂停，需 `--refresh-page`）

事实源是 `04-knowledge/accepted.yml`（KU 登记）、`units/*.md` 卡片（结构化事实 + 散文），以及 S7 的 `release/vX/*.csv` 发布导出。审计脚本读派生文件只为检查，不把它们当源。

不默认新增工作包、机器状态、全量收尾或固定审核轮数。每项实际任务的过程与结果按 pipeline 分布存储；系统调整只记 CHANGELOG.md。
