#!/usr/bin/env python3
"""
SCNet AI Chatbot 后端代理服务器
用于解决浏览器跨域 (CORS) 问题

使用方法:
    python scnet_proxy.py
    
默认监听: http://localhost:8787
"""

import json
import time
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests


# 配置
CONFIG = {
    'API_BASE': 'https://www.scnet.cn',
    'API_ENDPOINT': '/api/chat/completions',
    'PROXY_PORT': 8787,
    'REQUEST_TIMEOUT': 60,
    'RATE_LIMIT_SECONDS': 2,
}

last_request_time = 0


def check_rate_limit():
    """检查请求频率"""
    global last_request_time
    current_time = time.time()
    elapsed = current_time - last_request_time
    if elapsed < CONFIG['RATE_LIMIT_SECONDS']:
        time.sleep(CONFIG['RATE_LIMIT_SECONDS'] - elapsed)
    last_request_time = time.time()


class CORSRequestHandler(BaseHTTPRequestHandler):
    """支持 CORS 的 HTTP 请求处理器"""

    def _set_cors_headers(self):
        """设置 CORS 响应头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        """处理 OPTIONS 预检请求"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/':
            self._serve_index()
        elif path == '/health':
            self._serve_health()
        elif path == '/chat':
            params = parse_qs(parsed.query)
            message = params.get('message', [''])[0]
            if message:
                self._handle_chat(message)
            else:
                self._serve_error(400, 'Missing message parameter')
        else:
            self._serve_error(404, 'Not found')

    def do_POST(self):
        """处理 POST 请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/chat':
            self._handle_chat_post()
        else:
            self._serve_error(404, 'Not found')

    def _serve_index(self):
        """服务首页"""
        html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SCNet AI Proxy</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #00e676; }
        .endpoint { background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }
        code { background: #e0e0e0; padding: 2px 6px; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>🤖 SCNet AI Proxy Server</h1>
    <p>后端代理服务器运行正常</p>
    
    <div class="endpoint">
        <h3>API 端点</h3>
        <p><strong>POST</strong> <code>/chat</code></p>
        <p>请求体: <code>{"message": "你的问题"}</code></p>
        <p>响应: <code>{"response": "AI回复", "status": "ok"}</code></p>
    </div>
    
    <div class="endpoint">
        <h3>测试</h3>
        <input type="text" id="msg" placeholder="输入消息" style="width: 300px; padding: 8px;">
        <button onclick="send()" style="padding: 8px 20px;">发送</button>
        <pre id="result" style="background: #f5f5f5; padding: 15px; margin-top: 20px;"></pre>
    </div>
    
    <script>
        async function send() {
            const msg = document.getElementById('msg').value;
            const result = document.getElementById('result');
            result.textContent = '请求中...';
            
            try {
                const resp = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await resp.json();
                result.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
                result.textContent = '错误: ' + e.message;
            }
        }
    </script>
</body>
</html>
'''
        self._serve_html(html)

    def _serve_health(self):
        """健康检查"""
        self._serve_json({'status': 'ok', 'service': 'SCNet AI Proxy'})

    def _handle_chat(self, message: str):
        """处理 GET 聊天请求"""
        try:
            response = self._call_scnet_api(message)
            self._serve_json({'response': response, 'status': 'ok'})
        except Exception as e:
            self._serve_error(500, str(e))

    def _handle_chat_post(self):
        """处理 POST 聊天请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            
            if not message:
                self._serve_error(400, 'Missing message')
                return
                
            response = self._call_scnet_api(message)
            self._serve_json({'response': response, 'status': 'ok'})
        except json.JSONDecodeError:
            self._serve_error(400, 'Invalid JSON')
        except Exception as e:
            self._serve_error(500, str(e))

    def _call_scnet_api(self, message: str) -> str:
        """调用 SCNet API"""
        check_rate_limit()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/event-stream',
            'Content-Type': 'application/json',
            'Origin': 'https://www.scnet.cn',
            'Referer': 'https://www.scnet.cn/ui/chatbot/',
        }
        
        payload = {
            'model': 'qwen-turbo',
            'messages': [{'role': 'user', 'content': message}],
            'stream': True,
            'temperature': 0.7,
            'max_tokens': 2000,
        }
        
        url = CONFIG['API_BASE'] + CONFIG['API_ENDPOINT']
        
        try:
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=CONFIG['REQUEST_TIMEOUT']
            )
            resp.raise_for_status()
            
            # 解析 SSE 流
            full_text = []
            for line in resp.iter_lines():
                if not line:
                    continue
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    data = line[5:].strip()
                    if data == '[DONE]':
                        break
                    try:
                        json_data = json.loads(data)
                        content = json_data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        if content:
                            full_text.append(content)
                    except:
                        pass
            
            return ''.join(full_text) if full_text else '（无响应）'
            
        except requests.exceptions.RequestException as e:
            return f"[Error] API 请求失败: {e}"

    def _serve_html(self, html: str):
        """发送 HTML 响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _serve_json(self, data: dict):
        """发送 JSON 响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _serve_error(self, code: int, message: str):
        """发送错误响应"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'error': message, 'status': 'error'}).encode('utf-8'))

    def log_message(self, format, *args):
        """自定义日志"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")


def run_server(port: int = None):
    """启动代理服务器"""
    port = port or CONFIG['PROXY_PORT']
    server = HTTPServer(('0.0.0.0', port), CORSRequestHandler)
    print(f"\n🤖 SCNet AI Proxy Server")
    print(f"启动成功: http://localhost:{port}")
    print(f"API 端点: http://localhost:{port}/chat")
    print(f"按 Ctrl+C 停止\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_server(port)
