/**
 * SCNet AI Chatbot - 嵌入知识星系中心
 * 点击星系中心的 AI 图标开启聊天窗口
 */

(function() {
    'use strict';

    function createChatWidget() {
        const widget = document.createElement('div');
        widget.id = 'scnet-chat-widget';
        widget.innerHTML = `
            <div class="scnet-chat-overlay"></div>
            <div class="scnet-chat-container">
                <div class="scnet-chat-header">
                    <div class="scnet-chat-avatar">🤖</div>
                    <div class="scnet-chat-title-group">
                        <span class="scnet-chat-title">SCNet AI 助手</span>
                        <span class="scnet-chat-subtitle">国家超算互联网平台</span>
                    </div>
                    <button class="scnet-chat-close" title="关闭">
                        <svg viewBox="0 0 24 24" width="20" height="20">
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
            /* ===== SCNet AI Chat - 模态窗口 ===== */
            #scnet-chat-widget {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: none;
                align-items: center;
                justify-content: center;
            }

            #scnet-chat-widget.active {
                display: flex;
            }

            /* 遮罩层 */
            .scnet-chat-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(8px);
                animation: scnet-overlay-fade 0.3s ease;
            }

            @keyframes scnet-overlay-fade {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            /* 聊天窗口 */
            .scnet-chat-container {
                position: relative;
                width: 90vw;
                max-width: 500px;
                height: 80vh;
                max-height: 700px;
                background: rgba(13, 17, 23, 0.98);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 230, 118, 0.3);
                border-radius: 24px;
                box-shadow: 
                    0 25px 50px -12px rgba(0, 0, 0, 0.9),
                    0 0 0 1px rgba(0, 230, 118, 0.15),
                    0 0 80px rgba(0, 230, 118, 0.15);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                animation: scnet-chat-open 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            }

            @keyframes scnet-chat-open {
                from {
                    opacity: 0;
                    transform: scale(0.9) translateY(30px);
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
                gap: 14px;
                padding: 18px 24px;
                background: linear-gradient(135deg, rgba(0, 230, 118, 0.12), rgba(0, 229, 255, 0.06));
                border-bottom: 1px solid rgba(0, 230, 118, 0.2);
                flex-shrink: 0;
            }

            .scnet-chat-avatar {
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--neon-green, #00e676), var(--neon-blue, #00e5ff));
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                box-shadow: 0 4px 20px rgba(0, 230, 118, 0.4);
                flex-shrink: 0;
            }

            .scnet-chat-title-group {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 3px;
            }

            .scnet-chat-title {
                font-size: 16px;
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
                width: 40px;
                height: 40px;
                border-radius: 12px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
            }

            .scnet-chat-close:hover {
                background: rgba(255, 64, 129, 0.15);
                color: var(--neon-pink, #ff4081);
                transform: rotate(90deg);
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

            /* Mobile Responsive */
            @media (max-width: 640px) {
                .scnet-chat-container {
                    width: 95vw;
                    height: 85vh;
                    border-radius: 20px;
                }
                
                .scnet-chat-header {
                    padding: 14px 18px;
                }
                
                .scnet-chat-avatar {
                    width: 40px;
                    height: 40px;
                    font-size: 20px;
                }
                
                .scnet-chat-title {
                    font-size: 15px;
                }
            }
        `;
        document.head.appendChild(style);
        return widget;
    }

    function init() {
        // 只在首页显示
        if (!document.body.classList.contains('page-home')) return;

        const widget = createChatWidget();
        document.body.appendChild(widget);

        const overlay = widget.querySelector('.scnet-chat-overlay');
        const container = widget.querySelector('.scnet-chat-container');
        const closeBtn = widget.querySelector('.scnet-chat-close');

        function openChat() {
            widget.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        function closeChat() {
            widget.classList.remove('active');
            document.body.style.overflow = '';
        }

        // 绑定到中心 AI 图标
        const trigger = document.getElementById('center-ai-trigger');
        if (trigger) {
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                openChat();
            });
            
            // 添加悬停效果
            trigger.addEventListener('mouseenter', () => {
                trigger.style.filter = 'drop-shadow(0 0 20px rgba(0, 230, 118, 0.8))';
            });
            trigger.addEventListener('mouseleave', () => {
                trigger.style.filter = '';
            });
        }

        closeBtn.addEventListener('click', closeChat);
        overlay.addEventListener('click', closeChat);

        // ESC 关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && widget.classList.contains('active')) {
                closeChat();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
