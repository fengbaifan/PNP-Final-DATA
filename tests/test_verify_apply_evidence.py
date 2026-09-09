import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import verify_apply_evidence as verifier
from _runtime_state import RuntimeState, check_resumable


def test_extract_frontmatter_accepts_utf8_bom():
    text = "\ufeff---\ntitle: Example\nconfidence: medium\n---\n\nBody\n"

    frontmatter = verifier.extract_frontmatter(text)

    assert "title: Example" in frontmatter
    assert verifier.scalar_fm(frontmatter, "confidence") == "medium"


def test_null_run_state_does_not_persist_progress():
    state = verifier.NullRunState()

    state.track_progress(1, "example", True)

    assert state.get_processed_items() == set()
    assert state.get_progress_index() == -1


def evidence_entry(ku_path: str) -> dict:
    return {
        "evidence_id": "ev-test-1",
        "ku_path": ku_path,
        "platform": "Test archive",
        "source_type": "archive",
        "source_authority": "primary",
        "source_independence_group": "test-archive",
        "claim_scope": "entity_identity_only",
        "claim_target": "identity",
        "match_quality": "strong",
        "match_score": 1.0,
        "recommended_changes": {
            "evidence_status": "partially_verified",
            "verification_level": "L3",
            "confidence": "medium",
            "consensus": "tentative",
        },
    }


def ku_text() -> str:
    return (
        "---\n"
        "title: Example\n"
        "confidence: medium\n"
        "consensus: tentative\n"
        "evidence_status: source_backed\n"
        "verification_level: L7\n"
        "last_verified: 2026-01-01\n"
        "updated: 2026-01-01\n"
        "version: 1\n"
        "---\n\n"
        "Body\n"
    )


def test_verification_update_stays_in_third_part_and_preserves_neighbors():
    text = ku_text().replace("Body\n", (
        "## 内容\n\n### 描述\nChinese and English description.\n\n"
        "## 关系与证据\n\n### 关系\nExisting relation.\n\n"
        "### 验证状态\nOld status.\n\n### 待补与争议\nKeep this gap.\n\n"
        "## 附录\nKeep this appendix.\n"
    ))
    result, outcome, _ = verifier._render_entry(evidence_entry("unused.md"), text)
    assert outcome == "applied"
    assert result is not None
    assert "\n## 验证状态\n" not in result
    assert result.count("### 验证状态\n") == 1
    assert "Old status." not in result
    assert "Existing relation." in result and "Keep this gap." in result
    assert "Keep this appendix." in result
    assert result.index("### 验证状态") < result.index("### 待补与争议") < result.index("## 附录")


def test_legacy_verification_migrates_without_creating_a_version_counter():
    text = ku_text().replace("version: 1\n", "").replace("Body\n", (
        "## 内容\nKeep content.\n\n## 验证状态\nOld status.\n\n"
        "## 关系与证据\n### 待补与争议\nKeep gap.\n"
    ))
    result, _, _ = verifier._render_entry(evidence_entry("unused.md"), text)
    assert result is not None
    assert verifier.scalar_fm(verifier.extract_frontmatter(result), "version") == ""
    assert result.count("## 关系与证据\n") == 1
    assert result.count("### 验证状态\n") == 1
    assert "\n## 验证状态\n" not in result and "Old status." not in result
    assert "Keep content." in result and "Keep gap." in result


def test_duplicate_evidence_sections_block_without_rewriting():
    text = ku_text() + "\n## 关系与证据\nA\n## 关系与证据\nB\n"
    result, outcome, detail = verifier._render_entry(evidence_entry("unused.md"), text)
    assert result is None and outcome == "blocked"
    assert "ambiguous duplicate" in detail


def test_runtime_state_rejects_resume_after_input_change():
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "runner-state.json"
        RuntimeState(
            state_path=state_path,
            batch_id="batch-test",
            input_fingerprint="sha256:one",
        )

        try:
            check_resumable(
                state_path,
                expected_input_fingerprint="sha256:two",
            )
        except ValueError as exc:
            assert "fingerprint mismatch" in str(exc)
        else:
            raise AssertionError("changed input must reject resume")


def test_apply_is_atomic_and_records_truthful_completed_state(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ku = root / "04-knowledge" / "units" / "terms" / "example.md"
        ku.parent.mkdir(parents=True)
        ku.write_text(ku_text(), encoding="utf-8")
        evidence = root / "evidence.jsonl"
        evidence.write_text(
            json.dumps(evidence_entry("04-knowledge/units/terms/example.md")) + "\n",
            encoding="utf-8",
        )
        state_path = root / "06-runtime" / "automation" / "batch-test" / "runner-state.json"
        log_path = root / "04-knowledge" / "quality" / "verification-log.md"
        monkeypatch.setattr(verifier, "BASE", root)
        monkeypatch.setattr(verifier, "VERIFICATION_LOG", log_path)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "verify_apply_evidence.py",
                "--apply",
                "--state-file",
                str(state_path),
                "--batch-id",
                "batch-test",
                str(evidence),
            ],
        )

        result = verifier.main()
        state = json.loads(state_path.read_text(encoding="utf-8"))

        assert result == 0
        assert state["status"] == "completed"
        assert state["input_fingerprint"].startswith("sha256:")
        assert "partially_verified" in ku.read_text(encoding="utf-8")
        assert "ev-test-1" in log_path.read_text(encoding="utf-8")
        assert not list(root.rglob("*.bak"))


def test_blocked_batch_writes_no_knowledge_and_marks_blocked(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ku = root / "04-knowledge" / "units" / "terms" / "example.md"
        ku.parent.mkdir(parents=True)
        original = ku_text()
        ku.write_text(original, encoding="utf-8")
        entry = evidence_entry("04-knowledge/units/terms/example.md")
        entry["blocking_reason"] = "identity conflict"
        evidence = root / "evidence.jsonl"
        evidence.write_text(json.dumps(entry) + "\n", encoding="utf-8")
        state_path = root / "06-runtime" / "automation" / "batch-test" / "runner-state.json"
        monkeypatch.setattr(verifier, "BASE", root)
        monkeypatch.setattr(
            verifier,
            "VERIFICATION_LOG",
            root / "04-knowledge" / "quality" / "verification-log.md",
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "verify_apply_evidence.py",
                "--apply",
                "--state-file",
                str(state_path),
                str(evidence),
            ],
        )

        result = verifier.main()
        state = json.loads(state_path.read_text(encoding="utf-8"))

        assert result == 1
        assert state["status"] == "blocked"
        assert ku.read_text(encoding="utf-8") == original
        assert not verifier.VERIFICATION_LOG.exists()
