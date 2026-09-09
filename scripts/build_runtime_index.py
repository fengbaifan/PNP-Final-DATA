#!/usr/bin/env python3
"""Build a compact navigation index for runtime automation artifacts."""
from __future__ import annotations

import argparse
from collections import Counter
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re


BASE = Path(__file__).resolve().parents[1]
THEMES = ("relation", "claim", "rendgen", "lima", "isolated", "other")
DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})")
BATCH_SUFFIX = re.compile(r"batch-(\d+)$")
DEFAULT_LARGE_FILE_THRESHOLD = 512 * 1024
TEXT_ARTIFACT_SUFFIXES = {".csv", ".diff", ".json", ".jsonl", ".log", ".md", ".txt", ".yaml", ".yml"}
R2_REVIEW_MARKERS = (
    "current-window",
    "statistics",
    "metrics",
)


def classify_batch(name: str) -> str:
    lowered = name.lower()
    for theme in THEMES[:-1]:
        if theme in lowered:
            return theme
    return "other"


def find_summary(batch_dir: Path) -> Path | None:
    for name in ("summary.md", "defer_ledger_summary.md"):
        candidate = batch_dir / name
        if candidate.exists():
            return candidate
    return None


def relative_link(root: Path, path: Path) -> str:
    return path.relative_to(root / "06-runtime" / "automation").as_posix()


def batch_sort_key(path: Path) -> tuple[str, int, str]:
    name = path.name
    date_match = DATE_PREFIX.match(name)
    batch_match = BATCH_SUFFIX.search(name)
    return (
        date_match.group(1) if date_match else "",
        int(batch_match.group(1)) if batch_match else -1,
        name,
    )


def is_ephemeral_runtime_path(path: Path) -> bool:
    return (
        path.name == ".DS_Store"
        or path.suffix in {".bak", ".pyc", ".pyo", ".tmp", ".temp"}
        or "__pycache__" in path.parts
        or any(part.endswith(".egg-info") for part in path.parts)
    )


def canonical_artifact_bytes(path: Path) -> bytes:
    """Return platform-stable bytes for text artifact inventory signals."""
    content = path.read_bytes()
    if path.suffix.lower() in TEXT_ARTIFACT_SUFFIXES:
        return content.replace(b"\r\n", b"\n")
    return content


def _normalized_digest(value: object) -> str:
    text = str(value or "").strip().lower()
    return text.removeprefix("sha256:")


def _is_sha256(value: object) -> bool:
    return re.fullmatch(r"[0-9a-f]{64}", _normalized_digest(value)) is not None


