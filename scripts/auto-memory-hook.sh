#!/bin/bash
# Auto Memory Hook - 会话结束时自动记录到记忆文件
# 由 OpenClaw Hook 触发

set -e

# 配置
WORKSPACE_DIR="/home/node/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE_DIR/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
MEMORY_FILE="$MEMORY_DIR/$DATE.md"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"
}

# 检查环境
if [ ! -d "$MEMORY_DIR" ]; then
    mkdir -p "$MEMORY_DIR"
    log "创建记忆目录: $MEMORY_DIR"
fi

# 获取当前会话信息（从环境变量或参数）
SESSION_KEY="${SESSION_KEY:-unknown}"
CHANNEL="${CHANNEL:-unknown}"

# 创建记忆条目
log "自动记录会话到记忆文件..."

# 如果文件不存在，创建头部
if [ ! -f "$MEMORY_FILE" ]; then
    cat > "$MEMORY_FILE" << EOF
# $DATE - 自动记录

## 今日概要
- 日期: $DATE
- 自动记录时间: $TIME

EOF
    log "创建新的记忆文件: $MEMORY_FILE"
fi

# 追加会话记录
cat >> "$MEMORY_FILE" << EOF

---

### $TIME - 会话记录

**会话信息**:
- 时间: $TIME
- 渠道: $CHANNEL
- 会话: $SESSION_KEY

**自动记录**: 🤖 会话结束自动归档

EOF

log "✅ 已记录会话到: $MEMORY_FILE"

# 更新索引
INDEX_FILE="$MEMORY_DIR/INDEX.md"
if [ -f "$INDEX_FILE" ]; then
    # 更新索引中的今日条目（简化处理）
    log "索引已存在，跳过更新"
fi

log "✅ 自动记忆完成"
