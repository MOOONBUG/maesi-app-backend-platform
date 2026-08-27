import os
from pathlib import Path

candidates = list(Path('D:/').rglob('rag_service.py'))
if not candidates:
    raise SystemExit('rag_service.py not found')
path = candidates[0]
text = path.read_text(encoding='utf-8-sig')
if 'from data_pool import search_pool' not in text:
    text = text.replace('from pydantic import BaseModel, Field\n', 'from pydantic import BaseModel, Field\nfrom data_pool import search_pool\n')
old = '''def query_documents(question: str, top_k: int) -> List[Dict[str, Any]]:
    terms = extract_terms(question)
    if not terms: return []
    connection = pymysql.connect(**DB_CONFIG)'''
new = '''def query_documents(question: str, top_k: int) -> List[Dict[str, Any]]:
    terms = extract_terms(question)
    if not terms: return []
    # 本地开放数据池作为只读补充源：无需修改 MySQL 权限即可接入演示数据
    pool_docs = search_pool(terms, top_k=max(top_k, 3))
    connection = pymysql.connect(**DB_CONFIG)'''
if old not in text:
    raise SystemExit('query start pattern not found')
text = text.replace(old, new, 1)
old2 = '''        docs.sort(key=lambda x: (x["_score"], len(x["_matched"])), reverse=True)
        return docs[:top_k]
    finally: connection.close()'''
new2 = '''        docs.extend(pool_docs)
        # 同一标题去重，优先保留命中得分更高的来源
        unique = {}
        for doc in docs:
            key = str(doc.get("title", ""))
            if key not in unique or doc.get("_score", 0) > unique[key].get("_score", 0):
                unique[key] = doc
        docs = list(unique.values())
        docs.sort(key=lambda x: (x.get("_score", 0), len(x.get("_matched", []))), reverse=True)
        return docs[:top_k]
    finally: connection.close()'''
if old2 not in text:
    raise SystemExit('query end pattern not found')
text = text.replace(old2, new2, 1)
path.write_text(text, encoding='utf-8')
print(path)
