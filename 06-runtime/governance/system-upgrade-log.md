# 系统升级记录

## 工作流复刻初始化

- 原工作流按字节复刻，来源及哈希见 workflow-copy-manifest.json。
- 新增空数据目录与复用说明，不复制源项目知识和历史验收结果。
- 未执行新领域语义适配，未初始化 Git，未启用或验证客户端 Hook。
- 复制与回归验证结果见交付文件夹的 validation-report.json。
- 新项目正式运行后在本文件追加其自身升级记录。

## 领域迁移：信息图表史 → 《赞助人与画家》（2026-09-09）

### 目标与范围

把知识蒸馏系统从旧领域整体迁移到新领域《赞助人与画家》：巴洛克时期意大利艺术与社会。写入范围：01-domain 全部 6 个文件、项目标识（README、pyproject、02-sources 登记）、ingest/verify/enrich 参考文档、4 个脚本常量、5 组测试与 portable fixture、05-outputs 页面、客户端适配、运行状态重建。禁止改写 02-sources 来源本体；旧领域的知识元、数量、健康分数与验收结论一律不随迁。

### 领域模型决策（用户确认）

- 沿用 A–E 编码框架，五个维度重新定义并全部标为 pilot（赞助与市场机制 / 艺术家与职业网络 / 城市与区域艺术中心 / 宗教权力与机构 / 作品风格与图像志）。
- KU 双语约定：正文中文为主，人名/书名/术语附英文原文，引文保留英文原文。
- 项目命名：Patrons and Painters；domain slug 为 patrons-and-painters。

### 关联规则变更：02-sources 顶层登记文件可更新（用户明确授权）

- 原规则：02-sources 只追加，不改写、不删除。
- 新规则：来源本体（子目录）只追加；顶层登记类文件可更新、不可删除。
- 权威落点同步：AGENTS.md 规则 3、.agents/pipeline.md、distillation-system-contract.md、encoding-check、system-review、README.md。

- 可执行门禁：scripts/agent_guard.py 新增登记文件判定（父目录为 02-sources 的文件；Update 放行、Delete 仍阻断）。
- 行为测试：tests/test_agent_guard.py 新增 3 项，全部通过。

### 修复项

- taxonomy.md Structure Nodes 段层级倒置修正为 domain→dimension→theme→topic。
- 悬空引用（current-health.json、候选账本）在运行状态重建中补齐。
- 02-sources/README.md 旧模板文案更新为实际目录结构。

### 验收证据

- 便携回归全部通过（含新增 guard 测试）。
- 版本一致性（AGENTS/README/pyproject 三处 v5.3.0）通过。
- 未解决项：试点摄入尚未执行；05-outputs 图谱数据待生成后刷新；完整 closure 门禁待首次摄入后运行。

## 本地与远程同步检查（2026-09-09）

- 用户授权同步本地与远程 main。同步范围包含既有领域迁移、第一章试点及其运行工件。
- 修复同步阻断：候选 envelope 的 origin_type 统一为 source、knowledge_unit 拼写改为 unit，保留原候选决定与 approved 状态，并更新工作包输出指纹；为 KU 中含冒号的 YAML 标量加引号，保留原文。
- 补齐知识类型导航、输出登记与二维遗留模板完整性清单，重建派生索引；README 按当前路由与已存在的 10 个 KU、5 个 claim 登记修正。
- 完整 sync closure 通过，254 项测试及 16 项子测试通过；pre-commit 规则漂移为 0，第一章 compact-v4 包校验通过。
- 上节“试点摄入尚未执行”为迁移时快照。当前仍有来源处理链缺口、外部验证、Theme/Topic 挂载及候选写回状态收口待办；本次未重新进行来源语义验收，机械通过不表示这些工作完成。
