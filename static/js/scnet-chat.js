/**
 * SCNet AI Chatbot 网页组件
 * 集成国家超算互联网平台 AI 聊天功能
 * 
 * 优先级调用策略：
 * 1. Cloudflare Worker (如果配置了)
 * 2. 本地代理 (localhost:8787)
 * 3. 直接调用 SCNet (可能因 CORS 失败)
 * 4. 模拟模式 (最后的备选)
 */

(function() {
    'use strict';

    // ==================== 配置 ====================
    const CONFIG = {
        // 代理地址（按优先级排序）
        PROXY_URLS: [
            null, // 占位，用户可配置自己的 Worker
            'http://localhost:8787/chat',
        ],
        
        // SCNet API 直接地址（会受 CORS 限制）
        SCNET_API: 'https://www.scnet.cn/api/chat/completions',
        
        // 请求频率限制
        REQUEST_INTERVAL: 2000,
        TIMEOUT: 30000,
        
        // 模拟响应开关
        ENABLE_SIMULATION: true,
    };

    // 让用户可以配置自己的 Worker URL
    if (window.SCNET_WORKER_URL) {
        CONFIG.PROXY_URLS[0] = window.SCNET_WORKER_URL;
    }

    let lastRequestTime = 0;
    let isProcessing = false;
    let currentProxyIndex = 0;
    let availableProxy = null;

    // ==================== 工具函数 ====================

    function checkRateLimit() {
        const now = Date.now();
        const elapsed = now - lastRequestTime;
        return elapsed < CONFIG.REQUEST_INTERVAL ? CONFIG.REQUEST_INTERVAL - elapsed : 0;
    }

    async function testProxy(url) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);
            
            const response = await fetch(url.replace('/chat', '/health'), {
                method: 'GET',
                signal: controller.signal,
            }).catch(() => null);
            
            clearTimeout(timeoutId);
            return response && response.ok;
        } catch {
            return false;
        }
    }

    async function findWorkingProxy() {
        if (availableProxy) return availableProxy;

        for (let i = 0; i < CONFIG.PROXY_URLS.length; i++) {
            const url = CONFIG.PROXY_URLS[i];
            if (!url) continue;
            
            if (await testProxy(url)) {
                availableProxy = url;
                currentProxyIndex = i;
                console.log('[SCNet] 使用代理:', url);
                return url;
            }
        }
        return null;
    }

    // ==================== API 调用 ====================

    /**
     * 尝试直接调用 SCNet API（通常会因 CORS 失败）
     */
    async function callSCNetDirect(message, model = 'qwen-turbo') {
        const response = await fetch(CONFIG.SCNET_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Origin': 'https://www.scnet.cn',
                'Referer': 'https://www.scnet.cn/ui/chatbot/',
                'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzMDMzMDQiLCJhdWQiOiJTR05ldCIsInN1YiI6IuW8oOWbvjU3MTU1NSIsImlzcyI6IlNHTmV0IiwiaWF0IjoxNzYxOTM2Njc0LCJuYmYiOjE3NjE5MzY2NzQsImV4cCI6MTc2MTk0MDI3NH0.iyPaE8Q5uQ9d0_zUftX73-ZxzBdN8JzVUMdydF6qXf8',
            },
            body: JSON.stringify({
                model: model,
                messages: [{ role: 'user', content: message }],
                stream: false,
                temperature: 0.7,
                max_tokens: 2000,
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        return data.choices?.[0]?.message?.content;
    }

    /**
     * 通过代理调用
     */
    async function callViaProxy(proxyUrl, message, model = 'qwen-turbo') {
        const response = await fetch(proxyUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, model }),
        });

        if (!response.ok) {
            throw new Error(`Proxy error: ${response.status}`);
        }

        const data = await response.json();
        if (data.status === 'ok') {
            return data.response;
        }
        throw new Error(data.error || 'Unknown error');
    }

    /**
     * 主调用函数 - 智能选择调用方式
     */
    async function sendToAI(message, onStatus) {
        const waitTime = checkRateLimit();
        if (waitTime > 0) {
            onStatus(`等待 ${(waitTime/1000).toFixed(1)}s...`);
            await new Promise(r => setTimeout(r, waitTime));
        }
        lastRequestTime = Date.now();

        // 1. 尝试代理
        onStatus('连接中...');
        const proxy = await findWorkingProxy();
        
        if (proxy) {
            try {
                onStatus('通过代理请求...');
                const result = await callViaProxy(proxy, message);
                return { success: true, content: result, mode: 'proxy' };
            } catch (error) {
                console.log('[SCNet] 代理失败:', error.message);
            }
        }

        // 2. 尝试直接调用（几乎总会因 CORS 失败，但值得一试）
        try {
            onStatus('尝试直连...');
            const result = await callSCNetDirect(message);
            return { success: true, content: result, mode: 'direct' };
        } catch (error) {
            console.log('[SCNet] 直连失败:', error.message);
        }

        // 3. 模拟模式
        if (CONFIG.ENABLE_SIMULATION) {
            onStatus('使用模拟响应...');
            await new Promise(r => setTimeout(r, 500)); // 模拟延迟
            return { 
                success: true, 
                content: generateSimulatedResponse(message), 
                mode: 'simulation' 
            };
        }

        return { 
            success: false, 
            error: '无法连接到 AI 服务',
            content: generateErrorHelp()
        };
    }

    // ==================== 响应生成 ====================

    function generateSimulatedResponse(message) {
        const msg = message.toLowerCase();
        
        // 问候语
        if (/你好|hello|hi|嗨|hey/.test(msg)) {
            return `你好！我是 SCNet AI 助手 🤖

目前你看到的是**模拟回复**，因为我无法直接访问真实的 SCNet 服务。

💡 **获取真实 AI 回复的方法：**

**方法 1 - 部署 Cloudflare Worker（推荐）**
1. 访问 https://workers.cloudflare.com/ 注册免费账户
2. 创建新 Worker，粘贴 cloudflare-worker.js 的内容
3. 保存后获取 Worker URL
4. 在页面 JS 中添加：window.SCNET_WORKER_URL = '你的Worker地址'

**方法 2 - 本地代理**
运行：python scripts/scnet_proxy.py

**方法 3 - 直接访问官网**
https://www.scnet.cn/ui/chatbot/`;
        }
        
        // 代码相关
        if (/代码|code|python|javascript|js|编程|program/.test(msg)) {
            return `我可以帮你写代码！不过目前处于**模拟模式**。

比如，这是一个 Python 示例：

\`\`\`python
def greet(name):
    return f"Hello, {name}!"

print(greet("SCNet"))
\`\`\`

💡 如需真实 AI 编程助手，请查看上一条消息中的连接方案。`;
        }
        
        // 默认回复
        return `收到你的消息："${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"

🤖 **当前状态：模拟模式**

由于浏览器安全限制（CORS），我无法直接连接到 SCNet 的服务器。

**如何获得真实 AI 回复？**

1. **最简单**：部署 Cloudflare Worker（免费，5分钟搞定）
   - 复制 cloudflare-worker.js 到 Worker
   - 配置 window.SCNET_WORKER_URL

2. **本地测试**：运行 python scripts/scnet_proxy.py

3. **直接使用**：访问 https://www.scnet.cn/ui/chatbot/`;
    }

    function generateErrorHelp() {
        return `❌ **无法连接到 AI 服务**

所有连接方式都失败了：
- ❌ 代理服务器未运行
- ❌ 直接连接被浏览器阻止（CORS）

**解决方案：**

1. **部署 Cloudflare Worker**（推荐，一劳永逸）
2. **本地运行代理**：\`python scripts/scnet_proxy.py\`
3. **访问官网**：https://www.scnet.cn/ui/chatbot/`;
    }

    // ==================== UI 创建 ====================

    function createChatWidget() {
        const widget = document.createElement('div');
        widget.id = 'scnet-chat-widget';
        widget.innerHTML = `
            <div class="scnet-chat-container">
                <div class="scnet-chat-header">
                    <span class="scnet-chat-title">🤖 SCNet AI 助手</span>
                    <button class="scnet-chat-close" title="关闭">×</button>
                </div>
                <div class="scnet-chat-messages"></div>
                <div class="scnet-chat-input-area">
                    <input type="text" class="scnet-chat-input" placeholder="输入消息，按 Enter 发送..." maxlength="500">
                    <button class="scnet-chat-send" title="发送">➤</button>
                </div>
                <div class="scnet-chat-status"></div>
            </div>
        `;

        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            #scnet-chat-widget {
                position: fixed;
                bottom: 100px;
                right: 20px;
                width: 400px;
                max-width: calc(100vw - 40px);
                z-index: 9998;
                font-family: var(--font-primary, -apple-system, BlinkMacSystemFont, sans-serif);
            }
            .scnet-chat-container {
                background: rgba(13, 17, 23, 0.98);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 230, 118, 0.3);
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 230, 118, 0.15);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                max-height: 550px;
            }
            .scnet-chat-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 14px 18px;
                background: linear-gradient(135deg, rgba(0, 230, 118, 0.15), rgba(0, 229, 255, 0.08));
                border-bottom: 1px solid rgba(0, 230, 118, 0.25);
            }
            .scnet-chat-title {
                font-size: 15px;
                font-weight: 600;
                color: var(--neon-green, #00e676);
                text-shadow: 0 0 10px rgba(0, 230, 118, 0.3);
            }
            .scnet-chat-close {
                background: none;
                border: none;
                color: var(--text-muted, #8b949e);
                font-size: 22px;
                cursor: pointer;
                padding: 0;
                width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s;
                border-radius: 6px;
            }
            .scnet-chat-close:hover {
                color: var(--neon-green, #00e676);
                background: rgba(0, 230, 118, 0.1);
            }
            .scnet-chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 18px;
                max-height: 380px;
                display: flex;
                flex-direction: column;
                gap: 14px;
            }
            .scnet-chat-message {
                padding: 12px 16px;
                border-radius: 14px;
                max-width: 88%;
                font-size: 13.5px;
                line-height: 1.7;
                word-wrap: break-word;
                white-space: pre-wrap;
            }
            .scnet-chat-message.user {
                align-self: flex-end;
                background: linear-gradient(135deg, rgba(0, 230, 118, 0.2), rgba(0, 230, 118, 0.1));
                border: 1px solid rgba(0, 230, 118, 0.35);
                color: var(--text-primary, #e6edf3);
                border-bottom-right-radius: 4px;
            }
            .scnet-chat-message.ai {
                align-self: flex-start;
                background: rgba(0, 229, 255, 0.12);
                border: 1px solid rgba(0, 229, 255, 0.25);
                color: var(--text-primary, #e6edf3);
                border-bottom-left-radius: 4px;
            }
            .scnet-chat-message.ai code {
                background: rgba(0, 0, 0, 0.4);
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Fira Code', monospace;
                font-size: 12px;
                color: #ff4081;
            }
            .scnet-chat-message.ai pre {
                background: rgba(0, 0, 0, 0.4);
                padding: 12px;
                border-radius: 8px;
                overflow-x: auto;
                margin: 8px 0;
            }
            .scnet-chat-message.ai pre code {
                background: none;
                padding: 0;
                color: #e6edf3;
            }
            .scnet-chat-message.ai a {
                color: var(--neon-blue, #00e5ff);
                text-decoration: none;
            }
            .scnet-chat-message.ai a:hover {
                text-decoration: underline;
            }
            .scnet-chat-message.ai strong {
                color: var(--neon-green, #00e676);
            }
            .scnet-chat-message.simulation {
                border-left: 3px solid rgba(255, 193, 7, 0.6);
            }
            .scnet-chat-input-area {
                display: flex;
                gap: 10px;
                padding: 14px 18px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(0, 0, 0, 0.25);
            }
            .scnet-chat-input {
                flex: 1;
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                padding: 10px 14px;
                color: var(--text-primary, #e6edf3);
                font-size: 14px;
                outline: none;
                transition: all 0.3s;
            }
            .scnet-chat-input:focus {
                border-color: var(--neon-green, #00e676);
                background: rgba(255, 255, 255, 0.08);
                box-shadow: 0 0 0 3px rgba(0, 230, 118, 0.1);
            }
            .scnet-chat-input::placeholder {
                color: var(--text-muted, #6e7681);
            }
            .scnet-chat-send {
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                border: none;
                border-radius: 10px;
                color: #000;
                width: 40px;
                height: 40px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                transition: all 0.2s;
                font-weight: bold;
            }
            .scnet-chat-send:hover:not(:disabled) {
                transform: scale(1.08);
                box-shadow: 0 0 20px rgba(0, 230, 118, 0.5);
            }
            .scnet-chat-send:disabled {
                opacity: 0.4;
                cursor: not-allowed;
            }
            .scnet-chat-status {
                padding: 6px 18px;
                font-size: 11px;
                color: var(--text-muted, #8b949e);
                text-align: center;
                min-height: 22px;
                background: rgba(0, 0, 0, 0.2);
            }
            .scnet-chat-toggle {
                position: fixed;
                bottom: 100px;
                right: 20px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                border: none;
                color: #000;
                font-size: 26px;
                cursor: pointer;
                box-shadow: 0 4px 20px rgba(0, 230, 118, 0.4);
                transition: all 0.3s;
                z-index: 9997;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .scnet-chat-toggle:hover {
                transform: scale(1.1) rotate(5deg);
                box-shadow: 0 6px 25px rgba(0, 230, 118, 0.6);
            }
            .scnet-chat-toggle.pulse {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { box-shadow: 0 4px 20px rgba(0, 230, 118, 0.4); }
                50% { box-shadow: 0 4px 30px rgba(0, 230, 118, 0.7); }
            }
            @media (max-width: 480px) {
                #scnet-chat-widget {
                    width: calc(100vw - 30px);
                    right: 15px;
                    bottom: 90px;
                }
                .scnet-chat-container {
                    max-height: 60vh;
                }
            }
        `;
        document.head.appendChild(style);

        return widget;
    }

    function createToggleButton() {
        const btn = document.createElement('button');
        btn.className = 'scnet-chat-toggle pulse';
        btn.innerHTML = '🤖';
        btn.title = 'SCNet AI 助手';
        return btn;
    }

    // ==================== 初始化 ====================

    async function init() {
        // 只在首页显示
        if (!document.body.classList.contains('page-home')) {
            return;
        }

        const toggleBtn = createToggleButton();
        const widget = createChatWidget();
        widget.style.display = 'none';

        document.body.appendChild(toggleBtn);
        document.body.appendChild(widget);

        const messagesEl = widget.querySelector('.scnet-chat-messages');
        const inputEl = widget.querySelector('.scnet-chat-input');
        const sendBtn = widget.querySelector('.scnet-chat-send');
        const closeBtn = widget.querySelector('.scnet-chat-close');
        const statusEl = widget.querySelector('.scnet-chat-status');

        // 简单的 Markdown 渲染
        function renderMarkdown(text) {
            return text
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                .replace(/`(.+?)`/g, '<code>$1</code>')
                .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
                .replace(/```[\s\S]*?```/g, match => {
                    const code = match.slice(3, -3).trim();
                    return `<pre><code>${code}</code></pre>`;
                });
        }

        function addMessage(text, sender, isSimulation = false) {
            const msgEl = document.createElement('div');
            msgEl.className = `scnet-chat-message ${sender}`;
            if (isSimulation) msgEl.classList.add('simulation');
            
            if (sender === 'ai') {
                msgEl.innerHTML = renderMarkdown(text);
                // 为新窗口打开链接
                msgEl.querySelectorAll('a').forEach(a => {
                    a.target = '_blank';
                    a.rel = 'noopener';
                });
            } else {
                msgEl.textContent = text;
            }
            
            messagesEl.appendChild(msgEl);
            messagesEl.scrollTop = messagesEl.scrollHeight;
            return msgEl;
        }

        function setStatus(text) {
            statusEl.textContent = text;
        }

        async function sendMessage() {
            const text = inputEl.value.trim();
            if (!text || isProcessing) return;

            addMessage(text, 'user');
            inputEl.value = '';

            isProcessing = true;
            sendBtn.disabled = true;
            setStatus('准备发送...');

            try {
                const result = await sendToAI(text, setStatus);
                
                if (result.success) {
                    addMessage(result.content, 'ai', result.mode === 'simulation');
                    setStatus(result.mode === 'simulation' ? '模拟模式' : '已完成');
                } else {
                    addMessage(result.content, 'ai', true);
                    setStatus('请求失败');
                }
            } catch (error) {
                addMessage('抱歉，发生了意外错误。', 'ai', true);
                setStatus('错误');
            } finally {
                isProcessing = false;
                sendBtn.disabled = false;
                inputEl.focus();
            }
        }

        // 事件监听
        toggleBtn.addEventListener('click', () => {
            const isVisible = widget.style.display !== 'none';
            widget.style.display = isVisible ? 'none' : 'block';
            toggleBtn.style.display = isVisible ? 'flex' : 'none';
            if (!isVisible) {
                inputEl.focus();
                findWorkingProxy();
            }
        });

        closeBtn.addEventListener('click', () => {
            widget.style.display = 'none';
            toggleBtn.style.display = 'flex';
        });

        sendBtn.addEventListener('click', sendMessage);
        inputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // 欢迎消息
        setTimeout(() => {
            addMessage(
                `你好！我是 SCNet AI 助手 🤖\n\n` +
                `💡 **小提示**：由于浏览器限制，我目前运行在**模拟模式**。\n\n` +
                `要获得真实 AI 回复，你可以：\n` +
                `• 部署 Cloudflare Worker（5分钟，免费）\n` +
                `• 本地运行代理：python scripts/scnet_proxy.py\n\n` +
                `发送消息试试吧！`,
                'ai',
                true
            );
        }, 500);

        // 预查找代理
        findWorkingProxy();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
