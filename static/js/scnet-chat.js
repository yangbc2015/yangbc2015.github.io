/**
 * SCNet AI Chatbot 网页组件
 * 位置：左下角，避免与右下角返回顶部按钮冲突
 */

(function() {
    'use strict';

    // ==================== 配置 ====================
    const CONFIG = {
        PROXY_URLS: [
            null,
            'http://localhost:8787/chat',
        ],
        SCNET_API: 'https://www.scnet.cn/api/chat/completions',
        REQUEST_INTERVAL: 2000,
        TIMEOUT: 30000,
        ENABLE_SIMULATION: true,
    };

    if (window.SCNET_WORKER_URL) {
        CONFIG.PROXY_URLS[0] = window.SCNET_WORKER_URL;
    }

    let lastRequestTime = 0;
    let isProcessing = false;
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
        for (const url of CONFIG.PROXY_URLS) {
            if (!url) continue;
            if (await testProxy(url)) {
                availableProxy = url;
                console.log('[SCNet] 使用代理:', url);
                return url;
            }
        }
        return null;
    }

    // ==================== API 调用 ====================

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
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        return data.choices?.[0]?.message?.content;
    }

    async function callViaProxy(proxyUrl, message, model = 'qwen-turbo') {
        const response = await fetch(proxyUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, model }),
        });
        if (!response.ok) throw new Error(`Proxy error: ${response.status}`);
        const data = await response.json();
        if (data.status === 'ok') return data.response;
        throw new Error(data.error || 'Unknown error');
    }

    async function sendToAI(message, onStatus) {
        const waitTime = checkRateLimit();
        if (waitTime > 0) {
            onStatus(`等待 ${(waitTime/1000).toFixed(1)}s...`);
            await new Promise(r => setTimeout(r, waitTime));
        }
        lastRequestTime = Date.now();

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

        try {
            onStatus('尝试直连...');
            const result = await callSCNetDirect(message);
            return { success: true, content: result, mode: 'direct' };
        } catch (error) {
            console.log('[SCNet] 直连失败:', error.message);
        }

        if (CONFIG.ENABLE_SIMULATION) {
            onStatus('使用模拟响应...');
            await new Promise(r => setTimeout(r, 500));
            return { success: true, content: generateSimulatedResponse(message), mode: 'simulation' };
        }

        return { success: false, error: '无法连接到 AI 服务', content: generateErrorHelp() };
    }

    // ==================== 响应生成 ====================

    function generateSimulatedResponse(message) {
        const msg = message.toLowerCase();
        
        if (/你好|hello|hi|嗨|hey/.test(msg)) {
            return `你好！我是 SCNet AI 助手 🤖

目前你看到的是**模拟回复**。

💡 **获取真实 AI 回复：**

**方法 1 - Cloudflare Worker（推荐）**
1. 访问 https://dash.cloudflare.com 注册
2. 创建 Worker，粘贴 cloudflare-worker.js 代码
3. 部署后配置 window.SCNET_WORKER_URL

**方法 2 - 本地代理**
运行：python scripts/scnet_proxy.py

**方法 3 - 直接访问官网**
https://www.scnet.cn/ui/chatbot/`;
        }
        
        if (/代码|code|python|javascript|js|编程|program/.test(msg)) {
            return `我可以帮你写代码！目前处于**模拟模式**。

\`\`\`python
def hello():
    return "Hello, SCNet!"
\`\`\`

💡 如需真实 AI，请部署 Cloudflare Worker 或运行本地代理。`;
        }
        
        return `收到："${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"

🤖 **模拟模式**

由于浏览器 CORS 限制，无法直接连接 SCNet。

**解决方案：**
1. 部署 Cloudflare Worker（5分钟，免费）
2. 本地运行：python scripts/scnet_proxy.py
3. 访问官网：https://www.scnet.cn/ui/chatbot/`;
    }

    function generateErrorHelp() {
        return `❌ **连接失败**

请尝试：
1. 部署 Cloudflare Worker
2. 运行本地代理：python scripts/scnet_proxy.py
3. 访问官网：https://www.scnet.cn/ui/chatbot/`;
    }

    // ==================== UI 创建 ====================

    function createChatWidget() {
        const widget = document.createElement('div');
        widget.id = 'scnet-chat-widget';
        widget.innerHTML = `
            <div class="scnet-chat-container">
                <div class="scnet-chat-header">
                    <div class="scnet-chat-avatar">🤖</div>
                    <div class="scnet-chat-title-group">
                        <span class="scnet-chat-title">SCNet AI</span>
                        <span class="scnet-chat-subtitle">在线</span>
                    </div>
                    <button class="scnet-chat-close" title="关闭">
                        <svg viewBox="0 0 24 24" width="18" height="18">
                            <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>
                    </button>
                </div>
                <div class="scnet-chat-messages"></div>
                <div class="scnet-chat-input-area">
                    <div class="scnet-chat-input-wrapper">
                        <input type="text" class="scnet-chat-input" placeholder="输入消息..." maxlength="500">
                        <button class="scnet-chat-send" title="发送">
                            <svg viewBox="0 0 24 24" width="20" height="20">
                                <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="scnet-chat-footer">
                    <span class="scnet-chat-status"></span>
                </div>
            </div>
        `;

        const style = document.createElement('style');
        style.textContent = `
            /* ===== AI Chat Widget - 左下角布局 ===== */
            #scnet-chat-widget {
                position: fixed;
                bottom: 2rem;
                left: 2rem;
                width: 380px;
                max-width: calc(100vw - 2rem);
                z-index: 1000;
                font-family: var(--font-primary, -apple-system, BlinkMacSystemFont, sans-serif);
            }

            .scnet-chat-container {
                background: rgba(13, 17, 23, 0.98);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 230, 118, 0.2);
                border-radius: 20px;
                box-shadow: 
                    0 25px 50px -12px rgba(0, 0, 0, 0.7),
                    0 0 0 1px rgba(0, 230, 118, 0.1),
                    0 0 40px rgba(0, 230, 118, 0.08);
                overflow: hidden;
                display: none;
                flex-direction: column;
                height: 520px;
                max-height: calc(100vh - 100px);
                animation: scnet-chat-open 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            }

            @keyframes scnet-chat-open {
                from {
                    opacity: 0;
                    transform: scale(0.95) translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: scale(1) translateY(0);
                }
            }

            /* Header */
            .scnet-chat-header {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 20px;
                background: linear-gradient(135deg, rgba(0, 230, 118, 0.12), rgba(0, 229, 255, 0.06));
                border-bottom: 1px solid rgba(0, 230, 118, 0.15);
            }

            .scnet-chat-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3);
            }

            .scnet-chat-title-group {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 2px;
            }

            .scnet-chat-title {
                font-size: 15px;
                font-weight: 600;
                color: var(--text-primary, #e6edf3);
            }

            .scnet-chat-subtitle {
                font-size: 12px;
                color: var(--neon-green, #00e676);
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .scnet-chat-subtitle::before {
                content: '';
                width: 6px;
                height: 6px;
                background: var(--neon-green, #00e676);
                border-radius: 50%;
                animation: pulse-dot 2s ease-in-out infinite;
            }

            @keyframes pulse-dot {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.6; transform: scale(0.8); }
            }

            .scnet-chat-close {
                background: rgba(255, 255, 255, 0.05);
                border: none;
                color: var(--text-muted, #8b949e);
                width: 36px;
                height: 36px;
                border-radius: 10px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
            }

            .scnet-chat-close:hover {
                background: rgba(255, 64, 129, 0.15);
                color: var(--neon-pink, #ff4081);
            }

            /* Messages */
            .scnet-chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 16px;
                scrollbar-width: thin;
                scrollbar-color: rgba(0, 230, 118, 0.3) transparent;
            }

            .scnet-chat-messages::-webkit-scrollbar {
                width: 6px;
            }

            .scnet-chat-messages::-webkit-scrollbar-track {
                background: transparent;
            }

            .scnet-chat-messages::-webkit-scrollbar-thumb {
                background: rgba(0, 230, 118, 0.3);
                border-radius: 3px;
            }

            .scnet-chat-message {
                max-width: 85%;
                font-size: 13.5px;
                line-height: 1.7;
                word-wrap: break-word;
                white-space: pre-wrap;
                animation: message-appear 0.3s ease;
            }

            @keyframes message-appear {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .scnet-chat-message.user {
                align-self: flex-end;
                background: linear-gradient(135deg, var(--neon-green, #00e676), #00c853);
                color: #000;
                padding: 12px 16px;
                border-radius: 18px 18px 4px 18px;
                font-weight: 500;
                box-shadow: 0 4px 15px rgba(0, 230, 118, 0.25);
            }

            .scnet-chat-message.ai {
                align-self: flex-start;
                background: rgba(0, 229, 255, 0.1);
                border: 1px solid rgba(0, 229, 255, 0.2);
                color: var(--text-primary, #e6edf3);
                padding: 14px 18px;
                border-radius: 18px 18px 18px 4px;
            }

            .scnet-chat-message.ai.simulation {
                border-color: rgba(255, 193, 7, 0.4);
                background: rgba(255, 193, 7, 0.05);
            }

            .scnet-chat-message.ai code {
                background: rgba(0, 0, 0, 0.4);
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
                font-size: 12px;
                color: #ff4081;
            }

            .scnet-chat-message.ai pre {
                background: rgba(0, 0, 0, 0.4);
                padding: 14px;
                border-radius: 10px;
                overflow-x: auto;
                margin: 10px 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .scnet-chat-message.ai pre code {
                background: none;
                padding: 0;
                color: #e6edf3;
            }

            .scnet-chat-message.ai a {
                color: var(--neon-blue, #00e5ff);
                text-decoration: none;
                border-bottom: 1px dotted var(--neon-blue, #00e5ff);
            }

            .scnet-chat-message.ai a:hover {
                border-bottom-style: solid;
            }

            .scnet-chat-message.ai strong {
                color: var(--neon-green, #00e676);
                font-weight: 600;
            }

            /* Input Area */
            .scnet-chat-input-area {
                padding: 16px 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                background: rgba(0, 0, 0, 0.2);
            }

            .scnet-chat-input-wrapper {
                display: flex;
                align-items: center;
                gap: 10px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 14px;
                padding: 4px;
                transition: all 0.3s;
            }

            .scnet-chat-input-wrapper:focus-within {
                border-color: var(--neon-green, #00e676);
                background: rgba(255, 255, 255, 0.08);
                box-shadow: 0 0 0 3px rgba(0, 230, 118, 0.1);
            }

            .scnet-chat-input {
                flex: 1;
                background: none;
                border: none;
                padding: 12px 14px;
                color: var(--text-primary, #e6edf3);
                font-size: 14px;
                outline: none;
            }

            .scnet-chat-input::placeholder {
                color: var(--text-muted, #6e7681);
            }

            .scnet-chat-send {
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                border: none;
                width: 38px;
                height: 38px;
                border-radius: 10px;
                color: #000;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
                flex-shrink: 0;
            }

            .scnet-chat-send:hover:not(:disabled) {
                transform: scale(1.05);
                box-shadow: 0 4px 15px rgba(0, 230, 118, 0.4);
            }

            .scnet-chat-send:disabled {
                opacity: 0.4;
                cursor: not-allowed;
            }

            /* Footer */
            .scnet-chat-footer {
                padding: 8px 20px;
                background: rgba(0, 0, 0, 0.3);
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }

            .scnet-chat-status {
                font-size: 11px;
                color: var(--text-muted, #6e7681);
            }

            /* Toggle Button - 左下角 */
            .scnet-chat-toggle {
                position: fixed;
                bottom: 2rem;
                left: 2rem;
                width: 56px;
                height: 56px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                border: none;
                color: #000;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 
                    0 4px 20px rgba(0, 230, 118, 0.4),
                    0 0 0 4px rgba(0, 230, 118, 0.1);
                transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
                z-index: 1000;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .scnet-chat-toggle:hover {
                transform: scale(1.1) rotate(10deg);
                box-shadow: 
                    0 6px 25px rgba(0, 230, 118, 0.6),
                    0 0 0 6px rgba(0, 230, 118, 0.15);
            }

            .scnet-chat-toggle.pulse {
                animation: scnet-toggle-pulse 2s ease-in-out infinite;
            }

            @keyframes scnet-toggle-pulse {
                0%, 100% { 
                    box-shadow: 0 4px 20px rgba(0, 230, 118, 0.4), 0 0 0 4px rgba(0, 230, 118, 0.1);
                }
                50% { 
                    box-shadow: 0 4px 30px rgba(0, 230, 118, 0.7), 0 0 0 8px rgba(0, 230, 118, 0.05);
                }
            }

            /* Mobile Responsive */
            @media (max-width: 480px) {
                #scnet-chat-widget {
                    width: calc(100vw - 1.5rem);
                    left: 0.75rem;
                    bottom: 5rem;
                }
                
                .scnet-chat-container {
                    height: 60vh;
                    max-height: 500px;
                    border-radius: 16px;
                }
                
                .scnet-chat-toggle {
                    bottom: 5.5rem;
                    left: 0.75rem;
                    width: 50px;
                    height: 50px;
                    font-size: 20px;
                }
                
                .scnet-chat-header {
                    padding: 12px 16px;
                }
                
                .scnet-chat-messages {
                    padding: 16px;
                }
            }

            /* Hide when back-to-top is visible (optional) */
            @media (min-width: 768px) {
                .back-to-top.visible ~ .scnet-chat-toggle {
                    /* 可以与返回顶部按钮协调 */
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
        if (!document.body.classList.contains('page-home')) return;

        const toggleBtn = createToggleButton();
        const widget = createChatWidget();

        document.body.appendChild(toggleBtn);
        document.body.appendChild(widget);

        const container = widget.querySelector('.scnet-chat-container');
        const messagesEl = widget.querySelector('.scnet-chat-messages');
        const inputEl = widget.querySelector('.scnet-chat-input');
        const sendBtn = widget.querySelector('.scnet-chat-send');
        const closeBtn = widget.querySelector('.scnet-chat-close');
        const statusEl = widget.querySelector('.scnet-chat-status');

        function renderMarkdown(text) {
            return text
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                .replace(/`(.+?)`/g, '<code>$1</code>')
                .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
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

        async function handleSend() {
            const text = inputEl.value.trim();
            if (!text || isProcessing) return;

            addMessage(text, 'user');
            inputEl.value = '';

            isProcessing = true;
            sendBtn.disabled = true;
            setStatus('发送中...');

            try {
                const result = await sendToAI(text, setStatus);
                if (result.success) {
                    addMessage(result.content, 'ai', result.mode === 'simulation');
                    setStatus(result.mode === 'simulation' ? '模拟模式 · 配置 Worker 可获得真实 AI' : '已完成');
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
            const isVisible = container.style.display === 'flex';
            if (isVisible) {
                container.style.display = 'none';
                toggleBtn.style.display = 'flex';
            } else {
                container.style.display = 'flex';
                toggleBtn.style.display = 'none';
                inputEl.focus();
                findWorkingProxy();
            }
        });

        closeBtn.addEventListener('click', () => {
            container.style.display = 'none';
            toggleBtn.style.display = 'flex';
        });

        sendBtn.addEventListener('click', handleSend);
        inputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSend();
        });

        // 欢迎消息
        setTimeout(() => {
            container.style.display = 'flex';
            toggleBtn.style.display = 'none';
            addMessage(
                `你好！我是 SCNet AI 助手 👋\n\n` +
                `我可以帮你解答问题、编写代码、分析数据。\n\n` +
                `💡 **当前是模拟模式**，如需真实 AI 回复，请：\n` +
                `• 部署 Cloudflare Worker（推荐）\n` +
                `• 或运行本地代理：python scripts/scnet_proxy.py`,
                'ai',
                true
            );
        }, 800);

        findWorkingProxy();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
