# 领域配置总入口

本目录保存当前垂直领域的可替换配置。通用规则仍以 `AGENTS.md` 为权威；本目录只定义“信息可视化史”这一实例领域的类型、维度、验证和输出偏好。

## 一、当前领域

- **领域名称**：信息可视化史与信息图表史
- **核心研究对象**：视觉传知工具、图形方法、信息可视化实践及其理论传统
- **当前知识规模**：以 `06-runtime/state/current-health.json` 的实时扫描为准
- **当前 hierarchy**：v7.1
- **基础类型覆盖**：8/8
- **当前 Level 2 维度**：5 个核心维度

## 二、配置文件

| 文件 | 职责 |
|---|---|
| `taxonomy-registry.md` | 知识元类型体系：基础类型、候选类型、晋升/合并/弃用规则 |
| `domain-registry.md` | Level 1 Domain：当前实例、候选 Domain 与演化边界 |
| `dimension-registry.md` | Level 2 维度体系：当前核心维度、候选维度、拆分/合并/弃用规则 |
| `workflow-overrides.md` | 当前领域的对象、候选、层级演化与状态诚实覆盖规则 |

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
5. 类型或维度晋升必须通过 `evolve-hierarchy`、`sys-audit` 和状态诚实门槛；无人工工作流下由 Agent 写明 evidence、boundary test、hierarchy impact 与 unresolved items。
6. 若通用 Skill 与本领域配置出现可复现冲突，按 `AGENTS.md` 优先级解释并触发 `system-upgrade`，不得长期保留两套活跃规则。
7. 若确认某条领域经验需要升级为系统规则，应移交 `system-upgrade`，而不是只停留在对话中。

## 五、状态快照入口

本项目默认按 workflow-first 工作流执行。以下命令只用于生成辅助状态快照，不是领域配置、知识裁决或工作流完成标准：

```powershell
C:\Users\001\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\audit_repo.py
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
