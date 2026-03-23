#!/bin/bash
# 发送飞书消息辅助脚本
# 用于在 cron 环境中可靠地发送飞书消息

set -e

TARGET="$1"
MESSAGE="$2"

if [ -z "$TARGET" ] || [ -z "$MESSAGE" ]; then
    echo "Usage: $0 <target> <message>"
    echo "Example: $0 user:ou_xxx 'Hello World'"
    exit 1
fi

# 确保 PATH 包含 openclaw
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# 使用 openclaw 发送消息
openclaw message send \
    --channel feishu \
    --target "$TARGET" \
    --message "$MESSAGE"
