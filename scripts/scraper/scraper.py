#!/usr/bin/env python3
"""
AI 数据爬虫主程序
自动爬取 AI 新闻、榜单、论文和视频数据，更新 Hugo 数据文件
"""

import json
import yaml
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# 导入爬虫模块
from lmsys_scraper import LMSYSScraper
from news_scraper import NewsScraper
from papers_scraper import PapersScraper
from videos_scraper import VideosScraper
from csdn_scraper import CSDNScraper
from artificialanalysis_scraper import ArtificialAnalysisScraper
from investment_scraper import InvestmentScraper

# 数据目录
DATA_DIR = Path(__file__).parent.parent.parent / "data"
NEWS_DIR = DATA_DIR / "news"
LEADERBOARD_DIR = DATA_DIR / "leaderboard"
CONTENT_NEWS_DIR = Path(__file__).parent.parent.parent / "content" / "news"
CONTENT_PAPERS_DIR = Path(__file__).parent.parent.parent / "content" / "papers"
CONTENT_VIDEOS_DIR = Path(__file__).parent.parent.parent / "content" / "videos"
CONTENT_TUTORIALS_DIR = Path(__file__).parent.parent.parent / "content" / "tutorials"
CONTENT_INVESTMENT_DIR = Path(__file__).parent.parent.parent / "content" / "investment"


def ensure_dirs():
    """确保数据目录存在"""
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    LEADERBOARD_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_NEWS_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_TUTORIALS_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_INVESTMENT_DIR.mkdir(parents=True, exist_ok=True)


