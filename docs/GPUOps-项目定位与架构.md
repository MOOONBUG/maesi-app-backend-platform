# APP 服务端高并发微服务与 AI 运维平台

## 项目定位

这是一个面向 GPU 运维工程师 / AI 基础设施工程师岗位的作品集项目。它不是单纯的聊天页面，而是把以下工作流串起来：

```text
GPU 主机状态采集
→ 告警/故障现象输入
→ 运维知识检索
→ 相关性门禁
→ 诊断步骤生成
→ 原文引用
→ 审计与复盘
```

## 岗位能力映射

| 岗位能力 | 项目中的对应模块 |
|---|---|
| Linux / Shell 排障 | `scripts/`、诊断命令白名单、运行手册 |
| NVIDIA GPU / CUDA | `nvidia-smi` 状态采集、CUDA/驱动知识库 |
| Docker / 容器环境 | 容器故障排查文档、运行参数说明 |
| NVIDIA Container Toolkit | GPU 容器诊断清单 |
| Prometheus / Grafana | GPU 指标字段设计和后续 exporter 接入位 |
| Python 自动化 | FastAPI、采集器、验收脚本 |
| MySQL | 文档元数据、任务、会话、审计与检索日志 |
| 故障响应 | 无命中门禁、诊断步骤、来源引用和审计 |

## 目标架构

```text
Vue 运维控制台
   ├── 知识问答 / 引用
   ├── GPU 主机状态
   ├── 故障诊断记录
   └── 检索调试
          │ REST + SSE
FastAPI
   ├── RAG Query Service
   ├── GPU Ops Service
   ├── Auth / Audit
   └── Health / Readiness
          ├── MySQL：资产、知识库、任务、日志
          ├── GPU Collector：nvidia-smi / DCGM 接入位
          └── LLM：仅在相关性门禁通过后调用
```

## 当前版本边界

- 当前仓库已具备 MySQL 知识库检索、鉴权、SSE 和无关问题拦截基础。
- GPU 指标优先采用本机 `nvidia-smi` 的安全只读采集；没有 NVIDIA 环境时返回明确的 `unavailable`，不伪造数据。
- Prometheus/DCGM、Kubernetes 和多节点调度作为后续增强，不在没有实际环境验证时包装成已完成能力。

## 演示场景

1. 查询“GPU 显存持续升高如何排查”，返回驱动、进程、容器和指标检查步骤及来源。
2. 查询“CUDA 版本与驱动不兼容如何定位”，返回 `nvidia-smi`、容器 runtime 和版本矩阵检查项。
3. 打开 GPU 状态页，查看采集是否可用、GPU 型号、温度、显存和利用率。
4. 输入与运维知识库无关的问题，系统不调用模型并返回 `no_match`。

## 重要说明

项目用于技术作品集和面试演示。真实生产部署还需要 Linux 主机、权限隔离、DCGM exporter、Prometheus、Grafana、告警路由、密钥管理和变更审批。
