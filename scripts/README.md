# Scripts — 受控机械执行器

本目录只承载确定性索引、校验、证据分流和经授权写回。Agent 与 Skill Contract 负责语义阅读和裁决；脚本输出不得被解释为事实确认、关系批准或知识成熟。

## 主要入口

- `run_sync_closure.py`：默认读取 Git 变化集，只运行最近邻只读门禁；`--full` 强制全量审计与测试；发布门禁使用 `--refresh-generated --full --check-generated`。
- `apply_topic_memberships.py`：只消费已审、带 Topic 哈希和 Git 基线的精确计划；整批预检后 dry-run 或原子写回 KU 五级层级字段。默认拒绝已有层级；显式 `existing_hierarchy_policy: merge` 时按 Topic 键安全增量合并、保留既有关系并跳过无变化对象。脚本不负责语义分类。
- `evidence_batch_runner.py --batch-manifest <manifest>`：证据批次路由器。只做 evidence 分类、非空队列输出、可选 L1 dry-run/apply 和一次 change-aware closure，不承担通用 Pipeline、语义裁决、快照或 Git 操作。
- `audit_repo.py`：一次解析 KU 快照，分别报告结构契约健康、知识结构质量、证据质量、runtime 保留状态与未计分的知识成熟度。
- `audit_unverified_queue.py`：只读评估全库或指定结果集中的置信度、单来源、到期与状态冲突；必须显式指定 JSONL 输出，可附中文摘要，不修改 KU 状态。
- `plan_verification_batch.py`：从置信度队列中机械筛选 120–180 个同时为单来源与 tentative 的高价值 KU，可用重复的 `--unit-type` 限定批次对象类型，按 40–50 个划分 checkpoint，并报告 Topic 覆盖；不收集证据或改变知识状态。
- `verify_collect_wikidata.py`：Wikidata L2 evidence collector；单 KU 的候选实体一次批量拉取，429/5xx/超时采用有界重试并输出结构化 `collection_error`，`--retry-from` 只重跑历史 `api_error` 且不覆盖原 evidence。
- `verify_collect_lcnaf.py`：人物/机构的 LC/NACO 权威名称 evidence collector；校验名称与 authority 类型，歧义缩写和类型冲突 fail closed，只生成待 Agent 复核的 JSONL。
- `verify_collect_openlibrary.py`：Work/Publication 的 Open Library 书目 evidence collector；核对标题、初版年、作者、出版社与 ISBN，年份冲突和同名异作者 fail closed，不验证视觉解释或领域相关性。
- `build_discovery_index.py`：把关系、processing、runtime 与 output 的候选归并为统一 candidate index；不执行任何写回。
- `build_generated_projection_manifest.py`：为当前生成式 R2 投影记录有效输入、生成器、参数、KU 状态摘要与输出哈希。
- `validate_processing_package.py`：校验 compact-v4 指纹资产、processing scope、逐行跨度并集与 Agent 复读字段；来源漂移返回 `reopened_source_drift`。
- `build_runtime_index.py`：重建运行批次索引；`--retention-report` 只读报告 R1/R2/R3、容量与 provenance 状态。R2 必须由 manifest 精确声明且输出哈希匹配。
- `hierarchy_stress_test.py`：默认只读输出五级层级缺口；显式 `--queue-output` 才生成语义待审队列。
- `plan_relation_candidates.py`：默认只读召回关系候选；显式 `--write` 才刷新候选投影。

## 权限边界

| 类别 | 默认风险 | 约束 |
|---|---:|---|
| `audit_*.py` / `validate_*.py` | 只读 | 不修改知识或来源 |
| `build_*.py` / `generate_*.py` / `write_*.py` | 按脚本授权 | 只写明确定义的派生投影 |
| `collect_*.py` / `verify_collect_*.py` | 需确认 | 只收集证据，不自动 apply |
| `verify_apply_evidence.py` | 需确认 | 仅消费通过策略校验的 evidence JSONL；正式写回必须显式 `--apply` |
| `evidence_batch_runner.py` | 需确认 | `--apply-low-risk` 仅允许既有 KU 的 L1 证据写回 |
| `hierarchy_stress_test.py --queue-output` | 需确认 | 只生成缺口队列，不决定或写回归属 |
| `plan_relation_candidates.py --write` | 需确认 | 只刷新候选，不批准或应用关系 |

任何脚本都不得自动：

- 选择 KU 类型或裁决 claim 真伪；
- 将单来源证据升级为 `confirmed` 或 `externally_verified`；
- 把候选、health、backlog 或测试通过等同于语义验收；
- 创建分支、worktree、commit 或 push；
- 删除历史 runtime 工件。

## 收尾约定

一个用户目标原则上只有一个 work package。包内 checkpoint 不重复触发全量收尾；最终统一执行一次生成刷新和全量门禁。生成内容先刷新并提交，随后再以 `--check-generated` 验证相对 `HEAD` 无漂移。旧固定行切块摄入器和批次内一次性 writer 已退役，不在工作树保留第二套可执行系统。

退役脚本不在工作树建立第二套归档；Git 历史与系统升级记录承担 provenance。历史 runtime evidence 仍按保留契约原地保存，不受此规则影响。
