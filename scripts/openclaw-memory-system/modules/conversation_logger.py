#!/usr/bin/env python3
"""
对话实时记录器 v1.0

功能：每次对话结束后，自动提取关键信息追加到当天日记
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ConversationLogger:
    """对话实时记录器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.workspace = Path(self.config.get('workspace', '/home/node/.openclaw/workspace'))
        self.memory_dir = self.workspace / 'memory'
        self.sessions_dir = Path('/home/node/.openclaw/agents/main/sessions')
        
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_from_current_session(self) -> Optional[Dict]:
        """从当前会话提取摘要"""
        # 获取最新的 session 文件
        if not self.sessions_dir.exists():
            return None
        
        session_files = sorted(
            self.sessions_dir.glob('*.jsonl'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not session_files:
            return None
        
        # 取最近修改的 session
        latest_session = session_files[0]
        return self.extract_conversation_summary(latest_session)
    
    def extract_conversation_summary(self, session_file: Path) -> Optional[Dict]:
        """从 session 文件提取对话摘要"""
        if not session_file.exists():
            return None
        
        try:
            messages = []
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        messages.append(msg)
                    except:
                        continue
            
            if not messages:
                return None
            
            return self._analyze_conversation(messages, session_file)
            
        except Exception as e:
            print(f"❌ 提取失败: {e}")
            return None
    
    def _analyze_conversation(self, messages: List[Dict], session_file: Path = None) -> Dict:
        """分析对话内容，提取关键信息"""
        
        user_messages = []
        assistant_messages = []
        session_id = None
        
        # 提取 session ID
        if session_file:
            session_id = session_file.stem.replace('.jsonl', '')
        
        for msg in messages:
            # 处理 OpenClaw session 格式
            msg_data = msg.get('message', {})
            role = msg_data.get('role', '')
            content = msg_data.get('content', '')
            
            # content 可能是列表或字符串
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                        elif item.get('type') == 'toolCall':
                            # 工具调用记录
                            pass
                        elif item.get('type') == 'toolResult':
                            # 工具结果
                            result = item.get('content', [])
                            if isinstance(result, list):
                                for r in result:
                                    if isinstance(r, dict) and r.get('type') == 'text':
                                        text_parts.append(r.get('text', ''))
                content = '\n'.join(text_parts)
            
            if role == 'user' and content:
                clean_content = self._clean_user_message(content)
                if clean_content:
                    user_messages.append(clean_content)
            elif role == 'assistant' and content:
                assistant_messages.append(content)
        
        return {
            'timestamp': datetime.now().strftime('%H:%M'),
            'user_intent': self._extract_user_intent(user_messages),
            'assistant_actions': self._extract_assistant_actions(assistant_messages),
            'result': self._extract_result(assistant_messages),
            'tools_used': self._extract_tools_used(assistant_messages),
            'message_count': len(messages),
            'session_id': session_id
        }
    
    def _clean_user_message(self, text: str) -> str:
        """清理用户消息"""
        # 去除 Sender metadata（包括 json 块）
        text = re.sub(r'Sender \(untrusted metadata\):\s*```json.*?```', '', text, flags=re.DOTALL)
        # 去除时间戳行 [Mon 2026-03-16 18:47 GMT+8]
        text = re.sub(r'\[\w{3} \d{4}-\d{2}-\d{2} \d{2}:\d{2} GMT[+-]\d+\]', '', text)
        # 去除 Conversation info
        text = re.sub(r'Conversation info \(untrusted metadata\):\s*```json.*?```', '', text, flags=re.DOTALL)
        # 去除多余空白
        text = ' '.join(text.split())
        return text.strip()
    
    def _extract_user_intent(self, user_messages: List[str]) -> str:
        """提取用户主要意图（保留完整内容）"""
        if not user_messages:
            return ""
        
        # 合并所有用户消息，保留完整内容
        full_intent = " | ".join(user_messages[-3:])  # 最近3条
        return full_intent
    
    def _extract_assistant_actions(self, assistant_messages: List[str]) -> List[str]:
        """提取助手采取的行动"""
        actions = []
        
        for msg in assistant_messages[-3:]:  # 只看最近3条
            patterns = [
                r'✅\s*([^\n]+)',
                r'(?:读取|查看|检查|执行|运行|创建|生成|写入|修改|更新|编辑|搜索|查询|查找|推送|提交)[^\n]{2,20}',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, msg)
                actions.extend(matches)
        
        unique_actions = list(dict.fromkeys(actions))
        return unique_actions[:3]
    
    def _extract_result(self, assistant_messages: List[str]) -> str:
        """提取对话结果（保留完整内容）"""
        if not assistant_messages:
            return ""
        
        last_reply = assistant_messages[-1]
        
        # 提取关键结果
        result_patterns = [
            r'✅\s*([^\n]+)',
            r'完成[：:]\s*([^\n]+)',
            r'结果[：:]\s*([^\n]+)',
        ]
        
        for pattern in result_patterns:
            match = re.search(pattern, last_reply)
            if match:
                return match.group(1).strip()
        
        # 返回完整回复（不截断）
        return last_reply
    
    def _extract_tools_used(self, assistant_messages: List[str]) -> List[str]:
        """提取使用的工具"""
        tools = set()
        
        all_text = ' '.join(assistant_messages)
        
        tool_keywords = {
            'read': '读取',
            'edit': '编辑',
            'write': '写入',
            'exec': '执行命令',
            'web_search': '搜索',
            'web_fetch': '获取网页',
            'browser': '浏览器',
            'memory_search': '记忆搜索',
            'memory_get': '记忆读取',
            'message': '发消息',
            'cron': '定时任务',
            'gateway': '网关',
            'sessions_spawn': '子代理',
        }
        
        for keyword, tool_name in tool_keywords.items():
            if keyword in all_text.lower():
                tools.add(tool_name)
        
        return list(tools)[:3]
    
    def append_to_daily_memory(self, summary: Dict, date: str = None):
        """追加到当天记忆文件"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        memory_file = self.memory_dir / f"{date}.md"
        log_entry = self._format_log_entry(summary)
        
        if memory_file.exists():
            self._append_to_existing(memory_file, log_entry, summary)
        else:
            self._create_new_memory(memory_file, log_entry, date)
        
        print(f"✅ 已记录到 {memory_file.name}")
        return True
    
    def _format_log_entry(self, summary: Dict) -> str:
        """格式化日志条目"""
        lines = [
            f"\n### {summary['timestamp']} - 对话记录",
            f"**用户**: {summary['user_intent']}",
        ]
        
        if summary['assistant_actions']:
            actions = '、'.join(summary['assistant_actions'])
            lines.append(f"**行动**: {actions}")
        
        if summary['tools_used']:
            tools = '、'.join(summary['tools_used'])
            lines.append(f"**工具**: {tools}")
        
        lines.append(f"**结果**: {summary['result']}")
        
        return '\n'.join(lines)
    
    def _append_to_existing(self, memory_file: Path, log_entry: str, summary: Dict = None):
        """追加到现有记忆文件（智能合并，避免重复）"""
        try:
            content = memory_file.read_text(encoding='utf-8')
        except:
            content = ""
        
        # 检查是否已经记录过这个 session（避免重复）
        if summary and 'session_id' in summary:
            session_marker = f"<!-- session:{summary['session_id']} -->"
            if session_marker in content:
                print(f"⚠️ Session {summary['session_id'][:8]}... 已记录，跳过")
                return False
            log_entry += f"\n{session_marker}"
        
        # 在"对话记录"部分后插入
        if "## 对话记录" in content:
            # 找到最后一个对话记录条目后插入
            lines = content.split('\n')
            insert_pos = len(lines)
            
            # 从后往前找，找到最后一个 ### 开头的行
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].startswith('### '):
                    insert_pos = i
                    break
            
            # 在最后一个条目后插入
            new_lines = lines[:insert_pos] + [log_entry.strip()] + lines[insert_pos:]
            new_content = '\n'.join(new_lines)
        else:
            # 没有对话记录部分，追加到文件末尾
            new_content = content + "\n## 对话记录" + log_entry
        
        memory_file.write_text(new_content, encoding='utf-8')
        return True
    
    def _create_new_memory(self, memory_file: Path, log_entry: str, date: str):
        """创建新记忆文件"""
        header = f"# {date} - 自动记录\n\n"
        header += f"**日期**: {date}\n"
        header += f"**创建时间**: {datetime.now().strftime('%H:%M')}\n\n"
        
        content = header + "## 对话记录" + log_entry
        content += f"\n\n*🤖 自动创建: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        memory_file.write_text(content, encoding='utf-8')
    
    def log_current_conversation(self):
        """记录当前对话（主入口）"""
        print("📝 提取当前对话...")
        
        summary = self.extract_from_current_session()
        if not summary:
            print("⚠️ 没有可提取的内容")
            return False
        
        print(f"   用户意图: {summary['user_intent'][:50]}...")
        print(f"   消息数: {summary['message_count']}")
        
        return self.append_to_daily_memory(summary)


# 命令行入口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='对话实时记录器')
    parser.add_argument('--now', action='store_true', help='记录当前对话')
    parser.add_argument('--session', type=str, help='指定 session 文件')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    logger = ConversationLogger()
    
    if args.session:
        # 从指定 session 提取
        summary = logger.extract_conversation_summary(Path(args.session))
        if summary:
            logger.append_to_daily_memory(summary, args.date)
    elif args.now:
        # 记录当前对话
        logger.log_current_conversation()
    else:
        # 默认记录当前
        logger.log_current_conversation()
