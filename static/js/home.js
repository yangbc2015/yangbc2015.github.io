// AI WANDER - Homepage JavaScript
(function() {
    'use strict';

    // ===== Particle Background =====
    (function initParticles() {
        const canvas = document.getElementById('particle-canvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        let particles = [];
        let animationId;
        let isVisible = true;
        
        function resize() {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
        }
        
        function createParticles() {
            particles = [];
            const count = Math.min(60, Math.floor(canvas.width * canvas.height / 20000));
            
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: (Math.random() - 0.5) * 0.4,
                    vy: (Math.random() - 0.5) * 0.4,
                    radius: Math.random() * 1.5 + 0.5,
                    opacity: Math.random() * 0.4 + 0.15
                });
            }
        }
        
        function drawParticles() {
            if (!isVisible) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw connections
            particles.forEach((p1, i) => {
                particles.slice(i + 1).forEach(p2 => {
                    const dx = p1.x - p2.x;
                    const dy = p1.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    
                    if (dist < 130) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(136, 153, 255, ${0.12 * (1 - dist / 130)})`;
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(p1.x, p1.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                });
            });
            
            // Draw particles
            particles.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(136, 153, 255, ${p.opacity})`;
                ctx.fill();
                
                p.x += p.vx;
                p.y += p.vy;
                
                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
            });
            
            animationId = requestAnimationFrame(drawParticles);
        }
        
        resize();
        createParticles();
        drawParticles();
        
        window.addEventListener('resize', () => {
            resize();
            createParticles();
        });
        
        document.addEventListener('visibilitychange', () => {
            isVisible = !document.hidden;
            if (isVisible) {
                drawParticles();
            } else {
                cancelAnimationFrame(animationId);
            }
        });
    })();

    // ===== Galaxy Navigation System =====
    function initGalaxy() {
        const svg = document.getElementById('galaxy-svg');
        const planetsGroup = document.getElementById('planets');
        const connectionsGroup = document.getElementById('connections');
        const particlesGroup = document.getElementById('particles');
        
        if (!svg || !planetsGroup || !connectionsGroup || !particlesGroup) {
            console.warn('Galaxy elements not found:', { svg, planetsGroup, connectionsGroup, particlesGroup });
            return false;
        }
        
        console.log('Galaxy initialized successfully');

        const planets = [
            { id: 1, name: 'AI新闻', icon: '📰', desc: '行业动态', link: '/news/', color: 'url(#planetGradient1)', angle: 0, orbit: 3 },
            { id: 2, name: '机器人', icon: '🤖', desc: '具身智能', link: '/robotics/', color: 'url(#planetGradient2)', angle: 45, orbit: 2 },
            { id: 3, name: 'AI榜单', icon: '🏆', desc: '模型评测', link: '/leaderboard/', color: 'url(#planetGradient3)', angle: 90, orbit: 3 },
            { id: 4, name: '投资', icon: '💰', desc: 'AI投资', link: '/investment/', color: 'url(#planetGradient4)', angle: 135, orbit: 1 },
            { id: 5, name: '学术', icon: '🔬', desc: '前沿论文', link: '/papers/', color: 'url(#planetGradient5)', angle: 180, orbit: 2 },
            { id: 6, name: '技术基建', icon: '🏗️', desc: '系统架构', link: '/tutorials/', color: 'url(#planetGradient6)', angle: 225, orbit: 3 },
            { id: 7, name: '工具', icon: '🛠️', desc: '资源导航', link: '/tools/', color: 'url(#planetGradient7)', angle: 270, orbit: 1 },
            { id: 8, name: '视频', icon: '🎬', desc: '精选课程', link: '/videos/', color: 'url(#planetGradient8)', angle: 315, orbit: 2 }
        ];
        
        const centerX = 600;
        const centerY = 350;
        const orbits = [150, 250, 350];
        
        let currentRotation = 0;
        let isDragging = false;
        let lastMouseX = 0;
        let scale = 1;
        let planetElements = [];
        let hoveredPlanet = null;
        
        function createPlanet(planet, index) {
            const orbitRadius = orbits[planet.orbit - 1];
            const rad = (planet.angle + currentRotation) * Math.PI / 180;
            const x = centerX + orbitRadius * Math.cos(rad);
            const y = centerY + orbitRadius * Math.sin(rad) * 0.6;
            
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('class', 'planet');
            g.setAttribute('transform', `translate(${x}, ${y})`);
            g.style.cursor = 'pointer';
            // Start visible immediately - animation handled by CSS or simple fade
            g.style.opacity = '1';
            
            const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
            title.textContent = `${planet.name} - ${planet.desc}`;
            g.appendChild(title);
            
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('class', 'planet-circle');
            circle.setAttribute('r', 32);
            circle.setAttribute('stroke', planet.color);
            
            const icon = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            icon.setAttribute('class', 'planet-icon');
            icon.setAttribute('dy', '2');
            icon.textContent = planet.icon;
            
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('class', 'planet-label');
            label.setAttribute('dy', '50');
            label.textContent = planet.name;
            
            const desc = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            desc.setAttribute('class', 'planet-desc');
            desc.setAttribute('dy', '63');
            desc.textContent = planet.desc;
            
            g.appendChild(circle);
            g.appendChild(icon);
            g.appendChild(label);
            g.appendChild(desc);
            
            g.addEventListener('click', () => {
                window.location.href = planet.link;
            });
            
            g.addEventListener('mouseenter', () => {
                hoveredPlanet = { x, y, color: planet.color };
                createGlowEffect(x, y, planet.color);
            });
            
            g.addEventListener('mouseleave', () => {
                hoveredPlanet = null;
            });
            
            return { element: g, data: planet, x, y };
        }
        
        function createGlowEffect(x, y, color) {
            const glow = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            glow.setAttribute('cx', x);
            glow.setAttribute('cy', y);
            glow.setAttribute('r', 32);
            glow.setAttribute('fill', 'none');
            glow.setAttribute('stroke', color);
            glow.setAttribute('stroke-width', '2');
            glow.setAttribute('opacity', '0.7');
            
            particlesGroup.appendChild(glow);
            
            let radius = 32;
            let opacity = 0.7;
            
            function animate() {
                radius += 2.5;
                opacity -= 0.025;
                
                if (opacity > 0) {
                    glow.setAttribute('r', radius);
                    glow.setAttribute('opacity', opacity);
                    requestAnimationFrame(animate);
                } else {
                    glow.remove();
                }
            }
            
            animate();
        }
        
        function createConnections(planetElements) {
            connectionsGroup.innerHTML = '';
            
            for (let i = 0; i < planetElements.length; i++) {
                for (let j = i + 1; j < planetElements.length; j++) {
                    const p1 = planetElements[i];
                    const p2 = planetElements[j];
                    
                    if (Math.abs(p1.data.orbit - p2.data.orbit) <= 1) {
                        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('class', 'connection-line');
                        line.setAttribute('x1', p1.x);
                        line.setAttribute('y1', p1.y);
                        line.setAttribute('x2', p2.x);
                        line.setAttribute('y2', p2.y);
                        connectionsGroup.appendChild(line);
                    }
                }
            }
        }
        
        // Create mouse gravity line
        let mouseX = centerX;
        let mouseY = centerY;
        const gravityLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        gravityLine.setAttribute('class', 'connection-line');
        gravityLine.setAttribute('stroke-opacity', '0.15');
        gravityLine.style.pointerEvents = 'none';
        connectionsGroup.appendChild(gravityLine);
        
        svg.addEventListener('mousemove', (e) => {
            const rect = svg.getBoundingClientRect();
            mouseX = (e.clientX - rect.left) * (1200 / rect.width);
            mouseY = (e.clientY - rect.top) * (700 / rect.height);
            
            let nearest = null;
            let minDist = Infinity;
            
            planetElements.forEach(p => {
                const dx = p.x - mouseX;
                const dy = p.y - mouseY;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < minDist && dist < 150) {
                    minDist = dist;
                    nearest = p;
                }
            });
            
            if (nearest) {
                gravityLine.setAttribute('x1', nearest.x);
                gravityLine.setAttribute('y1', nearest.y);
                gravityLine.setAttribute('x2', mouseX);
                gravityLine.setAttribute('y2', mouseY);
                gravityLine.setAttribute('stroke', nearest.data.color);
                gravityLine.setAttribute('stroke-opacity', String(0.4 * (1 - minDist / 150)));
            } else {
                gravityLine.setAttribute('stroke-opacity', '0');
            }
        });
        
        svg.addEventListener('mouseleave', () => {
            gravityLine.setAttribute('stroke-opacity', '0');
        });
        
        function createFlowParticles(planetElements) {
            if (document.hidden || planetElements.length < 2) return;
            
            const validPairs = [];
            for (let i = 0; i < planetElements.length; i++) {
                for (let j = i + 1; j < planetElements.length; j++) {
                    if (Math.abs(planetElements[i].data.orbit - planetElements[j].data.orbit) <= 1) {
                        validPairs.push([planetElements[i], planetElements[j]]);
                    }
                }
            }
            
            if (validPairs.length === 0) return;
            
            const [p1, p2] = validPairs[Math.floor(Math.random() * validPairs.length)];
            
            const particle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            particle.setAttribute('class', 'flow-particle');
            particle.setAttribute('r', 2.5);
            particlesGroup.appendChild(particle);
            
            let progress = 0;
            const speed = 0.012;
            
            function animate() {
                progress += speed;
                
                if (progress < 1) {
                    const x = p1.x + (p2.x - p1.x) * progress;
                    const y = p1.y + (p2.y - p1.y) * progress;
                    particle.setAttribute('cx', x);
                    particle.setAttribute('cy', y);
                    requestAnimationFrame(animate);
                } else {
                    particle.remove();
                }
            }
            
            animate();
        }
        
        function render() {
            planetsGroup.innerHTML = '';
            planetElements = [];
            
            planets.forEach((planet, index) => {
                const pe = createPlanet(planet, index);
                planetsGroup.appendChild(pe.element);
                planetElements.push(pe);
            });
            
            createConnections(planetElements);
        }
        
        function autoRotate() {
            if (!isDragging) {
                currentRotation += 0.04;
                render();
            }
            requestAnimationFrame(autoRotate);
        }
        
        svg.addEventListener('mousedown', (e) => {
            isDragging = true;
            lastMouseX = e.clientX;
            svg.style.cursor = 'grabbing';
        });
        
        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const delta = e.clientX - lastMouseX;
                currentRotation += delta * 0.25;
                lastMouseX = e.clientX;
                render();
            }
        });
        
        document.addEventListener('mouseup', () => {
            isDragging = false;
            svg.style.cursor = 'grab';
        });
        
        svg.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? 0.92 : 1.08;
            scale = Math.max(0.5, Math.min(1.8, scale * delta));
            svg.style.transform = `scale(${scale})`;
        }, { passive: false });
        
        svg.style.cursor = 'grab';
        svg.style.transition = 'transform 0.3s ease';
        
        render();
        autoRotate();
        setInterval(() => createFlowParticles(planetElements), 600);
    }

    // ===== Visitor Counter (Busuanzi) =====
    (function initVisitorCounter() {
        let countDisplayed = false;
        let retryCount = 0;
        const MAX_RETRIES = 30;
        
        function updateDisplay(count) {
            if (countDisplayed) return;
            countDisplayed = true;
            const visitorCount = document.getElementById('visitor-count');
            if (visitorCount) visitorCount.textContent = count.toLocaleString();
        }
        
        function getBusuanziValue() {
            const pvElement = document.getElementById('busuanzi_value_site_pv');
            if (!pvElement) return null;
            const text = pvElement.textContent.trim();
            if (text && text !== '--' && text !== '') {
                const count = parseInt(text.replace(/,/g, ''));
                if (!isNaN(count) && count > 0) return count;
            }
            return null;
        }
        
        function pollBusuanzi() {
            if (countDisplayed) return;
            const count = getBusuanziValue();
            if (count !== null) { updateDisplay(count); return; }
            retryCount++;
            if (retryCount < MAX_RETRIES) {
                setTimeout(pollBusuanzi, 1000);
            } else {
                const visitorCount = document.getElementById('visitor-count');
                if (visitorCount) visitorCount.textContent = '∞';
            }
        }
        
        function watchBusuanzi() {
            const count = getBusuanziValue();
            if (count !== null) { updateDisplay(count); return; }
            
            const bodyObserver = new MutationObserver(() => {
                const count = getBusuanziValue();
                if (count !== null) {
                    updateDisplay(count);
                    bodyObserver.disconnect();
                }
            });
            
            bodyObserver.observe(document.body, { childList: true, subtree: true });
            pollBusuanzi();
            setTimeout(() => bodyObserver.disconnect(), 10000);
        }
        
        if (document.readyState === 'complete') {
            watchBusuanzi();
        } else {
            window.addEventListener('load', watchBusuanzi);
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                const count = getBusuanziValue();
                if (count !== null && !countDisplayed) updateDisplay(count);
            }, 2000);
        });
    })();

    // ===== Visitor Heatmap =====
    const SIMULATED_CITIES = [
        { name: '北京', lat: 39.9042, lng: 116.4074, weight: 0.9 },
        { name: '上海', lat: 31.2304, lng: 121.4737, weight: 0.85 },
        { name: '深圳', lat: 22.5431, lng: 114.0579, weight: 0.8 },
        { name: '杭州', lat: 30.2741, lng: 120.1551, weight: 0.7 },
        { name: '广州', lat: 23.1291, lng: 113.2644, weight: 0.65 },
        { name: '成都', lat: 30.5728, lng: 104.0668, weight: 0.5 },
        { name: '旧金山', lat: 37.7749, lng: -122.4194, weight: 0.95 },
        { name: '纽约', lat: 40.7128, lng: -74.0060, weight: 0.9 },
        { name: '西雅图', lat: 47.6062, lng: -122.3321, weight: 0.75 },
        { name: '洛杉矶', lat: 34.0522, lng: -118.2437, weight: 0.6 },
        { name: '波士顿', lat: 42.3601, lng: -71.0589, weight: 0.55 },
        { name: '伦敦', lat: 51.5074, lng: -0.1278, weight: 0.8 },
        { name: '柏林', lat: 52.5200, lng: 13.4050, weight: 0.6 },
        { name: '巴黎', lat: 48.8566, lng: 2.3522, weight: 0.55 },
        { name: '阿姆斯特丹', lat: 52.3676, lng: 4.9041, weight: 0.5 },
        { name: '东京', lat: 35.6762, lng: 139.6503, weight: 0.85 },
        { name: '新加坡', lat: 1.3521, lng: 103.8198, weight: 0.75 },
        { name: '首尔', lat: 37.5665, lng: 126.9780, weight: 0.7 },
        { name: '班加罗尔', lat: 12.9716, lng: 77.5946, weight: 0.65 },
        { name: '特拉维夫', lat: 32.0853, lng: 34.7818, weight: 0.5 },
        { name: '悉尼', lat: -33.8688, lng: 151.2093, weight: 0.45 },
        { name: '多伦多', lat: 43.6532, lng: -79.3832, weight: 0.5 },
        { name: '温哥华', lat: 49.2827, lng: -123.1207, weight: 0.4 },
    ];

    function generateMockHeatmapData() {
        const points = [];
        const today = Math.floor(Math.random() * 500) + 200;
        const week = today * 7 + Math.floor(Math.random() * 1000);
        
        SIMULATED_CITIES.forEach(city => {
            const numPoints = Math.floor(city.weight * 20) + 5;
            for (let i = 0; i < numPoints; i++) {
                const lat = city.lat + (Math.random() - 0.5) * 5;
                const lng = city.lng + (Math.random() - 0.5) * 8;
                const intensity = city.weight * (0.5 + Math.random() * 0.5);
                points.push([lat, lng, intensity]);
            }
        });
        
        for (let i = 0; i < 50; i++) {
            const lat = (Math.random() - 0.5) * 140;
            const lng = (Math.random() - 0.5) * 360;
            points.push([lat, lng, Math.random() * 0.3]);
        }
        
        return { points, stats: { today, week }, uniqueLocations: SIMULATED_CITIES.length + Math.floor(Math.random() * 30) };
    }

    async function loadHeatmap() {
        const container = document.getElementById('visitor-heatmap');
        if (!container) return;

        try {
            if (!document.querySelector('#leaflet-css')) {
                const link = document.createElement('link');
                link.id = 'leaflet-css';
                link.rel = 'stylesheet';
                link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
                document.head.appendChild(link);
            }

            await loadScript('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js');
            await loadScript('https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js');

            const data = generateMockHeatmapData();
            container.innerHTML = '';

            const map = L.map(container, {
                center: [20, 0],
                zoom: 1.5,
                minZoom: 1,
                maxZoom: 6,
                zoomControl: false,
                attributionControl: false,
                scrollWheelZoom: false,
            });

            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                subdomains: 'abcd',
                maxZoom: 19,
                opacity: 0.3,
            }).addTo(map);

            if (data.points && data.points.length > 0) {
                L.heatLayer(data.points, {
                    radius: 25,
                    blur: 15,
                    maxZoom: 10,
                    max: 1.0,
                    gradient: {
                        0.0: '#667eea',
                        0.3: '#764ba2',
                        0.5: '#f093fb',
                        0.7: '#f5576c',
                        1.0: '#e94560'
                    }
                }).addTo(map);

                SIMULATED_CITIES.forEach(city => {
                    if (city.weight > 0.5) {
                        L.circleMarker([city.lat, city.lng], {
                            radius: 4,
                            fillColor: '#e94560',
                            color: 'transparent',
                            fillOpacity: 0.8,
                            className: 'pulse-marker'
                        }).addTo(map);
                    }
                });
            }

            const style = document.createElement('style');
            style.textContent = `
                .pulse-marker {
                    animation: pulse-ring 2s ease-out infinite;
                }
                @keyframes pulse-ring {
                    0% { transform: scale(1); opacity: 1; }
                    100% { transform: scale(3); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        } catch (error) {
            console.error('Load heatmap error:', error);
            container.innerHTML = '<div class="heatmap-loading">热力图加载失败</div>';
        }
    }

    function loadScript(src) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${src}"]`)) { resolve(); return; }
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // ===== Background Music =====
    (function initMusic() {
        const musicToggle = document.getElementById('music-toggle');
        const bgMusic = document.getElementById('bg-music');
        const musicIcon = document.getElementById('music-icon');
        const musicIconPaused = document.getElementById('music-icon-paused');
        const visualizer = document.getElementById('music-visualizer');
        
        if (!musicToggle || !bgMusic) return;
        
        let isPlaying = false;
        
        bgMusic.volume = 0.4;
        bgMusic.muted = false;
        
        function updateUI(playing) {
            isPlaying = playing;
            if (playing) {
                // 显示播放图标（带音量动画），隐藏暂停图标
                musicIcon.style.display = 'flex';
                musicIcon.classList.add('active');
                musicIconPaused.style.display = 'none';
                // 按钮样式 - 绿色主题
                musicToggle.style.background = 'rgba(0, 230, 118, 0.15)';
                musicToggle.style.borderColor = 'var(--neon-green)';
                musicToggle.style.color = 'var(--neon-green)';
                musicToggle.style.boxShadow = '0 0 20px rgba(0, 230, 118, 0.3)';
            } else {
                // 显示暂停图标，隐藏播放图标
                musicIcon.style.display = 'none';
                musicIcon.classList.remove('active');
                musicIconPaused.style.display = 'flex';
                // 按钮样式 - 蓝色主题
                musicToggle.style.background = 'rgba(0, 229, 255, 0.08)';
                musicToggle.style.borderColor = 'rgba(0, 229, 255, 0.3)';
                musicToggle.style.color = 'var(--neon-blue)';
                musicToggle.style.boxShadow = 'none';
            }
        }
        
        musicToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            if (isPlaying) {
                bgMusic.pause();
                updateUI(false);
            } else {
                bgMusic.volume = 0.4;
                bgMusic.muted = false;
                bgMusic.play().then(() => updateUI(true)).catch(() => {
                    // Ignore autoplay errors
                });
            }
        });
        
        bgMusic.addEventListener('play', () => updateUI(true));
        bgMusic.addEventListener('pause', () => updateUI(false));
        bgMusic.addEventListener('ended', () => updateUI(false));
        
        // 初始状态：显示暂停图标
        updateUI(false);
    })();

    // Initialize galaxy and delay heatmap load
    document.addEventListener('DOMContentLoaded', () => {
        initGalaxy();
        setTimeout(loadHeatmap, 1200);
    });
})();
