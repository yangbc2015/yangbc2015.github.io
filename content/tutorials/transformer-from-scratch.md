---
title: "从零实现 Transformer"
date: 2026-03-10T10:00:00+08:00
draft: false
description: "手撕 Transformer 源码，深入理解注意力机制"
level: "intermediate"
tags: ["Transformer", "PyTorch", "教程", "实战"]
---

本教程将带你从零开始实现完整的 Transformer 模型，深入理解其工作原理。

## 环境准备

```bash
pip install torch numpy matplotlib
```

## 项目结构

```
transformer/
├── attention.py      # 注意力机制实现
├── encoder.py        # 编码器
├── decoder.py        # 解码器
├── model.py          # 完整模型
└── train.py          # 训练脚本
```

## 第1步：Scaled Dot-Product Attention

```python
import torch
import torch.nn as nn
import math

class ScaledDotProductAttention(nn.Module):
    def __init__(self, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, query, key, value, mask=None):
        d_k = query.size(-1)
        scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attn = torch.softmax(scores, dim=-1)
        attn = self.dropout(attn)
        
        return torch.matmul(attn, value), attn
```
