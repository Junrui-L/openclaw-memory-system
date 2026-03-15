#!/usr/bin/env python3
"""
Session 提取器 - v3.0 Phase 1 核心模块

职责：自动提取 sessions 记录，合并到每日记忆
原则：
    - 每小时自动执行
    - 智能去重、补充
    - 保障数据不丢失

重要说明：
    - memory_search 不覆盖 agents/main/sessions/ 目录
    - 必须直接读取文件系统
    - 提取后合并到 memory/，才能被 memory_search 搜索
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


class SessionExtractor:
    """
    Sessions 提取器
    
    职责：自动提取 sessions 记录，合并到每日记忆
    """
    
    def __init__(self, config: Dict):
        """
        初始化
        
        Args:
            config: 配置字典
        """
        self.config = config
        # Sessions 目录路径（直接指定，不通过 reader）
        self.sessions_dir = Path("/home/node/.openclaw/agents/main/sessions")
        self.memory_dir = Path(config.get('paths', {}).get('memory', '/home/node/.openclaw/workspace/memory'))
        self.extracted_cache: Dict[str, Set[str]] = {}  # 已提取的 session 缓存
    
    def extract_daily_sessions(self, date: str) -> List[Dict]:
        """
        提取指定日期的 sessions
        
        实现:
            1. 【直接读取】遍历 self.sessions_dir 下的 .jsonl 文件
            2. 【直接读取】读取 JSON Lines 格式
            3. 【直接读取】按日期过滤（检查 timestamp）
            4. 提取用户消息内容（过滤系统消息）
            5. 去重（基于消息内容 hash）
            6. 格式化返回
            
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            Session 列表
        """
        sessions = []
        
        if not self.sessions_dir.exists():
            print(f"⚠️ Sessions 目录不存在: {self.sessions_dir}")
            return sessions
        
        # 遍历所有 .jsonl 文件（包括 .jsonl.reset.*）
        for session_file in self.sessions_dir.glob('*.jsonl*'):
            # 跳过非相关文件（如 .lock）
            if '.lock' in session_file.name:
                continue
            if not ('.jsonl' in session_file.name or '.jsonl.reset' in session_file.name):
                continue
            
            try:
                session_data = self._read_session_file(session_file, date)
                if session_data:
                    sessions.append(session_data)
            except Exception as e:
                print(f"⚠️ 读取 session 文件失败 {session_file}: {e}")
                continue
        
        print(f"📊 提取到 {len(sessions)} 个 sessions")
        return sessions
    
    def _read_session_file(self, file_path: Path, target_date: str) -> Optional[Dict]:
        """
        读取单个 session 文件
        
        Args:
            file_path: .jsonl 文件路径
            target_date: 目标日期
            
        Returns:
            Session 数据或 None
        """
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
                        
                        # 检查日期是否匹配
                        timestamp = record.get('timestamp', '')
                        if target_date not in timestamp:
                            continue
                        
                        # 处理不同类型的记录
                        record_type = record.get('type', '')
                        
                        if record_type == 'message':
                            # 新格式：message 类型
                            # role 和 content 在 message 字段中
                            message_data = record.get('message', {})
                            role = message_data.get('role', '')
                            content_data = message_data.get('content', [])
                            
                            # content 是数组，提取文本
                            if isinstance(content_data, list) and content_data:
                                text_parts = []
                                for item in content_data:
                                    if isinstance(item, dict) and 'text' in item:
                                        text_parts.append(item['text'])
                                content = ' '.join(text_parts)
                            else:
                                content = str(content_data)
                            
                            if role == 'user' and content:
                                messages.append({
                                    'timestamp': timestamp,
                                    'content': content[:200]  # 截断长内容
                                })
                        
                        elif record_type == 'session':
                            # Session 元数据，跳过
                            continue
                        
                        elif 'role' in record and 'content' in record:
                            # 旧格式：直接包含 role/content
                            role = record.get('role', '')
                            content = record.get('content', '')
                            
                            if role == 'user' and content:
                                messages.append({
                                    'timestamp': timestamp,
                                    'content': content
                                })
                    except json.JSONDecodeError:
                        continue
            
            if not messages:
                return None
            
            # 生成摘要
            summary = self._generate_summary(messages)
            
            return {
                'session_id': session_id,
                'date': target_date,
                'messages': messages,
                'summary': summary,
                'message_count': len(messages)
            }
            
        except Exception as e:
            print(f"⚠️ 解析 session 文件失败 {file_path}: {e}")
            return None
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        """
        生成会话摘要
        
        Args:
            messages: 消息列表
            
        Returns:
            摘要文本
        """
        if not messages:
            return "无内容"
        
        # 取前3条消息生成摘要
        contents = [m['content'][:50] for m in messages[:3]]
        summary = " | ".join(contents)
        
        if len(messages) > 3:
            summary += f" ... (共 {len(messages)} 条)"
        
        return summary
    
    def merge_to_daily_memory(self, date: str) -> bool:
        """
        将 sessions 合并到每日记忆
        
        实现:
            1. 提取当日 sessions（直接读取文件系统）
            2. 【直接读取】读取现有记忆文件
            3. 智能合并:
               - 去重：已存在的 session 不重复添加
               - 补充：新 session 添加到合适位置
            4. 写回记忆文件
            
        Args:
            date: 日期
            
        Returns:
            合并成功返回 True
        """
        # 1. 提取 sessions
        sessions = self.extract_daily_sessions(date)
        if not sessions:
            print(f"ℹ️ {date} 无 sessions 需要合并")
            return True
        
        # 2. 读取现有记忆
        memory_file = self.memory_dir / f"{date}.md"
        existing_content = ""
        existing_sessions: Set[str] = set()
        
        if memory_file.exists():
            try:
                existing_content = memory_file.read_text(encoding='utf-8')
                # 提取已记录的 session IDs
                existing_sessions = self._extract_existing_sessions(existing_content)
            except Exception as e:
                print(f"⚠️ 读取记忆文件失败: {e}")
        
        # 3. 过滤已存在的 sessions
        new_sessions = [s for s in sessions if s['session_id'] not in existing_sessions]
        
        if not new_sessions:
            print(f"✅ {date} 所有 sessions 已存在，无需合并")
            return True
        
        # 4. 生成合并内容
        merge_content = self._format_sessions_for_merge(new_sessions)
        
        # 5. 写入记忆文件
        try:
            if existing_content:
                # 追加到现有文件
                updated_content = self._append_to_memory(existing_content, merge_content)
            else:
                # 创建新文件
                updated_content = self._create_new_memory(date, merge_content)
            
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            memory_file.write_text(updated_content, encoding='utf-8')
            
            print(f"✅ 已合并 {len(new_sessions)} 个 sessions 到 {memory_file}")
            return True
            
        except Exception as e:
            print(f"❌ 合并失败: {e}")
            return False
    
    def _extract_existing_sessions(self, content: str) -> Set[str]:
        """
        从现有记忆内容中提取已记录的 session IDs
        
        Args:
            content: 记忆内容
            
        Returns:
            Session ID 集合
        """
        sessions = set()
        
        # 查找 "## Session: xxx" 或 "- Session ID: xxx"
        import re
        
        # 匹配 "## Session: xxx"
        pattern1 = r'## Session:\s*(\S+)'
        matches1 = re.findall(pattern1, content)
        sessions.update(matches1)
        
        # 匹配 "- Session ID: xxx"
        pattern2 = r'Session ID:\s*(\S+)'
        matches2 = re.findall(pattern2, content)
        sessions.update(matches2)
        
        return sessions
    
    def _format_sessions_for_merge(self, sessions: List[Dict]) -> str:
        """
        格式化 sessions 为 Markdown
        
        Args:
            sessions: Session 列表
            
        Returns:
            Markdown 格式内容
        """
        lines = ["\n### Sessions 自动记录\n"]
        
        for session in sessions:
            lines.append(f"\n**Session**: {session['session_id']}")
            lines.append(f"- **时间**: {session['date']}")
            lines.append(f"- **消息数**: {session['message_count']}")
            lines.append(f"- **摘要**: {session['summary']}")
            
            # 添加消息详情（前5条）
            lines.append("\n**对话内容**:")
            for msg in session['messages'][:5]:
                time = msg['timestamp'].split('T')[1][:5]  # HH:MM
                content = msg['content'][:100]  # 截断长内容
                lines.append(f"- {time} {content}")
            
            if len(session['messages']) > 5:
                lines.append(f"- ... (还有 {len(session['messages']) - 5} 条)")
        
        return '\n'.join(lines)
    
    def _append_to_memory(self, existing: str, new_content: str) -> str:
        """
        追加内容到现有记忆
        
        Args:
            existing: 现有内容
            new_content: 新内容
            
        Returns:
            合并后内容
        """
        # 在文件末尾追加（在自动归档标记之前）
        if "*🤖 自动归档" in existing:
            # 在归档标记前插入
            parts = existing.rsplit("*🤖 自动归档", 1)
            return parts[0] + new_content + "\n\n*🤖 自动归档" + parts[1]
        else:
            # 直接追加
            return existing + new_content
    
    def _create_new_memory(self, date: str, content: str) -> str:
        """
        创建新的记忆文件
        
        Args:
            date: 日期
            content: 内容
            
        Returns:
            完整记忆内容
        """
        header = f"# {date} - 自动记录\n\n"
        header += f"**日期**: {date}\n"
        header += f"**创建时间**: {datetime.now().strftime('%H:%M')}\n\n"
        
        footer = f"\n\n*🤖 自动创建: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        footer += "*来源: SessionExtractor*"
        
        return header + content + footer
    
    def check_session_coverage(self, days: int = 7) -> Dict:
        """
        检查 session 覆盖度
        
        Args:
            days: 检查天数
            
        Returns:
            覆盖率报告
        """
        total_sessions = 0
        recorded_sessions = 0
        missing_dates = []
        
        for i in range(days):
            date = (datetime.now() - __import__('datetime').timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 统计 sessions 数量（直接读取）
            day_sessions = self._count_sessions_for_date(date)
            total_sessions += day_sessions
            
            # 检查是否已记录到 memory/
            memory_file = self.memory_dir / f"{date}.md"
            if memory_file.exists():
                content = memory_file.read_text(encoding='utf-8') if memory_file.exists() else ""
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
        import re
        return len(re.findall(r'\*\*Session\*\*:', content))
    
    def auto_extract_and_merge(self):
        """
        自动提取并合并（定时任务调用）
        
        执行:
            1. 获取今天和昨天的日期
            2. 提取 sessions
            3. 合并到记忆
            4. 记录日志
        """
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - __import__('datetime').timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"🔄 自动提取 Sessions...")
        print(f"   今天: {today}")
        print(f"   昨天: {yesterday}")
        
        # 合并今天和昨天（确保不遗漏）
        for date in [yesterday, today]:
            self.merge_to_daily_memory(date)
        
        print(f"✅ 自动提取完成")


# 命令行入口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Session 提取器')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--auto', action='store_true', help='自动模式（今天和昨天）')
    parser.add_argument('--check', action='store_true', help='检查覆盖率')
    
    args = parser.parse_args()
    
    config = {
        'paths': {
            'memory': '/home/node/.openclaw/workspace/memory'
        }
    }
    
    extractor = SessionExtractor(config)
    
    if args.check:
        result = extractor.check_session_coverage(days=7)
        print(f"\n📊 Session 覆盖率报告:")
        print(f"   总 Sessions: {result['total_sessions']}")
        print(f"   已记录: {result['recorded_sessions']}")
        print(f"   覆盖率: {result['coverage_rate']:.1%}")
        print(f"   状态: {result['status']}")
        if result['missing_dates']:
            print(f"   缺失日期: {', '.join(result['missing_dates'])}")
    
    elif args.auto:
        extractor.auto_extract_and_merge()
    
    elif args.date:
        extractor.merge_to_daily_memory(args.date)
    
    else:
        # 默认：今天
        today = datetime.now().strftime('%Y-%m-%d')
        extractor.merge_to_daily_memory(today)