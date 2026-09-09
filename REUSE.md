# 完整工作流复用说明

本包复刻 `Infographic Knowledge Distillation` 当前磁盘中的完整工作流系统。它是可移植的系统源文件包，不是已经为任意新领域完成配置的知识库。

原有 AGENTS、18 个 Skills、全部 direct references、路由、guards、执行器、测试和客户端配置均保留。知识发现、知识涌现、主题、层级、关系等现行功能也全部保留；本次对话中撤回的取舍不构成修改依据。

## 文件与边界

| 路径 | 内容及复用方式 |
|---|---|
| `AGENTS.md`、`CLAUDE.md`、`README.md` | 原项目权威入口和导航的原样副本；其中项目名、日期和历史数量仍指源项目 |
| `.agents/` | 唯一 Skill 权威根、完整规则和参考契约、事件路由、guards 与权限示例 |
| `.codex/`、`.claude/` | 原客户端适配配置；需按新机器修订 Hook 命令并恢复 Skill 链接 |
| `scripts/`、`tests/`、`pyproject.toml` | 全部当前受控执行器、共享模块、回归测试和依赖声明 |
| `.github/workflows/quality.yml` | 原单主线质量门禁示例；领域适配和 Git 初始化完成后再启用 |
| `01-domain/` | 原信息图表史领域配置，原样保留作为迁移起点；不是通用领域定义 |
| `02-sources/`、`03-processing/` | 空来源目录及处理层说明；不带书籍、全文或已处理证据 |
| `04-knowledge/` | 八类 KU 空目录、结构目录和空质量表；不带原知识、关系或研究层级节点 |
| `05-outputs/` | 输出说明、原图谱 HTML/CSS、静态资源与本地 D3（含其许可）；图谱数据为空 |
| `06-runtime/` | 运行层说明、新的空账本及重新派生的 Skill/工作包索引；不带原项目的健康分数或验收状态 |
| `workflow-copy-manifest.json` | 每个文件的来源分类、SHA-256、字节数和源 Git 提交；生成模板与原样复制明确区分 |
| `portable/verify_copy.py` | 只读检查原始副本的完整性；完成领域适配后哈希变化是预期现象 |
| `portable/run_tests.py` | 在临时目录中复制系统并生成 5 个最小合成测试样本，运行全部原测试；不向正式知识目录写入样本 |

未复制 `.git`、远端配置、个人设置、密钥、虚拟环境、缓存、书籍文本、知识实体、claim、实际关系、旧工作包和旧迁移映射。页面所需的原项目标识和封面缩略图作为静态展示依赖保留，迁移时应替换为新项目内容。

原项目中通过聊天或用户级配置注入的全局规则、已登录连接器、工具安装、模型权限及客户端信任状态不属于磁盘项目文件，不包含在副本中。

## 完整工作流

```text
新来源
  -> ingest: 登记 / 完整阅读 / source-map / semantic-units
  -> candidate-ledger: 检索现有知识 / 消歧 / 去重 / 冲突筛查 / 语义裁决
  -> 按目标类型写回 KU、claim、relation 或转交层级流程

已有知识
  -> enrich: 补充名称、属性、语境及来源
  -> verify: collect -> evidence JSONL -> 语义裁决 -> dry-run -> atomic apply
  -> reconcile: 仅在真实冲突出现时进行裁决

知识成长
  -> synthesize / build-hierarchy / evolve-hierarchy
  -> 候选、边界审查、主题与层级的受控变更

知识使用
  -> query / compose / knowledge-graph
  -> 输出与元数据；新发现经 retrospect 回到候选，输出不自动成为知识事实

横向治理
  -> lint / audit-confidence / encoding-check / read-full
  -> inspector / system-review / system-upgrade
  -> 定向门禁、状态诚实、必要收尾
```

这只是导航；执行规则以 `AGENTS.md -> .agents/pipeline.md / 对应 SKILL.md -> direct reference` 为准。流程由事件触发，不要求每项任务经过所有阶段。

## 迁入新项目

