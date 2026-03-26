#!/usr/bin/env python3
"""
机器人/具身智能领域爬虫
爬取机器人新闻、研究进展、产业动态等真实数据
"""

import requests
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup


class RoboticsScraper:
    """机器人领域爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_all_robotics(self):
        """获取所有机器人相关资讯"""
        print("  开始获取机器人领域资讯...")
        
        all_items = []
        
        # 从arXiv获取最新机器人论文
        try:
            items = self.fetch_arxiv_robotics()
            all_items.extend(items)
            print(f"    ✓ arXiv机器人论文: {len(items)}条")
        except Exception as e:
            print(f"    ✗ arXiv获取失败: {e}")
        
        # 从36氪获取机器人新闻
        try:
            items = self.fetch_36kr_robotics()
            all_items.extend(items)
            print(f"    ✓ 36氪机器人: {len(items)}条")
        except Exception as e:
            print(f"    ✗ 36氪获取失败: {e}")
        
        # 去重
        seen_titles = set()
        unique_items = []
        for item in all_items:
            title_key = item.get("title", "")[:50].lower().strip()
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_items.append(item)
        
        # 按日期排序，返回最新10条
        unique_items.sort(key=lambda x: x.get('date', ''), reverse=True)
        return unique_items[:10]
    
    def fetch_arxiv_robotics(self):
        """从arXiv获取最新机器人论文"""
        items = []
        try:
            import feedparser
            
            # arXiv cs.RO (机器人学) 分类
            url = "http://export.arxiv.org/api/query?search_query=cat:cs.RO&sortBy=submittedDate&sortOrder=descending&max_results=5"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:5]:
                    try:
                        arxiv_id = entry.id.split('/abs/')[-1] if '/abs/' in entry.id else entry.id
                        
                        # 提取摘要
                        summary = entry.get('summary', '').replace('\n', ' ').strip()
                        summary = re.sub(r'\s+', ' ', summary)[:250]
                        
                        # 提取作者
                        authors = [author.get('name', '') for author in entry.get('authors', [])]
                        authors_str = ', '.join(authors[:2]) + (' et al.' if len(authors) > 2 else '')
                        
                        # 解析日期
                        published = entry.get('published', '')
                        date_str = published[:10] if published else datetime.now(timezone.utc).strftime('%Y-%m-%d')
                        
                        items.append({
                            'title': entry.title.replace('\n', ' ').strip(),
                            'summary': summary + "..." if len(entry.get('summary', '')) > 250 else summary,
                            'url': entry.link,
                            'date': date_str,
                            'source': 'arXiv',
                            'category': '机器人学习',
                            'type': 'paper',
                            'arxiv_id': arxiv_id,
                            'authors': authors_str,
                            'tags': ['机器人学习', '研究论文', 'arXiv']
                        })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"    arXiv获取失败: {e}")
        
        return items
    
    def fetch_36kr_robotics(self):
        """从36氪获取机器人新闻"""
        items = []
        try:
            # 36氪机器人/具身智能频道
            url = "https://36kr.com/search/articles/%E6%9C%BA%E5%99%A8%E4%BA%BA"
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            
            # 解析文章列表
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', class_=re.compile('article-item|article-card'))
            
            for article in articles[:5]:
                try:
                    title_elem = article.find('a', class_=re.compile('title')) or article.find('h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    
                    # 只保留机器人相关文章
                    if not any(kw in title for kw in ['机器人', '人形', '具身', '机械臂', '自动化']):
                        continue
                    
                    link_elem = title_elem if title_elem.name == 'a' else article.find('a')
                    link = link_elem.get('href', '') if link_elem else ''
                    if link and not link.startswith('http'):
                        link = 'https://36kr.com' + link
                    
                    summary_elem = article.find('p') or article.find(class_=re.compile('summary|desc'))
                    summary = summary_elem.get_text().strip()[:200] if summary_elem else ""
                    
                    items.append({
                        'title': title,
                        'summary': summary,
                        'url': link,
                        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                        'source': '36氪',
                        'category': '机器人',
                        'type': 'news',
                        'tags': ['机器人', '具身智能']
                    })
                except:
                    continue
                    
        except Exception as e:
            print(f"    36氪爬取失败: {e}")
        
        return items


if __name__ == "__main__":
    scraper = RoboticsScraper()
    items = scraper.fetch_all_robotics()
    print(f"\n共获取 {len(items)} 条机器人资讯")
    for item in items[:5]:
        print(f"  - [{item['category']}] {item['title'][:50]}... ({item['source']})")
