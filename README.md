# MAESI APP 后端服务平台

**Maesi App Backend Platform** 是一个面向 APP 后端工程岗位的可运行型技术作品集项目，围绕 **FastAPI + MySQL + Vue 3 + Go + Kubernetes** 展示 AI 知识库问答、流式接口、GPU 运维诊断和后端工程化能力。

> 本项目用于技术作品集、岗位评审和本地演示。仓库只提交示例配置和源代码；真实数据库密码、模型 API Key、Bearer Token 以及业务数据均保留在本地，不进入 Git。

## 项目能力

- **RAG 知识库问答**：基于 MySQL 知识库检索，支持来源引用、无匹配门禁和 SSE 流式响应。
- **安全接口**：统一 Bearer Token 鉴权，多 API Key 切换，敏感配置通过环境变量注入。
- **GPU 运维入口**：只读采集 NVIDIA 主机状态，提供显存问题诊断记录和降级处理。
- **APP 后端工程实践**：FastAPI 健康检查、超时控制、事务与权限设计、Go Gateway、幂等接口和 Kubernetes 清单。
- **可验证交付**：包含 Python 语法检查、Go race detector、端到端验收和 GPUOps 验收脚本。

## 主要入口

| 路径 | 作用 |
|---|---|
| `rag_service.py` | FastAPI RAG、鉴权、SSE 和 GPUOps API |
| `index.html` | 本地演示前端和 GPU 运维入口 |
| `gpuops_console.html` | GPU 快照与诊断记录控制台 |
| `gateway/cmd/app-gateway` | Go HTTP Gateway 演示 |
| `deploy/k8s/app-gateway.yaml` | Kubernetes 部署、Service、HPA、探针和 NetworkPolicy |
| `.env.example` | 可公开提交的配置模板，不含真实密钥 |
| `acceptance_test.py` | RAG 接口端到端验收 |
| `gpuops_acceptance.py` | GPUOps 场景验收 |
| `启动与注意事项.md` | Windows 本地启动、排障和运行说明 |

## 快速开始（Windows）

### 1. 安装依赖

建议使用 Python 3.10+、MySQL 8.x、Go 1.23+。GPU 功能需要 NVIDIA 驱动和可用的 `nvidia-smi`；没有 GPU 时，主服务仍可运行，但 GPU 快照会返回不可用状态。

```powershell
cd /d "D:\数据图表类工具\MySQL数据"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. 创建本地配置

```powershell
Copy-Item .env.example .env
```

在项目根目录保留本地 `.env.secrets`，写入真实敏感配置：

```env
DB_PASSWORD=本地数据库密码
OPENAI_API_KEY=主模型APIKey
OPENAI_API_KEYS=主Key,备用Key
BEARER_TOKEN=本地接口Token
```

`.env`、`.env.secrets`、日志、验收结果和本地备份均不提交 Git。不要把真实密钥放入 README、Issue、截图、日志或聊天记录。

### 3. 初始化诊断表（可选）

需要保存 GPU 诊断记录时，使用数据库管理员账号执行：

```sql
SOURCE sql_gpuops_diagnostics.sql;
GRANT SELECT, INSERT, UPDATE ON ai_knowledge_db.diagnostic_record TO 'rag_app'@'127.0.0.1';
```

请按实际数据库名、账号和权限策略调整，管理员密码不要写入项目文件。

### 4. 启动服务

静默启动并打开本地页面：双击 `start.vbs`。需要查看后端窗口和实时错误时：双击 `start.bat`。

也可以手动启动：

```powershell
python -m uvicorn rag_service:app --host 127.0.0.1 --port 8000
```

### 5. 验证流程

1. 打开 `http://127.0.0.1:8000/health`，确认服务存活；
2. 打开 `http://127.0.0.1:8000/health/ready`，确认数据库、知识库和模型配置就绪；
3. 打开 `index.html`，在页面中填写本地 Token 后测试问答；
4. 执行 RAG 验收：`python acceptance_test.py`；
5. 执行 GPUOps 验收：`python gpuops_acceptance.py`。

有效知识库问题预期返回 `mode=llm`；无相关知识的问题应返回 `mode=no_match`。MySQL 不可用时，GPU 诊断接口按设计返回降级状态，不阻塞主服务。

## API 入口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 存活检查 |
| GET | `/health/ready` | 数据库、知识库和模型就绪检查 |
| POST | `/api/v1/ai/rag-stream-chat` | SSE 流式 RAG 问答，需要 Bearer Token |
| GET | `/api/v1/ops/gpu-snapshot` | 只读 GPU 主机快照，需要 Bearer Token |
| POST | `/api/v1/ops/diagnostics` | 创建 GPU 诊断记录，需要 Bearer Token |
| GET | `/api/v1/ops/diagnostics?limit=20` | 查询诊断记录，需要 Bearer Token |

## 质量检查

```powershell
python -m py_compile rag_service.py gpu_ops.py gpuops_acceptance.py acceptance_test.py
Set-Location gateway
go test -race ./...
Set-Location ..
git diff --check
```

GitHub Actions 会在 Push 和 Pull Request 中执行 Python 语法检查及 Go race detector。

## 安全与本地文件策略

可提交内容包括源代码、脱敏配置模板、SQL 结构、Kubernetes 清单、测试脚本和通用文档；不可提交内容包括 `.env`、`.env.secrets`、数据库导出、日志、验收输出、密钥、Token 和业务知识库内容。

本地备份目录（包括 `.repair-backup-*`）不会被清除，仅由 Git 忽略。若密钥曾经进入 Git、网盘或聊天记录，应先撤销并重新生成；仅删除当前文件不能清除 Git 历史风险。详见 [SECURITY.md](SECURITY.md)。

## 项目边界

这是一个可运行的工程化演示项目，不将尚未在真实 AWS 或生产集群验证的能力包装成生产经验。GPU 指标当前以 `nvidia-smi` 只读采集为主，生产环境可进一步接入 DCGM Exporter、Prometheus 和 Grafana。

## 知识产权

This is a source-available portfolio project for portfolio review and recruitment technical evaluation. Access and review do not transfer intellectual-property rights. Copying, deployment, commercial use, or internal business use requires prior written permission.
