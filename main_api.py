from fastapi import FastAPI, HTTPException
import pymysql
from pydantic import BaseModel

app = FastAPI(title="AI 知识库快速检索与后端服务", version="1.0")

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'ai_knowledge_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 接收前端请求的数据模型
class DocumentQuery(BaseModel):
    keyword: str

@app.get("/")
def health_check():
    return {"status": "running", "message": "AI 后端服务已就绪，随时准备对接前端与大模型！"}

# 核心检索接口：面试时必问的 RAG 数据源头接口
@app.post("/api/kb/search")
def search_documents(query: DocumentQuery):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            # 使用模糊查询模拟知识库向量检索前的关键词召回
            sql = "SELECT id, title, content, created_at FROM kb_document WHERE title LIKE %s OR content LIKE %s"
            search_term = f"%{query.keyword}%"
            cursor.execute(sql, (search_term, search_term))
            results = cursor.fetchall()
            return {
                "code": 200,
                "keyword": query.keyword,
                "count": len(results),
                "data": results
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()