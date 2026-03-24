# 🗺️ 访问者热力图部署指南

这个功能可以追踪网站访问者的地理位置，并在首页以热力图形式展示访问分布。

## 架构概览

```
┌─────────────┐      ┌─────────────────┐      ┌─────────────┐
│   网站访客   │ ──▶  │ Cloudflare Worker │ ──▶ │  KV 存储    │
└─────────────┘      └─────────────────┘      └─────────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │  ip-api.com │ (IP 地理位置查询)
                       └─────────────┘
```

## 部署步骤

### 1. 注册 Cloudflare 账号

访问 https://dash.cloudflare.com/sign-up 注册免费账号

### 2. 创建 KV Namespace

1. 登录 Cloudflare Dashboard
2. 左侧菜单选择 **Workers & Pages** > **KV**
3. 点击 **Create a namespace**
4. 名称填写：`VISITOR_DATA`
5. 点击 **Add**

### 3. 创建 Worker

1. 左侧菜单选择 **Workers & Pages** > **Create application**
2. 点击 **Create Worker**
3. 给 Worker 起个名字（例如：`ai-wander-tracker`）
4. 点击 **Deploy**
5. 部署完成后点击 **Edit code**
6. 删除默认代码，粘贴 `worker.js` 中的全部代码
7. 修改第 14 行的 `ALLOWED_ORIGINS`，添加你的网站域名：
   ```javascript
   const ALLOWED_ORIGINS = [
     'https://yangbc2015.github.io',  // 你的实际域名
     'http://localhost:1313',
     'http://127.0.0.1:1313',
   ];
   ```

### 4. 绑定 KV Namespace

1. 在 Worker 编辑页面，点击右侧 **Settings** 标签
2. 点击 **Variables** 下方的 **KV Namespace Bindings**
3. 点击 **Add binding**
4. Variable name: `VISITOR_DATA`
5. KV namespace: 选择刚才创建的 `VISITOR_DATA`
6. 点击 **Deploy**

### 5. 修改网站代码

#### 配置热力图（已有功能）

1. 复制 Worker 的 URL（例如：`https://ai-wander-tracker.your-subdomain.workers.dev`）
2. 修改 `layouts/index.html` 第 1143 行：
   ```javascript
   const WORKER_API = 'https://ai-wander-tracker.your-subdomain.workers.dev';
   ```

#### 配置访问计数器（新增功能）

修改 `layouts/index.html` 中访问统计部分的 `WORKER_API`：

```javascript
// 在第 1250 行附近找到并修改
const WORKER_API = 'https://ai-wander-tracker.your-subdomain.workers.dev';
```

3. 重新部署网站

### 6. 验证功能

#### 验证热力图

1. 访问你的网站
2. 打开浏览器开发者工具 (F12) > Console
3. 应该能看到：`Visitor tracked: {success: true, ...}`
4. 滚动到地图区域，应该能看到热力图

#### 验证访问计数器

1. 访问你的网站首页
2. 查看左下角浮动组件，应该显示：`你好！第 X 位AI漫游者`
3. 打开浏览器开发者工具 (F12) > Console，可以看到计数器 API 调用
4. 使用不同浏览器或隐身模式访问，数字应该保持一致（因为是服务器端计数）
5. 直接访问 Worker API 测试：
   ```
   https://ai-wander-tracker.your-subdomain.workers.dev/api/counter
   ```
   应该返回：`{"count": X, "isNew": true/false}`

## 数据说明

### 存储结构

**KV 存储键值对：**

| 键名格式 | 说明 | 过期时间 |
|---------|------|---------|
| `{ip_hash}_{YYYY-MM-DD}` | 单个访问者记录 | 7 天 |
| `heatmap_{YYYY-MM-DD}` | 每日热力图坐标数组 | 30 天 |

### 隐私保护

- ✅ IP 地址经过 SHA-256 哈希处理，不存储原始 IP
- ✅ 同一天内同一 IP 只记录一次
- ✅ 数据 7-30 天后自动过期删除
- ✅ 排除本地 IP 和已知爬虫

