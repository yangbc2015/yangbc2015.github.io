#!/usr/bin/env python3
"""
SCNet AI Chatbot API Client
用于与国家超算互联网平台 AI 聊天机器人对话
"""

import requests
import json
import time
import re
from typing import Generator, Optional


class SCNetChatBot:
    """国家超算互联网平台 AI 聊天客户端"""
    
    def __init__(self):
        self.base_url = "https://www.scnet.cn"
        self.chat_url = "https://www.scnet.cn/api/chat/completions"
        self.session = requests.Session()
        
        # 设置请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/event-stream",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://www.scnet.cn",
            "Referer": "https://www.scnet.cn/ui/chatbot/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        
        self.last_request_time = 0
        self.min_interval = 2  # 最小请求间隔 2 秒
        
    def _wait_for_rate_limit(self):
        """请求频率控制"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            print(f"[Rate Limit] 等待 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _get_auth_token(self) -> Optional[str]:
        """获取访问令牌（如果需要）"""
        try:
            # 访问首页获取可能的 token
            resp = self.session.get(
                f"{self.base_url}/ui/chatbot/",
                headers=self.headers,
                timeout=10
            )
            
            # 尝试从页面中提取 token
            # 常见的 token 格式
            token_patterns = [
                r'"token"[:\s]*"([^"]+)"',
                r'"access_token"[:\s]*"([^"]+)"',
                r'"authorization"[:\s]*"([^"]+)"',
            ]
            
            for pattern in token_patterns:
                match = re.search(pattern, resp.text)
                if match:
                    return match.group(1)
                    
            return None
        except Exception as e:
            print(f"[Warning] 获取 token 失败: {e}")
            return None
    
    def chat(self, message: str, stream: bool = True) -> str:
        """
        发送消息并获取 AI 回复
        
        Args:
            message: 用户输入的消息
            stream: 是否使用流式响应
            
        Returns:
            AI 的完整回复文本
        """
        self._wait_for_rate_limit()
        
        # 构造请求体（根据常见 AI 接口格式）
        payload = {
            "model": "qwen-turbo",  # 默认模型，可能需要调整
            "messages": [
                {"role": "user", "content": message}
            ],
            "stream": stream,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            print(f"[Request] 发送消息: {message[:50]}...")
            
            response = self.session.post(
                self.chat_url,
                headers=self.headers,
                json=payload,
                stream=stream,
                timeout=60
            )
            
            response.raise_for_status()
            
            if stream:
                return self._parse_stream_response(response)
            else:
                return self._parse_json_response(response)
                
        except requests.exceptions.RequestException as e:
            print(f"[Error] 请求失败: {e}")
            # 尝试备用端点
            return self._try_backup_endpoint(message)
    
    def _parse_stream_response(self, response) -> str:
        """解析 SSE 流式响应"""
        full_content = []
        
        print("[Stream] 接收流式响应...")
        
        for line in response.iter_lines():
            if not line:
                continue
                
            line = line.decode('utf-8')
            
            # SSE 格式: data: {...}
            if line.startswith('data:'):
                data = line[5:].strip()
                
                # 结束标记
                if data == '[DONE]':
                    break
                    
                try:
                    json_data = json.loads(data)
                    
                    # 提取内容（OpenAI 格式）
                    if 'choices' in json_data:
                        delta = json_data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_content.append(content)
                            print(content, end='', flush=True)
                            
                except json.JSONDecodeError:
                    continue
                    
        print()  # 换行
        return ''.join(full_content)
    
    def _parse_json_response(self, response) -> str:
        """解析普通 JSON 响应"""
        try:
            data = response.json()
            
            # 常见的响应格式
            if 'choices' in data:
                return data['choices'][0]['message']['content']
            elif 'data' in data:
                return data['data']['content']
            elif 'content' in data:
                return data['content']
            elif 'message' in data:
                return data['message']
            else:
                return json.dumps(data, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[Error] 解析响应失败: {e}")
            return response.text
    
    def _try_backup_endpoint(self, message: str) -> str:
        """尝试备用端点"""
        backup_urls = [
            "https://www.scnet.cn/api/v1/chat/completions",
            "https://www.scnet.cn/api/chat",
            "https://www.scnet.cn/api/ai/chat",
        ]
        
        for url in backup_urls:
            try:
                print(f"[Backup] 尝试备用端点: {url}")
                time.sleep(1)
                
                response = self.session.post(
                    url,
                    headers=self.headers,
                    json={
                        "message": message,
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return self._parse_json_response(response)
                    
            except Exception as e:
                print(f"[Backup] {url} 失败: {e}")
                continue
                
        return "[Error] 所有端点均无法访问，请检查网络或网站状态"
    
    def chat_stream(self, message: str) -> Generator[str, None, None]:
        """
        流式生成器，逐字返回 AI 回复
        
        Args:
            message: 用户输入的消息
            
        Yields:
            每个文本片段
        """
        self._wait_for_rate_limit()
        
        payload = {
            "model": "qwen-turbo",
            "messages": [
                {"role": "user", "content": message}
            ],
            "stream": True,
            "temperature": 0.7,
        }
        
        try:
            response = self.session.post(
                self.chat_url,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            response.raise_for_status()
            
            for line in response.iter_lines():
                if not line:
                    continue
                    
                line = line.decode('utf-8')
                
                if line.startswith('data:'):
                    data = line[5:].strip()
                    
                    if data == '[DONE]':
                        break
                        
                    try:
                        json_data = json.loads(data)
                        if 'choices' in json_data:
                            delta = json_data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            yield f"[Error] {str(e)}"


def main():
    """测试函数"""
    bot = SCNetChatBot()
    
    print("=" * 50)
    print("SCNet AI Chatbot 客户端")
    print("=" * 50)
    print("提示: 输入 'quit' 或 'exit' 退出")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见!")
                break
                
            print("AI: ", end='', flush=True)
            response = bot.chat(user_input, stream=True)
            
            if not response:
                print("(无响应)")
                
        except KeyboardInterrupt:
            print("\n\n再见!")
            break
        except Exception as e:
            print(f"\n[Error] {e}")


if __name__ == "__main__":
    main()
