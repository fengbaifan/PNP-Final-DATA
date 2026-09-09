import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import audit_repo


class UnitSnapshotCacheTests(unittest.TestCase):
    def setUp(self):
        audit_repo.read_text.cache_clear()
        audit_repo.split_frontmatter_body.cache_clear()
        audit_repo.extract_frontmatter.cache_clear()
        audit_repo.has_frontmatter_field.cache_clear()
        audit_repo.scalar_frontmatter_field.cache_clear()
        audit_repo.list_frontmatter_field.cache_clear()

    def test_snapshot_and_checks_read_each_unit_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unit = root / "04-knowledge" / "units" / "terms" / "one.md"
            unit.parent.mkdir(parents=True)
            unit.write_text(
                "---\ntitle: One\ntype: term\nconfidence: medium\nconsensus: tentative\n---\nBody\n",
                encoding="utf-8",
            )
            original = Path.read_text
            unit_reads = 0

            def counted_read(path, *args, **kwargs):
                nonlocal unit_reads
                if path == unit:
                    unit_reads += 1
                return original(path, *args, **kwargs)

            with patch.object(Path, "read_text", counted_read):
                snapshots = audit_repo.load_unit_snapshots(root)
                files = [snapshot.path for snapshot in snapshots]
                audit_repo.missing_fields(files, root, ["title", "type"])
                audit_repo.invalid_enum_issues(files, root)

        self.assertEqual(unit_reads, 1)
        self.assertEqual(snapshots[0].frontmatter.splitlines()[0], "title: One")
