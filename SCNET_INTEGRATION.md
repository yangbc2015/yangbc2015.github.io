# SCNet AI 聊天集成指南

本站点集成了国家超算互联网平台（SCNet）的 AI 聊天功能。

## 当前状态

由于 GitHub Pages 是纯静态托管，**无法直接运行后端代理**。浏览器 CORS 安全策略也阻止了前端直接调用 SCNet API。

**当前实现**：
- ✅ 前端聊天组件已集成
- ✅ 智能降级到模拟模式（确保用户体验）
- ⚠️ 需要额外配置才能获得真实 AI 回复

## 获取真实 AI 回复的三种方法

### 方法 1：部署 Cloudflare Worker（推荐 ⭐）

**优点**：永久有效，全球加速，完全免费  
**耗时**：约 5 分钟

#### 步骤：

1. **注册 Cloudflare 账户**
   - 访问 https://dash.cloudflare.com/sign-up
   - 使用邮箱注册（免费）

2. **创建 Worker**
   - 登录后点击左侧 "Workers & Pages"
   - 点击 "Create" → "Create Worker"
   - 给 Worker 起个名字（如 `scnet-proxy`）

3. **粘贴代码**
   - 删除默认代码
   - 复制 `cloudflare-worker.js` 的全部内容粘贴进去
   - 点击 "Save and deploy"

4. **获取 Worker URL**
   - 部署后会显示类似 `https://scnet-proxy.yourname.workers.dev` 的地址
   - 复制这个 URL

5. **配置网站**
   - 编辑 `layouts/index.html`
   - 在 `<script src="js/scnet-chat.js">` **之前**添加：
   ```html
   <script>window.SCNET_WORKER_URL = 'https://你的-worker-地址.workers.dev';</script>
   ```

6. **完成！**
   - 重新部署网站
   - 现在聊天框会显示真实 AI 回复

---

### 方法 2：本地代理（开发测试用）

**优点**：简单快速  
**缺点**：需要保持 Python 脚本运行

```bash
# 1. 安装依赖
pip install flask flask-cors requests

# 2. 启动代理
python scripts/scnet_proxy.py

# 3. 在浏览器中打开 http://localhost:1313
#    保持终端窗口运行
```

---

### 方法 3：直接使用 SCNet 官网

如果不想配置，直接访问官方聊天页面：
https://www.scnet.cn/ui/chatbot/

---

## 技术架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   用户浏览器     │────▶│  Cloudflare     │────▶│   SCNet API     │
│  (你的GitHub站点)│     │  Worker (代理)   │     │  (AI 服务)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        │ 备选：本地代理
        ▼
┌─────────────────┐
│  localhost:8787 │
│  (Python Flask) │
└─────────────────┘
```

## Token 更新

SCNet 的 token 会过期。如果发现 Worker 返回 401 错误，需要更新 token：

1. 访问 https://www.scnet.cn/ui/chatbot/
2. 发送任意消息
3. 按 F12 打开开发者工具 → Network 标签
4. 找到 `chat/completions` 请求
5. 复制 Request Headers 中的 `Authorization` 值
6. 更新到 `cloudflare-worker.js` 和 `scripts/scnet_proxy.py`
7. 重新部署 Worker

## 文件说明

| 文件 | 用途 |
|------|------|
| `static/js/scnet-chat.js` | 前端聊天组件 |
| `cloudflare-worker.js` | Cloudflare Worker 代理代码 |
| `scripts/scnet_proxy.py` | 本地 Python 代理 |
| `scripts/scnet_chat.py` | 命令行客户端 |

## 模拟模式说明

当无法连接到真实 AI 服务时，组件会自动切换到**模拟模式**：
- 显示预设的友好回复
- 告知用户如何获得真实 AI 功能
- 保持聊天界面可用

这是为了确保即使服务不可用，用户体验也不会中断。

## 故障排除

### Q: Worker 部署后仍然显示模拟回复？
A: 检查：
1. Worker URL 是否正确配置在 `window.SCNET_WORKER_URL`
2. Worker 是否成功部署（访问 Worker URL 看是否返回 JSON）
3. 浏览器控制台是否有错误信息

### Q: 提示 "Token expired"？
A: 按照上面的 "Token 更新" 步骤操作

### Q: 如何完全禁用 AI 聊天？
A: 从 `layouts/index.html` 中删除：
```html
<script src="{{ "js/scnet-chat.js" | relURL }}"></script>
```
