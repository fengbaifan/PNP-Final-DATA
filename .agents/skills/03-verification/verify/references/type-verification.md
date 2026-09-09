# 按类型验证流程 v4.0

> 本文件定义当前 8 类 Knowledge Unit 与 claim / structure node 的验证优先级。优先级不表示“命中即通过”，而表示应优先收集哪类 evidence。

所有验证必须遵守：

```text
collect → evidence JSONL → verify_apply_evidence.py
```

collect 阶段只收集 evidence，不直接写库。apply 阶段才允许更新验证字段。

## 一、通用限制

1. Wikipedia 页面存在不等于验证通过。
2. Wikidata QID 存在不等于 `externally_verified`。
3. API success 不等于知识成立。
4. Wikipedia 无页面不等于对象不存在。
5. Wikidata 无 QID 不等于对象不存在。
6. 外部数据库缺失不等于原始来源无效。
7. 单一 evidence 不能把 `confidence` 提升到 `high`。
8. 单一 limited-scope evidence 不能把 `consensus` 提升到 `confirmed`。

无数据处理见 `no-data-and-browser-research.md`。

## 二、Person

优先级：

1. Wikidata + Wikipedia 身份候选。
2. VIAF、ULAN、LCNAF、机构页面、档案记录。
3. 生卒年、职业、国籍、代表作品等字段比对。
4. 原始来源或学术来源确认其与十七世纪意大利艺术、赞助研究或本体系主题的关系。

写回规则：

- Wikipedia 可支持 `entity_identity_only`。
- Wikidata 字段匹配可支持 `basic_fact`。
- 人物在本知识体系中的贡献必须由原始来源、学术文献或权威档案支持。
- 单一 Wikipedia 页面不得把人物贡献写成已外部验证。

## 三、Institution

优先级：

1. 机构官网、馆藏页面、出版社页面、大学/博物馆/图书馆档案。
2. Wikidata / Wikipedia 基础身份辅助。
3. WorldCat、VIAF、archive、library record。
4. 原始来源确认机构与作品、出版物、事件、人物的关系。

写回规则：

- 机构存在不等于其在本体系中的角色成立。
- 历史机构与现代机构必须记录名称、时间范围和别名差异。

## 四、Place

优先级：

1. Wikidata / Wikipedia 基础地理身份。
2. 坐标、现代实体、历史名称、行政层级。
3. 档案、馆藏、机构官网或历史资料确认其与作品/人物/事件的关系。

写回规则：

- 现代地点不得自动等同于历史机构。
- 历史地点、图书馆、博物馆和馆藏地点必须记录别名、历史名称或现代实体关系。

## 五、Work

优先级：

1. 原始书目、馆藏、Open Library / archive.org 或档案记录。
2. 作者、年份、出版背景、收藏机构、图像出处。
3. 原始来源或学术来源确认作品与巴洛克艺术史、赞助史或社会史的关系。
4. Wikipedia / Wikidata 仅用于辅助身份确认。

写回规则：

- Wikipedia 页面存在只能证明作品候选存在。
- 作品与本体系的解释性关系必须由来源文献、档案或 claim evidence 支撑。

## 六、Publication

优先级：

1. CrossRef / DOI。
2. Google Books / WorldCat / Open Library / ISBN。
3. 出版社页面 / archive.org / 馆藏记录。
4. Wikipedia / Wikidata 仅作辅助身份确认。

写回规则：

- Publication 不应优先使用 Wikipedia。
- 只有书目字段匹配时，才可写为 `bibliographic_fact` 或 `bibliographic_hint`。
- 缺少 DOI/ISBN/馆藏/出版社证据时，不得升 `confidence: high`。

## 七、Term

优先级：

1. 原始来源与摄入文献中的定义。
2. 专业文献、学术论文、教材或权威网页。
3. Wikipedia / Wikidata 术语存在验证。
4. 浏览器与独立网页来源二次确认。
5. L7 模型内部知识兜底。

写回规则：

- Wikipedia / Wikidata 对 term 通常只能支持 `term_existence`。
- term 的领域定义、理论地位和中文译名必须由专业来源或来源内语境支撑。
- OpenAlex 摘要候选只在摘要确实定义或实质描述目标术语时支持 `scholarly_semantic_fact`；同词提及、跨领域同名或只有题名命中必须拒绝或延后。
- L7 只能写为 `model_supported` 或 `source_backed`，不得写成 `externally_verified`。

## 八、Procedure

优先级：

1. 原始来源与摄入文献中的操作语境。
2. 专业文献、技术史文献、教材或权威网页。
3. 作品实例、流程描述、方法步骤或操作条件。
4. Wikipedia / Wikidata 术语存在辅助。
5. 浏览器与独立网页来源二次确认。

写回规则：

- 方法名称存在不等于其技术史地位成立。
- OpenAlex 摘要候选必须明确描述方法、过程、步骤、操作条件或适用范围；仅出现 procedure 名称不能升级状态。
- procedure 与作品、人物、事件、term 的关系必须由 source claim 或 relation evidence 支撑。
- procedure 文件名应为动作或过程形式。

## 九、Event

优先级：

1. 原始事件来源、档案来源、报刊、图像出处。
2. 学术文献、历史数据库或权威二级来源。
3. Wikipedia / Wikidata 仅作为事件身份辅助。
4. 浏览器与独立网页来源二次确认。
5. L7 只能作为解释性兜底。

写回规则：

- 事件真实性、时间地点、参与者、相关图像和本体系相关性必须分开验证。
- 事件身份通过不等于相关 claim 通过。

## 十、Claim

claim 不属于 KU。claim 验证走 `quality/claim-registry.yml` 与 evidence 绑定。

优先级：

1. 原始来源中的明确论述。
2. 学术论文、专著、评论、教材中的二次论述。
3. 与 claim 绑定的 KU / relation evidence。
4. 浏览器与独立网页来源辅助发现证据候选。

写回规则：

- claim 必须区分事实、解释、归纳和评价。
- Wikipedia / Wikidata 命中通常不能验证解释性 claim。
- 只有来源支持的 claim 可标 `source_backed`；多源强证据后才可考虑 `partially_verified` 或更高状态。

## 十一、Structure Node

domain / dimension / theme / topic 不是 KU；cluster 是 discovery candidate，也不是 KU。

验证重点：

1. 是否组织多个 KU，而不是表达单一对象。
2. 是否有 supporting_units / supporting_claims / supporting_relations。
3. 是否与 A-E / 33 Themes 主骨架冲突。
4. 是否只是标签、临时聚类或输出视角。

写回规则：

- 新 Theme / Topic 必须通过 `.agents/skills/06-growth/synthesize/SKILL.md` 的候选与成熟边界；Cluster 只能通过边界审查成为发现信号，不能直接写入 structure。
- 新 dimension 必须进入 evolve-hierarchy 专项流程。

