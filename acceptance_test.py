import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
URL = "http://127.0.0.1:8000/api/v1/ai/rag-stream-chat"
HEADERS = {"Authorization": "Bearer " + os.getenv("BEARER_TOKEN", "")}
CASES = [
    ("finance", "\u5206\u6790\u4e00\u4e0b2026\u5e748\u6708\u7684\u7ecf\u8425\u8868\u73b0\u3002", []),
    ("region", "1\u6708\u81f38\u6708\u5404\u533a\u57df\u9500\u552e\u60c5\u51b5\u5982\u4f55\uff1f\u8bf7\u8fdb\u884c\u6392\u540d\u548c\u6bd4\u8f83\u3002", []),
    ("inventory", "\u5e93\u5b58\u6709\u4ec0\u4e48\u98ce\u9669\uff1f\u4e0d\u8981\u53ea\u544a\u8bc9\u6211\u662f\u5426\u9884\u8b66\u3002", []),
    ("sla", "\u5ba2\u6237\u670d\u52a1SLA\u662f\u5426\u8fbe\u6807\uff1f\u6709\u54ea\u4e9b\u503c\u5f97\u5173\u6ce8\u7684\u95ee\u9898\uff1f", []),
    ("followup", "\u6bd4\u7b2c\u4e8c\u540d\u9ad8\u591a\u5c11\uff1f", [
        {"role": "user", "content": "1\u6708\u81f38\u6708\u54ea\u4e2a\u533a\u57df\u9500\u552e\u989d\u6700\u9ad8\uff1f"},
        {"role": "assistant", "content": "\u534e\u4e1c\u533a\u57df\u6700\u9ad8\u3002"},
    ]),
    ("no_match", "\u8bf7\u5206\u67902025\u5e74\u540c\u671f\u9884\u7b97\u5b8c\u6210\u7387\u3002", []),
]

results = []
for name, question, history in CASES:
    try:
        response = requests.post(URL, headers=HEADERS, json={"question": question, "top_k": 5, "history": history}, timeout=50)
        events = []
        for block in response.text.split("\n\n"):
            if block.startswith("data: "):
                try:
                    events.append(json.loads(block[6:]))
                except json.JSONDecodeError:
                    pass
        sources = next((event.get("data", []) for event in events if event.get("type") == "sources"), [])
        text = "".join(str(event.get("data", "")) for event in events if event.get("type") == "content")
        done = next((event for event in events if event.get("type") == "done"), {})
        results.append({
            "case": name,
            "http": response.status_code,
            "sources": len(sources),
            "source_ids": [item.get("id") for item in sources],
            "mode": done.get("mode"),
            "done": bool(done),
            "chars": len(text),
            "preview": text[:260],
        })
    except Exception as exc:
        results.append({"case": name, "error": repr(exc)})

with open("acceptance_results.json", "w", encoding="utf-8") as output:
    json.dump(results, output, ensure_ascii=False, indent=2)
print(json.dumps(results, ensure_ascii=True))
