# AI漫游 | AI Wander

我的个人技术博客与 AI 资源导航站。

[![AI Research Hub](https://img.shields.io/badge/AI-Research%20Hub-00ff41?style=for-the-badge)](https://yangbc2015.github.io)
[![Hugo](https://img.shields.io/badge/Hugo-0.146-00f0ff?style=for-the-badge)](https://gohugo.io/)
[![Auto Update](https://img.shields.io/badge/Auto%20Update-Daily-ff00ff?style=for-the-badge)](https://github.com/yangbc2015/yangbc2015.github.io/actions)

> 🔗 **在线访问**: https://yangbc2015.github.io

---

## 📖 站点简介

**AI漫游** 是我的个人网站，整理和分享 AI 领域的学习笔记、技术资源与行业动态。

### 主要栏目

| 栏目 | 内容 | 更新频率 |
|------|------|----------|
| 📰 **AI新闻** | 机器之心、量子位、TechCrunch 等源头的最新 AI 资讯 | 每日自动更新 |
| 🏆 **AI榜单** | 模型性能榜单 (SuperCLUE、DataLearner、OpenRouter 等) | 每日自动更新 |
| 🔬 **学术前沿** | arXiv 论文精选与解读 | 每日自动更新 |
| 🤖 **机器人** | 机器人技术与行业动态 | 每日自动更新 |
| 💰 **投资资讯** | AI 领域融资与投资动态 | 每日自动更新 |
| 🎓 **基础教程** | AI 入门学习资料 | 手动整理 |
| 🎬️ **视频精选** | 技术讲座和课程汇总 | 定期更新 |

---

## ⚙️ 维护说明

### 本地开发

```bash
# 启动开发服务器
hugo server -D

# 访问 http://localhost:1313
```

### 添加内容

```bash
# 添加新闻
hugo new content news/标题.md

# 添加教程
hugo new content tutorials/标题.md

# 添加博客文章
hugo new content posts/标题.md
```

### 构建部署

```bash
# 构建（生成 public/ 目录）
hugo --gc --minify

# 推送到 GitHub Pages
git add -A
git commit -m "更新内容"
git push
```

---

## 🤖 自动化更新

网站通过 GitHub Actions 实现每日自动更新：

- **定时任务**: 每天 UTC 00:00 (北京时间 08:00) 自动运行
- **数据来源**: 爬虫自动抓取多个 AI 资讯源
- **更新内容**: AI新闻、榜单、论文、投资资讯等

### 爬虫脚本

位于 `scripts/scraper/` 目录：

```
scripts/scraper/
├── scraper.py          # 主爬虫
├── requirements.txt    # 依赖
└── ...
```

### 手动触发更新

GitHub → Actions → "Auto Update AI Data" → Run workflow

---

## 🔒 隐藏功能

网站包含一些设计好的"彩蛋"：

- **关于我页面**: 底部有一个隐藏入口，输入特定密码可访问个人简历页面
- **Konami Code**: 首页支持上上下下左右左右BA 彩蛋

---

## 🛠️ 技术栈

- **[Hugo](https://gohugo.io/)** - 静态站点生成器
- **[D3.js](https://d3js.org/)** - 数据可视化（首页知识图谱）
- **[GitHub Actions](https://github.com/features/actions)** - 自动化部署
- **[GitHub Pages](https://pages.github.com/)** - 静态托管
- **Vanilla JavaScript** - 前端交互
- **CSS3** - 样式与动画

---

## 📝 配置记录

### 评论系统 (Giscus)

使用 Giscus 提供文章评论功能，配置详见 [GISCUS_SETUP.md](./GISCUS_SETUP.md)

### 搜索功能

全文搜索基于自动生成的 `index.json`，无需额外配置。

---

## 📚 目录结构

```
├── .github/workflows/    # GitHub Actions 工作流
├── content/              # 网站内容
│   ├── news/            # AI新闻
│   ├── papers/          # 学术论文
│   ├── investment/      # 投资资讯
│   ├── robotics/        # 机器人
│   ├── tutorials/       # 教程
│   ├── videos/          # 视频
│   └── resume/          # 隐藏简历（需密码）
├── data/                 # JSON 数据文件
│   ├── leaderboard/     # 榜单数据
│   ├── news.json
│   ├── papers.json
│   └── ...
├── layouts/              # HTML 模板
├── scripts/scraper/      # 自动更新爬虫
├── static/               # 静态资源
└── hugo.toml             # 站点配置
```

---

## 📨 联系我

- **GitHub**: [@yangbc2015](https://github.com/yangbc2015)
- **网站**: https://yangbc2015.github.io

---

Cultivated with ◇ in Cyberspace
