#!/usr/bin/env python3
"""
数据读取模块
读取双记忆系统的各层数据
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class MemoryReader:
    """记忆数据读取器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.paths = config.get('paths', {})
    
    # ========== 日记层读取 ==========
    
    def read_daily_memory(self, date: str) -> Optional[str]:
        """读取指定日期的日记文件"""
        memory_dir = Path(self.paths.get('memory', ''))
        file_path = memory_dir / f"{date}.md"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"警告: 无法读取日记 {date}: {e}")
            return None
    
    def list_memory_files(self, days: int = 7) -> List[str]:
        """列出最近N天的记忆文件"""
        memory_dir = Path(self.paths.get('memory', ''))
        if not memory_dir.exists():
            return []
        
        files = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            file_path = memory_dir / f"{date}.md"
            if file_path.exists():
                files.append(date)
        
        return files
    
    def get_memory_stats(self) -> Dict:
        """获取日记层统计"""
        memory_dir = Path(self.paths.get('memory', ''))
        if not memory_dir.exists():
            return {'count': 0, 'total_size': 0}
        
        files = list(memory_dir.glob('*.md'))
        total_size = sum(f.stat().st_size for f in files)
        
        return {
            'count': len(files),
            'total_size': total_size,
            'files': [f.name for f in files]
        }
    
    # ========== 身份层读取 ==========
    
    def read_hot_memory(self) -> Optional[str]:
        """读取HOT记忆（self-improving/memory.md）"""
        file_path = Path(self.paths.get('self_improving', '')) / 'memory.md'
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"警告: 无法读取HOT记忆: {e}")
            return None
    
    def read_corrections(self, limit: int = 50) -> List[Dict]:
        """读取最近纠正记录"""
        file_path = Path(self.paths.get('self_improving', '')) / 'corrections.md'
        
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单解析纠正记录
            corrections = []
            lines = content.split('\n')
            for line in lines[-limit*3:]:  # 粗略估计
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    corrections.append({'content': line.strip()})
            
            return corrections[-limit:]
        except Exception as e:
            print(f"警告: 无法读取纠正记录: {e}")
            return []
    
    # ========== 任务层读取 ==========
    
    def read_learnings(self, status: Optional[str] = None) -> List[Dict]:
        """读取学习记录"""
        file_path = Path(self.paths.get('learnings', '')) / 'LEARNINGS.md'
        
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析学习记录条目
            learnings = []
            entries = re.split(r'\n## \[', content)
            
            for entry in entries[1:]:  # 跳过第一个空项
                learning = self._parse_learning_entry('## [' + entry)
                if learning:
                    if status is None or learning.get('status') == status:
                        learnings.append(learning)
            
            return learnings
        except Exception as e:
            print(f"警告: 无法读取学习记录: {e}")
            return []
    
    def _parse_learning_entry(self, content: str) -> Optional[Dict]:
        """解析单个学习记录条目"""
        learning = {}
        
        # 提取ID
        id_match = re.search(r'\[([A-Z]+-\d{8}-\d{3})\]', content)
        if id_match:
            learning['id'] = id_match.group(1)
        
        # 提取状态
        status_match = re.search(r'\*\*Status\*\*:\s*(\w+)', content)
        if status_match:
            learning['status'] = status_match.group(1)
        
        # 提取摘要
        summary_match = re.search(r'### Summary\s*\n([^\n]+)', content)
        if summary_match:
            learning['summary'] = summary_match.group(1).strip()
        
        return learning
    
    def read_errors(self, days: int = 7) -> List[Dict]:
        """读取近期错误记录"""
        file_path = Path(self.paths.get('learnings', '')) / 'ERRORS.md'
        
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析错误记录
            errors = []
            entries = re.split(r'\n## \[', content)
            
            for entry in entries[1:]:
                error = self._parse_error_entry('## [' + entry)
                if error:
                    errors.append(error)
            
            return errors
        except Exception as e:
            print(f"警告: 无法读取错误记录: {e}")
            return []
    
    def _parse_error_entry(self, content: str) -> Optional[Dict]:
        """解析单个错误记录条目"""
        error = {}
        
        id_match = re.search(r'\[(ERR-\d{8}-\d{3})\]', content)
        if id_match:
            error['id'] = id_match.group(1)
        
        summary_match = re.search(r'### Summary\s*\n([^\n]+)', content)
        if summary_match:
            error['summary'] = summary_match.group(1).strip()
        
        return error
    
    def get_learning_stats(self) -> Dict:
        """获取学习记录统计"""
        learnings = self.read_learnings()
        errors = self.read_errors()
        
        pending = len([l for l in learnings if l.get('status') == 'pending'])
        resolved = len([l for l in learnings if l.get('status') == 'resolved'])
        
        return {
            'total_learnings': len(learnings),
            'pending_learnings': pending,
            'resolved_learnings': resolved,
            'total_errors': len(errors)
        }
    
    # ========== 长期记忆读取 ==========
    
    def read_long_term_memory(self) -> Optional[str]:
        """读取长期记忆档案（MEMORY.md）"""
        file_path = Path(self.paths.get('memory_md', ''))
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"警告: 无法读取长期记忆: {e}")
            return None
    
    # ========== Sessions 读取 ==========
    
    def read_sessions(self, days: int = 1) -> List[Dict]:
        """读取最近N天的 sessions 记录"""
        sessions_dir = Path('/home/node/.openclaw/agents/main/sessions')
        if not sessions_dir.exists():
            return []
        
        sessions = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        try:
            # 读取 sessions.json 索引
            sessions_index = sessions_dir / 'sessions.json'
            if sessions_index.exists():
                with open(sessions_index, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                for session_key, session_info in index_data.items():
                    # 检查更新时间
                    updated_at = session_info.get('updatedAt', 0)
                    updated_time = datetime.fromtimestamp(updated_at / 1000)
                    
                    if updated_time >= cutoff_time:
                        session_data = {
                            'key': session_key,
                            'updated_at': updated_time.isoformat(),
                            'chat_type': session_info.get('chatType', 'unknown'),
                            'channel': session_info.get('deliveryContext', {}).get('channel', 'unknown'),
                            'session_file': session_info.get('sessionFile', ''),
                            'messages': []
                        }
                        
                        # 读取 session 内容
                        session_file = session_info.get('sessionFile', '')
                        if session_file and Path(session_file).exists():
                            messages = self._read_session_file(Path(session_file))
                            session_data['messages'] = messages
                            session_data['message_count'] = len(messages)
                        
                        sessions.append(session_data)
        except Exception as e:
            print(f"警告: 无法读取 sessions: {e}")
        
        return sessions
    
    def _read_session_file(self, session_file: Path) -> List[Dict]:
        """读取单个 session 文件内容"""
        messages = []
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        
                        # 只提取用户消息
                        if entry.get('type') == 'message':
                            msg_data = entry.get('message', {})
                            role = msg_data.get('role', '')
                            
                            if role == 'user':
                                content = msg_data.get('content', [])
                                text_content = self._extract_text_from_content(content)
                                
                                if text_content:
                                    messages.append({
                                        'timestamp': entry.get('timestamp', ''),
                                        'role': role,
                                        'content': text_content[:500]  # 限制长度
                                    })
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"警告: 无法读取 session 文件 {session_file}: {e}")
        
        return messages
    
    def _extract_text_from_content(self, content: List[Dict]) -> str:
        """从 content 中提取文本"""
        texts = []
        
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text = item.get('text', '')
                    if text:
                        texts.append(text)
        
        return '\n'.join(texts)
    
    def get_sessions_summary(self, days: int = 1) -> Dict:
        """获取 sessions 摘要"""
        sessions = self.read_sessions(days)
        
        total_messages = sum(s.get('message_count', 0) for s in sessions)
        
        return {
            'session_count': len(sessions),
            'total_messages': total_messages,
            'sessions': [
                {
                    'key': s['key'],
                    'channel': s['channel'],
                    'message_count': s.get('message_count', 0)
                }
                for s in sessions
            ]
        }
    
    # ========== 综合读取 ==========
    
    def get_all_stats(self) -> Dict:
        """获取所有层的统计信息"""
        return {
            'memory': self.get_memory_stats(),
            'learnings': self.get_learning_stats(),
            'sessions': self.get_sessions_summary(days=1),
            'timestamp': datetime.now().isoformat()
        }
