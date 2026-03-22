#!/bin/bash
# AI 研究站 - 自动更新脚本
# 功能：爬取最新数据并构建 Hugo 网站

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
log "${YELLOW}📡 步骤 1/2: 运行数据爬虫...${NC}"
if python3 scripts/scraper/scraper.py >> "$LOG_FILE" 2>&1; then
    log "${GREEN}✅ 数据爬虫执行成功${NC}"
else
    log "${RED}❌ 数据爬虫执行失败${NC}"
    exit 1
fi

# 步骤 2: 构建 Hugo 网站
log "${YELLOW}🔨 步骤 2/2: 构建 Hugo 网站...${NC}"
if hugo --minify --gc >> "$LOG_FILE" 2>&1; then
    log "${GREEN}✅ Hugo 构建成功${NC}"
else
    log "${RED}❌ Hugo 构建失败${NC}"
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
