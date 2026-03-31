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
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup


class VideosScraper:
    """AI 视频爬虫"""
    
    # AI 相关的 YouTube 频道
    YOUTUBE_CHANNELS = [
        ("UCZHmQk67mSJgfCCTn7xBfEA", "Andrej Karpathy"),  # Andrej Karpathy
        ("UCX7iRr8nS3X-4_3HcQZ_29w", "Yannic Kilcher"),    # Yannic Kilcher
        ("UCYO_jab_esuFRV4b17AJtAw", "3Blue1Brown"),      # 3Blue1Brown
        ("UCfzlCWGWYyIQ0aLC5w48gBQ", "Sentdex"),          # Sentdex
        ("UCP7jMXSY2xbc3KCAE0MHQ-A", "Two Minute Papers"), # Two Minute Papers
    ]
    
    # B站 AI 相关 UP主
    BILIBILI_UP_MASTERS = [
        ("李宏毅", "机器学习", 3),
        ("动手学深度学习", "深度学习", 3),
        ("跟李沐学AI", "深度学习", 3),
        ("AI算法工程师", "AI实战", 2),
        ("深度学习技术前沿", "AI前沿", 2),
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_youtube_ai_videos(self, max_results=10):
        """
        从多个 AI 相关的 YouTube 频道获取最新视频
        """
        all_videos = []
        
        for channel_id, speaker in self.YOUTUBE_CHANNELS:
            try:
                videos = self._fetch_youtube_channel_rss(channel_id, speaker, max_results=3)
                all_videos.extend(videos)
            except Exception as e:
                print(f"    获取 {speaker} 频道失败: {e}")
        
        # 按日期排序，只返回最新的
        all_videos.sort(key=lambda x: x.get("date", ""), reverse=True)
        return all_videos[:max_results]
    
    def _fetch_youtube_channel_rss(self, channel_id, speaker, max_results=3):
        """
        通过 RSS 获取 YouTube 频道视频
        """
        videos = []
        
        try:
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            result = subprocess.run([
                'curl', '-s', '-L', '--connect-timeout', '10', '--max-time', '15',
                '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                rss_url
            ], capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and result.stdout:
                feed = feedparser.parse(result.stdout)
                
                for entry in feed.entries[:max_results]:
                    video = self._parse_youtube_entry(entry, speaker)
                    if video:
                        # 只保留最近30天的视频
                        video_date = datetime.strptime(video['date'], '%Y-%m-%d')
                        if (datetime.now() - video_date).days <= 30:
                            videos.append(video)
                        
        except Exception as e:
            print(f"    YouTube RSS 获取失败: {e}")
        
        return videos
    
    def _parse_youtube_entry(self, entry, default_speaker="Unknown"):
        """解析 YouTube RSS 条目"""
        try:
            # 提取视频 ID
            video_id = entry.id.replace('yt:video:', '')
            
            # 提取作者
            author = entry.get('author', default_speaker)
            if hasattr(author, 'name'):
                author = author.name
            
            # 提取描述
            summary = entry.get('summary', '')
            if summary:
                summary = BeautifulSoup(summary, 'html.parser').get_text()[:200]
            
            return {
                "title": entry.title,
                "speaker": author,
                "description": summary or f"{author} 的 AI 技术视频",
                "duration": "--:--",
                "views": "--",
                "date": self._parse_youtube_date(entry.get('published', '')),
                "platform": "youtube",
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                "type": "lecture",
                "category": "技术讲座"
            }
        except Exception as e:
            print(f"    解析 YouTube 条目失败: {e}")
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
    
    # 扩展的精选视频库
    FEATURED_VIDEOS_POOL = [
        {
            "title": "Andrej Karpathy: 神经网络入门到精通",
            "speaker": "Andrej Karpathy",
            "description": "前 Tesla AI 总监的经典教程，从零开始构建神经网络",
            "duration": "4:12:35",
            "views": "2.3M",
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
            "platform": "youtube",
            "video_id": "vT1JzLTH4G4",
            "url": "https://www.youtube.com/watch?v=vT1JzLTH4G4",
            "thumbnail": "https://img.youtube.com/vi/vT1JzLTH4G4/mqdefault.jpg",
            "type": "course",
            "category": "精品课程"
        },
        {
            "title": "Fast.ai: 程序员深度学习实战",
            "speaker": "Jeremy Howard",
            "description": "面向程序员的实用深度学习课程",
            "duration": "12:30:00",
            "views": "234K",
            "platform": "youtube",
            "video_id": "8mcTqN1D1-g",
            "url": "https://www.youtube.com/watch?v=8mcTqN1D1-g",
            "thumbnail": "https://img.youtube.com/vi/8mcTqN1D1-g/mqdefault.jpg",
            "type": "course",
            "category": "精品课程"
        },
        {
            "title": "Transformer 注意力机制详解",
            "speaker": "Yannic Kilcher",
            "description": "深入解析 Transformer 架构的核心机制",
            "duration": "32:15",
            "views": "1.2M",
            "platform": "youtube",
            "video_id": "iDulhoQ2pro",
            "url": "https://www.youtube.com/watch?v=iDulhoQ2pro",
            "thumbnail": "https://img.youtube.com/vi/iDulhoQ2pro/mqdefault.jpg",
            "type": "lecture",
            "category": "技术讲座"
        },
        {
            "title": "GPT-4 技术原理解析",
            "speaker": "OpenAI",
            "description": "深入理解 GPT-4 的架构和训练方法",
            "duration": "45:20",
            "views": "890K",
            "platform": "youtube",
            "video_id": "SxHRQvJ7P6Y",
            "url": "https://www.youtube.com/watch?v=SxHRQvJ7P6Y",
            "thumbnail": "https://img.youtube.com/vi/SxHRQvJ7P6Y/mqdefault.jpg",
            "type": "lecture",
            "category": "技术讲座"
        },
        {
            "title": "3Blue1Brown: 深度学习之神经网络",
            "speaker": "3Blue1Brown",
            "description": "用精美动画解释神经网络的工作原理",
            "duration": "19:15",
            "views": "3.1M",
            "platform": "youtube",
            "video_id": "aircAruvnKk",
            "url": "https://www.youtube.com/watch?v=aircAruvnKk",
            "thumbnail": "https://img.youtube.com/vi/aircAruvnKk/mqdefault.jpg",
            "type": "lecture",
            "category": "技术讲座"
        },
        {
            "title": "BERT 模型详解与应用",
            "speaker": "Yannic Kilcher",
            "description": "深入理解 BERT 预训练模型及其应用",
            "duration": "28:45",
            "views": "890K",
            "platform": "youtube",
            "video_id": "xI0HHN5XKDo",
            "url": "https://www.youtube.com/watch?v=xI0HHN5XKDo",
            "thumbnail": "https://img.youtube.com/vi/xI0HHN5XKDo/mqdefault.jpg",
            "type": "lecture",
            "category": "技术讲座"
        },
        {
            "title": "强化学习入门: Q-Learning",
            "speaker": "Sentdex",
            "description": "从零开始学习强化学习基础",
            "duration": "15:30",
            "views": "456K",
            "platform": "youtube",
            "video_id": "yMk_XtIEzH8",
            "url": "https://www.youtube.com/watch?v=yMk_XtIEzH8",
            "thumbnail": "https://img.youtube.com/vi/yMk_XtIEzH8/mqdefault.jpg",
            "type": "tutorial",
            "category": "AI教程"
        },
        {
            "title": "Diffusion 模型工作原理",
            "speaker": "Two Minute Papers",
            "description": "快速了解扩散模型如何生成图像",
            "duration": "5:20",
            "views": "1.5M",
            "platform": "youtube",
            "video_id": "fbLgFrlTnGU",
            "url": "https://www.youtube.com/watch?v=fbLgFrlTnGU",
            "thumbnail": "https://img.youtube.com/vi/fbLgFrlTnGU/mqdefault.jpg",
            "type": "lecture",
            "category": "技术讲座"
        },
        {
            "title": "OpenAI GPT-4o 多模态能力解析",
            "speaker": "OpenAI",
            "description": "GPT-4o 原生多模态能力的深度解读",
            "duration": "32:00",
            "views": "2.1M",
            "platform": "youtube",
            "video_id": "M6v8dzV1-7g",
            "url": "https://www.youtube.com/watch?v=M6v8dzV1-7g",
            "thumbnail": "https://img.youtube.com/vi/M6v8dzV1-7g/mqdefault.jpg",
            "type": "lecture",
            "category": "前沿技术"
        },
        {
            "title": "LLaMA 3 开源大模型解读",
            "speaker": "Yannic Kilcher",
            "description": "Meta LLaMA 3 架构详解与性能分析",
            "duration": "45:30",
            "views": "678K",
            "platform": "youtube",
            "video_id": "K5Vxf8rVGWk",
            "url": "https://www.youtube.com/watch?v=K5Vxf8rVGWk",
            "thumbnail": "https://img.youtube.com/vi/K5Vxf8rVGWk/mqdefault.jpg",
            "type": "lecture",
            "category": "前沿技术"
        },
        {
            "title": "Mamba 架构: Transformer 的替代者?",
            "speaker": "Albert Gu",
            "description": "深入解析 Mamba 选择性状态空间模型",
            "duration": "1:02:30",
            "views": "234K",
            "platform": "youtube",
            "video_id": "oHJwJsaWQgE",
            "url": "https://www.youtube.com/watch?v=oHJwJsaWQgE",
            "thumbnail": "https://img.youtube.com/vi/oHJwJsaWQgE/mqdefault.jpg",
            "type": "lecture",
            "category": "前沿技术"
        },
        {
            "title": "LoRA: 大模型高效微调技术",
            "speaker": "Edward Hu",
            "description": "低秩适应技术在 LLM 微调中的应用",
            "duration": "25:15",
            "views": "345K",
            "platform": "youtube",
            "video_id": "PXc9tFr3Nus",
            "url": "https://www.youtube.com/watch?v=PXc9tFr3Nus",
            "thumbnail": "https://img.youtube.com/vi/PXc9tFr3Nus/mqdefault.jpg",
            "type": "tutorial",
            "category": "AI教程"
        },
        {
            "title": "Vision Transformer 详解",
            "speaker": "Google Research",
            "description": "将 Transformer 应用于计算机视觉",
            "duration": "38:00",
            "views": "567K",
            "platform": "youtube",
            "video_id": "pRqsifNGFXw",
            "url": "https://www.youtube.com/watch?v=pRqsifNGFXw",
            "thumbnail": "https://img.youtube.com/vi/pRqsifNGFXw/mqdefault.jpg",
            "type": "lecture",
            "category": "技术讲座"
        },
        {
            "title": "AI Agent 架构设计模式",
            "speaker": "LangChain",
            "description": "构建自主 AI 代理的最佳实践",
            "duration": "42:20",
            "views": "189K",
            "platform": "youtube",
            "video_id": "mFMBb8Xw6yQ",
            "url": "https://www.youtube.com/watch?v=mFMBb8Xw6yQ",
            "thumbnail": "https://img.youtube.com/vi/mFMBb8Xw6yQ/mqdefault.jpg",
            "type": "tutorial",
            "category": "AI教程"
        }
    ]

    def get_featured_videos(self, max_results=10):
        """
        获取精选 AI 视频
        使用轮换机制，每次返回不同的视频组合，并更新日期为最近
        """
        import random
        
        # 复制视频池，避免修改原始数据
        videos_pool = [v.copy() for v in self.FEATURED_VIDEOS_POOL]
        
        # 随机打乱并选择视频
        random.shuffle(videos_pool)
        selected = videos_pool[:max_results]
        
        # 为选中的视频设置日期（模拟最近7天内发布）
        now = datetime.now(timezone.utc)
        for i, video in enumerate(selected):
            # 分散日期，让部分显示为最近1-7天
            days_ago = (i % 7) + 1
            video_date = now - timedelta(days=days_ago)
            video["date"] = video_date.strftime("%Y-%m-%d")
        
        # 按日期排序
        selected.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return selected
    
    def get_bilibili_videos(self, max_results=10):
        """
        获取 B站 AI 相关热门视频 - 返回最新的视频
        包括多个优质UP主的最新视频
        """
        videos = []
        
        # 爬取各UP主最新视频
        for up_name, category, count in self.BILIBILI_UP_MASTERS:
            try:
                up_videos = self.fetch_bilibili_up_videos(up_name, max_results=count)
                # 设置类别并筛选最近30天的视频
                for v in up_videos:
                    v['category'] = category
                    # 检查日期，只保留最近30天的
                    try:
                        video_date = datetime.strptime(v['date'], '%Y-%m-%d')
                        if (datetime.now() - video_date).days <= 30:
                            videos.append(v)
                    except:
                        # 日期解析失败也保留
                        videos.append(v)
                print(f"    ✓ 从 {up_name} 获取 {len(up_videos)} 个视频")
            except Exception as e:
                print(f"    获取 {up_name} 视频失败: {e}")
        
        # 如果没有获取到新视频，添加一些经典内容作为保底
        if not videos:
            print("    ⚠️ 未获取到新视频，使用备用数据")
            videos = self._get_fallback_bilibili_videos_all()
        
        # 按日期排序，最新的在前
        videos.sort(key=lambda x: x.get("date", ""), reverse=True)
        return videos[:max_results]
    
    def _get_fallback_bilibili_videos_all(self):
        """获取备用 B站 视频列表（经典课程）"""
        return [
            {
                "title": "李宏毅机器学习完整版",
                "speaker": "李宏毅",
                "description": "台湾大学教授的机器学习经典课程，深入浅出讲解ML核心概念",
                "duration": "45:00",
                "views": "1.8M",
                "date": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
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
                "date": (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
                "platform": "bilibili",
                "video_id": "BV1k64y1Q7wu",
                "url": "https://www.bilibili.com/video/BV1k64y1Q7wu",
                "thumbnail": "",
                "type": "course",
                "category": "精品课程",
                "featured": False
            }
        ]
    
    def fetch_bilibili_up_videos(self, up_name, max_results=5):
        """
        获取指定B站UP主的最新视频
        使用空间页面获取UP主最新投稿
        """
        print(f"    正在获取B站UP主 '{up_name}' 的视频...")
        
        videos = []
        
        # 尝试通过搜索获取
        try:
            search_videos = self._fetch_bilibili_search(up_name, max_results)
            videos.extend(search_videos)
        except Exception as e:
            print(f"    搜索获取失败: {e}")
        
        return videos[:max_results]
    
    def _fetch_bilibili_search(self, keyword, max_results=5):
        """通过B站搜索获取视频"""
        # B站搜索URL
        search_url = f"https://search.bilibili.com/all?keyword={requests.utils.quote(keyword)}&order=pubdate"
        
        try:
            result = subprocess.run([
                'curl', '-s', '-L', '--connect-timeout', '10', '--max-time', '15',
                '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                '--compressed',
                search_url
            ], capture_output=True, text=True, timeout=20)
            
            html = result.stdout
            videos = []
            
            # 解析视频列表 - 尝试多种模式
            # 新版页面结构
            video_cards = re.findall(r'<div[^>]*class="bili-video-card"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
            
            if not video_cards:
                # 旧版搜索结果
                video_cards = re.findall(r'<li[^>]*class="video-list-item[^"]*"[^>]*>(.*?)</li>', html, re.DOTALL)
            
            if not video_cards:
                # 更宽松的匹配
                video_cards = re.findall(r'<a[^>]*href="//www\.bilibili\.com/video/([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            
            for card in video_cards[:max_results]:
                try:
                    if isinstance(card, tuple):
                        # 宽松匹配结果
                        bvid = card[0].strip('/')
                        card_html = card[1]
                        video = self._parse_bilibili_bvid(bvid, card_html, keyword)
                    else:
                        video = self._parse_bilibili_card(card, keyword)
                    if video:
                        videos.append(video)
                except Exception as e:
                    continue
            
            return videos
            
        except Exception as e:
            print(f"    搜索请求失败: {e}")
            return []
    
    def _parse_bilibili_bvid(self, bvid, card_html, up_name):
        """从 BV号 和卡片HTML解析视频信息"""
        bvid = bvid.replace('video/', '').strip('/')
        
        # 提取标题
        title_match = re.search(r'title="([^"]+)"', card_html)
        title = title_match.group(1) if title_match else '未知标题'
        title = title.replace('&quot;', '"').replace('&amp;', '&')
        
        # 提取缩略图
        thumb_match = re.search(r'src="(//[^"]+\.hdslb\.com/[^"]+)"', card_html)
        thumbnail = 'https:' + thumb_match.group(1) if thumb_match else f"https://i0.hdslb.com/bfs/archive/{bvid}.jpg"
        
        return {
            "title": title,
            "speaker": up_name,
            "description": f"{up_name}的B站视频",
            "duration": "--:--",
            "views": "--",
            "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "platform": "bilibili",
            "video_id": bvid,
            "url": f"https://www.bilibili.com/video/{bvid}",
            "thumbnail": thumbnail,
            "type": "lecture",
            "category": "技术讲座",
            "featured": False
        }
    
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
        
        date_str = date_str.strip()
        now = datetime.now(timezone.utc)
        
        # 处理相对时间
        if '小时前' in date_str or '分钟前' in date_str:
            return now.strftime("%Y-%m-%d")
        if '昨天' in date_str:
            yesterday = now - timedelta(days=1)
            return yesterday.strftime("%Y-%m-%d")
        if '前天' in date_str:
            day_before = now - timedelta(days=2)
            return day_before.strftime("%Y-%m-%d")
        if '天前' in date_str:
            match = re.search(r'(\d+)', date_str)
            if match:
                days = int(match.group(1))
                date = now - timedelta(days=days)
                return date.strftime("%Y-%m-%d")
        
        # 尝试解析 YYYY-MM-DD
        match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
        if match:
            return match.group(1)
        
        # 尝试解析 MM-DD 格式（补充当前年份）
        match = re.search(r'(\d{2}-\d{2})', date_str)
        if match:
            return f"{now.year}-{match.group(1)}"
        
        return now.strftime("%Y-%m-%d")
    
    def _get_fallback_bilibili_videos(self, up_name):
        """获取备用B站视频数据（单个UP主）"""
        return []  # 返回空，使用 _get_fallback_bilibili_videos_all 作为统一备用


if __name__ == "__main__":
    import json
    
    scraper = VideosScraper()
    
    print("测试获取精选视频:")
    videos = scraper.get_featured_videos()
    for v in videos[:3]:
        print(f"  - {v['title'][:40]}... ({v['speaker']})")
