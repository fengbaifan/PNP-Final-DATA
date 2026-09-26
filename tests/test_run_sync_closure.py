import unittest

from scripts import build_generated_projection_manifest, run_sync_closure


class SyncClosureTests(unittest.TestCase):
    def test_default_steps_are_read_only_and_skip_pytest(self):
        steps = run_sync_closure.build_steps(full=False, changed_paths=["README.md"])
        names = [step.name for step in steps]

        self.assertNotIn("build relation index", names)
        self.assertNotIn("write health and backlog", names)
        self.assertNotIn("audit repository", names)
        self.assertNotIn("run tests", names)
        self.assertIn("validate skill registry", names)

    def test_full_steps_include_tests_and_system_upgrade_audit(self):
        steps = run_sync_closure.build_steps(full=True, changed_paths=[])
        names = [step.name for step in steps]

        self.assertIn("audit content quality", names)
        self.assertIn("audit relation consistency", names)
        self.assertIn("audit repository", names)
        self.assertIn("audit structured tables", names)
        self.assertIn("audit system upgrade chain", names)
        self.assertIn("run tests", names)

    def test_refresh_generated_runs_builders_before_audits(self):
        steps = run_sync_closure.build_steps(full=False, refresh_generated=True, changed_paths=[])
        names = [step.name for step in steps]

        self.assertLess(names.index("build translation index"), names.index("audit content quality"))
        self.assertNotIn("build relation candidates", names)
        self.assertFalse(any("plan_relation_candidates.py" in " ".join(step.command) for step in steps))
        self.assertLess(names.index("build translation index"), names.index("write health and backlog"))
        self.assertNotIn("build knowledge graph data", names)
        self.assertGreater(
            names.index("build generated projection manifest"),
            names.index("write health and backlog"),
        )

    def test_page_projection_requires_explicit_refresh(self):
        steps = run_sync_closure.build_steps(
            full=False,
            refresh_generated=True,
            refresh_page=True,
            changed_paths=[],
        )
        names = [step.name for step in steps]

        self.assertIn("build knowledge graph data", names)
        self.assertLess(names.index("build knowledge graph data"), names.index("audit repository"))

    def test_generated_check_covers_all_declared_snapshots(self):
        steps = run_sync_closure.build_steps(
            full=False,
            check_generated=True,
            refresh_generated=True,
            changed_paths=[],
        )

        self.assertIn(
            ["git", "diff", "--exit-code", "HEAD", "--", *run_sync_closure.GENERATED_PATHS],
            [step.command for step in steps],
        )

        page_steps = run_sync_closure.build_steps(
            full=False,
            check_generated=True,
            refresh_generated=True,
            refresh_page=True,
            changed_paths=[],
        )
        self.assertIn(
            [
                "git",
                "diff",
                "--exit-code",
                "HEAD",
                "--",
                *run_sync_closure.GENERATED_PATHS,
                *run_sync_closure.PAGE_GENERATED_PATHS,
            ],
            [step.command for step in page_steps],
        )

    def test_relation_index_and_candidates_have_distinct_generators(self):
        specs = {spec["name"]: spec for spec in build_generated_projection_manifest.PROJECTIONS}

        self.assertNotIn("relation_index", specs)
        self.assertIn("04-knowledge/tables/relations.csv", specs["relation_candidates"]["inputs"])
        self.assertEqual(specs["relation_candidates"]["generator"], "scripts/plan_relation_candidates.py")
        self.assertIn("04-knowledge/structure/**/*.md", specs["relation_candidates"]["inputs"])
        self.assertEqual(
            specs["relation_candidates"]["outputs"],
            ("04-knowledge/quality/relation-candidates.yml",),
        )

    def test_execute_steps_stops_after_first_failure(self):
        called = []

        def fake_run(command):
            called.append(command)
            return 1 if len(called) == 2 else 0

        steps = [
            run_sync_closure.Step("first", ["first"]),
            run_sync_closure.Step("second", ["second"]),
            run_sync_closure.Step("third", ["third"]),
        ]

        result = run_sync_closure.execute_steps(steps, runner=fake_run)

        self.assertEqual(result, 1)
        self.assertEqual(called, [["first"], ["second"]])

    def test_knowledge_change_routes_to_all_semantic_mechanical_audits(self):
        steps = run_sync_closure.build_steps(
            full=False,
            changed_paths=["04-knowledge/units/terms/example.md"],
        )

        names = [step.name for step in steps]
        self.assertIn("audit content quality", names)
        self.assertIn("audit relation consistency", names)
        self.assertIn("audit repository", names)

    def test_processing_change_routes_only_repository_audit(self):
        steps = run_sync_closure.build_steps(
            full=False,
            changed_paths=["03-processing/example/manifest.json"],
        )

        names = [step.name for step in steps]
        self.assertNotIn("audit content quality", names)
        self.assertNotIn("audit relation consistency", names)
        self.assertIn("audit repository", names)

    def test_table_and_release_changes_route_structured_data_audit(self):
        for path in ["04-knowledge/tables/relations.csv", "release/v0.2-draft/metadata.json"]:
            with self.subTest(path=path):
                steps = run_sync_closure.build_steps(full=False, changed_paths=[path])
                names = [step.name for step in steps]
                self.assertIn("audit structured tables", names)
                if path.endswith("relations.csv"):
                    self.assertIn("audit relation consistency", names)


if __name__ == "__main__":
    unittest.main()
