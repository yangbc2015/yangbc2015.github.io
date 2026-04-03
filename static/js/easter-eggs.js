/**
 * AI漫游 - 赛博朋克彩蛋系统
 * Cyberpunk Easter Eggs System
 */

(function() {
    'use strict';

    // ===== 彩蛋 1: Konami 代码触发矩阵雨 =====
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    let konamiIndex = 0;
    let matrixActive = false;

    document.addEventListener('keydown', (e) => {
        if (e.key === konamiCode[konamiIndex]) {
            konamiIndex++;
            if (konamiIndex === konamiCode.length) {
                activateMatrixRain();
                konamiIndex = 0;
            }
        } else {
            konamiIndex = 0;
        }
    });

    function activateMatrixRain() {
        if (matrixActive) return;
        matrixActive = true;

        // 创建矩阵雨画布
        const canvas = document.createElement('canvas');
        canvas.id = 'matrix-rain';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 9999;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.5s ease;
        `;
        document.body.appendChild(canvas);

        // 触发重绘
        setTimeout(() => canvas.style.opacity = '0.8', 10);

        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        const fontSize = 14;
        const columns = canvas.width / fontSize;
        const drops = Array(Math.floor(columns)).fill(1);

        let frameCount = 0;
        const maxFrames = 600; // 约10秒

        function draw() {
            if (!matrixActive) return;
            
            frameCount++;
            if (frameCount > maxFrames) {
                canvas.style.opacity = '0';
                setTimeout(() => {
                    canvas.remove();
                    matrixActive = false;
                }, 500);
                return;
            }

            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#00e676';
            ctx.font = fontSize + 'px monospace';

            for (let i = 0; i < drops.length; i++) {
                const text = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);

                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }

            requestAnimationFrame(draw);
        }

        draw();

        // 点击停止
        canvas.addEventListener('click', () => {
            canvas.style.opacity = '0';
            setTimeout(() => {
                canvas.remove();
                matrixActive = false;
            }, 500);
        });

        // 显示提示
        showEasterEggToast('🎮 矩阵模式已激活！点击屏幕停止');
    }

    // ===== 彩蛋 2: 双击 Logo 触发粒子爆炸 =====
    let logoClickCount = 0;
    let logoClickTimer = null;

    document.addEventListener('DOMContentLoaded', () => {
        const logo = document.querySelector('.site-logo');
        if (logo) {
            logo.addEventListener('click', (e) => {
                logoClickCount++;
                
                if (logoClickCount === 1) {
                    logoClickTimer = setTimeout(() => {
                        logoClickCount = 0;
                    }, 500);
                } else if (logoClickCount >= 3) {
                    clearTimeout(logoClickTimer);
                    logoClickCount = 0;
                    createParticleExplosion(e.clientX, e.clientY);
                    showEasterEggToast('✨ 发现了隐藏彩蛋！');
                }
            });
        }
    });

    function createParticleExplosion(x, y) {
        const colors = ['#00e676', '#00e5ff', '#ff4081', '#ffd700', '#fff'];
        const particleCount = 30;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            const color = colors[Math.floor(Math.random() * colors.length)];
            const size = Math.random() * 8 + 4;
            const angle = (Math.PI * 2 * i) / particleCount;
            const velocity = Math.random() * 100 + 50;

            particle.style.cssText = `
                position: fixed;
                left: ${x}px;
                top: ${y}px;
                width: ${size}px;
                height: ${size}px;
                background: ${color};
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
                box-shadow: 0 0 10px ${color};
            `;

            document.body.appendChild(particle);

            const duration = Math.random() * 800 + 600;
            
            particle.animate([
                { transform: 'translate(0, 0) scale(1)', opacity: 1 },
                { 
                    transform: `translate(${Math.cos(angle) * velocity}px, ${Math.sin(angle) * velocity}px) scale(0)`,
                    opacity: 0 
                }
            ], {
                duration: duration,
                easing: 'cubic-bezier(0, .9, .57, 1)'
            }).onfinish = () => particle.remove();
        }
    }

    // ===== 彩蛋 3: 控制台赛博朋克 ASCII 艺术 =====
    function printConsoleEasterEgg() {
        const styles = [
            'color: #00e676',
            'font-size: 12px',
            'font-family: monospace',
            'padding: 10px',
            'border: 1px solid #00e676',
            'border-radius: 4px'
        ].join(';');

        const ascii = `
    █████╗ ██╗     ██╗    ██╗   ██╗██╗  ████████╗███████╗██████╗ 
   ██╔══██╗██║     ██║    ██║   ██║██║  ╚══██╔══╝██╔════╝██╔══██╗
   ███████║██║     ██║    ██║   ██║██║     ██║   █████╗  ██████╔╝
   ██╔══██║██║     ██║    ██║   ██║██║     ██║   ██╔══╝  ██╔══██╗
   ██║  ██║███████╗██║    ╚██████╔╝███████╗██║   ██║     ██║  ██║
   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═════╝ ╚══════╝╚═╝   ╚═╝     ╚═╝  ╚═╝
        
   ╔══════════════════════════════════════════════════════════════╗
   ║  WELCOME TO AI WANDER - CYBERPUNK AI RESOURCE NAVIGATOR      ║
   ║                                                              ║
   ║  > 发现隐藏彩蛋：                                            ║
   ║    • 输入 Konami 代码 (↑↑↓↓←→←→BA) 激活矩阵模式             ║
   ║    • 快速点击 Logo 3 次触发粒子爆炸                         ║
   ║    • 在搜索框输入 "matrix" 有惊喜                           ║
   ║                                                              ║
   ║  > GitHub: https://github.com/yangbc2015                     ║
   ╚══════════════════════════════════════════════════════════════╝
        `;

        console.log('%c' + ascii, styles);
        console.log('%c🔍 寻找更多彩蛋...', 'color: #00e5ff; font-size: 11px;');
    }

    // 页面加载后打印控制台彩蛋
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', printConsoleEasterEgg);
    } else {
        printConsoleEasterEgg();
    }

    // ===== 彩蛋 4: 搜索框输入 "matrix" 触发特效 =====
    document.addEventListener('DOMContentLoaded', () => {
        const searchInput = document.querySelector('.search-input, input[type="search"]');
        if (searchInput) {
            let typingTimer;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(typingTimer);
                const value = e.target.value.toLowerCase();
                
                if (value === 'matrix' || value === '黑客帝国') {
                    typingTimer = setTimeout(() => {
                        activateMatrixRain();
                        e.target.value = '';
                    }, 500);
                }
            });
        }
    });

    // ===== 辅助函数：显示彩蛋提示 =====
    function showEasterEggToast(message) {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 230, 118, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid var(--neon-green);
            border-radius: 50px;
            padding: 1rem 2rem;
            color: var(--neon-green);
            font-size: 1rem;
            font-weight: 500;
            z-index: 10000;
            animation: slideDown 0.5s ease;
            pointer-events: none;
            box-shadow: 0 0 30px rgba(0, 230, 118, 0.3);
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideUp 0.5s ease forwards';
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }

    // 添加动画样式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideDown {
            from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
            to { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
        @keyframes slideUp {
            from { opacity: 1; transform: translateX(-50%) translateY(0); }
            to { opacity: 0; transform: translateX(-50%) translateY(-20px); }
        }
    `;
    document.head.appendChild(style);

    // 彩蛋激活提示（延迟5秒显示，避免打扰）
    setTimeout(() => {
        console.log('%c💡 提示：尝试输入 Konami 代码 (↑↑↓↓←→←→BA) 或快速点击 Logo 3 次！', 'color: #ffd700; font-size: 11px;');
    }, 5000);

})();
