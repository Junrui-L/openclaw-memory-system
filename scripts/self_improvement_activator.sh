#!/bin/bash
# Self-Improvement 自动激活脚本
# 在每次会话后执行，检测并记录学习

set -e

WORKSPACE="/home/node/.openclaw/workspace"
SCRIPT_DIR="$WORKSPACE/scripts"

# 检查是否需要记录
python3 "$SCRIPT_DIR/auto_self_improvement.py" --check "$@" 2>/dev/null || true

echo "✅ Self-improvement check completed"
