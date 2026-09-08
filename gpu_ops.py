"""Read-only GPU diagnostics adapter.

The collector deliberately uses a short timeout and never fabricates GPU data.
It can be replaced by a DCGM/Prometheus adapter on Linux production hosts.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any, Dict, List


QUERY = [
    "index",
    "name",
    "driver_version",
    "temperature.gpu",
    "utilization.gpu",
    "memory.total",
    "memory.used",
    "memory.free",
    "power.draw",
    "pstate",
]


def collect_gpu_snapshot(timeout_seconds: float = 3.0) -> Dict[str, Any]:
    executable = shutil.which("nvidia-smi")
    if not executable:
        return {
            "status": "unavailable",
            "reason": "nvidia-smi not found; run on an NVIDIA host or configure a DCGM adapter",
            "gpus": [],
        }

    command = [
        executable,
        f"--query-gpu={','.join(QUERY)}",
        "--format=csv,noheader,nounits",
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "reason": "nvidia-smi timeout", "gpus": []}
    except OSError as exc:
        return {"status": "error", "reason": f"cannot execute nvidia-smi: {exc}", "gpus": []}

    if completed.returncode != 0:
        return {
            "status": "error",
            "reason": completed.stderr.strip() or "nvidia-smi failed",
            "gpus": [],
        }

    gpus: List[Dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        values = [value.strip() for value in line.split(",")]
        if len(values) != len(QUERY):
            continue
        item: Dict[str, Any] = dict(zip(QUERY, values))
        item["index"] = _to_int(item["index"])
        for field in QUERY[3:]:
            item[field] = _to_number(item[field])
        gpus.append(item)
    return {"status": "ok", "gpus": gpus, "count": len(gpus)}


def _to_int(value: str) -> Any:
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _to_number(value: str) -> Any:
    try:
        return float(value)
    except (TypeError, ValueError):
        return value
