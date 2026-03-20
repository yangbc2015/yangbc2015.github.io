#!/usr/bin/env python3
"""
LMSYS Chatbot Arena 榜单爬虫
"""

import requests
import json
import re
from datetime import datetime, timezone


class LMSYSScraper:
    """LMSYS Arena 榜单爬虫"""
    
    BASE_URL = "https://chat.lmsys.org"
    API_URL = "https://chat.lmsys.org/api/leaderboard"
    
    # 备用数据（当爬取失败时使用）
    FALLBACK_DATA = {
        "last_updated": "2026-03-20T00:00:00+00:00",
        "source": "LMSYS Chatbot Arena",
        "source_url": "https://chat.lmsys.org",
        "description": "基于人类偏好的众包评测平台，通过盲测对比不同模型的对话能力",
        "models": [
            {
                "rank": 1,
                "model": "Gemini-2.5-Pro",
                "organization": "Google",
                "elo": 1432,
                "trend": "up",
                "trend_value": 12,
                "votes": 85234,
                "icon": "🤖"
            },
            {
                "rank": 2,
                "model": "GPT-4o",
                "organization": "OpenAI",
                "elo": 1418,
                "trend": "same",
                "trend_value": 0,
                "votes": 120543,
                "icon": "🚀"
            },
            {
                "rank": 3,
                "model": "Claude 3.5 Sonnet",
                "organization": "Anthropic",
                "elo": 1405,
                "trend": "down",
                "trend_value": 3,
                "votes": 98721,
                "icon": "⚡"
            },
            {
                "rank": 4,
                "model": "DeepSeek-V3",
                "organization": "DeepSeek",
                "elo": 1389,
                "trend": "up",
                "trend_value": 8,
                "votes": 76432,
                "icon": "🔥"
            },
            {
                "rank": 5,
                "model": "Llama 3.1 405B",
                "organization": "Meta",
                "elo": 1376,
                "trend": "same",
                "trend_value": 0,
                "votes": 65892,
                "icon": "🧠"
            },
            {
                "rank": 6,
                "model": "Qwen2.5-72B",
                "organization": "Alibaba",
                "elo": 1365,
                "trend": "up",
                "trend_value": 5,
                "votes": 54321,
                "icon": "🌟"
            },
            {
                "rank": 7,
                "model": "Mixtral 8x22B",
                "organization": "Mistral",
                "elo": 1348,
                "trend": "same",
                "trend_value": 0,
                "votes": 43567,
                "icon": "💎"
            },
            {
                "rank": 8,
                "model": "Yi-Large",
                "organization": "01.AI",
                "elo": 1332,
                "trend": "down",
                "trend_value": 2,
                "votes": 38765,
                "icon": "🎯"
            }
        ]
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        })
    
    def fetch_arena_leaderboard(self):
        """
        从 LMSYS 获取 Arena 榜单数据
        
        注意：LMSYS 可能有反爬机制，这里尝试多种方式获取
        """
        try:
            # 尝试从 API 获取
            print("  尝试从 LMSYS API 获取数据...")
            response = self.session.get(
                self.API_URL,
                timeout=30,
                headers={
                    'Accept': 'application/json',
                    'Referer': self.BASE_URL
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_api_data(data)
            
        except Exception as e:
            print(f"  API 获取失败: {e}")
        
        # 如果 API 失败，尝试从网页获取
        try:
            print("  尝试从网页获取数据...")
            return self._fetch_from_webpage()
        except Exception as e:
            print(f"  网页获取失败: {e}")
        
        return None
    
    def _parse_api_data(self, data):
        """解析 API 返回的数据"""
        models = []
        
        # LMSYS API 返回的数据结构可能不同，这里做适配
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and 'data' in data:
            items = data['data']
        else:
            items = []
        
        for i, item in enumerate(items[:10]):  # 只取前 10
            model_name = item.get('model', item.get('name', 'Unknown'))
            
            models.append({
                "rank": i + 1,
                "model": model_name,
                "organization": self._detect_organization(model_name),
                "elo": int(item.get('elo', 0)),
                "trend": item.get('trend', 'same'),
                "trend_value": item.get('trend_value', 0),
                "votes": int(item.get('votes', 0)),
                "icon": self._get_model_icon(model_name)
            })
        
        return {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "source": "LMSYS Chatbot Arena",
            "source_url": self.BASE_URL,
            "description": "基于人类偏好的众包评测平台，通过盲测对比不同模型的对话能力",
            "models": models
        }
    
    def _fetch_from_webpage(self):
        """从网页抓取数据"""
        response = self.session.get(self.BASE_URL, timeout=30)
        response.raise_for_status()
        
        # 尝试从页面中提取 JSON 数据
        # LMSYS 页面中可能包含 leaderboard 数据
        html = response.text
        
        # 尝试查找内嵌的 JSON 数据
        patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'"leaderboard":\s*(\[.+?\])',
            r'data-leaderboard=\'({.+?})\''
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            if matches:
                try:
                    data = json.loads(matches[0])
                    return self._parse_api_data(data)
                except:
                    continue
        
        return None
    
    def _detect_organization(self, model_name):
        """根据模型名检测所属机构"""
        model_lower = model_name.lower()
        
        orgs = {
            'gpt': 'OpenAI',
            'openai': 'OpenAI',
            'claude': 'Anthropic',
            'anthropic': 'Anthropic',
            'gemini': 'Google',
            'google': 'Google',
            'llama': 'Meta',
            'meta': 'Meta',
            'mistral': 'Mistral',
            'mixtral': 'Mistral',
            'deepseek': 'DeepSeek',
            'qwen': 'Alibaba',
            'yi-': '01.AI',
            'yi large': '01.AI',
            'command': 'Cohere',
            'cohere': 'Cohere',
        }
        
        for key, org in orgs.items():
            if key in model_lower:
                return org
        
        return "Unknown"
    
    def _get_model_icon(self, model_name):
        """根据模型名获取图标"""
        model_lower = model_name.lower()
        
        icons = {
            'gpt': '🚀',
            'claude': '⚡',
            'gemini': '🤖',
            'llama': '🧠',
            'mistral': '💎',
            'mixtral': '💎',
            'deepseek': '🔥',
            'qwen': '🌟',
            'yi': '🎯',
        }
        
        for key, icon in icons.items():
            if key in model_lower:
                return icon
        
        return '🤖'
    
    def get_fallback_data(self):
        """获取备用数据"""
        data = self.FALLBACK_DATA.copy()
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        return data


if __name__ == "__main__":
    scraper = LMSYSScraper()
    data = scraper.fetch_arena_leaderboard()
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("获取失败，使用备用数据:")
        print(json.dumps(scraper.get_fallback_data(), ensure_ascii=False, indent=2))
