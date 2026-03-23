#!/usr/bin/env python3
"""
学习条目升降级脚本
- 检查 .learnings/LEARNINGS.md 中 status=pending 的条目
- 验证 3 次+ 的升级到 HOT (self-improving/memory.md)
- 30 天未使用的降级到 WARM
- 90 天未使用的归档到 COLD
"""

import re
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/node/.openclaw/workspace")
LEARNINGS_FILE = WORKSPACE / ".learnings" / "LEARNINGS.md"
HOT_MEMORY = WORKSPACE / "self-improving" / "memory.md"
WARM_PROJECTS = WORKSPACE / "self-improving" / "projects"
WARM_DOMAINS = WORKSPACE / "self-improving" / "domains"
COLD_ARCHIVE = WORKSPACE / "self-improving" / "archive"

def parse_learnings():
    """解析 LEARNINGS.md 文件"""
    if not LEARNINGS_FILE.exists():
        return []
    
    content = LEARNINGS_FILE.read_text(encoding='utf-8')
    entries = []
    
    # 匹配每个学习条目
    pattern = r'## \[(LRN-[\d-]+)\].*?\n\*\*Logged\*\*: ([^\n]+).*?\*\*Status\*\*: ([^\n]+).*?\*\*Recurrence-Count\*\*: (\d+).*?(?=---|$)'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        entry_id = match.group(1)
        logged = match.group(2)
        status = match.group(3).strip()
        recurrence = int(match.group(4))
        
        entries.append({
            'id': entry_id,
            'logged': logged,
            'status': status,
            'recurrence': recurrence,
            'content': match.group(0)
        })
    
    return entries

def should_promote(entry):
    """判断是否应该升级到 HOT"""
    return entry['status'] == 'pending' and entry['recurrence'] >= 3

def update_learning_status(entry_id, new_status):
    """更新 LEARNINGS.md 中的状态"""
    if not LEARNINGS_FILE.exists():
        return False
    
    content = LEARNINGS_FILE.read_text(encoding='utf-8')
    pattern = f'(## \[{entry_id}\].*?\*\*Status\*\*: )pending'
    replacement = f'\g<1>{new_status}'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content != content:
        LEARNINGS_FILE.write_text(new_content, encoding='utf-8')
        return True
    return False

def promote_to_hot(entry):
    """升级到 HOT 记忆"""
    # 提取关键信息
    summary_match = re.search(r'### Summary\s*\n([^\n]+)', entry['content'])
    summary = summary_match.group(1) if summary_match else entry['id']
    
    # 添加到 HOT memory
    hot_content = HOT_MEMORY.read_text(encoding='utf-8')
    
    # 在升降级状态表格中添加
    today = datetime.now().strftime('%Y-%m-%d')
    new_row = f"| {summary[:30]}... | {entry['id']} | {entry['recurrence']} | ✅ 已升级 ({today}) |\n"
    
    # 替换表格最后一行
    lines = hot_content.split('\n')
    for i, line in enumerate(lines):
        if '| 条目 | 来源 | 验证次数 | 状态 |' in line:
            # 找到表格末尾
            j = i + 2
            while j < len(lines) and lines[j].startswith('|'):
                j += 1
            lines.insert(j, new_row.rstrip())
            break
    
    HOT_MEMORY.write_text('\n'.join(lines), encoding='utf-8')
    
    # 更新状态
    update_learning_status(entry['id'], 'promoted')
    
    print(f"✅ 已升级: {entry['id']} -> HOT")
    return True

def check_cold_archive():
    """检查需要归档的 WARM 记忆"""
    cutoff_30 = datetime.now() - timedelta(days=30)
    cutoff_90 = datetime.now() - timedelta(days=90)
    
    # 检查 WARM 文件
    for warm_dir in [WARM_PROJECTS, WARM_DOMAINS]:
        if not warm_dir.exists():
            continue
        
        for file in warm_dir.glob('*.md'):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            
            if mtime < cutoff_90:
                # 归档到 COLD
                target = COLD_ARCHIVE / file.name
                file.rename(target)
                print(f"🧊 已归档: {file.name} -> COLD")
            elif mtime < cutoff_30:
                print(f"⏳ 提醒: {file.name} 30天未使用，考虑归档")

def main():
    """主函数"""
    print("=" * 50)
    print("学习条目升降级检查")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # 1. 检查待升级的条目
    entries = parse_learnings()
    promoted = 0
    
    print(f"\n📊 发现 {len(entries)} 个学习条目")
    
    for entry in entries:
        if should_promote(entry):
            print(f"\n🔄 准备升级: {entry['id']} (验证{entry['recurrence']}次)")
            if promote_to_hot(entry):
                promoted += 1
        elif entry['status'] == 'pending':
            print(f"⏳ 待验证: {entry['id']} (当前{entry['recurrence']}次, 需3次)")
    
    # 2. 检查归档
    print("\n🧊 检查 WARM 记忆归档...")
    check_cold_archive()
    
    print(f"\n✅ 完成: {promoted} 个条目已升级")
    print("=" * 50)

if __name__ == '__main__':
    main()
