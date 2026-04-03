# SCNet AI 聊天集成指南

本站点集成了国家超算互联网平台（SCNet）的 AI 聊天功能。

## 架构说明

由于浏览器 CORS 安全策略限制，前端无法直接调用 `scnet.cn` 的 API。我们提供三种解决方案：

### 方案 1：本地代理服务器（推荐开发使用）

**优点**: 简单快速，无需部署  
**缺点**: 需要本地运行 Python 脚本

```bash
# 1. 安装依赖
pip install flask flask-cors requests

# 2. 启动代理服务器
python scripts/scnet_proxy.py

# 3. 打开浏览器访问 http://localhost:1313
```

代理服务器特性：
- 自动处理 CORS 头
- 频率限制保护（2秒间隔）
- 流式响应支持
- 健康检查端点: `http://localhost:8787/health`

### 方案 2：部署到 Vercel（推荐生产使用）

**优点**: 无需用户本地运行，全球 CDN  ️
**缺点**: 需要创建 Vercel 账户，token 需定期更新

```bash
# 1. 安装 Vercel CLI
npm i -g vercel

# 2. 登录并部署
vercel --prod
```

部署后自动使用 Edge Functions 代理请求。

### 方案 3：直接使用 SCNet 官网

如果不想设置代理，可以直接访问 SCNet 官网使用 AI 功能：
https://www.scnet.cn/ui/chatbot/

## 前端组件

- **文件**: `static/js/scnet-chat.js`
- **位置**: 首页右下角悬浮按钮 🤖
- **功能**: 
  - 自动检测可用代理
  - 失败时提供清晰的错误提示
  - 赛博朋克风格 UI

## 常见问题

### Q: 为什么显示 "无法连接到 AI 服务"？

A: 请确保已启动本地代理服务器：
```bash
python scripts/scnet_proxy.py
```

### Q: Token 过期怎么办？

A: 需要从 SCNet 网站获取新的 token：
1. 访问 https://www.scnet.cn/ui/chatbot/
2. 打开浏览器开发者工具 (F12)
3. 发送一条消息
4. 在 Network 标签页找到 `chat/completions` 请求
5. 复制请求头中的 `Authorization` 值
6. 更新到 `scripts/scnet_proxy.py` 和 `api/chat.js`

### Q: 如何禁用聊天功能？

A: 从 `layouts/index.html` 中删除以下行：
```html
<script src="{{ "js/scnet-chat.js" | relURL }}"></script>
```

## 技术细节

- **前端**: 原生 JavaScript，无外部依赖
- **代理**: Flask + requests (Python)
- **部署**: Hugo + GitHub Pages / Vercel
- **API**: OpenAI 兼容格式 (chat.completions)

## 文件结构

```
scripts/
  scnet_proxy.py      # 本地代理服务器
  scnet_chat.py       # 命令行客户端
static/
  js/
    scnet-chat.js     # 前端聊天组件
api/
  chat.js             # Vercel Edge Function
```
