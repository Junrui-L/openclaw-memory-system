#!/bin/bash
# 修复 Cron 定时任务路径
# 在 fnOS 宿主机上执行

echo "=== 修复 Cron 定时任务路径 ==="
echo ""

# 备份当前 crontab
echo "1. 备份当前 crontab..."
sudo crontab -l > /tmp/crontab.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ 备份完成"
echo ""

# 更新 crontab 配置
echo "2. 更新路径..."
sudo crontab -l | sed 's|scripts/memory|scripts/openclaw-memory-system|g' > /tmp/crontab.new

# 显示变更
echo "3. 变更内容预览:"
echo "---"
diff -u <(sudo crontab -l) /tmp/crontab.new || true
echo "---"
echo ""

# 应用新配置
echo "4. 应用新配置..."
sudo crontab /tmp/crontab.new
echo "✅ 配置已更新"
echo ""

# 验证
echo "5. 验证新配置:"
sudo crontab -l | grep -E "(memory|openclaw-memory)" | head -10
echo ""

echo "=== 修复完成 ==="
echo ""
echo "注意:"
echo "- 旧备份在 /tmp/crontab.backup.*"
echo "- 如有问题可恢复: sudo crontab /tmp/crontab.backup.XXX"
