# no-data 与开放网页研究规则 v2.0

本文件定义 Wikipedia、Wikidata 或其他外部数据库有数据/无数据时的处理边界。规则面向能力，不绑定已经退役的 provider。

## 一、基础规则

```text
页面存在 != 验证通过
QID 存在 != externally_verified
API success != 知识成立
无页面或无 QID != 对象不存在
外部数据库缺失 != 原始来源无效
```

API、浏览器和开放网页研究只能产出 evidence candidate，不直接裁决 KU、claim 或 relation。

## 二、有数据时

命中外部来源后至少记录：

```yaml
platform:
url:
qid:
match_quality: strong | medium | weak
claim_scope:
candidate_rank:
redirect_or_disambiguation:
supports:
limits:
```

- `entity_identity_only` 只能证明实体身份候选。
- `term_existence` 只能证明术语存在。
- `bibliographic_hint` 只能证明书目信息线索。
- 单一 evidence 不得提升为 `confidence: high`、`consensus: confirmed` 或 `externally_verified`。

## 三、无数据时

无数据必须记录为证据状态，而不是删除或否定 KU：

```yaml
external_lookup:
  wikipedia: no_wikipedia_page
  wikidata: no_wikidata_qid
  external_databases: external_not_found
  next_route: browser_or_open_web
```

后续按对象类型选择独立来源：

```text
Wikipedia / Wikidata 无结果
-> 浏览器或开放网页搜索
-> CrossRef / DOI / WorldCat
-> archive.org / library / institutional page
-> source_backed_only 或 model_supported
```

如果原始文献明确存在，状态可保持 `source_backed` 或 `source_backed_only`；只有模型知识时必须写为 `model_supported`。

## 四、工具中立边界

任何外部研究工具可以搜索、打开、快照、抽取正文并生成 citation/evidence candidate，但不得：

- 判断 KU 类型；
- 裁决 claim 或 relation；
- 提升 confidence、consensus 或 verification 状态；
- 直接写 KU、claim 或 relation。

产物必须进入 evidence JSONL，再交给 Agent 复核和 apply gate：

```json
{
  "evidence_id": "ev-...",
  "adapter": "browser_or_open_web",
  "source_url": "",
  "snapshot_ref": "",
  "extracted_text_ref": "",
  "candidate_citation": "",
  "supports": [],
  "claim_scope": "",
  "match_quality": "weak",
  "limits": ""
}
```

## 五、验收信号

- apply gate 阻断把 no-data 解释为 deletion；
- apply gate 阻断单源 evidence 越权升级；
- backlog 能显示 `external_not_found` 与 `source_backed_only` 队列；
- 现行规则不依赖特定 provider 缓存、CLI 或兼容脚本。
