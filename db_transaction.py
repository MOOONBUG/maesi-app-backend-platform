import os

import pymysql
from dotenv import load_dotenv

load_dotenv()

connection = pymysql.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "ai_knowledge_db"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

try:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO kb_document (title, content) VALUES (%s, %s)",
            ("Production architecture guidelines", "Database pool and transaction isolation guidelines."),
        )
        cursor.execute(
            "INSERT INTO sys_user (username, role) VALUES (%s, %s)",
            ("system_auditor", "auditor"),
        )
    connection.commit()
    print("Transaction committed")
except Exception as exc:
    connection.rollback()
    print(f"Transaction rolled back: {exc}")
    raise
finally:
    connection.close()