def save_json(data, filepath):
    """保存数据到 JSON 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ 已保存: {filepath}")


def update_leaderboard():
    """更新榜单数据"""
    print("\n" + "="*50)
    print("📊 开始更新 AI 榜单数据...")
    print("="*50)
    
    # 爬取 LMSYS Arena 数据
    scraper = LMSYSScraper()
    lmsys_data = scraper.fetch_arena_leaderboard()
    if lmsys_data:
        save_json(lmsys_data, LEADERBOARD_DIR / "lmsys_arena.json")
    else:
        print("⚠️ 未能获取 LMSYS Arena 数据，使用备用数据")
        lmsys_data = scraper.get_fallback_data()
        save_json(lmsys_data, LEADERBOARD_DIR / "lmsys_arena.json")
    
    # 爬取 Artificial Analysis 数据
    print("\n  正在获取 Artificial Analysis 数据...")
    aa_scraper = ArtificialAnalysisScraper()
    aa_data = aa_scraper.fetch_leaderboard()
    if aa_data:
        save_json(aa_data, LEADERBOARD_DIR / "artificial_analysis.json")
        print(f"  ✓ 获取了 {len(aa_data.get('models', []))} 个模型数据")
    else:
        print("⚠️ 未能获取 Artificial Analysis 数据，使用备用数据")
        aa_data = aa_scraper.get_fallback_data()
        save_json(aa_data, LEADERBOARD_DIR / "artificial_analysis.json")
    
    # 创建综合榜单索引
    leaderboard_index = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "lmsys_arena": {
                "name": "LMSYS Chatbot Arena",
                "url": "https://chat.lmsys.org",
                "description": "基于人类偏好的众包评测平台",
                "data_file": "leaderboard/lmsys_arena.json"
            },
            "artificial_analysis": {
                "name": "Artificial Analysis",
                "url": "https://artificialanalysis.ai/leaderboards/models",
                "description": "综合AI模型性能排行榜，涵盖智能指数、价格、速度等多维度评测",
                "data_file": "leaderboard/artificial_analysis.json"
            }
        }
    }
    save_json(leaderboard_index, DATA_DIR / "leaderboard.json")
    
    return lmsys_data, aa_data


def update_news():
    """更新新闻数据"""
    print("\n" + "="*50)
    print("📰 开始更新 AI 新闻...")
    print("="*50)
    
    scraper = NewsScraper()
    all_news = []
    
    # 从多个源获取新闻
    sources = [
        ("机器之心", scraper.fetch_jiqizhixin),
        ("量子位", scraper.fetch_qbitai),
        ("TechCrunch", scraper.fetch_techcrunch_ai),
    ]
    
    for source_name, fetch_func in sources:
        try:
            print(f"\n  正在从 {source_name} 获取新闻...")
            news = fetch_func()
            all_news.extend(news)
            print(f"  ✓ 从 {source_name} 获取了 {len(news)} 条新闻")
        except Exception as e:
            print(f"  ✗ 从 {source_name} 获取失败: {e}")
    
    # 去重：基于标题
    seen_titles = set()
    unique_news = []
    for item in all_news:
        title = item.get("title", "")
        # 使用标题前30个字符作为去重键
        title_key = title[:30].lower() if title else ""
        if title_key and title_key in seen_titles:
            continue
        if title_key:
            seen_titles.add(title_key)
        unique_news.append(item)
    
    all_news = unique_news
    
    # 按日期排序
    all_news.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # 只保留最近 20 条
    all_news = all_news[:20]
    
    # 保存新闻数据
    news_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "count": len(all_news),
        "items": all_news
    }
    save_json(news_data, DATA_DIR / "news.json")
    
    # 为每条新闻创建 Hugo 内容文件（Markdown）
    create_news_content_files(all_news)
    
    return all_news


def update_papers():
    """更新论文数据"""
    print("\n" + "="*50)
    print("📄 开始更新 AI 论文...")
    print("="*50)
    
    scraper = PapersScraper()
    all_papers = []
    
    # 从 arXiv 获取论文
    try:
        print("\n  正在从 arXiv 获取论文...")
        arxiv_papers = scraper.fetch_arxiv_ai(max_results=10)
        all_papers.extend(arxiv_papers)
        print(f"  ✓ 从 arXiv 获取了 {len(arxiv_papers)} 篇论文")
    except Exception as e:
        print(f"  ✗ arXiv 获取失败: {e}")
    
    # 去重：基于 arxiv_id
    seen_arxiv_ids = set()
    unique_papers = []
    for paper in all_papers:
        arxiv_id = paper.get("arxiv_id", "")
        if arxiv_id and arxiv_id in seen_arxiv_ids:
            continue
        if arxiv_id:
            seen_arxiv_ids.add(arxiv_id)
        unique_papers.append(paper)
    
    all_papers = unique_papers
    
    # 按日期排序
    all_papers.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # 只保留最近 15 篇
    all_papers = all_papers[:15]
    
    # 保存论文数据
    papers_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "count": len(all_papers),
        "items": all_papers
    }
    save_json(papers_data, DATA_DIR / "papers.json")
    
    # 创建论文内容文件
    create_papers_content_files(all_papers)
    
    return all_papers


def update_videos():
    """更新视频数据"""
    print("\n" + "="*50)
    print("🎬 开始更新 AI 视频...")
    print("="*50)
    
    scraper = VideosScraper()
    all_videos = []
    
    # 获取精选视频
    try:
        print("\n  正在获取精选 AI 视频...")
        featured_videos = scraper.get_featured_videos()
        all_videos.extend(featured_videos)
        print(f"  ✓ 获取了 {len(featured_videos)} 个精选视频")
    except Exception as e:
        print(f"  ✗ 获取精选视频失败: {e}")
    
    # 获取 B站视频
    try:
        print("\n  正在获取 B站 AI 视频...")
        bilibili_videos = scraper.get_bilibili_videos()
        all_videos.extend(bilibili_videos)
        print(f"  ✓ 获取了 {len(bilibili_videos)} 个 B站视频")
    except Exception as e:
        print(f"  ✗ B站视频获取失败: {e}")
    
    # 保存视频数据
    videos_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "count": len(all_videos),
        "items": all_videos
    }
    save_json(videos_data, DATA_DIR / "videos.json")
    
    # 创建视频内容文件
    create_videos_content_files(all_videos)
    
    return all_videos


def create_news_content_files(news_items):
    """为新闻创建 Hugo 内容文件"""
    print(f"\n  正在创建新闻内容文件...")
    
    created_count = 0
    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    
    # 获取已存在的文章标题（用于去重）
    existing_titles = set()
    for f in CONTENT_NEWS_DIR.glob("*.md"):
        if f.name != "_index.md":
            try:
                content = f.read_text(encoding='utf-8')
                # 从 front matter 中提取标题
                if 'title:' in content:
                    title_line = [l for l in content.split('\n') if 'title:' in l][0]
                    existing_titles.add(title_line.split(':', 1)[1].strip().strip('"\''))
            except:
                pass
    
    for item in news_items[:10]:  # 只为前 10 条创建内容文件
        # 去重检查：如果标题已存在，跳过
        if item["title"] in existing_titles:
            print(f"    ⏭️ 已存在: {item['title'][:40]}...")
            continue
        
        # 生成文件名：使用当前日期 + 标题slug，确保每天创建新文件
        title_slug = "".join(c if c.isalnum() else "-" for c in item["title"][:30]).lower()
        # 添加时间戳确保唯一性
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        filename = f"{today_str}-{title_slug}-{timestamp}.md"
        filepath = CONTENT_NEWS_DIR / filename
        
        # 如果文件已存在（极端情况），跳过
        if filepath.exists():
            continue
        
        # 创建 front matter
        front_matter = {
            "title": item["title"],
            "date": item["date"],
            "type": item.get("type", "industry"),
            "source": item.get("source", "AI漫游"),
            "link": item.get("link", ""),
            "summary": item.get("summary", ""),
            "tags": item.get("tags", ["AI"]),
        }
        
        # 写入文件
        content = f"""---
{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---

{item.get('summary', '')}

<!-- 来源: {item.get('source', '未知')} -->
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        created_count += 1
    
    print(f"  ✓ 创建了 {created_count} 个新内容文件")


def create_papers_content_files(papers):
    """为论文创建 Hugo 内容文件"""
    print(f"\n  正在创建论文内容文件...")
    
    created_count = 0
    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    
    # 获取已存在的 arxiv_id（用于去重）
    existing_arxiv_ids = set()
    for f in CONTENT_PAPERS_DIR.glob("*.md"):
        if f.name != "_index.md":
            try:
                content = f.read_text(encoding='utf-8')
                if 'arxiv_id:' in content:
                    arxiv_line = [l for l in content.split('\n') if 'arxiv_id:' in l][0]
                    existing_arxiv_ids.add(arxiv_line.split(':', 1)[1].strip().strip('"\''))
            except:
                pass
    
    for paper in papers[:8]:  # 只为前 8 篇创建内容文件
        # 去重检查：如果 arxiv_id 已存在，跳过
        arxiv_id = paper.get("arxiv_id", "")
        if arxiv_id and arxiv_id in existing_arxiv_ids:
            print(f"    ⏭️ 已存在: {paper['title'][:40]}...")
            continue
        
        # 生成文件名：使用当前日期 + arxiv_id，确保每天创建新文件
        title_slug = "".join(c if c.isalnum() else "-" for c in paper["title"][:30]).lower()
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        filename = f"{today_str}-{arxiv_id}-{title_slug}-{timestamp}.md"
        filepath = CONTENT_PAPERS_DIR / filename
        
        # 如果文件已存在（极端情况），跳过
        if filepath.exists():
            continue
        
        # 创建 front matter
        front_matter = {
            "title": paper["title"],
            "date": paper["date"],
            "authors": paper.get("authors", ""),
            "venue": paper.get("venue", "arXiv"),
            "arxiv_id": paper.get("arxiv_id", ""),
            "categories": paper.get("categories", []),
            "paper_type": paper.get("type", "ai"),
            "pdf_url": paper.get("pdf_url", ""),
            "arxiv_url": paper.get("url", ""),
            "tags": paper.get("categories", [])[:3] + ["论文"],
        }
        
        # 写入文件
        content = f"""---
{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---

## 摘要

{paper.get('abstract', '')}

## 链接

- [📄 PDF]({paper.get('pdf_url', '')})
- [🔗 arXiv]({paper.get('url', '')})

<!-- 来源: {paper.get('source', 'arXiv')} -->
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        created_count += 1
    
    print(f"  ✓ 创建了 {created_count} 个新论文文件")


def create_videos_content_files(videos):
    """为视频创建 Hugo 内容文件"""
    print(f"\n  正在创建视频内容文件...")
    
    created_count = 0
    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    
    # 获取已存在的视频 URL（用于去重）
    existing_urls = set()
    for f in CONTENT_VIDEOS_DIR.glob("*.md"):
        if f.name != "_index.md":
            try:
                content = f.read_text(encoding='utf-8')
                if 'url:' in content:
                    url_line = [l for l in content.split('\n') if 'url:' in l and 'original_url' not in l][0]
                    existing_urls.add(url_line.split(':', 1)[1].strip().strip('"\''))
            except:
                pass
    
    for video in videos[:6]:  # 只为前 6 个创建内容文件
        # 去重检查：如果 URL 已存在，跳过
        video_url = video.get("url", "")
        if video_url and video_url in existing_urls:
            print(f"    ⏭️ 已存在: {video['title'][:40]}...")
            continue
        
        # 生成文件名：使用当前日期 + 标题slug，确保每天创建新文件
        title_slug = "".join(c if c.isalnum() else "-" for c in video["title"][:30]).lower()
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        filename = f"{today_str}-{title_slug}-{timestamp}.md"
        filepath = CONTENT_VIDEOS_DIR / filename
        
        # 如果文件已存在（极端情况），跳过
        if filepath.exists():
            continue
        
        # 创建 front matter
        front_matter = {
            "title": video["title"],
            "date": video["date"],
            "speaker": video.get("speaker", ""),
            "duration": video.get("duration", ""),
            "views": video.get("views", ""),
            "platform": video.get("platform", "youtube"),
            "video_id": video.get("video_id", ""),
            "url": video.get("url", ""),
            "thumbnail": video.get("thumbnail", ""),
            "video_type": video.get("type", "lecture"),
            "category": video.get("category", "技术讲座"),
            "featured": video.get("featured", False),
            "tags": [video.get("category", "AI"), "视频"],
        }
        
        # 写入文件
        content = f"""---
{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---

{video.get('description', '')}

## 观看

[▶ 在 {{ if eq .Params.platform "bilibili" }}B站{{ else }}YouTube{{ end }}观看]({{ video.get('url', '') }})

<!-- 来源: {{ video.get('platform', 'youtube') }} -->
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        created_count += 1
    
    print(f"  ✓ 创建了 {created_count} 个新视频文件")


def update_tutorials():
    """更新教程数据（从 data/tutorials.json 读取 CSDN 文章数据）"""
    print("\n" + "="*50)
    print("📚 开始更新 CSDN 教程数据...")
    print("="*50)
    
    try:
        # 读取已配置的教程数据
        tutorials_file = DATA_DIR / "tutorials.json"
        if tutorials_file.exists():
            with open(tutorials_file, 'r', encoding='utf-8') as f:
                tutorials_data = json.load(f)
            articles = tutorials_data.get("items", [])
            print(f"\n  ✓ 从配置文件读取 {len(articles)} 篇教程文章")
        else:
            # 如果文件不存在，使用备用数据
            print("\n  ⚠️ 配置文件不存在，使用备用数据")
            scraper = CSDNScraper('heroybc')
            articles = scraper.get_fallback_articles()
            tutorials_data = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "count": len(articles),
                "author": "heroybc",
                "source": "CSDN",
                "items": articles
            }
            save_json(tutorials_data, tutorials_file)
        
        # 更新最后更新时间
        tutorials_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        save_json(tutorials_data, tutorials_file)
        
        # 创建教程内容文件
        create_tutorial_content_files(articles)
        
        return articles
        
    except Exception as e:
        print(f"  ✗ 更新教程失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def create_tutorial_content_files(articles):
    """为教程创建 Hugo 内容文件（链接到外部 CSDN 文章）"""
    print(f"\n  正在创建教程内容文件...")
    
    # 清理旧的教程文件（保留 _index.md 和本地教程）
    for f in CONTENT_TUTORIALS_DIR.glob("*.md"):
        if f.name != "_index.md" and "transformer" not in f.name:
            f.unlink()
    
    created_count = 0
    for article in articles:
        # 生成文件名
        title_slug = "".join(c if c.isalnum() else "-" for c in article["title"][:40]).lower()
        date_str = article["date"].replace("-", "") if article.get("date") else ""
        filename = f"{date_str}-{title_slug}.md"
        filepath = CONTENT_TUTORIALS_DIR / filename
        
        level = article.get("level", "beginner")
        category = article.get("category", "技术文章")
        
        # 创建 front matter - 设置外部链接
        front_matter = {
            "title": article["title"],
            "date": article["date"],
            "author": article.get("author", "heroybc"),
            "source": "CSDN",
            "original_url": article.get("url", ""),
            "category": category,
            "level": level,
            "views": article.get("views", "0"),
            "summary": article.get("summary", ""),
            "tags": [category, "教程", "CSDN", "外部链接"],
            "external_link": article.get("url", ""),
        }
        
        # 写入文件 - 内容引导到外部链接
        summary = article.get('summary', '')
        url = article.get('url', '')
        views = article.get('views', '0')
        date = article.get('date', '')
        
        content = f"""---
{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---

## 📄 文章简介

{summary}

## 🔗 原文链接

此文章为 **CSDN 精选转载**，点击下方按钮阅读原文：

<p style="margin: 2rem 0;">
<a href="{url}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #fc5531, #ff6b35); color: white; text-decoration: none; border-radius: 8px; font-family: 'Orbitron', monospace; font-weight: 600;">
<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 22c-5.523 0-10-4.477-10-10S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
点击阅读 CSDN 原文 →
</a>
</p>

---

## 📊 文章信息

| 项目 | 内容 |
|------|------|
| **作者** | heroybc |
| **分类** | {category} |
| **难度** | {level} |
| **阅读量** | {views} |
| **发布日期** | {date} |
| **来源** | [CSDN博客](https://blog.csdn.net/heroybc) |

---

*本文内容版权归原作者所有，仅供学习交流使用。*
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        created_count += 1
    
    print(f"  ✓ 创建了 {created_count} 个新教程文件")


def update_investment():
    """更新投资资讯数据"""
    print("\n" + "="*50)
    print("💰 开始更新 AI 投资资讯...")
    print("="*50)
    
    scraper = InvestmentScraper()
    
    # 获取投资资讯
    try:
        investment_items = scraper.fetch_all_investments()
        
        # 保存投资数据
        investment_data = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "count": len(investment_items),
            "items": investment_items
        }
        save_json(investment_data, DATA_DIR / "investment.json")
        
        # 创建投资内容文件
        create_investment_content_files(investment_items)
        
        return investment_items
    except Exception as e:
        print(f"  ✗ 投资资讯更新失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def create_investment_content_files(items):
    """为投资资讯创建 Hugo 内容文件"""
    print(f"\n  正在创建投资内容文件...")
    
    created_count = 0
    for item in items[:15]:  # 只为前 15 条创建内容文件
        # 生成文件名
        title_slug = "".join(c if c.isalnum() else "-" for c in item["title"][:40]).lower()
        date_str = item["date"].replace("-", "") if item.get("date") else ""
        filename = f"{date_str}-{title_slug}.md"
        filepath = CONTENT_INVESTMENT_DIR / filename
        
        # 如果文件已存在，跳过
        if filepath.exists():
            continue
        
        # 创建 front matter
        front_matter = {
            "title": item["title"],
            "date": item["date"],
            "type": item.get("type", "news"),
            "source": item.get("source", "AI漫游"),
            "category": item.get("category", "AI投资"),
            "link": item.get("url", ""),
            "summary": item.get("summary", ""),
            "tags": item.get("tags", ["AI投资"]),
        }
        
        # 写入文件
        content = f"""---
{yaml.dump(front_matter, allow_unicode=True, sort_keys=False)}---

## 📊 投资摘要

{item.get('summary', '')}

## 🔗 原文链接

<a href="{item.get('url', '')}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #ffd700, #ffed4e); color: #000; text-decoration: none; border-radius: 8px; font-family: 'Orbitron', monospace; font-weight: 600;">
查看详情 →
</a>

---

*本文仅供参考，不构成投资建议。*
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        created_count += 1
    
    print(f"  ✓ 创建了 {created_count} 个新投资文件")


def main():
    """主函数"""
    print("🤖 AI 数据爬虫启动")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    ensure_dirs()
    
    try:
        # 更新榜单
        update_leaderboard()
        
        # 更新新闻
        update_news()
        
        # 更新论文
        update_papers()
        
        # 更新视频
        update_videos()
        
        # 更新教程（CSDN）
        update_tutorials()
        
        # 更新投资资讯
        update_investment()
        
        print("\n" + "="*50)
        print("✅ 所有数据更新完成!")
        print("="*50)
        return 0
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
