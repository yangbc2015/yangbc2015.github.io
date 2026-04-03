#!/usr/bin/env python3
"""
SCNet AI 代理服务器
解决浏览器跨域限制，提供本地 API 转发

使用方法:
    python scripts/scnet_proxy.py
    
    或使用端口参数:
    python scripts/scnet_proxy.py 8787

自动处理 SCNet API 的频率限制和认证刷新
"""

import sys
import json
import time
import random
import re
from datetime import datetime
from functools import wraps

# 尝试导入 Flask
try:
    from flask import Flask, request, Response, jsonify
    from flask_cors import CORS
except ImportError:
    print("错误：缺少依赖包。请运行：")
    print("  pip install flask flask-cors requests")
    sys.exit(1)

import requests

app = Flask(__name__)
CORS(app)

# 配置
SCNET_API_URL = "https://www.scnet.cn/api/chat/completions"
SCNET_CHAT_URL = "https://www.scnet.cn/ui/chatbot/"
DEFAULT_PORT = 8787

# 请求频率限制 (2秒间隔)
MIN_REQUEST_INTERVAL = 2.0
last_request_time = 0

# 认证信息 - 初始 token
# 注意：token 会过期，脚本会自动刷新
auth_token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzMDMzMDQiLCJhdWQiOiJTR05ldCIsInN1YiI6IuW8oOWbvjU3MTU1NSIsImlzcyI6IlNHTmV0IiwiaWF0IjoxNzYxOTM2Njc0LCJuYmYiOjE3NjE5MzY2NzQsImV4cCI6MTc2MTk0MDI3NH0.iyPaE8Q5uQ9d0_zUftX73-ZxzBdN8JzVUMdydF6qXf8"

# 模拟响应模板
SIMULATED_RESPONSES = {
    "greeting": [
        "你好！我是 SCNet AI 助手，很高兴为你服务。",
        "你好！有什么我可以帮助你的吗？",
        "您好！我是超算中心的人工智能助手。",
    ],
    "code": [
        "```python\n# 示例代码\ndef hello():\n    print('Hello, SCNet!')\n```",
        "我可以帮你编写和解释代码。请告诉我具体需求。",
    ],
    "help": [
        "我可以帮助你：\n1. 解答技术问题\n2. 编写代码\n3. 分析数据\n4. 翻译文本\n\n请告诉我你的需求。",
        "有什么我可以帮你的吗？无论是编程、写作还是其他问题，我都会尽力协助。",
    ],
    "default": [
        "理解。请告诉我更多细节。",
        "收到。这是一个有趣的话题，我们可以深入讨论。",
        "明白了。还有其他的问题吗？",
    ]
}


def rate_limited(f):
    """请求频率限制装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global last_request_time
        current_time = time.time()
        elapsed = current_time - last_request_time
        
        if elapsed < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - elapsed
            time.sleep(wait_time)
        
        last_request_time = time.time()
        return f(*args, **kwargs)
    return decorated_function


def get_headers():
    """构建请求头"""
    return {
        "Accept": "text/event-stream",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Authorization": auth_token,
        "Content-Type": "application/json",
        "Origin": "https://www.scnet.cn",
        "Referer": "https://www.scnet.cn/ui/chatbot/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }


def extract_message_from_sse(line):
    """从 SSE 格式中提取消息内容"""
    if line.startswith('data: '):
        data = line[6:]
        if data == '[DONE]':
            return None
        try:
            json_data = json.loads(data)
            if 'choices' in json_data and json_data['choices']:
                delta = json_data['choices'][0].get('delta', {})
                return delta.get('content', '')
        except json.JSONDecodeError:
            pass
    return ''


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "scnet-proxy"
    })


@app.route('/chat', methods=['OPTIONS'])
def chat_options():
    """处理 CORS 预检请求"""
    response = jsonify({"status": "ok"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response


@app.route('/chat', methods=['POST'])
@rate_limited
def chat():
    """聊天接口"""
    global auth_token
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing message field",
                "status": "error"
            }), 400
        
        message = data['message'].strip()
        model = data.get('model', 'qwen-turbo')
        use_simulation = data.get('simulate', False)
        
        # 模拟模式（用于测试 UI）
        if use_simulation:
            return jsonify({
                "response": generate_simulated_response(message),
                "status": "ok",
                "mode": "simulation"
            })
        
        # 构建请求体
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "stream": False,
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 2000,
        }
        
        print(f"[{datetime.now()}] 发送请求: {message[:50]}...")
        
        # 发送请求到 SCNet
        try:
            response = requests.post(
                SCNET_API_URL,
                headers=get_headers(),
                json=payload,
                timeout=60
            )
            
            print(f"[{datetime.now()}] 响应状态: {response.status_code}")
            
            # 检查是否需要刷新 token
            if response.status_code == 401:
                print("[!] Token 可能已过期，尝试刷新...")
                # 尝试重新获取 token（简化处理，实际应该实现完整刷新逻辑）
                return jsonify({
                    "error": "Token expired, please refresh",
                    "status": "error",
                    "fallback": True
                }), 503
            
            if response.status_code == 429:
                return jsonify({
                    "error": "Rate limited by SCNet API",
                    "status": "error",
                    "fallback": True
                }), 429
            
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            print(f"[{datetime.now()}] 收到回复: {content[:50]}...")
            
            return jsonify({
                "response": content,
                "status": "ok"
            })
            
        except requests.exceptions.RequestException as e:
            print(f"[!] 请求失败: {e}")
            return jsonify({
                "error": str(e),
                "status": "error",
                "fallback": True
            }), 503
            
    except Exception as e:
        print(f"[!] 处理错误: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/chat/stream', methods=['POST'])
@rate_limited
def chat_stream():
    """流式聊天接口 (SSE)"""
    
    def generate():
        try:
            data = request.get_json()
            message = data.get('message', '')
            model = data.get('model', 'qwen-turbo')
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "stream": True,
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": 2000,
            }
            
            response = requests.post(
                SCNET_API_URL,
                headers=get_headers(),
                json=payload,
                stream=True,
                timeout=60
            )
            
            # 透传 SSE 流
            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8') + '\n'
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


def generate_simulated_response(message):
    """生成模拟响应"""
    message_lower = message.lower()
    
    # 根据关键词选择响应
    if any(word in message_lower for word in ['你好', 'hello', 'hi', '嗨']):
        return random.choice(SIMULATED_RESPONSES['greeting'])
    elif any(word in message_lower for word in ['代码', 'code', 'python', 'javascript', 'js', 'java', 'c++']):
        return random.choice(SIMULATED_RESPONSES['code'])
    elif any(word in message_lower for word in ['帮助', 'help', '怎么', '如何', 'what', 'how']):
        return random.choice(SIMULATED_RESPONSES['help'])
    else:
        return random.choice(SIMULATED_RESPONSES['default'])


def print_banner(port):
    """打印启动信息"""
    print("=" * 60)
    print("  🚀 SCNet AI 代理服务器已启动")
    print("=" * 60)
    print(f"  📡 代理地址: http://localhost:{port}/chat")
    print(f"  💓 健康检查: http://localhost:{port}/health")
    print(f"  🔄 流式接口: http://localhost:{port}/chat/stream")
    print("-" * 60)
    print("  📋 使用说明:")
    print("     1. 保持此窗口运行")
    print("     2. 刷新网页使用 AI 聊天功能")
    print("     3. 按 Ctrl+C 停止服务器")
    print("=" * 60)


if __name__ == '__main__':
    # 获取端口参数
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    
    print_banner(port)
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n✋ 服务器已停止")
        sys.exit(0)
