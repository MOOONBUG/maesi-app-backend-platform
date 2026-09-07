from gpu_ops import collect_gpu_snapshot

result = collect_gpu_snapshot(timeout_seconds=0.2)
assert result["status"] in {"ok", "unavailable", "error"}
assert isinstance(result.get("gpus"), list)
print(result["status"])
