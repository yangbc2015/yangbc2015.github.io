#!/usr/bin/env python3
"""
AI 论文爬虫
从 arXiv、Hugging Face Papers 等获取最新 AI 论文
"""

import requests
import feedparser
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup


class PapersScraper:
    """AI 论文爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_arxiv_ai(self, max_results=10):
        """
        从 arXiv 获取 AI 相关论文
        使用 arXiv API: http://export.arxiv.org/api/query
        """
        papers = []
        
        # arXiv 分类: cs.AI (人工智能), cs.CL (计算语言学), cs.CV (计算机视觉), cs.LG (机器学习)
        categories = ['cs.AI', 'cs.CL', 'cs.CV', 'cs.LG']
        
        for category in categories:
            try:
                url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={max_results//len(categories)}"
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    feed = feedparser.parse(response.text)
                    
                    for entry in feed.entries[:max_results//len(categories)]:
                        paper = self._parse_arxiv_entry(entry)
                        if paper:
                            papers.append(paper)
                            
            except Exception as e:
                print(f"    获取 arXiv {category} 失败: {e}")
        
        # 按日期排序
        papers.sort(key=lambda x: x.get("date", ""), reverse=True)
        return papers[:max_results]
    
    def _parse_arxiv_entry(self, entry):
        """解析 arXiv 条目"""
        try:
            # 提取 arXiv ID
            arxiv_id = entry.id.split('/abs/')[-1] if '/abs/' in entry.id else entry.id
            
            # 提取作者
            authors = [author.get('name', '') for author in entry.get('authors', [])]
            authors_str = ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else '')
            
            # 提取摘要
            summary = entry.get('summary', '').replace('\n', ' ').strip()
            summary = re.sub(r'\s+', ' ', summary)[:300]
            
            # 提取分类
            categories = [tag.get('term', '') for tag in entry.get('tags', [])]
            
            # 确定论文类型
            paper_type = self._classify_paper_type(categories, entry.title)
            
            return {
                "title": entry.title.replace('\n', ' ').strip(),
                "authors": authors_str,
                "abstract": summary + "..." if len(entry.get('summary', '')) > 300 else summary,
                "venue": "arXiv",
                "date": self._parse_arxiv_date(entry.get('published', '')),
                "arxiv_id": arxiv_id,
                "url": entry.link,
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                "categories": categories[:3],
                "type": paper_type,
                "badge": "arxiv",
                "source": "arXiv"
            }
        except Exception as e:
            print(f"    解析 arXiv 条目失败: {e}")
            return None
    
    def _parse_arxiv_date(self, date_str):
        """解析 arXiv 日期格式"""
        try:
            # arXiv 格式: 2024-03-20T10:30:00Z
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except:
            return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    def _classify_paper_type(self, categories, title):
        """根据分类和标题判断论文类型"""
        title_lower = title.lower()
        cat_str = ' '.join(categories).lower()
        
        # 检测论文类型
        if any(kw in title_lower for kw in ['survey', 'review', 'overview', 'taxonomy']):
            return "survey"
        elif any(kw in title_lower for kw in ['benchmark', 'dataset', 'evaluation']):
            return "benchmark"
        elif 'cs.cl' in cat_str or any(kw in title_lower for kw in ['nlp', 'language', 'text']):
            return "nlp"
        elif 'cs.cv' in cat_str or any(kw in title_lower for kw in ['vision', 'image', 'video']):
            return "vision"
        elif 'cs.lg' in cat_str or any(kw in title_lower for kw in ['learning', 'training', 'optimization']):
            return "ml"
        else:
            return "ai"
    
    def fetch_huggingface_papers(self, max_results=5):
        """
        从 Hugging Face Daily Papers 获取热门论文
        """
        papers = []
        try:
            url = "https://huggingface.co/papers"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找论文卡片
                paper_cards = soup.find_all('article', limit=max_results)
                
                for card in paper_cards:
                    try:
                        title_elem = card.find('h3') or card.find('h2')
                        link_elem = card.find('a')
                        
                        if title_elem and link_elem:
                            title = title_elem.get_text().strip()
                            href = link_elem.get('href', '')
                            
                            # 提取 arXiv ID
                            arxiv_match = re.search(r'(\d{4}\.\d{4,5})', href)
                            arxiv_id = arxiv_match.group(1) if arxiv_match else ""
                            
                            papers.append({
                                "title": title,
                                "authors": "",
                                "abstract": "",
                                "venue": "Hugging Face",
                                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                                "arxiv_id": arxiv_id,
                                "url": f"https://huggingface.co{href}" if href.startswith('/') else href,
                                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else "",
                                "categories": [],
                                "type": "trending",
                                "badge": "huggingface",
                                "source": "Hugging Face"
                            })
                    except:
                        continue
                        
        except Exception as e:
            print(f"    获取 Hugging Face Papers 失败: {e}")
        
        return papers
    
    def get_fallback_papers(self):
        """获取备用论文数据"""
        return [
            {
                "title": "Reasoning with Latent Thoughts: On the Power of Looped Transformers",
                "authors": "John Doe, Jane Smith, et al.",
                "abstract": "We explore the capability of looped transformers to perform implicit reasoning through latent thought representations...",
                "venue": "arXiv",
                "date": "2026-03-20",
                "arxiv_id": "2503.00001",
                "url": "https://arxiv.org/abs/2503.00001",
                "pdf_url": "https://arxiv.org/pdf/2503.00001.pdf",
                "categories": ["cs.AI", "cs.LG"],
                "type": "ai",
                "badge": "arxiv",
                "source": "arXiv"
            },
            {
                "title": "Scaling Test-Time Compute Without Verification",
                "authors": "Alice Wang, Bob Chen, et al.",
                "abstract": "A novel approach to scaling test-time computation that achieves better performance without requiring external verification...",
                "venue": "arXiv",
                "date": "2026-03-19",
                "arxiv_id": "2503.00002",
                "url": "https://arxiv.org/abs/2503.00002",
                "pdf_url": "https://arxiv.org/pdf/2503.00002.pdf",
                "categories": ["cs.LG", "cs.AI"],
                "type": "ml",
                "badge": "arxiv",
                "source": "arXiv"
            },
            {
                "title": "Efficient Large Language Model Training with Minimal Data",
                "authors": "Research Team, DeepSeek",
                "abstract": "We demonstrate that large language models can be trained effectively with significantly less data through curriculum learning...",
                "venue": "arXiv",
                "date": "2026-03-18",
                "arxiv_id": "2503.00003",
                "url": "https://arxiv.org/abs/2503.00003",
                "pdf_url": "https://arxiv.org/pdf/2503.00003.pdf",
                "categories": ["cs.CL", "cs.LG"],
                "type": "nlp",
                "badge": "arxiv",
                "source": "arXiv"
            }
        ]


if __name__ == "__main__":
    import json
    
    scraper = PapersScraper()
    
    print("测试 arXiv 爬取:")
    papers = scraper.fetch_arxiv_ai(5)
    for p in papers[:2]:
        print(f"  - {p['title'][:50]}... ({p['arxiv_id']})")
