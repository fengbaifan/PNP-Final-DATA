# 规则变更日志

> 治理日志已冻结归档：`user-revisions.md` 与 `system-upgrade-log.md` 自 2026-09-25 起只读，不再追加。
> 此后的规则与系统变更只记在这里，按时间倒序；`current-requirements.md` 仍索引有效要求。

## 2026-09-26

### S2候选词覆盖扫描误报收敛
- 将已类型化候选表面扫描的单词长度门槛临时下调至3字符后，人工复核发现两处应记录的 Italy 提及及七处由匿名职衔候选 Pope 跨段产生的误报。两处提及已进入 S2 账本；扫描器现在将“仅由职衔识别”的未决人物候选限制在其来源段，并以回归测试覆盖。27个已迁移段的652个类型化标签低阈值复扫无未覆盖命中；严格表审计无结构错误。候选表面扫描仍不发现未列候选对象，也不提供全章召回率。全量闭包9/9、规则契约4/4、293项测试及2个子测试通过。

### 关系表来源 ID 唯一匹配补链（2026-09-26）
- `migrate_relation_context.py` dry-run 对关系记录 `source_file` 与 `sources.csv` URL 做精确且唯一匹配：740 条原先无 `source_id` 的记录中，622 条可唯一映射；105 条 URL 对应多个来源记录，13 条无精确登记，均保留空值。变更前快照与写后逐字段比较确认仅新增这 622 个 `source_id`，其余字段及1,227行顺序/ID不变，所有新增外键均存在。
- 已用现有授权的 `build_cards.py --render` 同步关系视图，537个文件写回、逐文件字节核对成功；随后 `--check` 为0个待写文件。草案包已刷新；严格表审计 errors=0，关系一致性审计断端点、非法类型、缺反向映射和弱证据均为0。来源URL唯一匹配仅解决登记链接，不等于独立事实核验。

### S0来源版本哈希闭环
- 复核S0验证实现后发现，生成器写入的`asset_sha256`曾仅检查非空，没有核验当前原始来源文件。`audit_tables.py`现逐段验证来源文件原始字节SHA-256；新增回归测试篡改该哈希后必须报错。当前62个来源分节、953段重新生成预览无问题，严格阶段审计 errors=0；完整同步闭环9/9、规则契约4/4、293项测试及2个子测试通过。仍有两条 enrichment 来源定位无法解析及S2语义质量警告，哈希闭环不代表实体/断言召回或事实准确。

### 数据集复用字段解释及来源引文交叉表
- 对照导出表实际数据发现，138条 enrichment 的显式来源ID数与引用字符串数不同；多个引文位置可对应同一来源记录，不能按数组顺序补配。字段字典明确 `source_id(s)` 是连接 `sources.csv` 的键，其余来源字段独立保留。新增 `enrichment-citation-links.csv`，对12,254条引文逐条建链接；9,328条与来源citation/label规范化精确匹配，另2,873条以唯一作者、书名、年份（Haskell《Patrons and Painters》1980版）匹配，53条仍未确定，0条歧义。验证器检查交叉表覆盖与确定性映射，明确书目匹配不证明事实支持。创建者字段按用户要求暂留空；未推断署名或许可。上述工作提升可追溯和字段可解释性，不解决未核验事实与发布权利问题。