def _contains_sha256(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            (key == "sha256" and _is_sha256(item)) or _contains_sha256(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_sha256(item) for item in value)
    return False


def _manifest_records_required_provenance(data: dict) -> bool:
    """Accept the repository manifest contract, not filename-only hints."""
    generator = data.get("generator")
    generator_ok = (
        isinstance(generator, dict)
        and bool(generator.get("path"))
        and _is_sha256(generator.get("sha256"))
    )
    parameters_ok = (
        ("parameters" in data and isinstance(data["parameters"], (dict, list)))
        or ("invocation" in data and isinstance(data["invocation"], dict))
    )
    inputs = data.get("inputs")
    effective_inputs_ok = (
        isinstance(inputs, dict)
        and bool(inputs)
        and _contains_sha256(inputs)
    ) or _is_sha256(data.get("effective_input_digest"))
    ku_state = inputs.get("ku_state") if isinstance(inputs, dict) else None
    ku_state_ok = (
        isinstance(ku_state, dict) and _is_sha256(ku_state.get("sha256"))
    ) or _is_sha256(data.get("ku_state_digest"))
    return generator_ok and parameters_ok and effective_inputs_ok and ku_state_ok


def _declared_output_hashes(data: dict) -> list[tuple[str, object]]:
    declared: list[tuple[str, object]] = []
    output_hashes = data.get("output_hashes")
    if isinstance(output_hashes, dict):
        declared.extend((str(path), digest) for path, digest in output_hashes.items())

    outputs = data.get("outputs")
    if isinstance(outputs, dict):
        declared.extend((str(path), digest) for path, digest in outputs.items())
    elif isinstance(outputs, list):
        for item in outputs:
            if not isinstance(item, dict) or not item.get("path"):
                continue
            declared.append((str(item["path"]), item.get("sha256")))
    return declared


def _manifest_path_candidates(path: Path, manifest_directory: Path) -> set[str]:
    candidates = {path.name, path.relative_to(manifest_directory).as_posix()}
    automation_dir = next(
        (parent for parent in path.parents if parent.name == "automation"),
        None,
    )
    if automation_dir is not None and automation_dir.parent.name == "06-runtime":
        repository_root = automation_dir.parent.parent
        candidates.add(path.relative_to(repository_root).as_posix())
    return candidates


def artifact_has_valid_provenance_manifest(path: Path) -> bool:
    """Return true only when a nearby manifest declares this exact output and hash."""
    actual_digest: str | None = None
    for directory in path.parents:
        if directory.name == "automation":
            break
        for name in ("generation-manifest.json", "provenance-manifest.json"):
            manifest = directory / name
            if not manifest.is_file():
                continue
            try:
                data = json.loads(manifest.read_text(encoding="utf-8-sig"))
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(data, dict) or not _manifest_records_required_provenance(data):
                continue
            path_candidates = _manifest_path_candidates(path, directory)
            for declared_path, declared_digest in _declared_output_hashes(data):
                normalized_path = str(declared_path).replace("\\", "/").removeprefix("./")
                if normalized_path not in path_candidates:
                    continue
                if actual_digest is None:
                    actual_digest = hashlib.sha256(canonical_artifact_bytes(path)).hexdigest()
                if _normalized_digest(declared_digest) == actual_digest:
                    return True
    return False


def is_r2_review_candidate(path: Path) -> bool:
    """Recognize only narrow generated-state names; inventories and summaries remain R1."""
    lowered = path.name.lower()
    return any(marker in lowered for marker in R2_REVIEW_MARKERS)


def retention_tier(path: Path) -> str:
    """Classify proven projections as R2; unknown and unproven files remain R1."""
    if is_ephemeral_runtime_path(path):
        return "R3"
    if artifact_has_valid_provenance_manifest(path):
        return "R2"
    return "R1"


def build_retention_inventory(
    root: Path = BASE,
    large_file_threshold: int = DEFAULT_LARGE_FILE_THRESHOLD,
) -> dict:
    """Return read-only runtime capacity signals without retention decisions."""
    automation_dir = root / "06-runtime" / "automation"
    batch_dirs = sorted(path for path in automation_dir.iterdir() if path.is_dir()) if automation_dir.is_dir() else []
    files = sorted(
        path
        for path in automation_dir.rglob("*")
        if path.is_file() and path != automation_dir / "index.md"
    )
    hash_groups: dict[tuple[str, int], list[Path]] = defaultdict(list)
    large_files = []
    ephemeral_residue = []
    total_bytes = 0
    tier_counts: Counter[str] = Counter()
    tier_bytes: Counter[str] = Counter()
    r2_with_manifest = 0
    r2_without_manifest = 0

    for path in files:
        content = canonical_artifact_bytes(path)
        size = len(content)
        total_bytes += size
        relative = path.relative_to(automation_dir).as_posix()
        tier = retention_tier(path)
        tier_counts[tier] += 1
        tier_bytes[tier] += size
        if tier == "R2":
            r2_with_manifest += 1
        elif tier == "R1" and is_r2_review_candidate(path):
            r2_without_manifest += 1
        if size >= large_file_threshold:
            large_files.append({"path": relative, "bytes": size})
        if is_ephemeral_runtime_path(path):
            ephemeral_residue.append(relative)
        if size > 0:
            digest = hashlib.sha256(content).hexdigest()
            hash_groups[(digest, size)].append(path)

    duplicate_groups = []
    for (digest, size), paths in hash_groups.items():
        if len(paths) < 2:
            continue
        duplicate_groups.append(
            {
                "sha256": digest,
                "bytes_each": size,
                "potential_duplicate_bytes": size * (len(paths) - 1),
                "paths": [path.relative_to(automation_dir).as_posix() for path in paths],
            }
        )
    duplicate_groups.sort(
        key=lambda group: (-group["potential_duplicate_bytes"], group["paths"][0])
    )
    large_files.sort(key=lambda item: (-item["bytes"], item["path"]))

    return {
        "batch_directories": len(batch_dirs),
        "files": len(files),
        "total_bytes": total_bytes,
        "large_file_threshold_bytes": large_file_threshold,
        "large_files": large_files,
        "exact_duplicate_groups": len(duplicate_groups),
        "exact_duplicate_files": sum(len(group["paths"]) - 1 for group in duplicate_groups),
        "potential_duplicate_bytes": sum(
            group["potential_duplicate_bytes"] for group in duplicate_groups
        ),
        "duplicate_groups": duplicate_groups,
        "ephemeral_residue": sorted(ephemeral_residue),
        "retention_tiers": {
            tier: {"files": tier_counts[tier], "bytes": tier_bytes[tier]}
            for tier in ("R1", "R2", "R3")
        },
        "r2_provenance": {
            "with_manifest": r2_with_manifest,
            "review_required": r2_without_manifest,
        },
    }


def build_runtime_index(root: Path = BASE, recent_limit: int = 15) -> str:
    automation_dir = root / "06-runtime" / "automation"
    batch_dirs = sorted(
        (path for path in automation_dir.iterdir() if path.is_dir()),
        key=batch_sort_key,
    ) if automation_dir.is_dir() else []
    retention = build_retention_inventory(root)
    summaries = [(batch, find_summary(batch)) for batch in batch_dirs]
    summaries = [(batch, summary) for batch, summary in summaries if summary is not None]
    counts = Counter(classify_batch(batch.name) for batch in batch_dirs)
    latest_by_theme: dict[str, tuple[Path, Path]] = {}
    for batch, summary in summaries:
        latest_by_theme[classify_batch(batch.name)] = (batch, summary)
    lines = [
        "# Automation Runtime Index",
        "",
        "> Generated by `python scripts/build_runtime_index.py`.",
        "> Runtime artifacts are status signals and provenance records, not semantic decisions.",
        "",
        "## Snapshot",
        "",
        f"- Batch directories: `{len(batch_dirs)}`",
        f"- Files: `{retention['files']}`",
        f"- Size: `{retention['total_bytes']}` bytes",
        "",
        "## Retention Signals",
        "",
        f"- Large files (>= {retention['large_file_threshold_bytes']} bytes): `{len(retention['large_files'])}`",
        f"- Exact duplicate groups: `{retention['exact_duplicate_groups']}`",
        f"- Exact duplicate files beyond the first copy: `{retention['exact_duplicate_files']}`",
        f"- Potential duplicate bytes: `{retention['potential_duplicate_bytes']}`",
        f"- Ephemeral residue: `{len(retention['ephemeral_residue'])}`",
        f"- R1 provenance: `{retention['retention_tiers']['R1']['files']}` files",
        f"- R2 validated rebuildable projections: `{retention['retention_tiers']['R2']['files']}` files",
        f"- Possible R2 projections without valid provenance: `{retention['r2_provenance']['review_required']}` files (`review_required`, retained as R1)",
        f"- R3 ephemeral residue: `{retention['retention_tiers']['R3']['files']}` files",
        "- These are capacity signals only; they do not authorize deletion or historical rewrite.",
        "- [Runtime artifact retention policy](../../.agents/skills/00-coordination/system-upgrade/references/runtime-artifact-retention.md)",
        "",
        "## Themes",
        "",
        "| Theme | Batches | Latest summary |",
        "|---|---:|---|",
    ]
    for theme in THEMES:
        latest = latest_by_theme.get(theme)
        latest_link = f"[summary]({relative_link(root, latest[1])})" if latest else "-"
        lines.append(f"| `{theme}` | {counts.get(theme, 0)} | {latest_link} |")

    lines.extend(["", f"## Recent Batches ({recent_limit})", ""])
    for batch, summary in reversed(summaries[-recent_limit:]):
        lines.append(f"- [{batch.name}]({relative_link(root, summary)})")

    lines.extend([
        "",
        "## Current State",
        "",
        "- [Current health](../state/current-health.json)",
        "- [Governance backlog](../governance/governance-backlog.md)",
        "- [Runtime layer README](../README.md)",
        "- Full historical artifacts remain in this directory.",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None, root: Path = BASE) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--retention-report",
        action="store_true",
        help="print a read-only JSON capacity inventory without writing index.md",
    )
    args = parser.parse_args(argv)
    if args.retention_report:
        print(json.dumps(build_retention_inventory(root), ensure_ascii=False, indent=2))
        return 0

    output = root / "06-runtime" / "automation" / "index.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_runtime_index(root), encoding="utf-8")
    print(f"wrote={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
