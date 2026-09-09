# Workflow Router — Skill 驱动的轻量编排契约 v2.5

> 本文件只定义跨 Skill 路由、正式状态边界和全局不变量。
> Skill 负责阶段内部流程，Agent 负责语义判断，脚本负责确定性重复工作。
> 本文件不是线性状态机，也不要求每个任务依次经过全部路由。

---

## 一、三条工作循环

```text
生产循环：source -> semantic processing -> candidate decision -> typed write-back -> knowledge
成长循环：knowledge/output/external signal -> discovery -> candidate -> typed write-back
治理循环：targeted check -> risk gate -> final closeout
```

治理循环是侧面控制，不是每个知识步骤都要进入的生产阶段。

---

## 二、五类事件路由

| 输入事件 | 主 Skill | 主要产物 | 下一路由 |
|---|---|---|---|
| 新来源或未处理来源包 | `ingest` | 覆盖证明、semantic units、candidate ledger | 验证、晋升或 defer |
| 已有 KU 需要补足、验证或冲突裁决 | `enrich` / `verify` / `reconcile` | evidence、decision、apply plan | 类型化写回 |
| 库内变化、外部研究或输出产生新信号 | `synthesize` / `retrospect` | discovery candidates | 证据绑定或 defer |
| 查询、写作和展示请求 | `query` / `compose` | output bundle + metadata | file-back 候选或结束 |
| 当前状态、规则、架构或发布收尾 | `inspector` / `system-review` / `system-upgrade` | 定向检查、审查结论、必要投影 | 完成或明确 blocked |

路由由当前对象状态触发，不以固定 P0-P13 顺序推进。

`candidate decision` 必须检索现有知识并识别重复/冲突信号。它是每个候选的轻量必检项；完整 `reconcile` 只在存在可复现冲突时触发，不是生产循环中的固定阶段。

---

## 三、统一候选边界

来源内发现、库内发现、关系图发现、外部研究和 output file-back 都先进入候选账本。
候选状态统一为：

```text
candidate
needs_evidence
ready_for_review
approved
applied
no_delta
deferred
rejected
blocked
```

候选不得直接等同于正式 KU、claim、relation、theme 或 hierarchy 变更。
统一投影把候选派生为 `active / terminal / historical_non_replay`；只有 active 进入 backlog 和下一动作路由，原始 R1 账本不因投影分类而被改写。
候选 envelope、发现边界与类型化写回规则见：

- `.agents/skills/06-growth/synthesize/SKILL.md`
- `.agents/skills/00-coordination/system-upgrade/references/work-package-contract.md`

---

## 四、类型化写回

| 目标状态 | 权威入口 |
|---|---|
| verification 字段与正文验证状态 | `verify -> verify_apply_evidence.py` |
| source 追加 | `ingest`，仅追加到 `02-sources/` |
| KU create / merge | `ingest` 或 `reconcile` 的已批准 exact change-set |
| claim | claim/evidence 治理规则下的已批准 exact change-set |
| relation | relation governance 下的受控 apply 入口 |
| theme / topic / hierarchy | `synthesize` boundary test 后交给 `evolve-hierarchy` |
| cluster | 只保留为发现信号；如需写回，另建 theme / topic / claim / relation / hierarchy_change 候选 |
| hierarchy | `evolve-hierarchy` 专项变更 |

不得建立自动决定语义的通用 writer。高频机械写回可以使用 map-driven 执行器，但决策必须先完成。
验证写回必须整批预检、原子提交知识与成功日志；恢复时先核对输入指纹。失败或阻断不产生 completed 状态。

---

## 五、自动化与风险

```text
L0 机械检查/索引：允许全量自动化
L1 已批准的低风险现有对象写回：dry-run 后允许受控批量 apply
L2 语义审查：自动收集和整理，Agent 决策
L3 冲突、建模和结构变化：专项审查，不自动 apply
```

允许并发：网络 collect、只读扫描、互不依赖的审计。
必须串行：同一文件写回、正式 relation/hierarchy 变更、生成投影发布。

---

## 六、工作包与收尾

一个用户目标原则上对应一个 work package；checkpoint 留在同一工作包内，不另建微批次。

最小工件按需使用：

```text
manifest.json
candidate-ledger.jsonl
evidence.jsonl
apply-plan.jsonl
summary.md
runner-state.json   # 仅长任务或可恢复写回
```

中间步骤运行最近邻定向检查；生成投影和完整 closure 每个工作包最多执行一次。

---

## 七、全局不变量

1. `02-sources/` 只追加，不改写、不删除。
2. collect 只产出 evidence，不直接写知识事实。
3. 证据不足必须保留不确定状态。
4. 脚本不得裁决 KU 类型、claim、relation、theme 成熟度或 hierarchy placement。
5. output 不是知识权威源；新发现必须先回到候选账本。
6. health、backlog、Hook 和脚本结果只是运行信号。
7. 历史 runtime 默认原地保留；新 R2 投影使用基线引用和增量，不重复复制全量状态。
8. Git 提交与推送不属于知识批次 runner 的职责，且必须有用户当次明确授权。
9. 用户级指令和自动记忆不属于项目权威状态；客户端硬门禁统一调用 `scripts/agent_guard.py`。

---

## 八、验收

- 路由目标 Skill 均存在且名称唯一。
- 注册表固定由磁盘契约派生；当前架构为 18 个 leaf，无聚合 router，分类 README 不参与执行。
- 活跃执行阅读深度最多为 `AGENTS -> SKILL -> direct reference`；reference 不得隐藏未由 Skill 直接登记的必读规则。
- 正式写回可反查 candidate、decision、evidence 和 apply 结果。
- `deferred` 候选仅在输入或证据变化后重新进入队列。
- 零候选输出使用 `reviewed_no_candidates`，不得标记为已写回。
- 完整发布验收不以 health 分数或 chain 文件存在性单独判定。

---

## 九、版本

当前版本：v2.5（2026-08-07）。历史修订只见 `06-runtime/governance/system-upgrade-log.md`。