### 全量审查、S2 迁移、预览核对与草案数据包更新
- 按用户授权执行 `build_cards.py --render`：全库预检通过后重建1,019张卡片中的2,608张结构化表、10,149行及CSV关系视图，保留现有小节、表头/分隔行和非表格说明；写后逐文件字节核对成功，临时恢复快照已清理。修复两张末尾新增关系小节的空行后再次写回，`--check` 得到0个待写文件。严格表审计无结构错误，系统闭包9项通过、规则契约4/4、287项测试及2个子测试通过；剩余1,501条enrichment未核验及2条来源定位未解析仍是已知待办，批量视图一致性不等于事实语义验收或数据集公开许可。
- 渲染后刷新 `release/v0.2-draft/` 并修正验证报告中的过时“待渲染”结论；查询示例默认输出精简摘要，`--full` 保留完整行，Windows UTF-8 输出正常。包内16个文件重新验证，Guercino样例返回35条字段、1条出向及4条入向关系。数据包仍缺作者、许可、持久标识和最终引用；未发布，也没有把机械检查时长冒充语义抽取吞吐。
- 独立核查发现 enrichment 的3,781处相对 Markdown 链接未被原验证器覆盖。新增 `portable-references.csv` 和逐链接覆盖、目标字段逐值一致及实体外键校验：3,751处解析到有效 KU ID，30处过程记录只保留稳定任务／文件／锚点指向并明确标为内容未打包；更新说明、字典和查询示例，不再误称完全没有项目内链。另在18文件草案中新增逐组件版权／引用清理清单，明确不得猜填许可或持久标识。导出测试覆盖引用缺失和目标篡改时失败；本次全量闭包9项通过、规则契约4/4、289项测试及2个子测试通过。
- 对 S0、S1、S5、严格表审计、全库 render 预检和数据包导出预览各进行5次只读热缓存计时，更新验证报告中的中位数和范围；明确这些数字仅代表本机机械步骤，不估算语义抽取吞吐，也不声称相对旧版提速。
- 将 README、字段契约和脚本指南中的重复章节计数收敛为权威链接；阶段统计留在 pipeline，业务进度留在结果文件，数据包检查留在 validation-report，减少更新时漂移。
- 新增只读 `audit_s2_candidate_surfaces.py`，对有类型候选的规范名／子项做 Unicode 偏移保真的未覆盖跨度提示；27个完成段、579个候选名称模式首次报出13处，逐项语义核对后均以复用候选写入提及账本；再次运行提示数为0。该工具不生成实体、不找候选表之外对象、不验证候选映射或全章召回率。第一章 S2 更新为663条提及、172条断言；导出草案、README、结果摘要与导出测试同步。新增测试覆盖跨行跨度定位和已有提及重叠过滤。

- 独立隔离上下文的9段盲审交叉核对363条提及和69条断言后，核实并修正4处高置信问题：Iris跨度错位、Pieter Van Laer姓名跨行截断、Rosa段断言增添原文未支持的“按成品质量定价”、无出处喜剧年份1635。按候选数据字典复核后撤回对4组索引子项的误报；Mr Coke 归属证据位于样本外脚注并有项目内核查记录，保留范围限定。更新S2过程与当前结果及草案验证报告；本次独立抽样不是正式人工验收，也不产生全章precision/recall估计。
- 关系来源预览复核后，对 `rel-0363`、`rel-0694`、`rel-0974` 按关系现存证据 URL 与 `sources.csv` 的唯一完全匹配补入三个 `source_id`。`migrate_relation_context.py` dry-run 只报告这三处单元格变化；五条多重 URL 匹配继续留空，未自动择源。

