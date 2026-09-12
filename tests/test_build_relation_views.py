from scripts.build_relation_views import _repo_relative_link, render_table, replace_relation_view


def test_relation_view_replaces_only_standard_table_and_preserves_following_prose():
    source = """## 关系与证据

### 当前关系记录（REV-060 定稿）

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
| old | [旧对象](old.md) | old evidence |

这段对象级边界说明必须保留。

### 身份与外部链接

link
"""
    row = "| → 创作者（`created_by`） | [新对象](new.md) | 新证据 |"

    result = replace_relation_view(source, [row])

    assert "### 关系记录" in result
    assert "REV-060" not in result
    assert render_table([row]) in result
    assert "这段对象级边界说明必须保留。" in result
    assert "### 身份与外部链接" in result


def test_repo_evidence_link_is_relative_to_the_knowledge_card():
    assert (
        _repo_relative_link("persons/caravaggio.md", "02-sources/02-Markdown/01_CHP-1.md")
        == "../../../02-sources/02-Markdown/01_CHP-1.md"
    )
