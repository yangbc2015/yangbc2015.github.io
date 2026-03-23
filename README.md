# AI漫游 | AI Wander

一个赛博朋克风格的 AI 资源导航站，使用 Hugo 构建。

![AI Research Hub](https://img.shields.io/badge/AI-Research%20Hub-00ff41?style=for-the-badge)
![Hugo](https://img.shields.io/badge/Hugo-0.146-00f0ff?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-ff00ff?style=for-the-badge)

## ✨ 特色功能

### 🎨 赛博朋克设计
- 霓虹绿主题配色
- 故障艺术 (Glitch) 效果
- 动态网格背景
- 扫描线视觉效果
- 发光边框和阴影

### 📄 页面结构
- 🏠 **首页** - 交互式 AI 知识图谱可视化
- 📰 **AI 新闻** - 最新 AI 行业动态
- 🏆 **AI 榜单** - 模型性能排行榜
- 🔬 **前沿学术** - 论文解读、ArXiv 精选
- 🎓 **基础知识** - AI 入门教程
- 💻 **技术博客** - 技术文章和实战教程
- 🎬 **视频精选** - 技术讲座和课程
- 🛠️ **工具导航** - AI 工具目录
- 📊 **归档** - 时间线浏览所有内容
- 🏷️ **标签** - 按主题分类探索
- 🔗 **友链** - 友情链接展示

### 🔧 功能特性
- 🔍 **搜索** - 全文搜索功能 (Ctrl/Cmd + K)
- 📖 **阅读进度** - 顶部进度条显示
- ⬆️ **返回顶部** - 快速返回页面顶部
- 📋 **代码复制** - 一键复制代码块
- 💬 **评论** - 支持 Giscus 评论系统
- 📱 **响应式** - 适配各种设备
- 🌙 **暗色主题** - 默认赛博朋克暗色主题
- 📡 **RSS** - 支持 RSS 订阅

## 🚀 快速开始

### 安装 Hugo

```bash
# macOS
brew install hugo

# Windows
winget install Hugo.Hugo.Extended

# Linux
sudo apt install hugo
```

### 本地运行

```bash
# 克隆仓库
git clone <your-repo-url>
cd mentors

# 启动开发服务器
hugo server -D

# 访问 http://localhost:1313
```

### 构建

```bash
# 构建网站
hugo --gc --minify

# 构建结果在 public/ 目录
```

## 📝 添加内容

### 添加新闻

```bash
hugo new content news/新闻标题.md
```

### 添加论文解读

```bash
hugo new content papers/论文标题.md
```

### 添加教程

```bash
hugo new content tutorials/教程标题.md
```

### 添加技术文章

```bash
hugo new content posts/文章标题.md
```

### 内容模板

```markdown
---
title: "文章标题"
date: 2024-03-20T10:00:00+08:00
draft: false
description: "文章描述"
tags: ["标签1", "标签2"]
---

文章内容...
```

## 🏗️ 项目结构

```
mentors/
├── archetypes/          # 内容模板
├── assets/             # 静态资源
├── content/            # 网站内容
│   ├── about/         # 关于页面
│   ├── archive/       # 归档页面
│   ├── friends/       # 友链页面
│   ├── leaderboard/   # AI 榜单
│   ├── news/          # AI 新闻
│   ├── nodes/         # 知识节点
│   ├── papers/        # 学术前沿
│   ├── posts/         # 技术博客
│   ├── tools/         # 工具导航
│   ├── tutorials/     # 基础知识
│   └── videos/        # 视频精选
├── data/              # 数据文件
├── layouts/           # HTML 模板
│   ├── _default/      # 默认模板
│   ├── leaderboard/   # 榜单页面模板
│   ├── news/          # 新闻页面模板
│   ├── papers/        # 学术页面模板
│   ├── partials/      # 组件
│   ├── tools/         # 工具页面模板
│   ├── tutorials/     # 教程页面模板
│   ├── videos/        # 视频页面模板
│   └── taxonomy/      # 分类模板
├── static/            # 静态文件
├── hugo.toml          # 站点配置
└── README.md          # 本文件
```

## 🛠️ 技术栈

- [Hugo](https://gohugo.io/) - 静态网站生成器
- [D3.js](https://d3js.org/) - 数据可视化
- [Giscus](https://giscus.app/) - 评论系统
- Vanilla JavaScript - 交互功能
- CSS3 - 样式和动画

## ⚙️ 配置

### 搜索功能

搜索功能会自动生成 `index.json`，无需额外配置。

### 评论功能 (Giscus)

AI漫游已集成 [Giscus](https://giscus.app) 评论系统，基于 GitHub Discussions。

#### 快速配置

1. 创建 GitHub 仓库用于存储评论
2. 启用仓库的 Discussions 功能
3. 安装 Giscus GitHub App: https://github.com/apps/giscus
4. 获取配置参数: https://giscus.app
5. 编辑 `hugo.toml`：

```toml
[params.giscus]
  repo = "your-username/your-repo"      # 仓库名
  repoId = "your-repo-id"               # 仓库 ID
  category = "Announcements"            # Discussion 分类
  categoryId = "your-category-id"       # 分类 ID
```

或使用配置助手脚本：

```bash
./scripts/setup-giscus.sh
```

详细配置说明请参考 [GISCUS_SETUP.md](./GISCUS_SETUP.md)

## 📄 许可证

MIT License

---

Cultivated with ◈ in Cyberspace
