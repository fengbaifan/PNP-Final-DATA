# 《赞助人与画家》全书语义处理（S2）当前结果

更新日期：2026-10-08。任务ID：`patrons-and-painters-full-book-s2`。**状态：S2交接审计进行中，尚未进入S3。**本文件只记录当前范围、状态、未决项和下一步；逐项语义裁决见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md)及[逐段结果](../../03-processing/patrons-and-painters-full-book-s2/results/stages.md)。

## 范围与覆盖

S0登记79个规范来源文件、832段，涵盖书前材料、第1–17章、结论、附录、第二版后记、书目和索引；42段为派生视觉转录。第十一、十二章与第十章同版扫描产生的44段重复OCR已排除。书目按出版记录和引文定位处理，索引按候选定位材料处理，不作为正文断言。

| 当前S2覆盖状态 | 段数 |
|---|---:|
| reviewed / complete | 678 |
| 有理由排除 / complete | 154 |
| queued | 0 |
| reviewed / partial | 0 |
| 合计 | 832 |

所有纳入处理的正文、注释、图版说明及书前/书后材料均有S2处理记录。书目段已处理至L3–1306；索引94段已处理并补入索引p.446四条纸本漏项。全库脚注续页、正文回链和statement引用已专项检查；第九章p.270注7的印本错位，以及第十四章p.359重复且无正文标号的注4，按来源异常保留，不强行回链。

## 当前数据与机械检查

当前表包含1,019个KU、11,477个候选、27,347条mentions及12,262条statement；索引候选2,934行。`python -X utf8 scripts/audit_tables.py --strict-stage`通过，`s2_missing=[]`、`errors=[]`。仍有两条既存enrichment `source_ref`警告：`enr-06678`、`enr-06937`无法从对应卡片source清单解析。结构检查不等于语义准确或实体召回完整；目前没有独立外部语义验收。

全库`footnote_pending`和`footnote_text_pending`为0，statement内引用目标失效数为0。候选外键及关系端点仍在最终S2交接审计范围内。

## 候选表面复核与当前游标

书前及第1–10章的候选表面提示已逐项裁决；第八章新增4个候选、47条mentions，第九章新增1个类型待定收藏候选及44条mentions，并拆分任职与收藏陈述；第十章新增1个类型待定Crozat收藏候选、60条mentions及4条statement。逐项结果见[第八章](../../03-processing/patrons-and-painters-full-book-s2/results/chp-08.md)、[第九章](../../03-processing/patrons-and-painters-full-book-s2/results/chp-09.md)和[第十章](../../03-processing/patrons-and-painters-full-book-s2/results/chp-10.md)。

第十三章24个reviewed段的33条提示中18条映射、15条不写；新增1个类型待定收藏候选、18条mentions及2条statement。第十四章18个reviewed段的24条提示中10条映射、14条不写；新增Mead藏画收藏、Treviso Algarotti—Bonomo书信群和Augustus III古代大师收藏3个候选，新增10条mentions并补齐10条既有statement候选引用。“their collection”的身份仍未决，按原判断不映射。两章写后定位器残余均与no-write裁决逐跨度一致。扫描只匹配已有候选词形，不发现未登记实体，不构成召回率验收；逐项裁决见[第十三章](../../03-processing/patrons-and-painters-full-book-s2/results/chp-13.md)和[第十四章](../../03-processing/patrons-and-painters-full-book-s2/results/chp-14.md)。

当前按书序转至第十五章：17个reviewed段中有16条提示待逐项审查。之后继续检查结论、附录、后记及书目边界，并完成跨页注释/指代、statement限定语、候选外键及关系候选的S2交接审计。第十章规范源同时承载第十一、十二章内容，44段重复OCR不重复计入。

## 全书S2交接审计

关系候选复核已覆盖第1–20章记录；当前2,331条relation candidate中2,325条端点完整、6条仍开放且有来源依据：第七章两件Poussin作品与Louvre/Detroit馆藏的逐件配对未明；第八章未具名女儿的分配对象、未具名联姻家族及p.238注4“These pictures”的具体范围未明；第十四章Brühl两处母题与Maecenas/Flora作品未逐项对应；第二十章Alazard/Franceschini作品委托者未明。它们继续保留待证，不转成无证正式关系。

S2交接前仍需完成后续候选提示复核，并逐项复查来源范围及重复副本、跨页脚注和指代、statement限定语、候选外键及全部关系候选，确认开放项的证据边界。交接审计完成后再进入S3全局身份对齐；此前不推进S3–S6、知识发现或页面工作。
