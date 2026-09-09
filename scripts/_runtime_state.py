#!/usr/bin/env python3
"""批次内运行状态。

运行状态只属于一个 work package。调用方必须显式提供状态文件、批次 ID 和
输入指纹；本模块不再读写仓库级全局状态，也不兼容第二套 agent/plan 状态机。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


VALID_STATUSES = {"running", "completed", "failed", "blocked"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _default_state(batch_id: str, input_fingerprint: str) -> dict:
    return {
        "batch_id": batch_id,
        "status": "running",
        "current_stage": "initialized",
        "updated_at": _now(),
        "events": [],
        "processed_items": [],
        "failed_items": [],
        "input_fingerprint": input_fingerprint,
    }


class RuntimeState:
    """读写一个符合 runtime-state-machine.md 的批次状态文件。"""

    def __init__(
        self,
        *,
        state_path: Path,
        batch_id: str | None = None,
        input_fingerprint: str | None = None,
    ) -> None:
        self._path = Path(state_path)
        if self._path.exists():
            self._data = json.loads(self._path.read_text(encoding="utf-8-sig"))
            self._validate()
            if batch_id and self._data["batch_id"] != batch_id:
                raise ValueError(
                    f"state batch mismatch: {self._data['batch_id']} != {batch_id}"
                )
            if input_fingerprint:
                self.assert_input_fingerprint(input_fingerprint)
        else:
            if not batch_id or not input_fingerprint:
                raise ValueError(
                    "new runtime state requires batch_id and input_fingerprint"
                )
            self._data = _default_state(batch_id, input_fingerprint)
            self._save()

    def _validate(self) -> None:
        required = {
            "batch_id",
            "status",
            "current_stage",
            "updated_at",
            "events",
            "processed_items",
            "failed_items",
            "input_fingerprint",
        }
        missing = sorted(required - set(self._data))
        if missing:
            raise ValueError(f"runtime state missing fields: {missing}")
        if self._data["status"] not in VALID_STATUSES:
            raise ValueError(f"invalid runtime status: {self._data['status']!r}")
        for field in ("events", "processed_items", "failed_items"):
            if not isinstance(self._data[field], list):
                raise ValueError(f"runtime state {field} must be a list")

    def _save(self) -> None:
        self._data["updated_at"] = _now()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(self._path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self._path)

    def assert_input_fingerprint(self, expected: str) -> None:
        actual = self._data["input_fingerprint"]
        if actual != expected:
            raise ValueError(
                f"runtime input fingerprint mismatch: {actual} != {expected}"
            )

    def _event(self, event: str, **details: object) -> None:
        record = {"at": _now(), "event": event}
        record.update(details)
        self._data["events"].append(record)

    def start(self, stage: str) -> None:
        self._data["status"] = "running"
        self._data["current_stage"] = stage
        self._event("stage_started", stage=stage)
        self._save()

    def checkpoint(self, name: str) -> None:
        self._event("checkpoint", name=name)
        self._save()

    def track_progress(
        self,
        _item_index: int,
        item_id: str,
        success: bool,
        detail: str | None = None,
    ) -> None:
        if success:
            if item_id not in self._data["processed_items"]:
                self._data["processed_items"].append(item_id)
            self._data["failed_items"] = [
                value for value in self._data["failed_items"] if value != item_id
            ]
            self._event("item_processed", item_id=item_id)
        else:
            if item_id not in self._data["failed_items"]:
                self._data["failed_items"].append(item_id)
            self._event("item_failed", item_id=item_id, detail=detail or "")
        self._save()

    def complete(self, stage: str) -> None:
        if self._data["failed_items"]:
            raise ValueError("cannot complete a batch with failed_items")
        self._data["status"] = "completed"
        self._data["current_stage"] = stage
        self._event("stage_completed", stage=stage)
        self._save()

    def fail(self, stage: str, message: str, *, blocked: bool = False) -> None:
        self._data["status"] = "blocked" if blocked else "failed"
        self._data["current_stage"] = stage
        self._event("stage_blocked" if blocked else "stage_failed", stage=stage, detail=message)
        self._save()

    def can_resume(self) -> bool:
        return self._data["status"] in {"running", "failed", "blocked"}

    def resume_info(self) -> dict:
        return {
            "batch_id": self._data["batch_id"],
            "status": self._data["status"],
            "current_stage": self._data["current_stage"],
            "processed_items": list(self._data["processed_items"]),
            "failed_items": list(self._data["failed_items"]),
            "input_fingerprint": self._data["input_fingerprint"],
        }

    def resume(self, expected_input_fingerprint: str, stage: str) -> dict:
        self.assert_input_fingerprint(expected_input_fingerprint)
        if not self.can_resume():
            raise ValueError(f"runtime state is not resumable: {self._data['status']}")
        previous = self.resume_info()
        self.start(stage)
        self._event("resumed", previous_status=previous["status"])
        self._save()
        return previous

    def get_processed_items(self) -> set[str]:
        return set(self._data["processed_items"])

    def get_progress_index(self) -> int:
        return len(self._data["processed_items"]) - 1

    @property
    def data(self) -> dict:
        return self._data


def check_resumable(
    state_path: Path,
    *,
    expected_input_fingerprint: str | None = None,
) -> dict | None:
    path = Path(state_path)
    if not path.is_file():
        return None
    state = RuntimeState(state_path=path)
    if expected_input_fingerprint:
        state.assert_input_fingerprint(expected_input_fingerprint)
    return state.resume_info() if state.can_resume() else None
