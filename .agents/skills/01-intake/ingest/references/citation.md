# 引用格式规范

> 现行总纲见仓库根目录 `AGENTS.md`；字段与存储边界见同目录 `knowledge-unit-field-contract.md`。

## Chicago 17th Edition（默认格式）

**所有知识元页面 `## 参考文献` 和 frontmatter `citation` 字段统一使用。**

### Bibliography 条目模板

```
书籍（单作者）:
  姓, 名. *书名：副标题*. 城市: 出版社, 年份.

书籍（编著）:
  编者姓, 名, ed. *书名*. 城市: 出版社, 年份.

多编者:
  编者一姓, 名, and 名 编者二姓, eds. *书名*. 城市: 出版社, 年份.

期刊论文:
  作者姓, 名. "文章标题." *期刊名* 卷, no. 期 (年份): 页码-页码. DOI.

网络/Wikipedia:
  "词条名." Wikipedia. 修改日期 月 日, 年份. URL.
```

### 脚注格式（sources.citation 字段使用简化 note 格式）

```
书籍: 名 姓, [ed.,] *书名* (城市: 出版社, 年份), 页码.
论文: 名 姓, "文章标题," *期刊名* 卷, no. 期 (年份): 页码.
```

### APA 7th Edition（可选）

可在 citation.json 的 `apa` 字段中额外记录，但不作主标识。

---

引用格式不定义验证平台或置信度晋升。状态裁决统一交给
`.agents/skills/03-verification/verify/SKILL.md`。
