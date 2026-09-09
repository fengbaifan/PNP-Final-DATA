---
name: compose
kind: leaf
phase: later
triggers:
  - compose
  - 知识呈现
  - 页面展示
  - 查询知识
description: 第二部分的成果组织、查询、内容设计与页面呈现技能。初期不自动启动；用户明确查询或展示时可定向调用。
---

# compose

第二部分的成果组织、查询、内容设计与页面呈现技能。初期不自动启动；用户明确查询或展示时可定向调用。

## 执行

1. 确认要回答的问题、受众与成果范围；直接检索相关 KU、关系和来源，区分已证事实、解释与未决项。
2. 先形成内容结构和文稿，记录取舍、证据责任与缺口。用户只要查询时交付有依据的回答，不强制生成页面。
3. 页面任务先形成内容定稿与设计说明，再制作展示；页面代码用于呈现，不能回头定义知识事实。
4. 图谱读取当前 KU 和正式关系索引。数据、词表、筛选和页面说明一致；本地打开验证必要资源与链接，禁止把静态旧指标当当前事实。
5. 输出 metadata 登记使用对象、来源、uncertain_points、candidate_refs 与 file_back_status。输出不是独立证据，不自动回流知识发现。

## 存储与完成

过程：05-outputs/process/<id>.md；最终结果与交付说明：05-outputs/results/<id>.md；实际页面沿用既有固定入口，不复制另一个当前主页面。
首次对象需要新页面时才新增；同一成果以版本更迭维护。检查内容、可读性、链接、交互与实际数据，不以文件存在代替展示验收。
必要的图谱生成器为 scripts/build_knowledge_graph_data.py，输出登记为 scripts/build_output_gallery.py；只在实际需要时调用。

## 按需直接参考

- `references/data-schema.md`
