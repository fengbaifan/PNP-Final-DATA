#!/usr/bin/env python3
"""Retired unsafe one-shot migration entry point.

The former implementation regenerated tables from cards and rewrote the frozen
release snapshot. Use the focused, preview-first builders and auditors instead.
Dataset exports belong in a new versioned draft directory.
"""
import sys


def main() -> int:
    print(
        "build_tables.py is retired: it could overwrite current tables and release/v0.1. "
        "Use build_source_segments.py, build_entity_candidates.py, "
        "build_field_facts.py, audit_tables.py, and export_dataset.py.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
