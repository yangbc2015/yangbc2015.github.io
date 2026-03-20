---
title: "使用 D3.js 构建知识图谱"
date: 2024-03-10T09:00:00+08:00
draft: false
description: "如何使用 D3.js 创建交互式知识图谱可视化"
category: "技术"
tags: ["D3.js", "数据可视化", "JavaScript", "知识图谱"]
icon: "🕸️"
---

## 为什么需要知识图谱？

在信息爆炸的时代，知识不再是线性的。概念之间相互关联，形成一个复杂的网络。知识图谱帮助我们：

- 🔍 **发现关联** - 看到想法之间的联系
- 🧠 **理解结构** - 理解知识的组织方式
- 💡 **激发创意** - 意外的连接带来新想法

## D3.js 简介

D3.js（Data-Driven Documents）是一个强大的 JavaScript 库，用于创建数据可视化。它允许你将数据绑定到 DOM，然后应用数据驱动的转换。

```javascript
// 基本的 D3 力导向图
const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));
```

## 数据准备

知识图谱需要两种数据：

### 节点（Nodes）

```javascript
const nodes = [
    { id: 1, label: '人工智能', category: '技术', icon: '🤖' },
    { id: 2, label: '机器学习', category: '技术', icon: '📊' },
    { id: 3, label: '神经网络', category: '算法', icon: '🧠' },
    // ...
];
```

### 连接（Links）

```javascript
const links = [
    { source: 1, target: 2 },  // AI -> ML
    { source: 2, target: 3 },  // ML -> Neural Networks
    // ...
];
```

## 创建力导向图

### 1. 设置 SVG 容器

```javascript
const svg = d3.select('#graph')
    .append('svg')
    .attr('width', width)
    .attr('height', height);
```

### 2. 创建连接线

```javascript
const link = svg.append('g')
    .selectAll('line')
    .data(links)
    .enter()
    .append('line')
    .attr('stroke', '#00ff41')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', 1.5);
```

### 3. 创建节点

```javascript
const node = svg.append('g')
    .selectAll('.node')
    .data(nodes)
    .enter()
    .append('g')
    .attr('class', 'node')
    .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

// 添加圆形
node.append('circle')
    .attr('r', 20)
    .attr('fill', '#0d1117')
    .attr('stroke', '#00ff41')
    .attr('stroke-width', 2);

// 添加图标
node.append('text')
    .attr('dy', '0.35em')
    .attr('text-anchor', 'middle')
    .text(d => d.icon);
```

### 4. 更新位置

```javascript
simulation.on('tick', () => {
    link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

    node.attr('transform', d => `translate(${d.x},${d.y})`);
});
```

## 添加交互

### 悬停效果

```javascript
node.on('mouseenter', function(event, d) {
    d3.select(this).select('circle')
        .transition()
        .duration(200)
        .attr('r', 28);
    
    // 高亮相关连接
    link.classed('active', l => 
        l.source.id === d.id || l.target.id === d.id
    );
});
```

### 缩放和平移

```javascript
const zoom = d3.zoom()
    .scaleExtent([0.5, 3])
    .on('zoom', (event) => {
        svg.selectAll('g').attr('transform', event.transform);
    });

svg.call(zoom);
```

## 高级功能

### 粒子效果

让连接线动起来：

```javascript
function createParticle(link) {
    const particle = svg.append('circle')
        .attr('r', 3)
        .attr('fill', '#00ff41')
        .attr('cx', link.source.x)
        .attr('cy', link.source.y);
    
    particle.transition()
        .duration(2000)
        .ease(d3.easeLinear)
        .attr('cx', link.target.x)
        .attr('cy', link.target.y)
        .on('end', function() {
            d3.select(this).remove();
        });
}

// 定期创建粒子
setInterval(() => {
    const randomLink = links[Math.floor(Math.random() * links.length)];
    createParticle(randomLink);
}, 500);
```

### 分类着色

```javascript
const colorScale = d3.scaleOrdinal()
    .domain(['技术', '设计', '生活'])
    .range(['#00ff41', '#00f0ff', '#ff00ff']);

node.select('circle')
    .attr('stroke', d => colorScale(d.category));
```

## 性能优化

对于大型图谱，考虑以下优化：

1. **使用 Canvas** - 代替 SVG 处理大量节点
2. **quadtree** - 优化碰撞检测
3. **Web Worker** - 在后台计算力导向布局

```javascript
// 使用 quadtree 优化
const quadtree = d3.quadtree()
    .x(d => d.x)
    .y(d => d.y)
    .addAll(nodes);
```

## 总结

D3.js 为我们提供了构建知识图谱的强大工具。通过力导向图，我们可以：

- 📊 可视化复杂的知识关系
- 🎨 创建美观的交互式图表
- 🔧 高度自定义样式和行为

开始构建你自己的知识图谱吧！
