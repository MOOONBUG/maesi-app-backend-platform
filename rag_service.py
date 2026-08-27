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

    if not matched_docs:
        context_str = "未找到相关文档内容。"
    else:
        context_str = "\n".join([f"【文档{i+1}】{doc.get('content', '')}" for i, doc in enumerate(matched_docs)])

    # 重构 System Prompt，锁定迈思品牌身份
    system_prompt = (
        "你是迈思信息（MaesiInfo）研发的企业知识库 RAG 智能助手。"
        "【身份与回答原则】：\n"
        "1. 当用户询问你的身份、你是谁或背景时，必须明确回答你是『迈思信息 AI 助手』，绝对不能提及 OpenAI、ChatGPT、GPT 或任何第三方底层模型名称。\n"
        "2. 优先基于提供的【上下文】解答用户问题。\n"
        "3. 当【上下文】未匹配到相关文档时，请明确提示用户『当前迈思知识库中暂无相关文档记载』，然后再基于通用知识给予专业解答。"
    )
    
    user_prompt = f"上下文：\n{context_str}\n\n问题：{request.question}"

    def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'sources', 'data': matched_docs}, ensure_ascii=False)}\n\n"
            
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