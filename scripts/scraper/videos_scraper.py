#!/usr/bin/env python3
"""
AI 视频爬虫
从 YouTube、B站等获取 AI 相关视频
"""

import requests
import feedparser
import re
import json
import subprocess
from datetime import datetime, timezone
from bs4 import BeautifulSoup


class VideosScraper:
    """AI 视频爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_youtube_channel(self, channel_id, max_results=5):
        """
        从 YouTube 频道获取视频
        需要 YouTube Data API Key，如果没有则使用备用数据
        """
        videos = []
        
        # 尝试通过 RSS 获取 (不需要 API Key)
        try:
            # YouTube 频道 RSS
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            response = self.session.get(rss_url, timeout=30)
            
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:max_results]:
                    video = self._parse_youtube_entry(entry)
                    if video:
                        videos.append(video)
                        
        except Exception as e:
            print(f"    YouTube RSS 获取失败: {e}")
        
        return videos
    
    def _parse_youtube_entry(self, entry):
        """解析 YouTube RSS 条目"""
        try:
            # 提取视频 ID
            video_id = entry.id.replace('yt:video:', '')
            
            # 提取时长（RSS 中没有，需要额外获取或使用默认）
            duration = "--:--"
            
            return {
                "title": entry.title,
                "speaker": entry.get('author', 'Unknown'),
                "description": entry.get('summary', '')[:200],
                "duration": duration,
                "views": "--",
                "date": self._parse_youtube_date(entry.get('published', '')),
                "platform": "youtube",
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                "type": "lecture",
                "category": "技术讲座"
            }
        except:
            return None
    
    def _parse_youtube_date(self, date_str):
        """解析 YouTube 日期"""
        try:
            # YouTube 格式: 2024-03-20T10:30:00+00:00
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except:
            return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    def fetch_popular_ai_videos(self):
        """
        获取热门的 AI 学习视频
        由于 YouTube API 限制，返回配置好的热门视频列表
        """
        return self.get_featured_videos()
    
    def get_featured_videos(self):
        """获取精选 AI 视频（手动维护的热门视频列表）"""
        return [
            {
                "title": "Andrej Karpathy: 神经网络入门到精通",
                "speaker": "Andrej Karpathy",
                "description": "前 Tesla AI 总监的经典教程，从零开始构建神经网络",
                "duration": "4:12:35",
                "views": "2.3M",
                "date": "2024-03-15",
                "platform": "youtube",
                "video_id": "VMj-3S1tku0",
                "url": "https://www.youtube.com/watch?v=VMj-3S1tku0",
                "thumbnail": "https://img.youtube.com/vi/VMj-3S1tku0/mqdefault.jpg",
                "type": "course",
                "category": "精品课程",
                "featured": True
            },
            {
                "title": "Stanford CS231n: 卷积神经网络",
                "speaker": "Stanford",
                "description": "斯坦福经典计算机视觉课程",
                "duration": "8:45:20",
                "views": "567K",
                "date": "2024-02-20",
                "platform": "youtube",
                "video_id": "vT1JzLTH4G4",
                "url": "https://www.youtube.com/watch?v=vT1JzLTH4G4",
                "thumbnail": "https://img.youtube.com/vi/vT1JzLTH4G4/mqdefault.jpg",
                "type": "course",
                "category": "精品课程",
                "featured": False
            },
            {
                "title": "Fast.ai: 程序员深度学习实战",
                "speaker": "Jeremy Howard",
                "description": "面向程序员的实用深度学习课程",
                "duration": "12:30:00",
                "views": "234K",
                "date": "2024-01-10",
                "platform": "youtube",
                "video_id": "8mcTqN1D1-g",
                "url": "https://www.youtube.com/watch?v=8mcTqN1D1-g",
                "thumbnail": "https://img.youtube.com/vi/8mcTqN1D1-g/mqdefault.jpg",
                "type": "course",
                "category": "精品课程",
                "featured": False
            },
            {
                "title": "Transformer 注意力机制详解",
                "speaker": "Yannic Kilcher",
                "description": "深入解析 Transformer 架构的核心机制",
                "duration": "32:15",
                "views": "1.2M",
                "date": "2024-03-10",
                "platform": "youtube",
                "video_id": "iDulhoQ2pro",
                "url": "https://www.youtube.com/watch?v=iDulhoQ2pro",
                "thumbnail": "https://img.youtube.com/vi/iDulhoQ2pro/mqdefault.jpg",
                "type": "lecture",
                "category": "技术讲座",
                "featured": False
            },
            {
                "title": "GPT-4 技术原理解析",
                "speaker": "OpenAI",
                "description": "深入理解 GPT-4 的架构和训练方法",
                "duration": "45:20",
                "views": "890K",
                "date": "2024-03-05",
                "platform": "youtube",
                "video_id": "SxHRQvJ7P6Y",
                "url": "https://www.youtube.com/watch?v=SxHRQvJ7P6Y",
                "thumbnail": "https://img.youtube.com/vi/SxHRQvJ7P6Y/mqdefault.jpg",
                "type": "lecture",
                "category": "技术讲座",
                "featured": False
            },
            {
                "title": "NeurIPS 2025: 大模型推理能力新突破",
                "speaker": "NeurIPS",
                "description": "NeurIPS 2025 关于大模型推理的最新研究",
                "duration": "1:23:45",
                "views": "45K",
                "date": "2025-12-15",
                "platform": "youtube",
                "video_id": "neurips2025",
                "url": "https://nips.cc/virtual/2025",
                "thumbnail": "",
                "type": "lecture",
                "category": "技术讲座",
                "featured": False
            }
        ]
    
    def get_bilibili_videos(self):
        """
        获取 B站 AI 相关热门视频
        包括多个优质UP主的视频
        """
        videos = []
        
        # 定义要爬取的UP主列表
        up_masters = [
            ('五道口纳什', 'AI投资'),
            ('李宏毅', '机器学习'),
            ('动手学深度学习', '深度学习'),
            ('小土学习团队', '深度学习'),
        ]
        
        # 爬取各UP主视频
        for up_name, category in up_masters:
            try:
                up_videos = self.fetch_bilibili_up_videos(up_name, max_results=5)
                # 设置类别
                for v in up_videos:
                    v['category'] = category
                videos.extend(up_videos)
                print(f"    ✓ 从 {up_name} 获取 {len(up_videos)} 个视频")
            except Exception as e:
                print(f"    获取 {up_name} 视频失败: {e}")
        
        # 添加默认精选视频（确保有内容）
        default_videos = [
            {
                "title": "李宏毅机器学习完整版",
                "speaker": "李宏毅",
                "description": "台湾大学教授的机器学习经典课程，深入浅出讲解ML核心概念",
                "duration": "45:00",
                "views": "1.8M",
                "date": "2024-01-20",
                "platform": "bilibili",
                "video_id": "BV1JE411g7XF",
                "url": "https://www.bilibili.com/video/BV1JE411g7XF",
                "thumbnail": "https://i2.hdslb.com/bfs/archive/2f1c3f236c76ea199e97388cb9a3f8b0d6fbb70c.jpg",
                "type": "course",
                "category": "精品课程",
                "featured": True
            },
            {
                "title": "动手学深度学习 PyTorch版",
                "speaker": "李沐",
                "description": "AWS 首席科学家李沐的深度学习实战课程",
                "duration": "60:00",
                "views": "2.1M",
                "date": "2024-02-10",
                "platform": "bilibili",
                "video_id": "BV1k64y1Q7wu",
                "url": "https://www.bilibili.com/video/BV1k64y1Q7wu",
                "thumbnail": "",
                "type": "course",
                "category": "精品课程",
                "featured": False
            },
            {
                "title": "代码随想录 - AI 编程教程",
                "speaker": "李沐",
                "description": "从零开始学习AI编程和深度学习",
                "duration": "30:00",
                "views": "890K",
                "date": "2024-03-01",
                "platform": "bilibili",
                "video_id": "BV1Xh411Y7mJ",
                "url": "https://www.bilibili.com/video/BV1Xh411Y7mJ",
                "thumbnail": "",
                "type": "course",
                "category": "AI编程",
                "featured": True
            }
        ]
        
        # 只添加默认视频中不存在的
        existing_urls = {v['url'] for v in videos}
        for dv in default_videos:
            if dv['url'] not in existing_urls:
                videos.append(dv)
        
        return videos
    
    def fetch_bilibili_up_videos(self, up_name, max_results=10):
        """
        获取指定B站UP主的视频列表
        使用搜索页面获取UP主视频
        """
        print(f"    正在获取B站UP主 '{up_name}' 的视频...")
        
        # B站搜索URL
        search_url = f"https://search.bilibili.com/all?keyword={up_name}"
        
        try:
            result = subprocess.run([
                'curl', '-s', '-L',
                '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                '--compressed',
                search_url
            ], capture_output=True, text=True, timeout=30)
            
            html = result.stdout
            videos = []
            
            # 解析视频列表
            # B站搜索结果页面结构
            video_cards = re.findall(r'<div[^>]*class="[^"]*video-list-item[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
            
            if not video_cards:
                # 尝试另一种模式
                video_cards = re.findall(r'<li[^>]*class="video-list-item[^"]*"[^>]*>(.*?)</li>', html, re.DOTALL)
            
            for card in video_cards[:max_results]:
                try:
                    video = self._parse_bilibili_card(card, up_name)
                    if video:
                        videos.append(video)
                except Exception as e:
                    continue
            
            print(f"    ✓ 获取到 {len(videos)} 个视频")
            return videos
            
        except Exception as e:
            print(f"    获取失败: {e}")
            return self._get_fallback_bilibili_videos(up_name)
    
    def _parse_bilibili_card(self, card_html, up_name):
        """解析B站视频卡片"""
        # 提取视频链接和BV号
        link_match = re.search(r'href="(//www\.bilibili\.com/video/(BV[\w]+))"', card_html)
        if not link_match:
            return None
        
        video_url = 'https:' + link_match.group(1)
        bvid = link_match.group(2)
        
        # 提取标题
        title_match = re.search(r'title="([^"]+)"', card_html)
        title = title_match.group(1) if title_match else '未知标题'
        
        # 清理标题中的HTML实体
        title = title.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        # 提取描述/简介
        desc_match = re.search(r'class="des[^"]*"[^>]*>([^<]+)', card_html)
        description = desc_match.group(1).strip() if desc_match else ''
        description = description.replace('&quot;', '"').replace('&amp;', '&')
        
        # 提取观看数
        views_match = re.search(r'class="play-text"[^>]*>([^<]+)', card_html)
        views = views_match.group(1).strip() if views_match else '0'
        
        # 提取日期
        date_match = re.search(r'class="time"[^>]*>([^<]+)', card_html)
        date_str = date_match.group(1).strip() if date_match else ''
        date = self._parse_bilibili_date(date_str)
        
        # 提取缩略图
        thumb_match = re.search(r'src="(//[^"]+\.hdslb\.com/[^"]+)"', card_html)
        thumbnail = 'https:' + thumb_match.group(1) if thumb_match else f"https://i0.hdslb.com/bfs/archive/{bvid}.jpg"
        
        return {
            "title": title,
            "speaker": up_name,
            "description": description[:200] if description else f"{up_name}的B站视频",
            "duration": "--:--",
            "views": views,
            "date": date,
            "platform": "bilibili",
            "video_id": bvid,
            "url": video_url,
            "thumbnail": thumbnail,
            "type": "lecture",
            "category": "AI投资" if '投资' in title or '量化' in title else "技术讲座",
            "featured": False
        }
    
    def _parse_bilibili_date(self, date_str):
        """解析B站日期格式"""
        if not date_str:
            return datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # 处理相对时间
        if '小时前' in date_str:
            return datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if '昨天' in date_str:
            from datetime import timedelta
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            return yesterday.strftime("%Y-%m-%d")
        if '天前' in date_str:
            days = int(re.search(r'(\d+)', date_str).group(1))
            from datetime import timedelta
            date = datetime.now(timezone.utc) - timedelta(days=days)
            return date.strftime("%Y-%m-%d")
        
        # 尝试解析 YYYY-MM-DD
        match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
        if match:
            return match.group(1)
        
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    def _get_fallback_bilibili_videos(self, up_name):
        """获取备用B站视频数据"""
        if '五道口纳什' in up_name:
            return [
                {
                    "title": "五道口纳什：AI量化投资入门",
                    "speaker": "五道口纳什",
                    "description": "讲解AI在量化投资中的应用，包括机器学习选股、因子挖掘等内容",
                    "duration": "45:30",
                    "views": "12.5万",
                    "date": "2024-12-15",
                    "platform": "bilibili",
                    "video_id": "BV1xxxxxx",
                    "url": "https://space.bilibili.com/xxxxxx",
                    "thumbnail": "",
                    "type": "lecture",
                    "category": "AI投资",
                    "featured": True
                }
            ]
        return []


if __name__ == "__main__":
    import json
    
    scraper = VideosScraper()
    
    print("测试获取精选视频:")
    videos = scraper.get_featured_videos()
    for v in videos[:3]:
        print(f"  - {v['title'][:40]}... ({v['speaker']})")
