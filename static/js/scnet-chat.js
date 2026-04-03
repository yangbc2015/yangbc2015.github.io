/**
 * SCNet AI Chatbot - 简单嵌入方案
 * 直接嵌入 SCNet 官方的 Chatbot 页面，无需代理、无需配置
 */

(function() {
    'use strict';

    function createChatWidget() {
        const widget = document.createElement('div');
        widget.id = 'scnet-chat-widget';
        widget.innerHTML = `
            <div class="scnet-chat-container">
                <div class="scnet-chat-header">
                    <div class="scnet-chat-avatar">🤖</div>
                    <div class="scnet-chat-title-group">
                        <span class="scnet-chat-title">SCNet AI</span>
                        <span class="scnet-chat-subtitle">国家超算互联网平台</span>
                    </div>
                    <button class="scnet-chat-close" title="关闭">
                        <svg viewBox="0 0 24 24" width="18" height="18">
                            <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>
                    </button>
                </div>
                <div class="scnet-chat-body">
                    <iframe 
                        src="https://www.scnet.cn/ui/chatbot/" 
                        class="scnet-chat-iframe"
                        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                        loading="lazy"
                    ></iframe>
                </div>
            </div>
        `;

        const style = document.createElement('style');
        style.textContent = `
            /* ===== SCNet AI Chat - 左下角悬浮 ===== */
            #scnet-chat-widget {
                position: fixed;
                bottom: 2rem;
                left: 2rem;
                z-index: 1000;
                font-family: var(--font-primary, -apple-system, BlinkMacSystemFont, sans-serif);
            }

            .scnet-chat-container {
                width: 400px;
                height: 600px;
                max-width: calc(100vw - 2rem);
                max-height: calc(100vh - 120px);
                background: rgba(13, 17, 23, 0.98);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 230, 118, 0.25);
                border-radius: 20px;
                box-shadow: 
                    0 25px 50px -12px rgba(0, 0, 0, 0.8),
                    0 0 0 1px rgba(0, 230, 118, 0.1),
                    0 0 60px rgba(0, 230, 118, 0.1);
                overflow: hidden;
                display: none;
                flex-direction: column;
                animation: scnet-chat-open 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            }

            @keyframes scnet-chat-open {
                from {
                    opacity: 0;
                    transform: scale(0.9) translateY(20px);
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
                background: linear-gradient(135deg, rgba(0, 230, 118, 0.15), rgba(0, 229, 255, 0.08));
                border-bottom: 1px solid rgba(0, 230, 118, 0.2);
                flex-shrink: 0;
            }

            .scnet-chat-avatar {
                width: 42px;
                height: 42px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 22px;
                box-shadow: 0 4px 15px rgba(0, 230, 118, 0.35);
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
                color: var(--text-muted, #8b949e);
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

            /* Body - iframe */
            .scnet-chat-body {
                flex: 1;
                overflow: hidden;
                position: relative;
            }

            .scnet-chat-iframe {
                width: 100%;
                height: 100%;
                border: none;
                background: #0d1117;
            }

            /* Toggle Button */
            .scnet-chat-toggle {
                position: fixed;
                bottom: 2rem;
                left: 2rem;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                border: none;
                color: #000;
                font-size: 26px;
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
                transform: scale(1.1) rotate(5deg);
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
                    left: 0.5rem;
                    bottom: 5rem;
                }
                
                .scnet-chat-container {
                    width: calc(100vw - 1rem);
                    height: 70vh;
                    max-height: 600px;
                    border-radius: 16px;
                }
                
                .scnet-chat-toggle {
                    bottom: 5.5rem;
                    left: 0.5rem;
                    width: 52px;
                    height: 52px;
                    font-size: 22px;
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

    function init() {
        // 只在首页显示
        if (!document.body.classList.contains('page-home')) return;

        const toggleBtn = createToggleButton();
        const widget = createChatWidget();

        document.body.appendChild(toggleBtn);
        document.body.appendChild(widget);

        const container = widget.querySelector('.scnet-chat-container');
        const closeBtn = widget.querySelector('.scnet-chat-close');

        function toggleChat(show) {
            if (show) {
                container.style.display = 'flex';
                toggleBtn.style.display = 'none';
            } else {
                container.style.display = 'none';
                toggleBtn.style.display = 'flex';
            }
        }

        toggleBtn.addEventListener('click', () => toggleChat(true));
        closeBtn.addEventListener('click', () => toggleChat(false));

        // 默认展开（延迟一点让用户看到动画）
        setTimeout(() => toggleChat(true), 500);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
