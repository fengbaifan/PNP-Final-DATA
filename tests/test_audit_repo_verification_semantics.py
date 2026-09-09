import tempfile
import unittest
from pathlib import Path

from scripts.audit_repo import verification_semantic_issues


def write_unit(root: Path, slug: str, source_count: int) -> Path:
    path = root / "04-knowledge" / "units" / "persons" / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                "confidence: medium",
                "consensus: tentative",
                f"source_count: {source_count}",
                "evidence_status: externally_verified",
                "verification_level: L6",
                "---",
                "## 验证状态",
                "- **证据范围**: entity_identity_only",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


class VerificationSemanticIssueTests(unittest.TestCase):
    def test_multi_source_limited_scope_is_not_external_overreach(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_unit(root, "multi-source", source_count=2)

            result = verification_semantic_issues([path], root)

        self.assertEqual(result["identity_only_external_overreach"], [])

    def test_single_source_limited_scope_remains_external_overreach(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_unit(root, "single-source", source_count=1)

            result = verification_semantic_issues([path], root)

        self.assertEqual(
            result["identity_only_external_overreach"],
            ["04-knowledge/units/persons/single-source.md"],
        )


if __name__ == "__main__":
    unittest.main()
