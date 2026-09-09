import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import build_translation_index


def write_unit(root: Path, unit_type: str, slug: str) -> None:
    path = root / "04-knowledge" / "units" / unit_type / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"title: {slug}\n"
        f"name_en: {slug}\n"
        f"name_original: {slug}\n"
        "language_original: en\n"
        "---\n",
        encoding="utf-8",
    )


class BuildTranslationIndexTests(unittest.TestCase):
    def test_render_index_does_not_truncate_more_than_500_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for number in range(501):
                write_unit(root, "persons", f"person-{number:03d}")

            index = build_translation_index.build_index(root)
            rendered = build_translation_index.render_index(index, generated="2026-06-02")
            data = yaml.safe_load(rendered)

        self.assertEqual(data["total"], 501)
        self.assertEqual(len(data["index"]), 501)

    def test_rebuild_drops_deleted_unit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_unit(root, "persons", "keep")
            write_unit(root, "persons", "delete-me")
            deleted = root / "04-knowledge" / "units" / "persons" / "delete-me.md"
            deleted.unlink()

            slugs = [row["slug"] for row in build_translation_index.build_index(root)]

        self.assertEqual(slugs, ["persons/keep"])

    def test_stable_generated_date_preserves_date_for_unchanged_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "translation-index.yml"
            index = [{"slug": "persons/keep", "type": "persons"}]
            output.write_text(
                build_translation_index.render_index(index, generated="2026-06-02"),
                encoding="utf-8",
            )

            generated = build_translation_index.stable_generated_date(index, output)

        self.assertEqual(generated, "2026-06-02")

    def test_stable_generated_date_advances_for_changed_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "translation-index.yml"
            output.write_text(
                build_translation_index.render_index([], generated="2026-06-02"),
                encoding="utf-8",
            )

            generated = build_translation_index.stable_generated_date(
                [{"slug": "persons/new", "type": "persons"}], output
            )

        self.assertEqual(generated, build_translation_index.date.today().isoformat())


if __name__ == "__main__":
    unittest.main()
