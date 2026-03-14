#!/bin/bash
# 安装 v3 版本定时任务
# 用法: bash install-cron-v3.sh

set -e

echo "🔄 OpenClaw 记忆管理系统 v3 - 定时任务安装"
echo "============================================"

# 检查目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

echo ""
echo "📁 检查目录..."
echo "   脚本目录: $SCRIPT_DIR"
echo "   工作目录: $WORKSPACE"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi
echo "✅ Python3 已安装"

# 检查日志目录
LOG_DIR="$WORKSPACE/logs"
if [ ! -d "$LOG_DIR" ]; then
    echo "📁 创建日志目录: $LOG_DIR"
    mkdir -p "$LOG_DIR"
fi
echo "✅ 日志目录: $LOG_DIR"

# 备份现有 crontab
echo ""
echo "💾 备份现有 crontab..."
if crontab -l &> /dev/null; then
    crontab -l > "$WORKSPACE/.backup/crontab-backup-$(date +%Y%m%d-%H%M%S).txt" 2>/dev/null || true
    echo "✅ 已备份现有 crontab"
else
    echo "ℹ️ 无现有 crontab"
fi

# 安装新 crontab
echo ""
echo "📝 安装 v3 定时任务..."
crontab "$SCRIPT_DIR/crontab-v3.txt"
echo "✅ 定时任务已安装"

# 验证
echo ""
echo "🔍 验证安装..."
echo ""
echo "当前定时任务:"
echo "----------------------------------------"
crontab -l | grep -E "^#|^\d" | head -20
echo "----------------------------------------"

echo ""
echo "🎉 安装完成!"
echo ""
echo "任务列表:"
echo "  00:30 daily       - 每日归档 + Session提取"
echo "  02:00 maintenance - 清理维护"
echo "  03:00 backup      - 增量备份"
echo "  04:00 health      - 健康检查"
echo "  08:00 report      - 晨报发送"
echo "  周一01:00 index   - 索引生成"
echo ""
echo "日志位置: $LOG_DIR/cron-*.log"
echo ""
echo "手动测试命令:"
echo "  cd $SCRIPT_DIR"
echo "  python3 memory_manager.py daily"
echo "  python3 memory_manager.py health"
echo "  python3 memory_manager.py report"