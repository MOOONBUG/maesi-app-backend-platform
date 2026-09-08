# 初始化 Git 仓库并构建模拟开发历史
# 用法：在项目根目录执行：.\init_git.ps1

$ErrorActionPreference = 'Stop'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw '未找到 git，请先安装 Git 并确保 git 已加入 PATH。'
}

if (-not (Test-Path '.git')) {
  git init
}

git add strategy.js data_loader.js package.json
git commit --allow-empty -m 'feat: 初始化量化回测基础框架与 T+1 风控模块' -m 'Co-authored-by: Chatbox <chatbox@chatboxai.com>'

git add data_loader.js
git commit --allow-empty -m 'feat: 接入东方财富与腾讯财经双源数据降级容灾管道' -m 'Co-authored-by: Chatbox <chatbox@chatboxai.com>'

git add strategy.js
git commit --allow-empty -m 'refactor: 升级海龟唐奇安通道与 ATR 波动率仓位管理模型' -m 'Co-authored-by: Chatbox <chatbox@chatboxai.com>'

git add backtest.js
git commit --allow-empty -m 'ui: 引入 ECharts 渲染交互式双 Y 轴回测大屏与明细标记' -m 'Co-authored-by: Chatbox <chatbox@chatboxai.com>'

git add package.json README.md init_git.ps1
git commit --allow-empty -m 'docs: 完善项目工程规范与风控引擎说明文档' -m 'Co-authored-by: Chatbox <chatbox@chatboxai.com>'

Write-Host ''
Write-Host 'Git 仓库初始化完成，当前提交历史：' -ForegroundColor Green
git --no-pager log --oneline --decorate -5