- 后续定向复核修正 `sec_ii:l118-127` 覆盖范围至 OCR L717–752，补录 L717–722 两条原书断言及相关提及；再复核 `l148-153`、`l155-159`、`l161-166`，新增16条提及和10个开放候选。复核 `l28-38` 又把 St John the Baptist 提及范围扩展为含原换行的全名，并用 PDF 核对 `Iris` / `his` 转录差异，未增候选或断言。当前表为3,592个候选（含195个正文提及候选）、649条提及和172条断言；严格阶段审计无错误。另盘点1,499条空 source_ref 的未核验字段：83条另有 source IDs/citations/URLs，464条 evidence 标记为项目命名，106条的证据栏与结构化来源字段均为空；这些是字段存在性分组，不判定事实支持。导出器新增 provenance diagnostics，避免将空 locator 自动解释为无来源；严格阶段审计无错误，全量闭环通过（9项检查、规则契约4/4、277项测试及2个子测试）。上述定向复核不提供全章准确率或召回率估计。
- 扩展草案导出器的 Wikidata 来源诊断：469条带 Wikidata 标记的未核验行中，465条为属性式字段；403条可映射到52个已 `same` 对齐 QID，但每个 QID 在来源登记中有两个记录，其中44组版本号相同、8组不同。其余62条无唯一 `same` 对齐，4条不是属性式字段。仅作为来源指针歧义诊断，不自动选源或视为属性核验；草案验证报告及导出测试已更新。
- 草案数据包新增 `wikidata-source-candidates.csv`，逐条列出465条属性式未核验记录及基于身份对齐的候选来源ID、修订号和访问日期；403条因每个QID有两个来源记录而标为候选歧义，62条标为缺少唯一身份对齐。包校验其记录唯一性与来源ID外键；该文件是人工复核清单，不写回 enrichment 来源字段。
- 对十二个正文段进行语义抽查，较原账本补33条提及和19个开放候选：`sec_ii:l3-8` 补 middlemen、foreign travellers 与其 agents 三个 term 候选；`sec_ii:l106-116` 将 picture dealers 映射到既有 art-dealer 候选，并为 feast of St Luke 登记 open person 候选；`sec_ii:l129-135` 将 gentiluomo d’onore 连到既有荣衔术语候选；`sec_ii:l137-146` 将 dealers 和 devotional pictures 连到既有术语候选；`sec_ii:l19-26` 新增补助换赞助人优先权的 open term 候选，由 subsidy 与 priority 两处精确跨度支撑；`sec_ii:l40-46` 扩展 San Sebastiano 教堂名跨度并登记 movable gallery picture、connoisseurship 两个 open term 候选；`sec_ii:l48-60` 登记 Caravaggesque genre scenes open term 候选；`sec_ii:l62-71` 补记 Holy Years 并登记 Baroque period、amateur 两个 open term 候选；`sec_ii:l73-77` 登记 canvas open term 候选；`sec_ii:l79-84` 将第二处 deposit 映射到既有 caparra 候选，并把身份未定的 Duke of Mantua 拆为独立候选 `cand-3572`；`sec_ii:l86-94` 补录 dilettantes 与 Venetian/Bolognese/Neapolitan 地理提及，新增 art dealing、art exhibitions、landscape painting、large historical scenes 四个 open term 候选；`sec_ii:l96-104` 补录 artist’s social status、Renaissance、Baroque、Bolognese、status of the artist、High Renaissance 六条提及，另增三个开放术语候选。未具名角色不转写成具体人物 KU。全章 S2 更新为623条提及、170条断言，覆盖状态不变；候选表为3,578行，其中正文提及候选181个。严格表审计通过；全量同步闭环需在本次更新后重跑。抽查不提供全章语义召回率估计。
- 后续逐行复核已闭合此前标为 partial 的 `sec_ii:l168-239`：将 OCR L321–322 的 Savini、Minnitti 记录拆出并归入实际承载段 `l28-38`，L323–330 归 `l168-239`；补齐该段提及与 archive 候选。当前 S2 为 27 个 reviewed 段完成、0 个 partial、3 个格式排除，590 条提及、170 条断言；严格阶段审计无结构或迁移错误。此更新替代本节后续所记的旧 partial 状态和375/169计数，不构成全章独立召回率或准确率验收。
- 第一章 30 条 S0 覆盖记录现为 27 个 reviewed 段中 26 个迁移完成、1 个部分迁移、3 个格式标题排除；账本现有 375 条实体提及和 169 条原书断言。补齐 Rosa、Baldinucci、De Rosis、Ferri、Luti 等段落与脚注记录，保留传说、转引、匿名代理人及局部相似案例的证据限定。
- 修正 `cand-3473` 的来源锚点至实际出现的 l155-159 / L909；为唯一无语义记录的 reviewed 段增加 `no_semantic_content:` 明示原因，为 `rel-1226` 记录待决理由。严格表审计现检查必填列、各表 ID、自然键、FK、状态前置条件、S0 来源锚点、S2 offsets/quotes 与空段理由；严格运行无结构错误，保留来源定位及语义质量警示。该结果不测召回率或独立语义准确率。
- 修复 `build_field_facts.py` 对带 UTF-8 BOM 的 enrichment JSONL 读取失败，并使预览显示逐记录差异。按现有卡片只为 `enr-06678`、`enr-06937` 补回 `S3–S4` 的规范化 `source_ref`；10,149 条记录 ID 集合不变，仅这两条记录发生变化，source registry 无改动。再次预览为零记录差异、零新旧 ID、零来源表变化；S3/S4 在卡片来源清单中仍无对应项，因此审计保留两条未解析警示，不猜补来源。相关修复与 BOM 回归测试已加入。
- `build_cards.py --preview` 现在从 enrichment 逐表重建行，保留现有小节、表头和证据单元格；未知/缺失结构记录阻断，渲染幂等，Windows 终端输出 UTF-8。测试覆盖九种 KU 类型，并核对多来源 archive、履历 person、Bologna place、争议 bozzetto 与原有散文。`--check` 核对当前字段表与结构化表一致；关系视图在 1,019 张卡均有 CSV 重建差异，已计入预览摘要且不写卡。当前无 `enrichment.jsonl.dispute` 已标记行，争议边界需由卡片散文保留。
- 更新可移植草案的数据字典、覆盖统计和验证报告，并记录本机 S0/S1/S5 机械预览、严格审计、全库 render check、单卡预览和导出预览的耗时观察；这不是模型推理或语义抽取吞吐基准。公开复用仍受第三方权利、许可、作者与稳定引用信息限制；未声称实体召回、字段准确率、关系精确率或独立语义验收已经达标。
- 根据逐段语义抽查澄清候选数据字典：`candidate_id` 是候选溯源标识，不是已接收实体 ID；索引行的 `canonical_name` 保留索引主标题，具体作品／地点可能在 `sub_entry`。例如 `Four Elements` 位于 Mola 主标题下，不能只读主标题判断提及目标。该说明已进入导出器并更新内部草案；抽查不构成全量准确率或独立验收。
- 修正脚注提及 `V. Ruffo` 曾误连到 De Rosis 书信 KU 的候选 FK；新增独立且身份未定的编辑者候选，并将 `V. Rufifo` OCR 变体和两处仅存 `V.` 的署名接到该候选。此处候选不与收信人 Antonio Ruffo 合并；账本增至 375 条提及。相应更新内部数据包、S2 统计和导出测试。严格表审计及草案导出测试通过。
- 延续脚注提及核对，补入 Jacopo Salviati、Cardinal Leopoldo de’ Medici、Fabrizio Arragona、Guercino 与 Antonio Ruffo 的书信端点提及；新增两名待处理候选，不自动成稿或建立正式关系。该核对发现 CSV 行宽异常会被 `DictReader` 静默接受；`audit_tables.py` 现对表行的额外字段和缺失字段报错，并加入损坏行回归测试。
- 后续语义复核发现 `sec_ii:l168-239` 仍有若干脚注具名参与者未进入提及账本，故将其迁移状态从 complete 更正为 partial。当前非严格审计无结构错误，严格阶段审计按设计报出这一未完成段；不能以先前严格审计结果宣称当前 S2 阶段闭合。该段需继续按 OCR 行范围补齐和核对提及后再恢复 complete。
- 更新活动入口、pipeline、字段契约和脚本说明中的过期 S2 统计与旧字段定义；数据包草案仅用于内部复核，未执行批量卡片写回、提交或推送。


