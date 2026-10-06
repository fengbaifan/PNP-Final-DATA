当前项目阶段游标与统计以[全书 S2 当前结果](../04-knowledge/results/patrons-and-painters-full-book-s2.md)及[S2过程记录](../03-processing/patrons-and-painters-full-book-s2/process/stages.md)为准；本文件维护稳定阶段规则与交接条件。

## 第一阶段框架：S0–S7

各阶段产物统一存放在 `04-knowledge/tables/`，目标是让表成为结构化事实的唯一权威。当前登记和结构化字段仍处迁移状态：`ku-manifest.csv` 与 `accepted.yml`、卡片元数据并行；S2 全书段落覆盖已建账，语义阅读和表迁移仍在进行，阶段数字见上方当前快照及全书 S2 结果；普通字段表按卡片现有小节与表头从 `enrichment.jsonl` 重建，关系行从 `relations.csv` 读取。`build_cards.py --check` 对全库预检且不写文件，`--preview` 输出单卡差异，`--render` 在预检通过后批量写回全部卡片；2026-09-26 批量重建后，`--check` 验证 1,019 张卡均无剩余差异。旧总构建器 `build_tables.py` 已退役，禁止用其重建覆盖。`release/vX/` 为独立快照；预览与发布包都不是工作事实源。

每张表都按「自然键」保持唯一（定义见 `01-domain/stage-artifact-schema.md` 0.1 节）。写入前先按自然键查重，已存在的记录复用原 ID，不新发号。

写入规定：字段与关系行只从结构化表读取；`--render` 会在全库预检和逐卡结构检查通过后批量写回卡片，执行须有明确用户授权。旧 `verify_apply_evidence.py --apply/--resume`、`apply_relation_plan.py --apply`、`build_relation_views.py --apply` 均已停用，避免从旧卡片入口分叉写入。

| 阶段 | 唯一产物 | 工作 | 放行条件（摘要） |
|---|---|---|---|
| S0 来源规范化 | `sources.csv`、`segments.jsonl` | 定一套分节切分，段落有稳定 ID 与内容哈希 | 只读分节文件；同章段落不重叠、覆盖 100% |
| S1 全书实体候选 | `entity-candidates.csv` | 以原书索引（`03-Index`）为种子，全书候选一次收齐 | 索引每条 → 候选或标 `excluded` 附理由 |
| S2 书内语义处理 | `s2-coverage.csv`、`mentions.csv`、`book-statements.jsonl` | 逐章完整阅读，提及→候选、断言/关系候选→段落锚点，并为每个源段记录已审阅或排除 | 每章S0段均有覆盖状态，排除有理由；每条提及/断言有锚点 |
| S3 身份对齐 | `alignment.csv` | 全局按类型对齐；**只做身份**，不注入内容事实 | 每候选一个决定（same/new/conflict/excluded/undecided）带证据 |
| S4 KU 登记 | `ku-manifest.csv` | 登记/复用 KU；**所有计数只从此清单算** | S3每个`new`有对应`ku_id` |
| S5 补足 | `enrichment.jsonl` | 按类型补明确缺口，字段级事实逐条带来源与访问日期 | 每类预声明字段填完或标「缺口」 |
| S6 关系 | `relations.csv` | 逐候选裁决正式/待证/否决，绑定证据 | 主客体类型过域值域矩阵；每条`formal`至少1条证据 |
| S7 发布与验证 | `release/vX/`、`validation-report.md` | 从tables导出数据集、统计和验证报告；排除标记为不发布的表 | 全部由S0–S6产物生成；打tag冻结；派生索引只在此生成；不读写`05-outputs/`，页面仅在用户指令下另行生成 |

## 切断回环：候选待办清单

S5/S6发现的新端点**不立即回知识元**，写入`candidate-backlog.csv`，本轮不建KU。硬门槛：关系阶段收口前backlog必须清空（每个待办要么建成KU、要么显式标`undecided`保留待证）；软触发：同类型backlog≥20时提前批量drain（走S1→S3→S4）。这等价于原有「端点缺则关系完整性保持未完成」的语义，只是不再逐条回环重跑上游。

