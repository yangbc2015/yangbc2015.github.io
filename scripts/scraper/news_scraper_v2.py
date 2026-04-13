#!/usr/bin/env python3
"""
AI 新闻爬虫 V2 - 时效性改进版
- 正确解析文章实际发布日期
- 只保留最近7天内的新闻
- 自动清理过期新闻
- 扩展消息源
"""

import requests
import re
import yaml
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import feedparser
from dateutil import parser as date_parser


class NewsScraperV2:
    """改进版 AI 新闻爬虫 - 确保时效性"""
    
    # 时效性配置：只保留最近7天的新闻
    MAX_NEWS_AGE_DAYS = 7
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.today = datetime.now(timezone.utc).date()
        self.cutoff_date = self.today - timedelta(days=self.MAX_NEWS_AGE_DAYS)
        
    def is_recent(self, date_str):
        """检查日期是否在有效期内（最近7天）"""
        try:
            if not date_str:
                return False
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            return date >= self.cutoff_date
        except:
            return False
    
    def parse_relative_date(self, text):
        """解析相对日期（今天、昨天、X天前等）"""
        text = text.strip().lower()
        
        # 匹配 "今天", "今天xx:xx"
        if '今天' in text or '刚刚' in text or '分钟前' in text or '小时前' in text:
            return self.today.strftime('%Y-%m-%d')
        
        # 匹配 "昨天"
        if '昨天' in text:
            return (self.today - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 匹配 "X天前"
        match = re.search(r'(\d+)\s*天前', text)
        if match:
            days = int(match.group(1))
            if days <= self.MAX_NEWS_AGE_DAYS:
                return (self.today - timedelta(days=days)).strftime('%Y-%m-%d')
            return None
        
        # 匹配 "X小时前", "X分钟前"
        if re.search(r'\d+\s*(小时|分钟|分)前', text):
            return self.today.strftime('%Y-%m-%d')
        
        # 匹配 "MM月DD日"
        match = re.match(r'(\d{1,2})月(\d{1,2})日', text)
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            year = self.today.year
            
            # 处理跨年情况
            if month > self.today.month or (month == self.today.month and day > self.today.day):
                year -= 1
                
            try:
                date = datetime(year, month, day).date()
                if date >= self.cutoff_date:
                    return date.strftime('%Y-%m-%d')
            except:
                pass
        
        # 匹配 "YYYY-MM-DD" 或 "YYYY/MM/DD"
        match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', text)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            try:
                date = datetime(year, month, day).date()
                if date >= self.cutoff_date:
                    return date.strftime('%Y-%m-%d')
            except:
                pass
        
        return None
    
    def fetch_all_news(self):
        """获取所有AI新闻，确保时效性"""
        print(f"  开始获取AI新闻（有效期：最近{self.MAX_NEWS_AGE_DAYS}天）...")
        print(f"  截止日期：{self.cutoff_date}")
        
        all_news = []
        
        sources = [
            ("机器之心", self.fetch_jiqizhixin),
            ("量子位", self.fetch_qbitai),
            ("TechCrunch AI", self.fetch_techcrunch_ai),
            ("RSS - AI News", self.fetch_rss_ai_news),
        ]
        
        for source_name, fetch_func in sources:
            try:
                print(f"\n  正在从 {source_name} 获取新闻...")
                news = fetch_func()
                # 过滤过期新闻
                recent_news = [n for n in news if self.is_recent(n.get('date'))]
                all_news.extend(recent_news)
                print(f"  ✓ 从 {source_name} 获取 {len(news)} 条，其中 {len(recent_news)} 条在有效期内")
            except Exception as e:
                print(f"  ✗ 从 {source_name} 获取失败: {e}")
        
        # 去重（基于标题前40个字符）
        seen_titles = set()
        unique_news = []
        for item in all_news:
            title_key = item.get("title", "")[:40].lower().strip()
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(item)
        
        # 按日期排序（最新的在前）
        unique_news.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        print(f"\n  📊 总计获取 {len(unique_news)} 条有效新闻（去重后）")
        return unique_news
    
    def fetch_jiqizhixin(self):
        """获取机器之心最新文章（带时效性验证）"""
        news = []
        try:
            url = "https://r.jina.ai/http://www.jiqizhixin.com/"
            response = self.session.get(url, timeout=30)
            content = response.text
            
            lines = content.split('\n')
            i = 0
            while i < len(lines) - 2:
                line = lines[i].strip()
                
                if not line or line.startswith('Title:') or line.startswith('URL Source:'):
                    i += 1
                    continue
                
                if 15 < len(line) < 100:
                    # 查找日期
                    date_str = None
                    for j in range(i+1, min(i+10, len(lines))):
                        date_line = lines[j].strip()
                        date_str = self.parse_relative_date(date_line)
                        if date_str:
                            break
                    
                    # 如果没有找到日期或日期过期，跳过
                    if not date_str:
                        i += 1
                        continue
                    
                    title = line
                    # 过滤垃圾内容
                    if any(skip in title for skip in ['扫码', '关注', '微信', '公众号', '推荐', '精选', '下载', '编辑：']):
                        i += 1
                        continue
                    
                    news.append({
                        'title': title,
                        'link': f"https://www.jiqizhixin.com/search/articles/{title[:15]}",
                        'summary': f'{title[:80]}...',
                        'date': date_str,
                        'source': '机器之心',
                        'type': 'industry',
                        'tags': ['AI', '人工智能']
                    })
                    
                    if len(news) >= 8:
                        break
                
                i += 1
                    
        except Exception as e:
            print(f"    机器之心爬取失败: {e}")
        
        return news
    
    def fetch_qbitai(self):
        """获取量子位最新文章（带时效性验证）"""
        news = []
        try:
            url = "https://r.jina.ai/http://www.qbitai.com/"
            response = self.session.get(url, timeout=30)
            content = response.text
            
            lines = content.split('\n')
            i = 0
            
            while i < len(lines) and len(news) < 8:
                line = lines[i].strip()
                
                if not line or line.startswith('Title:') or line.startswith('URL Source:'):
                    i += 1
                    continue
                
                if 15 < len(line) < 100 and not line.startswith('[') and not line.startswith('#'):
                    if any(skip in line for skip in ['扫码', '关注', '微信', '公众号', '推荐', '下载', '联系', '投稿']):
                        i += 1
                        continue
                    
                    # 查找日期（通常在标题附近）
                    date_str = None
                    for j in range(max(0, i-3), min(i+5, len(lines))):
                        date_str = self.parse_relative_date(lines[j])
                        if date_str:
                            break
                    
                    # 如果没有找到日期，尝试从上下文推断
                    if not date_str:
                        i += 1
                        continue
                    
                    summary = ''
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if 20 < len(next_line) < 300 and not next_line.startswith('['):
                            summary = next_line[:200]
                    
                    news.append({
                        'title': line,
                        'link': f"https://www.qbitai.com/?s={line[:10]}",
                        'summary': summary if summary else f'{line[:80]}...',
                        'date': date_str,
                        'source': '量子位',
                        'type': 'industry',
                        'tags': ['AI', '人工智能']
                    })
                
                i += 1
                    
        except Exception as e:
            print(f"    量子位爬取失败: {e}")
        
        return news
    
    def fetch_techcrunch_ai(self):
        """获取 TechCrunch AI 新闻"""
        news = []
        try:
            url = "https://r.jina.ai/http://techcrunch.com/category/artificial-intelligence/"
            response = self.session.get(url, timeout=30)
            content = response.text
            
            lines = content.split('\n')
            i = 0
            
            while i < len(lines) and len(news) < 5:
                line = lines[i].strip()
                
                if not line or line.startswith('Title:') or line.startswith('URL Source:'):
                    i += 1
                    continue
                
                if 20 < len(line) < 120 and not line.startswith('[') and not line.startswith('#'):
                    if any(skip in line for skip in ['TechCrunch', 'Privacy Policy', 'Terms of', 'Advertise', 'Login', 'Sign up']):
                        i += 1
                        continue
                    
                    # TechCrunch通常有明确日期
                    date_str = self.today.strftime('%Y-%m-%d')  # 默认今天
                    
                    summary = ''
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if 20 < len(next_line) < 400 and not next_line.startswith('['):
                            summary = next_line[:250]
                    
                    news.append({
                        'title': line,
                        'link': f"https://techcrunch.com/category/artificial-intelligence/",
                        'summary': summary if summary else f'{line[:80]}...',
                        'date': date_str,
                        'source': 'TechCrunch',
                        'type': 'industry',
                        'tags': ['AI', 'Artificial Intelligence']
                    })
                
                i += 1
                    
        except Exception as e:
            print(f"    TechCrunch 爬取失败: {e}")
        
        return news
    
    def fetch_rss_ai_news(self):
        """从RSS源获取AI新闻"""
        news = []
        
        rss_sources = [
            ("AI科技评论", "https://www.aichengzi.com/feed"),
            ("InfoQ AI", "https://www.infoq.cn/feed/ai"),
        ]
        
        for source_name, rss_url in rss_sources:
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:5]:
                    # 解析发布日期
                    pub_date = None
                    if hasattr(entry, 'published'):
                        try:
                            pub_date = date_parser.parse(entry.published).strftime('%Y-%m-%d')
                        except:
                            pass
                    
                    if not pub_date:
                        continue
                    
                    # 检查时效性
                    if not self.is_recent(pub_date):
                        continue
                    
                    news.append({
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.get('summary', entry.title)[:200],
                        'date': pub_date,
                        'source': source_name,
                        'type': 'industry',
                        'tags': ['AI', '人工智能']
                    })
            except Exception as e:
                print(f"    {source_name} RSS获取失败: {e}")
        
        return news


def cleanup_old_news_files(content_dir, max_age_days=7):
    """清理过期的新闻文件"""
    content_path = Path(content_dir)
    if not content_path.exists():
        return
    
    cutoff_date = datetime.now(timezone.utc).date() - timedelta(days=max_age_days)
    removed_count = 0
    
    for f in content_path.glob("*.md"):
        if f.name == "_index.md":
            continue
        
        try:
            # 从文件名解析日期 (格式: YYYYMMDD-title.md)
            date_match = re.match(r'(\d{8})', f.name)
            if date_match:
                file_date = datetime.strptime(date_match.group(1), '%Y%m%d').date()
                if file_date < cutoff_date:
                    f.unlink()
                    removed_count += 1
        except Exception as e:
            print(f"    清理文件失败 {f.name}: {e}")
    
    if removed_count > 0:
        print(f"\n  🗑️ 清理了 {removed_count} 条过期新闻")


if __name__ == "__main__":
    scraper = NewsScraperV2()
    news = scraper.fetch_all_news()
    print(f"\n共获取 {len(news)} 条时效性新闻")
    for i, item in enumerate(news[:10]):
        print(f"{i+1}. [{item['date']}] [{item['source']}] {item['title'][:50]}")
