/**
 * AI Chat - 内置助手
 * 点击星系中心开启 AI 对话
 */

(function() {
    'use strict';

    // 创建提示元素（HTML，确保在最顶层）
    function createHint() {
        const hint = document.createElement('div');
        hint.id = 'ai-chat-hint';
        hint.innerHTML = `
            <div class="ai-hint-glow"></div>
            <span class="ai-hint-text">开启 AI 对话</span>
            <div class="ai-hint-arrow">▼</div>
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            #ai-chat-hint {
                position: fixed;
                z-index: 9999;
                pointer-events: none;
                opacity: 0;
                transform: translate(-50%, -100%) scale(0.9);
                transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 4px;
            }
            
            #ai-chat-hint.visible {
                opacity: 1;
                transform: translate(-50%, -100%) scale(1);
            }
            
            .ai-hint-glow {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, 50%);
                width: 120px;
                height: 60px;
                background: radial-gradient(ellipse, rgba(0, 230, 118, 0.4) 0%, transparent 70%);
                pointer-events: none;
            }
            
            .ai-hint-text {
                background: linear-gradient(135deg, rgba(0, 230, 118, 0.95), rgba(0, 200, 100, 0.95));
                color: #000;
                padding: 8px 20px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
                white-space: nowrap;
                box-shadow: 
                    0 4px 20px rgba(0, 230, 118, 0.4),
                    0 0 0 1px rgba(0, 230, 118, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
                text-shadow: 0 1px 0 rgba(255, 255, 255, 0.3);
                letter-spacing: 0.5px;
            }
            
            .ai-hint-arrow {
                color: rgba(0, 230, 118, 0.9);
                font-size: 12px;
                animation: ai-hint-bounce 1.5s ease-in-out infinite;
                text-shadow: 0 0 10px rgba(0, 230, 118, 0.8);
            }
            
            @keyframes ai-hint-bounce {
                0%, 100% { transform: translateY(0); opacity: 0.8; }
                50% { transform: translateY(4px); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(hint);
        return hint;
    }

    // 创建聊天窗口
    function createChatWidget() {
        const widget = document.createElement('div');
        widget.id = 'ai-chat-widget';
        widget.innerHTML = `
            <div class="ai-chat-overlay"></div>
            <div class="ai-chat-container">
                <div class="ai-chat-header">
                    <div class="ai-chat-avatar">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5">
                            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                            <path d="M2 17l10 5 10-5"/>
                            <path d="M2 12l10 5 10-5"/>
                        </svg>
                    </div>
                    <div class="ai-chat-title-group">
                        <span class="ai-chat-title">AI 助手</span>
                        <span class="ai-chat-status">● 在线</span>
                    </div>
                    <button class="ai-chat-close" title="关闭">
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
                <div class="ai-chat-body">
                    <iframe 
                        src="https://www.scnet.cn/ui/chatbot/" 
                        class="ai-chat-iframe"
                        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                        loading="lazy"
                    ></iframe>
                </div>
            </div>
        `;

        const style = document.createElement('style');
        style.textContent = `
            #ai-chat-widget {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                visibility: hidden;
                transition: opacity 0.4s ease, visibility 0.4s ease;
            }
            
            #ai-chat-widget.active {
                opacity: 1;
                visibility: visible;
            }
            
            .ai-chat-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0);
                backdrop-filter: blur(0px);
                transition: all 0.4s ease;
            }
            
            #ai-chat-widget.active .ai-chat-overlay {
                background: rgba(0, 0, 0, 0.75);
                backdrop-filter: blur(8px);
            }
            
            .ai-chat-container {
                position: relative;
                width: 90vw;
                max-width: 480px;
                height: 75vh;
                max-height: 650px;
                background: rgba(13, 17, 23, 0.98);
                border: 1px solid rgba(0, 230, 118, 0.3);
                border-radius: 20px;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                transform: scale(0.9) translateY(30px);
                opacity: 0;
                transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
                box-shadow: 
                    0 25px 50px rgba(0, 0, 0, 0.6),
                    0 0 0 1px rgba(0, 230, 118, 0.2),
                    0 0 60px rgba(0, 230, 118, 0.15);
            }
            
            #ai-chat-widget.active .ai-chat-container {
                transform: scale(1) translateY(0);
                opacity: 1;
            }
            
            .ai-chat-header {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 20px;
                background: linear-gradient(135deg, rgba(0, 230, 118, 0.12), rgba(0, 200, 100, 0.06));
                border-bottom: 1px solid rgba(0, 230, 118, 0.2);
                flex-shrink: 0;
            }
            
            .ai-chat-avatar {
                width: 40px;
                height: 40px;
                border-radius: 10px;
                background: linear-gradient(135deg, #00e676, #00c853);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #000;
                box-shadow: 0 4px 15px rgba(0, 230, 118, 0.35);
            }
            
            .ai-chat-title-group {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 2px;
            }
            
            .ai-chat-title {
                font-size: 15px;
                font-weight: 600;
                color: #fff;
            }
            
            .ai-chat-status {
                font-size: 11px;
                color: #00e676;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .ai-chat-close {
                background: rgba(255, 255, 255, 0.05);
                border: none;
                color: rgba(255, 255, 255, 0.6);
                width: 36px;
                height: 36px;
                border-radius: 10px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
            }
            
            .ai-chat-close:hover {
                background: rgba(255, 64, 129, 0.15);
                color: #ff4081;
                transform: rotate(90deg);
            }
            
            .ai-chat-body {
                flex: 1;
                overflow: hidden;
                position: relative;
            }
            
            .ai-chat-iframe {
                width: 100%;
                height: 100%;
                border: none;
                background: #0d1117;
            }
            
            @media (max-width: 640px) {
                .ai-chat-container {
                    width: 95vw;
                    height: 85vh;
                    max-height: none;
                    border-radius: 16px;
                }
                
                .ai-chat-header {
                    padding: 12px 16px;
                }
            }
        `;
        document.head.appendChild(style);
        return widget;
    }

    function init() {
        if (!document.body.classList.contains('page-home')) return;

        const hint = createHint();
        const widget = createChatWidget();
        document.body.appendChild(widget);

        const overlay = widget.querySelector('.ai-chat-overlay');
        const closeBtn = widget.querySelector('.ai-chat-close');
        const trigger = document.getElementById('center-ai-trigger');

        // 提示位置更新
        function updateHintPosition() {
            if (!trigger) return;
            const rect = trigger.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const topY = rect.top;
            hint.style.left = centerX + 'px';
            hint.style.top = (topY - 10) + 'px';
        }

        function openChat() {
            widget.classList.add('active');
            document.body.style.overflow = 'hidden';
            hint.classList.remove('visible');
        }

        function closeChat() {
            widget.classList.remove('active');
            document.body.style.overflow = '';
        }

        if (trigger) {
            // 点击打开
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openChat();
            });

            // 鼠标悬停显示提示
            trigger.addEventListener('mouseenter', () => {
                updateHintPosition();
                trigger.style.filter = 'drop-shadow(0 0 40px rgba(0, 230, 118, 1)) brightness(1.2)';
                hint.classList.add('visible');
            });

            trigger.addEventListener('mouseleave', () => {
                trigger.style.filter = '';
                hint.classList.remove('visible');
            });

            // 初始位置
            updateHintPosition();
            window.addEventListener('resize', updateHintPosition);
            window.addEventListener('scroll', updateHintPosition);
        }

        closeBtn.addEventListener('click', closeChat);
        overlay.addEventListener('click', closeChat);

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
