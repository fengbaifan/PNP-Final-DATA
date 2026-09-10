# 知识元字段与存储

这是各类 KU 共用的 frontmatter 元数据契约（REV-019）。人物生平、作品属性、建筑沿革等属于正文内容，不能与来源/处理元数据混成一套类型各异的表头。内容判断不能由字段存在推导。

## 最小字段

```yaml
title: "那不勒斯（Naples）"
name_en: "Naples"
type: person | family | institution | place | work | archive | term | procedure | event
evidence_status: source_backed
sources:
  - citation: 来源书目信息
    location: 第几章、印刷页码（必要时另列 PDF 页）及行号；网页用实际小节定位
    sentence_summary: 对应句意的简短转述；多处引文分别注明页段
    evidence_ref:
      doc_id: 实际来源标识
      source_file: 实际文件路径
      source_span: "lines 起始行–结束行; print pp. 印刷页"
created: YYYY-MM-DD
updated: YYYY-MM-DD
```

来源应能核实对象和本次内容；定位不精确时记录原因，不填伪路径。日期对应实际创建/更新事件。成稿后通过 accepted.yml 登记有效引用，不表示外部事实已确认。
各类型统一使用 title、name_en、type、created、updated、evidence_status、sources 及其相同子字段；sub_type 等可选字段也使用统一含义。示例 source_backed 只适用于实际有原文支持的内容，不是所有新对象的默认值。
本地文本引用记录来源版本、文件和 source_span 中的具体行范围，PDF 同时保留印刷页/必要的 PDF 页区别；这里的“行数”指可追溯定位，不用总行数冒充覆盖。多个不连续位置分别列明。外部网页按实际 URL、访问日期、版本/段落或记录标识定位，不虚构本地行号。版本指纹可引用来源登记及处理记录，不在各 KU 重复复制整份来源清单。
每条来源还须提供支持相关内容的句子摘要（REV-030）：书籍在 sources.location 明写第几章、印刷页，sources.sentence_summary 保存简短转述；同一来源的不同页段分别登记或在摘要中逐段标明对应页／行，不用概括整本书代替句子依据。保留 evidence_ref 的原始定位，不把摘要当逐字引文或独立证据。网页无章节页码时以实际小节／属性定位，并记录内容摘要；没有的信息不伪填。
元数据登记“引用了什么”，内容属性/记录须注明“哪一出处支持这一信息”；整卡 evidence_status 不能代替事实级的支持范围。第三部分“关系与证据”（REV-020）解释证据绑定及其边界；现有 relations 在 frontmatter 中保留机器兼容位置，但逻辑上属于第三部分，不是一般来源元数据。不复制或搬动已成立的关系记录。
title 为“中文名（English name）”，name_en 保存同一英文名称，沿用现有字段，不再增加同义的 title_zh/title_en 副本。上述名称只是格式示例，不是待填的默认对象。英文惯用名与原语言名称分清，例如 Naples 是英文名，Napoli 是意大利语名，原文名/别名可按需另存。
人物以有依据的全名作为规范展示名；称号、昵称、别名、荣誉头衔和贵族头衔在内容中分别记录，不能互相替代。仅知惯用名时保留可确认名称并注明全名待对齐，不能为满足格式虚构全名；规范名变更不改稳定文件路径。
书信等无正式题名的文献，使用完整中文描述性标题及对应英文标题（REV-028），如“发信人中文名致收信人中文名的信（Letter from Sender to Recipient）”；不要用拉丁字母人名与“致／信”拼接充作双语标题。仅保留已知姓名，中文音译及自拟描述性题名在正文注明，不推定为档案原题；确知的日期可在两种表达中对应，主题说明可放正文，不因标题冗长省略另一种语言。
没有可靠通行译名时可以采用忠实的描述性暂译，并在正文注明；不得把暂译声称为官方题名。身份或名称无法确定时保留已知原名及明确待定说明，双语要求不授权臆造。原文名、别名、tags、sub_type 按实际内容写。描述中英文存于同一正文，见 body-template.md；不另设重复的 description 字段或语言副本文件。来源格式见 citation.md。

## 按实际事件启用的字段

- evidence_status：unverified/source_backed/partially_verified/externally_verified/model_supported；模型判断不能成为来源事实。
- confidence：low/medium/high；consensus：tentative/disputed/confirmed。有判断依据才赋值，不默认所有对象中等可信；confirmed 不由来源数量推导。
- verification_level 和 last_verified 仅在实际核验后记录；review_due 仅在有明确复查安排时使用。L1–L7 是既有接口兼容码。
- source_count 如使用，应与实际去重来源绑定一致；不存时可派生。
- relations 仅在关系成立后写，weak_associations 不自动转正。
- topic_memberships、primary_theme、primary_dimension、primary_domain 等只在相关结构实际形成后使用，父层缺失合法，不作为研究债务。
- version 仅供既有机器接口兼容，普通文档通过 Git 和过程记录追溯，不强制初稿填写。

机器验证状态写回仍遵守 verify 的 evidence 格式和受控 apply；其字段要求只在调用该接口时适用，不能反向强制普通初稿填满。
同一对象一个固定正文路径、一组 frontmatter；状态与正文一致，来源本体不改写。身份冲突不机械合并。

## 关联契约

层级表达见 hierarchy-field.md，关系类型见 relation-types.md。类型专有内容按真实材料选择，不能为字段完整编造国籍、日期、作品或验证结论。
