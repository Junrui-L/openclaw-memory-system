#!/bin/bash
# 检查定时任务状态
# 用法: bash check-cron-status.sh

echo "🔍 OpenClaw 记忆管理系统 v3 - 定时任务状态"
echo "==========================================="
echo ""

# 检查 crontab
echo "📋 当前定时任务:"
echo "----------------------------------------"
if crontab -l &> /dev/null; then
    crontab -l | grep -v "^#" | grep -v "^$" | head -10
else
    echo "❌ 无定时任务"
fi
echo "----------------------------------------"
echo ""

# 检查日志文件
echo "📁 最近日志文件:"
LOG_DIR="/home/node/.openclaw/workspace/logs"
if [ -d "$LOG_DIR" ]; then
    ls -lht "$LOG_DIR"/cron-*.log 2>/dev/null | head -10 || echo "无日志文件"
else
    echo "日志目录不存在"
fi
echo ""

# 检查运行状态
echo "⏰ 最近运行状态:"
for log in "$LOG_DIR"/cron-*.log; do
    if [ -f "$log" ]; then
        name=$(basename "$log" .log)
        last_line=$(tail -1 "$log" 2>/dev/null)
        size=$(du -h "$log" 2>/dev/null | cut -f1)
        echo "  $name: $size - $last_line"
    fi
done
echo ""

# 检查内存管理器
echo "🔧 记忆管理器状态:"
SCRIPT_DIR="/home/node/.openclaw/workspace/scripts/openclaw-memory-system"
if [ -f "$SCRIPT_DIR/memory_manager.py" ]; then
    echo "  ✅ memory_manager.py 存在"
    cd "$SCRIPT_DIR"
    python3 -c "print('  ✅ Python 语法正确')" 2>/dev/null || echo "  ❌ Python 语法错误"
else
    echo "  ❌ memory_manager.py 不存在"
fi
echo ""

echo "📊 总结:"
echo "  - 定时任务: $(crontab -l 2>/dev/null | grep -c "memory_manager" || echo 0) 个"
echo "  - 日志文件: $(ls -1 "$LOG_DIR"/cron-*.log 2>/dev/null | wc -l) 个"
echo ""