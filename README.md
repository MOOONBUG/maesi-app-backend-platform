# 迈思企业知识库智能问答系统（MaesiInfo AI RAG System）

基于 **FastAPI + MySQL + Vue 3** 构建的企业 RAG 知识库问答系统，支持知识库检索、来源溯源、Bearer Token 鉴权、多 API Key 故障切换及 SSE 流式回答。

## 核心文件

```text
index.html              前端页面
rag_service.py          RAG FastAPI 后端
main_api.py             其他 API 服务代码
.env                    非敏感运行配置
.env.secrets            敏感配置，禁止分享或提交 Git
start.bat               可见窗口一键启动
start.vbs               静默一键启动
acceptance_test.py      端到端验收脚本
启动与注意事项.md       完整启动、验收、排障和安全说明
文档注意事项.txt        知识库录入与运维原则
```

## 快速启动

### 1. 安装依赖

```powershell
cd /d "D:\数据图表类工具\MySQL数据"
python -m pip install -r requirements.txt
```

### 2. 检查配置

确保项目根目录存在：

```text
.env
.env.secrets
```

`.env.secrets` 必须包含数据库密码、模型 API Key 和接口 Bearer Token。不要把真实密钥写入 README 或提交到 Git。

### 3. 启动

直接双击：

```text
start.vbs
```

需要查看后端窗口时双击：

```text
start.bat
```

也可手动启动：

```powershell
python -m uvicorn rag_service:app --host 127.0.0.1 --port 8000
```

### 4. 检查

健康检查：

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/ready
```

完整验收：

```powershell
python acceptance_test.py
```

有效知识库问题应返回 `mode=llm`；没有相关知识时应返回 `mode=no_match`。

## 详细说明

请阅读：

- **[启动与注意事项.md](启动与注意事项.md)**：启动、关闭、健康检查、验收、排障和敏感配置管理；
- **文档注意事项.txt**：知识库录入、检索优化、权限和运维原则。

## 安全提醒

- 禁止分享或提交 `.env.secrets`；
- 不要在日志、截图、聊天或文档中粘贴真实密钥；
- 密钥泄露后应立即撤销并重新生成；
- 修改 `.env` 或 `.env.secrets` 后必须重启后端；
- 日志和 `acceptance_results.json` 可能含业务内容，分享前先脱敏。
