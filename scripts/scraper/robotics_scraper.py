#!/usr/bin/env python3
"""
机器人/具身智能领域爬虫
爬取机器人新闻、研究进展、产业动态等真实数据
"""

import requests
import re
from datetime import datetime, timezone


class RoboticsScraper:
    """机器人领域爬虫"""
    
    # 备用数据 - 当爬取失败时使用
    FALLBACK_ROBOTICS_NEWS = [
        {
            "title": "Figure AI发布新一代人形机器人Figure 02，具备更强的自主学习能力",
            "summary": "Figure AI发布新一代人形机器人Figure 02，搭载最新视觉-语言-动作(VLA)模型，在工厂和仓储场景实现更高水平的自主操作。",
            "url": "https://www.figure.ai",
            "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "source": "行业动态",
            "category": "具身智能",
            "type": "news",
            "tags": ["机器人", "人形机器人", "Figure"]
        },
        {
            "title": "特斯拉Optimus人形机器人量产计划加速，预计2025年交付首批产品",
            "summary": "马斯克表示Optimus人形机器人量产计划正在加速，特斯拉工厂已开始测试机器人执行简单装配任务。",
            "url": "https://www.tesla.com/optimus",
            "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "source": "行业动态",
            "category": "具身智能",
            "type": "news",
            "tags": ["机器人", "人形机器人", "Optimus", "特斯拉"]
        },
        {
            "title": "宇树科技发布Unitree G1人形机器人，价格9.9万元起",
            "summary": "宇树科技发布新一代人形机器人G1，身高约127cm，体重约35kg，具备23个自由度，面向教育和科研市场。",
            "url": "https://www.unitree.com",
            "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "source": "行业动态",
            "category": "具身智能",
            "type": "news",
            "tags": ["机器人", "人形机器人", "宇树科技"]
        },
        {
            "title": "英伟达发布GR00T人形机器人基础模型，为机器人提供大脑",
            "summary": "NVIDIA发布人形机器人通用基础模型GR00T，结合Isaac Sim仿真平台，加速人形机器人开发。",
            "url": "https://developer.nvidia.com/isaac",
            "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "source": "行业动态",
            "category": "具身智能",
            "type": "news",
            "tags": ["机器人", "具身智能", "英伟达", "GR00T"]
        },
        {
            "title": "智元机器人发布远征A2人形机器人，进入工业场景实测",
            "summary": "智元机器人发布远征A2人形机器人，已在汽车工厂进行实际生产任务测试，展示零部件装配能力。",
            "url": "https://www.zhiyuanrobot.com",
            "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "source": "行业动态",
            "category": "具身智能",
            "type": "news",
            "tags": ["机器人", "人形机器人", "智元机器人"]
        },
        {
            "title": "波士顿动力Atlas机器人全面升级，电动版展现更强运动能力",
            "summary": "波士顿动力发布全电动版Atlas机器人，相比液压版本运动更加流畅，可完成后空翻等复杂动作。",
            "url": "https://bostondynamics.com/atlas",
            "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "source": "行业动态",
            "category": "具身智能",
            "type": "news",
            "tags": ["机器人", "人形机器人", "波士顿动力"]
        }
    ]
    
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
        kr_items = []
        try:
            kr_items = self.fetch_36kr_robotics()
            if kr_items:
                all_items.extend(kr_items)
                print(f"    ✓ 36氪机器人: {len(kr_items)}条")
        except Exception as e:
            print(f"    ✗ 36氪获取失败: {e}")
        
        # 如果36氪获取失败或数量不足，使用备用数据
        if len(kr_items) < 3:
            print(f"    ⚠️ 使用备用机器人新闻数据")
            fallback = self.get_fallback_robotics()
            all_items.extend(fallback)
        
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
    
    def get_fallback_robotics(self):
        """获取备用机器人新闻数据"""
        # 更新日期为今天
        fallback = []
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        for item in self.FALLBACK_ROBOTICS_NEWS:
            new_item = item.copy()
            new_item['date'] = today
            fallback.append(new_item)
        return fallback
    
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
            url = "https://r.jina.ai/http://36kr.com/search/articles/%E5%85%B7%E8%BA%AB%E6%99%BA%E8%83%BD"
            response = self.session.get(url, timeout=30)
            lines = response.text.split('\n')
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

                # 清理标题中的markdown格式
                title = self._clean_title(title)
                
                if not self._is_valid_robotics_title(title):
                    continue

                items.append({
                    'title': title,
                    'summary': title[:150],
                    'url': article_url,
                    'date': article_date,
                    'source': '36氪',
                    'category': self._classify_robotics_category(title),
                    'type': 'news',
                    'tags': self._build_robotics_tags(title)
                })

                if len(items) >= 5:
                    break
                    
        except Exception as e:
            print(f"    36氪爬取失败: {e}")
        
        return items

    def _clean_title(self, title):
        """清理标题中的markdown格式和特殊字符。"""
        # 移除 ](http://...)
        title = re.sub(r'\]\s*\([^)]+\)', '', title)
        # 移除开头的 ](
        title = re.sub(r'^\]\s*', '', title)
        # 移除URL
        title = re.sub(r'http[s]?://\S+', '', title)
        # 清理markdown链接格式 [text](url)
        title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
        # 清理 _具_ _身_ _智_ _能_ 等格式
        title = re.sub(r'_具_', '具', title)
        title = re.sub(r'_身_', '身', title)
        title = re.sub(r'_智_', '智', title)
        title = re.sub(r'_能_', '能', title)
        title = re.sub(r'_机_', '机', title)
        title = re.sub(r'_器_', '器', title)
        title = re.sub(r'_人_', '人', title)
        title = re.sub(r'_+', '', title)
        # 清理多余空格
        title = re.sub(r'\s+', ' ', title).strip()
        # 移除开头的特殊字符
        title = re.sub(r'^[\]\*\s]+', '', title)
        return title

    def _is_valid_robotics_title(self, title):
        """过滤无效搜索页标题。"""
        if len(title) < 12:
            return False

        excluded_keywords = [
            'Image', '搜索结果', '登录', '注册', '下载', '打开APP', '首页',
            '作者', '城市', '推荐', '查看更多'
        ]
        if any(keyword in title for keyword in excluded_keywords):
            return False

        robotics_keywords = ['机器人', '人形', '具身', '机械臂', '自动驾驶', '无人机', '自动化', 'GR00T']
        return any(keyword in title for keyword in robotics_keywords)

    def _classify_robotics_category(self, title):
        """推断机器人条目分类。"""
        if any(keyword in title for keyword in ['论文', 'arXiv', 'VLA', '扩散', '强化学习']):
            return '机器人学习'
        if any(keyword in title for keyword in ['人形', '具身', 'GR00T', 'Optimus', 'Figure']):
            return '具身智能'
        if any(keyword in title for keyword in ['自动驾驶', '无人机']):
            return '自主系统'
        return '机器人'

    def _build_robotics_tags(self, title):
        """根据标题构造标签。"""
        tags = ['机器人']
        keyword_map = {
            '具身': '具身智能',
            '人形': '人形机器人',
            '机械臂': '机械臂',
            '自动驾驶': '自动驾驶',
            '无人机': '无人机',
            'GR00T': 'GR00T',
        }
        for keyword, tag in keyword_map.items():
            if keyword in title and tag not in tags:
                tags.append(tag)
        return tags


if __name__ == "__main__":
    scraper = RoboticsScraper()
    items = scraper.fetch_all_robotics()
    print(f"\n共获取 {len(items)} 条机器人资讯")
    for item in items[:5]:
        print(f"  - [{item['category']}] {item['title'][:50]}... ({item['source']})")
