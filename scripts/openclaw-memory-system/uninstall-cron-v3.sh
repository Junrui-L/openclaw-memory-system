#!/bin/bash
# 卸载 v3 版本定时任务
# 用法: bash uninstall-cron-v3.sh

echo "🗑️  OpenClaw 记忆管理系统 v3 - 定时任务卸载"
echo "============================================="
echo ""

# 备份现有 crontab
echo "💾 备份现有 crontab..."
WORKSPACE="/home/node/.openclaw/workspace"
mkdir -p "$WORKSPACE/.backup"

if crontab -l &> /dev/null; then
    BACKUP_FILE="$WORKSPACE/.backup/crontab-backup-$(date +%Y%m%d-%H%M%S).txt"
    crontab -l > "$BACKUP_FILE"
    echo "✅ 已备份到: $BACKUP_FILE"
else
    echo "ℹ️ 无现有 crontab"
fi

# 清空 crontab
echo ""
echo "🗑️  清空定时任务..."
crontab -r 2>/dev/null || true
echo "✅ 定时任务已清空"

echo ""
echo "🎉 卸载完成!"
echo ""
echo "如需重新安装，运行:"
echo "  bash install-cron-v3.sh"