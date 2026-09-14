# 章前材料：摄入与处理过程

task-id：`patrons-and-painters-front-matter`。依据REV-083、084，2026-09-14执行；输入提交为`8822e732c027fb5b6b137c9ccdf318e46db70fa1`。采用ingest阶段1–2，直接语义阅读，工具仅用于行号、PDF显示、指纹与覆盖核验。

## 摄入

核对CHP-0Cover.pdf全部15页、五份00开头Markdown，确认是同一印本的重叠载体，不计六份独立证据。摄入结果和文件指纹先保存至[阶段结果](../results/stages.md)。目录正文及第二版导言误放在List_of_Plates文件内；本轮按实际内容确定范围。CHP-1.pdf第1页Part I / Rome已经在第一章处理包覆盖，沿用该入口，避免重计。

## 处理与改变判断的依据

完整阅读五份Markdown的282个物理行和PDF全部文字层；另外逐页目视15页扫描，用于版面、分页和重点OCR核对，不宣称完成全文逐字符校勘。PDF文字层同样含OCR错误，不能仅凭两份相同OCR相互验证。

- PDF 1装饰线被识为“-SEGALS SSL—”，不当作题名或实体。
- PDF 3第二版序言两次斜体Patrons and Painters在Markdown B:L4丢失；根据扫描补入句意理解。seventeenthand恢复为seventeenth- and；B:L5的1966.1恢复句界1966. I。
- PDF 4确认Ann Sutherland Harris，OCR为Aim；Tim Munby／Ben Nicolson仅作为与首版全称可能同指的候选，不在本阶段外部确认。
- PDF 5确认filled而非silled。PDF 6页码为viii而非vili；C:L15–16跨行exceptions连接，不把“- tions”独立理解。
- PDF 7确认Elizabeth Orna而非Oma；原印本自身写“Alessandro Marabottini Marabotti”，保留复合写法，不把疑似印本错误强行裁成规范全名。my own College可由同序签署King's College, Cambridge作章内候选映射，不据此补出职衔。
- PDF 8第一章起页为3而非z；目录页号没有可见数字，不猜为x或xi。PDF 10的第21图版组following page为136，Markdown为126；这是装订定位，不是作品年代。第17组104夹进机构名，移出Museum Boymans—van Beuningen的实体提及。
- PDF 13的Prà della Valle与Markdown Prato della Valle分别保存；Stearn and Son不是Steam and Son，Gabinetto Fotografico Nazionale不是Naziotiale，Marlborough Fine Art Ltd不是Malborough；供片编号10a／10b而非ioa／rob。
- PDF 14→15的“centre of / art patronage”跨页接读，脚注187–188不插入主句。Markdown “[Page 1708]”是误识，扫描为xviii；1708属于Poerson来信时间。
- PDF 15实际印Pier Leoni Ghezzi、Tommaso Chiari；不凭常识替换为Giuseppe Ghezzi或Giuseppe Bartolomeo Chiari，分别待同书及外部身份核对。S. Clemente的教堂建筑与其主保圣人分开。

## 收口

原始PDF／Markdown均保留不变，校正只在处理成果记录。实体提及、图版对象及供片者保存在[实体候选](../results/entity-candidates.md)，逐行句意与关系候选保存在[阶段结果](../results/stages.md)，避免重复抄录同一清单。原句按来源文件与行号直接引用；扫描校正另列，不把校正文冒作原始OCR。

本轮不建立正式KU或写入accepted，不启动对齐／补足／正式关系。新候选的查重、规范双语标题、来源原句转写和正式端点映射属于下一个知识元阶段。实体候选与关系候选均是交付成果，不以候选数量声明唯一实体数或完整召回率。

## 核对与交接

核对37个语义跨度覆盖A–E的282个物理行，无行号缺口或越界；图版子项覆盖1–68，17／37的三子项和48的四子项均保留。六项来源SHA-256与摄入指纹一致，未修改来源本体。校核了候选表的图版角色与原目录对应，并将基金从确定机构改为收藏来源字段，补列缩引责任者和承载期刊；同名／别名及旧藏问题继续作为下一阶段辨识责任。

过程只保留上述来源校正、语义边界和核对依据；实体清单及逐行摘要各在对应结果固定路径维护。本任务未产生需要保留的重复草稿，也未改动第一章已有知识结果。
