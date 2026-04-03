#!/usr/bin/env python3
"""
Puppeteer 基础爬虫类
用于爬取 JavaScript 渲染的页面
"""

import asyncio
from pyppeteer import launch
from typing import Optional, Dict, Any
import json


class BasePuppeteerScraper:
    """基于 Puppeteer 的基础爬虫类"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.page = None
    
    async def init_browser(self):
        """初始化浏览器"""
        self.browser = await launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080',
            ]
        )
        self.page = await self.browser.newPage()
        
        # 设置 User-Agent
        await self.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 设置视口
        await self.page.setViewport({'width': 1920, 'height': 1080})
    
    async def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
    
    async def fetch_page(self, url: str, wait_for_selector: Optional[str] = None, 
                        timeout: int = 30000) -> str:
        """
        获取页面内容
        
        Args:
            url: 页面URL
            wait_for_selector: 等待元素加载完成的选择器
            timeout: 超时时间（毫秒）
        
        Returns:
            页面HTML内容
        """
        if not self.browser:
            await self.init_browser()
        
        try:
            await self.page.goto(url, {'waitUntil': 'networkidle2', 'timeout': timeout})
            
            # 等待特定元素加载（如果有）
            if wait_for_selector:
                await self.page.waitForSelector(wait_for_selector, {'timeout': timeout})
                # 额外等待确保数据渲染完成
                await asyncio.sleep(2)
            else:
                # 默认等待一些时间让JS执行
                await asyncio.sleep(3)
            
            content = await self.page.content()
            return content
            
        except Exception as e:
            print(f"  页面获取失败: {e}")
            return ""
    
    async def extract_data_from_page(self, url: str, extraction_js: str,
                                     wait_for_selector: Optional[str] = None) -> Any:
        """
        使用 JavaScript 从页面提取数据
        
        Args:
            url: 页面URL
            extraction_js: 用于提取数据的 JavaScript 代码
            wait_for_selector: 等待元素加载完成的选择器
        
        Returns:
            提取的数据
        """
        if not self.browser:
            await self.init_browser()
        
        try:
            await self.page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 30000})
            
            if wait_for_selector:
                await self.page.waitForSelector(wait_for_selector, {'timeout': 30000})
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(3)
            
            # 执行 JavaScript 提取数据
            data = await self.page.evaluate(extraction_js)
            return data
            
        except Exception as e:
            print(f"  数据提取失败: {e}")
            return None
    
    def run_sync(self, coro):
        """同步运行异步函数"""
        return asyncio.get_event_loop().run_until_complete(coro)


# 便捷函数：快速获取JS渲染页面
def fetch_js_page(url: str, wait_for_selector: Optional[str] = None) -> str:
    """
    获取 JavaScript 渲染的页面内容
    
    Args:
        url: 页面URL
        wait_for_selector: 等待元素加载完成的选择器
    
    Returns:
        页面HTML内容
    """
    scraper = BasePuppeteerScraper(headless=True)
    try:
        content = scraper.run_sync(scraper.fetch_page(url, wait_for_selector))
        return content
    finally:
        scraper.run_sync(scraper.close_browser())


if __name__ == "__main__":
    # 测试
    test_url = "https://www.google.com"
    print(f"测试获取页面: {test_url}")
    html = fetch_js_page(test_url)
    print(f"获取内容长度: {len(html)}")
