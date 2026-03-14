#!/usr/bin/env python3
"""
数据读取模块 - v3.0 重构版

职责：薄封装 OpenClaw memory_search/memory_get
原则：
    - 只做封装，不做逻辑
    - 所有数据查询都通过 search/get
    - 不直接操作文件系统（SessionExtractor 除外）
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


class MemoryReader:
    """
    记忆数据读取器 - 封装 OpenClaw 内置能力
    
    重要说明：
        - memory_search 只覆盖 workspace/memory/ 和 MEMORY.md
        - 不覆盖 agents/main/sessions/
        - Sessions 读取使用 SessionExtractor（直接读取文件系统）
    """
    
    def __init__(self, config: Dict):
        """
        初始化
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.paths = config.get('paths', {})
        self.cache: Dict[str, Any] = {}  # 简单缓存
    
    # ==================== 核心封装方法 ====================
    
    def search(
        self, 
        query: str, 
        max_results: int = 10,
        min_score: float = 0.5,
        **kwargs
    ) -> List[Dict]:
        """
        语义搜索记忆
        
        封装: OpenClaw memory_search 工具
        
        覆盖范围:
            - workspace/memory/*.md
            - workspace/MEMORY.md
        
        不覆盖:
            - agents/main/sessions/
            
        Args:
            query: 搜索查询
            max_results: 最大结果数
            min_score: 最小匹配分数
            
        Returns:
            搜索结果列表
        """
        try:
            # 调用 OpenClaw memory_search 工具
            # 注意：实际实现需要通过 OpenClaw 工具调用
            # 这里提供封装接口
            
            # 模拟调用（实际实现需替换）
            results = self._call_memory_search(query, max_results, min_score)
            return results
            
        except Exception as e:
            print(f"⚠️ search 失败: {e}")
            return []
    
    def _call_memory_search(self, query: str, max_results: int, min_score: float) -> List[Dict]:
        """
        调用 OpenClaw memory_search
        
        实际实现需使用 OpenClaw 工具调用
        """
        # TODO: 实现实际的工具调用
        # 目前返回空列表，需要接入 OpenClaw
        
        # 示例返回格式：
        return [
            {
                'path': 'memory/2026-03-13.md',
                'score': 0.85,
                'snippet': '...',
                'keywords': ['测试'],
                'source': 'memory'
            }
        ]
    
    def get(
        self, 
        path: str, 
        from_line: int = None, 
        lines: int = None
    ) -> Optional[str]:
        """
        精确读取文件内容
        
        封装: OpenClaw memory_get 工具
        
        Args:
            path: 文件路径（相对 workspace）
            from_line: 起始行号（1-based）
            lines: 读取行数
            
        Returns:
            文件内容字符串，文件不存在返回 None
        """
        try:
            # 调用 OpenClaw memory_get 工具
            content = self._call_memory_get(path, from_line, lines)
            return content
            
        except Exception as e:
            print(f"⚠️ get 失败 {path}: {e}")
            return None
    
    def _call_memory_get(self, path: str, from_line: int = None, lines: int = None) -> Optional[str]:
        """
        调用 OpenClaw memory_get
        
        实际实现需使用 OpenClaw 工具调用
        """
        # TODO: 实现实际的工具调用
        
        # 临时实现：直接读取文件
        full_path = Path(self.paths.get('workspace', '')) / path
        if not full_path.exists():
            return None
        
        try:
            content = full_path.read_text(encoding='utf-8')
            
            # 行范围截取
            if from_line is not None and lines is not None:
                all_lines = content.split('\n')
                start = from_line - 1  # 0-based
                end = start + lines
                content = '\n'.join(all_lines[start:end])
            
            return content
            
        except Exception as e:
            print(f"⚠️ 读取文件失败 {full_path}: {e}")
            return None
    
    # ==================== 便捷查询方法（基于 search） ====================
    
    def get_recent(self, days: int = 7) -> List[Dict]:
        """
        获取最近N天的记忆
        
        实现: 使用 search 查询日期范围
        
        Args:
            days: 天数
            
        Returns:
            记忆列表
        """
        results = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 使用 search 查询该日期
            search_results = self.search(date, max_results=5)
            
            for result in search_results:
                if date in result.get('path', ''):
                    results.append({
                        'date': date,
                        'path': result['path'],
                        'snippet': result.get('snippet', ''),
                        'score': result.get('score', 0)
                    })
                    break
        
        return results
    
    def get_todos(self, status: str = "pending") -> List[Dict]:
        """
        获取待办事项
        
        实现: 使用 search 搜索待办语法
        
        Args:
            status: 状态 (pending/done/all)
            
        Returns:
            待办列表
        """
        # 根据状态构建查询
        if status == "pending":
            query = "- [ ]"
        elif status == "done":
            query = "- [x]"
        else:
            query = "- ["
        
        results = self.search(query, max_results=100)
        
        todos = []
        for result in results:
            # 从 snippet 中提取待办文本
            snippet = result.get('snippet', '')
            if '- [ ]' in snippet or '- [x]' in snippet:
                todos.append({
                    'text': snippet.strip(),
                    'path': result['path'],
                    'source': result.get('source', 'memory')
                })
        
        return todos
    
    def get_keywords(self, path: str) -> List[str]:
        """
        获取指定记忆的关键词
        
        实现: 复用 search 返回的关键词
        
        Args:
            path: 记忆文件路径
            
        Returns:
            关键词列表
        """
        # 使用 search 查询该文件
        results = self.search(path, max_results=1)
        
        if results:
            return results[0].get('keywords', [])
        
        return []
    
    def get_stats(self) -> Dict:
        """
        获取记忆统计
        
        实现: 使用 search 聚合统计
        
        Returns:
            统计信息
        """
        # 获取总记忆数（搜索所有日期）
        all_results = self.search("2026-", max_results=1000)
        
        # 统计待办
        todos = self.get_todos("all")
        pending = len([t for t in todos if '- [ ]' in t['text']])
        
        return {
            'total_memories': len(all_results),
            'total_todos': len(todos),
            'pending_todos': pending,
            'recent_7_days': len(self.get_recent(7))
        }
    
    # ==================== 删除的方法（v2.0 → v3.0） ====================
    
    # ❌ 删除: read_daily_memory() - 使用 get() 替代
    # ❌ 删除: read_hot_memory() - 使用 search("HOT") 替代
    # ❌ 删除: read_warm_memory() - 使用 search("WARM") 替代
    # ❌ 删除: list_memory_files() - 使用 search 替代
    # ❌ 删除: read_sessions() - 使用 SessionExtractor 替代
    # ❌ 删除: get_learning_stats() - 使用 search("LEARNINGS") 替代


