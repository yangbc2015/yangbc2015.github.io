#!/bin/bash

# Giscus 配置辅助脚本
# 用法: ./scripts/setup-giscus.sh

echo "=========================================="
echo "   🤖 Giscus 评论系统配置助手"
echo "=========================================="
echo ""
echo "这个脚本将帮助你配置 Giscus 评论系统。"
echo ""

# 检查 hugo.toml 是否存在
if [ ! -f "hugo.toml" ]; then
    echo "❌ 错误: 未找到 hugo.toml 文件"
    echo "请确保在网站根目录运行此脚本"
    exit 1
fi

echo "📋 配置步骤:"
echo ""
echo "1. 创建 GitHub 仓库用于存储评论"
echo "   - 访问: https://github.com/new"
echo "   - 建议名称: ai-research-comments"
echo ""
echo "2. 启用 Discussions:"
echo "   - 进入仓库 Settings → General"
echo "   - 勾选 Discussions 功能"
echo ""
echo "3. 安装 Giscus 应用:"
echo "   - 访问: https://github.com/apps/giscus"
echo "   - 点击 Install，选择你的仓库"
echo ""
echo "4. 获取配置参数:"
echo "   - 访问: https://giscus.app"
echo "   - 输入你的仓库名"
echo "   - 复制生成的配置参数"
echo ""

read -p "按 Enter 键继续配置..."
echo ""

# 读取用户输入
read -p "请输入 GitHub 用户名: " username
read -p "请输入仓库名称 [ai-research-comments]: " repo
repo=${repo:-ai-research-comments}
read -p "请输入 Repo ID (从 giscus.app 获取): " repo_id
read -p "请输入 Category ID (从 giscus.app 获取): " category_id

echo ""
echo "📦 正在更新 hugo.toml..."

# 使用 sed 更新 hugo.toml
sed -i "s|repo = \"\"|repo = \"${username}/${repo}\"|" hugo.toml
sed -i "s|repoId = \"\"|repoId = \"${repo_id}\"|" hugo.toml
sed -i "s|categoryId = \"\"|categoryId = \"${category_id}\"|" hugo.toml

echo ""
echo "✅ 配置完成!"
echo ""
echo "📄 已更新 hugo.toml 中的 Giscus 配置:"
echo "   仓库: ${username}/${repo}"
echo "   Repo ID: ${repo_id}"
echo "   Category ID: ${category_id}"
echo ""
echo "🚀 现在可以构建和部署网站了:"
echo "   hugo --gc --minify"
echo ""
echo "📖 详细配置说明请参考: GISCUS_SETUP.md"
