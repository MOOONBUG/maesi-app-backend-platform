import os
from typing import Any, Dict, List

import pymysql
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.secrets"), override=True)
app = FastAPI(title="AI Knowledge Base Search API", version="1.1.0")


def env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value in {"your_password", "replace_me", "your_api_key"}:
        raise RuntimeError(f"Missing valid environment variable: {name}")
    return value


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": env_required("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "ai_knowledge_db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": 5,
    "read_timeout": 10,
    "write_timeout": 10,
}


class DocumentQuery(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=2000)


def query_documents(keyword: str) -> List[Dict[str, Any]]:
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            sql = (
                "SELECT id, title, content, created_at FROM kb_document "
                "WHERE title LIKE %s OR content LIKE %s ORDER BY id DESC"
            )
            pattern = f"%{keyword.strip()}%"
            cursor.execute(sql, (pattern, pattern))
            return cursor.fetchall()
    finally:
        if connection is not None:
            connection.close()


@app.get("/")
def health_check() -> Dict[str, str]:
    return {"status": "running", "message": "AI backend is ready"}


@app.post("/api/kb/search")
def search_documents(query: DocumentQuery) -> Dict[str, Any]:
    try:
        results = query_documents(query.keyword)
    except Exception as exc:
        print(f"Database query failed: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Knowledge base is temporarily unavailable",
        ) from exc
    return {
        "code": 200,
        "keyword": query.keyword.strip(),
        "count": len(results),
        "data": results,
    }
