#!/usr/bin/env python3
"""
Session 提取器 - 统一增强版 v3.1

整合原版 session_extractor.py + record-session.sh 的功能：
1. 保留原版的结构化输出和覆盖率检查
2. 添加 record-session.sh 的对话流格式和智能分类
3. 支持两种格式切换
4. 增强错误处理和日志
"""

import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class SessionExtractorUnified:
    """
    Sessions 提取器 - 统一增强版
    
    支持两种输出格式：
    - structured: 结构化格式（原版）
    - conversation: 对话流格式（来自 record-session.sh）
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.sessions_dir = Path("/home/node/.openclaw/agents/main/sessions")
        self.memory_dir = Path(config.get('paths', {}).get('memory', '/home/node/.openclaw/workspace/memory'))
        self.extracted_cache: Dict[str, Set[str]] = {}
    
    # ==================== 文本处理工具（来自 record-session.sh）====================
    
    def sanitize_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        
        # 替换转义字符
        text = text.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', '').replace('\\"', '"')
        
        # 提取时间戳后的实际内容
        match = re.search(r'\[\w{3}\s+[^\]]+\]\s*(.+)', text, re.DOTALL)
        if match:
            text = match.group(1)
        
        # 清理元数据标记
        text = re.sub(r'Sender \(untrusted metadata\):.*', '', text, flags=re.DOTALL)
        text = re.sub(r'Conversation info \(untrusted metadata\):.*', '', text, flags=re.DOTALL)
        text = re.sub(r'```json\s*\{.*?\}\s*```', '', text, flags=re.DOTALL)
        text = ' '.join(text.split())
        
        return text.strip()
    
    def classify_message(self, text: str) -> str:
        """消息分类标记"""
        if not text:
            return ""
        
        markers = []
        
        # 问题标记
        if any(k in text for k in ['?', '？', '吗', '什么', '怎么', '为什么', '如何']):
            markers.append("[问]")
        
        # 指令标记
        if any(text.startswith(k) for k in ['帮我', '请', '需要', '查看', '检查', '修复', '重写', '创建', '修改']):
            markers.append("[指令]")
        
        # 反馈标记
        if any(text.startswith(k) for k in ['好', '可以', '行', '不对', '错了', '很好']):
            markers.append("[反馈]")
        
        # 完成标记
        if any(k in text for k in ['✅', '完成', '成功', '搞定', '解决了']):
            markers.append("[完成]")
        
        return ' '.join(markers)
    
    def should_skip(self, text: str, role: str = "") -> bool:
        """判断是否跳过消息"""
        if not text:
            return True
        if role not in ["user", "assistant"]:
            return True
        if text == '...':
            return True
        
        # 跳过系统消息
        patterns = [r'^A new session', r'^Execute your', r'^\[Inter-session message\]']
        for p in patterns:
            if re.search(p, text, re.I):
                return True
        
        return False
    
    def extract_key_points(self, text: str) -> str:
        """提取关键点"""
        if not text:
            return ""
        
        lines = text.split('\\n')
        points = []
        
        # 提取列表项
        for l in lines:
            if re.match(r'^\s*[-*]\s', l):
                points.append(l.strip())
        
        points = points[:3]
        
        # 查找成功/完成标记
        for l in lines:
            if any(k in l for k in ['✅', '成功', '完成', '找到', '修复', '已创建']):
                if l.strip() not in points:
                    points.append(l.strip())
                    break
        
        if points:
            return '\\n'.join(points[:4])
        
        # 如果没有列表项，返回前300字符
        return text[:300] + "..." if len(text) > 300 else text
    
    # ==================== Session 提取（整合版）====================
    
    def extract_daily_sessions(self, date: str, include_assistant: bool = True) -> List[Dict]:
        """
        提取指定日期的 sessions - 增强版
        
        Args:
            date: 日期 (YYYY-MM-DD)
            include_assistant: 是否包含 assistant 消息
        """
        sessions = []
        
        if not self.sessions_dir.exists():
            print(f"⚠️ Sessions 目录不存在: {self.sessions_dir}")
            return sessions
        
        # 遍历所有 .jsonl 文件
        for session_file in self.sessions_dir.glob('*.jsonl*'):
            if '.lock' in session_file.name:
                continue
            if not ('.jsonl' in session_file.name or '.jsonl.reset' in session_file.name):
                continue
            
            try:
                session_data = self._read_session_file(session_file, date, include_assistant)
                if session_data:
                    sessions.append(session_data)
            except Exception as e:
                print(f"⚠️ 读取 session 文件失败 {session_file}: {e}")
                continue
        
        print(f"📊 提取到 {len(sessions)} 个 sessions")
        return sessions
    
    def _read_session_file(self, file_path: Path, target_date: str, include_assistant: bool = True) -> Optional[Dict]:
        """读取单个 session 文件 - 增强版"""
        messages = []
        session_id = file_path.stem
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        record = json.loads(line)
                        
                        # 检查日期
                        timestamp = record.get('timestamp', '')
                        if target_date not in timestamp:
                            continue
                        
                        record_type = record.get('type', '')
                        
                        if record_type == 'message':
                            message_data = record.get('message', {})
                            role = message_data.get('role', '')
                            content_data = message_data.get('content', [])
                            
                            # 跳过非目标角色（如果不包含 assistant）
                            if not include_assistant and role != 'user':
                                continue
                            
                            # 提取文本
                            if isinstance(content_data, list) and content_data:
                                text_parts = []
                                for item in content_data:
                                    if isinstance(item, dict) and 'text' in item:
                                        text_parts.append(item['text'])
                                content = ' '.join(text_parts)
                            else:
                                content = str(content_data)
                            
                            # 清理和过滤
                            content = self.sanitize_text(content)
                            
                            if self.should_skip(content, role):
                                continue
                            
                            messages.append({
                                'timestamp': timestamp,
                                'role': role,
                                'content': content
                            })
                    
                    except json.JSONDecodeError:
                        continue
            
            if not messages:
                return None
            
            # 生成增强摘要
            summary = self._generate_summary(messages)
            
            return {
                'session_id': session_id,
                'date': target_date,
                'messages': messages,
                'summary': summary,
                'message_count': len(messages),
                'user_count': len([m for m in messages if m['role'] == 'user']),
                'assistant_count': len([m for m in messages if m['role'] == 'assistant'])
            }
            
        except Exception as e:
            print(f"⚠️ 解析 session 文件失败 {file_path}: {e}")
            return None
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        """生成增强版摘要"""
        if not messages:
            return "无内容"
        
        user_messages = [m for m in messages if m['role'] == 'user']
        assistant_messages = [m for m in messages if m['role'] == 'assistant']
        
        # 提取主题（第一条用户消息）
        topic = ""
        if user_messages:
            first_user = user_messages[0]['content'][:50]
            topic = first_user
        
        return f"共 {len(user_messages)} 轮对话，{len(assistant_messages)} 条回复。主题: {topic}..."
    
    # ==================== 格式化输出（双格式支持）====================
    
    def format_conversation_flow(self, session: Dict) -> str:
        """对话流格式（来自 record-session.sh）"""
        lines = []
        
        for msg in session['messages']:
            if msg['role'] == 'user':
                marker = self.classify_message(msg['content'])
                # 截断用户消息
                display = msg['content'][:600] + "..." if len(msg['content']) > 600 else msg['content']
                if marker:
                    lines.append(f"\n**用户**: {marker} {display}")
                else:
                    lines.append(f"\n**用户**: {display}")
            
            elif msg['role'] == 'assistant':
                # 提取关键点
                key = self.extract_key_points(msg['content'])
                if key:
                    lines.append(f"**助手**: {key}")
        
        return '\n'.join(lines)
    
    def format_structured(self, session: Dict) -> str:
        """结构化格式（原版）"""
        lines = []
        lines.append(f"\n**Session**: {session['session_id']}")
        lines.append(f"- **时间**: {session['date']}")
        lines.append(f"- **消息数**: {session['message_count']}")
        lines.append(f"- **用户消息**: {session['user_count']}")
        lines.append(f"- **助手回复**: {session['assistant_count']}")
        lines.append(f"- **摘要**: {session['summary']}")
        
        # 只显示 user 消息（前5条）
        user_messages = [m for m in session['messages'] if m['role'] == 'user']
        lines.append("\n**用户消息**:")
        for msg in user_messages[:5]:
            time = msg['timestamp'].split('T')[1][:5] if 'T' in msg['timestamp'] else msg['timestamp'][-5:]
            content = msg['content'][:100]
            lines.append(f"- {time} {content}")
        
        if len(user_messages) > 5:
            lines.append(f"- ... (还有 {len(user_messages) - 5} 条)")
        
        return '\n'.join(lines)
    
    # ==================== 合并到记忆（双格式支持）====================
    
    def merge_to_daily_memory(self, date: str, format_type: str = "conversation") -> bool:
        """
        合并到每日记忆 - 简化版（不再写入 Sessions 详细对话记录）

        注意：详细的 Sessions 对话记录现在由 SessionExtractorOptimized
        生成到 session-daily-*.md 文件中，可被 memory_search 搜索。
        此方法仅保留 session 统计信息到每日记忆文件。

        Args:
            date: 日期 (YYYY-MM-DD)
            format_type: 保留参数（不再使用）
        """
        # 提取 sessions（包含 assistant）
        sessions = self.extract_daily_sessions(date, include_assistant=True)
        if not sessions:
            print(f"ℹ️ {date} 无 sessions 需要记录")
            return True

        # 读取现有记忆
        memory_file = self.memory_dir / f"{date}.md"
        existing_content = ""

        if memory_file.exists():
            try:
                existing_content = memory_file.read_text(encoding='utf-8')
            except Exception as e:
                print(f"⚠️ 读取记忆文件失败: {e}")

        # 只生成统计摘要（不包含详细对话）
        summary_content = self._format_session_summary(sessions, date)

        # 写入
        try:
            if memory_file.exists():
                updated_content = self._append_to_memory(existing_content, summary_content)
            else:
                updated_content = self._create_new_memory(date, summary_content)

            memory_file.parent.mkdir(parents=True, exist_ok=True)
            memory_file.write_text(updated_content, encoding='utf-8')

            print(f"✅ 已记录 {len(sessions)} 个 sessions 统计到 {memory_file}")
            return True

        except Exception as e:
            print(f"❌ 记录失败: {e}")
            return False

    def _format_session_summary(self, sessions: List[Dict], date: str) -> str:
        """生成 session 统计摘要（不包含详细对话）"""
        lines = ["\n### Sessions 统计\n"]
        lines.append(f"**日期**: {date}")
        lines.append(f"**Sessions 数量**: {len(sessions)}")
        lines.append(f"**总消息数**: {sum(s['message_count'] for s in sessions)}")
        lines.append("")
        lines.append("**Session 列表**:")

        for session in sessions:
            lines.append(f"- `{session['session_id']}`: {session['summary'][:80]}...")

        lines.append("")
        lines.append(f"📄 **详细对话记录**: 见 `session-daily-{date}.md`")
        lines.append("")

        return '\n'.join(lines)
    
    def _format_for_merge_conversation(self, sessions: List[Dict]) -> str:
        """对话流格式合并"""
        lines = ["\n### Sessions 对话记录\n"]
        
        for session in sessions:
            lines.append(f"\n**Session**: {session['session_id']}")
            lines.append(f"- **时间**: {session['date']}")
            lines.append(f"- **摘要**: {session['summary']}")
            lines.append("\n**对话内容**:")
            lines.append(self.format_conversation_flow(session))
        
        return '\n'.join(lines)
    
    def _format_for_merge_structured(self, sessions: List[Dict]) -> str:
        """结构化格式合并"""
        lines = ["\n### Sessions 自动记录\n"]
        
        for session in sessions:
            lines.append(self.format_structured(session))
        
        return '\n'.join(lines)
    
    def _extract_existing_sessions(self, content: str) -> Set[str]:
        """提取已记录的 session IDs"""
        sessions = set()
        patterns = [
            r'## Session:\s*(\S+)',
            r'Session ID:\s*(\S+)',
            r'\*\*Session\*\*:\s*(\S+)'
        ]
        for pattern in patterns:
            sessions.update(re.findall(pattern, content))
        return sessions
    
    def _append_to_memory(self, existing: str, new_content: str) -> str:
        """追加到现有记忆"""
        if "*🤖 自动归档" in existing:
            parts = existing.rsplit("*🤖 自动归档", 1)
            return parts[0] + new_content + "\n\n*🤖 自动归档" + parts[1]
        else:
            return existing + new_content
    
    def _create_new_memory(self, date: str, content: str) -> str:
        """创建新记忆文件"""
        header = f"# {date} - 自动记录\n\n"
        header += f"**日期**: {date}\n"
        header += f"**创建时间**: {datetime.now().strftime('%H:%M')}\n\n"
        
        footer = f"\n\n*🤖 自动创建: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        footer += "*来源: SessionExtractorUnified*"
        
        return header + content + footer
    
    # ==================== 覆盖率检查（原版功能）====================
    
    def check_session_coverage(self, days: int = 7) -> Dict:
        """检查 session 覆盖度"""
        total_sessions = 0
        recorded_sessions = 0
        missing_dates = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 统计 sessions 数量
            day_sessions = self._count_sessions_for_date(date)
            total_sessions += day_sessions
            
            # 检查是否已记录到 memory/
            memory_file = self.memory_dir / f"{date}.md"
            if memory_file.exists():
                try:
                    content = memory_file.read_text(encoding='utf-8')
                except:
                    content = ""
                recorded = self._count_recorded_sessions(content)
                recorded_sessions += recorded
                
                if recorded < day_sessions:
                    missing_dates.append(date)
            else:
                missing_dates.append(date)
        
        coverage_rate = recorded_sessions / total_sessions if total_sessions > 0 else 1.0
        
        return {
            'total_sessions': total_sessions,
            'recorded_sessions': recorded_sessions,
            'coverage_rate': coverage_rate,
            'missing_dates': missing_dates,
            'status': 'ok' if coverage_rate >= 0.95 else 'warning'
        }
    
    def _count_sessions_for_date(self, date: str) -> int:
        """统计指定日期的 session 数量"""
        count = 0
        
        if not self.sessions_dir.exists():
            return 0
        
        for session_file in self.sessions_dir.glob('*.jsonl'):
            if not session_file.name.endswith('.jsonl'):
                continue
            
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if date in line:
                            count += 1
                            break
            except:
                continue
        
        return count
    
    def _count_recorded_sessions(self, content: str) -> int:
        """统计已记录的 session 数量"""
        return len(re.findall(r'\*\*Session\*\*:', content))
    
    def auto_extract_and_merge(self, format_type: str = "conversation"):
        """自动提取并合并（定时任务调用）"""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"🔄 自动提取 Sessions...")
        print(f"   今天: {today}")
        print(f"   昨天: {yesterday}")
        
        # 合并今天和昨天（确保不遗漏）
        for date in [yesterday, today]:
            self.merge_to_daily_memory(date, format_type)
        
        print(f"✅ 自动提取完成")


# 命令行入口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Session 提取器 - 统一增强版')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--format', choices=['structured', 'conversation'], 
                       default='conversation', help='输出格式 (默认: conversation)')
    parser.add_argument('--auto', action='store_true', help='自动模式（今天和昨天）')
    parser.add_argument('--check', action='store_true', help='检查覆盖率')
    parser.add_argument('--days', type=int, default=7, help='检查天数 (默认: 7)')
    
    args = parser.parse_args()
    
    config = {
        'paths': {
            'memory': '/home/node/.openclaw/workspace/memory'
        }
    }
    
    extractor = SessionExtractorUnified(config)
    
    if args.check:
        result = extractor.check_session_coverage(days=args.days)
        print(f"\n📊 Session 覆盖率报告:")
        print(f"   总 Sessions: {result['total_sessions']}")
        print(f"   已记录: {result['recorded_sessions']}")
        print(f"   覆盖率: {result['coverage_rate']:.1%}")
        print(f"   状态: {result['status']}")
        if result['missing_dates']:
            print(f"   缺失日期: {', '.join(result['missing_dates'][:5])}")
    
    elif args.auto:
        extractor.auto_extract_and_merge(args.format)
    
    elif args.date:
        extractor.merge_to_daily_memory(args.date, args.format)
    
    else:
        # 默认：今天
        today = datetime.now().strftime('%Y-%m-%d')
        extractor.merge_to_daily_memory(today, args.format)
