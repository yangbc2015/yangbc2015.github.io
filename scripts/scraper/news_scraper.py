#!/usr/bin/env python3
"""
AI 新闻爬虫
从多个来源获取 AI 相关新闻
"""

import requests
import feedparser
import re
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


class NewsScraper:
    """AI 新闻爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0'
        })
    
    def fetch_jiqizhixin(self):
        """
        获取机器之心新闻
        """
        news = []
        try:
            # 机器之心的 RSS 或 API
            url = "https://www.jiqizhixin.com/rss"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                for entry in feed.entries[:5]:
                    news.append(self._parse_entry(
                        title=entry.get('title', ''),
                        link=entry.get('link', ''),
                        summary=entry.get('summary', entry.get('description', '')),
                        date=entry.get('published', ''),
                        source="机器之心",
                        default_type="research"
                    ))
        except Exception as e:
            print(f"    机器之心 RSS 获取失败: {e}")
            # 尝试网页抓取
            news = self._fetch_jiqizhixin_web()
        
        return news
    
    def _fetch_jiqizhixin_web(self):
        """从机器之心网页抓取"""
        news = []
        try:
            url = "https://www.jiqizhixin.com/"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章列表
            articles = soup.find_all('article', limit=5)
            for article in articles:
                title_elem = article.find('h2') or article.find('h3') or article.find('a')
                if title_elem:
                    title = title_elem.get_text().strip()
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = 'https://www.jiqizhixin.com' + link
                    
                    summary_elem = article.find('p') or article.find(class_=re.compile('summary|desc'))
                    summary = summary_elem.get_text().strip()[:200] if summary_elem else ""
                    
                    news.append(self._create_news_item(
                        title=title,
                        link=link,
                        summary=summary,
                        source="机器之心",
                        news_type="research"
                    ))
        except Exception as e:
            print(f"    机器之心网页抓取失败: {e}")
        
        return news
    
    def fetch_qbitai(self):
        """
        获取量子位新闻
        """
        news = []
        try:
            # 量子位的 RSS
            url = "https://www.qbitai.com/feed"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                for entry in feed.entries[:5]:
                    news.append(self._parse_entry(
                        title=entry.get('title', ''),
                        link=entry.get('link', ''),
                        summary=entry.get('summary', entry.get('description', '')),
                        date=entry.get('published', ''),
                        source="量子位",
                        default_type="industry"
                    ))
        except Exception as e:
            print(f"    量子位 RSS 获取失败: {e}")
            # 使用备用方法
            news = self._fetch_qbitai_web()
        
        return news
    
    def _fetch_qbitai_web(self):
        """从量子位网页抓取"""
        news = []
        try:
            url = "https://www.qbitai.com/"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章
            articles = soup.find_all('article', limit=5)
            for article in articles:
                title_elem = article.find('h2') or article.find('h3')
                if title_elem:
                    link_elem = title_elem.find('a')
                    if link_elem:
                        title = link_elem.get_text().strip()
                        link = link_elem.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://www.qbitai.com' + link
                        
                        news.append(self._create_news_item(
                            title=title,
                            link=link,
                            summary="",
                            source="量子位",
                            news_type="industry"
                        ))
        except Exception as e:
            print(f"    量子位网页抓取失败: {e}")
        
        return news
    
    def fetch_techcrunch_ai(self):
        """
        获取 TechCrunch AI 新闻
        """
        news = []
        try:
            # TechCrunch AI 分类 RSS
            url = "https://techcrunch.com/category/artificial-intelligence/feed/"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                for entry in feed.entries[:3]:
                    news.append(self._parse_entry(
                        title=entry.get('title', ''),
                        link=entry.get('link', ''),
                        summary=entry.get('summary', entry.get('description', '')),
                        date=entry.get('published', ''),
                        source="TechCrunch",
                        default_type="industry"
                    ))
        except Exception as e:
            print(f"    TechCrunch 获取失败: {e}")
        
        return news
    
    def _parse_entry(self, title, link, summary, date, source, default_type="industry"):
        """解析 RSS 条目"""
        # 清理 summary 中的 HTML
        summary_clean = re.sub(r'<[^>]+>', '', summary)
        summary_clean = summary_clean[:300] + "..." if len(summary_clean) > 300 else summary_clean
        
        # 解析日期
        parsed_date = self._parse_date(date)
        
        # 判断新闻类型
        news_type = self._classify_news_type(title, summary_clean, default_type)
        
        return self._create_news_item(
            title=title,
            link=link,
            summary=summary_clean,
            source=source,
            news_type=news_type,
            date=parsed_date
        )
    
    def _parse_date(self, date_str):
        """解析日期字符串"""
        if not date_str:
            return datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        try:
            dt = date_parser.parse(date_str)
            # 转换为北京时间
            beijing_tz = timezone(timedelta(hours=8))
            dt = dt.astimezone(beijing_tz)
            return dt.strftime("%Y-%m-%d")
        except:
            return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    def _classify_news_type(self, title, summary, default_type="industry"):
        """
        根据标题和内容分类新闻类型
        """
        text = (title + " " + summary).lower()
        
        # 突破/重大发布
        breakthrough_keywords = ['突破', '发布', '推出', ' unveiled', 'announced', 'release', 'launch', 'new model']
        # 产品
        product_keywords = ['产品', 'app', '应用', '上线', 'api', '服务']
        # 研究
        research_keywords = ['研究', '论文', 'arxiv', 'paper', 'study', 'research', '模型架构', '训练']
        # 行业
        industry_keywords = ['融资', '收购', '合作', '公司', '投资', '估值', 'funding', 'acquisition']
        
        if any(kw in text for kw in breakthrough_keywords):
            return "breakthrough"
        elif any(kw in text for kw in product_keywords):
            return "product"
        elif any(kw in text for kw in research_keywords):
            return "research"
        elif any(kw in text for kw in industry_keywords):
            return "industry"
        
        return default_type
    
    def _create_news_item(self, title, link, summary, source, news_type="industry", date=None):
        """创建新闻条目"""
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # 生成标签
        tags = self._generate_tags(title, summary, news_type)
        
        return {
            "title": title,
            "link": link,
            "summary": summary or title,
            "source": source,
            "date": date,
            "type": news_type,
            "tags": tags,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_tags(self, title, summary, news_type):
        """根据内容生成标签"""
        text = (title + " " + summary).lower()
        tags = ["AI"]
        
        # 检测模型名称
        models = {
            'gpt': 'GPT',
            'chatgpt': 'ChatGPT',
            'claude': 'Claude',
            'gemini': 'Gemini',
            'llama': 'Llama',
            'deepseek': 'DeepSeek',
            'qwen': 'Qwen',
            'mistral': 'Mistral',
            'grok': 'Grok',
        }
        
        for key, tag in models.items():
            if key in text:
                tags.append(tag)
                break  # 只添加第一个匹配的模型
        
        # 检测领域
        domains = {
            '多模态': ['multimodal', '图像', '视频', 'vision'],
            '代码': ['code', 'coding', '编程', 'coder'],
            'agent': ['agent', '智能体', 'autonomous'],
            '机器人': ['robot', '机器人', '具身'],
        }
        
        for domain_tag, keywords in domains.items():
            if any(kw in text for kw in keywords):
                tags.append(domain_tag)
                if len(tags) >= 4:
                    break
        
        # 根据类型添加标签
        type_tags = {
            "breakthrough": "重大突破",
            "product": "产品发布",
            "research": "研究进展",
            "industry": "行业动态"
        }
        
        if news_type in type_tags:
            tags.append(type_tags[news_type])
        
        return list(set(tags))[:5]  # 最多 5 个标签


if __name__ == "__main__":
    import json
    
    scraper = NewsScraper()
    
    print("测试机器之心:")
    news = scraper.fetch_jiqizhixin()
    for item in news[:2]:
        print(f"  - {item['title'][:50]}... ({item['source']})")
    
    print("\n测试量子位:")
    news = scraper.fetch_qbitai()
    for item in news[:2]:
        print(f"  - {item['title'][:50]}... ({item['source']})")
