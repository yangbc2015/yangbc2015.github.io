/**
 * SCNet AI Chatbot 网页组件
 * 集成国家超算互联网平台 AI 聊天功能
 */

(function() {
    'use strict';

    // 配置
    const CONFIG = {
        // 优先使用本地代理（避免 CORS）
        PROXY_URL: 'http://localhost:8787/chat',
        // 直接 API（会被 CORS 阻止）
        API_BASE: 'https://www.scnet.cn',
        API_ENDPOINT: '/api/chat/completions',
        MODEL: 'qwen-turbo',
        MAX_TOKENS: 2000,
        TEMPERATURE: 0.7,
        REQUEST_INTERVAL: 2000, // 2秒间隔
        USE_PROXY: true,  // 设为 true 使用代理，false 尝试直接访问
    };

    let lastRequestTime = 0;
    let isProcessing = false;

    /**
     * 检查请求频率
     */
    function checkRateLimit() {
        const now = Date.now();
        const elapsed = now - lastRequestTime;
        if (elapsed < CONFIG.REQUEST_INTERVAL) {
            return CONFIG.REQUEST_INTERVAL - elapsed;
        }
        return 0;
    }

    /**
     * 创建聊天组件 UI
     */
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
                    <input type="text" class="scnet-chat-input" placeholder="输入消息..." maxlength="500">
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
                width: 380px;
                max-width: calc(100vw - 40px);
                z-index: 9998;
                font-family: var(--font-primary, -apple-system, BlinkMacSystemFont, sans-serif);
            }
            .scnet-chat-container {
                background: rgba(13, 17, 23, 0.95);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 230, 118, 0.3);
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 230, 118, 0.1);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                max-height: 500px;
            }
            .scnet-chat-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background: linear-gradient(135deg, rgba(0, 230, 118, 0.1), rgba(0, 229, 255, 0.05));
                border-bottom: 1px solid rgba(0, 230, 118, 0.2);
            }
            .scnet-chat-title {
                font-size: 14px;
                font-weight: 600;
                color: var(--neon-green, #00e676);
            }
            .scnet-chat-close {
                background: none;
                border: none;
                color: var(--text-muted, #8b949e);
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: color 0.3s;
            }
            .scnet-chat-close:hover {
                color: var(--neon-green, #00e676);
            }
            .scnet-chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                max-height: 300px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .scnet-chat-message {
                padding: 10px 14px;
                border-radius: 12px;
                max-width: 85%;
                font-size: 13px;
                line-height: 1.5;
                word-wrap: break-word;
            }
            .scnet-chat-message.user {
                align-self: flex-end;
                background: rgba(0, 230, 118, 0.15);
                border: 1px solid rgba(0, 230, 118, 0.3);
                color: var(--text-primary, #e6edf3);
            }
            .scnet-chat-message.ai {
                align-self: flex-start;
                background: rgba(0, 229, 255, 0.1);
                border: 1px solid rgba(0, 229, 255, 0.2);
                color: var(--text-primary, #e6edf3);
            }
            .scnet-chat-message.loading {
                color: var(--text-muted, #8b949e);
                font-style: italic;
            }
            .scnet-chat-input-area {
                display: flex;
                gap: 8px;
                padding: 12px 16px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(0, 0, 0, 0.2);
            }
            .scnet-chat-input {
                flex: 1;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: var(--text-primary, #e6edf3);
                font-size: 13px;
                outline: none;
                transition: border-color 0.3s;
            }
            .scnet-chat-input:focus {
                border-color: var(--neon-green, #00e676);
            }
            .scnet-chat-input::placeholder {
                color: var(--text-muted, #6e7681);
            }
            .scnet-chat-send {
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                border: none;
                border-radius: 8px;
                color: #000;
                width: 36px;
                height: 36px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .scnet-chat-send:hover:not(:disabled) {
                transform: scale(1.05);
                box-shadow: 0 0 15px rgba(0, 230, 118, 0.4);
            }
            .scnet-chat-send:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .scnet-chat-status {
                padding: 4px 16px;
                font-size: 11px;
                color: var(--text-muted, #8b949e);
                text-align: center;
                min-height: 18px;
            }
            .scnet-chat-toggle {
                position: fixed;
                bottom: 100px;
                right: 20px;
                width: 56px;
                height: 56px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                border: none;
                color: #000;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3);
                transition: transform 0.3s, box-shadow 0.3s;
                z-index: 9997;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .scnet-chat-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0, 230, 118, 0.5);
            }
            @media (max-width: 480px) {
                #scnet-chat-widget {
                    width: calc(100vw - 40px);
                    right: 10px;
                    bottom: 90px;
                }
            }
        `;
        document.head.appendChild(style);

        return widget;
    }

    /**
     * 创建悬浮按钮
     */
    function createToggleButton() {
        const btn = document.createElement('button');
        btn.className = 'scnet-chat-toggle';
        btn.innerHTML = '🤖';
        btn.title = 'SCNet AI 助手';
        return btn;
    }

    /**
     * 调用 SCNet API（通过本地代理避免 CORS）
     */
    async function callSCNetAPI(message) {
        const waitTime = checkRateLimit();
        if (waitTime > 0) {
            await new Promise(r => setTimeout(r, waitTime));
        }
        lastRequestTime = Date.now();

        // 方式 1: 使用本地代理（推荐）
        if (CONFIG.USE_PROXY) {
            try {
                const response = await fetch(CONFIG.PROXY_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                });

                if (!response.ok) {
                    throw new Error(`Proxy HTTP ${response.status}`);
                }

                const data = await response.json();
                if (data.status === 'ok') {
                    return data.response;
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            } catch (error) {
                console.warn('[SCNet Proxy] 代理调用失败:', error.message);
                return generateProxyErrorResponse();
            }
        }

        // 方式 2: 直接 fetch（会被 CORS 阻止）
        return generateFallbackResponse(message);
    }

    /**
     * 代理未启动时的错误提示
     */
    function generateProxyErrorResponse() {
        return `🤖 SCNet AI 助手

抱歉，无法连接到 AI 服务。

💡 请确保本地代理服务器已启动：

   cd scripts
   python scnet_proxy.py

或者访问官网直接使用：
   https://www.scnet.cn/ui/chatbot/`;
    }

    /**
     * 生成备用响应（当 API 不可用时）
     */
    function generateFallbackResponse(message) {
        const responses = [
            "抱歉，由于浏览器跨域安全限制 (CORS)，无法直接连接到 SCNet API。",
            "",
            "💡 解决方案：",
            "1. 使用后端代理：部署一个本地服务器转发请求",
            "2. 使用浏览器扩展：安装 CORS Unblock 扩展",
            "3. 直接使用：访问 https://www.scnet.cn/ui/chatbot/",
            "",
            `📨 您发送的消息："${message}"`
        ];
        return responses.join('\n');
    }

    /**
     * 初始化聊天组件
     */
    function init() {
        // 只在首页显示
        if (!document.body.classList.contains('page-home')) {
            return;
        }

        const toggleBtn = createToggleButton();
        const widget = createChatWidget();

        // 初始状态：隐藏聊天窗口
        widget.style.display = 'none';

        document.body.appendChild(toggleBtn);
        document.body.appendChild(widget);

        // DOM 引用
        const container = widget.querySelector('.scnet-chat-container');
        const messagesEl = widget.querySelector('.scnet-chat-messages');
        const inputEl = widget.querySelector('.scnet-chat-input');
        const sendBtn = widget.querySelector('.scnet-chat-send');
        const closeBtn = widget.querySelector('.scnet-chat-close');
        const statusEl = widget.querySelector('.scnet-chat-status');

        // 切换显示
        toggleBtn.addEventListener('click', () => {
            const isVisible = widget.style.display !== 'none';
            widget.style.display = isVisible ? 'none' : 'block';
            toggleBtn.style.display = isVisible ? 'flex' : 'none';
            if (!isVisible) {
                inputEl.focus();
            }
        });

        // 关闭按钮
        closeBtn.addEventListener('click', () => {
            widget.style.display = 'none';
            toggleBtn.style.display = 'flex';
        });

        // 添加消息
        function addMessage(text, sender) {
            const msgEl = document.createElement('div');
            msgEl.className = `scnet-chat-message ${sender}`;
            msgEl.textContent = text;
            messagesEl.appendChild(msgEl);
            messagesEl.scrollTop = messagesEl.scrollHeight;
            return msgEl;
        }

        // 更新状态
        function setStatus(text) {
            statusEl.textContent = text;
        }

        // 发送消息
        async function sendMessage() {
            const text = inputEl.value.trim();
            if (!text || isProcessing) return;

            // 添加用户消息
            addMessage(text, 'user');
            inputEl.value = '';

            isProcessing = true;
            sendBtn.disabled = true;
            setStatus('正在连接 SCNet AI...');

            // 添加加载消息
            const loadingMsg = addMessage('思考中...', 'ai loading');

            try {
                const response = await callSCNetAPI(text);
                
                // 移除加载消息，添加真实响应
                loadingMsg.remove();
                addMessage(response, 'ai');
                setStatus('已完成');

            } catch (error) {
                loadingMsg.remove();
                addMessage(`错误: ${error.message}`, 'ai');
                setStatus('请求失败');
            } finally {
                isProcessing = false;
                sendBtn.disabled = false;
                inputEl.focus();
            }
        }

        // 事件监听
        sendBtn.addEventListener('click', sendMessage);
        inputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // 欢迎消息
        setTimeout(() => {
            const welcomeMsg = CONFIG.USE_PROXY 
                ? '你好！我是 SCNet AI 助手。🚀 如需使用，请先启动本地代理：python scripts/scnet_proxy.py'
                : '你好！我是 SCNet AI 助手。';
            addMessage(welcomeMsg, 'ai');
        }, 500);
    }

    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
