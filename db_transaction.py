import pymysql

# 建立连接
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='ai_knowledge_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    # 开启事务：默认情况下 Python 的 pymysql 不会自动提交，需要手动管理
    with connection.cursor() as cursor:
        # 1. 模拟业务操作一：插入一条新文档记录
        sql_doc = "INSERT INTO kb_document (title, content) VALUES (%s, %s)"
        cursor.execute(sql_doc, ("生产环境架构设计规范", "本文档详细规定了高并发下的数据库连接池与事务隔离级别..."))
        
        # 2. 模拟业务操作二：更新或插入关联日志（这里演示再插一条用户行为）
        sql_user = "INSERT INTO sys_user (username, role) VALUES (%s, %s)"
        cursor.execute(sql_user, ("系统审计员", "auditor"))

    # 如果上面两步都顺利执行没有报错，提交事务，真正写入数据库
    connection.commit()
    print("事务执行成功：文档与审计日志已全部安全入库！")

except Exception as e:
    # 如果中间任何一个环节报错，立刻回滚，撤销刚才所有的改动
    connection.rollback()
    print(f"检测到异常，事务已全部回滚！错误原因: {e}")

finally:
    # 关闭连接
    connection.close()