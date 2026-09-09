# 01_sources

科研级主干的原始来源层。

该目录用于承接冻结的输入记录及其注册信息，包括但不限于：

- 原始 PDF / 图像 / OCR 文本
- 索引行级记录
- source edition 与 snapshot 元数据
- 文档级与页级来源映射

当前阶段仅建立 canonical 目录入口，不直接迁移既有历史数据。现有来源仍以以下目录为准：

- `00-book/`
- `02-Markdown/`
- `03-Index/`
- `22-source-registry/`

后续迁移原则：

1. 先补 source registry 与 snapshot contract
2. 再通过适配器接入历史数据
3. 最后按需要归档 legacy 路径
