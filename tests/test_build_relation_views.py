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

    assert "### 当前关系记录（REV-060 定稿）" in result
    assert "REV-060" in result
    assert render_table([row]) in result
    assert "这段对象级边界说明必须保留。" in result
    assert "### 身份与外部链接" in result


def test_repo_evidence_link_is_relative_to_the_knowledge_card():
    assert (
        _repo_relative_link("persons/caravaggio.md", "02-sources/02-Markdown/01_CHP-1.md")
        == "../../../02-sources/02-Markdown/01_CHP-1.md"
    )


def test_empty_relation_view_is_idempotent_and_replaces_legacy_empty_marker():
    source = """## 关系与证据

### 关系记录
暂无正式关系。

### 身份与外部链接
link
"""

    first = replace_relation_view(source, [])
    second = replace_relation_view(first, [])

    assert first == second
    assert first.count("当前没有正式关系。正文中的导航与线索不自动形成关系边。") == 1
    assert "暂无正式关系。" not in first


def test_relation_rows_can_add_a_table_under_an_existing_subsection_without_losing_prose():
    source = """## 关系与证据

### 当前关系记录

暂无本项目已确认的正式出向关系。

### 身份与外部链接

identity prose
"""
    row = "| ← 所在地（`location_of`，反向投影） | [墨西拿](messina.md) | evidence |"

    result = replace_relation_view(source, [row])

    assert "### 当前关系记录" in result
    assert "| 方向与关系 | 关联知识元 | 语境与证据 |" in result
    assert row in result
    assert "暂无本项目已确认的正式出向关系。" in result
    assert "identity prose" in result


def test_relation_rows_at_end_of_card_do_not_add_blank_line_at_eof():
    source = "## 关系与证据\n\n### 关系记录\n"
    row = "| ← 保管对象 | [作品](work.md) | evidence |"

    result = replace_relation_view(source, [row])

    assert result.endswith(row + "\n")
    assert not result.endswith(row + "\n\n")


def test_relation_view_rebuilds_legacy_tables_and_preserves_prose_idempotently():
    source = """## 关系与证据

### 关系记录

| 关系类型 | 关联知识元 | 语境 |
|---|---|---|
| old relation | [旧对象](old.md) | old evidence |

这段关系边界说明必须保留。

### 身份与外部链接

identity prose
"""
    row = "| → 创作者（`created_by`） | [新对象](new.md) | 新证据 |"

    first = replace_relation_view(source, [row])
    second = replace_relation_view(first, [row])

    assert first == second
    assert "| 关系类型 | 关联知识元 | 语境 |" in first
    assert row in first
    assert "old relation" not in first
    assert "这段关系边界说明必须保留。" in first
    assert "identity prose" in first