## 关系候选的共同记录

关系候选最小包含：稳定锚点、原文提及与指代、候选关系表述、来源版本及章页行号／原句、时间／版本／发言者／语气等必要限定、端点映射与后续裁决入口。候选属于S2的`book-statements.jsonl`，是候选不是正式边；正式关系只在S6的`relations.csv`维护，卡片关系表由其渲染。原书候选与外部发现的事实分别归源，外部补足不覆盖原书表达。

依REV-032，收口仍要求：保存唯一当前定稿，清理确已替代的重复过程叙述，再交接；必要分析、来源定位、未决项及裁决须保留。S0–S6结构化产物已建立；第一章S2迁移完成只证明该章账本完整，不能代表全书语义召回或准确率验收。

## 第二阶段：知识发现与知识呈现

用户明确启动后，synthesize根据`ku-manifest.csv`、`relations.csv`与断言证据分析；不要求全库全部处理或全部外部验证。四层（Topic→Theme→Dimension→Domain）自下而上涌现，具体名称、数量和归属事先不设定；候选、成立和暂缓分别记录。有证据形成多少层就保存多少层，不凑完整树。

## 过程、结果与成果位置

| 工作 | 过程（只记阅读、判断与裁决理由） | 产物与结果 |
|---|---|---|
| S0–S2（来源、候选、语义处理） | `03-processing/<task-id>/process/stages.md`；`results/stages.md`记录逐行阅读结果 | 产物在`04-knowledge/tables/`：`segments.jsonl`、`entity-candidates.csv`、`mentions.csv`、`book-statements.jsonl`；来源资产在02-sources |
| S3–S6（对齐、KU、补足、关系） | `03-processing/<task-id>/process/knowledge.md`，按阶段分节 | 产物在`04-knowledge/tables/`：`alignment.csv`、`ku-manifest.csv`、`enrichment.jsonl`、`relations.csv`、`candidate-backlog.csv`、`id-redirects.csv`。`04-knowledge/results/<task-id>.md`写范围、状态、产物链接和未决项，不复制事实 |
| S7（发布验证） | 写在`release/vX/validation-report.md`内 | `release/vX/`（冻结快照，打tag）；不读写`05-outputs/` |
| 系统调整 | `06-runtime/governance/CHANGELOG.md` | 同一CHANGELOG，不新增报告副本 |

`source_id`标识来源版本，`ku_id`标识知识对象，`task-id`标识本次工作范围。不要以单章编号限制跨来源发现，也不按阶段复制KU。读取与接续先看当前results的范围、状态和未决项，再定位相关process段落与证据；每阶段只写实际发生的过程，更新对应结果后交接。

## 交接、状态与回退

过程说明做了什么及判断理由；结果说明范围、输入版本、成果位置、当前状态、未解决项，以及哪些对象可交给下一环节。状态使用未开始、处理中、已完成、部分完成、受阻、暂不开展。完成审查但仍缺证时写明「审查已结束、问题未解决」。

- 来源、阅读或语境不足：回S0/S2；原声明范围不得为通过检查任意缩小。
- 身份/版本/冲突问题：回S3；具体内容缺口：回S5。
- 关系依据不足：回S6或其必要上游；不让弱关联混入正式图谱。
- 已采纳字段出现可独立识别对象而缺KU：写`candidate-backlog.csv`，本轮不建KU，只在该对象及直接关系上补齐；不递归扩张所有外链。
- 发现不能被下层支持：暂缓、修订或撤回对应结构，不倒推原文事实。
- 页面暴露错误：回责任阶段，页面只能呈现已知状态。
- 输入或结论变动：标记受影响下游待复核，只重做相关依赖；已接受且未受影响对象不重复处理。

正式事实至少可追溯；必要检查可融入工作；批量机器写回才启用独立计划、dry-run和恢复日志。inspector按问题检查，system-upgrade维护规则，不成为每阶段必走的新流程。
