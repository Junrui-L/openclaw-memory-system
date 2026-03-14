#!/bin/bash
# 生成晨报并发送到飞书群组

CHAT_ID="oc_f55bc4b692dd99d18ba8b46d73e902cb"
REPORT_FILE="/home/node/.openclaw/workspace/reports/daily/$(date +%Y-%m-%d)-morning.md"

cd /home/node/.openclaw/workspace

# 生成报告
bash scripts/openclaw-memory-system/run.sh report

# 发送飞书
if [ -f "$REPORT_FILE" ]; then
    python3 << PYEOF
import sys
sys.path.insert(0, '/app')
from tools import message
message.send(channel='feishu', target='chat:$CHAT_ID', text=open('$REPORT_FILE').read()[:2000])
PYEOF
    echo "✅ 晨报已发送到群组"
fi
