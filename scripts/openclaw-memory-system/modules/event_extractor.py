#!/usr/bin/env python3
"""
事件提取器 - 从每日 Sessions 中提取关键事件并存入 lancedb-pro

功能：
1. 读取每日 Sessions
2. 使用 LLM 或规则提取关键事件
3. 结构化存储到 lancedb-pro
4. 避免重复存储（基于内容哈希去重）
"""

import json
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Event:
    """事件数据类"""
    date: str
    event_type: str  # decision, fact, preference, task, learning
    title: str
    content: str
    source_session: str
    importance: float  # 0.0 - 1.0
    tags: List[str]
    hash_id: str  # 内容哈希，用于去重
    
    def to_memory_text(self) -> str:
        """转换为 memory_store 的 text 格式"""
        return f"""[{self.date}] {self.title}

类型: {self.event_type}
内容: {self.content}
来源: {self.source_session}
标签: {', '.join(self.tags)}
"""


class EventExtractor:
    """
    事件提取器
    
    从 Sessions 中提取结构化事件，支持：
    - 规则提取（关键词、模式匹配）
    - 智能分类（决策、事实、偏好、任务、经验）
    """
    
    # 事件类型定义
    EVENT_TYPES = {
        'decision': '决策/决定',
        'fact': '重要事实',
        'preference': '用户偏好',
        'task': '任务/待办',
        'learning': '经验/教训',
        'entity': '实体信息',
        'reflection': '反思/总结'
    }
    
    # 提取规则（正则模式）
    EXTRACTION_RULES = {
        'decision': [
            r'(?:决定|采用|选择|使用|确定|定为)\s*[:：]\s*(.+?)(?:\n|$)',
            r'(?:最终|最后|结果).*?(?:采用|选择|使用|确定)\s*[:：]\s*(.+?)(?:\n|$)',
            r'(?:方案|计划).*?(?:确定|定为)\s*[:：]\s*(.+?)(?:\n|$)',
        ],
        'preference': [
            r'(?:我喜欢|我偏好|我习惯|我要|我希望)\s*[:：]\s*(.+?)(?:\n|$)',
            r'(?:不要|别|禁止)\s*[:：]\s*(.+?)(?:\n|$)',
            r'(?:总是|经常|通常)\s*[:：]\s*(.+?)(?:\n|$)',
        ],
        'task': [
            r'(?:待办|TODO|todo|任务)\s*[:：]\s*(.+?)(?:\n|$)',
            r'(?:需要|要|得)\s*(?:做|完成|处理)\s*[:：]\s*(.+?)(?:\n|$)',
            r'(?:接下来|下一步|稍后)\s*[:：]\s*(.+?)(?:\n|$)',
        ],
        'learning': [
            r'(?:教训|经验|总结|反思)\s*[:：]\s*(.+?)(?:\n|$)',
            r'(?:注意|小心|避免)\s*[:：]\s*(.+?)(?:\n|$)',
            r'(?:最佳实践|推荐|建议)\s*[:：]\s*(.+?)(?:\n|$)',
        ],
    }
    
    def __init__(self, config: Dict):
        self.config = config
        self.sessions_dir = Path("/home/node/.openclaw/agents/main/sessions")
        self.memory_dir = Path(config.get('paths', {}).get('memory', '/home/node/.openclaw/workspace/memory'))
        self.extracted_hashes: Set[str] = self._load_extracted_hashes()
    
    def _load_extracted_hashes(self) -> Set[str]:
        """加载已提取的事件哈希（用于去重）"""
        hash_file = self.memory_dir / '.extracted_events.json'
        if hash_file.exists():
            try:
                with open(hash_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except:
                pass
        return set()
    
    def _save_extracted_hashes(self):
        """保存已提取的事件哈希"""
        hash_file = self.memory_dir / '.extracted_events.json'
        try:
            with open(hash_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.extracted_hashes), f, indent=2)
        except Exception as e:
            print(f"⚠️ 无法保存哈希记录: {e}")
    
    def _compute_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    
    def _is_duplicate(self, content: str) -> bool:
        """检查是否重复"""
        hash_id = self._compute_hash(content)
        return hash_id in self.extracted_hashes
    
    def _mark_extracted(self, content: str):
        """标记为已提取"""
        hash_id = self._compute_hash(content)
        self.extracted_hashes.add(hash_id)
    
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
                        
                        # 检查日期
                        if timestamp:
                            try:
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                local_dt = dt.astimezone()
                                local_date = local_dt.strftime('%Y-%m-%d')
                                if local_date != target_date:
                                    continue
                            except:
                                if target_date not in timestamp:
                                    continue
                        else:
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
                                    'content': content.strip()
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
        """提取指定日期的所有 Sessions"""
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
    
    def _extract_by_rules(self, text: str, session_id: str, date: str) -> List[Event]:
        """使用规则提取事件"""
        events = []
        
        for event_type, patterns in self.EXTRACTION_RULES.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    content = match.group(1).strip()
                    if len(content) < 10 or len(content) > 500:
                        continue
                    
                    # 检查重复
                    if self._is_duplicate(content):
                        continue
                    
                    # 生成标题
                    title = self._generate_title(content, event_type)
                    
                    # 确定重要性
                    importance = self._calculate_importance(content, event_type)
                    
                    # 提取标签
                    tags = self._extract_tags(content)
                    
                    event = Event(
                        date=date,
                        event_type=event_type,
                        title=title,
                        content=content,
                        source_session=session_id,
                        importance=importance,
                        tags=tags,
                        hash_id=self._compute_hash(content)
                    )
                    
                    events.append(event)
                    self._mark_extracted(content)
        
        return events
    
    def _generate_title(self, content: str, event_type: str) -> str:
        """生成事件标题"""
        # 取前30个字符作为标题
        title = content[:30].replace('\n', ' ').strip()
        if len(content) > 30:
            title += '...'
        
        # 添加类型前缀
        type_emoji = {
            'decision': '🎯',
            'preference': '💡',
            'task': '📋',
            'learning': '📚',
            'fact': '📌',
            'entity': '👤',
            'reflection': '🤔'
        }
        
        emoji = type_emoji.get(event_type, '📝')
        return f"{emoji} {title}"
    
    def _calculate_importance(self, content: str, event_type: str) -> float:
        """计算事件重要性"""
        base_scores = {
            'decision': 0.8,
            'preference': 0.7,
            'task': 0.6,
            'learning': 0.75,
            'fact': 0.5,
            'entity': 0.6,
            'reflection': 0.65
        }
        
        score = base_scores.get(event_type, 0.5)
        
        # 根据内容调整
        if any(k in content for k in ['重要', '关键', '核心', '必须']):
            score += 0.1
        if any(k in content for k in ['错误', '失败', '问题', '教训']):
            score += 0.1
        if any(k in content for k in ['完成', '成功', '解决']):
            score += 0.05
        
        return min(score, 1.0)
    
    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = []
        
        # 技术相关
        if any(k in content for k in ['代码', '程序', '开发', 'Python', 'JavaScript']):
            tags.append('技术')
        if any(k in content for k in ['配置', '部署', '安装', '设置']):
            tags.append('配置')
        if any(k in content for k in ['错误', '失败', '异常', 'Bug']):
            tags.append('问题')
        if any(k in content for k in ['修复', '解决', '完成']):
            tags.append('解决')
        
        # 项目相关
        if any(k in content for k in ['项目', '任务', '功能', '需求']):
            tags.append('项目')
        
        # 学习相关
        if any(k in content for k in ['学习', '文档', '指南', '教程']):
            tags.append('学习')
        
        return tags
    
    def _extract_session_summary(self, session: Dict) -> Optional[Event]:
        """提取 Session 摘要作为事件"""
        messages = session.get('messages', [])
        if not messages:
            return None
        
        # 提取用户消息作为主题
        user_messages = [m for m in messages if m['role'] == 'user']
        if not user_messages:
            return None
        
        # 取前3条用户消息作为摘要
        topics = []
        for msg in user_messages[:3]:
            content = msg['content'][:50].replace('\n', ' ')
            if len(msg['content']) > 50:
                content += '...'
            topics.append(content)
        
        summary_content = ' | '.join(topics)
        
        # 检查重复
        if self._is_duplicate(summary_content):
            return None
        
        return Event(
            date=session['date'],
            event_type='fact',
            title=f"📄 Session 对话摘要: {session['session_id'][:8]}...",
            content=summary_content,
            source_session=session['session_id'],
            importance=0.5,
            tags=['对话', '摘要'],
            hash_id=self._compute_hash(summary_content)
        )
    
    def extract_events_from_sessions(self, date: str) -> List[Event]:
        """从 Sessions 中提取事件"""
        print(f"🔍 提取 {date} 的事件...")
        
        # 1. 读取 Sessions
        sessions = self.extract_daily_sessions(date)
        if not sessions:
            print(f"  ℹ️ {date} 无 Sessions")
            return []
        
        print(f"  📊 找到 {len(sessions)} 个 Sessions")
        
        all_events = []
        
        # 2. 从每个 Session 提取事件
        for session in sessions:
            session_text = '\n'.join([m['content'] for m in session['messages']])
            
            # 规则提取
            events = self._extract_by_rules(session_text, session['session_id'], date)
            all_events.extend(events)
            
            # Session 摘要
            summary_event = self._extract_session_summary(session)
            if summary_event:
                all_events.append(summary_event)
                self._mark_extracted(summary_event.content)
        
        # 3. 按重要性排序
        all_events.sort(key=lambda e: e.importance, reverse=True)
        
        # 4. 保存哈希记录
        self._save_extracted_hashes()
        
        print(f"  ✅ 提取 {len(all_events)} 个事件")
        return all_events
    
    def generate_daily_summary(self, events: List[Event], date: str) -> str:
        """生成每日事件摘要"""
        lines = []
        lines.append(f"# 📅 {date} - 每日事件摘要")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**事件数量**: {len(events)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 按类型分组
        events_by_type = {}
        for event in events:
            event_type = event.event_type
            if event_type not in events_by_type:
                events_by_type[event_type] = []
            events_by_type[event_type].append(event)
        
        # 输出各类事件
        for event_type, type_name in self.EVENT_TYPES.items():
            if event_type not in events_by_type:
                continue
            
            type_events = events_by_type[event_type]
            lines.append(f"## {type_name} ({len(type_events)})")
            lines.append("")
            
            for event in type_events[:10]:  # 每类最多10条
                lines.append(f"### {event.title}")
                lines.append(f"- **内容**: {event.content}")
                lines.append(f"- **重要性**: {'⭐' * int(event.importance * 5)}")
                lines.append(f"- **标签**: {', '.join(event.tags)}")
                lines.append(f"- **来源**: {event.source_session[:8]}...")
                lines.append("")
            
            if len(type_events) > 10:
                lines.append(f"*... 还有 {len(type_events) - 10} 条 ...*")
                lines.append("")
        
        return '\n'.join(lines)
    
    def save_events_to_file(self, events: List[Event], date: str):
        """保存事件到文件"""
        summary = self.generate_daily_summary(events, date)
        
        # 保存到 memory 目录
        output_file = self.memory_dir / f"events-{date}.md"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"  ✅ 事件摘要已保存: {output_file}")
        except Exception as e:
            print(f"  ❌ 保存失败: {e}")
        
        return output_file
    
    def store_events_to_lancedb(self, events: List[Event]):
        """将事件存储到 lancedb-pro"""
        print(f"\n💾 存储到 lancedb-pro...")
        
        stored_count = 0
        for event in events:
            try:
                # 这里需要调用 memory_store 工具
                # 由于是在 Python 脚本中，需要通过 subprocess 或其他方式调用
                # 暂时记录到文件，后续可以集成 OpenClaw API
                
                # 生成存储文本
                memory_text = event.to_memory_text()
                
                # 记录到存储日志（后续可以批量导入）
                self._append_to_storage_log(event)
                stored_count += 1
                
            except Exception as e:
                print(f"  ⚠️ 存储失败 {event.title}: {e}")
        
        print(f"  ✅ 已记录 {stored_count} 个事件到存储日志")
    
    def _append_to_storage_log(self, event: Event):
        """追加到存储日志（用于后续批量导入）"""
        log_file = self.memory_dir / '.events_storage.jsonl'
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'date': event.date,
            'type': event.event_type,
            'title': event.title,
            'content': event.content,
            'importance': event.importance,
            'tags': event.tags,
            'hash_id': event.hash_id
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️ 无法写入存储日志: {e}")
    
    def process_daily_events(self, date: str = None, store_to_lancedb: bool = True):
        """
        处理每日事件的主入口
        
        Args:
            date: 日期 (YYYY-MM-DD)，默认今天
            store_to_lancedb: 是否存储到 lancedb-pro
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n{'='*60}")
        print(f"📅 处理 {date} 的事件")
        print(f"{'='*60}\n")
        
        # 1. 提取事件
        events = self.extract_events_from_sessions(date)
        
        if not events:
            print(f"\nℹ️ {date} 无事件可提取")
            return
        
        # 2. 保存到文件
        self.save_events_to_file(events, date)
        
        # 3. 存储到 lancedb-pro
        if store_to_lancedb:
            self.store_events_to_lancedb(events)
        
        print(f"\n{'='*60}")
        print(f"✅ {date} 事件处理完成")
        print(f"   提取事件: {len(events)}")
        print(f"{'='*60}\n")


# 命令行入口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='事件提取器 - 从 Sessions 提取关键事件')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)，默认今天')
    parser.add_argument('--no-store', action='store_true', help='不存储到 lancedb-pro')
    
    args = parser.parse_args()
    
    # 加载配置
    config_path = Path(__file__).parent.parent / 'config.yaml'
    config = {}
    if config_path.exists():
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except:
            pass
    
    # 创建提取器并处理
    extractor = EventExtractor(config)
    extractor.process_daily_events(
        date=args.date,
        store_to_lancedb=not args.no_store
    )


if __name__ == '__main__':
    main()
