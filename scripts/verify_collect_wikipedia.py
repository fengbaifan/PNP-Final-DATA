#!/usr/bin/env python3
"""
verify_collect_wikipedia.py — Wikipedia 证据收集器（阶段1）
==========================================================
通过 Wikipedia REST API / Action API 收集证据，生成 evidence JSONL。
不直接修改知识元；写回必须通过 verify_apply_evidence.py 执行。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    requests = None

try:
    from scripts._verification_targets import load_result_targets, resolve, resolve_single_target, write_jsonl
except ModuleNotFoundError:
    from _verification_targets import load_result_targets, resolve, resolve_single_target, write_jsonl

BASE = Path(__file__).resolve().parents[1]
UNITS = BASE / "04-knowledge" / "units"
WIKIPEDIA_REST_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary"
WIKIPEDIA_ACTION_API = "https://en.wikipedia.org/w/api.php"
REQUEST_DELAY = 0.5
HTTP_TIMEOUT = 10
MAX_RATE_LIMIT_RETRIES = 1
MAX_SEARCH_CANDIDATES = 3
HEADERS = {"User-Agent": "Knowledge-Distillation/1.0"}

TYPE_ALIASES = {
    "persons": "person",
    "families": "family",
    "institutions": "institution",
    "places": "place",
    "works": "work",
    "archives": "archive",
    "terms": "term",
    "procedures": "procedure",
    "events": "event",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_frontmatter(text: str) -> str:
    match = re.search(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    return match.group(1).strip("\n") if match else ""


def scalar_fm(fm: str, field: str) -> str:
    m = re.search(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def normalize_text(text: str) -> str:
    text = re.sub(r"\s*\([^)]*\)", "", text or "")
    text = text.replace("_", " ").strip().lower()
    text = re.sub(r"[^a-z0-9\s\-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def title_for_lookup(name_en: str) -> str:
    cleaned = re.sub(r"\s*\([^)]*\)", "", name_en or "")
    cleaned = re.sub(r"\s*/\s*.*$", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.replace(" ", "_")


def token_overlap(a: str, b: str) -> float:
    a_tokens = set(t for t in normalize_text(a).split() if t)
    b_tokens = set(t for t in normalize_text(b).split() if t)
    if not a_tokens or not b_tokens:
        return 0.0
    intersection = len(a_tokens & b_tokens)
    return intersection / max(len(a_tokens), len(b_tokens))


def fetch_summary(title: str) -> dict:
    if not requests:
        return {}
    encoded = quote(title, safe="_-")
    url = f"{WIKIPEDIA_REST_BASE}/{encoded}"
    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT, allow_redirects=True)
            if r.status_code == 200:
                data = r.json()
                data["_api_url"] = url
                return data
            if r.status_code == 404:
                return {}
            if r.status_code == 429 and attempt < MAX_RATE_LIMIT_RETRIES:
                time.sleep(1)
                continue
            return {}
        except Exception:
            return {}
    return {}


def search_titles(query: str) -> list[dict]:
    if not requests:
        return []
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": MAX_SEARCH_CANDIDATES,
        "format": "json",
        "utf8": 1,
    }
    try:
        r = requests.get(WIKIPEDIA_ACTION_API, params=params, headers=HEADERS, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        return r.json().get("query", {}).get("search", [])
    except Exception:
        return []


LIMITED_SCOPES = {
    "entity_identity_only",
    "term_existence",
    "event_identity_only",
    "bibliographic_hint",
}


def infer_claim_scope(ku_type: str) -> str:
    if ku_type in {"term", "procedure"}:
        return "term_existence"
    if ku_type == "event":
        return "event_identity_only"
    if ku_type == "archive":
        return "bibliographic_hint"
    return "entity_identity_only"


def infer_claim_target(ku_type: str) -> str:
    if ku_type in {"term", "procedure"}:
        return "term"
    if ku_type == "archive":
        return "title_or_bibliographic_identity"
    if ku_type == "event":
        return "event_name"
    return "name_en"


def is_redirected(requested_title: str, summary: dict) -> bool:
    returned = summary.get("title", "")
    return bool(requested_title and returned and normalize_text(requested_title) != normalize_text(returned))


def evaluate_match(name_en: str, ku_type: str, summary: dict) -> tuple[str, float, list[str], list[dict]]:
    title = summary.get("title", "")
    description = summary.get("description", "")
    extract = summary.get("extract", "")
    page_type = summary.get("type", "")

    verified_fields: list[str] = []
    detail: list[dict] = []
    score = 0
    max_score = 3

    exact_title = normalize_text(name_en) == normalize_text(title)
    title_overlap = token_overlap(name_en, title)

    if exact_title:
        score += 1
        verified_fields.append("name_en")
        detail.append({"field": "title_match", "expected": name_en, "actual": title, "result": "pass"})
    elif title_overlap >= 0.6:
        score += 1
        verified_fields.append("name_en_partial")
        detail.append({"field": "title_match", "expected": name_en, "actual": title, "result": "partial"})
    else:
        detail.append({"field": "title_match", "expected": name_en, "actual": title, "result": "fail"})

    if page_type and page_type != "disambiguation":
        score += 1
        verified_fields.append("page_exists")
        detail.append({"field": "page_type", "expected": "non-disambiguation", "actual": page_type, "result": "pass"})
    else:
        detail.append({"field": "page_type", "expected": "non-disambiguation", "actual": page_type or "none", "result": "fail"})

    desc_or_extract_ok = bool(description) or bool(extract)
    if desc_or_extract_ok:
        score += 1
        verified_fields.append("description_or_extract")
        detail.append({"field": "description_or_extract", "expected": "present", "actual": "present", "result": "pass"})
    else:
        detail.append({"field": "description_or_extract", "expected": "present", "actual": "missing", "result": "fail"})

    title_failed = any(d.get("field") == "title_match" and d.get("result") == "fail" for d in detail)

    if ku_type in {"term", "procedure", "event"} and page_type in {"standard", "article"} and not title_failed:
        score = min(score + 1, max_score)
        existence_field = "event_identity" if ku_type == "event" else "term_existence"
        if existence_field not in verified_fields:
            verified_fields.append(existence_field)

    if score >= 3:
        quality = "strong"
    elif score == 2:
        quality = "medium"
    elif score == 1:
        quality = "weak"
    else:
        quality = "none"

    if title_failed and quality != "none":
        quality = "weak"

    match_score = round(score / max_score, 2) if max_score else 0.0
    if title_failed:
        match_score = min(match_score, 0.33)

    return quality, match_score, verified_fields, detail


def pick_recommended_changes(match_quality: str, claim_scope: str, second_source_confirmed: bool = False) -> dict:
    if match_quality == "strong":
        evidence_status = "externally_verified"
        if claim_scope in LIMITED_SCOPES and not second_source_confirmed:
            evidence_status = "partially_verified"
        return {
            "evidence_status": evidence_status,
            "verification_level": "L1",
            "confidence": "medium",
            "consensus": "tentative",
        }
    if match_quality == "medium":
        return {
            "evidence_status": "partially_verified",
            "verification_level": "L1",
            "confidence": "medium",
            "consensus": "tentative",
        }
    return {}


def collect_one(ku_path: Path, verbose: bool = False) -> dict | None:
    text = read_text(ku_path)
    fm = extract_frontmatter(text)
    if not fm:
        return None

    ku_type = scalar_fm(fm, "type").strip().lower()
    if not ku_type:
        ku_type = TYPE_ALIASES.get(ku_path.parent.name, "")
    name_en = scalar_fm(fm, "name_en") or scalar_fm(fm, "title") or ku_path.stem.replace("-", " ")

    rel = ku_path.relative_to(BASE).as_posix()
    claim_scope = infer_claim_scope(ku_type)

    if verbose:
        print(f"\n  [{ku_type}] {name_en}", file=sys.stderr)

    direct_title = title_for_lookup(name_en)
    summary = fetch_summary(direct_title)
    candidates: list[dict] = []

    if summary:
        quality, match_score, verified_fields, detail = evaluate_match(name_en, ku_type, summary)
        candidates.append(
            {
                "title": summary.get("title", ""),
                "description": summary.get("description", ""),
                "url": summary.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "match_quality": quality,
                "match_score": match_score,
                "matched_fields": detail,
                "candidate_rank": 1,
                "is_disambiguation": summary.get("type") == "disambiguation",
                "is_redirect": is_redirected(direct_title, summary),
                "redirect_from": direct_title if is_redirected(direct_title, summary) else "",
            }
        )
        best_summary = summary
        best_quality = quality
        best_score = match_score
        best_verified_fields = verified_fields
        best_detail = detail
        best_candidate_rank = 1
    else:
        best_summary = {}
        best_quality = "none"
        best_score = 0.0
        best_verified_fields = []
        best_detail = []
        best_candidate_rank = 0

    if best_quality not in {"strong", "medium"}:
        search_results = search_titles(name_en)
        for rank_index, item in enumerate(search_results[:5], start=1):
            title = item.get("title", "")
            if not title:
                continue
            summary_candidate = fetch_summary(title.replace(" ", "_"))
            if not summary_candidate:
                continue
            quality, score_value, fields, detail = evaluate_match(name_en, ku_type, summary_candidate)
            candidate_row = {
                "title": summary_candidate.get("title", title),
                "description": summary_candidate.get("description", ""),
                "url": summary_candidate.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "match_quality": quality,
                "match_score": score_value,
                "matched_fields": detail,
                "candidate_rank": rank_index,
                "is_disambiguation": summary_candidate.get("type") == "disambiguation",
                "is_redirect": is_redirected(title, summary_candidate),
                "redirect_from": title if is_redirected(title, summary_candidate) else "",
            }
            candidates.append(candidate_row)

            rank = {"none": 0, "weak": 1, "medium": 2, "strong": 3}
            if rank.get(quality, 0) > rank.get(best_quality, 0):
                best_summary = summary_candidate
                best_quality = quality
                best_score = score_value
                best_verified_fields = fields
                best_detail = detail
                best_candidate_rank = rank_index
            time.sleep(REQUEST_DELAY / 5)

    is_disambiguation = best_summary.get("type") == "disambiguation" if best_summary else False
    blocking_reason = None
    if is_disambiguation:
        blocking_reason = "disambiguation_page"
    elif best_quality == "weak":
        blocking_reason = "weak_title_match"
    elif best_quality == "none":
        blocking_reason = "no_suitable_page"

    recommended = {} if blocking_reason else pick_recommended_changes(best_quality, claim_scope)
    notes = (
        "Wikipedia identity/existence verification only; contribution claims still rely on source literature."
    )
    if best_quality == "none":
        notes = "No suitable Wikipedia page found via summary or search."

    evidence = {
        "ku_path": rel,
        "platform": "Wikipedia EN",
        "source_type": "encyclopedia_api",
        "source_authority": "tertiary_reference",
        "source_independence_group": "wikimedia",
        "url": best_summary.get("content_urls", {}).get("desktop", {}).get("page", "") if best_summary else "",
        "claim_scope": claim_scope,
        "claim_target": infer_claim_target(ku_type),
        "match_quality": best_quality,
        "match_score": best_score,
        "verified_fields": best_verified_fields,
        "conflicting_fields": [],
        "candidate_rank": best_candidate_rank,
        "candidate_count": len(candidates),
        "is_disambiguation": is_disambiguation,
        "is_redirect": is_redirected(direct_title, best_summary) if best_summary else False,
        "redirect_from": direct_title if best_summary and is_redirected(direct_title, best_summary) else "",
        "match_detail": best_detail,
        "candidates": candidates[:5],
        "recommended_changes": recommended,
        "blocking_reason": blocking_reason,
        "notes": notes,
    }

    if verbose:
        print(f"    quality={best_quality} matched={best_verified_fields}", file=sys.stderr)

    return evidence


def iter_units(limit: int = 0) -> list[Path]:
    files: list[Path] = []
    for type_dir in sorted(UNITS.iterdir()):
        if not type_dir.is_dir():
            continue
        for md in sorted(type_dir.glob("*.md")):
            if md.name.startswith("."):
                continue
            files.append(md)
            if limit and len(files) >= limit:
                return files
    return files


def main():
    parser = argparse.ArgumentParser(description="Wikipedia 证据收集器（阶段1）")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--ku", help="指定知识元（文件名，不含路径）")
    scope.add_argument("--input-result", type=Path, help="读取包含 targets 的批次规划 JSON")
    parser.add_argument("--checkpoint", type=int, default=0, help="只收集 input-result 中指定 checkpoint")
    parser.add_argument("--output", type=Path, help="原子写入 evidence JSONL；省略时输出到 stdout")
    parser.add_argument("--limit", type=int, default=0, help="批量限制")
    parser.add_argument("--verbose", action="store_true", help="详细输出到 stderr")
    parser.add_argument("--dry-run", action="store_true", help="仅预览")
    args = parser.parse_args()

    if not requests:
        print("[STUB] requests 库未安装。请先安装: pip install requests", file=sys.stderr)
        return

    if args.dry_run:
        print("[DRY RUN] 将扫描知识元并调用 Wikipedia API 收集证据")
        if args.ku:
            print(f"  target: {args.ku}")
        elif args.input_result:
            print(f"  input-result: {args.input_result} checkpoint={args.checkpoint or 'all'}")
        else:
            print(f"  scope: all UNITS (limit={args.limit})")
        print("  输出: evidence JSONL（每行一个 JSON 对象）")
        return

    if args.checkpoint and not args.input_result:
        parser.error("--checkpoint 只能与 --input-result 一起使用")
    if args.ku:
        one = resolve_single_target(args.ku, UNITS)
        if not one:
            print(f"未找到: {args.ku}", file=sys.stderr)
            sys.exit(1)
        files = [one]
    elif args.input_result:
        files = load_result_targets(resolve(args.input_result, BASE), BASE, UNITS, args.checkpoint)
    else:
        files = iter_units(limit=args.limit)

    if args.verbose:
        print(f"待验证: {len(files)} 个知识元", file=sys.stderr)

    evidence_rows = []
    for path in files:
        evidence = collect_one(path, verbose=args.verbose)
        if evidence:
            evidence_rows.append(evidence)
        time.sleep(REQUEST_DELAY)

    if args.output:
        output = resolve(args.output, BASE)
        write_jsonl(evidence_rows, output)
        if args.verbose:
            print(f"evidence={output}", file=sys.stderr)
    else:
        for evidence in evidence_rows:
            print(json.dumps(evidence, ensure_ascii=False))

    if args.verbose:
        print(f"\n完成: {len(evidence_rows)} 条证据", file=sys.stderr)


if __name__ == "__main__":
    main()
