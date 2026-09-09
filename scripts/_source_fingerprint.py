#!/usr/bin/env python3
"""Shared source-fingerprint primitives for compact ingest packages."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


FINGERPRINT_MODE = "text_crlf_to_lf_v1"


def canonical_source_bytes(path: Path) -> bytes:
    """Return checkout-independent bytes for a Git-governed text source.

    Git may materialize the same tracked text as LF or CRLF on different
    platforms. Canonicalizing only CRLF preserves encoding, BOM and all other
    content bytes while preventing checkout policy from reopening ingest.
    """
    return path.read_bytes().replace(b"\r\n", b"\n")


def source_sha256(path: Path) -> str:
    """Return the repository-canonical source fingerprint.

    LF and CRLF checkouts are equivalent. Encoding, BOM, lone CR bytes and
    every non-line-ending content change remain fingerprint-significant.
    """
    return f"sha256:{hashlib.sha256(canonical_source_bytes(path)).hexdigest()}"


def aggregate_input_fingerprint(
    source_assets: list[dict],
    fingerprint_mode: str = FINGERPRINT_MODE,
) -> str:
    """Build a stable fingerprint from sorted paths and canonical hashes."""
    payload = {
        "fingerprint_mode": fingerprint_mode,
        "source_assets": [
            {"path": str(item.get("path") or ""), "sha256": str(item.get("sha256") or "")}
            for item in sorted(source_assets, key=lambda item: str(item.get("path") or ""))
        ],
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def source_assets_state(manifest: dict, root: Path) -> dict:
    """Resolve the effective ingest state without mutating historical artifacts."""
    declared_status = str(manifest.get("status") or "unknown")
    issues: list[str] = []
    declared_mode = manifest.get("fingerprint_mode")
    if declared_mode != FINGERPRINT_MODE:
        issues.append(f"manifest fingerprint_mode must be {FINGERPRINT_MODE}")
    assets = manifest.get("source_assets")
    if not isinstance(assets, list) or not assets:
        issues.append("manifest source_assets must be a non-empty list")
        return {
            "declared_status": declared_status,
            "effective_status": "reopened_source_drift",
            "fingerprint_mode": declared_mode,
            "input_fingerprint": manifest.get("input_fingerprint"),
            "current_input_fingerprint": None,
            "assets_total": 0,
            "assets_matching": 0,
            "issues": issues,
        }

    checked_assets: list[dict] = []
    matching = 0
    root_resolved = root.resolve()
    for number, item in enumerate(assets, start=1):
        if not isinstance(item, dict):
            issues.append(f"source_assets[{number}] must be an object")
            continue
        rel = str(item.get("path") or "")
        expected = str(item.get("sha256") or "")
        if not rel:
            issues.append(f"source_assets[{number}].path is required")
            continue
        path = (root / rel).resolve()
        try:
            path.relative_to(root_resolved)
        except ValueError:
            issues.append(f"source asset is outside workspace: {rel}")
            continue
        current = source_sha256(path) if path.is_file() else None
        checked_assets.append({"path": rel, "sha256": current or "missing"})
        if not expected.startswith("sha256:"):
            issues.append(f"source asset fingerprint missing: {rel}")
        elif current is None:
            issues.append(f"source asset missing: {rel}")
        elif current != expected:
            issues.append(f"source asset hash drift: {rel}")
        else:
            matching += 1

    current_input = aggregate_input_fingerprint(checked_assets) if len(checked_assets) == len(assets) else None
    declared_input = manifest.get("input_fingerprint")
    if not isinstance(declared_input, str) or not declared_input.startswith("sha256:"):
        issues.append("manifest input_fingerprint is required")
    elif current_input != declared_input:
        issues.append("manifest input_fingerprint does not match current source assets")

    return {
        "declared_status": declared_status,
        "effective_status": "reopened_source_drift" if issues else declared_status,
        "fingerprint_mode": declared_mode,
        "input_fingerprint": declared_input,
        "current_input_fingerprint": current_input,
        "assets_total": len(assets),
        "assets_matching": matching,
        "issues": issues,
    }
