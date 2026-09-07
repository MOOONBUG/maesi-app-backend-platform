# GPU 集群运维知识库与智能诊断平台（GPUOps RAG Console）

基于 **FastAPI + MySQL + Vue 3** 构建的 GPU 集群运维知识库与智能诊断平台，面向 GPU 运维/AI 基础设施岗位，支持故障手册检索、来源溯源、Bearer Token 鉴权、多 API Key 故障切换、SSE 流式回答，以及 NVIDIA GPU 主机状态采集与诊断入口。

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

## GPU 运维岗位定位

本项目针对 GPU 运维工程师 / AI 基础设施岗位重构，重点展示：

- Linux、Python 自动化和故障排查思路；
- NVIDIA GPU、CUDA、驱动与容器运行时知识管理；
- MySQL 元数据、任务状态、权限、审计和索引设计；
- RAG 检索门禁、来源引用和不确定性控制；
- `nvidia-smi` 只读状态采集，以及后续 DCGM/Prometheus/Grafana 接入位；
- FastAPI、SSE、健康检查和安全配置。

项目名称：**GPU 集群运维知识库与智能诊断平台（GPUOps RAG Console）**。

详细架构与开源项目学习记录见：

- [GPUOps 项目定位与架构](docs/GPUOps-项目定位与架构.md)
- [开源项目学习与综合应用](docs/开源项目学习与综合应用.md)
## 安全提醒

- 禁止分享或提交 `.env.secrets`；
- 不要在日志、截图、聊天或文档中粘贴真实密钥；
- 密钥泄露后应立即撤销并重新生成；
- 修改 `.env` 或 `.env.secrets` 后必须重启后端；
- 日志和 `acceptance_results.json` 可能含业务内容，分享前先脱敏。

## Usage and intellectual property

This is a source-available portfolio project, not an open-source release. It is provided only for portfolio review and recruitment technical evaluation. Access and review do not transfer intellectual-property rights. Copying, deployment, commercial use, or internal business use requires prior written permission.




## GPUOps 场景验收

```powershell
python gpuops_acceptance.py
```

验收内容：

- 服务健康检查；
- GPU 主机事实状态采集；
- GPU 显存问题诊断记录创建；
- 诊断记录列表查询；
- MySQL 不可用时返回降级状态，不阻塞主服务。

接口：

```text
GET  /api/v1/ops/gpu-snapshot
POST /api/v1/ops/diagnostics
GET  /api/v1/ops/diagnostics?limit=20
```

### GPU 运维控制台

直接打开 gpuops_console.html 可查看 GPU 主机快照和最近诊断记录。后端启动后，页面通过 /api/v1/ops/gpu-snapshot 和 /api/v1/ops/diagnostics 获取数据。


### 数据库迁移

首次启用诊断记录前执行 sql_gpuops_diagnostics.sql 创建 diagnostic_record 表。

主页面左侧的“GPU 主机与诊断”入口会嵌入只读 GPU 运维控制台。

### 诊断记录数据库权限说明

首次启用诊断记录前，需要使用数据库管理员账号执行 `sql_gpuops_diagnostics.sql` 创建 `diagnostic_record` 表；应用账号 `rag_app` 还需要该表的 `SELECT`、`INSERT`、`UPDATE` 权限。当前环境已完成授权，诊断接口验收确认 `persisted=true`，记录可从数据库列表接口读回。

管理员授权示例（请按实际账号和环境调整，不要把管理员密码写入项目文件）：

```sql
SOURCE sql_gpuops_diagnostics.sql;
GRANT SELECT, INSERT, UPDATE ON ai_knowledge_db.diagnostic_record TO 'rag_app'@'127.0.0.1';
FLUSH PRIVILEGES;
```

授权完成后重启后端，并运行 `python gpuops_acceptance.py`；预期创建诊断记录的 `persisted=true`，且列表接口不再出现 `degraded=true`。
