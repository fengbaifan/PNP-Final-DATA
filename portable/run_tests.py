"""Run the unchanged source tests with isolated synthetic structural fixtures.

Five source tests depend on named structure nodes and at least one attached KU.
This runner supplies only that filesystem contract in a disposable clone. It
does not mock implementation functions, alter assertions or seed real knowledge.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if not (root / "workflow-copy-manifest.json").is_file():
        raise SystemExit("Run the copy inside the extracted package: python portable/run_tests.py")
    manifest = json.loads((root / "workflow-copy-manifest.json").read_text(encoding="utf-8"))
    fixture_texts = {
        "04-knowledge/structure/themes/b2-geometric-quantitative-encoding.md":
            "---\nnode_type: theme\ntheme_code: B.2\n---\n# Synthetic test fixture\n",
        "04-knowledge/structure/themes/c6-twentieth-century-visualization.md":
            "---\nnode_type: theme\ntheme_code: C.6\n---\n# Synthetic test fixture\n",
        "04-knowledge/structure/topics/visualization-as-reform-tool.md":
            "---\nnode_type: topic\n---\n# Synthetic test fixture\n",
        "04-knowledge/structure/topics/visualization-and-governance.md":
            "---\nnode_type: topic\n---\n# Synthetic test fixture\n",
        "04-knowledge/units/works/portable-test-example.md":
            "---\ntitle: Synthetic test object\nname_en: Synthetic test object\ntype: work\n"
            "primary_theme: B.2\nrole_in_theme: representative_work\n"
            "topic_memberships:\n  - topic: topics/visualization-as-reform-tool.md\n"
            "    role: representative_work\n    primary: true\n"
            "confidence: medium\nconsensus: tentative\nsource_count: 0\n"
            "sources: []\nrelations: []\n---\n## Description\nSynthetic test fixture only.\n",
    }
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    with tempfile.TemporaryDirectory(prefix="ikd-workflow-tests-") as temp:
        sandbox = Path(temp)
        for entry in manifest["files"]:
            rel = entry["path"]
            source = (root / rel).resolve()
            destination = (sandbox / rel).resolve()
            if not source.is_relative_to(root) or not destination.is_relative_to(sandbox):
                raise ValueError("Manifest path escapes package: " + rel)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        for rel, body in fixture_texts.items():
            destination = sandbox / rel
            if destination.exists():
                raise ValueError("Fixture would overwrite package content: " + rel)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(body, encoding="utf-8")
        print("Running all unchanged tests with 5 synthetic fixtures in a disposable directory.", flush=True)
        return subprocess.run([sys.executable, "-B", "-m", "pytest", "tests", "-p", "no:cacheprovider"],
                              cwd=sandbox, env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
