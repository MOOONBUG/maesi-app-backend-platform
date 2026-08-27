import json
import pymysql
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# 配置 CORS 跨域白名单
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "ai_knowledge_db",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

OPENAI_API_KEY = "sk-ZJFE938atAVvnsZ1DPAU7zRc38pGJiBDdzPA8ovCgi8birNk"
OPENAI_BASE_URL = "https://torchai.ai/v1"
LLM_MODEL_NAME = "gpt-5.6-sol"

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)

class RAGRequest(BaseModel):
    question: str
    top_k: int = 3

# 鉴权函数
def verify_token(authorization: str = Header(...)):
    expected_token = "Bearer prod_secure_token_2026"
    if authorization != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/api/v1/ai/rag-stream-chat", dependencies=[Depends(verify_token)])
async def rag_stream_chat(request: RAGRequest):
    matched_docs = []
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            sql = "SELECT id, title, content FROM kb_document WHERE title LIKE %s OR content LIKE %s LIMIT %s"
            like_pattern = f"%{request.question}%"
            cursor.execute(sql, (like_pattern, like_pattern, request.top_k))
            matched_docs = cursor.fetchall()
        connection.close()
    except Exception as e:
        print(f"数据库查询异常: {str(e)}")

    def event_generator():
        try:
            # 1. 优先推送关联数据源
            yield f"data: {json.dumps({'type': 'sources', 'data': matched_docs}, ensure_ascii=False)}\n\n"
            
            # 2. 知识库未命中直接拦截，不传给 LLM
            if not matched_docs:
                reject_msg = "当前迈思知识库中暂无相关文档记载，无法回答与知识库无关的问题。"
                yield f"data: {json.dumps({'type': 'content', 'data': reject_msg}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                return

            # 3. 命中知识库，严格约束边界调用 LLM
            context_str = "\n".join([f"【文档{i+1}】{doc.get('content', '')}" for i, doc in enumerate(matched_docs)])
            system_prompt = (
                "你是迈思信息（MaesiInfo）研发的企业知识库 RAG 智能助手。\n"
                "【严格回答原则】：\n"
                "1. 你只能基于提供的【上下文】解答企业内部相关问题。\n"
                "2. 绝对禁止回答写小说、闲聊、编写无关代码、解答非知识库范围的内容。\n"
                "3. 绝对不能提及 OpenAI、ChatGPT、GPT 或任何第三方底层模型名称。"
            )
            user_prompt = f"上下文：\n{context_str}\n\n问题：{request.question}"

            stream = client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        payload = json.dumps({"type": "content", "data": delta}, ensure_ascii=False)
                        yield f"data: {payload}\n\n"
                    
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
        except Exception as stream_err:
            error_payload = json.dumps({"type": "error", "message": str(stream_err)}, ensure_ascii=False)
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rag_service:app", host="127.0.0.1", port=8000, reload=True)