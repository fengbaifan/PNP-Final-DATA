import json
import tempfile
import unittest
from pathlib import Path

from scripts import write_current_health


class CurrentHealthWriterTests(unittest.TestCase):
    def test_unchanged_snapshot_keeps_timestamp_and_file_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "current-health.json"
            existing = {
                "timestamp": "2026-07-18T11:43:16",
                "summary": {"total_units": 1285},
            }
            path.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            before = path.read_bytes()

            written = write_current_health.write_health_snapshot(
                path,
                {
                    "timestamp": "2026-07-18T12:30:00",
                    "summary": {"total_units": 1285},
                },
                now="2026-07-18T12:30:00",
            )

            self.assertEqual(written["timestamp"], "2026-07-18T11:43:16")
            self.assertEqual(path.read_bytes(), before)

    def test_changed_snapshot_uses_new_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "current-health.json"
            path.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-07-18T11:43:16",
                        "summary": {"total_units": 1285},
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            written = write_current_health.write_health_snapshot(
                path,
                {
                    "timestamp": "ignored",
                    "summary": {"total_units": 1286},
                },
                now="2026-07-18T12:30:00",
            )

            self.assertEqual(written["timestamp"], "2026-07-18T12:30:00")
            self.assertEqual(written["summary"]["total_units"], 1286)


if __name__ == "__main__":
    unittest.main()
