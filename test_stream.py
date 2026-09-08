import time
import requests
import json
import os

# ==================== 1. 鎺㈡椿绛夊緟閫昏緫 ====================
SERVER_URL = "http://127.0.0.1:8000"


def wait_for_server(url, timeout=15):
    print("姝ｅ湪绛夊緟鍚庣 API 灏辩华...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            res = requests.get(f"{url}/docs", timeout=1)
            if res.status_code == 200:
                print("鍚庣鏈嶅姟宸茶繛鎺ワ紒寮€濮嬪彂閫?RAG 娴嬭瘯璇锋眰...\n")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    raise RuntimeError("backend startup timeout; inspect the server logs")


# 闃诲鐩村埌鍚庣瀹屽叏璧锋潵
wait_for_server(SERVER_URL)


# ==================== 2. 鐪熸鐨勪笟鍔℃祴璇曡姹?====================
url = f"{SERVER_URL}/api/v1/ai/rag-stream-chat"
headers = {
    "Authorization": f"Bearer {os.getenv('BEARER_TOKEN', '')}",
    "Content-Type": "application/json"
}
payload = {
    "question": "RAG",
    "top_k": 3
}

print("Connecting to SSE Stream...")
response = requests.post(url, headers=headers, json=payload, stream=True)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith("data: "):
                raw_json = decoded_line[6:]
                try:
                    data = json.loads(raw_json)
                    msg_type = data.get("type")
                    
                    if msg_type == "sources":
                        print(f"\n[鍛戒腑鐨勭煡璇嗗簱鏂囨。]: {data.get('data')}")
                        print("\n[AI 鍥炲寮€濮媇: ", end="", flush=True)
                    elif msg_type == "content":
                        print(data.get("data"), end="", flush=True)
                    elif msg_type == "done":
                        print("\n\n[娴佸紡浼犺緭缁撴潫]")
                    elif msg_type == "error":
                        print(f"\n[鍚庣鎹曡幏鍒伴敊璇痌: {data.get('message')}")
                except json.JSONDecodeError:
                    print(f"RAW (Non-JSON): {decoded_line}")
else:
    print(f"璇锋眰澶辫触锛屽搷搴斿唴瀹? {response.text}")
