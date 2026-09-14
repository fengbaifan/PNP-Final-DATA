# 知识元关系契约

> 受控类型与 inverse 映射的唯一机器事实源是同目录的 `relation-types.yml`。本文件只定义语义边界和字段契约，不复制完整枚举。

## 一、权威与投影

- 已批准的 KU `relations` 是当前关系断言输入。
- `04-knowledge/quality/relation-index.yml` 是由输入生成的 R2 投影，不是独立关系事实源。
- `related` 仅为历史兼容字段；`weak_associations` 对其具有排除优先级。
- 生成器、审计器和 batch prescreen 必须共同加载 `relation-types.yml`，不得各自维护类型集合或 inverse map。
- REV-019、020 的正文“关系与证据”部分解释并指向这些记录，不复制另一套正式边。内容表中的亲缘、创作者、设计师、所有者等项目须有各自依据；正式建边仍检查有效端点、受控类型、方向及具体证据，不能由字段/链接存在自动生成。历史角色与时间限定不得在建边时丢失。

## 二、字段

```yaml
relations:
  - relation_type: authored_by
    target: ../persons/example.md
    target_type: person
    note: "关系语义说明"
    evidence_ref: source-or-claim-reference
    confidence: medium
    relation_source: explicit
    review_status: evidence_backed_relation
```

最低要求：

- `relation_type` 必须属于受控 schema；历史 generic 类型只能按 baseline 读取，禁止新增。
- source/target 必须存在并满足方向语义。
- 要求 inverse 的类型使用 schema 中的映射；自动补全只生成派生 backlink，不构成第二次语义裁决。
- `evidence_ref`、`claim_id` 或明确的 `needs_evidence` 状态至少存在一个。
- 不得仅凭共享标签、年代、同章或正文链接提升为正式关系。
- 家族适用既有类型：`member_of` 从 person 指向 family，须有成员身份依据，并在 note 中注明已知亲缘／婚姻／收养性质和时期；指向 institution 时仍是组织成员关系。`part_of` 从 family 支系指向有据的上级家族，不用于联姻、受雇或同姓。两类关系都不因 family 分类自动生成；具体亲缘可先在内容表记录，未受控的关系谓词不临时写入正式图谱。

常用具体关系的方向：

| 事实 | 正向关系 | 方向与边界 |
|---|---|---|
| 通信 | `addressed_to` | archive → 收信人；作者仍用`authored_by`，通信双方的长期往来才另用`corresponded_with` |
| 师承／合作／雇佣 | `trained_by`、`collaborated_with`、`employed_by` | person → 教师／合作者／雇主；同一对人物可在不同时段有多种关系 |
| 教育 | `educated_at`／`education_of` | person → 就读机构；role保留学习阶段或学位，time保留入学／毕业或就读期间。仅有入学年不推定毕业，不与个人师承、雇佣或院士成员身份混合；反向只作导航。 |
| 委托／赞助／创作 | `commissioned_by`、`patronized_by`、`created_by` | work → 委托人／赞助人／创作者；仅有合同对象时用scope明确未锁定存世版本 |
| 所有／取得／经手 | `owned_by`、`acquired_by`、`handled_by` | work → 所有人／取得者／市场经手机构；三者不得互换 |
| 安置／保管／位置 | `installed_at`、`held_by`、`located_at` | work → 安置建筑／保管机构／物理地点，须保留适用时间或来源时点 |
| 配对作品 | `pendant_of` | work ↔ work；来源明确两件作品构成配对，单侧保存事实、反向仅作投影；同作者、同题材或同尺寸不构成配对依据 |
| 预备模型／样稿 | `model_for` | work → 为之准备的work；来源明确具体两件作品的模型／样稿关系，`modeled_by`为反向导航；同题材、年代先后或外观相近不证明预备关系 |
| 借入／出借 | `borrowed_by`、`lent_by` | work／archive → 借入者／出借者；保存具体借存或借阅的时间、对象与角色，不能据出借身份推定所有权；`borrower_of`、`lender_of`只作对应反向导航 |
| 亲缘／家族 | `parent_of`、`child_of`、`spouse_of`、`sibling_of`、`kin_of`、`member_of` | 具体亲属关系优先；只能确认一般亲族时才用`kin_of`并在role中保存原称 |
| 任命／荣衔／特权 | `appointed_by`、`honoured_by`、`privilege_granted_by` | 受任人／受荣人／机构 → 授予者；事件节点同时可用`has_participant`保存具体角色 |
| 文书／借阅／证词／建议 | `issued_by`、`borrowed_by`、`contributed_by`、`testified_about`、`advised` | 文书→发布主体、文献→借阅人、证词→发言者、证人→被证事项人物、建议者→受建议者；对象与事件仍须分别判断 |

`time`可以是有据日期、年份、区间或来源时点；`role`保存该端点在关系中的职责；`scope`保存具体作品版本、项目、地点作用或事实边界。投影的反向边必须原样保留这些限定，并标明其来源关系，不能把反向导航显示成另一张卡的本地S编号。

## 三、来源与审查状态

`relation_source`：

- `explicit`：Agent 已在 KU 中声明；
- `inferred_by_model` / `inferred_by_rule`：仅为候选信号；
- `migrated_from_related`：历史兼容记录，不自动成为正式关系。

`review_status`：

- `evidence_backed_relation`：证据和语义已审查；
- `needs_evidence`：语义可能成立但证据不足；
- `weak_inference`：仅保留候选信号；
- `conflict`：存在方向、对象或证据冲突。

## 四、弱关联

```yaml
weak_associations:
  - target: ../terms/example.md
    reason: co_occurrence_in_same_topic
    confidence: low
    evidence_gap: no_direct_evidence
```

weak association 不进入正式 relation index；重新运行生成器不得复活已排除信号。

## 五、变更流程

新增或修改关系类型时，先修改 `relation-types.yml`，再运行 schema 测试、relation index 重建与关系一致性审计。类型、方向和强度仍由 Agent 裁决，脚本只校验受控值、端点和 inverse。
