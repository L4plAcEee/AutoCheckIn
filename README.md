# 基于 GitHub Action 的自动任务仓库~

---
## [Bing Search Auto Check-In](/BingSearchPoints/README.md)
### 介绍
这是一个使用 **Selenium** 自动执行 Bing 搜索积分的 Python 脚本，支持在本地或 GitHub Actions 等 CI 环境中运行。通过注入 Bing 账号的 cookies，完成自动搜索任务，从而累积积分。

### 功能
* 自动使用指定关键词搜索 Bing
* 支持自定义搜索次数和随机等待
* 注入账号 cookie，无需手动登录
* 支持在 **headless** 模式下运行（适合 CI/CD）
* 兼容多种浏览器二进制和 chromedriver 路径
* 自动规范化 cookies，支持多种导出格式（JSON、Python 列表、Netscape 等）
---
