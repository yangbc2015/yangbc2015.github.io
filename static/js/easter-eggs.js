/**
 * AI漫游 - 赛博朋克彩蛋系统
 * Cyberpunk Easter Eggs System
 * 
 * 激活方式：Konami 代码 ↑↑↓↓←→←→BA
 */

(function() {
    'use strict';

    let matrixActive = false;

    // ===== Konami 代码触发矩阵雨 =====
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    let codeIndex = 0;

    document.addEventListener('keydown', (e) => {
        if (e.key === konamiCode[codeIndex]) {
            codeIndex++;
            if (codeIndex === konamiCode.length) {
                activateMatrixRain();
                codeIndex = 0;
            }
        } else {
            // 如果按错了，检查是否是序列的第一个键
            codeIndex = e.key === konamiCode[0] ? 1 : 0;
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
            cursor: pointer;
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

        // 点击或按 ESC 停止
        function stopMatrix() {
            if (!matrixActive) return;
            matrixActive = false;
            canvas.style.opacity = '0';
            setTimeout(() => {
                canvas.remove();
            }, 500);
        }
        
        canvas.addEventListener('click', stopMatrix);
        
        // ESC 键也能停止
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                stopMatrix();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
            }, 500);
        });

        // 显示提示
        showEasterEggToast('🎮 矩阵模式已激活！点击屏幕停止');
    }

    // ===== 控制台赛博朋克 ASCII 艺术 =====
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
   ║  > 上上下下左右左右BA                                        ║
   ║                                                              ║
   ║  > GitHub: https://github.com/yangbc2015                     ║
   ╚══════════════════════════════════════════════════════════════╝
        `;

        console.log('%c' + ascii, styles);
        console.log('%c🔍 ↑↑↓↓←→←→BA', 'color: #00e5ff; font-size: 11px;');
    }

    // 页面加载后打印控制台彩蛋
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', printConsoleEasterEgg);
    } else {
        printConsoleEasterEgg();
    }

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

    // 彩蛋提示（延迟5秒显示，避免打扰）
    setTimeout(() => {
        console.log('%c💡 提示：试试经典的 Konami 代码 ↑↑↓↓←→←→BA', 'color: #ffd700; font-size: 11px;');
    }, 5000);

})();
