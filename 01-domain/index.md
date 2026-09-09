# 领域配置总入口

本目录保存当前垂直领域的可替换配置。通用规则仍以 `AGENTS.md` 为权威；本目录只定义“《赞助人与画家》：巴洛克时期意大利艺术与社会”这一实例领域的类型、维度、验证和输出偏好。

## 一、当前领域

- **领域名称**：《赞助人与画家》——巴洛克时期意大利艺术与社会
- **英文名**：Patrons and Painters: Italian Art and Society in the Age of the Baroque
- **核心研究对象**：以 Francis Haskell《Patrons and Painters》（Yale University Press, 1980 修订版）为核心来源，研究 17 世纪意大利的赞助机制、艺术市场、艺术家职业网络、城市艺术中心与作品委托
- **源材料**：
  - `02-sources/01-book/`：23 个 PDF = 封面 1 + 正文 17 章 + 书后材料 5（结论/附录/第二版后记/参考书目/索引）
  - `02-sources/02-Markdown/`：79 个英文 OCR 文件（正文 17 章及各章分节拆分 + 书前/书后材料）
  - `02-sources/03-Index/`：人名/机构/地名索引三格式（MD/CSV/PDF）
- **全书结构**（正文 17 章，三部）：
  - Part I Rome：第 1–6 章（赞助机制 / 乌尔班八世及其随从 / 修会 / 私人赞助人 / 更广泛的公众 / 罗马赞助的衰落）
  - Part II Dispersal：第 7–8 章（欧洲的介入 / 外省景象）
  - Part III Venice：第 9–17 章（国家贵族与教会 / 外国影响 / 外国侨民 / 启蒙运动 / 出版商与鉴赏家 / 弗朗切斯科·阿尔加罗蒂 / 新方向 / 画商与小资产阶级 / 最后的赞助人）
- **当前知识规模**：以 `06-runtime/state/current-health.json` 的实时扫描为准
- **当前 hierarchy**：v1.0（2026-09-09 新建）
- **基础类型覆盖**：8/8
- **当前 Level 2 维度**：5 个 pilot 维度（A–E，见 `dimension-registry.md`）

## 二、配置文件

| 文件 | 职责 |
|---|---|
| `taxonomy-registry.md` | 知识元类型体系：基础类型、候选类型、晋升/合并/弃用规则 |
| `domain-registry.md` | Level 1 Domain：当前实例、候选 Domain 与演化边界 |
| `dimension-registry.md` | Level 2 维度体系：当前 pilot 维度、候选维度、拆分/合并/弃用规则 |
| `workflow-overrides.md` | 当前领域的对象、候选、层级演化、双语约定与状态诚实覆盖规则 |
| `naming-conventions.md` | 从 01 开始的目录职责、稳定命名与迁移边界 |

## 三、候选观察队列

| 文件 | 职责 |
|---|---|
| `04-knowledge/structure/taxonomy/type-candidates.md` | 类型候选观察队列 |
| `04-knowledge/structure/dimension-candidates.md` | 维度候选观察队列 |

## 四、当前执行约束

1. 不直接新增正式类型。新类型先进入候选观察队列。
2. 不直接新增正式 Level 2 维度。新维度先进入候选观察队列。
3. 能作为 `sub_type` 解决的问题，不晋升为新 `type`。
4. 能作为 Topic 或 Level 3 Theme 解决的问题，不晋升为新 Level 2 Dimension。
5. 类型或维度晋升必须通过 `synthesize`、`inspector` 和状态诚实门槛；无人工工作流下由 Agent 写明 evidence、boundary test、hierarchy impact 与 unresolved items。
6. 若通用 Skill 与本领域配置出现可复现冲突，按 `AGENTS.md` 优先级解释并触发 `system-upgrade`，不得长期保留两套活跃规则。
7. 若确认某条领域经验需要升级为系统规则，应移交 `system-upgrade`，而不是只停留在对话中。
8. 5 个 A–E 维度当前均为 `pilot`：新领域初始化设计的起始框架，第二部分启动后经 `synthesize` 重评方可晋升 `core`。

## 五、状态快照入口

本项目默认按 workflow-first 工作流执行。以下命令只用于生成辅助状态快照，不是领域配置、知识裁决或工作流完成标准：

```powershell
python scripts\audit_repo.py
```

该辅助工具会实时统计：

- 知识元数量和类型覆盖
- 必需字段与推荐字段缺失
- `MIGRATION_TODO` 来源队列
- `UNVERIFIED` 队列
- Markdown 链接和 `local_file` 可达性
- 类型候选信号与维度候选信号
- intake → processing 数据流完整性

语义阅读、类型判断、层级演化和关系裁决仍由 Agent / Skill Contract 处理。
