#!/usr/bin/env python3
"""
CSDN 博客爬虫
爬取指定用户的所有博客文章
"""

import requests
import time
import re
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse


class CSDNScraper:
    """CSDN 博客爬虫"""
    
    def __init__(self, username):
        self.username = username
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://blog.csdn.net/',
        })
        self.base_url = f"https://blog.csdn.net/{username}"
        self.articles = []
        
    def fetch_all_articles(self, max_pages=10):
        """
        获取所有文章列表
        CSDN 使用分页加载，每页大约 20-40 篇文章
        使用 curl 命令绕过 Cloudflare 防护
        """
        import subprocess
        
        print(f"  开始获取用户 '{self.username}' 的博客文章...")
        
        # 尝试不同的分页方式
        page = 1
        while page <= max_pages:
            try:
                # CSDN 分页 URL 格式
                if page == 1:
                    url = self.base_url
                else:
                    url = f"{self.base_url}/article/list/{page}"
                
                print(f"    正在获取第 {page} 页...")
                
                # 使用 curl 获取页面（绕过 Cloudflare）
                result = subprocess.run([
                    'curl', '-s', '-L',
                    '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                    '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    '--compressed',
                    url
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    print(f"    页面 {page} 获取失败，停止获取")
                    break
                
                html = result.stdout
                
                # 解析文章列表
                articles = self._parse_article_list_html(html)
                
                if not articles:
                    print(f"    第 {page} 页没有文章，停止获取")
                    break
                
                self.articles.extend(articles)
                print(f"    ✓ 第 {page} 页获取到 {len(articles)} 篇文章")
                
                # 检查是否有下一页
                if not self._has_next_page_html(html, page):
                    break
                
                page += 1
                time.sleep(1)  #  polite delay
                
            except Exception as e:
                print(f"    获取第 {page} 页失败: {e}")
                break
        
        print(f"  ✓ 共获取 {len(self.articles)} 篇文章")
        return self.articles
    
    def _parse_article_list_html(self, html):
        """从HTML字符串解析文章列表"""
        articles = []
        
        # 解析文章列表 - 查找 blog-list-box 结构
        pattern = r'<article class="blog-list-box"[^>]*>.*?<a href="(https://blog\.csdn\.net/' + self.username + r'/article/details/(\d+))"[^>]*>.*?<h4[^>]*>(.*?)</h4>.*?</article>'
        matches = re.findall(pattern, html, re.DOTALL)
        
        seen_ids = set()
        for url, article_id, title_html in matches:
            if article_id in seen_ids:
                continue
            seen_ids.add(article_id)
            
            # 清理标题
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            title = title.replace('&quot;', '"').replace('&amp;', '&')
            
            if len(title) > 5:
                # 从标题提取分类
                category_match = re.search(r'[【\[](.+?)[】\]]', title)
                category = category_match.group(1) if category_match else '技术文章'
                
                # 设置难度级别
                level = 'intermediate'
                if '基础' in title or '入门' in title:
                    level = 'beginner'
                elif '优化' in title or '进阶' in title or '高级' in title:
                    level = 'advanced'
                
                articles.append({
                    'title': title,
                    'url': url,
                    'article_id': article_id,
                    'summary': f'{category}相关技术文章',
                    'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                    'views': '0',
                    'category': category,
                    'level': level,
                    'source': 'CSDN',
                    'author': self.username
                })
        
        return articles
    
    def _has_next_page_html(self, html, current_page):
        """检查HTML中是否有下一页"""
        # 简单检查：如果页面内容较少，可能是最后一页
        if len(html) < 50000:
            return False
        return True
    
    def _parse_article_list(self, soup):
        """解析文章列表页面"""
        articles = []
        
        # CSDN 文章列表选择器（可能有多种布局）
        article_selectors = [
            '.article-item-box',  # 新版布局
            '.blog-list-box .blog-list-box-top',  # 另一种布局
            '.article-list .article-item',  # 旧版布局
            'main .article-item',  # 通用选择器
        ]
        
        article_boxes = []
        for selector in article_selectors:
            article_boxes = soup.select(selector)
            if article_boxes:
                break
        
        for box in article_boxes:
            try:
                article = self._parse_article_item(box)
                if article:
                    articles.append(article)
            except Exception as e:
                print(f"    解析文章项失败: {e}")
                continue
        
        return articles
    
    def _parse_article_item(self, box):
        """解析单个文章项"""
        article = {}
        
        # 标题
        title_elem = box.select_one('h4 a') or box.select_one('.title a') or box.select_one('a[href*="/article/details/"]')
        if title_elem:
            article['title'] = title_elem.get_text(strip=True)
            article['url'] = urljoin('https://blog.csdn.net/', title_elem.get('href', ''))
        else:
            return None
        
        # 摘要/描述
        desc_elem = box.select_one('.content .desc') or box.select_one('.article-desc') or box.select_one('.summary')
        if desc_elem:
            article['summary'] = desc_elem.get_text(strip=True)[:300]
        else:
            article['summary'] = ''
        
        # 日期
        date_elem = box.select_one('.date') or box.select_one('.time') or box.select_one('.article-info span')
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            article['date'] = self._parse_date(date_text)
        else:
            article['date'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # 阅读数
        read_elem = box.select_one('.read-num') or box.select_one('.view') or box.select_one('.num.read')
        if read_elem:
            read_text = read_elem.get_text(strip=True)
            article['views'] = self._parse_number(read_text)
        else:
            article['views'] = '0'
        
        # 分类/标签
        category_elem = box.select_one('.article-type') or box.select_one('.category')
        if category_elem:
            article['category'] = category_elem.get_text(strip=True)
        else:
            # 从标题提取分类，如 【AI系统】xxx
            match = re.search(r'【(.+?)】', article.get('title', ''))
            article['category'] = match.group(1) if match else '技术文章'
        
        article['source'] = 'CSDN'
        article['author'] = self.username
        
        return article
    
    def _parse_date(self, date_text):
        """解析日期字符串"""
        # CSDN 日期格式：2025.06.19 或 2025-06-19 或 3天前
        date_text = date_text.replace('博文更新于', '').strip()
        
        # 尝试多种格式
        formats = [
            '%Y.%m.%d',
            '%Y-%m-%d',
            '%Y/%m/%d',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_text[:10], fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        
        # 如果是相对时间，返回今天
        if '前' in date_text or '天' in date_text or '小时' in date_text:
            return datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        return datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    def _parse_number(self, num_text):
        """解析数字（处理 1.2k 这种格式）"""
        num_text = num_text.lower().replace(',', '')
        
        if 'k' in num_text:
            try:
                return str(int(float(num_text.replace('k', '')) * 1000))
            except:
                pass
        
        if 'w' in num_text or '万' in num_text:
            try:
                return str(int(float(num_text.replace('w', '').replace('万', '')) * 10000))
            except:
                pass
        
        # 提取数字
        numbers = re.findall(r'\d+', num_text)
        return numbers[0] if numbers else '0'
    
    def _has_next_page(self, soup, current_page):
        """检查是否有下一页"""
        # 查找分页控件
        pagination = soup.select_one('.pagination') or soup.select_one('.page-nav') or soup.select_one('.page-box')
        
        if pagination:
            # 查找下一页链接
            next_link = pagination.select_one('a[href*="list/{}"]'.format(current_page + 1))
            if next_link:
                return True
            
            # 或者检查是否有"下一页"文本
            next_text = pagination.find(string=re.compile(r'下一页|Next'))
            if next_text:
                parent = next_text.parent
                if parent and parent.name == 'a':
                    return True
                # 检查是否禁用状态
                if parent and 'disabled' not in str(parent.get('class', [])):
                    return True
        
        # 检查文章数量，如果少于一定数量，可能是最后一页
        article_count = len(soup.select('.article-item-box'))
        if article_count < 5:  # 如果少于5篇文章，可能是最后一页
            return False
        
        return True
    
    def fetch_article_content(self, url):
        """
        获取单篇文章的完整内容
        注意：CSDN 可能有反爬虫，这里简化处理
        """
        try:
            print(f"    获取文章内容: {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取文章内容
            content_selectors = [
                'article',
                '.article-content',
                '.blog-content-box',
                '#content_views',
                '.markdown_views',
            ]
            
            content = None
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if content:
                # 清理内容
                for script in content.find_all('script'):
                    script.decompose()
                for style in content.find_all('style'):
                    style.decompose()
                
                return {
                    'html': str(content),
                    'text': content.get_text(separator='\n', strip=True),
                }
            
            return None
            
        except Exception as e:
            print(f"    获取文章内容失败: {e}")
            return None
    
    def get_fallback_articles(self):
        """获取备用文章数据（当爬虫失败时使用）"""
        return [
            {
                "title": "【AI系统】一文讲完CPU计算与调度机制",
                "summary": "深入讲解 CPU 计算原理与调度机制，包括进程调度、中断处理、上下文切换等核心概念...",
                "url": "https://blog.csdn.net/heroybc/article/details/XXXXX",
                "date": "2025-06-29",
                "views": "1309",
                "category": "AI系统",
                "source": "CSDN",
                "author": "heroybc"
            },
            {
                "title": "【AI系统】一文讲完NPU计算与调度机制",
                "summary": "NPU 架构与调度机制详解，涵盖硬件映射空间、调度灵活性、吞吐量与延迟权衡...",
                "url": "https://blog.csdn.net/heroybc/article/details/XXXXX",
                "date": "2025-06-19",
                "views": "3263",
                "category": "AI系统",
                "source": "CSDN",
                "author": "heroybc"
            },
            {
                "title": "【AI工具链】CNN/LLM模型量化全解-以TensorRT为例",
                "summary": "AI模型量化技术详解，包括模型压缩、转换、量化和优化，以 TensorRT 为例...",
                "url": "https://blog.csdn.net/heroybc/article/details/XXXXX",
                "date": "2025-05-10",
                "views": "1366",
                "category": "AI工具链",
                "source": "CSDN",
                "author": "heroybc"
            },
            {
                "title": "【高性能计算】Sort排序的CUDA计算优化加速",
                "summary": "CUDA 并行排序算法优化，包括冒泡排序、归并排序、双调排序的 GPU 实现...",
                "url": "https://blog.csdn.net/heroybc/article/details/XXXXX",
                "date": "2025-05-05",
                "views": "1015",
                "category": "高性能计算",
                "source": "CSDN",
                "author": "heroybc"
            },
            {
                "title": "【机器学习】监督学习算法-二分类/多分类/回归",
                "summary": "监督学习核心算法详解，包括 KNN、威斯康辛乳腺癌分类、波士顿房价预测实战...",
                "url": "https://blog.csdn.net/heroybc/article/details/XXXXX",
                "date": "2025-01-27",
                "views": "511",
                "category": "机器学习",
                "source": "CSDN",
                "author": "heroybc"
            }
        ]


def main():
    """测试爬虫"""
    scraper = CSDNScraper('heroybc')
    
    # 尝试获取文章
    articles = scraper.fetch_all_articles(max_pages=5)
    
    if not articles:
        print("\n使用备用数据...")
        articles = scraper.get_fallback_articles()
    
    print(f"\n共获取 {len(articles)} 篇文章:\n")
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article['title']}")
        print(f"   分类: {article['category']}")
        print(f"   日期: {article['date']}")
        print(f"   阅读: {article['views']}")
        print()


if __name__ == "__main__":
    main()
