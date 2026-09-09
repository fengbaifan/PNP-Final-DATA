#!/usr/bin/env python3
"""
content-quality-audit — 知识元内容质量全量审查官
=================================================
补充 audit_repo.py 未覆盖的内容层检查：
- 正文结构完整性
- 文本碎片/损坏检测
- 同类型重复标题
- 跨类型同名消歧
- 正文验证状态与 frontmatter 对齐
- source local_file 可达性
- 空字段/空正文检测

本脚本只报告可确定性复现的机械内容完整性信号，不评估语义细节密度、
事实充分性或知识价值；这些判断必须由 Agent 语义复读或审查完成。

Read-only. 不修改知识元。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict
import yaml

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
INTAKE = BASE / "02-sources"
PROCESSING = BASE / "03-processing"

CONTENT_QUALITY_METRIC_KIND = "deterministic_content_integrity"
CONTENT_QUALITY_METRIC_BOUNDARY = (
    "仅检查可机械判定的结构、编码、占位、链接和状态一致性；"
    "不评估语义细节密度、事实充分性或知识价值。"
)

TYPE_DIR_MAP = {
    "persons": "person",
    "concepts": "concept",
    "works": "work",
    "publications": "publication",
    "cases": "case",
    "places": "place",
    "techniques": "technique",
    "ideas": "idea",
}
TITLE_BILINGUAL_RE = re.compile(r'[\u4e00-\u9fff].*[（(][^（）)]*[A-Za-zÀ-ÿ][^（）)]*[）)]')
TITLE_REVERSE_BILINGUAL_RE = re.compile(r'^[^（(]*[A-Za-zÀ-ÿ][^（(]*[（(][^）)]*[\u4e00-\u9fff][^）)]*[）)]$')

CHECKLIST_BLOCKS = [
    "## 验证状态",
    "- **证据状态**:",
    "- **验证层级**:",
    "- **验证平台**:",
    "- **匹配质量**:",
    "- **验证日期**:",
    "- **证据范围**:",
]

CORRUPTION_PATTERNS = [
    (re.compile(r"�"), "replacement character U+FFFD（疑似编码损坏）"),
    (re.compile(r"[鍩锛銆鐨绋]"), "常见 mojibake 汉字片段（疑似 UTF-8/GBK 解码损坏）"),
    (re.compile(r"鈥[滜濇]?"), "常见 mojibake 引号片段（疑似 UTF-8/GBK 解码损坏）"),
    (re.compile(r"(?<![a-zA-Z])echnique\b"), "echnique (疑似 technique 碎片)"),
    (re.compile(r"(?<![a-zA-Z])ublication\b"), "ublication (疑似 publication 碎片)"),
    (re.compile(r"(?<![a-zA-Z])ersons\b"), "ersons (疑似 persons 碎片)"),
    (re.compile(r"(?<![a-zA-Z])oncepts\b"), "oncepts (疑似 concepts 碎片)"),
    (re.compile(r"(?<![a-zA-Z])orks\b"), "orks (疑似 works 碎片)"),
    (re.compile(r"(?<![a-zA-Z])laces\b"), "laces (疑似 places 碎片)"),
    (re.compile(r"(?<![a-zA-Z])deas\b"), "deas (疑似 ideas 碎片)"),
    (re.compile(r"(?<![a-zA-Z])echniques\b"), "echniques (疑似 techniques 碎片)"),
    (re.compile(r"(?<![a-zA-Z])ublications\b"), "ublications (疑似 publications 碎片)"),
    (re.compile(r"(?<![a-zA-Z])ases\b"), "ases (疑似 cases 碎片)"),
    (re.compile(r"\bunknow\b"), "unknow (疑似 unknown 碎片)"),
]

FM_RE = re.compile(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_fm(text: str) -> str:
    match = FM_RE.match(text)
    return match.group(1).strip("\n") if match else ""


def extract_body(text: str) -> str:
    match = FM_RE.match(text)
    return text[match.end():] if match else text


def scalar_fm(fm: str, field: str) -> str:
    m = re.search(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def iter_units() -> list[Path]:
    files: list[Path] = []
    for type_dir in sorted(UNITS.iterdir()):
        if not type_dir.is_dir():
            continue
        files.extend(sorted(type_dir.glob("*.md")))
    return files


def check_empty_body(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        body = extract_body(text).strip()
        if len(body) < 20:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": "正文过短或为空",
                "body_chars": len(body),
            })
    return findings


def check_missing_sections(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        body = extract_body(text)
        has_description = "## 描述" in body or "## Description" in body
        has_verify = any(block in body for block in CHECKLIST_BLOCKS)
        if not has_description and len(body.strip()) > 50:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": "缺少 '## 描述' 区块",
            })
        if not has_verify and len(body.strip()) > 80:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": "缺少 '## 验证状态' 区块",
            })
    return findings


def check_text_corruption(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        body = extract_body(text)
        for pattern, label in CORRUPTION_PATTERNS:
            match = pattern.search(body)
            if match:
                findings.append({
                    "file": path.relative_to(BASE).as_posix(),
                    "issue": f"正文疑似文本碎片: {label}",
                    "context": body[max(0, match.start() - 30):match.end() + 30].strip(),
                })
    return findings


def check_duplicate_titles(files: list[Path]) -> list[dict]:
    title_map: dict[str, list[str]] = defaultdict(list)
    for path in files:
        text = read_text(path)
        fm = extract_fm(text)
        title = scalar_fm(fm, "title") or path.stem.replace("-", " ")
        title_map[title].append(path.relative_to(BASE).as_posix())
    findings: list[dict] = []
    for title, paths in title_map.items():
        if len(paths) > 1:
            disambiguated = all("类型消歧" in read_text(BASE / p) for p in paths)
            if disambiguated:
                continue
            findings.append({
                "issue": "同标题知识元存在重复",
                "title": title,
                "files": paths,
            })
    return findings


def check_cross_type_same_name(files: list[Path]) -> list[dict]:
    name_map: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for path in files:
        text = read_text(path)
        fm = extract_fm(text)
        name = scalar_fm(fm, "name_en") or scalar_fm(fm, "title") or path.stem.replace("-", " ")
        ku_type = path.parent.name
        name_key = name.lower().strip()
        name_map[name_key][ku_type].append(path.relative_to(BASE).as_posix())
    findings: list[dict] = []
    for name_key, type_paths in name_map.items():
        if len(type_paths) > 1:
            disambiguated = all(
                "类型消歧" in read_text(BASE / p)
                for paths in type_paths.values() for p in paths
            )
            if disambiguated:
                continue
            findings.append({
                "issue": "跨类型同名知识元（未确认是否已消歧）",
                "name": name_key,
                "by_type": dict(type_paths),
            })
    return findings


def check_title_format(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        fm = extract_fm(text)
        title = scalar_fm(fm, "title")
        name_en = scalar_fm(fm, "name_en")
        if not title:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": "title 为空",
            })
            continue
        quote_count = title.count('"')
        if quote_count % 2 == 1:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": f'title 疑似引号损坏: "{title}"',
            })
            continue
        has_chinese = bool(re.search(r"[\u4e00-\u9fff]", title))
        has_english = bool(re.search(r"[A-Za-z]{3,}", title))
        bilingual_ok = bool(TITLE_BILINGUAL_RE.search(title))
        reverse_bilingual = bool(TITLE_REVERSE_BILINGUAL_RE.search(title))
        if name_en and reverse_bilingual:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": f"title 为英文在前，应统一为“中文（English）”: {title}",
            })
        elif name_en and has_chinese and has_english and not bilingual_ok:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": f"title 含中英文但不符合“中文（English）”格式: {title}",
            })
        elif name_en and not bilingual_ok:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": f"title 未统一为中英双语: {title}",
            })
    return findings


def check_body_verify_vs_fm(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        fm = extract_fm(text)
        body = extract_body(text)
        fm_es = scalar_fm(fm, "evidence_status")
        fm_vl = scalar_fm(fm, "verification_level")

        body_has_verified = "externally_verified" in body or "partially_verified" in body
        fm_has_verified = fm_es in {"externally_verified", "partially_verified"}

        if fm_es in {"externally_verified", "partially_verified"} and not body_has_verified:
            has_verify_section = "## 验证状态" in body
            if not has_verify_section:
                findings.append({
                    "file": path.relative_to(BASE).as_posix(),
                    "issue": f"frontmatter evidence_status={fm_es} 但正文缺少'## 验证状态'区块",
                })

        if fm_vl and "## 验证状态" not in body:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": f"frontmatter verification_level={fm_vl} 但正文缺少'## 验证状态'区块",
            })

    return findings


def check_local_file_reachable(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        fm = extract_fm(text)
        for match in re.finditer(r'local_file:\s*"([^"]+)"', fm):
            local = match.group(1)
            candidate = BASE / local
            if not candidate.exists():
                findings.append({
                    "file": path.relative_to(BASE).as_posix(),
                    "issue": f"local_file 指向不存在的文件: {local}",
                })
    return findings


REQUIRED_PERIOD_TYPES = {"person", "persons", "work", "works", "publication", "publications", "case", "cases"}
OPTIONAL_PERIOD_TYPES = {"concept", "concepts", "technique", "techniques", "idea", "ideas", "place", "places"}


def check_empty_frontmatter_values(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        fm = extract_fm(text)
        try:
            fm_data = yaml.safe_load(fm) or {}
        except Exception:
            fm_data = {}
        for field in ["title", "name_en", "sub_type", "tags"]:
            value = fm_data.get(field)
            if value in (None, "", [], {}):
                findings.append({
                    "file": path.relative_to(BASE).as_posix(),
                    "issue": f"frontmatter 字段为空: {field}",
                })
    return findings


TYPE_NAMES_BARE = {"person", "concept", "work", "publication", "case", "place", "technique", "idea"}

PLACEHOLDER_PATTERNS = [
    "待补充", "TODO", "TBD", "相关描述", "相关内容", "重要概念",
    "待进一步研究", "待层级体系建立后补充",
]

GENERIC_SENTENCE_PATTERNS = [
    (re.compile(r"具有重要意义"), "具有重要意义（泛化表述）"),
    (re.compile(r"\b暂无\b"), "暂无（占位表述）"),
    (re.compile(r"的相关描述。"), "「的相关描述。」（低质量填充句）"),
]


def check_body_type_residue(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        body = extract_body(text)
        first_line = body.strip().split("\n")[0].strip()
        if first_line.lower() in TYPE_NAMES_BARE:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": f"frontmatter 后裸露 type 行: '{first_line}'",
            })
    return findings


def check_h1_in_body(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        body = extract_body(text)
        for m in re.finditer(r"^# (?!验证)(.+)$", body, re.MULTILINE):
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": f"正文存在一级标题: '# {m.group(1).strip()}'",
            })
    return findings


def check_english_headings(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        body = extract_body(text)
        for m in re.finditer(r"^## ([A-Z][a-z]+(?: [A-Z][a-z]+)*)$", body, re.MULTILINE):
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": f"英文 section 标题: '## {m.group(1)}'",
            })
    return findings


def check_placeholder_content(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        body = extract_body(text)
        for p in PLACEHOLDER_PATTERNS:
            if p in body:
                # find containing section
                sec_name = "?"
                for m in re.finditer(r"^## (.+)$", body, re.MULTILINE):
                    if m.start() <= body.index(p):
                        sec_name = m.group(1)
                findings.append({
                    "file": path.relative_to(BASE).as_posix(),
                    "issue": f"占位内容: '## {sec_name}' 中含 '{p}'",
                })
                break
    return findings


def check_fm_body_verify_conflict(files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for path in files:
        text = read_text(path)
        fm = extract_fm(text)
        body = extract_body(text)
        fm_es = ""
        m = re.search(r"^evidence_status\s*:\s*(.+)$", fm, re.MULTILINE)
        if m:
            fm_es = m.group(1).strip()
        body_internal = "内部验证" in body or "内部一致性" in body
        body_api_limited = "外部API受限" in body or "API受限" in body
        if fm_es in ("externally_verified", "partially_verified") and body_internal and body_api_limited:
            findings.append({
                "file": path.relative_to(BASE).as_posix(),
                "issue": "FM evidence_status 与正文验证描述矛盾（FM声称外部验证，正文说内部一致性/API受限）",
            })
    return findings


def type_summary(files: list[Path]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for path in files:
        counts[path.parent.name] += 1
    return dict(sorted(counts.items()))


def run_all_checks(files: list[Path]) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}

    results["empty_body"] = check_empty_body(files)
    results["empty_frontmatter_values"] = check_empty_frontmatter_values(files)
    results["missing_sections"] = check_missing_sections(files)
    results["text_corruption"] = check_text_corruption(files)
    results["title_format"] = check_title_format(files)
    results["duplicate_titles"] = check_duplicate_titles(files)
    results["cross_type_same_name"] = check_cross_type_same_name(files)
    results["body_verify_vs_fm"] = check_body_verify_vs_fm(files)
    results["local_file_broken"] = check_local_file_reachable(files)
    results["body_type_residue"] = check_body_type_residue(files)
    results["h1_in_body"] = check_h1_in_body(files)
    results["english_headings"] = check_english_headings(files)
    results["placeholder_content"] = check_placeholder_content(files)
    results["fm_body_verify_conflict"] = check_fm_body_verify_conflict(files)
    results["type_summary"] = [{"type": k, "count": v} for k, v in type_summary(files).items()]

    return results


def get_content_quality_summary() -> dict:
    files = iter_units()
    results = run_all_checks(files)
    return {
        "metric_kind": CONTENT_QUALITY_METRIC_KIND,
        "metric_boundary": CONTENT_QUALITY_METRIC_BOUNDARY,
        "empty_body": len(results.get("empty_body", [])),
        "empty_frontmatter_values": len(results.get("empty_frontmatter_values", [])),
        "missing_sections": len(results.get("missing_sections", [])),
        "text_corruption": len(results.get("text_corruption", [])),
        "title_format_issues": len(results.get("title_format", [])),
        "duplicate_titles": len(results.get("duplicate_titles", [])),
        "cross_type_same_name": len(results.get("cross_type_same_name", [])),
        "body_verify_vs_fm": len(results.get("body_verify_vs_fm", [])),
        "local_file_broken": len(results.get("local_file_broken", [])),
        "body_type_residue": len(results.get("body_type_residue", [])),
        "h1_in_body": len(results.get("h1_in_body", [])),
        "english_headings": len(results.get("english_headings", [])),
        "placeholder_content": len(results.get("placeholder_content", [])),
        "fm_body_verify_conflict": len(results.get("fm_body_verify_conflict", [])),
        "total_files": len(files),
        "total_findings": sum(
            len(v) for k, v in results.items()
            if k != "type_summary" and isinstance(v, list)
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="知识元内容质量全量审查官")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--summary", action="store_true", help="仅输出摘要 JSON（供机器读取）")
    parser.add_argument("--type", dest="type_filter", help="仅检查指定类型")
    parser.add_argument("--sample", type=int, default=0, help="抽查 N 个文件")
    args = parser.parse_args()

    all_files = iter_units()
    if args.type_filter:
        all_files = [f for f in all_files if f.parent.name == args.type_filter]
    if args.sample > 0:
        import random
        all_files = random.sample(all_files, min(args.sample, len(all_files)))

    print(f"审查范围: {len(all_files)} 个知识元", file=sys.stderr)
    results = run_all_checks(all_files)

    total_findings = sum(len(v) for k, v in results.items() if k != "type_summary" and isinstance(v, list))

    if args.summary:
        summary = {
            "content_quality": {
                "metric_kind": CONTENT_QUALITY_METRIC_KIND,
                "metric_boundary": CONTENT_QUALITY_METRIC_BOUNDARY,
                "empty_body": len(results.get("empty_body", [])),
                "empty_frontmatter_values": len(results.get("empty_frontmatter_values", [])),
                "missing_sections": len(results.get("missing_sections", [])),
                "text_corruption": len(results.get("text_corruption", [])),
                "title_format_issues": len(results.get("title_format", [])),
                "duplicate_titles": len(results.get("duplicate_titles", [])),
                "cross_type_same_name": len(results.get("cross_type_same_name", [])),
                "body_verify_vs_fm": len(results.get("body_verify_vs_fm", [])),
                "local_file_broken": len(results.get("local_file_broken", [])),
                "body_type_residue": len(results.get("body_type_residue", [])),
                "h1_in_body": len(results.get("h1_in_body", [])),
                "english_headings": len(results.get("english_headings", [])),
                "placeholder_content": len(results.get("placeholder_content", [])),
                "fm_body_verify_conflict": len(results.get("fm_body_verify_conflict", [])),
                "total_files": len(all_files),
                "total_findings": total_findings,
            }
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f" 内容质量全量审查报告")
        print(f" 审查范围: {len(all_files)} 个知识元 | 总发现: {total_findings}")
        print(f"{'='*60}\n")
        print(f"边界: {CONTENT_QUALITY_METRIC_BOUNDARY}\n")

        for category, findings in results.items():
            if category == "type_summary":
                continue
            if not findings:
                continue
            cat_label = {
                "empty_body": "空正文",
                "empty_frontmatter_values": "frontmatter 空字段",
                "missing_sections": "缺少必要区块",
                "text_corruption": "文本碎片/损坏",
                "title_format": "title 格式问题",
                "duplicate_titles": "同标题重复",
                "cross_type_same_name": "跨类型同名",
                "body_verify_vs_fm": "正文验证状态 vs frontmatter 不一致",
                "local_file_broken": "local_file 断链",
                "body_type_residue": "裸露 type 行",
                "h1_in_body": "一级标题违规",
                "english_headings": "英文 section 标题",
                "placeholder_content": "占位内容",
                "fm_body_verify_conflict": "FM-正文验证矛盾",
            }.get(category, category)

            print(f"\n## {cat_label} ({len(findings)} 项)")
            for f in findings:
                if "title" in f:
                    print(f"  - 标题: '{f['title']}' → {len(f.get('files', []))} 个文件")
                elif "name" in f:
                    print(f"  - 名称: '{f['name']}' → {len(f.get('by_type', {}))} 个类型")
                else:
                    ctx = f.get("context", "")
                    ctx_str = f" | 上下文: ...{ctx}..." if ctx else ""
                    print(f"  - [{f.get('file', '?')}] {f['issue']}{ctx_str}")

    print(f"\n总发现: {total_findings}", file=sys.stderr)


if __name__ == "__main__":
    main()
