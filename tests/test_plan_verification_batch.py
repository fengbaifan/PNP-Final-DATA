import unittest
from collections import Counter

from scripts import plan_verification_batch as planner


def queue_row(unit: str, *, degree_status: str = "source_backed", confidence: str = "medium") -> dict:
    return {
        "unit": f"04-knowledge/units/terms/{unit}.md",
        "title": unit,
        "type": "terms",
        "priority": "P2",
        "reasons": ["single_source", "tentative_or_missing_consensus"],
        "status_conflicts": [],
        "source_family": "test",
        "source_count": 1,
        "confidence": confidence,
        "consensus": "tentative",
        "evidence_status": degree_status,
    }


class PlanVerificationBatchTests(unittest.TestCase):
    def test_eligibility_requires_single_source_and_tentative(self):
        row = queue_row("eligible")
        self.assertTrue(planner.eligible(row))
        row["reasons"] = ["single_source"]
        self.assertFalse(planner.eligible(row))

    def test_selection_prioritizes_low_confidence_then_active_then_degree(self):
        rows = [
            queue_row("degree"),
            queue_row("active"),
            queue_row("low", confidence="low"),
        ]
        degrees = Counter(
            {
                rows[0]["unit"]: 100,
                rows[1]["unit"]: 10,
                rows[2]["unit"]: 1,
            }
        )
        selected = planner.select_targets(rows, degrees, {rows[1]["unit"]}, 3, 40)
        self.assertEqual([row["title"] for row in selected], ["low", "active", "degree"])

    def test_selection_assigns_recoverable_checkpoints(self):
        rows = [queue_row(f"u-{index:03d}") for index in range(120)]
        selected = planner.select_targets(rows, Counter(), set(), 120, 40)
        self.assertEqual(selected[0]["checkpoint"], 1)
        self.assertEqual(selected[39]["checkpoint"], 1)
        self.assertEqual(selected[40]["checkpoint"], 2)
        self.assertEqual(selected[-1]["checkpoint"], 3)
        self.assertEqual(planner.checkpoint_summary(selected)[-1]["target_count"], 40)

    def test_selection_respects_explicit_unit_type_scope(self):
        person = queue_row("person")
        person["unit"] = "04-knowledge/units/persons/person.md"
        person["type"] = "persons"
        term = queue_row("term")
        selected = planner.select_targets(
            [term, person], Counter(), set(), 1, 40, {"persons", "institutions"}
        )
        self.assertEqual([row["type"] for row in selected], ["persons"])

    def test_full_unit_path_excludes_structure_nodes(self):
        self.assertEqual(
            planner.full_unit_path("persons/example.md"),
            "04-knowledge/units/persons/example.md",
        )
        self.assertIsNone(planner.full_unit_path("structure/topics/example.md"))


if __name__ == "__main__":
    unittest.main()