### S2 候选外键前置补齐

- 第一章 `ku-manifest.csv` 中 325 个已接收 KU 原有候选身份映射只有 167 个可由候选对齐关系或 accepted-ku 候选记录取得，无法满足 S2 的 `candidate_id` 外键契约。
- 为缺少候选入口的 158 个第一章 KU 新增 `candidate_origin=accepted-ku` 记录，`candidate_source_ref` 指向已登记 KU 卡片；不创建新的实体判断，不补造外部对齐。现有索引记录、旧候选 ID 和 465 条 accepted-ku 记录均保留。
- `build_entity_candidates.py` 现在能够重建索引候选并稳定保留/补齐已接收 KU 候选；连续预览增量为 0。第一章 325 个 KU 到候选的映射检查为 325/325。S2 的 mentions 与 book-statements 仍未迁移，候选映射完整不代表语义账本完成。
- S1 结构复核发现 2,930 条索引行含 1,432 个不同主条目名；350 个同名组覆盖 1,848 行。第一章精确字符串预检得到 238 个段落-表面词组，其中 49 组对应多个候选。按契约保留逐条索引出处，不能将字符串匹配计作语义召回或自动合并；S2 仍需依逐段处理记录核对对象与指代。
- 将 `results/stages.md` 的原 OCR 行范围交接到当前 S0 段：91 个可映射行段通过规范化原文窗口覆盖（≥0.60 且高于次优段≥0.10），80 段处理表中 25 个正文段与 3 个 intro 元数据段均有有效 S0 外键；两个分节文件标题及 20 个页眉／页界／空白范围按非语义材料保留。该锚点映射降低了 S2 迁移的定位缺口，但不生成或验收 `mentions.csv`、`book-statements.jsonl`。
- 扩展 `audit_tables.py`：S2 表存在后检查必需列、唯一 ID、segment/candidate 外键、非空引文、qualifiers 对象及 `origin=book`。审计同时明确指出，两张稀疏事实表不能区分已阅读但无断言的段落与遗漏段落；100% 段落覆盖仍需对照语义处理记录核验。
- 新增 S2 `s2-coverage.csv`，以每章 S0 段为键记录 `reviewed` / `excluded` 与原 OCR 行范围；第一章 30 段均有状态，28 段指向既有语义阅读记录，2 段为分节文件标题并标注排除理由。它提供可机械复核的覆盖范围，不代替语义审查；`mentions.csv` 与 `book-statements.jsonl` 仍待迁移。
- 对 176 条第一章 `origin=book` 关系回查 S2 交接：352 个端点均唯一映射至候选 ID；176/176 条书内行范围可由覆盖台账定位，但 59 条涉及多个 S0 段，应拆分为逐段引文再迁移。仅以 KU 英文规范名精确匹配时，352 个端点中 107 个在引文中命中；其余涉及简称、异名或题名范围，需依语境记录确定原文表面形式，不能自动填 `mentions.csv`。本次只完成诊断，未将关系终表倒灌成 S2 完整账本。
- S2 覆盖台账新增 `migration_status`，避免段落覆盖完整被误读为提及/断言迁移完成；审计校验每条提及的 S0 段内 Unicode 字符偏移、同段原形准确，并校验每条书内断言的引文可在原始 OCR 指定行内复现、行范围属于该段覆盖记录。不同对象的严格嵌套提及允许共存；完全重复或交叉重叠的区间拒绝。现有 114 条提及和 46 条原子断言均通过锚点检查；7 段完整、1 段部分、19 段待迁移，3 个生成的分节标题按格式元数据排除。`l26-33` 有 24 条提及和 8 条断言，仍部分迁移。`build_entity_candidates.py` 现允许同一原书行有多个 source-derived 候选并按来源与名称稳定保留。数据包元数据分别报告 complete、partial、pending 数量；正文提及不自动转为已接收 KU。

