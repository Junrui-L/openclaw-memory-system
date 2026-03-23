#!/bin/bash
# 记录会话内容到记忆文件 - 智能提取版
# 用法: bash record-session.sh [会话描述]

set -e

WORKSPACE_DIR="/home/node/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE_DIR/memory"
SESSIONS_DIR="/home/node/.openclaw/agents/main/sessions"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
MEMORY_FILE="$MEMORY_DIR/$DATE.md"

log() { echo "[$(date '+%H:%M:%S')] $1"; }
warn() { echo "[$(date '+%H:%M:%S')] WARNING: $1"; }

DESCRIPTION="${1:-会话记录}"

[ -d "$MEMORY_DIR" ] || mkdir -p "$MEMORY_DIR"

if [ ! -d "$SESSIONS_DIR" ]; then
    warn "Sessions 目录不存在"
    fallback_record
    exit 0
fi

find_latest_session() {
    local latest="" latest_time=0
    for f in "$SESSIONS_DIR"/*.jsonl; do
        [ -f "$f" ] || continue
        [[ "$f" == *".reset."* ]] && continue
        [[ "$f" == *".deleted."* ]] && continue
        local mtime=$(stat -c %Y "$f" 2>/dev/null || echo 0)
        local today_start=$(date -d "$DATE 00:00:00" +%s 2>/dev/null || echo 0)
        local today_end=$(date -d "$DATE 23:59:59" +%s 2>/dev/null || echo 0)
        [ "$mtime" -ge "$today_start" ] && [ "$mtime" -le "$today_end" ] && [ "$mtime" -gt "$latest_time" ] && { latest_time=$mtime; latest=$f; }
    done
    echo "$latest"
}

extract_session_content() {
    local session_file="$1"
    python3 - "$session_file" << 'PYEOF'
import json, sys, re

session_file = sys.argv[1]

def sanitize(text):
    if not text: return ""
    text = text.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', '').replace('\\"', '"')
    # 先提取时间戳后的实际内容（在清理其他内容之前）
    match = re.search(r'\[\w{3}\s+[^\]]+\]\s*(.+)', text, re.DOTALL)
    if match:
        text = match.group(1)
    # 清理元数据标记
    text = re.sub(r'Sender \(untrusted metadata\):.*', '', text, flags=re.DOTALL)
    text = re.sub(r'Conversation info \(untrusted metadata\):.*', '', text, flags=re.DOTALL)
    text = re.sub(r'```json\s*\{.*?\}\s*```', '', text, flags=re.DOTALL)
    text = ' '.join(text.split())
    return text.strip()

def classify(text):
    if not text: return ""
    markers = []
    if any(k in text for k in ['?', '？', '吗', '什么', '怎么', '为什么']): markers.append("[问]")
    if any(text.startswith(k) for k in ['帮我', '请', '需要', '查看', '检查', '修复', '重写']): markers.append("[指令]")
    if any(text.startswith(k) for k in ['好', '可以', '行', '不对', '错了']): markers.append("[反馈]")
    if any(k in text for k in ['✅', '完成', '成功', '搞定']): markers.append("[完成]")
    return ' '.join(markers)

def should_skip(text, role=""):
    if not text: return True
    if role not in ["user", "assistant"]: return True
    if text == '...': return True  # 跳过被截断的tool结果
    for p in [r'^A new session', r'^Execute your']:
        if re.search(p, text, re.I): return True
    return False

def extract_key_points(text):
    if not text: return ""
    lines = text.split('\\n')
    points = [l.strip() for l in lines if re.match(r'^\\s*[-*]\\s', l)][:3]
    for l in lines:
        if any(k in l for k in ['✅', '成功', '完成', '找到', '修复']) and l not in points:
            points.append(l.strip())
            break
    if points: return '\\n'.join(points[:4])
    return text[:300] + "..." if len(text) > 300 else text

messages = []
try:
    with open(session_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                d = json.loads(line)
                if d.get('type') != 'message': continue
                msg = d.get('message', {})
                role = msg.get('role', '')
                content = msg.get('content', [])
                text = ' '.join([item.get('text', '') for item in content if isinstance(item, dict)])
                text = sanitize(text)
                if should_skip(text, role): continue
                messages.append({'role': role, 'text': text})
            except: continue
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

if not messages:
    print("")
    sys.exit(0)

output = []
for msg in messages:
    if msg['role'] == 'user':
        marker = classify(msg['text'])
        display = msg['text'][:600] + "..." if len(msg['text']) > 600 else msg['text']
        output.append(f"\n**用户**: {marker} {display}" if marker else f"\n**用户**: {display}")
    elif msg['role'] == 'assistant':
        key = extract_key_points(msg['text'])
        if key: output.append(f"**助手**: {key}")

print('\n'.join(output))
PYEOF
}

generate_summary() {
    local content="$1"
    local user_count=$(echo "$content" | grep -c "^\*\*用户\*\*:" || echo 0)
    local topic=$(echo "$content" | grep "^\*\*用户\*\*:" | head -1 | sed 's/^\*\*用户\*\*:\s*\[[^]]*\]\s*//' | cut -c1-50)
    echo "共 $user_count 轮对话。主题: $topic..."
}

fallback_record() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo -e "# $DATE\n\n## 今日概要\n- 日期: $DATE\n- 记录时间: $TIME\n" > "$MEMORY_FILE"
    fi
    echo -e "\n---\n\n### $TIME - $DESCRIPTION\n\n**时间**: $TIME  \n**类型**: 自动记录\n" >> "$MEMORY_FILE"
    log "已记录 (简单模式): $DESCRIPTION"
}

main() {
    log "开始记录会话..."
    local latest_session=$(find_latest_session)
    if [ -z "$latest_session" ]; then
        warn "未找到今天的活跃 session"
        fallback_record
        exit 0
    fi
    log "找到 session: $(basename "$latest_session")"
    
    local session_content=$(extract_session_content "$latest_session")
    if [ -z "$session_content" ]; then
        warn "未能提取到内容"
        fallback_record
        exit 0
    fi
    
    local summary=$(generate_summary "$session_content")
    
    if [ ! -f "$MEMORY_FILE" ]; then
        echo -e "# $DATE\n\n## 今日概要\n- 日期: $DATE\n- 记录时间: $TIME\n" > "$MEMORY_FILE"
    fi
    
    echo -e "\n---\n\n### $TIME - $DESCRIPTION\n\n**时间**: $TIME  \n**类型**: 会话记录  \n**摘要**: $summary\n\n**对话内容**:$session_content\n" >> "$MEMORY_FILE"
    
    log "已记录: $DESCRIPTION"
    log "摘要: $summary"
}

main
