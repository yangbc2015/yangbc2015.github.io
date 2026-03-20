#!/usr/bin/env python3
"""
AI 视频爬虫
从 YouTube、B站等获取 AI 相关视频
"""

import requests
import feedparser
import re
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
        由于 B站 API 限制，返回配置好的视频列表
        """
        return [
            {
                "title": "李宏毅机器学习",
                "speaker": "李宏毅",
                "description": "台湾大学教授的机器学习经典课程",
                "duration": "45:00",
                "views": "1.8M",
                "date": "2024-01-20",
                "platform": "bilibili",
                "video_id": "bv1",
                "url": "https://www.bilibili.com/video/BV1JE411g7XF",
                "thumbnail": "",
                "type": "course",
                "category": "精品课程",
                "featured": False
            },
            {
                "title": "动手学深度学习 PyTorch版",
                "speaker": "李沐",
                "description": "AWS 首席科学家李沐的深度学习实战课程",
                "duration": "60:00",
                "views": "2.1M",
                "date": "2024-02-10",
                "platform": "bilibili",
                "video_id": "bv2",
                "url": "https://www.bilibili.com/video/BV1k64y1Q7wu",
                "thumbnail": "",
                "type": "course",
                "category": "精品课程",
                "featured": False
            }
        ]


if __name__ == "__main__":
    import json
    
    scraper = VideosScraper()
    
    print("测试获取精选视频:")
    videos = scraper.get_featured_videos()
    for v in videos[:3]:
        print(f"  - {v['title'][:40]}... ({v['speaker']})")
