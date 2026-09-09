"""Load and validate the single controlled relation vocabulary."""
from __future__ import annotations

from pathlib import Path

import yaml


BASE = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    BASE
    / ".agents"
    / "skills"
    / "01-intake"
    / "ingest"
    / "references"
    / "relation-types.yml"
)


def load_relation_schema(path: Path = SCHEMA_PATH) -> tuple[set[str], set[str], dict[str, str]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw_types = data.get("types") or []
    raw_legacy = data.get("legacy_generic_types") or []
    inverse = data.get("inverse") or {}
    if not isinstance(raw_types, list) or not all(isinstance(item, str) for item in raw_types):
        raise ValueError("relation schema types must be a string list")
    if len(raw_types) != len(set(raw_types)):
        raise ValueError("relation schema contains duplicate controlled types")
    if not isinstance(raw_legacy, list) or not all(isinstance(item, str) for item in raw_legacy):
        raise ValueError("relation schema legacy_generic_types must be a string list")
    if not isinstance(inverse, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in inverse.items()
    ):
        raise ValueError("relation schema inverse must map strings to strings")

    controlled = set(raw_types)
    legacy = set(raw_legacy)
    unknown_inverse = (set(inverse) | set(inverse.values())) - controlled
    if unknown_inverse:
        raise ValueError(f"relation schema inverse references unknown types: {sorted(unknown_inverse)}")
    if controlled & legacy:
        raise ValueError("controlled and legacy generic relation types must not overlap")
    return controlled, legacy, dict(inverse)


RELATION_TYPES, LEGACY_GENERIC_RELATION_TYPES, INVERSE_MAP = load_relation_schema()
VALID_RELATION_TYPES = RELATION_TYPES | LEGACY_GENERIC_RELATION_TYPES