## 2026-09-25

### 全量审查后执行 1–4 项修复

- S0 改为依据真实物理行区间切段，953 段均通过 SHA-256、无重叠与非空行覆盖检查；S1 将原索引 2,930 行全部登记，其中 42 条 see-under 明确排除并记录理由，另补 278 个已接收 KU 候选。索引覆盖不等于全书实体召回率。
- S5 改为预览优先的逐表抽取，保留 10,149 行原始单元格、证据文字、表头/小节与多来源标记；1,501 行保持 `unverified`。sources.csv 登记 1,684 项；2 个旧来源引用无法映射，保留警告，不补造来源。
- 关系迁移逐一匹配 1,226 条卡内边，补回 432 条原注、5 个时间/角色/范围限定与 2 个定位；从一条带有证据状态的现存边恢复缺失行 `rel-1227`。关系表现为 1,225 formal、2 pending；3 条共享网址对应多个 source_id，未猜选 ID。卡片原 frontmatter 未批量改动。
- 新增独立原始 Markdown 重扫和 render preview。1,019 张卡的 2,608 张字段表、10,149 行、元数据及 2,436 条正向/反向关系投影通过预览核验；单卡示例 `arragona-mantua-letter-1621` 与 `musee-fesch` 均只输出差异，未写卡。全库 render 等待用户审阅单卡预览。
- 退役可能覆盖 enrichment、重写 `release/v0.1` 的 `build_tables.py`；停用仍写卡片 frontmatter 的关系和核验 apply 路径。表/发布目录变化现在路由到 `audit_tables.py`，关系表同时路由到关系检查。修订 pipeline、字段契约、Skills、脚本说明和论文差距表，删除失效脚本入口引用。
- 创建 `release/v0.2-draft/`，含独立 CSV/JSONL、字段字典、元数据、加载示例、机械验证报告；包内 foreign key 通过且无本机路径。许可、作者、DOI/正式引用和第三方权利仍未确定，明确禁止将草案当作公开发布物。

**截至该审查快照仍未完成项（后续状态见本日志顶部更新）**：S2 的 `mentions.csv` 与 `book-statements.jsonl` 尚未生成；37 条 legacy alignment 缺候选身份；1,501 条字段未核验。没有独立准确率/召回率、成本/速度对照或语义验收。上述工作改善了可追溯性与机械完整性，不证明高质量抽取已达到论文发表标准。批量卡片写回、提交与推送均未执行。

### S3 对齐记录恢复更正

- 复核发现此前报告的 37 条候选身份并非不可恢复：`alignment-evidence.jsonl` 使用 `unit` 字段而不是旧脚本预期的 `key`；335 条 JSONL 与 CSV 按序对应，且每条 `process_ref` 均与 JSONL 的 `review` 一致。
- 从原记录恢复 37 条 KU/候选映射及其中 25 条明确的 same/QID 决定；其余 12 条原记录为 unpaired，决定保持 undecided。为 29 个新增 KU 建立 accepted-ku 候选，另外 8 条复用已有候选。
- 当前对齐候选缺失数为 0，候选总数为 3,237。旧审计所记“37 条不可恢复”是当时的错误判断；本节记录修正依据，数据包与阶段状态同步更新。

### 系统全量审查（基于 main / 8339218）

本轮是系统审查，未执行事实修订、批量 render、删除、提交或推送。检查覆盖入口与阶段契约、8 个 Skill 的交接、46 个 Python 脚本的职责清单及主链实现、全量结构化表和有效卡片的机械检查、发布目录与 CI；对信息损失作了具名卡片回查。不等于对 1019 个实体逐条独立事实验收。以下是本轮快照，后续修复以实际差异和验证为准。

结论：现有语义规则与卡片成果可继续利用，但 S0–S7 尚未贯通；tables 迁移存在来源定位错误、证据丢失、状态提升和旧脚本覆盖风险。当前不具备安全批量重建卡片的条件，也不能宣称已经形成经验证的高效、高质量、可独立复用的数据集。