### API 端点

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/api/track` | POST | 记录当前访问者位置 |
| `/api/heatmap?days=7` | GET | 获取最近 N 天热力图数据 |
| `/api/stats` | GET | 获取访问统计 |
| `/api/counter` | GET | 获取累计访问次数并自动递增 |

### 访问计数器功能

新增的全局访问计数器，可以跨浏览器共享访问数据：

**工作原理：**
- 每次访问调用 `/api/counter` 接口
- 基于 IP 地址进行去重（同一 IP 每天只计一次）
- 使用 KV 存储累计访问次数，数据跨浏览器共享
- IP 经过哈希处理，保护用户隐私

**存储结构：**

| 键名 | 说明 | 过期时间 |
|-----|------|---------|
| `site_total_counter` | 累计访问次数 | 1年 |
| `counter_session_{hash}_{date}` | 今日访问标记 | 24小时 |

## 热力图效果

- **紫色/蓝色**：低访问量区域
- **粉色/红色**：高访问量区域
- **脉冲点**：实时活跃访问点

## 免费额度限制

Cloudflare Worker 免费版：
- 每天 100,000 次请求
- 足够支持日均 10 万 PV 的网站

KV 存储免费版：
- 每天 100,000 次读取
- 每天 1,000 次写入
- 足够支持日均 1 万 UV 的网站

## 故障排除

### 热力图不显示

1. 检查 Worker URL 是否正确配置
2. 检查浏览器 Console 是否有错误
3. 检查 Cloudflare Worker 日志（Workers & Pages > 你的 Worker > Logs）

### 跨域错误

确保 `ALLOWED_ORIGINS` 中包含你的网站完整域名（包括 `https://`）

### 数据不更新

- 同一 IP 每天只记录一次，这是正常行为
- 检查 KV 中是否有数据：Cloudflare Dashboard > Workers & Pages > KV > 浏览

### 访问计数器显示为 0 或不更新

1. **检查 Worker URL 配置**
   - 确认 `layouts/index.html` 中的 `WORKER_API` 地址正确
   - 确保没有拼写错误或多余的空格

2. **检查 CORS 配置**
   - 确认 `ALLOWED_ORIGINS` 中包含你的域名（包括 `https://`）
   - 如果使用自定义域名，需要同时添加自定义域名和默认 workers.dev 域名

3. **检查 KV 绑定**
   - 确认 Worker 已正确绑定 `VISITOR_DATA` KV namespace
   - 检查 KV namespace 名称是否为 `VISITOR_DATA`（区分大小写）

4. **本地测试**
   - 直接访问 `https://your-worker.workers.dev/api/counter`
   - 如果返回错误，查看 Worker Logs 排查问题

5. **计数器初始值**
   - 首次部署时计数器从 0 开始
   - 如需设置初始值，可以在 Cloudflare Dashboard > KV 中手动添加 `site_total_counter` 键

## 从 localStorage 迁移到 Worker 计数器

如果你之前使用 localStorage 统计访问次数，可以按以下步骤迁移：

1. **查看当前 localStorage 数据**
   - 在浏览器开发者工具 Console 中运行：
     ```javascript
     localStorage.getItem('site_total_visits');
     ```

2. **设置初始值到 Worker**
   - 在 Cloudflare Dashboard > Workers & Pages > KV > 浏览
   - 添加键 `site_total_counter`，值为你的当前访问次数

3. **部署新代码**
   - 更新 `worker.js` 代码
   - 更新 `layouts/index.html` 中的 `WORKER_API` 地址
   - 重新部署网站

4. **验证**
   - 访问网站确认计数器显示正确
   - 使用不同浏览器测试，确认数字一致

## 高级配置

### 更换 IP 地理位置服务

默认使用 ip-api.com（免费，非商业用途）。如需更高精度，可更换为：

- **MaxMind GeoIP2**（免费版每月 3 万次查询）
- **IP2Location**（免费版每月 3 万次查询）
- **IPGeolocation**（免费版每月 3 万次查询）

修改 `worker.js` 中的 `getGeoLocation` 函数即可。

### 自定义热力图颜色

修改 `layouts/index.html` 中的 `gradient` 配置：

```javascript
gradient: {
    0.0: 'blue',
    0.5: 'yellow', 
    1.0: 'red'
}
```

### 数据导出

可通过 Cloudflare API 导出数据用于分析：

```bash
curl "https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values" \
  -H "Authorization: Bearer {api_token}"
```
