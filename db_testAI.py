import pymysql

# 1. 建立与 MySQL 数据库的连接
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='ai_knowledge_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # 2. 编写查询 SQL：把系统用户全查出来
        sql = "SELECT id, username, role, created_at FROM sys_user"
        cursor.execute(sql)
        
        # 3. 获取所有查询结果
        result = cursor.fetchall()
        print("--- 成功从 MySQL 读取到以下用户数据 ---")
        for row in result:
            print(f"用户ID: {row['id']}, 账号: {row['username']}, 角色: {row['role']}")
            
finally:
    # 4. 关闭数据库连接，释放资源
    connection.close()