**已成立的基础**

- 1019 个有效 KU，覆盖 9 类；关系表 1226 行，其中 formal 1224、pending 2，主客体均能在 KU 清单中找到。
- 原书与外部来源、身份对齐与事实验证、待证与正式关系的语义边界已有明确规则；已有逐段阅读、来源摘录和裁决记录可供迁移，S2 新表缺失不等于历史语义工作未做。
- 公共采集模块、按变化选择检查、普通 CI 仅测试和规则检查、页面独立触发等精简已实施。pytest 为 254 passed（本机 33.84 秒）；规则漂移和 Skill 注册检查通过。该耗时仅为测试耗时，不是实体生产性能。

**阻断项与证据**

| 优先级 | 已确认问题 | 影响及修复去向 |
|---|---|---|
| P1 | [build_tables.py](../../scripts/build_tables.py) 用段落序号 pi 填 line_start，再加段落长度生成 line_end。953 段中，891 段的声明物理行切片与存储哈希不符；同文件存在大量跨度重叠 | S0 证据锚点不能可靠复现。按原文件实际行偏移重建并验证覆盖、哈希、版本；迁移已有整章定位时保留对应映射 |
| P1 | [build_field_facts.py](../../scripts/build_field_facts.py) 仅识别指定三列表和四列以上表；遗漏「项目/内容/依据」、多种三列履历表等。8536 行仅覆盖 980 个 KU，39 个 KU 无字段记录 | 信息导出并不完整。例如 [1621 年 Arragona 书信](../../04-knowledge/units/archives/arragona-mantua-letter-1621.md) 有结构化信息但未进入字段表。建立逐表布局与字段映射，未知布局阻断迁移，不能静默跳过 |
| P1 | 字段解析丢弃完整证据单元格，仅取 S 编号和第一条 citation；S2–S4 被读成 S2、S4。四列以上的末列限定被丢弃 | [Guercino](../../04-knowledge/units/persons/guercino.md) 的「仅核出版记录，论文未通读」没有进入表；「国籍／政治归属：待证」被写为 source_backed。需保留多来源、原始限定和阅读范围 |
| P1 | enrichment 的 8536 行全部 source_backed、dispute=false、访问日期为空；1358 行无 source_ref，6225 行无 source_id；sources.csv 仅登记原书 1 条 | 不能从抽取成功自动提升证据状态，也不能把无 S 编号一律视为推断。恢复逐事实状态、来源与未决原因；实际来源未知时保留缺失，不补造 |
| P1 | [_relation_tables.py](../../scripts/_relation_tables.py) 读取 evidence_doc_id/evidence_source_file/evidence_span，而 CSV 实际为 source_id/source_file/source_span | 1226 条关系经适配后全部失去文件/网址及跨度；原 CSV 有 1226 个 source_file、1224 个 source_span。[关系审计](../../scripts/audit_relation_consistency.py) 将含空值的 evidence_ref 字典视为有证据，故错误放行。修复列映射、必填校验与失败条件；域值域矩阵也尚无脚本/测试引用 |
| P1 | build_tables.py 仍可覆盖 enrichment 为旧的 1370 条 field/value 为空的记录，并清空 id-redirects、重写 release/v0.1；ID 计数器每次从零开始 | 当前不是安全增量构建器。一次性迁移与正式导出必须分开，复用自然键和既有 ID，禁止静默覆盖事实源及冻结版本 |
| P1 | [build_relation_views.py](../../scripts/build_relation_views.py) 仍从卡片 frontmatter.relations 生成关系视图；两个 apply 工具仍写卡片；有效对象选择仍读 accepted.yml | tables 与卡片存在并行写入口，尚未完成事实源反转。先统一表读写，再将 accepted、卡片结构化部分和关系导航改为派生视图 |
| P1 | [build_cards.py](../../scripts/build_cards.py) 的 check 与抽取器使用相同遗漏逻辑，只比 ku_id/field/value 集合；不比证据、限定、布局、重复或反向多余记录，有缺失仍 return 0 | 8534 个唯一三元组的「100%」不是无损往返证明；另有 2 条自然键重复。render 未实现，preview 未实现。现阶段不能批量改写 1019 卡 |

**各阶段剩余交接**

