# 章前材料：知识元与关系工作结果

任务：`patrons-and-painters-front-matter`；REV-083–086；当前阶段为**初步对齐，进行中**。摄入、处理与有据对象的初稿登记已完成；本轮解决8条主候选身份，仍有14条主候选暂缓。尚未逐一完成全部知识元的外部对齐；全面补足及正式关系未开展，知识发现与页面暂停。

## 当前成果

- 本任务累计**378个新知识元**、**43个既有有效知识元更新**、**4个未接收旧卡原位整理后接收**，共涉及425个KU；全库有效登记为800个。REV-086新增5个、更新12个已有对象；新增来源和身份入口不表示整卡补足完成。
- 初始241条主候选中，223条映射到知识元，4条作属性／语境保留，14条暂缓。图版中的多名创作者、肖像对象、保管机构与地点拆成独立端点，并进行跨图版复用，所以候选行数不等于实体数量。
- 书目缩引额外核出两种刊载期刊；仅依据所列书目和索引条目，不表示原论文全文已读。
- 全部新增卡有中英文标题与描述、分字段内容、原书摘录及页行定位；关联对象提供可点击KU链接，候选与正式关系分开。

| 类型 | 新建 | 更新已有有效KU | 旧卡整理后接收 |
|---|---:|---:|---:|
| 人物 | 144 | 28 | 3 |
| 机构 | 43 | 4 | 0 |
| 文献 | 15 | 1 | 0 |
| 术语 | 4 | 0 | 0 |
| 地点 | 65 | 10 | 0 |
| 事件 | 1 | 0 | 0 |
| 作品 | 104 | 0 | 1 |
| 家族 | 2 | 0 | 0 |

## 唯一成果与依据

- [摄入与处理定稿](../../03-processing/patrons-and-painters-front-matter/results/stages.md)：来源、15页PDF与282行Markdown覆盖、语义分析和原文关系候选。
- [实体候选](../../03-processing/patrons-and-painters-front-matter/results/entity-candidates.md)：原始提及与类型边界。
- [知识元映射与登记过程](../../03-processing/patrons-and-painters-front-matter/process/knowledge.md#候选登记映射)：全部候选与角色端点的知识元链接、属性处置及待决理由。
- [有效登记](../accepted.yml)：当前KU路径；每个对象正文唯一，不在本报告复制。

可直接查看：[芒比的全名与昵称](../units/persons/a-n-l-munby.md)、[尼科尔森的全名与昵称](../units/persons/benedict-nicolson.md)、[托马索·基亚里](../units/persons/tommaso-chiari.md)、[提埃坡罗及本轮两件作品入口](../units/persons/giambattista-tiepolo.md)、[科涅克—杰藏宴会](../units/works/tiepolo-banquet-cognacq-jay.md)、[维多利亚国家美术馆藏宴会](../units/works/tiepolo-banquet-victoria.md)。

## 本轮对齐结果

- Tim Munby＝Alan Noel Latimer Munby；Ben Nicolson＝Lionel Benedict Nicolson，沿用原路径，并补入第二版序言的朋友／咨询原句。
- Marabottini复姓保留原书次序，另列大学目录的倒序异文。Pier Leoni Ghezzi对应Pier Leone Ghezzi；Tommaso Chiari与Giuseppe Bartolomeo Chiari为官方目录分列的不同对象。
- 圣克莱孟堂项目原文列出的7位艺术家均有明确人物端点；目录的Pietro Antonio De Petri与原书Pietro di Pietri在同一卡中保留两种写法。
- 导言的Guido按语境对应Guido Reni；导言Tiepolo由同书索引定位Giambattista Tiepolo。圣克莱孟主保圣人对应早期教宗Clement I。
- 图版61a对应Paris Musées **J 104**；61b对应NGV **103-4**。两卡分别保存作者、题名、年代、材质、尺寸及馆藏入口；巴黎藏本的预备版本性质标为外部馆方依据。

来源、实际阅读范围、配对理由及14条剩余暂缓项见[初步对齐过程](../../03-processing/patrons-and-painters-front-matter/process/knowledge.md#初步对齐rev-086)。本轮没有新增QID或新的Wiki双向验证；采用专业机构记录完成上述特定身份问题，不代表Wikipedia全文已读。

## 完成依据与实际限制

REV-085登记时核对547条新增／重新登记原书摘录与实际行号、候选去向、引用序号和链接。REV-086核对17张受影响卡、其中25条原书摘录、全部新增来源编号和本地链接；已有sources前缀与正式relations保持原值，800条有效路径以及accepted原有claims／structure保留。针对这17卡的既有内容检查未报确定性缺陷；`git diff --check`通过。机械检查与语义自查分别解释，不称独立验收。

四张第六章旧卡仅采用REV-085有据内容，原稿由Git追溯，不代表第六章执行。图库条目已解析不等于观看了全部艺术作品原图，馆藏记录身份核对也不等于视觉比对或全面补足。

14条主候选暂缓涉及Lazzarini、11个供片署名、博尔盖塞胸像具体版本和三幅未具名总督肖像。卡内另有爵号收藏者、图像角色、5件其他Tiepolo图版的作者及书目版本等待逐项对齐；14不是全部缺口数。当前作品清单只覆盖已采用来源，不是人物作品全集；书中历史收藏记录与本轮馆方记录分别注明。

## 下一步

继续**初步对齐**：按未定图版作者、爵号／简称、摄影署名及书目版本集中核对；有充分身份依据的对象再交补足，证据不足的对象保留具体阻断理由。现有第一章结果继续按其自己的来源范围和任务结果解释。此次未提交或推送仓库。
