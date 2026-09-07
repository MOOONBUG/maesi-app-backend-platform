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
with open("gpuops_acceptance_results.json", "w", encoding="utf-8") as output:
    json.dump(checks, output, ensure_ascii=False, indent=2)
print(json.dumps(checks, ensure_ascii=False, indent=2))