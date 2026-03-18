#!/bin/bash
# 自动同步脚本 - 提交并推送本地修改到 GitHub

set -e  # 遇到错误立即退出

PROJECT_DIR="/Users/jiangzhuimacmini/Projects/jiangzhui-xhs-v1"
LOG_FILE="$PROJECT_DIR/logs/sync.log"
NOTIFY_SCRIPT="$PROJECT_DIR/scripts/notify.py"

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 记录日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== 开始自动同步 =========="

cd "$PROJECT_DIR"

# 检查是否有修改
if [[ -z $(git status -s) ]]; then
    log "✅ 没有需要提交的修改"
    exit 0
fi

log "📝 检测到以下修改："
git status -s | tee -a "$LOG_FILE"

# 添加所有修改（排除 .DS_Store）
git add scripts/ config/ templates/ README.md requirements.txt .gitignore docs/ 2>/dev/null || true

# 检查是否有暂存的修改
if [[ -z $(git diff --cached --name-only) ]]; then
    log "⚠️  没有可提交的文件（可能都被 .gitignore 忽略了）"
    exit 0
fi

# 统计修改文件数
FILES_CHANGED=$(git diff --cached --name-only | wc -l | tr -d ' ')

# 生成提交信息
COMMIT_MSG="chore: 自动同步 $(date '+%Y-%m-%d %H:%M')"

# 提交
log "💾 提交修改..."
if git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1; then
    COMMIT_HASH=$(git rev-parse HEAD)
    log "✅ 提交成功: $COMMIT_HASH"
else
    log "❌ 提交失败"
    python3 "$NOTIFY_SCRIPT" sync_failure "提交失败" 2>/dev/null || true
    exit 1
fi

# 推送到远程
log "📤 推送到 GitHub..."
if git push origin master >> "$LOG_FILE" 2>&1; then
    log "✅ 同步成功！"
    # 发送成功通知
    python3 "$NOTIFY_SCRIPT" sync_success "$COMMIT_HASH" "$FILES_CHANGED" 2>/dev/null || true
else
    log "❌ 推送失败，请检查网络或权限"
    # 发送失败通知
    python3 "$NOTIFY_SCRIPT" sync_failure "推送失败，请检查网络或权限" 2>/dev/null || true
    exit 1
fi

log "========== 同步完成 =========="
