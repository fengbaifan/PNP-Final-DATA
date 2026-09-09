import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_processing_package as validator
from scripts._source_fingerprint import FINGERPRINT_MODE, aggregate_input_fingerprint, source_sha256


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def source_contract(root: Path, source: Path, *, omissions: int = 0) -> dict:
    rel = source.relative_to(root).as_posix()
    assets = [{"path": rel, "sha256": source_sha256(source), "role": "primary_text"}]
    fingerprint = aggregate_input_fingerprint(assets)
    return {
        "fingerprint_mode": FINGERPRINT_MODE,
        "source_assets": assets,
        "processing_scope": {"mode": "full_asset", "assets": [rel]},
        "input_fingerprint": fingerprint,
        "semantic_acceptance": {
            "reread_status": "accepted_with_findings" if omissions else "accepted",
            "reviewer_kind": "agent",
            "reviewer_id": "test-agent",
            "reviewed_at": "2026-08-02T00:00:00Z",
            "source_version": fingerprint,
            "omission_count": omissions,
            "acceptance_boundary": "test semantic boundary",
        },
    }


class CompactProcessingPackageTests(unittest.TestCase):
    def test_source_fingerprint_ignores_checkout_line_endings_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.md"
            source.write_bytes(b"alpha\r\nbeta\r\n")
            crlf_hash = source_sha256(source)
            source.write_bytes(b"alpha\nbeta\n")
            lf_hash = source_sha256(source)
            source.write_bytes(b"\xef\xbb\xbfalpha\nbeta\n")
            bom_hash = source_sha256(source)

        self.assertEqual(crlf_hash, lf_hash)
        self.assertNotEqual(lf_hash, bom_hash)

    def test_complete_compact_package_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "02-sources" / "example" / "original.md"
            source.parent.mkdir(parents=True)
            source.write_text("source\n", encoding="utf-8")
            package = root / "03-processing" / "example"
            package.mkdir(parents=True)
            (package / "source-map.jsonl").write_text(
                json.dumps({
                    "block_id": "b001",
                    "source_file": "02-sources/example/original.md",
                    "line_start": 1,
                    "line_end": 1,
                    "read_status": "read",
                    "semantic_unit_refs": ["su001"],
                    "candidate_refs": [],
                    "no_candidate_reason": "scope contains no durable candidate",
                }) + "\n",
                encoding="utf-8",
            )
            (package / "semantic-units.jsonl").write_text(
                json.dumps({"semantic_unit_id": "su001", "source_block_refs": ["b001"]}) + "\n",
                encoding="utf-8",
            )
            (package / "candidate-ledger.jsonl").write_text("", encoding="utf-8")
            (package / "summary.md").write_text("# Summary\n", encoding="utf-8")
            manifest = {
                "processing_profile": "compact-v4",
                "status": "completed",
                **source_contract(root, source),
                "coverage": {
                    "source_blocks_total": 1,
                    "source_blocks_reviewed": 1,
                    "unread_blocks": 0,
                    "blocks_without_candidate_review": 0,
                    "scope_assets_total": 1,
                    "scope_assets_reviewed": 1,
                    "scope_lines_total": 1,
                    "scope_lines_reviewed": 1,
                },
                "output_hashes": {name: digest(package / name) for name in validator.LOGICAL_FILES},
            }
            (package / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            issues = validator.compact_package_issues(package, root=root)
            manifest.pop("semantic_acceptance")
            (package / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            missing_acceptance_issues = validator.compact_package_issues(package, root=root)

        self.assertEqual(issues, [])
        self.assertIn("completed package requires semantic_acceptance", missing_acceptance_issues)

    def test_completed_package_fails_on_unreviewed_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "03-processing" / "example"
            package.mkdir(parents=True)
            for name in validator.LOGICAL_FILES:
                (package / name).write_text("" if name.endswith("jsonl") else "# Summary\n", encoding="utf-8")
            source = root / "missing.md"
            source.write_text("source\n", encoding="utf-8")
            (package / "source-map.jsonl").write_text(
                json.dumps({"block_id": "b001", "source_file": "missing.md", "line_start": 1, "line_end": 1, "read_status": "needs_review"}) + "\n",
                encoding="utf-8",
            )
            (package / "manifest.json").write_text(json.dumps({
                "processing_profile": "compact-v4",
                "status": "completed",
                **source_contract(root, source),
                "coverage": {
                    "source_blocks_total": 1,
                    "source_blocks_reviewed": 0,
                    "unread_blocks": 1,
                    "blocks_without_candidate_review": 1,
                    "scope_assets_total": 1,
                    "scope_assets_reviewed": 1,
                    "scope_lines_total": 1,
                    "scope_lines_reviewed": 1,
                },
                "output_hashes": {name: digest(package / name) for name in validator.LOGICAL_FILES},
            }), encoding="utf-8")

            issues = validator.compact_package_issues(package, root=root)

        self.assertIn("completed package has unresolved coverage gaps", issues)

    def test_candidate_requires_existing_knowledge_screening(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "02-sources" / "example" / "original.md"
            source.parent.mkdir(parents=True)
            source.write_text("source\n", encoding="utf-8")
            package = root / "03-processing" / "example"
            package.mkdir(parents=True)
            candidate = {
                "candidate_id": "cand-1",
                "origin_type": "source",
                "origin_ref": "su001",
                "candidate_type": "unit",
                "payload": {},
                "evidence_refs": [],
                "state": "candidate",
                "decision": {"status": "pending"},
                "created_at": "2026-08-01T00:00:00Z",
                "updated_at": "2026-08-01T00:00:00Z",
            }
            (package / "source-map.jsonl").write_text(json.dumps({
                "block_id": "b001",
                "source_file": "02-sources/example/original.md",
                "line_start": 1,
                "line_end": 1,
                "read_status": "read",
                "semantic_unit_refs": ["su001"],
                "candidate_refs": ["cand-1"],
            }) + "\n", encoding="utf-8")
            (package / "semantic-units.jsonl").write_text(
                json.dumps({"semantic_unit_id": "su001", "source_block_refs": ["b001"]}) + "\n",
                encoding="utf-8",
            )
            (package / "candidate-ledger.jsonl").write_text(json.dumps(candidate) + "\n", encoding="utf-8")
            (package / "summary.md").write_text("# Summary\n", encoding="utf-8")
            (package / "manifest.json").write_text(json.dumps({
                "processing_profile": "compact-v4",
                "status": "completed",
                **source_contract(root, source),
                "coverage": {
                    "source_blocks_total": 1,
                    "source_blocks_reviewed": 1,
                    "unread_blocks": 0,
                    "blocks_without_candidate_review": 0,
                    "scope_assets_total": 1,
                    "scope_assets_reviewed": 1,
                    "scope_lines_total": 1,
                    "scope_lines_reviewed": 1,
                },
                "output_hashes": {name: digest(package / name) for name in validator.LOGICAL_FILES},
            }), encoding="utf-8")

            issues = validator.compact_package_issues(package, root=root)

        self.assertIn("candidate cand-1: payload.knowledge_match is required", issues)

    def test_source_hash_change_reopens_completed_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "02-sources" / "example" / "original.md"
            source.parent.mkdir(parents=True)
            source.write_text("version one\n", encoding="utf-8")
            package = root / "03-processing" / "example"
            package.mkdir(parents=True)
            (package / "source-map.jsonl").write_text(json.dumps({
                "block_id": "b001", "source_file": "02-sources/example/original.md",
                "line_start": 1, "line_end": 1, "read_status": "read",
                "semantic_unit_refs": ["su001"], "candidate_refs": [],
                "no_candidate_reason": "no durable candidate",
            }) + "\n", encoding="utf-8")
            (package / "semantic-units.jsonl").write_text(
                json.dumps({"semantic_unit_id": "su001", "source_block_refs": ["b001"]}) + "\n",
                encoding="utf-8",
            )
            (package / "candidate-ledger.jsonl").write_text("", encoding="utf-8")
            (package / "summary.md").write_text("# Summary\n", encoding="utf-8")
            manifest = {
                "processing_profile": "compact-v4", "status": "completed",
                **source_contract(root, source),
                "coverage": {
                    "source_blocks_total": 1,
                    "source_blocks_reviewed": 1,
                    "unread_blocks": 0,
                    "blocks_without_candidate_review": 0,
                    "scope_assets_total": 1,
                    "scope_assets_reviewed": 1,
                    "scope_lines_total": 1,
                    "scope_lines_reviewed": 1,
                },
                "output_hashes": {name: digest(package / name) for name in validator.LOGICAL_FILES},
            }
            (package / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            source.write_text("version two\n", encoding="utf-8")

            state = validator.package_source_state(package, root=root)
            issues = validator.compact_package_issues(package, root=root)

        self.assertEqual(state["effective_status"], "reopened_source_drift")
        self.assertIn("source asset hash drift: 02-sources/example/original.md", issues)
        self.assertIn("effective_status=reopened_source_drift", issues)

    def test_completed_package_fails_when_source_map_has_a_line_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "02-sources" / "example" / "original.md"
            source.parent.mkdir(parents=True)
            source.write_text("one\ntwo\nthree\n", encoding="utf-8")
            package = root / "03-processing" / "example"
            package.mkdir(parents=True)
            rows = [
                {
                    "block_id": "b001",
                    "source_file": source.relative_to(root).as_posix(),
                    "line_start": 1,
                    "line_end": 1,
                    "read_status": "read",
                    "semantic_unit_refs": [],
                    "candidate_refs": [],
                    "no_candidate_reason": "none",
                },
                {
                    "block_id": "b002",
                    "source_file": source.relative_to(root).as_posix(),
                    "line_start": 3,
                    "line_end": 3,
                    "read_status": "read",
                    "semantic_unit_refs": [],
                    "candidate_refs": [],
                    "no_candidate_reason": "none",
                },
            ]
            (package / "source-map.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows),
                encoding="utf-8",
            )
            (package / "semantic-units.jsonl").write_text("", encoding="utf-8")
            (package / "candidate-ledger.jsonl").write_text("", encoding="utf-8")
            (package / "summary.md").write_text("# Summary\n", encoding="utf-8")
            manifest = {
                "processing_profile": "compact-v4",
                "status": "completed",
                **source_contract(root, source),
                "coverage": {
                    "source_blocks_total": 2,
                    "source_blocks_reviewed": 2,
                    "unread_blocks": 0,
                    "blocks_without_candidate_review": 0,
                    "scope_assets_total": 1,
                    "scope_assets_reviewed": 0,
                    "scope_lines_total": 3,
                    "scope_lines_reviewed": 2,
                },
                "output_hashes": {
                    name: digest(package / name) for name in validator.LOGICAL_FILES
                },
            }
            (package / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            issues = validator.compact_package_issues(package, root=root)

        self.assertTrue(any("uncovered lines" in issue for issue in issues))
