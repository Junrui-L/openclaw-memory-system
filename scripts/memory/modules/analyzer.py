#!/usr/bin/env python3
"""
分析提取模块
分析日记内容，提取关键信息
"""

import re
import math
from collections import Counter
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class MemoryAnalyzer:
    """记忆分析器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.todo_config = config.get('todo', {})
    
    def extract_todos(self, content: str) -> List[Dict]:
        """提取待办事项"""
        todos = []
        
        # 匹配 Markdown 待办语法: - [ ] 待办内容
        pattern = r'^- \[ \]\s*(.+)$'
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            todo_text = match.group(1).strip()
            priority = self._analyze_todo_priority(todo_text)
            
            todos.append({
                'text': todo_text,
                'priority': priority,
                'priority_icon': self._get_priority_icon(priority),
                'raw': match.group(0)
            })
        
        return todos
    
    def _analyze_todo_priority(self, todo: str) -> str:
        """智能分析待办优先级"""
        if not self.todo_config.get('smart_priority', False):
            return 'normal'
        
        high_keywords = self.todo_config.get('high_keywords', [])
        medium_keywords = self.todo_config.get('medium_keywords', [])
        
        todo_lower = todo.lower()
        
        # 检查高优先级关键词
        for keyword in high_keywords:
            if keyword.lower() in todo_lower:
                return 'high'
        
        # 检查中优先级关键词
        for keyword in medium_keywords:
            if keyword.lower() in todo_lower:
                return 'medium'
        
        return 'low'
    
    def _get_priority_icon(self, priority: str) -> str:
        """获取优先级图标"""
        icons = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢',
            'normal': '⚪'
        }
        return icons.get(priority, '⚪')
    
    def extract_key_events(self, content: str) -> List[Dict]:
        """提取关键事件"""
        events = []
        
        # 匹配三级标题: ### 事件标题
        pattern = r'^###\s+(.+)$'
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            event_title = match.group(1).strip()
            events.append({
                'title': event_title,
                'type': 'heading'
            })
        
        return events
    
    def extract_time_entries(self, content: str) -> List[Dict]:
        """提取时间记录（如: ### 14:30 - 事件）"""
        entries = []
        
        # 匹配时间格式: ### HH:MM - 内容
        pattern = r'^###\s+(\d{1,2}:\d{2})\s*-\s*(.+)$'
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            entries.append({
                'time': match.group(1),
                'content': match.group(2).strip()
            })
        
        return entries
    
    def extract_lessons(self, content: str) -> List[str]:
        """提取经验教训"""
        lessons = []
        
        # 匹配经验总结部分
        pattern = r'## 经验总结\s*\n+((?:- .+\n?)+)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            lessons_text = match.group(1)
            for line in lessons_text.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    lessons.append(line[2:])
        
        return lessons
    
    def generate_summary(self, content: str, max_length: int = 500) -> str:
        """生成内容摘要"""
        if not content:
            return "无内容"
        
        # 移除Markdown标记
        clean = re.sub(r'#+\s*', '', content)
        clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)
        clean = re.sub(r'`+', '', clean)
        
        # 取前N个字符
        if len(clean) > max_length:
            return clean[:max_length] + "..."
        
        return clean
    
    def analyze_memory_file(self, file_path: Path) -> Dict:
        """分析单个记忆文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e)}
        
        return {
            'file': file_path.name,
            'date': file_path.stem,
            'size': len(content),
            'todos': self.extract_todos(content),
            'events': self.extract_key_events(content),
            'time_entries': self.extract_time_entries(content),
            'lessons': self.extract_lessons(content),
            'summary': self.generate_summary(content, 300)
        }
    
    def generate_index(self, config: Dict) -> str:
        """生成记忆索引（包含 sessions）"""
        memory_dir = Path(config.get('paths', {}).get('memory', ''))
        
        if not memory_dir.exists():
            return "记忆目录不存在"
        
        files = sorted(memory_dir.glob('*.md'), reverse=True)
        
        index_lines = ["# 记忆索引\n", f"\n*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"]
        index_lines.append("## 最近记忆\n\n")
        
        for file_path in files[:30]:  # 最近30天
            date = file_path.stem
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取标题
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else date
                
                # 提取关键词（合并记忆文件和 sessions）
                keywords = self._extract_keywords(content)
                
                # 尝试读取对应日期的 sessions
                try:
                    from modules.reader import MemoryReader
                    reader = MemoryReader(config)
                    sessions = reader.read_sessions(days=1)
                    
                    # 提取 sessions 中的关键词
                    for session in sessions:
                        for msg in session.get('messages', []):
                            msg_keywords = self.extract_keywords_tfidf(msg.get('content', ''), top_n=3)
                            keywords.extend(msg_keywords)
                    
                    # 去重
                    keywords = list(dict.fromkeys(keywords))
                except Exception:
                    pass
                
                # 统计
                todos = len(self.extract_todos(content))
                events = len(self.extract_key_events(content))
                
                index_lines.append(f"- **{date}** [{title}]")
                if keywords:
                    index_lines.append(f"  - 关键词: {', '.join(keywords[:5])}")
                index_lines.append(f"  - 待办: {todos}, 事件: {events}\n")
                
            except Exception as e:
                index_lines.append(f"- **{date}** [读取失败: {e}]\n")
        
        index_content = '\n'.join(index_lines)
        
        # 保存索引
        index_path = memory_dir / 'INDEX.md'
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
        except Exception as e:
            print(f"警告: 无法保存索引: {e}")
        
        return index_content
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词（使用TF-IDF算法）"""
        return self.extract_keywords_tfidf(content)
    
    def extract_keywords_tfidf(self, content: str, top_n: int = 5) -> List[str]:
        """使用TF-IDF算法提取关键词"""
        if not content or len(content) < 50:
            return []
        
        # 1. 文本预处理
        # 移除Markdown标记
        clean_content = self._clean_markdown(content)
        
        # 2. 分词（按空格和标点分割）
        words = self._tokenize(clean_content)
        
        # 3. 过滤停用词和短词
        words = self._filter_words(words)
        
        if not words:
            return []
        
        # 4. 计算TF（词频）
        word_count = Counter(words)
        total_words = len(words)
        tf_scores = {word: count / total_words for word, count in word_count.items()}
        
        # 5. 计算IDF（逆文档频率）- 简化版，假设当前文档是唯一的
        # 使用标题权重提升
        title_words = self._extract_title_words(content)
        
        # 6. 计算TF-IDF并排序
        keywords_scores = {}
        for word, tf in tf_scores.items():
            # 基础TF-IDF
            idf = math.log(1 + 1 / (word_count[word] + 1))  # 简化IDF
            tfidf = tf * idf
            
            # 标题权重加成
            if word in title_words:
                tfidf *= 2.0
            
            # 长度惩罚（避免太长或太短的词）
            if 3 <= len(word) <= 10:
                tfidf *= 1.2
            
            keywords_scores[word] = tfidf
        
        # 7. 排序并返回前N个
        sorted_keywords = sorted(keywords_scores.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, score in sorted_keywords[:top_n]]
    
    def _clean_markdown(self, content: str) -> str:
        """清理Markdown标记"""
        # 移除代码块
        content = re.sub(r'```[\s\S]*?```', ' ', content)
        # 移除行内代码
        content = re.sub(r'`[^`]*`', ' ', content)
        # 移除链接
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        # 移除图片
        content = re.sub(r'!\[[^\]]*\]\([^\)]+\)', ' ', content)
        # 移除标题标记
        content = re.sub(r'#+\s*', ' ', content)
        # 移除加粗/斜体
        content = re.sub(r'\*\*?|\_\_?', ' ', content)
        # 移除表格分隔符
        content = re.sub(r'\|', ' ', content)
        return content
    
    def _tokenize(self, content: str) -> List[str]:
        """分词"""
        # 转换为小写
        content = content.lower()
        # 替换标点为分隔符
        content = re.sub(r'[^\w\u4e00-\u9fff]', ' ', content)
        # 分割
        words = content.split()
        return words
    
    def _filter_words(self, words: List[str]) -> List[str]:
        """过滤停用词和无效词"""
        # 停用词列表
        stopwords = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上',
            '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
            '今天', '昨天', '明天', '现在', '已经', '进行', '使用', '需要', '可以', '如果',
            'md', 'http', 'https', 'www', 'com', 'cn', 'org'
        }
        
        filtered = []
        for word in words:
            # 过滤停用词
            if word in stopwords:
                continue
            # 过滤纯数字
            if word.isdigit():
                continue
            # 过滤太短或太长的词
            if len(word) < 2 or len(word) > 20:
                continue
            filtered.append(word)
        
        return filtered
    
    def _extract_title_words(self, content: str) -> set:
        """提取标题中的词（给予更高权重）"""
        title_words = set()
        
        # 匹配一级标题
        title_pattern = r'^#\s+(.+)$'
        matches = re.findall(title_pattern, content, re.MULTILINE)
        
        for title in matches:
            words = self._tokenize(title)
            words = self._filter_words(words)
            title_words.update(words)
        
        # 匹配二级标题
        subtitle_pattern = r'^##\s+(.+)$'
        matches = re.findall(subtitle_pattern, content, re.MULTILINE)
        
        for subtitle in matches:
            words = self._tokenize(subtitle)
            words = self._filter_words(words)
            title_words.update(words)
        
        return title_words
