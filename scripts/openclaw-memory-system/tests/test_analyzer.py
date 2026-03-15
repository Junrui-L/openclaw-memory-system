#!/usr/bin/env python3
"""
分析器模块单元测试
"""

import sys
import unittest
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.analyzer import MemoryAnalyzer


class TestMemoryAnalyzer(unittest.TestCase):
    """测试 MemoryAnalyzer 类"""
    
    def setUp(self):
        """测试前准备"""
        self.config = {
            'todo': {
                'smart_priority': True,
                'high_keywords': ['紧急', '重要', 'critical', 'urgent'],
                'medium_keywords': ['建议', 'todo', '应该', '需要']
            }
        }
        self.analyzer = MemoryAnalyzer(self.config)
    
    def test_extract_todos(self):
        """测试待办事项提取"""
        content = """
- [ ] 完成代码审查
- [ ] 修复紧急bug
- [x] 已完成的事项
- [ ] 普通待办
"""
        todos = self.analyzer.extract_todos(content)
        
        self.assertEqual(len(todos), 3)  # 排除已完成的
        self.assertEqual(todos[0]['text'], '完成代码审查')
        self.assertEqual(todos[0]['priority'], 'low')  # 无关键词
        self.assertEqual(todos[1]['priority'], 'high')  # 紧急
    
    def test_analyze_todo_priority(self):
        """测试待办优先级分析"""
        # 高优先级
        self.assertEqual(
            self.analyzer._analyze_todo_priority('这是一个紧急任务'),
            'high'
        )
        # 中优先级
        self.assertEqual(
            self.analyzer._analyze_todo_priority('建议完成这个任务'),
            'medium'
        )
        # 低优先级
        self.assertEqual(
            self.analyzer._analyze_todo_priority('普通任务'),
            'low'
        )
    
    def test_extract_key_events(self):
        """测试关键事件提取"""
        content = """
### 事件1
内容1

### 事件2
内容2
"""
        events = self.analyzer.extract_key_events(content)
        
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['title'], '事件1')
        self.assertEqual(events[1]['title'], '事件2')
    
    def test_extract_time_entries(self):
        """测试时间记录提取"""
        content = """
### 09:00 - 开始工作
### 12:30 - 午餐时间
### 18:00 - 下班
"""
        entries = self.analyzer.extract_time_entries(content)
        
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0]['time'], '09:00')
        self.assertEqual(entries[0]['content'], '开始工作')
    
    def test_generate_summary(self):
        """测试摘要生成"""
        content = "这是一段很长的内容" * 50
        summary = self.analyzer.generate_summary(content, max_length=50)
        
        self.assertLessEqual(len(summary), 53)  # 50 + "..."
        self.assertTrue(summary.endswith('...'))
    
    def test_extract_keywords_tfidf(self):
        """测试 TF-IDF 关键词提取"""
        content = """
# Python 开发指南

Python 是一种强大的编程语言。
Python 支持多种编程范式。
Python 有丰富的标准库。

## 关键特性
- Python 简洁优雅
- Python 易于学习
- Python 应用广泛
"""
        keywords = self.analyzer.extract_keywords_tfidf(content, top_n=3)
        
        self.assertEqual(len(keywords), 3)
        # Python 应该排在前面（出现次数多 + 在标题中）
        self.assertIn('python', [k.lower() for k in keywords])
    
    def test_clean_markdown(self):
        """测试 Markdown 清理"""
        content = """# 标题
**加粗** `代码` [链接](http://example.com)
```
code block
```
"""
        clean = self.analyzer._clean_markdown(content)
        
        self.assertNotIn('#', clean)
        self.assertNotIn('**', clean)
        self.assertNotIn('`', clean)
    
    def test_filter_words(self):
        """测试词过滤"""
        words = ['the', 'and', 'Python', '的', '了', 'code', 'a', 'test123']
        filtered = self.analyzer._filter_words(words)
        
        # 过滤后转为小写
        filtered_lower = [w.lower() for w in filtered]
        self.assertIn('python', filtered_lower)
        self.assertIn('code', filtered_lower)
        self.assertIn('test123', filtered_lower)
        self.assertNotIn('the', filtered)
        self.assertNotIn('的', filtered)
    
    def test_extract_title_words(self):
        """测试标题词提取"""
        content = """
# 主标题 Python
## 副标题 Django

普通内容 Flask
"""
        title_words = self.analyzer._extract_title_words(content)
        
        self.assertIn('python', title_words)
        self.assertIn('django', title_words)
        self.assertNotIn('flask', title_words)


class TestPriorityIcons(unittest.TestCase):
    """测试优先级图标"""
    
    def setUp(self):
        self.config = {'todo': {}}
        self.analyzer = MemoryAnalyzer(self.config)
    
    def test_priority_icons(self):
        """测试优先级图标映射"""
        self.assertEqual(self.analyzer._get_priority_icon('high'), '🔴')
        self.assertEqual(self.analyzer._get_priority_icon('medium'), '🟡')
        self.assertEqual(self.analyzer._get_priority_icon('low'), '🟢')
        self.assertEqual(self.analyzer._get_priority_icon('normal'), '⚪')
        self.assertEqual(self.analyzer._get_priority_icon('unknown'), '⚪')


if __name__ == '__main__':
    unittest.main()
