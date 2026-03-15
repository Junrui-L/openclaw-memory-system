#!/usr/bin/env python3
"""
Session 提取器 - 优化精简版 v3.3

去除冗余信息，保留关键内容
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class SessionExtractorOptimized:
    """优化版 Session 提取器 - 去除冗余"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.sessions_dir = Path("/home/node/.openclaw/agents/main/sessions")
        # session-daily 文件放在 memory/ 目录下，可被 memory_search 搜索
        self.memory_dir = Path(config.get('paths', {}).get('memory', '/home/node/.openclaw/workspace/memory'))
    
    def sanitize_text(self, text: str) -> str:
        """清理文本，去除冗余"""
        if not text:
            return ""
        
        # 替换转义字符
        text = text.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '').replace('\\"', '"')
        
        # 去除系统元数据
        text = re.sub(r'Sender \(untrusted metadata\):.*?\n', '', text, flags=re.DOTALL)
        text = re.sub(r'Conversation info \(untrusted metadata\):.*?\n', '', text, flags=re.DOTALL)
        text = re.sub(r'```json\s*\{.*?\}\s*```', '', text, flags=re.DOTALL)
        
        # 去除 OpenClaw 内部上下文
        text = re.sub(r'OpenClaw runtime context.*?\n', '', text, flags=re.DOTALL)
        text = re.sub(r'This context is runtime-generated.*?\n', '', text, flags=re.DOTALL)
        text = re.sub(r'Internal task completion event.*?\n', '', text, flags=re.DOTALL)
        
        # 去除重复空行
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        
        return text.strip()
    
    def is_redundant(self, text: str) -> bool:
        """判断是否为冗余消息"""
        if not text:
            return True
        
        # 系统消息
        patterns = [
            r'^A new session',
            r'^Execute your',
            r'^\[Inter-session message\]',
            r'^NO_REPLY$',
            r'^\s*\.\.\.\s*$',
        ]
        
        for p in patterns:
            if re.search(p, text, re.I):
                return True
        
        return False
    
    def extract_key_messages(self, messages: List[Dict]) -> List[Dict]:
        """提取关键消息，去除冗余"""
        key_messages = []
        last_content = ""
        
        for msg in messages:
            if msg['role'] not in ['user', 'assistant']:
                continue
            
            content = self.sanitize_text(msg.get('content', ''))
            
            # 过滤冗余
            if self.is_redundant(content):
                continue
            
            # 跳过重复
            if content == last_content:
                continue
            
            # 截断过长内容
            if len(content) > 600:
                content = content[:600] + "..."
            
            key_messages.append({
                'role': msg['role'],
                'content': content,
                'timestamp': msg.get('timestamp', '')
            })
            last_content = content
        
        return key_messages
    
    def format_session(self, session: Dict) -> str:
        """格式化 session - 按指定格式输出"""
        lines = []
        lines.append(f"## Session: {session['session_id']}")
        lines.append("")

        # 提取关键消息
        messages = self.extract_key_messages(session['messages'])

        if not messages:
            lines.append("*无有效对话内容*")
            return '\n'.join(lines)

        # 按指定格式组织内容
        lines.append("### 💬 详细对话记录")
        lines.append("")

        for msg in messages[:20]:  # 增加到20条
            if msg['role'] == 'user':
                lines.append(f"**👤 用户**: {msg['content'][:200]}")  # 增加长度限制
            else:
                lines.append(f"**🤖 助手**: {msg['content'][:250]}")
            lines.append("")

        if len(messages) > 20:
            lines.append(f"*... 还有 {len(messages) - 20} 条消息 ...*")
            lines.append("")

        # 添加对话主题摘要
        lines.append("### 📝 对话主题摘要")
        lines.append("")
        user_msgs = [m['content'][:50] for m in messages if m['role'] == 'user'][:3]
        if user_msgs:
            lines.append(f"主要话题: {' | '.join(user_msgs)}")
        lines.append("")

        return '\n'.join(lines)
    
    def read_session_file(self, file_path: Path, target_date: str) -> Optional[Dict]:
        """读取 session 文件"""
        messages = []
        session_id = file_path.stem
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    try:
                        record = json.loads(line)
                        timestamp = record.get('timestamp', '')
                        if target_date not in timestamp:
                            continue
                        
                        if record.get('type') == 'message':
                            msg_data = record.get('message', {})
                            role = msg_data.get('role', '')
                            content_parts = msg_data.get('content', [])
                            
                            content = ''
                            if isinstance(content_parts, list):
                                for part in content_parts:
                                    if isinstance(part, dict) and 'text' in part:
                                        content += part['text'] + ' '
                            else:
                                content = str(content_parts)
                            
                            if role in ['user', 'assistant'] and content.strip():
                                messages.append({
                                    'timestamp': timestamp,
                                    'role': role,
                                    'content': content
                                })
                    except json.JSONDecodeError:
                        continue
            
            if not messages:
                return None
            
            return {
                'session_id': session_id,
                'date': target_date,
                'messages': messages
            }
            
        except Exception as e:
            print(f"⚠️ 读取失败 {file_path}: {e}")
            return None
    
    def extract_daily_sessions(self, date: str) -> List[Dict]:
        """提取指定日期的 sessions"""
        sessions = []
        
        if not self.sessions_dir.exists():
            return sessions
        
        for session_file in self.sessions_dir.glob('*.jsonl'):
            if '.lock' in session_file.name:
                continue
            
            try:
                session_data = self.read_session_file(session_file, date)
                if session_data:
                    sessions.append(session_data)
            except Exception as e:
                print(f"⚠️ 读取失败 {session_file}: {e}")
                continue
        
        return sessions
    
    def write_optimized_log(self, date: str) -> bool:
        """写入优化后的日志到 memory/ 目录，可被 memory_search 搜索"""
        sessions = self.extract_daily_sessions(date)
        if not sessions:
            print(f"ℹ️ {date} 无 sessions")
            return True

        # 生成日志
        log_content = []
        log_content.append(f"# 📅 {date} - Sessions 对话记录")
        log_content.append("")
        log_content.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_content.append(f"**Sessions 数量**: {len(sessions)}")
        log_content.append(f"**类型**: 优化精简版（去除冗余，保留关键对话）")
        log_content.append("")
        log_content.append("---")
        log_content.append("")

        for session in sessions:
            log_content.append(self.format_session(session))
            log_content.append("")
            log_content.append("---")
            log_content.append("")

        # 写入 memory/ 目录，可被 memory_search 搜索
        log_file = self.memory_dir / f"session-daily-{date}.md"
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            log_file.write_text('\n'.join(log_content), encoding='utf-8')
            print(f"✅ 优化日志已写入: {log_file}")
            return True
        except Exception as e:
            print(f"❌ 写入失败: {e}")
            return False
    
    def auto_extract(self):
        """自动提取今天和昨天"""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"🔄 自动提取 Sessions (优化模式)...")
        for date in [yesterday, today]:
            self.write_optimized_log(date)
        print(f"✅ 完成")


# 命令行入口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='优化版 Session 提取器')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--auto', action='store_true', help='自动模式')
    
    args = parser.parse_args()
    
    config = {
        'paths': {
            'memory': '/home/node/.openclaw/workspace/memory'
        }
    }
    
    extractor = SessionExtractorOptimized(config)
    
    if args.auto:
        extractor.auto_extract()
    elif args.date:
        extractor.write_optimized_log(args.date)
    else:
        today = datetime.now().strftime('%Y-%m-%d')
        extractor.write_optimized_log(today)