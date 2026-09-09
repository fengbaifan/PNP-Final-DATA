# Index 分层契约

> 本契约定义仓库中各类 index 的职责边界，避免把权威索引、派生输出、浏览导航和候选状态混写为同一层。
> 它服务于 workflow-first 与渐进式披露体系，不改变当前 `04-knowledge/quality/` 的根目录位置。

## 一、总原则

1. index 不是单一概念，必须按职责分层解释。
2. 会被 pipeline、verify、quality、growth 或受控脚本直接读取并作为写回依据的 index，属于权威索引层。
3. 面向浏览、查询、写作和导出的 index，只能作为输出层导航或派生产物，不承担事实裁决。
4. 当不同层的 index 内容不一致时，以 `04-knowledge/` 下的权威知识文件与权威索引为准；`05-outputs/` 视为待同步的派生层。
5. 当前不迁移 `04-knowledge/quality/`；如未来要迁移，必须连同 pipeline、scripts、governance 记录做正式系统升级。

## 二、四类 index

### 1. 权威索引

定义：
- 属于知识权威层的一部分。
- 服务于 assertion、relation、verification、authority、hierarchy 等正式状态。
- 可以被 workflow 读取，可参与受控写回、验证与治理。

当前仓库中的权威索引：
- `04-knowledge/quality/claim-registry.yml`
- `04-knowledge/quality/relation-index.yml`
- `04-knowledge/quality/translation-index.yml`
- `04-knowledge/structure/hierarchy/index.md`
- `04-knowledge/structure/domains/`
- `04-knowledge/structure/dimensions/`
- `04-knowledge/structure/topics/`
- `04-knowledge/structure/themes/`

边界：
- 权威索引可以被输出层读取，但输出层不得反向覆盖其事实口径。
- 权威索引不是面向消费的目录页，不以浏览友好性替代结构完整性。
- `translation-index.yml` 必须完整投影 eligible KU，不得用固定行数截断；KU 删除后必须重建以移除 stale slug。

### 2. 派生输出

定义：
- 从权威知识层导出的辅助索引或数据投影。
- 主要服务于快速检索、展示或跨工具消费。
- 不直接承担知识裁决，也不是 workflow 的唯一事实来源。

当前仓库中的派生输出：
- `05-outputs/knowledge-graph-data.json`

边界：
- 派生输出可以为 query / compose / display 提供便利，但不能替代 `04-knowledge/` 的权威文件。
- 若派生输出与权威索引不一致，应先修生成链或刷新派生产物，而不是改写权威层去迁就输出层。

### 3. 浏览导航

定义：
- 面向人类阅读、写作和查询入口的导航页。
- 允许对权威层做摘要、聚合和重新编排。
- 只承担“如何找到内容”的职责，不承担“什么是最终事实”的职责。

当前仓库中的浏览导航：
- `05-outputs/index/index.md`
- `05-outputs/index/persons.md`
- `05-outputs/index/places.md`
- `05-outputs/index/publications.md`
- `05-outputs/index/works.md`
- `05-outputs/index/README.md`

边界：
- 浏览导航可以引用快照统计，但必须声明其为导航层说明，不是权威状态本体。
- 浏览导航一旦展示数值快照，必须在 sync closure 时与 `current-health.json` 及权威索引对齐；无法稳定维护的数值应删除而不是保留过期口径。
- 浏览导航不得继续维持已废弃 taxonomy、旧目录别名或不存在的索引页链接。

### 4. 候选状态

定义：
- 用于记录尚未进入权威知识层的候选、冲突或待裁决对象。
- 可以被 review、quality、growth 或 system-upgrade 读取，但不能被当作已成立事实。

当前仓库中的候选状态：
- `04-knowledge/quality/relation-candidates.yml`
- `04-knowledge/structure/dimension-candidates.md`
- `04-knowledge/structure/taxonomy/`
- `04-knowledge/quality/conflicts/`（冲突复核与裁决记录，不是 KU 类型）
- `06-runtime/state/candidate-index.jsonl`（统一派生候选视图，不是知识事实）

边界：
- 候选状态不是输出导航，也不是权威索引。
- 候选状态若要升级为权威层，必须经过对应 skill 的门禁和正式写回路径。

## 三、输出层读取顺序

当 output / query 场景需要读取索引时，默认顺序为：

1. `04-knowledge/units/` 与 `04-knowledge/structure/`
2. `04-knowledge/quality/` 中的权威索引
3. `05-outputs/index/` 作为浏览导航层
4. `05-outputs/results/<id>/` 中按需生成的导出附件

禁止把上述顺序改写为“先读 output index，再把其统计或 taxonomy 当作事实源”。

## 四、当前仓库的直接结论

1. `04-knowledge/quality/` 目前位置合理，继续视为 Layer 2b 的权威层，不迁移。
2. 当前主要问题不是 quality 放错位置，而是 `05-outputs/index/` 的导航页曾长期滞后于权威口径。
3. output 技能文档不得再使用 `records/index/` 这类旧别名，而应显式区分权威索引与输出导航。
4. 若未来扩充 output 导航页，应先确认导航页只做浏览入口，不复制或发明新的知识类型体系。

## 五、验收关注点

- `05-outputs/index/index.md` 是否已清除旧 taxonomy 与旧统计口径
- output / query skill 是否已显式区分权威索引、浏览导航与派生输出
- README 与 system-upgrade 记录是否能定位本契约
- `04-knowledge/quality/` 是否继续保持 Layer 2b 权威层定位
- `translation-index.yml` 的 indexed、declared total 和 eligible KU 是否一致，且 missing、stale、duplicate 均为 `0`
