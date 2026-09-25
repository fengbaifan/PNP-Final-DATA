#!/usr/bin/env python3
"""verify_collect_* 系列共享的采集基座。

各服务 collector 只需实现 Adapter（search / evaluate / build_evidence + 服务元数据），
公共的 frontmatter 解析、请求重试、CLI、批量编排与 evidence 写回都在这里。
"""
from __future__ import annotations

import argparse
import re
import sys
import time
import unicodedata
from pathlib import Path

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
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "PNP-Knowledge-Distillation/5.3 (+https://github.com/fengbaifan/PNP-Final-DATA)",
}
HTTP_TIMEOUT = 25
MAX_API_RETRIES = 2
REQUEST_DELAY = 0.15


def extract_frontmatter(text: str) -> str:
    match = re.search(r"^﻿?---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    return match.group(1).strip("\n") if match else ""


def scalar_fm(fm: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
    return match.group(1).strip().strip('"').strip("'") if match else ""


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value or "")
    asciiish = "".join(char for char in decomposed if not unicodedata.combining(char))
    asciiish = re.sub(r"[^a-z0-9]+", " ", asciiish.lower())
    return re.sub(r"\s+", " ", asciiish).strip()


def request_json(url: str, params: dict, *, stage: str) -> tuple[dict | None, dict | None]:
    """通用 GET + 指数退避重试，返回 (json_dict | None, error_dict | None)。"""
    if not requests:
        return None, {"stage": stage, "error_type": "missing_dependency", "attempts": 0, "retryable": False}
    last_error: dict | None = None
    for attempt in range(1, MAX_API_RETRIES + 2):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=HTTP_TIMEOUT)
            if response.status_code == 200:
                return response.json(), None
            retryable = response.status_code == 429 or response.status_code >= 500
            last_error = {
                "stage": stage,
                "error_type": "http_error",
                "http_status": response.status_code,
                "attempts": attempt,
                "retryable": retryable,
            }
            if not retryable or attempt > MAX_API_RETRIES:
                break
        except Exception as exc:
            last_error = {
                "stage": stage,
                "error_type": type(exc).__name__,
                "message": str(exc)[:300],
                "attempts": attempt,
                "retryable": True,
            }
            if attempt > MAX_API_RETRIES:
                break
        time.sleep(min(2 ** (attempt - 1), 4))
    return None, last_error


class Adapter:
    """各服务需提供的字段与方法。"""

    name: str = ""
    description: str = ""
    # 目录名 -> 类型（如 {"terms": "term", "procedures": "procedure"}）；空则不过滤
    type_aliases: dict[str, str] = {}

    def accepts(self, ku_type: str) -> bool:
        raise NotImplementedError

    def search(self, label: str, ku_type: str, fm: str, path: Path) -> tuple[dict | None, dict | None]:
        raise NotImplementedError

    def evaluate(self, label: str, ku_type: str, fm: str, path: Path, payload: dict | None) -> tuple[dict | None, list[dict], str | None]:
        raise NotImplementedError

    def build_evidence(
        self,
        path: Path,
        ku_type: str,
        label: str,
        fm: str,
        best: dict | None,
        candidates: list[dict],
        blocking_reason: str | None,
        payload: dict | None,
        collection_error: dict | None,
    ) -> dict:
        raise NotImplementedError


def ku_type_of(path: Path, fm: str, adapter: Adapter) -> str:
    return scalar_fm(fm, "type").lower() or adapter.type_aliases.get(path.parent.name, "")


def collect_one(adapter: Adapter, path: Path, verbose: bool = False) -> dict | None:
    fm = extract_frontmatter(path.read_text(encoding="utf-8"))
    if not fm:
        return None
    ku_type = ku_type_of(path, fm, adapter)
    if not adapter.accepts(ku_type):
        raise ValueError(f"{adapter.name} collector 不接受 {ku_type}：{path}")
    label = scalar_fm(fm, "name_en") or scalar_fm(fm, "title_original") or scalar_fm(fm, "title")
    payload, collection_error = adapter.search(label, ku_type, fm, path)
    best, candidates, blocking_reason = adapter.evaluate(label, ku_type, fm, path, payload)
    if collection_error:
        blocking_reason = "api_error"
    evidence = adapter.build_evidence(path, ku_type, label, fm, best, candidates, blocking_reason, payload, collection_error)
    if verbose:
        print(f"[{ku_type}] {label}: {blocking_reason or 'candidate'} {evidence.get('matched_title', '')}", file=sys.stderr)
    return evidence


def run(adapter: Adapter) -> int:
    parser = argparse.ArgumentParser(description=adapter.description)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--ku")
    scope.add_argument("--input-result", type=Path)
    parser.add_argument("--checkpoint", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.checkpoint and not args.input_result:
        parser.error("--checkpoint 只能与 --input-result 一起使用")
    if args.ku:
        target = resolve_single_target(args.ku, UNITS)
        if not target:
            parser.error(f"未找到 KU：{args.ku}")
        files = [target]
    else:
        files = load_result_targets(resolve(args.input_result, BASE), BASE, UNITS, args.checkpoint)
    invalid = [path for path in files if not adapter.accepts(ku_type_of(path, extract_frontmatter(path.read_text(encoding="utf-8")), adapter))]
    if invalid:
        parser.error(f"{adapter.name} collector 收到不接受的目标：{invalid[0]}")
    if args.dry_run:
        print(f"targets={len(files)} checkpoint={args.checkpoint or 'all'} output={args.output}")
        return 0
    rows = []
    for path in files:
        evidence = collect_one(adapter, path, verbose=args.verbose)
        if evidence:
            rows.append(evidence)
        time.sleep(REQUEST_DELAY)
    output = resolve(args.output, BASE)
    write_jsonl(rows, output)
    print(f"evidence={output.relative_to(BASE) if output.is_relative_to(BASE) else output}")
    print(f"rows={len(rows)}")
    print(f"blocked={sum(bool(row.get('blocking_reason')) for row in rows)}")
    print(f"candidates={sum(not row.get('blocking_reason') for row in rows)}")
    return 0
