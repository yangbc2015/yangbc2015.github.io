---
title: "Attention Is All You Need 解读"
date: 2026-03-15T09:00:00+08:00
draft: false
description: "Transformer 架构开山之作深度解读"
venue: "论文解读"
tags: ["Transformer", "Attention", "论文解读", "NLP"]
---

2017 年，Google 的研究团队发表了《Attention Is All You Need》，提出了 Transformer 架构，彻底改变了自然语言处理领域。

## 核心创新

### Self-Attention 机制
- 计算序列中每个位置与其他所有位置的关联
- 并行计算，训练效率大幅提升
- 捕捉长距离依赖关系

### Multi-Head Attention
- 多个注意力头并行工作
- 每个头学习不同的特征表示
- 增强模型的表达能力

### 位置编码
- 为序列添加位置信息
- 使用正弦和余弦函数
- 可以泛化到训练时未见过的长度
