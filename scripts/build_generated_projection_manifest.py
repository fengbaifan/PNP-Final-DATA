#!/usr/bin/env python3
"""Build deterministic provenance for repository-level generated projections."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
OUTPUT = BASE / "06-runtime" / "state" / "generated-projections-manifest.json"

PROJECTIONS = (
    {
        "name": "relation_candidates",
        "generator": "scripts/plan_relation_candidates.py",
        "inputs": (
            "04-knowledge/units/**/*.md",
            "04-knowledge/structure/**/*.md",
            "04-knowledge/quality/claim-registry.yml",
            "04-knowledge/tables/relations.csv",
        ),
        "outputs": ("04-knowledge/quality/relation-candidates.yml",),
    },
    {
        "name": "translation",
        "generator": "scripts/build_translation_index.py",
        "inputs": ("04-knowledge/units/**/*.md", "01-domain/naming-conventions.md"),
        "outputs": ("04-knowledge/quality/translation-index.yml",),
    },
    {
        "name": "knowledge_graph",
        "generator": "scripts/build_knowledge_graph_data.py",
        "inputs": ("04-knowledge/accepted.yml", "04-knowledge/units/**/*.md", "04-knowledge/structure/**/*.md", "04-knowledge/tables/relations.csv"),
        "outputs": ("05-outputs/knowledge-graph-data.json", "05-outputs/knowledge-graph-data.js"),
    },
    {
        "name": "discovery_index",
        "generator": "scripts/build_discovery_index.py",
        "inputs": ("04-knowledge/quality/relation-candidates.yml", "03-processing/**/candidate-ledger.jsonl", "06-runtime/automation/**/candidate-ledger.jsonl"),
        "outputs": ("06-runtime/state/candidate-index.jsonl", "06-runtime/state/discovery-manifest.json"),
    },
    {
        "name": "output_gallery",
        "generator": "scripts/build_output_gallery.py",
        "inputs": ("05-outputs/**/*",),
        "outputs": ("05-outputs/index/output-gallery.md",),
    },
    {
        "name": "output_navigation",
        "generator": "scripts/build_output_gallery.py",
        "inputs": ("04-knowledge/accepted.yml", "04-knowledge/units/**/*.md", "06-runtime/state/current-health.json"),
        "outputs": ("05-outputs/index/index.md", "05-outputs/index/persons.md", "05-outputs/index/institutions.md", "05-outputs/index/places.md", "05-outputs/index/works.md", "05-outputs/index/archives.md", "05-outputs/index/terms.md", "05-outputs/index/procedures.md", "05-outputs/index/events.md"),
    },
    {
        "name": "runtime_index",
        "generator": "scripts/build_runtime_index.py",
        "inputs": ("06-runtime/automation/**/*",),
        "outputs": ("06-runtime/automation/index.md",),
    },
    {
        "name": "skill_registry",
        "generator": "scripts/skill_registry.py",
        "inputs": (".agents/skills/**/SKILL.md", ".agents/skills/**/references/*.md"),
        "outputs": ("06-runtime/state/skill-registry.json",),
    },
    {
        "name": "health_and_backlog",
        "generator": "scripts/write_current_health.py",
        "inputs": ("04-knowledge/accepted.yml", "04-knowledge/units/**/*.md", "03-processing/**/*", "04-knowledge/quality/**/*"),
        "outputs": ("06-runtime/state/current-health.json", "06-runtime/governance/governance-backlog.md"),
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def expanded_files(patterns: tuple[str, ...]) -> list[Path]:
    files: set[Path] = set()
    for pattern in patterns:
        files.update(path for path in BASE.glob(pattern) if path.is_file() and path != OUTPUT)
    return sorted(files, key=lambda path: path.relative_to(BASE).as_posix())


def input_set(patterns: tuple[str, ...], excluded: set[Path] | None = None) -> dict:
    files = [path for path in expanded_files(patterns) if path not in (excluded or set())]
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(BASE).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256(path).encode("ascii"))
        digest.update(b"\n")
    return {"patterns": list(patterns), "files": len(files), "digest": f"sha256:{digest.hexdigest()}"}


def ku_state_summary() -> dict:
    units = expanded_files(("04-knowledge/units/**/*.md",))
    digest = hashlib.sha256()
    for path in units:
        digest.update(path.relative_to(BASE).as_posix().encode("utf-8"))
        digest.update(sha256(path).encode("ascii"))
    return {"units": len(units), "digest": f"sha256:{digest.hexdigest()}"}


def build_manifest() -> dict:
    records = []
    for spec in PROJECTIONS:
        generator = BASE / spec["generator"]
        outputs = [BASE / path for path in spec["outputs"]]
        missing = [path.relative_to(BASE).as_posix() for path in outputs if not path.is_file()]
        records.append({
            "name": spec["name"],
            "status": "rebuildable" if not missing else "review_required",
            "generator": spec["generator"],
            "generator_hash": f"sha256:{sha256(generator)}" if generator.is_file() else None,
            "parameters": [],
            "effective_inputs": input_set(spec["inputs"], set(outputs)),
            "outputs": {
                path.relative_to(BASE).as_posix(): f"sha256:{sha256(path)}"
                for path in outputs if path.is_file()
            },
            "missing_outputs": missing,
        })
    return {
        "schema_version": "1.0",
        "manifest_kind": "generated_projection_provenance",
        "ku_state": ku_state_summary(),
        "projections": records,
    }


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build_manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote={OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
