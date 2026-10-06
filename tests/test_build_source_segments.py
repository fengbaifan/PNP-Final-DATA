from scripts import build_source_segments


def test_source_files_excludes_parallel_named_backmatter_intro(tmp_path):
    names = (
        "01_CHP-1.md",
        "01_CHP-1_intro.md",
        "18_CHP-18Conclusion.md",
        "18_CHP-18Conclusion_intro.md",
        "00_01_Title_Copyright.md",
    )
    for name in names:
        (tmp_path / name).write_text("one source paragraph\n", encoding="utf-8")

    selected = {path.name for path in build_source_segments.source_files(tmp_path)}

    assert selected == {
        "01_CHP-1_intro.md",
        "18_CHP-18Conclusion.md",
        "00_01_Title_Copyright.md",
    }


def test_build_segments_uses_named_full_text_and_not_duplicate_intro(tmp_path, monkeypatch):
    monkeypatch.setattr(build_source_segments, "BASE", tmp_path)
    source_dir = tmp_path / "02-sources" / "02-Markdown"
    source_dir.mkdir(parents=True)
    monkeypatch.setattr(build_source_segments, "SOURCE_DIR", source_dir)
    (source_dir / "18_CHP-18Conclusion.md").write_text("First sentence.\n\nSecond sentence.\n", encoding="utf-8")
    (source_dir / "18_CHP-18Conclusion_intro.md").write_text("First sentence.\n\nSecond sentence.\n", encoding="utf-8")

    rows, issues = build_source_segments.build_segments()

    assert issues == []
    assert [row["source_file"] for row in rows] == [
        "02-sources/02-Markdown/18_CHP-18Conclusion.md",
        "02-sources/02-Markdown/18_CHP-18Conclusion.md",
    ]