1. 将 ZIP 解压到仓库之外的新空目录，或目标项目的独立暂存目录。解压内容本身就是项目根，包含隐藏目录。不要直接覆盖已有项目的 AGENTS、Skills、数据或 Git 配置；先逐项比较后合并。
2. 先运行 `python portable/verify_copy.py .`，确认与导出包一致。
3. 阅读并适配 `01-domain/`、`AGENTS.md`、`README.md` 和 `pyproject.toml` 中的项目名称、领域、对象类型、层级定义及描述。规则中的 8 类 KU、A–E、33 个 Theme 等假设在部分脚本和测试中也有实现；若要变更，须同步规则、代码与测试，不能只换项目名称。
4. 原 `01-domain/index.md` 含本机 Python 绝对路径，必须替换。原 HTML/CSS 含三书、进度、历史归档和项目品牌文案，必须按新项目改写；空图数据不使这些文案变成新项目事实。不要把模板网页当成已完成的研究成果。
5. 按下面说明准备 Python、客户端和 Git 环境。确定新项目 Domain/Dimension 等语义配置后，再建立对应结构节点；本包不会自动创建学术分类。
6. 新来源按 `ingest` 使用 `compact-v4`。来源目录的首次登记由新项目完成；空目录和空账本不表示摄入、语义验收或发布完成。
7. 用新项目自己的数据重新生成索引、健康状态、评测集和必要展示清单，按其真实状态执行完整门禁。源项目的既有数量、健康分数、查询答案、旧例外基线不能移植为验收证据。

### Python

项目声明 Python >= 3.10，运行依赖 PyYAML；开发验证需要 pytest；PDF/网络研究可选 pdfplumber、requests。新项目中建议使用自己的虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install PyYAML pytest
.\.venv\Scripts\python.exe scripts/skill_registry.py
.\.venv\Scripts\python.exe portable/run_tests.py
```

也保留了原 `pyproject.toml` 和 CI 中的 `pip install -e ".[dev]"` 配置。本复刻不改变打包方案；安装方式是否适合目标环境仍应在目标项目验证。外部数据库与浏览器工具不是 pip 依赖，须由目标运行环境提供。

原测试中有 5 项直接依赖源项目的 B.2/C.6 Theme、两个 Topic 路径以及至少一个层级挂载对象。直接对空包执行 `pytest tests` 时，这些用例会因缺少业务数据失败。`portable/run_tests.py` 在临时副本中提供 4 个仅含类型/代码的结构文件和 1 个合成 KU，再运行全部原测试；不跳过用例、不修改断言、不 mock 执行器，也不复制源项目知识。适配新项目后，应将这类测试改为目标项目自己的独立 fixture。

### Claude Skill 入口

当前 Windows checkout 中 `.claude/skills/<name>` 是 Git 符号链接的文本占位文件，内容形如 `../../.agents/skills/01-intake/ingest`。这些占位文件按原样复制，检查通过只证明目标声明有效，不证明 Claude 已加载 Skill。

在支持符号链接的目标机器，应将各入口恢复为指向包内 `.agents/skills/` 的目录符号链接；保留相同相对目标。在 Windows 上也可使用指向目标项目内实际 Skill 目录的目录联接。处理前先确认占位文本与对应 Skill 一致，并备份占位文件；不得覆盖已有的真实 Skill 目录。不要把 Skills 复制为第二套可编辑正文。只使用 Codex 且其已从 `.agents/skills/` 发现 Skills 时，无需为其创建 Claude 入口。

### Hook

- `.codex/hooks.json` 原命令使用 `/usr/bin/python3` 和 `$(git rev-parse --show-toplevel)`，依赖 POSIX shell 与独立 Git 根。原样配置不适合直接在 Windows PowerShell 中执行。
- `.claude/settings.json` 使用 `python3` 和 `${CLAUDE_PROJECT_DIR}`，同样需要核对客户端实际启动命令的 shell。
- 迁移时只调整解释器、路径与 shell 适配，保持调用目标为 `scripts/agent_guard.py`，并保留标准输入中的事件 JSON。
- 在目标客户端核验 Hook 是否被识别、加载和信任，再用只读允许事件及模拟拒绝事件检查。规则测试通过不等于客户端硬门禁已启用。

### Git 与首次完整门禁

原系统采用 `main` 单主线，禁止额外分支和 worktree。本包不包含 `.git`，也不会创建 Git 仓库、修改远端或推送。新项目如果采用其他 Git 策略，需要明确改写对应契约和检查器，不能直接忽略失败。

`run_sync_closure.py --full` 是已初始化项目的整体验收，依赖 Git、领域结构、数据状态、评测和派生文件；空工作流包不应伪装成一个已验收知识库。`--check-generated` 会比较派生文件与 Git HEAD，首次生成且未纳入目标项目基线时出现差异是预期现象。完成目标项目准备后再依据原契约运行：

```text
python scripts/run_sync_closure.py --refresh-generated --full --check-generated
```

这一步不是包的解压命令，也不授权 commit/push。仍须遵守目标项目当次授权。

## 本次验证边界

交付目录的 `validation-report.json` / `validation-report.md` 记录实际完成的哈希核对、依赖检查、隔离目录测试及限制。所有源文件保持复制时字节；未修复源系统既有规则差异，不把复刻任务扩大为系统重构。

本包保留全部工作流，但不保证任意新领域无需配置即可通过全仓门禁，不声称外部联网 collector、目标客户端 Hook 或目标项目图谱交互已经验收。
