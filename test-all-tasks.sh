#!/bin/bash
# 测试所有定时任务
# 用法: bash test-all-tasks.sh

echo "🧪 OpenClaw 记忆管理系统 v3 - 任务测试"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="/home/node/.openclaw/workspace/logs"

cd "$SCRIPT_DIR"

# 测试 daily
echo "1️⃣  测试 daily (每日归档)..."
python3 memory_manager.py daily 2>&1 | tail -5
echo ""

# 测试 health
echo "2️⃣  测试 health (健康检查)..."
python3 memory_manager.py health 2>&1 | tail -5
echo ""

# 测试 report (不发送)
echo "3️⃣  测试 report (生成报告)..."
python3 memory_manager.py report 2>&1 | tail -5
echo ""

# 测试 session-merge
echo "4️⃣  测试 session-merge (优化版)..."
python3 memory_manager.py session-merge --output log --log-type optimized 2>&1 | tail -5
echo ""

echo "✅ 测试完成!"
echo ""
echo "查看日志:"
echo "  ls -lh $LOG_DIR/"
echo ""
echo "如需安装定时任务，运行:"
echo "  bash install-cron-v3.sh"