# 兼容性：保留 v2.0 接口（逐步迁移）
class MemoryReaderV2Compat(MemoryReader):
    """
    v2.0 兼容接口
    
    用于逐步迁移，最终删除
    """
    
    def read_daily_memory(self, date: str) -> Optional[str]:
        """兼容 v2.0"""
        return self.get(f"memory/{date}.md")
    
    def list_memory_files(self, days: int = 7) -> List[str]:
        """兼容 v2.0"""
        recent = self.get_recent(days)
        return [r['date'] for r in recent]


if __name__ == '__main__':
    # 测试
    config = {
        'paths': {
            'workspace': '/home/node/.openclaw/workspace',
            'memory': '/home/node/.openclaw/workspace/memory'
        }
    }
    
    reader = MemoryReader(config)
    
    # 测试 search
    print("Testing search...")
    results = reader.search("测试", max_results=5)
    print(f"Found {len(results)} results")
    
    # 测试 get
    print("\nTesting get...")
    content = reader.get("memory/2026-03-13.md", from_line=1, lines=10)
    if content:
        print(f"Read {len(content)} characters")
    else:
        print("File not found")
    
    # 测试 get_recent
    print("\nTesting get_recent...")
    recent = reader.get_recent(3)
    print(f"Found {len(recent)} recent memories")