- S1：2888 条候选全部未分类；原索引 2930 行中的 42 条 see under 被直接跳过，没有保留映射或 excluded 理由。索引、图版目录、书目与正文补召回需要可追踪的对应关系；索引行数不是实体召回率分母。
- S2：mentions.csv、book-statements.jsonl 尚不存在，应从已有语义成果迁移并保留原句、否定、推测、转述和指代；确有缺口才回读相关上下文。
- S3：335 条对齐记录中 315 条没有 candidate_id，无法完整追踪候选到 KU；不能据此推断历史对齐未做，但新接口未接通。
- S4：KU 清单已有 1019 行，但仍依赖旧登记；YAML 正则读取还导致 1 条多行标题在 manifest 中截断。
- S5/S6：先修上述无损、证据和唯一写入口问题；candidate-backlog.csv 尚未落地。
- S7：release/v0.1/enrichment.jsonl 仍是 1370 条空 field/value 记录，报告把含 2 条 pending 的 1226 行统称正式关系；未形成当前有效数据的发布验收。未查到本地 Git tag。

**检查工具的实际边界**

- audit_repo 输出结构 130/130，但不能检测上述新表缺陷；candidate_inventory=0 不包含新表的 2888 条实体候选，需明确统计对象或补路由。
- run_sync_closure 对 tables 下的 relations.csv/enrichment.jsonl 修改不选择任何数据审计；普通 CI 缺少新表的 schema、自然键、外键、证据和导出一致性检查。
- --check-generated 用 git diff 比较已被忽略且未跟踪的派生文件，不能验证这些文件的内容一致性。应比较实际产物哈希/内容，或删去无效承诺。
- audit_content_quality 报 1 个标题格式问题；回查是合法 YAML 多行标量被正则截断，属于解析器误报，应修工具，不改正确卡片迎合检查。

**简化、合并与退役建议（本轮未执行）**

1. 保留 S0–S7 的证据责任，可合并执行操作：S3 判定与 S4 登记共用一个受控事务；同一次外部阅读产出身份依据和字段依据，分别保存其支持范围；S2 的提及与断言在一次语义阅读中形成。无需每个阶段再加审批或完整健康报告。
2. 先统一 AGENTS → pipeline → stage-artifact-schema → Skill。ingest 正文仍要求成稿后交 verify、登记 accepted；relate 正文仍规定 frontmatter 为权威；enrich/relate 仍含立即回 ingest 的旧循环。schema 内还并存 enrich/infer 与 external/inferred、S7 包含页面与页面暂停等不同约定。删除已被替代的现行指令，保留必要历史理由。
3. 合并公共 Markdown/YAML/表格读取和来源引用解析。build_cards 与 build_field_facts 不应复制同一解析器再相互证明正确；迁移覆盖检查须独立于渲染解析路径，未知表型或缺证应显式失败。
4. 将 build_tables.py 从日常构建入口退役为受控迁移用途，正式发布单独从当前 tables 导出。两种 apply 工具共享事务、预检和恢复实现，保留事实与关系各自语义校验，不再直接写卡片结构化事实。
5. 清理 scripts/README.md、run_sync_closure.py 和 naming-conventions.md 对已删除 build_relation_index.py 的引用；current-requirements.md 中六阶段与继续追加冻结日志的要求应更正。CHANGELOG 的历史发生记录不按现状倒改。
6. portable/verify_copy.py 与 workflow-copy-manifest.json 仅用于初始导入校验，可从日常导航移出，按历史证据保留。compact-v4 校验器和 _runtime_state.py 仍有调用与测试，不能直接删除；待替代协议与历史复验方式明确后再退役。
7. 关系候选、证据候选、孤立实体和补足待办工具可统一读取与队列汇总，避免相同实体被反复扫描；不同语义裁决不能仅因文件名相近合并。8 个 Skill 已较精简，数量本身不是问题。
8. discovery、hierarchy、gallery、页面脚本继续按需休眠，从日常关闭流程中排除；未启动第二部分不构成缺陷。02 来源、03 裁决证据、冻结治理历史、未登记旧卡不列为直接删除对象。
9. 外部采集的下一步效率改进宜为复用已核对来源、按请求/版本缓存、只重试失败项、只复核受影响对象；先记录实体/断言产出、调用量、耗时、返工量，再判断收益，不增加固定搜索轮数或新框架。

**数据集论文复用性**

