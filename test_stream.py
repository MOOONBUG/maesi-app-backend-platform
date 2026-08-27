import time
import requests
import json

# ==================== 1. 探活等待逻辑 ====================
SERVER_URL = "http://127.0.0.1:8000"


def wait_for_server(url, timeout=15):
    print("正在等待后端 API 就绪...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            res = requests.get(f"{url}/docs", timeout=1)
            if res.status_code == 200:
                print("后端服务已连接！开始发送 RAG 测试请求...\n")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    raise RuntimeError("后端服务启动超时，请检查控制台报错！")


# 阻塞直到后端完全起来
wait_for_server(SERVER_URL)


# ==================== 2. 真正的业务测试请求 ====================
url = f"{SERVER_URL}/api/v1/ai/rag-stream-chat"
headers = {
    "Authorization": "Bearer prod_secure_token_2026",
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
                        print(f"\n[命中的知识库文档]: {data.get('data')}")
                        print("\n[AI 回复开始]: ", end="", flush=True)
                    elif msg_type == "content":
                        print(data.get("data"), end="", flush=True)
                    elif msg_type == "done":
                        print("\n\n[流式传输结束]")
                    elif msg_type == "error":
                        print(f"\n[后端捕获到错误]: {data.get('message')}")
                except json.JSONDecodeError:
                    print(f"RAW (Non-JSON): {decoded_line}")
else:
    print(f"请求失败，响应内容: {response.text}")