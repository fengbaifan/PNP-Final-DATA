"""Verify a workflow archive or an unchanged extracted workflow, read-only.

Usage: python verify_copy.py knowledge-distillation-workflow.zip
       python portable/verify_copy.py .
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile


def check(target: Path) -> dict:
    issues = []
    archive = zipfile.ZipFile(target) if target.is_file() else None
    try:
        if archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                issues.append("duplicate ZIP members")
            for name in names:
                path = PurePosixPath(name)
                if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
                    issues.append("unsafe ZIP path: " + name)
            if issues:
                return {"passed": False, "issues": issues}
            corrupt = archive.testzip()
            if corrupt:
                issues.append("ZIP CRC failure: " + corrupt)
            read = archive.read
        else:
            root = target.resolve()

            def read(name: str) -> bytes:
                path = (root / name).resolve()
                if not path.is_relative_to(root):
                    raise ValueError("Path escapes extracted root: " + name)
                return path.read_bytes()

        manifest = json.loads(read("workflow-copy-manifest.json"))
        declared = [entry["path"] for entry in manifest["files"]]
        if len(declared) != len(set(declared)):
            issues.append("duplicate manifest entries")
        if archive and set(names) != set(declared) | {"workflow-copy-manifest.json"}:
            issues.append("ZIP members differ from manifest")
        for entry in manifest["files"]:
            name = entry["path"]
            try:
                data = read(name)
                if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                    issues.append("hash/size mismatch: " + name)
            except (OSError, KeyError, ValueError) as exc:
                issues.append(f"{name}: {exc}")
        return {"passed": not issues, "checked_files": len(declared),
                "skill_count": manifest["skill_count"], "issues": issues}
    finally:
        if archive:
            archive.close()


if __name__ == "__main__":
    result = check(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