按 [FAIR 原则](https://www.go-fair.org/fair-principles/)与 [Scientific Data 投稿指南](https://www.nature.com/sdata/submission-guidelines)、[数据仓储政策](https://www.nature.com/sdata/policies/repositories)评估：现有 CSV/JSONL 和来源意识是基础，当前尚欠缺可独立使用的发布物、稳定引用、清楚的许可及完整溯源，不能称已满足投稿发布要求。此判断不是期刊接收预测。

- 可发现：冻结数据版本、持久标识、可引用元数据与引用说明尚未在仓库落地；正式投稿时按所投期刊落实数据仓储。
- 可获取：提供无需本机路径、卡片目录或 Agent 上下文即可读取的完整数据包与加载示例；segments 不公开时也需可复核的来源版本、定位和处理说明。
- 可互操作：统一实际列名、类型、枚举、空值、限定、稳定 ID、多证据及重定向；附准确字段字典。CSV/JSONL 足以承载当前目标，无须为达标强加图数据库。
- 可复用：未见项目数据/代码 LICENSE 或 CITATION.cff（D3 的第三方许可不覆盖本数据）；需要分别说明自有数据/代码许可和第三方材料范围。来源表目前只有原书，外部引用仍依赖卡内 S 编号；更换卡片结构后无法独立解释。
- 技术验证：query-eval-set.jsonl 为空，07-paper 的对照、稳定性、查询和成本实验仍是建议，未见本轮可报告的结果。需报告实体边界、字段、关系和证据定位质量，区分原书提取与外部扩展；机械通过不等于语义准确率。未获授权的人工独立复核或新章节实验不在本轮自动开展。

**建议实施顺序与完成判据**

1. 修复覆盖入口、证据映射、S0 锚点和误报/漏报；给新表补必填、自然键、外键、状态、定位及失败返回检查。错误数据应能使检查失败。
2. 完成无损迁移及规则统一：补 S1/S2/S3 交接、来源登记、多证据与限定；原有事实、散文和未决状态都有明确去向，ID 重跑稳定。
3. 再做 render：先提供不写卡的 preview，覆盖九类及多来源、履历、争议等不同布局；证据单元格与散文保留、未知布局阻断、重复渲染幂等均通过后，再按用户保留的批量确认步骤执行。保留小节与表头的方案可以采用，但仅保留表头不足以修复现有证据和行布局丢失。
4. 最后形成可独立复用的版本包、数据字典、许可/引用说明、加载查询示例和诚实的质量/效率验证结果，再进入数据集论文定稿与发布。

- 冻结 `user-revisions.md`、`system-upgrade-log.md`，普通问答不再逐条记 REV，结果文件只保留当前状态。
- 新增 S0–S7 阶段产出规范（`01-domain/stage-artifact-schema.md`）与关系域值域矩阵（`01-domain/relation-domain-range.yml`）。
- 新增 `scripts/export_s0s7.py`（一次性转换产出 v0.1）与 `scripts/build_entity_candidates.py`（原书索引 → 全书候选）。
- 修正 `gianfranco-torcellan.md` 的 `authored_by` 反向边。
- 框架修订：`pipeline.md` 改为 S0–S7 并切断回环（backlog 替代「回知识元」），8 个 skill 与 `AGENTS.md` 对齐新阶段与产物。
- 派生文件约定：`relation-index.yml` 等派生文件只在 S7 发布或按需生成，不逐批重建、不当事实源（见 `scripts/README.md`）。
- 第 1–4 步规则收尾：统一事实源为 `04-knowledge/tables/`；S7 与 `05-outputs` 解耦；SKILL 正文对齐新顺序；ID 改单调发号 + 自然键 + 重定向表；origin 拆为 book/external/inferred；状态三维度统一（evidence_status/decision/relation_status）。
- 来源表修复：从同一记录的引文中唯一恢复 177 条被截断的 Treccani/Wikipedia URL；仅改 `sources.csv` 的 `url` 单元格，其他字段逐格核对一致；多候选、空值及非前缀差异均保留待查。
- 来源 URL 标点规范化：将 1,389 条 URL 字段末尾仅多出的句号删除；仅限同一记录只有一个引文 URL 且去除句号后完全一致者，2 条含多个引文 URL 的记录、9 条无匹配引文 URL 和 3 条空值未改。
- `build_cards.py --preview` 收口：关系子节改为完整投影 `relations.csv`，清除旧版/重复关系表并保留说明文字；修复空关系卡的空白行幂等问题，覆盖 1,019 张卡的只读双次渲染核对通过，未写回卡片。
- `build_field_facts.py` 来源 URL 解析固定为可重跑规则：识别平衡括号与 Markdown 链接，清理 URL 末尾句读标点；保留原表格单元格/引文，规范 `source_urls` 与来源登记。6,221 行仅 `source_urls` 更新、3 条来源 URL 标点修正，enrichment ID 无增删；应用后重跑预览为零记录/来源差异。
- 表审计补充 `occurrence_id` 唯一性失败条件与重复键回归测试；当前10,149行无重复。只读复跑确认S0 953段/0问题、S1 2,930索引行/3,592候选，更新草稿验证报告中的本机机械步骤单次耗时与候选计数。
