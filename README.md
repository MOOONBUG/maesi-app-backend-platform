# 迈思企业知识库智能问答系统 (MaesiInfo AI RAG System)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)
![Vue3](https://img.shields.io/badge/Vue.js-3.0+-4FC08D?style=flat&logo=vuedotjs&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

基于 **FastAPI + MySQL + Vue3** 构建的企业级检索增强生成 (RAG) 知识库系统，支持向量检索、流式 HTTP SSE (Server-Sent Events) 增量响应、深浅主题无缝切换，以及极简一键免配置启动。

---

## 🌟 核心特性

- **⚡ 实时流式响应**：采用 SSE (Server-Sent Events) 技术，实现打字机式的实时文本流输出。
- **🔍 知识库溯源**：对话回答中实时附带向量数据库/关系数据库命中的参考文档来源。
- **🛡️ 安全与合规**：内置 API Bearer Token 鉴权机制，预留 PII 敏感数据拦截与并发速率限制（Rate Limit）防护层。
- **🎨 现代化 UI 交互**：全套响应式布局，支持黑白/深浅主题自由切换，自带启动自检无痕加载蒙层。
- **🚀 零门槛启动**：内置 Windows 自动化脚本 (`start.vbs`)，实现后台静默启动服务并自动建立探针校验。

---

## 🛠️ 技术栈

- **后端**：Python / FastAPI / Uvicorn / SQLAlchemy
- **前端**：Vue 3 (Composition API) / Marked.js / Native CSS Custom Properties
- **数据存储**：MySQL
- **工具链**：VBScript (Windows 静默启动与端口清理)

---

## 🚀 快速启动

### 1. 依赖安装

在根目录下创建虚拟环境并安装所需的 Python 依赖包：

```bash
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv

📁 项目目录结构
├── index.html        # Vue3 响应式前端页面（含深浅主题与流式 SSE 解析）
├── rag_service.py    # FastAPI 后端核心服务（流式接口、鉴权与知识库查询）
├── start.vbs         # Windows 一键静默启动与端口管理脚本
├── .env              # 环境变量配置文件
├── .gitignore        # Git 忽略配置
└── README.md         # 项目架构与说明文档