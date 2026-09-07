import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env.secrets"), override=True)
BASE = os.getenv("GPUOPS_BASE_URL", "http://127.0.0.1:8000")
TOKEN = os.getenv("BEARER_TOKEN", "")
HEADERS = {"Authorization": "Bearer " + TOKEN}
checks = []

def check(name, method, path, **kwargs):
    try:
        response = requests.request(method, BASE + path, headers=HEADERS, timeout=8, **kwargs)
        checks.append({"name": name, "http": response.status_code, "ok": response.ok, "body": response.json()})
    except Exception as exc:
        checks.append({"name": name, "ok": False, "error": repr(exc)})

check("health", "GET", "/health")
check("gpu snapshot", "GET", "/api/v1/ops/gpu-snapshot")
check("create diagnostic", "POST", "/api/v1/ops/diagnostics", json={"question": "GPU 显存持续升高如何排查？", "severity": "WARNING"})
check("list diagnostics", "GET", "/api/v1/ops/diagnostics?limit=5")
# HTTP 200 不等于数据库真正写入；同时检查持久化标志和列表回读。
created = next((item for item in checks if item["name"] == "create diagnostic"), {})
created_data = created.get("body", {}).get("data", {})
listed = next((item for item in checks if item["name"] == "list diagnostics"), {})
listed_data = listed.get("body", {}).get("data", [])
created_id = created_data.get("id")
if created_data.get("persisted") is not True:
    raise SystemExit("FAIL: diagnostic record was not persisted")
if not created_id or not any(item.get("id") == created_id for item in listed_data):
    raise SystemExit("FAIL: persisted diagnostic record cannot be read back")
if listed.get("body", {}).get("degraded"):
    raise SystemExit("FAIL: diagnostics list is degraded")
with open("gpuops_acceptance_results.json", "w", encoding="utf-8") as output:
    json.dump(checks, output, ensure_ascii=False, indent=2)
print(json.dumps(checks, ensure_ascii=False, indent=2))
