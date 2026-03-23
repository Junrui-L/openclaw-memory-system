#!/usr/bin/env python3
"""
索引一致性检查修复脚本
"""

import re
from pathlib import Path

# 读取 health_v3.py
with open('/home/node/.openclaw/workspace/scripts/openclaw-memory-system/modules/health_v3.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复索引一致性检查函数
old_func = '''    def _check_index_consistency(self) -> Dict:
        """
        索引一致性检查
        
        检查项:
            1. INDEX.md 中的文件数 vs 实际文件数
            2. 待办统计是否准确
        """
        # 获取 INDEX.md 内容
        index_content = self.reader.get('memory/INDEX.md')
        
        if not index_content:
            return {
                'name': '索引一致性',
                'status': 'warning',
                'message': 'INDEX.md 不存在',
                'alert': '⚠️ 索引一致性: INDEX.md 不存在'
            }
        
        # 统计 INDEX.md 中的记忆数（支持多种格式）
        import re
        # 格式1: 表格格式 | 2026-03-13 | [2026-03-13.md](./2026-03-13.md) | Friday |
        # 格式2: 列表格式 - **2026-03-13** 或 **2026-03-13-xxx** [描述]
        # 格式3: 索引格式 - **2026-03-13** [标题]
        index_memories = len(re.findall(r'\\| (\\d{4}-\\d{2}-\\d{2}) \\|', index_content))
        if index_memories == 0:
            # 尝试列表格式: - **2026-03-13** 或 - **2026-03-13-xxx**
            # 匹配 - **YYYY-MM-DD 开头的条目（包括带后缀的）
            index_memories = len(re.findall(r'- \\*\\*\\d{4}-\\d{2}-\\d{2}', index_content))
        
        # 统计实际记忆文件数（排除 INDEX.md 本身和 session-daily/events 文件）
        memory_dir = Path(self.paths.get('memory', ''))
        if memory_dir.exists():
            # 统计所有 2026-*.md 文件，排除 session-daily、events 和其他辅助文件
            actual_memories = len([f for f in memory_dir.glob('2026-*.md') 
                                   if f.name != 'INDEX.md' 
                                   and not f.name.startswith('session-daily-')
                                   and not f.name.startswith('events-')
                                   and not f.name.startswith('memories-lancedb-export-')])
        else:
            actual_memories = 0
        
        if index_memories == actual_memories:
            return {
                'name': '索引一致性',
                'status': 'ok',
                'message': f'一致 ({actual_memories} 个记忆)'
            }
        else:
            return {
                'name': '索引一致性',
                'status': 'warning',
                'message': f'INDEX: {index_memories}, 实际: {actual_memories}',
                'alert': f'⚠️ 索引不一致: INDEX {index_memories} vs 实际 {actual_memories}'
            }'''

new_func = '''    def _check_index_consistency(self) -> Dict:
        """
        索引一致性检查
        
        检查项:
            1. INDEX.md 中的主记忆文件数 vs 实际主记忆文件数
            2. 待办统计是否准确
        
        注意: INDEX.md 是摘要索引，只包含主记忆文件（YYYY-MM-DD.md）
              不包含带后缀的文件（如 -session-recording, -heartbeat-check 等）
        """
        # 获取 INDEX.md 内容
        index_content = self.reader.get('memory/INDEX.md')
        
        if not index_content:
            return {
                'name': '索引一致性',
                'status': 'warning',
                'message': 'INDEX.md 不存在',
                'alert': '⚠️ 索引一致性: INDEX.md 不存在'
            }
        
        # 统计 INDEX.md 中的主记忆数（纯日期格式 YYYY-MM-DD）
        import re
        # 匹配 - **2026-03-13** 格式（纯日期，后面跟 [ 或 空格）
        index_memories = len(re.findall(r'- \\*\\*\\d{4}-\\d{2}-\\d{2}\\*\\*\\s*[\\[\\s]', index_content))
        
        # 统计实际主记忆文件数（纯日期格式 YYYY-MM-DD.md）
        memory_dir = Path(self.paths.get('memory', ''))
        if memory_dir.exists():
            # 只统计纯日期格式的主记忆文件
            actual_memories = len([f for f in memory_dir.glob('2026-*.md') 
                                   if re.match(r'^\\d{4}-\\d{2}-\\d{2}\\.md$', f.name)])
        else:
            actual_memories = 0
        
        if index_memories == actual_memories:
            return {
                'name': '索引一致性',
                'status': 'ok',
                'message': f'一致 ({actual_memories} 个主记忆)'
            }
        else:
            return {
                'name': '索引一致性',
                'status': 'warning',
                'message': f'INDEX: {index_memories}, 实际: {actual_memories}',
                'alert': f'⚠️ 索引不一致: INDEX {index_memories} vs 实际 {actual_memories}'
            }'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('/home/node/.openclaw/workspace/scripts/openclaw-memory-system/modules/health_v3.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 修复完成")
else:
    print("⚠️ 未找到匹配文本，可能需要手动修复")
