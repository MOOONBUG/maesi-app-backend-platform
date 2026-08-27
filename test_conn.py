import json
import os
import time
import requests
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "").strip()
base_url = os.getenv("OPENAI_BASE_URL", "https://torchai.ai/v1").strip()
model = os.getenv("LLM_MODEL_NAME", "gpt-5.6-sol").strip()
if not api_key or api_key in {"your_api_key", "replace_me"}:
    raise RuntimeError("璇峰厛鍦?.env 閰嶇疆 OPENAI_API_KEY")
client = OpenAI(api_key=api_key, base_url=base_url)
SERVER_URL = "http://127.0.0.1:8000"
def wait_for_server(url: str, timeout: int = 15) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(f"{url}/docs", timeout=1).status_code == 200:
                return True
        except requests.RequestException:
            time.sleep(0.5)
    return False
if __name__ == "__main__":
    if not wait_for_server(SERVER_URL):
        raise RuntimeError("鍚庣鏈嶅姟鍚姩瓒呮椂")
    token = os.getenv("BEARER_TOKEN", "").strip()
    if not token:
        raise RuntimeError("璇峰厛鍦?.env 閰嶇疆 BEARER_TOKEN")
    response = requests.post(
        f"{SERVER_URL}/api/v1/ai/rag-stream-chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "RAG", "top_k": 3},
        stream=True,
        timeout=60,
    )
    print(f"Status Code: {response.status_code}")
    for line in response.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            print(json.loads(line[6:]))
