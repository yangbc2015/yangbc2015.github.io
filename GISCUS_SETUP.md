# Giscus 评论系统配置指南

Giscus 是一个基于 GitHub Discussions 的评论系统，免费、开源且无广告。

## 🚀 快速配置步骤

### 第 1 步：准备 GitHub 仓库

1. **创建一个新的 GitHub 仓库**（或使用现有仓库）
   - 例如：`your-username/ai-research-hub-comments`
   - 仓库可以是私有的或公开的

2. **启用 Discussions 功能**
   - 进入仓库的 **Settings** → **General**
   - 向下滚动找到 **Features** 部分
   - 勾选 **Discussions**

### 第 2 步：安装 Giscus 应用

1. 访问 [giscus.app](https://giscus.app)
2. 点击 **"Get started"** 或直接进入安装页面
3. 选择你要使用的仓库
4. 点击 **Install** 安装 Giscus 应用

### 第 3 步：获取配置参数

在 [giscus.app](https://giscus.app) 页面上：

1. **选择仓库**: 输入 `username/repo-name`
2. **页面 ↔ Discussions 映射**: 选择 `pathname`（根据页面路径）
3. **Discussion 分类**: 选择 `Announcements`（推荐）
4. **主题**: 选择 `Dark`（与网站风格匹配）
5. **语言**: 选择 `zh-CN`（简体中文）

页面底部会生成配置代码，复制以下参数：
- `data-repo`
- `data-repo-id`
- `data-category`
- `data-category-id`

### 第 4 步：配置 hugo.toml

编辑 `hugo.toml` 文件，填入你的参数：

```toml
[params.giscus]
  repo = "your-username/ai-research-hub-comments"      # 仓库名
  repoId = "R_xxxxxxxxxx"                               # 仓库 ID
  category = "Announcements"                           # Discussion 分类
  categoryId = "DIC_xxxxxxxxxx"                        # 分类 ID
  mapping = "pathname"
  reactionsEnabled = "1"
  emitMetadata = "0"
  theme = "dark"
  lang = "zh-CN"
```

### 第 5 步：重新构建网站

```bash
hugo --gc --minify
```

## 📋 配置示例

假设你的 GitHub 用户名为 `zhangsan`，创建的仓库名为 `ai-research-comments`：

```toml
[params.giscus]
  repo = "zhangsan/ai-research-comments"
  repoId = "R_kgDOLZPphA"
  category = "Announcements"
  categoryId = "DIC_kwDOLZPphM4CclRj"
  mapping = "pathname"
  reactionsEnabled = "1"
  emitMetadata = "0"
  theme = "dark"
  lang = "zh-CN"
```

## 🎨 主题适配

网站使用赛博朋克暗色主题，Giscus 已经配置为 `dark` 主题，完美适配网站风格。

如果需要自定义主题颜色，可以在 Giscus 配置中使用 `dark_tritanopia`、`dark_high_contrast` 等变体。

## 🔧 高级配置

### 自定义 Discussion 标题

如果需要自定义 Discussion 的标题格式，修改 `mapping` 参数：

- `pathname` - 使用页面路径（推荐）
- `url` - 使用完整 URL
- `title` - 使用页面标题
- `og:title` - 使用 Open Graph 标题
- `specific` - 使用特定字符串

### 懒加载评论

为了提高页面性能，可以添加懒加载：

```html
<script src="https://giscus.app/client.js"
    ...
    data-loading="lazy"
    ...
>
</script>
```

## ✅ 验证配置

配置完成后：

1. 部署网站
2. 访问任意文章页面
3. 滚动到页面底部查看评论区
4. 尝试发表一条评论测试

## 🐛 常见问题

### Q: 评论区不显示？
- 检查仓库是否正确安装了 Giscus 应用
- 确认 Discussions 功能已启用
- 验证 hugo.toml 中的参数是否正确

### Q: 评论无法发表？
- 确保用户已登录 GitHub
- 检查用户是否有该仓库的 Discussions 权限

### Q: 如何管理评论？
- 直接在 GitHub Discussions 中管理
- 支持标签、锁定、删除等操作

## 📚 相关链接

- [Giscus 官网](https://giscus.app)
- [Giscus GitHub](https://github.com/giscus/giscus)
- [GitHub Discussions 文档](https://docs.github.com/en/discussions)
