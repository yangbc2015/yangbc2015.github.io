#!/bin/bash
# AI漫游 - 自动更新脚本
# 功能：爬取最新数据、构建 Hugo 网站，并推送到 GitHub 触发部署

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="/root/hugo/mentors"
LOG_DIR="/root/hugo/mentors/logs"
LOG_FILE="$LOG_DIR/auto-update-$(date +%Y%m%d).log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "${YELLOW}🚀 开始自动更新流程...${NC}"

# 进入项目目录
cd "$PROJECT_DIR"

# 步骤 1: 运行爬虫
log "${YELLOW}📡 步骤 1/3: 运行数据爬虫...${NC}"
if python3 scripts/scraper/scraper.py >> "$LOG_FILE" 2>&1; then
    log "${GREEN}✅ 数据爬虫执行成功${NC}"
else
    log "${RED}❌ 数据爬虫执行失败${NC}"
    exit 1
fi

# 检查是否有数据变更
if [ -z "$(git status --porcelain data/ content/)" ]; then
    log "${YELLOW}ℹ️ 没有数据变更，跳过构建和推送${NC}"
    exit 0
fi

# 步骤 2: 构建 Hugo 网站
log "${YELLOW}🔨 步骤 2/3: 构建 Hugo 网站...${NC}"
if hugo --minify --gc >> "$LOG_FILE" 2>&1; then
    log "${GREEN}✅ Hugo 构建成功${NC}"
else
    log "${RED}❌ Hugo 构建失败${NC}"
    exit 1
fi

# 步骤 3: 提交并推送到 GitHub（触发 Actions 部署）
log "${YELLOW}📤 步骤 3/3: 推送到 GitHub 触发部署...${NC}"
git add data/ content/
git commit -m "🤖 Auto-update AI data: $(date +'%Y-%m-%d %H:%M')

📊 更新内容:
- AI 新闻
- AI 榜单 (LMSYS Arena)
- AI 论文 (arXiv)
- AI 视频

🤖 通过服务器自动更新脚本生成" || true

# 先拉取远程更改，避免推送冲突
log "${YELLOW}🔄 同步远程更改...${NC}"
if git pull origin main --no-rebase --no-edit >> "$LOG_FILE" 2>&1; then
    log "${GREEN}✅ 同步成功${NC}"
else
    # 如果有冲突，使用本地版本解决
    log "${YELLOW}⚠️ 检测到冲突，使用本地版本解决...${NC}"
    git checkout --ours data/*.json >> "$LOG_FILE" 2>&1 || true
    git add data/*.json >> "$LOG_FILE" 2>&1 || true
    git commit -m "Resolve merge conflicts, keep local data" >> "$LOG_FILE" 2>&1 || true
fi

if git push origin main >> "$LOG_FILE" 2>&1; then
    log "${GREEN}✅ 推送成功，GitHub Actions 将自动部署${NC}"
else
    log "${RED}❌ 推送失败，请检查 Git 配置${NC}"
    exit 1
fi

# 统计更新内容
PAPERS_COUNT=$(grep -c '"title"' data/papers.json 2>/dev/null || echo "0")
VIDEOS_COUNT=$(grep -c '"title"' data/videos.json 2>/dev/null || echo "0")
NEWS_COUNT=$(grep -c '"title"' data/news.json 2>/dev/null || echo "0")

log "${GREEN}🎉 更新完成！当前数据：${NC}"
log "   📄 论文: $PAPERS_COUNT 篇"
log "   🎬 视频: $VIDEOS_COUNT 个"
log "   📰 新闻: $NEWS_COUNT 条"
log "   📁 日志: $LOG_FILE"

exit 0
