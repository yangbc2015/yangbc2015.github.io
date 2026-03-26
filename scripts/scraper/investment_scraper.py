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
            url = "https://r.jina.ai/http://36kr.com/search/articles/AI%E6%8A%95%E8%B5%84"
            response = self.session.get(url, timeout=30)
            content = response.text
            
            # 解析文章列表
            lines = content.split('\n')
            i = 0
            
            while i < len(lines) and len(items) < 8:
                line = lines[i].strip()
                
                # 跳过元数据
                if not line or line.startswith('Title:') or line.startswith('URL Source:'):
                    i += 1
                    continue
                
                # 查找可能是标题的行
                if 15 < len(line) < 100 and any(kw in line for kw in ['融资', '投资', 'AI', '人工智能', '大模型', '亿元', '美元', '融资']):
                    # 过滤
                    if any(skip in line for skip in ['扫码', '关注', '微信', '公众号', '推荐']):
                        i += 1
                        continue
                    
                    items.append({
                        'title': line,
                        'summary': f'AI投资动态：{line[:100]}',
                        'url': f"https://36kr.com/search/articles/{line[:15]}",
                        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                        'source': '36氪',
                        'category': 'AI投资',
                        'type': 'news',
                        'tags': ['AI投资', '融资']
                    })
                
                i += 1
                    
        except Exception as e:
            print(f"    36氪爬取失败: {e}")
        
        return items


if __name__ == "__main__":
    scraper = InvestmentScraper()
    items = scraper.fetch_all_investments()
    print(f"\n共获取 {len(items)} 条投资资讯")
    for i, item in enumerate(items[:5]):
        print(f"{i+1}. [{item['category']}] {item['title'][:50]} ({item['source']})")
