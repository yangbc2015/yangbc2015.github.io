#!/usr/bin/env python3
"""
AI投资资讯爬虫
爬取AI投资、融资、股市动态等真实数据
"""

import requests
import re
from datetime import datetime, timezone


class InvestmentScraper:
    """AI投资资讯爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_all_investments(self):
        """获取所有投资相关资讯"""
        print("  开始获取AI投资资讯...")
        
        all_items = []
        
        try:
            items = self.fetch_36kr_ai()
            all_items.extend(items)
            print(f"    ✓ 36氪AI: {len(items)}条")
        except Exception as e:
            print(f"    ✗ 36氪AI获取失败: {e}")
        
        # 去重
        seen_titles = set()
        unique_items = []
        for item in all_items:
            title_key = item.get("title", "")[:40].lower().strip()
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_items.append(item)
        
        unique_items.sort(key=lambda x: x.get('date', ''), reverse=True)
        return unique_items[:10]
    
    def fetch_36kr_ai(self):
        """从36氪获取AI投资资讯"""
        items = []
        try:
            url = "https://r.jina.ai/http://36kr.com/search/articles/AI%E8%9E%8D%E8%B5%84"
            response = self.session.get(url, timeout=30)
            content = response.text
            
            lines = content.split('\n')
            link_pattern = re.compile(r'(?:^\*\s+)?\[(?P<title>.+?)\]\((?P<url>https?://[^)]+)\)\s*(?P<date>\d{4}-\d{2}-\d{2})?$')

            for line in lines:
                line = line.strip()
                if not line or line.startswith(('Title:', 'URL Source:', 'Markdown Content:')):
                    continue

                match = link_pattern.search(line)
                if not match:
                    continue

                title = match.group('title').strip()
                article_url = match.group('url').strip()
                article_date = match.group('date') or datetime.now(timezone.utc).strftime('%Y-%m-%d')

                if not self._is_valid_investment_title(title):
                    continue

                items.append({
                    'title': title,
                    'summary': f'AI投资动态：{title[:100]}',
                    'url': article_url,
                    'date': article_date,
                    'source': '36氪',
                    'category': 'AI投资',
                    'type': self._classify_investment_type(title),
                    'tags': self._build_investment_tags(title)
                })

                if len(items) >= 8:
                    break
                    
        except Exception as e:
            print(f"    36氪爬取失败: {e}")
        
        return items

    def _is_valid_investment_title(self, title):
        """过滤 36 氪搜索结果页中的噪音条目。"""
        if len(title) < 12:
            return False

        excluded_keywords = [
            'Image', '搜索结果', '登录', '注册', '下载', 'APP', '打开APP', '免责声明',
            '首页', '快讯', '专题', '作者', '城市', '推荐', '查看更多'
        ]
        if any(keyword in title for keyword in excluded_keywords):
            return False

        required_keywords = ['AI', '人工智能', '大模型', '融资', '投资', '美元', '亿元', '芯片', '机器人', 'Anthropic', 'OpenAI']
        return any(keyword in title for keyword in required_keywords)

    def _classify_investment_type(self, title):
        """根据标题推断资讯类型。"""
        if any(keyword in title for keyword in ['研报', '报告', '券商', '高盛', '中金', '华泰', '摩根']):
            return 'report'
        if any(keyword in title for keyword in ['股', '市值', '纳指', '财报', '上涨', '下跌']):
            return 'stock'
        if any(keyword in title for keyword in ['地产', '写字楼', '楼市', '产业园']):
            return 'realestate'
        return 'news'

    def _build_investment_tags(self, title):
        """根据标题生成简单标签。"""
        tags = ['AI投资']
        keyword_map = {
            '融资': '融资',
            '投资': '投资',
            'OpenAI': 'OpenAI',
            'Anthropic': 'Anthropic',
            '机器人': '机器人',
            '芯片': '芯片',
            '大模型': '大模型',
        }
        for keyword, tag in keyword_map.items():
            if keyword in title and tag not in tags:
                tags.append(tag)
        return tags


if __name__ == "__main__":
    scraper = InvestmentScraper()
    items = scraper.fetch_all_investments()
    print(f"\n共获取 {len(items)} 条投资资讯")
    for i, item in enumerate(items[:5]):
        print(f"{i+1}. [{item['category']}] {item['title'][:50]} ({item['source']})")
