#!/bin/bash
# AI漫游 - 自动更新脚本
# 功能：爬取最新数据、构建 Hugo 网站，并推送到 GitHub 触发部署
# 更新频率：每日一次（已禁用每小时更新）

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
LOCK_FILE="/tmp/ai-update.lock"
LAST_RUN_FILE="/tmp/ai-update.last"

# 频率限制：最短运行间隔（秒）- 20小时 = 72000秒
MIN_INTERVAL=72000

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查是否已经在运行
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        log "${RED}❌ 另一个更新进程正在运行 (PID: $PID)，退出${NC}"
        exit 1
    else
        rm -f "$LOCK_FILE"
    fi
fi

# 检查运行频率
if [ -f "$LAST_RUN_FILE" ]; then
    LAST_RUN=$(cat "$LAST_RUN_FILE")
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - LAST_RUN))
    
    if [ $TIME_DIFF -lt $MIN_INTERVAL ]; then
        HOURS_AGO=$((TIME_DIFF / 3600))
        MINUTES_AGO=$(((TIME_DIFF % 3600) / 60))
        log "${YELLOW}⏱️ 距离上次更新仅 ${HOURS_AGO}小时${MINUTES_AGO}分钟，跳过本次更新${NC}"
        log "${YELLOW}   （每日只更新一次，如需立即更新请手动运行）${NC}"
        exit 0
    fi
fi

# 创建锁文件
echo $$ > "$LOCK_FILE"

# 记录本次运行时间
date +%s > "$LAST_RUN_FILE"

# 确保退出时删除锁文件
trap 'rm -f "$LOCK_FILE"' EXIT

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

# 先提交本地更改
git add data/ content/
git commit -m "🤖 Auto-update AI data: $(date +'%Y-%m-%d %H:%M')

📊 更新内容:
- AI 新闻
- AI 榜单 (LMSYS Arena)
- AI 论文 (arXiv)
- AI 视频
- 机器人/具身智能
- AI 投资资讯

🤖 通过服务器自动更新脚本生成" || true

# 获取远程最新状态
log "${YELLOW}🔄 同步远程更改...${NC}"
git fetch origin main >> "$LOG_FILE" 2>&1

# 尝试使用 rebase 合并远程更改
if git rebase origin/main >> "$LOG_FILE" 2>&1; then
    log "${GREEN}✅ 同步成功${NC}"
else
    # rebase 失败，取消并改用 merge
    log "${YELLOW}⚠️ 同步冲突，尝试合并...${NC}"
    git rebase --abort >> "$LOG_FILE" 2>&1 || true
    # 使用 merge，优先保留我们的更改
    if git merge origin/main --strategy-option=ours --no-edit >> "$LOG_FILE" 2>&1; then
        log "${GREEN}✅ 合并成功${NC}"
    else
        log "${RED}❌ 合并失败，请手动解决冲突${NC}"
        exit 1
    fi
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
ROBOTICS_COUNT=$(grep -c '"title"' data/robotics.json 2>/dev/null || echo "0")
INVESTMENT_COUNT=$(grep -c '"title"' data/investment.json 2>/dev/null || echo "0")

log "${GREEN}🎉 更新完成！当前数据：${NC}"
log "   📄 论文: $PAPERS_COUNT 篇"
log "   🎬 视频: $VIDEOS_COUNT 个"
log "   📰 新闻: $NEWS_COUNT 条"
log "   🤖 机器人: $ROBOTICS_COUNT 条"
log "   💰 投资: $INVESTMENT_COUNT 条"
log "   📁 日志: $LOG_FILE"

exit 0
