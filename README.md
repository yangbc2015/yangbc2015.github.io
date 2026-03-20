# 数字花园 | Digital Garden

一个赛博朋克风格的个人数字花园，使用 Hugo 构建。

![Digital Garden](https://img.shields.io/badge/Digital-Garden-00ff41?style=for-the-badge)
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
- 🏠 **首页** - 交互式知识图谱可视化
- 📝 **文章** - 技术博客和随笔
- 🌿 **节点** - 想法和项目的网络
- 📚 **归档** - 时间线浏览所有内容
- 🏷️ **标签** - 按主题分类探索
- 🔗 **友链** - 友情链接展示
- 📊 **统计** - 网站数据概览
- ℹ️ **关于** - 数字花园介绍

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

### 添加文章

```bash
hugo new content posts/my-article.md
```

### 添加节点

```bash
hugo new content nodes/my-node.md
```

### 内容模板

```markdown
---
title: "文章标题"
date: 2024-03-20T10:00:00+08:00
draft: false
description: "文章描述"
category: "分类"
tags: ["标签1", "标签2"]
icon: "🚀"
---

文章内容...
```

## ⚙️ 配置

### 搜索功能

搜索功能会自动生成 `index.json`，无需额外配置。

### 评论功能 (Giscus)

在 `hugo.toml` 中配置：

```toml
[params.giscus]
  repo = "your-username/your-repo"
  repoId = "your-repo-id"
  category = "Announcements"
  categoryId = "your-category-id"
```

### 友链

编辑 `content/friends/index.md` 添加你的友情链接。

## 🏗️ 项目结构

```
mentors/
├── archetypes/          # 内容模板
├── assets/             # 静态资源
├── content/            # 网站内容
│   ├── about/         # 关于页面
│   ├── archive/       # 归档页面
│   ├── friends/       # 友链页面
│   ├── nodes/         # 节点（想法/项目）
│   ├── posts/         # 文章
│   └── stats/         # 统计页面
├── data/              # 数据文件
├── layouts/           # HTML 模板
│   ├── _default/      # 默认模板
│   ├── partials/      # 组件
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

## 📄 许可证

MIT License

---

Cultivated with ◈ in Cyberspace
