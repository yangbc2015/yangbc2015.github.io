#!/usr/bin/env python3
"""
AI 新闻爬虫
从多个来源获取 AI 相关新闻
"""

import requests
import re
from datetime import datetime, timezone


class NewsScraper:
    """AI 新闻爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_all_news(self):
        """获取所有AI新闻"""
        print("  开始获取AI新闻...")
        all_news = []
        
        sources = [
            ("机器之心", self.fetch_jiqizhixin),
            ("量子位", self.fetch_qbitai),
        ]
        
        for source_name, fetch_func in sources:
            try:
                print(f"\n  正在从 {source_name} 获取新闻...")
                news = fetch_func()
                all_news.extend(news)
                print(f"  ✓ 从 {source_name} 获取了 {len(news)} 条新闻")
            except Exception as e:
                print(f"  ✗ 从 {source_name} 获取失败: {e}")
        
        # 去重
        seen_titles = set()
        unique_news = []
        for item in all_news:
            title_key = item.get("title", "")[:40].lower().strip()
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(item)
        
        unique_news.sort(key=lambda x: x.get("date", ""), reverse=True)
        return unique_news[:10]
    
    def fetch_jiqizhixin(self):
        """获取机器之心最新文章"""
        news = []
        try:
            url = "https://r.jina.ai/http://www.jiqizhixin.com/"
            response = self.session.get(url, timeout=30)
            content = response.text
            
            # 提取文章：标题 + 日期 + 标签
            lines = content.split('\n')
            i = 0
            while i < len(lines) - 2:
                line = lines[i].strip()
                
                # 跳过空行和元数据
                if not line or line.startswith('Title:') or line.startswith('URL Source:'):
                    i += 1
                    continue
                
                # 检查是否是文章标题（长度适中，不是标签）
                if 15 < len(line) < 100 and '03月' not in line and '04月' not in line:
                    # 查找日期
                    date_line = ''
                    for j in range(i+1, min(i+5, len(lines))):
                        if re.match(r'\d{2}月\d{2}日', lines[j].strip()):
                            date_line = lines[j].strip()
                            break
                    
                    if date_line:
                        # 解析日期
                        try:
                            match = re.match(r'(\d{2})月(\d{2})日', date_line)
                            if match:
                                month = int(match.group(1))
                                day = int(match.group(2))
                                year = datetime.now().year
                                date_formatted = f"{year}-{month:02d}-{day:02d}"
                        except:
                            date_formatted = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                        
                        title = line
                        # 过滤
                        if any(skip in title for skip in ['扫码', '关注', '微信', '公众号', '推荐', '精选', '下载']):
                            i += 1
                            continue
                        
                        news.append({
                            'title': title,
                            'link': f"https://www.jiqizhixin.com/search/articles/{title[:15]}",
                            'summary': f'{title[:80]}...',
                            'date': date_formatted,
                            'source': '机器之心',
                            'type': 'industry',
                            'tags': ['AI', '人工智能']
                        })
                        
                        if len(news) >= 6:
                            break
                
                i += 1
                    
        except Exception as e:
            print(f"    机器之心爬取失败: {e}")
        
        return news
    
    def fetch_qbitai(self):
        """获取量子位最新文章"""
        news = []
        try:
            url = "https://r.jina.ai/http://www.qbitai.com/"
            response = self.session.get(url, timeout=30)
            content = response.text
            
            # 查找文章标题（通常是Markdown标题格式或独立段落）
            lines = content.split('\n')
            i = 0
            
            while i < len(lines) and len(news) < 5:
                line = lines[i].strip()
                
                # 跳过元数据
                if not line or line.startswith('Title:') or line.startswith('URL Source:') or line.startswith('Markdown Content:'):
                    i += 1
                    continue
                
                # 查找可能是标题的行（长度适中，不含特殊标记）
                if 15 < len(line) < 100 and not line.startswith('[') and not line.startswith('#') and 'http' not in line:
                    # 过滤
                    if any(skip in line for skip in ['扫码', '关注', '微信', '公众号', '推荐', '下载', '联系', '投稿']):
                        i += 1
                        continue
                    
                    # 检查下一行是否是描述
                    summary = ''
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if 20 < len(next_line) < 300 and not next_line.startswith('['):
                            summary = next_line[:200]
                    
                    news.append({
                        'title': line,
                        'link': f"https://www.qbitai.com/?s={line[:10]}",
                        'summary': summary if summary else f'{line[:80]}...',
                        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
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
                
                # 跳过元数据
                if not line or line.startswith('Title:') or line.startswith('URL Source:') or line.startswith('Markdown Content:'):
                    i += 1
                    continue
                
                # 查找标题行
                if 20 < len(line) < 120 and not line.startswith('[') and not line.startswith('#'):
                    # 过滤无效内容
                    if any(skip in line for skip in ['TechCrunch', 'Privacy Policy', 'Terms of', 'Advertise', 'Login', 'Sign up']):
                        i += 1
                        continue
                    
                    # 查找描述
                    summary = ''
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if 20 < len(next_line) < 400 and not next_line.startswith('['):
                            summary = next_line[:250]
                    
                    news.append({
                        'title': line,
                        'link': f"https://techcrunch.com/category/artificial-intelligence/",
                        'summary': summary if summary else f'{line[:80]}...',
                        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                        'source': 'TechCrunch',
                        'type': 'industry',
                        'tags': ['AI', 'Artificial Intelligence']
                    })
                
                i += 1
                    
        except Exception as e:
            print(f"    TechCrunch 爬取失败: {e}")
        
        return news


if __name__ == "__main__":
    scraper = NewsScraper()
    news = scraper.fetch_all_news()
    print(f"\n共获取 {len(news)} 条新闻")
    for i, item in enumerate(news[:5]):
        print(f"{i+1}. [{item['source']}] {item['title'][:50]} ({item['date']})")
