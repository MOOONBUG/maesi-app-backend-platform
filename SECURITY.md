# Security Policy

## 保护范围

本项目只提交脱敏源代码和配置模板。以下内容必须留在本地：数据库密码、模型 API Key、Bearer Token、数据库导出、日志、验收输出和业务知识库数据。

## 本地配置

1. 复制 `.env.example` 为 `.env`；
2. 在本地 `.env.secrets` 中填写真实密钥；
3. 确认 `.gitignore` 生效后，再执行 `git status`；
4. 提交前执行敏感信息搜索和 `git diff --check`。

## 凭据泄露处理

1. 立即撤销或轮换数据库密码、API Key 和 Bearer Token；
2. 检查 GitHub Actions、日志、Issue、Pull Request 和备份是否包含该凭据；
3. 修复代码和配置，避免只删除当前文件而忽略 Git 历史；
4. 如需清理公开历史，先保留本地备份并制定回滚方案，再单独执行历史重写。

安全问题不要在公开 Issue 中发布，请通过仓库所有者可用的私下渠道报告。
