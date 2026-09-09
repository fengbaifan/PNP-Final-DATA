#!/usr/bin/env python3
"""
pre_commit_check.py — 提交前规则漂移检测
===========================================
.git/hooks/pre-commit 调用此脚本，在 git commit 前拦截规则漂移。
"""

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    try:
        from scripts.audit_rule_drift import collect_findings

        findings = collect_findings()

        if findings:
            print(f"[pre-commit] ❌ 规则漂移: {len(findings)} 个问题")
            for f in findings[:10]:
                detail = f.get("path") or f.get("skill") or f.get("event") or f.get("file") or f.get("dir") or f.get("script") or "?"
                print(f"           [{f['issue']}] {detail}")
            if len(findings) > 10:
                print(f"           ... 及 {len(findings) - 10} 个")
            print()
            print("  建议操作:")
            print("    1. 修复漂移项")
            print("    2. 运行 python scripts/run_sync_closure.py")
            print("    3. 重新提交")
            return 1

        print("[pre-commit] ✅ 规则漂移: 0 (所有规则文档与磁盘一致)")
        return 0
    except ImportError as e:
        print(f"[pre-commit] ❌ audit_rule_drift 导入失败: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
