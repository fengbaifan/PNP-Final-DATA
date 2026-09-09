#!/usr/bin/env python3
"""build_translation_index.py — 构建翻译索引 YAML"""
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "04-knowledge" / "quality" / "translation-index.yml"
TRANSLATION_UNIT_TYPES = ["persons", "terms", "publications", "works", "institutions"]


def build_index(base: Path = BASE) -> list[dict[str, str]]:
    units = base / "04-knowledge" / "units"
    index = []
    for dir_name in TRANSLATION_UNIT_TYPES:
        directory = units / dir_name
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            frontmatter = path.read_text(encoding="utf-8").split("---")[1]
            name_en = re.search(r"^name_en:\s*(.+)", frontmatter, re.MULTILINE)
            title = re.search(r"^title:\s*(.+)", frontmatter, re.MULTILINE)
            name_original = re.search(r"^name_original:\s*(.+)", frontmatter, re.MULTILINE)
            language_original = re.search(r"^language_original:\s*(.+)", frontmatter, re.MULTILINE)
            index.append({
                "slug": f"{dir_name}/{path.stem}",
                "type": dir_name,
                "name_en": name_en.group(1).strip() if name_en else "",
                "title": title.group(1).strip()[:100] if title else "",
                "name_original": name_original.group(1).strip() if name_original else "",
                "language_original": language_original.group(1).strip() if language_original else "",
            })
    return index


def render_index(index: list[dict[str, str]], generated: str | None = None) -> str:
    return yaml.dump(
        {"generated": generated or date.today().isoformat(), "total": len(index), "index": index},
        allow_unicode=True,
        sort_keys=False,
        width=200,
    )


def stable_generated_date(index: list[dict[str, str]], output: Path = OUT) -> str:
    """Preserve the prior date when the generated semantic content is unchanged."""
    if output.exists():
        existing = yaml.safe_load(output.read_text(encoding="utf-8")) or {}
        if existing.get("total") == len(index) and existing.get("index") == index:
            generated = existing.get("generated")
            if generated:
                return str(generated)
    return date.today().isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    index = build_index()
    if args.dry_run:
        print(f"  [DRY RUN] {len(index)} entries")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render_index(index, generated=stable_generated_date(index)), encoding="utf-8")
    print(f"  written: {OUT} ({len(index)} entries)")


if __name__ == "__main__":
    main()
